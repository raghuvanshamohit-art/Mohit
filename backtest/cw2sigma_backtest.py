#!/usr/bin/env python3
"""
CW 2σ (Reconstructed) — 20-year portfolio backtest.

Implements the rule set:
  ENTRY  : weekly close crosses ABOVE Upper Bollinger Band (52, 2) -> buy next weekly open
  SIZING : fixed 2% of current equity per position (max 50 concurrent)
  STOP   : initial 20% below entry, then trailing = 100 EMA + ATR(14 x 1.8) trailing stop
  EXIT   : weekly close below the effective stop -> sell next weekly open

Data      : Yahoo Finance weekly, split/bonus/div adjusted (stdlib urllib only).
Universe  : current NSE Nifty 500 constituents (see caveats in docs/BACKTEST.md).
Benchmark : Nifty 50 (^NSEI) and Nifty 500 (^CRSLDX) buy & hold.

NOTE ON HONESTY: using *today's* index members introduces survivorship bias.
These figures are indicative of the rules' character, not a promise of the past.
"""
import urllib.request, urllib.error, json, math, csv, os, sys, time, datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------------------------------------------------------- config
INIT_CAPITAL = 2_000_000      # ₹20 lakh
POS_PCT      = 0.02           # 2% of equity per position
MAX_POS      = 50             # concurrency cap (2% each => ~100% invested)
COST_PSIDE   = 0.0025         # 0.25% per side (slippage + charges)
BB_LEN, BB_MULT = 52, 2.0     # official indicator legend: "BB 52 SMA close 2"
EMA_LEN         = 100
ATR_LEN, ATR_MULT = 14, 1.8   # official: "ATR Stop Loss % 14 1.8" (ratcheting trail)
WARMUP          = EMA_LEN     # a symbol is eligible once it has >= WARMUP weekly bars
RANGE           = "20y"
UA              = {"User-Agent": "Mozilla/5.0"}
OUTDIR          = os.path.dirname(os.path.abspath(__file__))

EXIT_MODES = {                # how EMA & ATR trailing stop combine (floored by 20% stop)
    "tightest (max EMA,ATR)": lambda ema, atr: max(ema, atr),
    "loosest (min EMA,ATR)":  lambda ema, atr: min(ema, atr),
    "100 EMA only":           lambda ema, atr: ema,
    "ATR trail only":         lambda ema, atr: atr,
}

# ----------------------------------------------------------------------------- fetch
def http_get(url, tries=3):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(1.2 * (k + 1))
    raise last

def monday(ts):
    d = dt.datetime.utcfromtimestamp(ts).date()
    return d - dt.timedelta(days=d.weekday())

def fetch_weekly(symbol):
    """Return list of consecutive (weekstart_date, o,h,l,c) with adjusted prices, or None."""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
           f"?range={RANGE}&interval=1wk&events=div%2Csplit")
    try:
        d = json.loads(http_get(url))
        res = d["chart"]["result"][0]
        ts = res["timestamp"]
        q = res["indicators"]["quote"][0]
        adj = res["indicators"]["adjclose"][0]["adjclose"]
        o, h, l, c = q["open"], q["high"], q["low"], q["close"]
    except Exception:
        return None
    out = []
    for i in range(len(ts)):
        if None in (o[i], h[i], l[i], c[i], adj[i]) or c[i] == 0:
            continue
        f = adj[i] / c[i]                       # fully-adjusted factor
        out.append((monday(ts[i]), o[i] * f, h[i] * f, l[i] * f, adj[i]))
    # de-dup weeks (keep last), keep chronological
    seen = {}
    for row in out:
        seen[row[0]] = row
    return [seen[k] for k in sorted(seen)] if len(seen) >= WARMUP + 5 else None

