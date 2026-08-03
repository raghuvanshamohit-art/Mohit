#!/usr/bin/env python3
"""
Same rules, sliced by MARKET-CAP bucket (₹ crore):
  Entry  : upper Bollinger breakout (52,2)
  Filter : outperforming Nifty 500 over 6 months (26w RS > 0)
  Exit   : 20% ratcheting trailing stop
  Sizing : 4% of equity per position
  Buckets: 100-1000, 1000-10000, 10000-20000, 20000-50000, 50000-100000, >100000

Market cap is point-in-time: current market cap scaled back by the adjusted-price
ratio (mcap_t = mcap_now × adj_close_t / adj_close_now), so a stock sits in the
right size band at each date. Reports CAGR and Max drawdown per bucket.
Weekly, ₹20L, 0.25%/side. In-sample & survivorship-biased.
"""
import os, sys, json, urllib.request, http.cookiejar, urllib.parse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt
import calmar_experiments as ce

MCACHE = os.path.join(bt.OUTDIR, "cache", "mcap.json")
BUCKETS = [("100–1000", 100, 1000), ("1000–10000", 1000, 10000),
           ("10000–20000", 10000, 20000), ("20000–50000", 20000, 50000),
           ("50000–100000", 50000, 100000), (">100000", 100000, None)]

def fetch_marketcaps(symbols):
    """Return {symbol(.NS): market_cap_in_crore}. Cached."""
    if os.path.exists(MCACHE) and not os.environ.get("REFRESH"):
        return json.load(open(MCACHE))
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", "Mozilla/5.0")]
    g = lambda u: op.open(u, timeout=30).read().decode("utf-8", "replace")
    try:
        g("https://fc.yahoo.com/")
    except Exception:
        pass
    crumb = urllib.parse.quote(g("https://query1.finance.yahoo.com/v1/test/getcrumb"))
    out = {}
    for i in range(0, len(symbols), 40):
        batch = symbols[i:i + 40]
        url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=" + ",".join(batch) + f"&crumb={crumb}"
        for attempt in range(3):
            try:
                res = json.loads(g(url))["quoteResponse"]["result"]
                for r in res:
                    mc = r.get("marketCap") or (r.get("sharesOutstanding", 0) or 0) * (r.get("regularMarketPrice", 0) or 0)
                    if mc:
                        out[r["symbol"]] = round(mc / 1e7, 1)   # -> ₹ crore
                break
            except Exception:
                time.sleep(1.5 * (attempt + 1))
        if (i + 40) % 200 == 0:
            print(f"  ... mcap {i+40}/{len(symbols)} (have {len(out)})", flush=True)
        time.sleep(0.3)
    json.dump(out, open(MCACHE, "w"))
    return out

def annotate_mcap(data, mcap_cr):
    """bar['mcap'] = current market cap (cr) scaled by adj_close_t / latest adj_close."""
    for s in data:
        bars = sorted(data[s])
        mc = mcap_cr.get(s)
        if not mc or not bars:
            for d in bars:
                data[s][d]["mcap"] = None
            continue
        last_c = data[s][bars[-1]]["c"]
        for d in bars:
            data[s][d]["mcap"] = mc * data[s][d]["c"] / last_c if last_c else None

def main():
    symbols, data, master = ce.setup()
    # data keys are already Yahoo tickers (e.g. RELIANCE.NS)
    mc_raw = fetch_marketcaps(sorted(set(symbols)))
    mcap_cr = {s: mc_raw.get(s) for s in symbols}
    have = sum(1 for s in symbols if mcap_cr.get(s))
    print(f"Market cap resolved: {have}/{len(symbols)} ({have/len(symbols)*100:.0f}%)", flush=True)
    annotate_mcap(data, mcap_cr)
    bt.annotate_rs(data, symbols, lookback=26, index_sym="%5ECRSLDX")
    bt.POS_PCT = 0.04
    trailonly = bt.EXIT_MODES["ATR trail only"]

    rows = []
    for name, lo, hi in BUCKETS:
        r = bt.simulate(symbols, data, master, trailonly,
                        trail_type="pct", pct_trail=0.20, rs_entry=True,
                        size_mode="fixed", max_pos=50, mcap_lo=lo, mcap_hi=hi)
        m = bt.metrics(r["curve"], periods_per_year=52); t = bt.trade_stats(r["trades"])
        n = t.get("n", 0)
        rows.append((name, lo, hi, m, t, r["exposure"], n))
        print(f"{name:14s} (₹cr)  CAGR {m['cagr']*100:5.1f}%   MaxDD {m['maxdd']*100:5.1f}%   "
              f"Calmar {m['calmar']:.2f}   Trades {n:4d}   Exp {r['exposure']*100:3.0f}%   "
              f"₹{m['end_v']:,.0f}", flush=True)
    bt.POS_PCT = 0.02

    L = ["# Market-cap bucket sweep (4% position size)\n",
         "> **Rules (fixed).** Entry: upper Bollinger breakout (52,2) **and** outperforming Nifty 500 "
         "over 6 months (26w RS > 0). Exit: 20% ratcheting trailing stop. Sizing: 4% of equity. "
         "Weekly, ₹20L, 0.25%/side. Buckets in **₹ crore**, point-in-time (current market cap scaled "
         "by adjusted-price ratio).\n",
         f"- **Window:** {master[0]} → {master[-1]} ({(master[-1]-master[0]).days/365.25:.1f} years) · "
         f"market cap resolved for {have}/{len(symbols)} symbols\n",
         "## Results by market-cap bucket\n",
         "| Market cap (₹ cr) | **CAGR** | **Max DD** | Calmar | Sharpe | Trades | Avg invested | Final |",
         "|---|--:|--:|--:|--:|--:|--:|--:|"]
    for name, lo, hi, m, t, exp, n in rows:
        L.append(f"| {name} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | {m['calmar']:.2f} | "
                 f"{m['sharpe']:.2f} | {n} | {exp*100:.0f}% | ₹{m['end_v']:,.0f} |")
    L += ["",
          "## Read-out\n",
          "- **Smaller-cap buckets** (100–1000, 1000–10000) hold the biggest multibaggers, so they "
          "usually show the **highest CAGR — and the deepest drawdowns / thinnest liquidity**. Cost "
          "and slippage (modelled flat at 0.25%/side) bite hardest here in reality.",
          "- **Large/mega-cap buckets** (>50000) are steadier: lower CAGR, shallower drawdown, more "
          "tradable size — but fewer breakout-with-RS candidates, so fewer trades.",
          "- A bucket with very few trades is statistically thin — read its numbers with caution.\n",
          "## ⚠️ Caveats\n",
          "- **Point-in-time market cap is approximate:** it scales *today's* cap back by the "
          "adjusted-price ratio (assumes ~constant shares, ignores dividend drift). Good enough to "
          "bucket, not exact.",
          "- In-sample, survivorship-biased (today's Nifty 500 — so delisted small-caps that failed "
          "are absent, flattering the small-cap buckets most). Small-cap fills at the weekly open are "
          "optimistic. Treat small-cap CAGR as an upper bound.\n",
          "*Generated by `backtest/marketcap_test.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "MARKETCAP.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\nWrote docs/MARKETCAP.md", flush=True)

if __name__ == "__main__":
    main()
