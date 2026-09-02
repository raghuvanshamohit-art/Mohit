"""Interactive HTML dashboard generator for dyncorr.

Produces a single self-contained HTML page that embeds the (transformed)
series and computes rolling / EWMA correlations *in the browser*, so the
method, window, and "as-of date" controls are fully interactive with no server
and no network. Use it from the CLI::

    python -m dyncorr dashboard --params us_treasury_10y inflation gold \
        --out dashboard.html

The same renderer backs the hosted/interactive artifact version.
"""

from __future__ import annotations

import json

import pandas as pd

from .data import PanelResult, build_panel

# Short, chart-friendly labels (the preset labels are too long for a legend).
SHORT_LABELS = {
    "us_treasury_2y": "US 2Y",
    "us_treasury_10y": "US 10Y",
    "us_treasury_30y": "US 30Y",
    "inflation": "Inflation",
    "cpi": "CPI",
    "bond_rate": "Baa Bonds",
    "euro_treasury_10y": "Bund 10Y",
    "yen_treasury_10y": "JGB 10Y",
    "gold": "Gold",
    "gold_etf": "Gold ETF",
    "sp500": "S&P 500",
    "dollar_index": "US Dollar",
    "eurusd": "EUR/USD",
    "usdjpy": "USD/JPY",
    "oil": "Crude Oil",
    "vix": "VIX",
}

DEFAULT_PARAMS = [
    "us_treasury_10y", "us_treasury_2y", "inflation", "bond_rate",
    "euro_treasury_10y", "yen_treasury_10y", "gold", "sp500",
]


def _short(key: str) -> str:
    return SHORT_LABELS.get(key, key)


def build_dashboard_data(panel: PanelResult) -> dict:
    """Assemble the JSON payload embedded in the page."""
    df = panel.transformed
    order = list(df.columns)
    return {
        "dates": [d.strftime("%Y-%m-%d") for d in df.index],
        "series": {c: [round(float(v), 6) for v in df[c].to_numpy()] for c in order},
        "order": order,
        "labels": {c: _short(c) for c in order},
        "transforms": panel.transforms,
        "source": panel.source,
        "n": int(len(df)),
    }


def render_dashboard(
    params: list[str] | None = None,
    source: str = "synthetic",
    start: str = "2019-01-01",
    end: str = "2024-12-31",
    transform: str = "auto",
    csv_path: str | None = None,
    date_col: str | None = None,
    seed: int = 7,
    full: bool = True,
) -> str:
    """Render the dashboard HTML.

    ``full=True`` returns a complete standalone document (for saving to disk and
    opening locally). ``full=False`` returns only ``<title>+<style>+body+script``
    for embedding in the hosted artifact skeleton.
    """
    params = params or DEFAULT_PARAMS
    panel = build_panel(
        params=params,
        source="csv" if csv_path else source,
        start=start, end=end, transform=transform,
        csv_path=csv_path, date_col=date_col, seed=seed,
    )
    data = build_dashboard_data(panel)
    head = _HEAD
    body = _BODY.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    if not full:
        return head + "\n" + body
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n"
    )


def write_dashboard(out_path: str, **kwargs) -> str:
    html = render_dashboard(full=True, **kwargs)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out_path


# --------------------------------------------------------------------------- #
# HTML pieces
# --------------------------------------------------------------------------- #

