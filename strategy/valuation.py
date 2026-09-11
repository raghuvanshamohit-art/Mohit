"""Intrinsic value, margin of safety, and a buy/hold/avoid verdict.

Implements Lens 2 of the framework ("price is what you pay, value is what you
get"):

* A multi-stage **discounted cash-flow** on a per-share cash proxy (EPS or
  free cash flow / share): grow the cash through one or more explicit stages,
  then a Gordon terminal value, and discount everything back.
* The **discount rate is the bond market plus a risk premium** — exactly the
  framework's "if you don't understand bonds, you don't understand anything."
  Raise rates and the *price* you should pay falls, though the *value* of the
  business is unchanged.
* **Margin of safety** = how far price sits below intrinsic value, and a verdict
  from configurable bands.
* **Implied growth** (reverse DCF): the stage-1 growth the current price already
  bakes in — the guard against repeating the 2024 mistake of paying for a growth
  rate that cannot last.

All rates are decimals (0.12 == 12%). Monetary inputs are per share.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

# Verdict bands on margin of safety (intrinsic − price) / intrinsic.
# Pay meaningfully below value; treat "fair" as hold; refuse to overpay.
DEFAULT_BANDS = (
    (0.30, "BUY — strong margin of safety"),
    (0.10, "ACCUMULATE — modest margin of safety"),
    (-0.10, "HOLD — roughly fairly valued"),
    (float("-inf"), "AVOID — price above intrinsic value"),
)


def required_return(bond_yield: float, equity_risk_premium: float = 0.05) -> float:
    """Discount rate = risk-free (10Y G-sec) yield + an equity risk premium.

    This is how interest rates enter valuation. When the bond market reprices
    rates up, the discount rate rises and intrinsic value falls — the framework's
    shop example, where an RBI hike turned a ₹1cr shop into an ₹80L one.
    """
    return bond_yield + equity_risk_premium


@dataclass
class Stage:
    """One explicit growth stage: ``growth`` per year for ``years`` years."""
    growth: float
    years: int


@dataclass
class Valuation:
    intrinsic_value: float
    price: Optional[float]
    margin_of_safety: Optional[float]      # (intrinsic − price) / intrinsic
    verdict: Optional[str]
    pv_explicit: float                     # PV of the explicit-stage cash flows
    pv_terminal: float                     # PV of the Gordon terminal value
    terminal_share: float                  # fraction of value from the terminal
    cashflows: List[Tuple[int, float, float]] = field(default_factory=list)
    # each row: (year, undiscounted cash flow, discounted cash flow)


def intrinsic_value(
    base_cashflow: float,
    stages: Sequence[Stage],
    terminal_growth: float,
    discount: float,
) -> Valuation:
    """Multi-stage DCF on a per-share cash proxy (EPS or FCF/share).

    ``base_cashflow`` is the most recent trailing figure; year-1 cash flow is it
    grown by the first stage's rate. After the explicit stages, a Gordon growth
    terminal value caps it off.

    Raises ``ValueError`` if the discount rate does not exceed terminal growth
    (the Gordon formula diverges otherwise) or if no stages are given.
    """
    if not stages:
        raise ValueError("need at least one growth stage")
    if discount <= terminal_growth:
        raise ValueError(
            f"discount rate ({discount:.2%}) must exceed terminal growth "
            f"({terminal_growth:.2%}); otherwise value is infinite"
        )

    cf = base_cashflow
    pv_explicit = 0.0
    year = 0
    rows: List[Tuple[int, float, float]] = []
    for stage in stages:
        for _ in range(stage.years):
            year += 1
            cf *= (1.0 + stage.growth)
            discounted = cf / (1.0 + discount) ** year
            pv_explicit += discounted
            rows.append((year, cf, discounted))

    # Gordon terminal value at the end of the last explicit year.
    terminal_cf = cf * (1.0 + terminal_growth)
    terminal_value = terminal_cf / (discount - terminal_growth)
    pv_terminal = terminal_value / (1.0 + discount) ** year

    value = pv_explicit + pv_terminal
    return Valuation(
        intrinsic_value=value,
        price=None,
        margin_of_safety=None,
        verdict=None,
        pv_explicit=pv_explicit,
        pv_terminal=pv_terminal,
        terminal_share=(pv_terminal / value) if value else 0.0,
        cashflows=rows,
    )


def margin_of_safety(intrinsic: float, price: float) -> float:
    """How far price sits below intrinsic value. Positive == a discount."""
    if intrinsic <= 0:
        return float("-inf")
    return (intrinsic - price) / intrinsic


def verdict(mos: float, bands=DEFAULT_BANDS) -> str:
    """Map a margin of safety to a verdict using descending thresholds."""
    for threshold, label in bands:
        if mos >= threshold:
            return label
    return bands[-1][1]


def value_stock(
    base_cashflow: float,
    stages: Sequence[Stage],
    terminal_growth: float,
    discount: float,
    price: Optional[float] = None,
    bands=DEFAULT_BANDS,
) -> Valuation:
    """Full valuation: intrinsic value plus, if ``price`` is given, the margin
    of safety and verdict."""
    v = intrinsic_value(base_cashflow, stages, terminal_growth, discount)
    if price is not None:
        v.price = price
        v.margin_of_safety = margin_of_safety(v.intrinsic_value, price)
        v.verdict = verdict(v.margin_of_safety, bands)
    return v


def implied_growth(
    base_cashflow: float,
    price: float,
    years: int,
    terminal_growth: float,
    discount: float,
    lo: float = -0.50,
    hi: float = 1.00,
    tol: float = 1e-5,
    max_iter: int = 200,
) -> Optional[float]:
    """Reverse DCF: the single stage-1 growth rate that makes intrinsic value
    equal today's ``price`` (one explicit stage of ``years`` years, then the
    terminal). Tells you what the market is already assuming.

    Returns ``None`` if no solution exists within ``[lo, hi]`` (e.g. the price is
    below even a no-growth value, or above what 100%+ growth can justify).
    Value is monotically increasing in growth, so a simple bisection converges.
    """
    def iv(g: float) -> float:
        return intrinsic_value(
            base_cashflow, [Stage(g, years)], terminal_growth, discount
        ).intrinsic_value

    f_lo, f_hi = iv(lo) - price, iv(hi) - price
    if f_lo > 0 or f_hi < 0:
        return None  # price is outside the range this model can reach

    for _ in range(max_iter):
        mid = (lo + hi) / 2.0
        f_mid = iv(mid) - price
        if abs(f_mid) < tol or (hi - lo) < tol:
            return mid
        if f_mid < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0
