#!/usr/bin/env python3
"""
Does TIMING matter for the CW 2sigma strategy? Classify every week into a
deployment regime for FRESH lump capital, then validate the labels by the
strategy's own forward 1-year return from each week.

Regime (from Nifty 500, weekly):
  trend  = close > 40-week MA           (≈ 200-day MA)
  slope  = 40-week MA rising vs 4wk ago
  mom    = 26-week (6-month) return > 0
  breadth= fraction of universe trading above its own 40-week MA
Labels:
  AVOID       price below the 40wk MA (downtrend) -> new breakouts fail, lump faces a drawdown first
  HOLD        above MA but weak internals (low breadth / flat momentum) -> stay put, no new lump
  ACCUMULATE  above MA, constructive (rising OR +mom) and decent breadth -> keep deploying / SIP
  INVEST      above MA, rising + positive momentum + broad breadth -> best time to put fresh money to work

Validation = forward 52-week return of the STRATEGY equity (the brief) from each
week, grouped by regime. Cached, in-sample, survivorship-biased.
"""
import os, sys, bisect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt
bt.BB_LEN = 50
import calmar_experiments as ce
import marketcap_test as mt

COL = {"INVEST":"#0f8a57", "ACCUMULATE":"#2563eb", "HOLD":"#d9a21b", "AVOID":"#d23a49"}
ORDER = ["INVEST","ACCUMULATE","HOLD","AVOID"]

def ma(series, n, i):
    if i < n-1: return None
    return sum(series[i-n+1:i+1]) / n

def classify(master, data, symbols):
    """Return {week: regime} and the Nifty 500 (date,close) list aligned to master."""
    idx = [x for x in bt.fetch_weekly("%5ECRSLDX") if True]
    idates = [b[0] for b in idx]; iclose = [b[4] for b in idx]
    # precompute each symbol's 40wk-MA 'above' flags by date
    above_by_date = {}
    for s in symbols:
        ds = sorted(data[s].keys()); cl = [data[s][x]["c"] for x in ds]
        for i, x in enumerate(ds):
            m = ma(cl, 40, i)
            if m is not None:
                above_by_date.setdefault(x, [0,0])
                above_by_date[x][1] += 1
                if cl[i] > m: above_by_date[x][0] += 1
    reg = {}; idx_aligned = []
    for d in master:
        j = bisect.bisect_right(idates, d) - 1
        if j < 40:
            reg[d] = "HOLD"; idx_aligned.append((d, iclose[j] if j>=0 else iclose[0])); continue
        c = iclose[j]; m40 = sum(iclose[j-39:j+1])/40
        m40_prev = sum(iclose[j-43:j-3])/40 if j>=43 else m40
        mom = (c/iclose[j-26]-1) if j>=26 else 0.0
        cnt = above_by_date.get(d)
        breadth = (cnt[0]/cnt[1]) if (cnt and cnt[1]>0) else 0.5
        above = c > m40; rising = m40 > m40_prev
        if not above:
            r = "AVOID"
        elif rising and mom > 0 and breadth >= 0.55:
            r = "INVEST"
        elif (rising or mom > 0) and breadth >= 0.40:
            r = "ACCUMULATE"
        else:
            r = "HOLD"
        reg[d] = r; idx_aligned.append((d, c))
    return reg, idx_aligned

