---
name: dev-loop-lite
description: >
  The lightweight implement → test → four-lane review → fix → PR loop, for small
  contained changes. Use when asked for a lite run, or when the user types
  /dev-loop-lite. Four consolidated lanes, cheaper models, two rounds maximum.
  Not for changes touching security surfaces, migrations, public contracts, or
  more than one project — those go to the full `dev-loop` skill.
---

# Development and review loop — lite

You are the lead. Same shape as `dev-loop`, fewer lanes, cheaper tiers, tighter
bounds. You still write no implementation code yourself.

Lane definitions live in `references/review-lanes-lite.md` beside this file.
Pass each reviewer the path and its card name; never read the file whole.

The working-tree snapshot, the integrity check, and the scratch worktree the
Tests lane needs are shared with the full loop and live in
`dev-loop/references/tree-snapshot.md`. You run those commands; reviewers never
do. Read it before Phase 3.

## When this loop is the wrong one

Stop and use the full `dev-loop` instead if **any** of these hold:

- The diff touches authentication, authorization, secrets, or untrusted input.
- A migration, schema, or public API contract changes.
- More than one project in the solution is modified.
- The change is going to production on a path you cannot easily roll back.

If you are unsure, use the full loop. The lite loop's savings are not worth a
missed Critical.

## Phase 0 — Frame the slice

As in `dev-loop`: requirement, non-goals, constraints, entry points, definition
of done, and **the source branch** the PR will target.

Create `.claude/review/runs/<run-id>/` and write `brief.md`. Reviewers read it.

Then invoke the `implementation-notes` skill and create `notes.md` in the same
directory. Record the requirement, the non-goals, the constraints, and **which
loop you chose and the specific eligibility criterion that chose it**. You are
appending to this file for the rest of the run; Phase 8b turns it into the
walkthrough that ships with the PR.

## Phase 1 — Implement

**Implementation is not downgraded in this loop.** Use the same tiering as
`dev-loop`: `sidekick` by default, `sidekick-heavy` when the brief carries a
constraint needing real reasoning, `sidekick-lite` only for changes that are
purely mechanical. The lite loop economises on review, not on the code itself —
cheaper scrutiny of carefully written code is a reasonable trade; cheap code
reviewed cheaply is not.

One soft signal worth heeding: if you find yourself reaching for
`sidekick-heavy`, re-read the loop-selection criteria above. A change hard
enough to need it often turns out to touch something on that list.

**The brief must ask for the reasoning back.** Require the sidekick to return,
alongside its summary, the decisions it took, the alternatives it rejected and
why, and any constraint that forced a shape. Append what comes back to
`notes.md`. Without this the reasoning dies when the agent returns, and the
walkthrough in Phase 8b has nothing to work from but the diff.

## Phase 2 — Tests

A second handoff. Unit tests for logic and boundaries, integration tests for
anything crossing a process or service edge, UI tests for visible behaviour.
Each must fail if the behaviour regresses.

The brief also asks for the decisions taken and the alternatives rejected, and
the lead appends what comes back to `notes.md`.

## Phase 3 — Plan the round

Set `ROUND`, starting at 1. Create `round-N/`. Classify each lane and write
`round-N/plan.md` before spawning anything.

| Agent                        | Lane        | Applicable when                                                                                    |
| ---------------------------- | ----------- | -------------------------------------------------------------------------------------------------- |
| `reviewer-lite-correctness`  | Correctness | Always.                                                                                              |
| `reviewer-lite-structure`    | Structure   | Always.                                                                                              |
| `reviewer-lite-tests`        | Tests       | Always.                                                                                              |
| `reviewer-lite-security`     | Security    | The diff touches input handling, queries, serialization, file or network I/O, or dependencies. If it touches authn/authz or secrets, you are in the wrong loop. |

"The code looks fine" is never a skip reason. In round 2, rerun only the lanes
that owned accepted findings, plus `reviewer-lite-correctness` after any
behaviour-changing fix.

**Then snapshot the tree and set up the scratch worktree**, following
`dev-loop/references/tree-snapshot.md`. Record the digest in `round-N/plan.md` as
`tree: <sha>`, and create `round-N/scratch` for the Tests lane. Both are yours,
not a reviewer's, and both happen before you spawn anything.

## Phase 4 — Delegate

Spawn the applicable lanes **in parallel, in one turn**. Four fit in a single
batch; no waves needed.

Give each: its card name and path, the run directory and round, the diff base,
changed files, brief path, and available validation commands. Give the Tests
lane the scratch worktree path as well.

