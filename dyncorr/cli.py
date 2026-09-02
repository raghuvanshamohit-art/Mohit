"""Command-line interface for dyncorr.

Examples
--------
List everything you can correlate::

    python -m dyncorr list-presets

Dynamic correlation of gold vs. rates vs. inflation (offline synthetic data)::

    python -m dyncorr run --params gold us_treasury_10y inflation \
        --method rolling --window 60 --outdir out

Try live data (needs network + yfinance / pandas-datareader)::

    python -m dyncorr run --params gold us_treasury_10y euro_treasury_10y \
        --source live --start 2018-01-01 --method ewma --halflife 30

Your own data::

    python -m dyncorr run --csv prices.csv --params SPX GOLD --window 90
"""

from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

from . import __version__
from .correlation import (
    correlation_summary,
    dynamic_correlation,
    matrix_as_of,
    static_correlation,
)
from .data import VALID_TRANSFORMS, build_panel
from .presets import PRESETS, resolve


def _parse_pairs(raw: list[str] | None):
    if not raw:
        return None
    pairs = []
    for item in raw:
        if "~" not in item:
            raise SystemExit(f"--pairs entry {item!r} must look like A~B")
        a, b = item.split("~", 1)
        pairs.append((a.strip(), b.strip()))
    return pairs


