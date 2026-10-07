# Nasdaq-100 "Fair Value + High Growth" Screen

**Data date:**
- Prices are closing prices on **Oct 6, 2026**.
- Fundamentals are the latest reported fiscal year (FY) plus trailing twelve months (TTM) as of Oct 7, 2026.
- Consensus estimates and price targets are as of Oct 7, 2026.

**Data source:**
- Fundamentals, ratios, estimates and price targets come from [Bigdata.com](https://bigdata.com) Corporate Fundamentals (provider: FMP).
- News, filings and transcripts were retrieved through Bigdata.com search and are cited inline.

**Conventions:**
- **FY** = reported fiscal year (GAAP unless stated otherwise). Several companies have non-December year-ends (MSFT Jun, INTU Jul, ADBE Nov, AVGO Nov, NVDA/WDAY/ADSK Jan, SNPS Oct).
- **TTM** = trailing twelve months. **NTM** = next twelve months, time-weighted from the current and next fiscal-year consensus.
- All forward EPS figures are **analyst consensus estimates**, not reported results. For ADBE, INTU, ADSK, WDAY, AVGO, CDNS, SNPS and AMD the consensus is on an **adjusted (non-GAAP)** basis, which excludes SBC and amortization.
- **N/M** = not meaningful (negative or distorted base year). **N/A** = not available or not applicable. No figures were invented to fill gaps.
- Foreign reporters were converted: PDD from CNY at ~7.1 per USD (per-ADS figures); ASML from EUR at ~1.17 USD.

> **This is not investment advice.** Fair values come from a model that depends on stated assumptions, especially fair multiples and discount rates. Treat them as a structured starting point for your own work.

---

## 0. Method, coverage and limitations (read first)

**1. Universe.**
- The official Nasdaq-100 constituent list was **not available** in the data tool. The universe was approximated as Nasdaq-listed (XNAS) common stocks with market cap above $20B, excluding financials, ETFs and funds. This captures roughly 155 names, a superset of the index.
- Energy and Materials constituents (e.g., LIN, FANG, BKR) and Utilities (CEG, AEP, XEL) were not modelled. They rarely meet the growth bar without commodity help.
- **Coverage.** A full bottom-up DCF on every constituent was not feasible. About 37 companies were pulled in detail; **22 were fully modelled and scored**. The other 15 were screened out on a single decisive fact, shown in the table below.

| Ticker | Why it was not quantitatively scored |
|---|---|
| AAPL | 3-year revenue CAGR ~1.8% (FY22–FY25); ~35x NTM EPS. Fails growth. |
| COST | 3-year revenue CAGR ~7.8%; ~41x NTM. Fails growth and valuation. |
| AMZN | **TTM free cash flow negative** (AI capex of $132B in 2025). Fails the FCF > 0 test. FY26 EPS inflated by investment gains. |
| PLTR | ~84x FY27 EPS; consensus target $183 is below the $192 price. Overvalued. |
| MU | Memory super-cycle: FY23 was a loss, FY27 consensus EPS $174 implies ~6x **peak** earnings. On normalized EPS (FY23–FY28 average ≈ $77) it trades at ~13.6x. Cyclical; excluded. |
| KLAC | 3-year revenue CAGR 8.9%; 32x NTM. Fails growth. |
| TMUS | Revenue CAGR ~3.5%; ROIC ~7%. Fails growth and quality (cheap: ~12x FY27). |
| REGN | Revenue CAGR 5.6%; EPS CAGR 2.8%. Fails growth (cheap: 12.6x NTM). |
| CPRT | Revenue CAGR 6.5%, FY26 flat. Fails growth (cheap: 17x, net cash). |
| IDXX | Revenue CAGR 8.5%; 33x. Fails growth. |
| ORLY | Revenue CAGR 7.3%, EPS CAGR 8.3%. Fails growth. |
| AXON | GAAP operating loss in FY25; SBC 22.8% of revenue; FCF falling. Fails quality. |
| DASH | Insufficient profit history (first meaningful GAAP profit in 2024); ~46x NTM. |
| Others (CRWD, PANW, DDOG, TEAM, TTWO, MPWR, ROST, CTAS, ADP, PAYX, VRSK, MNST, GILD, AMGN) | Not pulled in detail. Most fail either the growth bar or valuation at current prices; **this is a coverage gap, not a verdict.** |

**2. Fair value formula** (the user's weights): **FV = 40% DCF + 25% earnings-based + 20% FCF-based + 15% historical/peer.** Identical to the NYSE screen.

| Component | How it was calculated |
|---|---|
| **DCF** | 10-year, two-stage model on FCF per share. Growth `g` for years 1–5, fading linearly to 3% by year 10; terminal growth 3%. Discount rate 8.5–13% depending on risk (PDD 13% for China/VIE). When SBC exceeds 5% of revenue, **FCF is reduced by SBC** (ADBE, INTU, META, ISRG, WDAY, ABNB, GOOGL, AVGO, ADSK, VRTX, CDNS). **Conservative case:** g × 0.6, rate +1 pt. **Bull case:** g × 1.3, rate −0.5 pt. |
| **Earnings-based** | NTM consensus EPS × a "fair" P/E reflecting growth, quality and peers (analyst assumption, shown below). |
| **FCF-based** | Forward FCF per share (unadjusted TTM × (1 + g)) × a fair P/FCF. |
| **Historical/peer** | NTM EPS × an approximate 5-year median forward P/E or a peer median. **Approximations; check independently.** |

- **MELI:** FCF is distorted by its credit book and payment float, so the DCF is run on earnings and the FCF leg is dropped (weights re-normalized).
- **Important caveat on the hyperscalers (MSFT, META, GOOGL).** Their FCF is temporarily depressed by record AI capex, and META/GOOGL are also SBC-adjusted. An FCF-based DCF therefore produces low values for them. Their earnings-based legs alone point to roughly fair value (e.g., GOOGL ~$353, META ~$800, MSFT ~$620). Their "Overvalued" readings are partly a capex-cycle artefact; see §G.

**3. Scores** (same as NYSE):
- **Growth (0–100):** 3-year revenue CAGR 35, 3-year EPS CAGR 35 (forward growth substituted where history is N/M), 3-year FCF CAGR 20, forward EPS growth 10.
- **Quality (0–100):** ROIC 40, operating margin 25, net debt/EBITDA 20, moat 15.
- **Valuation (0–100):** margin of safety 60, forward PEG 40.
- **Risk (0–100, 100 = lowest risk):** judgment rating covering leverage, regulation, cyclicality, China/EM exposure, governance.
- **Overall (/100):** Growth 25, Profitability 20, Financial Strength 15, Valuation 25, Moat 10, Management 5.

**4. Margin-of-safety classes:** >30% Excellent · 20–30% Attractive · 10–20% Reasonable · 0–10% Fully valued · <0% Overvalued.

**Headline result.** Applied strictly, the hard filter leaves **three companies: Booking Holdings (BKNG), PDD Holdings (PDD) and AppLovin (APP)**. None is clean:
- **BKNG** is the cleanest pass, but faces an FTC complaint recommendation and AI-agent disintermediation fears.
- **PDD** passes on trailing numbers, but growth has slowed sharply (Q2 2026 revenue +8%, net income −12%) and it carries China/VIE and governance risk.
- **APP** passes on the numbers but has **serious red flags**: securities class actions, a reported SEC inquiry and short-seller allegations. It is treated as speculative only.

The filter requires: Growth, Quality and Valuation ≥ 70; Overall ≥ 75; revenue CAGR ≥ 10%; EPS CAGR ≥ 12%; FCF > 0; ROIC > 12%; upside ≥ 20%; MoS ≥ 15%; no balance-sheet flag.

**The pattern differs from the NYSE.** The Nasdaq's AI winners (NVDA, AVGO, AMD, ASML, MU, PLTR, FTNT) are fully valued or overvalued after big 2026 runs. The cheapest growth names are the **2026 "AI-loser" software and internet de-ratings**: ADBE (−32% YTD), INTU (−56%), BKNG (−26%), NFLX (−27%), APP (−59%) and WDAY. Their valuations assume AI damages their franchises. The model, which trusts consensus earnings, says that fear is overdone. **That is the key bet in this report.** If consensus earnings are wrong because AI erodes these businesses, the margins of safety below are overstated.

---

## A. Top 20 ranked list

**Column definitions:** Rev/EPS/FCF CAGR = 3-year, FY2022 → FY2025 (or latest FY), GAAP. ROIC = TTM (calculated). P/E = forward NTM consensus. P/FCF = TTM.

| Rank | Ticker | Company | Sector | Mkt Cap ($B) | Rev CAGR 3y | EPS CAGR 3y | FCF CAGR 3y | ROIC (TTM) | ND/EBITDA | Fwd P/E (NTM) | P/FCF (TTM) | Price | Fair Value | Upside | MoS | Growth | Quality | Valuation | Overall | Hard filters |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | NVDA | NVIDIA | Tech (semis) | 5,795 | 100.0% | 206%¹ | 192%¹ | ~100% | net cash | 17.3x | 45.6x | $239.24 | $254 | 6% | 6% | 97 | 98 | 63 | 89 | Fails: V, Upside, MoS |
| 2 | PDD | PDD Holdings (ADS) | Cons. Cyclical (China e-com) | 111.6 | 48.6% | 43.9% | N/M (low base) | ~40% | net cash | 7.1x | 7.5x | $78.40 | $131 | 66% | 40% | 97 | 79 | 100 | 89 | **PASS** (high risk) |
| 3 | BKNG | Booking Holdings | Cons. Cyclical (online travel) | 122.1 | 16.4% | 29.0% | 13.7% | >50% (neg. equity) | 0.2x | 13.2x | 12.7x | $157.63 | $291 | 84% | 46% | 71 | 89 | 100 | 88 | **PASS** |
| 4 | APP | AppLovin | Tech (ad-tech) | 93.7 | 24.8% | N/M² | 112% | ~100% | 0.2x | 14.7x | 20.9x | $278.78 | $358 | 28% | 22% | 86 | 93 | 82 | 84 | **PASS** (red flags) |
| 5 | ADBE | Adobe | Tech (software) | 94.7 | 10.5% | 18.3% | 10.0% | ~60% | 0.1x | 8.7x³ | 8.6x | $238.12 | $529 | 122% | 55% | 44 | 91 | 100 | 81 | Fails: G |
| 6 | NFLX | Netflix | Comm. Services | 286.0 | 12.6% | 36.3% | 16.9% (2y) | ~36% | 0.4x | 18.3x | 26.2x | $68.69 | $96 | 40% | 29% | 67 | 85 | 84 | 81 | Fails: G |
| 7 | INTU | Intuit | Tech (software) | 79.3 | 14.3% | 25.0% | 21.6% | ~23% | 0.5x | 12.2x³ | 9.1x | $289.81 | $596 | 106% | 51% | 74 | 67 | 100 | 80 | Fails: Q |
| 8 | MELI | MercadoLibre | Cons. Cyclical (LatAm) | 94.2 | 38.9% | 60.0% | N/A (float) | ROE ~30% | credit book | 36.6x | N/A | $1,857.99 | $1,792 | −4% | −4% | 100 | 54 | 52 | 72 | Fails: Q, V, Overall, Upside, MoS |
| 9 | AVGO | Broadcom | Tech (semis) | 1,788 | 24.4% | 21.6% | 18.2% | ~18% | 1.2x | 20.3x³ | 45.4x | $375.81 | $384 | 2% | 2% | 86 | 64 | 62 | 71 | Fails: Q, V, Overall, Upside, MoS |
| 10 | ASML | ASML (ADR) | Tech (semicap) | 706.9 | 15.6% | 20.5% | 15.4% | very high | net cash | 31.4x | 54.9x | $1,834.10 | $1,440 | −21% | −27% | 65 | 94 | 25 | 71 | Fails: G, V, Overall, Upside, MoS |
| 11 | ADSK | Autodesk | Tech (software) | 48.8 | 12.9% | 11.4% | 6.0% | ~39% | 0.3x | 17.7x³ | 17.2x | $231.28 | $262 | 13% | 12% | 32 | 83 | 65 | 67 | Fails: G, V, Overall, EPS, Upside, MoS |
| 12 | MSFT | Microsoft | Tech (software/cloud) | 3,930 | 16.0% | 22.9% | 4.0% | ~25% | 0.5x | 25.6x | 58.7x | $529.30 | $461 | −13% | −15% | 59 | 83 | 37 | 67 | Fails: G, V, Overall, Upside, MoS |
| 13 | META | Meta Platforms | Comm. Services | 1,882 | 19.9% | 39.8%⁴ | 4.2% (4y) | ~28% | 0.5x | 22.2x | 45.9x | $738.88 | $567 | −23% | −30% | 68 | 81 | 30 | 66 | Fails: G, V, Overall, Upside, MoS |
| 14 | GOOGL | Alphabet (A) | Comm. Services | 4,208 | 12.5% | 33.4% | 6.9% | ~31% | net cash | 23.7x⁵ | 79.4x | $347.68 | $209 | −40% | −66% | 57 | 84 | 30 | 66 | Fails: G, V, Overall, Upside, MoS |
| 15 | ISRG | Intuitive Surgical | Healthcare (med-tech) | 143.0 | 17.4% | 29.2% | 37.5% | ~21% | net cash | 34.4x | 44.5x | $404.76 | $376 | −7% | −8% | 82 | 69 | 21 | 66 | Fails: Q, V, Overall, Upside, MoS |
| 16 | ABNB | Airbnb | Cons. Cyclical (travel) | 95.2 | 13.6% | 13.0% | 10.9% | high | net cash | 26.7x | 19.5x | $160.39 | $167 | 4% | 4% | 43 | 73 | 52 | 64 | Fails: G, V, Overall, Upside, MoS |
| 17 | WDAY | Workday | Tech (software) | 48.9 | 15.4% | N/M | 28.9% | ~12% | net cash | 15.9x³ | 16.4x | $186.55 | $215 | 15% | 13% | 65 | 40 | 73 | 63 | Fails: G, Q, Overall, ROIC, Upside, MoS |
| 18 | FTNT | Fortinet | Tech (cybersecurity) | 140.3 | 15.5% | 31.8% | 15.4% | very high | net cash | 51.7x | 45.0x | $191.27 | $127 | −34% | −51% | 68 | 88 | 0 | 62 | Fails: G, V, Overall, Upside, MoS |
| 19 | VRTX | Vertex Pharma | Healthcare (biotech) | 127.5 | 10.6% | 6.1% | −6.6% | ~30% | net cash | 24.5x | 33.6x | $502.31 | $415 | −17% | −21% | 18 | 86 | 27 | 55 | Fails: G, V, Overall, EPS, Upside, MoS |
| 20 | AMD | Advanced Micro Devices | Tech (semis) | 1,059 | 13.6% | 46.7% | 29.0% | ~6% (GAAP) | net cash | 46.7x³ | 157x | $649.42 | $293 | −55% | −122% | 80 | 33 | 29 | 54 | Fails: Q, V, Overall, ROIC, Upside, MoS |

Also modelled (ranks 21–22): **CDNS** (FV $238, MoS −51%, Overall 54) and **SNPS** (FV $482, MoS −5%, Overall 32; ND/EBITDA 4.6x leverage flag after the Ansys deal).

¹ Off a tiny FY23 base; NVDA growth is AI-capex driven and cyclical. ² APP GAAP EPS was negative in FY22; 2-year CAGR ~215%. Forward 2-year growth of ~18% is used in scoring. ³ Adjusted (non-GAAP) consensus EPS. ⁴ META off a depressed FY22 base; 4-year EPS CAGR is 14.3%. ⁵ GOOGL FY26 EPS is inflated by investment gains; NTM uses a normalized ~$14.7.

---

## B. Top 10: detailed analysis

The Top 10 is the ten highest-Overall companies with revenue CAGR ≥ 10% **and** a positive margin of safety. MELI (overvalued) is excluded and discussed in §G.

| # | Ticker | Stress value* | Bear (model) | Base FV | Bull | Ideal entry (25% MoS) | Expected 3-year return** | Street target |
|---|---|---|---|---|---|---|---|---|
| 1 | BKNG | $167 | $211 | $291 | $367 | ≤ $218 (now) | ~33%/yr | $232 |
| 2 | PDD | $66 | $100 | $131 | $158 | ≤ $98 (now) | ~29%/yr (very high variance) | $99 |
| 3 | APP | $190 | $265 | $358 | $446 | ≤ $268 | ~26%/yr (speculative) | $532 |
| 4 | ADBE | $219 | $399 | $529 | $649 | ≤ $397 (now) | ~45%/yr | $270 |
| 5 | NFLX | $56 | $70 | $96 | $122 | ≤ $72 (now) | ~29%/yr | $91 |
| 6 | INTU | $237 | $447 | $596 | $736 | ≤ $447 (now) | ~39%/yr | $380 |
| 7 | NVDA | $124 | $185 | $254 | $324 | ≤ $190 | ~25%/yr (cyclical) | $339 |
| 8 | AVGO | $200 | $275 | $384 | $498 | ≤ $288 | ~36%/yr (cyclical) | $510 |
| 9 | ADSK | $170 | $199 | $262 | $321 | ≤ $197 | ~22%/yr | $301 |
| 10 | ABNB | $108 | $125 | $167 | $206 | ≤ $125 | ~16%/yr | $181 |

\* **Stress value** = NTM EPS × a trough multiple (BKNG 14x, PDD 6x, APP 10x, ADBE 8x, NFLX 15x, INTU 10x, ADSK 13x, ABNB 18x). For NVDA and AVGO, EPS is also cut 40% to model an AI-capex downturn (×15x and ×18x).

\*\* The expected 3-year return assumes NTM EPS compounds at the forward 2-year consensus growth rate and the stock re-rates to the fair P/E. Dividends are excluded. **These are optimistic** because they need both delivered growth and a re-rating. A realistic haircut is 30–40%, more for ADBE and INTU, where the model's fair value is roughly double the street's.

**Note on ADBE and INTU.** Their model fair values ($529 and $596) are far above consensus price targets ($270 and $380). The gap exists because the model assumes consensus earnings are durable and applies a normal software multiple (18–22x). The street is already discounting AI disruption into the terminal value. Using street targets instead, MoS would be ~12% (ADBE) and ~24% (INTU). Both are still cheap, but less dramatically.

### 1. Booking Holdings (BKNG): Excellent margin of safety, the cleanest PASS

**Thesis.** Booking is the world's largest online travel agency. It generates an operating margin of ~34.5% and a 3-year EPS CAGR of 29%, and it is shrinking its share count fast (diluted shares 1,034M → 816M split-adjusted, about −21% in four years). It trades at ~13x NTM EPS and 12.7x TTM P/FCF, near its 52-week low, because investors fear AI agents will disintermediate OTAs.

**Recent results.** Q2 2026 room nights, gross bookings, revenue and adjusted EBITDA all beat the high end of guidance. Revenue rose 8%, adjusted EPS rose 15% and the share count fell 6% ([Quartr Transcripts - Aug 04, 2026](https://app.bigdata.com/documents/EFA580B76A98CCB280249BADCC14E673)). Booking repurchased $7.4B of stock in H1 2026 at ~$173/share, generated $3.6B of FCF in the quarter, and raised run-rate cost savings to ~$650M (same source).

**Why growth can last 3–5 years.** Connected Trip transactions growing low double digits, merchant mix rising to ~73% of gross bookings, US and Asia expansion, and Genius loyalty (L2/L3 members are a high-50s % share of room nights) ([Quartr Transcripts - Aug 04, 2026](https://app.bigdata.com/documents/EFA580B76A98CCB280249BADCC14E673)). Consensus EPS: FY26 $10.46 → FY27 $12.36 → FY28 $14.32.

**Moat.** Two-sided network (supply breadth + traveler traffic) and direct/loyalty traffic (strong). Management argues "trusted brands, proprietary travel data, broad supplier relationships, and global reach" are the AI-era moat (same source).

**Fair value: $291.**

| Component | Value | Inputs |
|---|---|---|
| DCF (conservative / base / bull) | $231 / $354 / $475 | TTM FCF $12.42/sh, g 12%, r 9% |
| Earnings-based | $238 | NTM EPS $11.9 × 20x |
| FCF-based | $250 | 18x forward FCF |
| Historical/peer | $262 | 22x |

**Risks.**
1. AI agents (Google, OpenAI) intermediate travel search and squeeze take rates.
2. FTC staff intend to recommend a complaint against Priceline over fees and disclosures ([Edgar SEC Filings (10-Q) - Aug 04, 2026](https://app.bigdata.com/documents/BE126BDACB44352E2DCCFC8059F093ED?cnum=41&cnum=47&cnum=45&cnum=46)).
3. European regulation: Spain's CNMC fine (€472M liability recorded), Swiss commission order, hotel parity class actions (same filing).
4. Travel demand shock (Middle East conflict noted by management).
5. Revenue growth is slowing to ~8–9% (FY26 consensus +8.7%), so EPS growth leans on buybacks.

**What would make the thesis wrong.** Room-night growth falling to low single digits while marketing spend rises (a sign of lost direct traffic).

**Entry.** ≤ $218; current $157.63, already below. **Red flags:** regulatory, not financial. Negative equity is the result of buybacks, not distress (ND/EBITDA 0.2x).

### 2. PDD Holdings (PDD): Excellent margin of safety, but high risk

**Thesis.** PDD trades at ~7x NTM EPS. Its net cash of ~$69B is about 62% of market cap, and FY25 revenue was CNY 432B with net income of CNY 97.8B ([Edgar SEC Filings (20-F) - Apr 29, 2026](https://app.bigdata.com/documents/8D222E498981F542ABEF30CCCF8692E3?cnum=193&cnum=195&cnum=326&cnum=453)). Excluding cash, the operating business trades at about 3x earnings.

**The problem: growth has collapsed from its historical rate.** Q2 2026 revenue was CNY 112.4B, up only 8%, and net income fell 12% as PDD keeps reinvesting in merchant support and a CNY 100B first-party brand program ([Quartr Transcripts - Aug 24, 2026](https://app.bigdata.com/documents/36C3048824864CF78BA1D2826BC76C82)). Management told investors that competition and regulation "will inevitably bring more challenges and weigh on our future performance, putting pressures on our profitability in short term" ([Quartr Transcripts - Mar 25, 2026](https://app.bigdata.com/documents/D5EB8DC673634A5024CA58FA6A23E299?cnum=14&cnum=13&cnum=26)). The 3-year CAGRs (revenue 48.6%, EPS 43.9%) that pass the screen are backward-looking.

**Fair value: $131** (DCF at a 13% discount rate; P/E 10x; historical 12x). Cash is not added, which is conservative.

**Risks.** (1) VIE structure and US delisting/China regulatory risk; (2) Temu exposure to US/EU tariffs and de-minimis rule changes; (3) no dividend or buyback, so the cash may never reach ADS holders; (4) opaque disclosure and limited management access; (5) margin reinvestment without a clear return.

**Entry.** ≤ $98 (now). Size small; consensus is HOLD (13 Buy / 14 Hold / 1 Sell).

### 3. AppLovin (APP): Attractive on the numbers, but significant red flags

**Thesis.** AppLovin has 76% operating margins, FCF up from $0.4B to $3.9B in three years and ~100% ROIC. It trades at ~15x NTM EPS after a −59% YTD decline.

**Why it fell.** Q2 2026 revenue of $1.92B missed (+53% y/y) because "the pace of meaningful model improvement was lighter than normal", and the stock fell 19.6% ([MT Newswires - Aug 06, 2026](https://app.bigdata.com/documents/AA818AD3998FB4D012D1A50825F100B6?cnum=1)).

**Red flags.**
- Securities class actions filed, with a lead-plaintiff deadline of Nov 16, 2026 ([Benzinga - Oct 06, 2026](https://app.bigdata.com/documents/EF5DEDA1BF73F213390A0DC375729A26?cnum=3)).
- A reported SEC inquiry into data-collection practices ([MT Newswires - Feb 23, 2026](https://app.bigdata.com/documents/B23F9B29230121CB7735337E110CEE80?cnum=1)).
- Short-seller allegations, disputed by the company, that sent shares down 17% ([AOL - Oct 02, 2026](https://app.bigdata.com/documents/8693CF70A76BBED4093414614253DB74?cnum=2)).
- Rising competition from Meta and litigation with Unity ([Benzinga - Oct 02, 2026](https://app.bigdata.com/documents/EC09F7251F01D4A4792B7CF9E050DBE6?cnum=1)).

**Fair value: $358** (r 11% for legal risk; P/E 18x). **Verdict:** passes the quantitative filter but is **excluded from the conviction list**. Speculative capital only, until the legal and regulatory picture clears.

### 4. Adobe (ADBE): Excellent margin of safety, fails the Growth score

**Thesis.** Adobe trades at ~8.7x NTM adjusted EPS and 8.6x TTM P/FCF, with a ~36% GAAP operating margin and a shrinking share count (481M → ~400M targeted for FY26). FY26 guidance was raised to adjusted EPS of $24.45–24.50 on revenue of $26.58–26.63B ([MT Newswires - Sep 11, 2026](https://app.bigdata.com/documents/58671562C7C429818F834E30893FB3BA?cnum=2)). AI-first ARR tripled to more than $500M, and freemium MAUs went from 50M to 90M ([PubT - Aug 21, 2026](https://app.bigdata.com/documents/9DA8BC3A039839F274D41BC547CE684B?cnum=2)).

**Why it fails.** Revenue CAGR of 10.5% and FCF CAGR of 10% give a Growth score of only 44. ARR growth is guided to slow to ~10.2% ([MT Newswires - Sep 11, 2026](https://app.bigdata.com/documents/58671562C7C429818F834E30893FB3BA?cnum=2)).

**Risks.**
1. Generative AI pressures paid seats and pricing (BofA) ([MT Newswires - Jul 07, 2026](https://app.bigdata.com/documents/AC91DA5AFEB04B9D7102952C0AA88B61?cnum=2)).
2. Leadership turnover: the CEO is stepping down and the CFO resigned in June (same source). Morgan Stanley went underweight with a $240 target ([CNBC - Jul 20, 2026](https://app.bigdata.com/documents/2736871B6D6A35B58D5C57AFA39FA93D?cnum=4)).
3. Freemium push and deferred Creative Cloud price changes cost ~$0.5B of ARR ([PubT - Aug 21, 2026](https://app.bigdata.com/documents/9DA8BC3A039839F274D41BC547CE684B?cnum=2)).
4. SBC is 8.2% of revenue (handled by the SBC-adjusted DCF).

**Fair value: $529** (model) vs street $270. Entry ≤ $397 (now). **Classic "value trap or value" debate.** Cheap on any measure if earnings hold.

### 5. Netflix (NFLX): Attractive margin of safety, Growth score 67 (just misses)

**Thesis.** Netflix has ~29.5% operating margins, ~36% ROIC and a 3-year EPS CAGR of 36%. It trades at ~18x NTM EPS, down from more than 40x in mid-2025 ([Edgar SEC Filings (Pershing Square N-CSRS) - Aug 21, 2026](https://app.bigdata.com/documents/C8BFCC6C41A9F23D426B87A6573A85CE?cnum=42)). FY26 guidance is revenue of $51.0–51.4B (+13–14%), a 31.5% operating margin and ad revenue doubling to ~$3B ([Alliance News - Jul 16, 2026](https://app.bigdata.com/documents/4EB92E73BD77AF52B347B9751DC42EAD?cnum=2)). Netflix also collected a $2.8B termination fee after losing the WBD bid (Pershing Square, same source).

**Risks.** Engagement is slipping: Wells Fargo went underweight ($57 target) and estimates viewing hours per subscriber are down ~8% ([Benzinga - Sep 18, 2026](https://app.bigdata.com/documents/F876C6F748B775E02FC6E2718788AF81?cnum=1)). YouTube and short-form video are competitors, AI-generated video is a long-run threat, and the stock has fallen after each of its last four reports ([The Globe And Mail - Oct 01, 2026](https://app.bigdata.com/documents/7111C7EAC0385AB481E3E11B8B97A000?cnum=2)). The next report is Oct 20.

**Fair value: $96.** Entry ≤ $72 (now).

### 6. Intuit (INTU): Excellent margin of safety, fails the Quality score (67, just under 70)

**Thesis.** Intuit grew revenue at 14.3% and EPS at 25% (3-year CAGRs), with FCF growth of 21.6%, yet trades at ~12x NTM adjusted EPS and 9x P/FCF after a −56% YTD decline. FY27 guidance is revenue +9–10% and EPS +22%, with the stock at about 13x forward on AI fears ([The Globe And Mail - Oct 06, 2026](https://app.bigdata.com/documents/4F836EA7F81B499A0D65866B12DA9732?cnum=3)).

**Why it fails Quality.** Calculated ROIC is ~23%, held down by goodwill (Credit Karma, Mailchimp), and the GAAP operating margin is 28.8%. SBC is 9.6% of revenue.

**Risks.** (1) AI tax agents commoditize TurboTax; (2) IRS Direct File and policy risk; (3) Credit Karma credit-cycle exposure; (4) Mailchimp stagnation; (5) a growth guide of +9–10% is now below the 10% bar.

**Fair value: $596** (model) vs street $380. Entry ≤ $447 (now).

### 7. NVIDIA (NVDA): Fully valued (MoS 6%), highest Growth and Quality scores

**Thesis.** NVIDIA's revenue grew from $27B (FY23) to $216B (FY26). It has ~60% operating margins, net cash, and trades at ~17x NTM EPS. Consensus FY28 EPS is $15.77 (range very wide; FY28 sales estimates span $517–749B).

**Why it is not a buy here.** Even with a 22x fair P/E, the DCF (on FCF of $5.25/sh at 20% growth and a 10% discount rate) holds fair value to ~$254. A 40% EPS cut in an AI-capex digestion gives a stress value of ~$124.

**Risks.** Hyperscaler capex cycle, customer concentration, China export controls, custom ASIC competition (AVGO), and estimate dispersion.

**Entry.** ≤ $190 (25% MoS).

### 8. Broadcom (AVGO): Fully valued (MoS 2%)

**Thesis.** AI ASIC and networking growth: consensus sales of $106B (FY26) → $174B (FY27) → $281B (FY28). At ~20x NTM adjusted EPS the PEG is undemanding.

**Why not.** GAAP ROIC is ~18%, held down by VMware goodwill. SBC is 11.8% of revenue, and FCF is SBC-adjusted to $6.68/sh. Customer concentration (Google, Meta, OpenAI) is high.

**Fair value: $384.** Entry ≤ $288.

### 9. Autodesk (ADSK): Reasonable margin of safety (12%)

**Thesis.** Durable design-software franchise with ~39% ROIC. Consensus FY27 sales are $8.32B (+15.5%), and the stock trades at 17.7x NTM adjusted EPS.

**Why not.** GAAP EPS CAGR is 11.4% (fails the 12% bar), and the FCF CAGR of 6% reflects billing-model change noise. SBC is 10.9% of revenue; SBC-adjusted FCF is $7.54/sh.

**Fair value: $262.** Entry ≤ $197.

### 10. Airbnb (ABNB): Fully valued (MoS 4%)

**Thesis.** Asset-light platform with net cash and FY26 consensus sales of $14.2B (+15%).

**Why not.** SBC is 12.9% of revenue (SBC-adjusted FCF $5.66/sh), and the stock trades at ~27x NTM. Growth score is 43.

**Fair value: $167.** Entry ≤ $125.

---

## C. Top 5 highest-conviction picks

Ranked by risk-adjusted expected return, combining overall score, margin of safety, risk score and red-flag status. APP is excluded for red flags despite passing.

| | **BKNG** | **INTU** | **ADBE** | **NFLX** | **PDD** |
|---|---|---|---|---|---|
| Current price | $157.63 | $289.81 | $238.12 | $68.69 | $78.40 |
| Fair value | $291 | $596 (street $380) | $529 (street $270) | $96 | $131 |
| Margin of safety | 46% (Excellent) | 51% (Excellent) | 55% (Excellent) | 29% (Attractive) | 40% (Excellent) |
| 3-year revenue CAGR | 16.4% | 14.3% | 10.5% | 12.6% | 48.6% (now +8%) |
| 3-year EPS CAGR | 29.0% | 25.0% | 18.3% | 36.3% | 43.9% |
| ROIC (TTM) | >50% | ~23% | ~60% | ~36% | ~40% |
| FCF growth (3-year CAGR) | 13.7% | 21.6% | 10.0% | 16.9% (2y) | N/M (low base) |
| Expected 3-year CAGR return (model; haircut) | ~20–33% | ~20–39% | ~15–45% | ~18–29% | ~15–29% |
| Risk level | Medium | Medium | Medium–High | Medium | **High** |
| Ideal entry price | ≤ $218 (now) | ≤ $447 (now) | ≤ $397 (now) | ≤ $72 (now) | ≤ $98 (now) |
| Filter status | **PASS** | Fails Q (67) | Fails G (44) | Fails G (67) | **PASS** |
| Thesis | Network-effect OTA at 13x EPS with 6% annual share shrink | Tax/SMB platform at 12x after a −56% AI scare | Creative + document monopoly at <9x EPS; turnaround optionality | Global streaming leader de-rated 50%; ads doubling | 7x EPS with 62% of market cap in net cash; growth reset |

---

## D. Top 5 by largest margin of safety

| Ticker | Margin of safety | Comment |
|---|---|---|
| ADBE | 55% | Fails Growth score; street target ($270) implies only ~12%. |
| INTU | 51% | Fails Quality by 3 points (goodwill-depressed ROIC). |
| BKNG | 46% | Full PASS. |
| PDD | 40% | Full PASS; growth reset and China/VIE risk. |
| NFLX | 29% | Growth score 67; engagement worries. |

---

## E. Top 5 highest-quality growth companies

Quality score combined with sustained growth, regardless of price.

| Ticker | Quality score | Why | Valuation today |
|---|---|---|---|
| NVDA | 98 | ~100% ROIC, 60%+ operating margin, net cash | Fully valued (MoS 6%) |
| ASML | 94 | EUV monopoly, net cash, 35% operating margin | **Overvalued** (MoS −27%, 31x NTM, +71% YTD) |
| ADBE | 91 | ~60% ROIC, 36% GAAP operating margin | Excellent (MoS 55%) |
| BKNG | 89 | 34.5% operating margin, very high ROIC | Excellent (MoS 46%) |
| FTNT | 88 | Very high ROIC, net cash, 31% operating margin | **Overvalued** (MoS −51%, 52x NTM, below street target) |

APP scores 93 on Quality but is excluded here because of its red flags. MSFT (83, moat 10) is the best large-cap compounder but is fully priced on capex-depressed FCF.

---

## F. Top 5 potentially undervalued (fail at least one growth or quality screen)

| Ticker | Why it looks cheap | Why it is not a "high growth" pick |
|---|---|---|
| ADBE | 8.7x NTM adjusted EPS, 8.6x P/FCF | Revenue CAGR 10.5%, FCF CAGR 10%; ARR slowing to ~10% |
| INTU | 12x NTM adjusted EPS, 9x P/FCF | ROIC ~23% (goodwill); FY27 revenue guide +9–10% |
| TMUS | ~12x FY27 EPS ($13.95); −18% YTD; street target $232 | Revenue CAGR ~3.5%; ROIC ~7% |
| REGN | 12.6x NTM; ~$13B net cash and investments | Revenue CAGR 5.6%; EYLEA biosimilar erosion |
| CPRT | ~17x; net cash $4.4B, no debt; −31% YTD | Revenue CAGR 6.5%; FY26 revenue flat |

---

## G. Stocks to avoid despite apparently attractive valuation

| Ticker | Looks cheap because… | Red flag |
|---|---|---|
| **APP** | 15x NTM, 76% operating margin, passes the filter | **Legal/regulatory:** class actions, a reported SEC inquiry and short-seller allegations (see §B.3). |
| **MU** | ~6x FY27 consensus EPS | **Peak cyclical earnings.** +266% YTD; FY23 was a loss; ~13.6x on normalized earnings. |
| **SNPS** | ~28x NTM adjusted EPS vs EDA history of 40x+ | **Leverage 4.6x ND/EBITDA** after Ansys; GAAP ROIC ~3%; FCF declining ($1.60B → $1.35B); GAAP EPS CAGR 8.5%. |
| **AXON** | −42% over 1 year; 39x adjusted EPS | GAAP operating loss; SBC 22.8% of revenue; FCF falling ($330M → $75M). |
| **WDAY** | 16x adjusted EPS, 16x P/FCF | SBC 17% of revenue; SBC-adjusted FCF only $4.38/sh; GAAP EPS N/M; ROIC ~12%. |
| **AMZN** | 20x TTM P/E | TTM FCF negative; EPS inflated by investment gains (FY27 consensus $10.63 is *below* FY26 $12.77). |

**Overvalued (not cheap; listed for completeness):**
- **AMD** (MoS −122%; +203% YTD; consensus target $608 below price).
- **FTNT** (MoS −51%; target $159 below price).
- **CDNS** (MoS −51%; 39x adjusted EPS).
- **PLTR** (~84x FY27 EPS; target below price).
- **ASML** (MoS −27%).
- **MELI** (MoS −4%; operating margin compressing to ~8%).
- **MSFT, META, GOOGL:** "Overvalued" on this FCF-heavy model because AI capex depresses FCF. On earnings alone they are roughly fairly valued. Not avoid-rated, but no margin of safety.

---

## H. Final "Best Risk/Reward" ranking

| Rank | Ticker | Margin of safety | Risk | One-line rationale |
|---|---|---|---|---|
| 1 | **BKNG** | 46% | Medium | Cleanest full PASS: 13x EPS, buybacks, beat-and-raise execution |
| 2 | **INTU** | 51% | Medium | Category leader at 12x after a −56% AI scare; EPS guided +22% |
| 3 | **ADBE** | 55% | Medium–High | Sub-9x EPS for a near-monopoly; leadership and AI-seat risk |
| 4 | **NFLX** | 29% | Medium | De-rated 50%; ads and pricing still growing revenue 12–14% |
| 5 | **PDD** | 40% | High | Deep value with huge net cash; growth reset and VIE risk, so size small |
| 6 | **NVDA** | 6% | Medium–High | Best business on the list; buy on a capex scare below ~$190 |
| 7 | **ADSK** | 12% | Medium | Steady compounder; add below ~$200 |
| 8 | **AVGO** | 2% | Medium–High | AI ASIC leader; wait for ≤ $290 |
| 9 | **WDAY** | 13% | Medium | Cheap on adjusted numbers, but SBC eats half the FCF |
| — | APP | 22% | **Very high** | Speculative only; binary legal/regulatory outcome |

---

## 13. Red-flag check (shortlist)

| Ticker | Declining revenue | Earnings-quality issue | FCF deterioration | Excess debt | Excess SBC / dilution | Concentration / litigation | Peak or cyclical earnings | Overall |
|---|---|---|---|---|---|---|---|---|
| BKNG | No (slowing to ~8%) | No | No | No (0.2x) | No (shares −21%) | FTC, EU competition cases | Travel cycle | Clean–moderate |
| PDD | No (slowing to +8%) | Net income −12% in Q2 2026 | Yes (FY25 FCF below FY24) | No (net cash) | Low | VIE, tariffs, governance | No | **Moderate–high** |
| APP | No | Model-performance volatility | No | No | Low (3.8%) | **Class actions, SEC, short seller** | Ad cycle | **Significant red flag** |
| ADBE | No | Adjusted vs GAAP gap (SBC 8.2%) | No | No | Shares falling | CEO/CFO turnover | No | Moderate |
| NFLX | No | No | No | No | Low (0.8%) | Engagement decline | No | Clean–moderate |
| INTU | No | Adjusted vs GAAP gap (SBC 9.6%) | No | No | Moderate | Tax-policy/IRS | Credit Karma cycle | Moderate |
| NVDA | No | No | No | No (net cash) | Low | Customer concentration, export controls | **Yes (AI capex)** | Moderate (cyclical) |
| AVGO | No | Goodwill-heavy GAAP | No | 1.2x | **SBC 11.8%** | Customer concentration | AI capex | Moderate |
| ADSK | No | Billing-model noise | Volatile | No | SBC 10.9% | — | No | Moderate |
| ABNB | No | No | No | No (net cash) | **SBC 12.9%** | City regulation | Travel cycle | Moderate |

---

## Data sources

- **[Bigdata.com](https://bigdata.com) Corporate Fundamentals (FMP):** company tearsheets as of Oct 7, 2026, providing annual income statements, balance sheets and cash flows for FY2021–FY2026, TTM ratios, key metrics, analyst estimates, ratings and price performance. Covered: ADBE, INTU, META, MSFT, AMZN, BKNG, NVDA, NFLX, MELI, ISRG, VRTX, CDNS, WDAY, PDD, ABNB, CPRT, GOOGL, AVGO, AXON, ORLY, APP, DASH, AMD, KLAC, ASML, REGN, IDXX, FTNT, ADSK, SNPS, AAPL, COST, PLTR, MU, TMUS, plus the Nasdaq sector screens.
- [Quartr Transcripts (Booking Q2 2026) - Aug 04, 2026](https://app.bigdata.com/documents/EFA580B76A98CCB280249BADCC14E673): BKNG results, buybacks, cost savings, strategy.
- [Edgar SEC Filings (Booking 10-Q) - Aug 04, 2026](https://app.bigdata.com/documents/BE126BDACB44352E2DCCFC8059F093ED?cnum=41&cnum=47&cnum=45&cnum=46): BKNG FTC and EU regulatory matters.
- [Quartr Transcripts (PDD Q2 2026) - Aug 24, 2026](https://app.bigdata.com/documents/36C3048824864CF78BA1D2826BC76C82): PDD revenue and net income.
- [Quartr Transcripts (PDD Q4 2025) - Mar 25, 2026](https://app.bigdata.com/documents/D5EB8DC673634A5024CA58FA6A23E299?cnum=14&cnum=13&cnum=26): PDD profitability warning.
- [Edgar SEC Filings (PDD 20-F) - Apr 29, 2026](https://app.bigdata.com/documents/8D222E498981F542ABEF30CCCF8692E3?cnum=193&cnum=195&cnum=326&cnum=453): PDD FY23–FY25 revenue and net income.
- [MT Newswires - Aug 06, 2026](https://app.bigdata.com/documents/AA818AD3998FB4D012D1A50825F100B6?cnum=1): APP Q2 miss.
- [Benzinga - Oct 06, 2026](https://app.bigdata.com/documents/EF5DEDA1BF73F213390A0DC375729A26?cnum=3): APP class actions.
- [MT Newswires - Feb 23, 2026](https://app.bigdata.com/documents/B23F9B29230121CB7735337E110CEE80?cnum=1): APP SEC scrutiny.
- [AOL - Oct 02, 2026](https://app.bigdata.com/documents/8693CF70A76BBED4093414614253DB74?cnum=2): APP short-seller allegations.
- [Benzinga - Oct 02, 2026](https://app.bigdata.com/documents/EC09F7251F01D4A4792B7CF9E050DBE6?cnum=1): APP competition and Unity litigation.
- [MT Newswires - Sep 11, 2026](https://app.bigdata.com/documents/58671562C7C429818F834E30893FB3BA?cnum=2): ADBE FY26 guidance and ARR.
- [MT Newswires - Jul 07, 2026](https://app.bigdata.com/documents/AC91DA5AFEB04B9D7102952C0AA88B61?cnum=2): ADBE AI risk and leadership turnover (BofA).
- [CNBC - Jul 20, 2026](https://app.bigdata.com/documents/2736871B6D6A35B58D5C57AFA39FA93D?cnum=4): ADBE Morgan Stanley downgrade.
- [PubT - Aug 21, 2026](https://app.bigdata.com/documents/9DA8BC3A039839F274D41BC547CE684B?cnum=2): ADBE freemium shift and AI-first ARR.
- [The Globe And Mail - Oct 06, 2026](https://app.bigdata.com/documents/4F836EA7F81B499A0D65866B12DA9732?cnum=3): INTU FY27 guidance and valuation.
- [Alliance News - Jul 16, 2026](https://app.bigdata.com/documents/4EB92E73BD77AF52B347B9751DC42EAD?cnum=2): NFLX 2026 guidance.
- [Benzinga - Sep 18, 2026](https://app.bigdata.com/documents/F876C6F748B775E02FC6E2718788AF81?cnum=1): NFLX Wells Fargo downgrade and engagement.
- [Edgar SEC Filings (Pershing Square USA N-CSRS) - Aug 21, 2026](https://app.bigdata.com/documents/C8BFCC6C41A9F23D426B87A6573A85CE?cnum=42): NFLX de-rating and WBD termination fee.
- [The Globe And Mail - Oct 01, 2026](https://app.bigdata.com/documents/7111C7EAC0385AB481E3E11B8B97A000?cnum=2): NFLX post-earnings reaction history.

*Valuation assumptions (fair multiples, growth rates, discount rates, historical-multiple approximations, risk and moat ratings) are the analyst's own and are listed in §0 and §B. They are not sourced data.*
