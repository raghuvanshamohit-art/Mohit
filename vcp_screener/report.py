"""Reporting: console summary, CSV matrix, and a styled HTML screener board."""

from __future__ import annotations

import html
from datetime import datetime
from typing import List

import pandas as pd

from .config import Config
from .constants import CRITERIA_ORDER, SHORT_HEADERS
from .criteria import MarketContext, StockResult


# --------------------------------------------------------------------------- #
# DataFrame
# --------------------------------------------------------------------------- #
def results_to_frame(results: List[StockResult], config: Config) -> pd.DataFrame:
    """One row per stock, one column per criterion, plus summary columns."""
    rows = []
    for r in results:
        row = {"Symbol": r.symbol, "Price": round(r.price, 2) if r.price == r.price else None}
        for label in CRITERIA_ORDER:
            row[label] = bool(r.criteria.get(label, False))
        row["RS_Rating"] = r.rs_rating
        row["Passed"] = r.passed_count(config)
        row["Mandatory"] = r.total_mandatory(config)
        row["FULL_VCP_SETUP"] = r.full_setup(config)
        row["Note"] = r.error or ""
        rows.append(row)
    return pd.DataFrame(rows)


def write_csv(results: List[StockResult], config: Config, path: str) -> None:
    results_to_frame(results, config).to_csv(path, index=False)


# --------------------------------------------------------------------------- #
# Console
# --------------------------------------------------------------------------- #
def print_summary(
    results: List[StockResult],
    market: MarketContext,
    config: Config,
    top: int = 25,
) -> None:
    total = len(results)
    errored = [r for r in results if r.error]
    full = [r for r in results if r.full_setup(config)]

    print()
    print("=" * 64)
    print("VCP F&O SCREENER")
    print("=" * 64)
    print(f"Universe evaluated : {total}   (skipped for data: {len(errored)})")
    print(f"Nifty in uptrend   : {'YES' if market.nifty_uptrend else 'NO'}")
    print(f"FULL VCP SETUP      : {len(full)} stock(s)")
    print("-" * 64)

    if full:
        print("FULL VCP SETUP (all mandatory checks pass):")
        for r in sorted(full, key=lambda x: (x.rs_rating or -1), reverse=True):
            rs = f"{r.rs_rating:.0f}" if r.rs_rating is not None else "  -"
            print(f"  ★ {r.symbol:<14} ₹{r.price:>9.2f}   RS {rs:>3}")
        print("-" * 64)

    ranked = [r for r in results if not r.error]
    ranked.sort(key=lambda r: (r.passed_count(config), r.rs_rating or -1), reverse=True)
    print(f"Top {min(top, len(ranked))} by checks passed:")
    print(f"  {'Symbol':<14}{'Price':>10}  {'Pass':>5}  {'RS':>4}  Setup")
    for r in ranked[:top]:
        rs = f"{r.rs_rating:.0f}" if r.rs_rating is not None else "-"
        flag = "FULL" if r.full_setup(config) else ""
        passed = f"{r.passed_count(config)}/{r.total_mandatory(config)}"
        print(f"  {r.symbol:<14}{r.price:>10.2f}  {passed:>5}  {rs:>4}  {flag}")
    print("=" * 64)


# --------------------------------------------------------------------------- #
# HTML
# --------------------------------------------------------------------------- #
def write_html(
    results: List[StockResult],
    market: MarketContext,
    config: Config,
    path: str,
    ranked: List[StockResult] | None = None,
) -> None:
    rows = ranked if ranked is not None else results
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    n_full = sum(1 for r in results if r.full_setup(config))
    n_eval = sum(1 for r in results if not r.error)

    header_cells = "".join(
        f'<th class="rot" title="{html.escape(label)}">'
        f'<span>{html.escape(SHORT_HEADERS.get(label, label))}</span></th>'
        for label in CRITERIA_ORDER
    )

    body_rows = []
    for r in rows:
        if r.error:
            body_rows.append(
                f'<tr class="err"><td class="sym">{html.escape(r.symbol)}</td>'
                f'<td class="px">-</td>'
                + "".join('<td class="na">·</td>' for _ in CRITERIA_ORDER)
                + '<td class="na">-</td><td class="na">-</td>'
                f'<td class="setup wait">DATA</td></tr>'
            )
            continue

        cells = []
        for label in CRITERIA_ORDER:
            ok = bool(r.criteria.get(label, False))
            cells.append(
                f'<td class="{"yes" if ok else "no"}">{"✓" if ok else "✕"}</td>'
            )
        rs = f"{r.rs_rating:.0f}" if r.rs_rating is not None else "-"
        passed = f"{r.passed_count(config)}/{r.total_mandatory(config)}"
        full = r.full_setup(config)
        setup = (
            '<td class="setup full">FULL ✓</td>'
            if full
            else '<td class="setup wait">WAIT</td>'
        )
        body_rows.append(
            f'<tr class="{"is-full" if full else ""}">'
            f'<td class="sym">{html.escape(r.symbol)}</td>'
            f'<td class="px">{r.price:,.2f}</td>'
            + "".join(cells)
            + f'<td class="rs">{rs}</td><td class="score">{passed}</td>{setup}</tr>'
        )

    legend = " &nbsp;·&nbsp; ".join(
        f"<b>{html.escape(SHORT_HEADERS.get(l, l))}</b> = {html.escape(l)}"
        for l in CRITERIA_ORDER
    )

    market_badge = (
        '<span class="badge up">Nifty: Uptrend</span>'
        if market.nifty_uptrend
        else '<span class="badge down">Nifty: Not in uptrend</span>'
    )

    doc = _HTML_TEMPLATE.format(
        generated=generated,
        n_full=n_full,
        n_eval=n_eval,
        market_badge=market_badge,
        header_cells=header_cells,
        body_rows="\n".join(body_rows),
        legend=legend,
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)


