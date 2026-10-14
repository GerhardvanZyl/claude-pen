# Hospital-model mechanisms for the dev-loop ladder — Stage 1 design

- Date: 2026-10-14
- Tracking issue: https://github.com/GerhardvanZyl/claude-pen/issues/3
- Source: https://www.cockroachlabs.com/blog/experiment-running-hospital-code/
- Status: approved design, awaiting implementation plan

## 1. Context

Cockroach Labs ran a teaching-hospital-shaped agent pipeline ("MOLT Sinai") for about five months on a mirror of their MOLT migration-tools repository. Roles ran Triage Nurse → Fellow (investigate and implement) → Review Attending (a separate instance tasked with finding fault) → Discharge Nurse (audits *the review*, not the code), with a Charge Nurse watchdog, Infection Control, Safety and Research departments alongside. State lived in GitHub issue labels. Reported outcome: ~1,238 PRs, 1,299 issues (nearly half filed by the agents themselves), over a million lines landed, seven reverts, ~$135K total.

Their stated motivation is the one that transfers: not throughput, but "how many of those PRs would we have been embarrassed to have merged ourselves?"

Issue #3 records the full gap analysis against this repository's loop family. This document specifies Stage 1 of the agreed two-stage response.

### What the ladder already does as well or better

Circuit breaking (`ROUND <= 3` plus the repeat-concern bound) is tighter than their after-the-fact "handoff after four rework rounds" patch. `.claude/review/conventions.md` is a lane-attributed precedent log; theirs is not attributed. Regression-test-before-fix, role-framing personas and tiered model routing are already in place, and `dev-loop-ultra`'s opposed prosecution/defence pair plus adjudicator exceeds their single Review Attending. None of this changes.

## 2. Goals

Stage 1 addresses three stated shortfalls, in this order of weight:

1. **Defects still escape** the lanes and reach the PR or past it.
2. **A run cannot be trusted after the fact** — whether skips were factual, whether accepted findings were really fixed, whether lane health is drifting.
3. **A run costs too much of the lead's attention** — framing, loop selection, triage, and chasing deferred findings.

### Non-goals

Cost is explicitly not a driver for Stage 1. The following are deferred:

- Per-stage cost telemetry in the index.
- The prompt audit. Their July audit removed 23% of ~100K words of instruction without changing a gate; this repository's skills plus agents are ~44K words and have accumulated the same way.
- Everything continuous: the tracker state machine, the Research Department, Infection Control, the Charge Nurse watchdog. These are Stage 2 and get their own brainstorm.

## 3. The loop family this applies to

The family is **seven skills**, not five. The general ladder is `dev-loop-ultralight`, `dev-loop-lite`, `dev-loop` (full), `dev-loop-ultra`, `dev-loop-ultra-opus`. Alongside it sits a parallel Unity pair, `dev-loop-unity` and `dev-loop-unity-lite`, which are not rungs of the general ladder but variants of it. For every mechanism below, the Unity pair takes the treatment of its general-ladder equivalent:

| Unity loop | Equivalent to |
| --- | --- |
| `dev-loop-unity` | `dev-loop` (full) |
| `dev-loop-unity-lite` | `dev-loop-lite` |

There are three lane-card files, and a mechanism touching lane cards touches all three:

| Lane-card file | Used by |
| --- | --- |
| `dev-loop/references/review-lanes.md` | full, ultra, ultra-opus |
| `dev-loop-lite/references/review-lanes-lite.md` | lite |
| `dev-loop-unity/references/review-lanes-unity.md` | unity, unity-lite |

`dev-loop-ultralight` has **no lane-card file**. Its single reviewer sweeps a fixed list of concerns held in `reviewer-ultralight.md` itself, and its log records a verdict for every concern on that list including the ones it found nothing on. Any mechanism that adds a lane concern therefore adds it to that sweep rather than to a card, and the new concern must appear in the per-concern verdict list.

The Unity loops add no test reviewer of their own: `dev-loop-unity` reuses `reviewer-tests`, and `dev-loop-unity-lite` reuses `reviewer-lite-correctness`, `reviewer-lite-tests` and `reviewer-lite-structure`, all reading the Unity cards in place of the lite ones.

