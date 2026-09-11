"""Minimal Yahoo Finance client (standard library only).

Fetches historical daily prices from the public Yahoo Finance chart endpoint.
No third-party dependencies are required, which keeps the tool runnable in any
Python 3.9+ environment.
"""

from __future__ import annotations

import gzip
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

_CHART_HOSTS = [
    "https://query1.finance.yahoo.com",
    "https://query2.finance.yahoo.com",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Encoding": "gzip",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class PriceSeries:
    symbol: str                 # Yahoo symbol, e.g. "RELIANCE.NS"
    currency: str
    long_name: str
    timestamps: list            # epoch seconds (UTC), ascending
    closes: list                # adjusted close (splits + dividends applied)

    def __len__(self):
        return len(self.timestamps)


class YahooError(Exception):
    pass


def _read_body(resp) -> bytes:
    raw = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
    return raw


def fetch_series(symbol: str, rng: str = "13mo", interval: str = "1d",
                 retries: int = 4, timeout: int = 25) -> PriceSeries:
    """Fetch an adjusted-close price series for a single Yahoo symbol.

    Retries transient failures (network errors, HTTP 429/5xx) with exponential
    backoff, and alternates between Yahoo's two query hosts.
    """
    params = urllib.parse.urlencode({
        "range": rng,
        "interval": interval,
        "events": "div,splits",
        "includeAdjustedClose": "true",
    })

    last_err = None
    for attempt in range(retries):
        host = _CHART_HOSTS[attempt % len(_CHART_HOSTS)]
        # Yahoo symbols may contain characters like "&" or "^".
        url = f"{host}/v8/finance/chart/{urllib.parse.quote(symbol)}?{params}"
        req = urllib.request.Request(url, headers=_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(_read_body(resp).decode("utf-8"))
            return _parse_chart(symbol, payload)
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            # 404 / 401 etc. are not going to recover on retry.
            raise YahooError(f"{symbol}: HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as exc:
            last_err = exc
            time.sleep(2 ** attempt)
            continue

    raise YahooError(f"{symbol}: failed after {retries} attempts ({last_err})")


def _parse_chart(symbol: str, payload: dict) -> PriceSeries:
    chart = payload.get("chart") or {}
    if chart.get("error"):
        raise YahooError(f"{symbol}: {chart['error']}")
    results = chart.get("result")
    if not results:
        raise YahooError(f"{symbol}: empty result")

    r = results[0]
    meta = r.get("meta", {})
    timestamps = r.get("timestamp") or []

    indicators = r.get("indicators", {})
    adj = None
    if indicators.get("adjclose"):
        adj = indicators["adjclose"][0].get("adjclose")
    quote = (indicators.get("quote") or [{}])[0]
    close = quote.get("close")

    series_close = adj if adj is not None else close
    if not timestamps or not series_close:
        raise YahooError(f"{symbol}: no price data")

    # Drop points where the close is null (holidays / bad ticks).
    ts_clean, px_clean = [], []
    for t, p in zip(timestamps, series_close):
        if p is not None:
            ts_clean.append(int(t))
            px_clean.append(float(p))
    if not px_clean:
        raise YahooError(f"{symbol}: all prices null")

    return PriceSeries(
        symbol=symbol,
        currency=meta.get("currency", ""),
        long_name=meta.get("longName") or meta.get("shortName") or "",
        timestamps=ts_clean,
        closes=px_clean,
    )
