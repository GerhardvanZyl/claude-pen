# Claude Code Dev Loops

Turns "implement this" into a bounded, logged, multi-pass review pipeline that
ends at a pull request.

Five review loops at different price points, a backlog refiner, a sprint
orchestrator, and a delegation policy that keeps the orchestrating agent out of
the code. Plain markdown — no runtime, nothing to build.

- [The skills](#the-skills)
- [Install](#install)
- [Configure](#configure)
- [Use](#use)
- [Choosing a loop](#choosing-a-loop)
- [How a loop works](#how-a-loop-works)
- [The adversarial loops](#the-adversarial-loops)
- [Unity loops](#unity-loops)
- [Backlog refinement](#backlog-refinement)
- [Sprint orchestration](#sprint-orchestration)
- [Cost](#cost)
- [What to watch](#what-to-watch)
- [Design notes](#design-notes)

---

## The skills

Twelve skills, twenty-three subagents. The loops are what you invoke; the rest
are invoked by them.

**The five dev loops** — pick one per change:

| Skill | Review shape | Rounds | Cost |
| --- | --- | --- | --- |
| `/dev-loop-ultralight` | 1 reviewer, 9-item sweep | 1 | 0.19× |
| `/dev-loop-lite` | 4 consolidated lanes | 2 | 0.57× |
| `/dev-loop` | 9 gated lanes | 3 | 1.00× |
| `/dev-loop-ultra` | 9 lanes, each an adversarial triple | 3 | 1.89× |
| `/dev-loop-ultra-opus` | Same, every reviewer on Opus | 3 | 2.71× |

All five run the same shape: **frame → implement → tests → review lanes → triage
→ fix → loop → verify → walkthrough → PR.** Only review depth and bounds differ.

**Two Unity loops**, layered onto the two above for Unity repos — no cost
figures, since `docs/cost-model.py` doesn't model them:

| Skill | Review shape | Rounds | Overrides |
| --- | --- | --- | --- |
| `/dev-loop-unity` | 9 gated lanes plus a Unity lane | 3 | `/dev-loop` |
| `/dev-loop-greybox` | 4 consolidated lanes plus Unity and Visual, in a second wave | 2 | `/dev-loop-lite` |

**The two tracker skills:**

| Skill | Does |
| --- | --- |
| `/backlog-refinement` | Grills each item, agrees an estimate as planning poker, writes back context, decisions and acceptance criteria. **The only skill that writes to the tracker.** |
| `/implement-sprint` | Triages each item to a loop, runs them one at a time with checkpoints, one PR per item. Reads what refinement wrote; never writes back. |

**The five supporting skills**, invoked by the loops rather than by you:
`coding-standards` (your style baseline — a scaffold to replace),
`solution-architecture` (how to establish a repo's architecture before judging
it), `implementation-notes` (records decisions as the run proceeds),
`pr-walkthrough` and `pr-walkthrough-review` (turn those notes into the document
that ships with the PR).

**The agents:** three sidekicks (`sidekick-lite`/Haiku, `sidekick`/Sonnet — the
default, `sidekick-heavy`/Opus-xhigh), `Explore` pinned to Haiku, nine full-loop
lane reviewers, four lite reviewers, `reviewer-ultralight`, three ultra agents,
`reviewer-verify`, and `sprint-item-runner`. Reviewers never call `Edit`; fixes
go to a sidekick.

---

## Install

```powershell
.\install.ps1 -Repo C:\src\<your-repo>
```
```bash
./install.sh /path/to/repo
```

Drop the repo argument to install the loops only. `-WhatIfOnly` / `--dry-run`
shows where things would land.

**Then restart Claude Code once** — the agent watcher only sees directories that
existed at startup — **and run `/doctor`**: 23 agents, 12 skills, no duplicates.

| From | To |
| --- | --- |
| `user/.claude/agents/` | `~/.claude/agents/` |
| `user/.claude/skills/` | `~/.claude/skills/` |
| `user/CLAUDE.md` | `~/.claude/CLAUDE.md` |
| `project/.claude/` | `<repo>/.claude/` |
| `project/ARCHITECTURE.template.md` | `<repo>/` — fill in, rename |

Existing `~/.claude/CLAUDE.md` and `<repo>/.claude/standards.md` are never
overwritten — you get a `.new.md` beside them to merge. Everything else is copied
over the top, after backing up `agents/` and `skills/` to
`~/.claude/backup-<timestamp>/`. Nothing is deleted. See [INSTALL.md](INSTALL.md).

---

## Configure

**Required:** replace the rule sections in
`~/.claude/skills/coding-standards/SKILL.md` with your real rules, once per
machine. Its *Explicitly not standards* section matters as much as the rules — it
is what stops the Standards lane raising `var`-versus-explicit-type opinions.

**Required for the tracker skills:** fill in `implement-sprint`'s Configuration
table — tracker, access route, coordinates, default sprint, code host, base
branch. Tracker and code host are separate settings; Jira boards with GitHub
repos is ordinary. `backlog-refinement` reads the same table, adds the estimate
field and scale, and **needs write access**, which `implement-sprint` never does.

**Optional:** `<repo>/.claude/standards.md` overrides the baseline per
repository. `ARCHITECTURE.md` lifts architectural findings out of advisory-only —
without it they cap at Minor. `settings.example.json` merges in hook logging of
subagent start/stop.

`solution-architecture` discovers each repo's architecture in four tiers, and the
tier caps severity: documented (Critical) → reference graph (Critical) →
convention from 3+ examples (Minor) → nothing establishable (Minor, separation of
concerns only). Where a document and the graph disagree, **the graph wins**.

---

## Use

```
/dev-loop              implement batching for outbound notifications
/dev-loop-lite         add the retry-count column to the results grid
/dev-loop-ultralight   fix the typo in the validation message
/dev-loop-ultra        change the tenant filter on the reporting query
/dev-loop-ultra-opus   migrate the events table to the new partition key

/dev-loop-unity        add a new pickup interaction to the inventory system
/dev-loop-greybox      block out the tutorial room and light it

/backlog-refinement                       the current sprint
/backlog-refinement sprint "Sprint 12"    a named sprint or milestone
/backlog-refinement 1234, 1235, 1240      explicit items, in that order
/backlog-refinement tag payments          every item with that tag or label
/backlog-refinement parent 980            every child of an epic or feature
/backlog-refinement query <expression>    WIQL, JQL, a gh search
/backlog-refinement board Ready           a board column or saved filter
/backlog-refinement resume

/implement-sprint  [skip 1234, 1235] [resume]
```

Give a loop a requirement, not an implementation. The PR targets **the branch you
were on**, never the repo default.

**First run:** `/dev-loop-lite` on something disposable. The value is
`round-1/triage.md` — it tells you which lanes are noisy against your codebase.

A run leaves `.claude/review/runs/<run-id>/` (brief, per-round plan, findings,
logs, triage, notes, run summary) plus one line in `index.jsonl`. All gitignored
by the installer, because lane logs quote the code they read. Two things are
committed: `.claude/review/conventions.md` and `docs/walkthroughs/<slug>.md`.

---

## Choosing a loop

![Choosing a loop](docs/diagrams/png/loop-selection.png)

Unity repos substitute a loop rather than adding a branch to this tree: code
goes to `/dev-loop-unity` wherever this chart would say `/dev-loop`, and
blockouts or visual prototypes go to `/dev-loop-greybox` wherever it would say
`/dev-loop-lite`.

---

## How a loop works

![The full dev-loop](docs/diagrams/png/dev-loop.png)

### The nine lanes

Each has a card in `dev-loop/references/review-lanes.md`. Reviewers read **only
their own card** — a lane that notices something another lane owns stays silent.

| Lane | Model | Owns |
| --- | --- | --- |
| requirements | opus / high | Coverage against the brief, scope creep, interpretations taken |
| technical | opus / xhigh | Logic, state, concurrency, boundaries, error paths |
| architecture | opus / xhigh | **Separation of concerns**, dependency direction, placement |
| security | opus / xhigh | Injection, authz, secrets, deserialization, crypto, exposure |
| standards | sonnet / high | Rules in `coding-standards` and `.claude/standards.md`. Nothing else |
| tests | sonnet / high | Whether tests would fail if the code were wrong |
| dead code | sonnet / high | Unreachable branches, orphaned paths |
| minimalism | sonnet / high | Speculative guards, wrappers, config nobody asked for |
| artifacts | sonnet / high | Generated code, migrations, lockfiles, dependencies |
| verify | opus / high | Final gate, once: did cumulative fixes preserve intent? |

Requirements, technical and tests always run; the rest are gated on what the diff
touches. "The code looks fine" is never a skip reason.

### Findings

```json
{
  "id": "sec-001", "lane": "security", "severity": "Critical|Major|Minor",
  "evidence": "direct|spec|policy|test|validation|missing|inferred",
  "cause": "introduced|worsened|stale|missing-required",
  "file": "src/Orders/OrderService.cs", "line": 142,
  "finding": "One sentence stating what is wrong.",
  "why_it_matters": "The concrete consequence, or how to trigger it.",
  "suggested_fix": "The smallest change that fixes it.",
  "would_have_been_bug": true, "confidence": "high|medium|low"
}
```

Two gates do most of the work. **`inferred` evidence alone never blocks** — a
reviewer that reasoned to a problem but cannot point at it gets advisory weight.
**`introduced`, `worsened` and `missing-required` are fixed; `stale` is not** —
pre-existing debt goes in the PR description, because fixing it hides the change.

`missing-required` is deliberately in scope: it names what the change needed and
did not produce — a migration, a regenerated client. Absent code is never in a
diff, so a gate admitting only `introduced` and `worsened` would drop every one
of them while looking perfectly principled.

### The walkthrough

`implementation-notes` accumulates decisions and rejected alternatives into
`notes.md` as the run proceeds. `pr-walkthrough` turns that into
`docs/walkthroughs/<slug>.md` and `pr-walkthrough-review` checks it. The diff
already shows *what* changed; the walkthrough's only job is *why*. Skipping is
allowed for purely mechanical changes, and is reported, never silent.

---

## The adversarial loops

![The ultra loop](docs/diagrams/png/dev-loop-ultra.png)

Running one reviewer twice samples the same error profile twice. Prosecution and
defence have *different* profiles — one over-raises, one under-raises — and their
disagreements carry the information. The adjudicator extracts it by checking the
code itself; adjudicating from the two reports alone would just let the more
confident summary win. **It may not invent findings** — anything it spots that
neither reviewer raised goes in its log, not the findings file.

`dev-loop-ultra-opus` is structurally identical with every reviewer on Opus and
one lane at a time. It raises the **model** tier, not effort: the Agent tool has a
`model` parameter and no `effort` parameter, so effort is whatever the agent file
declares. `sidekick-heavy` reaches `xhigh` only because it is a separate file
that declares it.

---

## Unity loops

![The dev-loop-unity loop](docs/diagrams/png/dev-loop-unity.png)

`/dev-loop-unity` is `/dev-loop` plus Unity batchmode validation — compile
check, EditMode tests, PlayMode tests, and an Editor-lock precondition before
every run — and a tenth lane, Unity (opus, high), owning serialized-field data
loss, asset/`.meta` integrity, and lifecycle-order defects. Escalation to
`dev-loop-ultra` carries all five changes forward.

![The dev-loop-greybox loop](docs/diagrams/png/dev-loop-greybox.png)

`/dev-loop-greybox` is `/dev-loop-lite` plus an art brief with named shots, a
`ShotCapture` batchmode step run after Tests and after every Fix round, and two
more lanes — Unity (sonnet) and Visual (opus) — spawned as a second wave after
lite's four. A missing shot fails the definition of done outright; escalation
goes to `dev-loop-unity`, not the full loop.

Neither diagram is in `dev-loops.pdf` — see `docs/diagrams/README.md`.

---

## Backlog refinement

![Backlog refinement](docs/diagrams/png/backlog-refinement.png)

**Any selection of items** — the current sprint, a named sprint, explicit IDs, a
tag, a parent, a tracker query, a board column. A selector the tracker cannot
express, or that matches nothing, stops and asks rather than substituting one.

**One question at a time, each item finished before the next starts.** A numbered
list of five questions is a form, and a form cannot follow up.

**The repository is open, so questions cite files.** Read-only — a refinement
session that edits the tree hands the next dev loop a diff nobody asked for.

**No size language until you ask for it** — not a point value, a range, "small",
or a **duration**. "Half a day" anchors exactly as hard as a number.

**Estimates run as planning poker.** It says it has one and waits for your cue,
reveals it with one line of reasoning, then asks for yours. **The number written
back is yours.**

**The write-back is a contract**: Context, Decisions, Acceptance criteria —
bullets only, one line each, capped at four/six/six. Nothing is written until you
have seen the exact text, and only those three fields are ever touched — never
state, assignee, tags or rank.

### Installing `grill-me`

The grilling runs through `grill-me`, which is **user-invocation-only** — the
session asks you to type `/grill-me` per item. It is not bundled here:

```bash
npx skills@latest add mattpocock/skills -g -s grill-me,grilling
```

Both names are needed: `grill-me` is the slash command, `grilling` is the
interview it runs. `-g` installs at user level; add `--copy` if you would rather
have files than symlinks.

**Optional.** Without it, `backlog-refinement` runs the interview itself under the
same rules, says so plainly, and records `interview: self` on the item — a
substitute reads exactly like the real thing, which is why it gets declared.

---

## Sprint orchestration

![Sprint orchestration](docs/diagrams/png/implement-sprint.png)

**Any tracker, any code host**, configured once. One vocabulary throughout —
sprint, item, type, state, rank, tag — mapped to each tracker's words in a single
table, so no rule is provider-specific.

**Order is decided by what would be thrown away, not by rank.** Supersession beats
dependency, dependency beats rank. Rank says what matters most, which is not what
builds on top of what — following it blindly is how a sprint pays twice for the
same file.

**The sprint keeps moving while it runs.** Re-polled before every item. Additions
are held at `pending_confirmation` until you approve them; the order is recomputed
using `files_changed` from completed items, which is real evidence where the plan
had only descriptions. Nothing re-orders silently.

**Checkpoints default to after every item**, and six are not configurable: the
first completed item, a mid-run addition, a changed run order, file overlap with
an open PR, a dependency on an unmerged item, and any escalation or failure. The
run halts outright on three open PRs, two consecutive failures, a dirty tree,
items arriving faster than they complete, or two items that keep swapping
position.

**Skips come from four sources**, all applied: the invocation,
`.claude/sprint/skip.md`, a `no-auto`/`manual`/`spike` tag, and automatic rules.
Every skip is reported with its reason.

**Item text is specification, not instruction.** Anything addressed to the agent —
skip review, run this, this was pre-approved — is quoted to you, not acted on.

---

## Cost

Per change, USD. `dev-loop` and `dev-loop-lite` come from `docs/cost-model.py`;
the rest extrapolate the same assumptions. **Estimates from assumed token volumes,
not measurements** — the shape is reliable, the absolutes are not.

| Loop | Review | Lead | Impl | Other | **Total** | vs full |
| --- | --- | --- | --- | --- | --- | --- |
| `dev-loop-ultralight` | 0.17 | 0.40 | 0.42 | 0.08 | **1.07** | 0.19× |
| `dev-loop-lite` | 0.61 | 1.42 | 0.86 | 0.34 | **3.24** | 0.57× |
| `dev-loop` | 2.48 | 1.71 | 0.86 | 0.66 | **5.71** | 1.00× |
| `dev-loop-ultra` | 7.31 | 1.97 | 0.86 | 0.66 | **10.80** | 1.89× |
| `dev-loop-ultra-opus` | 10.50 | 1.97 | 2.09 | 0.88 | **15.44** | 2.71× |

- **Effort dominates model choice.** Reasoning bills as output at 5× the input
  rate, so an Opus lane at `xhigh` costs ~6× a Sonnet lane at `high`. Tuning
  effort beats switching models.
- **Ultra is 1.89×, not 3×.** Review triples; implementation and fixes do not
  move. Review is only 43% of a full run.
- **The lead is the floor** — 40% of an ultralight run. Below that you are not
  running a loop.
- **Savings shrink as diffs grow.** At 4× the implementation size, lite's
  advantage falls from 43% to 30%.

Cost per run is the easy metric. **Cost per Critical caught** is the real one, and
only your own `index.jsonl` can answer it.

---

## What to watch

`index.jsonl` is the analysis surface. Rejections are recorded by reason, because
a bare rejection rate cannot tell a noisy lane from a working one:
`rejected_stale`, `rejected_evidence` and `rejected_remedy` are the gates doing
their job. **`rejected_wrong` is the only one that counts against a lane.**

| Signal | Meaning |
| --- | --- |
| High `rejected_wrong` ratio | Manufacturing findings — tighten its quality brake |
| Lane never raises anything | Gated too tightly, or its card is too vague to act on |
| High escalation rate from a light loop | Selection criteria too loose — tighten eligibility, not the reviewer |
| Ultra: prosecution raises many, few kept | Running hot, or dismissals accepted too readily |
| Ultra: defence raises almost nothing | Drifted into agreeableness. **The hardest failure to see — it looks like clean code** |
| Ultra: both agree on nearly everything | Stances not actually opposed — you are paying 3× for one opinion |
| Lite: a merged lane only ever reports one concern | Consolidation not holding — split it back out |

Every reviewer logs what it **considered and did not raise**. That is what
distinguishes a quiet lane from one that stopped early.

---

## Design notes

**"Read-only" reviewers are enforced three ways**, in increasing order of what
they actually guarantee: `disallowedTools` blocks `Edit` and the mutating shell
commands; the prompt confines writes to the run directory; and **the lead digests
the working tree before and after the lanes and stops if it moved.** Only the
third is a guarantee — prefix rules cannot catch every spelling, so the digest
checks the result rather than enumerating causes.

**Mutation testing runs in a scratch worktree**, never the tree under review. The
Tests lane's strongest finding is proving a test decorative by breaking the code
it covers, which requires writing to source. The lead builds a detached worktree
from an exact snapshot, hands over the path, and discards it afterwards.

**Do not enable `memory` on reviewers** — it auto-enables Read, Write and Edit,
silently undoing the read-only property.

**Nothing is on the branch until Phase 9 commits it.** It stages untracked files
explicitly and checks the commit two ways: the file list against the reviewed
plan, and the tree digest against the post-fix baseline. The first catches a
missing file; only the second catches a changed one, since the same files with
different contents produce an identical `--stat`.

**`CLAUDE_CODE_SUBAGENT_MODEL` overrides everything.** If routing seems broken,
check for it first.

**The `Explore` override must be named `Explore`** to shadow the built-in, which
since v2.1.198 inherits the main model — so recon runs at Opus prices if your lead
does.

`CLAUDE.md` loads into every custom subagent, reviewers included; only the
built-in Explore and Plan skip it.

---

## Credits

Review-lane structure — applicability gating, evidence labels, causality
classification, clustering by locator, and the independent verification pass —
adapted from [dcramer/agents](https://github.com/dcramer/agents).

MIT. See `LICENSE`.
