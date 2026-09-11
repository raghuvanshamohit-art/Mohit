"""A tiny local web server for the live valuation app (standard library only).

Serves the ``valuation_live.html`` front-end and a JSON API that runs the full
intrinsic-value + pyramiding engine with **live** data fetched from Yahoo:

    GET /                 -> the calculator page
    GET /api/value?...    -> JSON report (same shape as `run.py value --json`)

Because the server runs on your own machine (not the browser sandbox), it can
reach Yahoo directly: the current price comes from the reliable chart endpoint,
and fundamentals (EPS, book value, growth, dividend) are auto-fetched from
Yahoo's quoteSummary where your network allows it. Anything Yahoo won't give is
filled from the query parameters you pass, and the report labels every input's
source.

Start it with:  ``python run.py serve``  then open http://127.0.0.1:8000/.
Localhost only by default — this is a personal dev tool, not a public service.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .engine import value_stock

_REPO_ROOT = Path(__file__).resolve().parent.parent
_HTML_PATH = _REPO_ROOT / "web" / "valuation_live.html"

# Query params that are percentages in the UI but decimals in the engine.
_PERCENT_PARAMS = {
    "growth": "growth_rate",
    "terminal_growth": "terminal_growth",
    "discount": "discount_rate",
    "mos": "margin_of_safety",
    "step": "step",
    "stop": "stop_pct",
}
# Query params passed straight through (already in engine units).
_PLAIN_PARAMS = {
    "eps": "eps",
    "bvps": "book_value_per_share",
    "fcf": "fcf_per_share",
    "dividend": "dividend_per_share",
    "price": "current_price",
    "fair_pe": "fair_pe",
    "bond_yield": "bond_yield",
    "trend_entry": "trend_entry",
}


def _f(params, key):
    """Parse a float query param, or None when absent/blank/invalid."""
    raw = params.get(key, [None])[0]
    if raw is None or raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def build_report(query: str) -> dict:
    """Turn a URL query string into a valuation report dict."""
    params = urllib.parse.parse_qs(query, keep_blank_values=False)
    symbol = (params.get("symbol", [""])[0] or "").strip()
    if not symbol:
        return {"error": "Enter a stock symbol (e.g. RELIANCE, TCS, AAPL)."}

    kwargs = {}
    for q_key, eng_key in _PERCENT_PARAMS.items():
        val = _f(params, q_key)
        if val is not None:
            kwargs[eng_key] = val / 100.0
    for q_key, eng_key in _PLAIN_PARAMS.items():
        val = _f(params, q_key)
        if val is not None:
            kwargs[eng_key] = val

    tranches = _f(params, "tranches")
    if tranches is not None:
        kwargs["tranches"] = max(1, int(tranches))
    years = _f(params, "years")
    if years is not None:
        kwargs["years"] = max(1, int(years))

    mode = (params.get("mode", ["value"])[0] or "value").strip()
    kwargs["pyramid_mode"] = "trend" if mode == "trend" else "value"
    weighting = (params.get("weighting", [""])[0] or "").strip()
    if weighting in ("increasing", "equal", "decreasing"):
        kwargs["weighting"] = weighting
    elif kwargs["pyramid_mode"] == "trend":
        kwargs["weighting"] = "decreasing"

    yahoo_symbol = (params.get("yahoo_symbol", [""])[0] or "").strip() or None
    auto = (params.get("auto", ["1"])[0] or "1") != "0"

    try:
        return value_stock(symbol=symbol, auto=auto, yahoo_symbol=yahoo_symbol, **kwargs)
    except Exception as exc:  # noqa: BLE001 - report errors as JSON, don't 500
        return {"error": f"{type(exc).__name__}: {exc}"}


class _Handler(BaseHTTPRequestHandler):
    server_version = "ValuationApp/1.0"

    def log_message(self, fmt, *args):  # quieter console
        sys.stderr.write("  %s\n" % (fmt % args))

    def _send(self, code, body: bytes, content_type: str):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            try:
                html = _HTML_PATH.read_bytes()
            except OSError:
                self._send(500, b"valuation_live.html not found", "text/plain; charset=utf-8")
                return
            self._send(200, html, "text/html; charset=utf-8")
            return

        if parsed.path == "/api/value":
            report = build_report(parsed.query)
            body = json.dumps(report, default=str).encode("utf-8")
            code = 400 if "error" in report else 200
            self._send(code, body, "application/json; charset=utf-8")
            return

        self._send(404, b"Not found", "text/plain; charset=utf-8")


def serve(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> None:
    """Run the live valuation web app until interrupted."""
    httpd = ThreadingHTTPServer((host, port), _Handler)
    url = f"http://{host}:{port}/"
    print(f"Live valuation app running at {url}", file=sys.stderr)
    print("Type a symbol in the page; press Ctrl+C here to stop.", file=sys.stderr)
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001 - headless is fine
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.", file=sys.stderr)
    finally:
        httpd.server_close()
