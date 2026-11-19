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
| `user/.claude/skills/` | `~/.claude/skills/` — 13: 7 loops + `backlog-refinement` + `coding-standards` + `solution-architecture` + 3 walkthrough |
| `user/CLAUDE.md` | `~/.claude/CLAUDE.md` — delegation policy, loop selection |
| `project/.claude/` | `<repo>/.claude/` — per-project standards override, `implement-sprint`, `sprint-item-runner`, hook script |
| `project/ARCHITECTURE.template.md` | `<repo>/` — fill in and rename |
| `plugin/dev-loop-inspector/` | nowhere — the mod runs from the bundle where it sits. Enabled by hand, see *Manual steps after install* |

## After it runs

**Restart Claude Code once.** The agent directory watcher only covers folders
that existed when the session started, so a fresh `agents/` needs a restart to be
seen.

**Run `/doctor`.** With a repo wired up you should see 25 agents and 14 skills
(24 agents and 13 skills user-level, plus `sprint-item-runner` and
`implement-sprint` from the project), with no duplicate names. The mod does not
move those two numbers — a plugin is neither an agent nor a skill, and its own
tell is the `DL …` status-line entry plus `/dev-loop-inspect`. If a skill shows
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

**`dev-loop-inspector` is not enabled by the installer.** It reconciles a review
run against its own files and reports the two failures the loop is otherwise
blind to: a finding that reached no triage file, and a lane classified
`applicable` that never drained. It is a Claude Code plugin, so enabling it
means adding this bundle as a marketplace and then installing from it — two
commands, in two different places:

```bash
claude plugin marketplace add "/path/to/this/bundle"
```

```
/plugin install dev-loop-inspector@claude-pen
```

The first is a **shell** command. The second is typed **at the Claude Code
prompt**, not in a shell — the leading `/` is the tell. Both installers print
them with the bundle's absolute path already filled in, each quoted for the one
shell it names — `install.sh` for **bash**, `install.ps1` for **PowerShell** —
so a copy-paste survives a path with spaces in it. Neither is quoted for
`cmd.exe`: it treats `'` as an ordinary character rather than a quote, so paste
the first command into the shell its own installer names. Neither
installer runs them, and neither writes to `~/.claude/plugins/` or any
`settings.json`: that registry is Claude Code's own cache, not an install
target.

**The bundle folder stays a code source.** The marketplace entry's `source` is a
relative path, so the mod is loaded from this folder at every session start
rather than copied in once at install. Keep the bundle somewhere only you can
write, and re-check it after moving or replacing it.

The marketplace is named `claude-pen` regardless of what the unzipped folder is
called, and `@claude-pen` is how the second command finds it. `--marketplace`
would also work in place of `@`, but it takes a *source* — a path or an
`owner/repo` — not a marketplace name, so it is the one-command form
(`/plugin install dev-loop-inspector --marketplace "/path/to/this/bundle"`)
rather than a follow-on to the first step.

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
