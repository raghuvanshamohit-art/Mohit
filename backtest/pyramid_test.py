#!/usr/bin/env python3
"""
Pyramiding: add to winners as they run. Base = the exact screen:
  entry = upper Bollinger breakout (50,2) + RS ratio > 0.2, market cap 1000-20000 cr,
  4% base sizing, 20% ratcheting trailing stop, weekly.
Adds a tranche each time a position gains another +X% from its ORIGINAL entry
(pyr_trigger), up to pyr_max adds, funded from cash with PRIORITY over new entries.
The same ratcheting trailing stop exits the whole (base + added) position -> that
is the "when to exit if it fails" answer. Cached, in-sample, survivorship-biased.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt
bt.BB_LEN = 50
import calmar_experiments as ce
import marketcap_test as mt

def run(symbols, data, master, name, **pyr):
    r = bt.simulate(symbols, data, master, bt.EXIT_MODES["ATR trail only"],
                    trail_type="pct", pct_trail=0.20, rs_entry=True, rs_thresh=0.2,
                    size_mode="fixed", max_pos=50, mcap_lo=1000, mcap_hi=20000, **pyr)
    m = bt.metrics(r["curve"], periods_per_year=52); t = bt.trade_stats(r["trades"])
    print(f"{name:40s} CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  Calmar {m['calmar']:.2f}  "
          f"Sharpe {m['sharpe']:.2f}  Trades {t['n']:4d}  ₹{m['end_v']:,.0f}", flush=True)
    return name, m, t, r["curve"]

def main():
    symbols, data, master = ce.setup()
    mt.annotate_mcap(data, {s: v for s, v in mt.fetch_marketcaps(sorted(set(symbols))).items()})
    bt.annotate_rs(data, symbols, lookback=26, index_sym="%5ECRSLDX", mode="ratio")
    bt.POS_PCT = 0.04
    rows = []
    rows.append(run(symbols, data, master, "No pyramid (base 4%, 20% trail)"))
    rows.append(run(symbols, data, master, "+100%: add 4%, once",        pyramid=True, pyr_trigger=1.0, pyr_size=0.04, pyr_max=1))
    rows.append(run(symbols, data, master, "+100%: add 4%, up to 2x",    pyramid=True, pyr_trigger=1.0, pyr_size=0.04, pyr_max=2))
    rows.append(run(symbols, data, master, "+100%: add 4%, up to 3x",    pyramid=True, pyr_trigger=1.0, pyr_size=0.04, pyr_max=3))
    rows.append(run(symbols, data, master, "+100%: add 2% (half), 2x",   pyramid=True, pyr_trigger=1.0, pyr_size=0.02, pyr_max=2))
    rows.append(run(symbols, data, master, "+50%: add 4%, up to 3x",     pyramid=True, pyr_trigger=0.5, pyr_size=0.04, pyr_max=3))
    bt.POS_PCT = 0.02; bt.BB_LEN = 52

    best = max(rows, key=lambda x: x[1]["end_v"])
    n500 = [x for x in bt.fetch_weekly("%5ECRSLDX") if x[0] >= master[0]]
    n500c = [(x[0], bt.INIT_CAPITAL * x[4] / n500[0][4]) for x in n500]
    bt.make_svg([(f"{rows[0][0]} (₹{rows[0][1]['end_v']/1e7:.1f}cr)", "#9ca3af", rows[0][3]),
                 (f"{best[0]} (₹{best[1]['end_v']/1e7:.1f}cr)", "#2563eb", best[3]),
                 ("Nifty 500 buy&hold", "#f59e0b", n500c)],
                os.path.join(bt.OUTDIR, "results", "pyramid_equity.svg"),
                "Pyramiding into winners vs base (Rs 20L, log scale)")

    yrs = (master[-1] - master[0]).days / 365.25
    L = ["# Pyramiding — adding to winners\n",
         "> Base: breakout (BB 50,2) + RS ratio > 0.2 + market cap ₹1000–20000 cr + 4% base sizing + "
         "20% ratcheting trailing stop, weekly. Each **add** buys another tranche when the position "
         "gains another +X% from its original entry; the same trailing stop then exits the whole "
         "position. Adds get cash priority over new entries. Cached, in-sample, survivorship-biased. "
         f"Window {master[0]} → {master[-1]} ({yrs:.1f} yrs).\n",
         "## Results\n",
         "| Setup | CAGR | Max DD | Calmar | Sharpe | Trades | Final |",
         "|---|--:|--:|--:|--:|--:|--:|"]
    for name, m, t, _ in rows:
        star = " ⭐" if name == best[0] else ""
        L.append(f"| {name}{star} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} | "
                 f"{m['sharpe']:.2f} | {t['n']} | ₹{m['end_v']:,.0f} |")
    L += ["",
          "## How pyramiding works here (answering the questions)\n",
          "- **When to add:** each time an open position gains another **+100%** from its original "
          "entry (i.e. at 2×, 3×, 4× entry), buy another **4%** tranche (or a smaller half-tranche).",
          "- **Where the money comes from:** adds are funded from available cash with **priority over "
          "new entries** — so freed exit cash flows into proven winners first (your Option A). You can "
          "also just deploy fresh SIP cash the same way.",
          "- **How long you keep adding:** up to `pyr_max` times (test 1–3). More adds = more upside "
          "but more concentration and deeper drawdown.",
          "- **When to exit if it fails:** you do NOT need a new rule — the **same 20% ratcheting "
          "trailing stop governs the whole position**, base + all adds. When the weekly close falls "
          "20% below the position's ratcheted high, everything sells. Because the stop has ratcheted "
          "up near the price by the time you add, each added tranche only risks ~one trail-width "
          "(≈20%) of itself.\n",
          "## ⚠️ Caveats\n",
          "- In-sample, survivorship-biased. Pyramiding concentrates the book into fewer names, so it "
          "**raises drawdown** as well as return — watch the Calmar column, not just CAGR. Adding at "
          "2×/3× means buying high; the trailing stop is what makes it safe.\n",
          "*Generated by `backtest/pyramid_test.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "PYRAMID.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\nWrote docs/PYRAMID.md and backtest/results/pyramid_equity.svg")

if __name__ == "__main__":
    main()
