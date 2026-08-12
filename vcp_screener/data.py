"""Data providers.

The screener only needs, per symbol, a daily OHLCV ``DataFrame`` indexed by
date with columns ``Open, High, Low, Close, Volume``. Two providers ship:

* :class:`YFinanceProvider` -- live NSE data from Yahoo Finance (needs internet).
* :class:`CSVProvider`      -- reads local CSVs, for offline runs and tests.

Both expose the same tiny interface::

    provider.get_index(symbol) -> DataFrame | None
    provider.get_many(symbols) -> dict[symbol, DataFrame]
"""

from __future__ import annotations

import os
import time
from typing import Dict, Iterable, List, Optional

import pandas as pd

_OHLCV = ["Open", "High", "Low", "Close", "Volume"]


def _normalise(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """Coerce a raw frame to a clean, date-indexed OHLCV frame."""
    if df is None or len(df) == 0:
        return None
    df = df.copy()
    # Flatten any column MultiIndex left over from a batch download.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["_".join(str(c) for c in tup if c != "") for tup in df.columns]
    rename = {c: c.title() for c in df.columns if c.title() in _OHLCV}
    df = df.rename(columns=rename)
    missing = [c for c in _OHLCV if c not in df.columns]
    if missing:
        return None
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()].sort_index()
    df = df[_OHLCV].apply(pd.to_numeric, errors="coerce")
    return df.dropna(subset=["Close"])


class CSVProvider:
    """Read per-symbol CSVs from a directory (``<SYMBOL>.csv``).

    Each CSV must have a ``Date`` column plus ``Open, High, Low, Close,
    Volume``. The index symbol is read from ``<index_file>.csv``.
    """

    def __init__(self, directory: str, index_file: str = "NIFTY"):
        self.directory = directory
        self.index_file = index_file

    def _read(self, name: str) -> Optional[pd.DataFrame]:
        path = os.path.join(self.directory, f"{name}.csv")
        if not os.path.exists(path):
            return None
        df = pd.read_csv(path)
        date_col = next((c for c in df.columns if c.lower() == "date"), None)
        if date_col is not None:
            df = df.set_index(date_col)
        return _normalise(df)

    def get_index(self, symbol: str = "^NSEI") -> Optional[pd.DataFrame]:
        return self._read(self.index_file)

    def get_many(self, symbols: Iterable[str]) -> Dict[str, Optional[pd.DataFrame]]:
        return {s: self._read(s) for s in symbols}


class YFinanceProvider:
    """Fetch daily OHLCV from Yahoo Finance for NSE symbols.

    Symbols get a ``.NS`` suffix; the Nifty 50 index is ``^NSEI``. Downloads
    are chunked and retried, and optionally cached to CSV so repeat runs are
    cheap and offline-friendly.
    """

    def __init__(
        self,
        period: str = "2y",
        suffix: str = ".NS",
        chunk_size: int = 40,
        max_retries: int = 3,
        pause: float = 1.0,
        cache_dir: Optional[str] = None,
    ):
        self.period = period
        self.suffix = suffix
        self.chunk_size = chunk_size
        self.max_retries = max_retries
        self.pause = pause
        self.cache_dir = cache_dir
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)

    # -- caching -----------------------------------------------------------
    def _cache_path(self, ticker: str) -> Optional[str]:
        if not self.cache_dir:
            return None
        return os.path.join(self.cache_dir, f"{ticker.replace('^', '_')}.csv")

    def _from_cache(self, ticker: str) -> Optional[pd.DataFrame]:
        path = self._cache_path(ticker)
        if path and os.path.exists(path):
            try:
                return _normalise(pd.read_csv(path, index_col=0, parse_dates=True))
            except Exception:
                return None
        return None

    def _to_cache(self, ticker: str, df: Optional[pd.DataFrame]) -> None:
        path = self._cache_path(ticker)
        if path and df is not None and not df.empty:
            df.to_csv(path)

    # -- downloads ---------------------------------------------------------
    def _download(self, tickers: List[str]) -> Dict[str, Optional[pd.DataFrame]]:
        import yfinance as yf  # imported lazily so offline use needs no install

        out: Dict[str, Optional[pd.DataFrame]] = {}
        for attempt in range(1, self.max_retries + 1):
            try:
                raw = yf.download(
                    tickers=tickers,
                    period=self.period,
                    interval="1d",
                    auto_adjust=True,
                    actions=False,
                    group_by="ticker",
                    threads=True,
                    progress=False,
                )
                break
            except Exception as exc:  # network / rate-limit hiccups
                if attempt == self.max_retries:
                    print(f"  ! download failed for chunk after {attempt} tries: {exc}")
                    return {t: None for t in tickers}
                time.sleep(self.pause * attempt)
        else:  # pragma: no cover
            return {t: None for t in tickers}

        for ticker in tickers:
            try:
                sub = raw[ticker] if len(tickers) > 1 else raw
            except (KeyError, TypeError):
                sub = None
            out[ticker] = _normalise(sub)
        return out

    def get_index(self, symbol: str = "^NSEI") -> Optional[pd.DataFrame]:
        cached = self._from_cache(symbol)
        if cached is not None:
            return cached
        df = self._download([symbol]).get(symbol)
        self._to_cache(symbol, df)
        return df

    def get_many(self, symbols: Iterable[str]) -> Dict[str, Optional[pd.DataFrame]]:
        symbols = list(symbols)
        result: Dict[str, Optional[pd.DataFrame]] = {}
        pending: List[str] = []

        # Serve from cache first.
        for sym in symbols:
            ticker = sym + self.suffix
            cached = self._from_cache(ticker)
            if cached is not None:
                result[sym] = cached
            else:
                pending.append(sym)

        for i in range(0, len(pending), self.chunk_size):
            chunk = pending[i:i + self.chunk_size]
            tickers = [s + self.suffix for s in chunk]
            print(f"  downloading {i + 1}-{i + len(chunk)} of {len(pending)} ...")
            downloaded = self._download(tickers)
            for sym, ticker in zip(chunk, tickers):
                df = downloaded.get(ticker)
                self._to_cache(ticker, df)
                result[sym] = df
            if i + self.chunk_size < len(pending):
                time.sleep(self.pause)

        return result
