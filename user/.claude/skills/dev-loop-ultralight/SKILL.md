---
name: dev-loop-ultralight
description: >
  The minimal implement → test → single review → fix → PR loop, for trivial
  contained changes. Use when asked for an ultralight run, or when the user types
  /dev-loop-ultralight. One reviewer covering every concern, one round, no
  verification phase. Not for anything touching security surfaces, migrations,
  public contracts, concurrency, or more than a handful of files — those go to
  `dev-loop-lite` or the full `dev-loop`.
---

# Development and review loop — ultralight

You are the lead. One reviewer, one round, minimal ceremony. You still write no
implementation code yourself.

This loop trades review depth for speed. It is safe only because its eligibility
criteria are narrow — enforce them strictly, because nothing downstream will
catch a change that should not have been here.

## Eligibility — check before anything else

Use this loop **only if all of these hold**:

- One project, and roughly five files or fewer.
- No authentication, authorization, secrets, or untrusted input.
- No migration, schema, generated artifact, or public API contract change.
- No concurrency, async ordering, or transaction-boundary change.
- No new dependency.
- The change is easy to roll back.

**If any one fails, use `dev-loop-lite`.** If several fail, or you are unsure,
use the full `dev-loop`. The eligibility list is the entire safety mechanism of
this loop; treating it loosely is how a trivial-looking change ships a defect
that a heavier loop would have caught. One reviewer sweeping nine concerns in a
single pass covers the same ground as the full loop's nine lanes on paper, and
gives each of them a ninth of the attention in practice. The eligibility rules
are what make that trade acceptable — nothing downstream will.

## Phase 0 — Frame

Brief enough to fit in a short paragraph: what changes, what must not change,
which files, definition of done, and **the source branch** the PR targets.

Create `.claude/review/runs/<run-id>/` and write `brief.md`. It can be short,
but it must exist — the reviewer checks the change against it.

Then invoke the `implementation-notes` skill and create `notes.md` in the same
directory. Record the requirement, the non-goals, the constraints, and **which
loop you chose and the specific eligibility criterion that chose it**. You are
appending to this file for the rest of the run; Phase 5b turns it into the
walkthrough that ships with the PR.

## Phase 1 — Implement and test

**One handoff, not two.** Unlike the other loops, implementation and tests go in
a single brief here; a change this small does not justify splitting them.

**Implementation is not downgraded.** Same tiering as the other loops:
`sidekick` by default, `sidekick-lite` for purely mechanical work,
`sidekick-heavy` if a constraint needs reasoning — though reaching for heavy is
a strong sign you are in the wrong loop.

Tests are still required. Each must fail if the behaviour it covers regresses.

**The brief must ask for the reasoning back.** Require the sidekick to return,
alongside its summary, the decisions it took, the alternatives it rejected and
why, and any constraint that forced a shape. Append what comes back to
`notes.md`. Without this the reasoning dies when the agent returns, and the
walkthrough in Phase 5b has nothing to work from but the diff.

## Phase 2 — Review

**Snapshot the working tree first**, following
`dev-loop/references/tree-snapshot.md`, and record the digest in
`round-1/plan.md` as `tree: <sha>`. One reviewer is a smaller blast radius than
four, but this loop has no second round to notice a tree that moved, so the
check matters more here rather than less.

Mutation testing is **not** offered in this loop — no scratch worktree, and the
reviewer judges assertions by reading them. A change small enough for ultralight
does not justify the setup, and a test suite you need to break to trust belongs
in a loop with a second round.

Spawn `reviewer-ultralight` once. It sweeps every concern in a fixed order and
writes `round-1/ultralight.json` plus `round-1/ultralight.log.md`.

When it returns, **retake the snapshot and compare** before triage. If it moved,
the reviewer wrote to the code it was reviewing: restore the tree and rerun. Do
not triage findings that describe a tree that no longer exists.

Its log records a verdict for **every** concern, including the ones it found
nothing on. Read that list. A sweep that reports nothing on eight concerns and
findings on one may have been thorough or may have stopped early — the per
concern verdicts are the only way to tell, and they are the main thing you are
buying by using a checklist reviewer instead of separate lanes.

## Phase 3 — Triage

Same gates as the other loops, applied by you:

1. **Gate on evidence** — `inferred` alone is never Critical or Major.
2. **Gate on cause** — `introduced`, `worsened`, and `missing-required` are
   fixed; `stale` is recorded, not fixed. **`missing-required` counts even
   though what it names is absent from the diff.** It should be rare here — this
   loop's eligibility rules exclude migrations and generated artifacts — so if
   the reviewer raises one, read it as a signal the change was not eligible.
3. **Separate defect from remedy** — prefer the smallest fix preserving intent.
4. **Check `wontfix.json`**; append rejections with a reason. It dies with the
   run.
5. **Record durable decisions** in `.claude/review/conventions.md`, whichever
   concern raised it. That file is the only thing that survives to the next run.

Write `round-1/triage.md`: every finding, accepted or rejected, and why.
**Classify each rejection** as `stale`, `evidence`, `remedy`, or `wrong`. Only
`wrong` counts against the reviewer. With a single reviewer there is no second
opinion to calibrate against, so this classification is your only read on whether
the sweep is producing true findings.

