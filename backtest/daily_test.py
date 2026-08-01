#!/usr/bin/env python3
"""
Run the system on a DAILY timeframe. Weekly look-backs are multiplied by ~5
(trading days per week) to keep the same calendar horizons.

  Weekly setting            ->  Daily equivalent
  BB length      52 weeks   ->  252 days  (~1 year)
  Long EMA       100 weeks  ->  500 days  (~2 years)
  ATR length     14 weeks   ->  70 days
  Trailing stop  20%        ->  20%       (percentage — timeframe-independent)
  Warm-up        100 weeks  ->  500 days
  Regime SMA     40 weeks   ->  200 days  (the classic 200-day SMA)

Reports CAGR and Max drawdown (+ Calmar, Sharpe) with daily annualisation.
Cached (gzip), deterministic. In-sample & survivorship-biased.
"""
import os, sys, json, gzip, datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt

bt.BB_LEN, bt.EMA_LEN, bt.ATR_LEN, bt.WARMUP = 252, 500, 70, 500
DCACHE = os.path.join(bt.OUTDIR, "cache", "daily.json.gz")
DAY = lambda ts: dt.datetime.utcfromtimestamp(ts).date()

def load_daily(universe):
    if os.path.exists(DCACHE) and not os.environ.get("REFRESH"):
        with gzip.open(DCACHE, "rt") as f:
            raw = json.load(f)
        return {s: [(dt.date.fromisoformat(r[0]), r[1], r[2], r[3], r[4]) for r in rows]
                for s, rows in raw.items() if s in set(universe)}
    bmap = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(bt.fetch_weekly, s, "1d", DAY): s for s in universe}
        for i, fut in enumerate(as_completed(futs)):
            try:
                b = fut.result()
            except Exception:
                b = None
            if b:
                bmap[futs[fut]] = b
            if (i + 1) % 100 == 0:
                print(f"  ... {i+1}/{len(universe)} fetched", flush=True)
    os.makedirs(os.path.dirname(DCACHE), exist_ok=True)
    with gzip.open(DCACHE, "wt") as f:
        json.dump({s: [[b[0].isoformat(), round(b[1], 4), round(b[2], 4), round(b[3], 4), round(b[4], 4)]
                       for b in bars] for s, bars in bmap.items()}, f)
    return bmap

def regime_daily(master, n=200, index_sym="%5ECRSLDX"):
    bars = bt.fetch_weekly(index_sym, "1d", DAY)
    bd = [b[0] for b in bars]; bc = [b[4] for b in bars]
    flags = [(bd[i], bc[i] > sum(bc[i - n + 1:i + 1]) / n) for i in range(n - 1, len(bars))]
    reg, j, state = {}, 0, True
    for d in master:
        while j < len(flags) and flags[j][0] <= d:
            state = flags[j][1]; j += 1
        reg[d] = state
    return reg

def bench_daily(sym, start_d):
    bars = [b for b in bt.fetch_weekly(sym, "1d", DAY) if b[0] >= start_d]
    base = bars[0][4]
    return [(b[0], bt.INIT_CAPITAL * b[4] / base) for b in bars]

