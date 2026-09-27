---
name: dev-loop-unity
description: >
  The implement → test → multi-lane review → fix → PR loop for single-player
  Unity game development — scene composition, art direction from references,
  and gameplay systems together. Use when asked for a Unity loop, or when the
  user types /dev-loop-unity. Adds a Fable-driven Visual lane (an
  owner-approved exception) and drops the Security lane, since an eligible
  change has no reachable security surface. Not for a contained one-system or
  one-scene change with no settings/pipeline/package/asmdef change, no
  save-format change, no new shared primitive, and no new art direction — use
  dev-loop-unity-lite for that. Not for multiplayer, online services,
  accounts, purchases, analytics, downloaded or user-generated content, mod
  loading, or credentials — those go to the general dev-loop ladder.
---

# Development and review loop — Unity (single-player)

You are the lead. Same shape as `dev-loop` — frame → implement → tests → plan
→ parallel review lanes → triage → fix → loop → verify → walkthrough → PR —
with a Fable-driven Visual lane, Unity-specific phases, and Security dropped
because an eligible change cannot reach it. You still write no implementation
code yourself.

Lane definitions live in `references/review-lanes-unity.md`, shared with
`dev-loop-unity-lite`. Pass each reviewer the path and its card name; never
read the file whole.

Unity operating rules — editor isolation, batchmode, bridge CLIs, modal
dialogs, turn limits, scene-building lessons, the capture harness contract —
live in `references/unity-editor.md`. Read it in Phase 0 and hand it to every
sidekick and to the Visual lane.

The working-tree snapshot, the integrity check, and the scratch worktree the
Tests lane needs are shared with the general loop; follow
`dev-loop/references/tree-snapshot.md`.

**Everything this file does not restate is exactly `dev-loop`'s**: the
`implementation-notes` invocation at Phase 0 and the reasoning asked back in
every implement/test/fix brief, the `pr-walkthrough` / `pr-walkthrough-review`
pipeline at Phase 8b, the tree digest before and after reviewers, the evidence
and cause gates including `missing-required`, regression-test-before-fix,
findings/log/index formats, and the run log. Implementation and review conform
to the `coding-standards` and `solution-architecture` skills, the same as
every other loop.

## When this loop is the wrong one

**Eligibility, both Unity loops:** single-player, and the change touches none
of networking, multiplayer, online services, accounts, purchases,
analytics/personal data, downloaded or user-generated content, mod loading, or
credentials. If any of those hold, this is not a single-player change for
review purposes — use the general ladder (`dev-loop` or heavier), briefing
sidekicks with `references/unity-editor.md` regardless.

**Use `dev-loop-unity-lite` instead** when the change is contained: one
system or one scene, no settings/pipeline/package/asmdef change, no
save-format change, no new shared primitive, no new art direction.

**Escalation, one-way:**

- To `dev-loop-unity` from the lite loop: any Critical in round 1, or the
  change turns out to need art direction, a settings change, or a new shared
  primitive.
- To the general ladder, from either Unity loop: eligibility breaks mid-run.
- From `dev-loop-unity` itself: the same Critical surviving a fix is
  blocked — stop and report. No heavier Unity loop exists; say so and offer
  the general ladder.

## Phases (deltas from `dev-loop`)

### Phase 0 — Frame

As `dev-loop`, plus: read `references/unity-editor.md`; record which editor
instance belongs to this worktree and verify it against
`Application.dataPath` before the first command touches it. For visual scope,
the definition of done lists named shots — scene, camera, time of day — and
what each must *show*. A visual item is done when its shot shows the effect,
not when an object exists or a unit test passes.

### Phase 0a — Art direction (full loop only)

When the change has visual scope from references or a new look, hand it to
`sidekick-visual` before any building starts. It reads the references, the
game design doc, and the existing inventory, and writes or updates
`.claude/unity/scene-bible.md`: per reference, what makes it recognisable;
framing described by what the frame shows, not camera numbers alone; key
assets by exact name, verified to exist; lighting mood per time of day; which
gameplay or diegetic elements appear, from the design doc. One pass, no
building. `dev-loop-unity-lite` never runs this phase — a lite change needing
it means the wrong loop was chosen.

### Phase 0b — Inventory, primitives, harness (`sidekick`)

Before any building:

1. `.claude/unity/asset-inventory.md` — for every asset name the bible or
   brief uses: measured bounds, pivot, forward axis, variant materials the
   vendor already ships, and names that do not exist. Incremental — add only
   the missing entries.
2. Shared placement primitives, tested in EditMode: oriented-footprint
   clearance, spacing between agents, ground-height layering, camera-inside-
   geometry checks. Scene code places through them; no hand-rolled positions.
3. A capture harness honouring the contract in `references/unity-editor.md`.
   Skip any part that already exists and covers the need, and record the
   skip.

Both files under `.claude/unity/` are committed.

