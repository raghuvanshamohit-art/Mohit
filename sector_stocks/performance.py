"""Compute price-performance (growth %) over 3, 6, 9 and 12 months."""

from __future__ import annotations

from datetime import datetime, timezone

from .yahoo import PriceSeries

# The reporting periods, in months.
PERIODS = [3, 6, 9, 12]


def _months_ago(reference: datetime, months: int) -> datetime:
    """Return ``reference`` shifted back by a whole number of months."""
    month_index = (reference.year * 12 + (reference.month - 1)) - months
    year, month = divmod(month_index, 12)
    month += 1
    # Clamp day to the last valid day of the target month.
    day = reference.day
    while day > 0:
        try:
            return reference.replace(year=year, month=month, day=day)
        except ValueError:
            day -= 1
    return reference.replace(year=year, month=month, day=1)


def _base_price(series: PriceSeries, target: datetime):
    """Adjusted close on the last trading day on or before ``target``.

    Falls back to the earliest available point if the series does not reach
    that far back.
    """
    cutoff = target.timestamp()
    base = None
    base_ts = None
    for ts, px in zip(series.timestamps, series.closes):
        if ts <= cutoff:
            base, base_ts = px, ts
        else:
            break
    if base is None:  # target predates the series -> use earliest point
        base, base_ts = series.closes[0], series.timestamps[0]
    return base, base_ts


def compute_returns(series: PriceSeries, now: datetime | None = None) -> dict:
    """Return a dict of performance metrics for one price series."""
    if now is None:
        now = datetime.now(timezone.utc)

    latest_px = series.closes[-1]
    latest_ts = series.timestamps[-1]

    returns = {}
    coverage = {}
    for months in PERIODS:
        target = _months_ago(now, months)
        base, base_ts = _base_price(series, target)
        pct = (latest_px / base - 1.0) * 100.0 if base else None
        returns[f"{months}m"] = round(pct, 2) if pct is not None else None
        # How many days of history actually backed this figure.
        coverage[f"{months}m"] = round((latest_ts - base_ts) / 86400.0, 1)

    return {
        "price": round(latest_px, 2),
        "currency": series.currency,
        "as_of": datetime.fromtimestamp(latest_ts, tz=timezone.utc).strftime("%Y-%m-%d"),
        "returns": returns,
        "coverage_days": coverage,
        "history_days": round((latest_ts - series.timestamps[0]) / 86400.0, 1),
    }


def average_returns(members: list) -> dict:
    """Equal-weighted average return per period across a list of stock dicts.

    ``members`` are per-stock result dicts (each with a ``returns`` map). Only
    stocks that fetched successfully contribute.
    """
    agg = {}
    for months in PERIODS:
        key = f"{months}m"
        vals = [
            m["returns"][key]
            for m in members
            if m.get("returns") and m["returns"].get(key) is not None
        ]
        agg[key] = round(sum(vals) / len(vals), 2) if vals else None
    return agg
