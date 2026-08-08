# Replicating ExitMantra's Quant Rating & Exit Price on Chartink

A practical, honest guide to reproducing ExitMantra's 3‑criteria quant rating —
**ATH TTM Profits · 52‑Week Outperformance · Above Exit Price** — using free retail
tools (mainly **Chartink**, with **Screener.in** and **TradingView** where Chartink
falls short).

> **Reality check up front:** Criteria 1 and 2 can be approximated well on retail tools.
> The **Exit Price is proprietary** ("15 years of research, 600+ back‑tested indicators")
> and *cannot be reproduced exactly*. What we can do is build a **behaviourally identical
> proxy** (a long‑term, volatility‑based trailing stop) that moves and hides the same way
> ExitMantra describes. Treat the numbers as your own model, not theirs.

---

## The scoring model (what we are rebuilding)

| Score | Rating   | Criteria met |
|:-----:|:---------|:-------------|
| 3     | **ADD**     | All 3 |
| 2     | **HOLD**    | Any 2 |
| 1     | **REPLACE** | Any 1 |
| 0     | **EXIT**    | None |

The three criteria (each is a simple Yes/No):

1. **ATH TTM Profit** — Consolidated TTM PAT (ex‑exceptional) at an all‑time high.
2. **Outperformance** — Stock's 52‑week return > NIFTY 500's 52‑week return.
3. **Above Exit Price** — CMP above the quant trailing‑stop line.

**Zone** = a coarser view of the same three: **2–3 positive → Bull**, **1 positive → Pig**,
**0 positive → Bear**.

---

## 1 · All‑Time‑High TTM Profit

**Can Chartink do it? Partially — this is the weak spot.**

Chartink *does* expose fundamentals (quarterly net profit, and even a TTM‑net‑profit
concept — see the public screener "Latest Quarter Net Profit > Twice TTM NP"). But it
**cannot verify an *all‑time* high**, because:

- There is no "TTM PAT 5 years ago" clause to compare against — Chartink only reaches a
  handful of recent quarters, so at best you get a **recent high**, not a 30‑year ATH.
- Chartink net profit is typically **standalone and includes exceptional items**.
  ExitMantra uses **consolidated PAT, *excluding* exceptional items** (source: Accord
  Fintech). Different number entirely.

### Best Chartink approximation (a "profit is making new highs" filter)

Build TTM PAT from the four most recent quarters and require it to beat the previous
rolling‑TTM windows Chartink can reach:

```
TTM(now) = QNP(latest) + QNP(1q ago) + QNP(2q ago) + QNP(3q ago)
```

Condition (approximation of "profit at a high"):
```
TTM(now)  >  QNP(1q ago) + QNP(2q ago) + QNP(3q ago) + QNP(4q ago)      # beats 1‑qtr‑old TTM
AND  TTM(now)  >  QNP(4q ago)+QNP(5q ago)+QNP(6q ago)+QNP(7q ago)       # beats 1‑yr‑old TTM (if reachable)
```
In Chartink's editor pick the fundamental clauses **"Latest quarterly net profit"**,
**"1 quarter ago quarterly net profit"**, … and add them. This flags *rising* TTM profit
— useful, but it is **"near‑term high," not ATH.**

### Recommended tool for a true ATH: **Screener.in**

- Open any company → **Quarterly Results / P&L**. Screener shows a **TTM** column and lets
  you toggle **Consolidated**. Read the TTM PAT and confirm visually that it's the highest
  bar ever — this matches ExitMantra's definition far more closely than Chartink.
- For bulk filtering, a Screener custom query gets you *growth* (e.g.
  `Profit after tax latest quarter > Profit after tax preceding year quarter`) but still
  needs a manual/visual check for the true all‑time peak.
- Other options with clean TTM history: **Trendlyne, Tickertape, Tijori**.

**Verdict:** Use Chartink to shortlist "profit rising," then confirm ATH TTM (consolidated,
ex‑exceptional) on Screener.in.

---

## 2 · 52‑Week Outperformance vs NIFTY 500

**Can Chartink do it? Yes — cleanly.** This is Chartink's home turf (Relative Strength).
Several public screeners already do exactly this ("Comparative Relative Strength Nifty 500").

### The logic

Outperformer if the stock's 1‑year price ratio beats the index's 1‑year price ratio:

```
   latest close / 1 year ago close        (stock)
   ────────────────────────────────  >  1
   Nifty500 close / Nifty500 close_1yr     (index)
```

Equivalently, the classic **Relative Strength** value:
```
RS = ( StockClose / StockClose_52w ago ) / ( Nifty500 / Nifty500_52w ago )  − 1
RS > 0  →  Outperformer     RS < 0  →  Underperformer
```

### How to build it in Chartink

1. New scan → add a condition using **"1 year ago close"** for the stock
   (≈ 252 sessions ≈ 52 weeks).
2. Add the **index** as the benchmark: in the clause dropdown choose the index and set it
   to **NIFTY 500** (verify the exact label in Chartink's index list — it may show as
   *Nifty 500* / legacy *CNX 500*).
3. Require: `stock 1‑yr ratio  >  Nifty 500 1‑yr ratio`.

Readable form of the condition:
```
( {cash} ( latest close / "1 year ago close" ) > ( Nifty500 latest close / Nifty500 1 year ago close ) )
```

> **Fastest path:** don't hand‑type the index token — open a public
> **"Comparative Relative Strength — Nifty 500"** screener on Chartink, hit **Copy/Edit**,
> and reuse its index reference. Then just confirm the 52‑week (1‑year) offset.

