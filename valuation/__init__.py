"""Stock intrinsic-value & pyramiding toolkit.

Two independent, composable pieces:

* ``intrinsic`` — estimate a stock's *intrinsic value* (fair value) from its
  fundamentals using several classic methods (Graham Number, Graham's revised
  formula, two-stage DCF, an earnings-power / exit-multiple model and the
  Gordon dividend-discount model) and blend them into one figure with a
  margin-of-safety "best buy price".

* ``pyramid`` — turn an intrinsic value into a **pyramiding plan**: a ladder of
  buy tranches with concrete prices, sizes and a blended average entry, either
  *accumulating value* (buy more the cheaper it gets, below intrinsic value) or
  *trend pyramiding* (add to a winner as it rises, classic decreasing-size add).

``engine.value_stock`` ties them together and can best-effort auto-fill
fundamentals from Yahoo Finance, always letting explicitly supplied inputs win.

Pure standard library — nothing to install. Not investment advice.
"""

from __future__ import annotations

from .intrinsic import Fundamentals, intrinsic_value_estimates
from .pyramid import build_pyramid, build_trend_pyramid

__all__ = [
    "Fundamentals",
    "intrinsic_value_estimates",
    "build_pyramid",
    "build_trend_pyramid",
]

__version__ = "1.0.0"
