"""Offline tests for the backtest engine: stop/exit mechanics, the no-look-ahead
guarantee, and end-to-end orchestration on synthetic data."""

import numpy as np
import pandas as pd

from vcp_screener.backtest import (
    BacktestConfig,
    run_backtest,
    simulate_stock,
    stock_criteria,
    summarize,
)
from vcp_screener.config import Config


def _df(close, open_=None, high=None, low=None, vol=None, start="2021-01-01"):
    n = len(close)
    close = np.asarray(close, float)
    idx = pd.bdate_range(start=start, periods=n)
    return pd.DataFrame({
        "Open": close if open_ is None else np.asarray(open_, float),
        "High": close if high is None else np.asarray(high, float),
        "Low": close if low is None else np.asarray(low, float),
        "Close": close,
        "Volume": np.full(n, 1_000_000.0) if vol is None else np.asarray(vol, float),
    }, index=idx)


def test_stop_exit():
    # Flat at 100, signal fires at bar 5 (entry next open = 100), then bar 8 dips
    # to a low of 90 -> hard stop at 92 (8% below entry).
    close = [100.0] * 30
    low = list(close)
    low[8] = 90.0
    df = _df(close, low=low)
    sig = pd.Series(False, index=df.index)
    sig.iloc[5] = True
    trades = simulate_stock("X", df, sig,
                            BacktestConfig(use_trail_ma=False, stop_pct=0.08, cost_pct=0.0))
    assert len(trades) == 1
    t = trades[0]
    assert t["reason"] == "stop"
    assert abs(t["exit"] - 92.0) < 1e-6
    assert abs(t["ret"] - (-0.08)) < 1e-6


def test_time_exit():
    close = list(np.linspace(100, 110, 30))     # gentle uptrend, no stop hit
    df = _df(close)
    sig = pd.Series(False, index=df.index)
    sig.iloc[5] = True
    trades = simulate_stock("X", df, sig,
                            BacktestConfig(use_trail_ma=False, stop_pct=0.5,
                                           max_hold=3, cost_pct=0.0))
    assert len(trades) == 1
    assert trades[0]["reason"] == "time"
    assert trades[0]["bars"] == 3


def test_gap_through_stop_fills_at_open():
    close = [100.0] * 20
    open_ = list(close)
    open_[8] = 85.0                              # gaps below the 92 stop
    low = list(close)
    low[8] = 84.0
    df = _df(close, open_=open_, low=low)
    sig = pd.Series(False, index=df.index)
    sig.iloc[5] = True
    trades = simulate_stock("X", df, sig,
                            BacktestConfig(use_trail_ma=False, stop_pct=0.08, cost_pct=0.0))
    assert trades[0]["reason"] == "stop"
    assert abs(trades[0]["exit"] - 85.0) < 1e-6  # filled at the gapped-down open


def test_big_candle_exit():
    # Flat at 100 (small ranges -> small ATR), signal at bar 20, then a big green
    # candle at bar 25 (range ~33 >> 3xATR) -> take profit at its close.
    n = 40
    close = np.full(n, 100.0)
    high = close + 0.5
    low = close - 0.5
    open_ = close.copy()
    j = 25
    open_[j], low[j], high[j], close[j] = 100.0, 99.5, 132.0, 130.0
    df = _df(close, open_=open_, high=high, low=low)
    sig = pd.Series(False, index=df.index)
    sig.iloc[20] = True
    trades = simulate_stock("X", df, sig,
                            BacktestConfig(exit_mode="big_candle", big_candle_atr_mult=3.0,
                                           stop_pct=0.5, cost_pct=0.0))
    assert len(trades) == 1
    assert trades[0]["reason"] == "big_candle"
    assert abs(trades[0]["exit"] - 130.0) < 1e-6


def test_no_lookahead():
    # Criteria computed on the full series must match those computed on a
    # truncated (past-only) series, for every overlapping date.
    rng = np.random.default_rng(0)
    n = 500
    close = 100 * np.exp(np.cumsum(rng.normal(0.0006, 0.015, n)))
    df = _df(close, high=close * 1.01, low=close * 0.99)
    nifty = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0004, 0.01, n))), index=df.index)
    cfg = Config()

    full, _ = stock_criteria(df, nifty, cfg)
    k = 380
    trunc, _ = stock_criteria(df.iloc[:k], nifty.iloc[:k], cfg)

    a = full.iloc[:k].reset_index(drop=True)
    b = trunc.reset_index(drop=True)
    assert a.equals(b), "criteria changed when future bars were added -> look-ahead!"


def test_run_backtest_end_to_end():
    cfg = Config()
    n = 420
    up = 100 * np.exp(np.linspace(0, 0.9, n))
    data = {
        "AAA": _df(up, high=up * 1.02, low=up * 0.98),
        "BBB": _df(up[::-1].copy(), high=up[::-1] * 1.02, low=up[::-1] * 0.98),
    }
    nifty = _df(100 * np.exp(np.linspace(0, 0.3, n)))
    res = run_backtest(data, nifty, cfg,
                       BacktestConfig(apply_market_filter=True, max_positions=5))
    assert isinstance(res["trades"], list)
    assert "summary" in res and "equity" in res
    assert res["universe"] >= 1


def test_summarize_math():
    trades = [{"ret": 0.10, "bars": 5}, {"ret": -0.05, "bars": 3}, {"ret": 0.20, "bars": 8}]
    s = summarize(trades)
    assert s["n"] == 3
    assert abs(s["win_rate"] - 2 / 3) < 1e-9
    assert abs(s["profit_factor"] - (0.30 / 0.05)) < 1e-9
    assert abs(s["avg"] - (0.25 / 3)) < 1e-9
