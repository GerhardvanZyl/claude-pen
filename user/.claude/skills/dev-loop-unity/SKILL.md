---
name: dev-loop-unity
description: >
  The full dev loop for Unity projects — dev-loop plus Unity batchmode
  validation and a Unity review lane. Use when asked for a Unity run, or when
  the user types /dev-loop-unity. For in-engine blockouts and visual
  prototypes use dev-loop-greybox.
---

# Development and review loop — Unity

**Follow the `dev-loop` skill in full.** Every phase, bound, format, and rule
is the same. This file changes five things and nothing else.

Read `dev-loop/SKILL.md` now and work from it. Do not reimplement its phases
from this file.

## Change 1 — Unity definition of done

`## Phase 0 — Frame the slice`

Read `references/unity-batchmode.md` before writing the brief. Definition of
done must include compile check, EditMode tests, and PlayMode tests all
passing. PlayMode may be recorded as `none present` only if the project has no
PlayMode assembly.

## Change 2 — Batchmode is the validation loop; no hand-edited scene YAML

`## Phase 1 — Implement` and `## Phase 6 — Fix`

Sidekick briefs name the batchmode commands in `references/unity-batchmode.md`
as the validation loop the sidekick must run, and forbid editing
`.unity`/`.prefab` YAML by hand wherever an editor script or the component API
would do the same job — hand edits to that YAML break `fileID` references.

## Change 3 — Test framework

`## Phase 2 — Tests`

Tests use the Unity Test Framework, not a generic test runner. Pure logic goes
in EditMode; anything needing frames, physics, or a loaded scene goes in
PlayMode.

## Change 4 — A Unity lane, and who owns Unity-flavoured artifacts

`## Phase 3 — Plan the review round` and `## Phase 4 — Delegate`

Add one row to the lane table:

| Agent | Lane | Applicable when |
| --- | --- | --- |
| `reviewer-unity` | Unity | Anything under `Assets/`, `Packages/`, or `ProjectSettings/` changed. |

When spawning `reviewer-artifacts`, append to its prompt: "`.meta`, `.unity`,
`.prefab`, `.asset`, and `.asmdef` files are owned by the Unity lane. You keep
`Packages/manifest.json`, `packages-lock.json`, and CI."

`reviewer-unity` counts toward Phase 4's four-at-a-time wave limit like every
other lane — it does not get a wave of its own. From round 2 onward it
receives both scopes — the change base and the round base — exactly as every
other lane does under "Two scopes, from round 2 onward"; nothing here changes
that.

## Change 5 — Escalation carries the Unity lane forward

`## Phase 5 — Triage`

Where triage surfaces one of `dev-loop`'s triggers for escalating to
`dev-loop-ultra` (a Critical in a lane the change was not expected to touch at
all, or the same Critical surviving a fix and recurring in a later round),
carry this file's five changes into the escalated run. `reviewer-unity` runs
there as a single reviewer — no adversarial prosecution/defence pair exists for
the Unity lane.

## Run identity

`notes.md` records `loop: dev-loop-unity`. The run's `loop` field in findings
and `index.jsonl` is `"loop":"unity"`, not `"loop":"full"`.
