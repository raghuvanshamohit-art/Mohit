#!/usr/bin/env python3
"""
Run the system on a MONTHLY timeframe. Every "weekly" setting is translated to
its monthly-calendar equivalent, then back-tested on real monthly data.

  Weekly setting            ->  Monthly equivalent
  BB length      52 weeks   ->  12 months  (~1 year)
  Long EMA       100 weeks  ->  24 months  (~2 years)
  ATR length     14 weeks   ->  14 months  (kept; only used for the ATR trail)
  Trailing stop  20%        ->  20%        (percentage — timeframe-independent)
  Warm-up        100 weeks  ->  24 months
  Regime SMA     40 weeks   ->  10 months  (classic monthly trend filter)

Reports CAGR and Max drawdown (+ Calmar, Sharpe) with monthly annualisation.
Cached, deterministic. In-sample & survivorship-biased.
"""
import os, sys, json, datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt

# ---- monthly settings (override the weekly globals before building symbols) ----
bt.BB_LEN, bt.EMA_LEN, bt.ATR_LEN, bt.WARMUP = 12, 24, 14, 24
MCACHE = os.path.join(bt.OUTDIR, "cache", "monthly.json")

def load_monthly(universe):
    if os.path.exists(MCACHE) and not os.environ.get("REFRESH"):
        with open(MCACHE) as f:
            raw = json.load(f)
        return {s: [(dt.date.fromisoformat(r[0]), r[1], r[2], r[3], r[4]) for r in rows]
                for s, rows in raw.items() if s in set(universe)}
    bmap = {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(bt.fetch_weekly, s, "1mo", bt.month_start): s for s in universe}
        for i, fut in enumerate(as_completed(futs)):
            try:
                b = fut.result()
            except Exception:
                b = None
            if b:
                bmap[futs[fut]] = b
            if (i + 1) % 100 == 0:
                print(f"  ... {i+1}/{len(universe)} fetched", flush=True)
    os.makedirs(os.path.dirname(MCACHE), exist_ok=True)
    with open(MCACHE, "w") as f:
        json.dump({s: [[b[0].isoformat(), round(b[1], 4), round(b[2], 4), round(b[3], 4), round(b[4], 4)]
                       for b in bars] for s, bars in bmap.items()}, f)
    return bmap

def regime_monthly(master, n=10, index_sym="%5ECRSLDX"):
    bars = bt.fetch_weekly(index_sym, "1mo", bt.month_start)
    bd = [b[0] for b in bars]; bc = [b[4] for b in bars]
    flags = [(bd[i], bc[i] > sum(bc[i - n + 1:i + 1]) / n) for i in range(n - 1, len(bars))]
    reg, j, state = {}, 0, True
    for d in master:
        while j < len(flags) and flags[j][0] <= d:
            state = flags[j][1]; j += 1
        reg[d] = state
    return reg

def bench_monthly(sym, start_d):
    bars = [b for b in bt.fetch_weekly(sym, "1mo", bt.month_start) if b[0] >= start_d]
    base = bars[0][4]
    return [(b[0], bt.INIT_CAPITAL * b[4] / base) for b in bars]

