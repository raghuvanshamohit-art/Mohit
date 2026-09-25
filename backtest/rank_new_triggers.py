#!/usr/bin/env python3
"""
Rank this week's NEW screener triggers by 26-week relative strength vs Nifty 500,
using the user's exact formula:
    RS = (Close / Close_26w_ago) / (N500_Close / N500_Close_26w_ago) - 1
Then size the top-N at 4% of current equity to fill the paper book to 25 names.
Live fetch from Yahoo (weekly, adjusted). Prints a ranked table.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt

LOOKBACK = 26
EQUITY   = 2011112.0     # current paper-book equity (as of 25 Sep 2026)
POS_PCT  = 0.04
SLOTS    = 8             # 25 cap - 17 held

# (screener Sr., symbol, screener close)  -- row 13 was cut off
CANDS = [
    (1,"SHANTIGOLD",325.68),(2,"ROLEXRINGS",195.35),(3,"MUKANDLTD",167.05),
    (4,"ENGINERSIN",315.65),(5,"DHAMPURSUG",174.67),(6,"RPGLIFE",3055.0),
    (7,"STEELCAS",376.5),(8,"DYNAMATECH",13153.0),(9,"PGIL",1329.1),
    (10,"BALRAMCHIN",685.8),(11,"BLUSPRING",145.12),(12,"JASH",593.85),
    (14,"AYMSYNTEX",290.0),(15,"TCPLPACK",4103.8),(16,"E2E",652.15),
    (17,"HARSHA",460.55),(18,"AARTIPHARM",939.55),(19,"ONEPOINT",69.6),
    (20,"VINCOFE",184.15),(21,"SOUTHBANK",49.95),(22,"MARKSANS",336.95),
    (23,"KINGFA",6211.0),(24,"GNA",617.65),(25,"SGIL",642.35),
    (26,"SANATHAN",523.25),(27,"SRHHYPOLTD",594.8),(28,"KDDL",4033.4),
    (29,"OPTIEMUS",758.55),(30,"PREMIERPOL",95.4),
]

def rs_of(symbol, index_ratio):
    bars = bt.fetch_weekly(symbol + ".NS")
    if not bars or len(bars) < LOOKBACK + 1:
        return None, (len(bars) if bars else 0)
    c_now = bars[-1][4]; c_past = bars[-1 - LOOKBACK][4]
    if c_past <= 0:
        return None, len(bars)
    stock_ratio = c_now / c_past
    return stock_ratio / index_ratio - 1.0, len(bars)

def main():
    ib = bt.fetch_weekly("%5ECRSLDX")
    if not ib or len(ib) < LOOKBACK + 1:
        print("Could not fetch Nifty 500 index — aborting."); return
    index_ratio = ib[-1][4] / ib[-1 - LOOKBACK][4]
    print(f"Nifty 500 26-week ratio = {index_ratio:.4f} (return {(index_ratio-1)*100:+.1f}%)\n", flush=True)

    rows = []
    for sr, sym, close in CANDS:
        rs, n = rs_of(sym, index_ratio)
        rows.append((sym, sr, close, rs, n))
        tag = f"RS {rs*100:+6.1f}%" if rs is not None else f"no 26w RS (bars={n})"
        print(f"  {sym:12s} Sr{sr:>2}  ₹{close:>9,.2f}  {tag}", flush=True)

    ranked = sorted([r for r in rows if r[3] is not None], key=lambda r: -r[3])
    nodata = [r for r in rows if r[3] is None]

    print("\n=== RANKED BY 26-WEEK RS (strongest first) ===", flush=True)
    for i, (sym, sr, close, rs, n) in enumerate(ranked, 1):
        print(f"{i:>2}. {sym:12s} RS {rs*100:+6.1f}%   ₹{close:,.2f}", flush=True)
    if nodata:
        print("\n(No 26-week RS — likely recent listing, <26 weekly bars):", flush=True)
        for sym, sr, close, rs, n in nodata:
            print(f"    {sym:12s} bars={n}  ₹{close:,.2f}", flush=True)

    print(f"\n=== BUY TOP {SLOTS} (4% of ₹{EQUITY:,.0f} = ₹{POS_PCT*EQUITY:,.0f} each) ===", flush=True)
    spend = 0.0
    for i, (sym, sr, close, rs, n) in enumerate(ranked[:SLOTS], 1):
        qty = int(POS_PCT * EQUITY // close)
        cost = qty * close; spend += cost
        print(f"{i}. {sym:12s} entry ₹{close:>9,.2f}  qty {qty:>5d}  cost ₹{cost:>10,.0f}  RS {rs*100:+.1f}%", flush=True)
    print(f"\nTotal deployed: ₹{spend:,.0f}   Cash left: ₹{646030 - spend:,.0f}", flush=True)

if __name__ == "__main__":
    main()
