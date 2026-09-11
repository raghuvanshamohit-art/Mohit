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
from strategy import allocation, pyramid, valuation

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


def _pct(x):
    return "-" if x is None else f"{x * 100:.1f}%"


def _parse_kv(pairs, as_pct=False):
    """Parse ['equity=600000', 'gold=150000'] into {'equity': 600000.0, ...}."""
    out = {}
    for item in pairs or []:
        if "=" not in item:
            print(f"Expected key=value, got '{item}'", file=sys.stderr)
            sys.exit(1)
        key, val = item.split("=", 1)
        try:
            out[key.strip().lower()] = float(val)
        except ValueError:
            print(f"'{val}' is not a number (in '{item}')", file=sys.stderr)
            sys.exit(1)
    return out


def cmd_value(args):
    price = args.price
    currency = ""
    if args.symbol and price is None:
        from sector_stocks.yahoo import YahooError, fetch_series
        try:
            series = fetch_series(args.symbol)
            price = round(series.closes[-1], 2)
            currency = series.currency
            print(f"Live price for {args.symbol}: {price} {currency} "
                  f"(as of latest close)\n")
        except YahooError as exc:
            print(f"Could not fetch {args.symbol}: {exc}\n"
                  f"Pass --price to value it anyway.", file=sys.stderr)
            sys.exit(1)

    discount = args.discount
    if discount is None:
        if args.bond_yield is None:
            print("Provide --discount, or --bond-yield (plus optional --erp).",
                  file=sys.stderr)
            sys.exit(1)
        discount = valuation.required_return(args.bond_yield, args.erp)
        print(f"Discount rate = {args.bond_yield:.1%} bond yield + "
              f"{args.erp:.1%} risk premium = {discount:.1%}\n")

    stages = [valuation.Stage(args.growth, args.years)]
    if args.growth2 is not None and args.years2:
        stages.append(valuation.Stage(args.growth2, args.years2))

    v = valuation.value_stock(args.eps, stages, args.terminal, discount, price)

    sym = f" {currency}".rstrip()
    print(f"Intrinsic value: {v.intrinsic_value:.2f}{sym} / share")
    print(f"  from explicit cash flows : {v.pv_explicit:.2f}")
    print(f"  from terminal value      : {v.pv_terminal:.2f} "
          f"({v.terminal_share:.0%} of value)")
    stage_desc = ", ".join(f"{s.growth:+.0%}×{s.years}y" for s in stages)
    print(f"  assumptions: base={args.eps}, stages=[{stage_desc}], "
          f"terminal={args.terminal:+.0%}, discount={discount:.1%}")
    if price is not None:
        print(f"\nPrice: {price:.2f}{sym}")
        print(f"Margin of safety: {v.margin_of_safety * 100:+.1f}%")
        print(f"Verdict: {v.verdict}")

    if args.implied and price is not None:
        g = valuation.implied_growth(args.eps, price, args.years, args.terminal, discount)
        if g is None:
            print("\nImplied growth: price is outside this model's range "
                  "(below no-growth value, or above what ~100% growth justifies).")
        else:
            print(f"\nImplied stage-1 growth priced in: {g * 100:.1f}% for "
                  f"{args.years}y — is that realistic and sustainable?")


def _print_actions(actions, currency=""):
    cur = f" {currency}".rstrip()
    print(f"{'ASSET':<10}{'ACTION':<7}{'AMOUNT' + cur:>16}{'NOW':>9}{'TARGET':>9}{'DRIFT':>9}")
    print("-" * 60)
    for a in actions:
        amt = f"{a.amount:,.0f}" if a.amount else "-"
        print(f"{a.asset:<10}{a.side:<7}{amt:>16}"
              f"{_pct(a.current_weight):>9}{_pct(a.target_weight):>9}"
              f"{_pct(a.drift):>9}")


def cmd_rebalance(args):
    holdings = _parse_kv(args.holding)
    if not holdings:
        print("Give at least one --holding, e.g. --holding equity=600000",
              file=sys.stderr)
        sys.exit(1)

    if args.target:
        targets = allocation.normalize(_parse_kv(args.target))
    else:
        if args.profile not in allocation.PROFILES:
            print(f"Unknown profile '{args.profile}'. Choose from "
                  f"{', '.join(allocation.PROFILES)}.", file=sys.stderr)
            sys.exit(1)
        targets = allocation.PROFILES[args.profile]

    if args.years_to_goal is not None:
        targets = allocation.glide_targets(targets, args.years_to_goal)
        print(f"Glide path applied for {args.years_to_goal:g} years to goal.")

    total = sum(holdings.values())
    print(f"Portfolio: {total:,.0f}   Target mix: "
          f"{', '.join(f'{k} {v:.0%}' for k, v in targets.items())}\n")

    if args.new_money:
        print(f"Directing new money ({args.new_money:,.0f}) to the most "
              f"underweight sleeves (no selling):\n")
        actions = allocation.invest_new_money(holdings, targets, args.new_money)
    else:
        print(f"Rebalance to target (tolerance band ±{args.band:.0%}):\n")
        actions = allocation.rebalance(holdings, targets, args.band)
    _print_actions(actions)


