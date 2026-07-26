"""Tunable parameters for the VCP screener.

Every threshold used by the criteria engine lives here so the screen can be
tuned without touching logic. Defaults follow the checklist the tool mirrors
and Minervini's Trend-Template conventions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from .constants import DEFAULT_OPTIONAL


@dataclass
class Config:
    # --- Moving-average lengths (trading days) ---------------------------
    ma_short: int = 10
    ma_fast: int = 50
    ma_mid: int = 150
    ma_slow: int = 200

    # A moving average is "rising" if it is higher than it was this many
    # trading days ago (~1 month).
    rising_lookback: int = 21

    # 52-week window, in trading days.
    week52: int = 252

    # --- Distance from 52-week high / low --------------------------------
    within_high_pct: float = 0.25   # price within 25% of the 52-week high
    above_low_pct: float = 0.30     # price at least 30% above the 52-week low

    # --- Absolute price floor --------------------------------------------
    min_price: float = 50.0         # Price >= ₹50

    # --- Liquidity -------------------------------------------------------
    liquidity_lookback: int = 50
    # Minimum average daily traded value (turnover = close * volume), in ₹.
    # F&O names are liquid; ₹5 crore/day is a gentle floor.
    min_avg_turnover: float = 5e7

    # --- Relative strength vs Nifty --------------------------------------
    rs_lookback: int = 126          # ~6 months
    rs_line_near_high: float = 0.90  # RS line within 10% of its own high
    # When the whole universe is screened at once we can compute a proper
    # cross-sectional RS Rating (0-99 percentile). RS is then "strong" when
    # the rating clears this floor (Minervini uses ~70).
    use_rs_rating: bool = True
    rs_rating_min: float = 70.0

    # --- Nifty / market trend --------------------------------------------
    # Nifty is "in an uptrend" when it trades above its 200-DMA and its 50-DMA
    # is rising.
    nifty_ma_slow: int = 200
    nifty_ma_fast: int = 50

    # --- Weekly uptrend ---------------------------------------------------
    weekly_ma: int = 10             # 10-week EMA
    weekly_trend_ma: int = 30       # 30-week SMA (~150-DMA)
    weekly_slope_lookback: int = 4  # 10-week EMA higher than 4 weeks ago

    # --- Volatility contraction (the VCP core) ---------------------------
    atr_period: int = 14
    volatility_recent: int = 20     # recent ATR% window
    volatility_prior: int = 50      # prior ATR% window it is compared against

    # --- Volume contraction ----------------------------------------------
    volume_recent: int = 10
    volume_prior: int = 50

    # --- Aggregation ------------------------------------------------------
    optional_criteria: Tuple[str, ...] = field(default=DEFAULT_OPTIONAL)

    # Minimum rows of daily history required to evaluate a stock. Needs to
    # cover the 52-week window plus the rising lookback.
    @property
    def min_history(self) -> int:
        return self.week52 + self.rising_lookback + 5
