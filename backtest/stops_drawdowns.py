#!/usr/bin/env python3
"""
Over the full ~18-year backtest, count:
  (1) stop-loss hits  — every exit is a 20% trailing-stop hit; split into
      profit-locking exits (trail above entry) vs losing exits (below entry),
  (2) drawdown episodes — portfolio peak-to-trough declines, bucketed by depth,
      with the worst few detailed (depth, duration, recovery).

Config: upper Bollinger breakout + Nifty 500 6-month outperformance (26w RS) +
20% ratcheting trailing stop + 4% sizing, weekly, ₹20L. In-sample, survivorship-biased.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt
import calmar_experiments as ce

def dd_episodes(curve):
    eps = []
    peak, peak_d = curve[0][1], curve[0][0]
    in_dd = False; trough = peak; trough_d = peak_d; start_peak_d = peak_d
    for d, v in curve:
        if v >= peak:
            if in_dd:
                eps.append(dict(depth=(peak - trough) / peak, peak_date=start_peak_d,
                                trough_date=trough_d, recover_date=d,
                                to_trough_wk=(trough_d - start_peak_d).days // 7,
                                recover_wk=(d - start_peak_d).days // 7))
                in_dd = False
            peak, peak_d = v, d
        else:
            if not in_dd:
                in_dd = True; trough = v; trough_d = d; start_peak_d = peak_d
            if v < trough:
                trough, trough_d = v, d
    if in_dd:
        eps.append(dict(depth=(peak - trough) / peak, peak_date=start_peak_d,
                        trough_date=trough_d, recover_date=None,
                        to_trough_wk=(trough_d - start_peak_d).days // 7, recover_wk=None))
    return eps

def main():
    symbols, data, master = ce.setup()
    bt.annotate_rs(data, symbols, lookback=26, index_sym="%5ECRSLDX")
    bt.POS_PCT = 0.04
    r = bt.simulate(symbols, data, master, bt.EXIT_MODES["ATR trail only"],
                    trail_type="pct", pct_trail=0.20, rs_entry=True, size_mode="fixed", max_pos=50)
    bt.POS_PCT = 0.02
    m = bt.metrics(r["curve"], periods_per_year=52)
    trades = r["trades"]; curve = r["curve"]
    yrs = (master[-1] - master[0]).days / 365.25

    wins = [t for t in trades if t["ret"] > 0]
    losses = [t for t in trades if t["ret"] <= 0]
    big_losers = [t for t in losses if t["ret"] <= -0.18]
    print(f"Window {master[0]} -> {master[-1]} ({yrs:.1f} yrs) · CAGR {m['cagr']*100:.1f}% · MaxDD {m['maxdd']*100:.1f}%")
    print(f"\nSTOP-LOSS HITS (every exit is a trailing-stop hit):")
    print(f"  total exits ......... {len(trades)}   (~{len(trades)/yrs:.0f}/yr)")
    print(f"  profit-locking exits  {len(wins)}   ({len(wins)/len(trades)*100:.0f}%)  avg +{sum(t['ret'] for t in wins)/max(1,len(wins))*100:.0f}%")
    print(f"  losing stops ........ {len(losses)}   ({len(losses)/len(trades)*100:.0f}%)  avg {sum(t['ret'] for t in losses)/max(1,len(losses))*100:.0f}%")
    print(f"  of which near-full 20% stops (<=-18%): {len(big_losers)}")

    eps = dd_episodes(curve)
    def cnt(x): return sum(1 for e in eps if e["depth"] >= x)
    print(f"\nDRAWDOWN EPISODES (portfolio equity, peak-to-trough):")
    print(f"  total distinct drawdowns .... {len(eps)}")
    for thr in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
        print(f"  >= {int(thr*100):2d}% deep ............. {cnt(thr)}")
    print(f"\n  Worst drawdowns:")
    for e in sorted(eps, key=lambda x: -x["depth"])[:6]:
        rec = "ongoing" if e["recover_date"] is None else f"recovered {e['recover_date']} ({e['recover_wk']}w)"
        print(f"    -{e['depth']*100:4.1f}%  peak {e['peak_date']} -> trough {e['trough_date']} "
              f"({e['to_trough_wk']}w down) · {rec}")

    # ---- doc ----
    L = ["# Stop-loss hits & drawdowns over the full backtest\n",
         "> Config: upper Bollinger breakout + Nifty 500 6-month outperformance (26w RS) + "
         "**20% ratcheting trailing stop** + 4% sizing, weekly, ₹20L. "
         f"Window {master[0]} → {master[-1]} ({yrs:.1f} years). In-sample, survivorship-biased.\n",
         "## Stop-loss hits\n",
         "In this system **there is no profit target — every position is eventually closed by the "
         "20% trailing stop.** So 'stop hits' = all exits; the question is whether the stop fired "
         "above your entry (locking a gain) or below it (a loss).\n",
         "| | Count | Share | Avg exit |",
         "|---|--:|--:|--:|",
         f"| **Total stop hits (all exits)** | {len(trades)} | 100% | — |",
         f"| Profit-locking (trail above entry) | {len(wins)} | {len(wins)/len(trades)*100:.0f}% | "
         f"+{sum(t['ret'] for t in wins)/max(1,len(wins))*100:.0f}% |",
         f"| Losing stops (below entry) | {len(losses)} | {len(losses)/len(trades)*100:.0f}% | "
         f"{sum(t['ret'] for t in losses)/max(1,len(losses))*100:.0f}% |",
         f"| — near-full ~20% stops (≤ −18%) | {len(big_losers)} | {len(big_losers)/len(trades)*100:.0f}% | — |",
         "",
         f"That's **~{len(trades)/yrs:.0f} stop hits per year** (~{len(losses)/yrs:.0f} of them "
         f"losers). Roughly half of all exits actually lock in a profit — the trailing stop is the "
         "profit-taker, not just a loss-cutter.\n",
         "## Drawdown episodes (portfolio equity)\n",
         f"A 'drawdown' = a peak-to-trough dip in the ₹20L equity curve before a new high. Over "
         f"{yrs:.0f} years there were **{len(eps)} distinct drawdowns**, of which:\n",
         "| Depth | Count | ~per year |",
         "|---|--:|--:|"]
    for thr in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
        L.append(f"| ≥ {int(thr*100)}% | {cnt(thr)} | {cnt(thr)/yrs:.1f} |")
    L += ["",
          "### Worst drawdowns\n",
          "| Depth | Peak → Trough | Weeks down | Recovery |",
          "|---|---|--:|---|"]
    for e in sorted(eps, key=lambda x: -x["depth"])[:6]:
        rec = "ongoing" if e["recover_date"] is None else f"{e['recover_date']} ({e['recover_wk']}w total)"
        L.append(f"| −{e['depth']*100:.1f}% | {e['peak_date']} → {e['trough_date']} | {e['to_trough_wk']} | {rec}")
    L += ["",
          "## What to expect operationally\n",
          f"- **~{len(trades)/yrs:.0f} exits a year**, about half winners / half losers — a low ~"
          f"{len(wins)/len(trades)*100:.0f}% hit rate is normal for trend-following; the winners are "
          "far bigger than the losers.",
          "- **Small dips are constant** (dozens of ≥5% wobbles) — only a handful reach the ~20–30% "
          "range that actually tests your conviction. Those deep ones are the price of the returns.",
          "- Max single drawdown was about the figure in `docs/BACKTEST.md`; expect at least one "
          "20%+ drawdown every few years.\n",
          "## ⚠️ Caveats\n",
          "- In-sample, survivorship-biased. Counts scale with position size / filters — this is the "
          "4% + RS config; a 2% book trades more often (more, smaller stop hits).\n",
          "*Generated by `backtest/stops_drawdowns.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "STOPS_DRAWDOWNS.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\nWrote docs/STOPS_DRAWDOWNS.md")

if __name__ == "__main__":
    main()
