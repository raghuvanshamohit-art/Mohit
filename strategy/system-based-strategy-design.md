# Designing a System-Based Trading Strategy

*A practical, rule-first framework — built on the principles from the Vivek
Bajaj × Rakesh Pujara conversation on system-based trading.*

> **Disclaimer:** This is educational content, not investment advice. Every
> number below is an **illustrative parameter to be validated on your own
> data**, not a recommendation or a guarantee. Trading in derivatives carries
> substantial risk of loss. Test on paper before risking capital, and consult a
> SEBI-registered advisor where required.

---

## 0. The one idea

> **Understanding earns respect. Rules earn money.**

A system-based strategy is simply a set of rules — for *what* to trade, *when*
to enter, *when* to exit, and *how much* to risk — that you can follow
identically whether you feel confident or scared. If a rule can't be written
down and checked mechanically, it isn't part of the system.

---

## 1. Design principles (the non-negotiables)

Every strategy in this repo must respect five principles drawn from the
interview:

1. **Rules before trades.** Entries, exits, and sizing are defined *before* the
   market opens — never invented mid-trade.
2. **Risk sized to income, not to greed.** Capital at risk is a function of what
   your financial life can absorb, not of how good the setup "feels."
3. **A defined cycle.** Decisions happen on a fixed rhythm (here: **weekly,
   Friday-to-Friday**) so you stop reacting to intraday noise.
4. **Edge you can measure.** A "good strike rate" is *proven* on historical
   data across multiple regimes — not assumed.
5. **Multiple, low-correlation systems.** Maturity means running several
   independent systems so no single market condition can sink you (the 2008
   lesson: 90% of undisciplined "good" traders became the bottom 10%).

---

## 2. The seven components of any tradable system

No system is complete until all seven are specified in writing.

| # | Component | The question it answers |
|---|-----------|-------------------------|
| 1 | **Universe** | *What* do I trade? (e.g. NIFTY, Bank NIFTY) |
| 2 | **Cycle / timeframe** | *How often* do I decide and hold? |
| 3 | **Entry rule** | *What signal* puts me in? |
| 4 | **Exit rule** | *What* takes me out — target, stop, or time? |
| 5 | **Position sizing** | *How much* do I risk on this trade? |
| 6 | **Portfolio risk limits** | *When* does the whole book stop trading? |
| 7 | **Review & journal** | *How* do I know the system still works? |

A reusable blank template is in
[`strategy/strategy-spec-template.md`](strategy-spec-template.md).

---

## 3. The risk model (shared across all systems)

Risk is defined **top-down**, from your life to the trade — never bottom-up from
the setup.

- **Trading capital** = money you can lose entirely without affecting your
  lifestyle. Size it against **annual income**, e.g. cap trading capital at a
  fraction of annual income so a total wipeout is survivable.
- **Risk per trade `R`** = a fixed, small fraction of trading capital.
  *Illustrative:* `R = 1%` of capital.
- **Max weekly loss** = a hard stop for the cycle. *Illustrative:* `3R` in a
  week → stop trading until the next cycle.
- **Max system drawdown** = a kill switch for a single system. *Illustrative:*
  `-15%` peak-to-trough → pause the system, review, don't "make it back."
- **Concurrent exposure cap** = total risk live at once across all systems.
  *Illustrative:* ≤ `6R`.
- **Cooldown rule** = after a max-weekly-loss hit, no new positions for the rest
  of the cycle. No revenge trades.

The point of these numbers is not their exact value — it's that they exist,
they're written down, and they're obeyed automatically.

---

## 4. Example System A — "NIFTY Weekly Momentum" (directional)

A trend-following system that trades *with* the weekly momentum of the index.

| Component | Rule |
|-----------|------|
| **Universe** | NIFTY 50 index (traded via index futures or a defined-risk long option) |
| **Cycle** | Decide on **Friday close**; hold the following week; re-evaluate next Friday |
| **Bias filter** | **Long** only if weekly close > 20-week EMA **and** weekly RSI(14) > 55. **Flat** otherwise. (Symmetric short variant optional.) |
| **Entry** | On the bias signal, enter at Monday open (or Friday close). If using options, buy a slightly-ITM call of the next weekly/monthly expiry to bound risk. |
| **Stop** | Exit if NIFTY closes below the prior week's low, or at a fixed `1R` loss — whichever comes first. |
| **Target / exit** | Trail the stop to the prior week's low each Friday; take profits on a `2R` move or on the bias filter flipping to flat. Options positions are closed before theta decay accelerates. |
| **Sizing** | Position size so the distance to stop equals exactly `1R` (1% of capital). |
| **Skip conditions** | No new entry in the week of a major event (Budget, RBI policy, election result) unless the system is explicitly designed for it. |

