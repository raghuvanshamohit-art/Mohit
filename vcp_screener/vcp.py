"""VCP (Volatility Contraction Pattern) detection — the Minervini footprint.

The core screener uses an ATR%-recent-vs-prior *proxy* for contraction. This
module implements the real thing described in *Think & Trade Like a Champion*:
find the swing highs/lows of the base, measure the successive **contractions**
(each ideally ~half the prior), confirm the final contraction is **tight with
volume drying up**, and mark the **pivot buy point** (the right edge of the
base) that a breakout must clear on a volume surge.

It's a heuristic — real VCPs are read on a chart — but it captures the
footprint: contraction count, depths, tightness, volume dry-up, and the pivot.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import pandas as pd

from . import indicators as ind


@dataclass
class VCPConfig:
    base_lookback: int = 80       # bars of base to inspect
    swing_k: int = 3              # a swing needs k bars either side
    min_depth: float = 0.03       # ignore wiggles shallower than 3%
    min_contractions: int = 2
    max_contractions: int = 6
    last_contraction_max: float = 0.10   # final "T" should be tight (<=10%)
    contraction_tolerance: float = 1.15  # each T <= prior * tolerance (roughly shrinking)
    vol_recent: int = 10          # window for volume dry-up
    vol_base: int = 50
    near_pivot_pct: float = 0.05  # "at the pivot" if within 5% below it
    breakout_vol_mult: float = 1.4  # breakout volume vs 50-day average


@dataclass
class VCPResult:
    is_vcp: bool = False
    n_contractions: int = 0
    depths: List[float] = field(default_factory=list)   # each contraction %, left->right
    last_depth: float = float("nan")
    pivot: float = float("nan")           # buy point (right edge of the base)
    pivot_low: float = float("nan")       # low of the final contraction (danger point)
    volume_dryup: bool = False
    dist_to_pivot: float = float("nan")   # close/pivot - 1 (negative = below pivot)
    status: str = "no base"               # no base | in base | at pivot | breakout
    breakout_vol_ratio: float = float("nan")


def _swings(high: np.ndarray, low: np.ndarray, k: int):
    """Return an alternating list of (index, price, 'H'|'L') swing points."""
    n = len(high)
    raw = []
    for i in range(k, n - k):
        if high[i] == high[i - k:i + k + 1].max() and high[i] > high[i - 1]:
            raw.append((i, float(high[i]), "H"))
        elif low[i] == low[i - k:i + k + 1].min() and low[i] < low[i - 1]:
            raw.append((i, float(low[i]), "L"))
    # Collapse consecutive same-type swings, keeping the more extreme one.
    seq = []
    for pt in raw:
        if seq and seq[-1][2] == pt[2]:
            if (pt[2] == "H" and pt[1] > seq[-1][1]) or (pt[2] == "L" and pt[1] < seq[-1][1]):
                seq[-1] = pt
        else:
            seq.append(pt)
    return seq


def detect_vcp(df: pd.DataFrame, cfg: Optional[VCPConfig] = None) -> VCPResult:
    cfg = cfg or VCPConfig()
    res = VCPResult()
    if df is None or len(df) < cfg.base_lookback:
        return res

    window = df.iloc[-cfg.base_lookback:]
    high = window["High"].to_numpy(float)
    low = window["Low"].to_numpy(float)
    close = float(df["Close"].iloc[-1])
    vol = df["Volume"]

    seq = _swings(high, low, cfg.swing_k)
    if len(seq) < 2:
        return res

    # Contractions = each swing-high followed by the next swing-low (peak->trough).
    depths = []
    for a, b in zip(seq, seq[1:]):
        if a[2] == "H" and b[2] == "L":
            depth = (a[1] - b[1]) / a[1]
            if depth >= cfg.min_depth:
                depths.append(depth)

    if not depths:
        return res
    res.depths = [round(d, 4) for d in depths]
    res.n_contractions = len(depths)
    res.last_depth = depths[-1]

    # Pivot = the most recent swing high (right edge of the base).
    highs = [p for p in seq if p[2] == "H"]
    lows = [p for p in seq if p[2] == "L"]
    res.pivot = highs[-1][1] if highs else float(window["High"].max())
    res.pivot_low = lows[-1][1] if lows else float(window["Low"].min())
    res.dist_to_pivot = close / res.pivot - 1.0 if res.pivot else float("nan")

    # Volume dry-up: recent average volume below the base average.
    v_recent = vol.iloc[-cfg.vol_recent:].mean()
    v_base = vol.iloc[-cfg.vol_base:].mean()
    res.volume_dryup = bool(v_recent < v_base)
    res.breakout_vol_ratio = float(vol.iloc[-1] / v_base) if v_base else float("nan")

    # Contractions should roughly shrink left->right.
    shrinking = all(depths[i] <= depths[i - 1] * cfg.contraction_tolerance
                    for i in range(1, len(depths)))
    count_ok = cfg.min_contractions <= res.n_contractions <= cfg.max_contractions
    tight = res.last_depth <= cfg.last_contraction_max
    res.is_vcp = bool(count_ok and shrinking and tight and res.volume_dryup)

    # Status relative to the pivot.
    if close > res.pivot and res.breakout_vol_ratio >= cfg.breakout_vol_mult:
        res.status = "breakout"
    elif close > res.pivot:
        res.status = "breakout (weak vol)"
    elif res.dist_to_pivot >= -cfg.near_pivot_pct:
        res.status = "at pivot"
    else:
        res.status = "in base"
    return res