### 3.1 Phase naming — letters, not numbers

The two new phases are named **Phase P** (plan review) and **Phase D** (discharge audit), positionally rather than numerically, and the deferred-findings feed is a numbered **step inside the existing commit phase** rather than a phase of its own.

This is deliberate. Numeric sub-phase labels are already taken or absent in ways that make a single number impossible:

- `dev-loop-unity` already uses **Phase 0a** (art direction) and **Phase 0b** (inventory, primitives, harness), so the plan gate cannot be "Phase 0b".
- `dev-loop-ultralight` has no Phase 8 or 9 at all — its phases run 0, 1, 2, 3, 4, 5, 5b, 6, with commit at **Phase 6** — so the run audit cannot be "Phase 8c".

One letter per phase holds across all seven loops, survives future renumbering, and keeps the loops comparable, which is what the identical-formats rule exists to protect. Positions:

| New phase | Position |
| --- | --- |
| **Phase P** — plan review | Immediately after the framing phase (Phase 0 everywhere), before any implementation. |
| **Phase D** — discharge audit | Immediately after the walkthrough phase (8b, or 5b in ultralight), before the commit phase (9, or 6 in ultralight). |
| Deferred-findings feed | A numbered step inside the commit phase, after the PR is created. |

## 4. Mechanism 1 — `reviewer-plan`, new Phase P

**Rungs: full, ultra, ultra-opus, unity.** Not ultralight, lite, or unity-lite, whose eligibility criteria already bound the cost of a misframed brief.

A new read-only agent at `user/.claude/agents/reviewer-plan.md`, on **Opus** on every rung it runs on. It is the only lane that runs before any code exists, so it has no diff: its inputs are `brief.md`, the repository as it stands, `.claude/review/conventions.md`, and the `coding-standards` and `solution-architecture` skills.

It gets a Plan card in `review-lanes.md` (serving full, ultra and ultra-opus) and in `review-lanes-unity.md` (where the card states that only `dev-loop-unity` runs it, not `dev-loop-unity-lite`). No card is added to `review-lanes-lite.md`, since neither lite rung has the gate. Concerns it owns:

- **Completeness** — the requirement in plain language, explicit non-goals, named hard constraints, a definition of done naming the validation commands that must pass, and the source branch recorded.
- **Groundedness** — the files and entry points the brief names actually exist.
- **Loop fit** — whether the brief's own content satisfies the eligibility criterion the lead recorded for the loop it chose. A brief touching authentication under `dev-loop-lite` is a plan finding. This moves the escalation check ahead of the cost of discovering the misfit.
- **Unstated interpretation** — whether the brief has silently decided something the user did not say.
- **Anticipated `missing-required`** — whether the change implies a migration, a regenerated client or a lockfile change the brief does not mention. Catching this at plan time is strictly cheaper than the Artifacts lane catching it after implementation.
- **Size** — see mechanism 3.

### Output and schema

`plan-review.json` in the run directory root, not under `round-N/`, since it is not part of a review round. Plus `plan-review.log.md` in the standard reviewer log format.

It uses **the same findings schema as every other lane**, so runs stay comparable: `file` is `brief.md`, `line` is the line in the brief, `evidence` draws on the existing vocabulary (`direct` for read in the brief, `spec` for conflicts with the request, `missing` for something required and absent, `inferred`), and `cause` gains a fifth value, `plan-defect`.

### Failure behaviour

| Finding severity | Behaviour |
| --- | --- |
| Critical or Major | **Stop the run.** Present the findings. Do not enter the implementation phase. |
| Minor | The lead revises `brief.md` itself, records the revision in `notes.md`, and proceeds. No round-trip. |
| Empty | Silent. Straight to implementation. |

This keeps the attention cost of the gate at zero on a sound brief, which is the common case — their data has plans rejected under 10% of the time, and they still call plan review the highest-value check in the pipeline, because what it catches has not been built yet.

