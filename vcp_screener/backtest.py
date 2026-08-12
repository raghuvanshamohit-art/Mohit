"""Backtest the VCP setup on historical data.

The live screener asks "is this a FULL VCP SETUP *today*?". The backtest asks
"if I had bought every FULL setup as it appeared, with a stop and an exit rule,
how would it have done?".

Design notes:

* **No look-ahead.** Every criterion is a vectorized function of *past* data
  (rolling / shift), so the signal on day T uses only data up to T. The
  cross-sectional RS Rating ranks stocks against each other *within the same
  day*. Entries fill at the next day's open by default.
* **Entry** = the day a stock first becomes a FULL setup (a fresh flip from
  not-full to full).
* **Exit** = whichever comes first: initial stop, a close back below the trail
  MA, an optional % trailing stop, a max-hold time stop, or end of data.
* **Costs** = a round-trip slippage+brokerage haircut per trade.

Known limitations are documented in the README (survivorship bias from using
today's F&O list, next-open fills, no intraday path within a bar).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from . import indicators as ind
from .config import Config
from .constants import (
    C_ABOVE_LOW,
    C_MA150_RISING,
    C_MA200_RISING,
    C_MA50_RISING,
    C_MA_STACK,
    C_MIN_PRICE,
    C_PRICE_ABOVE_10,
    C_PRICE_ABOVE_MAS,
    C_VOLATILITY_CONTRACT,
    C_VOLUME_CONTRACT,
    C_VOLUME_OK,
    C_WEEKLY_UPTREND,
    C_WITHIN_HIGH,
)


@dataclass
class BacktestConfig:
    stop_pct: float = 0.08          # initial hard stop below entry
    exit_mode: str = "trail_ma"     # "trail_ma" or "big_candle" (sell into strength)
    use_trail_ma: bool = True       # exit when close falls below the trail MA
    trail_ma: int = 50
    trail_pct: float = 0.0          # optional % trailing stop from peak (0 = off)
    # "big_candle" exit: book profit on the first bullish day whose range is
    # >= big_candle_atr_mult x ATR, or whose gain >= big_candle_pct (if > 0).
    big_candle_atr_mult: float = 3.0
    big_candle_pct: float = 0.0
    max_hold: int = 250             # max trading days held
    entry: str = "next_open"        # "next_open" or "signal_close"
    apply_market_filter: bool = True  # include "Nifty in Uptrend" in the setup
    use_rs_rating: bool = True       # cross-sectional RS Rating >= threshold
    cost_pct: float = 0.001          # round-trip cost/slippage per trade
    max_positions: int = 10          # concurrency cap for the equity model
    capital: float = 1_000_000.0


# --------------------------------------------------------------------------- #
# Vectorized signals
# --------------------------------------------------------------------------- #
def nifty_uptrend_series(nifty_df: pd.DataFrame, cfg: Config) -> pd.Series:
    c = nifty_df["Close"]
    above = c > ind.sma(c, cfg.nifty_ma_slow)
    fast = ind.sma(c, cfg.nifty_ma_fast)
    rising = fast > fast.shift(cfg.rising_lookback)
    return (above & rising).fillna(False)


def stock_criteria(df: pd.DataFrame, nifty_close: pd.Series, cfg: Config):
    """Return ``(criteria_df, rs_score)`` for one stock, both indexed by date.

    ``criteria_df`` holds every check *except* "RS vs Nifty Strong" and "Nifty in
    Uptrend" (those are added by the caller, since they need cross-sectional /
    market context).
    """
    close, high, low, vol = df["Close"], df["High"], df["Low"], df["Volume"]
    sma10 = ind.sma(close, cfg.ma_short)
    sma50 = ind.sma(close, cfg.ma_fast)
    sma150 = ind.sma(close, cfg.ma_mid)
    sma200 = ind.sma(close, cfg.ma_slow)

    hi52 = high.rolling(cfg.week52).max()
    lo52 = low.rolling(cfg.week52).min()
    turnover = (close * vol).rolling(cfg.liquidity_lookback).mean()

    atrp = ind.atr(high, low, close, cfg.atr_period) / close
    atrp_recent = atrp.rolling(cfg.volatility_recent).mean()
    atrp_prior = atrp.shift(cfg.volatility_recent).rolling(cfg.volatility_prior).mean()
    vol_recent = vol.rolling(cfg.volume_recent).mean()
    vol_prior = vol.shift(cfg.volume_recent).rolling(cfg.volume_prior).mean()

    weekly = ind.to_weekly(df)
    wclose = weekly["Close"]
    wema = ind.ema(wclose, cfg.weekly_ma)
    wsma = ind.sma(wclose, cfg.weekly_trend_ma)
    w_up = (wclose > wsma) & (wema > wema.shift(cfg.weekly_slope_lookback))
    # ffill onto daily: a mid-week day inherits the *last completed* weekly bar.
    w_up_daily = w_up.reindex(df.index, method="ffill").fillna(False)

    n_aligned = nifty_close.reindex(df.index).ffill()
    stock_ret = close / close.shift(cfg.rs_lookback) - 1.0
    nifty_ret = n_aligned / n_aligned.shift(cfg.rs_lookback) - 1.0
    rs_score = (1.0 + stock_ret) / (1.0 + nifty_ret) - 1.0

    c = pd.DataFrame(index=df.index)
    c[C_PRICE_ABOVE_MAS] = (close > sma50) & (close > sma150) & (close > sma200)
    c[C_MA_STACK] = (sma50 > sma150) & (sma150 > sma200)
    c[C_MA200_RISING] = sma200 > sma200.shift(cfg.rising_lookback)
    c[C_MA50_RISING] = sma50 > sma50.shift(cfg.rising_lookback)
    c[C_WITHIN_HIGH] = close >= (1.0 - cfg.within_high_pct) * hi52
    c[C_ABOVE_LOW] = close >= (1.0 + cfg.above_low_pct) * lo52
    c[C_PRICE_ABOVE_10] = close > sma10
    c[C_MIN_PRICE] = close >= cfg.min_price
    c[C_WEEKLY_UPTREND] = w_up_daily
    c[C_MA150_RISING] = sma150 > sma150.shift(cfg.rising_lookback)
    c[C_VOLUME_OK] = turnover >= cfg.min_avg_turnover
    c[C_VOLATILITY_CONTRACT] = atrp_recent < atrp_prior
    c[C_VOLUME_CONTRACT] = vol_recent < vol_prior
    return c.fillna(False), rs_score


# --------------------------------------------------------------------------- #
# Trade simulation
# --------------------------------------------------------------------------- #
def simulate_stock(sym: str, df: pd.DataFrame, signal: pd.Series, bt: BacktestConfig) -> List[dict]:
    idx = df.index
    o = df["Open"].to_numpy(float)
    h = df["High"].to_numpy(float)
    lo = df["Low"].to_numpy(float)
    cl = df["Close"].to_numpy(float)
    big_candle = bt.exit_mode == "big_candle"
    trail = (ind.sma(df["Close"], bt.trail_ma).to_numpy(float)
             if bt.use_trail_ma and not big_candle else None)
    atr = (ind.atr(df["High"], df["Low"], df["Close"], 14).to_numpy(float)
           if big_candle else None)
    sig = signal.reindex(idx).fillna(False).to_numpy(bool)
    n = len(df)

    trades: List[dict] = []
    i = 0
    while i < n - 1:
        fresh = sig[i] and (i == 0 or not sig[i - 1])
        if not fresh:
            i += 1
            continue

        if bt.entry == "next_open":
            e = i + 1
            if e >= n:
                break
            entry_price = o[e]
        else:
            e = i
            entry_price = cl[i]
        if not np.isfinite(entry_price) or entry_price <= 0:
            i += 1
            continue

        stop = entry_price * (1.0 - bt.stop_pct)
        peak = entry_price
        exit_price = None
        reason = None
        x = e
        j = e + 1
        while j < n:
            if lo[j] <= stop:                                   # hard stop (intraday)
                exit_price = min(o[j], stop)                    # gap-through fills at open
                reason = "stop"; x = j; break
            if big_candle:                                      # sell into the first big up day
                rng = h[j] - lo[j]
                gain = (cl[j] / cl[j - 1] - 1.0) if cl[j - 1] > 0 else 0.0
                is_up = cl[j] > o[j]
                big = ((atr[j] > 0 and rng >= bt.big_candle_atr_mult * atr[j])
                       or (bt.big_candle_pct > 0 and gain >= bt.big_candle_pct))
                if is_up and big:
                    exit_price = cl[j]; reason = "big_candle"; x = j; break
            if trail is not None and np.isfinite(trail[j]) and cl[j] < trail[j]:
                exit_price = cl[j]; reason = "trail_ma"; x = j; break
            if bt.trail_pct > 0:
                peak = max(peak, h[j])
                ts = peak * (1.0 - bt.trail_pct)
                if lo[j] <= ts:
                    exit_price = ts; reason = "trail_pct"; x = j; break
            if j - e >= bt.max_hold:
                exit_price = cl[j]; reason = "time"; x = j; break
            j += 1
        if exit_price is None:
            x = n - 1
            exit_price = cl[x]
            reason = "eod"

        ret = (exit_price / entry_price - 1.0) - bt.cost_pct
        trades.append({
            "symbol": sym,
            "entry_date": idx[e], "exit_date": idx[x],
            "entry": round(float(entry_price), 2), "exit": round(float(exit_price), 2),
            "ret": float(ret), "bars": int(x - e), "reason": reason,
        })
        i = x + 1  # no overlapping trades in the same name
    return trades


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def _mandatory_from_criteria(cols) -> list:
    return [col for col in cols if col != C_ABOVE_LOW]


def run_backtest(
    data: Dict[str, Optional[pd.DataFrame]],
    nifty_df: pd.DataFrame,
    cfg: Optional[Config] = None,
    bt: Optional[BacktestConfig] = None,
):
    """Run the backtest and return a dict with trades and summary stats."""
    cfg = cfg or Config()
    bt = bt or BacktestConfig()

    nifty_up = nifty_uptrend_series(nifty_df, cfg)
    nclose = nifty_df["Close"]

    crits: Dict[str, pd.DataFrame] = {}
    rs_scores: Dict[str, pd.Series] = {}
    for sym, df in data.items():
        if df is None or len(df) < cfg.min_history:
            continue
        c, rs = stock_criteria(df, nclose, cfg)
        crits[sym] = c
        rs_scores[sym] = rs
    if not crits:
        return {"trades": [], "summary": {}, "note": "no stocks with enough history"}

    rs_mat = pd.DataFrame(rs_scores)
    rs_rating = rs_mat.rank(axis=1, pct=True) * 99.0

    def build_trades(apply_filter: bool) -> List[dict]:
        out: List[dict] = []
        for sym, c in crits.items():
            base = c[_mandatory_from_criteria(c.columns)].all(axis=1)
            if bt.use_rs_rating:
                rs_ok = (rs_rating[sym].reindex(c.index) >= cfg.rs_rating_min).fillna(False)
                base = base & rs_ok
            if apply_filter:
                base = base & nifty_up.reindex(c.index).fillna(False)
            out.extend(simulate_stock(sym, data[sym], base, bt))
        return out

    trades = build_trades(bt.apply_market_filter)
    result = {
        "trades": trades,
        "summary": summarize(trades),
        "by_year": by_year(trades),
        "by_reason": by_reason(trades),
        "equity": portfolio(trades, bt),
        "universe": len(crits),
        "span": _span(data, nifty_df),
        "config": bt,
    }
    # Contrast: same setup without the market filter (answers "does the gate help?").
    if bt.apply_market_filter:
        result["no_filter_summary"] = summarize(build_trades(False))
    return result


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def summarize(trades: List[dict]) -> dict:
    if not trades:
        return {"n": 0}
    r = np.array([t["ret"] for t in trades], float)
    wins, losses = r[r > 0], r[r <= 0]
    gross_win, gross_loss = wins.sum(), -losses.sum()
    return {
        "n": len(trades),
        "win_rate": len(wins) / len(trades),
        "avg": float(r.mean()),
        "median": float(np.median(r)),
        "avg_win": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss": float(losses.mean()) if len(losses) else 0.0,
        "expectancy": float(r.mean()),
        "profit_factor": float(gross_win / gross_loss) if gross_loss > 0 else float("inf"),
        "avg_bars": float(np.mean([t["bars"] for t in trades])),
        "best": float(r.max()),
        "worst": float(r.min()),
    }


def by_year(trades: List[dict]) -> Dict[int, dict]:
    out: Dict[int, dict] = {}
    for y in sorted({t["entry_date"].year for t in trades}):
        out[y] = summarize([t for t in trades if t["entry_date"].year == y])
    return out


def by_reason(trades: List[dict]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for t in trades:
        out[t["reason"]] = out.get(t["reason"], 0) + 1
    return out


def portfolio(trades: List[dict], bt: BacktestConfig) -> dict:
    """Approximate equal-weight, capped-concurrency equity curve.

    Each of ``max_positions`` slots compounds independently; a new trade takes
    the earliest-free slot or is skipped if all are busy. Open slots are marked
    at cost, so the curve is a realized-equity curve, not mark-to-market.
    """
    if not trades:
        return {}
    trades = sorted(trades, key=lambda t: (t["entry_date"], t["exit_date"]))
    slots = [bt.capital / bt.max_positions] * bt.max_positions
    free_at = [pd.Timestamp.min] * bt.max_positions
    curve: List[tuple] = []
    taken = skipped = 0
    for t in trades:
        free = [k for k in range(bt.max_positions) if free_at[k] <= t["entry_date"]]
        if not free:
            skipped += 1
            continue
        k = min(free, key=lambda k: free_at[k])
        slots[k] *= (1.0 + t["ret"])
        free_at[k] = t["exit_date"]
        taken += 1
        curve.append((t["exit_date"], sum(slots)))

    eq = pd.Series({d: v for d, v in curve}).sort_index()
    eq = eq[~eq.index.duplicated(keep="last")]
    final = float(sum(slots))
    start = trades[0]["entry_date"]
    end = trades[-1]["exit_date"]
    years = max((end - start).days / 365.25, 1e-9)
    peak = eq.cummax()
    max_dd = float(((eq - peak) / peak).min()) if len(eq) else 0.0
    return {
        "taken": taken, "skipped": skipped,
        "final_equity": final,
        "total_return": final / bt.capital - 1.0,
        "cagr": (final / bt.capital) ** (1.0 / years) - 1.0,
        "max_drawdown": max_dd,
        "years": years,
        "curve": eq,
    }


def _span(data, nifty_df) -> dict:
    starts, ends = [], []
    for df in data.values():
        if df is not None and len(df):
            starts.append(df.index.min())
            ends.append(df.index.max())
    if not starts:
        return {}
    return {"start": min(starts), "end": max(ends),
            "nifty_return": float(nifty_df["Close"].iloc[-1] / nifty_df["Close"].iloc[0] - 1.0)}
