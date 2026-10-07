# NYSE "Fair Value + High Growth" Screen

**Data date:**
- Prices are closing prices on **Oct 6, 2026**.
- Fundamentals are the latest reported fiscal year (FY) plus trailing twelve months (TTM) as of Oct 7, 2026.
- Consensus estimates are as of Oct 7, 2026.

**Data source:**
- Fundamentals, ratios, estimates and price targets come from [Bigdata.com](https://bigdata.com) Corporate Fundamentals (provider: FMP).
- News, filings and transcripts were retrieved through Bigdata.com search and are cited inline.

**Conventions:**
- **FY** = reported fiscal year (GAAP unless stated otherwise).
- **TTM** = trailing twelve months.
- **NTM** = next twelve months, built from consensus by time-weighting the current and next fiscal years.
- All forward EPS figures are **analyst consensus estimates**, not reported results. For several companies the consensus is on an adjusted (non-GAAP) basis; this is flagged where it applies.
- **N/M** = not meaningful, because the base year was negative or distorted by one-offs such as tax-valuation-allowance releases or impairments.
- **N/A** = data was not available or does not apply. No figures were invented to fill gaps.

> **This is not investment advice.** The fair values below come from a model that depends on stated assumptions, especially the fair multiples and discount rates. Treat them as a structured starting point for your own work.

---

## 0. Method, coverage and limitations (read first)

**1. Universe.**
- Started from NYSE-listed common stocks (exchange XNYS) that are actively trading and are not ETFs.
- Screened Technology, Industrials, Healthcare, Consumer Cyclical and Communication Services for market cap above $2B.
- Screened Financials for market cap above $8B, which keeps the list manageable.
- Excluded:
  - Funds, preferreds, warrants and SPACs.
  - Names with fewer than about 5 years of usable profitable history. For example, RDDT had its first GAAP-profitable year in 2025.
  - Companies whose GAAP statements are not meaningful for this method. For example, KKR consolidates its funds and an insurer.
- Energy, Materials, Utilities, Real Estate and Consumer Staples were **not screened in depth**. These sectors rarely combine at least 10% revenue CAGR with at least 12% EPS CAGR without commodity or cyclical help, and they would need normalized earnings first. TPL was checked as an example and fails: its 3-year revenue CAGR is 6.2%.

**2. Two-stage process.**
- A complete bottom-up DCF on every one of the roughly 1,000+ qualifying NYSE names was not feasible with the tools available.
- Stage 1 used sector screens. Stage 2 pulled full 5-year fundamentals for about 30 candidates and modelled 21 of them.
- Candidates were chosen for one of two reasons: a growth profile likely to pass the screen, or a 2026 price dislocation.
- **Survivorship-bias note:** the candidate pool deliberately includes 2026's large decliners (FICO, BSX, UBER, IT, ONON, DECK and others), not just this year's winners.

**3. Fair value formula** (the user's weights):
**FV = 40% DCF + 25% earnings-based + 20% FCF-based + 15% historical/peer-multiple**

| Component | How it was calculated |
|---|---|
| **DCF** | 10-year, two-stage model on FCF per share. Growth `g` runs for years 1–5, then fades linearly to 3% by year 10. Terminal growth is 3%. Discount rate is 8.5–13% depending on risk. When stock-based compensation (SBC) exceeds 5% of revenue, FCF **is reduced by SBC** (NOW, CRM, FICO). **Conservative case:** g × 0.6 and discount rate +1 pt. **Bull case:** g × 1.3 and discount rate −0.5 pt. |
| **Earnings-based** | NTM consensus EPS × a "fair" P/E. The fair P/E reflects growth, quality and peer multiples. It is the analyst's assumption and is shown in the deep dives. |
| **FCF-based** | Forward FCF per share × a fair P/FCF. |
| **Historical/peer** | NTM EPS × an approximate 5-year median forward P/E, or a peer median where history is short or distorted. **These multiples are approximations and should be checked independently.** |

- **Banks (NU):** FCF is not meaningful. The DCF is run on earnings instead, and the weights are re-normalized without the FCF leg.

**4. Scores.**
- **Growth (0–100):**
  - 3-year revenue CAGR: 35 points.
  - 3-year EPS CAGR: 35 points. Forward consensus EPS growth is substituted where the history is N/M.
  - 3-year FCF CAGR: 20 points.
  - Forward EPS growth: 10 points.
- **Quality (0–100):** ROIC 40, operating margin 25, net debt/EBITDA 20, moat 15.
- **Valuation (0–100):** margin of safety 60, forward PEG 40.
- **Risk (0–100, where 100 = lowest risk):** a judgment rating covering leverage, regulation, cyclicality, EM/FX exposure and listing history.
- **Overall (/100):** Growth 25, Profitability/ROIC 20, Financial Strength 15, Valuation 25, Moat 10, Management 5.

**5. Margin-of-safety classes.**

| Margin of safety | Class |
|---|---|
| Above 30% | Excellent |
| 20–30% | Attractive |
| 10–20% | Reasonable |
| 0–10% | Fully valued |
| Below 0% | Overvalued |

**Headline result.** Applied strictly, the full hard filter leaves **one company: Deckers (DECK)**. The filter requires all of the following:
- Growth, Quality and Valuation scores of at least 70.
- Overall score of at least 75.
- Revenue CAGR of at least 10% and EPS CAGR of at least 12%.
- Positive FCF and ROIC above 12%.
- Upside of at least 20% and margin of safety of at least 15%.
- No balance-sheet red flag.

That is a realistic outcome for October 2026. The best compounders (MA, MSCI, MCO, ANET, VEEV) are not cheap. The cheapest growth names (UBER, NU, SPOT, ONON, BSX, CRM, SPGI) each miss a quality test, such as ROIC, a GAAP-ROIC distortion from goodwill, or a short or volatile history.

The Top 20 below is ranked by Overall score. Each company's hard-filter status is shown, so you can see exactly why it falls short.

---

## A. Top 20 ranked list

**Column definitions:**
- **Rev/EPS/FCF CAGR:** 3-year, from FY2022 to FY2025 (or the latest FY), GAAP.
- **ROIC:** TTM.
- **P/E:** forward NTM consensus.
- **P/FCF:** TTM.

| Rank | Ticker | Company | Sector | Mkt Cap ($B) | Rev CAGR 3y | EPS CAGR 3y | FCF CAGR 3y | ROIC (TTM) | ND/EBITDA | Fwd P/E (NTM) | P/FCF (TTM) | Price | Fair Value | Upside | MoS | Growth | Quality | Valuation | Overall | Hard filters |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | DECK | Deckers Outdoor | Cons. Cyclical (footwear) | 11.1 | 14.7% | 29.5% | 34.0% | 34.0% | net cash | 10.3x | 9.4x | $81.66 | $148 | 82% | 45% | 76 | 79 | 100 | 86 | **PASS** |
| 2 | NU | Nu Holdings | Financials (digital bank) | 75.8 | 52.0% | N/M¹ | N/A (bank) | 30% (ROE) | N/A (bank) | 14.8x | N/A | $15.66 | $22 | 38% | 28% | 100 | 63 | 88 | 80 | Fails: Quality |
| 3 | MA | Mastercard | Financials (payments) | 496.9 | 13.8% | 17.3% | 18.8% | 48.0% | 0.6x | 25.4x | 30.4x | $566.58 | $651 | 15% | 13% | 58 | 97 | 61 | 78 | Fails: G, V, Upside, MoS |
| 4 | SPOT | Spotify | Comm. Services | 100.4 | 13.6% | N/M² | N/M² | 28.0% | net cash | 28.9x | 27.2x | $488.13 | $587 | 20% | 17% | 80 | 65 | 74 | 75 | Fails: Quality |
| 5 | UBER | Uber Technologies | Tech (mobility/delivery) | 140.6 | 17.7% | N/M³ | N/M² | 13.0% | 1.2x | 16.6x | 13.9x | $69.08 | $118 | 71% | 41% | 87 | 37 | 100 | 72 | Fails: Q, Overall |
| 6 | ANET | Arista Networks | Tech (networking) | 271.2 | 27.1% | 37.1% | 112% | 22.0% | net cash | 43.1x | 52.5x | $215.36 | $172 | −20% | −25% | 100 | 75 | 26 | 71 | Fails: V, Upside, MoS |
| 7 | ONON | On Holding | Cons. Cyclical (footwear) | 11.0 | ~33%⁴ | N/M⁴ | N/M² | 16.3% | net cash | 20.3x | 26.1x | $33.13 | $40 | 20% | 17% | 90 | 45 | 77 | 71 | Fails: Q, Overall |
| 8 | MCO | Moody's | Financials (ratings) | 78.3 | 12.2% | 22.4%⁵ | 29.3%⁵ | 23.9% | 1.5x | 24.6x | 23.4x | $452.32 | $536 | 18% | 16% | 67 | 75 | 53 | 67 | Fails: G, V, Upside |
| 9 | GDDY | GoDaddy | Tech (software) | 13.0 | 6.6% | N/M³ | 19.6% | 20.6% | 1.9x | 11.2x | 8.8x | $98.18 | $192 | 95% | 49% | 50 | 51 | 100 | 65 | Fails: Rev growth, G, Q |
| 10 | CMG | Chipotle | Cons. Cyclical (restaurants) | 39.7 | 11.4% | 21.2% | 19.6% | 18.0% | ~0 (leases only) | 23.4x | 25.3x | $30.92 | $38 | 23% | 18% | 63 | 50 | 72 | 64 | Fails: G, Q |
| 11 | FICO | Fair Isaac | Tech (analytics) | 15.0 | 13.1% | 23.2% | 15.2% | 59.0% | **4.2x** | 15.3x⁶ | 15.8x | $695.46 | $877 | 26% | 21% | 60 | 77 | 70 | 63 | Fails: G, Overall, **Leverage** |
| 12 | TPR | Tapestry | Cons. Cyclical (luxury) | 23.6 | 6.3% | N/M³ | 31.8% | 29.0% | 1.4x | 14.2x | 13.0x | $116.73 | $138 | 18% | 15% | 43 | 63 | 75 | 62 | Fails: Rev growth, G |
| 13 | MSCI | MSCI Inc. | Financials (index/data) | 40.3 | 11.7% | 13.2% | 14.9% | 39.0% | **3.0x** | 25.5x | 25.4x | $554.92 | $646 | 16% | 14% | 42 | 82 | 57 | 61 | Fails: G, V, MoS, Leverage |
| 14 | BSX | Boston Scientific | Healthcare (med-tech) | 62.7 | 16.5% | 63%⁵ | 58.7%⁵ | 10.6% | 2.1x | 12.6x | 17.2x | $42.19 | $63 | 48% | 33% | 77 | 34 | 78 | 60 | Fails: ROIC, Q |
| 15 | VEEV | Veeva Systems | Healthcare (software) | 46.1 | 14.0% | 21.9% | 21.8% | 10.4%⁷ | net cash | 28.6x | 28.0x | $283.55 | $317 | 12% | 11% | 67 | 51 | 42 | 59 | Fails: V, MoS |
| 16 | NOW | ServiceNow | Tech (software) | 142.6 | 22.4% | N/M³ | 28.0% | 5.5% | 1.7x | 28.7x | 31.1x | $137.97 | $138 | 0% | 0% | 91 | 29 | 54 | 59 | Fails: ROIC, V, MoS |
| 17 | SPGI | S&P Global | Financials (ratings/data) | 116.8 | 11.1%⁸ | 12.8% | 11.2%⁸ | 10.2%⁷ | 1.4x | 20.2x | 21.0x | $396.13 | $534 | 35% | 26% | 36 | 55 | 76 | 58 | Fails: G, Q (goodwill-depressed ROIC) |
| 18 | SN | SharkNinja | Cons. Cyclical (appliances) | 26.1 | 19.9% | 43.6% | 61.0% | 19.7% | 0.1x | 25.2x | 32.6x | $184.72 | $154 | −17% | −20% | 87 | 48 | 22 | 57 | Fails: V, MoS |
| 19 | CRM | Salesforce | Tech (software) | 184.3 | 9.8% | N/M³ | 31.6% | 8.7% | 2.1x | 13.8x | 12.2x | $224.99 | $342 | 52% | 34% | 52 | 31 | 94 | 56 | Fails: Rev growth, ROIC |
| 20 | CPAY | Corpay | Tech (B2B payments) | 26.6 | 9.7% | 6.6% | 29.0% | 8.9% | **3.1x** | 13.4x⁹ | 16.2x | $406.79 | $473 | 16% | 14% | 38 | 37 | 74 | 46 | Fails: most |

**Footnotes:**
1. NU had negative EPS in FY2022. FY2023–25 EPS went from $0.21 to $0.58, a 2-year CAGR of about 66%.
2. FCF or EPS was negative or near zero in the FY2022 base year.
3. GAAP EPS is distorted:
   - UBER: deferred-tax-asset valuation-allowance releases of $5.8B in 2024 and $4.3B in 2025. Normalized FY25 EPS is about $2.14.
   - NOW: a tax benefit in FY23.
   - GDDY: a tax benefit in FY23.
   - TPR: an impairment in FY25.
   - CRM: a low FY23 base.
4. On reports in CHF; the USD figures are FMP-converted. The 3-year revenue CAGR is computed from revenue per share. On has been listed only since 2021, so it has less than 5 years of public history.
5. The CAGR starts from a depressed FY2022 trough (MCO: ratings issuance trough; BSX: low base). The 4-year CAGR is much lower for MCO (EPS 3.8%).
6. FICO's NTM EPS is the pre-FHFA consensus for FY27 ($50.42) **cut by 10%** to reflect the Sep 29, 2026 regulatory change.
7. ROIC is depressed by goodwill (SPGI after the IHS Markit merger) or by excess cash (VEEV, about $6.5B net cash).
8. SPGI's 3-year revenue CAGR benefited from the IHS Markit merger; organic growth is roughly high single digits. The FCF figure shown is the 4-year CAGR, because FY2022 FCF was depressed by the merger.
9. CPAY's forward multiple uses adjusted EPS. GAAP EPS is far lower because of acquisition amortization.

Ratio and price sources: [Bigdata.com](https://bigdata.com) Corporate Fundamentals (FMP), Oct 7, 2026. Fair values come from the model described in §0.

---

## B. Top 10: detailed analysis

The deep-dive Top 10 is the highest-scoring companies that meet two conditions: revenue CAGR of at least 10% **and** a positive margin of safety. ANET is excluded because it is overvalued, and GDDY because it fails the growth screen. Both are discussed in sections E–G.

| # | Ticker | Bear (stress) value | Bear (model) | Base FV | Bull | Ideal entry (25% MoS) | Expected 3-year return* |
|---|---|---|---|---|---|---|---|
| 1 | DECK | $71 | $115 | $148 | $179 | ≤ $111 (already below) | ~26%/yr |
| 2 | NU | $11 | $14 | $22 | $30 | ≤ $16.3 (at the line) | ~35%/yr (high variance) |
| 3 | MA | $446 | $478 | $651 | $820 | ≤ $488 | ~23%/yr** |
| 4 | SPOT | $304 | $412 | $587 | $768 | ≤ $440 | ~27%/yr** |
| 5 | UBER | $50 | $85 | $118 | $151 | ≤ $88 (already below) | ~42%/yr** |
| 6 | ONON | $21 | $29 | $40 | $51 | ≤ $30 | ~28%/yr** |
| 7 | MCO | $331 | $405 | $536 | $657 | ≤ $402 | ~16%/yr |
| 8 | CMG | $24 | $29 | $38 | $47 | ≤ $28.4 | ~25%/yr** |
| 9 | FICO | $445 | $670 | $877 | $1,069 | ≤ $658 | ~20%/yr (very high variance) |
| 10 | MSCI | $436 | $485 | $646 | $797 | ≤ $484 | ~20%/yr |

\* The expected 3-year return assumes NTM EPS compounds at the consensus 2-year forward growth rate for three years and the stock re-rates to the fair P/E. Dividends are excluded. This is a model output, not a forecast.

\*\* These returns are optimistic because they assume consensus growth is delivered **and** the multiple re-rates. A realistic haircut is 30–40%.

**Stress value** = NTM EPS × a trough multiple. Examples: DECK 9x, NU 10x, UBER 12x, MA 20x, SPOT 18x. For FICO, EPS is also cut 30% to model a price war.

### 1. Deckers Outdoor (DECK): Excellent margin of safety, the only full PASS

**Thesis.**
- Two global brands, HOKA and UGG, produce top-tier margins: operating margin about 22.7%, ROIC 34%, net cash about $1.9B and no debt.
- The stock trades at about 10x NTM EPS and 9.4x TTM P/FCF, versus an EV/EBITDA history of roughly 12–22x.
- The market prices DECK as if HOKA's growth is over. Management instead guides to high-single-digit company growth through FY2030.

**Why growth can last 3–5 years.**
- Management expects "high single-digit revenue growth on a consolidated company basis through our fiscal year 2030, with HOKA expected to increase low double digits annually and UGG… mid-single digits" ([Quartr Transcripts - May 21, 2026](https://app.bigdata.com/documents/54825CA004BB2D2C46A25123308992F4?cnum=24&cnum=17&cnum=55)).
- International sales and DTC are both growing faster than the group average.

**FY27 (March 2027) guidance**, from [Quartr Reports - May 21, 2026](https://app.bigdata.com/documents/471A9212C9499F4A84F18604F4988307?cnum=8):
- Revenue of $5.86–5.91B.
- Diluted EPS of $7.30–7.45.
- Buybacks of about 80% of FCF.

**Drivers.** HOKA's international expansion and 20–25 new stores per year; UGG's year-round "365" product line and its men's business; continued buybacks, which have cut diluted shares from 166.7M to 145.8M over four years.

**Moat.** Brand strength and full-price sell-through (medium). Footwear moats are weaker than software or ratings moats.

**Fair value.** Blended FV is **$148**.

| Component | Value | Inputs |
|---|---|---|
| DCF (conservative / base / bull) | $128 / $173 / $211 | TTM FCF $8.70/share, g 7%, discount rate 9.5% |
| Earnings-based | $118 | NTM EPS $7.9 × 15x |
| FCF-based | $130 | 14x forward FCF |
| Historical/peer | $158 | 20x |

**Risks.**
1. HOKA decelerates further or loses share to On, Nike's running recovery and Asics.
2. UGG fashion-cycle reversal.
3. Tariffs on Vietnam sourcing. Management flagged about 200 bps of gross-margin headwind in Q4 FY26 ([Quartr - Jan 29, 2026](https://app.bigdata.com/documents/1FCF5B92928B39CC9A9CA24CEE8BA005?cnum=23&cnum=30)).
4. Wholesale inventory destocking.
5. Consensus is only HOLD (25 Buy / 25 Hold / 6 Sell), so sentiment is weak.

**What would make the thesis wrong.** HOKA growth turning negative in the US, or gross margin falling below about 54%.

**Entry.** $75–111; current price $81.66.

**Red flags.** None. Revenue growth slowing to about 7% is expected, not hidden.

### 2. Nu Holdings (NU): Attractive (high risk)

**Thesis.**
- The largest private financial institution in Brazil by customers. It has 139M customers in total, and 16M in Mexico as of July 2026.
- For the first time, it earned **more than $1B of net income in a single quarter**, in Q2 2026 ([Quartr Transcripts - Aug 13, 2026](https://app.bigdata.com/documents/DAE782291CC6BEA039500A7D92291F61?cnum=11&cnum=56&cnum=17&cnum=14&cnum=3)).
- ROE is about 30%.
- The stock trades at about 14.8x NTM EPS, against consensus EPS growth of about 29% a year: $0.87 in FY26, $1.12 in FY27, $1.45 in FY28.

**Why growth can last.**
- Mexico monetizes faster than Brazil did. ARPAC in Mexico is $12.3 at the same stage, versus $5.6 in Brazil.
- Expansion into Colombia and the US is underway (conditional US charter).
- Deposits are $45.3B and the loan-to-deposit ratio in Mexico is 35%, so there is plenty of funding capacity (same source).

**Fair value.** Blended FV is **$22**, using an EPS-based DCF (g 25%, discount rate 13% to reflect EM risk), 17x NTM EPS and 22x for the historical/peer leg.

**Risks.**
1. The Brazil credit cycle and high Selic rates.
2. BRL and MXN currency moves.
3. Delinquency in Mexico and Colombia, which management says structurally runs above Brazil ([Quartr - Feb 25, 2026](https://app.bigdata.com/documents/EE0633C16A401D5855B06EE9403216E0)).
4. A weak Latin American macro and political backdrop, flagged in the 20-F ([Edgar - Apr 8, 2026](https://app.bigdata.com/documents/F658A9E28B67909C2BBA47D6E1076533?cnum=173&cnum=91&cnum=40&cnum=573)).
5. Execution risk from expanding into the US and Mexico at the same time.

**What would make the thesis wrong.** A rise in NPLs that forces front-loaded provisions and stalls EPS growth.

**Entry.** Below about $16; it sits at the line today.

**Note on quality.** NU fails the Quality score only because bank metrics such as operating margin and FCF do not fit the template. On fundamentals, ROE of 30% is excellent.

### 3. Mastercard (MA): Reasonable margin of safety, highest quality

**Thesis.**
- One of the highest-quality compounders on the NYSE: ROIC 48%, operating margin 60%, ND/EBITDA 0.6x.
- 3-year CAGRs: revenue 13.8%, EPS 17.3%, FCF 18.8%.
- Share count fell from 992M to 898M.
- At 25.4x NTM EPS, it trades below its own history of roughly 30x and below its 2021–24 EV/EBITDA range of 26–32x (currently 23.1x TTM).

**Drivers.** The secular shift from cash to card; value-added services such as cyber, data and tokenization; cross-border travel.

**Fair value.** Blended FV is **$651** (DCF base $618; 30x NTM EPS gives $669). Margin of safety is about 13%, so it fails the 15% hard filter.

**Risks.**
1. Interchange regulation such as the CCCA in the US and EU caps.
2. Account-to-account payments and stablecoin disintermediation.
3. DOJ and litigation exposure.
4. A slowdown in cross-border volume.
5. Valuation de-rating.

**Entry.** Below about $488 for a 25% margin of safety. Starting a position under about $520 is reasonable.

### 4. Spotify (SPOT): Reasonable to Attractive

**Thesis.**
- Spotify has become structurally profitable: EPS went from −€2.73 in FY23 to €10.51 in FY25.
- FCF grew from €0.7B to €2.9B.
- It holds net cash of about €3.3B and ROIC of about 28%.
- Consensus EPS rises from €12.13 (FY26) to €19.16 (FY28), about 26% a year. NTM EPS is about 28.9x in USD.
- The stock is −16% YTD and −28% over one year.

**Drivers.** Price increases, a higher-margin ads and marketplace business, audiobooks and video, and operating leverage on a gross margin of about 33%.

**Fair value.** Blended FV is **$587** (DCF base $651 with g 18% and discount rate 9.5%; earnings-based $507 at 30x).

**Risks.**
1. Label and royalty renegotiations.
2. Competition from Apple, YouTube and Amazon.
3. EUR/USD currency moves (SPOT reports in EUR).
4. AI-generated music changing the economics of content.
5. Slowing subscriber growth.

**Data caveat.** The 3-year EPS and FCF CAGRs are N/M because of negative base years.

**Entry.** Below about $440.

### 5. Uber Technologies (UBER): Excellent margin of safety, but quality and risk caveats

**Thesis.**
- Revenue CAGR of 17.7%, and FCF rose from $0.4B in FY22 to $9.8B in FY25.
- At 16.6x NTM consensus EPS of $4.17 and 13.9x TTM P/FCF, the valuation assumes autonomous vehicles erode the platform.
- Pershing Square notes that earnings are "on pace to grow approximately 35% this year" and that the stock trades "at 19 times earnings, near its lowest-ever valuation" ([Quartr Reports (Pershing Square) - Aug 13, 2026](https://app.bigdata.com/documents/B7468DF6A3C4B0797C7936CBDC9F4E31?cnum=35)).

**GAAP caveat.** FY24 and FY25 GAAP EPS of $4.56 and $4.73 include tax-allowance releases. Normalized FY25 EPS is about $2.14, so the 3-year EPS CAGR is shown as N/M and forward consensus is used instead.

**Drivers.** Uber One membership; growth in delivery and ads; positioning as the AV aggregation layer. Partners include Pony.ai (2,000 robotaxis in Europe), WeRide, Nuro/Lucid and Wayve ([CNBC - Aug 14, 2026](https://app.bigdata.com/documents/80FC5AF11F5CE222AF45DAB41B4CB624?cnum=1); [Alliance News - Jun 17, 2026](https://app.bigdata.com/documents/176403B968CA269EF0A77CF52A3ECB45?cnum=3)).

**Fair value.** Blended FV is **$118** (DCF base $141 with g 15% and discount rate 10%; earnings-based $92 at 22x).

**Risks.**
1. Waymo or Tesla building direct-to-consumer robotaxi networks. The relationship with Waymo was described as "increasingly fraught" (Pershing Square, same source).
2. Capital intensity: more than $10B committed to AV equity stakes and fleets ([MT Newswires - Apr 15, 2026](https://app.bigdata.com/documents/C3906DE48974309D664F0F29074FBF92?cnum=1)). This could depress the FCF conversion that the valuation relies on.
3. Driver-classification law.
4. Price competition from Lyft and DoorDash.
5. AVs are still only about 0.5% of trips ([Benzinga - Aug 6, 2026](https://app.bigdata.com/documents/6534A2D06A77526782E8D9771839F21C?cnum=1&cnum=3)), so the payoff is uncertain.

**What would make the thesis wrong.** A major AV operator scaling outside Uber's network in Uber's top cities, combined with a falling take rate.

**Entry.** Below about $88; it is already below that level.

### 6. On Holding (ONON): Reasonable margin of safety, high risk

**Thesis.**
- Premium running brand with about 33% revenue CAGR (CHF-based, FMP-converted), gross margin of 65% and net cash.
- Consensus sales grow from $3.53B (FY26) to $4.97B (FY28), and EPS from $1.44 to $2.12.
- At 20x NTM EPS after a −29% YTD fall, its PEG is about 0.95.

**Fair value.** Blended FV is **$40**.

**Risks.**
1. Brand-heat cyclicality.
2. CHF strength hurting reported EPS. FY25 net margin fell to 6.8% on FX.
3. A short listed history (2021).
4. High beta (2.1).
5. Competition from HOKA and Nike.

**Data caveat.** Five-year history is N/A. FY2021 was loss-making.

**Entry.** Below about $30.

### 7. Moody's (MCO): Reasonable margin of safety

**Thesis.**
- A ratings duopoly with ROIC of 24% and operating margin of 45%.
- EV/EBITDA is 21x versus a history of about 24–30x.
- 2026 "AI-disruption" fears hit data and analytics stocks, but ratings revenue is regulation-embedded.

**Growth caveat.** The 3-year CAGR is flattered by the 2022 trough; 4-year EPS CAGR is only 3.8%. Forward consensus EPS growth is 11.6% a year.

**Fair value.** Blended FV is **$536**.

**Risks.**
1. Debt-issuance cyclicality.
2. AI competition in Moody's Analytics.
3. Regulation.
4. Private-credit stress.
5. Multiple compression.

**Entry.** Below about $402.

### 8. Chipotle (CMG): Reasonable margin of safety

**Thesis.**
- Debt-free (leases only) with ROIC of 18%.
- 3-year CAGRs: revenue 11.4%, EPS 21%, FCF 19.6%.
- EV/EBITDA has de-rated to 19.7x from a history of about 34–47x.
- The bear case is negative same-store sales in 2025–26, with FY26 EPS flat at $1.15.
- Consensus expects re-acceleration: FY27 EPS $1.37 and FY28 $1.59, on unit growth of roughly 8–10% a year.

**Fair value.** Blended FV is **$38**.

**Risks.**
1. Persistent traffic declines.
2. Food and labor cost inflation squeezing an operating margin that already fell from 16.9% to 15.2%.
3. Saturation of the US unit footprint.
4. Weak consumer spending.
5. Management execution after the CEO transition.

**Entry.** Below about $28.

### 9. Fair Isaac (FICO): Attractive on the numbers, but with a **significant red flag**

**What happened.**
- On Sep 28–29, 2026, the FHFA director said Fannie Mae and Freddie Mac would move to one pricing grid "with VantageScore joining the existing FICO classic pricing grid". The stock fell more than 26% ([MT Newswires - Sep 29, 2026](https://app.bigdata.com/documents/E0AB484CEA23DA05DD718F718AAE97F7?cnum=1)).
- BofA downgraded the stock to Neutral with a $700 target. Barclays cut its target to $935 and Wells Fargo to $950 ([Benzinga - Sep 30, 2026](https://app.bigdata.com/documents/D453315C3D577D7BB4D2371324094403?cnum=1); [Benzinga - Sep 30, 2026](https://app.bigdata.com/documents/35A072D01DC6A62C42E120C0FB54372A?cnum=1)).
- A US senator had earlier asked the DOJ to investigate FICO's pricing ([The Globe And Mail - Apr 16, 2026](https://app.bigdata.com/documents/06F1E6BE2E7EF877ADCED5D477B354F3?cnum=1&cnum=2)).

**Balance sheet.**
- FICO took a $1.5B term loan to fund an accelerated share repurchase ([Edgar 10-Q - Jul 29, 2026](https://app.bigdata.com/documents/DD01B20C7F056EF856D4F773B75AB9F5?cnum=113)).
- Debt is now about 33% of market value ([PubT - Sep 30, 2026](https://app.bigdata.com/documents/8953B3DE25E80E70CA811B0332685B06?cnum=2&cnum=1&cnum=3)).
- ND/EBITDA is 4.2x TTM and equity is negative.

**Fundamentals.**
- 3-year CAGRs: revenue 13.1%, EPS 23.2%, FCF 15.2%.
- ROIC is 59%.
- P/E is 15x on a consensus EPS that has been haircut 10%.

**Fair value.** Blended FV is **$877**. However, a scenario in which mortgage-score pricing is cut by 30–40% gives a stress value of about $445.

**Verdict.** Speculative. FICO fails the leverage hard filter, and the regulatory outcome is binary.

**Entry.** Only below about $600, with small position sizing.

### 10. MSCI (MSCI): Reasonable margin of safety, leverage flag

**Thesis.**
- ROIC of 39% and operating margin of 56%.
- 3-year CAGRs: revenue 11.7%, EPS 13.2%, FCF 14.9%.
- EV/EBITDA is 22.7x versus a history of about 29–46x.

**Flag.** ND/EBITDA of 3.0x and negative equity, both caused by buybacks.

**Fair value.** Blended FV is **$646**; margin of safety is about 14%.

**Risks.**
1. A shift toward passive investing that cuts asset-based fees.
2. ESG backlash.
3. Consolidation among asset-manager clients.
4. Leverage.
5. Equity-market drawdowns, which directly reduce asset-based fees.

**Entry.** Below about $484.

---

## C. Top 5 highest-conviction picks

Ranked by risk-adjusted expected return, combining overall score, margin of safety and risk score.

| | **DECK** | **UBER** | **MA** | **SPOT** | **NU** |
|---|---|---|---|---|---|
| Current price | $81.66 | $69.08 | $566.58 | $488.13 | $15.66 |
| Fair value | $148 | $118 | $651 | $587 | $22 |
| Margin of safety | 45% (Excellent) | 41% (Excellent) | 13% (Reasonable) | 17% (Reasonable) | 28% (Attractive) |
| 3-year revenue CAGR (FY22–25) | 14.7% | 17.7% | 13.8% | 13.6% | 52.0% |
| 3-year EPS CAGR | 29.5% | N/M (tax distortion); fwd ~29% | 17.3% | N/M (losses); fwd ~26% | N/M; 2-year ~66% |
| ROIC (TTM) | 34% | 13% | 48% | 28% | ROE 30% |
| FCF growth (3-year CAGR) | 34% | $0.4B → $9.8B | 18.8% | €0.02B → €2.9B | N/A (bank) |
| Expected 3-year CAGR return (model; haircut for realism) | ~18–26% | ~25–40% | ~13–20% | ~16–25% | ~20–35% |
| Risk level | Medium | Medium–High | Low | Medium | High |
| Ideal entry price | ≤ $111 (now) | ≤ $88 (now) | ≤ $488–520 | ≤ $440 | ≤ $16 |
| Thesis | Two premium brands, 34% ROIC, net cash, at about 10x EPS; the only full-filter PASS | Profitable platform priced for AV doom; FCF of about $10B and a 7% FCF yield | Best-in-class compounder below its historical multiple | Inflection to structural profitability; operating leverage | Highest-growth profitable bank; Mexico ramping faster than Brazil did |

---

## D. Top 5 by largest margin of safety

| Ticker | Margin of safety | Comment |
|---|---|---|
| GDDY | 49% | 8.8x P/FCF, heavy buybacks. **Fails** the growth screen (revenue CAGR 6.6%). |
| DECK | 45% | Full PASS. |
| UBER | 41% | Quality score held down by ROIC of 13% and operating margin of 12.5%. |
| CRM | 34% | P/FCF 12x. Revenue CAGR of 9.8% is just below 10%; ROIC 8.7% (goodwill); SBC 8.3% of revenue. |
| BSX | 33% | 2026 guidance cuts and US electrophysiology share loss. Growth is broken near term (FY26 about +5–6%). |

---

## E. Top 5 highest-quality growth companies

Quality score combined with sustained growth, regardless of price.

| Ticker | Quality score | Why | Valuation today |
|---|---|---|---|
| MA | 97 | 48% ROIC, 60% operating margin, about 14–17% revenue and EPS compounding | Reasonable (MoS 13%) |
| MSCI | 82 | 39% ROIC, 56% operating margin | Reasonable (MoS 14%) |
| DECK | 79 | 34% ROIC, net cash | Excellent (MoS 45%) |
| ANET | 75 | 27% revenue and 37% EPS 3-year CAGR, net cash $10.7B | **Overvalued** (MoS −25%, 43x NTM) |
| MCO | 75 | 24% ROIC, ratings duopoly | Reasonable (MoS 16%) |

---

## F. Top 5 potentially undervalued (fail at least one growth or quality screen)

| Ticker | Why it looks cheap | Why it is not a "high growth" pick |
|---|---|---|
| GDDY | 11x NTM EPS, 8.8x P/FCF; FV $192 | Revenue CAGR only 6.6% |
| SPGI | 20x NTM versus about 28x history; FV $534, MoS 26% | Organic growth in the high single digits; GAAP ROIC 10% (goodwill) |
| CRM | 13.8x NTM, 12x P/FCF; FV $342 | Revenue 9.8%, acquisition-aided; ROIC 8.7%; high SBC; AI seat-disruption risk |
| BSX | 12.6x NTM; FV $63 | FY26 growth reset to about 5–6% after share loss in electrophysiology and WATCHMAN; cyberattack and guidance issues in Sep 2026 |
| KKR | About 12.5x FY27 adjusted EPS of $7.28; consensus target $123.8 versus price $90.67 | **Quant scoring N/A**: consolidated GAAP is not meaningful; private-credit sentiment risk |

---

## G. Stocks to avoid despite apparently attractive valuation

| Ticker | Looks cheap because… | Red flag |
|---|---|---|
| **PGR** | P/E 10.6x; revenue CAGR 20.9% | **Peak cyclical earnings.** Consensus EPS *falls*: $19.23 (FY25) → $18.13 → $16.25 → $16.08. Consensus is HOLD. |
| **IT (Gartner)** | P/FCF 9.6x, P/E 16.6x | **Value trap.** Revenue expected to decline in FY26 ($6.42B vs $6.50B); contract value stalled; AI substitution risk for research seats. |
| **DELL** | 22x FY27 EPS after +71% revenue | **Cyclical boom.** +356% YTD; 3-year revenue CAGR 3.5% before the AI-server spike; low margin (operating margin about 10%); volatile FCF. |
| **HCA** | P/E 14.4x | Revenue CAGR 7.9% fails; EPS growth driven by buybacks (shares 329M → 231M); ND/EBITDA 3.0x; negative equity; Medicaid/ACA policy risk. |
| **CPAY** | 12.9x FY27 adjusted EPS | ND/EBITDA 3.1x; GAAP EPS CAGR 6.6%; acquisition-driven growth; volatile FCF. |
| **FICO** (conditional) | 15x EPS after −59% YTD | Regulatory monopoly erosion plus leveraged buybacks (ND/EBITDA 4.2x). Not "avoid" for speculative capital, but a significant red flag. |
| **RDDT** | 21x FY27 EPS with about 50% revenue growth | Insufficient profit history (first GAAP-profitable year 2025); SBC 12–16% of revenue; dilution 163M → 202M shares. |

**Also overvalued (not cheap; listed for completeness):**
- **ANET:** MoS −25%.
- **SN:** MoS −20%; tariffs on China sourcing.
- **PWR:** MoS −40%; GAAP ROIC 8.4%.
- **VEEV and NOW:** fully valued, MoS 0–11%.

---

## H. Final "Best Risk/Reward" ranking

| Rank | Ticker | Margin of safety | Risk | One-line rationale |
|---|---|---|---|---|
| 1 | **DECK** | 45% | Medium | Only full-filter PASS: cheap, net cash, 34% ROIC |
| 2 | **UBER** | 41% | Medium–High | About 7% FCF yield on a growing platform; the AV risk is priced in |
| 3 | **MA** | 13% | Low | Best quality at a below-history multiple; add on weakness |
| 4 | **SPOT** | 17% | Medium | Profit inflection with net cash |
| 5 | **NU** | 28% | High | Hyper-growth at about 15x; size for EM risk |
| 6 | **SPGI** | 26% | Low–Medium | High-single-digit organic grower at a 30% discount to its historical multiple (growth-screen miss) |
| 7 | **MCO** | 16% | Low–Medium | Duopoly at a de-rated multiple |
| 8 | **ONON** | 17% | High | Fast grower after a −29% YTD de-rating |
| 9 | **CMG** | 18% | Medium | De-rated quality restaurant; needs traffic recovery |
| 10 | **MSCI** | 14% | Medium | Elite margins; watch leverage |
| — | FICO | 21% | **Very high** | Speculative only; binary regulatory outcome |

---

## 13. Red-flag check (shortlist)

| Ticker | Declining revenue | Earnings-quality issue | FCF deterioration | Excess debt | Excess SBC / dilution | Concentration / litigation | Peak or cyclical earnings | Overall |
|---|---|---|---|---|---|---|---|---|
| DECK | No | No | No | No (net cash) | No (shares −13%) | Tariffs | Footwear fashion cycle (moderate) | **Clean** |
| NU | No | Provisions front-loaded | N/A | Bank | Low (SBC 1.7%) | Brazil concentration | Credit cycle | Moderate |
| MA | No | No | No | No | No | Interchange litigation | No | **Clean** |
| SPOT | No | Low base | No | Net cash | Mild dilution (194M → 210M) | Label dependence | No | Clean–moderate |
| UBER | No | **GAAP EPS inflated by tax releases** | No (but AV capex rising) | No | SBC about 3.5% | Driver-classification suits | No | Moderate |
| ONON | No | FX noise | Volatile (negative 2022) | Net cash | Low | — | Brand cycle | Moderate (short history) |
| MCO | No | No | No | No | No | Regulation | Issuance-cycle trough base | Clean |
| CMG | No (same-store sales negative) | No | Flat | No | No | Food safety | No | Moderate |
| FICO | No | No | No | **Yes (4.2x, negative equity)** | SBC 7.9% | **FHFA/DOJ regulatory** | No | **Significant red flag** |
| MSCI | No | No | No | **3.0x (flag)** | No | — | Market-linked | Moderate |

---

## Data sources

- **[Bigdata.com](https://bigdata.com) Corporate Fundamentals (FMP):** company tearsheets as of Oct 7, 2026. These provide annual income statements, balance sheets and cash flows for FY2021–25, TTM ratios and key metrics, analyst estimates and ratings, and price performance. They cover:
  - MA, MSCI, SPGI, MCO, FICO, NOW, UBER, VEEV, CRM, NU, SPOT, ANET, CMG, DECK, ONON, BSX, SN, PWR, GDDY, TPR, CPAY.
  - PGR, IT, DELL, HCA, RDDT, KKR, TPL.
  - The NYSE sector screens.
- [MT Newswires - Sep 29, 2026](https://app.bigdata.com/documents/E0AB484CEA23DA05DD718F718AAE97F7?cnum=1): FICO and the FHFA pricing grid.
- [Benzinga - Sep 30, 2026](https://app.bigdata.com/documents/D453315C3D577D7BB4D2371324094403?cnum=1): FICO downgrade by BofA.
- [Benzinga - Sep 30, 2026](https://app.bigdata.com/documents/35A072D01DC6A62C42E120C0FB54372A?cnum=1): FICO price-target cuts by Barclays and Wells Fargo.
- [PubT - Sep 30, 2026](https://app.bigdata.com/documents/8953B3DE25E80E70CA811B0332685B06?cnum=2&cnum=1&cnum=3): FICO leverage.
- [Edgar SEC Filings (FICO 10-Q) - Jul 29, 2026](https://app.bigdata.com/documents/DD01B20C7F056EF856D4F773B75AB9F5?cnum=113): FICO ASR and buyback.
- [The Globe And Mail - Apr 16, 2026](https://app.bigdata.com/documents/06F1E6BE2E7EF877ADCED5D477B354F3?cnum=1&cnum=2): FICO regulatory pressure.
- [Quartr Transcripts (Deckers Q4 FY26) - May 21, 2026](https://app.bigdata.com/documents/54825CA004BB2D2C46A25123308992F4?cnum=24&cnum=17&cnum=55): DECK long-term growth outlook.
- [Quartr Reports (Deckers Q4 FY26) - May 21, 2026](https://app.bigdata.com/documents/471A9212C9499F4A84F18604F4988307?cnum=8): DECK FY27 guidance.
- [Quartr Transcripts (Deckers Q3 FY26) - Jan 29, 2026](https://app.bigdata.com/documents/1FCF5B92928B39CC9A9CA24CEE8BA005?cnum=23&cnum=30): DECK tariff headwind.
- [Quartr Reports (Pershing Square H1 2026) - Aug 13, 2026](https://app.bigdata.com/documents/B7468DF6A3C4B0797C7936CBDC9F4E31?cnum=35): UBER earnings growth and valuation.
- [Benzinga - Aug 6, 2026](https://app.bigdata.com/documents/6534A2D06A77526782E8D9771839F21C?cnum=1&cnum=3): UBER Q2 results and AV share of trips.
- [MT Newswires - Apr 15, 2026](https://app.bigdata.com/documents/C3906DE48974309D664F0F29074FBF92?cnum=1): UBER AV investment.
- [CNBC - Aug 14, 2026](https://app.bigdata.com/documents/80FC5AF11F5CE222AF45DAB41B4CB624?cnum=1): UBER and Pony.ai.
- [Alliance News - Jun 17, 2026](https://app.bigdata.com/documents/176403B968CA269EF0A77CF52A3ECB45?cnum=3): UBER robotaxi rollouts.
- [Quartr Transcripts (Nu Q2 2026) - Aug 13, 2026](https://app.bigdata.com/documents/DAE782291CC6BEA039500A7D92291F61?cnum=11&cnum=56&cnum=17&cnum=14&cnum=3): NU quarterly profit, customers, deposits.
- [Quartr Reports (Nu Q4 2025) - Feb 25, 2026](https://app.bigdata.com/documents/EE0633C16A401D5855B06EE9403216E0): NU delinquency outlook.
- [Edgar SEC Filings (Nu 20-F) - Apr 8, 2026](https://app.bigdata.com/documents/F658A9E28B67909C2BBA47D6E1076533?cnum=173&cnum=91&cnum=40&cnum=573): NU macro risk.
- BSX 2026 guidance, cyberattack and downgrade facts come from news retrieved through Bigdata.com earlier in this research: MT Newswires Sep 8 and Sep 17, 2026; Nasdaq Sep 3, 2026; PubT Sep 28, 2026. Their document links were not retained.

*Valuation assumptions (fair multiples, growth rates, discount rates and historical-multiple approximations) are the analyst's own and are listed in §0 and §B. They are not sourced data.*
