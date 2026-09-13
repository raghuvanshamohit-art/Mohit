#!/usr/bin/env python3
"""
Single market-cap band runner (reusable). Rules:
  breakout + Nifty 500 6-month RS + 20% ratcheting trailing stop + 4% sizing, weekly.
Band (₹ crore) from env LO / HI (defaults 1000 / 20000). Reports CAGR and Max drawdown.
Cached, deterministic. In-sample & survivorship-biased.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt
import calmar_experiments as ce
import marketcap_test as mt

def main():
    LO = float(os.environ.get("LO", "1000"))
    HI = os.environ.get("HI", "20000")
    HI = float(HI) if HI not in ("", "none", "None") else None
    RS_LO = float(os.environ.get("RS_LO", "0"))          # min 6-month outperformance
    RS_HI = os.environ.get("RS_HI", "")                  # max (blank = no cap)
    RS_HI = float(RS_HI) if RS_HI not in ("", "none", "None") else None
    symbols, data, master = ce.setup()
    mc_raw = mt.fetch_marketcaps(sorted(set(symbols)))
    mt.annotate_mcap(data, {s: mc_raw.get(s) for s in symbols})
    bt.annotate_rs(data, symbols, lookback=26, index_sym="%5ECRSLDX")
    bt.POS_PCT = 0.04
    r = bt.simulate(symbols, data, master, bt.EXIT_MODES["ATR trail only"],
                    trail_type="pct", pct_trail=0.20, rs_entry=True, size_mode="fixed",
                    max_pos=50, mcap_lo=LO, mcap_hi=HI, rs_thresh=RS_LO, rs_thresh_hi=RS_HI)
    bt.POS_PCT = 0.02
    m = bt.metrics(r["curve"], periods_per_year=52); t = bt.trade_stats(r["trades"])
    band = f"{int(LO)}–{int(HI) if HI else '∞'}"
    rsband = f"RS {RS_LO:g}–{RS_HI:g}" if RS_HI is not None else f"RS >{RS_LO:g}"
    print(f"Market cap ₹{band} cr | {rsband} | window {master[0]} -> {master[-1]} "
          f"({(master[-1]-master[0]).days/365.25:.1f} yrs)")
    print(f"  CAGR {m['cagr']*100:.1f}%   Max DD {m['maxdd']*100:.1f}%   Calmar {m['calmar']:.2f}   "
          f"Sharpe {m['sharpe']:.2f}   Trades {t['n']}   Win {t['win_rate']*100:.0f}%   "
          f"Exposure {r['exposure']*100:.0f}%   Final ₹{m['end_v']:,.0f}")

    n500 = [x for x in bt.fetch_weekly("%5ECRSLDX") if x[0] >= master[0]]
    n500c = [(x[0], bt.INIT_CAPITAL * x[4] / n500[0][4]) for x in n500]
    bt.make_svg([(f"₹{band}cr band (Calmar {m['calmar']:.2f})", "#2563eb", r["curve"]),
                 ("Nifty 500 buy&hold", "#f59e0b", n500c)],
                os.path.join(bt.OUTDIR, "results", "mcap_band_equity.svg"),
                f"Market cap Rs{band} cr — breakout + N500 6M RS + 20% trail (log)")
    print("Wrote backtest/results/mcap_band_equity.svg")

if __name__ == "__main__":
    main()
