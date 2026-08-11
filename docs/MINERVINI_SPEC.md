# Minervini SEPA — reference spec for the screener/backtest

Distilled from Mark Minervini's *Think & Trade Like a Champion* (2017) and a
one-page VCP setup summary. This is the **source of truth** for aligning the
tool with the method. Each rule notes its status in the code and the change
needed to make the tool "book-faithful".

Status key: ✅ implemented · ⚠️ partial / differs · ❌ not yet.

---

## 1. Trend Template — the screen (Sec 6; one-pager)
The eligibility filter before any setup. Current tool covers this well.

| Rule | Param | Status |
|------|-------|--------|
| Price > 50-, 150- & 200-day MA | — | ✅ |
| 50-MA > 150-MA > 200-MA (stacked) | — | ✅ |
| 150-MA and 200-MA rising | 200-MA rising **≥ 3 months** | ⚠️ tool checks ~1 month → widen 200-MA lookback to ~63d |
| Within 25% of 52-week high | `within_high_pct=0.25` | ✅ |
| ≥ 30% above 52-week low (book); one-pager says ≥ 100% | `above_low_pct` | ⚠️ default 30% & optional; expose 100% strict variant |
| Price ≥ absolute floor | book ₹/$ ~30; tool ₹50 | ⚠️ trivial for F&O |
| Made a 52-week high every 4–6 months | — | ❌ add "new-high recency" check |
| RS vs market strong | RS Rating ≥ 70 percentile | ✅ |

## 2. Entry — the VCP setup (Sec 6–7)
The tool's biggest gap: it currently enters when the checklist turns green,
**not** on the pivot breakout.

- **VCP base** = 2–6 (usually 2–4) price contractions, volatility **high on the
  left → tight on the right**; each successive contraction **~½ the prior**.
- **Volume recedes** at the tightest points; the **final contraction is tight
  (~3–5%) with volume below the 50-day average** (a "dearth of sellers").
- **Pivot buy point** = the right edge of the base ("line of least resistance").
  **Buy as price breaks above the pivot on a volume surge** (well above the
  50-day average).
- Never buy a falling stock — trade **directionally** (Key 7).

**Tool change (priority #1):** replace the ATR%-proxy VCP + "green checklist"
entry with real **contraction detection + pivot breakout on volume**.
Status: ⚠️ VCP proxy · ❌ breakout entry.

## 3. Stops & trade management (Sec 1, 9)
- **Initial stop**: a **% below the pivot / danger point**, **capped at 8–10%**;
  his average loss is **4–5%**. He is **not a fan of pure ATR stops** — prefers
  a % keyed to the setup. `stop_pct=0.08` ✅ (ATR optional, off by default).
- **Breakeven (Key 8)**: once up a **decent gain / multiple of risk**, move the
  stop to entry — but **not too early** (allow normal fluctuation). ❌ add.
- **Trail the 50-DMA** once it rises to your breakeven price. ✅ (`trail_ma=50`).
- Cut on **violations** (heavy down-volume, break of 50-DMA). ⚠️ partial.

## 4. Selling — nail down profits (Sec 9; Key 5)
- **Sell into strength** on climax / blow-off: **price up ~25–50%+ in 1–3
  weeks**, accelerating advance, **largest up-volume since the move began**,
  **exhaustion gaps** → book profits (optionally **sell half**).
  ✅ `big_candle` exit approximates this → refine to the climax definition +
  add **sell-half** scale-out.
- **Sell into weakness** defensively when violations pile up. ⚠️.

## 5. Position sizing (Sec 8)
- Risk **1.25–2.5% of equity per trade** (either the stop tightens or the size
  shrinks to hold that).
- **≤ 10–12 names** (16–20 for large books).
- **Concentrate**: 20–25% in each of the **top 4–5**; 5–10% in unproven names.

**Tool change (priority #3):** replace equal-weight/cap-10 with **risk-based
sizing + concentration** in the equity model. Status: ❌.

## 6. Expectancy math (Sec 3–4)
- **Reward/risk ≥ 2:1**. Recovery is asymmetric (a 50% loss needs +100%).
- It's **batting average × win/loss ratio**: at 40% wins, need ~15% gains vs 5%
  losses; his ~50% batting average with 4–5% losses / ~15% gains.
- **"Plan B"**: compound **15–20% winners** via timing + concentration +
  **turnover** (sell into strength) → triple-digit annual returns; don't wait
  for one giant winner.

**Tool change (priority #4):** add **R-multiple / reward:risk** and batting-avg
lens to the backtest report (win/expectancy/PF already present ✅).

## 7. The Eight Keys to Superperformance (Sec 10)
1. **Timing** — buy at the precise low-risk moment (the pivot).
2. **Don't diversify** — concentrate in your best names.
3. **Turnover is not taboo** — recycle capital into fresh setups.
4. **Maintain the risk/reward relationship** — always ≥ 2:1.
5. **Sell into strength** — nail down profits on the way up.
6. **Trade small before you trade big** — scale up only after it works.
7. **Always trade directionally** — never buy a falling stock.
8. **Protect breakeven** after a decent gain.

---

## Implementation roadmap (to build "minervini" mode)
1. **VCP pivot detection + breakout-on-volume entry** (Sec 2 above) — the
   single biggest lever; also what our own backtest flagged.
2. **Climax sell-into-strength** (+25–50%/1–3wk, exhaustion, biggest volume)
   + **sell-half** + **breakeven-after-decent-gain** before the 50-DMA trail.
3. **Risk-based position sizing + concentration** in the equity model.
4. **Expectancy panel**: reward:risk, batting average, R-multiple.
5. Screen tweaks: 200-MA 3-month rising, 52-wk-high recency, expose the
   100%-above-low strict variant.

Each step ships with tests and a fresh backtest so the book-faithful numbers
can be compared against the current baseline.
