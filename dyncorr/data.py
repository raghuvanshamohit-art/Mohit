"""Data acquisition and preparation for the dynamic correlation tool.

Three ways to get a panel of series:

1. ``--csv``      Load a wide CSV (a date column + one column per series).
2. ``synthetic``  Fabricate a deterministic, plausible history offline. The
                  synthetic generator deliberately builds *time-varying*
                  correlations so the dynamic tool has something to reveal
                  without any network access. This is the default source.
3. ``live``       Best-effort fetch from FRED / Yahoo Finance (needs network
                  and, respectively, ``pandas-datareader`` / ``yfinance``).

Whatever the source, :func:`build_panel` returns a tidy, transformed
``DataFrame`` (one column per parameter) that is ready to be correlated.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .presets import Preset, resolve

# --------------------------------------------------------------------------- #
# Transforms
# --------------------------------------------------------------------------- #

VALID_TRANSFORMS = {"level", "diff", "returns", "log_returns", "zscore"}


def apply_transform(series: pd.Series, transform: str) -> pd.Series:
    """Transform a single level series into the space we correlate in."""
    if transform == "level":
        out = series
    elif transform == "diff":
        out = series.diff()
    elif transform == "returns":
        out = series.pct_change()
    elif transform == "log_returns":
        out = np.log(series).diff()
    elif transform == "zscore":
        out = (series - series.mean()) / series.std(ddof=0)
    else:
        raise ValueError(
            f"Unknown transform {transform!r}; choose from {sorted(VALID_TRANSFORMS)}"
        )
    return out.rename(series.name)


# --------------------------------------------------------------------------- #
# Synthetic data (offline, deterministic)
# --------------------------------------------------------------------------- #

# A small factor model. Each series loads on a few latent factors; a couple of
# loadings vary with normalized time ``t`` in [0, 1] so pairwise correlations
# drift and even flip sign — exactly what a dynamic correlation tool exists to
# surface. Loadings are constants or callables ``t -> float``.
_FACTORS = ["rates", "infl", "market", "fx"]

_SYNTH_LOADINGS: dict[str, dict] = {
    "us_treasury_2y":     {"rates": 0.90, "infl": 0.15},
    "us_treasury_10y":    {"rates": 1.00, "infl": 0.30},
    "us_treasury_30y":    {"rates": 0.95, "infl": 0.40},
    "inflation":          {"infl": 1.00, "rates": 0.20},
    "cpi":                {"infl": 0.80, "market": 0.10},
    "bond_rate":          {"rates": 0.80, "infl": 0.20, "market": -0.30},
    "euro_treasury_10y":  {"rates": 0.70, "infl": 0.20, "fx": 0.20},
    "yen_treasury_10y":   {"rates": 0.45, "fx": -0.25},
    # Gold's dependence on rates flips from negative to positive across the
    # sample, and its risk-hedge character strengthens late — the headline
    # example of a correlation that is anything but static.
    "gold":               {"infl": 0.45, "market": lambda t: 0.10 + 0.30 * t,
                           "rates": lambda t: -0.55 + 0.85 * t},
    "gold_etf":           {"infl": 0.45, "market": lambda t: 0.10 + 0.30 * t,
                           "rates": lambda t: -0.55 + 0.85 * t},
    "sp500":              {"market": 1.00, "rates": -0.20},
    "dollar_index":       {"rates": 0.40, "market": -0.30, "fx": 0.60},
    "eurusd":             {"rates": -0.30, "market": 0.20, "fx": -0.55},
    "usdjpy":             {"rates": 0.50, "market": 0.20, "fx": 0.30},
    "oil":                {"market": 0.55, "infl": 0.30},
    "vix":                {"market": -1.20},
}

# Per-kind integration settings.
#   rate  : mean-reverting (Ornstein-Uhlenbeck) around ``start`` with speed
#           ``kappa`` — keeps yields in a realistic band and, crucially, stops
#           a long random walk from drifting into the floor and flatlining
#           (a flat series has zero variance -> undefined correlation).
#   price : geometric random walk (level = start * exp(cumsum(returns))).
#   index : geometric with a small positive drift (e.g. CPI).
_KIND_CONFIG = {
    "rate":  {"start": 3.0, "scale": 0.07, "kappa": 0.02, "mode": "ou"},
    "price": {"start": 100.0, "scale": 0.011, "drift": 0.0002, "mode": "geometric"},
    "index": {"start": 100.0, "scale": 0.004, "drift": 0.0003, "mode": "geometric"},
}


def _integrate_ou(shocks: np.ndarray, start: float, kappa: float) -> np.ndarray:
    """Integrate shocks into a mean-reverting level path (Vasicek/OU)."""
    level = np.empty_like(shocks)
    level[0] = start
    for i in range(1, len(shocks)):
        level[i] = level[i - 1] + kappa * (start - level[i - 1]) + shocks[i]
    return level


def _loading_matrix(names: list[str], t: np.ndarray) -> np.ndarray:
    """Build a (T, n_series, n_factors) tensor of (possibly time-varying) loadings."""
    L = np.zeros((len(t), len(names), len(_FACTORS)))
    for j, name in enumerate(names):
        spec = _SYNTH_LOADINGS.get(name, {"market": 0.6, "infl": 0.1})
        for k, factor in enumerate(_FACTORS):
            val = spec.get(factor, 0.0)
            L[:, j, k] = val(t) if callable(val) else val
    return L


def generate_synthetic(
    names: list[str],
    start: str = "2015-01-01",
    end: str = "2024-12-31",
    seed: int = 7,
) -> pd.DataFrame:
    """Generate a deterministic level panel with time-varying correlations."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range(start=start, end=end)
    T = len(idx)
    if T < 3:
        raise ValueError("Date range too short to generate synthetic data.")
    t = np.linspace(0.0, 1.0, T)

    # Latent factor innovations, with a volatility regime around the midpoint
    # (a "crisis" where correlations tighten).
    vol = 1.0 + 1.5 * np.exp(-((t - 0.5) ** 2) / (2 * 0.03 ** 2))
    factors = rng.standard_normal((T, len(_FACTORS))) * vol[:, None]

    L = _loading_matrix(names, t)  # (T, n, k)
    # Common component per series: sum_k L[t, j, k] * factor[t, k]
    common = np.einsum("tjk,tk->tj", L, factors)
    idio = rng.standard_normal((T, len(names))) * 0.6
    innovations = common + idio  # standardized-ish daily changes/returns

    cols = {}
    for j, name in enumerate(names):
        preset = resolve(name)
        kind = preset.kind if preset else "price"
        cfg = _KIND_CONFIG.get(kind, _KIND_CONFIG["price"])
        shocks = innovations[:, j] * cfg["scale"] + cfg.get("drift", 0.0)
        shocks[0] = 0.0
        if cfg["mode"] == "ou":
            level = _integrate_ou(shocks, cfg["start"], cfg["kappa"])
            level = np.clip(level, 0.05, None)  # keep yields non-negative-ish
        else:
            level = cfg["start"] * np.exp(np.cumsum(shocks))
        cols[name] = level

    return pd.DataFrame(cols, index=idx)


