"""Options enrichment for the VCP screener.

Turns each stock signal into the options context you need to act on it: the
tradeable monthly expiry and DTE, ATM implied volatility (solved from the NSE
derivatives bhavcopy settle prices via Black-Scholes), an IV-rank / HV-rank
read, the option-implied expected move, ATM liquidity (OI + volume), and a
suggested structure.

Indian stock options are European, so plain Black-Scholes applies. Dividends are
ignored (small, and settle-price IV already reflects them approximately).
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd


@dataclass
class OptionsConfig:
    rate: float = 0.065            # risk-free rate (India ~6.5%)
    min_dte: int = 25             # skip near-expiry; want >= this many days
    hv_window: int = 20           # realized-vol window (trading days)
    hv_lookback: int = 252        # percentile window for HV-rank
    iv_rich_rank: float = 70.0    # >= this => "IV rich", prefer spreads
    min_atm_oi: int = 200         # ATM open interest (contracts) for "liquid"
    min_atm_volume: int = 50      # ATM volume (contracts) for "liquid"
    delta_target: float = 0.65    # suggested slightly-ITM call delta
    iv_cache_dir: str = "cache/iv"


# --------------------------------------------------------------------------- #
# Black-Scholes
# --------------------------------------------------------------------------- #
def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_price(S: float, K: float, T: float, r: float, sigma: float, call: bool = True) -> float:
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return max(0.0, (S - K) if call else (K - S))
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if call:
        return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)
    return K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


def bs_delta(S: float, K: float, T: float, r: float, sigma: float, call: bool = True) -> float:
    if T <= 0 or sigma <= 0:
        return float(S > K) if call else -float(S < K)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    return _norm_cdf(d1) if call else _norm_cdf(d1) - 1.0


def implied_vol(price: float, S: float, K: float, T: float, r: float, call: bool = True) -> float:
    """Invert Black-Scholes for sigma via bisection (robust, monotone in sigma)."""
    if not (price and price > 0) or T <= 0 or S <= 0 or K <= 0:
        return float("nan")
    lo, hi = 1e-4, 5.0
    p_lo = bs_price(S, K, T, r, lo, call)
    p_hi = bs_price(S, K, T, r, hi, call)
    if price <= p_lo:
        return float("nan")     # at/below intrinsic (stale settle) -> unusable
    if price >= p_hi:
        return hi
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if bs_price(S, K, T, r, mid, call) > price:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------- #
# Realized volatility (HV) rank -- an immediately-available IV-rank proxy
# --------------------------------------------------------------------------- #
def hv_rank(df: pd.DataFrame, cfg: OptionsConfig):
    """Return ``(annualised_hv, hv_rank_0_100)`` from close-to-close returns."""
    close = df["Close"].dropna()
    if len(close) < cfg.hv_window + 5:
        return float("nan"), float("nan")
    rv = np.log(close).diff().rolling(cfg.hv_window).std() * math.sqrt(252)
    cur = rv.iloc[-1]
    hist = rv.iloc[-cfg.hv_lookback:].dropna()
    if not np.isfinite(cur) or len(hist) < 20:
        return float(cur) if np.isfinite(cur) else float("nan"), float("nan")
    rank = float((hist < cur).mean() * 100.0)
    return float(cur), rank


def iv_rank(current_iv: float, history: Optional[pd.Series]) -> float:
    if history is None or current_iv != current_iv or len(history.dropna()) < 20:
        return float("nan")
    h = history.dropna()
    return float((h < current_iv).mean() * 100.0)


# --------------------------------------------------------------------------- #
# ATM metrics from an option chain
# --------------------------------------------------------------------------- #
def option_metrics(chain: pd.DataFrame, spot: float, today: pd.Timestamp,
                   cfg: OptionsConfig) -> dict:
    """Compute the ATM options read for one underlying.

    ``chain`` is that symbol's STO rows with columns Expiry, Strike, OptType,
    Settle, OI, Volume.
    """
    out: dict = {"atm_iv": float("nan"), "dte": None, "expiry": None,
                 "atm_strike": None, "exp_move_pct": float("nan"),
                 "atm_oi": 0, "atm_vol": 0, "liquid": False, "sug_strike": None}
    if chain is None or chain.empty or not (spot and spot > 0):
        return out

    expiries = sorted(pd.to_datetime(chain["Expiry"]).dt.normalize().unique())
    pick = next((e for e in expiries if (e - today).days >= cfg.min_dte), None)
    if pick is None:
        pick = expiries[-1] if expiries else None
    if pick is None:
        return out
    dte = int((pick - today).days)
    T = max(dte, 1) / 365.0
    sub = chain[pd.to_datetime(chain["Expiry"]).dt.normalize() == pick]
    strikes = np.sort(sub["Strike"].dropna().unique())
    if len(strikes) == 0:
        return out
    atm = float(strikes[np.argmin(np.abs(strikes - spot))])

    ivs = []
    atm_oi = atm_vol = 0
    for is_call, typ in ((True, "CE"), (False, "PE")):
        row = sub[(sub["Strike"] == atm) & (sub["OptType"] == typ)]
        if row.empty:
            continue
        price = float(row["Settle"].iloc[0])
        iv = implied_vol(price, spot, atm, T, cfg.rate, is_call)
        if iv == iv:
            ivs.append(iv)
        atm_oi = max(atm_oi, int(row["OI"].iloc[0]))
        atm_vol = max(atm_vol, int(row["Volume"].iloc[0]))
    atm_iv = float(np.mean(ivs)) if ivs else float("nan")

    # A slightly-ITM call near the target delta, as a concrete strike to trade.
    sug_strike = None
    if atm_iv == atm_iv:
        ce = sub[sub["OptType"] == "CE"]
        best = None
        for k in np.sort(ce["Strike"].dropna().unique()):
            d = bs_delta(spot, float(k), T, cfg.rate, atm_iv, True)
            score = abs(d - cfg.delta_target)
            if best is None or score < best[0]:
                best = (score, float(k))
        sug_strike = best[1] if best else None

    out.update({
        "atm_iv": atm_iv, "dte": dte, "expiry": pick, "atm_strike": atm,
        "exp_move_pct": (atm_iv * math.sqrt(T)) if atm_iv == atm_iv else float("nan"),
        "atm_oi": atm_oi, "atm_vol": atm_vol,
        "liquid": bool(atm_oi >= cfg.min_atm_oi and atm_vol >= cfg.min_atm_volume),
        "sug_strike": sug_strike,
    })
    return out


def suggest_structure(m: dict, rank: float, cfg: OptionsConfig) -> str:
    if not m.get("liquid"):
        return "Options thin — trade the stock"
    exp = m.get("expiry")
    tag = f"{exp:%d-%b} ({m['dte']}d)" if exp is not None else ""
    strike = m.get("sug_strike")
    if rank == rank and rank >= cfg.iv_rich_rank:
        return f"Bull call debit spread, {tag} (IV rich)"
    if strike:
        return f"Buy ~{cfg.delta_target:.2f}Δ CE {strike:g}, {tag}"
    return f"Buy slightly-ITM CE, {tag}"


# --------------------------------------------------------------------------- #
# IV history cache (accumulates so IV-rank becomes available over time)
# --------------------------------------------------------------------------- #
def load_iv_history(symbol: str, cfg: OptionsConfig) -> Optional[pd.Series]:
    path = os.path.join(cfg.iv_cache_dir, f"{symbol}.csv")
    if not os.path.exists(path):
        return None
    try:
        s = pd.read_csv(path, index_col=0)["atm_iv"]
        return pd.to_numeric(s, errors="coerce")
    except Exception:
        return None


def append_iv(symbol: str, day: pd.Timestamp, atm_iv: float, cfg: OptionsConfig) -> None:
    if atm_iv != atm_iv:
        return
    os.makedirs(cfg.iv_cache_dir, exist_ok=True)
    path = os.path.join(cfg.iv_cache_dir, f"{symbol}.csv")
    key = pd.Timestamp(day).strftime("%Y-%m-%d")
    hist = {}
    if os.path.exists(path):
        try:
            hist = pd.read_csv(path, index_col=0)["atm_iv"].to_dict()
        except Exception:
            hist = {}
    hist[key] = round(float(atm_iv), 4)
    pd.Series(hist, name="atm_iv").sort_index().to_csv(path, header=True)


# --------------------------------------------------------------------------- #
# Enrichment over a set of screener results
# --------------------------------------------------------------------------- #
def enrich(results, fo_df: pd.DataFrame, data: Dict[str, pd.DataFrame],
           day: pd.Timestamp, cfg: Optional[OptionsConfig] = None) -> Dict[str, dict]:
    """Return ``{symbol: metrics}`` for every result that has option data."""
    cfg = cfg or OptionsConfig()
    today = pd.Timestamp(day).normalize()
    by_symbol = {sym: g for sym, g in fo_df.groupby("Symbol")} if fo_df is not None else {}

    out: Dict[str, dict] = {}
    for r in results:
        if r.error:
            continue
        chain = by_symbol.get(r.symbol)
        df = data.get(r.symbol)
        spot = float(df["Close"].iloc[-1]) if df is not None and len(df) else r.price
        m = option_metrics(chain, spot, today, cfg)

        hv, hvr = hv_rank(df, cfg) if df is not None else (float("nan"), float("nan"))
        ivr = iv_rank(m["atm_iv"], load_iv_history(r.symbol, cfg))
        rank = ivr if ivr == ivr else hvr          # prefer IV-rank, fall back to HV-rank
        m["hv"], m["hv_rank"], m["iv_rank"], m["rank"], m["rank_kind"] = (
            hv, hvr, ivr, rank, "IV" if ivr == ivr else "HV")
        m["suggestion"] = suggest_structure(m, rank, cfg)
        append_iv(r.symbol, today, m["atm_iv"], cfg)
        out[r.symbol] = m
    return out


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def to_frame(results, metrics: Dict[str, dict], config) -> pd.DataFrame:
    rows = []
    for r in results:
        m = metrics.get(r.symbol)
        if r.error or m is None:
            continue
        rows.append({
            "Symbol": r.symbol,
            "FULL_SETUP": r.full_setup(config),
            "Passed": r.passed_count(config),
            "Price": round(r.price, 2),
            "RS_Rating": r.rs_rating,
            "Expiry": m["expiry"].strftime("%Y-%m-%d") if m["expiry"] is not None else "",
            "DTE": m["dte"],
            "ATM_Strike": m["atm_strike"],
            "ATM_IV_pct": round(m["atm_iv"] * 100, 1) if m["atm_iv"] == m["atm_iv"] else None,
            "Rank": round(m["rank"], 0) if m["rank"] == m["rank"] else None,
            "Rank_kind": m["rank_kind"],
            "ExpMove_pct": round(m["exp_move_pct"] * 100, 1) if m["exp_move_pct"] == m["exp_move_pct"] else None,
            "ATM_OI": m["atm_oi"],
            "ATM_Vol": m["atm_vol"],
            "Liquid": m["liquid"],
            "Sug_Strike": m["sug_strike"],
            "Suggestion": m["suggestion"],
        })
    return pd.DataFrame(rows)


def write_html(results, metrics: Dict[str, dict], config, path: str,
               as_of=None, top: int = 60) -> None:
    import html as _html

    df = to_frame(results, metrics, config)
    if df.empty:
        return
    df = df.sort_values(["FULL_SETUP", "Passed", "RS_Rating"], ascending=False).head(top)

    def cell(v, suffix=""):
        return "-" if v is None or (isinstance(v, float) and v != v) else f"{v}{suffix}"

    rows = []
    for _, r in df.iterrows():
        liq = ('<span class="badge y">liquid</span>' if r["Liquid"]
               else '<span class="badge n">thin</span>')
        setup = ('<b class="full">FULL</b>' if r["FULL_SETUP"] else f'{int(r["Passed"])}/14')
        rows.append(
            f"<tr><td class='sym'>{_html.escape(str(r['Symbol']))}</td>"
            f"<td>{setup}</td><td>{cell(r['Price'])}</td><td>{cell(r['RS_Rating'])}</td>"
            f"<td>{cell(r['ATM_IV_pct'],'%')}</td>"
            f"<td>{cell(r['Rank'])}{'' if r['Rank'] is None or r['Rank']!=r['Rank'] else ' '+str(r['Rank_kind'])}</td>"
            f"<td>{cell(r['ExpMove_pct'],'%')}</td><td>{cell(r['DTE'],'d')}</td>"
            f"<td>{cell(r['ATM_Strike'])}</td><td>{liq}</td>"
            f"<td class='sug'>{_html.escape(str(r['Suggestion']))}</td></tr>"
        )
    stamp = as_of if as_of is not None else ""
    doc = _OPT_TEMPLATE.format(as_of=_html.escape(str(stamp)), rows="\n".join(rows))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)


_OPT_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>VCP Options Ideas</title>
<style>:root{{--bg:#f6f7f9;--card:#fff;--ink:#1f2430;--muted:#6b7280;--line:#e5e7eb;--full:#2e7d32;}}
@media(prefers-color-scheme:dark){{:root{{--bg:#12151c;--card:#1a1f2b;--ink:#e6e9ef;--muted:#9aa4b2;--line:#2a3140;}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);
font:13px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:22px 16px 60px}}h1{{font-size:20px;margin:0 0 2px}}
.sub{{color:var(--muted);margin:0 0 16px}}.tablewrap{{overflow-x:auto;border:1px solid var(--line);
border-radius:12px;background:var(--card)}}table{{border-collapse:collapse;width:100%;min-width:820px}}
th,td{{padding:7px 9px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap;
font-variant-numeric:tabular-nums}}th{{color:var(--muted);font-weight:600;font-size:11px;text-transform:uppercase}}
td.sym,th.sym,td.sug,th.sug{{text-align:left}}td.sym{{font-weight:600}}td.sug{{white-space:normal;color:var(--muted)}}
b.full{{color:var(--full)}}.badge{{padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600}}
.badge.y{{background:rgba(76,175,80,.15);color:#4caf50}}.badge.n{{background:rgba(224,86,86,.15);color:#e05656}}
.foot{{color:var(--muted);font-size:12px;margin-top:18px}}</style></head><body><div class="wrap">
<h1>VCP Options Ideas</h1>
<p class="sub">Options context for each stock setup &middot; NSE F&amp;O &middot; data as of {as_of}</p>
<div class="tablewrap"><table><thead><tr>
<th class="sym">Symbol</th><th>Setup</th><th>Price</th><th>RS</th><th>ATM IV</th><th>Vol rank</th>
<th>Exp move</th><th>DTE</th><th>ATM strike</th><th>Liquidity</th><th class="sug">Suggested structure</th>
</tr></thead><tbody>{rows}</tbody></table></div>
<p class="foot">ATM IV solved via Black-Scholes from NSE settle prices. "Vol rank" is IV-rank once history
accrues, else HV-rank (realized). Expected move is 1&sigma; to the shown expiry. Educational only, not
investment advice; verify the live option chain and spreads before trading.</p>
</div></body></html>"""