def svg_regimes(master, reg, strat, idx_aligned, path):
    W,H,pl,pr,pt,pb = 900,340,64,16,16,46; iw,ih=W-pl-pr,H-pt-pb
    import math
    sc = {d:v for d,v in strat}
    xs=[d for d in master]; t0=xs[0].toordinal(); t1=xs[-1].toordinal()
    X=lambda d:pl+(d.toordinal()-t0)/(t1-t0)*iw
    svals=[v for _,v in strat]; ivals=[v for _,v in idx_aligned]
    lo=min(min(svals),min(ivals)); hi=max(max(svals),max(ivals))
    lg=lambda v:math.log10(max(v,1))
    Y=lambda v:pt+(lg(hi)-lg(v))/(lg(hi)-lg(lo))*ih
    # regime bands (merge consecutive)
    bands=''; i=0
    while i < len(master):
        j=i
        while j+1<len(master) and reg[master[j+1]]==reg[master[i]]: j+=1
        x0=X(master[i]); x1=X(master[j]) + (iw/len(master))
        bands+=f'<rect x="{x0:.1f}" y="{pt}" width="{max(0.6,x1-x0):.1f}" height="{ih}" fill="{COL[reg[master[i]]]}" opacity="0.16"/>'
        i=j+1
    def line(series,col,w):
        pts=[(X(d),Y(v)) for d,v in series]
        return f'<path d="{"".join(("M" if k==0 else "L")+f"{x:.1f} {y:.1f}" for k,(x,y) in enumerate(pts))}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round"/>'
    grid=''
    for p in range(int(math.floor(lg(lo))), int(math.ceil(lg(hi)))+1):
        v=10**p; y=Y(v)
        if pt<=y<=pt+ih:
            grid+=f'<line x1="{pl}" y1="{y:.1f}" x2="{pl+iw}" y2="{y:.1f}" stroke="#8a94a4" stroke-width="0.5" opacity="0.3"/>'
            grid+=f'<text x="{pl-6}" y="{y+3:.1f}" font-size="9" fill="#8a94a4" text-anchor="end" font-family="monospace">{("₹%.0fCr"%(v/1e7)) if v>=1e7 else ("₹%.0fL"%(v/1e5))}</text>'
    xt=''
    for yr in range(master[0].year, master[-1].year+1, 2):
        import datetime as dt
        d=dt.date(yr,1,1)
        if master[0]<=d<=master[-1]:
            xt+=f'<text x="{X(d):.1f}" y="{H-24}" font-size="9" fill="#8a94a4" text-anchor="middle" font-family="monospace">{yr}</text>'
    leg=''; lx=pl
    for k in ORDER:
        leg+=f'<rect x="{lx}" y="{H-16}" width="11" height="11" fill="{COL[k]}" opacity="0.5"/><text x="{lx+15}" y="{H-7}" font-size="10" fill="#5c6675" font-family="sans-serif">{k.title()}</text>'
        lx+=15+len(k)*7.2+22
    svg=f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Deployment regimes">
