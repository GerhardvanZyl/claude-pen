#!/usr/bin/env bash
# Verifies the filesystem contract install.sh promises:
#   - baseline coding-standards skill lands at the user level, not the project level
#   - <repo>/.claude/standards.md is installed once and never clobbered on re-install
#   - an edited standards.md survives a re-install byte-for-byte, with the bundled
#     version offered beside it as standards.new.md
#   - a missing standards.md is restored, with no .new file left behind
#   - an install that fails partway through destroys neither
#   - --dry-run writes nothing, anywhere
#
# This script actually runs install.sh from the repo under test -- it does not
# reimplement the installer's logic. HOME and the target "repo" are both
# redirected to scratch temp directories for the duration of the run and
# removed on exit (including on failure), so the real ~/.claude and the real
# repo this script lives in are never touched.
#
# Convention for anything added to tests/ later: plain bash, no framework, no
# dependencies beyond coreutils and git, one line of output per assertion,
# exit non-zero on the first failure.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_SH="$REPO_ROOT/install.sh"

if [ ! -f "$INSTALL_SH" ]; then
  echo "FAIL: setup -- install.sh not found at $INSTALL_SH" >&2
  exit 1
fi

TMP_HOME="$(mktemp -d)"
TMP_WORK="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_HOME" "$TMP_WORK"
}
trap cleanup EXIT

export HOME="$TMP_HOME"

ASSERTIONS=0

pass() {
  ASSERTIONS=$((ASSERTIONS + 1))
  echo "PASS: $1"
}

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

assert_exists() {
  local path="$1" desc="$2"
  if [ -e "$path" ]; then pass "$desc"; else fail "$desc -- expected to exist: $path"; fi
}

assert_not_exists() {
  local path="$1" desc="$2"
  if [ ! -e "$path" ]; then pass "$desc"; else fail "$desc -- expected NOT to exist: $path"; fi
}

assert_files_identical() {
  local a="$1" b="$2" desc="$3"
  if cmp -s "$a" "$b"; then
    pass "$desc"
    return
  fi
  echo "FAIL: $desc" >&2
  echo "  files differ: $a vs $b" >&2
  cmp "$a" "$b" >&2 || true
  exit 1
}

