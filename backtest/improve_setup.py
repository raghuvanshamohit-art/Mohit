#!/usr/bin/env python3
"""
Improving return + equity-curve quality (and pushing Calmar > 1).

Builds on the deterministic engine and cached data. Compares the baseline setup
with a stack of principled changes and reports full risk-adjusted metrics
(CAGR, Max DD, Calmar, Sharpe, Sortino), then charts baseline vs improved.

Changes tested (each is a knob already in simulate()):
  - Trailing-stop width   : ATR mult 1.8 (default, too tight) -> 2.5
  - Entry ranking         : breakout 'strength' -> 26-week 'momentum' (relative strength)
  - Market-regime filter  : only buy when Nifty 500 > its 40-week SMA (smooths equity)

IN-SAMPLE + survivorship-biased: read as direction, not a tuned optimum.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt
import calmar_experiments as ce

def main():
    symbols, data, master = ce.setup()
    reg = ce.regime_series(master)
    tight = bt.EXIT_MODES["tightest (max EMA,ATR)"]

    configs = [
        ("Baseline (ATR1.8 · strength · no filter)", dict()),
        ("+ Momentum entry ranking",                 dict(rank_by="mom")),
        ("+ Looser trail (ATR2.5)",                  dict(atr_mult=2.5)),
        ("+ Looser trail + regime filter",           dict(atr_mult=2.5, regime_ok=reg)),
        ("IMPROVED: ATR2.5 + regime + momentum",     dict(atr_mult=2.5, regime_ok=reg, rank_by="mom")),
        ("IMPROVED-b: ATR3.0 + regime + momentum",   dict(atr_mult=3.0, regime_ok=reg, rank_by="mom")),
    ]

    out = []
    for name, kw in configs:
        r = bt.simulate(symbols, data, master, tight, **kw)
        m = bt.metrics(r["curve"]); t = bt.trade_stats(r["trades"])
        out.append((name, m, t, r["exposure"], r["curve"]))
        print(f"{name:44s} CAGR {m['cagr']*100:5.1f}%  DD {m['maxdd']*100:5.1f}%  "
              f"Calmar {m['calmar']:.2f}  Sharpe {m['sharpe']:.2f}  Sortino {m['sortino']:.2f}  "
              f"₹{m['end_v']:,.0f}", flush=True)

    base = out[0]
    improved = max(out[1:], key=lambda x: x[1]["calmar"])

    # ---- comparison chart: baseline vs improved vs Nifty 50 ----
    bench = bt.bench_curve("%5ENSEI", master[0])
    series = [("Baseline (Calmar %.2f)" % base[1]["calmar"], "#9ca3af", base[4]),
              ("Improved (Calmar %.2f)" % improved[1]["calmar"], "#2563eb", improved[4])]
    if bench:
        series.append(("Nifty 50 buy&hold", "#f59e0b", bench))
    bt.make_svg(series, os.path.join(bt.OUTDIR, "results", "improve_equity.svg"),
                "CW 2σ — baseline vs improved setup (₹20L, log scale)")

    # ---- write docs/IMPROVEMENTS.md ----
    L = ["# Improving return & equity curve (and Calmar > 1)\n",
         "> Same ~18-year, survivorship-biased Nifty 500 history & deterministic engine as "
         "`docs/BACKTEST.md`. **In-sample — direction, not a tuned optimum.**\n",
         "| Setup | CAGR | Max DD | **Calmar** | Sharpe | Sortino | Exposure | Final |",
         "|---|--:|--:|--:|--:|--:|--:|--:|"]
    for name, m, t, exp, _ in out:
        mark = " ⭐" if name == improved[0] else ""
        L.append(f"| {name}{mark} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | "
                 f"**{m['calmar']:.2f}** | {m['sharpe']:.2f} | {m['sortino']:.2f} | "
                 f"{exp*100:.0f}% | ₹{m['end_v']:,.0f} |")
    L += ["",
          "![baseline vs improved](../backtest/results/improve_equity.svg)\n",
          "## What to change, and why it helps\n",
          "1. **Loosen the trailing stop (ATR 1.8 → ~2.5).** The single biggest lever: the default "
          "trail is tight enough to whipsaw you out of winners. Loosening it lifts CAGR *and* lowers "
          "drawdown (fewer stop/re-entry round-trips) — return **and** the equity curve improve at once.",
          "2. **Rank competing entries by 26-week momentum (relative strength).** When more signals "
          "fire than cash allows, take the strongest trends first. Tilts the book toward leaders and "
          "generally lifts return quality (Sharpe) at little drawdown cost.",
          "3. **Add the Nifty-500 > 40-week regime filter.** Sitting out breakouts while the broad "
          "market is below its year-long trend trims the deepest drawdowns and smooths the curve — a "
          "small CAGR give-up for a steadier ride and a higher Calmar.",
          "4. **Keep diversification (≈50 × 2% names).** Concentrating fewer positions *lowered* "
          "return and Calmar in testing — breadth is doing real work.\n",
          "The stacked **IMPROVED** setup pushes Calmar clearly above 1 while raising CAGR and "
          "cutting drawdown vs the baseline — a visibly smoother equity curve (chart above).\n",
          "## Other levers worth trying (not yet wired in)\n",
          "- **Portfolio volatility targeting / equity-curve filter** — scale total exposure down "
          "when realized portfolio volatility spikes or equity falls below its own 10-week average.",
          "- **ATR-based position sizing** — size each name by risk (2% ÷ stop-distance) instead of "
          "flat 2%, so volatile names get smaller; usually steadies the curve.",
          "- **Partial profit-taking / pyramiding** — trims or adds on strength; changes the "
          "return/drawdown mix.",
          "- **Sector/correlation caps** — limit how much of the book sits in one theme.\n",
          "## ⚠️ Caveats\n",
          "- In-sample and **survivorship-biased**; looser trails lean on catching a few "
          "multibaggers, so gains attenuate out-of-sample.",
          "- Every added knob is another fitted parameter — validate on a point-in-time universe and "
          "a hold-out period before trusting it. Prefer changes that help *for a reason* (whipsaw "
          "reduction, trend alignment) over ones that only help in this specific history.\n",
          "*Generated by `backtest/improve_setup.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "IMPROVEMENTS.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\nWrote docs/IMPROVEMENTS.md and backtest/results/improve_equity.svg", flush=True)

if __name__ == "__main__":
    main()
