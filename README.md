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

### Live scan — NSE Bhavcopy (default)

Uses NSE's official, free **End-Of-Day bhavcopy** (one file per trading day).
The first run **backfills ~2 years** of daily bhavcopies into `cache/bhav/`;
every run after that only fetches the new trading days, so it's fast:

```bash
python run_screener.py
```

The screen is meant to be run **once a day after the close** — NSE publishes the
bhavcopy around 6–7pm IST. Useful options:

```bash
python run_screener.py --full-only                 # print only FULL VCP SETUP names
python run_screener.py --min-passed 13             # + a watchlist of near-misses
python run_screener.py --history-days 1200         # backfill more history
python run_screener.py --no-adjust                 # skip split/bonus back-adjustment
python run_screener.py --limit 30                  # quick test on first 30 symbols
python run_screener.py --universe-file my_fno.txt  # custom symbol list
```

**Corporate actions:** bhavcopy prices are unadjusted, so splits/bonuses are
**back-adjusted automatically** using the adjusted previous-close NSE reports on
each ex-date (traded value = price × volume is preserved). Disable with
`--no-adjust`.

Each run writes a timestamped **CSV** (full matrix) and a **styled HTML board**
(green ✓ / red ✕ cells, one row per stock) into `output/`.

### Options enrichment

Add `--options` to layer options context onto each stock setup (needs the NSE
**FO/derivatives bhavcopy**):

```bash
python run_screener.py --options
```

For every candidate it computes, from the latest option chain: the tradeable
monthly **expiry & DTE** (skipping near-expiry), **ATM implied volatility**
(solved from settle prices via Black-Scholes — Indian stock options are
European), a **vol-rank** (IV-rank once history accrues in `cache/iv/`, else
HV-rank from realized vol), the **expected move** to expiry, **ATM OI/volume
liquidity**, and a **suggested structure** — buy a ~0.65Δ call when vol is
cheap and liquid, a **bull-call debit spread** when IV is rich, or "trade the
stock" when options are thin. Writes `vcp_fno_options_<ts>.{csv,html}`.

> Options change the payoff: this setup is low-win-rate with big winners, so
> long premium bleeds theta/IV on the many losers. The enrichment is decision
> support (structure, timing, liquidity) — not a signal to buy calls blindly.

### Practice the setup

Add `--practice` to turn the scan into a **VCP practice board** aligned with
*Think & Trade Like a Champion* (see [`docs/MINERVINI_SPEC.md`](docs/MINERVINI_SPEC.md)):

```bash
python run_screener.py --practice --account 500000 --risk-pct 0.0125
```

For every trend-template stock it runs **real VCP detection** ([`vcp.py`](vcp_screener/vcp.py))
— finding the swing highs/lows, counting the **contractions** (each should shrink
~½), checking the **final contraction is tight with volume drying up**, and
marking the **pivot buy point** — then builds the full Minervini **trade plan**:
buy the pivot on a volume breakout, an **initial stop** at the danger point
(capped 8%), a **position size** risking 1.25% of your equity (with a 25%
concentration cap), a **2:1 and a sell-into-strength target**, and the
**breakeven** trigger. It writes a board (`vcp_practice_*.{csv,html}`) and a
blank **journal** (`vcp_practice_journal.csv`) to log every paper trade.

This is decision support for practice — buy only on a real breakout above the
pivot, respect the stop, and log the reps. Not investment advice.

### Live scan — Yahoo Finance (alternative)

Free, no account, but unofficial and prone to occasional gaps/rate-limits:

```bash
python run_screener.py --provider yfinance --cache-dir cache
```

### Offline scan (local CSVs)

Point the screener at a directory of per-symbol CSVs (`<SYMBOL>.csv`, each with
`Date, Open, High, Low, Close, Volume`). This is how the test suite and demo
run without any network:

```bash
python tools/generate_sample_data.py --out sample_data     # make synthetic data
python run_screener.py --provider csv --csv-dir sample_data \
    --index-file NIFTY --universe-file sample_data/symbols.txt
```

## Automate the daily 8 PM scan

Run it once a day after the close. Ready-made runner scripts and scheduler
recipes (cron, systemd, macOS launchd, Windows Task Scheduler) are in
[`docs/AUTOMATION.md`](docs/AUTOMATION.md). Quick version on Linux/macOS:

```bash
chmod +x tools/daily_run.sh
crontab -e
# weekdays at 8 PM (machine clock on IST); use 30 14 on a UTC server
0 20 * * 1-5 /full/path/to/Mohit/tools/daily_run.sh
```

The runner writes timestamped reports to `output/`, refreshes
`output/latest.html`, and logs to `logs/`. It needs outbound access to
`archives.nseindia.com`, so run it on a machine/VM where NSE is reachable
(many sandboxed/cloud environments block it).

## How it's wired

