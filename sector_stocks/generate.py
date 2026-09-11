"""Build the sector-performance dataset.

Fetches adjusted-close history for every constituent stock from Yahoo Finance,
computes 3/6/9/12-month growth %, aggregates to sector level, and writes a
single JSON file the dashboard (and any other consumer) can read.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from . import sectors as sectors_mod
from .performance import PERIODS, average_returns, compute_returns
from .yahoo import YahooError, fetch_series


def _fetch_one(stock, now):
    """Fetch + compute for a single stock; never raises."""
    try:
        series = fetch_series(stock.yahoo_symbol)
        metrics = compute_returns(series, now=now)
        metrics.update({
            "symbol": stock.symbol,
            "yahoo_symbol": stock.yahoo_symbol,
            "name": stock.name,
            "long_name": series.long_name or stock.name,
            "ok": True,
        })
        return stock.symbol, metrics
    except (YahooError, Exception) as exc:  # noqa: BLE001 - report, don't crash
        return stock.symbol, {
            "symbol": stock.symbol,
            "yahoo_symbol": stock.yahoo_symbol,
            "name": stock.name,
            "ok": False,
            "error": str(exc),
            "returns": {f"{m}m": None for m in PERIODS},
        }


def build(max_workers: int = 8, progress=True) -> dict:
    """Fetch all stocks and assemble the full dataset dict."""
    now = datetime.now(timezone.utc)
    index = sectors_mod.stock_index()
    symbols = list(index)

    if progress:
        print(f"Fetching {len(symbols)} unique stocks from Yahoo Finance ...",
              file=sys.stderr)

    # Fetch each unique symbol once (stocks appear in multiple sectors).
    results = {}
    done = 0
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_fetch_one, index[s], now): s for s in symbols}
        for fut in as_completed(futures):
            sym, data = fut.result()
            results[sym] = data
            done += 1
            if progress:
                status = "ok " if data.get("ok") else "ERR"
                print(f"  [{done:>3}/{len(symbols)}] {status} {sym}", file=sys.stderr)

    ok = sum(1 for d in results.values() if d.get("ok"))
    failed = [s for s, d in results.items() if not d.get("ok")]

    # Assemble per-sector views.
    out_sectors = []
    for sec in sectors_mod.all_sectors():
        members = [results[st.symbol] for st in sec.stocks]
        ok_members = [m for m in members if m.get("ok")]
        out_sectors.append({
            "key": sec.key,
            "name": sec.name,
            "macro": sec.macro,
            "num_stocks": len(members),
            "num_ok": len(ok_members),
            "average_returns": average_returns(ok_members),
            "stocks": members,
        })

    return {
        "meta": {
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "price_source": "Yahoo Finance (adjusted close)",
            "sector_source": "NSE industry classification (72 industry groups)",
            "periods_months": PERIODS,
            "return_type": "Adjusted-close price return (total return incl. splits & dividends)",
            "sector_aggregate": "Equal-weighted average of constituent returns",
            "macros": sectors_mod.MACROS,
            "num_sectors": len(out_sectors),
            "num_unique_stocks": len(symbols),
            "num_ok": ok,
            "num_failed": len(failed),
            "failed_symbols": failed,
        },
        "sectors": out_sectors,
    }


def write(path: str = "output/sector_performance.json", **kwargs) -> dict:
    data = build(**kwargs)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"\nWrote {out} — {data['meta']['num_ok']}/{data['meta']['num_unique_stocks']} "
          f"stocks OK across {data['meta']['num_sectors']} sectors.", file=sys.stderr)
    return data
