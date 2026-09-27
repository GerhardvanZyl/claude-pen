# Review lanes — Unity

One file shared by `dev-loop-unity` and `dev-loop-unity-lite`. A reviewer
reads **only its own card** — never the whole file — plus the slice context
the lead provides. Same three-part shape as the other loops' cards:

- **Owns** — raise these.
- **Does not own** — you will notice some of these. Say nothing; another lane
  has them.
- **Quality brake** — the specific way this lane goes wrong. Read it twice.

There is no Security card. Both Unity loops are eligible only for
single-player changes that touch no networking, accounts, purchases,
analytics, downloaded content, or credentials — the surface Security exists
to cover is not reachable by an eligible change.

---

## Visual

*Fable lane. Not merged in either loop.*

- **Owns:** Likeness to the reference and to `.claude/unity/scene-bible.md`;
  framing — what the frame actually shows; readability per time of day;
  clipping, floating, or intersecting objects; T-poses and other broken
  poses; fused characters; z-fighting; black or washed-out frames; lights not
  reaching the framed core; missing post-processing or grading.
- **Does not own:** Whether the settings behind the image are saved
  correctly or safe to ship (Artifacts); whether the scene fulfils the
  brief's non-visual requirements (Requirements); whether the code compiles
  or the tests pass (Technical, Tests).
- **Quality brake:** Every finding cites a capture and a pixel region.
  Compare against the reference and the bible, not taste. "Fixed" means
  visible in a fresh capture, not that a fix was applied. Do not raise
  anything an image cannot show — code, settings, or intent live in other
  lanes' captures, not this one.

## Requirements

- **Owns:** Mismatch between the change and the brief — missing
  requirements, unmet definition-of-done items, unrequested scope, and
  interpretations taken on the user's behalf where the brief was ambiguous.
  For visual scope, the definition of done is the named shot list and what
  each must *show* — a capture existing is not the requirement met.
- **Does not own:** Whether a shot actually shows what it claims to (Visual),
  code correctness (Technical), whether tests exist (Tests).
- **Quality brake:** Form your expectation from the brief before reading the
  diff or the captures. Point at the line, or the named shot, that satisfies
  each requirement; one you cannot point at is missing. A brief that is
  incomplete or self-contradictory is itself a legitimate finding.

## Technical

- **Owns:** Demonstrable incorrect behaviour caused by this diff — logic
  errors, state and lifetime bugs, boundary handling, error paths — plus
  Unity lifecycle defects: execution order, missing `OnDisable`/`OnDestroy`
  cleanup, coroutines left running on inactive objects, allocation in
  per-frame paths, a serialized-field rename that loses data without
  `FormerlySerializedAs`, a save-data format change without backward
  compatibility, and an edit-time script writing an asset that was meant to
  stay transient.
- **Does not own:** Where responsibility sits (Structure), visual fidelity
  (Visual), project-wide settings and generated files themselves (Artifacts).
- **Quality brake:** State the defect and its trigger separately from the
  remedy; a defect with no describable trigger is a suspicion — mark
  confidence `low` or drop it. Prefer the narrowest fix. An edit-time write
  to a tracked asset is a finding regardless of whether the write looks
  harmless this time.

## Tests

- **Owns:** Whether EditMode versus PlayMode fits what is being tested;
  whether the tests would fail if the code were wrong; coverage of the
  behaviours named in the brief; assertion quality; missing negative cases.
  Tests must never write to production scenes, prefabs, or other tracked
  assets. Mutation testing only in the lead's scratch worktree, with its own
  editor.
- **Does not own:** The underlying defect the tests fail to catch
  (Technical); visual outcomes, which are accepted by capture, not a unit
  test (Visual).
- **Quality brake:** The question is "would it fail if the code were wrong",
  not "does a test exist". A test that writes to a tracked asset instead of a
  temporary scene is Major regardless of whether it passes. With no second
  editor available for the scratch worktree, mutation testing is
  `unavailable` — record that; do not improvise a mutation in the primary
  tree.

## Artifacts

- **Owns:** `ProjectSettings/`, render-pipeline and quality assets,
  `Packages/manifest.json` and its lock, `.asmdef` files, missing or
  unexpectedly regenerated `.meta` files (GUID churn), vendor import-setting
  changes, hand-edited scene or prefab YAML, and any project-wide rendering
  change made as a side effect of tooling rather than a stated brief
  decision.
- **Does not own:** The visual result these settings produce (Visual); the
  logic that consumes them (Technical).
- **Quality brake:** Run a generate-and-diff or asset-reimport check where
  one exists rather than reasoning about currency. A project-wide settings
  change with no brief authorization is Critical even if the resulting image
  looks fine — Visual cannot see a settings file and will not raise it.

## Structure

*Round 1 only, in both loops. Skipped for a throwaway tooling path recorded in
`.claude/review/conventions.md` — for example, capture or concept tooling
whose only output is images.*

- **Owns:** Separation of concerns first — a type or method holding
  responsibilities that belong apart. Then architecture (placement,
  dependency direction, conformance to the established pattern), coding
  standards, speculative additions nothing requires, dead code, and
  MonoBehaviour god objects or scene-manipulation logic embedded in editor
  tooling that should be a plain method.
- **Does not own:** Whether the code works (Technical/Correctness), visual
  fidelity (Visual), test structure (Tests).
- **Quality brake:** Establish the architecture in force using the tier
  procedure in `solution-architecture` before judging placement; a
  convention inferred from examples can never be a blocker. Never propose a
  new pattern, layer, or abstraction to fix a local problem. Check
  `.claude/review/conventions.md` first. Round-1-only means a repeated
  concern is not re-raised here in round 2 — see the recurring-concern rule
  in the skill's Phase 5; upgrading it into a shared primitive is a
  Technical or Requirements finding by then, not a fresh Structure one.

## Correctness

*Lite loop only. Merges Requirements, Technical, and Artifacts above.*

- **Owns:** All three concerns as the full-loop cards above define them —
  brief conformance including the named-shot definition of done; logic,
  state, and Unity lifecycle defects; and project settings, packages,
  `.asmdef`, `.meta`, and hand-edited scene/prefab YAML.
- **Does not own:** Visual fidelity (Visual), whether the code is shaped
  well (Structure), whether tests would catch a regression (Tests).
- **Quality brake:** Cover all three concerns before writing anything — the
  characteristic failure of a merged lane is finding one interesting problem
  and stopping. Run the generate-and-diff or reimport check where one
  exists. State each defect's trigger separately from its remedy, and prefer
  the narrowest fix.