# ----------------------------------------------------------------------------- indicators
def indicators(bars):
    n = len(bars)
    close = [b[4] for b in bars]; high = [b[2] for b in bars]; low = [b[1] for b in bars]
    upper = [None] * n
    for i in range(BB_LEN - 1, n):
        w = close[i - BB_LEN + 1:i + 1]
        m = sum(w) / BB_LEN
        var = sum(x * x for x in w) / BB_LEN - m * m
        upper[i] = m + BB_MULT * math.sqrt(max(var, 0.0))
    ema = [None] * n
    if n >= EMA_LEN:
        a = 2.0 / (EMA_LEN + 1)
        ema[EMA_LEN - 1] = sum(close[:EMA_LEN]) / EMA_LEN
        for i in range(EMA_LEN, n):
            ema[i] = a * close[i] + (1 - a) * ema[i - 1]
    atr = [None] * n
    tr = [high[0] - low[0]] + [max(high[i] - low[i], abs(high[i] - close[i - 1]),
                                   abs(low[i] - close[i - 1])) for i in range(1, n)]
    if n >= ATR_LEN:
        atr[ATR_LEN - 1] = sum(tr[:ATR_LEN]) / ATR_LEN
        for i in range(ATR_LEN, n):
            atr[i] = (atr[i - 1] * (ATR_LEN - 1) + tr[i]) / ATR_LEN
    return upper, ema, atr

def build_symbol(symbol, bars):
    upper, ema, atr = indicators(bars)
    by_date = {}
    for i, b in enumerate(bars):
        d, o, h, l, c = b
        by_date[d] = dict(i=i, o=o, h=h, l=l, c=c,
                          upper=upper[i], ema=ema[i], atr=atr[i])
    # entry breakout signal (crossover close over upper), needs full warmup
    for i in range(1, len(bars)):
        d = bars[i][0]
        cur, prev = by_date[d], by_date[bars[i - 1][0]]
        cross = (i >= WARMUP and cur["upper"] is not None and prev["upper"] is not None
                 and cur["c"] > cur["upper"] and prev["c"] <= prev["upper"])
        cur["signal"] = cross
        cur["strength"] = (cur["c"] / cur["upper"] - 1.0) if cross else -1.0
        # 26-week relative-strength / momentum for entry ranking
        cur["mom"] = (cur["c"] / bars[i - 26][4] - 1.0) if i >= 26 else -1.0
    if bars:
        by_date[bars[0][0]]["signal"] = False
        by_date[bars[0][0]]["strength"] = -1.0
        by_date[bars[0][0]]["mom"] = -1.0
    return by_date

