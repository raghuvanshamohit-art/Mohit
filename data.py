"""
Data acquisition for the Nifty Next 50 momentum backtest.

Two sources, both hit directly with a browser User-Agent (the pre-installed
yfinance/curl_cffi stack does not honour the sandbox proxy CA reliably here):

  1. NSE  -> current Nifty Next 50 constituent list.
  2. Yahoo Finance chart API -> ~20 years of split/dividend-adjusted daily
     closes per constituent.

Raw responses are cached under results/cache/ so re-runs are offline and cheap.
"""

from __future__ import annotations

import io
import json
import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CA_BUNDLE = os.environ.get("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
if not os.path.exists(CA_BUNDLE):
    CA_BUNDLE = True  # fall back to certifi / system trust store off-sandbox

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept": "application/json, text/csv, */*"}

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, "results", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

NSE_NEXT50_CSV = (
    "https://nsearchives.nseindia.com/content/indices/ind_niftynext50list.csv"
)

# Fallback universe (Nifty Next 50 constituents, 2024/25 reconstitution) used
# only if NSE is unreachable. Symbols are NSE tickers; ".NS" is added for Yahoo.
FALLBACK_NEXT50 = [
    "ABB", "ADANIENSOL", "ADANIGREEN", "ADANIPOWER", "AMBUJACEM", "DMART",
    "BAJAJHLDNG", "BANKBARODA", "BPCL", "BOSCHLTD", "BRITANNIA", "CGPOWER",
    "CHOLAFIN", "COLPAL", "DABUR", "DIVISLAB", "DLF", "GAIL", "GODREJCP",
    "HAVELLS", "HAL", "HINDPETRO", "ICICIGI", "ICICIPRULI", "INDHOTEL",
    "INDIGO", "IOC", "IRFC", "JINDALSTEL", "JSWENERGY", "LTIM", "LODHA",
    "MARICO", "PIDILITIND", "PFC", "PNB", "RECLTD", "MOTHERSON", "SHREECEM",
    "SIEMENS", "SBICARD", "TATAPOWER", "TORNTPHARM", "TVSMOTOR", "UNITDSPR",
    "VBL", "VEDL", "ZOMATO", "ZYDUSLIFE", "GODREJPROP",
]


# ---------------------------------------------------------------------------
# Universe
# ---------------------------------------------------------------------------
def get_universe(refresh: bool = False) -> pd.DataFrame:
    """Return the current Nifty Next 50 constituents as a DataFrame."""
    cache = os.path.join(CACHE_DIR, "universe.csv")
    if os.path.exists(cache) and not refresh:
        return pd.read_csv(cache)

    try:
        r = requests.get(NSE_NEXT50_CSV, headers=HEADERS, verify=CA_BUNDLE, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = [c.strip() for c in df.columns]
        df = df.rename(columns={"Company Name": "name", "Symbol": "symbol",
                                "Industry": "industry"})
        df = df[["symbol", "name", "industry"]].dropna(subset=["symbol"])
        df["symbol"] = df["symbol"].str.strip()
        print(f"[universe] fetched {len(df)} constituents from NSE")
    except Exception as e:  # pragma: no cover - network fallback
        print(f"[universe] NSE fetch failed ({e!r}); using fallback list")
        df = pd.DataFrame({"symbol": FALLBACK_NEXT50})
        df["name"] = df["symbol"]
        df["industry"] = ""

    df.to_csv(cache, index=False)
    return df


# ---------------------------------------------------------------------------
# Prices
# ---------------------------------------------------------------------------
def _fetch_chart_json(yahoo_symbol: str, years: int) -> dict | None:
    cache = os.path.join(CACHE_DIR, f"{yahoo_symbol}.json")
    if os.path.exists(cache):
        with open(cache) as f:
            return json.load(f)

    now = int(datetime.now(timezone.utc).timestamp())
    period1 = now - int(years * 366 * 24 * 3600)
    url = (
        f"https://query2.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
        f"?period1={period1}&period2={now}&interval=1d&events=div,split"
    )
    for attempt in range(4):
        try:
            r = requests.get(url, headers=HEADERS, verify=CA_BUNDLE, timeout=30)
            if r.status_code == 200 and r.text.strip().startswith("{"):
                data = r.json()
                with open(cache, "w") as f:
                    json.dump(data, f)
                return data
        except Exception as e:  # pragma: no cover
            print(f"  [{yahoo_symbol}] attempt {attempt+1} error: {e!r}")
        time.sleep(1.5 * (attempt + 1))
    print(f"  [{yahoo_symbol}] failed after retries")
    return None


def _chart_to_series(data: dict) -> pd.Series | None:
    """Extract an adjusted-close series from a Yahoo chart JSON payload."""
    try:
        res = data["chart"]["result"][0]
        ts = res["timestamp"]
        idx = pd.to_datetime(ts, unit="s", utc=True).tz_convert("Asia/Kolkata").normalize()
        idx = idx.tz_localize(None)
        adj = res.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose")
        if adj is None:
            adj = res["indicators"]["quote"][0]["close"]
        s = pd.Series(adj, index=idx, dtype="float64").dropna()
        s = s[~s.index.duplicated(keep="last")]
        return s
    except (KeyError, IndexError, TypeError):
        return None


def build_price_panel(symbols: list[str], years: int = 21,
                      refresh: bool = False) -> pd.DataFrame:
    """
    Return a wide DataFrame of adjusted daily closes:
    index = trading day, columns = NSE symbol.
    """
    cache = os.path.join(CACHE_DIR, "prices.parquet")
    if os.path.exists(cache) and not refresh:
        try:
            return pd.read_parquet(cache)
        except Exception:
            pass

    series = {}
    for i, sym in enumerate(symbols, 1):
        data = _fetch_chart_json(f"{sym}.NS", years)
        if data is None:
            continue
        s = _chart_to_series(data)
        if s is not None and len(s) > 60:
            series[sym] = s
            print(f"[{i}/{len(symbols)}] {sym}: {len(s)} days "
                  f"({s.index.min().date()} -> {s.index.max().date()})")
        else:
            print(f"[{i}/{len(symbols)}] {sym}: insufficient data")
        time.sleep(0.4)

    panel = pd.DataFrame(series).sort_index()
    try:
        panel.to_parquet(cache)
    except Exception:
        panel.to_csv(os.path.join(CACHE_DIR, "prices.csv"))
    return panel


def fetch_benchmark(symbol: str = "^NSEI", years: int = 21) -> pd.Series | None:
    """Fetch a benchmark index series (default Nifty 50, ^NSEI)."""
    data = _fetch_chart_json(symbol, years)
    if data is None:
        return None
    return _chart_to_series(data)


if __name__ == "__main__":
    uni = get_universe()
    syms = uni["symbol"].tolist()
    print(f"Universe: {len(syms)} symbols")
    panel = build_price_panel(syms, years=21, refresh=True)
    print(f"\nPrice panel: {panel.shape[0]} rows x {panel.shape[1]} tickers")
    print(f"Date range: {panel.index.min().date()} -> {panel.index.max().date()}")
    bench = fetch_benchmark()
    if bench is not None:
        print(f"Benchmark ^NSEI: {len(bench)} days")
