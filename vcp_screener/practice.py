"""Practice mode — turn each VCP setup into a Minervini trade plan you can
paper-trade, and a journal to log the reps.

For every stock that passes the trend template and is forming a VCP near its
pivot, it builds the full plan the book prescribes: buy the **pivot** on a
volume breakout, an initial **stop** at the danger point (capped at the max %),
a **position size** that risks a fixed fraction of equity, a **2:1 target** and
a **sell-into-strength** target, and the **breakeven** trigger. Then it writes a
board + a blank journal so you can practice executing the rules.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pandas as pd

from .vcp import VCPConfig, VCPResult, detect_vcp


@dataclass
class PracticeConfig:
    account: float = 100_000.0    # your capital (₹ by default)
    risk_pct: float = 0.0125      # risk 1.25% of equity per trade (Minervini 1.25–2.5%)
    max_stop: float = 0.08        # cap the initial stop at 8% below the pivot
    max_position_pct: float = 0.25  # concentration cap per name (top-name 20–25%)
    rr: float = 2.0               # minimum reward:risk target
    strength_gain: float = 0.20   # sell-into-strength: bank profit around +20%
    breakeven_R: float = 2.0      # move stop to breakeven after +2R


@dataclass
class TradePlan:
    symbol: str
    price: float
    pivot: float
    stop: float
    stop_pct: float
    risk_ps: float
    shares: int
    position_value: float
    position_pct: float
    capped: bool
    risk_amount: float
    rr_target: float
    strength_target: float
    breakeven_at: float
    status: str
    n_contractions: int
    last_depth: float
    dist_to_pivot: float


def build_plan(symbol: str, price: float, v: VCPResult, cfg: PracticeConfig) -> TradePlan:
    pivot = v.pivot
    danger = v.pivot_low if v.pivot_low == v.pivot_low else pivot * (1 - cfg.max_stop)
    # Stop at the danger point, but never risk more than max_stop below the pivot.
    stop = max(danger, pivot * (1 - cfg.max_stop))
    risk_ps = max(pivot - stop, 1e-9)
    stop_pct = risk_ps / pivot

    risk_amount = cfg.account * cfg.risk_pct
    shares = int(risk_amount // risk_ps)
    position_value = shares * pivot
    capped = False
    if position_value > cfg.max_position_pct * cfg.account:      # concentration cap
        shares = int((cfg.max_position_pct * cfg.account) // pivot)
        position_value = shares * pivot
        capped = True

    return TradePlan(
        symbol=symbol, price=round(price, 2), pivot=round(pivot, 2),
        stop=round(stop, 2), stop_pct=stop_pct, risk_ps=round(risk_ps, 2),
        shares=shares, position_value=round(position_value, 0),
        position_pct=position_value / cfg.account if cfg.account else 0.0,
        capped=capped, risk_amount=round(risk_amount, 0),
        rr_target=round(pivot + cfg.rr * risk_ps, 2),
        strength_target=round(pivot * (1 + cfg.strength_gain), 2),
        breakeven_at=round(pivot + cfg.breakeven_R * risk_ps, 2),
        status=v.status, n_contractions=v.n_contractions,
        last_depth=v.last_depth, dist_to_pivot=v.dist_to_pivot,
    )


def select_setups(results, data, screen_cfg, min_passed: int = 12,
                  vcp_cfg: Optional[VCPConfig] = None) -> List[Tuple[object, VCPResult]]:
    """Stocks that pass the trend template strongly and are forming a VCP at/near
    the pivot (or breaking out). Ranked by RS."""
    vcp_cfg = vcp_cfg or VCPConfig()
    out = []
    for r in results:
        if r.error or r.passed_count(screen_cfg) < min_passed:
            continue
        df = data.get(r.symbol)
        if df is None:
            continue
        v = detect_vcp(df, vcp_cfg)
        if v.status in ("at pivot", "breakout", "breakout (weak vol)") or v.is_vcp:
            out.append((r, v))
    out.sort(key=lambda rv: (rv[1].status == "breakout", rv[0].rs_rating or -1), reverse=True)
    return out


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def plans_frame(setups, cfg: PracticeConfig) -> pd.DataFrame:
    rows = []
    for r, v in setups:
        p = build_plan(r.symbol, r.price, v, cfg)
        rows.append({
            "Symbol": p.symbol, "Status": p.status, "RS": r.rs_rating,
            "Contractions": p.n_contractions, "LastT_pct": round(p.last_depth * 100, 1),
            "Price": p.price, "Pivot": p.pivot, "ToPivot_pct": round(p.dist_to_pivot * 100, 1),
            "Stop": p.stop, "Stop_pct": round(p.stop_pct * 100, 1), "Risk/sh": p.risk_ps,
            "Shares": p.shares, "Position": p.position_value,
            "Position_pct": round(p.position_pct * 100, 1), "Capped": p.capped,
            "Target_2R": p.rr_target, "SellStrength": p.strength_target,
            "MoveBE_at": p.breakeven_at,
        })
    return pd.DataFrame(rows)


def print_board(setups, cfg: PracticeConfig, top: int = 15) -> None:
    print("\n" + "=" * 100)
    print(f"VCP PRACTICE BOARD   (account ₹{cfg.account:,.0f} · risk {cfg.risk_pct*100:.2f}%/trade "
          f"· stop cap {cfg.max_stop*100:.0f}%)")
    print("=" * 100)
    if not setups:
        print("  No VCP setups at/near a pivot right now.")
        print("=" * 100)
        return
    print(f"  {'Symbol':<12}{'Status':<11}{'RS':>4}{'Ts':>3}{'lastT':>7}"
          f"{'Pivot':>10}{'Stop':>9}{'stop%':>6}{'Shares':>8}{'Pos%':>6}   Plan")
    print("  " + "-" * 96)
    for r, v in setups[:top]:
        p = build_plan(r.symbol, r.price, v, cfg)
        plan = f"buy>{p.pivot:g} · stop {p.stop:g} · sell-strength {p.strength_target:g} · BE@{p.breakeven_at:g}"
        rs = f"{r.rs_rating:.0f}" if r.rs_rating is not None else "-"
        print(f"  {p.symbol:<12}{p.status:<11}{rs:>4}{p.n_contractions:>3}"
              f"{p.last_depth*100:>6.1f}%{p.pivot:>10.1f}{p.stop:>9.1f}{p.stop_pct*100:>5.1f}%"
              f"{p.shares:>8}{p.position_pct*100:>5.1f}%   {plan}")
    print("=" * 100)
    print("  Rules: buy only on a breakout ABOVE the pivot with volume; if it stops you out, that's")
    print("  the cost of business. Move stop to breakeven at the BE price, then trail the 50-DMA.")
    print("=" * 100)


def write_journal_template(path: str) -> None:
    cols = ["Date", "Symbol", "Setup(status)", "Pivot/Entry", "Stop", "Stop_%",
            "Shares", "Risk_₹", "R:R_plan", "Exit_Date", "Exit_Price",
            "R_multiple", "Exit_reason", "Followed_rules(Y/N)", "Notes"]
    if not _exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False)


def _exists(path: str) -> bool:
    import os
    return os.path.exists(path)


def write_html(setups, cfg: PracticeConfig, path: str, as_of=None) -> None:
    import html as _h

    df = plans_frame(setups, cfg)
    rows = ""
    for _, r in df.iterrows():
        badge = {
            "breakout": '<span class="b go">breakout</span>',
            "breakout (weak vol)": '<span class="b warn">breakout·low vol</span>',
            "at pivot": '<span class="b warn">at pivot</span>',
            "in base": '<span class="b mut">in base</span>',
        }.get(r["Status"], f'<span class="b mut">{_h.escape(str(r["Status"]))}</span>')
        rows += (
            f"<tr><td class='sym'>{_h.escape(r['Symbol'])}</td><td>{badge}</td>"
            f"<td>{r['RS']}</td><td>{r['Contractions']} · {r['LastT_pct']}%</td>"
            f"<td>{r['Price']:g}</td><td>{r['Pivot']:g}</td>"
            f"<td>{r['Stop']:g} <span class='mut'>({r['Stop_pct']}%)</span></td>"
            f"<td>{r['Shares']:g}</td><td>{r['Position_pct']}%</td>"
            f"<td>{r['SellStrength']:g}</td><td>{r['MoveBE_at']:g}</td></tr>"
        )
    doc = _PRACTICE_TMPL.format(
        as_of=_h.escape(str(as_of or "")), acct=f"{cfg.account:,.0f}",
        risk=f"{cfg.risk_pct*100:.2f}", cap=f"{cfg.max_stop*100:.0f}", rows=rows or
        '<tr><td colspan="11" class="mut">No VCP setups at/near a pivot right now.</td></tr>')
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)


_PRACTICE_TMPL = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>VCP Practice Board</title>
<style>:root{{--bg:#eef1f5;--card:#fff;--ink:#0f1620;--mut:#5a6472;--line:#e2e7ee;--acc:#2f5fa6;
--go:#15a34a;--warn:#b9791a;}}@media(prefers-color-scheme:dark){{:root:not([data-theme=light]){{
--bg:#0d1117;--card:#151b24;--ink:#e7edf5;--mut:#8b97a7;--line:#232c39;--acc:#5f97d6;--go:#2fbf6b;--warn:#e0a53a;}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);
font:13px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
.wrap{{max-width:1000px;margin:0 auto;padding:22px 16px 60px}}h1{{font-size:20px;margin:0 0 2px}}
.sub{{color:var(--mut);margin:0 0 16px}}.mut{{color:var(--mut)}}
.tw{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--card)}}
table{{border-collapse:collapse;width:100%;min-width:820px;font-variant-numeric:tabular-nums}}
th,td{{padding:7px 9px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}}
th{{color:var(--mut);font-size:11px;text-transform:uppercase;font-weight:600}}
td.sym,th.sym{{text-align:left;font-weight:700;font-family:ui-monospace,Menlo,monospace}}
.b{{padding:2px 8px;border-radius:99px;font-size:11px;font-weight:600}}
.b.go{{background:rgba(21,163,74,.15);color:var(--go)}}.b.warn{{background:rgba(185,121,26,.16);color:var(--warn)}}
.b.mut{{background:rgba(127,127,127,.14);color:var(--mut)}}
.foot{{color:var(--mut);font-size:12px;margin-top:18px;line-height:1.6}}</style></head><body><div class="wrap">
<h1>VCP Practice Board</h1>
<p class="sub">Trade plans for setups at/near their pivot &middot; account ₹{acct} &middot; risk {risk}%/trade &middot;
stop cap {cap}% &middot; data as of {as_of}</p>
<div class="tw"><table><thead><tr><th class="sym">Symbol</th><th>Status</th><th>RS</th>
<th>Contr · lastT</th><th>Price</th><th>Pivot (buy&gt;)</th><th>Stop</th><th>Shares</th><th>Pos%</th>
<th>Sell-strength</th><th>Move BE @</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="foot"><b>How to practice:</b> wait for price to break <b>above the pivot on a volume surge</b>, then
buy; set the stop; if hit, log it and move on (losses are the cost of business). Bank some into strength near
the sell-strength level, move the stop to breakeven at "Move BE @", then trail the 50-DMA. Log every rep in the
journal CSV. Educational only, not investment advice.</p></div></body></html>"""
