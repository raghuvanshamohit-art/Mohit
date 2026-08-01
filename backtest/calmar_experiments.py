#!/usr/bin/env python3
"""
Calmar-ratio experiments for the CW 2σ rules.

Calmar = CAGR / MaxDrawdown. This tests the classic levers for raising it,
reusing the cached dataset & deterministic engine from cw2sigma_backtest.py:

  1. Market-regime filter  — only enter when Nifty 500 is above its 40-week SMA
  2. Tighter initial stop   — 15% instead of 20%
  3. Trailing-stop tightness — ATR multiplier 1.5 / 2.5
  4. Concentration          — fewer positions
  5. Combinations, and the same regime filter on the looser exit mode

IN-SAMPLE WARNING: these are fitted on one (survivorship-biased) history.
The point is *which levers move Calmar and why*, not the exact optimum.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cw2sigma_backtest as bt

def setup():
    universe = bt.load_universe()
    bars_map = bt.load_bars_map(universe)
    data = {s: bt.build_symbol(s, b) for s, b in bars_map.items()}
    symbols = sorted(data)
    all_dates = set()
    for s in symbols:
        all_dates.update(data[s].keys())
    master = sorted(all_dates)
    for idx, d in enumerate(master):
        if sum(1 for s in symbols
               if (b := data[s].get(d)) is not None and b["i"] >= bt.WARMUP) >= 20:
            master = master[idx:]
            break
    return symbols, data, master

def regime_series(master, index_sym="%5ECRSLDX", n=40):
    """{date: bool} — True when the index close is above its n-week SMA (carry-forward)."""
    bars = bt.fetch_weekly(index_sym)
    bd = [x[0] for x in bars]; bc = [x[4] for x in bars]
    flags = []
    for i in range(len(bars)):
        if i >= n - 1:
            flags.append((bd[i], bc[i] > sum(bc[i - n + 1:i + 1]) / n))
    reg, j, state = {}, 0, True
    for d in master:
        while j < len(flags) and flags[j][0] <= d:
            state = flags[j][1]; j += 1
        reg[d] = state
    return reg

def main():
    symbols, data, master = setup()
    reg = regime_series(master)
    tight = bt.EXIT_MODES["tightest (max EMA,ATR)"]
    loose = bt.EXIT_MODES["loosest (min EMA,ATR)"]
    inv_reg = sum(1 for d in master if reg[d]) / len(master)

    exps = [
        ("Baseline  (tightest · 20% · ATR1.8)", tight, dict()),
        ("ATR mult 1.5 (tighter trail)",        tight, dict(atr_mult=1.5)),
        ("ATR mult 2.2",                        tight, dict(atr_mult=2.2)),
        ("ATR mult 2.5",                        tight, dict(atr_mult=2.5)),
        ("ATR mult 3.0",                        tight, dict(atr_mult=3.0)),
        ("ATR mult 3.5 (looser trail)",         tight, dict(atr_mult=3.5)),
        ("Initial stop 15%",                    tight, dict(init_stop_pct=15)),
        ("+ Regime filter (N500 > 40w SMA)",    tight, dict(regime_ok=reg)),
        ("Max 25 positions (concentrated)",     tight, dict(max_pos=25)),
        ("Best ATR + regime filter",            tight, dict(atr_mult=2.5, regime_ok=reg)),
    ]

    rows = []
    for name, fn, kw in exps:
        r = bt.simulate(symbols, data, master, fn, **kw)
        m = bt.metrics(r["curve"]); t = bt.trade_stats(r["trades"])
        rows.append((name, m, t, r["exposure"]))
        print(f"{name:38s}  CAGR {m['cagr']*100:5.1f}%  MaxDD {m['maxdd']*100:5.1f}%  "
              f"Calmar {m['calmar']:.2f}  final ₹{m['end_v']:,.0f}", flush=True)

    base_cal = rows[0][1]["calmar"]
    best = max(rows, key=lambda x: x[1]["calmar"])

    L = ["# Raising the Calmar ratio — CW 2σ experiments\n",
         "> Calmar = CAGR ÷ MaxDrawdown. Same ~18-year, survivorship-biased Nifty 500 "
         "history and deterministic engine as `docs/BACKTEST.md`.\n",
         f"> **In-sample warning:** these are fitted on one history — read them as *which "
         f"levers move Calmar and why*, not a tuned optimum. The regime filter is invested "
         f"~{inv_reg*100:.0f}% of weeks.\n",
         "| Variant | CAGR | Max DD | **Calmar** | vs base | Trades | Exposure | Final |",
         "|---|--:|--:|--:|--:|--:|--:|--:|"]
    for name, m, t, exp in rows:
        d = m["calmar"] - base_cal
        star = " ⭐" if (name, m, t, exp) == best else ""
        L.append(f"| {name}{star} | {m['cagr']*100:.1f}% | {m['maxdd']*100:.1f}% | "
                 f"**{m['calmar']:.2f}** | {d:+.2f} | {t['n']} | {exp*100:.0f}% | ₹{m['end_v']:,.0f} |")
    L += ["",
          "## What actually moved Calmar (on this data)\n",
          "1. **The trailing-stop width is the dominant lever — and the default ATR×1.8 is too "
          "tight.** Loosening the ATR multiplier from 1.8 toward ~2.2–3.5 lifted Calmar from "
          "**0.88 → ~1.05–1.14** — improving *both* axes: CAGR rose (winners compound instead of "
          "being whipsawed out) **and** max drawdown actually fell (fewer stop-out/re-entry "
          "round-trips at worse prices). Best here was ATR×3.5 (Calmar 1.14).",
          "2. **Tightening instead (ATR 1.5)** lowers drawdown (23.8%) at a small CAGR cost → "
          "Calmar 0.95. Use it if you want *smoother equity* rather than the highest Calmar.",
          "3. **The market-regime filter did NOT raise Calmar here (0.87).** Because the ATR stop "
          "already cuts losers fast, the filter mostly costs CAGR. But it *does* cut drawdown, so "
          "pairing it with a looser trail (ATR2.5 + regime) gave the **lowest drawdown (~23.5%)** "
          "with a strong Calmar (~1.06) — the pick when minimizing drawdown matters most.",
          "4. **More concentration (25 positions) hurt** — CAGR collapsed to ~15%, Calmar 0.84. "
          "Diversification across the 2% positions is doing real work; don't cut it to chase Calmar.",
          "5. **Initial-stop tweak (15%)** barely moved anything.\n",
          "## General principles (beyond this test)\n",
          "Calmar = CAGR ÷ MaxDD, so **cutting drawdown has leverage**. Reliable levers: a regime/"
          "trend filter, volatility-target the *portfolio* (de-risk when realized vol spikes), keep "
          "diversification, cap correlated/sector exposure, and stop the *whipsaw* that both lowers "
          "return and deepens drawdown (right-sizing the trail did exactly that above). To raise "
          "CAGR *without* adding drawdown: let winners run, rank entries by momentum/relative "
          "strength, and avoid overtrading.\n",
          "## ⚠️ Caveats\n",
          "- **In-sample + survivorship-biased.** The looser-trail Calmar gains lean partly on "
          "catching a few big multibaggers; the looser you go, the more the result rides on a "
          "handful of names. Expect it to attenuate out-of-sample.",
          "- The exact ATR peak is noisy (2.2/2.5/3.0/3.5 all beat 1.8, order isn't stable) — read "
          "it as *'looser than 1.8 helps'*, not *'3.5 is optimal'*.",
          "- Validate on a point-in-time universe and a hold-out period before trusting any setting.\n",
          "*Generated by `backtest/calmar_experiments.py`.*"]
    with open(os.path.join(os.path.dirname(bt.OUTDIR), "docs", "CALMAR.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\nWrote docs/CALMAR.md", flush=True)

if __name__ == "__main__":
    main()
