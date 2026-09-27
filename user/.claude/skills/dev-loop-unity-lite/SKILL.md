---
name: dev-loop-unity-lite
description: >
  The lightweight Unity loop for a contained single-player change — one
  system or one scene, no settings/pipeline/package/asmdef change, no
  save-format change, no new shared primitive, no new art direction. Use when
  asked for a lite Unity run, or when the user types /dev-loop-unity-lite.
  Four consolidated lanes including a Fable-driven Visual lane (an
  owner-approved exception), two rounds plus a visual confirmation. Escalates
  to dev-loop-unity on a round-1 Critical, or when the change turns out to
  need art direction, a settings change, or a new shared primitive.
---

# Development and review loop — Unity lite (single-player)

Same shape as `dev-loop-unity`, fewer lanes, tighter bounds. You still write
no implementation code yourself.

Lane definitions live in
`dev-loop-unity/references/review-lanes-unity.md`, shared with the full
Unity loop. Unity operating rules live in
`dev-loop-unity/references/unity-editor.md` — read it in Phase 0 and hand it
to every sidekick and to the Visual lane. The working-tree snapshot, the
integrity check, and the scratch worktree the Tests lane needs are shared
with the general loop; follow `dev-loop/references/tree-snapshot.md`.

**Everything this file does not restate is exactly `dev-loop-unity`'s**,
which is in turn exactly `dev-loop`'s except where its own file states a
delta: implementation and review conform to `coding-standards` and
`solution-architecture`; notes (`implementation-notes` at Phase 0, reasoning
asked back in every implement/test/fix brief) and the walkthrough
(`pr-walkthrough` / `pr-walkthrough-review` at Phase 8b); the tree digest
before and after reviewers; the evidence and cause gates, including
`missing-required`; regression-test-before-fix; identical findings, log, and
index formats; and the run log.

## When this loop is the wrong one

**Eligibility, shared with `dev-loop-unity`:** single-player, and the change
touches none of networking, multiplayer, online services, accounts,
purchases, analytics/personal data, downloaded or user-generated content,
mod loading, or credentials. If any hold, use the general ladder instead,
briefing sidekicks with `unity-editor.md` regardless.

This loop is additionally the wrong one, even within single-player scope, if
the change is not contained: new scenes or a look built from references, a
settings/pipeline/package/asmdef change, a save-format change, a new shared
primitive, or multi-system work. Use `dev-loop-unity` for any of those.

**Escalation, one-way:**

- To `dev-loop-unity`: any Critical in round 1; or the change turns out to
  need art direction, a settings change, or a new shared primitive.
- To the general ladder: eligibility breaks mid-run.

If you are unsure, use the full Unity loop. This loop's savings are not
worth a missed Critical, exactly as `dev-loop-lite` is to `dev-loop`.

## Lite limits

- No Phase 0a art-direction pass — this loop never builds a look from
  references; needing one means the wrong loop.
- No Phase 0b shared-primitive authoring beyond what already exists — a
  change that needs a new primitive is not contained.
- At most 4 lanes: Visual, Correctness, Tests, Structure (round 1 only).
- 2 rounds, plus one visual confirmation after round 2 if any accepted
  finding was visual.
- Verify only after a Critical, or a Major with `would_have_been_bug: true`.
  Narrower than the full loop's triggers, because this loop has no Artifacts
  lane and a visual acceptance either confirms clean or escalates.

## Phases (deltas from `dev-loop-unity`)

### Phase 0 — Frame

As `dev-loop-unity`: read `unity-editor.md`, verify the editor instance,
record capture-level acceptance for any visual item.

### Phase 1 — Implement

As `dev-loop-unity`, routed by kind: `sidekick` for code, `sidekick-visual`
(Fable) for scene composition, lighting, framing, posing, materials — same
turn limits and self-QA cap. No Phase 0a or 0b here; the inventory and
primitives this change needs must already exist.

### Phase 2 — Tests

As `dev-loop-unity`: Unity Test Framework, EditMode/PlayMode split, visual
outcomes accepted by capture, not unit-tested.

### Phase 3 — Plan

`sidekick-lite` runs the capture harness for the brief's shots into
`round-N/captures/` before the snapshot, exactly as the full loop, with the
same before/after digest check. Lane table:

| Agent | Lane | Applicable when |
| --- | --- | --- |
| `reviewer-visual` | Visual | Anything that renders changed — scenes, prefabs, materials, shaders, lighting, post-processing, cameras, animation, UI, VFX — or the brief names shots. Later rounds: reruns if it owned an accepted finding, or for the visual confirmation. |
| `reviewer-lite-correctness` | Correctness | Always — reads the `## Correctness` card in `review-lanes-unity.md`. |
| `reviewer-lite-tests` | Tests | C# changed — runtime, editor, or test code. |
| `reviewer-lite-structure` | Structure | Round 1 only. Skipped for a recorded throwaway tooling path. |

Four lanes fit one wave — no waves needed, as `dev-loop-lite`.

### Phase 4 — Delegate

One batch, as `dev-loop-lite`. Give the Visual lane the captures directory,
matching references, the bible if one exists, and the brief's shot list.

### Phase 5 — Triage

As `dev-loop-unity`: a Visual finding uses the capture path as `file`,
`line: 0`, the pixel region in `finding`. The recurring-concern rule applies
identically. This loop has no separate Requirements lane —
`reviewer-lite-correctness` owns conformance to the brief; its
brief-related findings go into `notes.md` whether accepted or rejected,
exactly as `dev-loop-lite`.

### Phase 6 — Fix

As `dev-loop-unity`: code findings to `sidekick` or `sidekick-heavy`,
test-before-fix; visual findings to `sidekick-visual`, which recaptures and
confirms by eye before returning.

### Phase 7 — Loop or exit

Rounds capped at 2, as `dev-loop-lite`. After round 2's fixes, if any
accepted finding was visual, run the visual confirmation described in
`dev-loop-unity`'s Phase 7. A repeat Critical or no material progress is
blocked — stop and report, per `dev-loop-lite`'s termination rules.

### Phase 8 — Verify

Per Lite limits above: only after a Critical, or a Major with
`would_have_been_bug: true`.

### Phase 8b / 9 — Walkthrough, ship

As `dev-loop-unity`. Before staging: editor idle, scenes saved, `.meta`
staged for every new asset; never stage `Library/`, `Temp/`, `Logs/`, or
`UserSettings/`; commit `.claude/unity/*` if present. The index line carries
`"loop":"unity-lite"`.

## Agents

Same two Fable agents as `dev-loop-unity` — `sidekick-visual` and
`reviewer-visual` — the same owner-approved exception, with the same
fallbacks (`sidekick-heavy` on a usage-policy false positive; `reviewer-visual`
re-spawned on `opus` if it needs one). Reused lanes:
`reviewer-lite-correctness`, `reviewer-lite-tests`, `reviewer-lite-structure`,
all reading `review-lanes-unity.md` in place of `review-lanes-lite.md`.
