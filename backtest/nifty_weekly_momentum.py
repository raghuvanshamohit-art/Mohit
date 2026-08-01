#!/usr/bin/env python3
"""
Backtest — System A: "NIFTY Weekly Momentum" (directional trend-following).

Implements the rules from strategy/system-based-strategy-design.md exactly, on
weekly OHLC bars, with no external dependencies (Python standard library only).

RULES (long-only variant)
  Bias filter : long only if weekly close > EMA(20) AND weekly RSI(14) > 55.
  Entry       : on a long signal from the completed week, enter at NEXT week's open.
  Initial stop: the prior week's low  (structural stop).
  Sizing      : quantity so that (entry - stop) == R, where R = risk_pct of equity.
  Target      : entry + target_r * (entry - stop)   [default 2R].
  Trailing    : each completed week, raise the stop to that week's low (never lower).
  Bias-flip   : if the weekly close no longer satisfies the bias filter, exit at
                next week's open.
  Costs       : cost_bps charged per side on notional (brokerage + taxes + slippage).

RISK OVERLAY (portfolio discipline from the framework)
  kill_dd       : if equity drawdown from peak breaches this, pause NEW entries...
  cooldown_weeks: ...for this many weeks (no revenge trades).

No lookahead: signals are computed on completed weekly bars and acted on at the
open of the following week. Intrabar, the stop is checked before the target
(worst-case fill assumption). Gaps through a level fill at the open.

USAGE
  python3 nifty_weekly_momentum.py                 # runs on synthetic demo data
  python3 nifty_weekly_momentum.py --data nifty_weekly.csv
  python3 nifty_weekly_momentum.py --data nifty_weekly.csv --equity-out curve.csv

DATA FORMAT (CSV, weekly bars, ascending dates)
  date,open,high,low,close
  2015-01-02,8300.5,8420.0,8250.0,8395.0
  ...

DISCLAIMER: Educational tooling. Synthetic data is NOT real market data and is
for pipeline demonstration only. Parameters are illustrative, not advice.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
from dataclasses import dataclass, field


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #
@dataclass
class Bar:
    date: str
    o: float
    h: float
    l: float
    c: float


def load_csv(path: str) -> list[Bar]:
    bars: list[Bar] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        cols = {c.lower(): c for c in (reader.fieldnames or [])}
        need = ("date", "open", "high", "low", "close")
        missing = [n for n in need if n not in cols]
        if missing:
            raise ValueError(f"CSV missing column(s): {missing}. Found: {reader.fieldnames}")
        for row in reader:
            bars.append(
                Bar(
                    date=row[cols["date"]],
                    o=float(row[cols["open"]]),
                    h=float(row[cols["high"]]),
                    l=float(row[cols["low"]]),
                    c=float(row[cols["close"]]),
                )
            )
    if len(bars) < 40:
        raise ValueError(f"Need at least ~40 weekly bars; got {len(bars)}.")
    return bars


def synthetic_bars(n: int = 520, seed: int = 42, start: float = 5000.0) -> list[Bar]:
    """Regime-switching geometric random walk — a stand-in ONLY, not real data."""
    rng = random.Random(seed)
    # (weekly drift, weekly vol) regimes: bull / bear / sideways
    regimes = [(0.0035, 0.020), (-0.0045, 0.035), (0.0000, 0.017)]
    bars: list[Bar] = []
    price = start
    r_idx, r_left = 0, rng.randint(20, 60)
    y, m, d = 2015, 1, 2
    for _ in range(n):
        if r_left <= 0:
            r_idx = rng.randrange(len(regimes))
            r_left = rng.randint(20, 60)
        r_left -= 1
        drift, vol = regimes[r_idx]
        ret = rng.gauss(drift, vol)
        o = price
        c = max(1.0, o * (1.0 + ret))
        hi = max(o, c) * (1.0 + abs(rng.gauss(0, vol / 2)))
        lo = min(o, c) * (1.0 - abs(rng.gauss(0, vol / 2)))
        bars.append(Bar(f"{y:04d}-{m:02d}-{d:02d}", o, hi, lo, c))
        price = c
        # advance ~1 week
        d += 7
        if d > 28:
            d -= 28
            m += 1
            if m > 12:
                m = 1
                y += 1
    return bars


# --------------------------------------------------------------------------- #
# Indicators
# --------------------------------------------------------------------------- #
def ema(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if len(values) < period:
        return out
    k = 2.0 / (period + 1)
    seed = sum(values[:period]) / period
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(values)):
        prev = values[i] * k + prev * (1 - k)
        out[i] = prev
    return out


def rsi(values: list[float], period: int) -> list[float | None]:
    """Wilder's RSI."""
    out: list[float | None] = [None] * len(values)
    if len(values) <= period:
        return out
    gains = losses = 0.0
    for i in range(1, period + 1):
        ch = values[i] - values[i - 1]
        gains += max(ch, 0.0)
        losses += max(-ch, 0.0)
    avg_gain = gains / period
    avg_loss = losses / period
    out[period] = 100.0 if avg_loss == 0 else 100.0 - 100.0 / (1 + avg_gain / avg_loss)
    for i in range(period + 1, len(values)):
        ch = values[i] - values[i - 1]
        avg_gain = (avg_gain * (period - 1) + max(ch, 0.0)) / period
        avg_loss = (avg_loss * (period - 1) + max(-ch, 0.0)) / period
        out[i] = 100.0 if avg_loss == 0 else 100.0 - 100.0 / (1 + avg_gain / avg_loss)
    return out


