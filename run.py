#!/usr/bin/env python3
"""CLI for the Indian sector & stock performance tool.

Examples:
    python run.py generate                 # fetch data -> output/sector_performance.json
    python run.py generate -o data.json    # custom output path
    python run.py show                      # print a summary table from the JSON
    python run.py show --sector it          # print one sector's stocks
    python run.py list                       # list all sectors and constituents

    # Intrinsic value + pyramiding plan for a single stock:
    python run.py value RELIANCE                       # auto-fetch what it can
    python run.py value RELIANCE --eps 55 --bvps 668 --growth 10 --price 1257.5
    python run.py value INFY --eps 65 --growth 10 --capital 100000 --tranches 4
    python run.py value TCS --eps 130 --growth 8 --mode trend --price 3200
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sector_stocks import sectors as sectors_mod
from sector_stocks.generate import write as generate_write

DEFAULT_JSON = "output/sector_performance.json"
PERIOD_KEYS = ["3m", "6m", "9m", "12m"]


def _fmt(v):
    if v is None:
        return f"{'-':>9}"
    return f"{v:+9.2f}"


def cmd_generate(args):
    generate_write(path=args.output, max_workers=args.workers, progress=not args.quiet)


def cmd_list(args):
    current_macro = None
    for sec in sectors_mod.all_sectors():
        if sec.macro != current_macro:
            current_macro = sec.macro
            print(f"\n=== {current_macro.upper()} ===")
        print(f"\n{sec.name}  [{len(sec.stocks)} stocks]")
        for st in sec.stocks:
            print(f"    {st.symbol:<12} {st.name}")
    total = len(sectors_mod.unique_symbols())
    print(f"\n{len(sectors_mod.all_sectors())} sectors, {total} unique stocks.")


def _load(path):
    p = Path(path)
    if not p.exists():
        print(f"No dataset at {path}. Run:  python run.py generate", file=sys.stderr)
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))


def cmd_show(args):
    data = _load(args.input)
    meta = data["meta"]
    print(f"Generated: {meta['generated_at']}   "
          f"({meta['num_ok']}/{meta['num_unique_stocks']} stocks OK)")
    print(f"Price source: {meta['price_source']} | Sectors: {meta['sector_source']}\n")

    header = f"{'':<28}" + "".join(f"{k:>9}" for k in PERIOD_KEYS)

    if args.sector:
        sec = next((s for s in data["sectors"] if s["key"] == args.sector
                    or s["name"].lower() == args.sector.lower()), None)
        if not sec:
            print(f"Unknown sector '{args.sector}'.", file=sys.stderr)
            sys.exit(1)
        print(f"{sec['name']}  ({sec['macro']})")
        print(header)
        print("-" * len(header))
        stocks = [s for s in sec["stocks"]]
        stocks.sort(key=lambda s: (s.get("returns", {}).get(args.sort) is None,
                                   -(s.get("returns", {}).get(args.sort) or 0)))
        for st in stocks:
            r = st.get("returns", {})
            line = f"{st['symbol']:<10}{st['name'][:17]:<18}" + "".join(_fmt(r.get(k)) for k in PERIOD_KEYS)
            if not st.get("ok"):
                line += "   (no data)"
            print(line)
        avg = sec["average_returns"]
        print("-" * len(header))
        print(f"{'SECTOR AVERAGE':<28}" + "".join(_fmt(avg.get(k)) for k in PERIOD_KEYS))
        return

    # Sector overview, sorted by chosen period.
    print("SECTOR PERFORMANCE (equal-weighted average return %)")
    print(header)
    print("-" * len(header))
    secs = sorted(
        data["sectors"],
        key=lambda s: (s["average_returns"].get(args.sort) is None,
                       -(s["average_returns"].get(args.sort) or 0)),
    )
    for sec in secs:
        avg = sec["average_returns"]
        label = f"{sec['name'][:20]:<21}({sec['num_ok']}/{sec['num_stocks']})"
        print(f"{label:<28}" + "".join(_fmt(avg.get(k)) for k in PERIOD_KEYS))


def cmd_value(args):
    """Intrinsic value + pyramiding plan for one stock."""
    from valuation.engine import value_stock
    from valuation.report import format_report

    # Classic trend pyramids taper each add (decreasing); value ladders widen
    # as they get cheaper (increasing). Honor an explicit --weighting either way.
    weighting = args.weighting
    if weighting is None:
        weighting = "decreasing" if args.mode == "trend" else "increasing"

    rep = value_stock(
        symbol=args.symbol,
        auto=not args.no_fetch,
        yahoo_symbol=args.yahoo_symbol,
        av_key=args.av_key,
        margin_of_safety=args.mos / 100.0,
        tranches=args.tranches,
        step=args.step / 100.0,
        weighting=weighting,
        capital=args.capital,
        stop_pct=args.stop / 100.0,
        pyramid_mode=args.mode,
        trend_entry=args.trend_entry,
        # fundamental overrides (None means "not supplied")
        eps=args.eps,
        book_value_per_share=args.bvps,
        fcf_per_share=args.fcf,
        dividend_per_share=args.dividend,
        growth_rate=None if args.growth is None else args.growth / 100.0,
        terminal_growth=None if args.terminal_growth is None else args.terminal_growth / 100.0,
        discount_rate=None if args.discount is None else args.discount / 100.0,
        years=args.years,
        fair_pe=args.fair_pe,
        bond_yield=args.bond_yield,
        current_price=args.price,
    )

    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print(format_report(rep))


def cmd_serve(args):
    """Run the live valuation web app (type a symbol -> live fetch -> value)."""
    import os
    from valuation.server import serve
    if args.av_key:
        os.environ["ALPHAVANTAGE_API_KEY"] = args.av_key
    serve(host=args.host, port=args.port, open_browser=not args.no_browser)


def main(argv=None):
    p = argparse.ArgumentParser(description="Indian sector & stock performance")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="fetch data and write JSON")
    g.add_argument("-o", "--output", default=DEFAULT_JSON)
    g.add_argument("-w", "--workers", type=int, default=8)
    g.add_argument("-q", "--quiet", action="store_true")
    g.set_defaults(func=cmd_generate)

    l = sub.add_parser("list", help="list sectors and constituents")
    l.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="print a table from the JSON")
    s.add_argument("-i", "--input", default=DEFAULT_JSON)
    s.add_argument("--sector", help="show one sector by key or name")
    s.add_argument("--sort", default="12m", choices=PERIOD_KEYS,
                   help="period to sort by (default 12m)")
    s.set_defaults(func=cmd_show)

    v = sub.add_parser(
        "value",
        help="intrinsic value + pyramiding plan for one stock",
        description="Estimate a stock's intrinsic (fair) value and build a "
                    "pyramiding buy plan. Supply fundamentals as flags; a symbol "
                    "auto-fetches the current price (and fundamentals where Yahoo "
                    "allows it). Rates are entered as percentages.")
    v.add_argument("symbol", nargs="?", help="NSE symbol (RELIANCE) or Yahoo symbol")
    v.add_argument("--yahoo-symbol", dest="yahoo_symbol",
                   help="force a Yahoo symbol (for non-NSE tickers, e.g. AAPL)")
    v.add_argument("--no-fetch", action="store_true",
                   help="do not contact the network; use only supplied inputs")
    v.add_argument("--av-key", dest="av_key",
                   help="Alpha Vantage API key to auto-fetch fundamentals when "
                        "Yahoo is blocked (or set ALPHAVANTAGE_API_KEY)")
    v.add_argument("--json", action="store_true", help="emit the full report as JSON")
    # Fundamentals (per share).
    v.add_argument("--eps", type=float, help="trailing earnings per share")
    v.add_argument("--bvps", type=float, help="book value per share")
    v.add_argument("--fcf", type=float, help="free cash flow per share")
    v.add_argument("--dividend", type=float, help="trailing dividend per share")
    v.add_argument("--price", type=float, help="override the current market price")
    # Assumptions (percentages, except years / PE).
    v.add_argument("--growth", type=float, help="expected annual growth %% (e.g. 10)")
    v.add_argument("--terminal-growth", dest="terminal_growth", type=float,
                   help="perpetual growth %% after the horizon (default 3)")
    v.add_argument("--discount", type=float,
                   help="discount / required-return %% (default 12)")
    v.add_argument("--years", type=int, help="projection horizon in years (default 10)")
    v.add_argument("--fair-pe", dest="fair_pe", type=float,
                   help="exit P/E for the earnings-power model")
    v.add_argument("--bond-yield", dest="bond_yield", type=float,
                   help="AAA bond yield %% for Graham revised (default 4.4)")
    v.add_argument("--mos", type=float, default=30.0,
                   help="margin of safety %% (default 30)")
    # Pyramid options.
    v.add_argument("--mode", choices=["value", "trend"], default="value",
                   help="value = accumulate below fair value; trend = add to a winner")
    v.add_argument("--tranches", type=int, default=3, help="number of buy levels")
    v.add_argument("--step", type=float, default=10.0,
                   help="%% gap between tranches (default 10)")
    v.add_argument("--weighting", choices=["increasing", "equal", "decreasing"],
                   default=None,
                   help="tranche size scheme (default: increasing for value, "
                        "decreasing for trend)")
    v.add_argument("--capital", type=float, help="budget to size whole-share tranches")
    v.add_argument("--stop", type=float, default=10.0,
                   help="stop-loss %% below the last tranche (default 10)")
    v.add_argument("--trend-entry", dest="trend_entry", type=float,
                   help="base entry for --mode trend (default current price)")
    v.set_defaults(func=cmd_value)

    sv = sub.add_parser(
        "serve",
        help="run the live valuation web app (type a symbol in the browser)",
        description="Serve a local web page where you type a stock symbol and it "
                    "fetches live market data and computes intrinsic value + a "
                    "pyramiding plan. Runs on your machine so it can reach Yahoo "
                    "directly. Open http://127.0.0.1:8000/ (opens automatically).")
    sv.add_argument("-p", "--port", type=int, default=8000, help="port (default 8000)")
    sv.add_argument("--host", default="127.0.0.1",
                    help="bind address (default 127.0.0.1; use 0.0.0.0 to expose on LAN)")
    sv.add_argument("--no-browser", action="store_true",
                    help="do not open a browser automatically")
    sv.add_argument("--av-key", dest="av_key",
                    help="Alpha Vantage API key for auto-fetching fundamentals "
                         "(applies to every request; or set ALPHAVANTAGE_API_KEY)")
    sv.set_defaults(func=cmd_serve)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
