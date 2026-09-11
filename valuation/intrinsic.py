"""Intrinsic-value estimation from fundamentals.

Every model here is a small, pure function with no I/O, so the maths is easy to
read and to unit-test. A model returns ``None`` when the inputs it needs are
missing or nonsensical (e.g. a negative EPS for the Graham Number), rather than
guessing — partial data stays visible instead of producing a fake number.

Conventions
-----------
* Rates (growth, discount, terminal growth, dividend growth) are **decimals**:
  10% is ``0.10``.
* ``Fundamentals`` is the single input bag; the composite function decides which
  models it can run from the fields that are present.

None of this is investment advice. Intrinsic value is an estimate whose output
is only as good as the growth and discount-rate assumptions fed in.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from statistics import median

# Graham's constants for the Graham Number: max defensive P/E (15) x max P/B
# (1.5) = 22.5. The square root of (22.5 x EPS x BVPS) is the ceiling price a
# defensive investor should pay.
GRAHAM_PE_PB = 22.5

# Graham's revised-formula constants.
GRAHAM_BASE_PE = 8.5          # P/E for a no-growth company
GRAHAM_GROWTH_MULT = 2.0      # weight on the growth term (2 x g)
GRAHAM_BASE_BOND_YIELD = 4.4  # AAA corporate-bond yield when Graham set the rule

# Sensible defaults for the forward-looking models.
DEFAULT_DISCOUNT_RATE = 0.12   # required annual return (a.k.a. hurdle rate)
DEFAULT_TERMINAL_GROWTH = 0.03  # perpetual growth after the projection horizon
DEFAULT_YEARS = 10             # projection horizon for DCF / earnings power
DEFAULT_MARGIN_OF_SAFETY = 0.30  # Graham's classic 30% discount to fair value


@dataclass
class Fundamentals:
    """Per-share inputs an intrinsic-value estimate can draw on.

    Only what a given model needs must be set; unset fields simply switch that
    model off. Rates are decimals (0.10 == 10%).
    """

    symbol: str = ""
    name: str = ""
    currency: str = ""

    # Core per-share figures.
    eps: "float | None" = None                 # trailing earnings per share
    book_value_per_share: "float | None" = None  # BVPS
    fcf_per_share: "float | None" = None       # free cash flow per share
    dividend_per_share: "float | None" = None  # trailing dividend per share

    # Assumptions.
    growth_rate: "float | None" = None         # expected near-term annual growth
    terminal_growth: float = DEFAULT_TERMINAL_GROWTH
    discount_rate: float = DEFAULT_DISCOUNT_RATE
    dividend_growth: "float | None" = None     # if unset, falls back to growth_rate
    years: int = DEFAULT_YEARS

    # Multiples / market inputs.
    fair_pe: "float | None" = None             # exit P/E for the earnings-power model
    bond_yield: float = GRAHAM_BASE_BOND_YIELD  # current AAA yield (%) for Graham revised
    growth_cap: "float | None" = 0.15          # cap growth used by Graham revised (decimal)

    current_price: "float | None" = None       # latest market price, for comparison
    shares_outstanding: "float | None" = None

    # Free-form notes about where each value came from (fetched / supplied / default).
    provenance: dict = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Individual models. Each returns a float, or None when it cannot be computed.
# --------------------------------------------------------------------------- #

def graham_number(eps, book_value_per_share):
    """Graham Number — the defensive ceiling price ``sqrt(22.5 x EPS x BVPS)``.

    Requires positive EPS and BVPS (the model is undefined for loss-making or
    negative-equity companies).
    """
    if eps is None or book_value_per_share is None:
        return None
    if eps <= 0 or book_value_per_share <= 0:
        return None
    return math.sqrt(GRAHAM_PE_PB * eps * book_value_per_share)


def graham_revised(eps, growth_rate, bond_yield=GRAHAM_BASE_BOND_YIELD,
                   growth_cap=None):
    """Graham's revised intrinsic-value formula.

    ``V = EPS x (8.5 + 2g) x 4.4 / Y`` where ``g`` is the expected annual growth
    **in percent** and ``Y`` the current AAA corporate-bond yield (%). The
    ``4.4`` re-bases the formula to today's rates.

    ``growth_rate`` is passed as a decimal (0.10) and converted internally.
    ``growth_cap`` (decimal) optionally clamps runaway growth so the multiple
    stays defensive.
    """
    if eps is None or eps <= 0 or growth_rate is None:
        return None
    if bond_yield is None or bond_yield <= 0:
        return None
    g = growth_rate
    if growth_cap is not None:
        g = min(g, growth_cap)
    g_pct = g * 100.0
    multiple = GRAHAM_BASE_PE + GRAHAM_GROWTH_MULT * g_pct
    return eps * multiple * GRAHAM_BASE_BOND_YIELD / bond_yield


def dcf_two_stage(base_cash_flow, growth_rate, discount_rate,
                  terminal_growth=DEFAULT_TERMINAL_GROWTH, years=DEFAULT_YEARS):
    """Two-stage discounted cash flow, per share.

    Stage 1 grows ``base_cash_flow`` at ``growth_rate`` for ``years`` years;
    stage 2 is a Gordon terminal value growing perpetually at ``terminal_growth``.
    All flows are discounted back at ``discount_rate``.

    ``base_cash_flow`` should be free cash flow per share (preferred) or EPS as a
    proxy. Requires a positive base flow and ``discount_rate > terminal_growth``.
    """
    if base_cash_flow is None or base_cash_flow <= 0 or growth_rate is None:
        return None
    if discount_rate is None or discount_rate <= terminal_growth:
        return None  # terminal value diverges when r <= g
    if years <= 0:
        return None

    value = 0.0
    cash_flow = base_cash_flow
    for year in range(1, years + 1):
        cash_flow *= (1.0 + growth_rate)
        value += cash_flow / (1.0 + discount_rate) ** year

    terminal_cf = cash_flow * (1.0 + terminal_growth)
    terminal_value = terminal_cf / (discount_rate - terminal_growth)
    value += terminal_value / (1.0 + discount_rate) ** years
    return value


def earnings_power(eps, growth_rate, discount_rate, fair_pe, years=DEFAULT_YEARS):
    """Earnings-power value via a forward exit multiple.

    Grow EPS at ``growth_rate`` for ``years``, apply an exit P/E (``fair_pe``) to
    get a future price, then discount that price back to today at
    ``discount_rate``. A quick "what is a fair price if it trades at a normal
    multiple after growing" check.
    """
    if eps is None or eps <= 0 or growth_rate is None:
        return None
    if fair_pe is None or fair_pe <= 0 or discount_rate is None or years <= 0:
        return None
    future_eps = eps * (1.0 + growth_rate) ** years
    future_price = future_eps * fair_pe
    return future_price / (1.0 + discount_rate) ** years


def ddm_gordon(dividend_per_share, discount_rate, dividend_growth):
    """Gordon growth dividend-discount model: ``V = D1 / (r - g)``.

    ``D1`` is next year's dividend (``dividend_per_share`` grown one year).
    Requires a positive dividend and ``discount_rate > dividend_growth``.
    """
    if dividend_per_share is None or dividend_per_share <= 0:
        return None
    if dividend_growth is None or discount_rate is None:
        return None
    if discount_rate <= dividend_growth:
        return None
    next_dividend = dividend_per_share * (1.0 + dividend_growth)
    return next_dividend / (discount_rate - dividend_growth)


# --------------------------------------------------------------------------- #
# Composite: run every applicable model and blend.
# --------------------------------------------------------------------------- #

def intrinsic_value_estimates(f: Fundamentals,
                              margin_of_safety=DEFAULT_MARGIN_OF_SAFETY) -> dict:
    """Run every model the inputs support and blend them.

    Returns a dict with per-method values (``methods``), a robust ``composite``
    (the median of available estimates, which shrugs off a single wild model),
    plus ``mean``/``low``/``high`` for the range, the ``best_buy_price``
    (composite discounted by ``margin_of_safety``) and, when a current price is
    known, the ``upside`` and ``verdict`` versus fair value.
    """
    dividend_growth = f.dividend_growth
    if dividend_growth is None:
        dividend_growth = f.growth_rate

    methods = {
        "graham_number": graham_number(f.eps, f.book_value_per_share),
        "graham_revised": graham_revised(
            f.eps, f.growth_rate, bond_yield=f.bond_yield, growth_cap=f.growth_cap),
        "dcf": dcf_two_stage(
            f.fcf_per_share if f.fcf_per_share is not None else f.eps,
            f.growth_rate, f.discount_rate,
            terminal_growth=f.terminal_growth, years=f.years),
        "earnings_power": earnings_power(
            f.eps, f.growth_rate, f.discount_rate, f.fair_pe, years=f.years),
        "ddm": ddm_gordon(f.dividend_per_share, f.discount_rate, dividend_growth),
    }

    valid = {k: round(v, 2) for k, v in methods.items()
             if v is not None and v > 0 and math.isfinite(v)}
    values = list(valid.values())

    result = {
        "methods": valid,
        "methods_unavailable": [k for k, v in methods.items() if k not in valid],
        "num_methods": len(values),
        "composite": None,
        "mean": None,
        "low": None,
        "high": None,
        "margin_of_safety": margin_of_safety,
        "best_buy_price": None,
        "current_price": f.current_price,
        "upside": None,
        "verdict": None,
        "dcf_cash_flow_basis": "fcf_per_share" if f.fcf_per_share is not None else "eps",
    }
    if not values:
        return result

    composite = round(median(values), 2)
    result["composite"] = composite
    result["mean"] = round(sum(values) / len(values), 2)
    result["low"] = min(values)
    result["high"] = max(values)
    result["best_buy_price"] = round(composite * (1.0 - margin_of_safety), 2)

    if f.current_price and f.current_price > 0:
        upside = composite / f.current_price - 1.0
        result["upside"] = round(upside * 100.0, 2)  # % up/down to fair value
        result["verdict"] = _verdict(f.current_price, composite, result["best_buy_price"])
    return result


def _verdict(price, composite, best_buy_price) -> str:
    """Plain-language read of price vs. fair value."""
    if price <= best_buy_price:
        return "BUY ZONE — at/below the margin-of-safety price"
    if price < composite:
        return "FAIR — below intrinsic value but inside the safety margin"
    if price < composite * 1.15:
        return "FULLY VALUED — around intrinsic value"
    return "EXPENSIVE — above intrinsic value"
