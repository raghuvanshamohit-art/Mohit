"""Pyramiding plans — laddered entries around an intrinsic value.

*Pyramiding* means building a position in several tranches instead of one lump
buy. This module builds two kinds of ladder:

* :func:`build_pyramid` — **value accumulation**. Buy the first tranche once the
  price is a margin of safety below intrinsic value, and buy successively larger
  tranches at deeper discounts. The cheaper (and safer) it gets, the more you
  commit — the base of the pyramid is the widest. This is the value investor's
  scale-in and is the default.

* :func:`build_trend_pyramid` — **classic trend pyramiding**. Start from an
  entry and *add to a winner* as it rises, each add smaller than the last, with
  a stop trailing up under the position. This is the trend-follower's pyramid.

Both return plain dicts (JSON-friendly) describing every tranche plus a summary:
blended average entry, effective margin of safety, and — when a capital budget
is supplied — whole-share sizing per tranche and a suggested stop-loss.

Not investment advice. Sizing math assumes whole shares and ignores costs/taxes.
"""

from __future__ import annotations

DEFAULT_MARGIN_OF_SAFETY = 0.30  # first tranche buys at 30% below intrinsic value
DEFAULT_STEP = 0.10              # each further tranche is 10 pts deeper/higher
DEFAULT_TRANCHES = 3
DEFAULT_STOP_PCT = 0.10          # stop this far below the lowest planned entry


def _weights(n: int, scheme: str) -> list:
    """Return ``n`` allocation weights (summing to 1) for a scheme.

    * ``increasing`` — bigger tranches as price falls (value accumulation base).
    * ``equal``      — same size every tranche (dollar-cost style).
    * ``decreasing`` — smaller tranches as you go (classic add-to-winner shape).
    """
    if n <= 0:
        return []
    if scheme == "equal":
        raw = [1.0] * n
    elif scheme == "decreasing":
        raw = [float(n - i) for i in range(n)]        # n, n-1, ..., 1
    else:  # "increasing" (default)
        raw = [float(i + 1) for i in range(n)]        # 1, 2, ..., n
    total = sum(raw)
    return [w / total for w in raw]


