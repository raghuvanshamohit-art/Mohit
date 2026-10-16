#!/usr/bin/env python3
"""Rank this week's NEW screener candidates (16 Oct 2026) by 26-week RS vs Nifty 500,
to fill the single open slot. Already-held names (TATVA, MVGJL) excluded. Live fetch."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt

LOOKBACK = 26
EQUITY   = 1952477.0      # current paper equity (16 Oct)
CASH     = 93694.0
POS_PCT  = 0.04

# (symbol, screener close) — excludes TATVA & MVGJL (already held)
CANDS = [
    ("TIPSMUSIC",746.9),("SHRINGARMS",313.83),("ORIENTHOT",151.8),("TEXINFRA",128.14),
    ("NAZARA",418.15),("GOODLUCK",593.05),("IRISDOREME",64.34),("SANATHAN",556.65),
    ("SHREEPUSHK",503.8),("YUKEN",1152.6),("SOUTHBANK",51.45),("DALMIASUG",481.4),
    ("ADVANCE",158.08),("RUBYMILLS",515.95),("BALRAMCHIN",721.15),("KOPRAN",271.15),
    ("KRISHANA",208.71),
]

def rs_of(sym, index_ratio):
    bars = bt.fetch_weekly(sym + ".NS")
    if not bars or len(bars) < LOOKBACK + 1: return None, (len(bars) if bars else 0)
    c_now, c_past = bars[-1][4], bars[-1-LOOKBACK][4]
    if c_past <= 0: return None, len(bars)
    return (c_now/c_past)/index_ratio - 1.0, len(bars)

def main():
    ib = bt.fetch_weekly("%5ECRSLDX")
    if not ib or len(ib) < LOOKBACK+1: print("No index data"); return
    iratio = ib[-1][4]/ib[-1-LOOKBACK][4]
    print(f"Nifty 500 26wk ratio {iratio:.4f} ({(iratio-1)*100:+.1f}%)\n", flush=True)
    rows = []
    for sym, close in CANDS:
        rs, n = rs_of(sym, iratio); rows.append((sym, close, rs, n))
        print(f"  {sym:12s} ₹{close:>9,.2f}  " + (f"RS {rs*100:+6.1f}%" if rs is not None else f"no 26w RS (bars={n})"), flush=True)
    ranked = sorted([r for r in rows if r[2] is not None], key=lambda r:-r[2])
    nod = [r for r in rows if r[2] is None]
    print("\n=== RANKED BY 26-WEEK RS ===", flush=True)
    for i,(sym,close,rs,n) in enumerate(ranked,1):
        print(f"{i:>2}. {sym:12s} RS {rs*100:+6.1f}%  ₹{close:,.2f}", flush=True)
    if nod: print("\nNo 26wk RS (recent/SME, no Yahoo data): " + ", ".join(r[0] for r in nod), flush=True)
    if ranked:
        sym, close, rs, n = ranked[0]
        qty = int(POS_PCT*EQUITY//close); cost = qty*close
        print(f"\n=== BUY (fills the open slot): {sym} ===", flush=True)
        print(f"  entry ₹{close:,.2f}  qty {qty}  cost ₹{cost:,.0f}  (RS {rs*100:+.1f}%)  cash left ₹{CASH-cost:,.0f}", flush=True)

if __name__ == "__main__":
    main()