### Phase 1 — Implement, routed by kind

Code and systems go to `sidekick`, on the normal ladder. Scene composition,
lighting, framing, posing, and materials go to `sidekick-visual`: it builds,
captures, *looks at every capture*, fixes, at most two self-QA iterations per
handoff, one scene set per handoff. Both obey the reference; neither changes
project-wide rendering or settings unless the brief says so. Both briefs ask
for the reasoning back, same as `dev-loop`.

### Phase 2 — Tests

Unity Test Framework: EditMode for logic and primitives, PlayMode for frames,
physics, and loaded scenes. Visual outcomes are accepted by capture, not
unit-tested. Image-producing tooling needs no tests beyond the primitives it
calls.

### Phase 3 — Plan

Before the snapshot, `sidekick-lite` runs the capture harness for the brief's
shots into `round-N/captures/` — round 2 onward, affected shots only. Digest
the tree before and after capturing; if it moved, the harness has a side
effect — stop, that is a defect, not a review finding. Then follow
`dev-loop`'s snapshot and scratch-worktree setup exactly. The Tests lane's
scratch worktree needs its own editor opened on a copied `Library/`; never
more than two editors open at once. If a second editor cannot be opened,
mutation testing is unavailable this round — record it, do not improvise in
the primary tree.

Lane table:

| Agent | Lane | Applicable when |
| --- | --- | --- |
| `reviewer-visual` | Visual | Anything that renders changed — scenes, prefabs, materials, shaders, lighting, post-processing, cameras, animation, UI, VFX — or the brief names shots. Later rounds: reruns if it owned an accepted finding, or for the visual confirmation. |
| `reviewer-requirements` | Requirements | Always. |
| `reviewer-technical` | Technical | C# changed — runtime, editor, or test code. |
| `reviewer-tests` | Tests | C# changed — runtime, editor, or test code. |
| `reviewer-artifacts` | Artifacts | A settings, pipeline, package, asmdef, `.meta`, or scene/prefab YAML change — or should have been one. |
| `reviewer-lite-structure` | Structure | Round 1 only. Skipped for a throwaway tooling path recorded in `.claude/review/conventions.md` (capture or concept tooling whose output is images). |

### Phase 4 — Delegate

Wave limit of four, as `dev-loop`. Up to six lanes can apply; when more than
four do, split into two waves, Visual in the first. Give the Visual lane the captures directory, the
matching references, the bible, and the brief's shot list. Reviewers never
build, capture, enter play mode, or open an editor — only the Tests lane, and
only in scratch.

### Phase 5 — Triage

As `dev-loop`, plus: for a Visual finding, `file` is the capture path, `line`
is `0`, and the pixel region is stated in `finding`; `evidence: direct` means
seen in the capture. **Recurring-concern rule:** a concern raised in round 1
and again in round 2 is not patched in the scene a second time — its fix is
building or upgrading the shared primitive, with a regression test.

### Phase 6 — Fix

Code findings go to `sidekick` (or `sidekick-heavy`), test-before-fix as in
`dev-loop`. Visual findings go to `sidekick-visual`, which must recapture and
confirm by eye before returning.

### Phase 7 — Rounds capped at 2

After round 2's fixes, if any accepted finding was visual, run a **visual
confirmation**: recapture the affected shots, rerun only the Visual lane, and
ask only whether each fixed finding now shows as fixed. It raises nothing
new; a failure there is reported, not looped. Otherwise, termination follows
`dev-loop`'s Phase 7 rules.

### Phase 8 / 8b / 9 — Verify, walkthrough, ship

As `dev-loop`, plus verify also runs when the Artifacts lane ran this run or
a visual acceptance is unconfirmed, in addition to `dev-loop`'s own verify
triggers. Before staging: editor idle, scenes saved, every new asset's
`.meta` staged; never stage `Library/`, `Temp/`, `Logs/`, or `UserSettings/`;
commit `.claude/unity/*`. Captures stay in the run directory unless the
project already commits them. The index line carries `"loop":"unity"`.

## Agents

- **New, `sidekick-visual`** (`model: fable`) — the owner-approved Fable
  exception, confined to this agent and `reviewer-visual`. Roles: the bible
  (0a), visual build (1), visual fix (6). Fallback: on a usage-policy false
  positive (combat framed as game design still occasionally trips one), the
  lead retries once on `sidekick-heavy` and records it.
- **New, `reviewer-visual`** (`model: fable`) — the same exception, read-only
  like every other reviewer. Reads the `## Visual` card. Fallback: the lead
  re-spawns it with the model overridden to `opus`.
- **Reused, via `references/review-lanes-unity.md`:** `reviewer-requirements`,
  `reviewer-technical`, `reviewer-tests`, `reviewer-artifacts`,
  `reviewer-lite-structure`. `reviewer-verify` unchanged.

Every other agent, and every rule this file did not restate, is exactly
`dev-loop`'s.