def _size_tranches(tranches, capital):
    """Fill in whole-share sizing for a capital budget; returns portfolio totals."""
    total_cost = 0.0
    total_shares = 0
    for t in tranches:
        budget = capital * t["weight"]
        shares = int(budget // t["price"]) if t["price"] > 0 else 0
        cost = round(shares * t["price"], 2)
        t["budget"] = round(budget, 2)
        t["shares"] = shares
        t["cost"] = cost
        total_cost += cost
        total_shares += shares
    return total_shares, round(total_cost, 2)


def build_pyramid(intrinsic_value, *, margin_of_safety=DEFAULT_MARGIN_OF_SAFETY,
                  tranches=DEFAULT_TRANCHES, step=DEFAULT_STEP,
                  weighting="increasing", capital=None,
                  current_price=None, stop_pct=DEFAULT_STOP_PCT) -> dict:
    """Build a value-accumulation pyramid below ``intrinsic_value``.

    Tranche *i* (0-indexed) buys at a discount of ``margin_of_safety + i*step``
    to intrinsic value, so entries step *down*. Weights follow ``weighting``
    (default ``increasing`` — commit more the cheaper it gets).

    Parameters
    ----------
    intrinsic_value : float
        Fair value per share (e.g. the composite from :mod:`intrinsic`).
    margin_of_safety : float
        Discount of the first (shallowest) tranche, as a decimal.
    tranches : int
        Number of buy levels.
    step : float
        Extra discount added per subsequent tranche, as a decimal.
    weighting : str
        ``increasing`` | ``equal`` | ``decreasing``.
    capital : float, optional
        Total budget; when given, each tranche is sized in whole shares.
    current_price : float, optional
        Latest price, reported alongside each level (how far below to wait).
    stop_pct : float
        Suggested stop-loss below the deepest tranche, as a decimal.

    Returns
    -------
    dict
        ``mode``, ``tranches`` (list) and ``summary``.
    """
    if intrinsic_value is None or intrinsic_value <= 0:
        raise ValueError("intrinsic_value must be a positive number")
    if tranches < 1:
        raise ValueError("tranches must be >= 1")

    weights = _weights(tranches, weighting)
    rows = []
    for i in range(tranches):
        discount = margin_of_safety + i * step
        discount = min(discount, 0.95)  # keep prices positive/sane
        price = round(intrinsic_value * (1.0 - discount), 2)
        row = {
            "level": i + 1,
            "discount_to_intrinsic": round(discount * 100.0, 2),  # %
            "price": price,
            "weight": round(weights[i], 4),
            "weight_pct": round(weights[i] * 100.0, 2),
        }
        if current_price and current_price > 0:
            row["below_current_pct"] = round((price / current_price - 1.0) * 100.0, 2)
            row["triggered"] = current_price <= price  # already at/under this level
        rows.append(row)

    # Blended average entry (capital-weighted by plan weights).
    avg_entry = round(sum(r["price"] * w for r, w in zip(rows, weights)), 2)
    deepest_price = rows[-1]["price"]
    stop_loss = round(deepest_price * (1.0 - stop_pct), 2)

    summary = {
        "intrinsic_value": round(intrinsic_value, 2),
        "num_tranches": tranches,
        "weighting": weighting,
        "avg_entry_price": avg_entry,
        "effective_margin_of_safety": round((1.0 - avg_entry / intrinsic_value) * 100.0, 2),
        "upside_to_intrinsic_at_avg": round((intrinsic_value / avg_entry - 1.0) * 100.0, 2),
        "stop_loss": stop_loss,
        "risk_per_share_from_avg": round(avg_entry - stop_loss, 2),
        "current_price": current_price,
    }

    if capital and capital > 0:
        total_shares, total_cost = _size_tranches(rows, capital)
        summary["capital"] = round(capital, 2)
        summary["planned_shares"] = total_shares
        summary["planned_cost"] = total_cost
        summary["cash_deployed_pct"] = (
            round(total_cost / capital * 100.0, 2) if capital else None)
        if total_shares:
            realized_avg = round(total_cost / total_shares, 2)
            summary["realized_avg_entry"] = realized_avg
            summary["max_risk"] = round((realized_avg - stop_loss) * total_shares, 2)

    return {
        "mode": "value_accumulate",
        "description": (
            "Scale in below intrinsic value; buy larger tranches at deeper "
            "discounts (base of the pyramid is widest)."),
        "tranches": rows,
        "summary": summary,
    }


def build_trend_pyramid(entry_price, *, tranches=DEFAULT_TRANCHES,
                        step=DEFAULT_STEP, weighting="decreasing",
                        capital=None, trail_pct=DEFAULT_STOP_PCT,
                        intrinsic_value=None) -> dict:
    """Build a classic add-to-winner pyramid *above* ``entry_price``.

    Tranche *i* adds at ``entry_price * (1 + i*step)`` — entries step *up* as the
    trade proves right — with ``decreasing`` weights by default so each add is
    smaller than the last (the textbook pyramid shape). A stop trails
    ``trail_pct`` under the latest fill.
    """
    if entry_price is None or entry_price <= 0:
        raise ValueError("entry_price must be a positive number")
    if tranches < 1:
        raise ValueError("tranches must be >= 1")

    weights = _weights(tranches, weighting)
    rows = []
    for i in range(tranches):
        rise = i * step
        price = round(entry_price * (1.0 + rise), 2)
        row = {
            "level": i + 1,
            "above_entry_pct": round(rise * 100.0, 2),
            "price": price,
            "weight": round(weights[i], 4),
            "weight_pct": round(weights[i] * 100.0, 2),
            "trailing_stop": round(price * (1.0 - trail_pct), 2),
        }
        if intrinsic_value and intrinsic_value > 0:
            row["premium_to_intrinsic_pct"] = round(
                (price / intrinsic_value - 1.0) * 100.0, 2)
        rows.append(row)

    avg_entry = round(sum(r["price"] * w for r, w in zip(rows, weights)), 2)
    top_price = rows[-1]["price"]
    final_stop = round(top_price * (1.0 - trail_pct), 2)

    summary = {
        "base_entry_price": round(entry_price, 2),
        "num_tranches": tranches,
        "weighting": weighting,
        "avg_entry_price": avg_entry,
        "final_trailing_stop": final_stop,
        "risk_per_share_from_avg": round(avg_entry - final_stop, 2),
        "intrinsic_value": round(intrinsic_value, 2) if intrinsic_value else None,
    }
    if capital and capital > 0:
        total_shares, total_cost = _size_tranches(rows, capital)
        summary["capital"] = round(capital, 2)
        summary["planned_shares"] = total_shares
        summary["planned_cost"] = total_cost

    return {
        "mode": "trend_pyramid",
        "description": (
            "Add to a winner as it rises; each add smaller than the last, stop "
            "trailing up under the position."),
        "tranches": rows,
        "summary": summary,
    }
