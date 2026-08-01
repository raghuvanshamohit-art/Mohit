#!/usr/bin/env python3
"""
Fetch NIFTY 50 spot (^NSEI) and India VIX (^INDIAVIX) daily closes from Yahoo
Finance and write a combined CSV for the straddle backtest.

Output CSV columns: date,nifty_close,india_vix

Standard library only. Respects HTTPS_PROXY and common CA-bundle env vars
(SSL_CERT_FILE / REQUESTS_CA_BUNDLE), so it works behind a corporate/agent proxy.

Usage:
    python3 fetch_nifty_vix.py                     # 10y -> data/nifty_vix_daily.csv
    python3 fetch_nifty_vix.py --range 5y --out mydata.csv
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import ssl
import urllib.request

CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval=1d"


def _ssl_context() -> ssl.SSLContext:
    for var in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE"):
        p = os.environ.get(var)
        if p and os.path.exists(p):
            return ssl.create_default_context(cafile=p)
    for p in ("/root/.ccr/ca-bundle.crt",):
        if os.path.exists(p):
            return ssl.create_default_context(cafile=p)
    return ssl.create_default_context()


def _fetch(symbol: str, rng: str) -> dict[str, float]:
    url = CHART.format(sym=urllib.request.quote(symbol), rng=rng)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60, context=_ssl_context()) as r:
        data = json.load(r)
    res = data["chart"]["result"][0]
    ts = res["timestamp"]
    closes = res["indicators"]["quote"][0]["close"]
    out: dict[str, float] = {}
    for t, c in zip(ts, closes):
        if c is None:
            continue
        out[dt.datetime.utcfromtimestamp(t).date().isoformat()] = round(float(c), 2)
    return out


def main() -> None:
    here = __file__.rsplit("/", 1)[0]
    p = argparse.ArgumentParser(description="Fetch NIFTY + India VIX daily to CSV.")
    p.add_argument("--range", default="10y", help="Yahoo range: 5y, 10y, max ... (default 10y)")
    p.add_argument("--out", default=f"{here}/data/nifty_vix_daily.csv")
    args = p.parse_args()

    print(f"Fetching ^NSEI and ^INDIAVIX ({args.range}) ...")
    nse = _fetch("^NSEI", args.range)
    vix = _fetch("^INDIAVIX", args.range)

    days = sorted(set(nse) | set(vix))
    rows: list[tuple[str, float, float]] = []
    last_n = last_v = None
    for day in days:
        n = nse.get(day, last_n)
        v = vix.get(day, last_v)
        if n is None or v is None:
            continue
        last_n, last_v = n, v
        rows.append((day, n, v))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "nifty_close", "india_vix"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.out}  ({rows[0][0]} -> {rows[-1][0]})")


if __name__ == "__main__":
    main()
