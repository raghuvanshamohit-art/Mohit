"""
ExitMantra replication engine.

Fetches NSE price data (Yahoo Finance) and computes the three ExitMantra
criteria + score/zone/rating/cushion. Criteria 2 (52-week outperformance vs
Nifty 500) and 3 (quant exit price proxy) are computed from price data here.
Criterion 1 (ATH TTM profit) is supplied per-stock from the sample sheet,
because consolidated TTM PAT ex-exceptional is not reliably fetchable free.

No third-party Python deps required (uses urllib + stdlib only).
"""

from __future__ import annotations
import json
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

YF_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval={iv}"
NIFTY500_SYMBOL = "^CRSLDX"          # Nifty 500 (a.k.a. CNX 500) on Yahoo
UA = {"User-Agent": "Mozilla/5.0"}


# --------------------------------------------------------------------------- #
# Data fetch
# --------------------------------------------------------------------------- #
@dataclass
class Series:
    symbol: str
    ts: list[int]
    o: list[float]
    h: list[float]
    l: list[float]
    c: list[float]
    v: list[float]
    meta: dict = field(default_factory=dict)

    @property
    def last_close(self) -> float:
        return self.c[-1]


def fetch(symbol: str, rng: str = "2y", interval: str = "1wk", retries: int = 4) -> Series:
    url = YF_CHART.format(sym=urllib.parse.quote(symbol), rng=rng, iv=interval)
    last_err = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
            res = d["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            ts, o, h, l, c, v = res["timestamp"], q["open"], q["high"], q["low"], q["close"], q["volume"]
            # drop bars with any null OHLC (holidays / still-forming candle)
            rows = [(ts[k], o[k], h[k], l[k], c[k], v[k]) for k in range(len(ts))
                    if None not in (o[k], h[k], l[k], c[k])]
            s = Series(symbol,
                       [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows],
                       [r[3] for r in rows], [r[4] for r in rows], [r[5] or 0 for r in rows],
                       meta=res.get("meta", {}))
            return s
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(2 ** i)
    raise RuntimeError(f"fetch failed for {symbol}: {last_err}")


# --------------------------------------------------------------------------- #
# Indicators
# --------------------------------------------------------------------------- #
def wilder_atr(h: list[float], l: list[float], c: list[float], period: int) -> list[Optional[float]]:
    n = len(c)
    tr = [None] * n
    tr[0] = h[0] - l[0]
    for i in range(1, n):
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    atr: list[Optional[float]] = [None] * n
    if n <= period:
        return atr
    atr[period] = sum(tr[1:period + 1]) / period
    for i in range(period + 1, n):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr


def supertrend(s: Series, period: int = 10, mult: float = 3.0):
    """Returns (line, direction) where direction[i] = 'up' means the line sits
    below price and IS the trailing stop / exit level."""
    h, l, c = s.h, s.l, s.c
    n = len(c)
    atr = wilder_atr(h, l, c, period)
    line: list[Optional[float]] = [None] * n
    direction: list[Optional[str]] = [None] * n
    fu = fl = None
    for i in range(n):
        if atr[i] is None:
            continue
        hl2 = (h[i] + l[i]) / 2
        bu = hl2 + mult * atr[i]
        bl = hl2 - mult * atr[i]
        if fu is None:
            fu, fl = bu, bl
            direction[i] = "up" if c[i] >= fl else "down"
            line[i] = fl if direction[i] == "up" else fu
            prev_fu, prev_fl = fu, fl
            continue
        fu = bu if (bu < prev_fu or c[i - 1] > prev_fu) else prev_fu
        fl = bl if (bl > prev_fl or c[i - 1] < prev_fl) else prev_fl
        if line[i - 1] == prev_fu:
            direction[i] = "down" if c[i] <= fu else "up"
        else:
            direction[i] = "up" if c[i] >= fl else "down"
        line[i] = fl if direction[i] == "up" else fu
        prev_fu, prev_fl = fu, fl
    return line, direction


def chandelier_exit(s: Series, period: int = 22, mult: float = 3.0) -> list[Optional[float]]:
    """Long-side Chandelier stop = HighestHigh(period) - mult*ATR(period)."""
    h, l, c = s.h, s.l, s.c
    n = len(c)
    atr = wilder_atr(h, l, c, period)
    out: list[Optional[float]] = [None] * n
    for i in range(n):
        if atr[i] is None or i < period:
            continue
        hh = max(h[i - period + 1:i + 1])
        out[i] = hh - mult * atr[i]
    return out


# --------------------------------------------------------------------------- #
# Criteria
# --------------------------------------------------------------------------- #
def return_over(series: Series) -> float:
    """Total return across the fetched series (first valid to last)."""
    return series.c[-1] / series.c[0] - 1.0


def outperformance(stock_daily: Series, index_daily: Series) -> dict:
    rs = return_over(stock_daily)
    ri = return_over(index_daily)
    return {"stock_1y_ret": rs, "index_1y_ret": ri,
            "outperformer": rs > ri, "rs_spread": rs - ri}


def exit_level(s: Series, method: str = "supertrend", period: int = 10, mult: float = 3.0):
    """Current exit-price proxy. Only meaningful when the stock is in an uptrend
    (line below price). Returns (level, in_uptrend)."""
    if method == "supertrend":
        line, direction = supertrend(s, period, mult)
        return line[-1], direction[-1] == "up"
    elif method == "chandelier":
        line = chandelier_exit(s, period, mult)
        lvl = line[-1]
        return lvl, (lvl is not None and s.c[-1] > lvl)
    raise ValueError(method)


# --------------------------------------------------------------------------- #
# Scoring (deterministic — mirrors ExitMantra exactly)
# --------------------------------------------------------------------------- #
RATING = {3: "ADD", 2: "HOLD", 1: "REPLACE", 0: "EXIT"}


def score_rating_zone(ath_profit: bool, outperformer: bool, above_exit: bool) -> dict:
    score = int(bool(ath_profit)) + int(bool(outperformer)) + int(bool(above_exit))
    zone = "Bull" if score >= 2 else ("Pig" if score == 1 else "Bear")
    return {"score": score, "rating": RATING[score], "zone": zone}


def cushion_pct(cmp: float, exit_price: float) -> Optional[float]:
    if not exit_price or cmp <= 0:
        return None
    return (cmp - exit_price) / cmp * 100.0


def risk_level(cushion: Optional[float]) -> Optional[str]:
    if cushion is None:
        return None
    if cushion < 20:
        return "Low"
    if cushion <= 35:
        return "Moderate"
    return "High"


def position_size(total_risk: float, entry: float, exit_price: float) -> dict:
    per_share = entry - exit_price
    if per_share <= 0:
        return {"error": "entry must be above exit price"}
    qty = int(total_risk // per_share)
    return {"risk_per_share": per_share, "qty": qty, "allocation": qty * entry}
