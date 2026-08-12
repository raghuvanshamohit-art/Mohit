#!/usr/bin/env bash
# Daily VCP F&O screener runner -- intended for an 8 PM IST scheduled job.
#
# Runs the screener, writes a timestamped CSV+HTML into output/, keeps
# output/latest.{csv,html} pointing at the newest run, and logs to logs/.
#
# Override the data source with environment variables:
#   VCP_PROVIDER    data source           (default: bhavcopy; e.g. yfinance | csv)
#   VCP_EXTRA_ARGS  extra flags forwarded verbatim to run_screener.py
#   PYTHON          python executable     (default: python3)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_DIR"

# Activate a local virtualenv if one exists.
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

PYTHON="${PYTHON:-python3}"
PROVIDER="${VCP_PROVIDER:-bhavcopy}"
EXTRA_ARGS="${VCP_EXTRA_ARGS:-}"

mkdir -p logs output
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_FILE="logs/vcp_${STAMP}.log"

echo "[$(date '+%F %T %Z')] starting VCP F&O screener (provider=$PROVIDER)" | tee -a "$LOG_FILE"

set +e
# shellcheck disable=SC2086
"$PYTHON" run_screener.py \
    --provider "$PROVIDER" \
    --cache-dir cache/bhav \
    --output-dir output \
    --min-passed 13 \
    $EXTRA_ARGS >>"$LOG_FILE" 2>&1
STATUS=$?
set -e

# Point latest.* at the newest reports (handy for a dashboard or a quick open).
LATEST_CSV="$(ls -t output/vcp_fno_*.csv 2>/dev/null | head -1 || true)"
LATEST_HTML="$(ls -t output/vcp_fno_*.html 2>/dev/null | head -1 || true)"
[ -n "$LATEST_CSV" ] && cp -f "$LATEST_CSV" output/latest.csv
[ -n "$LATEST_HTML" ] && cp -f "$LATEST_HTML" output/latest.html

# Keep the log directory tidy.
find logs -name 'vcp_*.log' -mtime +30 -delete 2>/dev/null || true

echo "[$(date '+%F %T %Z')] finished (exit=$STATUS). latest: ${LATEST_HTML:-none}" | tee -a "$LOG_FILE"
exit "$STATUS"
