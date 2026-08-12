"""The 15 VCP / Trend-Template checks.

Each stock is reduced to an ordered dict of ``label -> bool``. A "FULL VCP
SETUP" is flagged only when every *mandatory* check passes (the checklist marks
"30%+ Above 52W Low" as Optional, so it is excluded by default).
"""

from __future__ import annotations

import math
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, Optional

import numpy as np
import pandas as pd

from . import indicators as ind
from .config import Config
from .constants import (
    CRITERIA_ORDER,
    C_ABOVE_LOW,
    C_MA150_RISING,
    C_MA200_RISING,
    C_MA50_RISING,
    C_MA_STACK,
    C_MIN_PRICE,
    C_NIFTY_UPTREND,
    C_PRICE_ABOVE_10,
    C_PRICE_ABOVE_MAS,
    C_RS_STRONG,
    C_VOLATILITY_CONTRACT,
    C_VOLUME_CONTRACT,
    C_VOLUME_OK,
    C_WEEKLY_UPTREND,
    C_WITHIN_HIGH,
)


@dataclass
class MarketContext:
    """Market-wide facts shared by every stock in a single screen run."""

    nifty_uptrend: bool = False
    nifty_close: Optional[pd.Series] = None


@dataclass
class StockResult:
    symbol: str
    price: float = float("nan")
    criteria: "OrderedDict[str, bool]" = field(default_factory=OrderedDict)
    rs_score: float = float("nan")     # raw relative outperformance vs Nifty
    rs_rating: Optional[float] = None  # 0-99 cross-sectional percentile
    high_52w: float = float("nan")
    low_52w: float = float("nan")
    error: Optional[str] = None

    # --- aggregation helpers ---------------------------------------------
    def mandatory_labels(self, config: Config):
        return [l for l in CRITERIA_ORDER if l not in config.optional_criteria]

    def total_mandatory(self, config: Config) -> int:
        return len(self.mandatory_labels(config))

    def passed_count(self, config: Config) -> int:
        return sum(1 for l in self.mandatory_labels(config) if self.criteria.get(l))

    def full_setup(self, config: Config) -> bool:
        if self.error:
            return False
        return all(self.criteria.get(l) for l in self.mandatory_labels(config))

    def apply_rs_rating(self, rating: Optional[float], config: Config) -> None:
        """Overlay a cross-sectional RS Rating computed across the universe."""
        self.rs_rating = rating
        if config.use_rs_rating and rating is not None:
            self.criteria[C_RS_STRONG] = bool(rating >= config.rs_rating_min)


def relative_strength(close: pd.Series, nifty_close: Optional[pd.Series], config: Config):
    """Return ``(rs_score, strong_bool)`` for a stock vs Nifty.

    ``rs_score`` is the excess return over the RS lookback (used later to rank
    the universe into an RS Rating). The self-contained ``strong_bool`` is True
    when the stock outperformed Nifty over the window *and* its RS line sits
    near its own recent high.
    """
    if nifty_close is None or len(nifty_close.dropna()) <= config.rs_lookback:
        return float("nan"), False

    stock_ret = ind.period_return(close, config.rs_lookback)
    nifty_ret = ind.period_return(nifty_close, config.rs_lookback)
    if math.isnan(stock_ret) or math.isnan(nifty_ret):
        return float("nan"), False

    rs_score = (1.0 + stock_ret) / (1.0 + nifty_ret) - 1.0

    aligned = pd.concat([close, nifty_close], axis=1, keys=["s", "n"]).dropna()
    near_high = False
    if len(aligned) > config.rs_lookback:
        rs_line = aligned["s"] / aligned["n"]
        window_high = rs_line.iloc[-config.rs_lookback:].max()
        near_high = ind._ge(rs_line.iloc[-1], config.rs_line_near_high * window_high)

    strong = (stock_ret > nifty_ret) and near_high
    return float(rs_score), bool(strong)


