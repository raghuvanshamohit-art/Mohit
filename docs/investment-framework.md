# The Investor's Framework

*A distilled framework and strategy built from a long-form conversation with a
veteran investor (33 years in Indian markets). The talk was about **mindset,
economics and behaviour** — not stock tips, PE ratios or "which option will
print money." This document turns that wisdom into something you can actually
use.*

> **Not investment advice.** This is an educational framework for thinking
> about money, markets and risk. Do your own work, size your own risk.

---

## The one-line thesis

> **Returns are the market's job. Your job is to assess risk, pay the right
> price, allocate well, and control your own behaviour.**

Everything below hangs off that sentence.

> **Want the numbers, not just the ideas?** The three operational questions —
> *which stock at what price, which asset to sell/buy, and how to pyramid* — are
> implemented as runnable engines. See [**The Decision System**](decision-system.md)
> (`python run.py value | rebalance | pyramid`, or the `web/strategy.html`
> calculator).

---

## Part 1 — Ten core beliefs (the mindset)

These are the foundations. If you disagree with these, the strategy in Part 3
won't make sense.

1. **Don't park long money in fixed instruments.** The things you actually
   want to buy (a flat, a car, a lifestyle) rise in price *faster* than a fixed
   deposit pays. A return that doesn't **beat inflation** quietly makes you
   poorer. *(His father saved diligently in FDs and the post office for 20
   years — and the flat's price ran away faster than the savings. The flat was
   never bought.)* Your minimum acceptable return is the one that **beats the
   price of the things you aspire to own.**

2. **Price is what you pay; value is what you get.** Investing does **not**
   begin with "what return will I get." It begins with **risk assessment.**
   *(The ₹500-note test: if a stranger offers you a genuine ₹500 note for ₹400,
   the right first thought isn't "bargain!" — it's "why is a normal person
   selling ₹500 for ₹400? Is the note fake?" The moment price drops, people
   forget to re-check value. That is exactly where losses come from.)*

3. **A good thing bought at the wrong price is still a bad investment.**
   *(First buy at Sensex ~4,400 in the Harshad Mehta era; ten years later, in
   2002, the Sensex was ~3,000.)* Even long-term holding does **not** guarantee
   profit. Price paid is everything.

4. **The market does not rise every year — and that's normal.** *(Over 33
   years, ~18 years made essentially no money. The other ~15 years made enough
   to never need to work for money again — he left his job 7 years early.)*
   Wealth is lumpy. The cost of the 15 good years is sitting through the 18
   flat ones without quitting.

5. **If you haven't made money in this market, the fault is usually yours, not
   the market's.** This market *does* create wealth. Start from that premise
   and the question becomes useful: *what am I doing wrong?*

6. **Your competition is not the market. It is yourself.** There are great
   investors in terrible economies and terrible investors in booming ones.
   Knowing the right thing ≠ doing it *(everyone knows not to text while
   driving; most people still do)*. **Understand yourself, not just the
   market.**

7. **Return is destiny; risk is your responsibility.** *(A newborn growing up
   is destiny — `niyati`. As a parent you don't ask "how fast will he grow?";
   you ask "when is the next vaccination?" You plug the dangers to growth.)* In
   investing, the economy growing is destiny. **Your job is to plug the risks
   on the way to that return — not to chase the return.**

8. **Almost no one actually becomes financially free — and it isn't the
   market's fault.** *(A leading flexicap fund compounded ~100×. Of ~60 lakh
   investors, only ~23 stayed the entire journey.)* The money was there. The
   **behaviour** wasn't.

9. **Invest in the direction, not the current state.** *(`Dasha` vs `disha`.)*
   A full moon looks grand but is about to shrink; a two-day crescent looks
   small and dark but its future is to grow. England's per-capita income is
   high but drifting down; India's is low but rising. **Always buy the
   trajectory, not the snapshot.**

