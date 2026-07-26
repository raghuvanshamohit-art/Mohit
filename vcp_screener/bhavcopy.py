"""NSE Bhavcopy provider -- official, free End-Of-Day data.

NSE publishes a daily "bhavcopy": one file per trading day containing OHLCV for
every stock. This provider downloads those day-files, caches each one locally
(so a backfill happens once and daily runs only fetch new days), then stacks
them into the per-symbol OHLCV frames the screener needs.

It understands both file layouts NSE has used:

* the current **UDiFF** common bhavcopy
  ``.../content/cm/BhavCopy_NSE_CM_0_0_0_<YYYYMMDD>_F_0000.csv.zip``
* the **legacy** equities bhavcopy
  ``.../content/historical/EQUITIES/<YYYY>/<MMM>/cm<DDMMMYYYY>bhav.csv.zip``

The Nifty 50 index comes from the daily indices close file
``.../content/indices/ind_close_all_<DDMMYYYY>.csv``.

Bhavcopy prices are *unadjusted*. On an ex-date NSE reports an adjusted previous
close, so splits/bonuses are back-adjusted here from that reported prev-close
(see :func:`_back_adjust`) -- keeping traded value (price x volume) intact.
"""

from __future__ import annotations

import io
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

ARCHIVE = "https://archives.nseindia.com"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) VCP-Screener/0.1",
    "Accept": "*/*",
}

# Column-name variants across the UDiFF / legacy layouts.
_COLMAP = {
    "symbol": ["TckrSymb", "SYMBOL"],
    "series": ["SctySrs", "SERIES"],
    "open": ["OpnPric", "OPEN"],
    "high": ["HghPric", "HIGH"],
    "low": ["LwPric", "LOW"],
    "close": ["ClsPric", "CLOSE"],
    "prevclose": ["PrvsClsgPric", "PREVCLOSE"],
    "volume": ["TtlTradgVol", "TOTTRDQTY"],
}


def _pick(df: pd.DataFrame, names: List[str]) -> Optional[str]:
    lookup = {c.strip().lower(): c for c in df.columns}
    for name in names:
        if name.strip().lower() in lookup:
            return lookup[name.strip().lower()]
    return None


