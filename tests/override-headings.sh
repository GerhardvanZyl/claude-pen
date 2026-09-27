#!/usr/bin/env bash
# Every base-loop heading an override skill quotes (as a backticked `## ...`
# literal) must exist verbatim in the base skill. Catches a renamed phase in
# dev-loop / dev-loop-lite silently orphaning dev-loop-unity / dev-loop-greybox.
# Convention: plain bash, one line per assertion, exit non-zero on first failure.
set -euo pipefail
SKILLS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/user/.claude/skills"
ASSERTIONS=0

check() {
  local override="$SKILLS/$1/SKILL.md" base="$SKILLS/$2/SKILL.md" found=0
  [ -f "$override" ] || { echo "FAIL: $1 -- missing $override" >&2; exit 1; }
  while IFS= read -r heading; do
    found=$((found + 1))
    if grep -qxF "$heading" "$base"; then
      ASSERTIONS=$((ASSERTIONS + 1)); echo "PASS: $1 -> $2: $heading"
    else
      echo "FAIL: $1 quotes '$heading', not a heading in $2/SKILL.md" >&2; exit 1
    fi
  done < <(grep -oE '`##+ [^`]+`' "$override" | tr -d '`' | tr -d '\r' | sort -u)
  [ "$found" -gt 0 ] || { echo "FAIL: $1 quotes no $2 headings -- test would pass vacuously" >&2; exit 1; }

  local override_loops base_loops distinct=0
  override_loops="$(grep -oE '"loop":"[^"]*"' "$override" | tr -d '\r' | sort -u || true)"
  base_loops="$(grep -oE '"loop":"[^"]*"' "$base" | tr -d '\r' | sort -u || true)"
  if [ -z "$override_loops" ]; then
    echo "FAIL: $1 has no literal \"loop\":\"<value>\" string -- run identity is not overridden" >&2
    exit 1
  fi
  while IFS= read -r line; do
    if ! grep -qxF "$line" <<< "$base_loops"; then
      distinct=1
    fi
  done <<< "$override_loops"
  if [ "$distinct" -eq 1 ]; then
    ASSERTIONS=$((ASSERTIONS + 1))
    echo "PASS: $1 overrides run identity with a \"loop\" value distinct from $2"
  else
    echo "FAIL: $1's \"loop\" value(s) [$override_loops] match $2's [$base_loops] -- run identity not overridden" >&2
    exit 1
  fi
}

check dev-loop-unity dev-loop
check dev-loop-greybox dev-loop-lite
echo "OK: $ASSERTIONS assertions"
