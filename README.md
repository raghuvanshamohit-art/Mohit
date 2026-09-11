# Indian Sectors & Stock Performance

Lists **all major Indian market sectors** (the NSE sectoral indices) with their
constituent stocks, and shows each stock's **price growth %** over **3, 6, 9 and
12 months** — plus an equal-weighted sector average.

- **Sector groupings** follow the **NSE sectoral indices** (Nifty Bank, Nifty IT,
  Nifty Auto, Nifty Pharma, …) — the exchange's own way of grouping companies.
- **Prices & returns** come from **Yahoo Finance** (adjusted close, so returns
  include the effect of splits and dividends).
- **Zero third-party dependencies** — pure Python standard library, runs anywhere
  with Python 3.9+.

![dashboard](docs/dashboard.png)

---

## Quick start

```bash
# 1. Fetch live data and build the dataset (≈ 5–10 s for ~160 stocks)
python run.py generate

# 2a. See it in the terminal
python run.py show                 # sector overview, sorted by 12-month return
python run.py show --sector it     # one sector's stocks
python run.py show --sort 3m       # sort by a different period

# 2b. …or open the web dashboard (browsers block fetch over file://, so serve it)
python -m http.server 8000
#     then open  http://localhost:8000/
```

List the sector → stock mapping without any network calls:

```bash
python run.py list
```

---

## What you get

**15 sectors, 160+ constituent stocks.** Example (`python run.py show`):

```
SECTOR PERFORMANCE (equal-weighted average return %)
                                   3m       6m       9m      12m
----------------------------------------------------------------
Metal                (15/15) +10.77 +20.41 +35.17 +42.73
Private Bank         (10/10)  +7.19 +10.78 +10.63 +23.09
Bank                 (12/12)  +4.70  +3.20  +1.78 +19.25
...
```

The web dashboard (`index.html`) adds:

- A **sector overview** table — click any sector to jump to its detail.
- **Per-sector stock tables** with live price and 3/6/9/12-month growth %,
  colour-coded green/red.
- **Sort** by any period (or name) and **filter** by symbol / company / sector.
- Light / dark theme, responsive down to phone width.

---

## How growth % is computed

For each stock the tool pulls ~13 months of daily adjusted-close prices and, for
each period *N* ∈ {3, 6, 9, 12} months:

```
growth% = (latest_adjusted_close / adjusted_close_N_months_ago − 1) × 100
```

The base price is the last trading day **on or before** the target calendar date.
Each figure records `coverage_days` (how much history actually backed it) and each
stock records `history_days`, so partial figures are transparent rather than
hidden.

**Sector figure** = the equal-weighted average of its constituents' returns. This
is a simple readable aggregate, **not** the official free-float market-cap-weighted
index return.

---

## Data sources & the NSE note

The sector membership mirrors the **NSE sectoral indices**. `sector_stocks/nse.py`
can refresh constituents **live from NSE** (`/api/equity-stockIndices`) when the
exchange is reachable. In practice NSE aggressively blocks datacenter / cloud /
non-Indian IP ranges (HTTP 403), so from a server the live refresh usually fails
and the tool falls back to the **bundled constituent list** in
`sector_stocks/sectors.py` — which tracks the same NSE indices. All **price** data
always comes from Yahoo Finance, which is reliably reachable.

### Corporate actions

The constituent list reflects recent restructurings, e.g.:

- **LTIMindtree → LTM** (renamed Feb 2026)
- **Gujarat Gas → Gujarat Energy** (GSPC group merger, May 2026)
- **Tata Motors** demerged into **TMPV** (passenger vehicles) and **TMCV**
  (commercial vehicles)
- **TV18 Broadcast** merged into **Network18**

Stocks affected by a very recent demerger / listing have limited price history;
those rows are flagged (⚠) in the dashboard, and long-period returns for a freshly
demerged entity can be distorted by the value split even when a full year of the
successor ticker exists.

---

## Project layout

```
Mohit/
├── run.py                       # CLI: generate / show / list
├── index.html                   # web dashboard (reads output/sector_performance.json)
├── output/
│   └── sector_performance.json  # generated dataset (a snapshot is committed)
├── sector_stocks/
│   ├── sectors.py               # sector → constituent stock definitions (NSE indices)
│   ├── yahoo.py                 # stdlib Yahoo Finance client
│   ├── nse.py                   # optional live NSE constituent fetch (+ fallback)
│   ├── performance.py           # 3/6/9/12-month return maths
│   └── generate.py              # orchestrates fetch → JSON
└── requirements.txt             # (no runtime deps required)
```

## Output schema (`output/sector_performance.json`)

```jsonc
{
  "meta": { "generated_at": "...", "price_source": "...", "periods_months": [3,6,9,12], ... },
  "sectors": [
    {
      "key": "bank", "name": "Bank", "nse_index": "NIFTY BANK",
      "num_stocks": 12, "num_ok": 12,
      "average_returns": { "3m": 4.70, "6m": 3.20, "9m": 1.78, "12m": 19.25 },
      "stocks": [
        {
          "symbol": "HDFCBANK", "name": "HDFC Bank", "price": 693.8, "currency": "INR",
          "as_of": "2026-09-10",
          "returns": { "3m": -5.57, "6m": -16.97, "9m": -28.75, "12m": -26.98 },
          "coverage_days": { ... }, "history_days": 395.0, "ok": true
        }
      ]
    }
  ]
}
```

---

*Data is for information only and is **not** investment advice. Figures depend on
Yahoo Finance availability and reflect the moment the dataset was generated.*
