"""Render a :func:`valuation.engine.value_stock` report as a terminal table."""

from __future__ import annotations

_METHOD_LABELS = {
    "graham_number": "Graham Number",
    "graham_revised": "Graham Revised",
    "dcf": "Two-stage DCF",
    "earnings_power": "Earnings Power",
    "ddm": "Dividend Discount",
}


def _money(v, currency=""):
    if v is None:
        return "-"
    sym = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£"}.get(currency, "")
    return f"{sym}{v:,.2f}"


def format_report(rep: dict, currency: str = "") -> str:
    """Return a multi-line, human-readable summary of a valuation report."""
    stock = rep["stock"]
    currency = currency or stock.get("currency") or ""
    out = []
    title = stock.get("name") or stock.get("symbol") or "(manual inputs)"
    out.append("=" * 64)
    out.append(f" INTRINSIC VALUE & PYRAMIDING — {title}")
    if stock.get("symbol"):
        out.append(f" Symbol: {stock['symbol']}   "
                   f"Current price: {_money(stock.get('current_price'), currency)}")
    out.append("=" * 64)

    # Inputs used.
    out.append("\nInputs used (source):")
    for name, node in rep["inputs"].items():
        val = node["value"]
        shown = f"{val:.4g}" if isinstance(val, float) else str(val)
        out.append(f"  {name:<22} {shown:>12}   [{node['source']}]")

    # Intrinsic value.
    iv = rep["intrinsic"]
    out.append("\nIntrinsic value estimates:")
    if iv["num_methods"]:
        for key, val in iv["methods"].items():
            out.append(f"  {_METHOD_LABELS.get(key, key):<20} {_money(val, currency):>14}")
        out.append("  " + "-" * 34)
        out.append(f"  {'COMPOSITE (median)':<20} {_money(iv['composite'], currency):>14}")
        out.append(f"  {'Range':<20} "
                   f"{_money(iv['low'], currency)} … {_money(iv['high'], currency)}")
        out.append(f"\n  Margin of safety : {iv['margin_of_safety']*100:.0f}%")
        out.append(f"  Best buy price   : {_money(iv['best_buy_price'], currency)}")
        if iv.get("upside") is not None:
            out.append(f"  Upside to fair   : {iv['upside']:+.1f}%")
            out.append(f"  Verdict          : {iv['verdict']}")
    else:
        out.append("  (none — insufficient inputs)")

    # Pyramid.
    pyr = rep.get("pyramid")
    if pyr:
        out.append(f"\nPyramiding plan — {pyr['mode']}:")
        out.append(f"  {pyr['description']}")
        header = f"  {'Lvl':<4}{'Price':>13}{'Weight':>9}"
        rows = pyr["tranches"]
        has_shares = any("shares" in r for r in rows)
        extra = "discount_to_intrinsic" in rows[0]
        if extra:
            header += f"{'Disc%':>8}"
        else:
            header += f"{'Above%':>8}"
        if has_shares:
            header += f"{'Shares':>9}{'Cost':>14}"
        out.append(header)
        out.append("  " + "-" * (len(header) - 2))
        for r in rows:
            line = f"  {r['level']:<4}{_money(r['price'], currency):>13}{r['weight_pct']:>8.1f}%"
            if extra:
                line += f"{r['discount_to_intrinsic']:>7.0f}%"
            else:
                line += f"{r['above_entry_pct']:>7.0f}%"
            if has_shares:
                line += f"{r.get('shares', 0):>9}{_money(r.get('cost'), currency):>14}"
            out.append(line)

        s = pyr["summary"]
        out.append("  " + "-" * (len(header) - 2))
        out.append(f"  Avg entry price      : {_money(s.get('avg_entry_price'), currency)}")
        if s.get("effective_margin_of_safety") is not None:
            out.append(f"  Effective MoS at avg : {s['effective_margin_of_safety']:.1f}%")
        if s.get("upside_to_intrinsic_at_avg") is not None:
            out.append(f"  Upside at avg entry  : {s['upside_to_intrinsic_at_avg']:+.1f}%")
        stop = s.get("stop_loss") or s.get("final_trailing_stop")
        if stop is not None:
            out.append(f"  Stop-loss            : {_money(stop, currency)}")
        if s.get("planned_shares"):
            out.append(f"  Planned position     : {s['planned_shares']} shares, "
                       f"cost {_money(s.get('planned_cost'), currency)}")
            if s.get("max_risk") is not None:
                out.append(f"  Max risk to stop     : {_money(s['max_risk'], currency)}")

    if rep.get("warnings"):
        out.append("\nNotes:")
        for w in rep["warnings"]:
            out.append(f"  ! {w}")

    out.append(f"\n{rep['disclaimer']}")
    return "\n".join(out)
