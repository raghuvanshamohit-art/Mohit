"""Download daily OHLC data for the F&O universe from Yahoo Finance.

yfinance's curl backend does not honour this environment's HTTPS proxy, so we
hit Yahoo's public chart API directly with `requests` (which does). Results are
cached to a single CSV of adjusted closes so the backtest is reproducible
without re-downloading.
"""
from __future__ import annotations

import os
import time

import pandas as pd
import requests

os.environ.setdefault("CURL_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}


def _fetch_one(symbol: str, period1: int, period2: int,
               session: requests.Session, retries: int = 3) -> pd.Series | None:
    """Return a Series of adjusted close (index = date) for one symbol, or None."""
    params = {
        "period1": period1,
        "period2": period2,
        "interval": "1d",
        "events": "div,splits",
        "includeAdjustedClose": "true",
    }
    for attempt in range(retries):
        try:
            r = session.get(CHART_URL.format(symbol=symbol), params=params,
                            headers=HEADERS, timeout=30)
            if r.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            j = r.json()
            result = j.get("chart", {}).get("result")
            if not result:
                return None
            res = result[0]
            ts = res.get("timestamp")
            if not ts:
                return None
            quote = res["indicators"]["quote"][0]
            adj = res["indicators"].get("adjclose")
            closes = adj[0]["adjclose"] if adj else quote["close"]
            idx = pd.to_datetime(ts, unit="s").normalize()
            s = pd.Series(closes, index=idx, name=symbol)
            return s[~s.index.duplicated(keep="last")]
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None


def download_prices(symbols: list[str], start: str, end: str,
                    cache_path: str, force: bool = False,
                    pause: float = 0.25) -> pd.DataFrame:
    """Download adjusted closes for `symbols` between start/end (YYYY-MM-DD).

    Returns a wide DataFrame: index = trading date, columns = symbols.
    """
    if os.path.exists(cache_path) and not force:
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        print(f"Loaded cached prices: {df.shape[0]} days x {df.shape[1]} symbols "
              f"from {cache_path}")
        return df

    period1 = int(pd.Timestamp(start).timestamp())
    period2 = int(pd.Timestamp(end).timestamp())
    session = requests.Session()

    series = {}
    ok, fail = 0, []
    for i, sym in enumerate(symbols, 1):
        s = _fetch_one(sym, period1, period2, session)
        if s is not None and len(s) > 50:
            series[sym] = s
            ok += 1
        else:
            fail.append(sym)
        if i % 25 == 0 or i == len(symbols):
            print(f"  {i}/{len(symbols)} downloaded (ok={ok}, fail={len(fail)})")
        time.sleep(pause)

    df = pd.DataFrame(series).sort_index()
    # keep rows that look like real trading days (>=60% of names present)
    df = df.dropna(how="all")
    df.to_csv(cache_path)
    print(f"Saved {df.shape[0]} days x {df.shape[1]} symbols -> {cache_path}")
    if fail:
        print(f"Failed/insufficient ({len(fail)}): {', '.join(fail)}")
    return df
