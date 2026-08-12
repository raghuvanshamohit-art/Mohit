"""
Forward projection of a lump-sum invested in the Nifty Next 50 top-10 momentum
strategy. Pure compounding scenarios -- NOT a prediction. Real path includes
50%+ drawdowns and multi-year flat stretches (the reason a live XIRR can sit at
~4% for a year or two even when the long-run CAGR is high).
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)

START = 12_00_000            # current portfolio, INR
RATES = {                    # annual CAGR scenarios
    "Conservative 15%": 0.15,
    "Base 20%": 0.20,
    "Optimistic 25%": 0.25,
    "Backtest 37% (biased)": 0.37,
}
YEARS = [1, 2, 3, 5, 7, 10]


def lakh(x: float) -> str:
    if x >= 1e7:
        return f"Rs {x/1e7:.2f} cr"
    return f"Rs {x/1e5:.1f} L"


def main():
    print(f"Starting capital: {lakh(START)}  (Rs {START:,})\n")
    header = "Horizon".ljust(10) + "".join(n.ljust(24) for n in RATES)
    print(header)
    print("-" * len(header))
    for y in YEARS:
        row = f"{y}y".ljust(10)
        for r in RATES.values():
            fv = START * (1 + r) ** y
            row += f"{lakh(fv)} ({(1+r)**y:.1f}x)".ljust(24)
        print(row)

    # ---- chart ----
    xs = np.linspace(0, 10, 121)
    fig, ax = plt.subplots(figsize=(11, 6.5))
    colors = ["#2ca02c", "#1f77b4", "#ff7f0e", "#9467bd"]
    for (name, r), c in zip(RATES.items(), colors):
        ys = START * (1 + r) ** xs / 1e5
        ax.plot(xs, ys, lw=2.2, color=c, label=f"{name}")
        ax.annotate(lakh(START * (1 + r) ** 10),
                    xy=(10, START * (1 + r) ** 10 / 1e5),
                    xytext=(6, 4), textcoords="offset points",
                    fontsize=9, color=c, fontweight="bold")
    ax.axhline(START / 1e5, color="#888", ls="--", lw=1)
    ax.set_yscale("log")
    ax.set_ylabel("Portfolio value (Rs lakh, log scale)")
    ax.set_xlabel("Years from now")
    ax.set_title(f"Rs {START/1e5:.0f} lakh compounded forward — Nifty Next 50 "
                 "top-10 momentum\n(compounding scenarios, not a forecast; "
                 "real path has 50%+ drawdowns)")
    ax.legend(loc="upper left")
    ax.grid(True, which="both", alpha=0.25)
    ax.set_xlim(0, 10.6)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "projection.png"), dpi=120)
    plt.close(fig)
    print(f"\nSaved chart to {OUT}/projection.png")

    # ---- "one bull-run year then normal" illustration ----
    print("\nNote — a bull run is one strong YEAR, not the average:")
    for bull in (0.60, 0.80, 1.00):
        after1 = START * (1 + bull)
        after3 = after1 * (1.20) ** 2   # then two normal-ish years
        print(f"  +{bull*100:.0f}% bull year -> {lakh(after1)}; "
              f"then +20%/yr for 2 yrs -> {lakh(after3)}")


if __name__ == "__main__":
    main()
