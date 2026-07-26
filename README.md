# VCP F&O Screener

A **Volatility Contraction Pattern (VCP)** + **Trend Template** screener for the
**NSE Futures & Options** universe, in the style of Mark Minervini's SEPA
methodology. It scans every F&O stock, runs the 15-point checklist below on each,
and flags the ones showing a **FULL VCP SETUP**.

The 15 checks and their labels mirror this on-screen checklist:

| # | Check | What it means |
|---|-------|---------------|
| 1 | **Price > 50/150/200 MA** | Close is above the 50-, 150- and 200-day SMAs |
| 2 | **MA 50>150>200** | Moving averages are stacked bullishly |
| 3 | **200 MA Rising (1M)** | 200-DMA is higher than ~1 month (21 sessions) ago |
| 4 | **50 MA Rising** | 50-DMA is rising over the same lookback |
| 5 | **Within 25% of 52W High** | Close is no more than 25% below the 52-week high |
| 6 | **30%+ Above 52W Low** *(optional)* | Close is at least 30% above the 52-week low |
| 7 | **Price > 10 MA** | Close is above the 10-day SMA (short-term strength) |
| 8 | **Price >= ₹50** | Absolute price floor |
| 9 | **Weekly Uptrend** | Weekly close above the 30-week SMA and 10-week EMA rising |
| 10 | **150 MA Rising** | 150-DMA is rising over the lookback |
| 11 | **Sufficient Volume** | Avg daily turnover (close × volume) over the liquidity floor |
| 12 | **RS vs Nifty Strong** | Cross-sectional RS Rating ≥ 70 (see below) |
| 13 | **Nifty in Uptrend** | Nifty above its 200-DMA with a rising 50-DMA |
| 14 | **Volatility Contracting** | Recent ATR% is below the prior ATR% (the VCP core) |
| 15 | **Volume Contracting** | Recent avg volume is below prior avg volume (dry-up) |

A **FULL VCP SETUP** requires every *mandatory* check to pass. Criterion #6 is
marked *optional* and does not block a full setup (matching the checklist). Every
threshold is configurable in [`vcp_screener/config.py`](vcp_screener/config.py).

> **Relative strength.** When the whole universe is screened together, RS is a
> proper **cross-sectional RS Rating** (0–99 percentile of each stock's excess
> return vs Nifty), and "RS vs Nifty Strong" means the rating clears the floor
> (default 70). Evaluating a single stock in isolation falls back to a
> self-contained rule (stock outperformed Nifty over the lookback *and* its RS
> line sits near its own recent high).

---

## Install

```bash
pip install -r requirements.txt
```

Requires Python 3.9+. Dependencies: `pandas`, `numpy`, and `yfinance` (only
needed for live data).

## Usage

### Live scan (Yahoo Finance)

Scans the built-in F&O universe using free Yahoo Finance data (needs internet):

```bash
python run_screener.py
```

Useful options:

```bash
python run_screener.py --full-only                 # print only FULL VCP SETUP names
python run_screener.py --min-passed 13             # + a watchlist of near-misses
python run_screener.py --limit 30                  # quick test on first 30 symbols
python run_screener.py --cache-dir cache           # cache downloads to disk
python run_screener.py --universe-file my_fno.txt  # custom symbol list
```

Each run writes a timestamped **CSV** (full matrix) and a **styled HTML board**
(green ✓ / red ✕ cells, one row per stock) into `output/`.

### Offline scan (local CSVs)

Point the screener at a directory of per-symbol CSVs (`<SYMBOL>.csv`, each with
`Date, Open, High, Low, Close, Volume`). This is how the test suite and demo
run without any network:

```bash
python tools/generate_sample_data.py --out sample_data     # make synthetic data
python run_screener.py --provider csv --csv-dir sample_data \
    --index-file NIFTY --universe-file sample_data/symbols.txt
```

## How it's wired

```
run_screener.py            CLI: parse args, run screen, write reports
vcp_screener/
  constants.py             criterion labels + display order (single source of truth)
  config.py                every threshold / lookback (tune here)
  indicators.py            SMA/EMA/ATR/returns/weekly resample (pure functions)
  criteria.py              the 15 checks + FULL-SETUP aggregation
  screener.py              orchestration + cross-sectional RS Rating
  data.py                  YFinanceProvider (live) & CSVProvider (offline)
  universe.py              the NSE F&O symbol list
  report.py                console summary, CSV matrix, styled HTML board
tools/generate_sample_data.py   synthetic OHLCV for offline demos/tests
tests/                     unit + integration tests (run fully offline)
```

The data layer is abstracted behind a two-method provider interface
(`get_index`, `get_many`), so the entire criteria/report pipeline is testable
offline and you can bolt on a broker API (Kite, Upstox, …) by writing one more
provider.

## Tuning

Open [`vcp_screener/config.py`](vcp_screener/config.py). Common tweaks:

- `within_high_pct`, `above_low_pct` — distance-from-high/low bands
- `min_price`, `min_avg_turnover` — price/liquidity floors
- `rs_rating_min` — how strong RS must be (lower = more candidates)
- `volatility_recent/prior`, `volume_recent/prior` — contraction windows
- `optional_criteria` — which checks don't block a FULL setup

## Updating the F&O universe

NSE revises the derivatives list periodically. Edit `FNO_SYMBOLS` in
[`vcp_screener/universe.py`](vcp_screener/universe.py), or pass
`--universe-file symbols.txt` (one plain NSE symbol per line, `#` for comments)
sourced from the current **"Securities in F&O"** list on the NSE website.

## Tests

```bash
python -m pytest -q
```

The suite is fully offline: it checks the indicators, each criterion against
designed synthetic data with known outcomes, the FULL-SETUP aggregation, and the
RS Rating overlay.

## Data note

The default provider uses **Yahoo Finance** (`<SYMBOL>.NS`, Nifty = `^NSEI`),
which is free but unofficial and occasionally rate-limits or gaps. For
production use, swap in a paid/official feed or your broker's API by adding a
provider in `data.py`. Note that some sandboxed environments block outbound
access to Yahoo Finance — run live scans where that host is reachable.

## Disclaimer

Educational tool, **not investment advice**. Screens surface candidates; they do
not make decisions. Always confirm signals on your own charts and do your own
risk management before trading.