10. **We are not one person — we are two.** A rational long-term human *and* an
    impulsive present-tense "monkey." *(A monkey won't give you its banana
    today for two bananas next week — it has no imagination of the future. When
    markets fall, your inner monkey wakes up and screams "no more money will be
    made here.")* **The investor's real skill is keeping the monkey caged.**

---

## Part 2 — The framework: four lenses

Run every decision through these four lenses, **in this order.**

### Lens 1 — Risk (assess this *first*, before return)

- Investing starts at risk, not reward. *(The CIA/Osama story: "My agency
  doesn't deal in certainty. We deal in uncertainty.")* You will **never** know
  what the market does tomorrow. The world is uncertain; your goals are
  certain. The whole game is manufacturing enough certainty to fund certain
  goals out of an uncertain market.
- So you hold **two views at once** and honour both:
  - *"The market will go up."* → keep buying.
  - *"The market can crash at any time, for no reason."* → stay allocated and
    prepared. **It is this second view that actually makes you the money**,
    because it keeps you solvent and buying when others panic.
- **Insurance + SIP logic:** *"I bought insurance so if I die, my family has
  money. I started an SIP so if I don't die, we have money."* Prepare for both
  outcomes; don't bet on one.

### Lens 2 — Value & price (learn to read the bond market)

- **If you don't understand bonds, you don't understand anything.** Money
  itself is a **commodity**; its price is **interest**; interest is set by the
  **bond market.** Interest rates silently set the price of *every* asset.
- **The shop example.** A shop costs ₹1 crore and nets ₹1 lakh/month (₹12
  lakh/yr ≈ 12%). Your bank pays 5%, so buying the shop doubles your yield —
  attractive. Overnight the RBI raises rates and the bank now pays 8%. The same
  shop is suddenly far less attractive, so you'd only pay ~₹80 lakh. **Nothing
  about the shop changed. Interest rates moved the price by ₹20 lakh.**
- **Value has three inputs:**
  1. **Utility / need** — water is worth ₹20 in the city and "everything you
     have" in the desert.
  2. **Interest rates (opportunity cost)** — your safe alternative return.
  3. **Growth** — how fast the cash flows grow.
  Feed these into a **discounted-cash-flow (intrinsic value)** calculation
  (an Excel sheet, or today an AI model, will do it). **Interest-rate changes
  move the *price*, not the *value*.** Grasp that and you understand long-term
  investing.
- **Voting machine vs weighing machine** *(Graham, via Buffett's teacher)*:
  - **Short term → voting machine.** Price = *opinion / emotion.* A popular
    actor with no record can win an election; a hyped stock can soar on zero
    substance.
  - **Long term → weighing machine.** Price = *performance / facts.* Jumping
    and shouting doesn't change your weight.
  - **Therefore:** to find value, study the **performance of the business** —
    don't even look at the price until *after* you like the business. Then
    check price against intrinsic value and refuse to overpay.
- **Japan, the cautionary tale.** The Nikkei fell from ~42,000 (1989) by more
  than half and took **33 years** to reclaim 42,000. Did Suzuki's profits
  collapse in 1989? No — profits kept growing. **The market didn't fall because
  the businesses were bad; it fell because investors had paid the wrong
  price.**

### Lens 3 — Macro & the India case (direction, not state)

Why hold the bulk of long-term money in **Indian equity**:

- **India is (almost) the only major economy where stock-market growth tracks
  GDP growth so tightly and positively.** Homework: for the top ~10–12
  economies, compare 10/20/30/40-year GDP growth with stock-market returns. In
  an ideal world they match; in most countries the market lags GDP badly.
  India is the standout. *(Korea grew GDP and per-capita faster over 40 years,
  yet markets and correlation tell a different story — study it yourself.)*
- **Survival instinct sets a floor.** The most powerful human instinct is
  survival. *(Imagine Indian incomes contracting 33% over 17 years the way
  Japan's economy did — with ~15% below the poverty line, the country wouldn't
  survive it.)* Probability says India's trajectory is **up**, not down.
- **India is the world's growth engine.** Of the new global wealth created over
  the next decade, India contributes the **highest share** of any large
  economy. Investing is **discounting the future**, and India's future is the
  strongest among majors.
- **ICOR is improving — uniquely.** Incremental Capital-Output Ratio: rupees of
  investment needed per rupee of extra GDP. India's is *falling* (≈6 → ≈5)
  while China's *rose* (≈3 → ≈5 → ≈8) and others worsen. India gets more growth
  per rupee invested, and savings → investment → GDP compounds.
- **Return on Equity is structurally higher in India** across most sectors —
  despite weaker efficiency, technology and labour — because of the demand
  side and capital discipline.
- **Appetite for risk capital is here.** Indians are willing to put risk
  capital into equities *(derivative turnover ran to ~400×+ cash turnover)*.
  That willingness is a national asset — the behaviour just needs fixing.
- **The self-correcting mechanism is the rupee.** India is a **consumption /
  import economy**, not an export model; imports exceed exports, so when
  dollars don't flow in, the rupee weakens. **A weakening rupee is *good*** — it
  forces discipline and reform, and historically the market tends to be strong
  the year *after* a sharp rupee fall. *(You only eat the home khichdi after
  the rich restaurant food upsets your stomach — you reform when it hurts.)*
- **Reforms come only when business stops earning.** *(Cyclical vs structural:
  guests sleeping over is cyclical and self-resolves; a growing family needing
  more rooms is structural and forces you to change the structure.)* When EPS
  stops rising, capex and jobs stall, and *that* is when governments act — e.g.
  GST / income-tax cuts arrive **because EPS wasn't rising.**
- **EPS growth is the whole story.** Post-COVID EPS grew ~60% (low base +
  formalisation of the economy + margin expansion). That normalised down
  60→40→30→20→~7% (large caps, last two years). **The 2024 mistake was
  assuming 20% was the permanent trend and paying for it.** When you judge
  whether India is "expensive," you're really judging **forward EPS growth —
  nothing else.**

### Lens 4 — Money supply, inflation & assets

- **Inflation is, at root, money supply** *(Friedman)*. Under a paper/digital
  currency with no metal standard, money can be created at will, so it is.
- **Quantity theory, in mangoes:** 100 mangoes and ₹100 → ₹1/mango. Print money
  to ₹120 with the same 100 mangoes → ₹1.20/mango. Across the world, **money
  supply grows faster than GDP — including in India** (India's faster partly
  because digitisation keeps money in banks, multiplying it).
- **Production efficiency (better tech, better ICOR) partly absorbs the
  printing** — that's why consumer inflation rises *less* than money supply
  does.
- **The surplus money flows into assets → "asset inflation."** This is why gold
  rises even though it produces nothing: *dollar supply ballooned, so
  dollar-denominated assets repriced up.* **When currency supply expands, asset
  prices rise because the currency weakens.**
- **Actionable:** to defend against a weakening rupee, **own land, equity and
  gold.** When debt/money-printing is rising globally, **don't fear falls — buy
  them**, because asset prices follow the money.
- **Currency-linked nuance:** you don't want the *debtor's* currency assets
  (e.g. US bonds as the dollar weakens), but you *do* want assets *denominated*
  in that currency that benefit from the weakness (e.g. gold). Rising gold *is
  itself the signal* that the dollar is weakening. Hold assets backed across
  **different currencies** where supply is expanding.

---

## Part 3 — The strategy: what to actually do

> **The headline rule, from the research:** ~**92% of your success comes from
> getting asset allocation right** — not from which stock or sector you pick,
> or when you time it.

### Rule 0 — Write it down before you invest

On paper, commit to two facts and keep buying regardless:
1. *"The market goes up and down."* (Yes/No → Yes.)
2. *"The market can fall at any time."* (Yes/No → Yes.)

The disease is **over-confidence** — behaving, on the day you buy, as if you
*know* the market only goes up from here. You don't. Hold both truths and your
buying never stops at the wrong time.

### Rule 1 — Allocate across assets, then rebalance against the trend

- Don't rely on a single asset. Spread across **equity (stocks, mutual funds,
  ETFs), gold, and — as you near your goal — bonds.**
- **Rebalance counter-trend at the *asset* level:** **sell the asset class that
  has run up, add to the one that has fallen.** This is averaging at the
  portfolio level and is where the ~92% lives.

### Rule 2 — Stocks and funds behave *oppositely*. Treat them oppositely.

| | **Individual stocks** | **Mutual funds / index / ETFs (the "asset")** |
|---|---|---|
| On the way **up** | **Pyramid** — keep buying the winner (if the business is good and price isn't stretched) | — |
| On the way **down** | Be careful — a broken small-cap may **never** come back | **Average down** — keep buying the falls |
| Nature | The **body** — a single stock can die permanently | The **soul** — a fund doesn't die; it sheds weak holdings and moves on |
| Example | A small-cap *stock* that crashes may not recover | A small-cap *index* that crashes **will** recover |

- **Let profits run; cut losers.** *(You fire the lazy employee, not the good
  one. Buffett sold ~80% of his stocks within 6 months and never sold a few
  others.)*
- **Profits are unlimited; losses are limited** — you always know your maximum
  loss in advance. **"Losses are the entry ticket to profits."** No wealthy
  investor never lost money; no one who refused to ever lose got rich.
- **Pyramiding still obeys price.** Buy the rising stock **only while price
  stays sensibly below intrinsic value.** Trim a stock only when price runs
  *far* above value — and with the intention to **buy it back** if the business
  is still good.

### Rule 3 — Nobody knows which one will win, so behave like it

- Buffett reportedly made his fortune in **~12 stocks out of ~560 investments.**
  Even he didn't know in advance which 12. **You can't know either.** So the
  edge isn't selection — it's **behaviour**: let the winners compound, cut the
  rest.
- **The single best stock/fund will almost never be in your portfolio** — you
  sold it early or never found it *(bounded rationality: like picking a Paris
  restaurant with limited time, info and competence — the best one has no
  track record for you to have chosen it)*. **Don't grieve it. Follow the
  process.**
- **Don't compare with others' returns.** *(In a cab home you don't track every
  other car's speed — you care about reaching *your* destination.)* Watch your
  **goals**, not the leaderboard.

### Rule 4 — Gold is insurance, sized deliberately

- **Why hold it:** central banks (the world's biggest investors) are buying
  gold; the dollar is structurally weakening; geopolitical friction is rising.
  **Gold is insurance against global shocks, not a wealth-creation machine.**
- **How much:**
  - **Aggressive (equity-tilted): ~10%.**
  - **Conservative: ~15–20%** *(stated as "up to ~20%", "not beyond 20%")*,
    because **over the long run Indian equity will out-compound gold.**
- **Buy-fresh caveat (India):** physical gold can carry ~15% making charges,
  and if the rupee has already fallen ~10% you may be buying ~25% above
  international price — so fresh physical buying is often a poor entry. If you
  already hold gold, **don't sell it.**
- **Homework:** pull 30 years of returns — in the years equity did *badly*,
  check what gold did. That's when the insurance earns its keep. In India, gold
  has often matched equity *because* of rupee depreciation **plus** the gold
  move.

### Rule 5 — Glide down as you approach the goal

- **Slow down near the destination.** *(On the road home you cut speed entering
  the city, the colony, the lane, the gate — speed → zero at home.)*
- Even money invested in equity for 20 years should, from roughly **year 15**,
  **shift gradually into bonds.** Equity + bonds combined is where
  **certainty** comes from. *"None of us is stronger than all of us."*

### Rule 6 — Invest to spend, and let desires retire themselves

- **Investing is *planning of spending*, not "creating wealth" for its own
  sake.** Savings = **deferred expenditure**; one person's saving becomes
  another's spending, and one day it becomes *your* spending. Define the goals
  the money is *for.*
- **Marginal utility is real:** *(the child obsesses over a new toy, then
  forgets it in a year.)* A fulfilled desire loses its grip. Money exists to
  **fulfil desires** so you can move on — not to hoard.

---

## Part 4 — Behaviour: caging the monkey

This is the part that decides outcomes.

- **Invest vs earn.** *Trading* is a **zero-sum game** — you win only by
  beating someone else, and it requires a **skill** you must prove you have.
  *Investing* is **not** about beating others; it's about **beating yourself**,
  and inflation takes care of itself. If you've never been demonstrably better
  than everyone else at anything, **don't assume you'll win a zero-sum game.**
- **Ghost vs God (loss aversion).** People fear the ghost (loss) more than they
  trust God (gain) — alone in a dark forest you imagine the ghost, not the god
  who "only comes to give." So when ₹40 becomes ₹80, you rush to sell to avoid
  giving back ₹10 — and you forfeit the path to ₹800. *(Jhunjhunwala kept
  buying Titan at every high and held for life; the person who bought the other
  30 lakh shares and sold early is forgotten.)* **Let the winner run.**
- **Instant gratification.** *(The chocolate test: offered 3 chocolates
  tomorrow vs 2 now, the child — and most adults — take 2 now.)* When the
  choice is *more vs sooner*, humans grab *sooner*. That single bias — wanting
  it **fast** — is where investing discipline collapses (and why Indians
  over-use derivatives: right intent to build wealth, wrong execution chasing
  speed).
- **Bounded rationality.** You decide with limited time, information and
  competence, so you lean on the familiar. Accept it, and **let a written
  process substitute for the judgment you can't perfect in the moment.**
- **Overconfidence** is the single biggest problem in investing — believing you
  know what the market does next. You don't. Build the plan so you don't need
  to.

---

## Part 5 — Mistakes to avoid (the anti-checklist)

- ❌ Keeping long-term money in fixed instruments that lose to inflation.
- ❌ Buying a good asset at any price ("it's a great company" is not a price).
- ❌ Expecting the market to pay you every year.
- ❌ Blaming the market instead of auditing your own behaviour.
- ❌ Chasing returns before assessing risk.
- ❌ Selling a healthy winner just because it doubled (the ghost).
- ❌ Averaging *down* into a single falling stock as if it were an index.
- ❌ Comparing your portfolio to the best stock you didn't own.
- ❌ Timing the market / demanding speed (the gateway to over-trading).
- ❌ Treating trading profits as proof you'll win a zero-sum game long term.
- ❌ Mistaking the current *state* (dasha) for the *direction* (disha).

---

## Part 6 — The one-page cheat sheet

**Before you buy**
- [ ] Assess **risk** before return. Accept the market can fall anytime.
- [ ] Like the **business / asset** first; check **price vs intrinsic value**
      second. Don't overpay.
- [ ] Confirm the **direction** is up (buy the crescent, not the full moon).

**Portfolio (the ~92%)**
- [ ] Set an **asset allocation**: equity (stocks + funds + ETFs), gold
      (~10% aggressive / ~15–20% conservative), bonds (rising as the goal
      nears).
- [ ] **Rebalance counter-trend:** trim what's run up, add to what's fallen.

**Stocks** → **pyramid up, cut losers, let winners run** (price-disciplined).
**Funds/index** → **average down, never stop buying the falls** (they recover).
**Gold** → **insurance, not a wealth engine.** Hold; don't over-buy fresh.
**Glide** → from ~**year 15**, shift equity → bonds for certainty.

**Behaviour (the real edge)**
- [ ] Compete with **yourself**, not the market or other investors.
- [ ] Cage the **monkey** when prices fall — keep the plan, keep buying.
- [ ] Don't fear the **ghost** (loss); don't chase **speed**.
- [ ] When in doubt, **follow the written process**, not the feeling.

**The mantra**
> *Returns are destiny. Risk, price, allocation and behaviour are yours. Win
> yourself, not the market.*

---

*Educational summary of one investor's philosophy; not a recommendation. Name
of specific stocks/funds mentioned are illustrative of behaviour, not buy
calls. Markets carry risk of loss.*
