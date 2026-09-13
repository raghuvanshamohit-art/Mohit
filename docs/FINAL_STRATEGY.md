# CW 2σ — Final Strategy (entry / exit conditions)

The configuration selected by `backtest/best_combo.py` after testing every lever.
Weekly timeframe, Nifty 500 universe. **Educational; in-sample & survivorship-biased.**

## Timeframe & universe
- **Weekly.** Evaluate on the **Friday (weekly) close**, execute at the **next Monday's open**.
- **Universe:** all Nifty 500 stocks (no market-cap restriction).

## ENTRY — buy at Monday's open when BOTH are true on Friday's close
1. **Bollinger breakout** — weekly close crosses **above the Upper Bollinger Band (SMA 52, 2σ)**:
   - `UpperBB = SMA(close, 52) + 2 × StdDev(close, 52)`
   - `close[t] > UpperBB[t]` **and** `close[t-1] ≤ UpperBB[t-1]`
2. **Relative strength > 0.2** — outperforming the Nifty 500 by **>20% over 26 weeks**:
   - `RS = (close[t] / close[t-26]) − (NIFTY500[t] / NIFTY500[t-26])`
   - require `RS > 0.20` (no upper cap)

## POSITION SIZING
- **4% of current equity** per position: `qty = floor(0.04 × equity ÷ price)`
- **Max 50 concurrent positions**; take a new signal only when a slot is free and cash allows.

## EXIT — 20% ratcheting trailing stop (sell at Monday's open)
- On entry: `stop = entry × 0.80`
- Each weekly close: `stop = max(prev_stop, weekly_close × 0.80)` — ratchets **up only**
- Exit when **weekly close < stop**. No profit target.

## Deliberately NOT used (each reduced performance in testing)
- No 100 EMA in the exit · No market-regime filter · No market-cap band · No upper cap on RS.

## Backtested result (2008–2026, ₹20L, 0.25%/side, in-sample)
| Metric | Value |
|---|--:|
| CAGR | ~29.4% |
| Max drawdown | ~24.5% |
| Calmar | ~1.20 |
| Sharpe | ~1.65 |
| Win rate | ~55% |
| vs Nifty 500 B&H | ~11.7% CAGR / 45% DD |

## Reproduce
```bash
python3 backtest/best_combo.py     # full candidate comparison + this pick
```

⚠️ In-sample and survivorship-biased (today's Nifty 500). The ~29% CAGR is an optimistic
upper bound; trust the rules and their relative edge over the alternatives, not the exact number.
Validate on a point-in-time universe and out-of-sample before risking capital. Not investment advice.
