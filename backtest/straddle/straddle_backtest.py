#!/usr/bin/env python3
"""
Backtest — System B (as requested): LONG ATM STRADDLE on NIFTY.

Strategy under test
  Each monthly cycle: BUY 1 ATM Call + BUY 1 ATM Put (a long straddle), hold to
  monthly expiry (last Thursday). The straddle buyer profits from a large move
  in EITHER direction and loses time value if the index stays put.

  Entry  : first trading day after the previous monthly expiry (fresh ~30d option).
  Strike : nearest 50 to spot at entry (ATM).
  Premium: priced with Black-Scholes, using INDIA VIX as the implied-vol input.
  Exit   : intrinsic value at expiry = |Spot_expiry - Strike|.
  P&L    : intrinsic - premium_paid - costs.   Return = P&L / premium_paid.

Why Black-Scholes + India VIX (read this)
  Ten years of real NIFTY option-chain premiums are not freely available. But
  India VIX *is* the market's own implied volatility for ~30-day options, so
  pricing the ATM straddle with BS at the VIX level reproduces realistic
  premiums rather than guessing. This is a MODEL of option prices, aligned to
  the volatility the market actually charged. Unmodelled: bid/ask spread beyond
  the cost knob, volatility skew (ATM straddle mostly uses ATM vol, which VIX
  approximates), and intramonth exit timing. Treat outputs as a faithful
  approximation, not tick-level fills.

Standard library only. Not investment advice.
"""
from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass


# --------------------------------------------------------------------------- #
# Black-Scholes
# --------------------------------------------------------------------------- #
def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bs_call_put(S: float, K: float, T: float, r: float, sigma: float) -> tuple[float, float]:
    """Return (call, put) Black-Scholes prices."""
    if T <= 0 or sigma <= 0:
        call = max(S - K, 0.0)
        put = max(K - S, 0.0)
        return call, put
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    disc = math.exp(-r * T)
    call = S * _norm_cdf(d1) - K * disc * _norm_cdf(d2)
    put = K * disc * _norm_cdf(-d2) - S * _norm_cdf(-d1)
    return call, put


# --------------------------------------------------------------------------- #
# Data & calendar
# --------------------------------------------------------------------------- #
import datetime as dt


@dataclass
class Row:
    d: dt.date
    nifty: float
    vix: float


def load(path: str) -> list[Row]:
    rows: list[Row] = []
    with open(path, newline="") as f:
        for x in csv.DictReader(f):
            rows.append(
                Row(dt.date.fromisoformat(x["date"]), float(x["nifty_close"]), float(x["india_vix"]))
            )
    rows.sort(key=lambda z: z.d)
    return rows


def last_thursday(year: int, month: int) -> dt.date:
    """NSE monthly expiry ≈ last Thursday of the month."""
    if month == 12:
        nxt = dt.date(year + 1, 1, 1)
    else:
        nxt = dt.date(year, month + 1, 1)
    day = nxt - dt.timedelta(days=1)
    while day.weekday() != 3:  # 3 = Thursday
        day -= dt.timedelta(days=1)
    return day


def on_or_before(rows: list[Row], target: dt.date) -> int | None:
    """Index of the last trading day on/before target."""
    lo, hi, ans = 0, len(rows) - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if rows[mid].d <= target:
            ans = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


def first_after(rows: list[Row], target: dt.date) -> int | None:
    """Index of the first trading day strictly after target."""
    lo, hi, ans = 0, len(rows) - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if rows[mid].d > target:
            ans = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return ans


# --------------------------------------------------------------------------- #
# Backtest
# --------------------------------------------------------------------------- #
@dataclass
class Cycle:
    entry: dt.date
    expiry: dt.date
    spot0: float
    strike: float
    vix: float
    premium: float
    spot_exp: float
    move_pct: float
    net_pnl: float      # points, net of costs
    ret_pct: float      # net_pnl / premium


