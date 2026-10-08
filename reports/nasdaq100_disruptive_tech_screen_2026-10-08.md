# Nasdaq-100 Disruptive-Technology Screen: AI, Robotics, Energy Storage, Blockchain, Multiomics

**Data date.**
- **Prices:** **closing prices on Oct 7, 2026** (Yahoo Finance chart API).
- **Fundamentals:** latest reported fiscal year (5–6 years of history) plus the latest 10-Q year-to-date.
- **Consensus EPS, revenue and price targets:** as of Oct 8, 2026.
- **Universe:** the **official Nasdaq-100 constituent list** from Nasdaq.com, dated Oct 8, 2026.

**Data sources.**
- **SEC EDGAR XBRL "companyfacts":** annual 10-K / 20-F data as filed, plus 10-Q year-to-date revenue.
- **Nasdaq.com:** listing exchange, market cap, consensus EPS (mostly adjusted, Zacks-sourced), price targets and ratings.
- **[stockanalysis.com](https://stockanalysis.com):** consensus **revenue** for the current and next fiscal year (free tier). It is also used as a **cross-check on reported revenue**: every company's latest-FY SEC revenue was compared with it. That check caught and fixed a revenue-tag error for MELI and CEG, where the contract-revenue tag excluded fintech and derivative income. The remaining mismatch is MU, whose FY Aug-26 10-K was not yet in the SEC data; MU is valued on normalized figures anyway.
- **Yahoo Finance:** closing prices.
- **[Bigdata.com](https://bigdata.com):** **out of credits** for this run. No Bigdata.com data was used. Cited facts come from web search of company releases and news, and the links are given inline.
- **Forward revenue growth** (current FY consensus vs the last reported FY) now feeds the Growth score. DCF growth rates remain analyst assumptions, anchored to consensus revenue and EPS.

**Conventions.** Same as the NYSE thematic screen in this repository (`reports/nyse_disruptive_tech_screen_2026-10-08.md`):
- **FY** = reported fiscal year, GAAP. **NTM** = time-weighted consensus.
- **"Latest YTD y/y"** = the latest 10-Q year-to-date revenue versus the same period a year earlier.
- **N/A** = not available. **N/M** = not meaningful.
- **No missing figure was estimated.** Analyst judgments (scores, TAM sizes, fair multiples, scenario growth and margins, discount rates) are labelled as such.

> **Not investment advice.** Fair values are model outputs driven by the analyst's stated assumptions.

---

## 0. Headline findings

1. **Two Nasdaq-100 stocks pass the strict "most important filter": Alnylam (ALNY) and MercadoLibre (MELI).** The filter requires revenue CAGR >15%, EPS/FCF growth >15%, a strong moat, a large TAM, upside >20%, positive FCF and a clean balance sheet. **NVIDIA (NVDA) misses by a hair**: 18% upside vs the 20% bar.
   - **ALNY:** RNAi leader, newly profitable. Base FV $384 (42% margin of safety) after its decline on a guidance cut.
   - **MELI:** ~39% revenue CAGR and consensus revenue +45% for FY26. Base FV $2,326 (19% margin of safety).
   - **NVDA:** ~17x NTM EPS with consensus revenue +91% for FY Jan-27. Base FV $279 (15% margin of safety).
2. **No ★★★★★.** The ★★★★☆ group is **NVDA, ALNY and MELI**.
3. **The Nasdaq-100 is far richer in disruptive-tech exposure than the NYSE**, but also far more expensive.
   - **Of 45 modelled companies, 35 trade above the model's base value.**
   - The most extreme are TSLA (~300x NTM EPS), PLTR (~111x), ARM (~185x), ALAB (~90x), DDOG and the AI-optical names (LITE, MRVL, AMD).
4. **AI:** the best risk/reward is in the platform leaders that look *cheapest on earnings*: **NVDA, META, MSFT** (and GOOGL on its earnings legs).
   - The AI hardware second tier (ALAB, LITE, MRVL, STX, AMD, ARM) prices in years of hyper-growth.
   - **Semicap (ASML, AMAT, LRCX, KLAC)** trades 30–50% above model value after the 2026 rally.
5. **Robotics:** **ISRG** is the purest quality play but expensive (42x). **TSLA** has the highest Disruption score (robotaxi, Optimus, Megapack) but the weakest valuation. **NVDA and GOOGL** (Waymo) are the robotics exposures worth owning at current prices.
6. **Energy storage:** only TSLA (Megapack: **13.5 GWh deployed in Q2 2026** ([pv magazine](https://pv-magazine-usa.com/2026/07/02/tesla-announces-13-5-gwh-energy-storage-deployments-in-q2-sets-july-earnings-date/))) has major exposure. Battery-management chip makers (ADI, NXPI, MPWR) are secondary. **No attractive pure play** exists in the Nasdaq-100.
7. **Blockchain:**
   - **Coinbase and Robinhood are *not* Nasdaq-100 constituents** (verified against the Oct 8, 2026 constituent list).
   - **Strategy (MSTR)** is a leveraged bitcoin treasury, assessed qualitatively in §12.
   - The investable exposure is **PYPL (PYUSD stablecoin)**, which is cheap (9.6x) but low-growth, plus small optionality in MELI and SHOP.
8. **Multiomics / genetic medicine:** **ALNY** is the standout. **REGN** (14x, genetics database) is fair-to-cheap but low growth. VRTX, AMGN and GILD do not meet the growth bar. Illumina is **not** in the index.

---

## 1. Method and coverage

**Universe and coverage.**
- **47 constituents** were mapped to the five themes and pulled.
- **45 were modelled.** Two were not:
  - **MSTR** is a bitcoin treasury company, valued on its holdings (mNAV), not cash flows.
  - **HON** recently separated its businesses, so the current share price and the historical financials describe different companies.
- The remaining **53 constituents** have no meaningful thematic exposure (e.g., COST, PEP, CSX, MAR) or only marginal exposure (e.g., ADBE, INTU, WDAY, TXN, CSCO). They were not modelled.

**Method.** Identical to the NYSE thematic screen.
- **Fair value = 40% scenario DCF + 25% earnings + 20% FCF + 15% historical/peer**, with bear, base and bull cases.
- **SBC adjustment:** when SBC exceeds 5% of revenue, it is deducted from FCF.
- **Early-stage companies:** 40% DCF plus 60% EV/NTM-sales.
- **Cyclical names:** MU uses normalized EPS (~$80, versus ~$176 FY27 peak consensus) and mid-cycle revenue.
- **MELI:** net income stands in for FCF because its credit book distorts cash flow.
- **ASML:** EUR financials converted at 1.17 USD/EUR (an analyst assumption).
- **Scores:** same definitions and weights as the NYSE screen: Growth, Quality, Financial strength, Valuation, Disruption (/100), and Overall (/100: Growth 20, Quality 15, ROIC 10, Financial strength 10, Valuation 20, Competitive advantage 10, TAM & technology 10, Risk 5). The star rules are also the same.

**Known limitations.**
- **The DCF starts from the last fiscal year's revenue.** This understates the base for hyper-growers whose year-to-date growth is far above the last full year: NVDA +96%, CRWV +112%, ALAB +99%, PLTR +89%, ALNY +80%, LITE +83% (FY), TER +95%.
- **SEC-data quirks:**
  - Pre-split years are excluded from EPS CAGRs (NVDA, AVGO, LRCX, KLAC).
  - NBIS's pre-2022 history (Yandex) is excluded.
  - KLAC's operating income was derived as pretax income plus interest.
- **The model is structurally conservative** on capex-heavy AI hyperscalers and SBC-heavy software. Their earnings-based legs are shown separately so the gap is visible.

---

## A. Final ranked table (all 45 modelled companies; the top 20 are the "Top 20 overall opportunities")

Rev/EPS/FCF CAGR = 3-year to the latest FY, GAAP. ROIC = latest FY (calculated). Debt/EBITDA on a net-debt basis.

| Rank | Ticker | Company | Theme | Secondary | Mkt Cap ($B) | Rev CAGR 3y | EPS CAGR 3y | FCF CAGR 3y | ROIC | Debt/EBITDA (net) | Price | Base FV | Upside | MoS | Growth | Quality | Disruption | Valuation | Overall | Risk | Rating |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | NVDA | NVIDIA | AI | Robotics | 5,723 | 100% | 207% | 194% | 66% | net cash | $237 | $279 | 18% | 15% | 100 | 92 | 88 | 75 | 89 | Med–High | ★★★★☆ |
| 2 | APP | Applovin | AI | — | 94 | 25% | N/A | 114% | 104% | 0.2x | $281 | $352 | 25% | 20% | 100 | 89 | 59 | 80 | 83 | Very high | ★★☆☆☆ |
| 3 | META | Meta Platforms | AI | Robotics | 1,838 | 20% | 40% | 34% | 34% | net cash | $721 | $661 | -8% | -9% | 95 | 90 | 73 | 48 | 81 | Medium | ★★★☆☆ |
| 4 | ASML | ASML | AI | — | 696 | 16% | 20% | 15% | 84% | net cash | $1,805 | $1,277 | -29% | -41% | 81 | 87 | 72 | 40 | 78 | Medium | ★★☆☆☆ |
| 5 | MSFT | Microsoft | AI | Robotics | 3,934 | 16% | 23% | 4% | 30% | net cash | $530 | $512 | -3% | -3% | 62 | 89 | 81 | 51 | 76 | Low | ★★★☆☆ |
| 6 | MELI | MercadoLibre | Blockchain | AI | 95 | 39% | 60% | 61% | 26% | 0.7x | $1,873 | $2,326 | 24% | 19% | 100 | 51 | 57 | 79 | 76 | Med–High | ★★★★☆ |
| 7 | ALNY | Alnylam Pharmaceuticals | Multiomics | — | 30 | 53% | N/A | N/A | N/A | net cash | $224 | $384 | 71% | 42% | 100 | 47 | 68 | 100 | 71 | Med–High | ★★★★☆ |
| 8 | GOOGL | Alphabet | AI | Robotics | 4,287 | 13% | 33% | 7% | 30% | net cash | $350 | $274 | -22% | -28% | 65 | 77 | 86 | 37 | 71 | Medium | ★★☆☆☆ |
| 9 | PLTR | Palantir | AI | Robotics | 466 | 33% | N/A | 125% | >200% | net cash | $194 | $76.99 | -60% | -152% | 100 | 91 | 77 | 5 | 70 | High | ★★☆☆☆ |
| 10 | STX | Seagate Technology PLC ( | AI | — | 185 | 18% | N/A | 71% | 80% | 0.4x | $808 | $378 | -53% | -114% | 86 | 73 | 51 | 40 | 68 | High | ★★☆☆☆ |
| 11 | KLAC | KLA | AI | — | 257 | 9% | N/A | 4% | 44% | 0.7x | $197 | $106 | -46% | -86% | 55 | 90 | 61 | 29 | 68 | Medium | ★★☆☆☆ |
| 12 | AVGO | Broadcom | AI | — | 1,797 | 24% | 22% | 18% | 15% | 1.5x | $377 | $301 | -20% | -25% | 97 | 76 | 75 | 40 | 67 | Medium | ★★☆☆☆ |
| 13 | LRCX | Lam Research | AI | — | 412 | 10% | 20% | 2% | 61% | net cash | $330 | $163 | -50% | -102% | 51 | 78 | 61 | 29 | 66 | Medium | ★★☆☆☆ |
| 14 | ALAB | Astera Labs | AI | — | 66 | 120% | N/A | N/A | 78% | net cash | $382 | $145 | -62% | -164% | 100 | 78 | 67 | 5 | 65 | High | ★★☆☆☆ |
| 15 | AMAT | Applied Materials | AI | — | 413 | 3% | 5% | 7% | 36% | net cash | $521 | $290 | -44% | -80% | 28 | 74 | 61 | 40 | 63 | Medium | ★★☆☆☆ |
| 16 | QCOM | QUALCOMMorporated | AI | Robotics | 186 | 0% | -24% | 23% | 38% | 0.3x | $177 | $152 | -14% | -16% | 38 | 80 | 56 | 44 | 63 | Medium | ★★☆☆☆ |
| 17 | ISRG | Intuitive Surgical | Robotics | AI | 146 | 17% | 29% | 37% | 20% | net cash | $415 | $318 | -23% | -30% | 81 | 75 | 78 | 0 | 63 | Low | ★★☆☆☆ |
| 18 | SHOP | Shopify | AI | Blockchain | 215 | 27% | N/A | N/A | 15% | net cash | $166 | $96.01 | -42% | -73% | 100 | 51 | 63 | 11 | 61 | Med–High | ★★☆☆☆ |
| 19 | CDNS | Cadence Design Systems | AI | — | 98 | 14% | 10% | 12% | 51% | net cash | $356 | $237 | -33% | -50% | 45 | 78 | 62 | 3 | 60 | Low | ★★☆☆☆ |
| 20 | AMZN | Amazon.com | AI | Robotics | 2,803 | 12% | N/A | N/A | 18% | net cash | $260 | $201 | -23% | -30% | 66 | 37 | 82 | 40 | 60 | Medium | ★★☆☆☆ |
| 21 | PYPL | PayPal | Blockchain | AI | 47 | 6% | 37% | 3% | 23% | 0.1x | $54.95 | $84.79 | 54% | 35% | 29 | 47 | 52 | 90 | 59 | Med–High | ★★☆☆☆ |
| 22 | MPWR | Monolithic Power Systems | AI | Energy Storage | 70 | 16% | 12% | 53% | 25% | net cash | $1,426 | $823 | -42% | -73% | 78 | 66 | 68 | 2 | 59 | Med–High | ★★☆☆☆ |
| 23 | AMD | Advanced Micro Devices | AI | Robotics | 1,054 | 14% | 47% | 29% | 5% | net cash | $646 | $250 | -61% | -159% | 92 | 38 | 71 | 40 | 58 | Med–High | ★★☆☆☆ |
| 24 | LITE | Lumentum | AI | — | 101 | 19% | N/A | 80% | 12% | net cash | $1,111 | $419 | -62% | -165% | 92 | 37 | 64 | 40 | 58 | High | ★★☆☆☆ |
| 25 | CRWV | CoreWeave | AI | Blockchain | 49 | 373% | N/A | N/A | -0% | 7.6x | $88.45 | $156 | 77% | 43% | 100 | 26 | 68 | 100 | 57 | Very high | ★☆☆☆☆ |
| 26 | CRWD | CrowdStrike | AI | — | 272 | 29% | N/A | 22% | N/A | N/A | $265 | $292 | 10% | 9% | 100 | 49 | 64 | 29 | 57 | Med–High | ★★☆☆☆ |
| 27 | ARM | Arm | AI | Robotics | 313 | 22% | 19% | 13% | 15% | net cash | $294 | $73.15 | -75% | -302% | 83 | 64 | 77 | 0 | 57 | Med–High | ★★☆☆☆ |
| 28 | VRTX | Vertex Pharmaceuticalsor | Multiomics | — | 128 | 10% | 6% | -7% | 27% | net cash | $506 | $400 | -21% | -26% | 20 | 86 | 61 | 0 | 53 | Medium | ★★☆☆☆ |
| 29 | AXON | Axon Enterprise | Robotics | AI | 33 | 33% | -9% | -25% | -1% | 4.9x | $406 | $483 | 19% | 16% | 68 | 32 | 65 | 74 | 52 | Med–High | ★★★☆☆ |
| 30 | REGN | Regeneron Pharmaceutical | Multiomics | AI | 76 | 6% | 3% | -3% | 11% | net cash | $742 | $833 | 12% | 11% | 18 | 50 | 67 | 56 | 52 | Medium | ★★★☆☆ |
| 31 | CEG | Constellation Energy | AI | Energy Storage | 106 | 1% | N/A | N/A | 13% | 0.7x | $300 | $220 | -26% | -36% | 56 | 35 | 60 | 33 | 51 | Medium | ★★☆☆☆ |
| 32 | MRVL | Marvell Technology | AI | — | 250 | 11% | N/A | 9% | 6% | 0.7x | $285 | $93.22 | -67% | -205% | 72 | 40 | 62 | 40 | 51 | Med–High | ★★☆☆☆ |
| 33 | TER | Teradyne | Robotics | AI | 64 | 0% | -6% | 3% | 19% | net cash | $412 | $171 | -59% | -141% | 25 | 54 | 68 | 34 | 50 | Med–High | ★★☆☆☆ |
| 34 | DDOG | Datadog | AI | — | 97 | 27% | N/A | 37% | N/A | net cash | $271 | $98.30 | -64% | -176% | 100 | 48 | 61 | 0 | 50 | Med–High | ★★☆☆☆ |
| 35 | ADI | Analog Devices | Robotics | Energy Storage | 199 | -3% | -5% | 4% | 6% | 0.9x | $410 | $288 | -30% | -42% | 30 | 58 | 64 | 34 | 48 | Medium | ★★☆☆☆ |
| 36 | PANW | Palo Alto Networks | AI | — | 332 | 19% | -15% | 16% | 2% | net cash | $406 | $148 | -63% | -173% | 66 | 53 | 62 | 0 | 46 | Medium | ★★☆☆☆ |
| 37 | NXPI | NXP Semiconductors | Robotics | Energy Storage | 59 | -2% | -9% | -5% | 14% | 2.0x | $235 | $205 | -13% | -15% | 17 | 54 | 59 | 45 | 46 | Medium | ★★☆☆☆ |
| 38 | SNPS | Synopsys | AI | — | 96 | 15% | 9% | -6% | 2% | 6.7x | $503 | $329 | -35% | -53% | 51 | 54 | 61 | 30 | 45 | Medium | ★★☆☆☆ |
| 39 | GEHC | GE HealthCare | Multiomics | AI | 29 | 4% | 3% | -6% | 14% | 1.6x | $64.67 | $71.02 | 10% | 9% | 3 | 40 | 57 | 64 | 44 | Medium | ★★☆☆☆ |
| 40 | GILD | Gilead Sciences | Multiomics | — | 182 | 3% | 23% | 4% | 20% | 1.4x | $147 | $125 | -15% | -17% | 21 | 77 | 44 | 3 | 44 | Medium | ★★☆☆☆ |
| 41 | NBIS | Nebius Group | AI | — | 64 | 240% | N/A | N/A | -10% | N/A | $237 | $221 | -7% | -7% | 100 | 24 | 65 | 21 | 43 | Very high | ★☆☆☆☆ |
| 42 | RKLB | Rocket Lab | Robotics | — | 45 | 42% | N/A | N/A | -21% | N/A | $71.92 | $20.76 | -71% | -246% | 100 | 17 | 57 | 0 | 41 | Very high | ★☆☆☆☆ |
| 43 | MU | Micron Technology | AI | — | 1,229 | 7% | -1% | -19% | 14% | 0.1x | $1,088 | $591 | -46% | -84% | 15 | 39 | 64 | 0 | 38 | High | ★★☆☆☆ |
| 44 | TSLA | Tesla | Robotics | Energy Storage | 1,492 | 5% | -33% | -6% | 8% | net cash | $378 | $90.13 | -76% | -319% | 28 | 22 | 88 | 0 | 34 | Very high | ★★☆☆☆ |
| 45 | AMGN | Amgen | Multiomics | — | 223 | 12% | 6% | -3% | 13% | 3.2x | $413 | $277 | -33% | -49% | 12 | 60 | 55 | 0 | 34 | Medium | ★★☆☆☆ |

### A.1 Growth, margins and balance-sheet detail

| Ticker | Rev 3y | Rev 5y | Latest FY YoY | Latest YTD y/y (10-Q) | EPS 3y | EPS 5y | Fwd EPS growth | FCF 3y | FCF 5y | FCF margin | Gross m. | Op. m. | Net m. | ROE | ROA | SBC % rev | Shares Δ3y | Int. cover | Current ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NVDA | 100% | 67% | 65% | 96% | 207% | N/A | 53% | 194% | 75% | 45% | 71% | 60% | 56% | 76% | 58% | 3% | -2% | 503x | 3.9 |
| APP | 25% | 30% | 70% | 56% | N/A | N/A | 26% | 114% | 78% | 72% | 88% | 76% | 61% | 156% | 46% | 4% | -8% | 21x | 3.3 |
| META | 20% | 19% | 22% | 30% | 40% | 18% | 19% | 34% | 14% | 23% | 82% | 41% | 30% | 28% | 17% | 10% | -5% | 71x | 2.6 |
| ASML | 16% | 19% | 16% | N/A | 20% | 24% | 35% | 15% | 25% | 34% | 53% | 35% | 29% | 49% | 19% | 1% | -2% | 96x | 1.3 |
| MSFT | 16% | 15% | 18% | N/A | 23% | 17% | 20% | 4% | 4% | 20% | 68% | 47% | 40% | 30% | 18% | 4% | -0% | 51x | 1.2 |
| MELI | 39% | N/A | 39% | 49% | 60% | N/A | 42% | 61% | N/A | 7% | 45% | 11% | 7% | 30% | 5% | 0% | -1% | 5x | 1.2 |
| ALNY | 53% | 50% | 65% | 80% | N/A | N/A | 34% | N/A | N/A | 13% | 82% | 14% | 8% | 40% | 6% | 9% | 11% | 2x | 2.8 |
| GOOGL | 13% | 17% | 15% | 23% | 33% | 30% | 20% | 7% | 11% | 18% | 60% | 32% | 33% | 32% | 22% | 6% | -7% | 175x | 2.0 |
| PLTR | 33% | 33% | 56% | 89% | N/A | N/A | 40% | 125% | N/A | 47% | 82% | 32% | 36% | 22% | 18% | 15% | 24% | 407x | 7.1 |
| STX | 18% | 3% | 34% | N/A | N/A | 21% | 69% | 71% | 22% | 25% | 46% | 34% | 26% | 147% | 32% | 2% | 11% | 14x | 1.7 |
| KLAC | 9% | 14% | 12% | N/A | N/A | N/A | 21% | 4% | 14% | 28% | 61% | 43% | 36% | 76% | 27% | 2% | 841% | 21x | 2.9 |
| AVGO | 24% | 22% | 24% | 55% | 22% | N/A | 65% | 18% | 18% | 42% | 68% | 40% | 36% | 28% | 14% | 12% | 15% | 8x | 1.7 |
| LRCX | 10% | 10% | 26% | N/A | 20% | N/A | 21% | 2% | 9% | 21% | 50% | 35% | 31% | 58% | 31% | 2% | -7% | 52x | 2.6 |
| ALAB | 120% | N/A | 115% | 99% | N/A | N/A | 33% | N/A | N/A | 33% | 76% | 20% | 26% | 16% | 14% | 19% | 425% | N/M | 10.2 |
| AMAT | 3% | 11% | 4% | 11% | 5% | 17% | 36% | 7% | 11% | 20% | 49% | 29% | 25% | 34% | 19% | 2% | -8% | 31x | 2.6 |
| QCOM | 0% | 13% | 14% | -1% | -24% | 2% | 31% | 23% | 24% | 29% | 55% | 28% | 13% | 26% | 11% | 6% | -3% | 19x | 2.8 |
| ISRG | 17% | 18% | 21% | 21% | 29% | 22% | 11% | 37% | 17% | 25% | 66% | 29% | 28% | 16% | 14% | 8% | 0% | N/M | 4.9 |
| SHOP | 27% | 32% | 30% | 34% | N/A | N/A | 38% | N/A | 39% | 17% | 48% | 13% | 11% | 9% | 8% | 4% | 3% | 1468x | 6.0 |
| CDNS | 14% | N/A | 14% | 19% | 10% | N/A | 17% | 12% | N/A | 30% | N/A | 28% | 21% | 20% | 11% | 9% | -1% | 13x | 2.9 |
| AMZN | 12% | 13% | 12% | 18% | N/A | 28% | 31% | N/A | -22% | 1% | 1% | 11% | 11% | 19% | 9% | 3% | 6% | 35x | 1.1 |
| PYPL | 6% | 9% | 4% | 7% | 37% | 9% | 8% | 3% | 1% | 17% | N/A | 18% | 16% | 26% | 7% | 3% | -16% | 14x | 1.3 |
| MPWR | 16% | 27% | 26% | 37% | 12% | 30% | 17% | 53% | 26% | 24% | 55% | 26% | 22% | 18% | 15% | 8% | -0% | N/M | 5.9 |
| AMD | 14% | 29% | 34% | 44% | 47% | 5% | 79% | 29% | 54% | 19% | 50% | 11% | 13% | 7% | 6% | 5% | 4% | 28x | 2.9 |
| LITE | 19% | 12% | 83% | N/A | N/A | N/A | 54% | 80% | -14% | 10% | 42% | 17% | -230% | -149% | -95% | 6% | 9% | 24x | 1.7 |
| CRWV | 373% | N/A | 168% | 112% | N/A | N/A | N/A | N/A | N/A | -141% | 72% | -1% | -23% | -35% | -2% | 12% | N/A | N/M | 0.5 |
| CRWD | 29% | 41% | 22% | 26% | N/A | N/A | N/A | 22% | 33% | 26% | 75% | -6% | -3% | -4% | -1% | 23% | 7% | N/M | 1.8 |
| ARM | 22% | N/A | 23% | 22% | 19% | N/A | 54% | 13% | N/A | 20% | 98% | 18% | 18% | 11% | 8% | 21% | 4% | N/M | 6.0 |
| VRTX | 10% | 14% | 9% | 10% | 6% | 8% | 8% | -7% | 1% | 27% | 86% | 35% | 33% | 21% | 15% | 6% | -0% | 314x | 2.9 |
| AXON | 33% | 32% | 33% | 35% | -9% | N/A | 85% | -25% | N/A | 3% | 60% | -2% | 4% | 4% | 2% | 23% | 14% | N/M | 2.5 |
| REGN | 6% | 11% | 1% | 18% | 3% | 6% | 8% | -3% | 15% | 28% | N/A | 25% | 31% | 14% | 11% | 7% | -4% | 82x | 4.1 |
| CEG | 1% | 8% | 8% | 45% | N/A | N/A | 17% | N/A | N/A | 5% | N/A | 12% | 9% | 16% | 4% | 2% | -5% | 6x | 1.5 |
| MRVL | 11% | 23% | 42% | 32% | N/A | N/A | 70% | 9% | 14% | 17% | 51% | 16% | 33% | 19% | 12% | 7% | 2% | 7x | 2.0 |
| TER | 0% | 0% | 13% | 95% | -6% | -4% | 29% | 3% | -8% | 14% | 58% | 20% | 17% | 20% | 13% | 2% | -6% | 95x | 1.7 |
| DDOG | 27% | 42% | 28% | 34% | N/A | N/A | 47% | 37% | 62% | 27% | 80% | -1% | 3% | 3% | 2% | 22% | 15% | N/M | 3.4 |
| ADI | -3% | 14% | 17% | 36% | -5% | 7% | 20% | 4% | 18% | 39% | 61% | 27% | 21% | 7% | 5% | 3% | -5% | 9x | 2.2 |
| PANW | 19% | 22% | 24% | N/A | -15% | N/A | 22% | 16% | 24% | 36% | 70% | 6% | 3% | 1% | 1% | 15% | 12% | N/M | 0.9 |
| NXPI | -2% | 7% | -3% | 12% | -9% | 113% | 20% | -5% | 3% | 20% | 55% | 25% | 16% | 20% | 8% | 4% | -4% | 7x | 2.0 |
| SNPS | 15% | 14% | 15% | 49% | 9% | 13% | 24% | -6% | 10% | 19% | 77% | 13% | 19% | 5% | 3% | 13% | 6% | 2x | 1.6 |
| GEHC | 4% | N/A | 5% | 7% | 3% | N/A | 10% | -6% | N/A | 7% | 40% | 13% | 10% | 20% | 6% | 1% | 1% | 5x | 1.4 |
| GILD | 3% | 4% | 2% | 7% | 23% | 132% | 3% | 4% | 5% | 32% | 79% | 34% | 29% | 37% | 14% | 3% | -1% | 10x | 1.6 |
| NBIS | 240% | N/A | 479% | N/A | N/A | N/A | N/A | N/A | N/A | -695% | 69% | -115% | 16% | 2% | 1% | 16% | -33% | N/M | 3.1 |
| RKLB | 42% | 76% | 38% | 63% | N/A | N/A | N/A | N/A | N/A | -53% | 34% | -38% | -33% | -12% | -9% | 12% | 14% | N/M | 4.1 |
| MU | 7% | 12% | 49% | 203% | -1% | 26% | 2% | -19% | 82% | 4% | 40% | 26% | 23% | 16% | 10% | 3% | 0% | 20x | 2.5 |
| TSLA | 5% | 25% | -3% | 21% | -33% | 39% | 20% | -6% | 17% | 7% | 18% | 5% | 4% | 5% | 3% | 3% | 2% | 13x | 2.2 |
| AMGN | 12% | 8% | 10% | 8% | 6% | 3% | 5% | -3% | -4% | 22% | 67% | 25% | 21% | 89% | 9% | 1% | 0% | 3x | 1.1 |

### A.2 Financial strength and cash runway

| Ticker | Profile | Cash & ST inv. ($M) | Net debt ($M) | Net debt/EBITDA | Interest cover | Current ratio | FCF per share (latest FY, USD) | Cash runway | SBC % rev | Share count Δ 3y |
|---|---|---|---|---|---|---|---|---|---|---|
| NVDA | Profitable growth | 10,605 | -2,137 | net cash | 503x | 3.9 | 3.94/sh | N/A (FCF positive) | 3% | -2% |
| APP | Profitable growth | 2,487 | 1,026 | 0.2x | 21x | 3.3 | 11.61/sh | N/A (FCF positive) | 4% | -8% |
| META | Profitable growth | 81,592 | -22,848 | net cash | 71x | 2.6 | 17.91/sh | N/A (FCF positive) | 10% | -5% |
| ASML | Profitable growth | 15,587 | -10,449 | net cash | 96x | 1.3 | 33.35/sh | N/A (FCF positive) | 1% | -2% |
| MSFT | Profitable growth | 76,843 | -36,549 | net cash | 51x | 1.2 | 8.99/sh | N/A (FCF positive) | 4% | -0% |
| MELI | Profitable growth | 6,299 | 2,894 | 0.7x | 5x | 1.2 | 39.39/sh | N/A (FCF positive) | 0% | -1% |
| ALNY | Profitable growth | 2,908 | -2,908 | net cash | 2x | 2.8 | 3.46/sh | N/A (FCF positive) | 9% | 11% |
| GOOGL | Profitable growth | 126,843 | -77,758 | net cash | 175x | 2.0 | 5.99/sh | N/A (FCF positive) | 6% | -7% |
| PLTR | Profitable growth | 7,177 | -7,177 | net cash | 407x | 7.1 | 0.82/sh | N/A (FCF positive) | 15% | 24% |
| STX | Profitable growth | 1,704 | 1,899 | 0.4x | 14x | 1.7 | 13.56/sh | N/A (FCF positive) | 2% | 11% |
| KLAC | Profitable growth | 1,650 | 4,238 | 0.7x | 21x | 2.9 | 2.85/sh | N/A (FCF positive) | 2% | 841% |
| AVGO | Profitable growth | 16,178 | 50,942 | 1.5x | 8x | 1.7 | 5.55/sh | N/A (FCF positive) | 12% | 15% |
| LRCX | Profitable growth | 5,579 | -1,857 | net cash | 52x | 2.6 | 3.88/sh | N/A (FCF positive) | 2% | -7% |
| ALAB | Profitable growth | 1,189 | -1,189 | net cash | N/M | 10.2 | 1.57/sh | N/A (FCF positive) | 19% | 425% |
| AMAT | Profitable growth | 8,573 | -2,118 | net cash | 31x | 2.6 | 7.05/sh | N/A (FCF positive) | 2% | -8% |
| QCOM | Profitable growth | 10,155 | 4,656 | 0.3x | 19x | 2.8 | 11.60/sh | N/A (FCF positive) | 6% | -3% |
| ISRG | Profitable growth | 5,935 | -5,935 | net cash | N/M | 4.9 | 6.87/sh | N/A (FCF positive) | 8% | 0% |
| SHOP | Profitable growth | 5,778 | -5,778 | net cash | 1468x | 6.0 | 1.54/sh | N/A (FCF positive) | 4% | 3% |
| CDNS | Profitable growth | 3,156 | -3,156 | net cash | 13x | 2.9 | 5.81/sh | N/A (FCF positive) | 9% | -1% |
| AMZN | Profitable growth | 123,029 | -54,193 | net cash | 35x | 1.1 | 0.71/sh | N/A (FCF positive) | 3% | 6% |
| PYPL | Profitable growth | 10,422 | 1,037 | 0.1x | 14x | 1.3 | 5.75/sh | N/A (FCF positive) | 3% | -16% |
| MPWR | Profitable growth | 1,257 | -1,257 | net cash | N/M | 5.9 | 13.79/sh | N/A (FCF positive) | 8% | -0% |
| AMD | Profitable growth | 10,552 | -7,330 | net cash | 28x | 2.9 | 4.12/sh | N/A (FCF positive) | 5% | 4% |
| LITE | Profitable growth | 2,738 | -1,101 | net cash | 24x | 1.7 | 4.02/sh | N/A (FCF positive) | 6% | 9% |
| CRWV | Early-stage (GAAP loss) | 3,161 | 18,212 | 7.6x | N/M | 0.5 | -16.63/sh | 0.4 yrs | 12% | N/A |
| CRWD | Early-stage (GAAP loss) | 5,230 | -4,485 | net cash | N/M | 1.8 | 4.95/sh | N/A (FCF positive) | 23% | 7% |
| ARM | Profitable growth | 3,601 | -3,601 | net cash | N/M | 6.0 | 0.92/sh | N/A (FCF positive) | 21% | 4% |
| VRTX | Profitable growth | 6,608 | -6,608 | net cash | 314x | 2.9 | 12.38/sh | N/A (FCF positive) | 6% | -0% |
| AXON | Early-stage (GAAP loss) | 1,707 | 104 | 4.9x | N/M | 2.5 | 0.91/sh | N/A (FCF positive) | 23% | 14% |
| REGN | Profitable growth | 8,605 | -6,619 | net cash | 82x | 4.1 | 37.57/sh | N/A (FCF positive) | 7% | -4% |
| CEG | Profitable growth | 3,641 | 3,762 | 0.7x | 6x | 1.5 | 4.10/sh | N/A (FCF positive) | 2% | -5% |
| MRVL | Profitable growth | 2,639 | 1,832 | 0.7x | 7x | 2.0 | 1.61/sh | N/A (FCF positive) | 7% | 2% |
| TER | Profitable growth | 294 | -94 | net cash | 95x | 1.7 | 2.82/sh | N/A (FCF positive) | 2% | -6% |
| DDOG | Profitable growth | 4,475 | -4,475 | net cash | N/M | 3.4 | 2.52/sh | N/A (FCF positive) | 22% | 15% |
| ADI | Profitable growth | 3,652 | 4,565 | 0.9x | 9x | 2.2 | 8.61/sh | N/A (FCF positive) | 3% | -5% |
| PANW | Profitable growth | 3,071 | -3,071 | net cash | N/M | 0.9 | 5.38/sh | N/A (FCF positive) | 15% | 12% |
| NXPI | Profitable growth | 3,267 | 7,773 | 2.0x | 7x | 2.0 | 9.53/sh | N/A (FCF positive) | 4% | -4% |
| SNPS | Profitable growth | 2,961 | 10,524 | 6.7x | 2x | 1.6 | 8.14/sh | N/A (FCF positive) | 13% | 6% |
| GEHC | Profitable growth | 4,492 | 5,511 | 1.6x | 5x | 1.4 | 3.29/sh | N/A (FCF positive) | 1% | 1% |
| GILD | Profitable growth | 7,632 | 17,305 | 1.4x | 10x | 1.6 | 7.53/sh | N/A (FCF positive) | 3% | -1% |
| NBIS | Early-stage (GAAP loss) | 3,678 | 425 | N/A | N/M | 3.1 | -14.86/sh | 1.0 yrs | 16% | -33% |
| RKLB | Early-stage (GAAP loss) | 1,017 | -864 | net cash | N/M | 4.1 | -0.61/sh | 3.2 yrs | 12% | 14% |
| MU | Profitable growth | 10,307 | 1,226 | 0.1x | 20x | 2.5 | 1.48/sh | N/A (FCF positive) | 3% | 0% |
| TSLA | Profitable growth | 44,059 | -37,475 | net cash | 13x | 2.2 | 1.76/sh | N/A (FCF positive) | 3% | 2% |
| AMGN | Profitable growth | 9,129 | 45,475 | 3.2x | 3x | 1.1 | 14.94/sh | N/A (FCF positive) | 1% | 0% |

---

## B–F. Top 5 by theme

Ranked by Overall score among companies with a theme score of at least 5/10 (4/10 for blockchain).

### AI (35 eligible)
| # | Ticker | Theme score | Exposure / Growth pot. / Comp. pos. | Overall | Disruption | MoS | Rating |
|---|---|---|---|---|---|---|---|
| 1 | NVDA | 10/10 | 10/9/10 | 89 | 88 | 15% | ★★★★☆ |
| 2 | APP | 8/10 | 8/8/6 | 83 | 59 | 20% | ★★☆☆☆ |
| 3 | META | 9/10 | 8/9/8 | 81 | 73 | -9% | ★★★☆☆ |
| 4 | ASML | 9/10 | 8/8/10 | 78 | 72 | -41% | ★★☆☆☆ |
| 5 | MSFT | 10/10 | 9/9/10 | 76 | 81 | -3% | ★★★☆☆ |

### Robotics (12 eligible)
| # | Ticker | Theme score | Exposure / Growth pot. / Comp. pos. | Overall | Disruption | MoS | Rating |
|---|---|---|---|---|---|---|---|
| 1 | NVDA | 6/10 | 10/9/10 | 89 | 88 | 15% | ★★★★☆ |
| 2 | GOOGL | 6/10 | 9/9/9 | 71 | 86 | -28% | ★★☆☆☆ |
| 3 | QCOM | 5/10 | 5/6/6 | 63 | 56 | -16% | ★★☆☆☆ |
| 4 | ISRG | 10/10 | 10/8/10 | 63 | 78 | -30% | ★★☆☆☆ |
| 5 | AMZN | 7/10 | 8/9/9 | 60 | 82 | -30% | ★★☆☆☆ |

### Energy Storage (3 eligible)
| # | Ticker | Theme score | Exposure / Growth pot. / Comp. pos. | Overall | Disruption | MoS | Rating |
|---|---|---|---|---|---|---|---|
| 1 | ADI | 5/10 | 6/7/8 | 48 | 64 | -42% | ★★☆☆☆ |
| 2 | NXPI | 5/10 | 5/6/6 | 46 | 59 | -15% | ★★☆☆☆ |
| 3 | TSLA | 8/10 | 8/9/7 | 34 | 88 | -319% | ★★☆☆☆ |

### Blockchain (3 eligible)
| # | Ticker | Theme score | Exposure / Growth pot. / Comp. pos. | Overall | Disruption | MoS | Rating |
|---|---|---|---|---|---|---|---|
| 1 | MELI | 4/10 | 3/6/8 | 76 | 57 | 19% | ★★★★☆ |
| 2 | SHOP | 4/10 | 5/7/8 | 61 | 63 | -73% | ★★☆☆☆ |
| 3 | PYPL | 6/10 | 4/5/5 | 59 | 52 | 35% | ★★☆☆☆ |

### Multiomics (5 eligible)
| # | Ticker | Theme score | Exposure / Growth pot. / Comp. pos. | Overall | Disruption | MoS | Rating |
|---|---|---|---|---|---|---|---|
| 1 | ALNY | 8/10 | 8/8/8 | 71 | 68 | 42% | ★★★★☆ |
| 2 | VRTX | 7/10 | 5/7/8 | 53 | 61 | -26% | ★★☆☆☆ |
| 3 | REGN | 8/10 | 5/7/7 | 52 | 67 | 11% | ★★★☆☆ |
| 4 | GEHC | 5/10 | 5/6/6 | 44 | 57 | 9% | ★★☆☆☆ |
| 5 | AMGN | 6/10 | 3/5/6 | 34 | 55 | -49% | ★★☆☆☆ |



**Commentary.**
- **AI:** NVDA is the clear pick. META and MSFT are fair-value compounders. APP scores high, but its legal red flags cap it at ★★. ASML is the best business at the wrong price.
- **Robotics:**
  - NVDA (Isaac/Omniverse, Jetson) and GOOGL (Waymo) give robotics exposure at reasonable earnings multiples.
  - ISRG (42x) and TSLA (~300x) are the purest exposures but expensive.
  - TER (Universal Robots) is an AI-chip-test cycle story first.
- **Energy storage:** only three names qualify. None is attractive.
  - TSLA's energy gross margin reportedly fell to ~20% in Q2 2026 ([Longbridge transcript summary](https://longbridge.com/news/294985240); verify against Tesla's update).
- **Blockchain:**
  - **MSTR is excluded** from the quantitative screen.
  - PYPL is the only cheap name, but it is not a growth stock.
  - MELI's crypto/stablecoin exposure is minor relative to its core business.
- **Multiomics:** ALNY (★★★★☆) and REGN (★★★☆☆) are the only names with acceptable risk/reward.

---

## Growth × Value matrix

| Growth \ Valuation | **Cheap** (MoS ≥ 20%) | **Fair** (−10% to 20%) | **Expensive** (< −10%) |
|---|---|---|---|
| **High** (Growth ≥ 65) | ★★★ **ALNY**, APP (red flags), CRWV (EV/sales-based; cash-runway flag) | ★★★ **NVDA, MELI, META**, AXON, CRWD, NBIS (speculative) | ★ ALAB, AMD, AMZN, ARM, ASML, AVGO, DDOG, ISRG, LITE, MPWR, MRVL, PANW, PLTR, RKLB, SHOP, STX |
| **Medium** (40–65) | ★★★ — | ★★ **MSFT** | ★ CDNS, CEG, GOOGL, KLAC, LRCX, SNPS |
| **Low** (< 40) | ★★ **PYPL** | ★ REGN, GEHC | Avoid: ADI, AMAT, AMGN, GILD, MU, NXPI, QCOM, TER, TSLA, VRTX |

**Focus list (High growth + Cheap or Fair, excluding the speculative names): NVDA, ALNY, MELI, META.** MSFT is a medium-growth, low-risk anchor. AXON and CRWD are fairly valued, but SBC-heavy and GAAP loss-making.

---

## Multi-theme winners

| Rank | Ticker | Themes (score ≥5) | Theme scores | Growth | Quality | Valuation | MoS | Multi-theme score |
|---|---|---|---|---|---|---|---|---|
| 1 | NVDA | AI + Robotics | AI 10, Robotics 6 | 100 | 92 | 75 | 15% | 92 |
| 2 | GOOGL | AI + Robotics | AI 10, Robotics 6 | 65 | 77 | 37 | -28% | 79 |
| 3 | AMZN | AI + Robotics | AI 9, Robotics 7 | 66 | 37 | 40 | -30% | 74 |
| 4 | ADI | Robotics + Energy Storage + AI | Robotics 7, Energy Storage 5, AI 5 | 30 | 58 | 34 | -42% | 72 |
| 5 | AXON | Robotics + AI | Robotics 6, AI 7 | 68 | 32 | 74 | 16% | 72 |
| 6 | TSLA | Robotics + Energy Storage + AI | Robotics 9, Energy Storage 8, AI 8 | 28 | 22 | 0 | -319% | 72 |
| 7 | ARM | AI + Robotics | AI 9, Robotics 5 | 83 | 64 | 0 | -302% | 70 |
| 8 | TER | Robotics + AI | Robotics 7, AI 8 | 25 | 54 | 34 | -141% | 67 |
| 9 | QCOM | AI + Robotics | AI 6, Robotics 5 | 38 | 80 | 44 | -16% | 66 |
| 10 | NXPI | Robotics + Energy Storage | Robotics 6, Energy Storage 5 | 17 | 54 | 45 | -15% | 60 |
| 11 | GEHC | Multiomics + AI | Multiomics 5, AI 6 | 3 | 40 | 64 | 9% | 58 |

- **NVDA** leads clearly on structural trends, strength of exposure, financial quality, growth and valuation combined.
- **TSLA and ADI** have the most themes (three each), but are expensive or low-growth.
- **GOOGL** (AI + Waymo robotics + Isomorphic multiomics) is the broadest platform. It screens expensive only on the capex-depressed FCF legs.

---

## Disruption scores (Ark-style)

| Ticker | AI | Robotics | Energy storage | Blockchain | Multiomics | Disruption | TAM expansion | Comp. advantage | **Disruption score /100** |
|---|---|---|---|---|---|---|---|---|---|
| NVDA | 10 | 6 | 0 | 1 | 3 | 10 | 10 | 9 | **88** |
| TSLA | 8 | 9 | 8 | 0 | 0 | 10 | 10 | 7 | **88** |
| GOOGL | 10 | 6 | 0 | 1 | 3 | 9 | 10 | 9 | **86** |
| AMZN | 9 | 7 | 1 | 0 | 0 | 8 | 10 | 9 | **82** |
| MSFT | 10 | 2 | 0 | 0 | 0 | 9 | 10 | 10 | **81** |
| ISRG | 4 | 10 | 0 | 0 | 0 | 8 | 8 | 10 | **78** |
| PLTR | 10 | 3 | 0 | 0 | 0 | 9 | 9 | 8 | **77** |
| ARM | 9 | 5 | 0 | 0 | 0 | 8 | 9 | 9 | **77** |
| AVGO | 10 | 1 | 0 | 0 | 0 | 8 | 9 | 9 | **75** |
| META | 9 | 2 | 0 | 0 | 0 | 8 | 9 | 9 | **73** |
| ASML | 9 | 0 | 0 | 0 | 0 | 8 | 9 | 10 | **72** |
| AMD | 9 | 3 | 0 | 0 | 0 | 8 | 9 | 7 | **71** |
| MPWR | 8 | 3 | 4 | 0 | 0 | 7 | 8 | 7 | **68** |
| ALNY | 3 | 0 | 0 | 0 | 8 | 8 | 8 | 8 | **68** |
| TER | 8 | 7 | 0 | 0 | 0 | 7 | 7 | 7 | **68** |
| CRWV | 10 | 0 | 0 | 2 | 0 | 8 | 9 | 4 | **68** |
| REGN | 4 | 0 | 0 | 0 | 8 | 7 | 8 | 8 | **67** |
| ALAB | 10 | 0 | 0 | 0 | 0 | 8 | 8 | 6 | **67** |
| AXON | 7 | 6 | 0 | 0 | 0 | 7 | 7 | 8 | **65** |
| NBIS | 10 | 0 | 0 | 0 | 0 | 8 | 9 | 4 | **65** |
| ADI | 5 | 7 | 5 | 0 | 0 | 5 | 7 | 8 | **64** |
| CRWD | 8 | 0 | 0 | 0 | 0 | 7 | 9 | 8 | **64** |
| LITE | 9 | 0 | 0 | 0 | 0 | 8 | 8 | 6 | **64** |
| MU | 9 | 0 | 0 | 0 | 0 | 7 | 9 | 6 | **64** |
| SHOP | 6 | 0 | 0 | 4 | 0 | 7 | 9 | 8 | **63** |
| CDNS | 8 | 0 | 0 | 0 | 0 | 6 | 7 | 10 | **62** |
| PANW | 8 | 0 | 0 | 0 | 0 | 6 | 9 | 8 | **62** |
| MRVL | 9 | 0 | 0 | 0 | 0 | 7 | 8 | 6 | **62** |
| VRTX | 0 | 0 | 0 | 0 | 7 | 7 | 8 | 9 | **61** |
| AMAT | 8 | 0 | 0 | 0 | 0 | 6 | 8 | 8 | **61** |
| DDOG | 8 | 0 | 0 | 0 | 0 | 7 | 8 | 7 | **61** |
| KLAC | 8 | 0 | 0 | 0 | 0 | 6 | 7 | 9 | **61** |
| LRCX | 8 | 0 | 0 | 0 | 0 | 6 | 8 | 8 | **61** |
| SNPS | 8 | 0 | 0 | 0 | 0 | 6 | 7 | 9 | **61** |
| CEG | 7 | 0 | 3 | 0 | 0 | 5 | 8 | 8 | **60** |
| APP | 8 | 0 | 0 | 0 | 0 | 7 | 8 | 6 | **59** |
| NXPI | 4 | 6 | 5 | 0 | 0 | 5 | 7 | 7 | **59** |
| GEHC | 6 | 2 | 0 | 0 | 5 | 5 | 7 | 7 | **57** |
| RKLB | 2 | 6 | 0 | 0 | 0 | 8 | 8 | 6 | **57** |
| MELI | 4 | 0 | 0 | 4 | 0 | 7 | 9 | 8 | **57** |
| QCOM | 6 | 5 | 0 | 0 | 0 | 5 | 7 | 7 | **56** |
| AMGN | 4 | 0 | 0 | 0 | 6 | 5 | 7 | 7 | **55** |
| PYPL | 3 | 0 | 0 | 6 | 0 | 5 | 7 | 6 | **52** |
| STX | 7 | 0 | 0 | 0 | 0 | 5 | 7 | 6 | **51** |
| GILD | 2 | 0 | 0 | 0 | 4 | 5 | 6 | 7 | **44** |

---

## TAM and adoption (analyst estimates, low confidence)

| Ticker | Addressable market: today → 5y → 10y (analyst estimate) | TAM opportunity | Tech adoption | Market-share potential |
|---|---|---|---|---|
| NVDA | AI accelerators ~$400B -> ~$900B -> ~$1.5T | 10/10 | 9/10 | 9/10 |
| APP | Mobile + web ad-tech ~$100B -> ~$200B | 8/10 | 7/10 | 6/10 |
| META | Digital ads + AI assistants ~$700B -> ~$1.2T | 9/10 | 8/10 | 8/10 |
| ASML | Lithography ~$45B -> ~$80B -> ~$120B | 9/10 | 8/10 | 9/10 |
| MSFT | Cloud + AI software ~$1T -> ~$2.5T | 10/10 | 9/10 | 9/10 |
| MELI | LatAm e-commerce + fintech ~$300B; Meli Dolar stablecoin | 9/10 | 8/10 | 8/10 |
| ALNY | RNAi medicines ~$15B -> ~$50B | 8/10 | 7/10 | 7/10 |
| GOOGL | Search/ads + cloud + Waymo ~$1T+ | 10/10 | 9/10 | 8/10 |
| PLTR | Enterprise/government AI platforms ~$100B -> ~$300B | 9/10 | 8/10 | 7/10 |
| STX | Mass-capacity storage ~$30B -> ~$50B (cyclical) | 7/10 | 7/10 | 6/10 |
| KLAC | Process control ~$15B -> ~$25B | 7/10 | 8/10 | 8/10 |
| AVGO | Custom AI ASICs + networking ~$150B -> ~$400B -> ~$600B | 9/10 | 9/10 | 8/10 |
| LRCX | Etch/deposition ~$50B -> ~$85B | 8/10 | 8/10 | 7/10 |
| ALAB | AI connectivity silicon ~$10B -> ~$40B | 8/10 | 8/10 | 6/10 |
| AMAT | Wafer-fab equipment ~$120B -> ~$200B | 8/10 | 8/10 | 7/10 |
| QCOM | Edge AI, auto, IoT ~$150B | 7/10 | 6/10 | 5/10 |
| ISRG | Soft-tissue surgical robotics ~$20B -> ~$50B | 8/10 | 7/10 | 9/10 |
| SHOP | Commerce software + payments ~$200B; USDC checkout | 9/10 | 8/10 | 8/10 |
| CDNS | EDA + simulation ~$20B -> ~$40B | 7/10 | 7/10 | 8/10 |
| AMZN | Cloud + e-commerce + ads ~$3T; warehouse robotics | 10/10 | 9/10 | 8/10 |
| PYPL | Digital wallets/checkout ~$100B; PYUSD stablecoin optionality | 7/10 | 6/10 | 5/10 |
| MPWR | Power management ICs ~$40B -> ~$70B | 8/10 | 8/10 | 7/10 |
| AMD | Data-center GPUs/CPUs ~$500B -> ~$1T | 9/10 | 8/10 | 7/10 |
| LITE | Optical transceivers/lasers ~$25B -> ~$60B | 8/10 | 8/10 | 7/10 |
| CRWV | GPU cloud ~$50B -> ~$250B | 9/10 | 8/10 | 6/10 |
| CRWD | Endpoint/cloud/identity security ~$120B -> ~$250B | 9/10 | 8/10 | 8/10 |
| ARM | CPU IP royalties ~$15B -> ~$40B | 9/10 | 8/10 | 8/10 |
| VRTX | CF franchise + gene editing (Casgevy) + pain | 8/10 | 6/10 | 7/10 |
| AXON | Public-safety tech + drones ~$50B -> ~$100B | 7/10 | 7/10 | 8/10 |
| REGN | Genetics-led biologics; Regeneron Genetics Center | 8/10 | 6/10 | 6/10 |
| CEG | Clean firm power for data centers ~$100B -> ~$200B | 8/10 | 7/10 | 7/10 |
| MRVL | Custom silicon + optical DSP ~$80B -> ~$200B | 8/10 | 8/10 | 6/10 |
| TER | Semi test + cobots ~$15B -> ~$30B | 7/10 | 7/10 | 7/10 |
| DDOG | Observability + AI monitoring ~$60B -> ~$120B | 8/10 | 8/10 | 7/10 |
| ADI | Industrial/auto analog + BMS ~$80B | 7/10 | 7/10 | 7/10 |
| PANW | Platform security ~$200B -> ~$350B | 9/10 | 8/10 | 8/10 |
| NXPI | Auto/industrial processors + BMS ~$70B | 7/10 | 6/10 | 6/10 |
| SNPS | EDA + simulation (Ansys) ~$30B -> ~$55B | 7/10 | 7/10 | 8/10 |
| GEHC | Imaging + molecular diagnostics + AI ~$100B | 7/10 | 6/10 | 6/10 |
| GILD | HIV + oncology + cell therapy | 6/10 | 6/10 | 6/10 |
| NBIS | GPU cloud ~$50B -> ~$250B | 9/10 | 8/10 | 5/10 |
| RKLB | Launch + spacecraft ~$40B -> ~$100B | 8/10 | 7/10 | 6/10 |
| MU | DRAM/HBM/NAND ~$300B -> ~$500B (cyclical) | 9/10 | 9/10 | 7/10 |
| TSLA | EVs + robotaxi + Optimus + Megapack; robotaxi TAM ~$1T+ (10y, speculative) | 10/10 | 6/10 | 6/10 |
| AMGN | Biologics; deCODE human-genetics platform | 7/10 | 6/10 | 6/10 |

---

## TOP 10 HIGH-CONVICTION STOCKS

Ranked by risk-adjusted attractiveness. **The expected returns are model outputs.** They assume NTM EPS compounds at the forward consensus growth rate (capped at 40%), 70% of that rate in years 4–5, and an exit at the fair P/E (90% of it at year 5). **Haircut them by 30–40%.**

| # | Ticker | Price | Bear / **Base** / Bull FV | MoS | Ideal entry (25% MoS) | 3-yr exp. return* | 5-yr exp. return* | Consensus target | Rating |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **NVDA** | $237.47 | $189 / **$279** / $387 | 15% | ≤ $210 | ~59%/yr (cap-limited; very high variance) | ~43%/yr | $324 | ★★★★☆ (borderline: 18% upside vs the 20% bar) |
| 2 | **ALNY** | $224.41 | $233 / **$384** / $584 | 42% | ≤ $288 (now) | ~44%/yr | ~33%/yr | $366 | ★★★★☆ (filter PASS) |
| 3 | **MELI** | $1,872.78 | $1,498 / **$2,326** / $3,395 | 19% | ≤ $1,745 | ~39%/yr | ~32%/yr | $2,276 | ★★★★☆ (filter PASS) |
| 4 | **META** | $721.31 | $465 / **$661** / $904 | −9% | ≤ $496 | ~23%/yr | ~16%/yr | $809 | ★★★☆☆ |
| 5 | **MSFT** | $529.76 | $373 / **$512** / $665 | −3% | ≤ $384 | ~27%/yr | ~19%/yr | $586 | ★★★☆☆ |
| 6 | **GOOGL** | $350.50 | $202 / **$274** / $356 | −28% | ≤ $205 | ~22%/yr | ~16%/yr | $427 | ★★☆☆☆ (model penalizes capex/SBC; see note) |
| 7 | **REGN** | $741.60 | $640 / **$833** / $1,074 | 11% | ≤ $625 | ~14%/yr | ~9%/yr | $854 | ★★★☆☆ |
| 8 | **PYPL** | $54.95 | $66 / **$85** / $105 | 35% | ≤ $64 (now) | ~19%/yr | ~11%/yr | $58 | ★★☆☆☆ (cheap, low growth) |
| 9 | **ASML** | $1,804.96 | $972 / **$1,277** / $1,629 | −41% | ≤ $958 | ~32%/yr | ~26%/yr | $2,471 | ★★☆☆☆ (wait for price) |
| 10 | **APP** | $281.29 | $247 / **$352** / $472 | 20% | ≤ $264 | ~35%/yr | ~25%/yr | $505 | ★★☆☆☆ (speculative: legal red flags) |

\* Model outputs, before the recommended 30–40% haircut. Prices are **closing prices on Oct 7, 2026** (Yahoo Finance).

### 1. NVIDIA (NVDA): AI (core) + Robotics. Reasonable margin of safety; just misses the strict filter (18% upside vs the 20% bar)

1. **Thesis.** The dominant AI accelerator platform, priced at only ~17x NTM consensus EPS. Consensus revenue for FY Jan-27 is $412B (+91%), then $692B ([stockanalysis.com](https://stockanalysis.com/stocks/nvda/forecast/)).
   - Q2 FY27 revenue was **$96.2B (+106% y/y)**, with data center at **$89.0B (+117%)**.
   - Q3 is guided to **$108B ±2%**.
   - Management gave a preliminary view of **~70% revenue growth in FY28**, describing it as supply-constrained ([Webull summary](https://www.webull.com/blog/304-Nvidia-Q2-FY2027-Earnings-Beats-Revenue-EPS-Estimates-Guides-Q3-to-108B); [Grafa](https://grafa.com/en/news/united-states/nvidia-q2-fiscal-2027-revenue-reaches-96-2-billion)).
2. **Disruptive technology.** GPUs, NVLink and networking, and the CUDA software stack for training and inference. Also Isaac/Omniverse for robotics and BioNeMo for drug discovery, which is why it has a multi-theme score.
3. **Why the market is large.** AI accelerators: ~$400B → ~$1.5T over 10 years (analyst estimate). Supply and capacity commitments reached **$279B** (same sources).
4. **Competitive advantage.** The CUDA ecosystem, full-stack systems and scale. Gross margin is 71%, operating margin 60% and ROIC 66% (FY Jan-26, SEC data).
5. **Revenue growth potential.** 3-year CAGR of 100%, latest year-to-date +96%. The base case assumes a 30% revenue CAGR over 5 years, well below what consensus implies for the next two years.
6. **Profitability potential.** Already exceptional. Q3 gross margin is guided to ~74% (same sources). The base case assumes a 60% operating margin and 45% FCF margin.
7. **Fair value.** Base **$279**: DCF $247, earnings $349 (25x), FCF $154, historical $419.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 18% | 55% | 40% | $8.76 | 10.5% | $189 |
   | Base | 30% | 60% | 45% | $15.50 | 10.0% | $279 |
   | Bull | 38% | 62% | 48% | $21.59 | 9.5% | $387 |

   Terminal growth is 3% in every case.
9. **Ideal entry.** ≤ $210 (25% margin of safety). Starting a position at today's 15% margin of safety is defensible.
10. **3-year expected return.** ~59%/yr (model; forward EPS growth capped at 40%). Realistically ~25–35%/yr.
11. **5-year expected return.** ~43%/yr (model). Realistically ~18–25%/yr.
12. **Biggest risk.** A hyperscaler capex digestion phase, which makes earnings cyclical. Also China export controls (Q3 guidance assumes no China data-center compute sales) and custom ASIC competition from AVGO and MRVL.
13. **Invalidation.** Two consecutive quarters of falling data-center revenue, or gross margin below 65%.

### 2. Alnylam (ALNY): Multiomics / genetic medicine. Filter PASS, Excellent margin of safety

1. **Thesis.** The RNAi platform leader is now profitable, at ~24x NTM EPS with ~34% forward EPS growth.
   - **Amvuttra passed $1B in quarterly revenue (+106%) in Q2 2026.** Total revenue was about **$1.29B (+67%)** and net income **$164.5M**.
   - The stock fell after **2026 TTR guidance was cut to $4.20–4.50B** (from $4.40–4.70B) as second-line demand normalized. The midpoint still implies ~75% TTR growth ([Pulse 2](https://pulse2.com/alnylam-amvuttra-revenue-tops-1-billion-but-pent-up-demand-normalization-triggers-guidance-cut/); [RTTNews](https://www.rttnews.com/3673187/alnylam-pharma-reports-net-income-in-q2-revises-2026-ttr-net-product-revenue-guidance.aspx?refresh=1); [MarketBeat](https://www.marketbeat.com/instant-alerts/alnylam-pharmaceuticals-q2-earnings-call-highlights-2026-07-30/)).
2. **Disruptive technology.** Gene silencing (siRNA) with genetics-validated targets. Durable, infrequent dosing.
3. **Opportunity.** RNAi medicines: ~$15B → ~$50B (analyst estimate). ATTR cardiomyopathy alone is a multi-billion-dollar market.
4. **Competitive advantage.** IP and delivery platform (GalNAc) with first-mover scale.
5. **Revenue growth.** 3-year CAGR of 53%, 5-year 50%, latest year-to-date +80%.
6. **Profitability.** First GAAP-profitable year was FY25 (operating margin 14%). Product gross margin is 75% (same sources). The base case assumes a 35% operating margin by year 5.
7. **Fair value.** Base **$384**: DCF $581, earnings $276, FCF $137, historical $368. The FCF leg is low because FCF only just turned positive.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin (SBC-adj.) | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 25% | 25% | 20% | $16.62 | 10.0% | $233 |
   | Base | 32% | 35% | 28% | $30.56 | 9.5% | $384 |
   | Bull | 38% | 40% | 33% | $43.61 | 9.0% | $584 |

   Terminal growth is 3% in every case.
9. **Ideal entry.** ≤ $288. The current price qualifies.
10. **3-year expected return.** ~44%/yr (model).
11. **5-year expected return.** ~33%/yr (model).
12. **Biggest risk.** Amvuttra concentration plus competition in ATTR-CM. Also royalty-driven gross-margin pressure (75% vs 79% a year ago).
13. **Invalidation.** TTR revenue growth falling below 30%, or a competitor showing superior outcomes data.

### 3. MercadoLibre (MELI): LatAm e-commerce + fintech (Blockchain secondary via the Meli Dólar stablecoin and crypto in Mercado Pago). Filter PASS, Reasonable margin of safety

1. **Thesis.** The highest-growth large-cap platform in the screen. The 3-year revenue CAGR is 39% (FY25 revenue $28.9B), with year-to-date growth of +49%. Consensus revenue is $41.8B for FY26 (+45%) and $54.0B for FY27 ([stockanalysis.com](https://stockanalysis.com/stocks/meli/forecast/)). It trades at ~36x NTM with ~42% forward EPS growth, a PEG below 1.
2. **Disruptive technology.** Digital banking and credit (Mercado Pago), logistics automation, and stablecoin/crypto rails. These are small today.
3. **Opportunity.** LatAm e-commerce plus fintech: a ~$300B revenue pool (analyst estimate).
4. **Competitive advantage.** Logistics network and two-sided marketplace plus a fintech flywheel. ROIC is 26%.
5. **Revenue growth.** Consensus EPS rises from $38.3 (FY26) to $114.6 (FY29).
6. **Profitability.** Operating margin is 11% (FY25, on total revenue including fintech income). FCF is distorted by credit-book funding, so the DCF uses net income as a proxy for FCF.
7. **Fair value.** Base **$2,326**: DCF $2,628, earnings $1,828, historical $2,351.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | Net margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 22% | 12% | 8% | $146.0 | 12% | $1,498 |
   | Base | 28% | 15% | 10% | $232.1 | 11% | $2,326 |
   | Bull | 33% | 18% | 12% | $337.3 | 10.5% | $3,395 |

   Terminal growth is 3% in every case.
9. **Ideal entry.** ≤ $1,745.
10. **3-year expected return.** ~39%/yr (model).
11. **5-year expected return.** ~32%/yr (model).
12. **Biggest risk.** Credit losses in Mercado Pago lending, plus Argentina/Brazil FX and politics. The Q1 2026 credit portfolio nearly doubled to $14.6B ([Munich Startup / company data](https://insights.munich-startup.de/news/feed/mercadolibre-posts-49-revenue-growth-in-q1-2026-as-credit-portfolio-doubles-to-14-6b)).
13. **Invalidation.** NPLs spiking while operating margin compresses below 10%.

### 4. Meta Platforms (META): AI + (AR/robotics optionality). Fairly valued

1. **Thesis.** AI-driven ad ranking is lifting growth (year-to-date +30%). The stock trades at ~21.7x NTM.
2. **Disruptive technology.** Llama and Meta AI, generative ad tools, and smart glasses.
3. **Opportunity.** Digital ads plus AI assistants: ~$700B → ~$1.2T (analyst estimate).
4. **Competitive advantage.** About 3.5B daily users and first-party data. ROIC is 34%.
5. **Revenue growth.** CAGRs of 20% (3-year) and 19% (5-year).
6. **Profitability.** Operating margin is 41%, but **FCF is depressed by AI capex, and SBC is 10% of revenue** (the DCF is SBC-adjusted).
7. **Fair value.** Base **$661**: DCF $527, earnings $800, FCF $629, historical $833.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 12% | 38% | 12% | $41.3 | 9.5% | $465 |
   | Base | 17% | 41% | 18% | $55.4 | 9.0% | $661 |
   | Bull | 21% | 43% | 23% | $68.8 | 8.5% | $904 |

   Terminal growth is 3% in every case.
9. **Ideal entry.** ≤ $496. An accumulate zone of ≤ $600 is reasonable for this quality.
10. **3-year expected return.** ~23%/yr.
11. **5-year expected return.** ~16%/yr.
12. **Biggest risk.** AI capex without a matching return, plus regulation (EU DMA, youth safety).
13. **Invalidation.** Ad revenue growth below 10% while capex keeps rising.

### 5. Microsoft (MSFT): AI (core). Fairly valued, lowest risk

1. **Thesis.** The broadest enterprise AI distribution (Azure, Copilot, GitHub) at ~25x NTM. FY Jun-26 revenue was $332B (+18%).
2. **Disruptive technology.** AI cloud and agents.
3. **Opportunity.** Cloud plus AI software: ~$1T → ~$2.5T (analyst estimate).
4. **Competitive advantage.** Enterprise lock-in and bundling. Moat 10/10; operating margin 47%; ROIC 30%.
5. **Revenue growth.** 3-year CAGR 16%; consensus EPS rises from $19.65 (FY27) to $28.28 (FY29).
6. **Profitability.** FCF margin fell to 20% on record capex. The base case assumes recovery to 28%.
7. **Fair value.** Base **$512**: DCF $459, earnings $625, FCF $362, historical $667.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 11% | 45% | 22% | $26.7 | 9.0% | $373 |
   | Base | 15% | 47% | 28% | $33.3 | 8.5% | $512 |
   | Bull | 18% | 49% | 32% | $39.4 | 8.0% | $665 |

   Terminal growth is 3% in every case.
9. **Ideal entry.** ≤ $384. An accumulate zone of ≤ $460 is reasonable.
10. **3-year expected return.** ~27%/yr.
11. **5-year expected return.** ~19%/yr.
12. **Biggest risk.** Capex intensity and OpenAI-relationship economics.
13. **Invalidation.** Azure growth below 20% while capex keeps rising.

### 6. Alphabet (GOOGL): AI + Robotics (Waymo) + Multiomics (Isomorphic/DeepMind). Rated ★★ by the model; the model is conservative on this name

1. **Thesis.** Year-to-date revenue growth is +23%. NTM P/E is ~22x on normalized EPS of ~$15.5, which excludes the investment gains in FY26 consensus.
2. **Disruptive technology.** Gemini, TPUs, **Waymo (autonomous ride-hailing)** and DeepMind/Isomorphic (AI drug discovery). It has the broadest multi-theme exposure in the Nasdaq-100.
3. **Opportunity.** Above $1T across search, cloud and autonomy (analyst estimate).
4. **Competitive advantage.** Distribution (Search, Android, YouTube), custom TPU silicon and data. ROIC is 30%.
5. **Revenue growth.** 3-year CAGR of 13% is below the 15% bar. The latest pace is higher.
6. **Profitability.** Operating margin is 32%. FCF margin is 18%, depressed by capex. **SBC is 6.2% of revenue**, so the DCF is SBC-adjusted.
7. **Fair value.** Base **$274**: DCF $211, earnings $372, FCF $205, historical $372. **Note:** the earnings-based legs alone put fair value at ~$372, roughly the price. The low reading comes from capex-depressed, SBC-adjusted FCF.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin (SBC-adj.) | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 10% | 32% | 15% | $13.4 | 9.5% | $202 |
   | Base | 14% | 34% | 20% | $17.0 | 9.0% | $274 |
   | Bull | 17% | 36% | 24% | $20.5 | 8.5% | $356 |

   Terminal growth is 3% in every case.
9. **Ideal entry.** ≤ $205 on the model; ≤ $300 on the earnings legs.
10. **3-year expected return.** ~22%/yr.
11. **5-year expected return.** ~16%/yr.
12. **Biggest risk.** AI-search disruption and antitrust remedies.
13. **Invalidation.** Search revenue declining year over year.

### 7. Regeneron (REGN): Multiomics (Regeneron Genetics Center). Reasonable margin of safety, low growth

1. **Thesis.** ~14x NTM EPS, net cash of about $6.6B, and one of the largest human-genetics databases supporting target discovery.
2. **Disruptive technology.** Genetics-led drug discovery, plus gene and cell medicine programs.
3. **Opportunity.** Large biologics markets (Dupixent).
4. **Competitive advantage.** VelociSuite discovery and genetics data.
5. **Revenue growth.** 3-year CAGR of 6% (fails the growth bar); year-to-date +18%.
6. **Profitability.** Operating margin 25%, FCF margin 28%.
7. **Fair value.** Base **$833**: DCF $831, earnings $872, FCF $724, historical $923.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 4% | 25% | 22% | $31.7 | 9.0% | $640 |
   | Base | 7% | 28% | 25% | $41.0 | 8.5% | $833 |
   | Bull | 10% | 31% | 28% | $52.1 | 8.0% | $1,074 |

   Terminal growth is 3% in every case. The model's year-5 EPS sits below consensus because the scenario uses GAAP margins.
9. **Ideal entry.** ≤ $625.
10. **3-year expected return.** ~14%/yr.
11. **5-year expected return.** ~9%/yr.
12. **Biggest risk.** EYLEA biosimilar erosion.
13. **Invalidation.** Dupixent growth stalling.

### 8. PayPal (PYPL): Blockchain (PYUSD). Excellent margin of safety, but low growth

1. **Thesis.** 9.6x NTM EPS and 9.6x P/FCF, with the share count falling about 4% a year.
2. **Disruptive technology.** The PYUSD stablecoin and agentic checkout.
3. **Opportunity.** Digital wallets and checkout, about a $100B revenue pool (analyst estimate).
4. **Competitive advantage.** Medium: branded checkout and Venmo, under pressure from Apple Pay and Shop Pay.
5. **Revenue growth.** 3-year CAGR of 6% (fails the growth bar).
6. **Profitability.** Operating margin 18%, FCF margin 17%.
7. **Fair value.** Base **$85**: DCF $96, earnings $74, FCF $78, historical $80.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 2% | 17% | 15% | $5.08 | 10.0% | $66 |
   | Base | 4% | 19% | 17% | $6.26 | 9.5% | $85 |
   | Bull | 6% | 20% | 18% | $7.25 | 9.0% | $105 |

   Terminal growth is 3% in every case.
9. **Ideal entry.** ≤ $64. The current price qualifies.
10. **3-year expected return.** ~19%/yr.
11. **5-year expected return.** ~11%/yr.
12. **Biggest risk.** Losing branded-checkout share. Consensus is Hold (4 Buy / 24 Hold / 2 Sell).
13. **Invalidation.** Branded TPV declining.

### 9. ASML (ASML): AI (EUV lithography monopoly). Highest quality, wait for the price

1. **Thesis.** Sole supplier of EUV, needed for every leading-edge AI chip. Operating margin 35%, ROIC 84%.
2. **Disruptive technology.** EUV and High-NA EUV.
3. **Opportunity.** Lithography: ~$45B → ~$120B (analyst estimate).
4. **Competitive advantage.** A monopoly (moat 10/10).
5. **Revenue growth.** CAGRs of 16% (3-year) and 19% (5-year). Consensus EPS rises from $43.9 (FY26) to $88.8 (FY29), in USD per ADR.
6. **Profitability.** FCF margin 34%.
7. **Fair value.** Base **$1,277**: DCF $869, earnings $1,678, FCF $1,206, historical $1,790. EUR financials were converted at 1.17 USD/EUR (an analyst assumption).
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 8% | 33% | 25% | $37.7 | 9.5% | $972 |
   | Base | 13% | 36% | 28% | $51.5 | 9.0% | $1,277 |
   | Bull | 17% | 38% | 31% | $64.7 | 8.5% | $1,629 |

   Terminal growth is 3% in every case. The model's year-5 EPS sits below consensus because it starts from FY25 revenue and uses a 13% base growth rate; consensus implies roughly 30%.
9. **Ideal entry.** ≤ $958 strictly. An accumulate zone of ~$1,300–1,450 is reasonable for a monopoly.
10. **3-year expected return.** ~32%/yr (model, using consensus EPS growth).
11. **5-year expected return.** ~26%/yr.
12. **Biggest risk.** The semicap cycle and China export controls.
13. **Invalidation.** A multi-quarter fall in EUV orders.

### 10. AppLovin (APP): AI ad-tech. Strong numbers, speculative because of red flags

1. **Thesis.** 14.5x NTM EPS, 76% operating margin, ~72% FCF margin, and year-to-date revenue growth of +56%.
2. **Disruptive technology.** The AXON machine-learning ad engine.
3. **Opportunity.** Mobile plus web performance ads, ~$100B → ~$200B (analyst estimate).
4. **Competitive advantage.** Model quality and data scale (moat 6/10, contested by Meta).
5. **Revenue growth.** 3-year CAGR of 25%, 5-year 30%.
6. **Profitability.** Already exceptional.
7. **Fair value.** Base **$352**: DCF $352, earnings $349, FCF $255, historical $485. A higher 11% discount rate is used for legal risk.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 15% | 65% | 55% | $16.6 | 12% | $247 |
   | Base | 22% | 72% | 62% | $24.6 | 11% | $352 |
   | Bull | 28% | 75% | 66% | $32.6 | 10.5% | $472 |

   Terminal growth is 3% in every case.
9. **Ideal entry.** ≤ $264. Speculative sizing only.
10. **3-year expected return.** ~35%/yr.
11. **5-year expected return.** ~25%/yr.
12. **Biggest risk.** Legal and regulatory: securities class actions, a reported SEC inquiry and short-seller allegations (cited in this repository's Oct 7 Nasdaq-100 report via Bigdata.com).
13. **Invalidation.** Enforcement action, or advertiser attrition to Meta.


---

## 12. Early-stage disruptors and excluded names

| Ticker | Theme | Price | Mkt cap | Revenue (latest FY) | Growth (FY / YTD) | FCF (latest FY) | Cash & ST inv. | Net debt | Cash runway | SBC % rev | Model base FV | Rating | Key point |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **CRWV** | AI GPU cloud | $88.45 | $49B | $5.13B | +168% / +112% | **−$7.25B** | $3.2B | **$18.2B (7.6x EBITDA)** | **~0.4 yrs** (externally funded) | 12% | $156 | ★☆☆☆☆ | The EV/sales leg on consensus revenue (+151%) gives a 43% "margin of safety", but the business depends on continuous debt and equity funding. Consensus EPS turns positive only in FY29. |
| **NBIS** | AI GPU cloud | $237.15 | $64B | $0.53B | +479% / N/A | **−$3.68B** | $3.7B | $0.4B | **~1.0 yr** | 16% | $221 | ★☆☆☆☆ | Consensus revenue is about 6x FY25. Its value rests almost entirely on the EV/sales leg; it needs continuous capital raising. |
| **RKLB** | Space/autonomous systems | $71.92 | $45B | $0.60B | +38% / +63% | −$0.32B | $1.0B | net cash | ~3.2 yrs | 12% | $21 | ★☆☆☆☆ | Strong execution (Neutron), but ~45x consensus NTM sales. |
| **CRWD** | AI security | $265.44 | $272B | $4.81B (FY Jan-26) | +22% / +26% | +$1.24B (≈ +$0.14B after SBC) | $5.2B | net cash | N/A | **23%** | $292 | ★★☆☆☆ | Category leader, fairly valued on EV/sales (9% margin of safety); GAAP loss. |
| **AXON** | Public-safety AI + drones | $406.00 | $33B | $2.78B | +33% / +35% | +$0.08B | $1.7B | $0.1B | N/A | **23%** | $483 | ★★★☆☆ | 16% margin of safety on EV/sales, but a GAAP operating loss and heavy SBC. |
| **ALAB** | AI connectivity | $382.25 | $66B | $0.85B | +115% / +99% | +$0.28B | $1.2B | net cash | N/A | 19% | $145 | ★★☆☆☆ | Profitable, but ~90x NTM EPS; share count up sharply since the 2024 IPO. |
| **MSTR** | Bitcoin treasury | $148.33 | $62.6B | $0.48B (software) | flat | ~−$0.08B operating | $2.3B | $5.9B (plus preferreds) | N/A | 11% | not modelled | ★☆☆☆☆ | **The value is a leveraged bet on the bitcoin price.** FY25 GAAP net loss of $3.8B (fair-value marks); shares 113M → 278M (2022–25). |
| **HON** | Automation | $206.18 | $65B | $37.4B (pre-separation) | +8% | — | — | — | — | — | not modelled | — | Post-separation financials are not yet comparable with the price. Revisit after clean filings. |

---

## G. Red-flag check (shortlist)

| Ticker | Excessive valuation | Debt | Cash burn | Dilution | SBC | Weak moat | One-product dependence | Regulatory | Obsolescence | Customer concentration | Execution | Subsidies | Crypto prices | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NVDA | No (17x NTM) | Net cash | No | No | 3% | No | Data-center GPUs | **Export controls** | Custom ASICs | **Hyperscalers** | Supply chain | No | No | Moderate (cyclical) |
| ALNY | No (24x) | Net cash | No (turned FCF-positive) | +8% / 3y | 9% | No | **Amvuttra** | Drug pricing (IRA) | Competing ATTR therapies | No | **Guidance cut** | No | No | Moderate |
| MELI | Moderate (35x) | 0.7x (excluding credit book) | No | No | 0% | No | No | LatAm regulation | No | No | Credit losses | No | Minor | Moderate |
| META | No (21.7x) | Net cash | No | Buybacks | 10% | No | Ads | **EU/US regulation** | AI substitution | No | AI capex | No | No | Moderate |
| MSFT | Moderate (25x) | Net cash | No | No | 4% | No | No | Antitrust | Low | OpenAI | Capex | No | No | Clean |
| GOOGL | No on P/E (22x) | Net cash | No | Buybacks | 6% | No | Search | **Antitrust remedies** | **AI search** | No | Capex | No | No | Moderate |
| APP | No (14x) | 0.2x | No | Buybacks | 4% | Medium | Ad engine | **SEC inquiry, class actions** | Meta competition | Gaming advertisers | Model volatility | No | No | **Significant red flag** |
| TSLA | **Yes (~300x)** | Net cash | No (but reported Q2 FCF −$1.1B) | Low | 3% | Medium | Autos | Autonomy regulation | EV competition | No | **Robotaxi and Optimus execution** | EV credits | No | **Valuation red flag** |
| PLTR | **Yes (111x)** | Net cash | No | +24% / 3y | 15% | No | No | Government budgets | Low | US government | — | No | No | Valuation red flag |
| CRWV / NBIS | Sales-multiple based | **CRWV 7.6x** | **Yes** | Heavy | 12–16% | Low | GPU leasing | — | **GPU obsolescence** | **Few AI labs** | Data-center build | No | No | **Speculative** |
| MSTR | NAV premium | $8.2B converts plus preferreds | Operating burn small | **Heavy** | 11% | — | **Bitcoin** | Accounting/tax | — | — | — | — | **Yes (direct)** | **Avoid as a "fundamental" pick** |

---

## H. Final classification

| Rating | Companies |
|---|---|
| ★★★★★ High growth + high quality + undervalued | **None** at Oct 7, 2026 closing prices |
| ★★★★☆ High growth + reasonable valuation | **NVDA, MELI, ALNY** |
| ★★★☆☆ Excellent technology, fairly valued | **META, MSFT, AXON, REGN** |
| ★★☆☆☆ Attractive theme, but excessive valuation or risk | APP, ASML, GOOGL, PLTR, STX, KLAC, AVGO, LRCX, ALAB, AMAT, QCOM, ISRG, SHOP, CDNS, AMZN, PYPL, MPWR, AMD, LITE, CRWD, ARM, VRTX, CEG, MRVL, TER, DDOG, ADI, PANW, NXPI, SNPS, GEHC, GILD, MU, TSLA, AMGN |
| ★☆☆☆☆ Speculative / avoid | CRWV, NBIS, RKLB, MSTR |

**Watch-list entry prices (25% margin of safety on base FV).** These are valuable franchises waiting for a better price:
- **ASML:** ≤ $958.
- **ISRG:** ≤ $239.
- **AVGO:** ≤ $226.
- **META:** ≤ $496.
- **MSFT:** ≤ $384.
- **GOOGL:** ≤ $205 on the model; ~$300 on the earnings legs.

---

## Data sources

**Structured data.**
- **SEC EDGAR XBRL companyfacts** (`https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`): annual 10-K/20-F data and 10-Q year-to-date revenue for all 47 companies.
- **Nasdaq.com:** the Nasdaq-100 constituent list (`api.nasdaq.com/api/quote/list-type/nasdaq100`, Oct 8, 2026), plus quote, summary, earnings-forecast and target-price endpoints.
- **[stockanalysis.com](https://stockanalysis.com) forecast pages** (`stockanalysis.com/stocks/<ticker>/forecast/`): consensus revenue for the current and next fiscal year and the revenue cross-check, retrieved Oct 8, 2026.
- **Yahoo Finance chart API:** Oct 7, 2026 closing prices.
- **[Bigdata.com](https://bigdata.com):** not used (credits exhausted). Earlier repository reports used it.

**Cited documents (web).**
- NVIDIA:
  - [Webull - NVIDIA Q2 FY2027 summary](https://www.webull.com/blog/304-Nvidia-Q2-FY2027-Earnings-Beats-Revenue-EPS-Estimates-Guides-Q3-to-108B)
  - [Grafa - NVIDIA Q2 FY2027 revenue](https://grafa.com/en/news/united-states/nvidia-q2-fiscal-2027-revenue-reaches-96-2-billion)
- Alnylam:
  - [Pulse 2 - Alnylam Q2 2026](https://pulse2.com/alnylam-amvuttra-revenue-tops-1-billion-but-pent-up-demand-normalization-triggers-guidance-cut/)
  - [RTTNews - Alnylam guidance revision](https://www.rttnews.com/3673187/alnylam-pharma-reports-net-income-in-q2-revises-2026-ttr-net-product-revenue-guidance.aspx?refresh=1)
  - [MarketBeat - Alnylam Q2 call, Jul 30, 2026](https://www.marketbeat.com/instant-alerts/alnylam-pharmaceuticals-q2-earnings-call-highlights-2026-07-30/)
- Tesla:
  - [pv magazine - Tesla Q2 2026 storage deployments](https://pv-magazine-usa.com/2026/07/02/tesla-announces-13-5-gwh-energy-storage-deployments-in-q2-sets-july-earnings-date/)
  - [ESS News - Tesla 13.5 GWh](https://www.ess-news.com/2026/07/02/tesla-deploys-13-5-gwh-of-energy-storage-in-q2/)
  - [Longbridge - Tesla Q2 2026 call transcript](https://longbridge.com/news/294985240)
- MercadoLibre:
  - [Munich Startup - MercadoLibre Q1 2026 credit portfolio](https://insights.munich-startup.de/news/feed/mercadolibre-posts-49-revenue-growth-in-q1-2026-as-credit-portfolio-doubles-to-14-6b)

*All scores, TAM figures, fair multiples, scenario assumptions, discount rates and risk ratings are the analyst's judgments, not sourced data.*
