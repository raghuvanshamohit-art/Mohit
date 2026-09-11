# The Decision System

*Turning [The Investor's Framework](investment-framework.md) into numbers.*
Three engines answer the three operational questions — **which stock at what
price, which asset to sell/buy, and how to pyramid** — with explicit formulas
and assumptions you control.

Use them from the CLI (`python run.py value | rebalance | pyramid`), from the
no-install page (`web/strategy.html`), or as a library (`from strategy import
valuation, allocation, pyramid`).

> **Not advice.** These are calculators. Every output is only as good as the
> assumptions *you* feed in — especially growth. The tool never guesses a growth
> rate or recommends a stock; that judgement stays yours.

---

## 1. Valuation — which stock, at what price?

Implements Lens 2 ("price is what you pay, value is what you get").

### What it computes

A **multi-stage discounted cash-flow** on a per-share cash proxy (EPS or free
cash flow per share):

- Year-*t* cash flow in an explicit stage: `CFₜ = base × (1 + g)ᵗ`
- Present value of the explicit years: `Σ CFₜ / (1 + d)ᵗ`
- **Gordon terminal value** at the end of the last explicit year *N*:
  `TV = CF_N × (1 + gₜ) / (d − gₜ)`, discounted back as `TV / (1 + d)ᴺ`
- **Intrinsic value** = PV(explicit) + PV(terminal)

where `d` = discount rate, `g` = stage growth, `gₜ` = terminal growth.
Requires `d > gₜ` (otherwise the terminal value is infinite).

### The discount rate *is* the bond market

> *"If you don't understand bonds, you don't understand anything."*

`discount = bond_yield + equity_risk_premium` (default ERP 5%). Raise the
risk-free rate and intrinsic value falls even though the business is unchanged —
this is the framework's shop example, where an RBI hike turned a ₹1cr shop into
an ₹80L one. **Interest rates move the price you should pay, not the value.**

### Margin of safety → verdict

`margin_of_safety = (intrinsic − price) / intrinsic`

| Margin of safety | Verdict |
|---|---|
| ≥ +30% | **BUY** — strong margin of safety |
| +10% to +30% | **ACCUMULATE** — modest margin of safety |
| −10% to +10% | **HOLD** — roughly fairly valued |
| < −10% | **AVOID** — price above intrinsic value |

### Implied growth (reverse DCF)

Given the current price, the tool can solve for the **stage-1 growth the market
is already pricing in**. This is the guard against the *2024 mistake* — paying
for a 20% growth rate as if it were permanent. If the price implies 25% growth
forever, ask whether that is realistic before buying.

### Worked example

```bash
python run.py value --eps 50 --growth 0.15 --years 10 \
                    --terminal 0.04 --bond-yield 0.07 --erp 0.05 \
                    --price 700 --implied
```

```
Discount rate = 7.0% bond yield + 5.0% risk premium = 12.0%

Intrinsic value: 1426.57 / share
  from explicit cash flows : 579.91
  from terminal value      : 846.66 (59% of value)
Price: 700.00
Margin of safety: +50.9%
Verdict: BUY — strong margin of safety
Implied stage-1 growth priced in: 5.0% for 10y — is that realistic?
```

Read it as: *if this business really grows EPS ~15% for a decade, ₹700 is a deep
discount — the market is only pricing ~5% growth.* Your whole job is to judge
whether 15% is honest. Watch the **terminal share** too: if most of the value
sits in the terminal, the answer is very sensitive to `gₜ` and `d`.

---

## 2. Allocation — which asset to sell, which to buy?

Implements the headline rule: **~92% of success is asset allocation**, and its
mechanic — *trim what has run up, add to what has fallen.*

### Target mixes

Gold is **insurance, not a wealth engine** — sized 10% (aggressive) to 20%
(conservative):

| Profile | Equity | Gold | Bonds |
|---|---|---|---|
| `aggressive` | 80% | 10% | 10% |
| `balanced` | 65% | 15% | 20% |
| `conservative` | 60% | 20% | 20% |

Pass your own with `--target equity=70 --target gold=12 --target bonds=18`.

### Counter-trend rebalance

For each sleeve: `drift = current_weight − target_weight`. If `|drift|` exceeds
the tolerance **band** (default 5%), act:

- **SELL** the overweight amount `value − target_value`, or
- **BUY** the underweight amount `target_value − value`.

Within the band → **HOLD** (bands stop you churning on noise). A full rebalance
is cash-neutral: rupees sold ≈ rupees bought.

```bash
python run.py rebalance --holding equity=750000 --holding gold=150000 \
                        --holding bonds=100000 --profile balanced --band 0.03
```
```
ASSET     ACTION           AMOUNT      NOW   TARGET    DRIFT
bonds     BUY             100,000    10.0%    20.0%   -10.0%
equity    SELL            100,000    75.0%    65.0%    10.0%
gold      HOLD                  -    15.0%    15.0%     0.0%
```

### Rebalance with new money (no selling)

The friction-free version: point fresh contributions at the **most underweight**
sleeves first (proportional to each sleeve's shortfall), so you never sell a
winner or trigger tax. `--new-money 100000`.

### Glide path — slow down near the goal

> *"Cut speed entering the city, the colony, the lane, the gate."*

`--years-to-goal N` shifts equity into bonds as the goal nears. Beyond 15 years
out, the base mix is untouched; inside 15 years, `equity → equity × (N/15)` and
the freed weight moves to bonds (gold held steady). At the goal, the mix is
bond-heavy and certain.

---

## 3. Pyramid — how to add to a winner?

Implements the stock rule: **let profits run; add on the way up; but never
pyramid above intrinsic value.**

### The ladder

- Rungs are spaced `step` apart: `priceₙ = entry × (1 + step)ⁿ`.
- Rung sizes **decay** geometrically (`weightₙ ∝ decayⁿ`), normalised across all
  planned tranches — so the cheapest buy is the biggest and the position is not
  top-heavy.
- Adding **stops** at the first rung whose price exceeds `cap × intrinsic_value`
  (`cap = 1.0` stops exactly at fair value; `0.9` keeps a 10% cushion). Skipped
  rungs leave their budget as **uninvested dry powder** rather than being crammed
  into an overvalued price.
- A trailing **stop-loss** is tracked off the running average cost.

```bash
python run.py pyramid --entry 100 --intrinsic 130 --budget 100000 \
                      --tranches 6 --step 0.08 --decay 0.65 --cap 1.0
```
```
 #     PRICE          BUY     SHARES     CUM COST  AVG COST     STOP
 1    100.00       37,855     378.55       37,855    100.00    85.00
 2    108.00       24,606     227.83       62,461    103.01    87.55
 3    116.64       15,994     137.12       78,454    105.52    89.69
 4    125.97       10,396      82.53       88,850    107.56    91.43
Deployed 88,850 of 100,000 (uninvested 11,150) | final avg cost 107.56 |
avg-cost margin of safety +17.3%
```

Rungs 5–6 (at ~₹136 and ₹147) were **skipped** — they breach the ₹130 fair
value. The decaying sizes keep the average cost (₹107.56) well below the last
buy (₹125.97), so a normal pullback doesn't erase the gain. **Pyramiding still
obeys price: add into a winner only while it stays below value.**

---

## Inputs cheat sheet

| Engine | You provide | The tool returns |
|---|---|---|
| **value** | base EPS/FCF, growth stage(s), terminal growth, discount (or bond yield + ERP), price | intrinsic value, terminal share, margin of safety, verdict, implied growth |
| **rebalance** | current holdings, target profile (or custom), band; optionally new money or years-to-goal | SELL / BUY / HOLD per sleeve |
| **pyramid** | entry price, intrinsic value, budget; optionally tranches/step/decay/stop/cap | rung-by-rung buy ladder, avg cost, dry powder, stop levels |

---

*Calculators, not recommendations. Growth assumptions are the hard part and are
entirely yours. Markets carry risk of loss.*
