"""Best-effort fundamentals auto-fetch (standard library only).

The intrinsic-value engine works entirely from explicitly supplied inputs; this
module is a *convenience* that tries to auto-fill EPS, book value, growth, etc.
so you don't have to type them. It uses a small **provider chain**:

1. **Yahoo** (``quoteSummary``) — free, no key, best coverage. But it needs a
   cookie + "crumb" handshake and Yahoo aggressively rate-limits datacenter /
   cloud IPs on it (HTTP 401), so it usually works from a home network and often
   fails from a server.
2. **Alpha Vantage** (``OVERVIEW``) — needs a free API key, but is reachable from
   cloud IPs, so it fills the gap when Yahoo is blocked. Set the key via the
   ``av_key`` argument or the ``ALPHAVANTAGE_API_KEY`` environment variable.

:func:`fetch_fundamentals` tries each available provider and merges the results,
tagging every field with the provider it came from. It raises
:class:`FundamentalsError` only when *no* provider yields anything; the engine
then falls back to whatever inputs were supplied. Nothing here is required for
the core calculation.
"""

from __future__ import annotations

import gzip
import http.cookiejar
import io
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from .intrinsic import Fundamentals

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Encoding": "gzip",
    "Accept-Language": "en-US,en;q=0.9",
}

_HOSTS = ["https://query1.finance.yahoo.com", "https://query2.finance.yahoo.com"]
_MODULES = "defaultKeyStatistics,financialData,summaryDetail,earningsTrend,price"

# Keep the fetch snappy: fundamentals are best-effort and Yahoo returns 401
# instantly when it blocks (cloud IPs), so a short, low-backoff loop fails fast
# instead of hanging the request for ~20 s before falling back to manual inputs.
_RETRY_SLEEP = 0.5  # seconds between attempts (× the 1-based attempt number)


class FundamentalsError(Exception):
    """Raised when Yahoo fundamentals cannot be fetched (blocked, missing, etc.)."""


def _read(resp) -> str:
    raw = resp.read()
    if resp.headers.get("Content-Encoding") == "gzip":
        raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
    return raw.decode("utf-8", "replace")


def _num(node):
    """Yahoo wraps numbers as ``{"raw": 1.23, "fmt": "1.23"}``; pull the raw float."""
    if isinstance(node, dict):
        node = node.get("raw")
    if node is None:
        return None
    try:
        val = float(node)
    except (TypeError, ValueError):
        return None
    return val if val == val else None  # drop NaN


def _five_year_growth(earnings_trend: dict):
    """Analyst long-term (+5y) growth estimate, as a decimal, if present."""
    for trend in earnings_trend.get("trend", []) or []:
        if trend.get("period") == "+5y":
            g = _num(trend.get("growth"))
            if g is not None:
                return g
    return None


def _raw_quote_summary(symbol: str, retries: int, timeout: int) -> dict:
    """Do the cookie -> crumb -> quoteSummary handshake; return the result node."""
    last_err = None
    for attempt in range(retries):
        host = _HOSTS[attempt % len(_HOSTS)]
        cookies = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cookies))

        def _get(url):
            req = urllib.request.Request(url, headers=_HEADERS)
            with opener.open(req, timeout=timeout) as resp:
                return _read(resp)

        try:
            # 1. Seed the session cookie by loading the quote page.
            _get(f"https://finance.yahoo.com/quote/{urllib.parse.quote(symbol)}")
            # 2. Get a crumb tied to that cookie.
            crumb = _get(f"{host}/v1/test/getcrumb").strip()
            if not crumb or "<" in crumb or len(crumb) > 40:
                raise FundamentalsError("no valid crumb returned")
            # 3. Fetch the fundamentals modules with the crumb.
            query = urllib.parse.urlencode({"modules": _MODULES, "crumb": crumb})
            url = (f"{host}/v10/finance/quoteSummary/"
                   f"{urllib.parse.quote(symbol)}?{query}")
            payload = json.loads(_get(url))
            qs = (payload.get("quoteSummary") or {})
            if qs.get("error"):
                raise FundamentalsError(str(qs["error"]))
            results = qs.get("result")
            if not results:
                raise FundamentalsError("empty quoteSummary result")
            return results[0]
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code in (401, 429, 500, 502, 503, 504):
                time.sleep(_RETRY_SLEEP * (attempt + 1))
                continue
            raise FundamentalsError(f"{symbol}: HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError,
                json.JSONDecodeError, FundamentalsError) as exc:
            last_err = exc
            time.sleep(_RETRY_SLEEP * (attempt + 1))
            continue
    raise FundamentalsError(
        f"{symbol}: fundamentals unavailable after {retries} attempts "
        f"(Yahoo often blocks quoteSummary from cloud IPs) — last error: {last_err}")


