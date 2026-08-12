#!/usr/bin/env python3
"""Backtest the VCP setup over historical NSE data.

Live data (needs ~3-5 years of history for meaningful results)::

    python run_backtest.py --history-days 1750

Offline (bundled synthetic sample data)::

    python run_backtest.py --provider csv --csv-dir sample_data \
        --index-file NIFTY --universe-file sample_data/symbols.txt

Common knobs::

    --stop-pct 0.08        initial stop below entry
    --trail-ma 50          exit on a close back below this MA
    --max-hold 250         max trading days per trade
    --no-market-filter     ignore the "Nifty in Uptrend" gate (for comparison)
    --max-positions 10     concurrency cap for the equity model
"""

from __future__ import annotations

import argparse
import html
import os
import sys
from datetime import datetime

from vcp_screener.backtest import BacktestConfig, run_backtest
from vcp_screener.config import Config
from vcp_screener.universe import load_universe


def build_provider(args):
    if args.provider == "csv":
        from vcp_screener.data import CSVProvider
        if not args.csv_dir:
            sys.exit("--csv-dir is required when --provider csv")
        return CSVProvider(args.csv_dir, index_file=args.index_file)
    from vcp_screener.bhavcopy import BhavcopyProvider
    return BhavcopyProvider(cache_dir=args.cache_dir or "cache/bhav",
                            history_days=args.history_days, workers=args.workers)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Backtest the VCP F&O setup.")
    p.add_argument("--provider", choices=["bhavcopy", "csv"], default="bhavcopy")
    p.add_argument("--history-days", type=int, default=1750)
    p.add_argument("--workers", type=int, default=10)
    p.add_argument("--cache-dir", default=None)
    p.add_argument("--csv-dir", default=None)
    p.add_argument("--index-file", default="NIFTY")
    p.add_argument("--index-symbol", default="^NSEI")
    p.add_argument("--universe-file", default=None)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--stop-pct", type=float, default=0.08)
    p.add_argument("--exit-mode", choices=["trail_ma", "big_candle"], default="trail_ma",
                   help="profit exit: ride the trend (trail_ma) or sell into the "
                        "first big up candle (big_candle)")
    p.add_argument("--big-candle-atr", type=float, default=3.0,
                   help="big_candle: bullish day with range >= N x ATR triggers the exit")
    p.add_argument("--big-candle-pct", type=float, default=0.0,
                   help="big_candle: alternatively, a day gaining >= this fraction (e.g. 0.07)")
    p.add_argument("--trail-ma", type=int, default=50)
    p.add_argument("--no-trail-ma", action="store_true")
    p.add_argument("--trail-pct", type=float, default=0.0)
    p.add_argument("--max-hold", type=int, default=250)
    p.add_argument("--entry", choices=["next_open", "signal_close"], default="next_open")
    p.add_argument("--no-market-filter", action="store_true")
    p.add_argument("--cost-pct", type=float, default=0.001)
    p.add_argument("--max-positions", type=int, default=10)
    p.add_argument("--capital", type=float, default=1_000_000.0)
    p.add_argument("--output-dir", default="output")
    return p.parse_args(argv)


def _pct(x):
    return f"{x*100:.1f}%" if x is not None else "-"


def print_summary(res):
    s = res["summary"]
    print("\n" + "=" * 64)
    print("VCP SETUP BACKTEST")
    print("=" * 64)
    if not s or s.get("n", 0) == 0:
        print("No trades generated.", res.get("note", ""))
        return
    span = res.get("span", {})
    if span:
        print(f"Period      : {span['start'].date()} -> {span['end'].date()}"
              f"   (Nifty buy&hold: {_pct(span.get('nifty_return'))})")
    print(f"Universe    : {res['universe']} stocks with sufficient history")
    print("-" * 64)
    print(f"Trades      : {s['n']}")
    print(f"Win rate    : {_pct(s['win_rate'])}")
    print(f"Avg trade   : {_pct(s['avg'])}   (median {_pct(s['median'])})")
    print(f"Avg win     : {_pct(s['avg_win'])}    Avg loss: {_pct(s['avg_loss'])}")
    print(f"Expectancy  : {_pct(s['expectancy'])} per trade")
    print(f"Profit factor: {s['profit_factor']:.2f}")
    print(f"Avg hold    : {s['avg_bars']:.0f} trading days")
    print(f"Best / Worst: {_pct(s['best'])} / {_pct(s['worst'])}")
    eq = res.get("equity", {})
    if eq:
        print("-" * 64)
        print(f"Equity model (equal-weight, max {res['config'].max_positions} concurrent):")
        print(f"  Taken/Skipped : {eq['taken']} / {eq['skipped']}")
        print(f"  Total return  : {_pct(eq['total_return'])} over {eq['years']:.1f}y"
              f"   CAGR {_pct(eq['cagr'])}")
        print(f"  Max drawdown  : {_pct(eq['max_drawdown'])}")
    if "no_filter_summary" in res and res["no_filter_summary"].get("n"):
        nf = res["no_filter_summary"]
        print("-" * 64)
        print("Without the 'Nifty in Uptrend' market filter:")
        print(f"  Trades {nf['n']}   Win {_pct(nf['win_rate'])}"
              f"   Expectancy {_pct(nf['expectancy'])}   PF {nf['profit_factor']:.2f}")
    print("-" * 64)
    print("Exit reasons:", ", ".join(f"{k}={v}" for k, v in sorted(res["by_reason"].items())))
    print("=" * 64)


