"""Asset allocation and counter-trend rebalancing.

Implements the framework's headline rule — "~92% of your success comes from
asset allocation, not stock picking or timing" — and its mechanic: **sell the
sleeve that has run up, add to the sleeve that has fallen.**

* ``PROFILES``        — ready target mixes (aggressive / balanced / conservative),
  with gold sized as insurance (10% aggressive → 20% conservative).
* ``glide_targets``   — shifts equity into bonds as the goal nears ("slow down
  as you approach the destination").
* ``rebalance``       — compares holdings to target and emits SELL/BUY actions for
  any sleeve that has drifted beyond a tolerance band.
* ``invest_new_money``— directs fresh cash to the most-underweight sleeves first,
  rebalancing without selling (no tax, no friction).

Weights are decimals that sum to 1.0. Holdings are current market values.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

# Target mixes from the framework. Gold is insurance, not a wealth engine:
# ~10% when aggressive (equity-tilted), up to ~20% when conservative.
PROFILES: Dict[str, Dict[str, float]] = {
    "aggressive":   {"equity": 0.80, "gold": 0.10, "bonds": 0.10},
    "balanced":     {"equity": 0.65, "gold": 0.15, "bonds": 0.20},
    "conservative": {"equity": 0.60, "gold": 0.20, "bonds": 0.20},
}

GLIDE_START_YEARS = 15  # begin shifting equity → bonds this many years out


def normalize(weights: Dict[str, float]) -> Dict[str, float]:
    """Scale weights to sum to 1.0 (accepts percentages or raw ratios)."""
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("weights must sum to a positive number")
    return {k: v / total for k, v in weights.items()}


def glide_targets(
    base: Dict[str, float],
    years_to_goal: float,
    glide_start: int = GLIDE_START_YEARS,
) -> Dict[str, float]:
    """Shift equity into bonds as the goal nears.

    At ``years_to_goal >= glide_start`` the base mix is untouched. As the goal
    approaches 0, equity is progressively moved into bonds; gold is held steady.
    Mirrors cutting speed entering the city, the colony, the lane, the gate.
    """
    base = normalize(base)
    if years_to_goal >= glide_start:
        return base
    frac = max(0.0, years_to_goal) / glide_start  # 1.0 far out → 0.0 at the goal
    equity = base.get("equity", 0.0)
    new_equity = equity * frac
    moved = equity - new_equity
    out = dict(base)
    out["equity"] = new_equity
    out["bonds"] = base.get("bonds", 0.0) + moved
    return normalize(out)


@dataclass
class Action:
    asset: str
    side: str            # "SELL", "BUY", or "HOLD"
    amount: float        # currency amount to trade (0 for HOLD)
    current_weight: float
    target_weight: float
    drift: float         # current_weight − target_weight


def rebalance(
    holdings: Dict[str, float],
    targets: Dict[str, float],
    band: float = 0.05,
) -> List[Action]:
    """Counter-trend rebalance: trim what's overweight, add to what's underweight.

    ``band`` is the tolerance (decimal) a sleeve may drift before it's acted on —
    a 5% band means a sleeve is left alone until it is >5 percentage points off
    target. Returns one ``Action`` per asset (the union of holdings and targets),
    SELL/BUY actions first and largest-drift first.
    """
    targets = normalize(targets)
    total = sum(holdings.values())
    assets = sorted(set(holdings) | set(targets))
    actions: List[Action] = []
    for asset in assets:
        value = holdings.get(asset, 0.0)
        tgt_w = targets.get(asset, 0.0)
        cur_w = (value / total) if total else 0.0
        drift = cur_w - tgt_w
        target_value = tgt_w * total
        if abs(drift) <= band:
            side, amount = "HOLD", 0.0
        elif drift > 0:
            side, amount = "SELL", value - target_value
        else:
            side, amount = "BUY", target_value - value
        actions.append(Action(asset, side, round(amount, 2), cur_w, tgt_w, drift))

    actions.sort(key=lambda a: (a.side == "HOLD", -abs(a.drift)))
    return actions


def invest_new_money(
    holdings: Dict[str, float],
    targets: Dict[str, float],
    amount: float,
) -> List[Action]:
    """Allocate fresh cash to close the biggest underweights first (buy-only).

    The friction-free way to rebalance: instead of selling winners, point new
    contributions at the sleeves furthest below target until the cash is spent.
    Returns BUY actions (plus HOLD for sleeves that got nothing).
    """
    if amount <= 0:
        raise ValueError("new-money amount must be positive")
    targets = normalize(targets)
    future_total = sum(holdings.values()) + amount
    assets = sorted(set(holdings) | set(targets))

    # Shortfall = how far below its future target value each sleeve is now.
    shortfalls = {
        a: max(0.0, targets.get(a, 0.0) * future_total - holdings.get(a, 0.0))
        for a in assets
    }
    total_short = sum(shortfalls.values())

    actions: List[Action] = []
    for asset in assets:
        value = holdings.get(asset, 0.0)
        tgt_w = targets.get(asset, 0.0)
        cur_w = (value / future_total) if future_total else 0.0
        # Spread the cash in proportion to each sleeve's shortfall.
        buy = (amount * shortfalls[asset] / total_short) if total_short else 0.0
        side = "BUY" if buy > 0 else "HOLD"
        actions.append(Action(asset, side, round(buy, 2), cur_w, tgt_w, cur_w - tgt_w))

    actions.sort(key=lambda a: (a.side == "HOLD", -a.amount))
    return actions
