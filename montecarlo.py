"""
Forward projection driven by the HISTORICAL whipsaw pattern.

The 37% backtest CAGR is already whipsaw-adjusted (it is geometric, taken from
the jagged equity curve). What inflates it is survivorship bias. So we:

  1. Take the strategy's real historical monthly returns (their whipsaw shape:
     fat tails, momentum crashes, drawdown clustering).
  2. Recenter the mean DOWN to a realistic, survivorship-free CAGR target,
     while KEEPING the volatility and the whipsaw structure intact.
  3. Block-bootstrap (12-month blocks) that series forward 10 years, many
     times, so autocorrelation / drawdown clustering is preserved.
  4. Plot the fan of future outcomes for Rs 12 lakh and report the realistic
     CAGR distribution + drawdown probabilities.
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
START = 12_00_000
HORIZON_Y = 10
N_PATHS = 5000
BLOCK = 12                    # months per bootstrap block (preserves whipsaw)
TARGET_CAGR = 0.18           # realistic, survivorship-free central estimate
RNG = np.random.default_rng(42)


def lakh(x):
    return f"Rs {x/1e7:.2f} cr" if x >= 1e7 else f"Rs {x/1e5:.1f} L"


def load_returns():
    df = pd.read_csv(os.path.join(OUT, "monthly_returns.csv"),
                     index_col=0, parse_dates=True)
    return df.iloc[:, 0].dropna().values


def recenter(rets, target_cagr):
    """Shift monthly returns so the geometric annual return hits target,
    keeping volatility and shape unchanged."""
    cur_geo_m = np.exp(np.mean(np.log1p(rets))) - 1          # current monthly geo
    tgt_geo_m = (1 + target_cagr) ** (1 / 12) - 1
    shift = tgt_geo_m - cur_geo_m
    return rets + shift, shift


def block_bootstrap_paths(rets, n_months, n_paths, block):
    n = len(rets)
    n_blocks = int(np.ceil(n_months / block))
    paths = np.empty((n_paths, n_months))
    for p in range(n_paths):
        starts = RNG.integers(0, n, size=n_blocks)
        seq = np.concatenate([np.take(rets, range(s, s + block), mode="wrap")
                              for s in starts])[:n_months]
        paths[p] = seq
    return paths


def max_dd_of_path(equity_row):
    peak = np.maximum.accumulate(equity_row)
    return (equity_row / peak - 1).min()


def main():
    rets = load_returns()
    hist_cagr = np.exp(np.mean(np.log1p(rets)) * 12) - 1
    hist_arith = (1 + np.mean(rets)) ** 12 - 1   # compounded arithmetic mean
    hist_vol = np.std(rets, ddof=1) * np.sqrt(12)

    print("HISTORICAL strategy monthly returns (survivorship-biased):")
    print(f"  Arithmetic mean return (annualised): {hist_arith*100:.1f}%")
    print(f"  Geometric CAGR (whipsaw-adjusted)  : {hist_cagr*100:.1f}%")
    print(f"  => volatility drag from whipsaw    : {(hist_arith-hist_cagr)*100:.1f} pts/yr")
    print(f"  Annualised volatility             : {hist_vol*100:.1f}%\n")

    de_rets, shift = recenter(rets, TARGET_CAGR)
    print(f"Recentred to a realistic {TARGET_CAGR*100:.0f}% CAGR "
          f"(shift {shift*100:.2f}%/mo), whipsaw shape kept.\n")

    n_months = HORIZON_Y * 12
    paths = block_bootstrap_paths(de_rets, n_months, N_PATHS, BLOCK)
    equity = START * np.cumprod(1 + paths, axis=1)
    equity = np.hstack([np.full((N_PATHS, 1), START), equity])

    terminal = equity[:, -1]
    realized_cagr = (terminal / START) ** (1 / HORIZON_Y) - 1
    dd = np.array([max_dd_of_path(equity[i]) for i in range(N_PATHS)])

    pct = lambda a, q: np.percentile(a, q)
    print(f"Rs 12 lakh after {HORIZON_Y} years — distribution of outcomes:")
    for q, name in [(5, "Bad (5th pct)"), (25, "Below-avg (25th)"),
                    (50, "MEDIAN"), (75, "Above-avg (75th)"),
                    (95, "Great (95th pct)")]:
        print(f"  {name:18}: {lakh(pct(terminal, q)):>10}   "
              f"(CAGR {pct(realized_cagr, q)*100:+.1f}%)")

    print(f"\n  Median realized CAGR over 10y : {np.median(realized_cagr)*100:.1f}%")
    print(f"  P(end below starting 12 L)    : {(terminal < START).mean()*100:.0f}%")
    print(f"  P(a >30% drawdown on the way) : {(dd < -0.30).mean()*100:.0f}%")
    print(f"  P(a >50% drawdown on the way) : {(dd < -0.50).mean()*100:.0f}%")
    print(f"  Median worst drawdown         : {np.median(dd)*100:.0f}%")

    _plot_fan(equity)
    print(f"\nSaved chart to {OUT}/montecarlo.png")


def _plot_fan(equity):
    months = np.arange(equity.shape[1])
    yrs = months / 12
    fig, ax = plt.subplots(figsize=(11, 6.8))

    bands = [(5, 95, "#c6dbef"), (25, 75, "#6baed6")]
    for lo, hi, col in bands:
        ax.fill_between(yrs, np.percentile(equity, lo, axis=0) / 1e5,
                        np.percentile(equity, hi, axis=0) / 1e5,
                        color=col, alpha=0.6,
                        label=f"{lo}-{hi}th percentile")
    med = np.percentile(equity, 50, axis=0) / 1e5
    ax.plot(yrs, med, color="#08306b", lw=2.5, label="Median path")

    # a few individual jagged paths to show the whipsaw explicitly
    for i in RNG.integers(0, equity.shape[0], size=4):
        ax.plot(yrs, equity[i] / 1e5, lw=0.9, color="#d62728", alpha=0.55)
    ax.plot([], [], lw=0.9, color="#d62728", alpha=0.7,
            label="Individual simulated paths (whipsaw)")

    ax.axhline(START / 1e5, color="#888", ls="--", lw=1)
    ax.set_yscale("log")
    ax.set_xlabel("Years from now")
    ax.set_ylabel("Portfolio value (Rs lakh, log scale)")
    ax.set_title("Rs 12 lakh projected forward with the historical whipsaw\n"
                 "(block-bootstrap of real monthly returns, recentred to a "
                 "realistic 18% CAGR)")
    ax.legend(loc="upper left")
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "montecarlo.png"), dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    main()
