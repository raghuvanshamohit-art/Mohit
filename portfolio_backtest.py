"""
Equal-weight, annually-rebalanced portfolio backtest.

Strategy
--------
Split money equally (1/3 each) across three instruments:
    * Nasdaq-100      (^NDX,  priced in USD -> converted to INR)
    * Nifty 50        (^NSEI, priced in INR)
    * Gold            (GC=F,  COMEX gold, USD -> converted to INR)
Rebalance back to 1/3 : 1/3 : 1/3 on the last trading day of every calendar year.

Everything is measured in INR, i.e. the point of view of an Indian investor who
holds Nifty 50 directly and holds the US index / international gold with rupee
money (so USD/INR moves flow into the returns of those two legs).

Outputs
-------
    * CAGR and maximum drawdown of the blended portfolio
    * The same two metrics for each instrument on its own (for comparison)
    * A cached copy of the raw price data (data/prices_inr.csv)
    * An equity-curve + drawdown chart (results/equity_drawdown.png)

Data source: Yahoo Finance v8 chart API (daily closes). Indices are PRICE
indices (dividends excluded) so the three legs are compared on a like-for-like
price-return basis; gold pays no dividend anyway.
"""

import io
import os
import time
import datetime as dt

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
RESULTS_DIR = os.path.join(HERE, "results")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

TICKERS = {
    "nasdaq100": "^NDX",   # Nasdaq-100 price index (USD)
    "nifty50":   "^NSEI",  # Nifty 50 price index (INR)
    "gold":      "GC=F",   # COMEX gold front-month (USD)
    "usdinr":    "INR=X",  # USD/INR spot
}