Each writes `round-N/<lane>.json` and `round-N/<lane>.log.md`, and returns one
line — path and counts by severity.

**When all four have drained, retake the snapshot and compare it against
`plan.md` before you read a single finding.** If it moved, a reviewer wrote to
the tree under review — stop and follow the recovery steps in
`tree-snapshot.md`. Four lanes reading one tree concurrently is exactly the
situation this check exists for.

## Phase 5 — Triage

Same rules as `dev-loop`, in this order:

1. **Cluster by locator and cause**; one owning lane per concern.
2. **Gate on evidence** — `inferred` alone is never Critical or Major.
3. **Gate on cause** — `introduced`, `worsened`, and `missing-required` are
   fixed; `stale` is recorded, not fixed. **`missing-required` counts even
   though what it names is absent from the diff** — the correctness lane owns
   artifacts here and will raise a missing migration or an unregenerated client,
   neither of which can appear in a diff.
4. **Separate defect from remedy** — accepting a finding does not make its
   suggested fix authoritative. Prefer the smallest fix preserving intent.
5. **Check `wontfix.json`**; append every rejection with a reason. It dies with
   the run.
6. **Record durable decisions** — a rejection that reflects a deliberate
   repository decision goes in `.claude/review/conventions.md`, whichever lane
   raised it. That file is the only thing that survives to the next run.

Write `round-N/triage.md`: every finding, accepted or rejected, and why.
**Classify each rejection** as `stale`, `evidence`, `remedy`, or `wrong` — only
`wrong` counts against a lane. The consolidated lanes make this more important
than in the full loop, not less: a merged lane's total rejection rate blends four
concerns and tells you nothing on its own.

Then append the **Interesting finds** to `notes.md`: any finding worth explaining
to a reviewer, every accepted-defect-but-rejected-remedy pair, and every
`conventions.md` entry created this run.

**This loop has no separate requirements lane — `reviewer-lite-correctness`
owns conformance to the brief.** Apply the full loop's rule to its findings
about the brief: they go into `notes.md` whether you accepted them or rejected
them. Every other lane's rejected findings are correctly dropped here. A
rejected requirements finding is not noise — it is a statement that the brief
was ambiguous, or that the reviewer read it differently from the implementer,
and that is exactly what a reviewer of the change needs to be told. Record the
finding, the decision, and the reason.

### Escalation to the full loop

**If any lane reports a Critical in round 1, abandon this loop and restart under
`dev-loop`.** A Critical in a change small enough for the lite loop means the
change was misjudged.

Be clear about *why* that follows, because it is not a coverage argument: these
four consolidated lanes do cover all nine of the full loop's concerns. What they
do not have is **depth or tiering.** Nine concerns compressed into four contexts
means each gets a fraction of the attention, on Sonnet and Haiku rather than
four Opus lanes, with two rounds instead of three and verification usually
skipped. A Critical is evidence that this change needed the attention the full
loop gives it — not evidence that some concern went unexamined.

Say clearly that you are escalating and why. Do not fix the Critical here and
carry on.

## Phase 6 — Fix

One brief to `sidekick`, or `sidekick-heavy` if the fixes need judgment. Same
tiering as `dev-loop` — fixes are not downgraded either.

For each accepted finding with `would_have_been_bug: true`: write a test that
**fails against the current code**, confirm it fails, apply the fix, confirm it
passes. That order, stated explicitly in the brief.

Then run the smallest relevant validation, not the whole suite.

The brief also asks for the decisions taken and the alternatives rejected, and
the lead appends what comes back to `notes.md`.

## Phase 7 — Loop or exit

