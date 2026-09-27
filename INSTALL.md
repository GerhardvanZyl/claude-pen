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

If `<repo>/.claude/standards.md` already exists, the script writes
`standards.new.md` beside it and tells you. **Merge it by hand** — that file
carries this repository's real rule overrides.

Everything else is copied over the top.

## Where things go

| From | To |
| --- | --- |
| `user/.claude/agents/` | `~/.claude/agents/` — 24 agents |
| `user/.claude/skills/` | `~/.claude/skills/` — 7 loops + `solution-architecture` + `coding-standards` + 3 walkthrough |
| `user/CLAUDE.md` | `~/.claude/CLAUDE.md` — delegation policy, loop selection |
| `project/.claude/` | `<repo>/.claude/` — per-project standards override, the 2 sprint skills, `sprint-item-runner`, hook script |
| `project/ARCHITECTURE.template.md` | `<repo>/` — fill in and rename |

## After it runs

**Restart Claude Code once.** The agent directory watcher only covers folders
that existed when the session started, so a fresh `agents/` needs a restart to be
seen.

**Run `/doctor`.** With a repo wired up you should see 25 agents and 14 skills
(24 agents and 12 skills user-level, plus `sprint-item-runner`, `implement-sprint`
and `backlog-refinement` from the project), with no duplicate names. If a skill shows
up under a filename rather than its folder name, a `SKILL.md` was renamed
somewhere.

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

**`~/.claude/skills/coding-standards/SKILL.md` is a scaffold**, installed once
per machine. Replace its rule sections with your real cross-project rules. Its
*Explicitly not standards* section matters as much as the rules themselves.

Three more things need your input, per repository, before the loops behave
well:

1. **`.claude/standards.md` is optional.** It overrides and extends the
   baseline for this repository only — a rule here on a subject the baseline
   also covers wins, and a subject listed under its own *Explicitly not
   standards* removes a baseline rule outright. Leave it exactly as shipped if
   this repository has nothing to override.
2. **`ARCHITECTURE.template.md`** — fill it in from your dependency graph, not
   from a preferred design, then rename it `ARCHITECTURE.md`. Without it,
   architectural findings are capped at Minor and can never block a PR.
3. **`.claude/skills/implement-sprint/SKILL.md`** has a *Configuration* table.
   Set the tracker, access route, coordinates, sprint identifier, code host and
   base branch, or the skill will stop and ask. **`backlog-refinement` reads the
   same table** and adds two settings of its own — the estimate field and the
   scale — and needs its access route to have **write** access, which
   `implement-sprint` never does. Check that before the first planning session,
   not at the first write-back.
4. **`grill-me` is optional and not bundled here.** `backlog-refinement` runs
   its interview through it. Install with
   `npx skills@latest add mattpocock/skills -g -s grill-me,grilling` — both
   names are needed, and `-g` puts them at user level. Without it the skill
   runs the interview itself under the same rules and says so.

## First run

Try `/dev-loop-lite` on something small and disposable. The value of the first
run is not the code — it is `round-1/triage.md`, which tells you which lanes are
noisy against your codebase before you trust the loops with anything real.