def fetch_yahoo(symbol: str, retries: int = 2, timeout: int = 8) -> Fundamentals:
    """Return a :class:`Fundamentals` populated from Yahoo, or raise on failure.

    ``symbol`` is a Yahoo symbol (e.g. ``RELIANCE.NS``). Each field is tagged in
    ``.provenance`` as ``"yahoo"`` so callers can see what was auto-filled.
    """
    r = _raw_quote_summary(symbol, retries, timeout)
    key_stats = r.get("defaultKeyStatistics", {}) or {}
    fin = r.get("financialData", {}) or {}
    summary = r.get("summaryDetail", {}) or {}
    price = r.get("price", {}) or {}
    earnings_trend = r.get("earningsTrend", {}) or {}

    eps = _num(key_stats.get("trailingEps"))
    bvps = _num(key_stats.get("bookValue"))
    shares = _num(key_stats.get("sharesOutstanding"))
    fcf_total = _num(fin.get("freeCashflow"))
    fcf_per_share = (fcf_total / shares) if (fcf_total and shares) else None

    # Prefer the analyst +5y growth; fall back to trailing earnings growth.
    growth = _five_year_growth(earnings_trend)
    if growth is None:
        growth = _num(fin.get("earningsGrowth"))

    fundamentals = Fundamentals(
        symbol=symbol,
        name=price.get("longName") or price.get("shortName") or "",
        currency=price.get("currency") or fin.get("financialCurrency") or "",
        eps=eps,
        book_value_per_share=bvps,
        fcf_per_share=fcf_per_share,
        dividend_per_share=_num(summary.get("dividendRate")),
        growth_rate=growth,
        fair_pe=_num(summary.get("trailingPE")),
        current_price=_num(fin.get("currentPrice")) or _num(price.get("regularMarketPrice")),
        shares_outstanding=shares,
    )

    for name in ("eps", "book_value_per_share", "fcf_per_share",
                 "dividend_per_share", "growth_rate", "fair_pe",
                 "current_price"):
        if getattr(fundamentals, name) is not None:
            fundamentals.provenance[name] = "yahoo"
    return fundamentals


# --------------------------------------------------------------------------- #
# Alpha Vantage provider (keyed; reachable from cloud IPs).
# --------------------------------------------------------------------------- #

_AV_URL = "https://www.alphavantage.co/query"


def _avnum(s):
    """Parse an Alpha Vantage numeric string; treat 'None'/'-'/'' as missing."""
    if s is None:
        return None
    s = str(s).strip()
    if s in ("", "None", "-", "0", "0.0"):
        # Alpha Vantage returns "0"/"None" for fields it doesn't have; treat a
        # literal zero EPS/book value as missing rather than a real figure.
        return None
    try:
        val = float(s)
    except ValueError:
        return None
    return val if val == val else None


def _to_av_symbol(symbol: str) -> str:
    """Map a Yahoo/NSE symbol to Alpha Vantage's convention.

    Alpha Vantage lists Indian equities under the BSE suffix ``.BSE``; US tickers
    are bare. So ``RELIANCE.NS`` / ``RELIANCE.BO`` -> ``RELIANCE.BSE`` and a bare
    ``AAPL`` stays ``AAPL``.
    """
    up = symbol.upper()
    if up.endswith(".NS") or up.endswith(".BO"):
        return up.rsplit(".", 1)[0] + ".BSE"
    return up


