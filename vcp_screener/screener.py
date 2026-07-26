"""Screen a universe: fetch data, evaluate every stock, rank by RS."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

import pandas as pd

from . import indicators as ind
from .config import Config
from .criteria import (
    MarketContext,
    StockResult,
    build_market_context,
    evaluate_stock,
)


def run_screen(
    symbols: List[str],
    provider,
    config: Optional[Config] = None,
    index_symbol: str = "^NSEI",
) -> Tuple[List[StockResult], MarketContext]:
    """Evaluate ``symbols`` and return ``(results, market_context)``.

    ``provider`` is any object exposing ``get_index`` and ``get_many`` (see
    :mod:`vcp_screener.data`).
    """
    config = config or Config()

    nifty_df = provider.get_index(index_symbol)
    market = build_market_context(nifty_df, config)
    if not market.nifty_uptrend:
        note = "no Nifty data" if nifty_df is None else "Nifty not in uptrend"
        print(f"  market context: {note}")

    data = provider.get_many(symbols)

    results: List[StockResult] = []
    for sym in symbols:
        df = data.get(sym)
        weekly = ind.to_weekly(df) if df is not None and not df.empty else None
        results.append(evaluate_stock(sym, df, weekly, market, config))

    _assign_rs_ratings(results, config)
    return results, market


def _assign_rs_ratings(results: List[StockResult], config: Config) -> None:
    """Turn raw RS scores into a 1-99 cross-sectional RS Rating and overlay it
    on the "RS vs Nifty Strong" check when enabled."""
    scored = {
        r.symbol: r.rs_score
        for r in results
        if not r.error and not math.isnan(r.rs_score)
    }
    if not scored:
        return
    ranks = pd.Series(scored).rank(pct=True) * 99.0
    by_symbol = {r.symbol: r for r in results}
    for sym, rating in ranks.items():
        by_symbol[sym].apply_rs_rating(round(float(rating), 1), config)


def rank_results(results: List[StockResult], config: Config) -> List[StockResult]:
    """Sort: FULL SETUP first, then by mandatory checks passed, then RS Rating."""

    def key(r: StockResult):
        return (
            r.full_setup(config),
            r.passed_count(config),
            r.rs_rating if r.rs_rating is not None else -1.0,
        )

    return sorted(results, key=key, reverse=True)
