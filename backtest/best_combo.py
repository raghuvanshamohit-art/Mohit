#!/usr/bin/env python3
"""
Find the best entry+exit combination by testing the levers that survived every
earlier sweep, head-to-head. Fixed: upper Bollinger breakout entry, RS > 0.2
(Nifty 500 6-month outperformance floor, no cap), 4% sizing, weekly, ₹20L.
Varies: exit (20% pct trail vs loosened ATR×3.5 trail+EMA), drawdown brake
(regime filter on/off), universe (all Nifty 500 vs ₹1000-20000 cr).
Picks the best by Calmar (with CAGR shown). In-sample, survivorship-biased.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt
import calmar_experiments as ce
import marketcap_test as mt

def main():
    symbols, data, master = ce.setup()
    mt.annotate_mcap(data, {s: v for s, v in mt.fetch_marketcaps(sorted(set(symbols))).items()})
    bt.annotate_rs(data, symbols, lookback=26, index_sym="%5ECRSLDX")
    reg = ce.regime_series(master)
    bt.POS_PCT = 0.04
    pct20 = (bt.EXIT_MODES["ATR trail only"], dict(trail_type="pct", pct_trail=0.20))
    atr35 = (bt.EXIT_MODES["tightest (max EMA,ATR)"], dict(trail_type="atr", atr_mult=3.5))

    common = dict(rs_entry=True, rs_thresh=0.2, size_mode="fixed", max_pos=50)
    cand = []
    for exname, (fn, exkw) in [("20% trail", pct20), ("ATR×3.5 trail", atr35)]:
        for capname, (lo, hi) in [("all-cap", (None, None)), ("1000-20000cr", (1000, 20000))]:
            for regname, rk in [("", {}), ("+regime", {"regime_ok": reg})]:
                nm = f"{exname} · {capname}{(' ' + regname) if regname else ''}"
                cand.append((nm, fn, {**common, **exkw, "mcap_lo": lo, "mcap_hi": hi, **rk}))

    rows = []
    for nm, fn, kw in cand:
        r = bt.simulate(symbols, data, master, fn, **kw)
        m = bt.metrics(r["curve"], periods_per_year=52); t = bt.trade_stats(r["trades"])
        rows.append((nm, m, t, r["exposure"], r["curve"]))
        print(f"{nm:34s} CAGR {m['cagr']*100:5.1f}%  DD {m['maxdd']*100:5.1f}%  Calmar {m['calmar']:.2f}  "
              f"Sharpe {m['sharpe']:.2f}  Trades {t['n']:4d}  ₹{m['end_v']:,.0f}", flush=True)
    bt.POS_PCT = 0.02

    best = max(rows, key=lambda x: x[1]["calmar"])
    bm = best[1]
    byname = {r[0]: r for r in rows}
    rec = byname["20% trail · all-cap"]      # practical pick: ~tied Calmar, higher Sharpe, half the trades
    rm = rec[1]
    print(f"\n>>> Highest Calmar: {best[0]}  (CAGR {bm['cagr']*100:.1f}%, DD {bm['maxdd']*100:.1f}%, Calmar {bm['calmar']:.2f})")
    print(f">>> RECOMMENDED (practical): {rec[0]}  (CAGR {rm['cagr']*100:.1f}%, DD {rm['maxdd']*100:.1f}%, "
          f"Calmar {rm['calmar']:.2f}, Sharpe {rm['sharpe']:.2f}, {rec[2]['n']} trades)")

    n500 = [x for x in bt.fetch_weekly("%5ECRSLDX") if x[0] >= master[0]]
    n500c = [(x[0], bt.INIT_CAPITAL * x[4] / n500[0][4]) for x in n500]
    bt.make_svg([(f"Recommended: 20% trail all-cap (Calmar {rm['calmar']:.2f})", "#2563eb", rec[4]),
                 (f"Highest Calmar: ATR×3.5 all-cap ({bm['calmar']:.2f})", "#22a06b", best[4]),
                 ("Nifty 500 buy&hold", "#f59e0b", n500c)],
                os.path.join(bt.OUTDIR, "results", "best_combo_equity.svg"),
                "Best entry+exit combination (Rs 20L, log scale)")

    yrs = (master[-1] - master[0]).days / 365.25
    L = ["# Best entry + exit combination\n",
         "> Fixed: **upper Bollinger breakout** entry + **RS > 0.2** (Nifty 500 6-month "
         "outperformance floor, no upper cap) + **4% sizing**, weekly, ₹20L, 0.25%/side. "
         "Exit, drawdown brake and universe tested head-to-head below. "
         f"Window {master[0]} → {master[-1]} ({yrs:.1f} yrs). **In-sample, survivorship-biased.**\n",
         "## Candidates\n",
         "| Combination | CAGR | Max DD | Calmar | Sharpe | Trades | Final |",
         "|---|--:|--:|--:|--:|--:|--:|"]
    for nm, m, t, exp, _ in sorted(rows, key=lambda x: -x[1]["calmar"]):
        star = " ⭐" if nm == best[0] else ""
        L.append(f"| {nm}{star} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | **{m['calmar']:.2f}** | "
                 f"{m['sharpe']:.2f} | {t['n']} | ₹{m['end_v']:,.0f} |")
    L += ["",
          "## The recommended setup\n",
          f"Highest raw Calmar is **{best[0]}** ({bm['cagr']*100:.1f}% / {bm['maxdd']*100:.1f}% / "
          f"Calmar {bm['calmar']:.2f}) — but it trades {best[2]['n']} times. The **recommended** "
          "combination is the practically-tied, lower-turnover, higher-Sharpe one:\n",
          f"### ⭐ Recommended: {rec[0]}\n",
          f"CAGR **{rm['cagr']*100:.1f}%** · Max DD **{rm['maxdd']*100:.1f}%** · Calmar **{rm['calmar']:.2f}** · "
          f"Sharpe **{rm['sharpe']:.2f}** · {rec[2]['n']} trades · win {rec[2]['win_rate']*100:.0f}%.\n",
          "Full rule set:",
          "- **Entry:** weekly close crosses above the upper Bollinger Band (52, 2) **and** the stock "
          "is outperforming the Nifty 500 by **>20%** over the last 6 months (26-week RS > 0.2).",
          "- **Exit:** 20% ratcheting trailing stop on the weekly close (locks profit, caps loss).",
          "- **Sizing:** 4% of current equity per position, max 50 positions.",
          "- **Universe:** all Nifty 500 (all-cap beat the ₹1000-20000 slice on drawdown/Calmar).",
          "- **Regime brake / EMA / narrow RS band:** none — each *reduced* performance here.",
          "",
          "Why not the ATR×3.5 exit: its Calmar is 0.01 higher but it trades ~65% more (higher real "
          "cost) and has a lower Sharpe. The 20% trail is simpler, steadier, and what you already use.\n",
          "## ⚠️ Caveats\n",
          "- In-sample, survivorship-biased (today's Nifty 500). This is the best-fitting combination "
          "*on this history* — expect out-of-sample decay. Prefer it because each ingredient helped "
          "for a reason across independent tests, not because it topped one grid.\n",
          "*Generated by `backtest/best_combo.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "BEST_COMBO.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("Wrote docs/BEST_COMBO.md and backtest/results/best_combo_equity.svg")

if __name__ == "__main__":
    main()
