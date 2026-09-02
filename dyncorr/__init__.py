"""dyncorr — a dynamic (time-varying) correlation tool for financial series.

Correlate any set of parameters — US Treasuries, inflation, bond rates,
Euro/Yen Treasuries, gold, equities, FX, or your own CSV columns — and see how
those relationships move through time, not just a single static number.

Quick start
-----------
>>> from dyncorr import build_panel, dynamic_correlation
>>> panel = build_panel(["gold", "us_treasury_10y", "inflation"])
>>> roll = dynamic_correlation(panel.transformed, method="rolling", window=60)
>>> roll.tail(1)
"""

from __future__ import annotations

from .correlation import (
    correlation_summary,
    dynamic_correlation,
    ewma_correlation,
    matrix_as_of,
    rolling_correlation,
    static_correlation,
)
from .data import PanelResult, apply_transform, build_panel, generate_synthetic
from .presets import PRESETS, Preset, resolve

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "build_panel",
    "generate_synthetic",
    "apply_transform",
    "PanelResult",
    "static_correlation",
    "rolling_correlation",
    "ewma_correlation",
    "dynamic_correlation",
    "matrix_as_of",
    "correlation_summary",
    "PRESETS",
    "Preset",
    "resolve",
]
