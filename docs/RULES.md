# CW 2σ — System Rules Specification

This document records the rules of the **CW 2σ** ("Compounding Wealth 2-Sigma")
weekly investment system as stated publicly by **Rakesh Pujara** on the
*Masters in One* podcast, and the exact interpretation used by
[`pine/CW_2Sigma.pine`](../pine/CW_2Sigma.pine).

It is an independent educational reconstruction — **not** the official invite-only
script, and **not** investment advice.

---

## 1. Design intent (why a system at all)

The system exists to remove discretionary, emotional decisions from investing:

- Don't sell a ₹10 stock at ₹20 if it is on its way to ₹1,000 (**ride winners**).
- Don't ride a ₹10 stock to ₹0 (**cut losers** — max hit ≈ one position's size).
- Wealth comes from holding a *few* big winners for a long time; the rules exist to
  make holding them psychologically possible.
- Everything is **rule-based / quantitative / price-action** — no news, no
  fundamentals, no market timing by opinion.

Reference metric: **Calmar ratio = average annual return ÷ maximum drawdown.**
Higher is better; it rewards return *per unit of drawdown pain*.

---

## 2. Market & timeframe

- **Timeframe:** Weekly. All decisions are made on the **Friday close** and executed
  on **Monday's open**. Nothing is done intra-week. ~5 minutes of work per week.
- **Universe:** A pre-defined list (the talk references variants tracking the
  NSE 500 and mid/small-cap baskets). The indicator is applied per symbol; the
  universe is your watchlist.

---

## 3. Entry

- Indicator: **Bollinger Band** with basis length **50** and **2** standard
  deviations (this "2σ" is the source of the name). Source: `close`.
- **Signal:** the weekly `close` **crosses above the Upper Bollinger Band**.
  Rationale: ~95% of observations sit within ±2σ, so a close beyond +2σ is a
  statistically unusual, high-momentum event worth participating in.
- **Execution:** enter at the **next weekly open** (Monday), after the Friday
  signal is confirmed.

---

## 4. Position sizing

- Fixed **2% of capital per position**.
- `quantity = floor( capital × 2% ÷ entry_price )`.
- Example: ₹1,00,000 capital → ₹2,000 per stock. A ₹500 stock → 4 shares; a ₹50
  stock → 40 shares.
- Because every position is capped, the worst-case loss on any single name (even
  to zero) is about one position's weight of the portfolio.
- When the portfolio is "full", new signals are **ignored** until a slot frees up.
  (This is a portfolio-level rule you enforce across your watchlist; the indicator
  sizes one symbol at a time.)

---

## 5. Exits / stops (all on a weekly-close basis)

Three stop references, applied together:

1. **Initial stop — 20% below the entry price.** Active from entry; acts as the
   floor for the trailing stop.
2. **100 EMA** trailing reference.
3. **Volatility trail** — the ATR-based trailing line, chosen via the
   `Volatility trail engine` input:
   - **SuperTrend** *(default)* — `ta.supertrend(factor = 1.8, atrPeriod = 14)`.
     The classic SuperTrend support line that trails up in an uptrend and flips
     above price when the trend breaks.
   - **ATR chandelier** — `highest_high_since_entry − 1.8 × ATR(14)`. Trails up as
     new highs are made; never moves down.

   Both are ATR-driven; SuperTrend simply replaces the chandelier as the default.
   Note a SuperTrend `factor` of `1.8` is tighter than the common `~3`.

**Exit test:** on a confirmed weekly close **below the effective stop**, exit at the
next open.

### Combining the trailing references

The podcast says exit on *"whichever is earlier"*, yet also says the system holds
through 50%+ corrections in strong movers — these tug in opposite directions, so the
combination is a configurable input (`Effective trailing stop`):

In the table, `vol_trail` is the chosen engine (SuperTrend or ATR chandelier):

| Mode | `effective_stop =` |
|---|---|
| **Whichever hit first (tightest)** *(default)* | `max( 20%_stop, max(EMA100, vol_trail) )` |
| Volatility trail only | `max( 20%_stop, vol_trail )` |
| 100 EMA only | `max( 20%_stop, EMA100 )` |
| Both broken (loosest) | `max( 20%_stop, min(EMA100, vol_trail) )` |

- The 20% initial stop is always the floor.
- Early in a trade the 20% stop dominates; as price rises the trailing references
  climb above it and take over.
- **Loosest** gives multi-baggers the room the podcast emphasises (only exits once
  *both* the EMA and the ATR line are broken). **Tightest** locks profit sooner.

---

## 6. What the indicator draws

| Colour | Meaning |
|---|---|
| Blue | Upper Bollinger Band `(50, 2)` — the entry trigger |
| Red | `100 EMA` |
| Green | Volatility trail — SuperTrend `(1.8, 14)` *(default)* or `ATR(14) × 1.8` chandelier |
| Orange | Initial 20% stop (fixed from entry) |
| Fuchsia | Effective stop used for the exit test |
| Grey | Entry price |
| BUY / EXIT | Trade markers; green background tint while in a trade |

Dashboard (top-right): status, last close, entry price, each stop level, open P&L%,
suggested quantity for your capital, position value, and trade count / win rate.

---

## 7. Reported historical character (from the talk — not a promise)

The presenter cited back-test/live figures such as ~40% CAGR against ~24% max
drawdown (Calmar ≈ 1.67), an average holding period around 750 days (winners far
longer, ~1,350 days), and roughly 68% time invested / 32% in cash. These are the
*speaker's* figures for their own implementation and are **not reproduced or
guaranteed here** — always run your own back-test.

---

## 8. Interpretation notes / open points

- **Repainting:** weekly signals are only final at Friday's close; the current
  forming week can change. The script evaluates entries/exits on the *confirmed*
  bar and models fills at the next open.
- **Entry price basis:** modelled as the next weekly open (Monday). Slippage and
  costs (the talk assumes ~0.25% cost + brokerage) are not modelled by the plot.
- **EMA vs SMA:** "100 EMA" is used; if the original used an SMA, change `emaLen`'s
  calculation accordingly.
- **Volatility trail:** default is `ta.supertrend(1.8, 14)`; the alternative ATR
  chandelier uses `ta.atr()` (Wilder/RMA smoothing) over 14 weekly bars ×1.8,
  anchored to the highest high since entry. Both use the same ATR family.
