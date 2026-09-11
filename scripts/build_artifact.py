#!/usr/bin/env python3
"""Build the standalone screener artifact (data embedded) from the template.

Reads ``web/screener_template.html`` (which contains a ``/*__DATA__*/``
placeholder inside a JSON <script> tag) and ``output/sector_performance.json``,
and writes ``web/screener.html`` with the data embedded so the page needs no
network access — suitable for publishing as a Claude artifact.

Usage:
    python scripts/build_artifact.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "web" / "screener_template.html"
DATASET = ROOT / "output" / "sector_performance.json"
OUT = ROOT / "web" / "screener.html"


def main() -> int:
    tpl = TEMPLATE.read_text(encoding="utf-8")
    raw = DATASET.read_text(encoding="utf-8")

    # Embedding inside a <script> tag: the JSON must not contain a closing tag.
    if "</script" in raw.lower():
        print("ERROR: dataset contains a </script> sequence; refusing to embed.",
              file=sys.stderr)
        return 1

    # Fail loudly on a clearly-broken dataset rather than shipping empty tables.
    data = json.loads(raw)
    meta = data.get("meta", {})
    n, ok = meta.get("num_unique_stocks", 0), meta.get("num_ok", 0)
    if not n or ok / n < 0.8:
        print(f"ERROR: coverage too low ({ok}/{n}); not building artifact.",
              file=sys.stderr)
        return 1

    if "/*__DATA__*/" not in tpl:
        print("ERROR: template is missing the /*__DATA__*/ placeholder.", file=sys.stderr)
        return 1

    OUT.write_text(tpl.replace("/*__DATA__*/", raw), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} — {ok}/{n} stocks, "
          f"{meta.get('num_sectors', '?')} sectors ({len(tpl) + len(raw)} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