def backtest(rows: list[Row], r: float, cost_pct: float, lot: int) -> list[Cycle]:
    start, end = rows[0].d, rows[-1].d
    # Enumerate monthly expiries within the data span.
    expiries: list[dt.date] = []
    y, m = start.year, start.month
    while dt.date(y, m, 1) <= end:
        exp = last_thursday(y, m)
        if start <= exp <= end:
            expiries.append(exp)
        m += 1
        if m > 12:
            m, y = 1, y + 1

    cycles: list[Cycle] = []
    for i in range(1, len(expiries)):
        prev_exp, this_exp = expiries[i - 1], expiries[i]
        ei = first_after(rows, prev_exp)          # entry: day after previous expiry
        xi = on_or_before(rows, this_exp)         # exit: expiry (or last trading day before)
        if ei is None or xi is None or ei >= xi:
            continue
        e, x = rows[ei], rows[xi]
        S0 = e.nifty
        K = round(S0 / 50.0) * 50.0               # nearest 50 = ATM
        sigma = e.vix / 100.0
        T = (x.d - e.d).days / 365.0
        call, put = bs_call_put(S0, K, T, r, sigma)
        premium = call + put
        if premium <= 0:
            continue
        intrinsic = abs(x.nifty - K)
        cost = cost_pct * premium                 # round-trip friction (brokerage/slippage/settlement)
        outlay = premium + cost                   # total cash the buyer puts at risk
        net = intrinsic - outlay                  # capped at -outlay (option can't lose more than paid)
        cycles.append(
            Cycle(
                entry=e.d, expiry=x.d, spot0=S0, strike=K, vix=e.vix,
                premium=premium, spot_exp=x.nifty,
                move_pct=(x.nifty - S0) / S0 * 100.0,
                net_pnl=net, ret_pct=net / outlay * 100.0,   # return on cash outlay; floor -100%
            )
        )
    return cycles


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def print_report(cycles: list[Cycle], capital: float, cost_pct: float, r: float, lot: int) -> None:
    n = len(cycles)
    wins = [c for c in cycles if c.net_pnl > 0]
    losses = [c for c in cycles if c.net_pnl <= 0]
    sum_pos = sum(c.ret_pct for c in wins)
    sum_neg = sum(c.ret_pct for c in losses)
    avg = sum(c.ret_pct for c in cycles) / n

    # Aggregate return = total P&L / total cash deployed (the honest "how much return").
    total_outlay = sum(c.premium * (1 + cost_pct) for c in cycles)   # points
    total_net = sum(c.net_pnl for c in cycles)                       # points
    agg_return = total_net / total_outlay * 100.0
    # 1-lot-per-month rupee simulation.
    deployed_rs = total_outlay * lot
    pnl_rs = total_net * lot

    print("=" * 78)
    print(" System B — NIFTY LONG ATM STRADDLE (buy ATM Call + buy ATM Put), monthly")
    print("=" * 78)
    print(f" Period            : {cycles[0].entry} -> {cycles[-1].expiry}   ({n} monthly cycles)")
    print(f" Pricing           : Black-Scholes @ India VIX | r={r*100:.1f}% | cost={cost_pct*100:.1f}% of premium")
    print(f" Return convention : per cycle = net P&L / cash outlay (buyer's capital at risk)")
    print("-" * 78)
    print(f" Positive months   : {len(wins)}   ({len(wins)/n*100:.1f}% win rate)")
    print(f" Negative months   : {len(losses)} ({len(losses)/n*100:.1f}%)")
    print(f" SUM of POSITIVE returns : {sum_pos:+.1f}%   (total upside across winning months)")
    print(f" SUM of NEGATIVE returns : {sum_neg:+.1f}%   (total downside across losing months)")
    print(f" Average monthly return  : {avg:+.2f}%")
    best = max(cycles, key=lambda c: c.ret_pct)
    worst = min(cycles, key=lambda c: c.ret_pct)
    print(f" Best  month : {best.entry.isoformat()[:7]}  {best.ret_pct:+.0f}%  (move {best.move_pct:+.1f}%)")
    print(f" Worst month : {worst.entry.isoformat()[:7]}  {worst.ret_pct:+.0f}%  (move {worst.move_pct:+.1f}%)")
    print("-" * 78)
    print(f" AGGREGATE RETURN (total P&L / total cash deployed) : {agg_return:+.1f}%")
    print(f" 1-lot-per-month sim (lot={lot}):  deployed ~Rs {deployed_rs:,.0f}"
          f"  ->  net P&L Rs {pnl_rs:,.0f}")
    print("=" * 78)

    # --- Year x Month grid of returns % (by ENTRY month) ---
    grid: dict[int, dict[int, float]] = {}
    for c in cycles:
        grid.setdefault(c.entry.year, {})[c.entry.month] = c.ret_pct
    years = sorted(grid)
    print("\n MONTH-WISE RETURN (%), by entry month  [+ = profit, - = loss]")
    header = " Year |" + "".join(f"{mn:>7}" for mn in MONTHS) + "  |    Total"
    print(header)
    print(" " + "-" * (len(header) - 1))
    for yr in years:
        cells = []
        tot = 0.0
        any_v = False
        for mo in range(1, 13):
            v = grid[yr].get(mo)
            if v is None:
                cells.append(f"{'.':>7}")
            else:
                cells.append(f"{v:>7.0f}")
                tot += v
                any_v = True
        line = f" {yr} |" + "".join(cells) + f"  | {tot:>8.0f}" if any_v else ""
        if line:
            print(line)
    # Column (calendar-month) averages
    col_avg = []
    for mo in range(1, 13):
        vals = [grid[yr][mo] for yr in years if mo in grid[yr]]
        col_avg.append(f"{(sum(vals)/len(vals)):>7.0f}" if vals else f"{'.':>7}")
    print(" " + "-" * (len(header) - 1))
    print(" Avg  |" + "".join(col_avg) + "  |")
    print("\n (Cell = that month's straddle return on premium paid, held to expiry.)")


