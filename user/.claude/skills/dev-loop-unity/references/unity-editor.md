# Unity editor operating rules

Every Unity brief — implement, test, fix, or review — carries this file's
rules. They are generalised from a comparison run against real single-player
work; nothing here names a specific place, project, or vendor.

## Editor isolation

- One editor instance per worktree. Put the project path on every command
  that talks to an editor — never rely on "the" editor being the right one.
- Verify the target instance by reading `Application.dataPath` before the
  first command in a session touches it. A command sent to the wrong instance
  fails silently or edits the wrong project.
- Never more than two editors open at once (the primary worktree and, when
  the Tests lane needs mutation testing, a scratch worktree with its own
  copied `Library/`). A third editor is where memory and command routing
  start failing.
- Reviewers never drive the editor, build, capture, or enter play mode. Only
  the Tests lane may, and only inside its scratch worktree.

## Batchmode tests

A project already open in an editor cannot also be opened in batchmode — the
two fight over the same `Library/` lock. Run tests through the open editor's
test runner. Batchmode is only for the scratch worktree, which has its own
copied `Library/` and is not open anywhere else.

## Bridge CLIs

- Give every command an explicit timeout longer than an asset import can take
  — a default timeout will fire mid-import and look like a hang.
- One command at a time. Queuing several against one editor produces
  interleaved output that is worse than serial waiting.
- Snippet evaluators may silently ignore `using` directives and cannot see
  `internal` members. Where a snippet needs either, write a small editor
  script and run that instead of trusting the evaluator to resolve it.

## Modal dialogs

Never trigger one — a modal dialog hangs the editor at 0% CPU with no error.
Save scenes and assets with explicit paths so no "Save changes?" prompt can
appear unattended. If an editor shows 0% CPU and a log that stopped mid-line,
treat it as hung: kill the process and restart, and check for a stale
`.git/index.lock` left behind by the kill before running any git command.

## Turn limits

Cap scene-building work at one scene or system per handoff. An agent that
tries to do more in one turn tends to lose track of which capture belongs to
which fix, and self-QA quality drops as the turn count climbs.

## Usage-policy false positives

Combat, hazards, and other adversarial game-design elements occasionally trip
a usage-policy check when described in blunt terms. Describe them in
game-design language — encounter, obstacle, hazard, defeat condition — rather
than literal terms, and if a stop still happens, use the tier's stated
fallback rather than retrying the same brief unchanged.

## Scene-building rules

- **Measure, don't assume.** Read an asset's actual bounds, pivot, and
  forward axis before placing it; do not place from a guessed footprint. Cap
  placement-retry loops rather than letting one fail silently forever.
- **Surface heights are layered, not implicit.** Two coplanar surfaces
  z-fight; the fix is separating their heights, never a shadow or
  render-settings change.
- **Post-process volume profiles must be shared profiles with overrides
  persisted as sub-assets**, or they silently fail to save and the next load
  reverts to defaults.
- **Occluders block a shot's frontage.** Keep near-side geometry low or cut it
  away rather than fighting it with camera tricks.
- **Humanoid animation clips carry root motion.** Bake a pose by sampling the
  clip, then restore the root transform — otherwise root motion drags the
  character back toward the origin.
- **A light only counts where the capture shows it.** Do not accept "the
  light is in the scene" as done; the shot must show its effect.
- **Check vendor-shipped variants (colour, skin, wear) before building a
  custom system to produce the same effect.** The simplest solution is
  usually already in the package.
- **Pivots and orientation differ per asset pack.** Do not assume the last
  asset's convention holds for the next one — measure each.
- **Tooling never changes project-wide rendering settings** as a side effect
  of doing its job. If a change to those settings is genuinely needed, it is
  a brief-level decision, not something a capture or placement script does
  quietly.

## Capture harness contract

A capture harness, wherever the run's Phase 0b builds or reuses one, must:

- Take named shots — scene, camera, and time of day identify each one.
- Use a fixed resolution and be deterministic: the same shot run twice
  produces the same image.
- Write only to the directory it is given.
- Change no tracked file as a side effect of running.
- Use project settings as they already are; per-shot adjustments go through
  scene-local volumes or camera settings, never global ones.

## Stale locks

A killed editor or CLI process can leave `.git/index.lock` behind. If a git
command reports the index is locked and no editor process is actually
running, remove the stale lock file before retrying.