# --------------------------------------------------------------------------- #
# Live data (best effort)
# --------------------------------------------------------------------------- #


def _fetch_fred(symbol: str, start, end) -> pd.Series:
    from pandas_datareader import data as pdr  # type: ignore

    return pdr.DataReader(symbol, "fred", start, end)[symbol]


def _fetch_yahoo(symbol: str, start, end) -> pd.Series:
    import yfinance as yf  # type: ignore

    df = yf.download(symbol, start=start, end=end, progress=False, auto_adjust=True)
    if df is None or df.empty:
        raise RuntimeError(f"No data returned for {symbol!r}")
    col = "Close" if "Close" in df.columns else df.columns[0]
    s = df[col]
    if isinstance(s, pd.DataFrame):  # yfinance can return a 1-col frame
        s = s.iloc[:, 0]
    return s


def fetch_series(preset: Preset, start, end) -> pd.Series:
    """Fetch one preset's level series from its live source."""
    if preset.source == "fred":
        s = _fetch_fred(preset.symbol, start, end)
    elif preset.source == "yahoo":
        s = _fetch_yahoo(preset.symbol, start, end)
    else:
        raise ValueError(f"Unknown source {preset.source!r} for {preset.key!r}")
    return s.rename(preset.key)


# --------------------------------------------------------------------------- #
# Panel assembly
# --------------------------------------------------------------------------- #


@dataclass
class PanelResult:
    levels: pd.DataFrame       # raw aligned level series
    transformed: pd.DataFrame  # after per-series transforms; ready to correlate
    transforms: dict[str, str]
    source: str


def load_csv(path: str, date_col: str | None = None) -> pd.DataFrame:
    """Load a wide CSV of level series indexed by date."""
    df = pd.read_csv(path)
    if date_col is None:
        date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()
    return df.select_dtypes(include="number")


def build_panel(
    params: list[str],
    source: str = "synthetic",
    start: str = "2015-01-01",
    end: str = "2024-12-31",
    transform: str = "auto",
    csv_path: str | None = None,
    date_col: str | None = None,
    seed: int = 7,
    dropna: bool = True,
) -> PanelResult:
    """Resolve parameters into an aligned, transformed panel ready for correlation.

    ``transform="auto"`` uses each preset's recommended transform (yields are
    differenced, prices become log returns); any other value forces a single
    transform across every column.
    """
    # 1) Obtain level series.
    if source == "csv" or csv_path is not None:
        levels = load_csv(csv_path, date_col)
        if params:
            missing = [p for p in params if p not in levels.columns]
            if missing:
                raise KeyError(
                    f"Columns not in CSV: {missing}. Available: {list(levels.columns)}"
                )
            levels = levels[params]
    elif source == "synthetic":
        levels = generate_synthetic(params, start=start, end=end, seed=seed)
    elif source == "live":
        series = []
        for name in params:
            preset = resolve(name)
            if preset is None:
                raise KeyError(
                    f"{name!r} is not a known preset; use --csv for custom series."
                )
            try:
                series.append(fetch_series(preset, start, end))
            except Exception as exc:  # pragma: no cover - network dependent
                warnings.warn(f"Failed to fetch {name!r} ({preset.symbol}): {exc}")
        if not series:
            raise RuntimeError("No live series could be fetched.")
        levels = pd.concat(series, axis=1)
    else:
        raise ValueError(f"Unknown source {source!r}")

    levels = levels.sort_index()

    # 2) Decide per-column transforms.
    transforms: dict[str, str] = {}
    for col in levels.columns:
        if transform == "auto":
            preset = resolve(col)
            transforms[col] = preset.transform if preset else "log_returns"
        else:
            transforms[col] = transform

    # 3) Apply transforms and align.
    transformed = pd.DataFrame(
        {col: apply_transform(levels[col], transforms[col]) for col in levels.columns}
    )
    # Forward-fill mixed-frequency gaps (e.g. monthly macro vs daily prices)
    # in the *levels* space would be ideal, but for correlation we simply drop
    # rows without full coverage.
    if dropna:
        transformed = transformed.dropna(how="any")

    return PanelResult(
        levels=levels,
        transformed=transformed,
        transforms=transforms,
        source=source,
    )