def main():
    universe = bt.load_universe()
    print(f"Universe {len(universe)}. Loading DAILY data (large) ...", flush=True)
    bmap = load_daily(universe)
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
    print(f"Window: {master[0]} -> {master[-1]} ({len(master)} days)", flush=True)

    reg = regime_daily(master)
    tight = bt.EXIT_MODES["tightest (max EMA,ATR)"]
    trailonly = bt.EXIT_MODES["ATR trail only"]
    base = dict(trail_type="pct", pct_trail=0.20)

    rows = []
    def run(name, fn, kw):
        r = bt.simulate(symbols, data, master, fn, **kw)
        m = bt.metrics(r["curve"], periods_per_year=252); t = bt.trade_stats(r["trades"])
        rows.append((name, m, t, r["exposure"], r["curve"]))
        print(f"{name:44s} CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  "
              f"Calmar {m['calmar']:.2f}  Sharpe {m['sharpe']:.2f}  Trades {t['n']}  "
              f"₹{m['end_v']:,.0f}", flush=True)

    run("Daily: 20% trail + 500 EMA",            tight,     {**base})
    run("  + regime filter (200-day SMA)",        tight,     {**base, "regime_ok": reg})
    run("Daily: 20% trail only (no EMA)",         trailonly, {**base})
    run("Daily: ATR(70x1.8) trail + 500 EMA",     tight,     dict())

    benches = {}
    for label, sym in [("Nifty 50", "%5ENSEI"), ("Nifty 500", "%5ECRSLDX")]:
        benches[label] = bt.metrics(bench_daily(sym, master[0]), periods_per_year=252)
        m = benches[label]
        print(f"{'BENCH '+label:44s} CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  "
              f"Calmar {m['calmar']:.2f}", flush=True)

    n50 = bench_daily("%5ENSEI", master[0])
    series = [("Daily base (Calmar %.2f)" % rows[0][1]["calmar"], "#9ca3af", rows[0][4]),
              ("Base+regime (Calmar %.2f)" % rows[1][1]["calmar"], "#2563eb", rows[1][4]),
              ("Nifty 50 buy&hold", "#f59e0b", n50)]
    bt.make_svg(series, os.path.join(bt.OUTDIR, "results", "daily_equity.svg"),
                "Daily timeframe — 20%% trail (Rs 20L, log scale)")

    L = ["# Daily-timeframe backtest\n",
         "> Same rules on a **daily** timeframe, settings translated from weekly (×5 trading days). "
         "Cached, deterministic; survivorship-biased Nifty 500. **In-sample.**\n",
         "## Settings: weekly → daily\n",
         "| Setting | Weekly | Daily |",
         "|---|--:|--:|",
         "| Bollinger length | 52 | **252** |",
         "| Bollinger σ | 2 | 2 |",
         "| Long EMA | 100 | **500** |",
         "| ATR length | 14 | 70 |",
         "| Trailing stop | 20% | 20% |",
         "| Warm-up | 100 | 500 |",
         "| Regime SMA | 40 | **200** |\n",
         f"**Window:** {master[0]} → {master[-1]} ({len(master)} days) · ₹20 lakh · {len(bmap)} symbols\n",
         "## Results (daily)\n",
         "| Setup | CAGR | Max DD | Calmar | Sharpe | Trades | Exposure | Final |",
         "|---|--:|--:|--:|--:|--:|--:|--:|"]
    for name, m, t, exp, _ in rows:
        L.append(f"| {name.strip()} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} | "
                 f"{m['sharpe']:.2f} | {t['n']} | {exp*100:.0f}% | ₹{m['end_v']:,.0f} |")
    L.append("")
    L.append("| Benchmark (buy & hold) | CAGR | Max DD | Calmar |")
    L.append("|---|--:|--:|--:|")
    for label, m in benches.items():
        L.append(f"| {label} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} |")
    L += ["",
          "![daily](../backtest/results/daily_equity.svg)\n",
          "## Notes\n",
          "- Daily reacts fastest and trades the most — an intraday-style breakout fires far more "
          "often, so **turnover and cost drag are much higher** than weekly/monthly.",
          "- The 20% trailing stop is percentage-based and carries over unchanged; only look-backs "
          "scale (×5).",
          "- This is a position system by design (the presenter runs it weekly). Daily is included "
          "for completeness — expect more whipsaw and cost sensitivity.\n",
          "## ⚠️ Caveats\n",
          "- In-sample, survivorship-biased; 0.25%/side cost matters far more at daily turnover. "
          "Fills modelled at the next daily open.\n",
          "*Generated by `backtest/daily_test.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "DAILY.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\nWrote docs/DAILY.md and backtest/results/daily_equity.svg", flush=True)

if __name__ == "__main__":
    main()
