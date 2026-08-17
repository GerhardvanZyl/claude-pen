#!/usr/bin/env bash
# Installs everything.
#   ./install.sh
#   ./install.sh /path/to/repo
#   ./install.sh /path/to/repo --dry-run
#
# Existing user-level agents and skills are backed up before anything is
# overwritten. The backup directory is printed; nothing is deleted.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE="$HOME/.claude"

REPO=""
DRY=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    -*)        echo "Unknown option: $arg" >&2; exit 2 ;;
    *)         REPO="$arg" ;;
  esac
done

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$CLAUDE/backup-$STAMP"
DID_BACKUP=""

backup_tree() {
  local path="$1"
  [ -d "$path" ] || return 0
  [ -n "$(ls -A "$path" 2>/dev/null)" ] || return 0
  if [ -n "$DRY" ]; then echo "  would back up existing $(basename "$path") -> $BACKUP"; return 0; fi
  mkdir -p "$BACKUP/$(basename "$path")"
  cp -r "$path/." "$BACKUP/$(basename "$path")/"
  DID_BACKUP=1
}

add_ignore_rule() {
  local repo="$1" rule="$2" why="$3"
  if [ -f "$repo/.gitignore" ] && grep -qF "$rule" "$repo/.gitignore"; then
    echo "  .gitignore already has $rule"; return 0
  fi
  if [ -n "$DRY" ]; then echo "  would append $rule to .gitignore"; return 0; fi
  printf '\n# %s\n%s\n' "$why" "$rule" >> "$repo/.gitignore"
  echo "  appended $rule to .gitignore"
}

echo
echo "=== User level -> $CLAUDE ==="

# Back up first. These trees are overwritten wholesale, and a user's own
# same-named agent or skill would otherwise vanish without a trace.
backup_tree "$CLAUDE/agents"
backup_tree "$CLAUDE/skills"
if [ -n "$DID_BACKUP" ]; then echo "  backed up existing agents/skills -> $BACKUP"; fi

if [ -z "$DRY" ]; then
  mkdir -p "$CLAUDE/agents" "$CLAUDE/skills"
  cp -r "$HERE/user/.claude/agents/." "$CLAUDE/agents/"
  cp -r "$HERE/user/.claude/skills/." "$CLAUDE/skills/"
  if [ -f "$CLAUDE/CLAUDE.md" ]; then
    cp "$HERE/user/CLAUDE.md" "$CLAUDE/CLAUDE.new.md"
    echo "  ! $CLAUDE/CLAUDE.md exists. Wrote CLAUDE.new.md beside it -- MERGE MANUALLY."
  else
    cp "$HERE/user/CLAUDE.md" "$CLAUDE/CLAUDE.md"; echo "  CLAUDE.md installed"
  fi
else
  echo "  would copy agents (22) and skills (5 loops + solution-architecture + 3 walkthrough)"
fi

if [ -n "$REPO" ]; then
  [ -d "$REPO" ] || { echo "No such directory: $REPO" >&2; exit 1; }
  echo
  echo "=== Project level -> $REPO/.claude ==="
  if [ -z "$DRY" ]; then
    mkdir -p "$REPO/.claude"
    cp -r "$HERE/project/.claude/." "$REPO/.claude/"
    cp "$HERE/project/ARCHITECTURE.template.md" "$REPO/"
  else
    echo "  would copy project layer -> $REPO/.claude"
  fi

  # Run output quotes the source it examined. Ignoring it is not a nicety.
  add_ignore_rule "$REPO" '.claude/review/runs/' 'Review lane logs quote the code they read'
fi

if [ -n "$DRY" ]; then
  echo
  echo "Dry run only. Re-run without --dry-run to apply."
  echo
  exit 0
fi

echo
echo "=== Verify ==="
AGENTS=$(ls -1 "$CLAUDE/agents"/*.md 2>/dev/null | wc -l)
SKILLS=$(ls -1d "$CLAUDE/skills"/*/ 2>/dev/null | wc -l)
echo "  $AGENTS agent files, $SKILLS skill folders"
if [ "$AGENTS" -lt 22 ]; then echo "  ! expected at least 22 agents"; fi
if [ "$SKILLS" -lt 9 ];  then echo "  ! expected at least 9 skill folders"; fi
if [ -n "$REPO" ]; then echo "  $(find "$REPO/.claude" -type f | wc -l) files in $REPO/.claude"; fi
if [ -n "$DID_BACKUP" ]; then echo "  previous agents/skills preserved in $BACKUP"; fi

echo
echo "=== Do these by hand ==="
if [ -n "$REPO" ]; then
  echo "  1. Edit .claude/skills/coding-standards/SKILL.md -- it is a scaffold."
  echo "  2. Fill in ARCHITECTURE.template.md, rename to ARCHITECTURE.md at the repo root."
  echo "  3. Set org/project/team in .claude/skills/implement-sprint/SKILL.md (Configuration)."
fi
echo "  * Merge .claude/settings.example.json into .claude/settings.json for hook logging,"
echo "    then run /doctor -- the hook fails silently if its path is wrong."
echo
echo "Restart Claude Code once, then run /doctor."
echo
