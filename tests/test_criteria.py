"""Tests for the criteria engine and aggregation, using designed synthetic data
with known outcomes (fully offline, deterministic)."""

import numpy as np
import pandas as pd

from vcp_screener import indicators as ind
from vcp_screener.config import Config
from vcp_screener.constants import (
    C_ABOVE_LOW,
    C_MA_STACK,
    C_PRICE_ABOVE_MAS,
    C_RS_STRONG,
    C_VOLATILITY_CONTRACT,
    C_VOLUME_CONTRACT,
)
from vcp_screener.criteria import (
    MarketContext,
    evaluate_stock,
    relative_strength,
)


def _frame(close, band, volume, start="2020-01-01"):
    n = len(close)
    dates = pd.bdate_range(start=start, periods=n)
    close = np.asarray(close, dtype=float)
    band = np.asarray(band, dtype=float)
    high = close * (1 + band)
    low = close * (1 - band)
    open_ = np.concatenate([[close[0]], close[:-1]])
    return pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
        index=dates,
    )


def _ideal_stock(n=600):
    """Clean uptrend with a tight, low-volume contraction into the highs."""
    close = 100.0 * np.exp(np.linspace(0.0, 1.2, n))
    band = np.full(n, 0.04)
    band[-30:] = 0.005                    # volatility contracts at the pivot
    volume = np.full(n, 1_000_000.0)
    volume[-10:] = 400_000.0              # volume dries up
    return _frame(close, band, volume)


def _ideal_market(n=600):
    close = 18000.0 * np.exp(np.linspace(0.0, 0.30, n))   # slower than the stock
    return MarketContext(nifty_uptrend=True, nifty_close=_frame(
        close, np.full(n, 0.01), np.full(n, 1.0))["Close"])


def test_ideal_stock_is_full_setup():
    cfg = Config()
    df = _ideal_stock()
    result = evaluate_stock("WIN", df, ind.to_weekly(df), _ideal_market(), cfg)

    assert result.error is None
    # Every mandatory check should pass.
    missing = [l for l in result.mandatory_labels(cfg) if not result.criteria.get(l)]
    assert missing == [], f"unexpected failing checks: {missing}"
    assert result.full_setup(cfg) is True
    assert result.passed_count(cfg) == result.total_mandatory(cfg)
    # The VCP-specific checks in particular.
    assert result.criteria[C_VOLATILITY_CONTRACT] is True
    assert result.criteria[C_VOLUME_CONTRACT] is True


def test_optional_does_not_block_full_setup():
    cfg = Config()
    df = _ideal_stock()
    result = evaluate_stock("WIN", df, ind.to_weekly(df), _ideal_market(), cfg)
    # Force the optional criterion off; FULL setup must still hold.
    result.criteria[C_ABOVE_LOW] = False
    assert C_ABOVE_LOW in cfg.optional_criteria
    assert result.full_setup(cfg) is True


def test_downtrend_fails_trend_checks():
    cfg = Config()
    n = 600
    close = 400.0 * np.exp(np.linspace(0.0, -0.9, n))     # persistent downtrend
    df = _frame(close, np.full(n, 0.03), np.full(n, 800_000.0))
    result = evaluate_stock("LAG", df, ind.to_weekly(df), _ideal_market(), cfg)

    assert result.criteria[C_PRICE_ABOVE_MAS] is False
    assert result.criteria[C_MA_STACK] is False
    assert result.full_setup(cfg) is False


def test_insufficient_history():
    cfg = Config()
    n = 100
    df = _frame(np.linspace(100, 120, n), np.full(n, 0.02), np.full(n, 500_000.0))
    result = evaluate_stock("SHORT", df, ind.to_weekly(df), _ideal_market(), cfg)
    assert result.error is not None
    assert result.full_setup(cfg) is False


def test_relative_strength_outperformer_is_strong():
    cfg = Config()
    n = 400
    stock = pd.Series(100.0 * np.exp(np.linspace(0, 0.8, n)))
    nifty = pd.Series(100.0 * np.exp(np.linspace(0, 0.1, n)))
    score, strong = relative_strength(stock, nifty, cfg)
    assert score > 0
    assert strong is True

    # Underperformer: weaker than the index.
    weak = pd.Series(100.0 * np.exp(np.linspace(0, 0.02, n)))
    score2, strong2 = relative_strength(weak, nifty, cfg)
    assert strong2 is False


def test_rs_rating_overlay():
    cfg = Config()
    df = _ideal_stock()
    result = evaluate_stock("WIN", df, ind.to_weekly(df), _ideal_market(), cfg)
    # A low RS Rating overlay should flip the RS check off.
    result.apply_rs_rating(40.0, cfg)
    assert result.criteria[C_RS_STRONG] is False
    # A high rating flips it back on.
    result.apply_rs_rating(85.0, cfg)
    assert result.criteria[C_RS_STRONG] is True