**Verdict:** Fully replicable on Chartink and updates intraday, exactly like ExitMantra's
"real‑time during market hours" behaviour.

---

## 3 · The Quant Exit Price — how to derive a working proxy

**This is the hard one and the one you most want.** ExitMantra keeps the formula secret,
but their *description* tells us what kind of tool it is. Match the clues:

| ExitMantra says…                                  | Which means…                          |
|:--------------------------------------------------|:--------------------------------------|
| "Derived from **long‑term trends**"               | Long timeframe → **weekly**           |
| "Adjusts with the stock's **movement and volatility**" | **ATR / volatility‑based**            |
| "May shift daily **or stay unchanged for extended periods**" | A **ratchet/trailing** stop that locks on pullbacks |
| "**Not shown when the stock is in the Bear zone**" | The line flips *above* price and stops being a stop |

That behaviour profile — trails up, freezes during pullbacks, flips side on breakdown —
is almost exactly a **Supertrend** or a **Chandelier Exit**. A plain moving average is a
weaker match because it drifts continuously (never "stays unchanged").

### Best proxy: Weekly Supertrend (recommended)

- Read the **Exit Price ≈ the value of the weekly Supertrend line**.
- Suggested starting params: **Supertrend(10, 3)** or **(14, 3)** on the **weekly** chart.
  Tune the multiplier so the plotted line visually matches ExitMantra's Exit Price on a few
  stocks you can see, then keep those settings fixed.

**Chartink scan — "is the stock above its exit (Bull structure)":**
```
Weekly Close  >  Weekly Supertrend( 10, 3 )
```
**Below exit / breakdown ("Exit triggered"):**
```
Weekly Close  <  Weekly Supertrend( 10, 3 )
```
(Clone any public *"weekly close above supertrend"* screener to get the exact clause tokens,
then set your period/multiplier.)

### Alternative proxy: Chandelier Exit (pure volatility trailing stop)

A textbook long‑term stop you can compute or plot directly:
```
Exit Price (long) = Highest High(22)  −  ATR(22) × 3        # on the WEEKLY chart
```
22 weeks ≈ 6 months of look‑back. This is arguably the closest *formula* to "downside,
volatility‑based, long‑term."

### Reading the actual number per stock: TradingView

ExitMantra already embeds TradingView, so use it:
1. Open the weekly chart of the stock.
2. Add indicator **Supertrend** (10,3) *or* **Chandelier Exit** (22, 3).
3. The line's current value **is your Exit Price**. It updates as the stock moves — the
   same "dynamic, may change daily or hold for weeks" behaviour ExitMantra describes.

> **Honesty note:** these will *not* match ExitMantra tick‑for‑tick — their exact indicator,
> parameters and smoothing are undisclosed. But a weekly ATR trailing stop reproduces the
> *logic and behaviour* (cut losers when structure breaks, ride winners while it holds).

---

## Putting the three together

Once you have the three Yes/No flags, the rest is arithmetic — identical to ExitMantra:

**Score & Zone**
```
score = (ATH_TTM_profit? 1:0) + (outperformer? 1:0) + (above_exit? 1:0)
3→ADD  2→HOLD  1→REPLACE  0→EXIT
Zone:  score≥2 → Bull   |   score==1 → Pig   |   score==0 → Bear
```

**Risk Meter — "Cushion"** (how far price is above the exit)
```
Cushion % = (CMP − ExitPrice) / CMP × 100
```
| Cushion    | ExitMantra label | Meaning |
|:-----------|:-----------------|:--------|
| **< 20%**  | Low Risk         | Small gap; exit may trigger on minor moves, but loss if hit is small |
| **20–35%** | Moderate Risk    | — |
| **> 35%**  | High Risk        | Big gap; unlikely to hit soon, but a larger loss if it does |

**Position‑Sizing / Stock Allocation Calculator** (their calculator, reproduced)
```
Risk per share   = Entry − ExitPrice
Quantity         = Total Risk you accept ÷ Risk per share
Total Allocation = Quantity × Entry
```
Example: risk ₹10,000; Entry ₹500; Exit ₹450 → risk/share ₹50 → **200 shares** →
allocation **₹1,00,000**.

---

## Tool cheat‑sheet

| Criterion               | Best tool        | Replicable? |
|:------------------------|:-----------------|:-----------:|
| ATH TTM Profit          | Screener.in (Chartink to shortlist) | ⚠️ Approx (data source & ATH depth differ) |
| 52‑wk Outperformance    | **Chartink**     | ✅ Yes |
| Exit Price              | TradingView / Chartink (weekly Supertrend or Chandelier) | ⚠️ Behavioural proxy only |
| Score / Zone / Risk / Sizing | Any (arithmetic) | ✅ Yes |

---

## Caveats

- The **Exit Price proxy is a model, not ExitMantra's number.** Back‑test and tune it
  before relying on it.
- **Data source matters:** consolidated vs standalone, with/without exceptional items, and
  Accord vs Chartink feeds will produce different profit figures.
- This document is an educational how‑to for building your own screens. It is **not
  investment advice.** Do your own due diligence and consult a SEBI‑registered advisor
  before acting.

---

### Reference screeners used to confirm feasibility
- Comparative Relative Strength vs Nifty 500 — `chartink.com/screener/copy-comparative-relative-strength-for-cash-basis-nifty-500-ranking-928`
- Weekly close above Supertrend — `chartink.com/screener/weekly-close-above-super-trend`
- Latest Quarter Net Profit vs TTM NP — `chartink.com/screener/copy-shares-latest-quarter-net-profit-twice-ttm-np`
- Chartink Scanner User Guide — `chartink.com/articles/scanner/scanner-user-guide/`