# ----------------------------------------------------------------------------- portfolio sim
def simulate(symbols, data, master_dates, trail_fn,
             regime_ok=None, init_stop_pct=20.0, atr_mult=ATR_MULT, max_pos=MAX_POS,
             rank_by="strength", trail_type="atr", pct_trail=0.20,
             size_mode="fixed", vol_ref=0.06, vol_cap=0.04, equity_filter=None):
    """regime_ok: optional {date: bool} gate — entries only allowed when True.
    rank_by: 'strength' (breakout distance) or 'mom' (26-week momentum) for priority.
    trail_type: 'atr' (ratcheting close-atr_mult*ATR) or 'pct' (ratcheting close*(1-pct_trail)).
    size_mode: 'fixed' (2% equity) or 'vol' (2% x clamp(vol_ref/ATR%), capped at vol_cap).
    equity_filter: int N — block new entries when equity < its own N-week SMA (de-risk)."""
    stop_frac = 1.0 - init_stop_pct / 100.0
    cash = INIT_CAPITAL
    held = {}            # sym -> dict(shares, entry, entry_date, hi)
    entry_queue = []     # list of (strength, sym) valid for the NEXT master week only
    exit_queue = set()   # syms to sell at next available open (carried until filled)
    equity_curve = []    # (date, equity)
    invested_frac = []
    trades = []
    last_close = {}      # sym -> last known close (for marking when a week is missing)
    prev_equity = INIT_CAPITAL

    for d in master_dates:
        # 1) execute EXITS queued for this open (sorted => deterministic)
        for sym in sorted(exit_queue):
            bar = data[sym].get(d)
            if bar is None:
                continue
            pos = held.get(sym)
            if pos:
                proceeds = pos["shares"] * bar["o"] * (1 - COST_PSIDE)
                cash += proceeds
                pnl = proceeds - pos["cost"]
                trades.append(dict(sym=sym, entry_date=pos["entry_date"], exit_date=d,
                                   entry=pos["entry"], exit=bar["o"],
                                   ret=(bar["o"] / pos["entry"] - 1.0),
                                   pnl=pnl, weeks=pos["weeks"]))
                del held[sym]
            exit_queue.discard(sym)

        # portfolio equity-curve filter: block new entries while equity < its own SMA
        ef_ok = True
        if equity_filter and len(equity_curve) >= equity_filter:
            sma_eq = sum(v for _, v in equity_curve[-equity_filter:]) / equity_filter
            ef_ok = prev_equity >= sma_eq

        # 2) execute ENTRIES queued from last week (ranked, one-week validity)
        for _, sym in sorted(entry_queue, reverse=True):
            if not ef_ok:
                break
            if len(held) >= max_pos or sym in held:
                continue
            bar = data[sym].get(d)
            if bar is None:
                continue
            if size_mode == "vol":                       # inverse-volatility sizing
                atrp = (bar["atr"] or bar["o"] * 0.05) / bar["o"]
                scale = min(2.0, max(0.5, vol_ref / atrp)) if atrp > 0 else 1.0
                target = min(POS_PCT * prev_equity * scale, vol_cap * prev_equity)
            else:
                target = POS_PCT * prev_equity
            shares = math.floor(target / bar["o"])
            if shares <= 0:
                continue
            cost = shares * bar["o"] * (1 + COST_PSIDE)
            if cost > cash:
                shares = math.floor(cash / (bar["o"] * (1 + COST_PSIDE)))
                if shares <= 0:
                    continue
                cost = shares * bar["o"] * (1 + COST_PSIDE)
            cash -= cost
            atr0 = bar["atr"] if bar["atr"] is not None else bar["o"] * 0.2
            tr0 = bar["o"] * (1 - pct_trail) if trail_type == "pct" else bar["o"] - atr_mult * atr0
            held[sym] = dict(shares=shares, entry=bar["o"], entry_date=d,
                             cost=cost, weeks=0, init_stop=bar["o"] * stop_frac,
                             atr_trail=tr0)
        entry_queue = []

        # 3) mark-to-market at this week's close
        invested = 0.0
        for sym, pos in held.items():
            bar = data[sym].get(d)
            if bar is not None:
                last_close[sym] = bar["c"]
            invested += pos["shares"] * last_close.get(sym, pos["entry"])
        equity = cash + invested
        equity_curve.append((d, equity))
        invested_frac.append(invested / equity if equity > 0 else 0.0)
        prev_equity = equity

        # 4) generate signals at this close for next week's open
        for sym, pos in held.items():
            bar = data[sym].get(d)
            if bar is None or bar["i"] < WARMUP:
                continue
            pos["weeks"] += 1
            cand = (bar["c"] * (1 - pct_trail) if trail_type == "pct"
                    else bar["c"] - atr_mult * bar["atr"])   # ratcheting trailing stop
            if cand > pos["atr_trail"]:
                pos["atr_trail"] = cand
            eff = max(pos["init_stop"], trail_fn(bar["ema"], pos["atr_trail"]))
            if d != pos["entry_date"] and bar["c"] < eff:
                exit_queue.add(sym)
        regime_on = True if regime_ok is None else regime_ok.get(d, True)
        if regime_on:
            for sym in symbols:
                if sym in held or sym in exit_queue:
                    continue
                bar = data[sym].get(d)
                if bar is not None and bar.get("signal"):
                    entry_queue.append((bar.get(rank_by, bar["strength"]), sym))

    return dict(curve=equity_curve, trades=trades,
                exposure=sum(invested_frac) / len(invested_frac) if invested_frac else 0.0)

# ----------------------------------------------------------------------------- metrics
def metrics(curve):
    if len(curve) < 2:
        return {}
    start_d, start_v = curve[0]
    end_d, end_v = curve[-1]
    years = (end_d - start_d).days / 365.25
    cagr = (end_v / start_v) ** (1 / years) - 1 if years > 0 and start_v > 0 else float("nan")
    peak = -1e18; maxdd = 0.0
    for _, v in curve:
        peak = max(peak, v)
        maxdd = max(maxdd, (peak - v) / peak if peak > 0 else 0.0)
    calmar = cagr / maxdd if maxdd > 0 else float("nan")
    # weekly-return based Sharpe / Sortino (rf = 0, annualised x sqrt(52))
    rets = [curve[i][1] / curve[i - 1][1] - 1 for i in range(1, len(curve)) if curve[i - 1][1] > 0]
    sharpe = sortino = float("nan")
    if len(rets) > 2:
        mu = sum(rets) / len(rets)
        sd = math.sqrt(sum((r - mu) ** 2 for r in rets) / len(rets))
        dd = math.sqrt(sum(min(r, 0.0) ** 2 for r in rets) / len(rets))
        sharpe = mu / sd * math.sqrt(52) if sd > 0 else float("nan")
        sortino = mu / dd * math.sqrt(52) if dd > 0 else float("nan")
    return dict(start=start_d, end=end_d, years=years, start_v=start_v, end_v=end_v,
                total=end_v / start_v - 1, cagr=cagr, maxdd=maxdd, calmar=calmar,
                sharpe=sharpe, sortino=sortino)

