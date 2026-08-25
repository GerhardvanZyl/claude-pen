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

# Copies a directory's contents into $to, optionally leaving out one top-level
# entry. That exclusion is how the repository's own standards.md stays out of
# the project-layer copy: a file that is never overwritten has no window
# between overwrite and restore for a failure to land in.
copy_layer() {
  local from="$1" to="$2" skip="${3:-}" entry
  shopt -s dotglob nullglob
  for entry in "$from"/*; do
    if [ "${entry##*/}" != "$skip" ]; then
      cp -r "$entry" "$to/"
    fi
  done
  shopt -u dotglob nullglob
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
  echo "  would copy agents (22) and skills (5 loops + solution-architecture + coding-standards + 3 walkthrough)"
fi

if [ -n "$REPO" ]; then
  [ -d "$REPO" ] || { echo "No such directory: $REPO" >&2; exit 1; }
  echo
  echo "=== Project level -> $REPO/.claude ==="

  # standards.md is user-editable and lives inside the tree the bulk copy
  # below overwrites wholesale. It is kept out of that copy rather than
  # overwritten and put back afterwards: a run that died between the two --
  # permission error, full disk, antivirus lock, Ctrl-C -- would take the one
  # file this contract exists to protect. The bundled version is written as
  # .new before anything else lands, so a copy that fails partway through has
  # still honoured the same non-clobber contract CLAUDE.md gets above.
  STANDARDS_DEST="$REPO/.claude/standards.md"
  STANDARDS_EXISTED=""
  if [ -f "$STANDARDS_DEST" ]; then STANDARDS_EXISTED=1; fi

  if [ -z "$DRY" ]; then
    mkdir -p "$REPO/.claude"
    if [ -n "$STANDARDS_EXISTED" ]; then
      cp "$HERE/project/.claude/standards.md" "$REPO/.claude/standards.new.md"
      copy_layer "$HERE/project/.claude" "$REPO/.claude" standards.md
      echo "  ! $STANDARDS_DEST already exists. Wrote standards.new.md beside it -- MERGE MANUALLY."
    else
      copy_layer "$HERE/project/.claude" "$REPO/.claude"
      echo "  standards.md installed"
    fi
    cp "$HERE/project/ARCHITECTURE.template.md" "$REPO/"
  else
    echo "  would copy project layer -> $REPO/.claude"
    if [ -f "$STANDARDS_DEST" ]; then
      echo "  would NOT overwrite existing $STANDARDS_DEST -- would write standards.new.md beside it"
    else
      echo "  would write $STANDARDS_DEST"
    fi
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
if [ "$SKILLS" -lt 10 ]; then echo "  ! expected at least 10 skill folders"; fi
if [ -n "$REPO" ]; then echo "  $(find "$REPO/.claude" -type f | wc -l) files in $REPO/.claude"; fi
if [ -n "$DID_BACKUP" ]; then echo "  previous agents/skills preserved in $BACKUP"; fi

echo
echo "=== Do these by hand ==="
echo "  * Edit $CLAUDE/skills/coding-standards/SKILL.md -- replace its rule sections with"
echo "    your real cross-project rules. Leave its precedence section as shipped."
if [ -n "$REPO" ]; then
  echo "  1. Put repository-specific rules in .claude/standards.md, which overrides the"
  echo "     baseline -- optional, leave it alone if there is nothing to override."
  echo "  2. Fill in ARCHITECTURE.template.md, rename to ARCHITECTURE.md at the repo root."
  echo "  3. Fill in the Configuration table in .claude/skills/implement-sprint/SKILL.md"
  echo "     -- tracker, access route, coordinates, code host, base branch. sprint-planning"
  echo "     reads the same table, and needs its access route to have write access."
fi
echo "  * Merge .claude/settings.example.json into .claude/settings.json for hook logging,"
echo "    then run /doctor -- the hook fails silently if its path is wrong."
echo
echo "Restart Claude Code once, then run /doctor."
echo