### Bound

**Two plan reviews per run, maximum.** The second is spent on one of:

- a brief the user told the lead to revise after a stop; or
- the "don't improvise" rule: if the triage phase accepts a requirements finding that redefines the definition of done, the brief is revised and the plan review re-runs.

A second rejection stops the run and reports. The loop does not iterate on plans.

`notes.md` records the plan review outcome either way, including a silent pass.

## 5. Mechanism 2 — `reviewer-discharge`, new Phase D

**All seven loops.** Its cost scales with the size of the run directory, so on `dev-loop-ultralight` it is nearly free — and a trust gate covering only the expensive runs leaves the cheap rungs unaudited, which is where corner-cutting is likeliest.

A new read-only agent at `user/.claude/agents/reviewer-discharge.md`, on **Sonnet**. It **reads the run directory and never the source diff.** Its card forbids code findings outright: a code concern it happens to notice belongs to another lane under one-owner-per-concern, and raising it here would reintroduce exactly the confusion the Discharge Nurse exists to avoid. It audits the run, not the change.

### Checks

1. Every `round-N/plan.md` exists and carries its `tree:` and `snapshot:` lines.
2. Every lane in every round is classified `applicable` or `skipped` with a reason.
3. **Every skip reason is a factual statement about what the diff does not touch**, verified against the changed-file list. "The code looks fine", or a reason that is not a statement about the diff, is a finding.
4. **The snapshot chain is unbroken**: each round's `snapshot:` is the next round's round base, up to the walkthrough-phase baseline. The commit comparison stays in the commit phase, which runs after this one.
5. **Every accepted finding in every `triage.md` has a corresponding change.** This is the headline check.
6. Every accepted finding with `would_have_been_bug: true` has a regression test, and the notes record it failing before the fix.
7. Every `wontfix.json` entry carries a reason and a classification.
8. **Rejection classifications are defensible on spot-check.** `rejected_wrong` is the only classification that counts against a lane, so misclassifying a wrong finding as `stale` or `remedy` hides lane drift.
9. Existing-test modifications are justified — see mechanism 4.
10. The walkthrough exists, or its skip reason is one of the permitted mechanical-change reasons and is recorded in both the PR description and `run.md`.
11. The exit condition the lead recorded actually holds.
12. Deferred findings were filed, or the cap was reached and recorded — see mechanism 6.
13. The `index.jsonl` line is true against the round files.

### Output and failure behaviour

`discharge.json` (standard findings schema, `file` being the run-directory file at fault) and `discharge.log.md`, with an explicit `verdict: pass | fail` line.

**A `fail` stops the run before the commit phase.** Nothing is committed or pushed. Where the failure is a record defect, the lead corrects the record and discharge re-runs once. Where the failure is check 5 — an accepted finding that was never fixed — the run returns to the fix phase, not forward.

### Accepted seam

The lead remains the sole author of its own `index.jsonl` line; discharge check 13 verifies it is true, which is most but not all of the fix. Having discharge author the line was considered and deliberately not taken, to keep a single writer for that file. This is recorded here so it is a known seam rather than an oversight.

## 6. Mechanism 3 — decomposition ceiling

**All seven loops**, enforced differently depending on whether the rung has a plan gate.

Default cap: **1,000 changed lines including tests**, matching the source article. The default is stated in each loop skill. A repository overriding it records the override in `.claude/review/conventions.md`, which is already the file for deliberate repository decisions deliberately accepted — no new configuration file is introduced.

### Two parties, so neither grades itself

- The **lead writes its line estimate into `brief.md`** at the framing phase.
- **`reviewer-plan` independently assesses whether that estimate is plausible** given the named files and the requirement, and raises a Major — which stops the run — when the estimate exceeds the cap or is implausibly low for what the brief describes. The finding names suggested sub-slices.

On rungs without a plan gate, only the measurement below applies.

### Measurement after the tests phase

The lead measures the actual change — `git diff --shortstat <base>` plus the line count of untracked files that will be staged — and records `lines_estimated` and `lines_actual` in `notes.md` and in the index line.

