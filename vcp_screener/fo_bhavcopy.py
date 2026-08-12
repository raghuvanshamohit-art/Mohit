"""NSE derivatives (F&O) bhavcopy provider -- daily option-chain snapshots.

Fetches the UDiFF F&O bhavcopy for a trading day and returns the stock-option
rows (``FinInstrmTp == 'STO'``) the options enrichment needs: expiry, strike,
CE/PE, settle price, open interest, volume and the underlying price.

The daily screener only needs the *latest* day; each day is cached locally.
"""

from __future__ import annotations

import io
import os
import zipfile
from datetime import date, timedelta
from typing import Optional, Tuple

import pandas as pd

ARCHIVE = "https://archives.nseindia.com"
_HEADERS = {"User-Agent": "Mozilla/5.0 (VCP-Screener/0.1)", "Accept": "*/*"}

_KEEP = {
    "TckrSymb": "Symbol", "XpryDt": "Expiry", "StrkPric": "Strike",
    "OptnTp": "OptType", "SttlmPric": "Settle", "ClsPric": "Close",
    "OpnIntrst": "OI", "TtlTradgVol": "Volume", "UndrlygPric": "Underlying",
    "NewBrdLotQty": "Lot",
}


class FOBhavcopyProvider:
    def __init__(self, cache_dir: str = "cache/fo", max_retries: int = 3, session=None):
        self.cache_dir = cache_dir
        self.max_retries = max_retries
        os.makedirs(cache_dir, exist_ok=True)
        self._session = session

    def _get(self, url: str):
        import requests
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(_HEADERS)
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._session.get(url, timeout=40)
                if resp.status_code == 404:
                    return None, True
                resp.raise_for_status()
                return resp.content, False
            except Exception:
                if attempt == self.max_retries:
                    return None, False
        return None, False

    @staticmethod
    def _url(d: date) -> str:
        return f"{ARCHIVE}/content/fo/BhavCopy_NSE_FO_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"

    def _cache_path(self, d: date) -> str:
        return os.path.join(self.cache_dir, f"fo_{d:%Y%m%d}.csv")

    def get_day(self, d: date) -> Optional[pd.DataFrame]:
        """Normalized stock-option rows for one day, or None (holiday/no data)."""
        path = self._cache_path(d)
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, parse_dates=["Expiry"])
            except Exception:
                return None
            return df if len(df) else None

        blob, absent = self._get(self._url(d))
        if blob is None:
            if absent:
                pd.DataFrame(columns=list(_KEEP.values())).to_csv(path, index=False)
            return None
        try:
            zf = zipfile.ZipFile(io.BytesIO(blob))
            name = next(n for n in zf.namelist() if n.lower().endswith(".csv"))
            raw = pd.read_csv(zf.open(name))
        except Exception:
            return None

        raw = raw[raw["FinInstrmTp"] == "STO"]
        if raw.empty:
            pd.DataFrame(columns=list(_KEEP.values())).to_csv(path, index=False)
            return None
        df = raw[list(_KEEP)].rename(columns=_KEEP).copy()
        df["Symbol"] = df["Symbol"].astype(str).str.strip()
        df["OptType"] = df["OptType"].astype(str).str.strip()
        for col in ("Strike", "Settle", "Close", "OI", "Volume", "Underlying", "Lot"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["Expiry"] = pd.to_datetime(df["Expiry"], errors="coerce")
        df = df.dropna(subset=["Strike", "Expiry"])
        df.to_csv(path, index=False)
        return df

    def latest_day(self, max_back: int = 7) -> Tuple[Optional[date], Optional[pd.DataFrame]]:
        """Return ``(date, chain_df)`` for the most recent available trading day."""
        d = date.today()
        for _ in range(max_back + 1):
            if d.weekday() < 5:                      # skip weekends outright
                df = self.get_day(d)
                if df is not None and len(df):
                    return d, df
            d -= timedelta(days=1)
        return None, None