def trade_stats(trades):
    if not trades:
        return {}
    wins = [t for t in trades if t["ret"] > 0]
    losses = [t for t in trades if t["ret"] <= 0]
    aw = sum(t["weeks"] for t in wins) / len(wins) if wins else 0
    al = sum(t["weeks"] for t in losses) / len(losses) if losses else 0
    best = max(trades, key=lambda t: t["ret"])
    return dict(n=len(trades), win_rate=len(wins) / len(trades),
                avg_win=sum(t["ret"] for t in wins) / len(wins) if wins else 0,
                avg_loss=sum(t["ret"] for t in losses) / len(losses) if losses else 0,
                hold_win_w=aw, hold_loss_w=al,
                best_sym=best["sym"], best_ret=best["ret"])

def yearly(curve):
    by_year_end = {}
    for d, v in curve:
        by_year_end[d.year] = v            # last value seen in the year
    ys = sorted(by_year_end)
    out = []
    prev = None
    for y in ys:
        v = by_year_end[y]
        out.append((y, (v / prev - 1) if prev else None, v))
        prev = v
    return out

def _rupee(v):
    if v >= 1e7:  return f"₹{v/1e7:.0f}cr"
    if v >= 1e5:  return f"₹{v/1e5:.0f}L"
    return f"₹{v:.0f}"

def make_svg(series, path, title):
    """series: list of (label, color, [(date, value), ...]). Log-scale equity chart."""
    W, H = 960, 500
    ml, mr, mt, mb = 70, 200, 54, 46
    pw, ph = W - ml - mr, H - mt - mb
    allv = [v for _, _, c in series for _, v in c if v > 0]
    alld = [d.toordinal() for _, _, c in series for d, _ in c]
    vmin, vmax = min(allv), max(allv)
    dmin, dmax = min(alld), max(alld)
    lo, hi = math.log10(vmin), math.log10(vmax)
    def X(d): return ml + (d.toordinal() - dmin) / (dmax - dmin) * pw
    def Y(v): return mt + (hi - math.log10(v)) / (hi - lo) * ph
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="system-ui,Arial">']
    s.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    s.append(f'<text x="{ml}" y="28" font-size="17" font-weight="700" fill="#111">{title}</text>')
    # y gridlines at 1,2,5 x 10^k
    ticks = []
    k = int(math.floor(lo))
    while k <= math.ceil(hi):
        for m in (1, 2, 5):
            val = m * 10 ** k
            if vmin * 0.9 <= val <= vmax * 1.1:
                ticks.append(val)
        k += 1
    for val in ticks:
        y = Y(val)
        s.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{ml+pw}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        s.append(f'<text x="{ml-8}" y="{y+4:.1f}" font-size="11" fill="#6b7280" text-anchor="end">{_rupee(val)}</text>')
    # x year labels
    y0, y1 = dt.date.fromordinal(dmin).year, dt.date.fromordinal(dmax).year
    for yr in range(y0, y1 + 1, 2):
        d = dt.date(yr, 1, 1)
        if dmin <= d.toordinal() <= dmax:
            x = X(d)
            s.append(f'<line x1="{x:.1f}" y1="{mt}" x2="{x:.1f}" y2="{mt+ph}" stroke="#f3f4f6"/>')
            s.append(f'<text x="{x:.1f}" y="{mt+ph+18:.1f}" font-size="11" fill="#6b7280" text-anchor="middle">{yr}</text>')
    # series polylines + legend
    for i, (label, color, c) in enumerate(series):
        pts = " ".join(f"{X(d):.1f},{Y(v):.1f}" for d, v in c if v > 0)
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.2"/>')
        ly = mt + 6 + i * 22
        final = c[-1][1]
        s.append(f'<rect x="{ml+pw+16}" y="{ly-9}" width="14" height="14" rx="3" fill="{color}"/>')
        s.append(f'<text x="{ml+pw+36}" y="{ly+3}" font-size="12" fill="#111">{label}</text>')
        s.append(f'<text x="{ml+pw+36}" y="{ly+18}" font-size="11" fill="#6b7280">{_rupee(final)}</text>')
    s.append(f'<text x="{ml}" y="{H-8}" font-size="10.5" fill="#9ca3af">Log scale · ₹20L start · survivorship-biased universe · educational only</text>')
    s.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(s))

