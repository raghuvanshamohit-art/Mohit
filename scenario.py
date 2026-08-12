"""
Saw-tooth market scenario: Nifty 50 cycles +37% / -17% (with occasional
sideways years), and we translate each yearly Nifty move into the momentum
strategy's move using the measured sensitivity (up-capture ~1.3-1.4x,
down-capture that is kind in mild dips but NOT in real corrections).

The whole point: alternating +37/-17 does NOT compound at 37%. The -17% legs
create volatility drag. This shows the realistic bumpy path of Rs 12 lakh.
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

# A ~12-year Nifty 50 saw-tooth: bull, bear, bull, bear, ... "sometimes sideways"
NIFTY_PATH = [0.37, -0.17, 0.37, -0.17, 0.04, 0.37, -0.17, 0.37, -0.17, -0.03, 0.37, -0.17]


def strat_return(nifty_ret: float, up_mult: float, down_mult: float,
                 side_alpha: float) -> float:
    """Map a yearly Nifty return to the strategy's yearly return."""
    if nifty_ret >= 0.15:            # bull year: amplify
        return up_mult * nifty_ret
    if nifty_ret <= -0.10:           # real correction: little/no protection
        return down_mult * nifty_ret
    return nifty_ret + side_alpha    # sideways: small momentum alpha


def lakh(x):
    return f"Rs {x/1e7:.2f} cr" if x >= 1e7 else f"Rs {x/1e5:.1f} L"


def run_path(up_mult, down_mult, side_alpha):
    nifty_eq = [START]
    strat_eq = [START]
    strat_rets = []
    for nr in NIFTY_PATH:
        sr = strat_return(nr, up_mult, down_mult, side_alpha)
        strat_rets.append(sr)
        nifty_eq.append(nifty_eq[-1] * (1 + nr))
        strat_eq.append(strat_eq[-1] * (1 + sr))
    return np.array(nifty_eq), np.array(strat_eq), np.array(strat_rets)


def cagr(eq):
    n = len(eq) - 1
    return (eq[-1] / eq[0]) ** (1 / n) - 1


def max_dd(eq):
    peak = np.maximum.accumulate(eq)
    return (eq / peak - 1).min()


def main():
    print(f"Start: {lakh(START)}   |   {len(NIFTY_PATH)}-year saw-tooth "
          "(+37 / -17 with 2 sideways years)\n")

    # base case: momentum edge holds; harsh case: no downside defence
    cases = {
        "BASE  (up 1.40x, down 0.78x)": (1.40, 0.78, 0.02),
        "HARSH (up 1.30x, down 1.15x)": (1.30, 1.15, 0.00),
    }

    results = {}
    for name, (u, d, a) in cases.items():
        neq, seq, srets = run_path(u, d, a)
        results[name] = (neq, seq)
        print(f"{name}")
        print(f"  Strategy yearly returns: "
              f"{'  '.join(f'{r*100:+.0f}' for r in srets)}")
        print(f"  Final value : {lakh(seq[-1])}  ({seq[-1]/START:.1f}x)")
        print(f"  Eff. CAGR   : {cagr(seq)*100:.1f}%   "
              f"(Nifty path CAGR {cagr(neq)*100:.1f}%)")
        print(f"  Worst drawdown along the way : {max_dd(seq)*100:.0f}%\n")

    # reference: what "naive 37% every year" would wrongly imply
    naive = START * 1.37 ** len(NIFTY_PATH)
    print(f"For contrast, naive '+37% every year' would say: {lakh(naive)} "
          f"({naive/START:.0f}x) -- the fantasy the saw-tooth destroys.\n")

    _plot(results)
    print(f"Saved chart to {OUT}/scenario.png")


def _plot(results):
    years = np.arange(0, len(NIFTY_PATH) + 1)
    fig, ax = plt.subplots(figsize=(11, 6.5))
    (neq, seq_base) = results["BASE  (up 1.40x, down 0.78x)"]
    (_, seq_harsh) = results["HARSH (up 1.30x, down 1.15x)"]

    ax.plot(years, seq_base / 1e5, "-o", color="#1f77b4", lw=2.2,
            label=f"Strategy — base case  (end {seq_base[-1]/1e5:.0f} L)")
    ax.plot(years, seq_harsh / 1e5, "-o", color="#ff7f0e", lw=2.0,
            label=f"Strategy — harsh case  (end {seq_harsh[-1]/1e5:.0f} L)")
    ax.plot(years, neq / 1e5, "-s", color="#7f7f7f", lw=1.8, alpha=0.8,
            label=f"Nifty 50 path  (end {neq[-1]/1e5:.0f} L)")
    ax.axhline(START / 1e5, color="#aaa", ls="--", lw=1)

    ax.set_xlabel("Year")
    ax.set_ylabel("Portfolio value (Rs lakh)")
    ax.set_title("Rs 12 lakh through a +37% / -17% saw-tooth market\n"
                 "Alternating boom/bust does NOT compound at 37% — "
                 "the down-legs create drag")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "scenario.png"), dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    main()
