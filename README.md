# Indian Sectors & Stock Performance

Lists the **whole Indian market across 72 industry groups** — from Banks and IT
to Defence, Specialty Chemicals, Cables & Wires and Restaurants/QSR — with each
group's constituent stocks and their **price growth %** over **3, 6, 9 and 12
months**, plus an equal-weighted sector average.

- **72 sectors**, grouped under 12 macro-economic sectors, following the **NSE
  macro → sector → industry classification**. This is far finer than the ~15
  tradeable NSE sectoral indices: "Auto", for example, is split into Passenger
  Vehicles, Two & Three Wheelers, Commercial Vehicles, Tyres, Auto Components
  and Batteries & EV.
- **~530 constituent stocks**, prices & returns from **Yahoo Finance** (adjusted
  close, so returns include splits and dividends).
- **Zero third-party dependencies** — pure Python standard library, Python 3.9+.

![dashboard](docs/dashboard.png)

---

## Quick start

```bash
# 1. Fetch live data and build the dataset (~15 s for ~530 stocks)
python run.py generate

# 2a. See it in the terminal
python run.py show                       # 72-sector leaderboard, sorted by 12m
python run.py show --sector defence      # one sector's stocks
python run.py show --sort 3m             # sort by a different period

# 2b. …or open the web dashboard (browsers block fetch over file://, so serve it)
python -m http.server 8000
#     then open  http://localhost:8000/
```

List the full sector → stock mapping (grouped by macro sector, no network):

```bash
python run.py list
```

Estimate a stock's **intrinsic (fair) value** and get a **pyramiding buy plan**:

```bash
python run.py value RELIANCE --eps 55 --bvps 668 --growth 10 --price 1257.5
python run.py value INFY --eps 65 --growth 10 --capital 100000 --tranches 4

# …or just type a symbol in the browser and let it fetch live:
python run.py serve                       # opens http://127.0.0.1:8000/
```

---

## What you get

**72 sectors, ~530 constituent stocks.** Example (`python run.py show`):

```
SECTOR PERFORMANCE (equal-weighted average return %)
                                   3m       6m       9m      12m
----------------------------------------------------------------
Telecom Equipment &  (5/5)     +13.54  +123.27  +208.96  +172.97
Cables & Wires       (6/6)     +14.59   +57.56   +61.76   +69.94
Two & Three Wheelers (5/5)     +23.58   +33.96   +41.03   +54.12
Defence              (11/11)    +7.34   +25.86   +36.28   +28.48
Banks – Private      (12/12)    +7.68   +11.86   +16.17   +28.44
...
```

The web dashboard (`index.html`, and the shareable screener artifact) adds:

- A **sector leaderboard** — all 72 sectors ranked by any period, with in-cell
  magnitude heat-bars; click a sector to jump to its detail.
- **Macro-grouped, collapsible per-sector tables** with live price and 3/6/9/12
  month growth %, colour-coded green/red.
- **Macro filter** (Financials, Energy & Utilities, …), **sort** by any period,
  and **search** across symbol / company / sector / macro.
- Light / dark theme, responsive down to phone width.

---

## Intrinsic value & pyramiding

Beyond screening *what* has moved, `python run.py value` answers *what a stock is
worth* and *at which prices to build a position* — the classic value-investing
pair of **intrinsic value** and a **pyramiding** (scale-in) plan.

```bash
python run.py value RELIANCE --eps 55 --bvps 668 --growth 10 --dividend 6 \
    --fair-pe 20 --price 1257.5 --capital 100000 --tranches 4
```

```
Intrinsic value estimates:
  Graham Number                909.20
  Graham Revised             1,567.50
  Two-stage DCF              1,024.43
  Earnings Power               918.63
  Dividend Discount            330.00
  ----------------------------------
  COMPOSITE (median)           918.63     <- robust to any single wild model
  Best buy price   : 643.04              <- composite discounted 30% (margin of safety)
  Verdict          : EXPENSIVE — above intrinsic value

Pyramiding plan — value_accumulate:
  Lvl         Price   Weight   Disc%   Shares          Cost
  1          643.04    10.0%     30%       15      9,645.60
  2          551.18    20.0%     40%       36     19,842.48
  3          459.31    30.0%     50%       65     29,855.15
  4          367.45    40.0%     60%      108     39,684.60
  Avg entry price      : 459.31    Effective MoS at avg : 50.0%
  Stop-loss            : 330.70    Planned position     : 224 shares
```

