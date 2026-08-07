"""Run the full 'top-10 F&O daily gainers' analysis and write a report.

Usage:
    python -m fo_top10.analyze --start 2018-01-01 --end 2025-08-01 --top 10
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from .backtest import (
    backtest_hold,
    benchmark_equal_weight,
    daily_returns,
    forward_return_persistence,
    hold_until_exit,
    membership_sustain,
    performance,
    selection_mask,
)
from .data import download_prices
from .universe import yahoo_symbols

HOLD_PERIODS = [1, 2, 3, 5, 10, 15, 20]
ROUND_TRIP_COST = 0.0025  # 0.25% round-trip (brokerage + STT/charges + slippage)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2018-01-01")
    ap.add_argument("--end", default="2025-08-01")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--cost", type=float, default=ROUND_TRIP_COST)
    ap.add_argument("--force", action="store_true", help="re-download prices")
    ap.add_argument("--cache", default="data/fo_prices.csv")
    ap.add_argument("--out", default="results/report.md")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.cache), exist_ok=True)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    prices = download_prices(yahoo_symbols(), args.start, args.end,
                             cache_path=args.cache, force=args.force)
    # keep days where a healthy fraction of the universe traded
    prices = prices[prices.notna().sum(axis=1) >= 0.6 * prices.shape[1]]
    returns = daily_returns(prices)
    mask = selection_mask(returns, top_n=args.top)

    # -- Q1a: membership persistence ------------------------------------------
    sustain = membership_sustain(mask)

    # -- Q1b: return persistence ----------------------------------------------
    persist = forward_return_persistence(returns, mask)

    # -- Q2: tradable strategy across hold periods ----------------------------
    rows_gross, rows_net = [], []
    curves = {}
    for h in HOLD_PERIODS:
        eq_g = backtest_hold(returns, mask, h, cost_per_turn=0.0)
        eq_n = backtest_hold(returns, mask, h, cost_per_turn=args.cost)
        curves[h] = eq_n
        pg, pn = performance(eq_g), performance(eq_n)
        pg["hold_days"] = h
        pn["hold_days"] = h
        rows_gross.append(pg)
        rows_net.append(pn)
    perf_gross = pd.DataFrame(rows_gross).set_index("hold_days")
    perf_net = pd.DataFrame(rows_net).set_index("hold_days")

    # -- hold-until-exit event study ------------------------------------------
    exit_study = hold_until_exit(returns, mask)

    # -- benchmark ------------------------------------------------------------
    bench = benchmark_equal_weight(returns)
    bench_perf = performance(bench)

    report = build_report(args, prices, returns, sustain, persist,
                          perf_gross, perf_net, exit_study, bench_perf)
    with open(args.out, "w") as f:
        f.write(report)
    # also dump the machine-readable tables
    perf_net.to_csv("results/strategy_performance_net.csv")
    perf_gross.to_csv("results/strategy_performance_gross.csv")
    persist.to_csv("results/forward_return_persistence.csv", index=False)
    print("\n" + report)
    print(f"\nReport written to {args.out}")


def _fmt(df: pd.DataFrame) -> str:
    return df.to_markdown()


def build_report(args, prices, returns, sustain, persist,
                 perf_gross, perf_net, exit_study, bench_perf) -> str:
    start = prices.index.min().date()
    end = prices.index.max().date()
    n_names = prices.shape[1]
    n_days = prices.shape[0]

    best_net = perf_net["CAGR_%"].idxmax()

    L = []
    L.append("# Top-10 F&O Daily Gainers — Backtest Results\n")
    L.append(f"*Strategy:* each trading day, rank the NSE F&O universe by that "
             f"day's % change and buy the **top {args.top} gainers** "
             f"(equal-weight), then hold.\n")
    L.append(f"**Data:** {n_names} F&O stocks, {n_days} trading days, "
             f"{start} → {end} (Yahoo Finance, adjusted close).\n")
    L.append(f"**Costs:** net results charge {args.cost*100:.2f}% round-trip "
             f"per rebalance (brokerage + STT/exchange charges + slippage).\n")

    L.append("\n## 1. How many days do they sustain?\n")
    L.append("**(a) Staying in the top-10** — once a stock enters the daily "
             "top-10 gainers, how many consecutive days it stays there:\n")
    L.append(f"- Episodes analysed: **{sustain['episodes']:,}**")
    L.append(f"- Mean sustain: **{sustain['mean_days']:.2f} days**, "
             f"median **{sustain['median_days']:.0f} day(s)**")
    L.append(f"- One-and-done (exactly 1 day): **{sustain['pct_1_day']:.1f}%**")
    L.append(f"- Lasts ≥2 days: {sustain['pct_ge_2_days']:.1f}%, "
             f"≥3 days: {sustain['pct_ge_3_days']:.1f}% "
             f"(max ever {sustain['max_days']} days)\n")

    L.append("**(b) Does the up-move continue?** Average *forward* return after "
             "entering the top-10 (vs. the universe average = the edge):\n")
    L.append(_fmt(persist.round(2)))
    L.append("")

    L.append("\n## 2. Strategy performance by hold period (NET of costs)\n")
    L.append(_fmt(perf_net))
    L.append(f"\nBest net CAGR is at a **{best_net}-day hold**. "
             "For reference, the same table **gross** (no trading costs):\n")
    L.append(_fmt(perf_gross))

    L.append("\n## 3. 'Hold until it drops out of the top-10' (event study)\n")
    L.append(f"- Trades: **{exit_study['trades']:,}**")
    L.append(f"- Average hold period: **{exit_study['avg_hold_days']:.2f} days** "
             f"(median {exit_study['median_hold_days']:.0f})")
    L.append(f"- Average trade return: **{exit_study['avg_return_%']:.2f}%** "
             f"(median {exit_study['median_return_%']:.2f}%), "
             f"win rate {exit_study['win_rate_%']:.1f}%\n")

    L.append("\n## 4. Benchmark — equal-weight F&O universe (buy & hold)\n")
    L.append(f"- CAGR **{bench_perf['CAGR_%']}%**, "
             f"max drawdown {bench_perf['max_drawdown_%']}%, "
             f"Sharpe {bench_perf['sharpe']} over the same window.\n")

    L.append("\n## Caveats\n")
    L.append("- **Constituent/survivorship bias:** uses today's F&O list over "
             "the whole window; names that were dropped are missing, which "
             "flatters results.")
    L.append("- Enters/exits at the **close**; no impact modelling beyond the "
             "flat cost. Real slippage on chasing gappy movers is worse.")
    L.append("- Yahoo adjusted-close data has occasional gaps/adjustment "
             "errors; treat figures as indicative, not exact.")
    L.append("- No leverage, no overnight-futures financing; this is modelled "
             "as a cash-equity basket.")
    return "\n".join(L)


if __name__ == "__main__":
    main()