**A breach is recorded, not blocked.** The code already exists, killing the run wastes it, and the review lanes are what protect correctness. The value of the record is calibration: after a handful of runs the estimated/actual pair says whether to adjust the cap or stop trusting estimates, and neither question can be answered today.

## 7. Mechanism 4 — test integrity

**All seven loops.** The ladder already forbids weak *new* tests, by requiring each to fail against the pre-fix code. This closes the easier cheat: weakening an *existing* one.

- **Rule.** Weakening, skipping, deleting, or loosening an assertion in an existing test must be named and justified in the sidekick's returned reasoning and recorded as its own item in `notes.md`.
- **Lane ownership.** The Tests card in all three lane-card files gains existing-test modifications as an owned concern. **Unjustified weakening is Critical** — it is the one change that blinds every other gate in the loop.
- **Brief requirement.** The implement, tests and fix briefs gain an explicit line: you may not weaken, skip or delete an existing test to make a change pass; if a test is genuinely wrong, say so and stop. The line also goes into `sidekick.md`, `sidekick-heavy.md` and `sidekick-lite.md` as a standing rule, so it cannot be lost by a brief that forgets it. `sidekick-visual.md` is excluded — it builds scenes and art, not tests.
- **Audit.** `reviewer-discharge` check 9 cross-references existing-test modifications in the diff against justifications present in the notes.

In `dev-loop-ultralight` the concern joins `reviewer-ultralight.md`'s fixed sweep rather than a card, and must appear in that reviewer's per-concern verdict list so a silent omission is visible.

The article's "test changes must be separate, reviewed commits" does not transfer, because the unit of review here is the working tree rather than a commit series. The justification-in-notes requirement achieves the same end.

## 8. Mechanism 5 — I-PASS handoff

**All seven loops.** A new `user/.claude/skills/dev-loop/references/handoff.md`, referenced by all seven skills, so the format travels without growing seven skill bodies.

Required whenever:

- a sidekick returns blocked or wrong and the lead re-delegates the same brief;
- the lead escalates rung, per the one-way escalation table; or
- the loop-or-exit phase exits `blocked`.

Written to `handoff.md` in the run directory:

- **I** — illness severity: what is blocked and how badly (cannot proceed / proceeding degraded / cosmetic).
- **P** — patient summary: the requirement, the non-goals and the constraints, stated in the receiver's terms rather than referenced.
- **A** — action list: what has been tried, each with its outcome.
- **S** — situation awareness and contingency: what is likely wrong, what to try next, and what not to retry and why.
- **S** — synthesis by the receiver: **the receiving brief requires the agent to restate its understanding before editing anything.**

That last clause is the mechanism. Without it a handoff is only a longer brief, and the receiving agent inherits the sender's framing unexamined — which is how the same wrong approach gets attempted twice at two tiers.

The index line gains a `handoffs` count.

## 9. Mechanism 6 — deferred-findings feed, a step in the commit phase

**All seven loops**, as a numbered step at the end of the commit phase — after the PR exists, so each filed item can link to it. That is `dev-loop`'s Phase 9 and `dev-loop-ultralight`'s Phase 6.

Today `stale` and deferred-but-real findings go into the PR description and are never seen again.

- **Host detection** from `git remote get-url origin`: `github.com` uses `gh`, `dev.azure.com` or `visualstudio.com` uses the `ado-rest` skill, and anything else appends to `.claude/review/deferred.md` and says so in `run.md`.
- **Cap: five filed items per run**, by default. Beyond the cap the remainder stays in the PR description, and `run.md` plus the index record `deferred_filed` against `deferred_unfiled`. The cap ships from day one rather than being learned: the article's Research Department had to be throttled and backlog-capped because it generated more issues than the team could review, and many duplicated older ones.
- **Dedupe before filing**, matching on file plus concern against open items. A match comments on the existing item instead of filing a new one and counts as `deferred_deduped`.
- **Each filed item carries** the finding body, the run id, the owning lane, and a link to the PR. On GitHub it is labelled by severity (`bug` or `enhancement`); on Azure DevOps it takes the matching work-item type.