def cmd_pyramid(args):
    plan = pyramid.pyramid_plan(
        entry_price=args.entry,
        intrinsic_value=args.intrinsic,
        budget=args.budget,
        tranches=args.tranches,
        step=args.step,
        decay=args.decay,
        stop_loss=args.stop,
        cap=args.cap,
    )
    print(f"Entry {args.entry:g} | intrinsic {args.intrinsic:g} | "
          f"budget {args.budget:,.0f} | stop-loss {args.stop:.0%} off avg cost")
    print(f"{plan.note}\n")
    if not plan.rungs:
        return
    print(f"{'#':>2}{'PRICE':>10}{'BUY':>13}{'SHARES':>11}"
          f"{'CUM COST':>13}{'AVG COST':>10}{'STOP':>9}")
    print("-" * 68)
    for r in plan.rungs:
        print(f"{r.n:>2}{r.price:>10.2f}{r.amount:>13,.0f}{r.shares:>11.2f}"
              f"{r.cum_cost:>13,.0f}{r.avg_cost:>10.2f}{r.stop_price:>9.2f}")
    print("-" * 68)
    print(f"Deployed {plan.deployed:,.0f} of {plan.budget:,.0f} "
          f"(uninvested {plan.uninvested:,.0f}) | "
          f"final avg cost {plan.final_avg_cost:.2f} | "
          f"avg-cost margin of safety {plan.avg_cost_mos * 100:+.1f}%")


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

    # --- strategy engines -------------------------------------------------
    v = sub.add_parser("value", help="intrinsic value + margin of safety (DCF)")
    v.add_argument("--eps", type=float, required=True,
                   help="current per-share cash flow (EPS or FCF/share)")
    v.add_argument("--growth", type=float, required=True,
                   help="stage-1 growth, decimal (0.15 = 15%%)")
    v.add_argument("--years", type=int, default=10, help="stage-1 years (default 10)")
    v.add_argument("--growth2", type=float, help="optional stage-2 growth, decimal")
    v.add_argument("--years2", type=int, help="optional stage-2 years")
    v.add_argument("--terminal", type=float, default=0.04,
                   help="terminal growth, decimal (default 0.04)")
    v.add_argument("--discount", type=float,
                   help="discount rate, decimal; or derive it from --bond-yield")
    v.add_argument("--bond-yield", type=float, dest="bond_yield",
                   help="risk-free (10Y G-sec) yield, decimal")
    v.add_argument("--erp", type=float, default=0.05,
                   help="equity risk premium added to bond yield (default 0.05)")
    v.add_argument("--price", type=float, help="current price; else pass --symbol")
    v.add_argument("--symbol", help="Yahoo symbol to fetch a live price (e.g. TCS.NS)")
    v.add_argument("--implied", action="store_true",
                   help="also show the growth the current price bakes in")
    v.set_defaults(func=cmd_value)

    r = sub.add_parser("rebalance", help="which asset to sell / buy")
    r.add_argument("--holding", action="append", metavar="ASSET=VALUE",
                   help="current value of a sleeve (repeatable)")
    r.add_argument("--profile", default="balanced",
                   help="target mix: aggressive / balanced / conservative")
    r.add_argument("--target", action="append", metavar="ASSET=WEIGHT",
                   help="custom target weight (repeatable); overrides --profile")
    r.add_argument("--band", type=float, default=0.05,
                   help="drift tolerance before acting, decimal (default 0.05)")
    r.add_argument("--new-money", type=float, dest="new_money",
                   help="allocate this much fresh cash to underweights (no selling)")
    r.add_argument("--years-to-goal", type=float, dest="years_to_goal",
                   help="apply the equity→bond glide path for this horizon")
    r.set_defaults(func=cmd_rebalance)

    y = sub.add_parser("pyramid", help="how to add to a winner on the way up")
    y.add_argument("--entry", type=float, required=True, help="first buy price")
    y.add_argument("--intrinsic", type=float, required=True, help="fair value/share")
    y.add_argument("--budget", type=float, required=True, help="total capital for the position")
    y.add_argument("--tranches", type=int, default=5, help="number of rungs (default 5)")
    y.add_argument("--step", type=float, default=0.08,
                   help="price rise between rungs, decimal (default 0.08)")
    y.add_argument("--decay", type=float, default=0.65,
                   help="size multiplier per rung (default 0.65)")
    y.add_argument("--stop", type=float, default=0.15,
                   help="trailing stop below avg cost, decimal (default 0.15)")
    y.add_argument("--cap", type=float, default=1.0,
                   help="stop adding at cap×intrinsic (default 1.0)")
    y.set_defaults(func=cmd_pyramid)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
