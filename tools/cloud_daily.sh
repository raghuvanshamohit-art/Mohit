#!/usr/bin/env bash
# Cloud Routine runner: run the live VCP F&O scan and write reports/ (timestamped
# + latest.*). Git commit/push and the summary are handled by the Routine
# session, not here. Bounded history: keeps the most recent ~90 dated reports.
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p reports

python run_screener.py \
    --provider bhavcopy --history-days 480 --workers 10 \
    --cache-dir cache/bhav --output-dir reports --min-passed 13

LC="$(ls -t reports/vcp_fno_*.csv 2>/dev/null | head -1 || true)"
LH="$(ls -t reports/vcp_fno_*.html 2>/dev/null | head -1 || true)"
[ -n "$LC" ] && cp -f "$LC" reports/latest.csv
[ -n "$LH" ] && cp -f "$LH" reports/latest.html

# Bound repo growth: keep the newest ~90 dated reports.
ls -t reports/vcp_fno_*.html 2>/dev/null | tail -n +91 | xargs -r rm -f
ls -t reports/vcp_fno_*.csv  2>/dev/null | tail -n +91 | xargs -r rm -f
