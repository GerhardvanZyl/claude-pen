# Global Instructions

These apply across all folders and repositories.

## Git & Branch Rules

- **Always merge a branch back into the branch it was branched off from** — its actual parent/source branch. Do NOT default to merging into the repository's default branch or `main`/`master` just because it is the default. If the source branch is unknown or ambiguous, ask before merging rather than assuming the default branch.

## Pull Request Reviews

- **When reviewing a PR, post findings as comments on the PR itself, and when you fix an item raised in review, resolve its thread.** Use whatever the PR host supports for inline comments and thread resolution; a chat-only summary does not satisfy this.
- This rule governs review of **existing** PRs. It does not apply to the internal review rounds in the `dev-loop` skill, which run before a PR exists.

# Coding standards & architecture

- **All implementation and review must conform to the `coding-standards` skill and the `solution-architecture` skill.** Both are preloaded into the sidekick agents and into their owning review lanes.
- Style rules come from exactly two files: the `coding-standards` skill — the cross-project baseline, edited once per machine — and the repository's own `.claude/standards.md`, which wins over the baseline on any subject it covers and is read from the repo rather than preloaded. Do not enforce, or let a reviewer enforce, a rule written in neither.
- **`solution-architecture` is repository-agnostic.** It carries the reasoning, not any particular solution's structure. Establish the architecture actually in force — discovered documents, then the project reference graph, then convention inferred from existing examples — before judging anything against it. Never apply a remembered or textbook architecture to a repo you have not established the architecture of.
- **The strength of an architectural finding is capped by how it was established.** Documented or structurally evident can block; inferred from convention cannot.
- **Separation of concerns outranks every other architectural consideration.** Where a structural finding conflicts with a separation-of-concerns finding, separation of concerns wins.
- Deviation from what a repository consistently does is the finding. The convention itself is not, however suboptimal it looks.
- `.claude/review/conventions.md` records deviations already examined and deliberately accepted. Anything in it is never a finding. It accumulates from triage decisions — do not author it speculatively.

# Development loop

Five loops exist. **Choose before starting; do not switch mid-run except by the escalation rules below.**

| | `dev-loop-ultralight` | `dev-loop-lite` | `dev-loop` (full) | `dev-loop-ultra` | `dev-loop-ultra-opus` |
| --- | --- | --- | --- | --- | --- |
| Trigger | `/dev-loop-ultralight` | `/dev-loop-lite` | `/dev-loop` | `/dev-loop-ultra` | `/dev-loop-ultra-opus` |
| Review lanes | 1 reviewer, 9-item sweep | 4 consolidated | 9, gated | 9, gated | 9, gated |
| Agents per lane | 1 | 1 | 1 | 3 (opposed pair + adjudicator) | 3 |
| Reviewer tiers | 1 Sonnet | 3 Sonnet, 1 Haiku | 4 Opus, 5 Sonnet | as full, ×3 | all Opus, xhigh |
| Implementation | **identical**, single handoff | **identical** | full ladder | **identical** | `sidekick-heavy` throughout |
| Rounds | 1 | 2 | 3 | 3 | 3 |
| Verification | none | after a Critical | when risky | always | always |
| Rough review cost | 0.1× | 0.3× | 1× | 3× | 8× |

**Implementation and the orchestrator are never downgraded.** The first four loops write and fix code at the same tiers; only review depth and bounds differ. `dev-loop-ultra-opus` is the sole exception — it raises implementation to Opus as well, on the grounds that paying for adversarial review of code written a tier below the reviewers is a false economy.

Work **down** this list and stop at the first loop that fits. Nine of ten changes are lite or full.

**Use `dev-loop-ultralight`** only when every one of these holds: one project and roughly five files or fewer; no authn/authz, secrets, or untrusted input; no migration, schema, generated artifact, or public contract change; no concurrency or transaction-boundary change; no new dependency; easy to roll back.

**Use `dev-loop-lite`** for contained single-project changes that fail an ultralight criterion but none of the full-loop criteria below.

**Use the full `dev-loop`** when any of these hold — this list decides it, not diff size:

- The change touches authentication, authorization, secrets, or untrusted input.
- A migration, schema, or public API contract changes.
- More than one project in the solution is modified.
- It ships on a path that is hard to roll back.

