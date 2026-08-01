# CW 2σ — Rule-Based Investment System (TradingView Pine Script)

An independent, **educational** reconstruction of the rule-based weekly investment
system publicly described by **Rakesh Pujara** (Compounding Wealth) on the
*"Masters in One"* podcast with **Vijay Thakkar**.

> ⚠️ **Disclaimer.** This is **not** the official invite-only "CW 2σ" indicator and
> is not affiliated with or endorsed by its author. It only re-implements the
> *publicly stated* rules so they can be studied and charted. It is provided for
> education and research — **not investment advice**. Markets carry risk; back-test
> and paper-trade before risking capital.

## What it is

A single Pine v5 indicator, [`pine/CW_2Sigma.pine`](pine/CW_2Sigma.pine), that plots
the system on a **weekly** chart and shows a live dashboard:

- **Blue** — Upper Bollinger Band `(50, 2)`; the breakout trigger (the "2σ").
- **Red** — `100 EMA`, one of the trailing-stop references.
- **Green** — volatility trailing line: **SuperTrend** (default) or an `ATR(14) × 1.8` chandelier.
- **Orange** — the initial **20%** stop, fixed from the entry price.
- **Fuchsia** — the *effective* stop actually used for the exit test.
- **BUY / EXIT** markers, an in-trade background tint, and a corner dashboard.

## The rules (as extracted from the podcast)

| Element | Rule |
|---|---|
| **Timeframe** | Weekly. Check the Friday close, act on Monday's open (~5 min/week). |
| **Universe** | A predefined list (e.g. NSE 500 / mid-small cap). Apply the script per symbol. |
| **Entry** | Weekly **close crosses above the Upper Bollinger Band (50, 2)** → buy at the **next weekly open**. |
| **Position size** | Fixed **2% of capital** per stock → `qty = floor(capital × 2% ÷ price)`. |
| **Initial stop** | **20% below** the entry price (weekly-close basis). |
| **Trailing stop** | Built from the **100 EMA** and a volatility line — **SuperTrend** (default) or an **ATR(14) × 1.8** chandelier; exit on a weekly close below the effective stop. |
| **Style** | Ride winners, cut losers. Pure price action — **no fundamentals**. |
| **Tracked metric** | Calmar ratio = CAGR ÷ max drawdown (the "cal-mar ratio" in the talk). |

Full spec, including the interpretation choices, is in [`docs/RULES.md`](docs/RULES.md).

## How to use it on TradingView

1. Open TradingView → **Pine Editor** (bottom panel).
2. Paste the contents of [`pine/CW_2Sigma.pine`](pine/CW_2Sigma.pine).
3. Click **Add to chart**.
4. Switch the chart to the **Weekly (1W)** timeframe.
5. (Optional) Open the indicator's ⚙️ settings to set your **Capital** and tune stops.
6. (Optional) Right-click → **Add alert** and pick one of the three CW 2σ alert
   conditions (breakout / entry / exit).

## Inputs

- **Entry — Bollinger Band:** length `50`, σ multiplier `2.0`, source `close`.
- **Exit — Stops:** initial stop `20%`, trailing EMA `100`, a **volatility trail
  engine** (SuperTrend *default*, or ATR chandelier), SuperTrend `factor 1.8` /
  `ATR period 14` (chandelier `length 14` / `mult 1.8`), and an **effective-stop
  mode** (see below).
- **Position sizing:** capital (₹) and allocation per position (`2%`).
- **Display:** toggle lines, labels, dashboard, and the in-trade background tint.

### Effective-stop mode

The podcast phrases the trailing exit as *"whichever is earlier"* while also noting
the system tolerates deep (50%+) corrections in strong movers. Those pull in
opposite directions, so the combination is exposed as an input. The *volatility
trail* below is whichever engine you pick — **SuperTrend** (default) or the ATR
chandelier:

| Mode | Exit when weekly close falls below… |
|---|---|
| **Whichever hit first (tightest)** *(default)* | `max(100 EMA, volatility trail)`, floored by the 20% stop |
| Volatility trail only | the SuperTrend/ATR line (floored by the 20% stop) |
| 100 EMA only | the 100 EMA (floored by the 20% stop) |
| Both broken (loosest) | `min(100 EMA, volatility trail)` — most room to run |

Use **loosest** if you want to give multi-baggers the room the podcast describes;
**tightest** locks profits earlier. All modes keep the 20% initial floor.

> **SuperTrend note:** a `factor` of `1.8` keeps parity with the original ATR
> setting and is fairly tight; the more common SuperTrend default is ~`3`, which
> gives price more room. Tune it to taste.

## Notes & caveats

- Signals are evaluated on the **confirmed weekly close**; the current forming week
  can change until Friday. Entries/exits are modelled at the **next open**.
- One open position per symbol (this is a charting/scanning aid, not a portfolio
  back-tester — position sizing across many symbols is a portfolio-level rule).
- The `2%` cap and universe selection are enforced by you across your watchlist.

## Backtest (20-year portfolio simulation)

A pure-Python portfolio backtester implements the exact rule set over ~18 years
(the honest maximum — free Indian-equity history starts ~2006), ₹20 lakh start,
current Nifty 500 universe, Nifty 50 / Nifty 500 benchmarks.

```bash
python3 backtest/cw2sigma_backtest.py      # downloads data & writes docs/BACKTEST.md
```

Headline (2008–2026, *loosest* exit; **survivorship-biased**, see the report):
**₹20L → ~₹13.6 cr, CAGR ~26%, max DD ~28%, Calmar ~0.93** — vs Nifty 50 buy &
hold ~10.5% CAGR / 43% DD. Full numbers, all four exit modes, year-by-year and a
long list of caveats are in **[`docs/BACKTEST.md`](docs/BACKTEST.md)**.

> ⚠️ Results use *today's* index members, so they overstate reality (delisted
> losers are excluded). Treat as indicative of the rules' *character*, not a promise.

## Files

```
pine/CW_2Sigma.pine          # the indicator
backtest/cw2sigma_backtest.py # 20-year portfolio backtester (stdlib only)
backtest/results/            # equity_curve.csv/.svg, trades.csv
docs/RULES.md                # detailed rule specification & interpretation notes
docs/BACKTEST.md             # backtest methodology, results & limitations
README.md                    # this file
```
