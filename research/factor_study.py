#!/usr/bin/env python3
"""Cross-sectional factor study + backtest on the Indian stock universe.

For every month-end t, each stock gets a score on several technical factors,
computed only from prices up to t. We then measure how well each score ranks
the *next* month's returns:

  * IC (information coefficient) = Spearman rank correlation, across stocks,
    between factor(t) and return(t -> t+h). Averaged over all months.
  * Quintile backtest: equal-weight the 20% highest- and lowest-scored stocks,
    rebalance monthly, report CAGR / Sharpe / drawdown after costs.

    python research/fetch_history.py   # once, downloads prices
    python research/factor_study.py    # -> research/results/*.csv + console report

Requires pandas + numpy (research only; the main tool stays stdlib-only).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PRICES = HERE / "cache" / "prices.csv"
RESULTS = HERE / "results"
BENCH = "NIFTY50"
COST_ONE_WAY = 0.002        # 20 bps per side (brokerage + STT + impact, rough)
MIN_STOCKS = 100            # skip months with too thin a cross-section
HORIZONS = {"1m": 1, "3m": 3, "6m": 6}


def load():
    px = pd.read_csv(PRICES, index_col="date", parse_dates=True).sort_index()
    px = px.ffill(limit=5)
    return px


def factors(px: pd.DataFrame) -> "dict[str, pd.DataFrame]":
    """Every factor is oriented so that HIGHER = expected to do better
    according to the published literature (so a positive IC = 'it worked')."""
    ret = px.pct_change(fill_method=None)
    mret = ret[BENCH]
    stocks = px.drop(columns=[BENCH])
    r = ret.drop(columns=[BENCH])
    m = stocks.resample("ME").last()
    me_idx = m.index

    def at_me(df):
        return df.resample("ME").last().reindex(me_idx)

    vol63 = r.rolling(63, min_periods=50).std() * np.sqrt(252)
    beta = (r.rolling(252, min_periods=200).cov(mret)
            .div(mret.rolling(252, min_periods=200).var(), axis=0))
    hi252 = stocks.rolling(252, min_periods=200).max()
    ma200 = stocks.rolling(200, min_periods=180).mean()
    maxret21 = r.rolling(21, min_periods=15).max()

    f = {
        "Momentum 12-1m":        m.shift(1) / m.shift(12) - 1,
        "Momentum 6-1m":         m.shift(1) / m.shift(6) - 1,
        "Short-term reversal":   -(m / m.shift(1) - 1),            # loser last month -> high score
        "Low volatility (3m)":   -at_me(vol63),
        "Low beta (1y)":         -at_me(beta),
        "Near 52-week high":     at_me(stocks / hi252),
        "Trend (price/200DMA)":  at_me(stocks / ma200 - 1),
        "Low MAX (lottery)":     -at_me(maxret21),
    }

    def z(df):
        return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0).clip(-3, 3)

    # Pre-specified (not optimised) blend: momentum + quality-of-trend + low risk.
    f["Composite (Mom+52wH+LowVol)"] = (
        z(f["Momentum 12-1m"]) + z(f["Near 52-week high"]) + z(f["Low volatility (3m)"])
    ) / 3
    return f, m


def fwd_returns(m: pd.DataFrame, h: int) -> pd.DataFrame:
    return m.shift(-h) / m - 1


def ic_series(fac: pd.DataFrame, fwd: pd.DataFrame) -> pd.Series:
    out = {}
    for d in fac.index:
        a, b = fac.loc[d], fwd.loc[d]
        ok = a.notna() & b.notna()
        if ok.sum() >= MIN_STOCKS:
            out[d] = a[ok].rank().corr(b[ok].rank())
    return pd.Series(out, dtype=float)


def quintile_backtest(fac: pd.DataFrame, fwd1: pd.DataFrame, q=5):
    rets, turn = {k: {} for k in range(1, q + 1)}, {}
    prev_top = set()
    for d in fac.index:
        a, b = fac.loc[d], fwd1.loc[d]
        ok = a.notna() & b.notna()
        if ok.sum() < MIN_STOCKS:
            continue
        buckets = pd.qcut(a[ok].rank(method="first"), q, labels=False) + 1
        for k in range(1, q + 1):
            rets[k][d] = b[ok][buckets == k].clip(upper=3).mean()   # cap one-month +300% outliers
        top = set(buckets[buckets == q].index)
        turn[d] = 1.0 if not prev_top else 1 - len(top & prev_top) / len(top)
        prev_top = top
    df = pd.DataFrame(rets)
    df.columns = [f"Q{k}" for k in df.columns]
    df["Q5 net"] = df[f"Q{q}"] - pd.Series(turn) * 2 * COST_ONE_WAY
    df["Q5-Q1"] = df[f"Q{q}"] - df["Q1"]
    df["turnover"] = pd.Series(turn)
    return df


def perf(r: pd.Series) -> dict:
    r = r.dropna()
    if r.empty:
        return {}
    eq = (1 + r).cumprod()
    yrs = len(r) / 12
    return {
        "CAGR %": (eq.iloc[-1] ** (1 / yrs) - 1) * 100,
        "Vol %": r.std() * np.sqrt(12) * 100,
        "Sharpe": r.mean() / r.std() * np.sqrt(12) if r.std() else np.nan,
        "MaxDD %": (eq / eq.cummax() - 1).min() * 100,
    }


def main():
    px = load()
    facs, m = factors(px)
    bench_m = px[BENCH].resample("ME").last()
    fwd = {k: fwd_returns(m, h) for k, h in HORIZONS.items()}

    ic_rows, bt_rows, ic_ts = [], [], {}
    for name, fac in facs.items():
        row = {"Factor": name}
        for k in HORIZONS:
            ics = ic_series(fac, fwd[k])
            if k == "1m":
                ic_ts[name] = ics
                n = len(ics)
                row.update({
                    "IC 1m": ics.mean(),
                    "IC std": ics.std(),
                    "ICIR (ann.)": ics.mean() / ics.std() * np.sqrt(12),
                    # Newey-West-free simple t; overlapping not an issue at h=1
                    "t-stat": ics.mean() / ics.std() * np.sqrt(n),
                    "% months IC>0": (ics > 0).mean() * 100,
                    "months": n,
                })
                half = n // 2
                row["IC 1st half"] = ics.iloc[:half].mean()
                row["IC 2nd half"] = ics.iloc[half:].mean()
            else:
                row[f"IC {k}"] = ics.mean()
        ic_rows.append(row)

        bt = quintile_backtest(fac, fwd["1m"])
        bt_rows.append({"Factor": name, "Portfolio": "Top quintile (net)", **perf(bt["Q5 net"]),
                        "Avg turnover %": bt["turnover"].mean() * 100})
        bt_rows.append({"Factor": name, "Portfolio": "Bottom quintile", **perf(bt["Q1"])})
        bt_rows.append({"Factor": name, "Portfolio": "Long-short Q5-Q1 (gross)", **perf(bt["Q5-Q1"])})
        if name.startswith("Composite"):
            comp_bt, comp_start = bt, bt.index[0]

    bench_r = bench_m.pct_change().shift(-1).reindex(comp_bt.index)
    ew = comp_bt[[f"Q{k}" for k in range(1, 6)]].mean(axis=1)
    bt_rows.append({"Factor": "Benchmark", "Portfolio": "Nifty 50", **perf(bench_r)})
    bt_rows.append({"Factor": "Benchmark", "Portfolio": "Equal-weight universe", **perf(ew)})

    ic_df = pd.DataFrame(ic_rows).set_index("Factor").sort_values("IC 1m", ascending=False)
    bt_df = pd.DataFrame(bt_rows)
    # Correlation between the factors' monthly ICs: are they telling the same story?
    ic_corr = pd.DataFrame(ic_ts).corr()

    RESULTS.mkdir(exist_ok=True)
    ic_df.round(4).to_csv(RESULTS / "factor_ic.csv")
    bt_df.round(3).to_csv(RESULTS / "factor_backtest.csv", index=False)
    ic_corr.round(2).to_csv(RESULTS / "factor_ic_correlation.csv")
    pd.DataFrame(ic_ts).round(4).to_csv(RESULTS / "factor_ic_monthly.csv")
    eq = pd.DataFrame({
        "Composite top quintile (net)": (1 + comp_bt["Q5 net"]).cumprod(),
        "Composite bottom quintile": (1 + comp_bt["Q1"]).cumprod(),
        "Equal-weight universe": (1 + ew).cumprod(),
        "Nifty 50": (1 + bench_r.fillna(0)).cumprod(),
    })
    eq.round(4).to_csv(RESULTS / "composite_equity_curve.csv")

    pd.set_option("display.width", 200, "display.max_columns", 20)
    print(f"Universe: {m.shape[1]} stocks | months scored: {ic_df['months'].max():.0f} "
          f"({comp_start:%Y-%m} -> {comp_bt.index[-1]:%Y-%m})\n")
    print("=== Information Coefficient (Spearman, factor vs forward return) ===")
    print(ic_df.round(3).to_string(), "\n")
    print("=== Quintile backtest (monthly rebalance, equal weight) ===")
    print(bt_df.round(2).to_string(index=False), "\n")
    print("=== Correlation of monthly ICs between factors ===")
    print(ic_corr.round(2).to_string())


if __name__ == "__main__":
    main()
