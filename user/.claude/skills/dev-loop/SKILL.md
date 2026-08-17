---
name: dev-loop
description: >
  The implement → test → multi-lane review → fix → PR loop. Use when asked to
  implement a feature or change end to end, or when the user types /dev-loop.
  Owns the lane set, applicability gating, the findings format, triage rules,
  termination conditions, run logging, and PR creation.
---

# Development and review loop

You are the lead. You run this loop. You do not write implementation code
yourself at any point in it.

Lane definitions live in `references/review-lanes.md` beside this file. You
never read that file whole — you pass each reviewer the path and tell it which
card to read.

`references/tree-snapshot.md` holds the working-tree snapshot, the integrity
check, and the scratch worktree the Tests lane needs. You run those commands;
reviewers never do. Read it before Phase 3.

## Phase 0 — Frame the slice

Establish, in writing, before anything else:

- The requirement, in plain language, and the explicit non-goals.
- Hard constraints.
- Files and entry points identified in reconnaissance.
- Definition of done, including which validation commands must pass.
- **The source branch.** Create the working branch from it and record it. The PR
  targets this branch, not the repo default.

Create the run directory `.claude/review/runs/<run-id>/` where `<run-id>` is
`YYYYMMDD-HHMM-<branch-slug>`. Write the brief to `brief.md` inside it. All
paths below are relative to the run directory.

Reviewers read `brief.md`. If it is not written down, the requirements lane
cannot run.

Then invoke the `implementation-notes` skill and create `notes.md` in the same
directory. Record the requirement, the non-goals, the constraints, and **which
loop you chose and the specific eligibility criterion that chose it**. You are
appending to this file for the rest of the run; Phase 8b turns it into the
walkthrough that ships with the PR.

## Phase 1 — Implement

Delegate to the appropriate sidekick tier. The brief must require conformance to
the `coding-standards` skill and the `solution-architecture` skill, both
preloaded into the sidekick agents.

**The brief must ask for the reasoning back.** Require the sidekick to return,
alongside its summary, the decisions it took, the alternatives it rejected and
why, and any constraint that forced a shape. Append what comes back to
`notes.md`. Without this the reasoning dies when the agent returns, and the
walkthrough in Phase 8b has nothing to work from but the diff.

## Phase 2 — Tests

A second handoff, not part of Phase 1. Require unit tests for logic and
boundaries, integration tests for anything crossing a process, database, queue,
or service edge, and UI tests for user-visible behaviour changes. Each test must
fail if the behaviour it covers regresses — state this in the brief.

The brief also asks for the decisions taken and the alternatives rejected, and
the lead appends what comes back to `notes.md`.

## Phase 3 — Plan the review round

Set `ROUND`, starting at 1. Create `round-N/`.

Classify each lane `applicable` or `skipped` with a concrete, diff-based reason.
Write the classification to `round-N/plan.md` **before** spawning anything.

| Agent                   | Lane          | Applicable when                                                                                                          |
| ----------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `reviewer-requirements` | Requirements  | Always.                                                                                                                    |
| `reviewer-technical`    | Technical     | Always.                                                                                                                    |
| `reviewer-tests`        | Tests         | Always.                                                                                                                    |
| `reviewer-architecture` | Architecture  | Types were added, moved, or renamed; responsibilities shifted between types; project or layer dependencies changed; a method or class gained a new kind of work. |
| `reviewer-standards`    | Standards     | Any source file changed.                                                                                                   |
| `reviewer-security`     | Security      | The diff touches input handling, authn/authz, secrets, serialization, queries, file or network I/O, or dependencies.       |
| `reviewer-deadcode`     | Dead code     | Paths were removed, replaced, narrowed, or refactored.                                                                     |
| `reviewer-minimalism`   | Minimalism    | Guards, fallbacks, wrappers, configuration, error handling, abstractions, or supporting tests were added.                  |
| `reviewer-artifacts`    | Artifacts     | A migration, schema, generated file, lockfile, project file, package reference, or CI configuration changed — or should have. |