def _svg_equity(eq_series, width=760, height=220):
    if eq_series is None or len(eq_series) < 2:
        return "<p>(not enough trades to plot an equity curve)</p>"
    vals = eq_series.to_numpy(float)
    lo, hi = vals.min(), vals.max()
    rng = (hi - lo) or 1.0
    n = len(vals)
    pts = []
    for i, v in enumerate(vals):
        x = 40 + (width - 60) * i / (n - 1)
        y = 10 + (height - 30) * (1 - (v - lo) / rng)
        pts.append(f"{x:.1f},{y:.1f}")
    base_y = 10 + (height - 30) * (1 - (eq_series.iloc[0] - lo) / rng)
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" '
        f'aria-label="Equity curve">'
        f'<line x1="40" y1="{base_y:.1f}" x2="{width-20}" y2="{base_y:.1f}" '
        f'stroke="#9aa4b2" stroke-dasharray="4 4" stroke-width="1"/>'
        f'<polyline fill="none" stroke="#2e7d32" stroke-width="2" points="{" ".join(pts)}"/>'
        f'</svg>'
    )


def write_html(res, path):
    s = res["summary"]
    eq = res.get("equity", {})
    span = res.get("span", {})
    cfg = res["config"]
    tiles = [
        ("Trades", str(s.get("n", 0))),
        ("Win rate", _pct(s.get("win_rate", 0))),
        ("Expectancy/trade", _pct(s.get("expectancy", 0))),
        ("Profit factor", f"{s.get('profit_factor', 0):.2f}"),
        ("CAGR", _pct(eq.get("cagr")) if eq else "-"),
        ("Max drawdown", _pct(eq.get("max_drawdown")) if eq else "-"),
        ("Avg win", _pct(s.get("avg_win", 0))),
        ("Avg loss", _pct(s.get("avg_loss", 0))),
    ]
    tile_html = "".join(
        f'<div class="tile"><b>{html.escape(v)}</b><span>{html.escape(k)}</span></div>'
        for k, v in tiles
    )
    yr = res.get("by_year", {})
    yr_rows = "".join(
        f"<tr><td>{y}</td><td>{d['n']}</td><td>{_pct(d['win_rate'])}</td>"
        f"<td>{_pct(d['expectancy'])}</td><td>{d['profit_factor']:.2f}</td></tr>"
        for y, d in yr.items()
    )
    nf = res.get("no_filter_summary")
    nf_html = ""
    if nf and nf.get("n"):
        nf_html = (
            '<p class="note"><b>Market filter test.</b> Same setup with the '
            f'"Nifty in Uptrend" gate <b>ON</b>: {s["n"]} trades, win {_pct(s["win_rate"])}, '
            f'expectancy {_pct(s["expectancy"])}, PF {s["profit_factor"]:.2f}. '
            f'With it <b>OFF</b>: {nf["n"]} trades, win {_pct(nf["win_rate"])}, '
            f'expectancy {_pct(nf["expectancy"])}, PF {nf["profit_factor"]:.2f}.</p>'
        )
    period = (f"{span['start'].date()} to {span['end'].date()}" if span else "")
    nifty_bh = _pct(span.get("nifty_return")) if span else "-"
    doc = _TEMPLATE.format(
        generated=datetime.now().strftime("%Y-%m-%d %H:%M"),
        period=html.escape(period), nifty_bh=nifty_bh,
        stop=_pct(cfg.stop_pct), trail=(f"close &lt; {cfg.trail_ma}-DMA" if cfg.use_trail_ma else "off"),
        maxhold=cfg.max_hold, cost=_pct(cfg.cost_pct),
        tiles=tile_html, equity=_svg_equity(eq.get("curve")),
        year_rows=yr_rows or '<tr><td colspan="5">no trades</td></tr>',
        nf=nf_html,
        reasons=html.escape(", ".join(f"{k}={v}" for k, v in sorted(res.get("by_reason", {}).items()))),
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)