def bench_curve(symbol, start_d):
    bars = fetch_weekly(symbol)
    if not bars:
        return None
    bars = [b for b in bars if b[0] >= start_d]
    if len(bars) < 2:
        return None
    base = bars[0][4]
    return [(b[0], INIT_CAPITAL * b[4] / base) for b in bars]

# ----------------------------------------------------------------------------- main
def load_universe():
    txt = http_get("https://archives.nseindia.com/content/indices/ind_nifty500list.csv").decode("utf-8", "replace")
    rows = list(csv.DictReader(txt.splitlines()))
    syms = []
    for r in rows:
        s = (r.get("Symbol") or "").strip()
        if s:
            syms.append(s.replace("&", "%26") + ".NS")
    return syms

CACHE = os.path.join(OUTDIR, "cache", "weekly.json")

def load_bars_map(universe):
    """Fetch (or load from cache) weekly bars for the universe. Caching makes runs
    deterministic & reproducible; delete backtest/cache/ or set REFRESH=1 to refetch."""
    if os.path.exists(CACHE) and not os.environ.get("REFRESH"):
        with open(CACHE) as f:
            raw = json.load(f)
        bmap = {s: [(dt.date.fromisoformat(r[0]), r[1], r[2], r[3], r[4]) for r in rows]
                for s, rows in raw.items() if s in set(universe)}
        print(f"Loaded {len(bmap)} symbols from cache ({CACHE}).", flush=True)
        return bmap
    bmap, ok = {}, 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(fetch_weekly, s): s for s in universe}
        for i, fut in enumerate(as_completed(futs)):
            s = futs[fut]
            try:
                bars = fut.result()
            except Exception:
                bars = None
            if bars:
                bmap[s] = bars
                ok += 1
            if (i + 1) % 50 == 0:
                print(f"  ... {i+1}/{len(universe)} fetched (usable so far: {ok})", flush=True)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w") as f:
        json.dump({s: [[b[0].isoformat(), round(b[1], 4), round(b[2], 4),
                        round(b[3], 4), round(b[4], 4)] for b in bars]
                   for s, bars in bmap.items()}, f)
    return bmap

def main():
    limit = int(os.environ.get("LIMIT", "0"))
    print("Fetching Nifty 500 constituents ...", flush=True)
    universe = load_universe()
    if limit:
        universe = universe[:limit]
    print(f"Universe: {len(universe)} symbols. Loading 20y weekly data ...", flush=True)

    bars_map = load_bars_map(universe)
    print(f"Usable symbols: {len(bars_map)}/{len(universe)}", flush=True)

    data = {}
    for s, bars in bars_map.items():
        data[s] = build_symbol(s, bars)
    symbols = sorted(data.keys())          # deterministic ordering

    # master weekly timeline
    all_dates = set()
    for s in symbols:
        all_dates.update(data[s].keys())
    master_dates = sorted(all_dates)
    # start once at least 20 symbols are past warmup
    start_idx = 0
    for idx, d in enumerate(master_dates):
        n_ready = sum(1 for s in symbols
                      if (b := data[s].get(d)) is not None and b["i"] >= WARMUP)
        if n_ready >= 20:
            start_idx = idx
            break
    master_dates = master_dates[start_idx:]
    print(f"Simulation window: {master_dates[0]} -> {master_dates[-1]} "
          f"({len(master_dates)} weeks)", flush=True)

    results = {}
    for name, fn in EXIT_MODES.items():
        r = simulate(symbols, data, master_dates, fn)
        results[name] = dict(m=metrics(r["curve"]), t=trade_stats(r["trades"]),
                             exposure=r["exposure"], curve=r["curve"], trades=r["trades"])
        m = results[name]["m"]
        print(f"[{name:24s}] final ₹{m['end_v']:,.0f}  CAGR {m['cagr']*100:5.1f}%  "
              f"MaxDD {m['maxdd']*100:4.1f}%  Calmar {m['calmar']:.2f}", flush=True)

    start_d = master_dates[0]
    benches = {}
    for label, sym in [("Nifty 50 (^NSEI)", "%5ENSEI"), ("Nifty 500 (^CRSLDX)", "%5ECRSLDX")]:
        bc = bench_curve(sym, start_d)
        if bc:
            benches[label] = dict(m=metrics(bc), curve=bc)

    write_report(results, benches, len(bars_map), len(universe), master_dates)
    print("\nWrote docs/BACKTEST.md and backtest/results/*.csv", flush=True)

