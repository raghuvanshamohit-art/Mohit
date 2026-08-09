#!/usr/bin/env bash
# build_home.sh — regenerate the homepage content block in README.md straight
# from the real entries in knowledge/*.md, so the homepage always shows the
# exact current content. Called automatically by capture.sh; safe to run anytime.

set -euo pipefail
cd "$(dirname "$0")"

# Print a section file's entries: everything after the <!-- ENTRIES --> marker,
# dropping the placeholder line, and demoting "## " entry headings to "### " so
# they nest correctly under the homepage's "## Section" headings.
extract() {
  awk '
    seen {
      if ($0 ~ /^_Nothing here yet/) next
      line = $0
      sub(/^## /, "### ", line)
      print line
    }
    /<!-- ENTRIES -->/ { seen = 1 }
  ' "$1" | sed '/./,$!d'
}

section() {
  local title="$1" file="$2" body
  printf '## %s\n\n' "$title"
  body="$(extract "$file")"
  if printf '%s' "$body" | grep -q '[^[:space:]]'; then
    printf '%s\n\n' "$body"
  else
    printf '_Nothing here yet._\n\n'
  fi
}

content="$(
  section "🔎 Searches" "knowledge/searches.md"
  section "📚 Studies"  "knowledge/studies.md"
  section "💡 Notes"    "knowledge/notes.md"
)"

marker_note='<!-- This block is generated from knowledge/*.md by ./build_home.sh — do not edit by hand. -->'

# Keep everything up to and including HOME:START, then our generated content,
# then everything from HOME:END onward. Avoids fragile in-place editing.
before="$(awk '{ print } /<!-- HOME:START -->/ { exit }' README.md)"
after="$(awk '/<!-- HOME:END -->/ { p = 1 } p { print }' README.md)"

{
  printf '%s\n' "$before"
  printf '%s\n\n' "$marker_note"
  printf '%s\n' "$content"
  printf '%s\n' "$after"
} > README.tmp && mv README.tmp README.md

echo "Homepage rebuilt from knowledge/*.md"