**Why it fits the principles:** one clear signal, a weekly cycle, a hard `1R`
stop, and a filter that keeps you out of chop.

---

## 5. Example System B — "Bank NIFTY Weekly Range" (non-directional)

A premium-capture system that profits when Bank NIFTY stays inside an expected
weekly range — low correlation to System A's directional bet.

| Component | Rule |
|-----------|------|
| **Universe** | Bank NIFTY weekly options |
| **Cycle** | Enter at the start of the weekly expiry cycle; must be flat by expiry |
| **Entry** | Sell a **delta-neutral iron condor**: short strikes near the ±1 expected-move boundary (derived from ATR or option-implied move), long wings further out to cap risk. Enter only if implied volatility rank > 50 (sell when premium is rich). |
| **Defined risk** | Wings make max loss known at entry. Size so max loss on the structure ≤ `1R`. |
| **Adjustment** | If the underlying reaches a tested short strike (≈ 30-delta), roll the untested side toward price to re-center — one adjustment maximum. |
| **Profit target** | Close the structure at **50% of credit captured**. Don't hold for the last rupee. |
| **Stop** | Exit the whole structure at a loss of `1R` (≈ 1.5–2× credit), or on adjustment failure. |
| **Skip conditions** | Don't initiate before a scheduled high-impact event inside the cycle; IV crush after the event is not worth the gap risk. |

**Why it fits the principles:** capped, known risk; a mechanical 50%-profit
exit; and a directional-independence that diversifies the book.

---

## 6. Validation — before a single rupee goes live

A strategy is a *hypothesis* until the data agrees. Run this checklist:

- [ ] **Sample size:** enough trades to be statistically meaningful (aim for
      100+ per system), not five lucky ones.
- [ ] **Regime coverage:** backtest spans bull, bear, and sideways — and
      explicitly includes stress windows (2008, 2020) so you see the worst case.
- [ ] **Metrics computed:** strike rate, average win / average loss,
      **expectancy per trade**, max drawdown, and a risk-adjusted return
      (Sharpe or Calmar).
- [ ] **Costs included:** brokerage, slippage, taxes, and the bid-ask spread —
      an edge that dies after costs was never an edge.
- [ ] **Out-of-sample test:** parameters fit on one period, results confirmed on
      an untouched period. Beware curve-fitting.
- [ ] **Forward (paper) test:** trade it live-but-simulated for several cycles
      and confirm results match the backtest before deploying capital.

**Expectancy** is the number that matters most:

```
Expectancy per trade = (Win% × Avg Win) − (Loss% × Avg Loss)
```

A system with a modest 45% strike rate can still compound beautifully if its
average win is meaningfully larger than its average loss. A 70% strike rate can
still blow up if the occasional loss is enormous. **Strike rate alone lies —
expectancy tells the truth.**

---

## 7. Go-live and review

1. **Start small.** Deploy at a fraction of full size; scale up only as live
   results track the backtest.
2. **Journal every trade.** Log the setup, the rule that triggered it, and the
   outcome — the journal is how you catch a system that has quietly stopped
   working.
3. **Review on a cadence.** Weekly: did I follow every rule? Monthly: is live
   expectancy still in line with the backtest?
4. **Pause, don't force.** If a system breaches its max-drawdown kill switch,
   stop it and investigate. Never try to "win it back" — that's the exact
   instinct that turned 90% of good traders into the bottom 10% in 2008.

---

## The takeaway

> Nobody hands you a system. **Everyone does their own hard work** — write the
> rules, size the risk to your life, prove the edge on data, then follow the
> system through good weeks and bad. The market becomes easy only *after* the
> rules are non-negotiable.

---

*Framework adapted from the StockEdge / Elearnmarkets conversation between Vivek
Bajaj and Rakesh Pujara on system-based trading. See the companion piece:
[System-Based Trading Journey](../content/system-based-trading-journey.md).*
