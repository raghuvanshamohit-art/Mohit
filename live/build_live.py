#!/usr/bin/env python3
"""
build_live.py — Live NSE Sector Tightness Model.

Fetches real market data (NSE sector indices + global commodities) from
Yahoo Finance, computes a supply/demand "tightness" score for each sector,
and regenerates a self-contained interactive dashboard: sector-tightness-live.html

Run:
    python3 build_live.py

No third-party packages required (standard library only). On the user's own
machine it reaches Yahoo directly; inside a proxied container it automatically
honours HTTPS_PROXY and SSL_CERT_FILE from the environment.

The four model inputs, and exactly how each is made "live":

  flow       Capital rotation = sector index relative strength vs Nifty 50,
             blended 0.6*(3M) + 0.4*(6M) excess return.           [real, all sectors]
  product    Real-economy supply/demand of the sector's key commodity =
             3M commodity price momentum, UNSIGNED (rising = scarce).
             The producer/consumer sign flip is applied at scoring time.  [real / proxy]
  margin     Near-term pricing power = 1M commodity acceleration (sign-baked),
             or, for non-commodity sectors, 1M relative strength.         [real]
  valuation  Technical stretch vs the 200-day moving average (NOT a P/E).  [proxy]

Honest limitations are documented in live/README.md and surfaced in the
dashboard's provenance panel. This is a research tool, not investment advice.
"""

import os
import sys
import json
import ssl
import time
import datetime
import urllib.request
import urllib.parse

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

RANGE = "1y"
INTERVAL = "1d"

# trading-day windows
N1, N3, N6, MA = 21, 63, 126, 200

# scaling divisors (percentage-point move that maps to a full +/-100)
SC_FLOW = 15.0     # 15pp relative outperformance (blend) -> +/-100
SC_PROD = 20.0     # 20% commodity 3M move -> +/-100
SC_PROD_FX = 8.0   # 8% USD/INR 3M move -> +/-100 (IT)
SC_MARGIN = 12.0   # 12% commodity 1M move -> +/-100
SC_MARGIN_FLOW = 8.0
SC_VAL = 15.0      # 15% above/below 200-DMA -> +/-100

WEIGHTS = {"product": 35, "margin": 20, "flow": 30, "valuation": 15}

NIFTY = "^NSEI"

# Sector definitions. type/sign follow the model: producer +1, consumer -1, flow +1.
# commodity: list of (ticker, weight) blended into the input; None => no commodity driver.
SECTORS = [
    dict(id="metal",  name="Metal",      ticker="^CNXMETAL",   type="producer",
         sign=1,  commodity=[("HG=F", 1.0)], comm_label="Copper (global metals proxy)",
         driver="Steel / aluminium / copper", note="Copper stands in for the metals complex — Yahoo has no liquid Indian steel price."),
    dict(id="energy", name="Oil & Gas",  ticker="^CNXENERGY",  type="producer",
         sign=1,  commodity=[("CL=F", 1.0)], comm_label="WTI crude",
         driver="Crude & natural gas", note="Upstream sells crude; refiners buy it — treated producer-led."),
    dict(id="auto",   name="Auto",       ticker="^CNXAUTO",    type="consumer",
         sign=-1, commodity=[("CL=F", 0.5), ("HG=F", 0.5)], comm_label="Crude + copper (input cost)",
         driver="Steel/rubber input costs", note="Consumer of metals & fuel — rising inputs squeeze margins."),
    dict(id="it",     name="IT",         ticker="^CNXIT",      type="flow",
         sign=1,  commodity=[("INR=X", 1.0)], comm_label="USD/INR (weak rupee ↑ = tailwind)", fx=True,
         driver="Global tech spend · USD/INR", note="Not commodity-driven — a weaker rupee lifts reported margins."),
    dict(id="bank",   name="Bank",       ticker="^NSEBANK",    type="flow",
         sign=1,  commodity=None, comm_label="—",
         driver="Credit demand · NIMs · rates", note="Flow-led: no daily commodity driver. Score leans on relative strength."),
    dict(id="fmcg",   name="FMCG",       ticker="^CNXFMCG",    type="consumer",
         sign=-1, commodity=[("SB=F", 0.5), ("CL=F", 0.5)], comm_label="Sugar + crude (input proxy)",
         driver="Agri & packaging input costs", note="Soft-commodity proxy — real FMCG inputs (palm oil, grains) aren't on Yahoo."),
    dict(id="pharma", name="Pharma",     ticker="^CNXPHARMA",  type="flow",
         sign=1,  commodity=None, comm_label="—",
         driver="US generics pricing · defensive", note="Flow-led defensive: driven by US price cycles, not a tradable commodity."),
    dict(id="realty", name="Realty",     ticker="^CNXREALTY",  type="flow",
         sign=1,  commodity=None, comm_label="—",
         driver="Housing demand · rates", note="Flow-led: rate-sensitive. A live rate feed would sharpen this."),
    dict(id="infra",  name="Infra",      ticker="^CNXINFRA",   type="consumer",
         sign=-1, commodity=[("HG=F", 1.0)], comm_label="Copper (construction-metal proxy)",
         driver="Capex cycle · steel/cement costs", note="Consumer of construction metals — copper as a rough input proxy."),
    dict(id="psu",    name="PSU Bank",   ticker="^CNXPSUBANK", type="flow",
         sign=1,  commodity=None, comm_label="—",
         driver="Credit · rates · value", note="Flow-led: rate- and value-sensitive, distinct from private banks."),
]

