"""Tests for VCP pivot/contraction detection and the practice trade plan."""

import numpy as np
import pandas as pd

from vcp_screener.practice import PracticeConfig, build_plan
from vcp_screener.vcp import VCPConfig, VCPResult, detect_vcp


def _interp(anchors, n):
    xs = np.array([a[0] for a in anchors], float)
    ys = np.array([a[1] for a in anchors], float)
    return np.interp(np.arange(n), xs, ys)


def _vcp_frame():
    """A base with three shrinking contractions (15% -> ~7% -> ~3.5%) and drying
    volume, ending just below the pivot (99)."""
    n = 120
    anchors = [(0, 50), (50, 100), (60, 85), (72, 98), (80, 91),
               (92, 99), (100, 95.5), (119, 98)]
    close = _interp(anchors, n)
    df = pd.DataFrame({
        "Open": close, "High": close * 1.004, "Low": close * 0.996,
        "Close": close, "Volume": np.linspace(1_500_000, 500_000, n),
    }, index=pd.bdate_range("2024-01-01", periods=n))
    return df


def test_detect_vcp_three_contractions():
    v = detect_vcp(_vcp_frame(), VCPConfig(swing_k=3, min_depth=0.03))
    assert v.n_contractions == 3
    # contractions shrink left -> right
    assert v.depths[0] > v.depths[1] > v.depths[2]
    assert v.depths[0] > 0.13 and v.depths[-1] < 0.06
    assert abs(v.pivot - 99) < 1.0            # pivot is the last swing high
    assert v.volume_dryup is True
    assert v.is_vcp is True
    assert v.status == "at pivot"             # close 98 is just below the 99 pivot


def test_no_vcp_on_downtrend():
    n = 120
    close = np.linspace(200, 100, n)          # steady decline, no base
    df = pd.DataFrame({
        "Open": close, "High": close * 1.01, "Low": close * 0.99,
        "Close": close, "Volume": np.full(n, 1e6),
    }, index=pd.bdate_range("2024-01-01", periods=n))
    v = detect_vcp(df, VCPConfig())
    assert v.is_vcp is False


def test_trade_plan_math():
    v = VCPResult(pivot=100.0, pivot_low=94.0, status="at pivot",
                  n_contractions=3, last_depth=0.035)
    cfg = PracticeConfig(account=100_000, risk_pct=0.0125, max_stop=0.08)
    p = build_plan("TEST", price=98.0, v=v, cfg=cfg)
    assert abs(p.stop - 94.0) < 1e-6          # danger point (within the 8% cap)
    assert abs(p.stop_pct - 0.06) < 1e-6
    assert abs(p.risk_ps - 6.0) < 1e-6
    assert p.shares == 208                    # floor(1250 / 6)
    assert abs(p.rr_target - 112.0) < 1e-6    # pivot + 2R
    assert p.capped is False


def test_trade_plan_stop_capped_at_max():
    # Danger point 30% below pivot -> stop capped at 8%.
    v = VCPResult(pivot=100.0, pivot_low=70.0, status="at pivot")
    cfg = PracticeConfig(account=100_000, risk_pct=0.0125, max_stop=0.08)
    p = build_plan("T", price=99.0, v=v, cfg=cfg)
    assert abs(p.stop - 92.0) < 1e-6          # 8% cap, not 70
    assert abs(p.stop_pct - 0.08) < 1e-6


def test_trade_plan_concentration_cap():
    # A very tight stop would size the position past the 25% cap.
    v = VCPResult(pivot=100.0, pivot_low=99.0, status="at pivot")
    cfg = PracticeConfig(account=100_000, risk_pct=0.0125, max_stop=0.08,
                         max_position_pct=0.25)
    p = build_plan("T", price=100.0, v=v, cfg=cfg)
    assert p.capped is True
    assert p.position_pct <= 0.2501