### Required rule amendment

This contradicts two rules currently in force, and the contradiction must be resolved in writing rather than left for a future run to resolve by guessing:

- `dev-loop`'s "Work tracker changes" section states that the loop does not create or change work items unless the user asked it to.
- `user/CLAUDE.md` states that being told to file a bug on one run is not authorisation to file bugs on the next.

Both gain an explicit, narrow carve-out: **filing deferred review findings at the end of the commit phase is standing authorisation, capped and deduped as specified, and nothing else about work-item handling changes.** In particular this does not authorise creating, closing or state-changing any other work item, and does not authorise merging.

## 10. Mechanism 7 — records branch

**All seven loops.** Plans, triage files, per-lane logs, handoffs, the plan review, the discharge verdict and `index.jsonl` are pushed to a `review-records` orphan branch.

Rationale: the per-lane `dropped` and `uncertain` log lines are what lane health is computed from, and they are exactly what dies today, since `.claude/review/runs/` is deliberately excluded from the commit and archived nowhere. An orphan branch works on any git host, so it covers the Azure DevOps repositories as well as GitHub, and it keeps PR diffs code-only.

The procedure gets its own reference file, `user/.claude/skills/dev-loop/references/records-branch.md`, following the precedent of `tree-snapshot.md`: the lead runs it, reviewers never do. The working-tree layout of `.claude/review/runs/` is unchanged, so no path in any skill moves; the records branch receives a copy at the end of the run. `.claude/review/conventions.md` continues to be committed with the change on the feature branch, because it is shared repository knowledge rather than run output.

## 11. Index format

All seven loops write these additions identically, so runs stay comparable:

```
"lines_estimated": N,
"lines_actual": N,
"plan_review": {"raised": N, "accepted": N, "rejected_wrong": N, "re_reviews": N},
"discharge": "pass" | "fail:<n>",
"deferred_filed": N,
"deferred_deduped": N,
"deferred_unfiled": N,
"existing_tests_modified": N,
"handoffs": N
```

On a rung with no plan gate, `plan_review` is omitted rather than zeroed, so a missing gate is distinguishable from a gate that found nothing.

## 12. Cascade summary

| Mechanism | ultralight | lite | full | ultra | ultra-opus | unity | unity-lite |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `reviewer-plan` (Phase P) | — | — | yes | yes | yes | yes | — |
| `reviewer-discharge` (Phase D) | yes | yes | yes | yes | yes | yes | yes |
| Ceiling: estimate + plan check | — | — | yes | yes | yes | yes | — |
| Ceiling: measure and record | yes | yes | yes | yes | yes | yes | yes |
| Test integrity | yes | yes | yes | yes | yes | yes | yes |
| I-PASS handoff | yes | yes | yes | yes | yes | yes | yes |
| Deferred feed (commit-phase step) | yes | yes | yes | yes | yes | yes | yes |
| Records branch | yes | yes | yes | yes | yes | yes | yes |
| Index additions | yes | yes | yes | yes | yes | yes | yes |

## 13. Files affected

**New:**

- `user/.claude/agents/reviewer-plan.md`
- `user/.claude/agents/reviewer-discharge.md`
- `user/.claude/skills/dev-loop/references/handoff.md`
- `user/.claude/skills/dev-loop/references/records-branch.md`

**Edited.** The seven loop skills are not uniform in how they are written, and the plan must respect that rather than inserting the same headings seven times:

