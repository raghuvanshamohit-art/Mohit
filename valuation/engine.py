"""Orchestrate a full valuation: fetch (best-effort) -> intrinsic value -> pyramid.

``value_stock`` is the one entry point. Explicitly supplied inputs always win;
anything left ``None`` is auto-filled from Yahoo when a symbol is given and
``auto`` is on, and the latest price is taken from the reliable chart endpoint.
Every field records where it came from (``supplied`` / ``yahoo`` / ``default``)
so the report is honest about which numbers are real and which are assumptions.
"""

from __future__ import annotations

from .intrinsic import (
    DEFAULT_DISCOUNT_RATE,
    DEFAULT_MARGIN_OF_SAFETY,
    DEFAULT_TERMINAL_GROWTH,
    DEFAULT_YEARS,
    Fundamentals,
    GRAHAM_BASE_BOND_YIELD,
    intrinsic_value_estimates,
)
from .pyramid import build_pyramid, build_trend_pyramid

# Core per-share/assumption fields the user may override explicitly.
_OVERRIDE_FIELDS = (
    "eps", "book_value_per_share", "fcf_per_share", "dividend_per_share",
    "growth_rate", "terminal_growth", "discount_rate", "dividend_growth",
    "years", "fair_pe", "bond_yield", "growth_cap", "current_price",
)


def _to_yahoo_symbol(symbol: str, yahoo_symbol=None) -> str:
    """Resolve a Yahoo symbol from a user symbol.

    A symbol already containing a ``.`` (e.g. ``RELIANCE.NS``, ``AAPL`` stays
    ``AAPL`` only if passed via ``yahoo_symbol``) is used verbatim; a bare NSE
    symbol is mapped to ``<sym>.NS`` (via the project's override table).
    """
    if yahoo_symbol:
        return yahoo_symbol
    if "." in symbol:
        return symbol
    try:  # reuse the project's NSE -> Yahoo mapping (handles .BO overrides)
        from sector_stocks.sectors import to_yahoo
        return to_yahoo(symbol.upper())
    except Exception:  # noqa: BLE001 - fall back to the plain .NS convention
        return f"{symbol.upper()}.NS"


def _reliable_price(yahoo_symbol: str):
    """Latest adjusted close from the reliable chart endpoint, or None."""
    try:
        from sector_stocks.yahoo import fetch_series
        # Snappy: 2 attempts / short timeout so a typo doesn't hang the request.
        series = fetch_series(yahoo_symbol, rng="1mo", retries=2, timeout=10)
        return round(series.closes[-1], 2), series.currency, series.long_name
    except Exception:  # noqa: BLE001 - price is best-effort too
        return None, "", ""


