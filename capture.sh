#!/usr/bin/env bash
# capture.sh — quickly add a dated entry to the knowledge base.
#
# Usage:
#   ./capture.sh <searches|studies|notes> "Title" "Body text..."
#
# Examples:
#   ./capture.sh searches "React hooks" "useEffect runs after render"
#   ./capture.sh studies  "Spanish"     "Past-tense conjugations"
#   ./capture.sh notes    "Idea"        "A blog post about ..."

set -euo pipefail
cd "$(dirname "$0")"

usage() {
  echo "Usage: $0 <searches|studies|notes> \"Title\" \"Body\"" >&2
  exit 1
}

[ "$#" -ge 2 ] || usage

case "${1:-}" in
  s|search|searches)          file="knowledge/searches.md" ;;
  st|study|studies)           file="knowledge/studies.md" ;;
  n|note|notes|k|knowledge)   file="knowledge/notes.md" ;;
  *) usage ;;
esac
shift

title="$1"; shift
body="${*:-}"
date="$(date +%Y-%m-%d)"

if [ ! -f "$file" ]; then
  echo "Missing $file" >&2
  exit 1
fi

tmp="$(mktemp)"
awk -v d="$date" -v t="$title" -v b="$body" '
  /^_Nothing here yet/ { next }          # drop placeholder once real content exists
  { print }
  /<!-- ENTRIES -->/ && !ins {
    print "";
    print "## " d " \xe2\x80\x94 " t;     # "YYYY-MM-DD — Title"
    print "";
    print b;
    ins = 1
  }
' "$file" > "$tmp"

mv "$tmp" "$file"
echo "Added to $file:  $date — $title"