# --------------------------------------------------------------------------- #
# Backtest engine
# --------------------------------------------------------------------------- #
@dataclass
class Trade:
    entry_date: str
    exit_date: str
    entry: float
    exit: float
    qty: float
    r_unit: float           # initial risk per unit (entry - initial stop)
    reason: str
    pnl: float              # net of costs
    r_multiple: float       # pnl / (r_unit * qty)  == pnl / risk_rupees


@dataclass
class Position:
    entry: float
    stop: float
    target: float
    qty: float
    r_unit: float
    entry_date: str


@dataclass
class Config:
    capital: float = 1_000_000.0
    risk_pct: float = 0.01
    ema_period: int = 20
    rsi_period: int = 14
    rsi_threshold: float = 55.0
    target_r: float = 2.0
    cost_bps: float = 5.0          # per side, on notional
    kill_dd: float = 0.15          # pause new entries when DD from peak >= this
    cooldown_weeks: int = 4


@dataclass
class Result:
    trades: list[Trade] = field(default_factory=list)
    equity_curve: list[tuple[str, float]] = field(default_factory=list)
    final_equity: float = 0.0
    kill_switch_hits: int = 0


def _cost(cfg: Config, price: float, qty: float) -> float:
    return abs(price * qty) * cfg.cost_bps / 10_000.0


def backtest(bars: list[Bar], cfg: Config) -> Result:
    closes = [b.c for b in bars]
    ema_v = ema(closes, cfg.ema_period)
    rsi_v = rsi(closes, cfg.rsi_period)

    def bias_long(i: int) -> bool | None:
        if ema_v[i] is None or rsi_v[i] is None:
            return None
        return closes[i] > ema_v[i] and rsi_v[i] > cfg.rsi_threshold

    res = Result()
    equity = cfg.capital
    peak = cfg.capital
    pos: Position | None = None
    pending_entry = False       # signalled on prior completed bar
    pending_exit = False        # bias-flip exit scheduled at next open
    cooldown = 0
    armed = True                # kill-switch re-arms only after equity recovers

    first = max(cfg.ema_period, cfg.rsi_period + 1)  # first bar with both indicators

    for i in range(first, len(bars)):
        bar = bars[i]

        # 1) Execute actions scheduled from the previous completed bar, at THIS open.
        if pos is not None and pending_exit:
            exit_px = bar.o
            gross = (exit_px - pos.entry) * pos.qty
            pnl = gross - _cost(cfg, exit_px, pos.qty)
            equity += pnl
            res.trades.append(_close(pos, bar.date, exit_px, "bias-flip", pnl))
            pos = None
        pending_exit = False

        if pos is None and pending_entry and cooldown == 0:
            entry_px = bar.o
            stop = bars[i - 1].l                 # prior week's low
            r_unit = entry_px - stop
            if r_unit > 0:
                risk_rupees = cfg.risk_pct * equity
                qty = risk_rupees / r_unit
                target = entry_px + cfg.target_r * r_unit
                equity -= _cost(cfg, entry_px, qty)
                pos = Position(entry_px, stop, target, qty, r_unit, bar.date)
        pending_entry = False

        # 2) Intrabar management of an open position (stop checked before target).
        if pos is not None:
            if bar.l <= pos.stop:
                exit_px = pos.stop if bar.o >= pos.stop else bar.o   # gap-through fills at open
                gross = (exit_px - pos.entry) * pos.qty
                pnl = gross - _cost(cfg, exit_px, pos.qty)
                equity += pnl
                res.trades.append(_close(pos, bar.date, exit_px, "stop", pnl))
                pos = None
            elif bar.h >= pos.target:
                exit_px = pos.target if bar.o <= pos.target else bar.o
                gross = (exit_px - pos.entry) * pos.qty
                pnl = gross - _cost(cfg, exit_px, pos.qty)
                equity += pnl
                res.trades.append(_close(pos, bar.date, exit_px, "target", pnl))
                pos = None

        # 3) End-of-week decisions on the completed bar.
        b = bias_long(i)
        if pos is not None:
            pos.stop = max(pos.stop, bar.l)      # trail up to this week's low
            if b is False:
                pending_exit = True
        elif b is True and cooldown == 0:
            pending_entry = True

        # 4) Mark-to-market equity, drawdown, kill-switch / cooldown.
        mtm = equity + ((bar.c - pos.entry) * pos.qty if pos is not None else 0.0)
        peak = max(peak, mtm)
        dd = (peak - mtm) / peak if peak > 0 else 0.0
        if cooldown > 0:
            cooldown -= 1
        elif armed and dd >= cfg.kill_dd:
            cooldown = cfg.cooldown_weeks
            armed = False                       # stay disarmed until we recover
            res.kill_switch_hits += 1
        if not armed and dd <= cfg.kill_dd / 2:  # meaningful recovery re-arms it
            armed = True
        res.equity_curve.append((bar.date, mtm))

    # Close any open position at the last close.
    if pos is not None:
        last = bars[-1]
        gross = (last.c - pos.entry) * pos.qty
        pnl = gross - _cost(cfg, last.c, pos.qty)
        equity += pnl
        res.trades.append(_close(pos, last.date, last.c, "eod", pnl))

    res.final_equity = equity
    return res


