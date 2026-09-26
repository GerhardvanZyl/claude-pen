#!/usr/bin/env bash
# Every docs/diagrams/*.svg path referenced from README.md must exist on disk.
# Catches a renamed or missing diagram file silently breaking the <picture>
# embeds. Convention: plain bash, one line per assertion, exit non-zero on
# first failure.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
README="$ROOT/README.md"
[ -f "$README" ] || { echo "FAIL: missing $README" >&2; exit 1; }

CHECKED=0
while IFS= read -r path; do
  CHECKED=$((CHECKED + 1))
  if [ -f "$ROOT/$path" ]; then
    echo "PASS: $path exists"
  else
    echo "FAIL: README.md references $path, which does not exist" >&2
    exit 1
  fi
done < <(grep -oE 'docs/diagrams/[A-Za-z0-9_.-]+\.svg' "$README" | sort -u)

[ "$CHECKED" -gt 0 ] || { echo "FAIL: README.md references no docs/diagrams/*.svg paths -- test would pass vacuously" >&2; exit 1; }
echo "OK: $CHECKED diagram path(s) verified"