Then append the **Interesting finds** to `notes.md`: any finding worth explaining
to a reviewer, every accepted-defect-but-rejected-remedy pair, and every
`conventions.md` entry created this run.

**`reviewer-ultralight` owns conformance to the brief as part of its sweep.**
Its findings on requirements go into `notes.md` whether you accepted or rejected
them — a rejected requirements finding says the brief was ambiguous or read
differently from the implementer, which is exactly what a reviewer of the change
needs to be told. Every other rejected finding is correctly dropped here.

### Escalation — mandatory, one-way

Abandon this loop and restart under a heavier one if **any** of these hold:

| Trigger | Restart under |
| --- | --- |
| Any Critical finding | `dev-loop` (full) |
| A Major in security, architecture, or concurrency | `dev-loop` (full) |
| Any other Major | `dev-loop-lite` |
| More than four accepted findings | `dev-loop-lite` |
| The reviewer reports it could not cover a concern | `dev-loop-lite` |

Do not fix and carry on. A trivial change producing a Major was not trivial, and
the concerns this loop compressed into one pass have had a fraction of the
attention they would get elsewhere. Say plainly that you are escalating and why.

## Phase 4 — Fix

One brief to `sidekick`. For each accepted finding with
`would_have_been_bug: true`: write a test that **fails against the current
code**, confirm it fails, apply the fix, confirm it passes.

Then run the relevant tests, lint, and build.

The brief also asks for the decisions taken and the alternatives rejected, and
the lead appends what comes back to `notes.md`.

## Phase 5 — Exit

**There is no second round.** If the fixes did not clear the findings, or the fix
introduced something new, escalate to `dev-loop-lite` rather than reviewing
again. One reviewer looking twice at its own missed work is not independent.

**There is no verification phase.** Anything risky enough to warrant one has
already triggered escalation.

## Phase 5b — Walkthrough

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

2. **Check it yourself.** This loop does not spawn `pr-walkthrough-review` — a
   change small enough for ultralight does not justify another agent. Read the
   draft against that skill's criteria: does it explain why rather than what, is
   it calibrated to a senior engineer, are the cited line anchors real, do both
   Mermaid diagrams parse, and does it call `.sln` files solution files and
   `.csproj` files project files. Correct it in place.

3. **Retake the working-tree snapshot and record it as the new baseline** for
   Phase 6, per `dev-loop/references/tree-snapshot.md`. **Do this whether or not you wrote
   a walkthrough** — on a skip the digest simply matches the tree as it stood at
   the end of Phase 4, which the skipped walkthrough left untouched, and Phase 6
   compares against this step unconditionally, so it must always have a value to
   compare against. **This is not bookkeeping.**
   The walkthrough is a new file under `docs/`, which is not `.gitignore`d, so it
   changes the digest — and Phase 6 step 4 stops the run when the digest differs
   from the recorded baseline. Without this step, every run halts there. The only
   legitimate delta is the walkthrough file itself; anything else is the failure
   that check has always been for, and is handled the same way.

Skipping the walkthrough is permitted only for a purely mechanical change — a
rename, a dependency bump, a formatting sweep. A skip is stated in the PR
description and in `run.md`. It is never silent.

## Phase 6 — Commit, push, pull request

**Nothing is on the branch until you put it there.** This loop's brevity makes
this step easier to skip and no less necessary.

1. Build and tests green.
2. **Stage everything, including untracked files.** Read `git status --porcelain`
   — new files show as `??` and a path-pattern `git add` misses them. Confirm
   after staging. Exclude `.claude/review/runs/`; commit
   `.claude/review/conventions.md`. The walkthrough at `docs/walkthroughs/` **is**
   committed — it is part of the change and the PR description links it.
3. Commit, referencing the work item where there is one.
4. **Verify the committed diff is the reviewed diff — by content, not filename.**
   `git diff <base>...HEAD --stat` against what the reviewer swept; a missing
   file means the sweep covered something you are not pushing, so **stop**. Then
   `git rev-parse HEAD^{tree}` against the digest recorded at the end of Phase
   5b — the same files with different contents give an identical `--stat`, and
   with one reviewer and no second round this is the only content check the
   change gets.
5. Push, and confirm the remote has the branch.
6. Create the PR targeting the source branch from Phase 0, and **confirm its file
   list matches step 4.**
7. Description states what changed, why, **that this was an ultralight run with a
   single review pass**, a link to the walkthrough, and any deferred findings.
   Say it explicitly — a reviewer reading the PR should know how much scrutiny it
   actually had.
8. Write `run.md`; append one line to `.claude/review/runs/index.jsonl` with
   `"loop":"ultralight"`, rejections split by reason.

### Work tracker changes

This loop does not create, close, or change work item state, and does not merge
anything, **unless the user asked it to.** A specific instruction covers this run
only.

## Formats

Findings, logs, and the index line use exactly the formats in the `dev-loop`
skill, with `"loop":"ultralight"`. `"walkthrough"` is the committed path, or
`skipped:<reason>`, same as the other loops. Do not diverge — identical formats
are what let you compare the three loops in `index.jsonl` and find out whether
ultralight is cheap or merely blind.

That comparison is the point. Watch for changes reviewed here that later produce
bugs, and for the escalation rate: if a meaningful share of ultralight runs
escalate, the eligibility criteria are too loose, not the reviewer too strict.
