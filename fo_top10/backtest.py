"""Backtest: 'buy the top-N daily gainers in the F&O universe' strategy.

Core question set:
  1. Once a stock is a top-N gainer, how many days does it *sustain*
     (stay in the top-N, and keep going up)?
  2. If you trade this basket, what CAGR, hold period and drawdown result?

No look-ahead: selection on day t uses only the return of day t (known at that
day's close); the strategy earns returns from day t+1 onward.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS = 252


# --------------------------------------------------------------------------- #
# Building blocks
# --------------------------------------------------------------------------- #
def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Simple daily returns from a wide adjusted-close frame."""
    return prices.sort_index().pct_change()


def selection_mask(returns: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """1.0 where a stock is among the top_n gainers that day, else 0.0.

    A stock is eligible on day t only if it has a valid return on day t.
    """
    ranks = returns.rank(axis=1, ascending=False, method="first")
    mask = (ranks <= top_n) & returns.notna()
    return mask.astype(float)


# --------------------------------------------------------------------------- #
# Question 1a: membership persistence (how long they stay in the top-N)
# --------------------------------------------------------------------------- #
def membership_sustain(mask: pd.DataFrame) -> dict:
    """Distribution of consecutive-day runs a stock spends in the top-N."""
    runs = []
    arr = mask.values.astype(bool)
    cols = mask.columns
    for j in range(arr.shape[1]):
        col = arr[:, j]
        length = 0
        for v in col:
            if v:
                length += 1
            elif length:
                runs.append(length)
                length = 0
        if length:
            runs.append(length)
    runs = np.array(runs)
    return {
        "episodes": int(runs.size),
        "mean_days": float(runs.mean()),
        "median_days": float(np.median(runs)),
        "pct_1_day": float((runs == 1).mean() * 100),
        "pct_ge_2_days": float((runs >= 2).mean() * 100),
        "pct_ge_3_days": float((runs >= 3).mean() * 100),
        "max_days": int(runs.max()),
    }


# --------------------------------------------------------------------------- #
# Question 1b: return persistence (does the up-move continue?)
# --------------------------------------------------------------------------- #
def forward_return_persistence(returns: pd.DataFrame, mask: pd.DataFrame,
                               horizons=(1, 2, 3, 5, 10, 15, 20)) -> pd.DataFrame:
    """Average forward CUMULATIVE return after entering the top-N on day t,
    entering at day t's close (so horizon h = returns of days t+1..t+h).

    Compared against the universe average over the same horizon (edge).
    """
    r = returns.copy()
    rows = []
    for h in horizons:
        # forward cumulative return over the next h days, aligned to entry day t
        fwd = (1 + r).rolling(h).apply(np.prod, raw=True).shift(-h) - 1
        sel = mask.values.astype(bool)
        picked = fwd.values[sel]
        picked = picked[~np.isnan(picked)]
        uni = fwd.values
        uni = uni[~np.isnan(uni)]
        rows.append({
            "horizon_days": h,
            "avg_fwd_return_%": picked.mean() * 100,
            "median_fwd_return_%": np.median(picked) * 100,
            "win_rate_%": (picked > 0).mean() * 100,
            "universe_avg_%": uni.mean() * 100,
            "edge_vs_universe_%": (picked.mean() - uni.mean()) * 100,
            "n_obs": picked.size,
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Question 2: the tradable strategy (overlapping daily cohorts)
# --------------------------------------------------------------------------- #
def _cohort_daily_returns(returns: pd.DataFrame, mask: pd.DataFrame,
                          max_h: int) -> list[np.ndarray]:
    """b_k[d] = equal-weight return on day d of the cohort selected k days
    earlier, for k = 1..max_h."""
    R = returns.values
    M = mask.values
    valid = ~np.isnan(R)
    Rz = np.where(valid, R, 0.0)
    b = []
    for k in range(1, max_h + 1):
        sel = np.zeros_like(M)
        sel[k:] = M[:-k]                      # row d holds selection from day d-k
        num = np.einsum("ij,ij->i", Rz, sel)  # sum of returns of selected names
        den = np.einsum("ij,ij->i", valid.astype(float), sel)  # count still trading
        with np.errstate(invalid="ignore", divide="ignore"):
            bk = np.where(den > 0, num / den, 0.0)
        b.append(bk)
    return b


def backtest_hold(returns: pd.DataFrame, mask: pd.DataFrame, hold_days: int,
                  cost_per_turn: float = 0.0) -> pd.Series:
    """Equity curve for holding each day's top-N basket for `hold_days`.

    Capital is split across `hold_days` overlapping daily cohorts (so the book
    is always fully invested and turns over 1/hold_days of itself each day).
    `cost_per_turn` is a round-trip cost (fraction) charged on the fraction of
    the book rebalanced each day (= 1/hold_days).
    """
    b = _cohort_daily_returns(returns, mask, hold_days)
    port = np.mean(np.vstack(b), axis=0)          # average of open cohorts
    daily_turnover = 1.0 / hold_days
    port = port - cost_per_turn * daily_turnover  # subtract trading friction
    port = pd.Series(port, index=returns.index)
    port = port.iloc[hold_days:]                  # drop warm-up (not all cohorts open)
    equity = (1 + port).cumprod()
    equity.name = f"hold_{hold_days}d"
    return equity


def hold_until_exit(returns: pd.DataFrame, mask: pd.DataFrame,
                    max_hold: int = 60) -> dict:
    """Event study: enter at day-t close when a stock joins the top-N, hold
    until it drops out of the top-N (or max_hold), exit at that close.
    Reports realised return and holding-period distributions."""
    R = returns.values
    M = mask.values.astype(bool)
    T, N = M.shape
    rets, holds = [], []
    for j in range(N):
        t = 1
        col = M[:, j]
        while t < T:
            if col[t] and not col[t - 1]:        # fresh entry into top-N on day t
                # hold while still in top-N, exit the first day it is not (or max)
                d = t + 1
                cum = 1.0
                days = 0
                while d < T and days < max_hold:
                    if np.isnan(R[d, j]):
                        break
                    cum *= (1 + R[d, j])
                    days += 1
                    if not col[d]:               # dropped out at close of day d
                        break
                    d += 1
                if days > 0:
                    rets.append(cum - 1)
                    holds.append(days)
                t = d + 1
            else:
                t += 1
    rets = np.array(rets)
    holds = np.array(holds)
    return {
        "trades": int(rets.size),
        "avg_hold_days": float(holds.mean()),
        "median_hold_days": float(np.median(holds)),
        "avg_return_%": float(rets.mean() * 100),
        "median_return_%": float(np.median(rets) * 100),
        "win_rate_%": float((rets > 0).mean() * 100),
    }


# --------------------------------------------------------------------------- #
# Performance metrics
# --------------------------------------------------------------------------- #
def performance(equity: pd.Series) -> dict:
    equity = equity.dropna()
    if equity.empty:
        return {}
    daily = equity.pct_change().dropna()
    n = len(equity)
    years = n / TRADING_DAYS
    total = equity.iloc[-1] / equity.iloc[0] - 1
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1 if years > 0 else np.nan
    vol = daily.std() * np.sqrt(TRADING_DAYS)
    sharpe = (daily.mean() / daily.std() * np.sqrt(TRADING_DAYS)
              if daily.std() > 0 else np.nan)
    dd = equity / equity.cummax() - 1
    max_dd = dd.min()
    calmar = cagr / abs(max_dd) if max_dd < 0 else np.nan
    return {
        "years": round(years, 2),
        "total_return_%": round(total * 100, 1),
        "CAGR_%": round(cagr * 100, 2),
        "ann_vol_%": round(vol * 100, 1),
        "sharpe": round(sharpe, 2),
        "max_drawdown_%": round(max_dd * 100, 1),
        "calmar": round(calmar, 2) if not np.isnan(calmar) else None,
    }


def benchmark_equal_weight(returns: pd.DataFrame) -> pd.Series:
    """Equal-weight, daily-rebalanced buy-and-hold of the whole universe."""
    port = returns.mean(axis=1, skipna=True).fillna(0)
    equity = (1 + port).cumprod()
    equity.name = "EW_universe"
    return equity
