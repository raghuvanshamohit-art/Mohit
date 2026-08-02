#!/usr/bin/env python3
"""
Backtest the ENTRY SIGNALS supplied in the uploaded spreadsheet
("Stock with RS positive w.r.t NIFTY 50 — outperform NIFTY 50 in 52 weeks").

The sheet is a weekly list of (Date, Symbol) picks. We execute each pick at that
week's open and manage it with the locked exit — a 20% ratcheting trailing stop
(optionally + 100 EMA) — 2% sizing, ₹20L, weekly. Reports CAGR and Max drawdown.

Entries come from the file; only price data is fetched (Yahoo, weekly adjusted).
In-sample only in the sense that the signal list is given; survivorship of the
signal generator is unknown.
"""
import os, sys, json, gzip, datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt
import openpyxl

XLSX = ("/root/.claude/uploads/4c191904-85a7-5dee-8ea4-9b83c4f54368/"
        "39b6b4a9-Backtest_Copy__Stock_with_RS_positive_w.r.t_NIFTY_50_"
        "i.e._Outperform_NIFTY_50_in_52_weeks_copy.xlsx")
SCACHE = os.path.join(bt.OUTDIR, "cache", "signals_weekly.json.gz")

def monday(d):
    return d - dt.timedelta(days=d.weekday())

def read_signals():
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    ws = wb["in"]
    by_week = {}
    syms = set()
    for r in ws.iter_rows(min_row=2, values_only=True):
        d, sym = r[0], r[1]
        if not d or not sym:
            continue
        wk = monday(d.date() if hasattr(d, "date") else d)
        by_week.setdefault(wk, []).append(sym.strip())
        syms.add(sym.strip())
    return by_week, sorted(syms)

def load_prices(symbols):
    tick = {s: s.replace("&", "%26") + ".NS" for s in symbols}
    if os.path.exists(SCACHE) and not os.environ.get("REFRESH"):
        with gzip.open(SCACHE, "rt") as f:
            raw = json.load(f)
        return {s: [(dt.date.fromisoformat(r[0]), r[1], r[2], r[3], r[4]) for r in rows]
                for s, rows in raw.items()}
    bmap = {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(bt.fetch_weekly, tick[s]): s for s in symbols}
        for i, fut in enumerate(as_completed(futs)):
            try:
                b = fut.result()
            except Exception:
                b = None
            if b:
                bmap[futs[fut]] = b
            if (i + 1) % 150 == 0:
                print(f"  ... {i+1}/{len(symbols)} fetched (usable {len(bmap)})", flush=True)
    os.makedirs(os.path.dirname(SCACHE), exist_ok=True)
    with gzip.open(SCACHE, "wt") as f:
        json.dump({s: [[b[0].isoformat(), round(b[1], 4), round(b[2], 4), round(b[3], 4), round(b[4], 4)]
                       for b in bars] for s, bars in bmap.items()}, f)
    return bmap