def main():
    universe = bt.load_universe()
    print(f"Universe {len(universe)}. Loading MONTHLY data ...", flush=True)
    bmap = load_monthly(universe)
    print(f"Usable symbols: {len(bmap)}/{len(universe)}", flush=True)
    data = {s: bt.build_symbol(s, b) for s, b in bmap.items()}
    symbols = sorted(data)
    all_dates = set()
    for s in symbols:
        all_dates.update(data[s].keys())
    master = sorted(all_dates)
    for idx, d in enumerate(master):
        if sum(1 for s in symbols if (b := data[s].get(d)) is not None and b["i"] >= bt.WARMUP) >= 20:
            master = master[idx:]; break
    print(f"Window: {master[0]} -> {master[-1]} ({len(master)} months)", flush=True)

    reg = regime_monthly(master)
    tight = bt.EXIT_MODES["tightest (max EMA,ATR)"]
    trailonly = bt.EXIT_MODES["ATR trail only"]
    base = dict(trail_type="pct", pct_trail=0.20)

    rows = []
    def run(name, fn, kw):
        r = bt.simulate(symbols, data, master, fn, **kw)
        m = bt.metrics(r["curve"], periods_per_year=12); t = bt.trade_stats(r["trades"])
        rows.append((name, m, t, r["exposure"], r["curve"]))
        print(f"{name:44s} CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  "
              f"Calmar {m['calmar']:.2f}  Sharpe {m['sharpe']:.2f}  ₹{m['end_v']:,.0f}", flush=True)

    run("Monthly: 20% trail + 24 EMA",           tight,     {**base})
    run("  + regime filter (10-month SMA)",       tight,     {**base, "regime_ok": reg})
    run("Monthly: 20% trail only (no EMA)",       trailonly, {**base})
    run("Monthly: ATR(14x1.8) trail + 24 EMA",    tight,     dict())   # ATR-trail variant

    benches = {}
    for label, sym in [("Nifty 50", "%5ENSEI"), ("Nifty 500", "%5ECRSLDX")]:
        bc = bench_monthly(sym, master[0])
        benches[label] = bt.metrics(bc, periods_per_year=12)
        m = benches[label]
        print(f"{'BENCH '+label:44s} CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  "
              f"Calmar {m['calmar']:.2f}", flush=True)

    # chart: monthly base vs base+regime vs Nifty 50
    n50 = bench_monthly("%5ENSEI", master[0])
    series = [("Monthly base (Calmar %.2f)" % rows[0][1]["calmar"], "#9ca3af", rows[0][4]),
              ("Base+regime (Calmar %.2f)" % rows[1][1]["calmar"], "#2563eb", rows[1][4]),
              ("Nifty 50 buy&hold", "#f59e0b", n50)]
    bt.make_svg(series, os.path.join(bt.OUTDIR, "results", "monthly_equity.svg"),
                "Monthly timeframe — 20%% trail (Rs 20L, log scale)")

    L = ["# Monthly-timeframe backtest\n",
         "> Same rules on a **monthly** timeframe, settings translated from weekly (see table). "
         "Cached, deterministic; survivorship-biased Nifty 500. **In-sample.**\n",
         "## Settings: weekly → monthly\n",
         "| Setting | Weekly | Monthly |",
         "|---|--:|--:|",
         "| Bollinger length | 52 | **12** |",
         "| Bollinger σ | 2 | 2 |",
         "| Long EMA | 100 | **24** |",
         "| ATR length | 14 | 14 |",
         "| Trailing stop | 20% | 20% |",
         "| Warm-up | 100 | 24 |",
         "| Regime SMA | 40 | **10** |",
         "| RS look-backs | 13/26/52 | 3/6/12 |\n",
         f"**Window:** {master[0]} → {master[-1]} ({len(master)} months) · ₹20 lakh · {len(bmap)} symbols\n",
         "## Results (monthly)\n",
         "| Setup | CAGR | Max DD | Calmar | Sharpe | Exposure | Final |",
         "|---|--:|--:|--:|--:|--:|--:|"]
    for name, m, t, exp, _ in rows:
        L.append(f"| {name.strip()} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} | "
                 f"{m['sharpe']:.2f} | {exp*100:.0f}% | ₹{m['end_v']:,.0f} |")
    L.append("")
    L.append("| Benchmark (buy & hold) | CAGR | Max DD | Calmar |")
    L.append("|---|--:|--:|--:|")
    for label, m in benches.items():
        L.append(f"| {label} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} |")
    L += ["",
          "![monthly](../backtest/results/monthly_equity.svg)\n",
          "## Notes\n",
          "- Monthly trades far less often (fewer bars) and reacts slower — signals and exits lag by "
          "up to a month, so **drawdowns are usually deeper** than the weekly version even though the "
          "logic is identical.",
          "- The 20% trailing stop is percentage-based, so it carries over unchanged; only the "
          "look-back lengths shrink (≈ ÷4.3) to keep the same calendar horizons.",
          "- ATR(14) on monthly bars spans >1 year and makes a very wide trail — prefer the 20% "
          "percentage trail on this timeframe.\n",
          "## ⚠️ Caveats\n",
          "- In-sample, survivorship-biased; the current (partial) month is included as one bar. "
          "Fewer monthly bars per name = coarser statistics than the weekly test.\n",
          "*Generated by `backtest/monthly_test.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "MONTHLY.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\nWrote docs/MONTHLY.md and backtest/results/monthly_equity.svg", flush=True)

if __name__ == "__main__":
    main()
