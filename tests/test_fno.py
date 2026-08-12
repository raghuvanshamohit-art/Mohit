"""Tests for F&O sizing: futures lots, defined-risk spread, and the verdict."""

import numpy as np
import pandas as pd

from vcp_screener.fno import (
    FnoConfig,
    build_row,
    bull_call_spread,
    futures_sizing,
    lot_size,
)
from vcp_screener.options import bs_price
from vcp_screener.practice import PracticeConfig, build_plan
from vcp_screener.vcp import VCPResult


def test_lot_size():
    chain = pd.DataFrame({"Lot": [75, 75, 75, 75]})
    assert lot_size(chain) == 75
    assert lot_size(pd.DataFrame()) is None


def test_futures_sizing_too_big():
    # pivot 11856, risk/share 948 (8% stop), lot 75 -> risk/lot ~71,100.
    f = futures_sizing(11856.0, 948.48, 75, 500_000, 0.0125, FnoConfig())
    assert f["lots"] == 0                       # can't take even one lot at 1.25%
    assert f["cap_for_1lot"] > 5_000_000        # would need >50L for one lot


def test_futures_sizing_affordable():
    # tight 2% stop on a cheaper stock -> a lot fits the risk budget.
    f = futures_sizing(500.0, 10.0, 1000, 5_000_000, 0.0125, FnoConfig())
    assert f["risk_per_lot"] == 10_000.0
    assert f["lots"] == int(62_500 // 10_000)   # budget 62,500 / 10,000


def _ce_chain(spot, iv=0.30):
    today = pd.Timestamp("2026-01-01")
    exp = today + pd.Timedelta(days=35)
    T = 35 / 365
    rows = []
    for k in range(int(spot * 0.9), int(spot * 1.2), 20):
        rows.append({"Symbol": "X", "Expiry": exp, "Strike": float(k), "OptType": "CE",
                     "Settle": bs_price(spot, k, T, 0.065, iv, True), "Lot": 50})
    return today, pd.DataFrame(rows)


def test_bull_call_spread_defined_risk():
    today, chain = _ce_chain(1000)
    s = bull_call_spread(chain, pivot=1000.0, lot=50, budget=100_000, today=today,
                         cfg=FnoConfig(spread_width=0.10))
    assert s is not None
    assert s["short"] > s["long"]                     # a real spread
    assert 0 < s["cost_ps"]                           # net debit
    assert s["max_loss"] > 0 and s["max_profit"] > 0
    assert s["spreads"] == int(100_000 // s["max_loss"])


def test_verdict_wide_stop_is_cash_only():
    v = VCPResult(pivot=11856.0, pivot_low=9501.0, status="at pivot")
    plan = build_plan("BAJAJ-AUTO", 11717.0, v, PracticeConfig(account=500_000, max_stop=0.08))
    chain = pd.DataFrame({"Symbol": ["BAJAJ-AUTO"], "Expiry": [pd.Timestamp("2026-02-24")],
                          "Strike": [11800.0], "OptType": ["CE"], "Settle": [300.0], "Lot": [75]})
    row = build_row(plan, chain, pd.Timestamp("2026-01-20"), 500_000, 0.0125, liquid=True)
    assert "CASH only" in row["Verdict"]              # 8% stop -> don't leverage
    assert "0 lots" in row["Futures_@risk"]