**Use `dev-loop-ultra`** when a missed defect is expensive rather than merely annoying: payment, billing, or anything moving money or goods; auth, permissions, or data isolation between tenants; migrations that alter or destroy existing data; integration contracts other systems depend on; anything where rollback is slow or costly; code you are handing over and will not maintain.

**Use `dev-loop-ultra-opus`** only when being wrong is severe and largely irreversible: a migration destroying production data, tenant-isolation logic where a defect exposes other people's data, money movement with a regulatory consequence, a contract other organisations build against, or code going to someone who cannot fix it.

**When unsure, go heavier.** The savings never justify a missed Critical. But note the cost column: `ultra` is three times a full run and `ultra-opus` roughly eight. Reaching past the point where the extra scrutiny changes the outcome is spending, not diligence — and the honest default for most work remains `dev-loop`.

**Unity repos:** `/dev-loop-unity` for code, `/dev-loop-greybox` for blockouts and visual prototypes. Both follow a base loop and override only what differs.

**Escalation is one-way and mandatory.** It climbs the same ladder:

| Loop | Escalate when | To |
| --- | --- | --- |
| ultralight | Any Critical; a Major in security, architecture, or concurrency | `dev-loop` |
| ultralight | Any other Major; more than four accepted findings; a reviewer reporting it could not cover a concern | `dev-loop-lite` |
| lite | Any Critical in round 1 | `dev-loop` |
| full | A Critical in a lane the change was not expected to touch at all, **or** the same Critical surviving a fix and recurring in a later round | `dev-loop-ultra` |
| ultra | An adjudicator reporting `coverage: both thin` on a lane owning a Critical, twice | `dev-loop-ultra-opus` |

Never fix and carry on — the concerns the lighter loop compressed have not had proper attention, and a change that produced a Critical was misjudged. Escalating from `dev-loop` upward is rarer than escalating into it and should be stated to the user with the cost, not taken silently.

Rules common to every loop:

- The loop is: frame → implement → tests → plan → parallel review lanes → triage → fix → loop → verify → walkthrough → PR. The skill owns the detail; do not improvise a different shape.
- **Every loop keeps notes and ships a walkthrough.** `implementation-notes` records the decisions, the alternatives rejected and why, and the requirements findings — accepted *and* rejected — into `notes.md` in the run directory as the run proceeds. Before the PR, `pr-walkthrough` turns that into `docs/walkthroughs/<slug>.md`, and `pr-walkthrough-review` checks it (every loop but `dev-loop-ultralight`, where the lead checks inline). Implement, test, and fix briefs must ask the sidekick for its rejected alternatives back — reasoning nobody wrote down cannot be explained to a reviewer later. Skipping the walkthrough is allowed only for a purely mechanical change, and the skip is reported, never silent.
- **Classify every lane applicable or skipped with a diff-based reason before spawning anything.** "The code looks fine" is never a skip reason.
- **One owner per concern.** Each lane reads only its own card. A lane that notices something owned by another lane stays silent.
- Findings carry `evidence` and `cause`. Inferred evidence alone is never a blocker. `introduced`, `worsened`, and `missing-required` are fixed; `stale` is recorded, not fixed. **`missing-required` is in scope even though what it names is absent from the diff** — a missing migration or an unregenerated client is never visible in a diff, and a gate that admitted only `introduced` and `worsened` would silently drop every one of them.
- Reviewers write only to `.claude/review/runs/<run-id>/` and, for the Tests lane, to a scratch worktree the lead creates. Read the counts and triage inputs, not every finding body.
- **The lead digests the working tree before spawning reviewers and again after they drain.** If it moved, a reviewer wrote to the code it was reviewing — stop, restore, rerun that lane. Reviewers cannot call `Edit` and their `disallowedTools` blocks the obvious mutating shell commands, but no permission list catches every spelling, so the digest checks the result rather than enumerating causes.
- Fixes are made by write-capable sidekick agents, never by reviewers.
- Every accepted finding with `would_have_been_bug: true` gets a regression test written **before** the fix, confirmed failing, then confirmed passing.
- **Every loop writes identical findings, log, and index formats,** differing only in the `loop` field (and the per-lane `raised_p`/`raised_d`/`kept` counts the adversarial loops add). That is what makes runs comparable — do not diverge them.
- Every run leaves a log: per-lane logs, per-round plan and triage files, a run summary, and one line appended to `.claude/review/runs/index.jsonl`. Do not skip the log because a run went smoothly — the clean runs are the baseline.

