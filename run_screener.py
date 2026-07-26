#!/usr/bin/env python3
"""Command-line entry point for the VCP F&O screener.

Live run -- official NSE Bhavcopy EOD data (the default). The first run
backfills ~2 years of daily bhavcopies into a local cache; later runs only
fetch new trading days::

    python run_screener.py

Alternative live source (Yahoo Finance)::

    python run_screener.py --provider yfinance

Offline run against local CSVs (e.g. the bundled sample data)::

    python run_screener.py --provider csv --csv-dir sample_data --index-file NIFTY

Common options::

    --limit 30            only the first N symbols (quick test)
    --full-only           print only FULL VCP SETUP stocks
    --min-passed 13       treat "near misses" >= N mandatory checks as watchlist
    --history-days 900    bhavcopy: how much history to backfill
    --output-dir output   where CSV + HTML reports are written
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

from vcp_screener.config import Config
from vcp_screener.report import print_summary, write_csv, write_html
from vcp_screener.screener import rank_results, run_screen
from vcp_screener.universe import load_universe


def build_provider(args):
    if args.provider == "csv":
        from vcp_screener.data import CSVProvider

        if not args.csv_dir:
            sys.exit("--csv-dir is required when --provider csv")
        return CSVProvider(args.csv_dir, index_file=args.index_file)

    if args.provider == "bhavcopy":
        from vcp_screener.bhavcopy import BhavcopyProvider

        return BhavcopyProvider(
            cache_dir=args.cache_dir or "cache/bhav",
            history_days=args.history_days,
            adjust_corporate_actions=not args.no_adjust,
            workers=args.workers,
        )

    from vcp_screener.data import YFinanceProvider

    return YFinanceProvider(period=args.period, cache_dir=args.cache_dir)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="VCP screener for the NSE F&O universe.")
    p.add_argument("--provider", choices=["bhavcopy", "yfinance", "csv"], default="bhavcopy",
                   help="data source (default: bhavcopy / official NSE EOD)")
    p.add_argument("--period", default="2y", help="yfinance history window (default: 2y)")
    p.add_argument("--history-days", type=int, default=900,
                   help="bhavcopy: calendar days of history to fetch (default: 900)")
    p.add_argument("--no-adjust", action="store_true",
                   help="bhavcopy: skip split/bonus back-adjustment")
    p.add_argument("--workers", type=int, default=6,
                   help="bhavcopy: parallel download workers (default: 6)")
    p.add_argument("--cache-dir", default=None,
                   help="cache directory (bhavcopy day-files / yfinance CSVs)")
    p.add_argument("--csv-dir", default=None, help="directory of per-symbol CSVs (csv provider)")
    p.add_argument("--index-file", default="NIFTY",
                   help="index CSV basename for csv provider (default: NIFTY)")
    p.add_argument("--universe-file", default=None,
                   help="file of symbols (one per line); default: built-in F&O list")
    p.add_argument("--limit", type=int, default=None, help="evaluate only first N symbols")
    p.add_argument("--min-passed", type=int, default=None,
                   help="watchlist: also list stocks passing >= N mandatory checks")
    p.add_argument("--full-only", action="store_true", help="console: only FULL VCP SETUP")
    p.add_argument("--output-dir", default="output", help="report output directory")
    p.add_argument("--index-symbol", default="^NSEI", help="index ticker (yfinance)")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    config = Config()

    symbols = load_universe(args.universe_file)
    if args.limit:
        symbols = symbols[: args.limit]

    print(f"Screening {len(symbols)} symbols via '{args.provider}' ...")
    provider = build_provider(args)
    results, market = run_screen(symbols, provider, config, index_symbol=args.index_symbol)

    ranked = rank_results(results, config)

    os.makedirs(args.output_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(args.output_dir, f"vcp_fno_{stamp}.csv")
    html_path = os.path.join(args.output_dir, f"vcp_fno_{stamp}.html")
    write_csv(ranked, config, csv_path)
    write_html(results, market, config, html_path, ranked=ranked)

    if args.full_only:
        full = [r for r in ranked if r.full_setup(config)]
        print(f"\nFULL VCP SETUP ({len(full)}):")
        for r in full:
            rs = f"{r.rs_rating:.0f}" if r.rs_rating is not None else "-"
            print(f"  ★ {r.symbol:<14} ₹{r.price:>9.2f}   RS {rs}")
    else:
        print_summary(ranked, market, config)

    if args.min_passed is not None:
        watch = [
            r for r in ranked
            if not r.error and not r.full_setup(config)
            and r.passed_count(config) >= args.min_passed
        ]
        if watch:
            print(f"\nWatchlist (>= {args.min_passed} mandatory checks, not yet FULL):")
            for r in watch:
                miss = [l for l in r.mandatory_labels(config) if not r.criteria.get(l)]
                print(f"  {r.symbol:<14} {r.passed_count(config)}/{r.total_mandatory(config)}"
                      f"  missing: {', '.join(miss)}")

    print(f"\nReports written:\n  {csv_path}\n  {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
