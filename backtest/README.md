# Backtest — System A: NIFTY Weekly Momentum

A dependency-free (Python 3 standard library only) backtesting engine that
implements **System A** from
[`strategy/system-based-strategy-design.md`](../strategy/system-based-strategy-design.md)
*exactly*, and computes the validation metrics from the framework's checklist —
so the "prove the edge on data" step is executable, not just described.

> **Disclaimer:** Educational tooling. The built-in synthetic data is **not real
> market data** — it exists so the pipeline runs out of the box. Plug in real
> NIFTY weekly OHLC to evaluate the real edge. Not investment advice.

---

## Run it

No install required:

```bash
# Runs on synthetic demo data (regime-switching random walk)
python3 backtest/nifty_weekly_momentum.py

# Run on your own data
python3 backtest/nifty_weekly_momentum.py --data nifty_weekly.csv

# Tune parameters and export the equity curve
python3 backtest/nifty_weekly_momentum.py --data nifty_weekly.csv \
    --risk-pct 0.01 --target-r 2 --cost-bps 5 --equity-out curve.csv
```

### Data format
A CSV of **weekly** bars in ascending date order:

```csv
date,open,high,low,close
2015-01-02,8300.5,8420.0,8250.0,8395.0
2015-01-09,8395.0,8500.0,8280.0,8310.0
```

### Key options
| Flag | Default | Meaning |
|------|---------|---------|
| `--data` | *(synthetic)* | Path to weekly OHLC CSV. Omit to use demo data. |
| `--capital` | 1,000,000 | Starting capital. |
| `--risk-pct` | 0.01 | Risk per trade (`R`) as a fraction of equity. |
| `--ema` | 20 | EMA period for the bias filter. |
| `--rsi-period` / `--rsi-threshold` | 14 / 55 | RSI filter. |
| `--target-r` | 2.0 | Profit target as a multiple of `R`. |
| `--cost-bps` | 5.0 | Per-side cost (brokerage + taxes + slippage), bps of notional. |
| `--kill-dd` / `--cooldown-weeks` | 0.15 / 4 | Drawdown kill switch and cooldown. |
| `--equity-out` | — | Write the equity curve to CSV. |

Run `python3 backtest/nifty_weekly_momentum.py -h` for the full list.

---

## What the engine does (and doesn't)

**Implements, faithfully:**
- Bias filter `close > EMA(20) AND RSI(14) > 55`, evaluated on completed weekly
  bars; acted on at the **next** week's open (no lookahead).
- Structural stop at the prior week's low; position sized so `entry − stop = R`.
- `2R` target, weekly trailing stop up to each week's low, and a bias-flip exit.
- Costs on every side; a portfolio drawdown kill switch with cooldown.
- Metrics: strike rate, avg win/loss in `R`, **expectancy per trade**, CAGR,
  max drawdown, annualized Sharpe, and Calmar.

**Honest limitations (read before trusting a number):**
- **Weekly bars only** → intrabar fills are approximate. The stop is checked
  *before* the target within a bar (worst-case), and gaps through a level fill
  at the open.
- **Fractional index units** are allowed (no lot rounding); real futures/options
  trade in lots, which changes sizing granularity.
- **Long-only, index-level.** The options-execution nuances of System A's
  live version (theta, IV, strike selection) are not modelled here — this
  measures the *signal's* edge on the underlying.
- Synthetic data is a random walk with regime shifts; it is a **plumbing test**,
  not a market.

---

## Reading the output

The single most important line is **expectancy per trade**:

```
Expectancy/trade  : +0.227R   <-- the number that matters
```

- **Positive after costs** → the signal has an edge worth forward-testing on
  paper (per the framework's go-live checklist).
- **Non-positive after costs** → do **not** deploy, no matter how good the
  strike rate looks. Strike rate alone lies; expectancy tells the truth.

### Sanity check the engine itself
The engine is not hard-wired to any verdict — it reflects the data:

| Input series | Expectancy | Verdict |
|--------------|-----------|---------|
| Near-random-walk (default synthetic) | **negative** | correctly rejects a no-edge system |
| Genuinely trending series | **positive** | correctly identifies a real trend edge |

That discrimination — negative on noise, positive on trend — is exactly what a
trend-following system *should* show, and it's why you run the backtest on
**real** data before risking a rupee.

---

*Companion to the [strategy design framework](../strategy/system-based-strategy-design.md)
and the [trading-journey article](../content/system-based-trading-journey.md).*