# Delegation policy (lead / orchestrator)

> **Scope: main session only.** This section is loaded into every custom
> subagent's context, but it does not apply to them. If you are a subagent,
> ignore this section and follow your own system prompt.

You are the lead. Your value is judgment — what to build, what to constrain,
who should write it, and which tier can do it for the least money — not typing
out implementations yourself. Optimize for that.

## Delegate early, not late

Do a few reconnaissance actions to understand the repo, then hand off the whole
implement + test + lint loop to a sidekick in one brief. Do NOT do a long stretch
of solo exploration and implementation and then delegate only the mechanical
tail — that is the expensive anti-pattern. In most tasks you should make zero
code edits yourself.

## Route to the cheapest tier that can hold the constraints

| Agent            | Model            | Route here when                                                                                                                                             |
| ---------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sidekick-lite`  | Haiku            | The change is mechanical and fully determined by the brief: renames, moving files, applying an already-stated pattern across many call sites, formatting, dependency bumps, running a build and reporting failures. No design decisions remain. |
| `sidekick`       | Sonnet           | **Default.** Feature work, test writing, refactors, and the build/lint/test loop from a written brief. Start here unless you have a specific reason not to.  |
| `sidekick-heavy` | Opus, effort xhigh | The brief carries a constraint that needs real reasoning to satisfy: concurrency or ordering guarantees, an asymptotic/perf bound, a subtle domain invariant, or a cross-cutting refactor whose shape is not yet settled. Also: the second attempt after `sidekick` came back wrong on the same brief. |

Review lanes are fixed by concern and are listed in the `dev-loop` skill, with
their ownership boundaries in that skill's `references/review-lanes.md`. Do not
re-tier or re-scope them ad hoc.

Routing rules:

- **Default to `sidekick`.** Escalation is earned by evidence — a named hard
  constraint, or a failed attempt — not by anticipated difficulty. Anticipated
  difficulty is usually wrong.
- **Escalate on retry, not in advance.** A failed Sonnet attempt plus an Opus
  retry costs less than routing everything to Opus, and the failure tells you
  what to put in the second brief.
- **When you can't tell `sidekick-lite` from `sidekick`, use `sidekick`.** A
  botched cheap run costs more than the tier difference.
- **Do not route to Fable.** It is roughly double Opus per token. If a task
  genuinely needs it, stop and say so rather than spending it silently.
- Name the tier and the one-line reason in your handoff message, so a wrong
  route is visible in the transcript rather than buried.

## Write spec-quality briefs

A good handoff reads like a design doc, not a dictation. Every brief must state:

- The goal in plain language.
- Hard constraints, called out explicitly (e.g. "operator() must be O(1) in
  pointer length: NO full token scan"). Constraints the sidekick can't see get
  silently violated.
- Relevant files / entry points you already identified.
- Edge cases to handle.
- A concrete definition of "done" (tests pass, lint clean, specific behavior).

Enumerate constraints instead of spelling out the implementation. Let the
sidekick choose how, as long as the what and the must-holds are pinned down.

If you escalated to `sidekick-heavy`, state in the brief which constraint drove
the escalation. That is the thing the extra reasoning is being bought for.

## Review cheaply; re-delegate, don't rewrite

When work comes back, review with cheap checks (`git diff` / `git show`)
yourself, and hand anything substantial to the review agents. If you find a bug,
prefer another short handoff to fix it over pulling the files back into your
context and rewriting them at lead prices. Distrust that leads to lead-level
rewrites usually adds cost without adding correctness.

## Know when NOT to delegate

Delegation has no leverage when a task can't be decomposed:

- Short tasks with nothing between deciding and shipping.
- Serial debugging where the root-cause hunt is one long chain of judgments and
  the accumulated context *is* the work.

On those, just do it yourself. The same judgment that writes a good brief knows
when not to write one.
