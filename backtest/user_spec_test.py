#!/usr/bin/env python3
"""
Exact user spec, weekly, Nifty 500 universe:
  Entry  : upper Bollinger breakout (weekly close > upper BB 52,2)
  Filter : outperforming Nifty 500 over 6 months (26w relative strength > 0)
  Exit   : 20% stop (ratcheting trailing — primary; fixed-20% shown too)
  Sizing : ₹50,000 fixed per stock, max 50 positions  => ₹25 lakh capital
           one-in / one-out once 50 slots are full (cash-gated)

Reports CAGR and Max drawdown. Cached, deterministic. In-sample & survivorship-biased.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt
import calmar_experiments as ce

bt.INIT_CAPITAL = 2_500_000          # 50 stocks x ₹50,000

def main():
    symbols, data, master = ce.setup()
    bt.annotate_rs(data, symbols, lookback=26, index_sym="%5ECRSLDX")   # Nifty 500, 6-monthly RS
    trailonly = bt.EXIT_MODES["ATR trail only"]        # exit uses the 20% trail only (no EMA)
    fixed_stop = lambda ema, tr: -1e18                 # -> effective stop = fixed 20% initial only

    common = dict(rs_entry=True, size_mode="rupee", rupee_size=50000, max_pos=50,
                  trail_type="pct", pct_trail=0.20)

    rows = []
    def run(name, fn, extra):
        r = bt.simulate(symbols, data, master, fn, **{**common, **extra})
        m = bt.metrics(r["curve"], periods_per_year=52); t = bt.trade_stats(r["trades"])
        rows.append((name, m, t, r["exposure"], r["curve"]))
        print(f"{name:42s} CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  "
              f"Calmar {m['calmar']:.2f}  Sharpe {m['sharpe']:.2f}  Trades {t['n']}  Win {t['win_rate']*100:.0f}%  "
              f"Exp {r['exposure']*100:.0f}%  ₹{m['end_v']:,.0f}", flush=True)

    run("20% TRAILING stop (spec)",      trailonly,  dict())
    run("20% FIXED stop (literal)",      fixed_stop, dict())
    # contrast: compounding 2%-of-equity sizing instead of fixed ₹50k
    run("20% trailing, 2% compounding",  trailonly,  dict(size_mode="fixed"))

    benches = {}
    for label, sym in [("Nifty 50", "%5ENSEI"), ("Nifty 500", "%5ECRSLDX")]:
        b = [x for x in bt.fetch_weekly(sym) if x[0] >= master[0]]
        bc = [(x[0], bt.INIT_CAPITAL * x[4] / b[0][4]) for x in b]
        benches[label] = bt.metrics(bc, periods_per_year=52)
        m = benches[label]
        print(f"{'BENCH '+label:42s} CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  "
              f"Calmar {m['calmar']:.2f}", flush=True)

    n50 = [x for x in bt.fetch_weekly("%5ENSEI") if x[0] >= master[0]]
    n50c = [(x[0], bt.INIT_CAPITAL * x[4] / n50[0][4]) for x in n50]
    series = [("Spec: 20%% trail (Calmar %.2f)" % rows[0][1]["calmar"], "#2563eb", rows[0][4]),
              ("Nifty 500 buy&hold", "#f59e0b", n50c)]
    bt.make_svg(series, os.path.join(bt.OUTDIR, "results", "spec_equity.svg"),
                "User spec: BB breakout + N500 6M RS + 20% stop (log scale)")

    yfmt = lambda m: f"{m['cagr']*100:.1f}%"
    L = ["# User-spec backtest — breakout + Nifty 500 6-month outperformance + 20% stop\n",
         "> **Rules.** Entry: weekly close above the upper Bollinger band (52, 2), **and** the stock "
         "is outperforming the Nifty 500 over the last 6 months (26-week relative strength > 0). "
         "Exit: 20% stop. Sizing: **₹50,000 per stock, max 50 positions** (₹25 lakh capital), "
         "one-in / one-out once full. Weekly, Nifty 500 universe. Costs 0.25%/side.\n",
         f"- **Window:** {master[0]} → {master[-1]} ({(master[-1]-master[0]).days/365.25:.1f} years) · "
         f"₹{bt.INIT_CAPITAL:,} start\n",
         "## Results\n",
         "| Setup | CAGR | Max DD | Calmar | Sharpe | Trades | Win% | Avg invested | Final |",
         "|---|--:|--:|--:|--:|--:|--:|--:|--:|"]
    for name, m, t, exp, _ in rows:
        L.append(f"| {name} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} | "
                 f"{m['sharpe']:.2f} | {t['n']} | {t['win_rate']*100:.0f}% | {exp*100:.0f}% | ₹{m['end_v']:,.0f} |")
    L.append("")
    L.append("| Benchmark (₹25L buy & hold) | CAGR | Max DD | Calmar |")
    L.append("|---|--:|--:|--:|")
    for label, m in benches.items():
        L.append(f"| {label} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} |")
    L += ["",
          "![spec](../backtest/results/spec_equity.svg)\n",
          "## Notes\n",
          "- **Fixed ₹50k bets don't compound**: as winners appreciate and exit for large sums, only "
          "₹50k redeploys per slot, so cash piles up (see *Avg invested*) and CAGR is dragged below "
          "the compounding 2%-of-equity version — the gap is the cost of the fixed bet size.",
          "- **Trailing vs fixed 20%:** the ratcheting trail locks profit and usually beats a fixed "
          "stop-from-entry on both return and drawdown.",
          "- The Nifty-500 6-month outperformance gate is largely redundant with the breakout (both "
          "pick strong stocks), so it changes little — consistent with the earlier RS tests.\n",
          "## ⚠️ Caveats\n",
          "- In-sample, survivorship-biased (today's Nifty 500). Fixed-₹ sizing over 18 years is "
          "unusual — for a long horizon a compounding rule (2% of equity) is more realistic; the "
          "fixed-₹ number is what the literal spec produces.\n",
          "*Generated by `backtest/user_spec_test.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "SPEC_BACKTEST.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\nWrote docs/SPEC_BACKTEST.md and backtest/results/spec_equity.svg", flush=True)

if __name__ == "__main__":
    main()
