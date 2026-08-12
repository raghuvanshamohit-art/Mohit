"""F&O suitability & sizing — should you take this setup in futures/options, and
how much?

The VCP plan gives an entry (pivot) and a stop (risk per share). Leverage turns
that stop into real money fast, so this module answers, in plain English, per
stock:

* **Futures** — how many lots you can take while risking only ``risk_pct`` of
  equity (often **0**, i.e. the lot is too big → skip), and the margin needed.
* **Options** — a **defined-risk bull-call debit spread** whose *max loss is the
  premium*, sized to the same risk budget (no wide stop needed).
* A **verdict**: CASH only (stop too wide to lever), or F&O-OK with the numbers.

Lot size and option prices come from the NSE F&O bhavcopy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd


@dataclass
class FnoConfig:
    margin_pct: float = 0.20        # approx futures margin (span+exposure), illustrative
    max_fo_stop_pct: float = 0.05   # lever only when the stop is <= 5%
    min_dte: int = 25               # skip near expiry for the spread
    spread_width: float = 0.10      # short leg ~10% above the long leg (toward target)


def lot_size(chain: pd.DataFrame) -> Optional[int]:
    if chain is None or chain.empty or "Lot" not in chain.columns:
        return None
    vals = pd.to_numeric(chain["Lot"], errors="coerce").dropna()
    return int(vals.mode().iloc[0]) if len(vals) else None


def futures_sizing(pivot: float, risk_ps: float, lot: int, account: float,
                   risk_pct: float, cfg: FnoConfig) -> dict:
    notional = pivot * lot
    margin = notional * cfg.margin_pct
    risk_per_lot = risk_ps * lot
    budget = account * risk_pct
    lots = int(budget // risk_per_lot) if risk_per_lot > 0 else 0
    # Capital that one properly-risked lot would require.
    cap_for_1lot = risk_per_lot / risk_pct if risk_pct else float("inf")
    return {"lot": lot, "notional": notional, "margin": margin,
            "risk_per_lot": risk_per_lot, "lots": lots, "cap_for_1lot": cap_for_1lot}


def bull_call_spread(chain: pd.DataFrame, pivot: float, lot: int, budget: float,
                     today: pd.Timestamp, cfg: FnoConfig) -> Optional[dict]:
    if chain is None or chain.empty:
        return None
    exps = sorted(pd.to_datetime(chain["Expiry"]).dt.normalize().unique())
    pick = next((e for e in exps if (e - today).days >= cfg.min_dte), exps[-1] if exps else None)
    if pick is None:
        return None
    ce = chain[(pd.to_datetime(chain["Expiry"]).dt.normalize() == pick) & (chain["OptType"] == "CE")]
    strikes = np.sort(ce["Strike"].dropna().unique())
    if len(strikes) < 2:
        return None
    long_k = float(strikes[np.argmin(np.abs(strikes - pivot))])                 # ~ATM
    short_k = float(strikes[np.argmin(np.abs(strikes - pivot * (1 + cfg.spread_width)))])
    if short_k <= long_k:                                                       # need width
        higher = strikes[strikes > long_k]
        if not len(higher):
            return None
        short_k = float(higher[0])

    def prem(k):
        row = ce[ce["Strike"] == k]
        return float(row["Settle"].iloc[0]) if len(row) else float("nan")

    lp, sp = prem(long_k), prem(short_k)
    if not (np.isfinite(lp) and np.isfinite(sp)) or lp <= sp:
        return None
    cost_ps = lp - sp                                     # net debit per share
    max_loss = cost_ps * lot                              # per spread (= your risk)
    max_profit = (short_k - long_k - cost_ps) * lot
    spreads = int(budget // max_loss) if max_loss > 0 else 0
    return {"expiry": pick, "dte": int((pick - today).days), "long": long_k, "short": short_k,
            "cost_ps": cost_ps, "max_loss": max_loss, "max_profit": max_profit,
            "spreads": spreads, "rr": (max_profit / max_loss) if max_loss > 0 else float("nan")}


def build_row(plan, chain: pd.DataFrame, today: pd.Timestamp, account: float,
              risk_pct: float, liquid: bool, cfg: Optional[FnoConfig] = None) -> dict:
    """Return an F&O sizing row (with a plain-English verdict) for one plan."""
    cfg = cfg or FnoConfig()
    lot = lot_size(chain)
    budget = account * risk_pct
    fut = futures_sizing(plan.pivot, plan.risk_ps, lot, account, risk_pct, cfg) if lot else None
    spread = bull_call_spread(chain, plan.pivot, lot, budget, today, cfg) if lot else None

    # Plain-English verdict.
    if plan.stop_pct > cfg.max_fo_stop_pct:
        verdict = f"CASH only — {plan.stop_pct*100:.0f}% stop too wide to leverage"
    elif not liquid:
        verdict = "Cash/futures — options too thin"
    else:
        verdict = "F&O-OK"

    fut_txt = "-"
    if fut:
        if fut["lots"] >= 1:
            fut_txt = f"{fut['lots']} lot(s) · margin ₹{fut['margin']:,.0f}"
        else:
            fut_txt = f"0 lots — 1 lot needs ₹{fut['cap_for_1lot']:,.0f} at {risk_pct*100:.2f}% risk"

    opt_txt = "-"
    if spread and spread["spreads"] >= 1:
        opt_txt = (f"Buy {spread['long']:g}/Sell {spread['short']:g} CE {spread['expiry']:%d-%b}"
                   f" · risk ₹{spread['max_loss']:,.0f}/lot ×{spread['spreads']}"
                   f" · reward ₹{spread['max_profit']:,.0f} ({spread['rr']:.1f}:1)")
    elif spread:
        opt_txt = (f"Buy {spread['long']:g}/Sell {spread['short']:g} CE · risk ₹{spread['max_loss']:,.0f}/lot"
                   f" (> budget ₹{budget:,.0f})")

    return {"Symbol": plan.symbol, "Lot": lot, "Stop_pct": round(plan.stop_pct * 100, 1),
            "Verdict": verdict, "Futures_@risk": fut_txt, "Option_spread": opt_txt}


def print_board(rows, account: float, risk_pct: float) -> None:
    print("\n" + "=" * 108)
    print(f"F&O SIZING  (account ₹{account:,.0f} · risk {risk_pct*100:.2f}%/trade · futures margin ~20% illustrative)")
    print("=" * 108)
    if not rows:
        print("  No setups to size.")
        print("=" * 108)
        return
    for r in rows:
        print(f"  {r['Symbol']:<12} stop {r['Stop_pct']:>4}%  lot {str(r['Lot']):>5}  →  {r['Verdict']}")
        print(f"       Futures: {r['Futures_@risk']}")
        print(f"       Options: {r['Option_spread']}")
    print("=" * 108)
    print("  Rule of thumb: only leverage the tight setups (stop <= 5%). Prefer the debit spread —")
    print("  its max loss IS your risk, so an 8% wiggle can't wipe you. Margins are approximate.")
    print("=" * 108)


def to_frame(rows) -> pd.DataFrame:
    return pd.DataFrame(rows)
