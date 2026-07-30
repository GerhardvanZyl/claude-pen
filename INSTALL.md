# INSTALL

Read this file only. Everything else is reference.

## The one command

From the unzipped folder, in PowerShell:

```powershell
.\install.ps1 -Repo C:\src\<your-repo>
```

Drop `-Repo` entirely to install the loops without wiring up a specific project.

Add `-WhatIfOnly` first if you want to see where things would land without
writing anything.

macOS / Linux:

```bash
./install.sh /path/to/repo
```

## What it will not overwrite

If `~/.claude/CLAUDE.md` already exists, the script writes `CLAUDE.new.md`
beside it and tells you. **Merge it by hand** — that file is yours and may hold
instructions unrelated to this repo.

Everything else is copied over the top.

## Where things go

| From | To |
| --- | --- |
| `user/.claude/agents/` | `~/.claude/agents/` — 22 agents |
| `user/.claude/skills/` | `~/.claude/skills/` — 5 loops + `solution-architecture` |
| `user/CLAUDE.md` | `~/.claude/CLAUDE.md` — delegation policy, loop selection |
| `project/.claude/` | `<repo>/.claude/` — standards, sprint skill, hook script |
| `project/ARCHITECTURE.template.md` | `<repo>/` — fill in and rename |

## After it runs

**Restart Claude Code once.** The agent directory watcher only covers folders
that existed when the session started, so a fresh `agents/` needs a restart to be
seen.

**Run `/doctor`.** You should see 22 agents and 6 skills, with no duplicate
names. If a skill shows up under a filename rather than its folder name, a
`SKILL.md` was renamed somewhere.

**Merge `settings.example.json` into `.claude/settings.json`** if you want hook
logging. Merge, do not overwrite — you may have settings already. Then run
`/doctor` and confirm `.claude/review/runs/_agent-events.jsonl` appears once a
subagent has run: the hook script exits 0 on every error so it can never block a
subagent, which also means a wrong path fails completely silently.

**`.claude/review/runs/` is added to the repo's `.gitignore` by the installer.**
Lane logs quote the code they examined, which can include credentials and
internal paths, so check the line is actually there before running a loop.
Commit `.claude/review/conventions.md` — that one is shared knowledge and
belongs in version control.

**Existing `~/.claude/agents/` and `~/.claude/skills/` are backed up** to
`~/.claude/backup-<timestamp>/` before anything is overwritten. If you had your
own agent or skill with a name this bundle also uses, that is where the previous
version is. Nothing is deleted. Use `-WhatIfOnly` (PowerShell) or `--dry-run`
(shell) to see what would move without moving it.

## Manual steps after install

Three things need your input before the loops behave well:

1. **`.claude/skills/coding-standards/SKILL.md` is a scaffold.** Replace it with
   your real rules. Its *Explicitly not standards* section matters as much as the
   rules themselves.
2. **`ARCHITECTURE.template.md`** — fill it in from your dependency graph, not
   from a preferred design, then rename it `ARCHITECTURE.md`. Without it,
   architectural findings are capped at Minor and can never block a PR.
3. **`.claude/skills/implement-sprint/SKILL.md`** has a *Configuration* table.
   Set the organisation, project, team, and base branch, or the skill will stop
   and ask.

## First run

Try `/dev-loop-lite` on something small and disposable. The value of the first
run is not the code — it is `round-1/triage.md`, which tells you which lanes are
noisy against your codebase before you trust the loops with anything real.