| Skill | Shape | Edit needed |
| --- | --- | --- |
| `dev-loop` | Full phase bodies, 0–9 | Phase P and Phase D as new sections; ceiling, test integrity, handoff and records references; deferred-feed step in Phase 9; index additions; work-tracker carve-out. This is the canonical copy the others defer to. |
| `dev-loop-lite` | Full phase bodies, 0–9 | Phase D; ceiling measurement; test integrity; handoff and records references; deferred-feed step in Phase 9. No Phase P. |
| `dev-loop-ultralight` | Full phase bodies, 0–6 with 5b | Phase D between 5b and 6; ceiling measurement; deferred-feed step in Phase 6; handoff and records references. No Phase P. Its Formats section defers wholesale to `dev-loop`, so the index additions propagate with no edit there. |
| `dev-loop-ultra` | Phases 0–2 merged into one section | Phase P stated as a line in the merged "Phases 0 to 2" section, not a new heading; Phase D; the rest as `dev-loop`. |
| `dev-loop-ultra-opus` | Deltas only — no phase bodies | Index line section only. It inherits ultra's phases, so no phase edits. |
| `dev-loop-unity` | Deltas from `dev-loop`, with its own 0a and 0b | Phase P as a delta — **not** "0b", which is already inventory/primitives/harness; Phase D as a delta in the merged "Phase 8 / 8b / 9" section. |
| `dev-loop-unity-lite` | Deltas from `dev-loop-unity` | Phase D delta; no Phase P. |

- The three lane-card files: `review-lanes.md` and `review-lanes-unity.md` gain a Plan card (the Unity one stating that only the full Unity loop runs it); all three gain a Discharge card and the existing-test concern on the Tests card. `review-lanes-lite.md` gains no Plan card.
- The test reviewer agents: `reviewer-tests.md` (full, ultra, ultra-opus, unity) and `reviewer-lite-tests.md` (lite, unity-lite). `reviewer-ultralight.md` gains the concern in its fixed sweep and its per-concern verdict list. There is no separate Unity test reviewer.
- `sidekick.md`, `sidekick-heavy.md`, `sidekick-lite.md` — the test-integrity standing rule. Not `sidekick-visual.md`.
- `user/CLAUDE.md` — the work-tracker carve-out, and the loop table corrected from five loops to seven with the new phases named.
- `README.md` and `INSTALL.md` where either enumerates agents or phases.

**Unchanged:** every existing lane's concerns, the round bound, the triage gates, the two-scope rule, `conventions.md` semantics, and the model tiers of all existing agents.

## 14. Definition of done for Stage 1

- `reviewer-plan` and `reviewer-discharge` exist, are read-only in the same sense as the other reviewers, and are wired into the rungs named in section 12.
- A deliberately underspecified brief on a `dev-loop` run is stopped at Phase P with a Major, and the run does not reach implementation.
- A run whose `triage.md` records an accepted finding with no corresponding change is stopped at Phase D and returned to the fix phase.
- A run with a lane skipped for a non-factual reason is stopped at Phase D.
- Phase P and Phase D carry those labels in all seven skills, and neither collides with `dev-loop-unity`'s existing 0a and 0b or depends on a phase number `dev-loop-ultralight` does not have.
- All seven loops write the section 11 index fields, with `plan_review` omitted on the rungs that have no gate.
- A completed run's records are present on the `review-records` branch and absent from the PR diff.
- A run with more than five deferred findings files five, records the remainder, and dedupes a finding that matches an open item.
- A sidekick retry, a rung escalation and a `blocked` exit each produce a `handoff.md` in the I-PASS format, and the receiving brief demands a restatement before editing.
- `user/CLAUDE.md` and `dev-loop`'s work-tracker section no longer contradict the deferred-findings feed, and `user/CLAUDE.md`'s ladder table lists all seven loops.

## 15. Stage 2 — shape only, not specified here

Three candidate shapes, to be brainstormed on their own once Stage 1 is in:

- **A. Tracker-as-state-machine.** The faithful hospital: state in labels or tags, a scheduled pipeline polling and running the Stage 1 loop per patient, plus a charge-nurse watchdog and infection control locking on a red main. Highest autonomy; needs agent-capable CI with credentials and spend controls.
- **B. Local queue driver.** A `/dev-queue` skill reading a selection of work items — the `backlog-refinement` selection vocabulary already exists — and running loops back to back locally, paced by `/loop`. Cheap to build, keeps the human in the room, loses the round-the-clock property.
- **C. Hybrid, recommended.** Build B, but hold the state in the tracker from day one, so A becomes "run the same driver from a pipeline" rather than a rewrite.