_HEAD = """<title>Cross-Asset Correlation Monitor</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{
  color-scheme: light;
  --page:#eef1f4; --surface:#ffffff; --surface-2:#f5f7fa; --inset:#eef1f5;
  --ink:#10151b; --ink-2:#4a5560; --muted:#8792a0;
  --grid:#e4e9ef; --axis:#c4ccd6; --border:rgba(16,21,27,.10);
  --accent:#0d7490; --accent-ink:#ffffff; --accent-soft:rgba(13,116,144,.10);
  --pos:#2a78d6; --neg:#e34948; --mid:#eef0ee;
  /* categorical series slots (dataviz-validated, light) */
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100;
  --s5:#e87ba4; --s6:#008300; --s7:#4a3aa7; --s8:#e34948;
  --shadow:0 1px 2px rgba(16,21,27,.05), 0 8px 24px rgba(16,21,27,.06);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme: dark;
    --page:#0d1216; --surface:#151b21; --surface-2:#1a2128; --inset:#10161b;
    --ink:#e9eef3; --ink-2:#a7b2bd; --muted:#748090;
    --grid:#232c34; --axis:#38424c; --border:rgba(233,238,243,.10);
    --accent:#2bb6d6; --accent-ink:#04222b; --accent-soft:rgba(43,182,214,.14);
    --pos:#3987e5; --neg:#e66767; --mid:#2a3138;
    --s1:#3987e5; --s2:#f0763f; --s3:#22c48c; --s4:#f0b53a;
    --s5:#ee92b4; --s6:#3aad3a; --s7:#9085e9; --s8:#e66767;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px rgba(0,0,0,.35);
  }
}
:root[data-theme="dark"]{
  color-scheme: dark;
  --page:#0d1216; --surface:#151b21; --surface-2:#1a2128; --inset:#10161b;
  --ink:#e9eef3; --ink-2:#a7b2bd; --muted:#748090;
  --grid:#232c34; --axis:#38424c; --border:rgba(233,238,243,.10);
  --accent:#2bb6d6; --accent-ink:#04222b; --accent-soft:rgba(43,182,214,.14);
  --pos:#3987e5; --neg:#e66767; --mid:#2a3138;
  --s1:#3987e5; --s2:#f0763f; --s3:#22c48c; --s4:#f0b53a;
  --s5:#ee92b4; --s6:#3aad3a; --s7:#9085e9; --s8:#e66767;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px rgba(0,0,0,.35);
}

*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased;}
.mono{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  font-variant-numeric:tabular-nums;}
.wrap{max-width:1220px;margin:0 auto;padding:22px 20px 60px;}

/* Header */
.top{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;
  flex-wrap:wrap;padding-bottom:14px;border-bottom:1px solid var(--border);}
.brand h1{margin:0;font-size:22px;font-weight:700;letter-spacing:-.02em;
  text-wrap:balance;}
.brand p{margin:5px 0 0;color:var(--ink-2);font-size:13px;max-width:60ch;}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--accent);font-weight:600;margin-bottom:6px;}
.top-right{display:flex;align-items:center;gap:10px;}
.chip{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.03em;
  padding:5px 9px;border:1px solid var(--border);border-radius:999px;
  color:var(--ink-2);background:var(--surface-2);white-space:nowrap;}
.chip b{color:var(--ink);font-weight:600;}
.tbtn{appearance:none;border:1px solid var(--border);background:var(--surface-2);
  color:var(--ink-2);border-radius:8px;padding:7px 10px;cursor:pointer;font:inherit;
  font-size:12px;display:inline-flex;align-items:center;gap:6px;}
.tbtn:hover{color:var(--ink);border-color:var(--axis);}

/* KPI strip */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0;}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:12px;
  padding:13px 15px;box-shadow:var(--shadow);min-width:0;}
.kpi .k-label{font-size:11px;letter-spacing:.04em;text-transform:uppercase;
  color:var(--muted);display:flex;align-items:center;gap:6px;}
.kpi .k-val{font-size:22px;font-weight:600;margin-top:7px;letter-spacing:-.01em;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.kpi .k-sub{font-size:12px;color:var(--ink-2);margin-top:2px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.dot{width:9px;height:9px;border-radius:2px;flex:none;display:inline-block;}

/* Controls */
.controls{display:flex;flex-wrap:wrap;gap:16px 22px;align-items:flex-end;
  background:var(--surface);border:1px solid var(--border);border-radius:12px;
  padding:14px 16px;box-shadow:var(--shadow);}
.ctl{display:flex;flex-direction:column;gap:7px;}
.ctl>label{font-size:11px;letter-spacing:.05em;text-transform:uppercase;
  color:var(--muted);}
.seg{display:inline-flex;background:var(--inset);border:1px solid var(--border);
  border-radius:9px;padding:3px;gap:2px;}
.seg button{appearance:none;border:0;background:transparent;color:var(--ink-2);
  padding:6px 13px;border-radius:6px;cursor:pointer;font:inherit;font-size:13px;
  font-weight:500;}
.seg button[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);}
select{appearance:none;font:inherit;font-size:13px;color:var(--ink);
  background:var(--inset);border:1px solid var(--border);border-radius:8px;
  padding:7px 30px 7px 11px;cursor:pointer;
  background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),
    linear-gradient(135deg,var(--muted) 50%,transparent 50%);
  background-position:calc(100% - 15px) 52%,calc(100% - 10px) 52%;
  background-size:5px 5px,5px 5px;background-repeat:no-repeat;}
.slider{display:flex;align-items:center;gap:10px;min-width:190px;}
.slider input[type=range]{flex:1;accent-color:var(--accent);height:4px;cursor:pointer;}
.slider .v{font-family:"IBM Plex Mono",monospace;font-size:13px;color:var(--ink);
  min-width:78px;text-align:right;font-variant-numeric:tabular-nums;}

/* Chart + heatmap grid */
.grid{display:grid;grid-template-columns:1.55fr 1fr;gap:16px;margin-top:16px;}
.panel{background:var(--surface);border:1px solid var(--border);border-radius:12px;
  box-shadow:var(--shadow);padding:15px 16px 12px;min-width:0;}
.panel h2{margin:0;font-size:14px;font-weight:600;letter-spacing:-.01em;}
.panel .sub{color:var(--muted);font-size:12px;margin:3px 0 10px;}
.legend{display:flex;flex-wrap:wrap;gap:6px 12px;margin-top:10px;}
.lg{display:inline-flex;align-items:center;gap:7px;font-size:12px;cursor:pointer;
  color:var(--ink-2);user-select:none;padding:2px 3px;border-radius:5px;}
.lg:hover{color:var(--ink);}
.lg.off{opacity:.38;}
.lg .dot{width:11px;height:3px;border-radius:2px;}
.chartbox{position:relative;width:100%;}
canvas{display:block;width:100%;}
.tip{position:absolute;pointer-events:none;z-index:6;background:var(--surface);
  border:1px solid var(--border);border-radius:9px;padding:9px 11px;
  box-shadow:var(--shadow);font-size:12px;min-width:150px;opacity:0;
  transition:opacity .08s;color:var(--ink);}
.tip .tt-date{font-family:"IBM Plex Mono",monospace;color:var(--muted);
  font-size:11px;margin-bottom:6px;letter-spacing:.02em;}
.tip .tt-row{display:flex;align-items:center;gap:7px;justify-content:space-between;
  margin:2px 0;}
.tip .tt-row span{display:inline-flex;align-items:center;gap:7px;color:var(--ink-2);}
.tip .tt-row b{font-family:"IBM Plex Mono",monospace;font-weight:600;
  font-variant-numeric:tabular-nums;}

/* Table */
.tablepanel{margin-top:16px;background:var(--surface);border:1px solid var(--border);
  border-radius:12px;box-shadow:var(--shadow);padding:15px 16px;}
.tablewrap{overflow-x:auto;}
table{width:100%;border-collapse:collapse;font-size:13px;}
th,td{text-align:right;padding:8px 10px;white-space:nowrap;}
th:first-child,td:first-child{text-align:left;}
thead th{font-size:11px;letter-spacing:.04em;text-transform:uppercase;
  color:var(--muted);font-weight:600;border-bottom:1px solid var(--border);
  cursor:pointer;user-select:none;}
thead th.sorted::after{content:" \\25BC";font-size:9px;color:var(--accent);}
tbody tr{border-bottom:1px solid var(--border);cursor:pointer;}
tbody tr:last-child{border-bottom:0;}
tbody tr:hover{background:var(--surface-2);}
tbody tr.active{background:var(--accent-soft);}
td.num{font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums;}
.pairname{display:inline-flex;align-items:center;gap:8px;}
.pairname .dd{display:inline-flex;gap:3px;}
.bar-cell{min-width:130px;}
.bar{height:7px;border-radius:3px;background:var(--inset);position:relative;
  overflow:hidden;}
.bar>i{position:absolute;top:0;bottom:0;left:0;border-radius:3px;
  background:var(--accent);}
.val-pos{color:var(--pos);} .val-neg{color:var(--neg);}
.foot{color:var(--muted);font-size:12px;margin-top:22px;line-height:1.7;
  border-top:1px solid var(--border);padding-top:14px;}
.foot b{color:var(--ink-2);font-weight:600;}
@media (max-width:900px){
  .grid{grid-template-columns:1fr;}
  .kpis{grid-template-columns:repeat(2,1fr);}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;}}
</style>"""


