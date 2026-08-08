# ExitMantra replication + calibration toolkit

A self-contained engine that reproduces ExitMantra's 3-criteria rating and
**calibrates the exit-price proxy against real ExitMantra readings** you supply.

## What it does by itself (from a ticker alone)
- **Criterion 2 — 52-week outperformance vs Nifty 500** (`^CRSLDX`): computed from
  Yahoo Finance price data. No input needed beyond the ticker.
- **Criterion 3 — Exit Price proxy**: weekly **Supertrend** or **Chandelier Exit**,
  parameters grid-searched to best fit your real exit prices.
- **Score / Rating / Zone / Cushion / Risk / Position-size**: deterministic math.

## What it needs from you (per stock)
Criterion 1 (ATH TTM profit) is not reliably fetchable free, so you provide that
`Y/N` flag from the ExitMantra stock page, plus ExitMantra's outputs to calibrate
against. See `samples_template.csv` for the exact columns.

**Minimum to be useful:** `ticker`, `cmp`, `rating`, `zone`, `exit_price`,
`ath_profit`, `super_performer`. The more you fill, the tighter the calibration.

## Run it
```bash
cp tools/samples_template.csv tools/samples.csv    # then paste your 10-20 rows
python3 tools/em_calibrate.py tools/samples.csv
```

Output: outperformance match rate, the best-fit exit indicator + params with
per-stock error, rating-reconstruction match rate, and a Super Performer profile.

## Files
- `em_engine.py` — data fetch (stdlib only), indicators, criteria, scoring.
- `em_calibrate.py` — reads samples, fits params, prints the comparison report.
- `samples_template.csv` — data intake template.

No pip installs required (Python 3.9+, stdlib `urllib`).