_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VCP Setup Backtest</title><style>
:root{{--bg:#f6f7f9;--card:#fff;--ink:#1f2430;--muted:#6b7280;--line:#e5e7eb;--accent:#2e7d32;}}
@media(prefers-color-scheme:dark){{:root{{--bg:#12151c;--card:#1a1f2b;--ink:#e6e9ef;--muted:#9aa4b2;--line:#2a3140;}}}}
*{{box-sizing:border-box;}}body{{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}}
.wrap{{max-width:900px;margin:0 auto;padding:24px 16px 60px;}}h1{{font-size:22px;margin:0 0 2px;}}
.sub{{color:var(--muted);margin:0 0 18px;}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0;}}
.tile{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;}}
.tile b{{font-size:22px;display:block;font-variant-numeric:tabular-nums;}}
.tile span{{color:var(--muted);font-size:12px;}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:16px 0;}}
h2{{font-size:15px;margin:0 0 10px;}}table{{border-collapse:collapse;width:100%;}}
th,td{{padding:6px 8px;text-align:right;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums;}}
th:first-child,td:first-child{{text-align:left;}}th{{color:var(--muted);font-weight:600;}}
.note{{color:var(--muted);font-size:13px;}}.foot{{color:var(--muted);font-size:12px;margin-top:20px;}}
</style></head><body><div class="wrap">
<h1>VCP Setup Backtest</h1>
<p class="sub">NSE F&amp;O universe &middot; {period} &middot; Nifty buy&amp;hold over the span: <b>{nifty_bh}</b></p>
<div class="tiles">{tiles}</div>
<div class="card"><h2>Equity curve (realized, equal-weight)</h2>{equity}</div>
<div class="card"><h2>By entry year</h2>
<table><thead><tr><th>Year</th><th>Trades</th><th>Win</th><th>Expectancy</th><th>PF</th></tr></thead>
<tbody>{year_rows}</tbody></table></div>
{nf}
<div class="card"><h2>Rules</h2><p class="note">Entry: next-day open on a fresh FULL VCP SETUP.
Initial stop: {stop}. Trailing exit: {trail}. Max hold: {maxhold} days. Round-trip cost: {cost}.
Exit reasons: {reasons}.</p></div>
<p class="foot">Backtest of a rules-based screen on historical data. Past performance does not
predict future results, and results are sensitive to the rules, costs, and survivorship bias
(today's F&amp;O list applied historically). Educational only, not investment advice. Generated {generated}.</p>
</div></body></html>"""


def main(argv=None):
    args = parse_args(argv)
    cfg = Config()
    bt = BacktestConfig(
        stop_pct=args.stop_pct, exit_mode=args.exit_mode,
        big_candle_atr_mult=args.big_candle_atr, big_candle_pct=args.big_candle_pct,
        use_trail_ma=not args.no_trail_ma, trail_ma=args.trail_ma,
        trail_pct=args.trail_pct, max_hold=args.max_hold, entry=args.entry,
        apply_market_filter=not args.no_market_filter, cost_pct=args.cost_pct,
        max_positions=args.max_positions, capital=args.capital,
    )
    symbols = load_universe(args.universe_file)
    if args.limit:
        symbols = symbols[: args.limit]

    print(f"Backtesting {len(symbols)} symbols via '{args.provider}' ...")
    provider = build_provider(args)
    nifty_df = provider.get_index(args.index_symbol)
    if nifty_df is None or nifty_df.empty:
        sys.exit("No index data - cannot run backtest.")
    data = provider.get_many(symbols)

    res = run_backtest(data, nifty_df, cfg, bt)
    print_summary(res)

    os.makedirs(args.output_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    import pandas as pd
    trades = res["trades"]
    if trades:
        csv_path = os.path.join(args.output_dir, f"backtest_{stamp}.csv")
        pd.DataFrame(trades).to_csv(csv_path, index=False)
        html_path = os.path.join(args.output_dir, f"backtest_{stamp}.html")
        write_html(res, html_path)
        print(f"\nReports written:\n  {csv_path}\n  {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