**"The code looks fine" is not a skip reason.** Only a factual statement about
what the diff does not touch is a skip reason. Record each skip as
`skipped — <what the diff does not touch>`.

### Snapshot the tree, then set up the scratch worktree

Still in Phase 3, **before you spawn anything**, follow
`references/tree-snapshot.md`:

1. Take the working-tree snapshot and record it in `round-N/plan.md` as
   `tree: <sha>`. This is what Phase 4 compares against to prove no reviewer
   wrote to the code it was reviewing.
2. If the Tests lane is applicable, create the scratch worktree at
   `round-N/scratch` and pass its path to that lane. It is the only place any
   reviewer may write outside the run directory.

Neither step is optional and neither belongs to a reviewer. A lane that had to
create its own scratch space would be creating it from a tree it has already
been told not to touch.

In round 2 and later, recompute applicability from the fix delta: rerun the
lanes that owned accepted findings, plus any lane the fixes newly made
applicable. Always rerun `reviewer-technical` after a behaviour-changing fix.
Do not rerun every lane by reflex — a comment-only or test-only fix does not
justify a full round.

## Phase 4 — Delegate

Spawn the applicable reviewers **in parallel, in one turn**, up to four at a
time. If more than four are applicable, run them in waves and let each wave
drain before starting the next; five-plus Opus reviewers at once will hit
concurrency and rate limits before they hit anything useful.

Give each reviewer:

- The lane card path and the name of its card. Only its card.
- The run directory path and round number.
- The diff base, the changed files, and the brief path.
- The validation commands available and any intentional tradeoffs.
- **For the Tests lane only:** the scratch worktree path from Phase 3.

Each reviewer writes findings to `round-N/<lane>.json` and its own log to
`round-N/<lane>.log.md`, and returns **one line** to you: path written and counts
by severity. Do not read the finding bodies into your own context yet.

### Verify the tree before you triage

When every reviewer has drained, **retake the snapshot and compare it against
the `tree:` line in `plan.md`** before reading a single finding.

If it differs, a reviewer wrote to the tree under review. **Stop and follow the
recovery steps in `references/tree-snapshot.md`** — identify the lane, restore
the tree, rerun that lane from the restored tree. Do not assess whether the
mutation looked harmless: every finding from that round describes a tree that no
longer exists.

Reviewers are barred from `Edit` and from the obvious mutating shell commands,
so this check should pass every time. That is the point of running it — it is
cheap, and the one run where it fails is a run where the file-list comparison in
Phase 9 would have said everything was fine.

## Phase 5 — Triage

Read the findings files. Then, in this order:

1. **Cluster by locator and cause.** Group findings pointing at the same
   location and underlying cause. Assign **one owning lane** per concern; the
   rest become corroborating evidence or an alternative suggested fix. Never fix
   the same thing twice because two lanes described it differently.
2. **Gate on evidence.** A finding whose only evidence is `inferred` can never
   be Critical or Major. Demote it or drop it. Reject vague, preference-only,
   and trigger-less findings outright.
3. **Gate on cause.** `introduced`, `worsened`, and `missing-required` are in
   scope and get fixed. `stale` and pre-existing debt go in the PR description,
   not the fix brief — fixing them expands the diff and hides the actual change.

   **`missing-required` is in scope precisely because the thing it names is not
   in the diff.** It is the cause for something the change required and did not
   produce: the migration for a schema change, the regenerated client for an
   altered contract, the lockfile for a new package. The artifacts lane is
   explicitly gated on "changed — **or should have**" and will raise these; a
   gate that admitted only `introduced` and `worsened` would drop every one of
   them, because absent code is never in a diff. Treat these at face value:
   a missing destructive-migration guard is Critical whether or not anything
   was written down.