# --------------------------------------------------------------------------
# Fetch
# --------------------------------------------------------------------------

def _ssl_context():
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    ctx = ssl.create_default_context()
    if ca and os.path.exists(ca):
        try:
            ctx.load_verify_locations(ca)
        except Exception:
            pass
    return ctx

_CTX = _ssl_context()
_CACHE = {}

def fetch_closes(symbol, retries=3):
    """Return a list of daily close prices (oldest -> newest), Nones dropped."""
    if symbol in _CACHE:
        return _CACHE[symbol]
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=%s"
           % (urllib.parse.quote(symbol), RANGE, INTERVAL))
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30, context=_CTX) as r:
                d = json.load(r)
            res = d.get("chart", {}).get("result")
            if not res:
                raise ValueError("no result payload")
            quote = res[0]["indicators"]["quote"][0]
            closes = [c for c in quote.get("close", []) if c is not None]
            if len(closes) < N3 + 2:
                raise ValueError("history too short (%d pts)" % len(closes))
            _CACHE[symbol] = closes
            return closes
        except Exception as e:  # noqa
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("fetch failed for %s: %s" % (symbol, last_err))

# --------------------------------------------------------------------------
# Signal maths
# --------------------------------------------------------------------------

def ret(closes, n):
    if len(closes) <= n:
        return 0.0
    a, b = closes[-1], closes[-1 - n]
    if not b:
        return 0.0
    return (a / b - 1.0) * 100.0

def clip(x, lo=-100, hi=100):
    return max(lo, min(hi, x))

def sma(closes, n):
    if len(closes) < n:
        n = len(closes)
    return sum(closes[-n:]) / n

def blend_ret(commodity, n):
    total = 0.0
    for tk, w in commodity:
        total += ret(fetch_closes(tk), n) * w
    return total

# --------------------------------------------------------------------------
# Compute
# --------------------------------------------------------------------------

def compute():
    nifty = fetch_closes(NIFTY)
    nifty1, nifty3, nifty6 = ret(nifty, N1), ret(nifty, N3), ret(nifty, N6)

    out = []
    for s in SECTORS:
        closes = fetch_closes(s["ticker"])
        price = closes[-1]

        # --- flow: relative strength vs Nifty (3M/6M blend) ---
        rel3 = ret(closes, N3) - nifty3
        rel6 = ret(closes, N6) - nifty6
        rel1 = ret(closes, N1) - nifty1
        blend = 0.6 * rel3 + 0.4 * rel6
        flow = round(clip(blend / SC_FLOW * 100))

        # --- product: commodity 3M momentum (unsigned); sign flip applied at scoring ---
        comm3 = comm1 = None
        if s["commodity"]:
            comm3 = blend_ret(s["commodity"], N3)
            comm1 = blend_ret(s["commodity"], N1)
            div = SC_PROD_FX if s.get("fx") else SC_PROD
            product = round(clip(comm3 / div * 100))
        else:
            product = 0

        # --- margin: near-term pricing power (sign baked) or 1M relative strength ---
        if s["commodity"] and not s.get("fx"):
            margin = round(clip(comm1 / SC_MARGIN * 100) * s["sign"])
        elif s.get("fx"):
            margin = round(clip(comm1 / SC_PROD_FX * 100))  # FX 1M, no flip (IT sign +1)
        else:
            margin = round(clip(rel1 / SC_MARGIN_FLOW * 100))

        # --- valuation: stretch vs 200-DMA (technical proxy) ---
        ma200 = sma(closes, MA)
        stretch = (price / ma200 - 1.0) * 100.0 if ma200 else 0.0
        valuation = round(clip(stretch / SC_VAL * 100))

        out.append(dict(
            id=s["id"], name=s["name"], ticker=s["ticker"], type=s["type"], sign=s["sign"],
            driver=s["driver"], note=s["note"], comm_label=s["comm_label"],
            inputs=dict(product=product, margin=margin, flow=flow, valuation=valuation),
            signals=dict(
                rel3=round(rel3, 1), rel6=round(rel6, 1), blend=round(blend, 1),
                comm3=(round(comm3, 1) if comm3 is not None else None),
                comm1=(round(comm1, 1) if comm1 is not None else None),
                stretch=round(stretch, 1), price=round(price, 2),
            ),
        ))
    return out

# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def render(sectors, as_of):
    payload = dict(
        asOf=as_of,
        source="Yahoo Finance (delayed quotes)",
        weights=WEIGHTS,
        sectors=sectors,
    )
    tmpl = HTML_TEMPLATE
    tmpl = tmpl.replace("__LIVE_JSON__", json.dumps(payload))
    tmpl = tmpl.replace("__AS_OF__", as_of)
    return tmpl

# The HTML template lives at the bottom for readability.
from string import Template  # noqa: E402  (only used to keep template literal-safe)

def main():
    print("Fetching NSE sector indices + commodities from Yahoo Finance ...")
    sectors = compute()
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    as_of = now.strftime("%Y-%m-%d %H:%M IST")

    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)

    # data snapshot for reproducibility
    with open(os.path.join(here, "sector_data.json"), "w") as f:
        json.dump(dict(asOf=as_of, source="Yahoo Finance (delayed)",
                       weights=WEIGHTS, sectors=sectors), f, indent=2)

    html = render(sectors, as_of)
    out_path = os.path.join(root, "sector-tightness-live.html")
    with open(out_path, "w") as f:
        f.write(html)

    # console summary
    ranked = sorted(sectors, key=lambda s: score_of(s), reverse=True)
    print("\n  as of %s" % as_of)
    print("  %-10s %6s  %-12s" % ("sector", "score", "verdict"))
    print("  " + "-" * 34)
    for s in ranked:
        sc = score_of(s)
        v = "OVERWEIGHT" if sc >= 65 else ("UNDERWEIGHT" if sc < 45 else "neutral")
        print("  %-10s %5d   %-12s" % (s["name"], sc, v))
    print("\nWrote %s" % out_path)
    print("Wrote %s" % os.path.join(here, "sector_data.json"))

def score_of(s):
    w = WEIGHTS
    i = s["inputs"]
    raw = (w["product"] * s["sign"] * i["product"] + w["margin"] * i["margin"]
           + w["flow"] * i["flow"] - w["valuation"] * i["valuation"])
    den = (w["product"] + w["margin"] + w["flow"] + w["valuation"]) * 100 or 1
    return max(0, min(100, round((raw / den + 1) / 2 * 100)))