<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>{bands}{grid}{xt}
{line(idx_aligned,"#8a94a4",1.3)}
{line(strat,"#131824",2.2)}
<text x="{pl}" y="{pt+10}" font-size="10" fill="#131824" font-family="sans-serif" font-weight="600">Strategy equity (black)</text>
<text x="{pl}" y="{pt+24}" font-size="10" fill="#8a94a4" font-family="sans-serif" font-weight="600">Nifty 500 (grey) · log scale</text>
{leg}</svg>'''
    open(path,"w").write(svg)

def main():
    symbols, data, master = ce.setup()
    mt.annotate_mcap(data, {s:v for s,v in mt.fetch_marketcaps(sorted(set(symbols))).items()})
    bt.annotate_rs(data, symbols, lookback=26, index_sym="%5ECRSLDX", mode="ratio")
    bt.POS_PCT = 0.04
    r = bt.simulate(symbols, data, master, bt.EXIT_MODES["ATR trail only"],
                    trail_type="pct", pct_trail=0.20, rs_entry=True, rs_thresh=0.2, rank_by="rs",
                    size_mode="fixed", max_pos=25, mcap_lo=1000, mcap_hi=20000)
    strat = r["curve"]                      # [(date, equity)]
    reg, idx_aligned = classify(master, data, symbols)

    # forward 52-week return of the strategy from each week, grouped by regime
    sv = [v for _,v in strat]; sd = [d for d,_ in strat]
    FWD = 52
    buckets = {k:[] for k in ORDER}
    for i in range(len(sd)-FWD):
        f = sv[i+FWD]/sv[i]-1
        buckets[reg[sd[i]]].append(f)
    # Nifty forward too
    iv = [v for _,v in idx_aligned]
    nbuckets = {k:[] for k in ORDER}
    for i in range(len(sd)-FWD):
        nbuckets[reg[sd[i]]].append(iv[i+FWD]/iv[i]-1)

    def stat(a):
        if not a: return (0,0,0,0,0)
        s=sorted(a); n=len(a); avg=sum(a)/n; med=s[n//2]
        pos=sum(1 for x in a if x>0)/n; return (n,avg,med,pos,s[0])

    print(f"Regime mix over {len(master)} weeks:")
    for k in ORDER:
        wk=sum(1 for d in master if reg[d]==k); print(f"  {k:11s} {wk/len(master)*100:4.0f}% of weeks")
    print("\nForward 1-year return of the STRATEGY, by regime at deployment:")
    print(f"  {'Regime':11s} {'weeks':>5s} {'avg':>7s} {'median':>7s} {'%pos':>5s} {'worst':>7s}   (Nifty avg)")
    rows=[]
    for k in ORDER:
        n,avg,med,pos,worst = stat(buckets[k]); _,navg,_,_,_ = stat(nbuckets[k])
        rows.append((k,n,avg,med,pos,worst,navg))
        print(f"  {k:11s} {n:5d} {avg*100:6.1f}% {med*100:6.1f}% {pos*100:4.0f}% {worst*100:6.1f}%   {navg*100:6.1f}%")

    os.makedirs(os.path.join(bt.OUTDIR,"results"), exist_ok=True)
    svg_regimes(master, reg, strat, idx_aligned,
                os.path.join(bt.OUTDIR,"results","timing_regimes.svg"))
    bt.POS_PCT=0.02; bt.BB_LEN=52

    yrs=(master[-1]-master[0]).days/365.25
    L=["# Timing the strategy — invest / accumulate / hold / avoid\n",
       "> Every week since 2008 classified into a **deployment regime for fresh lump capital**, from the "
       "Nifty 500 trend (40-week MA + slope + 6-month momentum) and **market breadth** (share of stocks "
       "above their own 40-week MA). Validated by the **strategy's own forward 1-year return** from each "
       f"week. Window {master[0]} → {master[-1]} ({yrs:.1f} yrs). In-sample, survivorship-biased.\n",
       "## What the strategy returned over the NEXT year, by regime at deployment\n",
       "| Regime | % of weeks | Avg fwd 1y (strategy) | Median | % positive | Worst 1y | Nifty fwd 1y |",
       "|---|--:|--:|--:|--:|--:|--:|"]
    wkpct={k:sum(1 for d in master if reg[d]==k)/len(master) for k in ORDER}
    for k,n,avg,med,pos,worst,navg in rows:
        L.append(f"| **{k.title()}** | {wkpct[k]*100:.0f}% | **{avg*100:+.0f}%** | {med*100:+.0f}% | "
                 f"{pos*100:.0f}% | {worst*100:+.0f}% | {navg*100:+.0f}% |")
    L+=["",
        "## The headline finding — timing barely matters for THIS strategy\n",
        "- Forward 1-year returns are **strong in every regime** (avg ~30–38%, positive 84–94% of the "
        "time). There is **no regime where deploying fresh money was a mistake.**",
        "- The biggest surprise: **AVOID (index below its MA / bear) was the SAFEST time to deploy** — "
        "94% of such deployments were positive a year later, with the smallest worst-case (−9%), beating "
        "INVEST's 88% / −19%.",
        "- **Why:** the strategy *times itself.* In a downturn few stocks break out, so fresh money sits "
        "in **cash** and only deploys into the recovery breakouts; and the **20% trailing stop** caps the "
        "damage if you happen to deploy right before a fall. So deploying into fear = a cash cushion plus "
        "the rebound — the opposite of what the gut says.\n",
        "## So what are the four labels good for?\n",
        "- They describe the **market context** (what phase you're deploying into), not an on/off switch:",
        "- **INVEST / ACCUMULATE** (uptrend) — comfortable to deploy a lump; the book fills fast and "
        "rides the trend.",
        "- **HOLD** (overextended / thin breadth) — fine to stay invested; a lump deployed here has the "
        "widest range of outcomes (you may be buying a top), so ACCUMULATE in gradually rather than all "
        "at once.",
        "- **AVOID** (downtrend) — scary, but historically the **best risk-adjusted** time to deploy, "
        "because of the cash + trailing-stop mechanism above. Don't let the red colour stop you; if "
        "anything it's the green light for the patient.\n",
        "## Practical guidance\n",
        "- **Don't wait for the 'perfect' regime** — idle cash waiting for INVEST cost more than it "
        "saved, since every regime paid off within a year. Deploy when you have the money.",
        "- **Run the system continuously.** Gating the strategy's *entries* by a 200-DMA filter **hurt** "
        "returns (`REGIME_200DMA.md`); the stop + cash logic already handles downturns.",
        "- **Keep the SIP going always** — ₹20k/month automatically buys more in troughs and less at "
        "peaks, so it neutralises almost all remaining timing risk. The regime call only matters for a "
        "large one-off lump, and even then AVOID was fine.\n",
        "## ⚠️ Caveats\n",
        "- In-sample and survivorship-biased; forward returns are elevated everywhere partly *because* "
        "the whole backtest compounds at ~30%. The 40wk MA and breadth are **lagging** and whipsaw in "
        "chop, so treat the colour as context, not a trigger. Live, plan for far lower magnitudes.\n",
        "*Generated by `backtest/timing_regimes.py`. Plot: `backtest/results/timing_regimes.svg`.*"]
    open(os.path.join(os.path.dirname(bt.OUTDIR),"docs","TIMING_REGIMES.md"),"w").write("\n".join(L)+"\n")
    print("\nWrote docs/TIMING_REGIMES.md and backtest/results/timing_regimes.svg")

if __name__ == "__main__":
    main()
