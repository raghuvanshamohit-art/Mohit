"""Pyramiding: how to add to a winner on the way up — with discipline.

Implements the framework's stock rule: **let profits run, add as price rises,
but only while price stays sensibly below intrinsic value.** Classic pyramiding
uses *decreasing* add sizes as price climbs, so the average cost stays well
below the current price and the position is not top-heavy.

The plan:

* Rungs are spaced ``step`` above each other (e.g. +8% per rung).
* Each rung's size *decays* (e.g. ×0.65), so the cheapest buy is the biggest.
* Adding **stops** at the rung where price would reach ``cap × intrinsic_value``
  — the gate that keeps you from pyramiding into an overvalued price.
* A trailing **stop-loss** is tracked off the running average cost.

This protects the thing that kills most pyramids: averaging *up* so fast that a
pullback wipes the gain.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Rung:
    n: int
    price: float
    weight: float            # fraction of budget intended for this rung
    amount: float            # currency deployed at this rung
    shares: float
    cum_shares: float
    cum_cost: float
    avg_cost: float          # running average cost after this rung
    unrealized_pct: float    # price vs running average cost, %
    stop_price: float        # trailing stop off the running average cost


@dataclass
class PyramidPlan:
    entry_price: float
    intrinsic_value: float
    budget: float
    rungs: List[Rung]
    deployed: float
    uninvested: float         # budget not deployed because adds hit the cap
    final_avg_cost: float
    final_shares: float
    avg_cost_mos: float       # margin of safety of the avg cost vs intrinsic
    note: str


def pyramid_plan(
    entry_price: float,
    intrinsic_value: float,
    budget: float,
    tranches: int = 5,
    step: float = 0.08,
    decay: float = 0.65,
    stop_loss: float = 0.15,
    cap: float = 1.0,
) -> PyramidPlan:
    """Build a pyramiding ladder.

    Args:
        entry_price: price of the first (base) buy.
        intrinsic_value: your estimate of fair value (see ``valuation``).
        budget: total capital earmarked for the full position.
        tranches: number of rungs to attempt.
        step: price rise between rungs, as a decimal (0.08 == +8%).
        decay: size multiplier per rung (0.65 → each add is 65% of the last).
        stop_loss: trailing stop below running average cost (0.15 == 15%).
        cap: stop adding once a rung's price reaches ``cap × intrinsic_value``
            (1.0 == stop at intrinsic value; 0.9 == keep a 10% cushion).

    Rungs above the cap are dropped and their intended budget is left
    uninvested rather than spent into an overvalued price.
    """
    if entry_price <= 0 or budget <= 0:
        raise ValueError("entry_price and budget must be positive")
    if intrinsic_value <= 0:
        raise ValueError("intrinsic_value must be positive")

    ceiling = cap * intrinsic_value

    # Candidate rung prices and their sizes. Weights decay across *all* planned
    # tranches and are fixed up front — so a rung dropped for breaching the
    # valuation ceiling leaves its share as uninvested dry powder rather than
    # being crammed into the cheaper rungs.
    prices = [entry_price * (1.0 + step) ** i for i in range(tranches)]
    raw_weights = [decay ** i for i in range(tranches)]
    wsum = sum(raw_weights)
    weights = [w / wsum for w in raw_weights]

    # Keep only rungs at or below the valuation ceiling.
    kept = [(p, weights[i]) for i, p in enumerate(prices) if p <= ceiling]
    if not kept:
        # Even the entry is above the ceiling — nothing to do.
        return PyramidPlan(
            entry_price, intrinsic_value, budget, [], 0.0, budget,
            0.0, 0.0, 0.0,
            note=f"entry price {entry_price:.2f} is already above "
                 f"{cap:.0%} of intrinsic value ({ceiling:.2f}); do not buy.",
        )

    cum_shares = cum_cost = 0.0
    rungs: List[Rung] = []
    for i, (price, weight) in enumerate(kept):
        amount = budget * weight
        shares = amount / price
        cum_shares += shares
        cum_cost += amount
        avg_cost = cum_cost / cum_shares
        rungs.append(Rung(
            n=i + 1,
            price=round(price, 2),
            weight=round(weight, 4),
            amount=round(amount, 2),
            shares=round(shares, 4),
            cum_shares=round(cum_shares, 4),
            cum_cost=round(cum_cost, 2),
            avg_cost=round(avg_cost, 2),
            unrealized_pct=round((price / avg_cost - 1.0) * 100.0, 2),
            stop_price=round(avg_cost * (1.0 - stop_loss), 2),
        ))

    deployed = cum_cost
    final_avg = cum_cost / cum_shares
    avg_mos = (intrinsic_value - final_avg) / intrinsic_value

    dropped = tranches - len(kept)
    if dropped:
        note = (f"{dropped} of {tranches} rungs skipped — they breached "
                f"{cap:.0%} of intrinsic value ({ceiling:.2f}). Let the winner "
                f"run, but don't pyramid above value.")
    else:
        note = (f"All {tranches} rungs sit below {cap:.0%} of intrinsic value "
                f"({ceiling:.2f}).")

    return PyramidPlan(
        entry_price=entry_price,
        intrinsic_value=intrinsic_value,
        budget=budget,
        rungs=rungs,
        deployed=round(deployed, 2),
        uninvested=round(budget - deployed, 2),
        final_avg_cost=round(final_avg, 2),
        final_shares=round(cum_shares, 4),
        avg_cost_mos=round(avg_mos, 4),
        note=note,
    )
