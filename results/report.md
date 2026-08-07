# Top-10 F&O Daily Gainers — Backtest Results

*Strategy:* each trading day, rank the NSE F&O universe by that day's % change and buy the **top 10 gainers** (equal-weight), then hold.

**Data:** 218 F&O stocks, 1873 trading days, 2018-01-01 → 2025-07-31 (Yahoo Finance, adjusted close).

**Costs:** net results charge 0.25% round-trip per rebalance (brokerage + STT/exchange charges + slippage).


## 1. How many days do they sustain?

**(a) Staying in the top-10** — once a stock enters the daily top-10 gainers, how many consecutive days it stays there:

- Episodes analysed: **16,698**
- Mean sustain: **1.12 days**, median **1 day(s)**
- One-and-done (exactly 1 day): **89.8%**
- Lasts ≥2 days: 10.2%, ≥3 days: 1.5% (max ever 8 days)

**(b) Does the up-move continue?** Average *forward* return after entering the top-10 (vs. the universe average = the edge):

|    |   horizon_days |   avg_fwd_return_% |   median_fwd_return_% |   win_rate_% |   universe_avg_% |   edge_vs_universe_% |   n_obs |
|---:|---------------:|-------------------:|----------------------:|-------------:|-----------------:|---------------------:|--------:|
|  0 |              1 |               0.21 |                 -0.02 |        49.08 |             0.09 |                 0.13 |   18710 |
|  1 |              2 |               0.25 |                 -0.06 |        48.94 |             0.17 |                 0.08 |   18700 |
|  2 |              3 |               0.33 |                 -0.04 |        49.42 |             0.26 |                 0.07 |   18690 |
|  3 |              5 |               0.51 |                  0    |        49.99 |             0.43 |                 0.08 |   18670 |
|  4 |             10 |               0.95 |                  0.37 |        52.1  |             0.87 |                 0.07 |   18620 |
|  5 |             15 |               1.48 |                  0.72 |        53.42 |             1.33 |                 0.16 |   18570 |
|  6 |             20 |               2    |                  1.2  |        54.83 |             1.79 |                 0.22 |   18520 |


## 2. Strategy performance by hold period (NET of costs)

|   hold_days |   years |   total_return_% |   CAGR_% |   ann_vol_% |   sharpe |   max_drawdown_% |   calmar |
|------------:|--------:|-----------------:|---------:|------------:|---------:|-----------------:|---------:|
|           1 |    7.43 |            -62.7 |   -12.42 |        26.4 |    -0.37 |            -76.9 |    -0.16 |
|           2 |    7.42 |            -20.2 |    -2.99 |        23.4 |    -0.01 |            -68.2 |    -0.04 |
|           3 |    7.42 |             29.9 |     3.59 |        22.1 |     0.27 |            -60.7 |     0.06 |
|           5 |    7.41 |            106.4 |    10.27 |        21.3 |     0.57 |            -53.5 |     0.19 |
|          10 |    7.39 |            190.9 |    15.54 |        21   |     0.79 |            -43.9 |     0.35 |
|          15 |    7.37 |            263.3 |    19.12 |        20.9 |     0.94 |            -42.7 |     0.45 |
|          20 |    7.35 |            308.7 |    21.1  |        20.8 |     1.03 |            -39.8 |     0.53 |

Best net CAGR is at a **20-day hold**. For reference, the same table **gross** (no trading costs):

|   hold_days |   years |   total_return_% |   CAGR_% |   ann_vol_% |   sharpe |   max_drawdown_% |   calmar |
|------------:|--------:|-----------------:|---------:|------------:|---------:|-----------------:|---------:|
|           1 |    7.43 |           3902.5 |    64.32 |        26.4 |     2.02 |            -32.7 |     1.97 |
|           2 |    7.42 |            725.7 |    32.89 |        23.4 |     1.33 |            -38.2 |     0.86 |
|           3 |    7.42 |            516.4 |    27.77 |        22.1 |     1.22 |            -38.8 |     0.72 |
|           5 |    7.41 |            424.7 |    25.06 |        21.3 |     1.16 |            -39.4 |     0.64 |
|          10 |    7.39 |            363.2 |    23.04 |        21   |     1.09 |            -35.8 |     0.64 |
|          15 |    7.37 |            394.9 |    24.22 |        20.9 |     1.14 |            -37.4 |     0.65 |
|          20 |    7.35 |            415   |    24.97 |        20.8 |     1.18 |            -35.9 |     0.7  |

## 3. 'Hold until it drops out of the top-10' (event study)

- Trades: **16,689**
- Average hold period: **1.12 days** (median 1)
- Average trade return: **0.24%** (median -0.06%), win rate 48.4%


## 4. Benchmark — equal-weight F&O universe (buy & hold)

- CAGR **21.47%**, max drawdown -38.4%, Sharpe 1.13 over the same window.


## Caveats

- **Constituent/survivorship bias:** uses today's F&O list over the whole window; names that were dropped are missing, which flatters results.
- Enters/exits at the **close**; no impact modelling beyond the flat cost. Real slippage on chasing gappy movers is worse.
- Yahoo adjusted-close data has occasional gaps/adjustment errors; treat figures as indicative, not exact.
- No leverage, no overnight-futures financing; this is modelled as a cash-equity basket.