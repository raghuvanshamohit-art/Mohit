"""Optional live fetch of sector constituents from NSE.

The National Stock Exchange of India publishes the live membership of each
sectoral index at ``/api/equity-stockIndices?index=<INDEX NAME>``. Accessing it
requires first visiting the site to obtain session cookies.

NSE aggressively blocks non-Indian / datacenter / cloud IP ranges (Akamai edge
denial, HTTP 403), so this refresh will usually fail from a server. When it
does, callers fall back to the bundled constituents in ``sectors.py`` — which
mirror the same NSE sectoral indices. This module makes the "data from NSE"
path real when the exchange is reachable, and honest when it is not.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

_BASE = "https://www.nseindia.com"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/market-data/live-equity-market",
}


class NSEUnavailable(Exception):
    """Raised when NSE cannot be reached (typically an IP block)."""


def _session_opener(timeout: int = 20):
    """Build a cookie-bearing opener by priming an NSE homepage visit."""
    import http.cookiejar

    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    req = urllib.request.Request(_BASE + "/", headers=_HEADERS)
    try:
        opener.open(req, timeout=timeout).read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise NSEUnavailable(f"NSE homepage unreachable: {exc}") from exc
    return opener


def fetch_index_constituents(index_name: str, timeout: int = 20) -> list:
    """Return ``[(symbol, company_name), ...]`` for one NSE sectoral index.

    Raises :class:`NSEUnavailable` if NSE blocks the request.
    """
    opener = _session_opener(timeout=timeout)
    url = _BASE + "/api/equity-stockIndices?index=" + urllib.parse.quote(index_name)
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        body = opener.open(req, timeout=timeout).read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise NSEUnavailable(f"NSE API blocked for '{index_name}': {exc}") from exc

    payload = json.loads(body.decode("utf-8"))
    out = []
    for row in payload.get("data", []):
        sym = row.get("symbol", "")
        # The index row itself (e.g. "NIFTY IT") is not a constituent.
        if not sym or sym.upper().startswith("NIFTY"):
            continue
        out.append((sym, row.get("meta", {}).get("companyName", sym)))
    if not out:
        raise NSEUnavailable(f"NSE returned no constituents for '{index_name}'")
    return out