4. **Separate defect from remedy.** Accepting that a finding is real does not
   make its `suggested_fix` authoritative. Prefer the smallest fix preserving
   intent. Before accepting a fix that adds a wrapper, validator, cache, config
   flag, state field, or compatibility layer, check whether a narrower change at
   a boundary or type would do.
5. **Check `wontfix.json`** at the run root. Anything rejected in an earlier
   round is dropped, not re-litigated. Append every rejection with a one-line
   reason. This is what stops the loop oscillating **within** a run.
6. **Record durable decisions.** `wontfix.json` dies with the run. When a
   rejection reflects a *deliberate decision in this repository* — not merely
   something out of scope for this slice — append it to
   `.claude/review/conventions.md` at the repo root, with the decision and one
   line of reasoning. That file is read on every future run, and it is the only
   thing that stops a known non-finding being raised forever. It accumulates
   from real triage decisions; never author it speculatively.

   **This is not only for architecture and standards.** Any lane can produce a
   finding that is correctly rejected for a durable reason — technical flagging a
   hot path deliberately left unguarded because the caller holds the invariant,
   minimalism flagging a wrapper that exists for a recorded reason. Those recur
   exactly as reliably as architectural ones, and without an entry they are
   re-argued from scratch every run at full price. Name the owning lane in the
   entry so a future reviewer can see which card it answers.

Write every decision to `round-N/triage.md`: each finding, accepted or rejected,
and why. **Classify each rejection** as `stale`, `evidence`, `remedy`, or
`wrong` — the index line carries these separately, and the distinction is what
lets you tell a lane whose findings the gates correctly filtered from a lane that
is producing untrue findings. Only the last kind counts against a lane.

This file is the main thing you will want when a run goes wrong.

Then append the **Interesting finds** to `notes.md`: any finding worth explaining
to a reviewer, every accepted-defect-but-rejected-remedy pair, and every
`conventions.md` entry created this run.

**Requirements-lane findings go in whether you accepted them or rejected them.**
Every other lane's rejected findings are correctly dropped here. A rejected
requirements finding is not noise — it is a statement that the brief was
ambiguous, or that the reviewer read it differently from the implementer, and
that is exactly what a reviewer of the change needs to be told. Record the
finding, the decision, and the reason.

You are the arbiter. A reviewer's output is advice.

## Phase 6 — Fix

One brief to a sidekick containing the accepted findings and their smallest
fixes. Fixes are made by write-capable agents; reviewers never edit.

For each accepted finding with `would_have_been_bug: true`:

1. Write a test that **fails against the current code**.
2. Confirm it fails.
3. Apply the fix.
4. Confirm it passes.

State that order explicitly in the brief. A test written after the fix proves
nothing about whether it would have caught the bug.

Then run the smallest relevant validation — the affected tests, type check,
linter, build, and any generated-artifact check — not the whole suite.

The brief also asks for the decisions taken and the alternatives rejected, and
the lead appends what comes back to `notes.md`.

## Phase 7 — Loop or exit