# --------------------------------------------------------------------------
# HTML template (self-contained, theme-aware, interactive)
# --------------------------------------------------------------------------
HTML_TEMPLATE = r"""<title>Live Sector Tightness</title>
<style>
  :root{
    --bg:#EDEFF2;--surface:#FFFFFF;--surface-2:#F4F6F8;--ink:#161C24;--muted:#5A6675;
    --faint:#8A96A3;--line:#DBE0E6;--line-strong:#C6CDD5;--accent:#0B6B72;--accent-soft:#0b6b7218;
    --heat-loose:#2E7CB0;--heat-mid:#8E8C86;--heat-tight:#C0472E;
    --tag-prod-bg:#f4e3d5;--tag-prod-fg:#9a4a20;--tag-cons-bg:#dceaf2;--tag-cons-fg:#215a78;
    --tag-flow-bg:#d7ecec;--tag-flow-fg:#0b6b72;--live:#1f9d55;
    --shadow:0 1px 2px rgba(20,28,38,.06),0 8px 24px -12px rgba(20,28,38,.18);
    --serif:"Hoefler Text","Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --mono:ui-monospace,"SF Mono","Cascadia Code","JetBrains Mono","Roboto Mono",Menlo,Consolas,monospace;
  }
  @media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
    --bg:#0F141A;--surface:#161D25;--surface-2:#1C2530;--ink:#E7ECF1;--muted:#9EABB8;--faint:#6C7A88;
    --line:#28323D;--line-strong:#37434F;--accent:#41A9AE;--accent-soft:#41a9ae22;
    --heat-loose:#4C9AD0;--heat-mid:#9A999285;--heat-tight:#E0674A;
    --tag-prod-bg:#3a2a1e;--tag-prod-fg:#e0a06a;--tag-cons-bg:#1d2f3c;--tag-cons-fg:#8bc2df;
    --tag-flow-bg:#123433;--tag-flow-fg:#5bc9ce;--live:#3fc47a;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px -14px rgba(0,0,0,.7);
  }}
  :root[data-theme="dark"]{
    --bg:#0F141A;--surface:#161D25;--surface-2:#1C2530;--ink:#E7ECF1;--muted:#9EABB8;--faint:#6C7A88;
    --line:#28323D;--line-strong:#37434F;--accent:#41A9AE;--accent-soft:#41a9ae22;
    --heat-loose:#4C9AD0;--heat-mid:#9A999285;--heat-tight:#E0674A;
    --tag-prod-bg:#3a2a1e;--tag-prod-fg:#e0a06a;--tag-cons-bg:#1d2f3c;--tag-cons-fg:#8bc2df;
    --tag-flow-bg:#123433;--tag-flow-fg:#5bc9ce;--live:#3fc47a;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px -14px rgba(0,0,0,.7);
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.6;font-size:16px;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1160px;margin:0 auto;padding:0 22px}
  .prose{max-width:70ch}
  h1,h2,h3{font-family:var(--serif);font-weight:600;text-wrap:balance;line-height:1.15;letter-spacing:-.01em}
  a{color:var(--accent)}
  .mono{font-family:var(--mono)}
  .tnum{font-variant-numeric:tabular-nums}
  .eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);font-weight:600}

  .topbar{position:sticky;top:0;z-index:40;background:color-mix(in srgb,var(--bg) 86%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
  .topbar .row{display:flex;align-items:center;justify-content:space-between;height:56px;gap:12px}
  .brand{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:.82rem;color:var(--muted)}
  .brand b{color:var(--ink);font-weight:600}
  .livedot{display:inline-flex;align-items:center;gap:6px;font-family:var(--mono);font-size:.72rem;color:var(--live);letter-spacing:.06em}
  .livedot .d{width:8px;height:8px;border-radius:50%;background:var(--live);box-shadow:0 0 0 0 var(--live);animation:pulse 2.4s infinite}
  @keyframes pulse{0%{box-shadow:0 0 0 0 color-mix(in srgb,var(--live) 60%,transparent)}70%{box-shadow:0 0 0 7px transparent}100%{box-shadow:0 0 0 0 transparent}}
  .toggle{font-family:var(--mono);font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;border:1px solid var(--line-strong);background:var(--surface);color:var(--muted);padding:7px 12px;border-radius:8px;cursor:pointer}
  .toggle:hover{color:var(--ink);border-color:var(--accent)}

  header.hero{padding:54px 0 26px}
  .hero h1{font-size:clamp(2.2rem,5vw,3.4rem);margin:.3em 0 .25em}
  .hero .dek{font-size:1.12rem;color:var(--muted);max-width:52ch}
  .hero .dek b{color:var(--ink)}
  .asof{font-family:var(--mono);font-size:.8rem;color:var(--faint);margin-top:14px}
  .asof b{color:var(--live)}

  section{padding:30px 0}
  .rule{height:1px;background:var(--line);border:0;margin:0}
  h2{font-size:clamp(1.5rem,3vw,2rem);margin:.1em 0 .3em}
  .lead{font-size:1.02rem;color:var(--muted);max-width:70ch}

  .model-shell{background:var(--surface-2);border:1px solid var(--line);border-radius:18px;padding:20px;margin-top:18px}
  .controls{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:16px}
  @media(max-width:820px){.controls{grid-template-columns:1fr}}
  .panel{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:15px 17px}
  .panel .ph{font-family:var(--mono);font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);margin-bottom:12px;display:flex;justify-content:space-between;align-items:center}
  .panel .ph .reset{cursor:pointer;color:var(--accent);border:0;background:none;font-family:var(--mono);font-size:.72rem}
  .presets{display:flex;flex-wrap:wrap;gap:8px}
  .preset{font-family:var(--mono);font-size:.78rem;border:1px solid var(--line-strong);background:var(--surface-2);color:var(--ink);padding:9px 13px;border-radius:9px;cursor:pointer}
  .preset:hover{border-color:var(--accent)}
  .preset.active{background:var(--accent);color:#fff;border-color:var(--accent)}
  .preset.live.active{background:var(--live);border-color:var(--live)}
  .wgrid{display:grid;gap:12px}
  .wrow{display:grid;grid-template-columns:110px 1fr 40px;align-items:center;gap:10px}
  .wrow .wl{font-size:.84rem;color:var(--muted)}
  .wrow .wv{font-family:var(--mono);font-size:.82rem;color:var(--ink);text-align:right}

  .legend{display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-family:var(--mono);font-size:.73rem;color:var(--muted);margin:2px 0 14px}
  .legend .bar{height:8px;width:170px;border-radius:6px;background:linear-gradient(90deg,var(--heat-loose),var(--heat-mid),var(--heat-tight))}

  .board{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:15px}
  .scard{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--heat-mid);border-radius:12px;padding:15px 15px 16px;box-shadow:var(--shadow);will-change:transform}
  .scard .top{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
  .scard .rank{font-family:var(--mono);font-size:.72rem;color:var(--faint)}
  .scard .name{font-family:var(--serif);font-size:1.2rem;font-weight:600;line-height:1.1}
  .scard .driver{font-size:.8rem;color:var(--muted);margin-top:2px}
  .type-tag{font-family:var(--mono);font-size:.62rem;letter-spacing:.08em;text-transform:uppercase;padding:3px 7px;border-radius:6px;font-weight:600;white-space:nowrap}
  .type-tag.producer{background:var(--tag-prod-bg);color:var(--tag-prod-fg)}
  .type-tag.consumer{background:var(--tag-cons-bg);color:var(--tag-cons-fg)}
  .type-tag.flow{background:var(--tag-flow-bg);color:var(--tag-flow-fg)}
  .scoreline{display:flex;align-items:center;gap:11px;margin:11px 0 4px}
  .score{font-family:var(--mono);font-size:2rem;font-weight:600;line-height:1;font-variant-numeric:tabular-nums;min-width:2.4ch}
  .meter{flex:1;height:9px;border-radius:6px;background:var(--surface-2);overflow:hidden;border:1px solid var(--line)}
  .meter i{display:block;height:100%;border-radius:6px;transition:width .3s,background .3s}
  .verdict{font-family:var(--mono);font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;font-weight:700;padding:4px 8px;border-radius:6px;white-space:nowrap}
  .chips{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 2px}
  .chip{font-family:var(--mono);font-size:.68rem;color:var(--muted);background:var(--surface-2);border:1px solid var(--line);border-radius:6px;padding:3px 7px}
  .chip b{color:var(--ink);font-weight:600}
  .chip .pos{color:var(--heat-tight)}.chip .neg{color:var(--heat-loose)}
  .sliders{margin-top:12px;display:grid;gap:10px;border-top:1px solid var(--line);padding-top:12px}
  .srow label{display:flex;justify-content:space-between;align-items:baseline;font-size:.76rem;color:var(--muted);margin-bottom:4px}
  .srow label .sv{font-family:var(--mono);color:var(--ink);font-size:.76rem}
  input[type=range]{-webkit-appearance:none;appearance:none;width:100%;height:5px;border-radius:6px;background:var(--line-strong);outline:none;cursor:pointer;margin:0}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;border-radius:50%;background:var(--accent);border:2px solid var(--surface);box-shadow:0 1px 4px rgba(0,0,0,.25)}
  input[type=range]::-moz-range-thumb{width:15px;height:15px;border-radius:50%;background:var(--accent);border:2px solid var(--surface)}
  input[type=range]:focus-visible{box-shadow:0 0 0 3px var(--accent-soft)}
  .note-line{font-size:.75rem;color:var(--faint);margin-top:9px;font-style:italic;font-family:var(--serif)}

  .prov{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:22px 24px;box-shadow:var(--shadow);margin-top:16px}
  .prov h3{font-size:1.15rem;margin:0 0 6px}
  .prov table{width:100%;border-collapse:collapse;font-size:.85rem;margin-top:10px}
  .prov th,.prov td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
  .prov th{font-family:var(--mono);font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);font-weight:600}
  .prov td.k{font-family:var(--mono);color:var(--ink);white-space:nowrap}
  .prov .flags{margin-top:16px;display:grid;gap:10px}
  .prov .flags li{display:grid;grid-template-columns:auto 1fr;gap:12px;list-style:none;font-size:.9rem;color:var(--muted)}
  .prov .flags{padding:0}
  .prov .flags b{color:var(--ink)}
  .prov .flags .k2{font-family:var(--mono);font-size:.68rem;color:var(--accent);letter-spacing:.06em;padding-top:2px}
  .tblwrap{overflow-x:auto}
  footer{padding:34px 0 64px;color:var(--faint);font-size:.82rem;font-family:var(--mono)}
  footer .disclaim{color:var(--muted);font-family:var(--sans);font-size:.9rem;max-width:64ch;margin-bottom:14px;line-height:1.5}
  @media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>

<div class="topbar"><div class="wrap row">
  <div class="brand"><span class="livedot"><span class="d"></span>LIVE</span> NSE · <b>Sector Tightness</b></div>
  <button class="toggle" id="themeBtn">Theme</button>
</div></div>

<header class="hero"><div class="wrap prose">
  <div class="eyebrow">Supply · Demand · NSE sector rotation</div>
  <h1>Which sectors are tight right now?</h1>
  <p class="dek">Real NSE sector indices and global commodities, scored on the supply/demand tightness model and <b>ranked live</b>. Drag any slider to what-if from today's actual readings.</p>
  <div class="asof">Data: <span id="src"></span> · as of <b>__AS_OF__</b></div>
</div></header>

<hr class="rule">

<section><div class="wrap">
  <div class="prose">
    <div class="eyebrow">The board</div>
    <h2>Live sector tightness.</h2>
    <p class="lead">Score 0–100. Tight/scarce sectors run hot (overweight); loose/abundant run cool (underweight). Chips under each show the <em>real</em> signals feeding the score. The <b>● Live</b> preset restores today's data; drag to explore, or hit Reset for neutral.</p>
  </div>

  <div class="model-shell">
    <div class="controls">
      <div class="panel">
        <div class="ph"><span>State</span></div>
        <div class="presets" id="presets"></div>
        <div class="note-line">Live values are computed from delayed market data — a research signal, not a trade instruction.</div>
      </div>
      <div class="panel">
        <div class="ph"><span>Model weights</span><button class="reset" id="wReset">reset</button></div>
        <div class="wgrid" id="weights"></div>
      </div>
    </div>
    <div class="legend"><span>Loose / abundant</span><span class="bar"></span><span>Scarce / tight</span>
      <span style="margin-left:auto">≥65 overweight · 45–65 neutral · &lt;45 underweight</span></div>
    <div class="board" id="board"></div>
  </div>
</div></section>

<hr class="rule">

<section><div class="wrap">
  <div class="prose">
    <div class="eyebrow">Under the hood</div>
    <h2>How each number is made live.</h2>
    <p class="lead">Nothing here is hand-set. Every input is derived from price history pulled at build time. Strong price-based signals and flagged proxies are labelled honestly below.</p>
  </div>
  <div class="prov">
    <h3>Signal → data mapping</h3>
    <div class="tblwrap"><table>
      <thead><tr><th>Model input</th><th>Live computation</th><th>Strength</th></tr></thead>
      <tbody>
        <tr><td class="k">flow</td><td>Sector index relative strength vs Nifty 50, blended 0.6·(3M) + 0.4·(6M) excess return</td><td>real · all sectors</td></tr>
        <tr><td class="k">product</td><td>3-month momentum of the sector's key commodity (rising = scarce); producer/consumer sign applied at scoring</td><td>real / proxy</td></tr>
        <tr><td class="k">margin</td><td>1-month commodity acceleration (sign-baked), or 1-month relative strength for non-commodity sectors</td><td>real</td></tr>
        <tr><td class="k">valuation</td><td>Stretch of price above/below its 200-day moving average</td><td>proxy (technical, not P/E)</td></tr>
      </tbody>
    </table></div>
    <ul class="flags">
      <li><span class="k2">PROXY</span><span><b>Copper</b> stands in for the metals complex, <b>sugar+crude</b> for FMCG inputs, <b>USD/INR</b> for IT — Yahoo has no liquid Indian steel/palm-oil price. Directionally right, not exact.</span></li>
      <li><span class="k2">FLOW</span><span><b>Bank, PSU Bank, Pharma, Realty</b> have no daily commodity driver, so their <em>product</em> input is neutral and the score leans on relative strength. A credit-growth or rates feed would sharpen these.</span></li>
      <li><span class="k2">VAL</span><span><b>Valuation is a 200-DMA stretch proxy</b>, not a real P/E. Wiring NSE's published index P/E would upgrade it to a true mean-reversion guardrail.</span></li>
      <li><span class="k2">LAG</span><span>Quotes are <b>delayed</b> and momentum is backward-looking — markets often price scarcity before it shows. Re-run the pipeline to refresh; backtest before sizing anything.</span></li>
    </ul>
  </div>
</div></section>

<hr class="rule">

<footer><div class="wrap">
  <p class="disclaim">Generated by <span class="mono">live/build_live.py</span> from delayed Yahoo Finance data. A research framework for your own thinking — not investment advice, not a recommendation, no guarantee of returns. Re-run the script any time to refresh; see <span class="mono">live/README.md</span> to schedule it.</p>
  <div>SECTOR TIGHTNESS · LIVE · built __AS_OF__</div>
</div></footer>

<script>
(function(){
  "use strict";
  var LIVE = __LIVE_JSON__;
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var root=document.documentElement;
  document.getElementById("src").textContent=LIVE.source;

  document.getElementById("themeBtn").addEventListener("click",function(){
    var cur=root.getAttribute("data-theme");
    var isDark=cur?cur==="dark":matchMedia("(prefers-color-scheme: dark)").matches;
    root.setAttribute("data-theme",isDark?"light":"dark");
  });

  function css(v){return getComputedStyle(root).getPropertyValue(v).trim();}
  function hx(h){h=(h||"").replace('#','').slice(0,6);if(h.length===3)h=h.split('').map(function(c){return c+c;}).join('');
    return [parseInt(h.substr(0,2),16),parseInt(h.substr(2,2),16),parseInt(h.substr(4,2),16)];}
  function mix(a,b,t){return a.map(function(x,i){return Math.round(x+(b[i]-x)*t);});}
  function heat(sc){var lo=hx(css('--heat-loose')||'#2E7CB0'),mid=hx(css('--heat-mid')||'#8E8C86'),hi=hx(css('--heat-tight')||'#C0472E');
    var t=Math.max(0,Math.min(1,sc/100)),r=t<.5?mix(lo,mid,t/.5):mix(mid,hi,(t-.5)/.5);return 'rgb('+r[0]+','+r[1]+','+r[2]+')';}

  var WEIGHTS=[{key:'product',label:'Product supply',val:LIVE.weights.product},
    {key:'margin',label:'Margin trend',val:LIVE.weights.margin},
    {key:'flow',label:'Capital flow',val:LIVE.weights.flow},
    {key:'valuation',label:'Valuation',val:LIVE.weights.valuation}];
  var WDEF=WEIGHTS.map(function(w){return w.val;});
  var INPUT_LABEL={product:function(s){return s.type==='producer'?'Product scarcity (sells)':s.type==='consumer'?'Input-cost scarcity (buys)':(s.comm_label.charAt(0)==='—'?'End-demand (no commodity)':'FX / end-demand tailwind');},
    margin:function(){return 'Margin / pricing momentum';},flow:function(){return 'Capital flow — rel. strength vs Nifty';},valuation:function(){return 'Valuation — stretch vs 200-DMA';}};

  var state={};
  LIVE.sectors.forEach(function(s){state[s.id]={product:s.inputs.product,margin:s.inputs.margin,flow:s.inputs.flow,valuation:s.inputs.valuation};});

  // weights
  var wWrap=document.getElementById('weights');
  function totalW(){return WEIGHTS.reduce(function(a,w){return a+w.val;},0)||1;}
  function pct(k){var w=WEIGHTS.filter(function(x){return x.key===k;})[0];return Math.round(w.val/totalW()*100)+'%';}
  WEIGHTS.forEach(function(w){var r=document.createElement('div');r.className='wrow';
    r.innerHTML='<span class="wl">'+w.label+'</span><input type="range" min="0" max="60" value="'+w.val+'" data-w="'+w.key+'"><span class="wv tnum" id="wv-'+w.key+'">'+pct(w.key)+'</span>';
    wWrap.appendChild(r);});
  wWrap.addEventListener('input',function(e){var k=e.target.getAttribute('data-w');if(!k)return;
    WEIGHTS.filter(function(x){return x.key===k;})[0].val=+e.target.value;
    WEIGHTS.forEach(function(w){document.getElementById('wv-'+w.key).textContent=pct(w.key);});recompute();});
  document.getElementById('wReset').addEventListener('click',function(){
    WEIGHTS.forEach(function(w,i){w.val=WDEF[i];});
    wWrap.querySelectorAll('input').forEach(function(inp){inp.value=WEIGHTS.filter(function(x){return x.key===inp.getAttribute('data-w');})[0].val;});
    WEIGHTS.forEach(function(w){document.getElementById('wv-'+w.key).textContent=pct(w.key);});recompute();reorder();});

  // presets
  var pWrap=document.getElementById('presets');
  [['live','● Live'],['reset','Reset']].forEach(function(p,i){var b=document.createElement('button');
    b.className='preset'+(p[0]==='live'?' live':'')+(i===0?' active':'');b.type='button';b.textContent=p[1];
    b.addEventListener('click',function(){applyPreset(p[0]);});pWrap.appendChild(b);});
  function applyPreset(kind){
    LIVE.sectors.forEach(function(s){
      if(kind==='reset')state[s.id]={product:0,margin:0,flow:0,valuation:0};
      else state[s.id]={product:s.inputs.product,margin:s.inputs.margin,flow:s.inputs.flow,valuation:s.inputs.valuation};});
    pWrap.querySelectorAll('.preset').forEach(function(el,idx){el.classList.toggle('active',(kind==='live')===(idx===0));});
    syncSliders();recompute();reorder();
  }

  // board
  var board=document.getElementById('board');
  var INPUTS=['product','margin','flow','valuation'];
  LIVE.sectors.forEach(function(s){
    var card=document.createElement('div');card.className='scard';card.setAttribute('data-id',s.id);
    var sliders=INPUTS.map(function(k){return '<div class="srow"><label for="'+s.id+'-'+k+'">'+INPUT_LABEL[k](s)+
      ' <span class="sv tnum" id="sv-'+s.id+'-'+k+'">0</span></label>'+
      '<input type="range" min="-100" max="100" value="0" data-id="'+s.id+'" data-k="'+k+'" id="'+s.id+'-'+k+'"></div>';}).join('');
    var sig=s.signals;
    function chip(lbl,val,suf){if(val===null||val===undefined)return '';var cls=val>0?'pos':(val<0?'neg':'');
      return '<span class="chip">'+lbl+' <b class="'+cls+'">'+(val>0?'+':'')+val+(suf||'')+'</b></span>';}
    var chips='<div class="chips">'+chip('RS 3M',sig.rel3,'%')+chip('RS 6M',sig.rel6,'%')+
      (sig.comm3!==null?chip('Comm 3M',sig.comm3,'%'):'<span class="chip">Comm <b>n/a</b></span>')+
      chip('vs 200DMA',sig.stretch,'%')+'</div>';
    card.innerHTML='<div class="top"><div><span class="rank" id="rank-'+s.id+'">—</span>'+
      '<div class="name">'+s.name+'</div><div class="driver">'+s.driver+'</div></div>'+
      '<span class="type-tag '+s.type+'">'+s.type+'</span></div>'+
      '<div class="scoreline"><span class="score tnum" id="score-'+s.id+'">50</span>'+
      '<span class="meter"><i id="meter-'+s.id+'"></i></span><span class="verdict" id="verdict-'+s.id+'">NEUTRAL</span></div>'+
      chips+'<div class="sliders">'+sliders+'</div>'+
      '<div class="note-line">'+s.note+'</div>';
    board.appendChild(card);
  });
  board.addEventListener('input',function(e){var id=e.target.getAttribute('data-id'),k=e.target.getAttribute('data-k');if(!id||!k)return;
    state[id][k]=+e.target.value;document.getElementById('sv-'+id+'-'+k).textContent=(+e.target.value>0?'+':'')+e.target.value;
    pWrap.querySelectorAll('.preset').forEach(function(el){el.classList.remove('active');});recompute();});
  board.addEventListener('change',function(e){if(e.target.getAttribute('data-id'))reorder();});
  function syncSliders(){LIVE.sectors.forEach(function(s){INPUTS.forEach(function(k){
    var v=state[s.id][k],el=document.getElementById(s.id+'-'+k);if(el)el.value=v;
    var sv=document.getElementById('sv-'+s.id+'-'+k);if(sv)sv.textContent=(v>0?'+':'')+v;});});}

  function scoreOf(s){var st=state[s.id],W=WEIGHTS;
    var raw=W[0].val*s.sign*st.product+W[1].val*st.margin+W[2].val*st.flow-W[3].val*st.valuation;
    var den=(W[0].val+W[1].val+W[2].val+W[3].val)*100||1;return Math.max(0,Math.min(100,Math.round((raw/den+1)/2*100)));}
  function verdict(sc){if(sc>=65)return{t:'Overweight',c:heat(80)};if(sc<45)return{t:'Underweight',c:heat(18)};return{t:'Neutral',c:'var(--muted)'};}
  function recompute(){
    var ranked=LIVE.sectors.map(function(s){return{s:s,sc:scoreOf(s)};}).sort(function(a,b){return b.sc-a.sc;});
    ranked.forEach(function(r,i){document.getElementById('rank-'+r.s.id).textContent='#'+(i+1);});
    LIVE.sectors.forEach(function(s){var sc=scoreOf(s),col=heat(sc),v=verdict(sc);
      var card=board.querySelector('[data-id="'+s.id+'"]');card.style.borderLeftColor=col;card.setAttribute('data-score',sc);
      document.getElementById('score-'+s.id).textContent=sc;document.getElementById('score-'+s.id).style.color=col;
      var m=document.getElementById('meter-'+s.id);m.style.width=sc+'%';m.style.background=col;
      var vd=document.getElementById('verdict-'+s.id);vd.textContent=v.t;vd.style.color=v.c;
      vd.style.background='color-mix(in srgb,'+(v.c.indexOf('var')===0?'var(--muted)':v.c)+' 14%,transparent)';});}
  function reorder(){var cards=[].slice.call(board.children),first={};
    cards.forEach(function(c){first[c.getAttribute('data-id')]=c.getBoundingClientRect();});
    cards.sort(function(a,b){return (+b.getAttribute('data-score'))-(+a.getAttribute('data-score'));});
    cards.forEach(function(c){board.appendChild(c);});
    if(reduce)return;
    cards.forEach(function(c){var id=c.getAttribute('data-id'),last=c.getBoundingClientRect();
      var dx=first[id].left-last.left,dy=first[id].top-last.top;
      if(dx||dy){c.style.transform='translate('+dx+'px,'+dy+'px)';c.style.transition='none';
        requestAnimationFrame(function(){c.style.transition='transform .5s cubic-bezier(.2,.7,.2,1)';c.style.transform='';});}});}

  syncSliders();recompute();reorder();
  matchMedia("(prefers-color-scheme: dark)").addEventListener('change',recompute);
})();
</script>
"""

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)
