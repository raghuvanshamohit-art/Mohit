# Mohit

Content notes and articles.

## Articles

- [From Easy Money to a System: Rakesh Pujara's Trading Journey](content/system-based-trading-journey.md) — Vivek Bajaj in conversation with Rakesh Pujara on the transition from arbitrage and discretionary trading to system-based, rule-based trading.

## Strategy

- [Designing a System-Based Trading Strategy](strategy/system-based-strategy-design.md) — a rule-first framework: the seven components of a tradable system, a shared risk model, two fully-specified example systems (NIFTY momentum & Bank NIFTY range), and a validation checklist.
- [Strategy Specification Template](strategy/strategy-spec-template.md) — a reusable blank spec to define any new system in writing before it goes live.

## Backtest

- [System A — NIFTY Weekly Momentum backtest](backtest/) — a dependency-free Python engine that implements System A exactly and computes expectancy, drawdown, Sharpe and Calmar. Runs out of the box on synthetic data; point `--data` at real NIFTY weekly OHLC to evaluate the real edge.
- [Long ATM Straddle backtest (10 years, real data)](backtest/straddle/) — buy ATM Call + ATM Put monthly, held to expiry, on **10 years of real NIFTY + India VIX data**. Includes a month-wise return table and positive/negative breakdown ([results](backtest/straddle/RESULTS.md)). Finding: holding straddles to expiry has negative expectancy (≈ −10%).
