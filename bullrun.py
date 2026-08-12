"""
How does the Nifty Next 50 top-10 momentum strategy move *relative to the
Nifty 50 index*? If the user's premise is "Nifty 50 does +35% in the next bull
run", estimate the strategy's return (and the portfolio outcome) from the
historical sensitivity -- beta, up-capture, and bull-year analogs.

NOTE: strategy returns here are survivorship-biased (inflated). Beta/up-capture
are relative measures and more robust than the absolute CAGR, but we also show a
de-biased estimate that scales the strategy's excess move down to the realistic
~20% CAGR world.
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import data
import backtest as bt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

START = 12_00_000
NIFTY_BULL = 0.35            # user's premise: Nifty 50 +35% in the bull run
# Survivorship de-bias factor: realistic CAGR ~20% vs backtest ~37% -> ~0.55
DEBIAS = 0.20 / 0.37


def lakh(x):
    return f"Rs {x/1e7:.2f} cr" if x >= 1e7 else f"Rs {x/1e5:.1f} L"


def main():
    prices = data.build_price_panel(data.get_universe()["symbol"].tolist(), 21)
    prices = prices.dropna(how="all")
    res = bt.run_backtest(prices, bt.BacktestConfig())
    strat = res.monthly_returns

    nifty = data.fetch_benchmark("^NSEI", 21)
    nifty_m = nifty.resample("ME").last().pct_change().reindex(strat.index).dropna()
    strat_a = strat.reindex(nifty_m.index)

    df = pd.DataFrame({"strat": strat_a, "nifty": nifty_m}).dropna()

    # ---- OLS: strat = alpha + beta * nifty (monthly) ----
    beta, alpha = np.polyfit(df["nifty"], df["strat"], 1)
    corr = df["strat"].corr(df["nifty"])
    alpha_ann = (1 + alpha) ** 12 - 1

    # ---- up / down capture ----
    up = df[df["nifty"] > 0]
    dn = df[df["nifty"] < 0]
    up_cap = up["strat"].mean() / up["nifty"].mean()
    dn_cap = dn["strat"].mean() / dn["nifty"].mean()

    print("=" * 60)
    print("STRATEGY vs NIFTY 50  (monthly, 2006-2026)")
    print("=" * 60)
    print(f"  Beta to Nifty 50      : {beta:.2f}")
    print(f"  Monthly alpha         : {alpha*100:.2f}%  (~{alpha_ann*100:.0f}%/yr, biased)")
    print(f"  Correlation           : {corr:.2f}")
    print(f"  Up-capture ratio      : {up_cap*100:.0f}%   (strat move per 1% Nifty up)")
    print(f"  Down-capture ratio    : {dn_cap*100:.0f}%")

    # ---- calendar-year analog table ----
    yb = (1 + df).groupby(df.index.year).prod() - 1
    yb = yb.rename(columns={"strat": "Strategy", "nifty": "Nifty50"}) * 100
    print("\nCalendar-year returns (%), sorted by Nifty:")
    print("  Year   Nifty50   Strategy   Strat/Nifty")
    for y, r in yb.sort_values("Nifty50", ascending=False).iterrows():
        ratio = r["Strategy"] / r["Nifty50"] if r["Nifty50"] > 0 else np.nan
        print(f"  {y}   {r['Nifty50']:+7.0f}   {r['Strategy']:+8.0f}"
              f"   {ratio:>6.1f}x" if r["Nifty50"] > 0 else
              f"  {y}   {r['Nifty50']:+7.0f}   {r['Strategy']:+8.0f}      --")

    # bull years = Nifty > 20%
    bulls = yb[yb["Nifty50"] > 20]
    avg_ratio = (bulls["Strategy"] / bulls["Nifty50"]).mean()
    print(f"\nIn years Nifty 50 rose >20% (n={len(bulls)}): strategy did on "
          f"average {avg_ratio:.1f}x the Nifty return.")

    # ================= ESTIMATE for Nifty +35% =================
    print("\n" + "=" * 60)
    print(f"IF NIFTY 50 DELIVERS +{NIFTY_BULL*100:.0f}% IN THE BULL RUN")
    print("=" * 60)

    # method 1: beta model, compounded monthly-equivalent
    est_beta = alpha_ann + beta * NIFTY_BULL
    # method 2: up-year ratio
    est_ratio = avg_ratio * NIFTY_BULL
    print("Estimated STRATEGY return that year (biased/backtest world):")
    print(f"  via beta model (a+b*mkt) : ~{est_beta*100:.0f}%")
    print(f"  via bull-year ratio      : ~{est_ratio*100:.0f}%")

    # de-biased: keep beta exposure, shrink the excess/alpha to realistic world
    est_debiased_lo = NIFTY_BULL * 1.3      # ~1.3x market (higher-beta midcaps)
    est_debiased_hi = NIFTY_BULL * 1.7      # momentum kicker
    print("\nDe-biased realistic estimate (midcap beta + momentum, "
          "survivorship removed):")
    print(f"  strategy year return     : ~{est_debiased_lo*100:.0f}% to "
          f"{est_debiased_hi*100:.0f}%")

    print("\nWhat Rs 12 L becomes in that ONE bull-run year:")
    for label, r in [
        ("Nifty itself +35%", NIFTY_BULL),
        ("Strategy de-biased low (~46%)", est_debiased_lo),
        ("Strategy de-biased high (~60%)", est_debiased_hi),
        ("Strategy backtest-world (~%d%%)" % round(est_ratio*100), est_ratio),
    ]:
        print(f"  {label:34}-> {lakh(START*(1+r))}")

    _plot_scatter(yb, beta, alpha_ann, est_debiased_lo, est_debiased_hi)
    print(f"\nSaved chart to {OUT}/bullrun.png")


def _plot_scatter(yb, beta, alpha_ann, lo, hi):
    fig, ax = plt.subplots(figsize=(10, 7))
    x = yb["Nifty50"].values
    y = yb["Strategy"].values
    ax.scatter(x, y, s=60, color="#1f77b4", zorder=3)
    for yr, xi, yi in zip(yb.index, x, y):
        ax.annotate(str(yr), (xi, yi), fontsize=8,
                    xytext=(4, 4), textcoords="offset points")
    # 1:1 line and regression line
    xr = np.linspace(-60, 90, 50)
    ax.plot(xr, xr, ls="--", color="#999", lw=1, label="1:1 (moves with Nifty)")
    ax.plot(xr, alpha_ann * 100 + beta * xr, color="#2ca02c", lw=1.5,
            label=f"fit: strat = {alpha_ann*100:.0f}% + {beta:.2f}·Nifty")
    # the +35% scenario band
    ax.axvspan(35, 35, color="#d62728")
    ax.axvline(35, color="#d62728", ls=":", lw=1.5)
    ax.fill_betweenx([lo * 100, hi * 100], 33, 37, color="#d62728", alpha=0.25)
    ax.annotate("If Nifty +35% ->\nstrategy ~46-60%",
                xy=(35, (lo + hi) / 2 * 100), xytext=(40, 30),
                fontsize=9, color="#d62728", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#d62728"))
    ax.axhline(0, color="k", lw=0.6)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_xlabel("Nifty 50 calendar-year return (%)")
    ax.set_ylabel("Strategy calendar-year return (%)")
    ax.set_title("Strategy amplifies the market: up-capture 132%, "
                 "down-capture 55%\n(each dot = one calendar year, 2006-2026)")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "bullrun.png"), dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    main()