def fetch_series(symbol, retries=6):
    """Fetch a daily close series from Yahoo Finance as a pandas Series."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "25y", "interval": "1d"}
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, headers={"User-Agent": UA},
                             timeout=30)
            if r.status_code == 200:
                res = r.json()["chart"]["result"][0]
                ts = res["timestamp"]
                close = res["indicators"]["quote"][0]["close"]
                idx = pd.to_datetime([dt.datetime.utcfromtimestamp(t).date()
                                      for t in ts])
                s = pd.Series(close, index=idx, name=symbol).astype(float)
                return s[~s.index.duplicated(keep="last")].dropna()
            last_err = f"HTTP {r.status_code}"
        except Exception as e:  # noqa: BLE001
            last_err = repr(e)
        time.sleep(2 ** attempt)  # 1,2,4,8,16,32s backoff for rate limits
    raise RuntimeError(f"Failed to fetch {symbol}: {last_err}")


def load_prices():
    """Return a DataFrame of daily closes for all tickers (raw, native units)."""
    cache = os.path.join(DATA_DIR, "prices_raw.csv")
    if os.path.exists(cache):
        df = pd.read_csv(cache, index_col=0, parse_dates=True)
        return df
    series = {}
    for name, sym in TICKERS.items():
        series[name] = fetch_series(sym)
        time.sleep(1.5)  # be gentle with the rate limiter
    df = pd.DataFrame(series)
    df.to_csv(cache)
    return df


def to_inr(df):
    """Convert USD-priced legs to INR; align on common trading days."""
    df = df.copy()
    # Forward-fill FX and gold across small gaps, then take the common window.
    df["usdinr"] = df["usdinr"].ffill()
    inr = pd.DataFrame(index=df.index)
    inr["nasdaq100"] = df["nasdaq100"] * df["usdinr"]   # USD index -> INR
    inr["nifty50"] = df["nifty50"]                       # already INR
    inr["gold"] = df["gold"] * df["usdinr"]              # USD gold -> INR
    inr = inr.dropna()
    return inr


def max_drawdown(equity):
    """Maximum drawdown of an equity curve (as a negative fraction)."""
    running_peak = equity.cummax()
    dd = equity / running_peak - 1.0
    trough = dd.idxmin()
    peak = equity.loc[:trough].idxmax()
    return dd.min(), peak, trough


def cagr(equity):
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    return (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1, years


def simulate_rebalanced(prices_inr, weights):
    """
    Simulate a lump-sum portfolio that is reset to `weights` on the last
    trading day of every calendar year. Returns the daily equity curve
    (starting value = 1.0).
    """
    cols = list(prices_inr.columns)
    w = np.array([weights[c] for c in cols], dtype=float)
    px = prices_inr[cols].values
    dates = prices_inr.index

    # A rebalance day is the last trading day of its calendar year:
    # the following day belongs to a different year.
    years = dates.year.values
    is_rebalance_day = np.zeros(len(px), dtype=bool)
    is_rebalance_day[:-1] = years[:-1] != years[1:]

    equity = np.empty(len(px))
    units = w / px[0]             # units bought at inception with 1.0 total
    equity[0] = units @ px[0]
    for i in range(1, len(px)):
        equity[i] = units @ px[i]
        if is_rebalance_day[i]:   # reset to target weights at this close
            units = (equity[i] * w) / px[i]
    return pd.Series(equity, index=dates, name="portfolio")


def metrics_table(prices_inr, portfolio):
    rows = []
    curves = {c: prices_inr[c] / prices_inr[c].iloc[0] for c in prices_inr.columns}
    curves["Portfolio (1/3 each, yearly rebal.)"] = portfolio
    label = {
        "nasdaq100": "Nasdaq-100 (INR)",
        "nifty50": "Nifty 50 (INR)",
        "gold": "Gold (INR)",
    }
    for key, curve in curves.items():
        name = label.get(key, key)
        c, yrs = cagr(curve)
        mdd, peak, trough = max_drawdown(curve)
        rows.append({
            "Instrument": name,
            "CAGR": c,
            "Max Drawdown": mdd,
            "MDD peak": peak.date(),
            "MDD trough": trough.date(),
            "Total x": curve.iloc[-1] / curve.iloc[0],
        })
    return pd.DataFrame(rows), yrs


def main():
    raw = load_prices()
    inr = to_inr(raw)

    start, end = inr.index[0], inr.index[-1]
    inr.to_csv(os.path.join(DATA_DIR, "prices_inr.csv"))

    weights = {"nasdaq100": 1 / 3, "nifty50": 1 / 3, "gold": 1 / 3}
    port = simulate_rebalanced(inr, weights)

    table, yrs = metrics_table(inr, port)

    pd.set_option("display.width", 120)
    pd.set_option("display.max_columns", 20)
    print(f"\nWindow: {start.date()} -> {end.date()}  ({yrs:.1f} years)\n")
    disp = table.copy()
    disp["CAGR"] = (disp["CAGR"] * 100).map("{:.2f}%".format)
    disp["Max Drawdown"] = (disp["Max Drawdown"] * 100).map("{:.1f}%".format)
    disp["Total x"] = disp["Total x"].map("{:.2f}x".format)
    print(disp.to_string(index=False))

    # correlation of annual returns, for context
    ann = inr.resample("YE").last().pct_change().dropna()
    print("\nAnnual-return correlation (INR):")
    print((ann.corr()).round(2).to_string())

    table.to_csv(os.path.join(RESULTS_DIR, "metrics.csv"), index=False)
    make_chart(inr, port)
    return table, port, inr


def make_chart(inr, port):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    curves = {
        "Nasdaq-100 (INR)": inr["nasdaq100"] / inr["nasdaq100"].iloc[0],
        "Nifty 50 (INR)": inr["nifty50"] / inr["nifty50"].iloc[0],
        "Gold (INR)": inr["gold"] / inr["gold"].iloc[0],
        "Portfolio (1/3 each)": port,
    }
    colors = {
        "Nasdaq-100 (INR)": "#7aa2f7",
        "Nifty 50 (INR)": "#e0af68",
        "Gold (INR)": "#bb9af7",
        "Portfolio (1/3 each)": "#f7768e",
    }

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 8), gridspec_kw={"height_ratios": [2.2, 1]},
        sharex=True)

    for name, curve in curves.items():
        lw = 2.6 if "Portfolio" in name else 1.4
        ax1.plot(curve.index, curve.values, label=name,
                 color=colors[name], linewidth=lw)
    ax1.set_yscale("log")
    ax1.set_ylabel("Growth of 1 (log scale)")
    ax1.set_title("Equal-weight Nasdaq-100 + Nifty 50 + Gold, rebalanced yearly (INR)")
    ax1.legend(loc="upper left", frameon=False)
    ax1.grid(True, which="both", alpha=0.25)

    peak = port.cummax()
    dd = (port / peak - 1.0) * 100
    ax2.fill_between(dd.index, dd.values, 0, color="#f7768e", alpha=0.35)
    ax2.plot(dd.index, dd.values, color="#f7768e", linewidth=1.0)
    ax2.set_ylabel("Portfolio drawdown (%)")
    ax2.grid(True, alpha=0.25)

    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, "equity_drawdown.png")
    fig.savefig(out, dpi=130)
    print(f"\nChart saved -> {out}")


if __name__ == "__main__":
    main()