### Intrinsic value — five models, blended

Each model runs only when its inputs are present, and the **composite** is the
**median** of whatever ran (so one runaway estimate can't dominate):

| Model | Formula | Needs |
|---|---|---|
| **Graham Number** | √(22.5 × EPS × BVPS) | positive EPS + book value |
| **Graham revised** | EPS × (8.5 + 2g) × 4.4 / Y | EPS + growth (+ bond yield Y) |
| **Two-stage DCF** | discounted FCF/share (or EPS), then Gordon terminal | cash flow + growth + discount |
| **Earnings power** | forward EPS × exit P/E, discounted back | EPS + growth + exit P/E |
| **Gordon DDM** | D₁ / (r − g) | a dividend + growth < discount |

The **best buy price** = composite × (1 − *margin of safety*), Graham's classic
30 % discount by default (`--mos`).

### Pyramiding — a laddered scale-in

Pyramiding means entering in tranches instead of one lump. Two modes:

- **`--mode value`** (default) — *accumulate below fair value*. Buy the first
  tranche at the margin-of-safety discount and each further tranche `--step`
  deeper, committing **more** the cheaper (and safer) it gets. The tool reports
  the blended average entry, the effective margin of safety there, a stop-loss,
  and — with `--capital` — whole-share sizing per tranche.
- **`--mode trend`** — *classic add-to-winner*. Start at the current price and
  add as it rises, each add **smaller** than the last, with a stop trailing up.

Supply fundamentals as flags (rates are percentages); a bare symbol auto-fetches
the **current price** from Yahoo's chart endpoint and the **fundamentals** from a
provider chain — Yahoo `quoteSummary` first, then Alpha Vantage when a free key
is given (`--av-key` / `ALPHAVANTAGE_API_KEY`), which works even where Yahoo
blocks cloud IPs. Anything no provider returns you can pass yourself (`--eps`,
`--bvps`, `--growth`, …); the report labels every input `supplied` / `yahoo` /
`alphavantage` / `chart` / `default`. Add `--json` for a machine-readable report,
or `--no-fetch` to stay fully offline.

### Live web app — just type a symbol

```bash
python run.py serve            # opens http://127.0.0.1:8000/
```

A local web page where you **type a ticker and it fetches live and values it** —
no manual number entry. It runs on your machine (not a browser sandbox), so it
reaches the market directly. Fundamentals come from a **provider chain**, and
every input is tagged by source (`chart` / `yahoo` / `alphavantage` / `supplied`
/ `default`):

- **Current price** — always live from Yahoo's reliable chart endpoint.
- **Fundamentals** (EPS, book value, growth, dividend) — **Yahoo** first (free,
  no key, best coverage; works from a home network but Yahoo blocks it from many
  cloud/office IPs), then **Alpha Vantage** as a fallback that *does* work from
  blocked networks. Get a free key at
  [alphavantage.co](https://www.alphavantage.co/support/#api-key) and pass it
  with `--av-key KEY` (or set `ALPHAVANTAGE_API_KEY`, or paste it into the page —
  it's saved in your browser). With a key, a bare symbol values **fully
  automatically** anywhere.

Anything no provider returns, you can type in the collapsible *Assumptions &
manual overrides* panel. NSE symbols work bare (`TCS`); for other markets use the
full Yahoo symbol (`AAPL`, `TATASTEEL.BO`). `-p 8000` sets the port; `--host
0.0.0.0` exposes it on your LAN.

```bash
python run.py serve --av-key YOUR_ALPHAVANTAGE_KEY   # fully automatic
python run.py value AAPL --av-key YOUR_KEY           # same, on the CLI
```

> **Why not a claude.ai artifact?** A shared artifact runs in a locked-down
> browser sandbox that blocks all network calls to outside sites (Yahoo
> included), so a hosted artifact *cannot* fetch live quotes. This local app can,
> which is why live valuation ships as `serve` rather than a shareable link.

### Browser calculator (offline, shareable)

`web/valuation.html` is a **self-contained** version of the same maths with no
live fetch — open it (or serve it with `python -m http.server`) and type the
numbers to watch the fair value, verdict and pyramid ladder update live. It runs
entirely in the browser, matches the dashboard's light/dark theme, sends nothing
anywhere, and works as a shareable claude.ai artifact.

*Intrinsic value is an estimate; it is only as good as the growth and
discount-rate assumptions fed in. Nothing here is investment advice.*

---

## The 72 sectors, by macro group

| Macro sector | Industry groups |
|---|---|
| **Financials** | Banks – Private · Banks – Public Sector · Small Finance & Microfinance · NBFC · Housing Finance · Life Insurance · General & Health Insurance · Asset Management · Capital Markets & Exchanges · Fintech, Payments & Internet |
| **Information Technology** | IT Services & Consulting · Software Products & Platforms · Electronics Manufacturing (EMS) |
| **Consumer Discretionary** | Passenger Vehicles · Two & Three Wheelers · Commercial Vehicles · Tyres · Auto Components · Batteries & EV · Consumer Durables & Appliances · Footwear · Jewellery & Watches · Retail |
| **Consumer Staples** | Packaged Foods · Beverages · Personal & Household Care · Tobacco · Sugar · Breweries & Distilleries · Agri & Edible Oils |
| **Healthcare** | Pharmaceuticals · Hospitals · Diagnostics · CRAMS & Contract Research |
| **Energy & Utilities** | Oil E&P · Oil Refining & Marketing · Gas Distribution · Power Generation · Power Transmission & Distribution · Renewable Energy · Coal · Lubricants |
| **Metals & Mining** | Iron & Steel · Aluminium & Non-Ferrous · Mining & Minerals |
| **Chemicals** | Specialty Chemicals · Commodity Chemicals · Fertilizers · Agrochemicals · Paints · Plastics & Packaging |
| **Construction & Materials** | Cement · Building Materials · Cables & Wires · Real Estate · Construction & Engineering (EPC) |
| **Industrials** | Capital Goods & Electrical · Industrial Machinery & Bearings · Defence · Railways · Ports & Marine · Logistics · Aviation & Airports |
| **Telecom, Media & Hospitality** | Telecom Services · Telecom Equipment & Infrastructure · Media & Entertainment · Hotels & Tourism |
| **Diversified & Others** | Textiles & Apparel · Paper & Forest Products · Diversified / Conglomerates · Shipping · Restaurants & QSR |

---

## How growth % is computed

For each stock the tool pulls ~13 months of daily adjusted-close prices and, for
each period *N* ∈ {3, 6, 9, 12} months:

```
growth% = (latest_adjusted_close / adjusted_close_N_months_ago − 1) × 100
```

The base price is the last trading day **on or before** the target calendar date.
Each figure records `coverage_days` (how much history actually backed it) and each
stock records `history_days`, so partial figures are transparent, not hidden.

**Sector figure** = the equal-weighted average of its constituents' returns — a
simple, readable aggregate, **not** the official free-float market-cap-weighted
index return.

---

## Data sources & the NSE note

The sector taxonomy mirrors the **NSE industry classification**.
`sector_stocks/nse.py` can refresh constituents **live from NSE**
(`/api/equity-stockIndices`) when the exchange is reachable. In practice NSE
aggressively blocks datacenter / cloud IP ranges (HTTP 403), so from a server the
live refresh usually fails and the tool uses the **bundled constituent list** in
`sector_stocks/sectors.py`. All **price** data comes from Yahoo Finance, which is
reliably reachable.

### Corporate actions handled

Constituent symbols track recent restructurings, e.g.: **LTIMindtree → LTM**,
**Gujarat Gas → Gujarat Energy**, **Tata Motors** demerged into **TMPV + TMCV**,
**TV18 Broadcast** merged into **Network18**, **Kalpataru → KPIL**, **Hitachi
Energy India = POWERINDIA**, **Godawari = GPIL**. A few names Yahoo only carries
on BSE (e.g. **SpiceJet**, via a `.BO` override). Stocks with limited history
(recent listing / demerger) are flagged ⚠ in the dashboard and their longer-period
returns are partial.

---

## Automatic daily updates

The data is **not** live — it is a snapshot produced by `python run.py generate`.
Two mechanisms keep it fresh daily:

1. **GitHub Actions** (`.github/workflows/update-data.yml`) regenerates
   `output/sector_performance.json`, rebuilds `web/screener.html`, sanity-checks
   coverage (≥ 80 % of stocks must fetch), and commits — every weekday at
   **7 PM IST** (after the NSE close). GitHub only runs scheduled workflows from
   the **default branch**, so this begins firing once merged to `main`; until
   then, trigger it manually from the repo's **Actions → Update sector data →
   Run workflow**.

2. **Live artifact republish** — the shareable dashboard link embeds its data and
   cannot self-refresh, so a scheduled Claude routine regenerates and republishes
   it daily. Rebuild it manually anytime with:

   ```bash
   python run.py generate && python scripts/build_artifact.py
   ```

Markets trade Mon–Fri; Yahoo occasionally rate-limits cloud/CI IPs, which is why
the workflow refuses to commit a partial pull.

---

## Project layout

```
Mohit/
├── run.py                       # CLI: generate / show / list / value
├── index.html                   # web dashboard (reads output/sector_performance.json)
├── output/
│   └── sector_performance.json  # generated dataset (a snapshot is committed)
├── valuation/                   # intrinsic value + pyramiding engine
│   ├── intrinsic.py             # 5 fair-value models + composite
│   ├── pyramid.py               # value / trend pyramiding ladders
│   ├── fundamentals.py          # best-effort Yahoo fundamentals fetch
│   ├── engine.py                # orchestrates fetch → intrinsic → pyramid
│   ├── report.py                # terminal report formatter
│   └── server.py                # local live web app (stdlib http.server + JSON API)
├── tests/
│   └── test_valuation.py        # unittest suite (no network)
├── web/
│   ├── screener_template.html   # artifact template (/*__DATA__*/ placeholder)
│   ├── screener.html            # standalone artifact page (data embedded)
│   ├── valuation.html           # self-contained (offline) intrinsic-value / pyramid calculator
│   └── valuation_live.html      # front-end for `python run.py serve` (live fetch)
├── scripts/
│   └── build_artifact.py        # builds web/screener.html from template + data
├── .github/workflows/
│   └── update-data.yml          # daily GitHub Actions refresh
├── sector_stocks/
│   ├── sectors.py               # 72 industry groups → constituent stocks (+ macro map)
│   ├── yahoo.py                 # stdlib Yahoo Finance client
│   ├── nse.py                   # optional live NSE constituent fetch (+ fallback)
│   ├── performance.py           # 3/6/9/12-month return maths
│   └── generate.py              # orchestrates fetch → JSON
└── requirements.txt             # (no runtime deps required)
```

## Output schema (`output/sector_performance.json`)

```jsonc
{
  "meta": { "generated_at": "...", "price_source": "...", "periods_months": [3,6,9,12],
            "macros": ["Financials", "..."], "num_sectors": 72, ... },
  "sectors": [
    {
      "key": "defence", "name": "Defence", "macro": "Industrials",
      "num_stocks": 11, "num_ok": 11,
      "average_returns": { "3m": 7.34, "6m": 25.86, "9m": 36.28, "12m": 28.48 },
      "stocks": [
        {
          "symbol": "HAL", "name": "Hindustan Aeronautics", "price": 4900.0, "currency": "INR",
          "as_of": "2026-09-10",
          "returns": { "3m": ..., "6m": ..., "9m": ..., "12m": ... },
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