_BODY = r"""<div class="wrap">
  <header class="top">
    <div class="brand">
      <div class="eyebrow">Dynamic Correlation</div>
      <h1>Cross-Asset Correlation Monitor</h1>
      <p>How the correlations between Treasuries, inflation, bond rates, gold and
      equities <em>move through time</em> — not a single static number. Drag the
      window and date controls to watch relationships form, decay and flip sign.</p>
    </div>
    <div class="top-right">
      <span class="chip" id="src-chip">&nbsp;</span>
      <button class="tbtn" id="theme-btn" type="button" aria-label="Toggle theme">
        <span id="theme-ico">◐</span><span id="theme-txt">Theme</span>
      </button>
    </div>
  </header>

  <section class="kpis" id="kpis" aria-label="Summary"></section>

  <section class="controls" aria-label="Controls">
    <div class="ctl">
      <label>Estimator</label>
      <div class="seg" id="method" role="group" aria-label="Estimator">
        <button data-m="rolling" aria-pressed="true">Rolling</button>
        <button data-m="ewma" aria-pressed="false">EWMA</button>
      </div>
    </div>
    <div class="ctl" id="window-ctl">
      <label id="win-label">Window (obs)</label>
      <div class="slider">
        <input type="range" id="window" min="20" max="252" step="1" value="90">
        <span class="v mono" id="window-v">90</span>
      </div>
    </div>
    <div class="ctl">
      <label>Correlation of&nbsp;— vs all</label>
      <select id="anchor"></select>
    </div>
    <div class="ctl" style="flex:1;min-width:230px;">
      <label>As of date <span id="asof-v" class="mono" style="color:var(--ink);"></span></label>
      <div class="slider">
        <input type="range" id="asof" min="0" max="100" step="1" value="100">
      </div>
    </div>
  </section>

  <section class="grid">
    <div class="panel">
      <h2>Rolling correlation over time</h2>
      <div class="sub" id="chart-sub">&nbsp;</div>
      <div class="chartbox">
        <canvas id="line" height="340"></canvas>
        <div class="tip" id="line-tip"></div>
      </div>
      <div class="legend" id="legend"></div>
    </div>
    <div class="panel">
      <h2>Correlation matrix</h2>
      <div class="sub" id="hm-sub">as of the selected date</div>
      <div class="chartbox">
        <canvas id="heat" height="340"></canvas>
        <div class="tip" id="heat-tip"></div>
      </div>
    </div>
  </section>

  <section class="tablepanel">
    <h2 style="margin:0 0 3px;font-size:14px;">Pair stability — ranked by how far correlation swings</h2>
    <div class="sub" style="color:var(--muted);font-size:12px;margin-bottom:10px;">
      Click any row (or a heatmap cell) to focus that pair in the chart.</div>
    <div class="tablewrap">
      <table id="tbl">
        <thead><tr>
          <th data-c="pair">Pair</th>
          <th data-c="latest">Latest</th>
          <th data-c="mean">Mean</th>
          <th data-c="min">Min</th>
          <th data-c="max">Max</th>
          <th data-c="swing" class="sorted">Swing</th>
          <th class="bar-cell">Range</th>
        </tr></thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
  </section>

  <p class="foot">
    <b>Method.</b> Series are transformed before correlating — yields &amp; rates
    are differenced, prices become log returns — so this measures co-movement of
    <em>changes</em>, not shared trends. <b>Rolling</b> uses a trailing window of
    N observations; <b>EWMA</b> is an exponentially weighted (RiskMetrics)
    correlation with the chosen half-life, weighting recent data more. The matrix
    and the "swing" ranking are computed from the same live estimates.<br>
    <b>Data.</b> <span id="foot-src"></span> Correlations are computed in your
    browser. This is an analysis tool, not investment advice.
  </p>
</div>

<script>
const DATA = __DATA__;
(function(){
"use strict";
const $ = s => document.querySelector(s);
const SCOL = ["--s1","--s2","--s3","--s4","--s5","--s6","--s7","--s8"];
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const order = DATA.order;
const labels = DATA.labels;
const dates = DATA.dates;
const T = dates.length;
const seriesArr = order.map(k => DATA.series[k]);
const colorOf = {}; order.forEach((k,i)=> colorOf[k] = SCOL[i % SCOL.length]);
const idxOf = {}; order.forEach((k,i)=> idxOf[k]=i);

// ---- state ----
const state = {
  method:"rolling", window:90, halflife:30,
  anchor: order.includes("gold") ? "gold" : order[0],
  asof: T-1, off:new Set(), focus:null, sortKey:"swing"
};

// ---- correlation math ----
function pearson(xi, yi, a, b){ // inclusive [a,b]
  let n=0,sx=0,sy=0,sxx=0,syy=0,sxy=0;
  for(let k=a;k<=b;k++){const x=xi[k],y=yi[k];n++;sx+=x;sy+=y;sxx+=x*x;syy+=y*y;sxy+=x*y;}
  if(n<3) return NaN;
  const cov=sxy-sx*sy/n, vx=sxx-sx*sx/n, vy=syy-sy*sy/n;
  const d=vx*vy; return d>0 ? cov/Math.sqrt(d) : NaN;
}
function rollingPair(i, j){
  const xi=seriesArr[i], yi=seriesArr[j], W=state.window, out=new Array(T).fill(NaN);
  for(let t=W-1;t<T;t++) out[t]=pearson(xi,yi,t-W+1,t);
  return out;
}
function ewmaPair(i, j){
  const xi=seriesArr[i], yi=seriesArr[j], out=new Array(T).fill(NaN);
  const decay=Math.pow(0.5, 1/state.halflife), minp=Math.max(5, Math.round(state.halflife/3));
  let Sw=0,Sx=0,Sy=0,Sxx=0,Syy=0,Sxy=0,n=0;
  for(let t=0;t<T;t++){
    const x=xi[t],y=yi[t];
    Sw=decay*Sw+1; Sx=decay*Sx+x; Sy=decay*Sy+y;
    Sxx=decay*Sxx+x*x; Syy=decay*Syy+y*y; Sxy=decay*Sxy+x*y; n++;
    const mx=Sx/Sw,my=Sy/Sw, cov=Sxy/Sw-mx*my, vx=Sxx/Sw-mx*mx, vy=Syy/Sw-my*my;
    out[t] = (n>=minp && vx>0 && vy>0) ? cov/Math.sqrt(vx*vy) : NaN;
  }
  return out;
}
const _cache = {};
function pairKey(a,b){ return a<b ? a+"~"+b : b+"~"+a; }
function pairSeries(ka, kb){
  const key=state.method+":"+(state.method==="rolling"?state.window:state.halflife)+":"+pairKey(ka,kb);
  if(_cache[key]) return _cache[key];
  const i=idxOf[ka], j=idxOf[kb];
  const arr = state.method==="rolling" ? rollingPair(i,j) : ewmaPair(i,j);
  _cache[key]=arr; return arr;
}
function firstValid(){ // earliest index with a defined value for the anchor pairs
  const W=state.method==="rolling"?state.window:Math.max(5,Math.round(state.halflife/3));
  return Math.min(T-1, W-1);
}

// ---- derived: all pairs summary at current settings ----
function allPairs(){
  const res=[];
  for(let i=0;i<order.length;i++)for(let j=i+1;j<order.length;j++){
    const a=order[i], b=order[j], arr=pairSeries(a,b);
    let mn=Infinity,mx=-Infinity,sum=0,c=0,latest=NaN;
    for(let t=0;t<T;t++){const v=arr[t]; if(v===v){if(v<mn)mn=v; if(v>mx)mx=v; sum+=v; c++; latest=v;}}
    if(c===0) continue;
    res.push({a,b,key:pairKey(a,b),arr,latest,mean:sum/c,min:mn,max:mx,swing:mx-mn});
  }
  return res;
}
function fmt(v){ return (v>=0?"+":"")+v.toFixed(2); }

// ================= LINE CHART =================
const lc = $("#line"), lctx = lc.getContext("2d");
let lineGeom=null;
function anchorPairs(){ // {other, arr, color}
  return order.filter(k=>k!==state.anchor).map(k=>({
    other:k, color:colorOf[k], arr:pairSeries(state.anchor,k), off:state.off.has(k)
  }));
}
function drawLine(){
  const dpr=Math.min(2,window.devicePixelRatio||1);
  const W=lc.clientWidth, H=340;
  lc.width=W*dpr; lc.height=H*dpr; lc.style.height=H+"px";
  lctx.setTransform(dpr,0,0,dpr,0,0); lctx.clearRect(0,0,W,H);
  const m={l:38,r:16,t:10,b:26}, pw=W-m.l-m.r, ph=H-m.t-m.b;
  const x0=firstValid();
  const xToPx = t => m.l + (t-x0)/Math.max(1,(T-1-x0))*pw;
  const yToPx = v => m.t + (1-(v+1)/2)*ph;
  lineGeom={m,pw,ph,x0,xToPx,yToPx,W,H};
  // gridlines at correlation levels
  lctx.font='11px "IBM Plex Mono", monospace'; lctx.textBaseline="middle";
  [-1,-0.5,0,0.5,1].forEach(v=>{
    const y=yToPx(v);
    lctx.strokeStyle = v===0 ? css("--axis") : css("--grid");
    lctx.lineWidth=1; lctx.beginPath(); lctx.moveTo(m.l,y); lctx.lineTo(W-m.r,y); lctx.stroke();
    lctx.fillStyle=css("--muted"); lctx.textAlign="right";
    lctx.fillText(fmt(v), m.l-7, y);
  });
  // year ticks
  lctx.textAlign="center"; lctx.textBaseline="top";
  let lastYr=null;
  for(let t=x0;t<T;t++){
    const yr=dates[t].slice(0,4);
    if(yr!==lastYr){ lastYr=yr; const x=xToPx(t);
      lctx.fillStyle=css("--muted"); lctx.fillText(yr, x, H-m.b+7);
      lctx.strokeStyle=css("--grid"); lctx.lineWidth=1;
      lctx.beginPath(); lctx.moveTo(x,m.t); lctx.lineTo(x,m.t+ph); lctx.stroke();
    }
  }
  // as-of marker
  const ax=xToPx(state.asof);
  if(state.asof>=x0){
    lctx.strokeStyle=css("--accent"); lctx.globalAlpha=.55; lctx.lineWidth=1.5;
    lctx.setLineDash([4,4]); lctx.beginPath(); lctx.moveTo(ax,m.t); lctx.lineTo(ax,m.t+ph);
    lctx.stroke(); lctx.setLineDash([]); lctx.globalAlpha=1;
  }
  // lines
  const pairs=anchorPairs();
  pairs.forEach(p=>{
    if(p.off) return;
    const emph = state.focus===p.other;
    const dim = state.focus && !emph;
    lctx.strokeStyle=css(p.color); lctx.lineWidth=emph?2.6:2;
    lctx.globalAlpha=dim?0.22:1; lctx.lineJoin="round";
    lctx.beginPath(); let started=false;
    for(let t=x0;t<T;t++){const v=p.arr[t]; if(v!==v){started=false;continue;}
      const x=xToPx(t),y=yToPx(v); if(!started){lctx.moveTo(x,y);started=true;}else lctx.lineTo(x,y);}
    lctx.stroke(); lctx.globalAlpha=1;
  });
  lctx.textAlign="left";
  $("#chart-sub").textContent = "Correlation of "+labels[state.anchor]+" vs each series · "
    + (state.method==="rolling" ? state.window+"-obs rolling" : "EWMA half-life "+state.halflife);
}

// crosshair tooltip
const ltip=$("#line-tip");
lc.addEventListener("mousemove", e=>{
  if(!lineGeom) return; const r=lc.getBoundingClientRect();
  const px=e.clientX-r.left; const {m,pw,x0,xToPx,yToPx}=lineGeom;
  if(px<m.l||px>m.l+pw){ ltip.style.opacity=0; drawLine(); return; }
  const frac=(px-m.l)/pw; let t=Math.round(x0+frac*(T-1-x0)); t=Math.max(x0,Math.min(T-1,t));
  drawLine();
  const x=xToPx(t);
  lctx.strokeStyle=css("--axis"); lctx.lineWidth=1; lctx.setLineDash([3,3]);
  lctx.beginPath(); lctx.moveTo(x,lineGeom.m.t); lctx.lineTo(x,lineGeom.m.t+lineGeom.ph); lctx.stroke();
  lctx.setLineDash([]);
  let rows="";
  anchorPairs().filter(p=>!p.off).forEach(p=>{
    const v=p.arr[t]; if(v!==v) return;
    const y=yToPx(v); lctx.fillStyle=css(p.color);
    lctx.beginPath(); lctx.arc(x,y,3,0,7); lctx.fill();
    rows+='<div class="tt-row"><span><i class="dot" style="width:9px;height:3px;background:'+css(p.color)+'"></i>'+labels[p.other]+'</span><b>'+fmt(v)+'</b></div>';
  });
  ltip.innerHTML='<div class="tt-date">'+dates[t]+'</div>'+rows;
  ltip.style.opacity=1;
  const tw=ltip.offsetWidth, box=lc.parentElement.clientWidth;
  let lx=x+12; if(lx+tw>box) lx=x-tw-12;
  ltip.style.left=Math.max(0,lx)+"px"; ltip.style.top=(lineGeom.m.t+4)+"px";
});
lc.addEventListener("mouseleave", ()=>{ ltip.style.opacity=0; drawLine(); });

// ================= HEATMAP =================
const hc=$("#heat"), hctx=hc.getContext("2d");
let heatGeom=null;
function heatColor(v){
  if(v!==v) return css("--inset");
  const mid=cssRGB("--mid"), pos=cssRGB("--pos"), neg=cssRGB("--neg");
  const t=Math.max(-1,Math.min(1,v)); const end = t>=0?pos:neg; const a=Math.abs(t);
  const r=Math.round(mid[0]+(end[0]-mid[0])*a), g=Math.round(mid[1]+(end[1]-mid[1])*a), b=Math.round(mid[2]+(end[2]-mid[2])*a);
  return "rgb("+r+","+g+","+b+")";
}
function cssRGB(v){ const c=css(v);
  if(c.startsWith("#")){const n=c.slice(1); const f=n.length===3?n.split("").map(h=>h+h).join(""):n;
    return [parseInt(f.slice(0,2),16),parseInt(f.slice(2,4),16),parseInt(f.slice(4,6),16)];}
  const m=c.match(/\d+/g); return m?m.slice(0,3).map(Number):[128,128,128]; }
function matrixAsOf(){
  const N=order.length, M=[];
  for(let i=0;i<N;i++){M.push(new Array(N).fill(NaN)); M[i][i]=1;}
  for(let i=0;i<N;i++)for(let j=i+1;j<N;j++){
    const arr=pairSeries(order[i],order[j]); let t=state.asof;
    while(t>=0 && arr[t]!==arr[t]) t--; const v=t>=0?arr[t]:NaN;
    M[i][j]=M[j][i]=v;
  }
  return M;
}
function drawHeat(){
  const dpr=Math.min(2,window.devicePixelRatio||1);
  const W=hc.clientWidth, N=order.length;
  const labW=64, top=8, gap=2;
  const cell=Math.floor((W-labW-2)/N);
  const H=labW+ top + cell*N + 2;
  hc.width=W*dpr; hc.height=H*dpr; hc.style.height=H+"px";
  hctx.setTransform(dpr,0,0,dpr,0,0); hctx.clearRect(0,0,W,H);
  const gx=labW, gy=top;
  heatGeom={gx,gy,cell,N,labW};
  const M=matrixAsOf();
  hctx.font='10px "IBM Plex Mono", monospace';
  for(let i=0;i<N;i++)for(let j=0;j<N;j++){
    const x=gx+j*cell, y=gy+i*cell, v=M[i][j];
    hctx.fillStyle=heatColor(v);
    hctx.fillRect(x+gap/2,y+gap/2,cell-gap,cell-gap);
    const foc = state.focus && ((order[i]===state.anchor&&order[j]===state.focus)||(order[j]===state.anchor&&order[i]===state.focus));
    if(foc){ hctx.strokeStyle=css("--ink"); hctx.lineWidth=2;
      hctx.strokeRect(x+gap/2,y+gap/2,cell-gap,cell-gap); }
    if(cell>=26 && v===v){
      hctx.fillStyle = Math.abs(v)>0.55 ? "#fff" : css("--ink");
      hctx.textAlign="center"; hctx.textBaseline="middle";
      hctx.fillText(v.toFixed(2), x+cell/2, y+cell/2);
    }
  }
  // labels
  hctx.fillStyle=css("--ink-2"); hctx.font='11px "IBM Plex Sans", sans-serif';
  hctx.textAlign="right"; hctx.textBaseline="middle";
  for(let i=0;i<N;i++) hctx.fillText(labels[order[i]], gx-6, gy+i*cell+cell/2);
  for(let j=0;j<N;j++){ hctx.save();
    hctx.translate(gx+j*cell+cell/2, gy+N*cell+10); hctx.rotate(-Math.PI/4);
    hctx.textAlign="right"; hctx.textBaseline="middle";
    hctx.fillText(labels[order[j]],0,0); hctx.restore(); }
  $("#hm-sub").textContent = "as of "+dates[state.asof]+" · "+(state.method==="rolling"?state.window+"-obs rolling":"EWMA hl "+state.halflife);
}
const htip=$("#heat-tip");
hc.addEventListener("mousemove", e=>{
  if(!heatGeom) return; const r=hc.getBoundingClientRect();
  const {gx,gy,cell,N}=heatGeom; const j=Math.floor((e.clientX-r.left-gx)/cell), i=Math.floor((e.clientY-r.top-gy)/cell);
  if(i<0||j<0||i>=N||j>=N){ htip.style.opacity=0; return; }
  const M=matrixAsOf(), v=M[i][j];
  htip.innerHTML='<div class="tt-date">'+dates[state.asof]+'</div><div class="tt-row"><span>'+labels[order[i]]+' · '+labels[order[j]]+'</span><b>'+(v===v?fmt(v):"—")+'</b></div>';
  htip.style.opacity=1; const tw=htip.offsetWidth;
  let lx=e.clientX-r.left+12; if(lx+tw>hc.clientWidth) lx=e.clientX-r.left-tw-12;
  htip.style.left=Math.max(0,lx)+"px"; htip.style.top=Math.max(0,e.clientY-r.top-10)+"px";
});
hc.addEventListener("mouseleave", ()=>htip.style.opacity=0);
hc.addEventListener("click", e=>{
  if(!heatGeom) return; const r=hc.getBoundingClientRect();
  const {gx,gy,cell,N}=heatGeom; const j=Math.floor((e.clientX-r.left-gx)/cell), i=Math.floor((e.clientY-r.top-gy)/cell);
  if(i<0||j<0||i>=N||j>=N||i===j) return;
  focusPair(order[i], order[j]);
});

// ================= KPIs + TABLE =================
function renderKpis(pairs){
  if(!pairs.length){ $("#kpis").innerHTML=""; return; }
  const byswing=[...pairs].sort((a,b)=>b.swing-a.swing);
  const bypos=[...pairs].sort((a,b)=>b.latest-a.latest);
  const mostU=byswing[0], sPos=bypos[0], sNeg=bypos[bypos.length-1];
  const tile=(lab,val,sub,cls)=>'<div class="kpi"><div class="k-label">'+lab+'</div><div class="k-val '+(cls||"")+'">'+val+'</div><div class="k-sub">'+sub+'</div></div>';
  const nm=p=>labels[p.a]+" · "+labels[p.b];
  $("#kpis").innerHTML =
    tile("Observations", DATA.n.toLocaleString(),
         dates[0]+" → "+dates[T-1]) +
    tile("Most unstable pair", "&#8597; "+mostU.swing.toFixed(2),
         nm(mostU)+" (max−min)") +
    tile("Strongest + now", '<span class="val-pos">'+fmt(sPos.latest)+'</span>', nm(sPos)) +
    tile("Strongest − now", '<span class="val-neg">'+fmt(sNeg.latest)+'</span>', nm(sNeg));
}
function renderTable(pairs){
  const key=state.sortKey;
  const rows=[...pairs].sort((a,b)=> key==="pair" ? (labels[a.a]+labels[a.b]).localeCompare(labels[b.a]+labels[b.b]) : b[key]-a[key]);
  const maxSwing=Math.max(...pairs.map(p=>p.swing),0.001);
  const tb=$("#tbody"); tb.innerHTML="";
  rows.forEach(p=>{
    const tr=document.createElement("tr");
    if(state.focus && ((p.a===state.anchor&&p.b===state.focus)||(p.b===state.anchor&&p.a===state.focus))) tr.className="active";
    const cl=v=>v>=0?"val-pos":"val-neg";
    const w=Math.round(p.swing/maxSwing*100);
    // range bar mapped from [-1,1] to [0,100]
    const lo=(p.min+1)/2*100, hi=(p.max+1)/2*100;
    tr.innerHTML=
      '<td><span class="pairname"><span class="dd"><i class="dot" style="background:'+css(colorOf[p.a])+'"></i><i class="dot" style="background:'+css(colorOf[p.b])+'"></i></span>'+labels[p.a]+' · '+labels[p.b]+'</span></td>'+
      '<td class="num '+cl(p.latest)+'">'+fmt(p.latest)+'</td>'+
      '<td class="num">'+fmt(p.mean)+'</td>'+
      '<td class="num">'+fmt(p.min)+'</td>'+
      '<td class="num">'+fmt(p.max)+'</td>'+
      '<td class="num"><b>'+p.swing.toFixed(2)+'</b></td>'+
      '<td class="bar-cell"><div class="bar"><i style="left:'+lo.toFixed(1)+'%;width:'+(hi-lo).toFixed(1)+'%"></i></div></td>';
    tr.addEventListener("click", ()=>focusPair(p.a,p.b));
    tb.appendChild(tr);
  });
}

// ================= wiring =================
function focusPair(a,b){
  // put one member on the anchor, focus the other
  if(a===state.anchor){ state.focus=b; }
  else if(b===state.anchor){ state.focus=a; }
  else { state.anchor=a; state.focus=b; $("#anchor").value=a; }
  state.off.delete(state.focus);
  renderAll();
}
function renderLegend(){
  const lg=$("#legend"); lg.innerHTML="";
  order.filter(k=>k!==state.anchor).forEach(k=>{
    const el=document.createElement("span");
    el.className="lg"+(state.off.has(k)?" off":"")+(state.focus===k?" foc":"");
    el.innerHTML='<i class="dot" style="background:'+css(colorOf[k])+'"></i>'+labels[k];
    el.addEventListener("click", ()=>{ if(state.off.has(k))state.off.delete(k); else state.off.add(k);
      if(state.focus===k) state.focus=null; renderAll(); });
    lg.appendChild(el);
  });
}
function renderAll(){
  const pairs=allPairs();
  renderKpis(pairs); renderTable(pairs);
  renderLegend(); drawLine(); drawHeat();
}
function clampAsof(){
  const fv=firstValid();
  const asofEl=$("#asof"); asofEl.min=fv; asofEl.max=T-1;
  if(state.asof<fv) state.asof=T-1;
  asofEl.value=state.asof; $("#asof-v").textContent="· "+dates[state.asof];
}

// controls
$("#method").addEventListener("click", e=>{
  const b=e.target.closest("button"); if(!b) return;
  state.method=b.dataset.m;
  [...$("#method").children].forEach(x=>x.setAttribute("aria-pressed", x===b));
  $("#win-label").textContent = state.method==="rolling"?"Window (obs)":"Half-life (obs)";
  const w=$("#window");
  if(state.method==="rolling"){ w.min=20;w.max=252;w.value=state.window; $("#window-v").textContent=state.window; }
  else { w.min=5;w.max=120;w.value=state.halflife; $("#window-v").textContent=state.halflife; }
  clampAsof(); renderAll();
});
$("#window").addEventListener("input", e=>{
  const v=+e.target.value;
  if(state.method==="rolling"){ state.window=v; $("#window-v").textContent=v; }
  else { state.halflife=v; $("#window-v").textContent=v; }
  clampAsof(); renderAll();
});
$("#anchor").addEventListener("change", e=>{ state.anchor=e.target.value; state.focus=null; state.off.clear(); renderAll(); });
$("#asof").addEventListener("input", e=>{ state.asof=+e.target.value; $("#asof-v").textContent="· "+dates[state.asof]; drawHeat(); drawLine(); });
document.querySelectorAll("#tbl thead th[data-c]").forEach(th=>{
  th.addEventListener("click", ()=>{ state.sortKey=th.dataset.c;
    document.querySelectorAll("#tbl thead th").forEach(x=>x.classList.remove("sorted"));
    th.classList.add("sorted"); renderTable(allPairs()); });
});

// theme toggle
function applyThemeLabel(){
  const dark = document.documentElement.getAttribute("data-theme")==="dark" ||
    (!document.documentElement.getAttribute("data-theme") && matchMedia("(prefers-color-scheme:dark)").matches);
  $("#theme-ico").textContent = dark ? "☀" : "☾";
}
$("#theme-btn").addEventListener("click", ()=>{
  const cur=document.documentElement.getAttribute("data-theme");
  const dark = cur==="dark" || (!cur && matchMedia("(prefers-color-scheme:dark)").matches);
  document.documentElement.setAttribute("data-theme", dark?"light":"dark");
  applyThemeLabel(); _cache.__none=0; renderAll();
});
matchMedia("(prefers-color-scheme:dark)").addEventListener("change", ()=>{ applyThemeLabel(); renderAll(); });

// anchor options + source chip
const anchorSel=$("#anchor");
order.forEach(k=>{ const o=document.createElement("option"); o.value=k; o.textContent=labels[k]; if(k===state.anchor)o.selected=true; anchorSel.appendChild(o); });
const srcName = DATA.source==="synthetic" ? "Synthetic sample" : DATA.source==="csv" ? "CSV data" : "Live data";
$("#src-chip").innerHTML = '<b>'+srcName+'</b> · '+order.length+' series';
$("#foot-src").textContent = DATA.source==="synthetic"
  ? "Synthetic sample data — deterministic, with deliberately time-varying correlations for demonstration (no live market data)."
  : "Loaded from "+(DATA.source==="csv"?"a user CSV.":"live sources (FRED / Yahoo Finance).");

// init
$("#window-v").textContent=state.window;
clampAsof(); applyThemeLabel(); renderAll();
window.addEventListener("resize", ()=>{ drawLine(); drawHeat(); });
})();
</script>"""