**Remove the round's scratch worktree first** — `git worktree remove --force
round-N/scratch && git worktree prune` — pass, fail, or blocked. Then retake the
snapshot: Phase 6's fixes changed the tree legitimately and the new digest is
round 2's baseline.

Increment `ROUND` and return to Phase 3. **Rounds are capped at 2, not 3.**

*Pass:* no Critical or Major survived triage and targeted validation passes.

*Blocked — stop and report:* `ROUND` would exceed 2, the same concern was raised
and fixed twice, a round made no material progress, or completion needs
clarification or redesign.

A lite change that cannot converge in two rounds is not a lite change. Report and
switch loops rather than adding a third round.

## Phase 8 — Verification

Spawn `reviewer-verify` only if a Critical or a Major with `would_have_been_bug`
was fixed this run, or artifacts changed. Otherwise skip it and say so in
`run.md`. This agent stays on Opus deliberately — it is the last gate before a
human sees the work.

## Phase 8b — Walkthrough

The change has been reviewed, but the reasoning behind it still exists only in
`notes.md`. This phase turns it into the document that ships with the PR.

1. **Author it.** Invoke the `pr-walkthrough` skill. Delegate the draft to
   `sidekick`, passing the `notes.md` path, the diff base, the changed-file
   list, the path to `pr-walkthrough/SKILL.md`, and the resolved exemplar path
   (newest file in `docs/walkthroughs/`, else the bundled
   `references/example-walkthrough.md`). `sidekick` cannot fetch either
   itself, so the format has to travel in the brief alongside the reasons.
   **The notes are the brief, not the diff** — a draft briefed on the diff
   comes back as a narrated changelog, which is the one failure this phase
   exists to prevent. If `notes.md` is missing or thin, write the walkthrough
   yourself and record in `run.md` that the notes were inadequate; that is a
   defect in the run worth seeing.

2. **Review it.** Delegate to `sidekick`, passing the `pr-walkthrough-review`
   skill path and the walkthrough path. It is write-capable on the walkthrough
   file only and returns one line — path, whether it edited, and issues
   corrected by category. Do not read the document into your own context to
   judge it — that is why this is a delegation, not an invocation in the
   lead's own context.

3. **Retake the working-tree snapshot and record it as the new baseline** for
   Phase 9, per `dev-loop/references/tree-snapshot.md`. **Do this whether or not you wrote
   a walkthrough** — on a skip the digest simply matches the one Phase 7
   recorded, and Phase 9 compares against this step unconditionally, so it must
   always have a value to compare against. **This is not bookkeeping.** The
   walkthrough is a new file under `docs/`, which is not `.gitignore`d, so it
   changes the digest — and Phase 9 step 4 stops the run when the digest differs
   from the recorded baseline. Without this step, every run halts there. The only
   legitimate delta is the walkthrough file itself; anything else is the failure
   that check has always been for, and is handled the same way.

Skipping the walkthrough is permitted only for a purely mechanical change — a
rename, a dependency bump, a formatting sweep. A skip is stated in the PR
description and in `run.md`. It is never silent.

## Phase 9 — Commit, push, pull request

Everything reviewed so far lives in the working tree. **Nothing is on the branch
until you put it there.**

0. **Remove every scratch worktree from this run** — `git worktree list`, then
   `git worktree remove --force <path>` for anything under this run directory,
   then `git worktree prune`. Before staging, so a stray worktree cannot surface
   as untracked content.
1. Full build and test suite green.
2. **Stage everything, including untracked files.** Read `git status --porcelain`
   — new files show as `??` and are not picked up by a path-pattern `git add`.
   Re-run it after staging and confirm nothing relevant is left. Exclude
   `.claude/review/runs/`; commit `.claude/review/conventions.md`. The
   walkthrough at `docs/walkthroughs/` **is** committed — it is part of the
   change and the PR description links it.
3. Commit, referencing the work item where there is one.
4. **Verify the committed diff is the reviewed diff — by content, not filename.**
   `git diff <base>...HEAD --stat` against the changed-file list in
   `round-1/plan.md`; if a reviewed file is missing, **stop**, staging went
   wrong. Then `git rev-parse HEAD^{tree}` against the digest recorded at the
   end of Phase 8b. Same files with different contents produce an identical
   `--stat`, so only the digest catches content that moved between the last
   review and the commit.
5. Push, and confirm the remote has the branch.
6. Create the PR targeting the source branch recorded in Phase 0.
7. **Confirm the PR's file list matches step 4.**
8. Description: what changed, why, lanes run and skipped, rounds taken, **that
   this was a lite run**, a link to the walkthrough, and any deferred findings.
9. Write `run.md`; append one line to `.claude/review/runs/index.jsonl` with
   `"loop":"lite"`.

### Work tracker changes

This loop does not create, close, or change the state of work items, and does not
merge anything, **unless the user asked it to.** A specific instruction covers
this run only; it is not standing authorisation.

## Formats

Findings, logs, and the index line use exactly the formats in the `dev-loop`
skill. Do not diverge — a shared format is what lets you compare lite and full
runs in `index.jsonl` and see whether the lite loop is missing things the full
loop catches.

The one addition is `"loop":"lite"` in the index line. The full loop writes
`"loop":"full"`. `"walkthrough"` is the committed path, or `skipped:<reason>`,
same as the full loop.
