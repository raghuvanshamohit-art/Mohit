# Long ATM Straddle on NIFTY — 10-Year Backtest

Backtests the strategy **buy 1 ATM Call + buy 1 ATM Put** (a *long straddle*),
rolled monthly and held to expiry, on NIFTY over 10 years. Answers: **how much
return does it generate, month by month, and how much is positive vs negative.**

➡️ **[See the results: `RESULTS.md`](RESULTS.md)** (headline numbers + month-wise table)

> **Disclaimer:** Educational. Option premiums are **modelled** (Black-Scholes
> priced at India VIX), because real 10-year NIFTY option-chain data is not
> freely available. Not investment advice.

---

## The bottom line

Over **119 monthly cycles (Aug 2016 → Jul 2026)**:

| | |
|---|---|
| Positive months | **45 (37.8%)** |
| Negative months | **74 (62.2%)** |
| Aggregate return (P&L ÷ cash deployed) | **≈ −10%** |
| 1-lot/month sim | deployed ≈ ₹35.1 lakh → net **≈ −₹3.6 lakh** |

**Buying straddles and holding to expiry loses money here** — option buyers pay
a volatility risk premium, and theta bleeds the ~62% of months where NIFTY
doesn't move enough. The rare big win (COVID crash, Feb 2020, +344%) doesn't
cover the steady drip of losses. Full breakdown in [`RESULTS.md`](RESULTS.md).

---

## How to reproduce

```bash
# 1) Fetch 10y of NIFTY 50 spot + India VIX (Yahoo Finance)
python3 backtest/straddle/fetch_nifty_vix.py

# 2) Run the backtest; print report + write the month-wise table
python3 backtest/straddle/straddle_backtest.py \
    --csv-out backtest/straddle/data/straddle_cycles.csv \
    --md-out  backtest/straddle/RESULTS.md
```

Both scripts are **standard-library only** — no pip install. The committed
`data/nifty_vix_daily.csv` lets you skip step 1 and run offline.

### Useful knobs
| Flag | Default | Meaning |
|------|---------|---------|
| `--rate` | 0.065 | Risk-free rate for Black-Scholes. |
| `--cost-pct` | 0.02 | Round-trip cost as a fraction of premium. |
| `--lot` | 50 | NIFTY lot size (for the rupee simulation). |
| `--csv-out` / `--md-out` | — | Write the per-cycle table / full Markdown report. |

---

## Methodology

- **Universe / cycle:** NIFTY monthly options; one straddle per cycle. Entry =
  first trading day after the previous monthly expiry (a fresh ~30-day option);
  exit = monthly expiry (last Thursday).
- **Strike:** nearest 50 to spot at entry (ATM).
- **Premium (the modelled part):** Black-Scholes call + put, with **India VIX**
  as the implied-volatility input. India VIX *is* the market's ~30-day implied
  vol, so this reproduces realistic premiums rather than guessing them.
- **Payoff at expiry:** intrinsic value `|Spot_expiry − Strike|` (one leg pays,
  the other expires worthless).
- **P&L:** `intrinsic − premium − costs`. Return = P&L ÷ cash outlay, so a total
  loss is correctly floored at −100% (an option buyer can't lose more than the
  premium paid).

### Why the modelling is fair — and where it isn't
India VIX drives the premium, so entries are priced at the volatility the market
actually charged. What's **not** captured, all of which would make a straddle
*buyer* do **worse**, not better:
- **Bid/ask spread** beyond the flat cost knob (buyers cross the spread twice).
- **Volatility skew** (ATM straddle mostly uses ATM vol, which VIX approximates).
- **Intramonth path** — held strictly to expiry, with no stop, adjustment, or
  profit-taking. An exit rule would change results; test variants via `--` flags
  or by editing the loop.
- **Weekly straddles** behave differently (more decay events); this models
  monthly only.

So the real-world result for this exact strategy would most likely be **at least
as bad** as the ≈ −10% shown.

---

*Companion to the [strategy design framework](../../strategy/system-based-strategy-design.md)
and the [System A momentum backtest](../README.md).*