def cmd_list_presets(args: argparse.Namespace) -> int:
    width = max(len(k) for k in PRESETS)
    print(f"{'KEY'.ljust(width)}  SOURCE  TRANSFORM     DESCRIPTION")
    print("-" * (width + 48))
    for key, p in PRESETS.items():
        print(
            f"{key.ljust(width)}  {p.source.ljust(6)}  "
            f"{p.transform.ljust(12)}  {p.description}"
        )
    print(
        "\nUse any KEY (or a CSV column) with `run --params ...`. "
        "Aliases like `us_treasuries`, `bund`, `jgb`, `dxy` also work."
    )
    return 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    from .dashboard import DEFAULT_PARAMS, write_dashboard

    params = args.params or (DEFAULT_PARAMS if not args.csv else [])
    if not args.csv:
        unknown = [p for p in params if resolve(p) is None]
        if unknown:
            raise SystemExit(
                f"Unknown parameter(s): {unknown}. Run `list-presets`, "
                f"or load them from a CSV with --csv."
            )
    out = write_dashboard(
        args.out,
        params=params,
        source="csv" if args.csv else args.source,
        start=args.start, end=args.end, transform=args.transform,
        csv_path=args.csv, date_col=args.date_col, seed=args.seed,
    )
    print(f"dyncorr v{__version__}")
    print(f"Wrote interactive dashboard to {out}")
    print(f"Open it in a browser:  file://{os.path.abspath(out)}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    params = args.params or []
    if not params and not args.csv:
        raise SystemExit("Provide --params (and/or --csv). See `list-presets`.")

    # Warn about unknown names early (unless a CSV supplies the columns).
    if not args.csv:
        unknown = [p for p in params if resolve(p) is None]
        if unknown:
            raise SystemExit(
                f"Unknown parameter(s): {unknown}. Run `list-presets`, "
                f"or load them from a CSV with --csv."
            )

    panel = build_panel(
        params=params,
        source="csv" if args.csv else args.source,
        start=args.start,
        end=args.end,
        transform=args.transform,
        csv_path=args.csv,
        date_col=args.date_col,
        seed=args.seed,
    )

    df = panel.transformed
    if df.shape[1] < 2:
        raise SystemExit("Need at least two series to compute correlations.")
    if len(df) < 3:
        raise SystemExit(
            "Not enough overlapping observations after alignment/transform. "
            "Check date range or mixed data frequencies."
        )

    pairs = _parse_pairs(args.pairs)

    print(f"dyncorr v{__version__}")
    print(f"source={panel.source}  observations={len(df)}  "
          f"range={df.index.min().date()}..{df.index.max().date()}")
    print("series & transforms:")
    for col in df.columns:
        print(f"  - {col}: {panel.transforms[col]}")
    print()

    # Static (full-sample) matrix for reference.
    static = static_correlation(df, method=args.corr_method)
    print("Static (full-sample) correlation matrix:")
    print(static.round(2).to_string())
    print()

    # Dynamic correlation series.
    roll = dynamic_correlation(
        df, method=args.method, window=args.window,
        halflife=args.halflife, pairs=pairs,
    )
    summary = correlation_summary(roll)
    if not summary.empty:
        label = f"rolling (window={args.window})" if args.method == "rolling" \
            else f"ewma (halflife={args.halflife})"
        print(f"Dynamic correlation summary — {label}, "
              f"ranked by swing (max-min):")
        show = summary[["pair", "latest", "mean", "min", "max", "swing"]]
        print(show.round(3).to_string(index=False))
        print()

    # Current dynamic matrix (as of the last observation).
    current = matrix_as_of(
        df, method=args.method, window=args.window, halflife=args.halflife
    )

    # Outputs.
    os.makedirs(args.outdir, exist_ok=True)
    roll.to_csv(os.path.join(args.outdir, "dynamic_correlation.csv"))
    static.to_csv(os.path.join(args.outdir, "static_correlation.csv"))
    current.to_csv(os.path.join(args.outdir, "current_correlation_matrix.csv"))
    if not summary.empty:
        summary.to_csv(os.path.join(args.outdir, "summary.csv"), index=False)

    wrote = ["dynamic_correlation.csv", "static_correlation.csv",
             "current_correlation_matrix.csv", "summary.csv"]

    if not args.no_plots:
        try:
            from .plotting import plot_dynamic_correlation, plot_heatmap

            title = "Dynamic correlation — " + (
                f"rolling {args.window}-obs" if args.method == "rolling"
                else f"EWMA halflife={args.halflife}"
            )
            plot_dynamic_correlation(
                roll, title=title,
                path=os.path.join(args.outdir, "dynamic_correlation.png"),
            )
            plot_heatmap(
                current,
                title="Correlation as of "
                f"{df.index.max().date()} ({args.method})",
                path=os.path.join(args.outdir, "current_correlation_heatmap.png"),
            )
            wrote += ["dynamic_correlation.png", "current_correlation_heatmap.png"]
        except Exception as exc:  # pragma: no cover
            print(f"(plotting skipped: {exc})", file=sys.stderr)

    print(f"Wrote {len(wrote)} file(s) to {args.outdir}/:")
    for name in wrote:
        print(f"  - {name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dyncorr",
        description="Dynamic (time-varying) correlation between financial parameters.",
    )
    parser.add_argument("--version", action="version",
                        version=f"dyncorr {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-presets", help="list built-in parameters").set_defaults(
        func=cmd_list_presets
    )

    dash = sub.add_parser("dashboard", help="generate an interactive HTML dashboard")
    dash.add_argument("--params", nargs="+", default=[],
                      help="parameter keys/aliases, or CSV columns (default: a mix)")
    dash.add_argument("--source", choices=["synthetic", "live", "csv"],
                      default="synthetic")
    dash.add_argument("--csv", help="load level series from a wide CSV")
    dash.add_argument("--date-col", help="date column name in the CSV")
    dash.add_argument("--start", default="2019-01-01")
    dash.add_argument("--end", default="2024-12-31")
    dash.add_argument("--transform", default="auto",
                      choices=["auto", *sorted(VALID_TRANSFORMS)])
    dash.add_argument("--seed", type=int, default=7)
    dash.add_argument("--out", default="dashboard.html",
                      help="output HTML file (default: dashboard.html)")
    dash.set_defaults(func=cmd_dashboard)

    run = sub.add_parser("run", help="compute dynamic correlations")
    run.add_argument("--params", nargs="+", default=[],
                     help="parameter keys/aliases, or CSV columns")
    run.add_argument("--source", choices=["synthetic", "live", "csv"],
                     default="synthetic",
                     help="data source (default: synthetic/offline)")
    run.add_argument("--csv", help="load level series from a wide CSV")
    run.add_argument("--date-col", help="date column name in the CSV")
    run.add_argument("--start", default="2015-01-01")
    run.add_argument("--end", default="2024-12-31")
    run.add_argument("--transform", default="auto",
                     choices=["auto", *sorted(VALID_TRANSFORMS)],
                     help="per-series transform (default: auto = preset-recommended)")
    run.add_argument("--method", choices=["rolling", "ewma"], default="rolling",
                     help="dynamic estimator (default: rolling)")
    run.add_argument("--window", type=int, default=60,
                     help="rolling window length in observations (default: 60)")
    run.add_argument("--halflife", type=float, default=30.0,
                     help="EWMA halflife in observations (default: 30)")
    run.add_argument("--corr-method", choices=["pearson", "spearman", "kendall"],
                     default="pearson", help="static matrix method")
    run.add_argument("--pairs", nargs="+",
                     help="restrict to specific pairs, e.g. gold~us_treasury_10y")
    run.add_argument("--outdir", default="dyncorr_out",
                     help="output directory (default: dyncorr_out)")
    run.add_argument("--no-plots", action="store_true", help="skip PNG plots")
    run.add_argument("--seed", type=int, default=7,
                     help="RNG seed for synthetic data")
    run.set_defaults(func=cmd_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
