#!/usr/bin/env python3
"""Generate synthetic OHLCV CSVs so the whole pipeline can run offline.

Creates a ``sample_data/`` directory with a Nifty proxy and a few stocks that
deliberately land in different states (a clean VCP setup, a base-building near
miss, and a downtrending laggard). Purely for demos and tests -- not real
market data.

    python tools/generate_sample_data.py --out sample_data
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd


def _ohlc_from_close(dates, close, vol, seed=0):
    rng = np.random.default_rng(seed)
    close = np.asarray(close, dtype=float)
    intraday = np.abs(rng.normal(0, 0.004, len(close))) * close
    high = close + intraday
    low = close - intraday
    open_ = np.concatenate([[close[0]], close[:-1]])
    return pd.DataFrame(
        {"Open": open_, "High": np.maximum(open_, high), "Low": np.minimum(open_, low),
         "Close": close, "Volume": np.asarray(vol, dtype=float)},
        index=dates,
    )


def _trend(n, start, drift, noise, seed):
    rng = np.random.default_rng(seed)
    steps = rng.normal(drift, noise, n)
    return start * np.exp(np.cumsum(steps))


def _winner(dates, start, drift, base_price, seed):
    """A strong uptrend that tightens into a low-volume contraction (a VCP)."""
    n = len(dates)
    close = _trend(n, base_price, drift, 0.010, seed=seed)
    tail = 60
    ramp = np.linspace(1.0, 0.15, tail)            # volatility shrinks into the pivot
    contraction = np.cumsum(np.random.default_rng(seed + 100).normal(0, 0.004, tail) * ramp)
    close[-tail:] = close[-tail - 1] * np.exp(contraction) * np.linspace(1.0, 1.04, tail)
    vol = np.concatenate([
        np.random.default_rng(seed + 200).normal(1_400_000, 120_000, n - tail),
        np.linspace(1_300_000, 450_000, tail),     # volume dries up
    ])
    return _ohlc_from_close(dates, close, np.abs(vol), seed=seed)


def make_series(n_days=600):
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n_days)
    out = {}

    # Nifty: steady uptrend.
    nifty_close = _trend(n_days, 18000, 0.0005, 0.006, seed=1)
    out["NIFTY"] = _ohlc_from_close(dates, nifty_close, np.full(n_days, 1.0), seed=1)

    # A spread of VCP winners with different trend strength (so the
    # cross-sectional RS Rating actually varies across the universe).
    winners = [
        ("WINSTOCK", 0.0020, 200),
        ("ALPHACORP", 0.0018, 320),
        ("MOMENTUMX", 0.0016, 150),
        ("BREAKOUTCO", 0.0015, 480),
        ("STEADYRISE", 0.0013, 90),
    ]
    for i, (name, drift, px) in enumerate(winners):
        out[name] = _winner(dates, 0, drift, px, seed=10 + i)

    # BUILDERs: uptrend but still extended / no clean contraction (near miss).
    for i, (name, drift, px) in enumerate(
        [("BUILDER", 0.0012, 150), ("CHOPPYTREND", 0.0010, 260), ("WIDERANGE", 0.0011, 130)]
    ):
        close = _trend(n_days, px, drift, 0.020, seed=30 + i)
        vol = np.random.default_rng(40 + i).normal(900_000, 200_000, n_days)
        out[name] = _ohlc_from_close(dates, close, np.abs(vol), seed=30 + i)

    # LAGGARDs: downtrends -> fail the trend-template checks.
    for i, (name, drift, px) in enumerate(
        [("LAGGARD", -0.0011, 400), ("FALLINGKNIFE", -0.0016, 220), ("DOWNBEAT", -0.0008, 310)]
    ):
        close = _trend(n_days, px, drift, 0.014, seed=50 + i)
        vol = np.random.default_rng(60 + i).normal(700_000, 150_000, n_days)
        out[name] = _ohlc_from_close(dates, close, np.abs(vol), seed=50 + i)

    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sample_data")
    ap.add_argument("--days", type=int, default=600)
    args = ap.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)
    series = make_series(args.days)
    for name, df in series.items():
        df.index.name = "Date"
        df.to_csv(os.path.join(args.out, f"{name}.csv"))
    # A universe file listing every non-index symbol, so the offline run is
    # reproducible straight from this script.
    symbols = sorted(n for n in series if n != "NIFTY")
    with open(os.path.join(args.out, "symbols.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(symbols) + "\n")
    print(f"wrote sample data ({len(symbols)} symbols + NIFTY) to {args.out}/")


if __name__ == "__main__":
    main()