def simulate_signals(by_week, data, master, pct=0.20, use_ema=True, entry_lag=0):
    INIT, POS, MAXP, COST = bt.INIT_CAPITAL, bt.POS_PCT, bt.MAX_POS, bt.COST_PSIDE
    cash = INIT; held = {}; exitq = set(); pend = {}
    curve = []; trades = []; last_close = {}; prev_eq = INIT; inv_frac = []
    # map each signal week to the execution week (entry_lag weeks later on the master grid)
    midx = {d: i for i, d in enumerate(master)}
    exec_week = {}
    for wk, syms in by_week.items():
        if wk in midx:
            j = min(midx[wk] + entry_lag, len(master) - 1)
            exec_week.setdefault(master[j], []).extend(syms)

    for d in master:
        for sym in sorted(exitq):
            bar = data[sym].get(d)
            if bar is None:
                continue
            pos = held.get(sym)
            if pos:
                proceeds = pos["sh"] * bar[1] * (1 - COST)   # sell at open
                cash += proceeds
                trades.append(dict(sym=sym, ret=bar[1] / pos["entry"] - 1.0, weeks=pos["weeks"]))
                del held[sym]
            exitq.discard(sym)
        for sym in sorted(set(exec_week.get(d, []))):
            if len(held) >= MAXP or sym in held or sym not in data:
                continue
            bar = data[sym].get(d)
            if bar is None:
                continue
            tgt = POS * prev_eq
            sh = int(tgt // bar[1])
            if sh <= 0:
                continue
            cost = sh * bar[1] * (1 + COST)
            if cost > cash:
                sh = int(cash // (bar[1] * (1 + COST)))
                if sh <= 0:
                    continue
                cost = sh * bar[1] * (1 + COST)
            cash -= cost
            held[sym] = dict(sh=sh, entry=bar[1], entry_date=d, trail=bar[1] * (1 - pct), weeks=0)
        invested = 0.0
        for sym, pos in held.items():
            bar = data[sym].get(d)
            if bar is not None:
                last_close[sym] = bar[4]
            invested += pos["sh"] * last_close.get(sym, pos["entry"])
        eq = cash + invested
        curve.append((d, eq)); inv_frac.append(invested / eq if eq > 0 else 0.0); prev_eq = eq
        for sym, pos in held.items():
            bar = data[sym].get(d)
            if bar is None:
                continue
            pos["weeks"] += 1
            cand = bar[4] * (1 - pct)
            if cand > pos["trail"]:
                pos["trail"] = cand
            eff = pos["trail"]
            if use_ema:
                em = data[sym].get(d)
                emav = emamap[sym].get(d)
                if emav is not None:
                    eff = max(eff, emav)
            if d != pos["entry_date"] and bar[4] < eff:
                exitq.add(sym)
    return dict(curve=curve, trades=trades,
                exposure=sum(inv_frac) / len(inv_frac) if inv_frac else 0.0)

def main():
    by_week, syms = read_signals()
    print(f"Signals: {sum(len(v) for v in by_week.values())} picks, {len(syms)} unique symbols, "
          f"{len(by_week)} weeks {min(by_week)} -> {max(by_week)}", flush=True)
    bmap = load_prices(syms)
    print(f"Price data resolved for {len(bmap)}/{len(syms)} symbols "
          f"({len(bmap)/len(syms)*100:.0f}%)", flush=True)

    # price dict keyed by weekstart -> (date,o,h,l,c); plus 100-EMA per week
    global emamap
    data, emamap = {}, {}
    for s, bars in bmap.items():
        data[s] = {b[0]: b for b in bars}
        _, ema, _ = bt.indicators(bars)
        emamap[s] = {bars[i][0]: ema[i] for i in range(len(bars))}

    first = min(by_week)
    all_dates = set()
    for s in data:
        all_dates.update(d for d in data[s] if d >= first)
    master = sorted(all_dates)
    print(f"Backtest window: {master[0]} -> {master[-1]} "
          f"({(master[-1]-master[0]).days/365.25:.1f} years)", flush=True)

    rows = []
    def run(name, **kw):
        r = simulate_signals(by_week, data, master, **kw)
        m = bt.metrics(r["curve"], periods_per_year=52); t = bt.trade_stats(r["trades"])
        rows.append((name, m, t, r["exposure"], r["curve"]))
        print(f"{name:40s} CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  "
              f"Calmar {m['calmar']:.2f}  Sharpe {m['sharpe']:.2f}  Trades {t['n']}  Win {t['win_rate']*100:.0f}%  "
              f"₹{m['end_v']:,.0f}", flush=True)

    run("20% trail + 100 EMA (same-week entry)", pct=0.20, use_ema=True,  entry_lag=0)
    run("20% trail only (same-week entry)",      pct=0.20, use_ema=False, entry_lag=0)
    run("20% trail + 100 EMA (next-week entry)", pct=0.20, use_ema=True,  entry_lag=1)

    benches = {}
    for label, sym in [("Nifty 50", "%5ENSEI"), ("Nifty 500", "%5ECRSLDX")]:
        b = [x for x in bt.fetch_weekly(sym) if x[0] >= master[0]]
        bc = [(x[0], bt.INIT_CAPITAL * x[4] / b[0][4]) for x in b]
        benches[label] = bt.metrics(bc, periods_per_year=52)
        m = benches[label]
        print(f"{'BENCH '+label:40s} CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  "
              f"Calmar {m['calmar']:.2f}", flush=True)

    n50 = [x for x in bt.fetch_weekly("%5ENSEI") if x[0] >= master[0]]
    n50c = [(x[0], bt.INIT_CAPITAL * x[4] / n50[0][4]) for x in n50]
    series = [(f"Signals: 20%+EMA (Calmar {rows[0][1]['calmar']:.2f})", "#2563eb", rows[0][4]),
              ("Nifty 50 buy&hold", "#f59e0b", n50c)]
    bt.make_svg(series, os.path.join(bt.OUTDIR, "results", "signals_equity.svg"),
                "RS-vs-Nifty50 signals backtest (Rs 20L, log scale)")

    L = ["# Backtest of the uploaded RS-vs-Nifty-50 signal list\n",
         "> Entries are the weekly picks from the spreadsheet "
         "(*stocks outperforming Nifty 50 over 52 weeks*). Exit = 20% ratcheting trailing stop "
         "(± 100 EMA), 2% sizing, ₹20L, 0.25%/side, weekly.\n",
         f"- **Signals:** {sum(len(v) for v in by_week.values())} picks · {len(syms)} unique symbols · "
         f"{len(by_week)} weeks",
         f"- **Price data resolved:** {len(bmap)}/{len(syms)} symbols ({len(bmap)/len(syms)*100:.0f}%)",
         f"- **Window:** {master[0]} → {master[-1]} ({(master[-1]-master[0]).days/365.25:.1f} years)\n",
         "## Results\n",
         "| Setup | CAGR | Max DD | Calmar | Sharpe | Trades | Win% | Final |",
         "|---|--:|--:|--:|--:|--:|--:|--:|"]
    for name, m, t, exp, _ in rows:
        L.append(f"| {name} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} | "
                 f"{m['sharpe']:.2f} | {t['n']} | {t['win_rate']*100:.0f}% | ₹{m['end_v']:,.0f} |")
    L.append("")
    L.append("| Benchmark (buy & hold) | CAGR | Max DD | Calmar |")
    L.append("|---|--:|--:|--:|")
    for label, m in benches.items():
        L.append(f"| {label} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} |")
    L += ["",
          "![signals](../backtest/results/signals_equity.svg)\n",
          "## Notes\n",
          "- Only ~3 years of signals, so CAGR is a short-window figure — treat drawdown and hit-rate "
          "as more informative than the annualised return here.",
          "- Unresolved symbols (renamed/delisted or not on Yahoo) are dropped; that removes some "
          "picks and mildly flatters or distorts results.",
          "- Same-week vs next-week entry brackets execution timing; the truth is in between.\n",
          "*Generated by `backtest/signals_backtest.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "SIGNALS_BACKTEST.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\nWrote docs/SIGNALS_BACKTEST.md and backtest/results/signals_equity.svg", flush=True)

if __name__ == "__main__":
    main()