_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VCP F&amp;O Screener</title>
<style>
  :root {{ --yes:#4caf50; --no:#e05656; --full:#2e7d32; --wait:#e05656;
           --bg:#f6f7f9; --card:#fff; --ink:#1f2430; --muted:#6b7280; --line:#e5e7eb; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#12151c; --card:#1a1f2b; --ink:#e6e9ef; --muted:#9aa4b2; --line:#2a3140; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
          background:var(--bg); color:var(--ink); }}
  .wrap {{ max-width:1200px; margin:0 auto; padding:20px 16px 60px; }}
  h1 {{ font-size:20px; margin:0 0 4px; }}
  .sub {{ color:var(--muted); margin:0 0 14px; }}
  .stats {{ display:flex; flex-wrap:wrap; gap:10px; margin:12px 0 18px; }}
  .stat {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:10px 14px; }}
  .stat b {{ font-size:20px; display:block; }}
  .stat span {{ color:var(--muted); font-size:12px; }}
  .badge {{ display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:600; }}
  .badge.up {{ background:rgba(76,175,80,.15); color:var(--yes); }}
  .badge.down {{ background:rgba(224,86,86,.15); color:var(--no); }}
  .tablewrap {{ overflow-x:auto; border:1px solid var(--line); border-radius:12px; background:var(--card); }}
  table {{ border-collapse:collapse; width:100%; min-width:1000px; }}
  th, td {{ padding:7px 6px; text-align:center; border-bottom:1px solid var(--line); white-space:nowrap; }}
  thead th {{ position:sticky; top:0; background:var(--card); z-index:2; font-size:11px; color:var(--muted); }}
  th.rot span {{ display:inline-block; }}
  td.sym {{ text-align:left; font-weight:600; position:sticky; left:0; background:var(--card); }}
  tr.is-full td.sym {{ color:var(--full); }}
  td.px, td.rs, td.score {{ font-variant-numeric:tabular-nums; }}
  td.yes {{ color:#fff; background:var(--yes); font-weight:700; }}
  td.no  {{ color:#fff; background:var(--no); font-weight:700; }}
  td.na  {{ color:var(--muted); }}
  td.setup {{ font-weight:700; color:#fff; border-radius:0; }}
  td.setup.full {{ background:var(--full); }}
  td.setup.wait {{ background:var(--wait); }}
  tr.is-full {{ background:rgba(76,175,80,.06); }}
  tr.err {{ opacity:.55; }}
  tbody tr:hover {{ background:rgba(127,127,127,.08); }}
  .legend {{ color:var(--muted); font-size:12px; margin-top:16px; line-height:1.9; }}
  .foot {{ color:var(--muted); font-size:12px; margin-top:20px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>VCP F&amp;O Screener</h1>
  <p class="sub">Volatility Contraction Pattern &middot; Trend Template &middot; NSE Futures &amp; Options universe</p>
  <div class="stats">
    <div class="stat"><b>{n_full}</b><span>FULL VCP SETUP</span></div>
    <div class="stat"><b>{n_eval}</b><span>Stocks evaluated</span></div>
    <div class="stat">{market_badge}<br><span>Generated {generated}</span></div>
  </div>
  <div class="tablewrap">
    <table>
      <thead>
        <tr>
          <th class="sym" style="text-align:left">Symbol</th>
          <th>Price</th>
          {header_cells}
          <th>RS</th><th>Pass</th><th>Setup</th>
        </tr>
      </thead>
      <tbody>
        {body_rows}
      </tbody>
    </table>
  </div>
  <div class="legend">{legend}<br>* optional criterion (not required for a FULL setup)</div>
  <p class="foot">Educational tool, not investment advice. Verify signals on your own charts before acting.</p>
</div>
</body>
</html>
"""
