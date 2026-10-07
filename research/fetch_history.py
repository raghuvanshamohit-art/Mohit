#!/usr/bin/env python3
"""Download ~10 years of daily adjusted closes for every stock in the universe
(plus the Nifty 50 benchmark) into one wide CSV used by factor_study.py.

    python research/fetch_history.py            # -> research/cache/prices.csv
"""

from __future__ import annotations

import csv
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sector_stocks import sectors as sectors_mod  # noqa: E402
from sector_stocks.yahoo import YahooError, fetch_series  # noqa: E402

OUT = Path(__file__).resolve().parent / "cache" / "prices.csv"
BENCHMARK = "^NSEI"


def _fetch(symbol, yahoo_symbol):
    s = fetch_series(yahoo_symbol, rng="10y", interval="1d")
    days = [datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d") for t in s.timestamps]
    return symbol, dict(zip(days, s.closes))


def main():
    idx = sectors_mod.stock_index()
    jobs = {sym: st.yahoo_symbol for sym, st in idx.items()}
    jobs["NIFTY50"] = BENCHMARK
    data, failed = {}, []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(_fetch, s, y): s for s, y in jobs.items()}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                sym, series = f.result()
                data[sym] = series
            except YahooError as exc:
                failed.append(futs[f])
                print(f"  ! {exc}", file=sys.stderr)
            if i % 50 == 0:
                print(f"  {i}/{len(jobs)}", file=sys.stderr)

    dates = sorted({d for s in data.values() for d in s})
    cols = sorted(data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", *cols])
        for d in dates:
            w.writerow([d, *(data[c].get(d, "") for c in cols)])
    print(f"Wrote {OUT} ({len(dates)} days x {len(cols)} series; {len(failed)} failed)")


if __name__ == "__main__":
    main()