**Remove the round's scratch worktree first** — `git worktree remove --force
round-N/scratch && git worktree prune` — whether the round passed, failed, or
blocked. A left-behind worktree holds a snapshot commit alive and confuses the
next round's setup. Then retake the snapshot: Phase 6's fixes changed the tree
legitimately, and the new digest is the baseline the next round records.

Increment `ROUND` and return to Phase 3. **Stop when any of these holds:**

*Pass:*
- No Critical or Major findings survived triage, and targeted validation passes.
- Two consecutive rounds produced only Minor findings.

*Blocked — stop and report, do not continue:*
- `ROUND` would exceed 3.
- The same concern has been raised and fixed twice. The fix is not addressing
  the cause and a third attempt will not help.
- A round produced no material progress.
- Completion needs clarification, a broad redesign, or behaviour outside the
  brief's intent.

Never loop unbounded. Yield falls off sharply after round two.

## Phase 8 — Independent verification

Before the PR, spawn `reviewer-verify` once when validation is uncertain, the
slice is risky, artifacts changed, or a Critical was fixed this run. Ask it only
whether the final diff preserves intent, validation matches the touched
behaviour, required checks ran or have stated blockers, and deferrals have
concrete reasons. Do not ask it to re-review the whole diff.

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
   Phase 9, per `references/tree-snapshot.md`. **Do this whether or not you wrote
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
until you put it there**, and a PR raised from an unpushed or partially staged
branch either is empty or contains a different diff from the one the lanes just
approved. Work through this in order and verify each step rather than assuming it.

0. **Remove every scratch worktree from this run**, including from rounds that
   ended early: `git worktree list`, then `git worktree remove --force <path>`
   for anything under this run directory, then `git worktree prune`. Do this
   before staging, so a stray worktree cannot surface as untracked content.

1. **Full build and test suite green.**

2. **Stage everything, including untracked files.** Run `git status --porcelain`
   and read it. New files show as `??` and **are not picked up by a path-pattern
   `git add`** — a missed DTO or test file produces a PR that does not compile.
   Stage explicitly, then re-run `git status --porcelain` and confirm nothing
   relevant is left unstaged or untracked.

   Exclude the run directory: `.claude/review/runs/` is working output, not part
   of the change. `.claude/review/conventions.md` **is** committed — it is shared
   repository knowledge. The walkthrough at docs/walkthroughs/ **is** committed —
   it is part of the change and the PR description links it.

3. **Commit**, referencing the work item where there is one.

4. **Verify the committed diff is the diff that was reviewed — by content, not
   by filename.** Two checks, and the second is the one that matters:

   - `git diff <base>...HEAD --stat` against the changed-file list in
     `round-1/plan.md`. They must match, allowing for files the fix phases
     touched. **If a file the lanes reviewed is missing from the commit, stop**
     — staging went wrong, and the review no longer describes what you are about
     to push.
   - `git rev-parse HEAD^{tree}` against the digest recorded at the end of
     Phase 8b. **If they differ, something changed the tree
     between the last review and the commit** — an editor, a formatter on save,
     a stray command — and a matching file list will not reveal it, because the
     same files with different contents produce the same `--stat`. Stop and find
     out what moved.

   A file-list comparison catches a missing file. Only the digest catches
   changed content in a file that is present, which is the failure this loop is
   otherwise blind to.

5. **Push the branch** and confirm the remote has it.

6. **Create the PR targeting the source branch recorded in Phase 0.** Never the
   repository default.

7. **Confirm the PR's file list matches step 4.** A PR opened against the wrong
   base, or from a branch pushed before the final commit, shows a diff nobody
   reviewed. Check it rather than trusting that the previous steps worked.

8. Description: what changed, why, constraints verified, lanes run and skipped,
   rounds taken, every deferred or unresolved finding stated honestly, and a
   link to the walkthrough, per the hosting table in the pr-walkthrough skill.

9. Write `run.md` at the run root: outcome, rounds, validation results,
   verification result, residual concerns.

10. Append one line to `.claude/review/runs/index.jsonl` (format below). You are
    the only writer of this file.

If verification (Phase 8) ran before the work was committed, its findings still
hold — it verified the working tree, which is the same content. But **it did not
verify the commit**, so steps 2 and 4 are yours alone and cannot be skipped on
the grounds that verification passed.

### Work tracker changes

This loop does not create, close, or change the state of work items, and does not
merge anything, **unless the user asked it to.** When they have — filing a bug
for a defect found and deferred, for instance — do it and record what was created
in `run.md`. Do not extend a specific instruction into a standing one: being told
to file a bug this run is not authorisation to file bugs next run.

The `reviewing-prs` skill governs review of *existing* PRs. It does not apply
here — these findings are already fixed and the PR does not exist until now.

## Findings format

Every reviewer writes an array of these to its JSON file:

```json
[
  {
    "id": "sec-001",
    "lane": "security",
    "severity": "Critical|Major|Minor",
    "evidence": "direct|spec|policy|test|validation|missing|inferred",
    "cause": "introduced|worsened|stale|missing-required",
    "file": "src/Gateway/MovementService.cs",
    "line": 142,
    "finding": "One sentence stating what is wrong.",
    "why_it_matters": "The concrete consequence, or how to trigger it.",
    "suggested_fix": "The smallest change that fixes it. Not a diff.",
    "would_have_been_bug": true,
    "confidence": "high|medium|low"
  }
]
```

`evidence` records what the reviewer actually saw. `direct` — read it in the
changed code. `spec` / `policy` / `test` / `validation` — conflicts with the
brief, the standards, an existing test, or a command's output. `missing` —
something required is absent. `inferred` — reasoned out but not pointed at.
**Inferred alone is never a blocker.**

`cause` records the finding's relationship to this diff. Only `introduced` and
`worsened` are fixed here.

An empty array is a valid and expected result.

## Run log

Every agent writes its own log file — no shared file, to avoid interleaved
writes from parallel agents.

Each reviewer writes `round-N/<lane>.log.md`:

```markdown
# <lane> — round N
- model: <model>, started: <ts>, finished: <ts>
- inputs read: <files, commands run>
- applicability: applicable | skipped — <reason>
- findings: <n> Critical, <n> Major, <n> Minor
- dropped before reporting: <what you considered and did not raise, and why>
- uncertain about: <anything you could not verify, or "nothing">
```

The `dropped` and `uncertain` lines are the point of the log. They are how you
tell later whether a lane is too quiet or too noisy.

The lead writes `plan.md` and `triage.md` per round, `run.md` at the end, and
appends to `.claude/review/runs/index.jsonl`:

```json
{"run_id":"20260728-1430-feat-movement-batching","loop":"full","branch":"feature/movement-batching","base":"develop","rounds":2,"outcome":"pass","lanes":{"security":{"raised":3,"accepted":1,"rejected_stale":1,"rejected_evidence":0,"rejected_remedy":1,"rejected_wrong":0},"technical":{"raised":2,"accepted":2,"rejected_stale":0,"rejected_evidence":0,"rejected_remedy":0,"rejected_wrong":0}},"regression_tests_added":1,"walkthrough":"docs/walkthroughs/movement-batching.md","pr":"<url>"}
```

The `loop` field is `full` here, `lite`, `ultralight`, `ultra`, or `ultra-opus`
elsewhere. All loops write this format identically so runs are comparable.

`walkthrough` is the committed path, or `skipped:<reason>`. All five loops write
it identically.

**Rejections are split by reason, and the split is the point.** A bare
accepted-versus-rejected ratio cannot tell a noisy lane from a well-functioning
one, because most rejections are the gates doing their job rather than the lane
misbehaving:

| Field | Meaning | What it says about the lane |
| --- | --- | --- |
| `rejected_stale` | Real, but `cause: stale` or pre-existing | Lane is fine. The cause gate worked. |
| `rejected_evidence` | Demoted or dropped for `inferred`-only evidence | Lane is fine, though a lot of these means it is reasoning past what it can see. |
| `rejected_remedy` | Correct observation, remedy rejected or out of scope | Lane is fine — arguably doing its best work. |
| `rejected_wrong` | The finding was simply not true | **This is the only one that counts against the lane.** |

Judge lane health on `rejected_wrong` against `raised`, not on the total
rejection rate. A lane raising five findings of which four are rejected as
`stale` is working correctly; a lane raising two of which one is `rejected_wrong`
is not.

If you cannot cleanly classify a rejection, use `rejected_wrong` — over-counting
against a lane is the safer error, since it prompts a look at the card rather
than quiet confidence in a lane that is drifting.

The accepted-versus-rejected ratio per lane, across runs, is the signal worth
watching. A lane consistently below roughly a third accepted is producing noise
— tighten its card's quality brake or narrow its applicability rule. A lane that
never raises anything may be gated too tightly, or its card may be too vague to
act on.
