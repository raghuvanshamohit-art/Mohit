"""
Run the Nifty Next 50 top-10 momentum backtest end to end and write outputs
(charts, CSVs, summary JSON) to results/.
"""

from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import data
import backtest as bt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
os.makedirs(OUT, exist_ok=True)


def fmt(d: dict) -> str:
    return "\n".join(f"  {k:>22}: {v}" for k, v in d.items())


def main():
    uni = data.get_universe()
    prices = data.build_price_panel(uni["symbol"].tolist(), years=21)
    prices = prices.dropna(how="all")

    # ---- main strategy (with realistic costs) ----
    cfg = bt.BacktestConfig(top_n=10, lookback_m=12, skip_recent_m=0,
                            cost_bps_per_side=20.0)
    res = bt.run_backtest(prices, cfg)

    # ---- variants for context ----
    res_nocost = bt.run_backtest(prices, bt.BacktestConfig(cost_bps_per_side=0.0))
    res_12_1 = bt.run_backtest(prices, bt.BacktestConfig(skip_recent_m=1,
                                                         cost_bps_per_side=20.0))

    # ---- benchmarks aligned to the strategy window ----
    nifty = data.fetch_benchmark("^NSEI", years=21)
    bench_nifty = bt.benchmark_from_index(nifty, res.monthly_returns)
    bench_ew = bt.equal_weight_buyhold(prices, res.monthly_returns)

    # ================= console summary =================
    print("\n" + "=" * 64)
    print("NIFTY NEXT 50  |  TOP-10 12-MONTH MOMENTUM  |  MONTHLY REBALANCE")
    print("=" * 64)
    print(f"\nStrategy (net of {cfg.cost_bps_per_side:.0f} bps/side costs):")
    print(fmt(res.stats))

    print("\nComparison — CAGR / MaxDD / Sharpe:")
    rows = {
        "Strategy (net costs)": res.stats,
        "Strategy (gross)": res_nocost.stats,
        "Strategy 12-1 variant": res_12_1.stats,
    }
    print(f"  {'':28}{'CAGR%':>8}{'MaxDD%':>9}{'Vol%':>8}{'Sharpe':>8}")
    for name, s in rows.items():
        print(f"  {name:28}{s['CAGR_pct']:>8}{s['max_drawdown_pct']:>9}"
              f"{s['annual_vol_pct']:>8}{s['sharpe']:>8}")
    if bench_nifty is not None and len(bench_nifty):
        s = bt.series_stats(bench_nifty)
        print(f"  {'Nifty 50 (price index)':28}{s['CAGR_pct']:>8}"
              f"{s['max_drawdown_pct']:>9}{s['annual_vol_pct']:>8}{s['sharpe']:>8}")
    s = bt.series_stats(bench_ew)
    print(f"  {'Next50 equal-wt buy&hold':28}{s['CAGR_pct']:>8}"
          f"{s['max_drawdown_pct']:>9}{s['annual_vol_pct']:>8}{s['sharpe']:>8}")

    print("\nYear-by-year strategy return (%):")
    yr = res.yearly["return_pct"]
    print("  " + "  ".join(f"{y}:{v:+.0f}" for y, v in yr.items()))

    # ================= save artifacts =================
    res.monthly_returns.to_csv(os.path.join(OUT, "monthly_returns.csv"))
    res.equity.to_frame("equity").to_csv(os.path.join(OUT, "equity_curve.csv"))
    res.drawdown.to_frame("drawdown").to_csv(os.path.join(OUT, "drawdown.csv"))
    res.holdings.to_csv(os.path.join(OUT, "holdings_history.csv"))
    res.yearly.to_csv(os.path.join(OUT, "yearly_returns.csv"))
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump({
            "strategy_net": res.stats,
            "strategy_gross": res_nocost.stats,
            "strategy_12_1": res_12_1.stats,
            "benchmark_nifty50": bt.series_stats(bench_nifty) if bench_nifty is not None else None,
            "benchmark_ew_buyhold": bt.series_stats(bench_ew),
        }, f, indent=2)

    _plot(res, bench_nifty, bench_ew, cfg)
    print(f"\nSaved charts and CSVs to {OUT}/")


def _plot(res, bench_nifty, bench_ew, cfg):
    eq = res.equity
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 8), sharex=True,
        gridspec_kw={"height_ratios": [3, 1]})

    ax1.plot(eq.index, eq.values, lw=2, color="#1f77b4",
             label="Top-10 momentum (net costs)")
    if bench_nifty is not None and len(bench_nifty):
        bn = (1 + bench_nifty).cumprod()
        bn = bn / bn.iloc[0]
        ax1.plot(bn.index, bn.values, lw=1.5, color="#7f7f7f",
                 label="Nifty 50 (price index)")
    bew = (1 + bench_ew).cumprod()
    bew = bew / bew.iloc[0]
    ax1.plot(bew.index, bew.values, lw=1.5, color="#2ca02c", alpha=0.8,
             label="Next 50 equal-weight buy & hold")

    ax1.set_yscale("log")
    ax1.set_ylabel("Growth of ₹1 (log scale)")
    ax1.set_title("Nifty Next 50 — Top-10 12-Month Momentum, Monthly Rebalance"
                  f"  |  CAGR {res.stats['CAGR_pct']}%  "
                  f"MaxDD {res.stats['max_drawdown_pct']}%")
    ax1.legend(loc="upper left")
    ax1.grid(True, which="both", alpha=0.25)

    ax2.fill_between(res.drawdown.index, res.drawdown.values * 100, 0,
                     color="#d62728", alpha=0.4)
    ax2.set_ylabel("Drawdown %")
    ax2.set_xlabel("Year")
    ax2.grid(True, alpha=0.25)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "equity_curve.png"), dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    main()