def _close(pos: Position, date: str, exit_px: float, reason: str, pnl: float) -> Trade:
    risk_rupees = pos.r_unit * pos.qty
    return Trade(
        entry_date=pos.entry_date,
        exit_date=date,
        entry=pos.entry,
        exit=exit_px,
        qty=pos.qty,
        r_unit=pos.r_unit,
        reason=reason,
        pnl=pnl,
        r_multiple=(pnl / risk_rupees) if risk_rupees else 0.0,
    )


# --------------------------------------------------------------------------- #
# Metrics & reporting
# --------------------------------------------------------------------------- #
def _max_drawdown(curve: list[tuple[str, float]]) -> float:
    peak = -math.inf
    mdd = 0.0
    for _, v in curve:
        peak = max(peak, v)
        if peak > 0:
            mdd = max(mdd, (peak - v) / peak)
    return mdd


def _sharpe(curve: list[tuple[str, float]], periods_per_year: int = 52) -> float:
    vals = [v for _, v in curve]
    rets = [(vals[i] / vals[i - 1] - 1.0) for i in range(1, len(vals)) if vals[i - 1] > 0]
    if len(rets) < 2:
        return 0.0
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
    return (mean / sd) * math.sqrt(periods_per_year)


def report(bars: list[Bar], cfg: Config, res: Result) -> str:
    t = res.trades
    n = len(t)
    wins = [x for x in t if x.pnl > 0]
    losses = [x for x in t if x.pnl <= 0]
    strike = (len(wins) / n * 100) if n else 0.0
    avg_win_r = (sum(x.r_multiple for x in wins) / len(wins)) if wins else 0.0
    avg_loss_r = (sum(x.r_multiple for x in losses) / len(losses)) if losses else 0.0
    win_rate = len(wins) / n if n else 0.0
    expectancy_r = win_rate * avg_win_r + (1 - win_rate) * avg_loss_r
    total_ret = res.final_equity / cfg.capital - 1.0
    years = len(bars) / 52.0
    cagr = ((res.final_equity / cfg.capital) ** (1 / years) - 1.0) if years > 0 and res.final_equity > 0 else 0.0
    mdd = _max_drawdown(res.equity_curve)
    sharpe = _sharpe(res.equity_curve)
    calmar = (cagr / mdd) if mdd > 0 else float("inf")

    reasons: dict[str, int] = {}
    for x in t:
        reasons[x.reason] = reasons.get(x.reason, 0) + 1

    L = []
    L.append("=" * 60)
    L.append(" System A — NIFTY Weekly Momentum : Backtest Report")
    L.append("=" * 60)
    L.append(f" Bars (weeks)      : {len(bars)}  (~{years:.1f} yrs)  [{bars[0].date} -> {bars[-1].date}]")
    L.append(f" Start capital     : {cfg.capital:,.0f}")
    L.append(f" Risk / trade (R)  : {cfg.risk_pct*100:.2f}% of equity")
    L.append(f" Filter            : close>EMA({cfg.ema_period}) & RSI({cfg.rsi_period})>{cfg.rsi_threshold:.0f}"
             f" | target {cfg.target_r:.1f}R | cost {cfg.cost_bps:.1f}bps/side")
    L.append("-" * 60)
    L.append(f" Trades            : {n}   (wins {len(wins)} / losses {len(losses)})")
    L.append(f" Strike rate       : {strike:.1f}%")
    L.append(f" Avg win           : {avg_win_r:+.2f}R")
    L.append(f" Avg loss          : {avg_loss_r:+.2f}R")
    L.append(f" Expectancy/trade  : {expectancy_r:+.3f}R   <-- the number that matters")
    L.append(f" Exit breakdown    : " + ", ".join(f"{k}={v}" for k, v in sorted(reasons.items())))
    L.append("-" * 60)
    L.append(f" Final equity      : {res.final_equity:,.0f}")
    L.append(f" Total return      : {total_ret*100:+.1f}%")
    L.append(f" CAGR              : {cagr*100:+.1f}%")
    L.append(f" Max drawdown      : {mdd*100:.1f}%")
    L.append(f" Sharpe (ann.)     : {sharpe:.2f}")
    L.append(f" Calmar            : {calmar:.2f}" if math.isfinite(calmar) else " Calmar            : inf")
    L.append(f" Kill-switch hits  : {res.kill_switch_hits}  (pause {cfg.cooldown_weeks}w on >={cfg.kill_dd*100:.0f}% DD)")
    L.append("=" * 60)
    verdict = "POSITIVE expectancy after costs" if expectancy_r > 0 else "NON-POSITIVE expectancy after costs -> do NOT deploy"
    L.append(f" Verdict           : {verdict}")
    L.append("=" * 60)
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main() -> None:
    p = argparse.ArgumentParser(description="Backtest System A — NIFTY Weekly Momentum.")
    p.add_argument("--data", help="CSV of weekly OHLC (date,open,high,low,close). Omit for synthetic demo data.")
    p.add_argument("--capital", type=float, default=1_000_000.0)
    p.add_argument("--risk-pct", type=float, default=0.01, help="Risk per trade as fraction of equity (default 0.01).")
    p.add_argument("--ema", type=int, default=20)
    p.add_argument("--rsi-period", type=int, default=14)
    p.add_argument("--rsi-threshold", type=float, default=55.0)
    p.add_argument("--target-r", type=float, default=2.0)
    p.add_argument("--cost-bps", type=float, default=5.0, help="Per-side cost in bps of notional (default 5).")
    p.add_argument("--kill-dd", type=float, default=0.15)
    p.add_argument("--cooldown-weeks", type=int, default=4)
    p.add_argument("--seed", type=int, default=42, help="Seed for synthetic data (ignored with --data).")
    p.add_argument("--weeks", type=int, default=520, help="Weeks of synthetic data (ignored with --data).")
    p.add_argument("--equity-out", help="Optional path to write the equity curve as CSV.")
    args = p.parse_args()

    if args.data:
        bars = load_csv(args.data)
        source = f"real data: {args.data}"
    else:
        bars = synthetic_bars(n=args.weeks, seed=args.seed)
        source = f"SYNTHETIC demo data (seed={args.seed}) — NOT real market data"

    cfg = Config(
        capital=args.capital,
        risk_pct=args.risk_pct,
        ema_period=args.ema,
        rsi_period=args.rsi_period,
        rsi_threshold=args.rsi_threshold,
        target_r=args.target_r,
        cost_bps=args.cost_bps,
        kill_dd=args.kill_dd,
        cooldown_weeks=args.cooldown_weeks,
    )

    res = backtest(bars, cfg)
    print(f"[data source] {source}\n")
    print(report(bars, cfg, res))

    if args.equity_out:
        with open(args.equity_out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "equity"])
            w.writerows(res.equity_curve)
        print(f"\n[equity curve written] {args.equity_out}")


if __name__ == "__main__":
    main()