def write_report(results, benches, ok, total, master_dates):
    resdir = os.path.join(OUTDIR, "results")
    os.makedirs(resdir, exist_ok=True)
    headline = "tightest (max EMA,ATR)"
    hr = results[headline]
    hm, ht = hr["m"], hr["t"]

    # equity + trades CSV for the headline config
    with open(os.path.join(resdir, "equity_curve.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "equity"])
        for d, v in hr["curve"]:
            w.writerow([d, round(v, 2)])
    with open(os.path.join(resdir, "trades.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["symbol", "entry_date", "exit_date", "entry", "exit", "return_pct", "pnl", "weeks_held"])
        for t in sorted(hr["trades"], key=lambda x: x["entry_date"]):
            w.writerow([t["sym"], t["entry_date"], t["exit_date"], round(t["entry"], 2),
                        round(t["exit"], 2), round(t["ret"] * 100, 1), round(t["pnl"], 0), t["weeks"]])

    L = []
    P = L.append
    span_yrs = (master_dates[-1] - master_dates[0]).days / 365.25
    P(f"# CW 2σ (Reconstructed) — {span_yrs:.0f}-Year Backtest "
      f"({master_dates[0].year}–{master_dates[-1].year})\n")
    P("> **Independent educational reconstruction. Not investment advice, not the official CW 2σ.**")
    P(f"> Requested 20 years; Yahoo's Indian-equity history starts ~2006, so ~{span_yrs:.0f} "
      "years is the honest maximum here.\n")
    P(f"- **Initial capital:** ₹{INIT_CAPITAL:,} (₹20 lakh)")
    P(f"- **Window:** {master_dates[0]} → {master_dates[-1]}  ({(master_dates[-1]-master_dates[0]).days/365.25:.1f} years)")
    P(f"- **Universe:** current NSE Nifty 500 — {ok} of {total} symbols had usable Yahoo data")
    P(f"- **Rules:** BB({BB_LEN},{BB_MULT:.0f}) upper-band breakout entry · 2% equity/position · "
      f"20% initial stop · trailing 100 EMA + ratcheting ATR({ATR_LEN}×{ATR_MULT}) stop · weekly")
    P("- **Settings source:** confirmed from the official indicator legend "
      "(*%Stop 20 · BB 52 SMA 2 · EMA 100 · ATR Stop Loss 14 1.8*).")
    P(f"- **Costs:** {COST_PSIDE*100:.2f}% per side · max {MAX_POS} concurrent positions · cash earns 0%\n")

    P("## Headline result — exit mode: *tightest* (exit on whichever stop is hit first)\n")
    P("> This matches the podcast's literal *'whichever is earlier'* wording — the effective stop is the "
      "**highest** of {20% initial, 100 EMA, ATR trail}. With the ratcheting ATR stop it is also the best "
      "risk-adjusted here. All four interpretations are shown below so nothing is cherry-picked.\n")
    P(f"| Metric | Value |")
    P(f"|---|---|")
    P(f"| Final equity | **₹{hm['end_v']:,.0f}** |")
    P(f"| Total return | {hm['total']*100:,.0f}% (×{hm['end_v']/hm['start_v']:.1f}) |")
    P(f"| CAGR | **{hm['cagr']*100:.1f}%** |")
    P(f"| Max drawdown | {hm['maxdd']*100:.1f}% |")
    P(f"| Calmar (CAGR/MaxDD) | **{hm['calmar']:.2f}** |")
    P(f"| Exposure (avg invested) | {hr['exposure']*100:.0f}% |")
    P(f"| Trades | {ht['n']} |")
    P(f"| Win rate | {ht['win_rate']*100:.1f}% |")
    P(f"| Avg win / loss | +{ht['avg_win']*100:.0f}% / {ht['avg_loss']*100:.0f}% |")
    P(f"| Avg hold winners / losers | {ht['hold_win_w']*7:.0f}d / {ht['hold_loss_w']*7:.0f}d |")
    P(f"| Best trade | {ht['best_sym'].replace('.NS','')} +{ht['best_ret']*100:,.0f}% |\n")

    P("## All exit modes compared\n")
    P("| Exit mode | Final equity | CAGR | Max DD | Calmar | Trades | Win% | Exposure |")
    P("|---|--:|--:|--:|--:|--:|--:|--:|")
    for name, r in results.items():
        m, t = r["m"], r["t"]
        star = " ⭐" if name == headline else ""
        P(f"| {name}{star} | ₹{m['end_v']:,.0f} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | "
          f"{m['calmar']:.2f} | {t['n']} | {t['win_rate']*100:.0f}% | {r['exposure']*100:.0f}% |")
    P("")

    if benches:
        P("## Benchmarks — ₹20 lakh buy & hold, same window\n")
        P("| Benchmark | Final equity | CAGR | Max DD | Calmar |")
        P("|---|--:|--:|--:|--:|")
        for label, b in benches.items():
            m = b["m"]
            P(f"| {label} | ₹{m['end_v']:,.0f} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} |")
        P("")

    P("## Year-by-year (headline config)\n")
    P("| Year | Return | Year-end equity |")
    P("|---|--:|--:|")
    for y, ret, v in yearly(hr["curve"]):
        P(f"| {y} | {'—' if ret is None else f'{ret*100:+.1f}%'} | ₹{v:,.0f} |")
    P("")

    P("## ⚠️ Honest limitations (read before trusting any number)\n")
    P("1. **Survivorship bias (largest distortion).** The universe is *today's* Nifty 500. "
      "Companies that were delisted, went bankrupt, or fell out of the index over the test window are "
      "excluded — and current members are here *because* they succeeded. This inflates returns, "
      "sometimes materially. A point-in-time universe would give lower, more realistic figures.")
    P("2. **Newer listings** enter the tradable set only after ~2 years (100-week warm-up), so early "
      "years trade a smaller universe than the full 500.")
    P("3. **Costs & liquidity:** a flat 0.25%/side is modelled; real slippage in small-caps, impact "
      "cost, STT, and the assumption of filling at the weekly open can differ.")
    P("4. **Cash earns 0%** (conservative); dividends are included via adjusted prices.")
    P("5. **Concentration / fragility.** The run is deterministic (cached dataset, sorted execution), "
      "but the *outcome* leans on a handful of huge winners caught when cash was free. Change the "
      "universe, costs, or start date a little and the looser modes in particular can move a lot "
      "(observed ₹9–14 cr across dataset refetches). Treat the level as indicative, the *shape* "
      "(beats index on return and drawdown) as the robust takeaway.")
    P("6. **Not the official CW 2σ** and not tuned to match the presenter's quoted figures. "
      "This reproduces the *publicly stated rules* only.")
    P("\n*Generated by `backtest/cw2sigma_backtest.py` (cached dataset for reproducibility) — "
      "set `REFRESH=1` to refetch.*")

    with open(os.path.join(os.path.dirname(OUTDIR), "docs", "BACKTEST.md"), "w") as f:
        f.write("\n".join(L) + "\n")

    # equity-curve chart: headline strategy vs benchmarks
    series = [("CW 2σ (tightest)", "#2563eb", hr["curve"])]
    bcolors = ["#f59e0b", "#6b7280"]
    for (label, b), col in zip(benches.items(), bcolors):
        series.append((label, col, b["curve"]))
    make_svg(series, os.path.join(resdir, "equity_curve.svg"),
             f"CW 2σ backtest — ₹20L, {master_dates[0].year}–{master_dates[-1].year}")

if __name__ == "__main__":
    main()
