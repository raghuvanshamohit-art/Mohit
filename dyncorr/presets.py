"""Registry of built-in financial parameters.

Each preset maps a friendly name (e.g. ``gold``, ``us_treasury_10y``) to a
concrete data source, a symbol/series code, and a recommended transform.

The transform matters a great deal for correlation analysis:

* **Yields / rates / inflation** are already expressed in "percent" units.
  Correlating their *levels* mostly measures shared trends, so we difference
  them (``diff``) to correlate day-to-day *changes* in yield.
* **Prices** (gold, equities, FX, ETFs) are correlated on *log returns*.

Presets are a convenience only. The tool is source-agnostic: you can always
point it at your own CSV, and the offline ``synthetic`` source can fabricate a
plausible history for any preset so the tool runs with no network access.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Preset:
    """Definition of a single named parameter."""

    key: str
    label: str
    source: str  # "fred" | "yahoo"
    symbol: str
    transform: str  # "diff" | "returns" | "log_returns" | "level"
    kind: str  # "rate" | "price" | "index" — used to seed synthetic data
    description: str


# The core set the tool is designed around, plus a handful of common companions.
PRESETS: dict[str, Preset] = {
    p.key: p
    for p in [
        Preset(
            "us_treasury_10y", "US 10Y Treasury Yield", "fred", "DGS10",
            "diff", "rate", "US 10-year Treasury constant-maturity yield.",
        ),
        Preset(
            "us_treasury_2y", "US 2Y Treasury Yield", "fred", "DGS2",
            "diff", "rate", "US 2-year Treasury constant-maturity yield.",
        ),
        Preset(
            "us_treasury_30y", "US 30Y Treasury Yield", "fred", "DGS30",
            "diff", "rate", "US 30-year Treasury constant-maturity yield.",
        ),
        Preset(
            "inflation", "US 10Y Breakeven Inflation", "fred", "T10YIE",
            "diff", "rate", "10-year breakeven inflation (market-implied).",
        ),
        Preset(
            "cpi", "US CPI (headline)", "fred", "CPIAUCSL",
            "returns", "index", "Consumer Price Index, all urban (monthly).",
        ),
        Preset(
            "bond_rate", "US Baa Corporate Bond Yield", "fred", "DBAA",
            "diff", "rate", "Moody's seasoned Baa corporate bond yield.",
        ),
        Preset(
            "euro_treasury_10y", "German 10Y Bund Yield", "fred",
            "IRLTLT01DEM156N", "diff", "rate",
            "Germany 10-year benchmark government bond yield (monthly).",
        ),
        Preset(
            "yen_treasury_10y", "Japan 10Y JGB Yield", "fred",
            "IRLTLT01JPM156N", "diff", "rate",
            "Japan 10-year benchmark government bond yield (monthly).",
        ),
        Preset(
            "gold", "Gold (spot/futures)", "yahoo", "GC=F",
            "log_returns", "price", "Gold front-month futures price.",
        ),
        Preset(
            "gold_etf", "Gold ETF (GLD)", "yahoo", "GLD",
            "log_returns", "price", "SPDR Gold Shares ETF.",
        ),
        Preset(
            "sp500", "S&P 500", "yahoo", "^GSPC",
            "log_returns", "price", "S&P 500 equity index.",
        ),
        Preset(
            "dollar_index", "US Dollar Index (DXY)", "yahoo", "DX-Y.NYB",
            "log_returns", "price", "Trade-weighted US dollar index.",
        ),
        Preset(
            "eurusd", "EUR/USD", "yahoo", "EURUSD=X",
            "log_returns", "price", "Euro to US dollar exchange rate.",
        ),
        Preset(
            "usdjpy", "USD/JPY", "yahoo", "JPY=X",
            "log_returns", "price", "US dollar to Japanese yen exchange rate.",
        ),
        Preset(
            "oil", "Crude Oil (WTI)", "yahoo", "CL=F",
            "log_returns", "price", "WTI crude oil front-month futures.",
        ),
        Preset(
            "vix", "VIX", "yahoo", "^VIX",
            "diff", "index", "CBOE volatility index.",
        ),
    ]
}


def resolve(name: str) -> Preset | None:
    """Return the preset for ``name`` (case/alias insensitive), or ``None``."""
    if name in PRESETS:
        return PRESETS[name]
    key = name.strip().lower().replace("-", "_").replace(" ", "_")
    if key in PRESETS:
        return PRESETS[key]
    return _ALIASES.get(key)


# Convenience aliases so casual names resolve to a sensible preset.
_ALIASES: dict[str, Preset] = {
    "us_treasuries": PRESETS["us_treasury_10y"],
    "treasuries": PRESETS["us_treasury_10y"],
    "ust": PRESETS["us_treasury_10y"],
    "10y": PRESETS["us_treasury_10y"],
    "2y": PRESETS["us_treasury_2y"],
    "euro_treasuries": PRESETS["euro_treasury_10y"],
    "bund": PRESETS["euro_treasury_10y"],
    "yen_treasuries": PRESETS["yen_treasury_10y"],
    "jgb": PRESETS["yen_treasury_10y"],
    "dxy": PRESETS["dollar_index"],
    "spx": PRESETS["sp500"],
    "wti": PRESETS["oil"],
}