def value_stock(symbol=None, *, auto=True, yahoo_symbol=None,
                margin_of_safety=DEFAULT_MARGIN_OF_SAFETY,
                # pyramid options
                tranches=3, step=0.10, weighting="increasing", capital=None,
                stop_pct=0.10, pyramid_mode="value", trend_entry=None,
                **overrides) -> dict:
    """Produce a complete intrinsic-value + pyramiding report as a dict.

    Parameters
    ----------
    symbol : str, optional
        NSE symbol (``RELIANCE``) or full Yahoo symbol (``RELIANCE.NS``). When
        set with ``auto=True`` the fundamentals and price are fetched.
    auto : bool
        Whether to attempt the best-effort Yahoo fundamentals fetch.
    yahoo_symbol : str, optional
        Force a specific Yahoo symbol (use for non-NSE tickers, e.g. ``AAPL``).
    margin_of_safety : float
        Discount to intrinsic value for the "best buy price" and first tranche.
    tranches, step, weighting, capital, stop_pct
        Pyramid ladder options (see :mod:`valuation.pyramid`).
    pyramid_mode : str
        ``value`` (accumulate below intrinsic value) or ``trend`` (add-to-winner).
    trend_entry : float, optional
        Base entry for ``trend`` mode; defaults to the current price.
    **overrides
        Any of :data:`_OVERRIDE_FIELDS` to supply/override a fundamental.

    Returns
    -------
    dict
        ``{"stock", "inputs", "intrinsic", "pyramid", "warnings", "disclaimer"}``.
    """
    warnings = []
    fetched = None
    resolved_symbol = None

    if symbol or yahoo_symbol:
        resolved_symbol = _to_yahoo_symbol(symbol or yahoo_symbol, yahoo_symbol)

    # 1. Best-effort fundamentals fetch.
    if resolved_symbol and auto:
        try:
            from .fundamentals import FundamentalsError, fetch_fundamentals
            fetched = fetch_fundamentals(resolved_symbol)
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            warnings.append(
                f"Could not auto-fetch fundamentals for {resolved_symbol}: {exc}. "
                f"Supply values manually (--eps, --bvps, --growth, ...).")

    # 2. Start from fetched values (if any), then apply explicit overrides.
    f = fetched or Fundamentals(symbol=resolved_symbol or (symbol or ""))
    if resolved_symbol:
        f.symbol = resolved_symbol

    supplied = {k: v for k, v in overrides.items()
                if k in _OVERRIDE_FIELDS and v is not None}
    for key, val in supplied.items():
        setattr(f, key, val)
        f.provenance[key] = "supplied"
    f.margin_of_safety = margin_of_safety  # informational; used below

    # 3. Authoritative latest price: supplied > reliable chart > fetched.
    if "current_price" not in supplied and resolved_symbol and auto:
        px, currency, long_name = _reliable_price(resolved_symbol)
        if px is not None:
            f.current_price = px
            f.provenance["current_price"] = "chart"
            if currency and not f.currency:
                f.currency = currency
            if long_name and not f.name:
                f.name = long_name

    # 4. Fill assumption defaults + record provenance for them.
    _apply_defaults(f, supplied)

    # 5. Intrinsic value.
    intrinsic = intrinsic_value_estimates(f, margin_of_safety=margin_of_safety)
    if intrinsic["num_methods"] == 0:
        warnings.append(
            "No intrinsic-value model could run — supply at least EPS (+ book "
            "value for the Graham Number, or a growth rate for DCF / Graham "
            "revised).")

    # 6. Pyramid plan (only when we have a fair value / entry to build from).
    pyramid = None
    composite = intrinsic.get("composite")
    if pyramid_mode == "trend":
        entry = trend_entry if trend_entry is not None else f.current_price
        if entry:
            pyramid = build_trend_pyramid(
                entry, tranches=tranches, step=step, weighting=weighting,
                capital=capital, trail_pct=stop_pct, intrinsic_value=composite)
        else:
            warnings.append(
                "Trend pyramid needs a base entry — pass --trend-entry or a price.")
    elif composite:
        pyramid = build_pyramid(
            composite, margin_of_safety=margin_of_safety, tranches=tranches,
            step=step, weighting=weighting, capital=capital,
            current_price=f.current_price, stop_pct=stop_pct)
    else:
        warnings.append("No pyramid built — needs a positive intrinsic value.")

    return {
        "stock": {
            "symbol": f.symbol,
            "name": f.name,
            "currency": f.currency,
            "current_price": f.current_price,
        },
        "inputs": _inputs_view(f),
        "intrinsic": intrinsic,
        "pyramid": pyramid,
        "warnings": warnings,
        "disclaimer": (
            "For information/education only — not investment advice. Estimates "
            "are only as good as the growth and discount-rate assumptions used."),
    }


def _apply_defaults(f: Fundamentals, supplied: dict) -> None:
    """Record provenance for assumption fields, marking defaults as such."""
    default_map = {
        "discount_rate": DEFAULT_DISCOUNT_RATE,
        "terminal_growth": DEFAULT_TERMINAL_GROWTH,
        "years": DEFAULT_YEARS,
        "bond_yield": GRAHAM_BASE_BOND_YIELD,
    }
    for key, default in default_map.items():
        if key in supplied:
            continue
        if key not in f.provenance:
            f.provenance[key] = "default" if getattr(f, key) == default else "yahoo"


def _inputs_view(f: Fundamentals) -> dict:
    """A JSON-friendly view of the inputs actually used, with provenance."""
    fields = (
        "eps", "book_value_per_share", "fcf_per_share", "dividend_per_share",
        "growth_rate", "terminal_growth", "discount_rate", "dividend_growth",
        "years", "fair_pe", "bond_yield", "growth_cap", "current_price",
    )
    view = {}
    for name in fields:
        val = getattr(f, name, None)
        if val is None:
            continue
        view[name] = {"value": val, "source": f.provenance.get(name, "default")}
    return view
