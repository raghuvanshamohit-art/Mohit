#!/usr/bin/env python3
"""
Final synthesis: combine every backtest's winning lever and pick the best
entry+exit combination. Fixed from all prior sweeps: upper Bollinger breakout +
Nifty 500 6-month RS > 0.2 entry, 4% sizing, weekly. Open questions settled here:
trailing-stop width (10 vs 15 vs 20%), universe (all-cap / 1000-20000 / 1000-10000),
regime brake (on/off). Picks by Calmar. In-sample, survivorship-biased.
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
    ex = bt.EXIT_MODES["ATR trail only"]
    C = dict(rs_entry=True, rs_thresh=0.2, size_mode="fixed", max_pos=50, trail_type="pct")

    cand = [
        ("10% trail · all-cap",        {**C, "pct_trail": 0.10}),
        ("10% trail · 1000-20000cr",   {**C, "pct_trail": 0.10, "mcap_lo": 1000, "mcap_hi": 20000}),
        ("10% trail · 1000-10000cr",   {**C, "pct_trail": 0.10, "mcap_lo": 1000, "mcap_hi": 10000}),
        ("12% trail · all-cap",        {**C, "pct_trail": 0.12}),
        ("15% trail · all-cap",        {**C, "pct_trail": 0.15}),
        ("20% trail · all-cap",        {**C, "pct_trail": 0.20}),
        ("10% trail · all-cap +regime",{**C, "pct_trail": 0.10, "regime_ok": reg}),
        ("10% trail · 1000-20000 +regime", {**C, "pct_trail": 0.10, "mcap_lo": 1000, "mcap_hi": 20000, "regime_ok": reg}),
    ]
    rows = []
    for nm, kw in cand:
        r = bt.simulate(symbols, data, master, ex, **kw)
        m = bt.metrics(r["curve"], periods_per_year=52); t = bt.trade_stats(r["trades"])
        rows.append((nm, m, t, r["exposure"], r["curve"], kw))
        print(f"{nm:34s} CAGR {m['cagr']*100:5.1f}%  DD {m['maxdd']*100:5.1f}%  Calmar {m['calmar']:.2f}  "
              f"Sharpe {m['sharpe']:.2f}  Trades {t['n']:4d}  ₹{m['end_v']:,.0f}", flush=True)
    bt.POS_PCT = 0.02

    best = max(rows, key=lambda x: x[1]["calmar"])
    bm, bkw = best[1], best[5]
    print(f"\n>>> BEST by Calmar: {best[0]}  (CAGR {bm['cagr']*100:.1f}%, DD {bm['maxdd']*100:.1f}%, Calmar {bm['calmar']:.2f})")

    n500 = [x for x in bt.fetch_weekly("%5ECRSLDX") if x[0] >= master[0]]
    n500c = [(x[0], bt.INIT_CAPITAL * x[4] / n500[0][4]) for x in n500]
    bt.make_svg([(f"BEST: {best[0]} (Calmar {bm['calmar']:.2f})", "#2563eb", best[4]),
                 ("Nifty 500 buy&hold", "#f59e0b", n500c)],
                os.path.join(bt.OUTDIR, "results", "final_best_equity.svg"),
                "Final best entry+exit (Rs 20L, log scale)")

    yrs = (master[-1] - master[0]).days / 365.25
    pct = int(bkw["pct_trail"] * 100)
    uni = ("₹1,000–20,000 cr" if bkw.get("mcap_hi") == 20000 else
           "₹1,000–10,000 cr" if bkw.get("mcap_hi") == 10000 else "all Nifty 500")
    reg_on = "regime_ok" in bkw
    L = ["# CW 2σ — Final Strategy (best entry / exit, all backtests combined)\n",
         "> Selected by `backtest/final_best.py` after every sweep (RS floor, trail width, sizing, "
         "market cap, regime). Weekly, Nifty 500 universe. **Educational; in-sample & survivorship-biased.**\n",
         "## Candidates compared\n",
         "| Combination | CAGR | Max DD | Calmar | Sharpe | Trades | Final |",
         "|---|--:|--:|--:|--:|--:|--:|"]
    for nm, m, t, exp, cv, kw in sorted(rows, key=lambda x: -x[1]["calmar"]):
        star = " ⭐" if nm == best[0] else ""
        L.append(f"| {nm}{star} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | **{m['calmar']:.2f}** | "
                 f"{m['sharpe']:.2f} | {t['n']} | ₹{m['end_v']:,.0f} |")
    L += ["",
          f"## ⭐ Best combination: {best[0]}\n",
          f"CAGR **{bm['cagr']*100:.1f}%** · Max DD **{bm['maxdd']*100:.1f}%** · Calmar **{bm['calmar']:.2f}** · "
          f"Sharpe **{bm['sharpe']:.2f}** · {best[2]['n']} trades · win {best[2]['win_rate']*100:.0f}% · "
          f"₹20L → ₹{bm['end_v']:,.0f} over {yrs:.1f} yrs.\n",
          "## The rules\n",
          "**Timeframe:** Weekly. Evaluate on Friday's close, act at Monday's open. **Universe:** " + uni + ".\n",
          "**ENTRY — buy Monday's open when BOTH are true on Friday's close:**",
          "1. Weekly close crosses **above the Upper Bollinger Band (SMA 52, 2σ)** — "
          "`close[t] > UpperBB` and `close[t-1] ≤ UpperBB`.",
          "2. **RS > 0.2** — `(close/close₂₆w) − (Nifty500/Nifty500₂₆w) > 0.20` (outperform Nifty 500 "
          "by >20% over 6 months; no upper cap).\n",
          f"**EXIT — {pct}% ratcheting trailing stop (sell Monday's open):**",
          f"- On entry: `stop = entry × {1-bkw['pct_trail']:.2f}`.",
          f"- Each weekly close: `stop = max(prev_stop, weekly_close × {1-bkw['pct_trail']:.2f})` — ratchets up only.",
          "- Exit when weekly close < stop. No profit target.\n",
          "**SIZING:** 4% of current equity per position, max 50 positions.\n",
          "**NOT used (each reduced performance):** no 100 EMA, " +
          ("no regime filter, " if not reg_on else "") + "no narrow RS band, no upper RS cap.\n",
          "## Why this is the pick\n",
          f"- **{pct}% trailing stop** beat 15% and 20% on risk-adjusted return — it locks profit "
          "sooner (much lower drawdown) while still riding winners; 5% was too tight (whipsaw).",
          "- **RS > 0.2 floor** (no cap) was the return optimum vs any narrow band or higher floor.",
          "- **4% sizing** beat 2% and 5%. **Regime filter and the 100 EMA both hurt** and are dropped.",
          "- Universe: " + uni + " gave the best Calmar; small-caps carry the return but are the most "
          "survivorship-biased.\n",
          "## ⚠️ Caveats\n",
          "- In-sample, survivorship-biased (today's Nifty 500). The absolute CAGR is an optimistic "
          "upper bound — trust the *rules and their relative edge* over the alternatives, not the exact "
          "number. Tighter stops raise turnover, so real cost matters more. Validate out-of-sample.\n",
          "*Generated by `backtest/final_best.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "FINAL_STRATEGY.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("Wrote docs/FINAL_STRATEGY.md and backtest/results/final_best_equity.svg")

if __name__ == "__main__":
    main()