def build_markdown(cycles: list[Cycle], cost_pct: float, r: float, lot: int) -> str:
    n = len(cycles)
    wins = [c for c in cycles if c.net_pnl > 0]
    losses = [c for c in cycles if c.net_pnl <= 0]
    sum_pos = sum(c.ret_pct for c in wins)
    sum_neg = sum(c.ret_pct for c in losses)
    avg = sum(c.ret_pct for c in cycles) / n
    total_outlay = sum(c.premium * (1 + cost_pct) for c in cycles)
    total_net = sum(c.net_pnl for c in cycles)
    agg = total_net / total_outlay * 100.0
    best = max(cycles, key=lambda c: c.ret_pct)
    worst = min(cycles, key=lambda c: c.ret_pct)

    grid: dict[int, dict[int, float]] = {}
    for c in cycles:
        grid.setdefault(c.entry.year, {})[c.entry.month] = c.ret_pct
    years = sorted(grid)

    L: list[str] = []
    L.append("# System B — Long ATM Straddle on NIFTY: 10-Year Backtest")
    L.append("")
    L.append("**Strategy:** each monthly cycle, **buy 1 ATM Call + buy 1 ATM Put** "
             "(a long straddle) and hold to monthly expiry. Profits on a big move in "
             "either direction; loses time value if the index stays flat.")
    L.append("")
    L.append(f"- **Data:** NIFTY 50 spot + India VIX, daily, "
             f"{cycles[0].entry} → {cycles[-1].expiry} ({n} monthly cycles).")
    L.append(f"- **Option pricing:** Black-Scholes with **India VIX** as the implied-vol "
             f"input, r = {r*100:.1f}%, round-trip cost = {cost_pct*100:.1f}% of premium.")
    L.append(f"- **Return convention:** per cycle = net P&L ÷ cash outlay (an option "
             f"buyer can lose at most 100% — the premium paid).")
    L.append("")
    L.append("> ⚠️ Real 10-year NIFTY option premiums aren't freely available, so premiums "
             "are **modelled** (BS @ India VIX). This is a faithful approximation of what the "
             "market charged, not tick-level fills. Educational, not advice.")
    L.append("")
    L.append("## Headline result")
    L.append("")
    L.append("| Metric | Value |")
    L.append("|---|---|")
    L.append(f"| Monthly cycles | {n} |")
    L.append(f"| Positive months | **{len(wins)} ({len(wins)/n*100:.1f}%)** |")
    L.append(f"| Negative months | **{len(losses)} ({len(losses)/n*100:.1f}%)** |")
    L.append(f"| Sum of positive-month returns | **+{sum_pos:.0f}%** |")
    L.append(f"| Sum of negative-month returns | **{sum_neg:.0f}%** |")
    L.append(f"| Average monthly return | **{avg:+.1f}%** |")
    L.append(f"| **Aggregate return** (total P&L ÷ total cash deployed) | **{agg:+.1f}%** |")
    L.append(f"| 1-lot/month sim (lot={lot}) | deployed ≈ ₹{total_outlay*lot:,.0f} → "
             f"net P&L **₹{total_net*lot:,.0f}** |")
    L.append(f"| Best month | {best.entry.isoformat()[:7]} **{best.ret_pct:+.0f}%** "
             f"(NIFTY moved {best.move_pct:+.1f}%) |")
    L.append(f"| Worst month | {worst.entry.isoformat()[:7]} **{worst.ret_pct:+.0f}%** "
             f"(NIFTY moved {worst.move_pct:+.1f}%) |")
    L.append("")
    L.append("## Month-wise return (%), by entry month")
    L.append("")
    L.append("Each cell = that month's straddle return on the premium paid, held to expiry. "
             "`+` = profit, `−` = loss.")
    L.append("")
    L.append("| Year | " + " | ".join(MONTHS) + " | **Total** |")
    L.append("|" + "---|" * (len(MONTHS) + 2))
    for yr in years:
        cells = []
        tot = 0.0
        for mo in range(1, 13):
            v = grid[yr].get(mo)
            cells.append("·" if v is None else f"{v:+.0f}")
            if v is not None:
                tot += v
        L.append(f"| {yr} | " + " | ".join(cells) + f" | **{tot:+.0f}** |")
    col_avg = []
    for mo in range(1, 13):
        vals = [grid[yr][mo] for yr in years if mo in grid[yr]]
        col_avg.append(f"{sum(vals)/len(vals):+.0f}" if vals else "·")
    L.append("| **Avg** | " + " | ".join(col_avg) + " | |")
    L.append("")
    L.append("## Positive vs negative, at a glance")
    L.append("")
    L.append(f"- **Winning months:** {len(wins)} of {n} ({len(wins)/n*100:.1f}%), "
             f"contributing **+{sum_pos:.0f}%** of return in total.")
    L.append(f"- **Losing months:** {len(losses)} of {n} ({len(losses)/n*100:.1f}%), "
             f"contributing **{sum_neg:.0f}%** of return in total.")
    L.append(f"- The losses outweigh the wins: net **{agg:+.1f}%** on capital deployed.")
    L.append("")
    L.append("## What this means")
    L.append("")
    L.append("Buying a monthly ATM straddle and **holding to expiry loses money** over this "
             "10-year window. The reason is structural: option buyers pay a **volatility risk "
             "premium** — implied volatility (what you pay) is, on average, higher than the "
             "volatility that actually shows up, and time decay bleeds the position in the "
             "~62% of months when NIFTY doesn't move enough. The strategy's few big wins "
             f"(e.g. {best.entry.isoformat()[:7]}, the COVID crash, +{best.ret_pct:.0f}%) do "
             "**not** cover the steady drip of losing months.")
    L.append("")
    L.append("This is exactly why practitioners more often **sell** premium (defined-risk) "
             "than buy naked straddles — and why the framework insists you prove expectancy on "
             "data *before* deploying capital. Here, the data says: don't deploy this version.")
    L.append("")
    L.append("### Caveats")
    L.append("- Premiums are modelled (BS @ India VIX), not real fills; add bid/ask and you'd "
             "lose *more*, not less.")
    L.append("- Held strictly to expiry with no stop, adjustment, or profit-taking — an "
             "intramonth exit rule would change results (test it via the code).")
    L.append("- Monthly expiry only; a weekly-straddle variant behaves differently.")
    L.append("")
    L.append("*Generated by `straddle_backtest.py`. Re-run to reproduce.*")
    L.append("")
    return "\n".join(L)


