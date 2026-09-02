"""Correlation estimators — static and *dynamic* (time-varying).

The point of this tool is that correlation is not a single number. Between two
series it is a *process*: gold vs. real yields, Bunds vs. Treasuries, or stocks
vs. bonds can be strongly positive in one regime and negative in another. Two
complementary dynamic estimators are provided:

* **Rolling** — Pearson correlation over a trailing window of ``window``
  observations. Simple, transparent, and the market-standard first look.
* **EWMA** — exponentially weighted correlation (the RiskMetrics estimator).
  Every past observation contributes, weighted by a decay (``halflife``), so
  the estimate reacts faster to new information without a hard window edge.

Each returns a tidy frame indexed by date with one column per pair, named
``"A~B"``. Helpers also produce the correlation *matrix* as of any date.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd


def _pairs(columns, pairs=None) -> list[tuple[str, str]]:
    if pairs is None:
        return list(combinations(columns, 2))
    resolved = []
    for a, b in pairs:
        if a not in columns or b not in columns:
            raise KeyError(f"Pair ({a}, {b}) references unknown column(s).")
        resolved.append((a, b))
    return resolved


def static_correlation(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Full-sample correlation matrix (``pearson``, ``spearman`` or ``kendall``)."""
    return df.corr(method=method)


def rolling_correlation(
    df: pd.DataFrame,
    window: int = 60,
    pairs: list[tuple[str, str]] | None = None,
    min_periods: int | None = None,
) -> pd.DataFrame:
    """Trailing-window pairwise correlation series.

    Parameters
    ----------
    window : trailing window length in observations.
    min_periods : minimum observations before a value is produced
        (defaults to ``window``).
    """
    if window < 2:
        raise ValueError("window must be >= 2")
    if min_periods is None:
        min_periods = window
    out = {}
    for a, b in _pairs(df.columns, pairs):
        out[f"{a}~{b}"] = df[a].rolling(window, min_periods=min_periods).corr(df[b])
    return pd.DataFrame(out, index=df.index)


def ewma_correlation(
    df: pd.DataFrame,
    halflife: float = 30.0,
    pairs: list[tuple[str, str]] | None = None,
    min_periods: int = 10,
) -> pd.DataFrame:
    """Exponentially weighted pairwise correlation series (RiskMetrics style)."""
    if halflife <= 0:
        raise ValueError("halflife must be > 0")
    out = {}
    for a, b in _pairs(df.columns, pairs):
        out[f"{a}~{b}"] = (
            df[a].ewm(halflife=halflife, min_periods=min_periods).corr(df[b])
        )
    return pd.DataFrame(out, index=df.index)


def dynamic_correlation(
    df: pd.DataFrame,
    method: str = "rolling",
    window: int = 60,
    halflife: float = 30.0,
    pairs: list[tuple[str, str]] | None = None,
) -> pd.DataFrame:
    """Dispatch to the requested dynamic estimator (``rolling`` or ``ewma``)."""
    if method == "rolling":
        return rolling_correlation(df, window=window, pairs=pairs)
    if method == "ewma":
        return ewma_correlation(df, halflife=halflife, pairs=pairs)
    raise ValueError(f"Unknown dynamic method {method!r}; use 'rolling' or 'ewma'.")


def matrix_as_of(
    df: pd.DataFrame,
    method: str = "rolling",
    window: int = 60,
    halflife: float = 30.0,
    when=None,
) -> pd.DataFrame:
    """Reconstruct the full correlation matrix at a single point in time.

    For ``rolling`` this is the correlation over the last ``window`` rows up to
    ``when``. For ``ewma`` it is the exponentially weighted matrix as of
    ``when``. ``when`` defaults to the final observation.
    """
    if when is None:
        sub = df
    else:
        sub = df.loc[:when]
    if method == "rolling":
        return sub.tail(window).corr()
    if method == "ewma":
        # Build the matrix from exponentially weighted pairwise correlations.
        cols = list(df.columns)
        mat = pd.DataFrame(np.eye(len(cols)), index=cols, columns=cols)
        for a, b in combinations(cols, 2):
            val = sub[a].ewm(halflife=halflife, min_periods=1).corr(sub[b]).iloc[-1]
            mat.loc[a, b] = mat.loc[b, a] = val
        return mat
    raise ValueError(f"Unknown method {method!r}.")


def correlation_summary(roll: pd.DataFrame) -> pd.DataFrame:
    """Per-pair summary of a dynamic correlation frame.

    Reports the latest value, the sample mean, the range, and how much the
    correlation has *moved* (max minus min) — a quick read on which
    relationships are the least stable.
    """
    rows = []
    for col in roll.columns:
        s = roll[col].dropna()
        if s.empty:
            continue
        a, b = col.split("~", 1)
        rows.append(
            {
                "pair": col,
                "a": a,
                "b": b,
                "latest": s.iloc[-1],
                "mean": s.mean(),
                "min": s.min(),
                "max": s.max(),
                "swing": s.max() - s.min(),
                "std": s.std(ddof=0),
            }
        )
    summary = pd.DataFrame(rows)
    if not summary.empty:
        summary = summary.sort_values("swing", ascending=False).reset_index(drop=True)
    return summary
