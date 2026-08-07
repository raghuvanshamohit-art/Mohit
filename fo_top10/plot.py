"""Generate summary charts for the top-10 F&O daily-gainers backtest."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .backtest import (
    backtest_hold,
    benchmark_equal_weight,
    daily_returns,
    selection_mask,
)
from .data import download_prices
from .universe import yahoo_symbols

COST = 0.0025


def main() -> None:
    prices = download_prices(yahoo_symbols(), "2018-01-01", "2025-08-01",
                             cache_path="data/fo_prices.csv")
    prices = prices[prices.notna().sum(axis=1) >= 0.6 * prices.shape[1]]
    returns = daily_returns(prices)
    mask = selection_mask(returns, top_n=10)
    bench = benchmark_equal_weight(returns)

    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    # (1) equity curves, net of costs, log scale
    for h in [1, 3, 5, 10, 20]:
        eq = backtest_hold(returns, mask, h, cost_per_turn=COST)
        ax[0].plot(eq.index, eq.values, label=f"{h}-day hold")
    b = bench.reindex(prices.index).dropna()
    b = b / b.iloc[0]
    ax[0].plot(b.index, b.values, "k--", lw=2, label="EW F&O buy & hold")
    ax[0].set_yscale("log")
    ax[0].set_title("Top-10 daily gainers — equity (NET of 0.25% cost)")
    ax[0].set_ylabel("Growth of ₹1 (log scale)")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)

    # (2) net CAGR vs hold period bar
    holds = [1, 2, 3, 5, 10, 15, 20]
    from .backtest import performance
    cagr_net = [performance(backtest_hold(returns, mask, h, COST))["CAGR_%"]
                for h in holds]
    cagr_gross = [performance(backtest_hold(returns, mask, h, 0.0))["CAGR_%"]
                  for h in holds]
    x = range(len(holds))
    ax[1].bar([i - 0.2 for i in x], cagr_gross, width=0.4, label="gross",
              color="#8ecae6")
    ax[1].bar([i + 0.2 for i in x], cagr_net, width=0.4, label="net of costs",
              color="#fb8500")
    ax[1].axhline(performance(bench)["CAGR_%"], color="k", ls="--",
                  label="EW F&O buy & hold")
    ax[1].set_xticks(list(x))
    ax[1].set_xticklabels([f"{h}d" for h in holds])
    ax[1].set_title("CAGR vs hold period — costs kill the fast versions")
    ax[1].set_ylabel("CAGR %")
    ax[1].set_xlabel("hold period")
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.3, axis="y")

    fig.tight_layout()
    fig.savefig("results/summary.png", dpi=110)
    print("Saved results/summary.png")


if __name__ == "__main__":
    main()
