#!/usr/bin/env python3
"""CLI for the Indian sector & stock performance tool.

Examples:
    python run.py generate                 # fetch data -> output/sector_performance.json
    python run.py generate -o data.json    # custom output path
    python run.py show                      # print a summary table from the JSON
    python run.py show --sector it          # print one sector's stocks
    python run.py list                       # list all sectors and constituents
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
        return "    -  "
    return f"{v:+7.2f}"


def cmd_generate(args):
    generate_write(path=args.output, max_workers=args.workers, progress=not args.quiet)


def cmd_list(args):
    for sec in sectors_mod.all_sectors():
        print(f"\n{sec.name}  ({sec.nse_index})  [{len(sec.stocks)} stocks]")
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
        print(f"{sec['name']}  ({sec['nse_index']})")
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

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
