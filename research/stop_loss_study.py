#!/usr/bin/env python3
"""How reliable is a ratchet (trailing) stop-loss?

Rule tested: after buying, track the highest close since entry. Sell at the
close of the first day the price closes X% or more below that peak. The stop
only ever moves up ("ratchets"). After a stop-out the money sits in cash.

Simulation: a trade is opened in every stock at every month-end and held for
HORIZON trading days. Each trade is run twice, with the stop and without it
(plain buy-and-hold), and the two outcomes are compared.

    python research/fetch_history.py    # once
    python research/stop_loss_study.py  # -> research/results/stop_loss_*.csv
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PRICES = HERE / "cache" / "prices.csv"
RESULTS = HERE / "results"
BENCH = "NIFTY50"
COST_ONE_WAY = 0.002
CASH_RATE = 0.065                  # annual return on cash after a stop-out (liquid fund)
STOPS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40]
HORIZONS = {"6m": 126, "12m": 252, "24m": 504}
MIN_HISTORY = 252                  # need 1y history to score momentum
# A one-day drop this large is almost always an unadjusted split/bonus/demerger
# in the Yahoo data, not a real loss; trades spanning one are dropped.
DATA_BREAK = -0.45


def simulate(px: np.ndarray, entries: "list[int]", horizon: int, stop: float, eligible=None, breaks=None):
    """Return one row per (entry, stock) trade."""
    rows = []
    daily_cash = (1 + CASH_RATE) ** (1 / 252) - 1
    for e in entries:
        win = px[e:e + horizon + 1]
        if len(win) < horizon + 1:
            continue
        p0 = win[0]
        ok = ~np.isnan(p0) & ~np.isnan(win[-1])
        if eligible is not None:
            ok &= eligible[e]
        if breaks is not None:
            ok &= ~breaks[e + 1:e + horizon + 1].any(axis=0)
        if not ok.any():
            continue
        w = win[:, ok]
        w = pd.DataFrame(w).ffill().to_numpy()
        rel = w / w[0]
        peak = np.maximum.accumulate(rel, axis=0)
        hold = rel[-1] - 1 - 2 * COST_ONE_WAY
        breach = rel <= peak * (1 - stop)
        hit = breach.any(axis=0)
        idx = np.where(hit, breach.argmax(axis=0), horizon)
        exit_rel = rel[idx, np.arange(rel.shape[1])]
        days_in_cash = horizon - idx
        stopped = np.where(hit, (exit_rel * (1 + daily_cash) ** days_in_cash) - 1 - 2 * COST_ONE_WAY, hold)
        # How far below the stop level the exit actually happened (gap / slippage).
        stop_level = peak[idx, np.arange(rel.shape[1])] * (1 - stop)
        gap = np.where(hit, exit_rel / stop_level - 1, np.nan)
        # Worst peak-to-trough while holding with no stop.
        mdd = (rel / peak - 1).min(axis=0)
        rows.append(pd.DataFrame({
            "entry": e, "hold": hold, "stop": stopped, "hit": hit,
            "exit_gap": gap, "hold_mdd": mdd,
        }))
    return pd.concat(rows, ignore_index=True)


def summarise(t: pd.DataFrame) -> dict:
    hit = t[t["hit"]]
    diff = t["stop"] - t["hold"]
    return {
        "trades": len(t),
        "% stopped out": t["hit"].mean() * 100,
        "Avg return hold %": t["hold"].mean() * 100,
        "Avg return stop %": t["stop"].mean() * 100,
        "Median hold %": t["hold"].median() * 100,
        "Median stop %": t["stop"].median() * 100,
        "Worst 5% hold %": t["hold"].quantile(0.05) * 100,
        "Worst 5% stop %": t["stop"].quantile(0.05) * 100,
        "Worst 1% hold %": t["hold"].quantile(0.01) * 100,
        "Worst 1% stop %": t["stop"].quantile(0.01) * 100,
        "% trades stop beat hold": (diff > 1e-9).mean() * 100,
        # Of the trades that got stopped: how often was selling a mistake?
        "Whipsaw % (stopped, hold did better)": (hit["hold"] > hit["stop"]).mean() * 100 if len(hit) else np.nan,
        "Avg gap below stop %": hit["exit_gap"].mean() * 100 if len(hit) else np.nan,
        "Worst gap below stop %": hit["exit_gap"].min() * 100 if len(hit) else np.nan,
    }


def main():
    px_df = pd.read_csv(PRICES, index_col="date", parse_dates=True).sort_index()
    px_df = px_df.ffill(limit=5)
    stocks = px_df.drop(columns=[BENCH])
    px = stocks.to_numpy(dtype=float)
    dates = stocks.index
    with np.errstate(invalid="ignore", divide="ignore"):
        breaks = np.nan_to_num(px[1:] / pd.DataFrame(px).ffill().to_numpy()[:-1] - 1) < DATA_BREAK
    breaks = np.vstack([np.zeros((1, px.shape[1]), bool), breaks])

    month_end = pd.Series(np.arange(len(dates)), index=dates).resample("ME").last().dropna().astype(int)
    entries = [i for i in month_end.values if i >= MIN_HISTORY]

    # Momentum 12-1m top-quintile flag at each day, to test the stop on "good" picks.
    mom = stocks.shift(21) / stocks.shift(252) - 1
    rank = mom.rank(axis=1, pct=True)
    top_q = (rank >= 0.8).to_numpy()

    rows = []
    for universe, elig in [("All stocks", None), ("Momentum top 20%", top_q)]:
        for hname, h in HORIZONS.items():
            for s in STOPS:
                t = simulate(px, entries, h, s, elig, breaks)
                rows.append({"Universe": universe, "Horizon": hname, "Stop %": int(s * 100), **summarise(t)})
                if universe == "All stocks" and hname == "12m" and s == 0.20:
                    t["entry_date"] = dates[t["entry"]]
                    by_year = t.groupby(t["entry_date"].dt.year).apply(
                        lambda g: pd.Series({
                            "% stopped": g["hit"].mean() * 100,
                            "Avg hold %": g["hold"].mean() * 100,
                            "Avg stop %": g["stop"].mean() * 100,
                            "Stop minus hold (pp)": (g["stop"] - g["hold"]).mean() * 100,
                        }), include_groups=False)
    res = pd.DataFrame(rows)

    RESULTS.mkdir(exist_ok=True)
    res.round(2).to_csv(RESULTS / "stop_loss_summary.csv", index=False)
    by_year.round(2).to_csv(RESULTS / "stop_loss_by_entry_year.csv")

    pd.set_option("display.width", 250, "display.max_columns", 30)
    cols = ["Universe", "Horizon", "Stop %", "% stopped out", "Avg return hold %", "Avg return stop %",
            "Median hold %", "Median stop %", "Worst 5% hold %", "Worst 5% stop %",
            "Worst 1% hold %", "Worst 1% stop %",
            "Whipsaw % (stopped, hold did better)", "Avg gap below stop %", "Worst gap below stop %"]
    print(res[cols].round(1).to_string(index=False))
    print("\n=== 20% stop, 12m horizon, all stocks: by entry year ===")
    print(by_year.round(1).to_string())


if __name__ == "__main__":
    main()