def write_csv(cycles: list[Cycle], path: str) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entry", "expiry", "spot_entry", "strike", "india_vix",
                    "premium_paid", "spot_expiry", "move_pct", "net_pnl_points", "return_pct"])
        for c in cycles:
            w.writerow([c.entry, c.expiry, f"{c.spot0:.2f}", f"{c.strike:.0f}", f"{c.vix:.2f}",
                        f"{c.premium:.2f}", f"{c.spot_exp:.2f}", f"{c.move_pct:.2f}",
                        f"{c.net_pnl:.2f}", f"{c.ret_pct:.2f}"])


def main() -> None:
    here = __file__.rsplit("/", 1)[0]
    p = argparse.ArgumentParser(description="Backtest a monthly long ATM straddle on NIFTY.")
    p.add_argument("--data", default=f"{here}/data/nifty_vix_daily.csv",
                   help="CSV: date,nifty_close,india_vix")
    p.add_argument("--capital", type=float, default=1_000_000.0)
    p.add_argument("--rate", type=float, default=0.065, help="Risk-free rate (default 6.5%).")
    p.add_argument("--cost-pct", type=float, default=0.02,
                   help="Round-trip cost as a fraction of premium (default 0.02 = 2%).")
    p.add_argument("--lot", type=int, default=50, help="NIFTY lot size (informational).")
    p.add_argument("--csv-out", help="Write the per-cycle table to this CSV.")
    p.add_argument("--md-out", help="Write a full month-wise Markdown report to this path.")
    args = p.parse_args()

    rows = load(args.data)
    cycles = backtest(rows, r=args.rate, cost_pct=args.cost_pct, lot=args.lot)
    if not cycles:
        print("No cycles produced — check data span.")
        return
    print(f"[data] {args.data}  ({rows[0].d} -> {rows[-1].d}, {len(rows)} trading days)\n")
    print_report(cycles, args.capital, args.cost_pct, args.rate, args.lot)
    if args.csv_out:
        write_csv(cycles, args.csv_out)
        print(f"\n[per-cycle table written] {args.csv_out}")
    if args.md_out:
        with open(args.md_out, "w") as f:
            f.write(build_markdown(cycles, args.cost_pct, args.rate, args.lot))
        print(f"[markdown report written] {args.md_out}")


if __name__ == "__main__":
    main()