def fetch_alphavantage(symbol: str, api_key: str, timeout: int = 15) -> Fundamentals:
    """Return a :class:`Fundamentals` from Alpha Vantage's OVERVIEW, or raise."""
    if not api_key:
        raise FundamentalsError("no Alpha Vantage API key")
    av_symbol = _to_av_symbol(symbol)
    params = urllib.parse.urlencode(
        {"function": "OVERVIEW", "symbol": av_symbol, "apikey": api_key})
    req = urllib.request.Request(f"{_AV_URL}?{params}", headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(_read(resp))
    except (urllib.error.URLError, TimeoutError, ConnectionError,
            json.JSONDecodeError) as exc:
        raise FundamentalsError(f"Alpha Vantage: {exc}") from exc

    # Rate-limit / bad-key / empty responses come back as a note, not an error.
    if not data or "Symbol" not in data:
        note = data.get("Note") or data.get("Information") or data.get("Error Message")
        raise FundamentalsError(
            "Alpha Vantage returned no data for "
            f"{av_symbol}" + (f" — {note}" if note else " (rate limit or unknown symbol)"))

    growth = _avnum(data.get("QuarterlyEarningsGrowthYOY"))
    fundamentals = Fundamentals(
        symbol=symbol,
        name=data.get("Name") or "",
        currency=data.get("Currency") or "",
        eps=_avnum(data.get("EPS")),
        book_value_per_share=_avnum(data.get("BookValue")),
        dividend_per_share=_avnum(data.get("DividendPerShare")),
        growth_rate=growth if (growth is not None and growth > 0) else None,
        fair_pe=_avnum(data.get("PERatio")),
    )
    for name in ("eps", "book_value_per_share", "dividend_per_share",
                 "growth_rate", "fair_pe"):
        if getattr(fundamentals, name) is not None:
            fundamentals.provenance[name] = "alphavantage"
    return fundamentals


# --------------------------------------------------------------------------- #
# Orchestrator: try providers in order and merge what they return.
# --------------------------------------------------------------------------- #

_MERGE_FIELDS = ("eps", "book_value_per_share", "fcf_per_share",
                 "dividend_per_share", "growth_rate", "fair_pe",
                 "current_price", "shares_outstanding")


def fetch_fundamentals(symbol: str, av_key: "str | None" = None,
                       retries: int = 2, timeout: int = 8) -> Fundamentals:
    """Auto-fetch fundamentals via the provider chain, merged, or raise.

    Tries Yahoo first (free, best coverage), then Alpha Vantage when an API key
    is available (``av_key`` or the ``ALPHAVANTAGE_API_KEY`` env var). Fields are
    taken from the first provider that has them and tagged with that provider in
    ``.provenance``. Raises :class:`FundamentalsError` only if every provider
    fails.
    """
    api_key = av_key or os.environ.get("ALPHAVANTAGE_API_KEY") or ""

    providers = [("yahoo", lambda: fetch_yahoo(symbol, retries=retries, timeout=timeout))]
    if api_key:
        providers.append(("alphavantage", lambda: fetch_alphavantage(symbol, api_key)))

    merged = Fundamentals(symbol=symbol)
    errors = []
    got_any = False
    for _name, call in providers:
        try:
            part = call()
        except Exception as exc:  # noqa: BLE001 - remember and try the next one
            errors.append(str(exc))
            continue
        got_any = True
        if part.name and not merged.name:
            merged.name = part.name
        if part.currency and not merged.currency:
            merged.currency = part.currency
        for field_name in _MERGE_FIELDS:
            if getattr(merged, field_name) is None:
                val = getattr(part, field_name, None)
                if val is not None:
                    setattr(merged, field_name, val)
                    if field_name in part.provenance:
                        merged.provenance[field_name] = part.provenance[field_name]
        # Stop early once we have the essentials (EPS is enough to value).
        if merged.eps is not None:
            break

    if not got_any:
        raise FundamentalsError(
            f"{symbol}: fundamentals unavailable from all providers — "
            + " | ".join(errors))
    return merged
