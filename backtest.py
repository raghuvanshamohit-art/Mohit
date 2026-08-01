"""
Momentum backtest for the Nifty Next 50 universe.

Strategy (as specified):
  * Universe   : Nifty Next 50 constituents.
  * Signal     : trailing 12-month total return ("yearly return"), recomputed
                 every month.
  * Selection  : rank all eligible stocks, hold the top 10.
  * Weighting  : equal weight (10% each).
  * Rebalance  : monthly, at the month-end close.

Outputs CAGR, maximum drawdown, the full equity curve and supporting stats.
Transaction costs are modelled on rebalance turnover and can be switched off.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class BacktestConfig:
    top_n: int = 10              # number of stocks held
    lookback_m: int = 12         # momentum lookback in months ("yearly return")
    skip_recent_m: int = 0       # months to skip (1 -> classic 12-1 momentum)
    min_names: int = 10          # need at least this many eligible names to trade
    cost_bps_per_side: float = 20.0   # one-way transaction cost on turnover
    rf_annual: float = 0.06      # risk-free rate for Sharpe (India ~6%)


@dataclass
class BacktestResult:
    monthly_returns: pd.Series
    equity: pd.Series
    drawdown: pd.Series
    holdings: pd.DataFrame
    yearly: pd.DataFrame
    stats: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def to_month_end(prices: pd.DataFrame) -> pd.DataFrame:
    """Last available adjusted close in each calendar month."""
    return prices.resample("ME").last()


def _max_drawdown(equity: pd.Series) -> tuple[float, pd.Timestamp, pd.Timestamp]:
    running_max = equity.cummax()
    dd = equity / running_max - 1.0
    trough = dd.idxmin()
    peak = equity.loc[:trough].idxmax()
    return dd.min(), peak, trough


# ---------------------------------------------------------------------------
# Core backtest
# ---------------------------------------------------------------------------
def run_backtest(prices: pd.DataFrame, cfg: BacktestConfig = BacktestConfig()
                 ) -> BacktestResult:
    mp = to_month_end(prices)
    months = mp.index
    lb = cfg.lookback_m + cfg.skip_recent_m

    port_rets: list[float] = []
    dates: list[pd.Timestamp] = []
    holdings_rows: dict[pd.Timestamp, list[str]] = {}
    prev_weights = pd.Series(dtype=float)

    # Form a portfolio at month t (using data up to t), realise its return over
    # [t, t+1]. Loop stops at the second to last month.
    for i in range(lb, len(months) - 1):
        t = months[i]
        t_next = months[i + 1]

        p_now = mp.loc[t]
        p_lb = mp.loc[months[i - cfg.lookback_m - cfg.skip_recent_m]]
        p_skip = mp.loc[months[i - cfg.skip_recent_m]] if cfg.skip_recent_m else p_now

        # trailing return over the lookback window (optionally skipping recent month)
        mom = p_skip / p_lb - 1.0
        eligible = mom.dropna()
        # must also have a tradable price now and next month
        tradable = mp.loc[t].notna() & mp.loc[t_next].notna()
        eligible = eligible[tradable.reindex(eligible.index, fill_value=False)]

        if len(eligible) < cfg.min_names:
            continue

        winners = eligible.sort_values(ascending=False).head(cfg.top_n).index
        w_new = pd.Series(1.0 / len(winners), index=winners)

        # realised next-month return of the equal-weight basket
        fwd = mp.loc[t_next, winners] / mp.loc[t, winners] - 1.0
        gross = float(fwd.mean())

        # turnover vs previous book (one-way) -> transaction cost
        all_names = prev_weights.index.union(w_new.index)
        turnover = (w_new.reindex(all_names, fill_value=0.0)
                    - prev_weights.reindex(all_names, fill_value=0.0)).abs().sum()
        cost = (cfg.cost_bps_per_side / 1e4) * turnover
        net = gross - cost

        port_rets.append(net)
        dates.append(t_next)
        holdings_rows[t] = list(winners)
        # weights drift with prices over the month; approximate next book start
        prev_weights = (w_new * (1 + fwd)) / (w_new * (1 + fwd)).sum()

    monthly = pd.Series(port_rets, index=pd.DatetimeIndex(dates), name="strategy")
    equity = (1 + monthly).cumprod()
    equity.iloc[0] = equity.iloc[0]  # keep first realised month
    equity = pd.concat([pd.Series([1.0], index=[monthly.index[0] - pd.offsets.MonthEnd(1)]),
                        equity])
    running_max = equity.cummax()
    drawdown = equity / running_max - 1.0

    holdings = pd.DataFrame(
        {d: pd.Series(names) for d, names in holdings_rows.items()}
    ).T

    stats = _compute_stats(monthly, equity, drawdown, cfg)
    yearly = _yearly_table(monthly)

    return BacktestResult(monthly, equity, drawdown, holdings, yearly, stats)


def _compute_stats(monthly, equity, drawdown, cfg) -> dict:
    n_months = len(monthly)
    years = n_months / 12.0
    total_return = equity.iloc[-1] / equity.iloc[0] - 1.0
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1.0
    vol = monthly.std(ddof=1) * np.sqrt(12)
    ann_mean = monthly.mean() * 12
    sharpe = (ann_mean - cfg.rf_annual) / vol if vol else np.nan
    downside = monthly[monthly < 0].std(ddof=1) * np.sqrt(12)
    sortino = (ann_mean - cfg.rf_annual) / downside if downside else np.nan
    maxdd, peak, trough = _max_drawdown(equity)
    calmar = cagr / abs(maxdd) if maxdd else np.nan

    return {
        "start": equity.index[0].date().isoformat(),
        "end": equity.index[-1].date().isoformat(),
        "years": round(years, 2),
        "months": n_months,
        "total_return_pct": round(total_return * 100, 1),
        "CAGR_pct": round(cagr * 100, 2),
        "annual_vol_pct": round(vol * 100, 2),
        "max_drawdown_pct": round(maxdd * 100, 2),
        "max_dd_peak": peak.date().isoformat(),
        "max_dd_trough": trough.date().isoformat(),
        "sharpe": round(sharpe, 2),
        "sortino": round(sortino, 2),
        "calmar": round(calmar, 2),
        "best_month_pct": round(monthly.max() * 100, 1),
        "worst_month_pct": round(monthly.min() * 100, 1),
        "pct_positive_months": round((monthly > 0).mean() * 100, 1),
        "final_multiple": round(equity.iloc[-1] / equity.iloc[0], 1),
    }


def _yearly_table(monthly: pd.Series) -> pd.DataFrame:
    by_year = (1 + monthly).groupby(monthly.index.year).prod() - 1
    df = by_year.to_frame("return")
    df["return_pct"] = (df["return"] * 100).round(1)
    return df


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------
def benchmark_from_index(index_series: pd.Series,
                         align_to: pd.Series) -> pd.Series | None:
    """Monthly returns of an index series, aligned to the strategy window."""
    if index_series is None:
        return None
    m = index_series.resample("ME").last().pct_change().dropna()
    return m.reindex(align_to.index).dropna()


def equal_weight_buyhold(prices: pd.DataFrame,
                         align_to: pd.Series) -> pd.Series:
    """Monthly return of an equal-weight, monthly-rebalanced hold of the whole
    (currently-listed) universe -- a fair 'own no skill' benchmark."""
    mp = to_month_end(prices)
    rets = mp.pct_change()
    ew = rets.mean(axis=1)  # equal weight across names available that month
    return ew.reindex(align_to.index).dropna()


def series_stats(monthly: pd.Series, rf_annual: float = 0.06) -> dict:
    equity = (1 + monthly).cumprod()
    years = len(monthly) / 12.0
    cagr = equity.iloc[-1] ** (1 / years) - 1
    vol = monthly.std(ddof=1) * np.sqrt(12)
    maxdd, _, _ = _max_drawdown(equity)
    sharpe = (monthly.mean() * 12 - rf_annual) / vol if vol else np.nan
    return {
        "CAGR_pct": round(cagr * 100, 2),
        "annual_vol_pct": round(vol * 100, 2),
        "max_drawdown_pct": round(maxdd * 100, 2),
        "sharpe": round(sharpe, 2),
    }
