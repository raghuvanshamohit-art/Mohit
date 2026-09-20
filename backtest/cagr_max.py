#!/usr/bin/env python3
"""
Maximise CAGR (accepting higher drawdown). Base = the highest-return corner found
across all sweeps: breakout (BB 50,2) + RS ratio > 0.2 + market cap 1000-10000 cr
+ 20% ratcheting trailing stop (widest = lets winners run), weekly.
Pushes the CAGR levers: position size / concentration, momentum ranking when
concentrated, and trail width. Reports CAGR (primary) with drawdown as the cost.
Cached, in-sample, survivorship-biased.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt
bt.BB_LEN = 50
import calmar_experiments as ce
import marketcap_test as mt

def run(symbols, data, master, name, pos, pct_trail=0.20, rank="strength"):
    bt.POS_PCT = pos
    r = bt.simulate(symbols, data, master, bt.EXIT_MODES["ATR trail only"],
                    trail_type="pct", pct_trail=pct_trail, rs_entry=True, rs_thresh=0.2,
                    size_mode="fixed", max_pos=50, mcap_lo=1000, mcap_hi=10000, rank_by=rank)
    m = bt.metrics(r["curve"], periods_per_year=52); t = bt.trade_stats(r["trades"])
    print(f"{name:34s} CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  Calmar {m['calmar']:.2f}  "
          f"Sharpe {m['sharpe']:.2f}  Trades {t['n']:4d}  ₹{m['end_v']:,.0f}", flush=True)
    return name, m, t, r["curve"]

def main():
    symbols, data, master = ce.setup()
    mt.annotate_mcap(data, {s: v for s, v in mt.fetch_marketcaps(sorted(set(symbols))).items()})
    bt.annotate_rs(data, symbols, lookback=26, index_sym="%5ECRSLDX", mode="ratio")
    rows = []
    rows.append(run(symbols, data, master, "4% (~25 names) ref",        0.04))
    rows.append(run(symbols, data, master, "6.25% (~16 names)",         0.0625))
    rows.append(run(symbols, data, master, "8% (~12 names)",            0.08))
    rows.append(run(symbols, data, master, "10% (~10 names)",           0.10))
    rows.append(run(symbols, data, master, "10% + momentum rank",       0.10, rank="mom"))
    rows.append(run(symbols, data, master, "12.5% (~8) + momentum",     0.125, rank="mom"))
    rows.append(run(symbols, data, master, "20% (~5) + momentum",       0.20, rank="mom"))
    rows.append(run(symbols, data, master, "8% + 30% trail (max ride)", 0.08, pct_trail=0.30))
    rows.append(run(symbols, data, master, "10% + 30% trail + momentum",0.10, pct_trail=0.30, rank="mom"))
    bt.POS_PCT = 0.02; bt.BB_LEN = 52

    best = max(rows, key=lambda x: x[1]["cagr"])
    n500 = [x for x in bt.fetch_weekly("%5ECRSLDX") if x[0] >= master[0]]
    n500c = [(x[0], bt.INIT_CAPITAL * x[4] / n500[0][4]) for x in n500]
    bt.make_svg([(f"{rows[0][0]} CAGR {rows[0][1]['cagr']*100:.0f}%", "#9ca3af", rows[0][3]),
                 (f"MAX: {best[0]} CAGR {best[1]['cagr']*100:.0f}%", "#2563eb", best[3]),
                 ("Nifty 500 buy&hold", "#f59e0b", n500c)],
                os.path.join(bt.OUTDIR, "results", "cagr_max_equity.svg"),
                "Maximising CAGR: concentration & trail (Rs 20L, log)")

    yrs = (master[-1] - master[0]).days / 365.25
    L = ["# Maximising CAGR (accepting higher drawdown)\n",
         "> Base: breakout (BB 50,2) + RS ratio > 0.2 + market cap ₹1000–10000 cr + 20% ratcheting "
         "trailing stop, weekly. Pushing concentration (position size), momentum ranking, and trail "
         "width. **CAGR up = drawdown up.** Cached, in-sample, survivorship-biased. "
         f"Window {master[0]} → {master[-1]} ({yrs:.1f} yrs).\n",
         "## Results (sorted by CAGR)\n",
         "| Setup | **CAGR** | Max DD | Calmar | Sharpe | Trades | Final |",
         "|---|--:|--:|--:|--:|--:|--:|"]
    for name, m, t, _ in sorted(rows, key=lambda x: -x[1]["cagr"]):
        star = " ⭐" if name == best[0] else ""
        L.append(f"| {name}{star} | **{m['cagr']*100:.1f}%** | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} | "
                 f"{m['sharpe']:.2f} | {t['n']} | ₹{m['end_v']:,.0f} |")
    L += ["",
          "## The levers that raise CAGR (in order of impact)\n",
          "1. **Concentration (bigger position size / fewer names).** Going from 4% (~25 names) toward "
          "8–12% (~8–12 names) raises CAGR — you back your best ideas harder — but drawdown climbs fast.",
          "2. **Momentum entry ranking** — when concentrated and cash-limited, take the strongest RS "
          "names first; helps CAGR at high concentration.",
          "3. **Wider trailing stop (20–30%)** — gives winners maximum room, catching the full "
          "multibagger run (at the cost of giving back more before exiting).",
          "4. **Small-cap universe (₹1000–10000 cr)** — the highest-return slice.\n",
          "## ⚠️ The cost / the honest warning\n",
          "- **Maximising CAGR maximises drawdown and fragility.** Concentrated small-cap books can "
          "swing 30–45%+ and hinge on a handful of names.",
          "- **Survivorship bias is worst exactly here** — concentrated small-cap CAGR is the most "
          "inflated number in the whole study; real-world (with the failed small-caps, gaps, and "
          "single-stock blow-ups a backtest can't see) it would be far lower and far riskier.",
          "- A concentrated small-cap position that gaps down through the stop (news, fraud, "
          "circuit-lock) can lose far more than the trail suggests — the backtest assumes clean fills.",
          "- **Practical stance:** chase CAGR with *moderate* concentration (say 6–8%, momentum-ranked, "
          "20% trail) and treat the number as a ceiling; the Calmar-optimal 4% / 10% trail is the "
          "safer wealth-builder.\n",
          "*Generated by `backtest/cagr_max.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "CAGR_MAX.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\nWrote docs/CAGR_MAX.md and backtest/results/cagr_max_equity.svg")

if __name__ == "__main__":
    main()
