"""Technical indicators and small numeric helpers.

Everything here is a pure function of pandas objects, which keeps the criteria
engine trivial to unit-test with hand-built series.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple moving average."""
    return series.rolling(window, min_periods=window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    """Exponential moving average (span form)."""
    return series.ewm(span=window, adjust=False, min_periods=window).mean()


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range using Wilder's smoothing."""
    prev_close = close.shift(1)
    true_range = pd.concat(
        [
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


def is_rising(series: pd.Series, lookback: int) -> bool:
    """True if the latest value is above the value ``lookback`` bars ago."""
    s = series.dropna()
    if len(s) <= lookback:
        return False
    return _gt(s.iloc[-1], s.iloc[-1 - lookback])


def period_return(series: pd.Series, lookback: int) -> float:
    """Simple return over ``lookback`` bars, or NaN if not enough data."""
    s = series.dropna()
    if len(s) <= lookback or s.iloc[-1 - lookback] == 0:
        return float("nan")
    return float(s.iloc[-1] / s.iloc[-1 - lookback] - 1.0)


def to_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """Resample a daily OHLCV frame to weekly bars (week ending Friday)."""
    agg = {
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }
    cols = [c for c in agg if c in df.columns]
    return df[cols].resample("W-FRI").agg({c: agg[c] for c in cols}).dropna(how="any")


def contracting(series: pd.Series, recent: int, prior: int) -> bool:
    """True if the mean of the ``recent`` window is below the mean of the
    ``prior`` window that immediately precedes it.

    Used for both volatility (ATR%) and volume dry-up.
    """
    s = series.dropna()
    if len(s) < recent + prior:
        return False
    recent_mean = s.iloc[-recent:].mean()
    prior_mean = s.iloc[-(recent + prior):-recent].mean()
    return _lt(recent_mean, prior_mean)


# --- NaN-safe scalar comparisons --------------------------------------------
def _gt(a, b) -> bool:
    return bool(pd.notna(a) and pd.notna(b) and a > b)


def _lt(a, b) -> bool:
    return bool(pd.notna(a) and pd.notna(b) and a < b)


def _ge(a, b) -> bool:
    return bool(pd.notna(a) and pd.notna(b) and a >= b)


def chain_gt(*values) -> bool:
    """True if values are strictly decreasing left-to-right and all present."""
    if any(pd.isna(v) for v in values):
        return False
    return all(values[i] > values[i + 1] for i in range(len(values) - 1))