class BhavcopyProvider:
    def __init__(
        self,
        cache_dir: str = "cache/bhav",
        history_days: int = 900,
        series: Iterable[str] = ("EQ", "BE"),
        adjust_corporate_actions: bool = True,
        ca_min_gap: float = 0.10,
        workers: int = 6,
        max_retries: int = 3,
        session=None,
    ):
        self.cache_dir = cache_dir
        self.history_days = history_days
        self.series = tuple(series)
        self.adjust = adjust_corporate_actions
        self.ca_min_gap = ca_min_gap
        self.workers = max(1, workers)
        self.max_retries = max_retries
        os.makedirs(cache_dir, exist_ok=True)
        self._session = session  # lazily created requests.Session
        self._cm_cache: Dict[date, Optional[pd.DataFrame]] = {}
        self._idx_cache: Dict[date, Optional[pd.Series]] = {}

    # -- HTTP --------------------------------------------------------------
    def _get(self, url: str) -> Optional[bytes]:
        import requests

        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(_HEADERS)
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._session.get(url, timeout=30)
                if resp.status_code == 404:
                    return None  # no trading that day / file absent
                resp.raise_for_status()
                return resp.content
            except Exception:
                if attempt == self.max_retries:
                    return None
        return None

    @staticmethod
    def _read_zip_csv(blob: bytes) -> Optional[pd.DataFrame]:
        try:
            zf = zipfile.ZipFile(io.BytesIO(blob))
        except zipfile.BadZipFile:
            return None
        name = next((n for n in zf.namelist() if n.lower().endswith(".csv")), None)
        if not name:
            return None
        with zf.open(name) as fh:
            return pd.read_csv(fh)

    # -- URLs --------------------------------------------------------------
    @staticmethod
    def _cm_urls(d: date) -> List[str]:
        # Current UDiFF common bhavcopy, tried first.
        udiff = f"{ARCHIVE}/content/cm/BhavCopy_NSE_CM_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"
        # Legacy equities bhavcopy (e.g. .../2024/JUN/cm28JUN2024bhav.csv.zip).
        legacy = (
            f"{ARCHIVE}/content/historical/EQUITIES/"
            f"{d.year}/{d.strftime('%b').upper()}/"
            f"cm{d.strftime('%d%b%Y').upper()}bhav.csv.zip"
        )
        return [udiff, legacy]

    @staticmethod
    def _index_url(d: date) -> str:
        return f"{ARCHIVE}/content/indices/ind_close_all_{d:%d%m%Y}.csv"

    # -- per-day CM bhavcopy ----------------------------------------------
    def _cm_cache_path(self, d: date) -> str:
        return os.path.join(self.cache_dir, f"cm_{d:%Y%m%d}.csv")

    def _fetch_cm_day(self, d: date) -> Optional[pd.DataFrame]:
        """Return a normalized frame for one day, or None (holiday/no data)."""
        path = self._cm_cache_path(d)
        if os.path.exists(path):
            df = pd.read_csv(path)
            return df if len(df) else None

        raw = None
        for url in self._cm_urls(d):
            blob = self._get(url)
            if blob is not None:
                raw = self._read_zip_csv(blob)
                if raw is not None and len(raw):
                    break
        norm = self._normalize_cm(raw, d)
        # Cache even an empty frame (as a marker) so holidays aren't refetched.
        (norm if norm is not None else pd.DataFrame(
            columns=["Date", "Symbol", "Open", "High", "Low", "Close", "PrevClose", "Volume"]
        )).to_csv(path, index=False)
        return norm

    def _normalize_cm(self, raw: Optional[pd.DataFrame], d: date) -> Optional[pd.DataFrame]:
        if raw is None or len(raw) == 0:
            return None
        cols = {k: _pick(raw, v) for k, v in _COLMAP.items()}
        if not all(cols[k] for k in ("symbol", "open", "high", "low", "close", "volume")):
            return None
        df = pd.DataFrame({
            "Symbol": raw[cols["symbol"]].astype(str).str.strip(),
            "Series": raw[cols["series"]].astype(str).str.strip() if cols["series"] else "EQ",
            "Open": pd.to_numeric(raw[cols["open"]], errors="coerce"),
            "High": pd.to_numeric(raw[cols["high"]], errors="coerce"),
            "Low": pd.to_numeric(raw[cols["low"]], errors="coerce"),
            "Close": pd.to_numeric(raw[cols["close"]], errors="coerce"),
            "PrevClose": pd.to_numeric(raw[cols["prevclose"]], errors="coerce")
            if cols["prevclose"] else np.nan,
            "Volume": pd.to_numeric(raw[cols["volume"]], errors="coerce"),
        })
        df = df[df["Series"].isin(self.series)]
        df = df.dropna(subset=["Close"])
        df.insert(0, "Date", pd.Timestamp(d))
        return df.reset_index(drop=True)

    # -- per-day index -----------------------------------------------------
    def _idx_cache_path(self, d: date) -> str:
        return os.path.join(self.cache_dir, f"idx_{d:%Y%m%d}.csv")

    def _fetch_index_day(self, d: date) -> Optional[pd.Series]:
        path = self._idx_cache_path(d)
        if os.path.exists(path):
            df = pd.read_csv(path)
            return df.iloc[0] if len(df) else None

        raw = None
        blob = self._get(self._index_url(d))
        if blob is not None:
            try:
                raw = pd.read_csv(io.BytesIO(blob))
            except Exception:
                raw = None
        row = self._normalize_index(raw, d)
        (pd.DataFrame([row]) if row is not None else pd.DataFrame()).to_csv(path, index=False)
        return pd.Series(row) if row is not None else None

    @staticmethod
    def _normalize_index(raw: Optional[pd.DataFrame], d: date, index_name: str = "Nifty 50"):
        if raw is None or len(raw) == 0:
            return None
        name_col = _pick(raw, ["Index Name", "IndexName"])
        if name_col is None:
            return None
        mask = raw[name_col].astype(str).str.strip().str.lower() == index_name.lower()
        sub = raw[mask]
        if sub.empty:
            return None
        r = sub.iloc[0]

        def num(names):
            c = _pick(raw, names)
            return float(pd.to_numeric(r[c], errors="coerce")) if c else np.nan

        return {
            "Date": pd.Timestamp(d),
            "Open": num(["Open Index Value", "Open"]),
            "High": num(["High Index Value", "High"]),
            "Low": num(["Low Index Value", "Low"]),
            "Close": num(["Closing Index Value", "Close"]),
            "Volume": num(["Volume"]),
        }

    # -- trading calendar --------------------------------------------------
    def _date_range(self) -> List[date]:
        end = date.today()
        start = end - timedelta(days=self.history_days)
        days = pd.bdate_range(start=start, end=end)  # Mon-Fri; holidays 404 and are skipped
        return [dt.date() for dt in days]

    def _missing_days(self, days: List[date]) -> List[date]:
        return [d for d in days if not os.path.exists(self._cm_cache_path(d))]

    def _prefetch(self, days: List[date]) -> None:
        missing = self._missing_days(days)
        if not missing:
            return
        print(f"  bhavcopy: fetching {len(missing)} missing day(s) "
              f"(cached: {len(days) - len(missing)}) ...")
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            list(pool.map(self._fetch_cm_day, missing))
            list(pool.map(self._fetch_index_day, missing))

    # -- public interface --------------------------------------------------
    def get_index(self, symbol: str = "^NSEI") -> Optional[pd.DataFrame]:
        days = self._date_range()
        self._prefetch(days)
        rows = []
        for d in days:
            s = self._fetch_index_day(d)
            if s is not None and pd.notna(s.get("Close")):
                rows.append(s)
        if not rows:
            return None
        df = pd.DataFrame(rows)
        df["Date"] = pd.to_datetime(df["Date"])
        return df.set_index("Date").sort_index()[["Open", "High", "Low", "Close", "Volume"]]

    def get_many(self, symbols: Iterable[str]) -> Dict[str, Optional[pd.DataFrame]]:
        symbols = [s.upper() for s in symbols]
        wanted = set(symbols)
        days = self._date_range()
        self._prefetch(days)

        frames = []
        for d in days:
            day = self._fetch_cm_day(d)
            if day is not None and len(day):
                frames.append(day[day["Symbol"].isin(wanted)])
        if not frames:
            return {s: None for s in symbols}

        allrows = pd.concat(frames, ignore_index=True)
        allrows["Date"] = pd.to_datetime(allrows["Date"])

        out: Dict[str, Optional[pd.DataFrame]] = {}
        for sym, g in allrows.groupby("Symbol"):
            g = g.sort_values("Date").set_index("Date")
            g = g[["Open", "High", "Low", "Close", "PrevClose", "Volume"]]
            g = g[~g.index.duplicated(keep="last")]
            if self.adjust:
                g = _back_adjust(g, self.ca_min_gap)
            out[str(sym)] = g[["Open", "High", "Low", "Close", "Volume"]]
        for s in symbols:
            out.setdefault(s, None)
        return out


