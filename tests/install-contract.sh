#!/usr/bin/env bash
# Verifies the filesystem contract install.sh promises:
#   - baseline coding-standards skill lands at the user level, not the project level
#   - <repo>/.claude/standards.md is installed once and never clobbered on re-install
#   - an edited standards.md survives a re-install byte-for-byte, with the bundled
#     version offered beside it as standards.new.md
#   - a missing standards.md is restored, with no .new file left behind
#   - an install that fails partway through destroys neither
#   - --dry-run writes nothing, anywhere
#   - the vendored dev-loop-inspector mod is complete, its two manifests agree
#     on the plugin name, and the installer prints the enablement commands
#     while writing nothing at all for it
#   - the printed enablement commands name the shells their quoting is for, and
#     are safe to paste from a bundle directory whose name carries shell
#     metacharacters
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
LAST_INSTALL_LOG=""

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

assert_equal() {
  local actual="$1" expected="$2" desc="$3"
  if [ "$actual" = "$expected" ]; then
    pass "$desc"
  else
    fail "$desc -- expected [$expected], got [$actual]"
  fi
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

# Literal substring checks against a captured install log. -F because every
# needle here is a command line full of slashes, quotes and dashes, and -- so
# the one that starts with -- is not read as an option.
assert_log_contains() {
  local log="$1" needle="$2" desc="$3"
  if grep -qF -- "$needle" "$log"; then pass "$desc"; else fail "$desc -- not in $log: $needle"; fi
}

assert_log_lacks() {
  local log="$1" needle="$2" desc="$3"
  if grep -qF -- "$needle" "$log"; then fail "$desc -- found in $log: $needle"; else pass "$desc"; fi
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

# Reads one "name" value out of a JSON manifest, from the first match inside a
# sed line range. No jq: this suite's dependency list is coreutils and git, and
# jq is on neither, nor is it installable on the locked-down machine the
# find/sort note above refers to.
#
# What the shortcut costs, stated rather than glossed: it is line-oriented and
# order-dependent, so it relies on the manifests staying pretty-printed one key
# per line, it would return the wrong value if a nested "name" (an author's,
# say) came before the intended one inside the range, and it would mangle a
# value containing an escaped quote or a \u escape. None of that can weaken an
# assertion silently -- every value it extracts is compared against a literal
# below, so a misparse fails the comparison rather than passing it vacuously.
json_name_in_range() {
  local file="$1" range="$2"
  { sed -n "${range}p" "$file" \
      | grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' \
      | sed -n '1s/^"name"[[:space:]]*:[[:space:]]*"\(.*\)"$/\1/p'; } || true
}

MOD_HEADER='=== Mod: dev-loop-inspector ==='

# Everything the installer prints for the mod, from its section header up to the
# next section. The idempotence assertion compares two of these rather than two
# whole logs because the surrounding output names a backup directory stamped to
# the second, which differs between two runs by construction.
mod_section() {
  local line out="" in_section=""
  while IFS= read -r line; do
    # install.sh is CRLF in the working tree here (core.autocrlf, no
    # .gitattributes). Git for Windows' bash drops the CR, so the log comes out
    # clean -- but a bash that does not would leave the header unmatchable and
    # this function would return nothing.
    line="${line%$'\r'}"
    if [ -n "$in_section" ] && [ "${line:0:4}" = "=== " ]; then break; fi
    if [ "$line" = "$MOD_HEADER" ]; then in_section=1; fi
    if [ -n "$in_section" ]; then out+="$line"$'\n'; fi
  done < "$1"
  printf '%s' "$out"
}

run_install() {
  local label="$1"; shift
  local slug
  slug="$(echo "$label" | tr -c 'A-Za-z0-9' '-')"
  local log="$TMP_WORK/log-$slug.txt"
  LAST_INSTALL_LOG="$log"
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

# Baseline for the plugin-registry assertion in the mod section, taken here and
# not beside the install it guards: HOME is still pristine, so a digest taken
# now catches an installer that *creates* ~/.claude/plugins as well as one that
# edits it. A before/after pair around a single later install cannot -- an
# earlier install would already have put the same bytes there, leaving the pair
# equal and the assertion green.
PRISTINE_PLUGINS="$(snapshot "$HOME/.claude/plugins")"

echo "=== Fresh install into an empty scratch repo ==="
SCRATCH="$TMP_WORK/repo"
mkdir -p "$SCRATCH"
run_install "fresh install" "$SCRATCH"

assert_exists "$HOME/.claude/skills/coding-standards/SKILL.md" \
  "baseline coding-standards skill lands at user level"
assert_exists "$HOME/.claude/skills/backlog-refinement/SKILL.md" \
  "backlog-refinement skill lands at user level"
assert_exists "$SCRATCH/.claude/standards.md" \
  "per-repo standards.md is installed"
assert_not_exists "$SCRATCH/.claude/skills/coding-standards" \
  "project-level coding-standards skill does not come back"
assert_not_exists "$SCRATCH/.claude/skills/backlog-refinement" \
  "project-level backlog-refinement skill does not come back"
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
# The mod section is the one part of the installer that could plausibly write
# outside the two trees above -- ~/.claude/plugins is where Claude Code keeps
# its own plugin registry, and an installer that decided to "help" would write
# there. Nothing under skills/ would move if it did, so the dry-run guarantee
# needs its own digest for that path.
HOME_PLUGINS_BEFORE="$(snapshot "$HOME/.claude/plugins")"
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
HOME_PLUGINS_AFTER="$(snapshot "$HOME/.claude/plugins")"
if [ "$HOME_PLUGINS_BEFORE" = "$HOME_PLUGINS_AFTER" ]; then
  pass "dry run leaves ~/.claude/plugins unchanged"
else
  fail "dry run leaves ~/.claude/plugins unchanged -- digest before=$HOME_PLUGINS_BEFORE after=$HOME_PLUGINS_AFTER"
fi
# Writing nothing is only half the dry-run contract: the mod section reports
# either way, because what it reports is all it ever does.
DRY_MOD_SECTION="$TMP_WORK/mod-section-dry.txt"
mod_section "$LAST_INSTALL_LOG" > "$DRY_MOD_SECTION"
assert_log_contains "$DRY_MOD_SECTION" "/plugin install dev-loop-inspector@claude-pen" \
  "dry run still prints the mod enablement commands"

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
echo "=== Mod: dev-loop-inspector ==="
# Nothing is copied for the mod. A marketplace whose source is a relative path
# is read from the bundle folder in place, so the installer's entire job is to
# verify the vendored tree and print the two enablement commands -- which makes
# most of what follows an assertion that nothing happened.
MOD_DIR="$REPO_ROOT/plugin/dev-loop-inspector"
PLUGIN_JSON="$MOD_DIR/.claude-plugin/plugin.json"
MARKETPLACE_JSON="$REPO_ROOT/.claude-plugin/marketplace.json"

assert_exists "$PLUGIN_JSON" \
  "vendored mod carries its plugin manifest"
assert_exists "$MOD_DIR/hooks/hooks.json" \
  "vendored mod carries its hooks manifest"
assert_exists "$MOD_DIR/hooks/register.tsx" \
  "vendored mod carries its hook source"
assert_exists "$MARKETPLACE_JSON" \
  "repository root carries the marketplace manifest"

# The failure these three guard against is the quiet one: if the marketplace
# entry and the plugin manifest disagree on the name, /plugin install answers
# `Plugin "..." not found in marketplace` and nothing else in the bundle shows
# any symptom. The marketplace's own name is pinned for the same reason -- it is
# the half after the @ in the command the installer prints below, so a rename
# there breaks the route while both manifests stay internally consistent.
MOD_PLUGIN_NAME="$(json_name_in_range "$PLUGIN_JSON" '1,$')"
MOD_ENTRY_NAME="$(json_name_in_range "$MARKETPLACE_JSON" '/"plugins"/,$')"
MOD_MARKET_NAME="$(json_name_in_range "$MARKETPLACE_JSON" '1,/"plugins"/')"
assert_equal "$MOD_PLUGIN_NAME" "dev-loop-inspector" \
  "plugin manifest names the mod dev-loop-inspector"
assert_equal "$MOD_ENTRY_NAME" "$MOD_PLUGIN_NAME" \
  "marketplace entry name matches the plugin manifest name"
assert_equal "$MOD_MARKET_NAME" "claude-pen" \
  "marketplace manifest names the marketplace claude-pen"

# Enabling a plugin is the user's decision and it is recorded in a settings
# file, so the installer must leave those alone as firmly as it leaves the
# registry alone. Both settings files are planted with sentinel bytes before the
# run, which makes this a non-clobber assertion rather than the weaker
# non-creation one; settings.local.json is left absent instead, because nothing
# in the bundle ships one and creating it is the whole risk.
MOD_SCRATCH="$TMP_WORK/mod-repo"
mkdir -p "$MOD_SCRATCH/.claude"
write_sentinel "$SENTINEL-user-settings" "$HOME/.claude/settings.json"
write_sentinel "$SENTINEL-repo-settings" "$MOD_SCRATCH/.claude/settings.json"
EXPECTED_USER_SETTINGS="$TMP_WORK/expected-user-settings.json"
EXPECTED_REPO_SETTINGS="$TMP_WORK/expected-repo-settings.json"
cp "$HOME/.claude/settings.json" "$EXPECTED_USER_SETTINGS"
cp "$MOD_SCRATCH/.claude/settings.json" "$EXPECTED_REPO_SETTINGS"

run_install "install with the mod present" "$MOD_SCRATCH"

assert_files_identical "$HOME/.claude/settings.json" "$EXPECTED_USER_SETTINGS" \
  "install leaves an existing user-level settings.json byte-identical"
assert_not_exists "$HOME/.claude/settings.local.json" \
  "install creates no user-level settings.local.json"
assert_files_identical "$MOD_SCRATCH/.claude/settings.json" "$EXPECTED_REPO_SETTINGS" \
  "install leaves an existing repo settings.json byte-identical"
assert_not_exists "$MOD_SCRATCH/.claude/settings.local.json" \
  "install creates no settings.local.json in the target repo"

# The printed commands are the only output of this section anyone acts on, so
# they are asserted as literal text. The quotes around the path are part of the
# contract, not formatting: this bundle's own folder name contains a space, and
# an unquoted path would split on it. Single quotes rather than double, because
# a double-quoted path re-enters the shell parser when the line is pasted --
# the hostile-path block further down is what pins that down.
#
# The positives read the extracted section rather than the whole log, which is
# what keeps the idempotence comparison below honest: an extraction that
# matched nothing would compare empty against empty and pass, and these fail on
# an empty section.
MOD_SECTION_FIRST="$TMP_WORK/mod-section-1.txt"
mod_section "$LAST_INSTALL_LOG" > "$MOD_SECTION_FIRST"
assert_log_contains "$MOD_SECTION_FIRST" "/plugin install dev-loop-inspector@claude-pen" \
  "install prints the marketplace-qualified /plugin install command"
assert_log_contains "$MOD_SECTION_FIRST" "claude plugin marketplace add '$REPO_ROOT'" \
  "install prints the marketplace add command with the bundle path quoted"

# The label is contract text, not decoration: single quotes are right for bash
# and PowerShell and mean nothing in cmd.exe, where a bundle name carrying one
# of that shell's separators -- & ^ ( ) -- splits the line and runs the rest.
# No quoting fixes all three at once, so naming the two this form is for is the
# only thing standing between the printed line and a cmd.exe paste.
assert_log_contains "$MOD_SECTION_FIRST" "1. in bash (not cmd.exe) --" \
  "install names the shell the printed quoting is correct for"

# The verdict itself, both halves of it. Without these the branch that decides
# what the user is told could be inverted, or its needed-file list could name a
# file that does not exist, and every other assertion here would stay green.
assert_log_contains "$MOD_SECTION_FIRST" "vendored source and marketplace entry present" \
  "a complete bundle reports the vendored source and marketplace entry present"
assert_log_lacks "$MOD_SECTION_FIRST" "! missing" \
  "a complete bundle names no missing file"

# `--marketplace <name>` is asserted absent deliberately, and over the whole log
# rather than the section, since the closing hints talk about the mod too. That
# flag takes a marketplace *source* -- a path, a URL, owner/repo -- and adds it,
# so pairing it with the name of a marketplace already added is rejected by the
# CLI; the valid way to name an added marketplace is <plugin>@<marketplace>.
# README.md and INSTALL.md legitimately write --marketplace followed by a path,
# which is why the negative names the invalid pairing and not the flag.
assert_log_lacks "$LAST_INSTALL_LOG" "--marketplace claude-pen" \
  "install prints no --marketplace claude-pen, which the CLI rejects"

MOD_SECTION_SECOND="$TMP_WORK/mod-section-2.txt"
run_install "re-install with the mod present" "$MOD_SCRATCH"
mod_section "$LAST_INSTALL_LOG" > "$MOD_SECTION_SECOND"
assert_files_identical "$MOD_SECTION_FIRST" "$MOD_SECTION_SECOND" \
  "a second install prints an identical mod section"

# A partial unzip must cost the user the mod and nothing else. Mutating a bundle
# is the only way to test that, and the repository under test is never a
# legitimate thing to mutate, so this runs a copy carrying just what install.sh
# reads: the three layers, the marketplace manifest and the script. docs/ is
# ~10 MB of PNGs the installer never opens and is left out.
#
# run_install is not used here: it runs the repository's own installer, and the
# assertion is the exit status itself rather than a filesystem effect, so the
# status has to be captured instead of being turned into a bail-out.
MOD_BUNDLE="$TMP_WORK/partial-bundle"
mkdir -p "$MOD_BUNDLE"
cp "$INSTALL_SH" "$MOD_BUNDLE/install.sh"
cp -r "$REPO_ROOT/user" "$REPO_ROOT/project" "$REPO_ROOT/plugin" "$REPO_ROOT/.claude-plugin" "$MOD_BUNDLE/"
rm "$MOD_BUNDLE/plugin/dev-loop-inspector/hooks/hooks.json"
PARTIAL_SCRATCH="$TMP_WORK/partial-repo"
mkdir -p "$PARTIAL_SCRATCH"
PARTIAL_LOG="$TMP_WORK/log-partial-bundle.txt"
PARTIAL_STATUS=0
bash "$MOD_BUNDLE/install.sh" "$PARTIAL_SCRATCH" >"$PARTIAL_LOG" 2>&1 || PARTIAL_STATUS=$?

assert_equal "$PARTIAL_STATUS" "0" \
  "an incomplete mod bundle does not fail the install"
assert_log_contains "$PARTIAL_LOG" "! missing plugin/dev-loop-inspector/hooks/hooks.json" \
  "an incomplete mod bundle names the missing file"
assert_log_contains "$PARTIAL_LOG" "mod incomplete" \
  "an incomplete mod bundle says the mod is incomplete"

# The bundle's own directory name is the one part of an install an attacker can
# choose while leaving the scripts genuine and inspectable, and the installer
# interpolates it into a command line the user is told to paste. Safe means the
# paste runs exactly one command, with the real path as its last argument, and
# nothing else -- so the test pastes it: `claude` is shadowed by a function that
# records what it was handed, and the payload baked into the directory name
# would create a marker in the sandbox if it ran. --dry-run, and a bundle
# carrying only the script, because how the installer prints its own path is the
# whole of what is under test here.
EVIL_BUNDLE="$TMP_WORK/evil \$(mkdir pwned) \`mkdir pwned\` it's"
mkdir -p "$EVIL_BUNDLE"
cp "$INSTALL_SH" "$EVIL_BUNDLE/install.sh"
EVIL_SCRATCH="$TMP_WORK/evil-repo"
mkdir -p "$EVIL_SCRATCH"
EVIL_LOG="$TMP_WORK/log-evil-bundle.txt"
bash "$EVIL_BUNDLE/install.sh" "$EVIL_SCRATCH" --dry-run >"$EVIL_LOG" 2>&1

PASTE_SANDBOX="$TMP_WORK/paste-sandbox"
mkdir -p "$PASTE_SANDBOX"
PASTE_ARGS="$TMP_WORK/paste-args.txt"
printf '' > "$PASTE_ARGS"
claude() { local IFS='|'; printf '%s' "$*" > "$PASTE_ARGS"; }
# One line, so a path containing a newline is outside this check -- as it is
# outside NTFS, where the suite's own bundle lives.
PASTE_LINE="$(grep -F -m1 -- 'claude plugin marketplace add' "$EVIL_LOG")"
PASTE_STATUS=0
( cd "$PASTE_SANDBOX" && eval "$PASTE_LINE" ) || PASTE_STATUS=$?
unset -f claude

assert_equal "$PASTE_STATUS" "0" \
  "the printed add command parses as one command when pasted"
assert_not_exists "$PASTE_SANDBOX/pwned" \
  "pasting the printed add command runs nothing hidden in the bundle path"
assert_equal "$(cat "$PASTE_ARGS")" "plugin|marketplace|add|$EVIL_BUNDLE" \
  "the pasted add command receives the bundle path exactly as it is on disk"

# No cmd.exe counterpart to the paste above lives here, and that is deliberate:
# install.sh runs on machines where cmd.exe does not exist, so the exercise
# could only be conditional, and the path this script prints is POSIX
# (/c/Users/...), which is why the `claude` call cannot succeed from cmd.exe --
# not why the line is harmless there. An & in the bundle name splits the pasted
# line in cmd.exe whichever installer printed it. The PowerShell suite carries
# the exercise, against the native path install.ps1 prints. The label assertion
# above is what covers cmd.exe on both sides.

# Last, so it speaks for every install this run made: the mod is enabled through
# Claude Code's own registry under ~/.claude/plugins, which is that program's
# cache and not an install target, and the digest is compared against the one
# taken while HOME was still pristine. Whatever it was then -- MISSING, in a
# scratch HOME -- is what it has to be now.
assert_equal "$(snapshot "$HOME/.claude/plugins")" "$PRISTINE_PLUGINS" \
  "no install writes anything under ~/.claude/plugins"

echo
echo "All $ASSERTIONS assertions passed."