```
run_screener.py            CLI: parse args, run screen, write reports
vcp_screener/
  constants.py             criterion labels + display order (single source of truth)
  config.py                every threshold / lookback (tune here)
  indicators.py            SMA/EMA/ATR/returns/weekly resample (pure functions)
  criteria.py              the 15 checks + FULL-SETUP aggregation
  screener.py              orchestration + cross-sectional RS Rating
  bhavcopy.py              NSE Bhavcopy EOD provider (default; back-adjusts CA)
  fo_bhavcopy.py           NSE derivatives bhavcopy (option chains)
  options.py               Black-Scholes IV, ranks, expected move, suggestions
  vcp.py                   real VCP pivot/contraction detection (Minervini footprint)
  practice.py              trade-plan cards + paper-trade journal (practice mode)
  backtest.py              vectorized historical backtest of the setup
  data.py                  YFinanceProvider (live) & CSVProvider (offline)
  universe.py              the NSE F&O symbol list
  report.py                console summary, CSV matrix, styled HTML board
run_backtest.py            CLI: backtest the setup over history
tools/generate_sample_data.py   synthetic OHLCV for offline demos/tests
tests/                     unit + integration tests (run fully offline)
```

The data layer is abstracted behind a two-method provider interface
(`get_index`, `get_many`), so the entire criteria/report pipeline is testable
offline and you can bolt on a broker API (Kite, Upstox, …) by writing one more
provider.

## Backtesting

Backtest the setup over history to see how it would have performed:

```bash
python run_backtest.py --history-days 1750          # ~5 years of NSE data
python run_backtest.py --no-market-filter           # compare without the Nifty gate
python run_backtest.py --stop-pct 0.07 --trail-ma 50 --max-hold 250
```

**Rules simulated:** enter at next-day open when a stock *first* becomes a FULL
VCP SETUP; exit on the first of — an initial stop (`--stop-pct`, default 8%),
the profit-exit chosen by `--exit-mode`, a max-hold time stop, or end of data.
A round-trip cost is applied.

Two profit-exits (`--exit-mode`):

- `trail_ma` (default) — ride the trend, exit on a close back below the
  `--trail-ma` (default 50-DMA). Also supports an optional `--trail-pct`.
- `big_candle` — sell into strength on the first bullish day whose range is
  `>= --big-candle-atr` × ATR (default 3×), or whose gain `>= --big-candle-pct`
  (e.g. `0.07`). No MA trail, so winners run until a big candle, the stop, or
  the time exit. This models "enter when all green, book profit on the next big
  candle." It reports per-trade stats (win rate, expectancy, profit factor),
a by-year table, an equal-weight capped-concurrency equity curve, and an
A/B of the market filter on vs off. Outputs a trades CSV and an HTML report.

The engine is **vectorized and look-ahead-free** — every criterion on day *T*
uses only data up to *T*, and the cross-sectional RS Rating ranks stocks within
the same day (there is a unit test asserting truncating future bars doesn't
change past signals).

**Read results with care — known limitations:**

- **Survivorship bias.** The backtest applies *today's* F&O list historically;
  names added/removed over time aren't handled point-in-time.
- **Corporate actions.** Splits/bonuses are back-adjusted heuristically from the
  overnight gap (NSE's bhavcopy prev-close isn't reliably adjusted). A genuine
  >30% overnight move could be mis-treated; a corporate-actions feed is the
  robust fix.
- **Fills.** Entries fill at the next open; there's no intraday path within a
  bar, and slippage is modelled only as a flat cost.
- **The equity curve is illustrative** (equal-weight, capped concurrency, open
  positions marked at cost) — the per-trade expectancy and profit factor are the
  more reliable measures of the setup's edge.
- **A signal is not a strategy.** Entering on "the checklist just went green" is
  cruder than a real breakout entry (through the pivot on volume); refining the
  entry is the biggest lever on results.

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
designed synthetic data with known outcomes, the FULL-SETUP aggregation, the
RS Rating overlay, and the bhavcopy parsing + split/bonus back-adjustment.

## Data note

The default provider uses NSE's official **Bhavcopy** archives
(`archives.nseindia.com`). It reads both the current **UDiFF** common bhavcopy
and the **legacy** equities bhavcopy, and pulls Nifty 50 from the daily indices
close file. Each trading day is cached under `cache/bhav/` as a small CSV, so the
heavy backfill happens once and daily runs are cheap. Holidays return 404 and are
skipped automatically.

Yahoo Finance (`<SYMBOL>.NS`, Nifty = `^NSEI`) is available as an alternative.
To use a broker feed (Kite, Upstox, Angel One …), add a provider exposing
`get_index()` / `get_many()` — nothing else needs to change. Note that some
sandboxed/corporate networks block `archives.nseindia.com` and Yahoo; run live
scans where those hosts are reachable.

## Disclaimer

Educational tool, **not investment advice**. Screens surface candidates; they do
not make decisions. Always confirm signals on your own charts and do your own
risk management before trading.
