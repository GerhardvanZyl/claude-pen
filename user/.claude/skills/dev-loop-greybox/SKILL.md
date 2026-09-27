---
name: dev-loop-greybox
description: >
  The lite dev loop for in-engine Unity concept work — greybox/ProBuilder
  blockouts, placeholder materials, lighting mood — with rendered camera shots
  reviewed against an art brief. Use when asked for a greybox run, or when the
  user types /dev-loop-greybox. For Unity gameplay code use dev-loop-unity.
---

# Development and review loop — Unity greybox

**Follow the `dev-loop-lite` skill in full.** Every phase, bound, format, and
rule is the same. This file changes six things and nothing else.

Read `dev-loop-lite/SKILL.md` now and work from it. Do not reimplement its
phases from this file.

## Change 1 — The art brief

`## Phase 0 — Frame the slice`

`brief.md` additionally records: mood and reference, in words; scale (player
height, key dimensions); palette and lighting intent; and **named shots**, one
row per shot in a table with columns `Name`, `Camera position`, `Look target`,
`Must show`. Definition of done: compile check passes and every named shot
renders.

## Change 2 — Build the blockout and its shot cameras

`## Phase 1 — Implement`

The sidekick builds with ProBuilder or primitives, placeholder materials, and
lighting. For each named shot it places a camera named `Shot_<name>` —
**Camera component disabled, GameObject active.** If
`Assets/Editor/ShotCapture.cs` is absent, it copies it in from this skill's
`references/ShotCapture.cs` (editor-only; excluded from builds).

## Change 3 — Capture is a new step, run after Tests and after every Fix

`## Phase 2 — Tests` and `## Phase 6 — Fix`

After Phase 2, and again after every Phase 6 fix round, the lead runs the
*Shot capture* command from `dev-loop-unity/references/unity-batchmode.md`
into `round-N/shots/`. A missing PNG is a failed definition-of-done item, not a
review finding — it stops the round rather than being handed to a lane.

**No-GPU rule:** capture failing for lack of a graphics device stops the run
and reports the failure. It is never treated as a reason to skip the Visual
lane — the Visual lane is always run, and a run with no shots to review is a
blocked run, not a clean one.

## Change 4 — Two more lanes, and who owns Unity-flavoured artifacts

`## Phase 3 — Plan the round` and `## Phase 4 — Delegate`

Lite lanes apply as normal — Tests is typically `skipped — no logic added`,
Security typically `skipped — no input, secrets, or I/O`. Add two lanes,
always applicable in this loop:

| Agent | Lane | Model | Applicable when |
| --- | --- | --- | --- |
| `reviewer-unity` | Unity | `sonnet` (passed) | Always in this loop. |
| `reviewer-visual` | Visual | its own (opus) | Always in this loop. |

`reviewer-unity` reads the same card `dev-loop-unity` uses:
`dev-loop-unity/references/review-lanes-unity.md`, the Unity section.
`reviewer-visual` reads the Visual section of the same file.

Correctness's artifact concerns cede `.meta`/`.unity`/`.prefab`/`.asset`/`.asmdef`
to the Unity lane via the same spawn-prompt addendum `dev-loop-unity` uses for
`reviewer-artifacts`.

`dev-loop-lite`'s Phase 4 assumes its four lanes fit in a single batch, but
with Unity and Visual always applicable this loop can have up to six. Spawn
the applicable `dev-loop-lite` lanes as one batch and let it drain, then spawn
Unity and Visual as a second wave — and take the working-tree snapshot
comparison after the second wave drains, before triage.

This split is about batch size only. Every lane in both waves still receives
both scopes exactly as `dev-loop-lite`'s Phase 3/4 state for its own four
lanes — the change base always, and from round 2 the round base (the
`snapshot:` sha recorded in the previous round's `plan.md`). Applicability in
round 2 is still computed from the fix delta alone, per `dev-loop-lite`'s
Phase 3; a rerun `reviewer-unity` or `reviewer-visual` reviews the whole
change, not just the delta that made it applicable again.

## Change 5 — Escalation target

`### Escalation to the full loop` and `## When this loop is the wrong one`

Both of `dev-loop-lite`'s exits to `dev-loop` retarget to `dev-loop-unity`
instead: the round-1 Critical escalation, and the Phase 0 pre-flight check
that sends an out-of-scope change to the full loop before work starts —
full loop depth, plus the Unity lane, either way.

## Change 6 — Shots ship with the walkthrough

`## Phase 8b — Walkthrough`

The final round's shots are copied to `docs/walkthroughs/<slug>/shots/` and
embedded in the walkthrough. **Retake the working-tree snapshot after copying
them, not before** — they are new files under `docs/`, which is not
`.gitignore`d, so they change the digest exactly as the walkthrough file
itself does. Phase 9 compares against whichever snapshot was taken last; if
the shots are copied after that snapshot, the digest will not match the
commit and the run will stop for a reason that is not actually a problem.

## Run identity

`notes.md` records `loop: dev-loop-greybox`. The run's `loop` field in
findings and `index.jsonl` is `"loop":"greybox"`, replacing dev-loop-lite's
`"loop":"lite"`.
