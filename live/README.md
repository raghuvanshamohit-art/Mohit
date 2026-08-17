# Live NSE Sector Tightness Model

Turns the supply/demand *tightness* concept into a **live, data-driven ranking**
of NSE sectors. `build_live.py` fetches real sector indices and global
commodities, scores each sector 0–100, and regenerates the interactive
dashboard `../sector-tightness-live.html`.

> Research tool, **not** investment advice. Momentum is backward-looking and
> quotes are delayed — backtest before you act on any of it.

---

## Run it

```bash
python3 build_live.py
```

- **No dependencies** — Python 3.8+ standard library only.
- On your own machine it reaches Yahoo Finance directly. Behind a proxy it
  honours `HTTPS_PROXY` / `SSL_CERT_FILE` from the environment automatically.

**Outputs**
| File | What it is |
|------|------------|
| `../sector-tightness-live.html` | Self-contained interactive dashboard (open in any browser) |
| `sector_data.json` | The computed snapshot — inputs + raw signals, for reproducibility/backtesting |

The console also prints the ranked table.

---

## How each input is made "live"

Every number is derived from price history pulled at build time — nothing is
hand-set.

| Model input | Live computation | Strength |
|-------------|------------------|----------|
| **flow** | Sector index relative strength vs Nifty 50, blended `0.6·(3M) + 0.4·(6M)` excess return | real, all sectors |
| **product** | 3-month momentum of the sector's key commodity (rising = scarce); producer/consumer **sign flip** applied at scoring | real / proxy |
| **margin** | 1-month commodity acceleration (sign-baked), or 1-month relative strength for non-commodity sectors | real |
| **valuation** | Stretch of price above/below its 200-day moving average | proxy (technical, not P/E) |

**Score** (identical to the concept model):

```
raw   = wP·(sign·product) + wM·margin + wF·flow − wV·valuation
score = clamp( (raw / (Σw·100) + 1) / 2 · 100 , 0, 100 )
```

Default weights: product 35 / margin 20 / flow 30 / valuation 15.
Verdict: **≥65 overweight · 45–65 neutral · <45 underweight**.

### Sector → data map

| Sector | Index | Commodity / driver | Type (sign) |
|--------|-------|--------------------|-------------|
| Metal | `^CNXMETAL` | Copper `HG=F` (metals proxy) | producer (+) |
| Oil & Gas | `^CNXENERGY` | WTI crude `CL=F` | producer (+) |
| Auto | `^CNXAUTO` | Crude + copper (inputs) | consumer (−) |
| IT | `^CNXIT` | USD/INR `INR=X` (weak ₹ = tailwind) | flow/FX (+) |
| Bank | `^NSEBANK` | — (flow-led) | flow (+) |
| FMCG | `^CNXFMCG` | Sugar `SB=F` + crude (input proxy) | consumer (−) |
| Pharma | `^CNXPHARMA` | — (flow-led, defensive) | flow (+) |
| Realty | `^CNXREALTY` | — (rate-sensitive) | flow (+) |
| Infra | `^CNXINFRA` | Copper (construction-metal proxy) | consumer (−) |
| PSU Bank | `^CNXPSUBANK` | — (flow-led, value) | flow (+) |

---

## Honest limitations (read before trusting it)

- **Proxies, not exact inputs.** Copper stands in for the metals complex,
  sugar+crude for FMCG inputs, USD/INR for IT — Yahoo has no liquid Indian
  steel or palm-oil price. Directionally right, not precise.
- **Flow-led sectors have no commodity driver.** Bank, PSU Bank, Pharma and
  Realty score on relative strength alone (`product = 0`). A credit-growth or
  rates feed would sharpen them.
- **Valuation is a technical stretch proxy**, not a real P/E. Wiring NSE's
  published per-index P/E would upgrade it to a true mean-reversion guardrail.
- **Delayed, backward-looking data.** Markets often price scarcity before it
  shows up in momentum.

### Natural upgrades
1. NSE per-index **P/E / PB** → real valuation guardrail.
2. **Breadth** (% of a sector's constituents above their 200-DMA) → a second
   flow signal.
3. **FII/DII sector flows** and **commodity inventories** (crude stocks, metal
   warehouse levels) → hardens Lens A.
4. A **backtest harness** over `sector_data.json` history to validate that
   top-ranked sectors actually outperform after costs.

---

## Keep it refreshed

**cron** — rebuild every weekday at 6pm IST (12:30 UTC):

```cron
30 12 * * 1-5  cd /path/to/repo/live && /usr/bin/python3 build_live.py >> build.log 2>&1
```

**GitHub Actions** — `.github/workflows/refresh.yml`:

```yaml
name: refresh-sector-tightness
on:
  schedule: [{ cron: "30 12 * * 1-5" }]   # 18:00 IST on weekdays
  workflow_dispatch:
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: python3 live/build_live.py
      - run: |
          git config user.name  "sector-bot"
          git config user.email "bot@users.noreply.github.com"
          git add sector-tightness-live.html live/sector_data.json
          git commit -m "chore: refresh live sector tightness" || echo "no changes"
          git push
```