def _back_adjust(df: pd.DataFrame, min_gap: float) -> pd.DataFrame:
    """Back-adjust prices/volume for splits & bonuses.

    On an ex-date NSE reports an adjusted previous close in ``PrevClose``. When
    that differs from the actual prior close by more than ``min_gap``, a
    corporate action occurred; historical prices before it are scaled onto the
    current price basis (and volumes scaled inversely, so price x volume is
    preserved).
    """
    df = df.copy()
    close = df["Close"].to_numpy(dtype=float)
    prevc = df["PrevClose"].to_numpy(dtype=float)
    n = len(df)
    if n < 2:
        return df

    # factor[i] compares day i's reported prev-close with day i-1's actual close.
    factor = np.ones(n)
    for i in range(1, n):
        if prevc[i] > 0 and close[i - 1] > 0:
            factor[i] = prevc[i] / close[i - 1]

    adj = np.ones(n)
    cum = 1.0
    for i in range(n - 1, -1, -1):
        adj[i] = cum
        if i >= 1 and abs(factor[i] - 1.0) > min_gap:
            cum *= factor[i]

    for col in ("Open", "High", "Low", "Close"):
        df[col] = df[col].to_numpy(dtype=float) * adj
    with np.errstate(divide="ignore", invalid="ignore"):
        df["Volume"] = df["Volume"].to_numpy(dtype=float) / np.where(adj == 0, 1.0, adj)
    return df