def print_table(results, metrics: Dict[str, dict], config, top: int = 15) -> None:
    ranked = [r for r in results if not r.error and r.symbol in metrics]
    ranked.sort(key=lambda r: (r.full_setup(config), r.passed_count(config),
                               r.rs_rating or -1), reverse=True)
    print("\n" + "=" * 98)
    print("OPTIONS IDEAS (top candidates)")
    print("=" * 98)
    print(f"  {'Symbol':<12}{'Setup':>6}{'IV%':>6}{'Rank':>7}{'ExpMv%':>8}{'DTE':>5}{'Liq':>5}   Suggestion")
    print("  " + "-" * 94)
    for r in ranked[:top]:
        m = metrics[r.symbol]
        setup = "FULL" if r.full_setup(config) else f"{r.passed_count(config)}/14"
        iv = f"{m['atm_iv']*100:.0f}" if m["atm_iv"] == m["atm_iv"] else "-"
        rk = f"{m['rank']:.0f}{m['rank_kind']}" if m["rank"] == m["rank"] else "-"
        em = f"{m['exp_move_pct']*100:.1f}" if m["exp_move_pct"] == m["exp_move_pct"] else "-"
        dte = m["dte"] if m["dte"] is not None else "-"
        liq = "Y" if m["liquid"] else "n"
        print(f"  {r.symbol:<12}{setup:>6}{iv:>6}{rk:>7}{em:>8}{str(dte):>5}{liq:>5}   {m['suggestion']}")
    print("=" * 98)