# Content digest of a directory tree: path + hash of every file, hashed
# together. Used to prove --dry-run left a tree byte-for-byte alone.
#
# Deliberately avoids `find`/`sort`/`xargs`: on at least one real dev machine
# this script is meant to run on, corporate endpoint security blocks those two
# binaries by name even though their permission bits are unremarkable --
# `sha256sum` and `cmp` are unaffected. Bash's own recursive glob (globstar)
# does the walk instead, so the script keeps working in that environment. The
# two snapshots being compared always come from the same unmodified directory
# read twice in the same process, so glob enumeration order does not need to
# be independently sorted -- it only needs to be consistent with itself.
snapshot() {
  local dir="$1"
  if [ ! -d "$dir" ]; then printf 'MISSING:%s' "$dir"; return; fi
  local out="" f
  shopt -s globstar nullglob
  for f in "$dir"/**; do
    [ -f "$f" ] && out+="$(sha256sum "$f")"$'\n'
  done
  shopt -u globstar nullglob
  printf '%s' "$out" | sha256sum
}

run_install() {
  local label="$1"; shift
  local slug
  slug="$(echo "$label" | tr -c 'A-Za-z0-9' '-')"
  local log="$TMP_WORK/log-$slug.txt"
  if ! bash "$INSTALL_SH" "$@" >"$log" 2>&1; then
    fail "$label -- install.sh exited non-zero, see $log"
  fi
}

run_install_expect_failure() {
  local label="$1"; shift
  local slug
  slug="$(echo "$label" | tr -c 'A-Za-z0-9' '-')"
  local log="$TMP_WORK/log-$slug.txt"
  if bash "$INSTALL_SH" "$@" >"$log" 2>&1; then
    fail "$label -- install.sh was expected to fail but exited zero, see $log"
  fi
}

# Deliberately not plain ASCII: a UTF-8 BOM, a non-ASCII character, a CRLF and
# no trailing newline. A restore that round-trips the file through a text decode
# instead of copying its bytes changes at least one of those whatever the
# default encoding is, so the byte comparison catches a file that was reported
# untouched but was really rewritten.
write_sentinel() {
  local tag="$1" path="$2"
  printf '\xef\xbb\xbf# %s\r\nnon-ASCII \xe2\x80\x94 and no trailing newline' "$tag" > "$path"
}

echo "=== Fresh install into an empty scratch repo ==="
SCRATCH="$TMP_WORK/repo"
mkdir -p "$SCRATCH"
run_install "fresh install" "$SCRATCH"

assert_exists "$HOME/.claude/skills/coding-standards/SKILL.md" \
  "baseline coding-standards skill lands at user level"
assert_exists "$SCRATCH/.claude/standards.md" \
  "per-repo standards.md is installed"
assert_not_exists "$SCRATCH/.claude/skills/coding-standards" \
  "project-level coding-standards skill does not come back"
assert_exists "$SCRATCH/.claude/skills/implement-sprint" \
  "bulk project-layer copy still lands implement-sprint"
assert_not_exists "$SCRATCH/.claude/standards.new.md" \
  "no standards.new.md on a fresh install"

echo
echo "=== Re-install over an edited standards.md ==="
SENTINEL="SENTINEL-install-contract-test-$$-$(date +%s)"
write_sentinel "$SENTINEL" "$SCRATCH/.claude/standards.md"
EXPECTED_SENTINEL="$TMP_WORK/expected-sentinel.md"
cp "$SCRATCH/.claude/standards.md" "$EXPECTED_SENTINEL"

run_install "re-install over edited standards.md" "$SCRATCH"

assert_files_identical "$SCRATCH/.claude/standards.md" "$EXPECTED_SENTINEL" \
  "edited standards.md survives re-install byte-identical"
assert_exists "$SCRATCH/.claude/standards.new.md" \
  "bundled version offered as standards.new.md"
assert_files_identical "$SCRATCH/.claude/standards.new.md" "$REPO_ROOT/project/.claude/standards.md" \
  "standards.new.md matches the bundled project/.claude/standards.md"

echo
echo "=== Re-install with standards.md missing, rest of .claude present ==="
rm -f "$SCRATCH/.claude/standards.md" "$SCRATCH/.claude/standards.new.md"

run_install "re-install with standards.md missing" "$SCRATCH"

assert_exists "$SCRATCH/.claude/standards.md" \
  "standards.md is restored when missing"
assert_files_identical "$SCRATCH/.claude/standards.md" "$REPO_ROOT/project/.claude/standards.md" \
  "restored standards.md matches the bundled version"
assert_not_exists "$SCRATCH/.claude/standards.new.md" \
  "no standards.new.md appears when nothing needed merging"

echo
echo "=== Dry run writes nothing ==="
HOME_SKILLS_BEFORE="$(snapshot "$HOME/.claude/skills")"
DRY_SCRATCH="$TMP_WORK/dryrun-repo"
mkdir -p "$DRY_SCRATCH"

run_install "dry run" "$DRY_SCRATCH" --dry-run

assert_not_exists "$DRY_SCRATCH/.claude" \
  "dry run into a fresh scratch dir writes no .claude directory"
HOME_SKILLS_AFTER="$(snapshot "$HOME/.claude/skills")"
if [ "$HOME_SKILLS_BEFORE" = "$HOME_SKILLS_AFTER" ]; then
  pass "dry run leaves \$HOME/.claude/skills unchanged"
else
  fail "dry run leaves \$HOME/.claude/skills unchanged -- digest before=$HOME_SKILLS_BEFORE after=$HOME_SKILLS_AFTER"
fi

echo
echo "=== A failure mid-install does not destroy the repository's standards.md ==="
# The project layer is copied over <repo>/.claude wholesale and standards.md
# lives inside it, so anything that can fail while that copy is in flight -- a
# permission error, a full disk, an antivirus lock, a Ctrl-C -- can take the one
# file the non-clobber contract promises to leave alone. Standing in for all of
# those: replace ARCHITECTURE.template.md with a directory of the same name.
# Copying a file over a directory fails on every platform, deterministically,
# and the installer needs no test hook for it to happen.
FAULT="$TMP_WORK/fault-repo"
mkdir -p "$FAULT"
run_install "fresh install into the fault-injection repo" "$FAULT"

write_sentinel "$SENTINEL-fault" "$FAULT/.claude/standards.md"
EXPECTED_FAULT="$TMP_WORK/expected-fault.md"
cp "$FAULT/.claude/standards.md" "$EXPECTED_FAULT"

rm -f "$FAULT/ARCHITECTURE.template.md"
mkdir -p "$FAULT/ARCHITECTURE.template.md"

run_install_expect_failure "re-install that fails partway through" "$FAULT"

assert_files_identical "$FAULT/.claude/standards.md" "$EXPECTED_FAULT" \
  "an install that fails partway through leaves the edited standards.md intact"
assert_exists "$FAULT/.claude/standards.new.md" \
  "an install that fails partway through still honours the standards.new.md contract"

echo
echo "All $ASSERTIONS assertions passed."
