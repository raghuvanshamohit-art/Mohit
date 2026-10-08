# NYSE Disruptive-Technology Screen: AI, Robotics, Energy Storage, Blockchain, Multiomics

**Data date.**
- Prices are closing prices on **Oct 7, 2026** (Nasdaq.com quote API).
- Fundamentals are the latest reported fiscal year (5–6 years of history) plus the latest 10-Q year-to-date.
- Consensus estimates and price targets are as of Oct 7–8, 2026.

**Data sources.** Two primary sources were used. The source is marked for every company.

| Source | Used for | Companies |
|---|---|---|
| **[Bigdata.com](https://bigdata.com)** Corporate Fundamentals (FMP) plus Bigdata.com news, transcript and filing search | 5-year financials, consensus revenue and EPS, price targets, cited facts | TSM, ANET, ORCL, NOW, UBER, SYK, ALB, SQM, CRCL, XYZ, TMO |
| **SEC EDGAR XBRL** "companyfacts" (annual 10-K / 20-F data as filed) plus **Nasdaq.com** (price, exchange, market cap, consensus EPS, price targets) | Same, minus consensus *revenue* | All other companies |

- **Why two sources:** Bigdata.com credits ran out partway through the data pull. The remaining companies were filled from primary SEC filings and Nasdaq.com instead.
- **Consensus EPS is mostly adjusted (non-GAAP).** That applies to both Nasdaq.com (Zacks) and FMP consensus.
- **Missing revenue consensus:** for the SEC-sourced names, "forward revenue growth" is **N/A** and the DCF growth rate is an analyst assumption.
- **Cited facts for SEC-sourced names** come from web search of company releases and SEC 8-K exhibits. Links are given inline.

**Conventions.**
- **FY** = reported fiscal year, GAAP.
- **"Latest YTD y/y"** = latest 10-Q year-to-date revenue versus the same period a year earlier. It stands in for TTM growth: the data could not produce a clean TTM series for every company.
- **NTM** = next twelve months, time-weighted from current and next fiscal-year consensus.
- **N/A** = not available. **N/M** = not meaningful (negative or distorted base).
- **No number in this report was estimated where data was missing.** Analyst judgments (scores, TAM sizes, fair multiples, scenario growth and margins) are labelled as such.

> **Not investment advice.** Fair values come from a model whose key inputs (growth, margins, discount rates, fair multiples) are the analyst's assumptions, listed in §7. Use them as a structured starting point.

---

## 0. Headline findings

1. **Two stocks pass the strict "most important filter": Uber (UBER) and Amphenol (APH).** The filter requires revenue CAGR >15%, EPS/FCF growth >15%, a strong moat, a large TAM, upside >20%, positive FCF and a clean balance sheet.
   - **UBER** is the clearer pass: 35% margin of safety at about 16x NTM EPS.
   - **APH** passes at the margin: 25% upside and a 20% margin of safety. Its 3-year growth is partly acquisition-driven (CommScope CCS).
2. **No company earns ★★★★★** (high growth + high quality + undervalued). The ★★★★☆ group is **APH, UBER, NOW, MA and XYZ**.
3. **AI is where the quality is, but most of it is priced in.**
   - TSM, ANET, VRT, CLS, FN, CIEN and DELL all have Growth scores of 75–100.
   - Apart from TSM (fair, −7% margin of safety), they trade 17–65% above the model's base value after their 2025–26 rallies.
   - **The model is more conservative than the street** on these names. For example, the consensus price targets are $727 for FN vs model $334 and $326 for VRT vs model $211. The reason: the model uses a 40% FCF-based DCF, and AI-hardware FCF margins are thin (CLS 4%, FN ~0%, DELL 8%) while capex is heavy.
4. **Robotics on the NYSE is mostly indirect.** The listed pure plays are Nasdaq stocks (ISRG, TER, SYM, Mobileye) or pre-revenue (JOBY, ACHR). The NYSE exposure is through UBER (AV aggregation), SYK (Mako), APH (sensors and connectors), DE (autonomy) and ROK and TDY (automation and machine vision).
5. **Energy storage: no attractive pick.**
   - Lithium producers (ALB, SQM) are deep-cyclical commodity plays.
   - The quality electrical names (ETN, VRT) are richly valued.
   - EnerSys (ENS) is fairly valued but low-growth.
   - **QuantumScape is Nasdaq-listed** (verified), so it is excluded.
6. **Blockchain: the best risk/reward is in the incumbent rails, not crypto-native names.**
   - **MA, V and XYZ** monetize stablecoin settlement and bitcoin with little dependence on crypto prices.
   - **Circle (CRCL)** is the purest play but trades at 57x NTM EPS. Its revenue is mostly interest income on reserves, so it is rate-sensitive.
7. **Multiomics on the NYSE is a group of mature tool makers with no high growth.**
   - TMO, DHR, A, QGEN, RVTY, BIO, LH and IQV have 3-year revenue CAGRs between −9% and +6%.
   - The high-growth genomics names (Illumina, Natera, Tempus AI, Guardant) are **Nasdaq-listed** (verified), so none of the eight scores well on growth.

---

## 1. Method and coverage

**Universe.**
- Started from NYSE-listed common stocks with a market cap above $1B that map to the five themes.
- **Exchange was verified per company** through Nasdaq.com and Bigdata.com. These are listed elsewhere and were excluded: **QS, OUST, FLNC, EOSE, TEM, NTRA, ILMN** (Nasdaq). **PSTG** did not resolve in either data source and was also dropped.
- Excluded throughout: ETFs, funds, SPACs, preferreds, warrants and illiquid issues.

**Coverage.** 47 NYSE names were pulled and **41 were quantitatively modelled**. The other six are handled qualitatively (§12):
- **JOBY, ACHR:** pre-revenue.
- **BLSH, BKKT:** report gross crypto trading volume as revenue, so revenue is not meaningful. BKKT's market cap is also under $1B.

A full screen of every NYSE stock was not feasible. The candidates were chosen by theme. **Survivorship-bias note:** 2026 decliners (ORCL −49% over 1 year, UBER −30%, SYK −25%, CRCL −46%, ALB) are included alongside the winners.

**Fair value = 40% DCF + 25% earnings-based + 20% FCF-based + 15% historical/peer**, with a bear, base and bull case for every company.

| Leg | Method |
|---|---|
| **DCF (scenario)** | 10-year revenue-driven model. Revenue grows at `g` for years 1–5, then fades linearly to terminal growth `tg` (3%) by year 10. The FCF margin moves linearly from today's level to the scenario target by year 5. Discount rate `r` is 8–15% depending on risk. Equity value = PV − net debt. **When SBC exceeds 5% of revenue, FCF is reduced by SBC.** |
| **Earnings-based** | NTM consensus EPS × fair P/E (×0.8 in bear, ×1.2 in bull). |
| **FCF-based** | Latest FCF/share × (1 + g) × fair P/FCF (×0.8 / ×1.2). |
| **Historical/peer** | NTM EPS × an approximate historical or peer P/E (×0.85 / ×1.15). |

**Special cases.**
- **Early-stage companies** with negative NTM EPS (SNOW, NET, S, AMPX): **40% scenario DCF + 60% EV/NTM-sales peer multiple**. Low confidence.
- **Banks (BNY):** earnings replace FCF.
- **Lithium producers (ALB, SQM):** the DCF starts from **mid-cycle revenue**, defined as the average of FY2021–25 actuals and the next two years of consensus. A single upcycle or downcycle year is not capitalized.

**Scores (0–100).**
- **Growth:**
  - 3-year revenue CAGR: 25 points. 5-year revenue CAGR: 15.
  - EPS CAGR: 20 (forward growth substituted when history is N/M). FCF CAGR: 15.
  - Forward revenue growth: 15. Forward EPS growth: 10.
  - Missing items are re-weighted. **+3 points** for each of revenue, EPS and FCF CAGR above 15%, per the brief.
- **Quality:** gross margin 15, operating margin 20, ROIC 25, FCF margin 15, moat 15, recurring revenue / pricing power 10.
- **Financial strength:**
  - Net debt/EBITDA 40, or cash runway for cash burners.
  - Interest cover 20, current ratio 15, SBC % of revenue 15, 3-year share-count change 10.
- **Valuation:** margin of safety 60 plus forward PEG 40 (MoS only, when PEG is N/M).
- **Disruption:** theme strength 50 (best theme ×3 + second ×1.25 + third ×0.75, capped at 50) plus (disruption + TAM expansion + competitive advantage) × 50/30. The plain sum of eight /10 scores would penalize focused leaders for not being in all five themes.
- **Overall (/100):** Growth 20, Quality 15, Profitability/ROIC 10, Financial strength 10, Valuation 20, Competitive advantage 10, TAM & technology 10, Risk 5.

**Star rules.**
- **★★★★★:** Growth ≥ 60, Quality ≥ 65 and MoS ≥ 20%.
- **★★★★☆:** Growth ≥ 55 and MoS ≥ 0.
- **★★★☆☆:** MoS ≥ −15% with Quality or Disruption ≥ 60.
- **★★☆☆☆:** everything else, plus anything with negative FCF, risk score < 45, or a major red flag.
- **★☆☆☆☆:** loss-making with a cash runway under 3 years or a very high risk score.

**Known limitations.**
- The DCF starts from **last fiscal-year revenue**. For hyper-growers whose year-to-date growth is far above trend (APH +57%, CLS +58%, DELL +71%, ANET +36%), this understates the near-term base. The base-case `g` was raised toward the year-to-date pace to compensate, partly.
- **Acquisition effects:** reported growth includes acquisitions for APH (CommScope CCS), SYK (Inari), NOW, TMO (Clario, Solventum F&F), XYZ (Afterpay, 2022), ORCL (Cerner, FY2023) and VRT (about 5 pts in Q2 2026).
- **Divestitures and spin-offs** depress reported 3–5-year CAGRs: DHR (Veralto spin), RVTY (2023 divestiture) and SQM/ALB (lithium price collapse).
- **SEC data quirks:**
  - Pre-split EPS years are excluded from EPS CAGRs (APH, CLS, NOW).
  - Visa's EPS is not tagged in XBRL, so its EPS CAGR uses net income.
  - Operating income for ETN, IBM and DE was derived as pretax income plus interest expense.

---

## A. Final ranked table (all 41 modelled companies; the top 20 are the "Top 20 overall opportunities")

Rev/EPS/FCF CAGR = 3-year, FY2022 → FY2025 (or latest FY), GAAP. ROIC = latest FY (calculated where the source did not provide it). Debt/EBITDA is on a net-debt basis. Risk band comes from the risk score (Low ≥ 70 … Very high < 35).

| Rank | Ticker | Company | Theme | Secondary | Mkt Cap ($B) | Rev CAGR 3y | EPS CAGR 3y | FCF CAGR 3y | ROIC | Debt/EBITDA (net) | Price | Base FV | Upside | MoS | Growth | Quality | Disruption | Valuation | Overall | Risk | Rating |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | APH | Amphenol Corp. | AI | Robotics | 216 | 22% | 30% | 35% | 28% | 0.5x | $87.55 | $104 | 19% | 16% | 100 | 62 | 70 | 72 | 80 | Medium | ★★★★☆ |
| 2 | TSM | Taiwan Semiconductor Manuf | AI | Robotics | 2,449 | 19% | 19% | 28% | 25% | net cash | $472 | $440 | -7% | -7% | 93 | 82 | 83 | 53 | 80 | Medium | ★★★☆☆ |
| 3 | MA | Mastercard Inc. | Blockchain | AI | 499 | 14% | 17% | 17% | 92% | 0.4x | $570 | $607 | 6% | 6% | 60 | 83 | 55 | 52 | 75 | Low | ★★★★☆ |
| 4 | ANET | Arista Networks, Inc. | AI | — | 272 | 27% | 37% | 112% | 23% | net cash | $216 | $151 | -30% | -43% | 100 | 80 | 73 | 26 | 72 | Medium | ★★☆☆☆ |
| 5 | NOW | ServiceNow, Inc. | AI | Robotics | 143 | 22% | 73% | 28% | 9% | net cash | $138 | $144 | 4% | 4% | 100 | 64 | 72 | 59 | 70 | Medium | ★★★★☆ |
| 6 | VRT | Vertiv Holdings Co. | AI | Energy Storage | 95 | 22% | N/A | N/A | 28% | 0.6x | $246 | $199 | -19% | -24% | 93 | 57 | 73 | 40 | 69 | Med–High | ★★☆☆☆ |
| 7 | CLS | Celestica Inc. | AI | — | 43 | 20% | 70% | 65% | 35% | 0.1x | $372 | $240 | -36% | -55% | 99 | 41 | 61 | 40 | 68 | Med–High | ★★☆☆☆ |
| 8 | UBER | Uber Technologies, Inc. | Robotics | AI | 140 | 18% | N/A | 193% | 11% | 0.7x | $68.45 | $105 | 53% | 35% | 86 | 42 | 67 | 95 | 68 | Medium | ★★★★☆ |
| 9 | V | Visa Inc. | Blockchain | AI | 665 | 11% | 10% | 6% | 41% | 0.3x | $372 | $369 | -1% | -1% | 28 | 83 | 55 | 42 | 66 | Low | ★★★☆☆ |
| 10 | ORCL | Oracle Corporation | AI | — | 435 | 10% | 24% | N/A | 8% | 3.7x | $144 | $204 | 42% | 30% | 75 | 50 | 75 | 90 | 62 | High | ★★☆☆☆ |
| 11 | XYZ | Block, Inc. | Blockchain | AI | 46 | 11% | N/A | 681% | 8% | net cash | $76.07 | $84.99 | 12% | 10% | 71 | 34 | 55 | 70 | 58 | Med–High | ★★★★☆ |
| 12 | FN | Fabrinet | AI | — | 18 | 21% | 25% | -73% | 23% | net cash | $498 | $303 | -39% | -65% | 75 | 31 | 61 | 35 | 58 | Med–High | ★★☆☆☆ |
| 13 | SYK | Stryker Corporation | Robotics | AI | 106 | 11% | 11% | 28% | 9% | 2.0x | $275 | $322 | 17% | 14% | 43 | 51 | 63 | 65 | 56 | Low | ★★★☆☆ |
| 14 | DELL | Dell Technologies Inc. | AI | — | 368 | 4% | 39% | 148% | 37% | 1.8x | $579 | $324 | -44% | -79% | 53 | 45 | 62 | 31 | 55 | Med–High | ★★☆☆☆ |
| 15 | ETN | Eaton Corp. PLC | AI | Energy Storage | 168 | 10% | 19% | 22% | 14% | 1.5x | $431 | $333 | -23% | -29% | 56 | 45 | 72 | 29 | 54 | Low | ★★☆☆☆ |
| 16 | PATH | UiPath Inc. | AI | Robotics | 7 | 15% | N/A | N/A | 7% | net cash | $13.07 | $11.37 | -13% | -15% | 75 | 45 | 58 | 42 | 52 | Med–High | ★★☆☆☆ |
| 17 | DE | Deere & Co. | Robotics | AI | 177 | -5% | -7% | 20% | 24% | 0.5x | $657 | $429 | -35% | -53% | 28 | 49 | 65 | 39 | 51 | Medium | ★★☆☆☆ |
| 18 | NET | Cloudflare Inc. | AI | Blockchain | 122 | 31% | N/A | N/A | N/A | N/A | $343 | $110 | -68% | -212% | 100 | 42 | 68 | 0 | 51 | Med–High | ★★☆☆☆ |
| 19 | ENS | EnerSys Inc. | Energy Storage | AI | 7 | 0% | 22% | 35% | 13% | 1.2x | $182 | $181 | -1% | -1% | 48 | 33 | 53 | 59 | 50 | Medium | ★★☆☆☆ |
| 20 | ICE | Intercontinental Exchange  | Blockchain | — | 86 | 9% | 31% | 8% | 8% | 2.9x | $153 | $158 | 3% | 3% | 42 | 59 | 46 | 48 | 50 | Low | ★★☆☆☆ |
| 21 | SNOW | Snowflake Inc. | AI | — | 117 | 31% | N/A | 31% | N/A | N/A | $333 | $186 | -44% | -79% | 100 | 45 | 69 | 0 | 50 | Med–High | ★★☆☆☆ |
| 22 | ROK | Rockwell Automation Inc. | Robotics | AI | 49 | 2% | -1% | 26% | 23% | 1.1x | $442 | $300 | -32% | -48% | 25 | 57 | 65 | 7 | 45 | Medium | ★★☆☆☆ |
| 23 | CRCL | Circle Internet Group Inc. | Blockchain | AI | 21 | 53% | N/A | N/A | -2% | N/A | $80.84 | $49.52 | -39% | -63% | 79 | 24 | 72 | 31 | 45 | High | ★★☆☆☆ |
| 24 | IBM | IBM Corp. | AI | Blockchain | 208 | 4% | 84% | 10% | 12% | 2.8x | $221 | $225 | 2% | 2% | 32 | 53 | 60 | 37 | 45 | Medium | ★★★☆☆ |
| 25 | BNY | The Bank of New York Mello | Blockchain | — | 97 | 7% | 37% | 29% | N/A | N/A | $143 | $124 | -13% | -15% | 53 | 32 | 43 | 39 | 44 | Medium | ★★☆☆☆ |
| 26 | QGEN | Qiagen N.V. | Multiomics | AI | 9 | -1% | 2% | -8% | 8% | 0.8x | $44.79 | $46.14 | 3% | 3% | 2 | 55 | 59 | 44 | 44 | Medium | ★★☆☆☆ |
| 27 | S | SentinelOne Inc. | AI | — | 9 | 33% | N/A | N/A | -31% | N/A | $25.31 | $18.92 | -25% | -34% | 100 | 33 | 53 | 0 | 43 | High | ★★☆☆☆ |
| 28 | TDY | Teledyne Technologies Inc. | Robotics | AI | 28 | 10% | 23% | 14% | 7% | 1.4x | $604 | $508 | -16% | -19% | 50 | 41 | 56 | 5 | 42 | Low | ★★☆☆☆ |
| 29 | CIEN | Ciena Corp. | AI | — | 63 | 10% | -5% | N/A | 5% | 0.7x | $446 | $208 | -53% | -114% | 24 | 28 | 62 | 40 | 40 | Med–High | ★★☆☆☆ |
| 30 | A | Agilent Technologies Inc. | Multiomics | — | 48 | 0% | 3% | 4% | 15% | 0.7x | $169 | $123 | -27% | -37% | 4 | 52 | 52 | 15 | 40 | Low | ★★☆☆☆ |
| 31 | AMPX | Amprius Technologies Inc. | Energy Storage | Robotics | 1 | 155% | N/A | N/A | -276% | N/A | $9.33 | $5.28 | -43% | -77% | 100 | 10 | 67 | 0 | 39 | Very high | ★☆☆☆☆ |
| 32 | DHR | Danaher Corp. | Multiomics | — | 154 | -3% | -19% | -11% | 6% | 1.9x | $218 | $184 | -16% | -19% | 2 | 53 | 60 | 9 | 37 | Low | ★★☆☆☆ |
| 33 | GNRC | Generac Holdings Inc. | Energy Storage | AI | 13 | -3% | -21% | N/A | 7% | 1.8x | $221 | $150 | -32% | -48% | 19 | 25 | 54 | 40 | 37 | Med–High | ★★☆☆☆ |
| 34 | TMO | Thermo Fisher Scientific I | Multiomics | AI | 245 | -0% | 0% | -3% | 8% | 2.6x | $662 | $471 | -29% | -41% | 5 | 45 | 61 | 10 | 36 | Low | ★★☆☆☆ |
| 35 | IQV | IQVIA Holdings Inc. | Multiomics | AI | 42 | 4% | 11% | 9% | 9% | 4.1x | $258 | $208 | -19% | -24% | 17 | 33 | 58 | 27 | 34 | Medium | ★★☆☆☆ |
| 36 | GXO | GXO Logistics Inc. | Robotics | AI | 5 | 14% | -45% | -18% | 4% | 2.5x | $45.99 | $40.91 | -11% | -12% | 29 | 13 | 47 | 48 | 33 | Med–High | ★★☆☆☆ |
| 37 | ALB | Albemarle Corporation | Energy Storage | — | 12 | -11% | N/A | 2% | 1% | 3.0x | $103 | $103 | -0% | -0% | 12 | 19 | 62 | 33 | 33 | High | ★★☆☆☆ |
| 38 | SQM | Sociedad Quimica y Minera  | Energy Storage | — | 18 | -25% | -47% | -48% | 6% | 1.9x | $64.61 | $46.40 | -28% | -39% | 18 | 33 | 62 | 0 | 32 | High | ★★☆☆☆ |
| 39 | LH | Labcorp Holdings Inc. | Multiomics | — | 25 | 6% | -9% | -8% | 8% | 2.4x | $312 | $272 | -13% | -15% | 2 | 29 | 49 | 20 | 31 | Medium | ★★☆☆☆ |
| 40 | BIO | Bio-Rad Laboratories Inc. | Multiomics | — | 10 | -3% | N/A | 66% | 1% | net cash | $368 | $240 | -35% | -53% | 21 | 32 | 48 | 0 | 31 | Medium | ★★☆☆☆ |
| 41 | RVTY | Revvity Inc. | Multiomics | AI | 17 | -9% | -36% | -27% | 3% | 3.0x | $154 | $92.46 | -40% | -66% | 4 | 45 | 55 | 10 | 29 | Medium | ★★☆☆☆ |

### A.1 Growth, margins and balance-sheet detail

| Ticker | Rev 3y | Rev 5y | Latest FY YoY | Latest YTD y/y (10-Q) | EPS 3y | EPS 5y | Fwd EPS growth | FCF 3y | FCF 5y | FCF margin | Gross m. | Op. m. | Net m. | ROE | ROA | SBC % rev | Shares Δ3y | Int. cover | Current ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APH | 22% | 22% | 52% | 57% | 30% | N/A | 23% | 35% | 27% | 19% | 37% | 25% | 19% | 32% | 12% | 1% | 3% | 20x | 3.0 |
| TSM | 19% | N/A | 32% | N/A | 19% | N/A | 29% | 28% | N/A | 29% | 60% | 51% | 45% | 32% | 22% | 0% | 0% | 156x | 2.6 |
| MA | 14% | 16% | 16% | 15% | 17% | 21% | 15% | 17% | 20% | 52% | N/A | 58% | 46% | 193% | 28% | 2% | -7% | 26x | 1.0 |
| ANET | 27% | N/A | 29% | 36% | 37% | N/A | 25% | 112% | N/A | 47% | 64% | 43% | 39% | 28% | 18% | 5% | 1% | N/M | 3.0 |
| VRT | 22% | 19% | 28% | 27% | N/A | N/A | 33% | N/A | 65% | 18% | 36% | 18% | 13% | 34% | 11% | 0% | 3% | 21x | 1.5 |
| NOW | 22% | N/A | 21% | 23% | 73% | N/A | 22% | 28% | N/A | 34% | 78% | 14% | 13% | 13% | 7% | 15% | 3% | 79x | 1.0 |
| CLS | 20% | N/A | 28% | 58% | 70% | N/A | 70% | 65% | N/A | 4% | 12% | 8% | 7% | 38% | 12% | 1% | -6% | 20x | 1.4 |
| UBER | 18% | N/A | 18% | 13% | N/A | N/A | 29% | 193% | N/A | 19% | 40% | 11% | 19% | 37% | 16% | 4% | 7% | 13x | 1.1 |
| V | 11% | 13% | 11% | 16% | 10% | 13% | 13% | 6% | 17% | 54% | N/A | 60% | 50% | 53% | 20% | 2% | N/A | 41x | 1.1 |
| ORCL | 10% | N/A | 17% | 30% | 24% | N/A | 38% | N/A | N/A | -35% | 65% | 31% | 25% | 40% | 7% | 7% | 5% | 5x | 1.1 |
| XYZ | 11% | N/A | 0% | 7% | N/A | N/A | 27% | 681% | N/A | 10% | 43% | 13% | 5% | 6% | 3% | 5% | 8% | 24x | 2.2 |
| FN | 21% | 20% | 36% | N/A | 25% | 27% | 22% | -73% | -47% | 0% | 12% | 10% | 10% | 19% | 12% | 1% | -2% | N/M | 2.3 |
| SYK | 11% | N/A | 11% | 6% | 11% | N/A | 11% | 28% | N/A | 17% | 64% | 19% | 13% | 14% | 7% | 1% | 0% | 8x | 1.9 |
| DELL | 4% | 6% | 19% | 71% | 39% | 16% | 14% | 148% | -2% | 8% | 20% | 7% | 5% | N/A | 6% | 1% | -9% | 6x | 0.9 |
| ETN | 10% | 9% | 10% | 19% | 19% | 25% | 18% | 22% | 7% | 13% | 38% | 19% | 15% | 21% | 10% | 0% | -2% | 21x | 1.3 |
| PATH | 15% | 22% | 13% | 15% | N/A | N/A | 20% | N/A | 68% | 22% | 83% | 4% | 18% | 14% | 9% | 18% | -1% | N/M | 2.5 |
| DE | -5% | 5% | -12% | 7% | -7% | 16% | 28% | 20% | -2% | 13% | N/A | 21% | 11% | 19% | 5% | 0% | -11% | 3x | N/A |
| NET | 31% | 38% | 30% | 35% | N/A | N/A | N/A | N/A | N/A | 12% | 75% | -10% | -5% | -7% | -2% | 21% | 7% | N/M | 2.0 |
| ENS | 0% | 5% | 4% | 5% | 22% | 18% | 13% | 35% | 10% | 12% | 29% | 11% | 8% | 15% | 7% | 1% | -8% | 8x | 2.7 |
| ICE | 9% | 9% | 7% | 12% | 31% | 9% | 10% | 8% | 9% | 31% | N/A | 39% | 26% | 11% | 2% | 2% | 2% | 6x | 1.0 |
| SNOW | 31% | 51% | 29% | 34% | N/A | N/A | N/A | 31% | N/A | 24% | 67% | -31% | -28% | -69% | -15% | 34% | 6% | N/M | 1.3 |
| ROK | 2% | 6% | 1% | 10% | -1% | -3% | 11% | 26% | 6% | 16% | 48% | 20% | 10% | 24% | 8% | 1% | -3% | 11x | 1.1 |
| CRCL | 53% | N/A | 64% | N/A | N/A | N/A | 40% | N/A | N/A | 19% | 9% | -3% | -3% | -2% | -0% | 21% | 419% | N/M | 1.0 |
| IBM | 4% | 4% | 8% | 5% | 84% | 12% | 8% | 10% | -5% | 18% | 58% | 18% | 16% | 32% | 7% | 3% | 4% | 6x | 1.0 |
| BNY | 7% | 5% | 8% | N/A | 37% | 14% | 11% | 29% | 9% | 28% | N/A | N/A | 28% | 13% | 1% | 0% | -12% | N/M | N/A |
| QGEN | -1% | 2% | 6% | N/A | 2% | 5% | 9% | -8% | 24% | 21% | 62% | 22% | 20% | 11% | 7% | 2% | -5% | 16x | 3.9 |
| S | 33% | 61% | 22% | 21% | N/A | N/A | N/A | N/A | N/A | 5% | 74% | -32% | -45% | -31% | -18% | 30% | 19% | N/M | 1.4 |
| TDY | 10% | N/A | 8% | 9% | 23% | N/A | 8% | 14% | N/A | 18% | 43% | 19% | 15% | 9% | 6% | 0% | 7% | 19x | 1.6 |
| CIEN | 10% | 6% | 19% | 37% | -5% | -18% | 60% | N/A | 10% | 14% | 42% | 4% | 3% | 5% | 2% | 4% | -5% | 2x | 2.7 |
| A | 0% | 5% | 7% | 8% | 3% | 15% | 11% | 4% | 8% | 17% | 52% | 21% | 19% | 19% | 10% | 2% | -5% | 13x | 2.0 |
| AMPX | 155% | N/A | 202% | 137% | N/A | N/A | N/A | N/A | N/A | -49% | 11% | -64% | -60% | -42% | -28% | 10% | 75% | N/M | 7.1 |
| DHR | -3% | 2% | 3% | 5% | -19% | 1% | 9% | -11% | -1% | 21% | 59% | 19% | 15% | 7% | 4% | 1% | -3% | 18x | 1.9 |
| GNRC | -3% | 11% | -2% | 11% | -21% | -13% | 22% | N/A | -9% | 6% | 38% | 7% | 4% | 6% | 3% | 1% | -8% | 4x | 2.0 |
| TMO | -0% | N/A | 4% | 8% | 0% | N/A | 10% | -3% | N/A | 14% | 41% | 18% | 15% | 13% | 6% | 1% | -4% | 6x | 1.9 |
| IQV | 4% | 8% | 6% | 8% | 11% | 41% | 12% | 9% | 9% | 13% | N/A | 13% | 8% | 21% | 5% | 2% | -9% | 3x | 0.7 |
| ALB | -11% | N/A | -4% | 32% | N/A | N/A | -4% | 2% | N/A | 13% | 13% | 2% | -10% | -5% | -3% | 1% | -0% | 0x | 2.2 |
| SQM | -25% | N/A | 1% | N/A | -47% | N/A | 1% | -48% | N/A | 10% | 29% | 25% | 13% | 10% | 4% | 0% | 0% | 6x | 3.3 |
| GXO | 14% | 16% | 13% | 7% | -45% | N/A | 15% | -18% | -0% | 1% | N/A | 2% | 0% | 1% | 0% | 0% | -1% | 2x | 0.8 |
| LH | 6% | -0% | 7% | 6% | -9% | -8% | 7% | -8% | -7% | 9% | 29% | 10% | 6% | 10% | 5% | 1% | -9% | 6x | 1.4 |
| BIO | -3% | 0% | 1% | 0% | N/A | -26% | -2% | 66% | -5% | 15% | 52% | 2% | 29% | 10% | 7% | 2% | -8% | 1x | 5.6 |
| RVTY | -9% | N/A | 4% | 4% | -36% | N/A | 11% | -27% | N/A | 18% | 70% | 12% | 8% | 3% | 2% | 1% | -0% | 4x | 1.7 |

### A.2 Financial strength and cash runway

| Ticker | Profile | Cash & ST inv. ($M) | Net debt ($M) | Net debt/EBITDA | Interest cover | Current ratio | FCF per share (latest FY, USD) | Cash runway | SBC % rev | Share count Δ 3y |
|---|---|---|---|---|---|---|---|---|---|---|
| APH | Profitable growth | 11,434 | 3,131 | 0.5x | 20x | 3.0 | 3.43/sh | N/A (FCF positive) | 1% | 3% |
| TSM | Profitable growth | 112,525 | -62,459 | net cash | 156x | 2.6 | 7.68/sh | N/A (FCF positive) | 0% | 0% |
| MA | Profitable growth | 10,566 | 8,434 | 0.4x | 26x | 1.0 | 18.94/sh | N/A (FCF positive) | 2% | -7% |
| ANET | Profitable growth | 10,743 | -1,964 | net cash | N/M | 3.0 | 3.33/sh | N/A (FCF positive) | 5% | 1% |
| VRT | Profitable growth | 1,728 | 1,185 | 0.6x | 21x | 1.5 | 4.83/sh | N/A (FCF positive) | 0% | 3% |
| NOW | Profitable growth | 6,284 | -1,323 | net cash | 79x | 1.0 | 4.37/sh | N/A (FCF positive) | 15% | 3% |
| CLS | Profitable growth | 596 | 155 | 0.1x | 20x | 1.4 | 3.94/sh | N/A (FCF positive) | 1% | -6% |
| UBER | Profitable growth | 7,633 | 4,975 | 0.7x | 13x | 1.1 | 4.61/sh | N/A (FCF positive) | 4% | 7% |
| V | Profitable growth | 17,164 | 8,007 | 0.3x | 41x | 1.1 | 12.08/sh | N/A (FCF positive) | 2% | N/A |
| ORCL | Profitable, FCF negative | 31,894 | 124,900 | 3.7x | 5x | 1.1 | -8.13/sh | 1.3 yrs | 7% | 5% |
| XYZ | Profitable growth | 11,964 | -2,370 | net cash | 24x | 2.2 | 3.89/sh | N/A (FCF positive) | 5% | 8% |
| FN | Profitable growth | 875 | -875 | net cash | N/M | 2.3 | 0.08/sh | N/A (FCF positive) | 1% | -2% |
| SYK | Profitable growth | 4,100 | 12,349 | 2.0x | 8x | 1.9 | 11.21/sh | N/A (FCF positive) | 1% | 0% |
| DELL | Profitable growth | 11,528 | 19,975 | 1.8x | 6x | 0.9 | 12.50/sh | N/A (FCF positive) | 1% | -9% |
| ETN | Profitable growth | 803 | 9,091 | 1.5x | 21x | 1.3 | 9.08/sh | N/A (FCF positive) | 0% | -2% |
| PATH | Profitable growth | 1,472 | -1,472 | net cash | N/M | 2.5 | 0.65/sh | N/A (FCF positive) | 18% | -1% |
| DE | Profitable growth | 8,276 | 5,520 | 0.5x | 3x | N/A | 22.45/sh | N/A (FCF positive) | 0% | -11% |
| NET | Early-stage (GAAP loss) | 4,101 | -4,101 | net cash | N/M | 2.0 | 0.75/sh | N/A (FCF positive) | 21% | 7% |
| ENS | Profitable growth | 439 | 670 | 1.2x | 8x | 2.7 | 12.26/sh | N/A (FCF positive) | 1% | -8% |
| ICE | Profitable growth | 837 | 18,807 | 2.9x | 6x | 1.0 | 6.73/sh | N/A (FCF positive) | 2% | 2% |
| SNOW | Early-stage (GAAP loss) | 4,030 | -4,030 | net cash | N/M | 1.3 | 3.32/sh | N/A (FCF positive) | 34% | 6% |
| ROK | Profitable growth | 468 | 2,148 | 1.1x | 11x | 1.1 | 12.01/sh | N/A (FCF positive) | 1% | -3% |
| CRCL | Profitable growth | 1,527 | -1,489 | net cash | N/M | 1.0 | 2.19/sh | N/A (FCF positive) | 21% | 419% |
| IBM | Profitable growth | 13,587 | 48,699 | 2.8x | 6x | 1.0 | 12.76/sh | N/A (FCF positive) | 3% | 4% |
| BNY | Profitable growth | 5,111 | 26,762 | N/A | N/M | N/A | 7.74/sh | N/A (FCF positive) | 0% | -12% |
| QGEN | Profitable growth | 1,099 | 556 | 0.8x | 16x | 3.9 | 2.04/sh | N/A (FCF positive) | 2% | -5% |
| S | Early-stage (GAAP loss) | 629 | -629 | net cash | N/M | 1.4 | 0.16/sh | N/A (FCF positive) | 30% | 19% |
| TDY | Profitable growth | 352 | 2,123 | 1.4x | 19x | 1.6 | 22.66/sh | N/A (FCF positive) | 0% | 7% |
| CIEN | Profitable growth | 1,308 | 228 | 0.7x | 2x | 2.7 | 4.58/sh | N/A (FCF positive) | 4% | -5% |
| A | Profitable growth | 1,789 | 1,261 | 0.7x | 13x | 2.0 | 4.04/sh | N/A (FCF positive) | 2% | -5% |
| AMPX | Early-stage (GAAP loss) | 90 | -90 | net cash | N/M | 7.1 | -0.29/sh | 2.5 yrs | 10% | 75% |
| DHR | Profitable growth | 4,615 | 13,803 | 1.9x | 18x | 1.9 | 7.35/sh | N/A (FCF positive) | 1% | -3% |
| GNRC | Profitable growth | 341 | 865 | 1.8x | 4x | 2.0 | 4.52/sh | N/A (FCF positive) | 1% | -8% |
| TMO | Profitable growth | 10,105 | 29,533 | 2.6x | 6x | 1.9 | 16.69/sh | N/A (FCF positive) | 1% | -4% |
| IQV | Profitable growth | 2,141 | 13,659 | 4.1x | 3x | 0.7 | 11.82/sh | N/A (FCF positive) | 2% | -9% |
| ALB | Profitable growth | 1,618 | 1,679 | 3.0x | 0x | 2.2 | 5.88/sh | N/A (FCF positive) | 1% | -0% |
| SQM | Profitable growth | 2,729 | 3,067 | 1.9x | 6x | 3.3 | 1.53/sh | N/A (FCF positive) | 0% | 0% |
| GXO | Profitable growth | 854 | 1,765 | 2.5x | 2x | 0.8 | 0.95/sh | N/A (FCF positive) | 0% | -1% |
| LH | Profitable growth | 532 | 5,052 | 2.4x | 6x | 1.4 | 14.39/sh | N/A (FCF positive) | 1% | -9% |
| BIO | Profitable growth | 1,541 | -338 | net cash | 1x | 5.6 | 13.73/sh | N/A (FCF positive) | 2% | -8% |
| RVTY | Profitable growth | 920 | 2,320 | 3.0x | 4x | 1.7 | 4.37/sh | N/A (FCF positive) | 1% | -0% |

---

## B–F. Top 5 by theme

Ranked by Overall score among companies with a theme score of at least 5/10 (4/10 for blockchain, where few NYSE names have meaningful exposure).

### AI (21 eligible)
| # | Ticker | Theme score | Exposure / Growth pot. / Comp. pos. | Overall | Disruption | MoS | Rating |
|---|---|---|---|---|---|---|---|
| 1 | APH | 8/10 | 7/8/9 | 81 | 70 | 20% | ★★★★☆ |
| 2 | TSM | 10/10 | 10/9/10 | 80 | 83 | -7% | ★★★☆☆ |
| 3 | ANET | 10/10 | 9/9/8 | 72 | 73 | -43% | ★★☆☆☆ |
| 4 | VRT | 9/10 | 8/9/8 | 70 | 73 | -17% | ★★☆☆☆ |
| 5 | NOW | 9/10 | 8/8/8 | 70 | 72 | 4% | ★★★★☆ |

### Robotics (9 eligible)
| # | Ticker | Theme score | Exposure / Growth pot. / Comp. pos. | Overall | Disruption | MoS | Rating |
|---|---|---|---|---|---|---|---|
| 1 | APH | 5/10 | 7/8/9 | 81 | 70 | 20% | ★★★★☆ |
| 2 | UBER | 7/10 | 6/8/8 | 68 | 67 | 35% | ★★★★☆ |
| 3 | SYK | 7/10 | 6/7/8 | 56 | 63 | 14% | ★★★☆☆ |
| 4 | PATH | 6/10 | 7/7/5 | 52 | 58 | -15% | ★★☆☆☆ |
| 5 | DE | 7/10 | 5/7/8 | 51 | 65 | -53% | ★★☆☆☆ |

### Energy Storage (7 eligible)
| # | Ticker | Theme score | Exposure / Growth pot. / Comp. pos. | Overall | Disruption | MoS | Rating |
|---|---|---|---|---|---|---|---|
| 1 | VRT | 5/10 | 8/9/8 | 70 | 73 | -17% | ★★☆☆☆ |
| 2 | ETN | 6/10 | 7/8/8 | 54 | 72 | -29% | ★★☆☆☆ |
| 3 | ENS | 8/10 | 8/6/5 | 50 | 53 | -1% | ★★☆☆☆ |
| 4 | AMPX | 9/10 | 10/9/5 | 39 | 67 | -77% | ★☆☆☆☆ |
| 5 | GNRC | 6/10 | 5/6/6 | 37 | 54 | -48% | ★★☆☆☆ |

### Blockchain (6 eligible)
| # | Ticker | Theme score | Exposure / Growth pot. / Comp. pos. | Overall | Disruption | MoS | Rating |
|---|---|---|---|---|---|---|---|
| 1 | MA | 5/10 | 3/6/9 | 75 | 55 | 6% | ★★★★☆ |
| 2 | V | 5/10 | 3/6/9 | 66 | 55 | -1% | ★★★☆☆ |
| 3 | XYZ | 6/10 | 5/6/6 | 58 | 55 | 10% | ★★★★☆ |
| 4 | ICE | 4/10 | 3/6/8 | 50 | 46 | 3% | ★★☆☆☆ |
| 5 | CRCL | 10/10 | 10/9/7 | 45 | 72 | -63% | ★★☆☆☆ |

### Multiomics (8 eligible)
| # | Ticker | Theme score | Exposure / Growth pot. / Comp. pos. | Overall | Disruption | MoS | Rating |
|---|---|---|---|---|---|---|---|
| 1 | QGEN | 8/10 | 8/6/7 | 44 | 59 | 3% | ★★☆☆☆ |
| 2 | A | 6/10 | 5/6/6 | 40 | 52 | -37% | ★★☆☆☆ |
| 3 | DHR | 7/10 | 6/6/8 | 37 | 60 | -19% | ★★☆☆☆ |
| 4 | TMO | 7/10 | 5/6/9 | 36 | 61 | -41% | ★★☆☆☆ |
| 5 | IQV | 5/10 | 4/6/7 | 34 | 58 | -24% | ★★☆☆☆ |



**Theme commentary.**
- **AI:** APH is the best risk/reward. NOW is the best AI *software* pick at a fair price. TSM is the highest-quality business, fairly priced at 19x NTM with consensus FY26 revenue growth of about 43%. ANET and VRT are excellent businesses at expensive prices. ORCL (top-10 #8) is the highest-upside but highest-risk AI name.
- **Robotics:** UBER is the one cheap, high-growth name; its thesis is that autonomous vehicles are a demand-side opportunity rather than an extinction risk. SYK is a fair-value quality compounder; Mako has more than 2.5M procedures ([Globe and Mail, Jul 31, 2026](https://app.bigdata.com/documents/D3364E16863089E3AA9868A9675D10B2?cnum=12)). DE and ROK are cyclical and expensive at their trough.
- **Energy storage:** none is attractive. VRT and ETN are AI-power plays first. ENS is fair but low-growth. AMPX is speculative. ALB and SQM are lithium-price bets (see §G).
- **Blockchain:** MA, V and XYZ capture stablecoin and bitcoin flows without crypto-price dependence. CRCL is the pure play but overvalued on the model. ICE is a tokenization option, not a growth driver.
- **Multiomics:** no NYSE name passes the growth screen. QGEN (17x NTM, fairly valued) is the cheapest way to own sample-to-insight genomics. TMO has the best platform (Orbitrap Astral + Olink proteomics) but trades above both the model value and the consensus target.

---

## Growth × Value matrix

| Growth \ Valuation | **Cheap** (MoS ≥ 20%) | **Fair** (−10% to 20%) | **Expensive** (< −10%) |
|---|---|---|---|
| **High** (Growth ≥ 65) | ★★★ **UBER**, ORCL (leverage flag) | ★★★ **APH, NOW, TSM, XYZ** | ★ ANET, VRT, CLS, FN, PATH, CRCL, NET, SNOW, S, AMPX |
| **Medium** (40–65) | ★★★ — | ★★ **MA, SYK**, ENS, ICE | ★ DELL, ETN, TDY, BNY |
| **Low** (< 40) | ★★ — | ★ V, IBM, QGEN, ALB | Avoid: TMO, DHR, A, RVTY, BIO, LH, IQV, ROK, DE, CIEN, GNRC, GXO, SQM |

**Focus list (High growth + Cheap or Fair):** UBER, APH, NOW, TSM, XYZ, plus ORCL for risk-tolerant capital only.

---

## Multi-theme winners

Multi-theme score = 10 × (number of themes scoring ≥ 5) + 2 × (top two theme scores) + 0.15 × (Growth + Quality + Valuation).

| Rank | Ticker | Themes (score ≥5) | Theme scores | Growth | Quality | Valuation | MoS | Multi-theme score |
|---|---|---|---|---|---|---|---|---|
| 1 | APH | AI + Robotics | AI 8, Robotics 5 | 100 | 62 | 76 | 20% | 82 |
| 2 | UBER | Robotics + AI | Robotics 7, AI 6 | 86 | 42 | 95 | 35% | 79 |
| 3 | VRT | AI + Energy Storage | AI 9, Energy Storage 5 | 93 | 57 | 43 | -17% | 77 |
| 4 | PATH | AI + Robotics | AI 7, Robotics 6 | 75 | 45 | 42 | -15% | 70 |
| 5 | ETN | AI + Energy Storage | AI 8, Energy Storage 6 | 56 | 45 | 29 | -29% | 68 |
| 6 | AMPX | Energy Storage + Robotics | Energy Storage 9, Robotics 5 | 100 | 10 | 0 | -77% | 64 |
| 7 | DE | Robotics + AI | Robotics 7, AI 6 | 28 | 49 | 39 | -53% | 63 |
| 8 | ROK | Robotics + AI | Robotics 8, AI 5 | 25 | 57 | 7 | -48% | 59 |
| 9 | GNRC | Energy Storage + AI | Energy Storage 6, AI 5 | 19 | 25 | 40 | -48% | 55 |
| 10 | IQV | Multiomics + AI | Multiomics 5, AI 6 | 17 | 33 | 27 | -24% | 54 |

**Interpretation.**
- **APH (AI + Robotics):** the one company that is a picks-and-shovels supplier to both AI data centers and robots/automation, at a fair price.
- **UBER (Robotics + AI):** the leading demand aggregator if robotaxis scale.
- **VRT and ETN (AI + Energy storage):** the "AI needs power" trade. Both are good businesses, but expensive.
- **No NYSE company has strong exposure to three or more themes** at a reasonable price.

---

## Disruption scores (Ark-style)

| Ticker | AI | Robotics | Energy storage | Blockchain | Multiomics | Disruption | TAM expansion | Comp. advantage | **Disruption score /100** |
|---|---|---|---|---|---|---|---|---|---|
| TSM | 10 | 4 | 0 | 2 | 1 | 8 | 10 | 10 | **83** |
| ORCL | 10 | 0 | 0 | 1 | 0 | 8 | 10 | 8 | **75** |
| VRT | 9 | 0 | 5 | 0 | 0 | 8 | 9 | 7 | **73** |
| ANET | 10 | 1 | 0 | 0 | 0 | 8 | 9 | 8 | **73** |
| CRCL | 2 | 0 | 0 | 10 | 0 | 9 | 9 | 6 | **72** |
| NOW | 9 | 3 | 0 | 0 | 0 | 7 | 9 | 9 | **72** |
| ETN | 8 | 0 | 6 | 0 | 0 | 7 | 9 | 8 | **72** |
| APH | 8 | 5 | 2 | 0 | 0 | 6 | 9 | 8 | **70** |
| SNOW | 9 | 0 | 0 | 0 | 0 | 8 | 9 | 8 | **69** |
| NET | 8 | 0 | 0 | 2 | 0 | 8 | 9 | 8 | **68** |
| UBER | 6 | 7 | 0 | 0 | 0 | 7 | 9 | 7 | **67** |
| AMPX | 0 | 5 | 9 | 0 | 0 | 8 | 7 | 5 | **67** |
| ROK | 5 | 8 | 0 | 0 | 0 | 6 | 8 | 7 | **65** |
| DE | 6 | 7 | 0 | 0 | 0 | 6 | 8 | 8 | **65** |
| SYK | 4 | 7 | 0 | 0 | 0 | 6 | 8 | 8 | **63** |
| ALB | 0 | 0 | 9 | 0 | 0 | 6 | 9 | 6 | **62** |
| CIEN | 9 | 0 | 0 | 0 | 0 | 7 | 8 | 6 | **62** |
| DELL | 9 | 0 | 0 | 0 | 0 | 6 | 9 | 6 | **62** |
| SQM | 0 | 0 | 9 | 0 | 0 | 5 | 9 | 7 | **62** |
| TMO | 3 | 0 | 0 | 0 | 7 | 5 | 8 | 9 | **61** |
| CLS | 9 | 2 | 0 | 0 | 0 | 6 | 8 | 5 | **61** |
| FN | 9 | 2 | 0 | 0 | 0 | 6 | 8 | 5 | **61** |
| IBM | 7 | 0 | 0 | 3 | 1 | 6 | 8 | 7 | **60** |
| DHR | 2 | 0 | 0 | 0 | 7 | 5 | 8 | 9 | **60** |
| QGEN | 3 | 0 | 0 | 0 | 8 | 5 | 7 | 7 | **59** |
| PATH | 7 | 6 | 0 | 0 | 0 | 6 | 7 | 5 | **58** |
| IQV | 6 | 0 | 0 | 0 | 5 | 5 | 8 | 7 | **58** |
| TDY | 3 | 7 | 0 | 0 | 0 | 5 | 7 | 7 | **56** |
| MA | 3 | 0 | 0 | 5 | 0 | 4 | 8 | 10 | **55** |
| V | 3 | 0 | 0 | 5 | 0 | 4 | 8 | 10 | **55** |
| XYZ | 3 | 0 | 0 | 6 | 0 | 6 | 8 | 6 | **55** |
| RVTY | 3 | 0 | 0 | 0 | 7 | 5 | 7 | 6 | **55** |
| GNRC | 5 | 0 | 6 | 0 | 0 | 5 | 7 | 6 | **54** |
| ENS | 3 | 0 | 8 | 0 | 0 | 4 | 6 | 5 | **53** |
| S | 7 | 0 | 0 | 0 | 0 | 6 | 8 | 5 | **53** |
| A | 2 | 0 | 0 | 0 | 6 | 5 | 7 | 7 | **52** |
| LH | 2 | 0 | 0 | 0 | 6 | 4 | 7 | 6 | **49** |
| BIO | 0 | 0 | 0 | 0 | 7 | 4 | 6 | 6 | **48** |
| GXO | 3 | 6 | 0 | 0 | 0 | 5 | 6 | 4 | **47** |
| ICE | 2 | 0 | 0 | 4 | 0 | 4 | 6 | 9 | **46** |
| BNY | 0 | 0 | 0 | 5 | 0 | 4 | 6 | 7 | **43** |

---

## TAM and adoption (analyst estimates, low confidence)

These addressable-market figures are **the analyst's order-of-magnitude estimates, not sourced data**. They frame the scores; they are not inputs to the fair values.

| Ticker | Addressable market: today → 5y → 10y (analyst estimate) | TAM opportunity | Tech adoption | Market-share potential |
|---|---|---|---|---|
| APH | Interconnect ~$100B -> ~$160B -> ~$220B | 9/10 | 8/10 | 8/10 |
| TSM | Foundry ~$150B -> ~$300B (5y) -> ~$500B (10y) | 10/10 | 9/10 | 9/10 |
| MA | Digital payments ~$2.5T revenue pool; stablecoin settlement optionality | 8/10 | 7/10 | 8/10 |
| ANET | DC switching ~$50B -> ~$100B -> ~$150B | 9/10 | 9/10 | 8/10 |
| VRT | DC power & thermal ~$60B -> ~$120B -> ~$180B | 9/10 | 9/10 | 8/10 |
| NOW | Enterprise workflow + agentic AI ~$275B -> ~$500B -> ~$700B | 9/10 | 8/10 | 8/10 |
| CLS | AI hardware EMS/ODM ~$100B -> ~$200B -> ~$300B | 8/10 | 8/10 | 7/10 |
| UBER | Mobility + delivery GBV ~$1T -> AV ride-hail adds ~$0.5–1T (10y) | 9/10 | 6/10 | 7/10 |
| V | Digital payments ~$2.5T revenue pool; stablecoin settlement optionality | 8/10 | 7/10 | 8/10 |
| ORCL | Cloud infra + DB ~$400B -> ~$900B -> ~$1.5T | 10/10 | 9/10 | 7/10 |
| XYZ | Payments/fintech + bitcoin ~$200B gross profit pool | 8/10 | 6/10 | 6/10 |
| FN | Optical/photonic contract mfg ~$30B -> ~$60B -> ~$90B | 8/10 | 8/10 | 7/10 |
| SYK | Orthopedic robotics ~$5B -> ~$12B -> ~$25B within ~$60B ortho | 8/10 | 7/10 | 8/10 |
| DELL | AI servers + storage ~$200B -> ~$450B -> ~$600B | 9/10 | 8/10 | 7/10 |
| ETN | Electrical equipment ~$400B -> ~$600B -> ~$800B | 9/10 | 8/10 | 7/10 |
| PATH | Automation/agentic AI ~$30B -> ~$60B -> ~$90B | 7/10 | 6/10 | 4/10 |
| DE | Precision/autonomous ag ~$15B -> ~$40B -> ~$80B | 8/10 | 6/10 | 8/10 |
| NET | Edge network/security/AI inference ~$220B -> ~$400B -> ~$600B | 9/10 | 8/10 | 8/10 |
| ENS | Industrial/DC batteries ~$40B -> ~$60B -> ~$80B | 6/10 | 6/10 | 5/10 |
| ICE | Exchanges + mortgage tech + data; tokenized assets optionality | 6/10 | 5/10 | 6/10 |
| SNOW | Data cloud + AI data ~$340B -> ~$600B -> ~$900B | 9/10 | 8/10 | 7/10 |
| ROK | Industrial automation ~$200B -> ~$280B -> ~$380B | 8/10 | 7/10 | 6/10 |
| CRCL | Stablecoin float ~$300B -> ~$1–2T -> ~$3T+ | 9/10 | 7/10 | 6/10 |
| IBM | Hybrid cloud + AI consulting ~$600B -> ~$900B -> ~$1.2T | 8/10 | 7/10 | 5/10 |
| BNY | Custody/asset servicing; digital-asset & stablecoin-reserve custody optionality | 6/10 | 5/10 | 6/10 |
| QGEN | Sample-to-insight genomics ~$15B -> ~$25B -> ~$35B | 7/10 | 6/10 | 6/10 |
| S | Endpoint/cloud security ~$80B -> ~$140B -> ~$200B | 8/10 | 7/10 | 5/10 |
| TDY | Machine vision/sensors/drones ~$80B -> ~$120B -> ~$160B | 7/10 | 6/10 | 6/10 |
| CIEN | Optical networking ~$20B -> ~$40B -> ~$60B | 8/10 | 8/10 | 7/10 |
| A | Analytical/genomics tools ~$80B | 7/10 | 6/10 | 6/10 |
| AMPX | High-energy cells for drones/aviation ~$3B -> ~$15B -> ~$40B | 7/10 | 6/10 | 4/10 |
| DHR | Bioprocess + diagnostics + genomics ~$150B | 8/10 | 6/10 | 7/10 |
| GNRC | Backup power + home/C&I storage ~$30B -> ~$50B -> ~$70B | 7/10 | 6/10 | 6/10 |
| TMO | Life-science tools ~$250B; omics/sequencing workflows ~$60B -> ~$110B -> ~$180B | 8/10 | 6/10 | 7/10 |
| IQV | Pharma services + health data ~$150B | 8/10 | 6/10 | 6/10 |
| ALB | Lithium ~$35B -> ~$70B -> ~$120B | 9/10 | 8/10 | 7/10 |
| SQM | Lithium ~$35B -> ~$70B -> ~$120B | 9/10 | 8/10 | 7/10 |
| GXO | Contract logistics + automation ~$500B -> ~$650B -> ~$800B | 6/10 | 6/10 | 5/10 |
| LH | US lab testing ~$100B; genomic/oncology testing ~$15B -> ~$30B | 7/10 | 6/10 | 6/10 |
| BIO | ddPCR/single-cell/proteomics tools ~$15B | 6/10 | 5/10 | 4/10 |
| RVTY | Genomic screening + life-science software ~$20B | 7/10 | 6/10 | 5/10 |

---

## TOP 10 HIGH-CONVICTION STOCKS

Ranked by risk-adjusted attractiveness: Overall score, margin of safety, star rating and red flags. **The expected returns are model outputs.** They assume NTM EPS compounds at the forward consensus growth rate (capped at 40%), 70% of that rate in years 4–5, and an exit at the fair P/E (90% of it at year 5), with no dividends. **Haircut them by 30–40% for realism.**

| # | Ticker | Price | Bear / **Base** / Bull FV | MoS | Ideal entry | 3-yr exp. return* | 5-yr exp. return* | Rating |
|---|---|---|---|---|---|---|---|---|
| 1 | **UBER** | $68.45 | $73 / **$105** / $142 | 35% | ≤ $78 (now) | ~43%/yr | ~31%/yr | ★★★★☆ (filter PASS) |
| 2 | **APH** | $87.55 | $75 / **$109** / $146 | 20% | ≤ $82 | ~26%/yr | ~20%/yr | ★★★★☆ (filter PASS) |
| 3 | **TSM** (ADR) | $472.20 | $296 / **$440** / $602 | −7% | ≤ $330 | ~36%/yr | ~27%/yr | ★★★☆☆ |
| 4 | **NOW** | $137.87 | $103 / **$144** / $189 | 4% | ≤ $108 | ~25%/yr | ~18%/yr | ★★★★☆ |
| 5 | **MA** | $570.06 | $465 / **$607** / $746 | 6% | ≤ $455 | ~19%/yr | ~13%/yr | ★★★★☆ |
| 6 | **XYZ** | $76.07 | $61 / **$85** / $112 | 10% | ≤ $64 | ~35%/yr | ~25%/yr | ★★★★☆ |
| 7 | **SYK** | $275.40 | $244 / **$322** / $406 | 14% | ≤ $241 | ~26%/yr | ~16%/yr | ★★★☆☆ |
| 8 | **ORCL** | $143.56 | $88 / **$204** / $377 | 30% | ≤ $153 (now), *speculative sizing* | ~50%/yr | ~37%/yr | ★★☆☆☆ (leverage flag) |
| 9 | **V** | $372.10 | $289 / **$369** / $452 | −1% | ≤ $277 | ~17%/yr | ~11%/yr | ★★★☆☆ |
| 10 | **ANET** | $215.83 | $104 / **$151** / $206 | −43% | ≤ $113 | ~14%/yr | ~13%/yr | ★★☆☆☆ (quality, wait for price) |

\* Model outputs, before the 30–40% haircut recommended above. **Consensus price targets for comparison:** UBER $104.7, APH $102.5, NOW $146.0, MA $670.4, XYZ $97.5, SYK $368.1, ORCL $236.5, V $425.5, ANET $226.6. TSM's ADR target is N/A in the data.

### 1. Uber Technologies (UBER): Robotics (autonomous vehicles) + AI. Filter PASS, Excellent margin of safety

1. **Thesis.**
   - A global mobility and delivery network generating more than $10B of trailing-12-month FCF ([Quartr - Aug 05, 2026](https://app.bigdata.com/documents/81B2A5B12A3CF73841F657BA415666EB)).
   - It trades at ~16x NTM EPS because the market fears robotaxis will bypass it.
   - The thesis: autonomous vehicles need demand aggregation and utilization, and Uber is the largest aggregator.
2. **Disruptive technology.** Autonomous ride-hail and delivery.
   - Partnerships include Waymo, WeRide, Wayve, Pony.ai, Avride, Motional, Zoox and Nuro.
   - **Up to $1.25B invested in Rivian, with an option on 50,000 robotaxis** ([Globe and Mail - Oct 07, 2026](https://app.bigdata.com/documents/5117ECF10C90BA28A1F9E3FDEF95C385?cnum=3)).
   - **About 120,000 AV vehicle commitments** ([Quartr - Aug 05, 2026](https://app.bigdata.com/documents/81B2A5B12A3CF73841F657BA415666EB)).
3. **Why the opportunity is large.** Mobility and delivery gross bookings are already ~$1T globally. Lower AV cost per mile expands trips (analyst estimate).
4. **Competitive advantage.** Two-sided network liquidity in roughly 70 countries, cross-selling between mobility and delivery, and the Uber One membership.
5. **Revenue growth potential.**
   - Q2 2026 gross bookings rose **22% y/y to more than $58B** (same source).
   - Consensus sales: $57.8B (FY26) → $75.8B (FY28).
   - Model base case: ~13% revenue CAGR.
6. **Profitability potential.** Operating margin is 11% (FY25). The base case reaches 14% operating and 18% FCF margin by year 5. Note: FY24–25 GAAP net income is inflated by tax-valuation-allowance releases.
7. **Fair value.** Base **$105**: DCF $111, earnings $94, FCF $104, historical $106.
8. **Bear / base / bull.**

   | Case | Revenue growth (yrs 1–5) | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 8% | 11% | 14% | $3.13 | 10.5% | $73 |
   | Base | 13% | 14% | 18% | $5.00 | 10.0% | $105 |
   | Bull | 17% | 17% | 21% | $7.23 | 9.5% | $142 |

   Terminal growth is 3% in all three cases.
9. **Ideal entry.** ≤ $78 (25% margin of safety). The current price is already below it.
10. **3-year expected return.** ~43%/yr (model), ~26–30%/yr after the haircut.
11. **5-year expected return.** ~31%/yr (model), ~19–22%/yr after the haircut.
12. **Biggest risk.** **Robotaxi disintermediation.** Waymo has taken roughly a quarter of San Francisco ride-hailing, and the Atlanta and Austin partnerships reportedly end in 2028 ([Yahoo! Finance - Sep 22, 2026](https://app.bigdata.com/documents/A7BDBF6CBD4848BD4BF1E2C1A385609F?cnum=2)). Also: Delivery Hero integration, with close assumed in H2 2027.
13. **Invalidation.** Waymo or Tesla building scaled first-party networks in Uber's top 10 cities, *and* Uber's AV trips stalling below a low-single-digit share of trips.

### 2. Amphenol (APH): AI + Robotics. Filter PASS, Reasonable-to-Attractive

1. **Thesis.** A connector and interconnect leader riding AI data-center buildouts.
   - Q2 2026 sales rose **55% y/y to $8.8B (+30% organic)**.
   - Orders were **$10.7B (+94%), a book-to-bill of 1.23** ([TIKR](https://www.tikr.com/blog/amphenols-q2-earnings-beat-every-estimate-the-commscope-bet-is-paying-off-faster-than-expected); [MarketBeat - Jul 29, 2026](https://www.marketbeat.com/instant-alerts/amphenol-q2-earnings-call-highlights-2026-07-29/)).
   - It trades at ~28x NTM EPS with a PEG of about 1.2.
2. **Disruptive technology.** High-speed copper and optical interconnect for AI racks: **IT datacom is 43% of sales, +89% y/y** (same sources). Sensors and connectors also serve robotics, EVs and defense.
3. **Why the opportunity is large.** Each AI rack needs far more interconnect content than prior generations. The analyst's TAM estimate is ~$100B today rising to ~$220B in 10 years.
4. **Competitive advantage.**
   - A decentralized, acquisitive operating model.
   - Broad catalog and custom-design wins.
   - ROIC of 28% and an operating margin of 25% (FY25, SEC data).
5. **Revenue growth.** Revenue CAGRs are 22% over both 3 and 5 years (FY25 +52%), but that includes acquisitions. **CommScope CCS is expected to contribute ~$4.6B of 2026 sales** (same sources).
   - Q3 2026 guidance: sales of $9.3–9.4B (+50–52%).
6. **Profitability.** Adjusted operating margin was 29.8% in Q2 2026. The base case assumes a 26% GAAP operating margin and a 17% FCF margin.
7. **Fair value.** Base **$109**: DCF $114, earnings $95, FCF $128, historical $95.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 10% | 24% | 15% | $5.52 | 9.5% | $75 |
   | Base | 17% | 26% | 17% | $8.14 | 9.0% | $109 |
   | Bull | 21% | 27% | 19% | $10.00 | 8.5% | $146 |

   Terminal growth is 3% in all three cases.
9. **Ideal entry.** ≤ $82.
10. **3-year expected return.** ~26%/yr (model).
11. **5-year expected return.** ~20%/yr (model).
12. **Biggest risk.** The AI capex cycle. IT datacom is 43% of sales and concentrated in hyperscalers.
13. **Invalidation.** Book-to-bill falling below 1.0 for two quarters, or the IT datacom share falling with no offset from other markets.

### 3. Taiwan Semiconductor (TSM ADR): AI (core) + Robotics. Fairly valued, best-in-class quality

1. **Thesis.** TSMC is the monopoly-like foundry for leading-edge AI accelerators.
   - FY26 revenue guidance was raised to **slightly above 40% growth in USD** ([Quartr - Jul 16, 2026](https://app.bigdata.com/documents/06C7F92371AB2A1E81899B8CEFED270C)).
   - It trades at ~19x NTM EPS with a PEG of 0.65.
2. **Disruptive technology.** 3nm and 2nm logic plus CoWoS advanced packaging. The 2nm ramp supports Q3 2026 (same source).
3. **Opportunity.** Foundry TAM of ~$150B today → ~$500B in 10 years (analyst estimate). Consensus revenue is TWD 5.46T (FY26) → TWD 11.7T (FY29).
4. **Competitive advantage.** Process leadership, scale, and customer trust. Gross margin is 60%, operating margin 51% and ROIC 25% (FY25).
5. **Revenue growth.** 3-year CAGR of 19% (FY22–25) and +32% in FY25. Consensus implies a ~30% CAGR to FY29; the model base case uses 25%.
6. **Profitability.** Overseas fabs dilute gross margin by 2–3 percentage points early, widening to 3–4 points later (same source). Capex is about 33% of revenue.
7. **Fair value.** Base **$440/ADR**: DCF $449, earnings $550, FCF $240, historical $500. The FCF leg is depressed by peak capex.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS/ADR | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 16% | 45% | 27% | $20.11 | 10.5% | $296 |
   | Base | 25% | 50% | 31% | $32.47 | 9.5% | $440 |
   | Bull | 31% | 53% | 34% | $43.51 | 9.0% | $602 |

   Terminal growth is 3% in all three cases. FX was converted at the market-cap-implied rate of 0.0367 USD/TWD, with 5 shares per ADR.
9. **Ideal entry.** ≤ $330. A 10–15% margin of safety (≈ $375–395) is reasonable for this quality.
10. **3-year expected return.** ~36%/yr (model).
11. **5-year expected return.** ~27%/yr (model).
12. **Biggest risk.** Taiwan geopolitics and an AI capex digestion phase.
13. **Invalidation.** Losing 2nm leadership to Intel 18A or 14A or to Samsung, or a multi-quarter decline in AI wafer orders.

### 4. ServiceNow (NOW): AI software + automation. Fairly valued

1. **Thesis.** Agentic-AI workflow is becoming a monetization layer on top of an entrenched enterprise platform.
   - Deal volume among first-time AI buyers grew more than 45%, with a **20–30% price uplift on AI SKUs** ([Quartr - Jul 22, 2026](https://app.bigdata.com/documents/E23A87D24A4660CDDDAFB6EF7634E88D?cnum=26&cnum=27&cnum=49&cnum=50&cnum=45)).
2. **Disruptive technology.** AI agents (Now Assist, AI Control Tower) applied to IT, HR, customer service and security workflows.
3. **Opportunity.** Enterprise workflow plus agentic AI: ~$275B → ~$700B (analyst estimate).
4. **Competitive advantage.** System-of-record lock-in, a single data model, and a 78% gross margin.
5. **Revenue growth.** 3-year CAGR of 22%. FY26 subscription guidance is $15.755–15.770B (+21% constant currency), with Q3 guided to +20% (same source).
6. **Profitability.** FY26 guidance: operating margin 31.5% and FCF margin 35% (non-GAAP). **SBC is 14.7% of revenue**, so the DCF uses SBC-adjusted FCF (about 20% of revenue).
7. **Fair value.** Base **$144**: DCF $114, earnings $146, FCF $143, historical $219.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin (SBC-adj.) | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 11% | 26% | 19% | $4.39 | 9.5% | $103 |
   | Base | 17% | 30% | 24% | $6.59 | 9.0% | $144 |
   | Bull | 21% | 33% | 28% | $8.58 | 8.5% | $189 |

   Terminal growth is 3% in all three cases.
9. **Ideal entry.** ≤ $108.
10. **3-year expected return.** ~25%/yr (model).
11. **5-year expected return.** ~18%/yr (model).
12. **Biggest risk.** AI agents shrink seat counts faster than AI SKUs raise prices. The subscription gross margin is also guided down to 81% (same source).
13. **Invalidation.** cRPO growth falling below 15%, or net-new AI ACV stalling.

### 5. Mastercard (MA): Blockchain (stablecoin settlement) + AI (fraud/tokenization). Fairly valued

1. **Thesis.** A toll road on digital payments that is adding stablecoin settlement rather than being disrupted by it.
   - Q2 2026 net revenue was **~$9.3B, +14%** ([Mastercard 8-K](https://www.sec.gov/Archives/edgar/data/0001141391/000114139126000081/ma06302026-exx991xearnings.htm)).
   - Value-added services grew **+20%** ([Pulse 2](https://pulse2.com/mastercards-value-added-services-revenue-jumps-20-as-business-becomes-major-growth-engine/)).
2. **Disruptive technology.** On-chain card settlement with regulated stablecoins (USDC, PYUSD, RLUSD and others) ([The Block](https://www.theblock.co/post/403474/mastercard-expands-stablecoin-settlement-options-with-usdc-pyusd-and-rlusd)). Also the reported BVNK stablecoin-infrastructure acquisition (web search; verify), plus AI-based fraud scoring.
3. **Opportunity.** Card and A2A rails plus value-added services in a ~$2.5T global payments revenue pool (analyst estimate).
4. **Competitive advantage.** A network-effect duopoly. Operating margin is 58%, FCF margin 52% (FY25).
5. **Revenue growth.** Revenue CAGRs of 14% (3-year) and 16% (5-year), with year-to-date growth of +15%.
6. **Profitability.** Already best-in-class. The upside is in VAS mix.
7. **Fair value.** Base **$607**: DCF $559, earnings $628, FCF $594, historical $718.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 8% | 56% | 48% | $23.53 | 9.0% | $465 |
   | Base | 12% | 58% | 50% | $29.23 | 8.5% | $607 |
   | Bull | 14% | 60% | 52% | $33.03 | 8.0% | $746 |

   Terminal growth is 3% in all three cases.
9. **Ideal entry.** ≤ $455. Accumulating at or below the ~$520 bear-to-base midpoint is reasonable for a low-risk compounder.
10. **3-year expected return.** ~19%/yr (model).
11. **5-year expected return.** ~13%/yr (model).
12. **Biggest risk.** Interchange regulation and litigation, or stablecoins bypassing card rails at the merchant.
13. **Invalidation.** A sustained decline in cross-border volume growth, or regulation that caps network fees.

### 6. Block (XYZ): Blockchain (bitcoin) + AI. Reasonable margin of safety

1. **Thesis.** Cash App and Square trade at ~15x NTM EPS. Bitcoin swings reported revenue but barely affects profit: **bitcoin was 45% of Cash App revenue but only 3% of Cash App gross profit**, and ex-bitcoin Cash App revenue grew +32% ([Block 10-Q - Aug 05, 2026](https://app.bigdata.com/documents/03BCD7E8C1A8A5986FDF183CF93F1251?cnum=104)).
2. **Disruptive technology.** Bitcoin payments, Bitkey self-custody, Proto mining hardware, and USDC support (negligible revenue today) ([Globe and Mail - Sep 29, 2026](https://app.bigdata.com/documents/763904ED89642B2B9A683390323FE9BD?cnum=4)).
3. **Opportunity.** Consumer fintech and SMB payments. A national trust bank charter is being pursued (same source).
4. **Competitive advantage.** Medium. Cash App network effects compete against PayPal/Venmo, banks and Robinhood.
5. **Revenue growth.** The 3-year revenue CAGR of 11% is distorted by bitcoin. FY26 adjusted EPS guidance was raised to **$4.02** ([MT Newswires - Aug 06, 2026](https://app.bigdata.com/documents/E32AF05F620427129E5A7DA9625CBB32?cnum=1)).
6. **Profitability.** Operating margin is 13% (FY25), rising from 2% in FY23. Base case: 12% operating margin and 10% FCF margin.
7. **Fair value.** Base **$85**: DCF $80, earnings $91, FCF $76, historical $101.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 5% | 10% | 8% | $3.92 | 11.0% | $61 |
   | Base | 9% | 12% | 10% | $5.67 | 10.0% | $85 |
   | Bull | 12% | 14% | 12% | $7.57 | 9.5% | $112 |

   Terminal growth is 3% in all three cases.
9. **Ideal entry.** ≤ $64.
10. **3-year expected return.** ~35%/yr (model). Haircut heavily: the consensus FY30 sales figure looks inconsistent, which signals thin coverage of the outer years.
11. **5-year expected return.** ~25%/yr (model).
12. **Biggest risk.** Credit losses in lending (Afterpay, Borrow), plus execution after the reported layoffs.
13. **Invalidation.** Cash App gross-profit growth falling below 10%.

### 7. Stryker (SYK): Robotics (Mako). Reasonable margin of safety

1. **Thesis.** A quality medtech compounder at ~17x NTM EPS after a −25% decline over one year.
   - Q2 2026 adjusted EPS rose **17.9%**; FY26 organic growth is guided to **8.3–9.3%** ([Quartr - Jul 30, 2026](https://app.bigdata.com/documents/1F3E422F6E278B9C498440D2A5323811?cnum=14&cnum=4&cnum=13&cnum=48)).
2. **Disruptive technology.** Mako SmartRobotics for knee, hip, spine and shoulder. More than 2.5M procedures, best-ever Q2 installs, and the Mako RPS launch ([Globe and Mail - Jul 31, 2026](https://app.bigdata.com/documents/D3364E16863089E3AA9868A9675D10B2?cnum=12)).
3. **Opportunity.** Orthopedic robotics: ~$5B → ~$25B within a ~$60B orthopedics market (analyst estimate).
4. **Competitive advantage.** Mako's installed base and implant pull-through.
5. **Revenue growth.** 3-year CAGR of 11% (includes acquisitions such as Inari). Consensus sales: $27.2B (FY26) → $31.9B (FY28).
6. **Profitability.** Adjusted operating margin was 27.4% (Q2); GAAP was 19% (FY25).
7. **Fair value.** Base **$322**: DCF $247, earnings $394, FCF $303, historical $427.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 5% | 23% | 15% | $15.24 | 9.0% | $244 |
   | Base | 8% | 25% | 17% | $19.07 | 8.5% | $322 |
   | Bull | 10% | 27% | 19% | $22.57 | 8.0% | $406 |

   Terminal growth is 3% in all three cases.
9. **Ideal entry.** ≤ $241.
10. **3-year expected return.** ~26%/yr (model).
11. **5-year expected return.** ~16%/yr (model).
12. **Biggest risk.** **CEO transition**: Kevin Lobo is stepping down ([8-K - Oct 06, 2026](https://app.bigdata.com/documents/6349593A58E192865144D7A8999D57F0?cnum=21)). Net debt is $12.3B after acquisitions.
13. **Invalidation.** Organic growth below 6%, or Mako share loss to J&J (Velys) or Zimmer (ROSA).

### 8. Oracle (ORCL): AI cloud infrastructure. High upside, significant balance-sheet red flag

1. **Thesis.** RPO (contracted backlog) stood at **$638B, +363% y/y** at the end of Q4 FY26 ([Oracle 8-K - Jun 10, 2026](https://app.bigdata.com/documents/7433D60CC460B11C881DB4E59647D187?cnum=10)). FY27 revenue is guided to +34% ([Quartr - Jun 10, 2026](https://app.bigdata.com/documents/3653D21D1CDC2C28D37AF11C78F07D68?cnum=47&cnum=23)). The stock trades at ~15x NTM EPS after a −49% decline over one year.
2. **Disruptive technology.** OCI GPU capacity for AI training and inference, plus AI-vector databases. Cloud is now **60% of revenue** ([10-Q - Sep 11, 2026](https://app.bigdata.com/documents/EF37BE6099EB6B88444F99235B8F8667?cnum=60&cnum=58&cnum=59)).
3. **Opportunity.** AI cloud infrastructure: ~$400B → ~$1.5T (analyst estimate). Consensus revenue: $90B (FY27) → $272B (FY31).
4. **Competitive advantage.** Database lock-in and multicloud distribution. In AI infrastructure itself it competes on price and speed (medium moat).
5. **Revenue growth.** Year-to-date growth is +30%. The base case uses a 30% CAGR.
6. **Profitability.** **FY26 FCF was −$23.7B on $55.7B of capex.** The base case assumes FCF recovers to a 20% margin by year 5. That assumption carries the whole valuation, which is why the bear value of $88 is far below the bull value of $377.
7. **Fair value.** Base **$204**: DCF $204, earnings $187, historical $233. The FCF leg is N/A because FCF is negative.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 18% | 28% | 12% | $11.69 | 11.0% | $88 |
   | Base | 30% | 32% | 20% | $21.69 | 10.0% | $204 |
   | Bull | 38% | 36% | 26% | $32.89 | 9.5% | $377 |

   Terminal growth is 3% in all three cases.
9. **Ideal entry.** ≤ $153 on the base value (the current price qualifies). **Size as a speculative position.**
10. **3-year expected return.** ~50%/yr (model; very high variance).
11. **5-year expected return.** ~37%/yr (model).
12. **Biggest risk.**
    - **Leverage and financing:** net debt is about $125B. Oracle raised $43B of debt and $5B of equity in FY26 and plans about $40B more in FY27, including a **$20B at-the-market equity program** ([8-K](https://app.bigdata.com/documents/7433D60CC460B11C881DB4E59647D187?cnum=10)).
    - **Counterparty concentration:** some customers are "highly leveraged" AI labs ([10-K](https://app.bigdata.com/documents/0D9D23892B0F67C68848BE5880D16C8C?cnum=78)).
13. **Invalidation.** RPO cancellations, an AI-lab customer default, or FCF still negative in FY28.

### 9. Visa (V): Blockchain (stablecoin settlement) + AI. Fairly valued

1. **Thesis.** The same toll-road economics as MA, with an even higher margin (operating margin 60%, FCF margin 54%). Year-to-date revenue growth is +16%.
2. **Disruptive technology.** Stablecoin settlement pilots and tokenization, plus AI-based risk and agentic-commerce credentials. (No specific Visa document was cited because Bigdata.com search was unavailable; exposure is per company disclosures in general terms.)
3. **Opportunity.** The same payments revenue pool as MA.
4. **Competitive advantage.** The strongest payments network globally (moat 10/10).
5. **Revenue growth.** 3-year CAGR of 11%; the 5-year CAGR is 13%.
6. **Profitability.** Already at the top of the industry. EPS growth comes from volume and buybacks.
7. **Fair value.** Base **$369**: DCF $322, earnings $409, FCF $372, historical $424.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 7% | 60% | 50% | $14.88 | 9.0% | $289 |
   | Base | 10% | 62% | 52% | $17.66 | 8.5% | $369 |
   | Bull | 12% | 64% | 54% | $19.95 | 8.0% | $452 |

   Terminal growth is 3% in all three cases. EPS history is from net income, because the SEC data has no class-level EPS tag.
9. **Ideal entry.** ≤ $277. Accumulating at ≤ $330 (about a 10% margin of safety) is reasonable given the low risk.
10. **3-year expected return.** ~17%/yr (model).
11. **5-year expected return.** ~11%/yr (model).
12. **Biggest risk.** DOJ antitrust action and interchange caps.
13. **Invalidation.** Payment-volume growth falling to mid-single digits.

### 10. Arista Networks (ANET): AI networking. Highest quality, but wait for the price

1. **Thesis.** The leader in Ethernet for AI back-end fabrics. FY26 guidance was raised a third time to **~40% growth (~$12.6B)**, with an **AI fabrics goal of at least $3.5B** ([Quartr - Aug 04, 2026](https://app.bigdata.com/documents/E8743C13A5F68B9A9F09E884D36E908C)).
2. **Disruptive technology.** Scale-out and scale-across Ethernet replacing InfiniBand in AI clusters.
3. **Opportunity.** Data-center switching: ~$50B → ~$150B (analyst estimate). Consensus sales: $12.7B (FY26) → $25.1B (FY29).
4. **Competitive advantage.** EOS software, merchant-silicon agility, and depth with the cloud titans. Operating margin is 43% (FY25); Q3 is guided to 48–49% non-GAAP (same source).
5. **Revenue growth.** 3-year CAGR of 27%; year-to-date +36%.
6. **Profitability.** Already elite (FCF margin 47%).
7. **Fair value.** Base **$151**: DCF $144, earnings $162, FCF $132, historical $177. At 43x NTM EPS the price embeds more than the base case.
8. **Bear / base / bull.**

   | Case | Revenue growth | Operating margin | FCF margin | Year-5 EPS | Discount rate | FV |
   |---|---|---|---|---|---|---|
   | Bear | 15% | 40% | 35% | $4.49 | 10.0% | $104 |
   | Base | 24% | 43% | 40% | $7.03 | 9.5% | $151 |
   | Bull | 30% | 45% | 44% | $9.32 | 9.0% | $206 |

   Terminal growth is 3% in all three cases. The DCF starts from FY25 revenue, which understates the base given +36% year-to-date growth. That is a known model limitation.
9. **Ideal entry.** ≤ $113 under the strict rule. A more practical accumulate zone is $150–165, near the base value.
10. **3-year expected return.** ~14%/yr (model).
11. **5-year expected return.** ~13%/yr (model).
12. **Biggest risk.** Customer concentration in a few cloud titans, plus memory and silicon supply costs ([10-Q - Aug 05, 2026](https://app.bigdata.com/documents/1F9C32636C5A55961A2B567065BE0C64?cnum=45)).
13. **Invalidation.** A major hyperscaler shifting AI fabrics to white-box or Nvidia Spectrum-X networking.


---

## Early-stage disruptors (separate category)

Current profitability is weak, but the technology and TAM could justify substantial growth. These are **not** valued on the main framework's terms and are sized as options.

| Ticker | Theme | Price | Mkt cap | Revenue (latest FY) | Revenue growth | FCF (latest FY) | Cash & ST inv. | Cash runway | Dilution | Model base FV | Rating | Key point |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **SNOW** | AI data | $332.85 | $117B | $4.68B (FY Jan-26) | +29% FY; +34% YTD | +$1.12B, but **−$0.5B after SBC** (SBC 34% of revenue) | $4.0B | N/A (FCF positive before SBC) | +6% / 3y | $186 | ★★☆☆☆ | Real AI data franchise. Not profitable on a GAAP basis yet, and ~23x EV/sales. |
| **NET** | AI edge / security | $342.97 | $122B | $2.17B | +30%; +35% YTD | +$0.26B (SBC 21% of revenue) | $4.1B | N/A | +7% / 3y | $110 | ★★☆☆☆ | Strongest edge-network platform, but about 40x sales. Price assumes perfection. |
| **S** | AI security | $25.31 | $8.8B | $1.00B (FY Jan-26) | +22%; +21% YTD | +$0.05B (SBC 30% of revenue) | $0.63B | N/A | +19% / 3y | $18.92 | ★★☆☆☆ | Sub-scale against CrowdStrike/Microsoft; SBC-heavy. |
| **AMPX** | Silicon-anode batteries | $9.33 | $1.4B | $0.07B | +202%; +137% YTD | −$0.04B | $0.09B (FY25) | **~2.5 yrs** | **+75% / 3y** | $5.28 | ★☆☆☆☆ | Leading energy density for drones and aviation. Tiny revenue base, heavy dilution. |
| **JOBY** | eVTOL / autonomy | $5.75 | $5.7B | $0.05B (first revenue) | N/M | −$0.56B | $1.41B | **~2.5 yrs** | **+42% / 3y** (586M → 826M shares) | N/M (pre-revenue) | ★☆☆☆☆ | Certification and commercial launch pending. Consensus EPS stays negative through FY29 (−$0.45). |
| **ACHR** | eVTOL / autonomy | $4.67 | $3.6B | $0.3M | N/M | −$0.54B | $1.96B | **~3.6 yrs** | **+160% / 3y** (240M → 624M shares) | N/M (pre-revenue) | ★☆☆☆☆ | Better funded than JOBY. Consensus sees first positive EPS only in FY29 ($0.06, one analyst). |
| **CRCL** | Stablecoins | $80.84 | $20.5B | $2.75B | +64% | +$0.53B (≈ −$0.03B after SBC) | $1.5B corporate | N/A | IPO-related | $49.52 | ★★☆☆☆ | GAAP loss in FY25. Revenue is mostly reserve interest income (see the red-flag table). |
| **BLSH** | Crypto exchange | $31.82 | $5.1B | N/M (gross trading volume booked as revenue) | N/M | +$0.02B | N/A (corporate cash not separable in the data) | N/A | — | not modelled | ★☆☆☆☆ | Consensus EPS of $0.46 (FY26) → $1.50 (FY27). Earnings depend directly on crypto volumes. |
| **BKKT** | Crypto infrastructure | $7.27 | $0.33B | N/M (gross crypto) | N/M | −$0.15B | $0.03B (EDGAR cash tag; verify) | **< 1 yr on this data** | Reverse split; heavy dilution | not modelled | ★☆☆☆☆ | Below $1B and cash-constrained. **Avoid.** |

---

## G. Red-flag check (shortlist)

| Ticker | Excessive valuation | Debt | Cash burn | Dilution | SBC | Weak moat | One-product dependence | Regulatory | Obsolescence | Customer concentration | Execution | Subsidies | Crypto prices | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UBER | No (16x NTM) | No (0.7x) | No | +7% / 3y | 3.5% | — | Ride-hail + delivery | Driver classification | **Robotaxi disintermediation** (Waymo/Tesla) | No | Delivery Hero integration | No | No | **Moderate** |
| APH | Moderate (28x) | No (0.5x) | No | Low | 1% | No | No | Tariffs | Low | AI hyperscalers | CommScope integration | No | No | **Clean–moderate** |
| TSM | No (19x) | Net cash | No | No | 0% | No | Leading-edge logic | Export controls | Low | Top AI customers | Overseas-fab margin dilution | US CHIPS grants (minor) | No | **Moderate (geopolitics)** |
| NOW | Moderate (28x adj.) | Net cash; $2.1B commercial paper | No | +3% / 3y | **14.7%** | No | Workflow platform | — | **AI-agent seat disruption** | No | Acquisitions | No | No | Moderate |
| MA | No (25x) | 0.4x | No | Buybacks | 2% | No | No | **Interchange regulation and litigation** | Stablecoin bypass (low) | No | No | No | No | **Clean** |
| XYZ | No (15x) | Net cash | No | +8% / 3y | 5% | Moderate | Cash App + Square | Bank-charter process | Fintech competition | No | Reported layoffs | No | **Low** (bitcoin is 29% of revenue but ~3% of gross profit) | Moderate |
| SYK | No (17x) | 2.0x | No | No | 1% | No | No | Medical-device regulation | Low | No | **CEO transition (Oct 2026)** | No | No | Clean–moderate |
| ORCL | No on P/E (15x) | **Yes (~3.7x; net debt ~$125B)** | **FCF −$23.7B** | **$20B ATM equity planned** | 7.1% | No | OCI AI capacity | — | GPU-cycle risk | **Yes (leveraged AI labs)** | Data-center build-out | No | No | **Significant red flag** |
| V | Moderate (25x) | 0.3x | No | Buybacks | 2% | No | No | **Interchange and DOJ** | Stablecoin bypass (low) | No | No | No | No | Clean |
| ANET | **Yes (43x NTM)** | Net cash | No | No | 5% | No | Switching | — | Low | **Yes (cloud titans)** | Supply costs | No | No | Valuation flag |
| CRCL | **Yes (57x)** | Corporate net cash | No | IPO-related | **20.6%** | Moderate | **USDC reserve income** | **Stablecoin regulation** | Competing stablecoins | Coinbase distribution economics | — | No | Indirect (USDC demand) | **Significant red flag (rate sensitivity)** |
| ALB / SQM | No (10x / 9x on peak-ish EPS) | ALB 3.0x | ALB burned cash 2023–24 | ALB convertible preferred | Low | Commodity | Lithium | **SQM loses control of its Atacama JV to Codelco after 2030** | Sodium-ion / LFP chemistries | Battery makers | ALB Greenbushes fire delay | — | No | **Cyclical, avoid as a "growth" pick** |
| TMO / DHR / A / RVTY / IQV | **Yes (24–27x for 0–6% growth)** | IQV 4.1x; RVTY 3.0x | No | No | Low | No | No | NIH/pharma funding | Low | Pharma (~60% for TMO) | — | — | No | Growth too low, not a red flag |

---

## H. Final classification

| Rating | Definition | Companies |
|---|---|---|
| ★★★★★ | High growth + high quality + undervalued | **None** at Oct 7, 2026 prices |
| ★★★★☆ | High growth + reasonable valuation | **APH, UBER, NOW, MA, XYZ** |
| ★★★☆☆ | Excellent technology, fairly valued | **TSM, SYK, V, IBM** |
| ★★☆☆☆ | Attractive theme but excessive valuation or risk | ANET, VRT, CLS, ORCL, FN, DELL, ETN, PATH, DE, NET, SNOW, ENS, ICE, ROK, CRCL, BNY, QGEN, S, TDY, CIEN, A, DHR, GNRC, TMO, IQV, ALB, SQM, GXO, LH, BIO, RVTY |
| ★☆☆☆☆ | Speculative / avoid | AMPX, JOBY, ACHR, BLSH, BKKT |

**Watch-list entry prices (25% margin of safety on the base fair value):**
- **TSM:** ≤ $330.
- **ANET:** ≤ $113.
- **VRT:** ≤ $158.
- **NOW:** ≤ $108.
- **MA:** ≤ $455.
- **APH:** ≤ $82.
- **SYK:** ≤ $241.

---

## Data sources

**Structured data.**
- **[Bigdata.com](https://bigdata.com) Corporate Fundamentals (FMP):** tearsheets as of Oct 7–8, 2026 for TSM, ANET, ORCL, NOW, UBER, SYK, ALB, SQM, CRCL, XYZ and TMO.
- **SEC EDGAR XBRL companyfacts** (`https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`): annual 10-K/20-F data for all other companies, plus 10-Q year-to-date revenue for every US filer.
- **Nasdaq.com** quote, summary, earnings-forecast (consensus EPS) and target-price endpoints for prices at the Oct 7, 2026 close, exchange verification, market caps, consensus EPS, price targets and ratings.

**Cited documents (Bigdata.com).**
- [TSMC Q2 2026 call - Jul 16, 2026](https://app.bigdata.com/documents/06C7F92371AB2A1E81899B8CEFED270C)
- [Arista Q2 2026 call - Aug 04, 2026](https://app.bigdata.com/documents/E8743C13A5F68B9A9F09E884D36E908C)
- [Arista 10-Q - Aug 05, 2026](https://app.bigdata.com/documents/1F9C32636C5A55961A2B567065BE0C64?cnum=45)
- Oracle:
  - [Oracle 8-K - Jun 10, 2026](https://app.bigdata.com/documents/7433D60CC460B11C881DB4E59647D187?cnum=10)
  - [Oracle Q1 FY27 call - Sep 10, 2026](https://app.bigdata.com/documents/8290DC1105B7144E57BC5ECD99D8DAAB?cnum=5)
  - [Oracle FY27 guidance - Jun 10, 2026](https://app.bigdata.com/documents/3653D21D1CDC2C28D37AF11C78F07D68?cnum=47&cnum=23)
  - [Oracle 10-Q - Sep 11, 2026](https://app.bigdata.com/documents/EF37BE6099EB6B88444F99235B8F8667?cnum=60&cnum=58&cnum=59)
  - [Oracle 10-K - Jun 22, 2026](https://app.bigdata.com/documents/0D9D23892B0F67C68848BE5880D16C8C?cnum=78)
- ServiceNow:
  - [ServiceNow Q2 2026 call - Jul 22, 2026](https://app.bigdata.com/documents/E23A87D24A4660CDDDAFB6EF7634E88D?cnum=26&cnum=27&cnum=49&cnum=50&cnum=45)
  - [ServiceNow 10-Q - Jul 23, 2026](https://app.bigdata.com/documents/E2BE1653EB00135C1B34F6B56C8EE2DB?cnum=124&cnum=104)
- Uber:
  - [Uber Q2 2026 call - Aug 05, 2026](https://app.bigdata.com/documents/81B2A5B12A3CF73841F657BA415666EB)
  - [Globe and Mail (Uber/Rivian) - Oct 07, 2026](https://app.bigdata.com/documents/5117ECF10C90BA28A1F9E3FDEF95C385?cnum=3)
  - [Yahoo! Finance (Uber disruption risk) - Sep 22, 2026](https://app.bigdata.com/documents/A7BDBF6CBD4848BD4BF1E2C1A385609F?cnum=2)
- Stryker:
  - [Stryker Q2 2026 call - Jul 30, 2026](https://app.bigdata.com/documents/1F3E422F6E278B9C498440D2A5323811?cnum=14&cnum=4&cnum=13&cnum=48)
  - [Globe and Mail (Mako) - Jul 31, 2026](https://app.bigdata.com/documents/D3364E16863089E3AA9868A9675D10B2?cnum=12)
  - [Stryker 8-K (CEO transition) - Oct 06, 2026](https://app.bigdata.com/documents/6349593A58E192865144D7A8999D57F0?cnum=21)
- Circle:
  - [Circle 10-Q - Aug 05, 2026](https://app.bigdata.com/documents/F192D88D8B04C06E72A0ED31057223D9?cnum=126&cnum=154)
  - [Circle Q2 2026 call - Aug 05, 2026](https://app.bigdata.com/documents/5B92FAAFE8AC1B63BB51E8FC8DAAAB66?cnum=29&cnum=38&cnum=26&cnum=28&cnum=36)
- Block:
  - [Block 10-Q - Aug 05, 2026](https://app.bigdata.com/documents/03BCD7E8C1A8A5986FDF183CF93F1251?cnum=104)
  - [MT Newswires (Block Q2) - Aug 06, 2026](https://app.bigdata.com/documents/E32AF05F620427129E5A7DA9625CBB32?cnum=1)
  - [Block press release - Jul 09, 2026](https://app.bigdata.com/documents/69FD32A4522E06636FA9588C7141B8AB?cnum=3&cnum=2)
- Thermo Fisher:
  - [Thermo Fisher Q2 2026 call - Jul 23, 2026](https://app.bigdata.com/documents/A227C59D89414DC54D66D9876EE17578?cnum=14)
  - [Thermo Fisher investor conference - Sep 15, 2026](https://app.bigdata.com/documents/59AB4DD5D718C3EC68354D36AA58FA2F?cnum=5&cnum=3&cnum=20)
  - [Benzinga (PRECISE-SG100K) - Oct 05, 2026](https://app.bigdata.com/documents/DB2EF350E522AF283373F446F0181408?cnum=2&cnum=1&cnum=5)
- Albemarle:
  - [Albemarle 8-K - Aug 05, 2026](https://app.bigdata.com/documents/72A64DF27681CD96EB4844F3602FEE87?cnum=8&cnum=7&cnum=16)
  - [Albemarle Q2 2026 call - Aug 06, 2026](https://app.bigdata.com/documents/8D692AACFD28AD4EE1483BEB48B2BF25?cnum=8&cnum=7&cnum=20&cnum=4&cnum=39)
  - [Benzinga (JPMorgan on ALB) - Aug 25, 2026](https://app.bigdata.com/documents/71F74C5CF84C64E5F29A606E6A62B415?cnum=2)
- SQM:
  - [SQM Q2 2026 call - Aug 19, 2026](https://app.bigdata.com/documents/F99174F5A992F93E6F27EA9F69873731)
  - [SQM 20-F - Apr 22, 2026](https://app.bigdata.com/documents/7635DD914F65BC8510C89CF338FF6D04?cnum=39&cnum=35&cnum=528)

**Cited documents (web / SEC).**
- Amphenol:
  - [TIKR (Amphenol Q2 2026)](https://www.tikr.com/blog/amphenols-q2-earnings-beat-every-estimate-the-commscope-bet-is-paying-off-faster-than-expected)
  - [MarketBeat (Amphenol Q2 2026 call) - Jul 29, 2026](https://www.marketbeat.com/instant-alerts/amphenol-q2-earnings-call-highlights-2026-07-29/)
- Mastercard:
  - [Mastercard 8-K Q2 2026 earnings release](https://www.sec.gov/Archives/edgar/data/0001141391/000114139126000081/ma06302026-exx991xearnings.htm)
  - [Pulse 2 (Mastercard VAS)](https://pulse2.com/mastercards-value-added-services-revenue-jumps-20-as-business-becomes-major-growth-engine/)
  - [The Block (Mastercard stablecoin settlement)](https://www.theblock.co/post/403474/mastercard-expands-stablecoin-settlement-options-with-usdc-pyusd-and-rlusd)
- Vertiv:
  - [Vertiv 8-K Q2 2026 earnings release](https://www.sec.gov/Archives/edgar/data/0001674101/000162828026050323/q22026exhibit991vrt07292026.htm)
  - [Vertiv Q2 2026 press release](https://investors.vertiv.com/news/news-details/2026/Vertiv-Reports-Strong-Second-Quarter-2026-with-Diluted-EPS-Growth-of-53-Adjusted-Diluted-EPS-Growth-of-60-Raises-Full-Year-2026-Guidance-Across-All-Key-Metrics/default.aspx)

*All scores, TAM figures, fair multiples, scenario growth rates and margins, discount rates and risk ratings are the analyst's judgments. They are not sourced data.*
