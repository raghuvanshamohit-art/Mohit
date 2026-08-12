"""Unit tests for the indicator helpers (all offline, deterministic)."""

import numpy as np
import pandas as pd

from vcp_screener import indicators as ind


def test_sma_basic():
    s = pd.Series([1, 2, 3, 4, 5], dtype=float)
    out = ind.sma(s, 2)
    assert np.isnan(out.iloc[0])
    assert out.iloc[1] == 1.5
    assert out.iloc[-1] == 4.5


def test_is_rising():
    assert ind.is_rising(pd.Series([1, 2, 3, 4, 5], dtype=float), 2) is True
    assert ind.is_rising(pd.Series([5, 4, 3, 2, 1], dtype=float), 2) is False
    # Not enough data for the lookback -> False, never an exception.
    assert ind.is_rising(pd.Series([1, 2], dtype=float), 5) is False


def test_period_return():
    s = pd.Series([100, 110, 121], dtype=float)
    assert abs(ind.period_return(s, 2) - 0.21) < 1e-9
    assert np.isnan(ind.period_return(pd.Series([1.0]), 3))


def test_chain_gt():
    assert ind.chain_gt(3, 2, 1) is True
    assert ind.chain_gt(3, 3, 1) is False       # not strict
    assert ind.chain_gt(1, 2, 3) is False
    assert ind.chain_gt(3, float("nan"), 1) is False


def test_contracting():
    # recent window (last 3) lower than the prior window (3 before) -> True
    s = pd.Series([10, 10, 10, 2, 2, 2], dtype=float)
    assert ind.contracting(s, recent=3, prior=3) is True
    # rising -> not contracting
    s2 = pd.Series([2, 2, 2, 10, 10, 10], dtype=float)
    assert ind.contracting(s2, recent=3, prior=3) is False
    # insufficient data -> False
    assert ind.contracting(pd.Series([1, 2, 3], dtype=float), 3, 3) is False


def test_atr_positive():
    n = 30
    high = pd.Series(np.linspace(10, 12, n))
    low = pd.Series(np.linspace(9, 11, n))
    close = pd.Series(np.linspace(9.5, 11.5, n))
    a = ind.atr(high, low, close, period=14).dropna()
    assert (a > 0).all()


def test_to_weekly():
    dates = pd.bdate_range("2023-01-02", periods=20)
    df = pd.DataFrame(
        {"Open": 1.0, "High": 2.0, "Low": 0.5, "Close": 1.5, "Volume": 100.0},
        index=dates,
    )
    w = ind.to_weekly(df)
    assert list(w.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert (w["Volume"] >= 100).all()   # weekly volume is a sum of daily