def build_market_context(nifty_df: Optional[pd.DataFrame], config: Config) -> MarketContext:
    """Compute the once-per-run market facts from the Nifty daily frame."""
    if nifty_df is None or nifty_df.empty:
        return MarketContext(nifty_uptrend=False, nifty_close=None)

    close = nifty_df["Close"]
    sma_slow = ind.sma(close, config.nifty_ma_slow)
    sma_fast = ind.sma(close, config.nifty_ma_fast)
    uptrend = ind._gt(close.iloc[-1], sma_slow.iloc[-1]) and ind.is_rising(
        sma_fast, config.rising_lookback
    )
    return MarketContext(nifty_uptrend=bool(uptrend), nifty_close=close)


def _weekly_uptrend(weekly: Optional[pd.DataFrame], config: Config) -> bool:
    if weekly is None or len(weekly) < config.weekly_trend_ma + config.weekly_slope_lookback:
        return False
    wclose = weekly["Close"]
    wema = ind.ema(wclose, config.weekly_ma)
    wsma = ind.sma(wclose, config.weekly_trend_ma)
    price_ok = ind._gt(wclose.iloc[-1], wsma.iloc[-1])
    slope_ok = ind.is_rising(wema, config.weekly_slope_lookback)
    return bool(price_ok and slope_ok)


def evaluate_stock(
    symbol: str,
    df: pd.DataFrame,
    weekly: Optional[pd.DataFrame],
    market: MarketContext,
    config: Config,
) -> StockResult:
    """Run the full checklist for one stock and return a :class:`StockResult`."""
    result = StockResult(symbol=symbol)

    if df is None or df.empty:
        result.error = "no data"
        return result

    df = df.dropna(subset=["Close"]) if "Close" in df.columns else df
    if len(df) < config.min_history:
        result.error = f"insufficient history ({len(df)} rows, need {config.min_history})"
        return result

    close, high, low, volume = df["Close"], df["High"], df["Low"], df["Volume"]
    price = float(close.iloc[-1])
    result.price = price

    sma10 = ind.sma(close, config.ma_short)
    sma50 = ind.sma(close, config.ma_fast)
    sma150 = ind.sma(close, config.ma_mid)
    sma200 = ind.sma(close, config.ma_slow)

    high_52w = float(high.iloc[-config.week52:].max())
    low_52w = float(low.iloc[-config.week52:].min())
    result.high_52w, result.low_52w = high_52w, low_52w

    turnover = (close * volume).iloc[-config.liquidity_lookback:].mean()
    atr_pct = ind.atr(high, low, close, config.atr_period) / close

    rs_score, rs_strong = relative_strength(close, market.nifty_close, config)
    result.rs_score = rs_score

    c: "OrderedDict[str, bool]" = OrderedDict()
    c[C_PRICE_ABOVE_MAS] = (
        ind._gt(price, sma50.iloc[-1])
        and ind._gt(price, sma150.iloc[-1])
        and ind._gt(price, sma200.iloc[-1])
    )
    c[C_MA_STACK] = ind.chain_gt(sma50.iloc[-1], sma150.iloc[-1], sma200.iloc[-1])
    c[C_MA200_RISING] = ind.is_rising(sma200, config.rising_lookback)
    c[C_MA50_RISING] = ind.is_rising(sma50, config.rising_lookback)
    c[C_WITHIN_HIGH] = ind._ge(price, (1.0 - config.within_high_pct) * high_52w)
    c[C_ABOVE_LOW] = ind._ge(price, (1.0 + config.above_low_pct) * low_52w)
    c[C_PRICE_ABOVE_10] = ind._gt(price, sma10.iloc[-1])
    c[C_MIN_PRICE] = ind._ge(price, config.min_price)
    c[C_WEEKLY_UPTREND] = _weekly_uptrend(weekly, config)
    c[C_MA150_RISING] = ind.is_rising(sma150, config.rising_lookback)
    c[C_VOLUME_OK] = ind._ge(turnover, config.min_avg_turnover)
    c[C_RS_STRONG] = rs_strong  # may be overlaid with RS Rating by the screener
    c[C_NIFTY_UPTREND] = market.nifty_uptrend
    c[C_VOLATILITY_CONTRACT] = ind.contracting(
        atr_pct, config.volatility_recent, config.volatility_prior
    )
    c[C_VOLUME_CONTRACT] = ind.contracting(
        volume, config.volume_recent, config.volume_prior
    )

    result.criteria = c
    return result
