# Strategy Specification Template

Copy this file for each new system. A system is not "ready" until every field is
filled in writing — an empty field is an undefined rule, and an undefined rule is
a discretionary decision waiting to happen.

---

## 1. Identity
- **Name:**
- **Author / date:**
- **Type:** ☐ Directional  ☐ Non-directional  ☐ Mean-reversion  ☐ Other: ____
- **One-line thesis:** *(Why should this have an edge?)*

## 2. Universe
- **Instrument(s):**
- **Liquidity check:** *(min volume / OI you require)*

## 3. Cycle / timeframe
- **Decision point:** *(e.g. Friday close)*
- **Holding period:**
- **Signal timeframe:** *(e.g. weekly candles)*

## 4. Entry rule
- **Signal / filter(s):** *(must be mechanically checkable)*
- **Entry instrument & timing:**
- **Skip conditions:** *(events, low liquidity, etc.)*

## 5. Exit rule
- **Stop loss:** *(price/level and the `R` value it represents)*
- **Profit target:**
- **Time exit:** *(latest exit regardless of P&L)*
- **Adjustment rules (if any):**

## 6. Position sizing
- **Risk per trade `R`:** ____ % of capital
- **Sizing formula:** *(how you convert the stop distance into quantity)*

## 7. Portfolio risk limits
- **Max weekly loss:** ____ `R`
- **Max system drawdown (kill switch):** ____ %
- **Concurrent exposure cap:** ____ `R`
- **Cooldown rule:**

## 8. Validation record
- **Backtest period(s):**
- **Regimes covered:** ☐ Bull ☐ Bear ☐ Sideways ☐ Stress (2008/2020)
- **Trades in sample:**
- **Strike rate:** ____ %  | **Avg win / Avg loss:** ____ | **Expectancy/trade:** ____
- **Max drawdown:** ____ %  | **Sharpe / Calmar:** ____
- **Costs modelled?** ☐ Brokerage ☐ Slippage ☐ Taxes ☐ Spread
- **Out-of-sample confirmed?** ☐  | **Forward/paper cycles:** ____

## 9. Go-live
- **Start size:** *(fraction of full)*
- **Scale-up trigger:**
- **Review cadence:** Weekly ____ | Monthly ____

---

> Expectancy per trade = (Win% × Avg Win) − (Loss% × Avg Loss)
>
> If this number isn't positive after costs, the system does not go live.
