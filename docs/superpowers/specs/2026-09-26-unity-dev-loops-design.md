# Unity dev loops — design

**Date:** 2026-09-26
**Branch:** `feat/unity-dev-loops`
**Status:** approved in conversation, awaiting written-spec review

## Goal

Add two loops for Unity projects:

1. **`dev-loop-greybox`** — game-dev concept art, meaning *in-engine* visual
   prototyping: greybox/ProBuilder blockouts, placeholder materials, shaders,
   lighting mood. Output merges through a PR like any other change.
2. **`dev-loop-unity`** — Unity game code at full-loop depth.

Verification runs through the Unity Editor CLI in batchmode: compile check,
Unity Test Framework (EditMode/PlayMode), and camera screenshots rendered to PNG.

## Non-goals

- Changing `dev-loop`, `dev-loop-lite`, or `dev-loop/references/review-lanes.md`.
  Unity is used rarely; the most-used skills carry nothing Unity-specific.
- Image generation, art briefs for external artists, or reviewing human-made art.
- A Unity MCP integration. Batchmode only.
- Unity variants of ultralight, ultra, or ultra-opus.
- draw.io diagrams for the new loops (add later if wanted).

## Approach: thin overrides

Both new skills follow the pattern `dev-loop-ultra-opus` already uses: *"Follow
`<base>` in full. This file changes N things and nothing else."* The base
loop's phases, findings format, triage rules, run log and index line are
inherited, so the global rule that every loop writes identical formats holds
without duplicating ~500 lines.

| New skill | Base | Why that base |
| --- | --- | --- |
| `dev-loop-unity` | `dev-loop` | Game code can carry migrations (save formats, Addressables) and cross-assembly changes; it gets full depth. |
| `dev-loop-greybox` | `dev-loop-lite` | Blockouts are scaffold, not shipping logic; code review stays shallow and the visual lane carries the weight. |

**Known coupling:** overrides name base-loop phase headings. A renamed heading
silently orphans an override. Mitigated by a contract assertion (below).

## Files

```
user/.claude/skills/dev-loop-unity/SKILL.md
user/.claude/skills/dev-loop-unity/references/unity-batchmode.md
user/.claude/skills/dev-loop-unity/references/review-lanes-unity.md   # Unity + Visual cards
user/.claude/skills/dev-loop-greybox/SKILL.md
user/.claude/skills/dev-loop-greybox/references/ShotCapture.cs
user/.claude/agents/reviewer-unity.md
user/.claude/agents/reviewer-visual.md
```

Also touched:

- `user/CLAUDE.md` — one line in the Development loop section:
  "Unity repos: `/dev-loop-unity` for code, `/dev-loop-greybox` for blockouts
  and visual prototypes. Both follow a base loop and override only what differs."
- `README.md` — two rows in the loops table, one short section.
- `install.sh`, `install.ps1` — agent/skill counts (22 → 24 agents; skill list).
- `tests/install-contract.sh`, `tests/install-contract.ps1` — count bump, plus an
  assertion that every `## Phase …` heading referenced by the two override files
  exists verbatim in its base `SKILL.md`.

## `unity-batchmode.md` (shared reference)

Read by the lead in both Unity loops; `dev-loop-greybox` references it by path
across skills.

**Locate the Editor**, in order:

1. `$UNITY_EDITOR` if set.
2. `m_EditorVersion` from `ProjectSettings/ProjectVersion.txt`, then
   `<Unity Hub editor root>/<version>/Editor/Unity.exe` (Windows default
   `C:\Program Files\Unity\Hub\Editor\`; macOS
   `/Applications/Unity/Hub/Editor/<version>/Unity.app/Contents/MacOS/Unity`).
3. Otherwise stop and ask the user. Never guess a different version.

**Before any batchmode run:** if `Temp/UnityLockfile` exists the project is
open in an Editor; batchmode will fail. Ask the user to close it.

**Commands** (all write logs into the run directory):

| Purpose | Command | Pass condition |
| --- | --- | --- |
| Compile check | `-batchmode -quit -projectPath <p> -logFile <run>/compile.log` | exit 0 |
| EditMode tests | `-batchmode -runTests -testPlatform EditMode -projectPath <p> -testResults <run>/editmode.xml -logFile <run>/editmode.log` | exit 0 |
| PlayMode tests | same with `PlayMode` / `playmode.xml` | exit 0 |
| Shot capture | `-batchmode -quit -projectPath <p> -executeMethod ShotCapture.Run -scene <path> -shotsOut <dir> -logFile <run>/capture.log` | exit 0, one PNG per `Shot_*` camera |

`-runTests` exits by itself; never add `-quit` to it. Shot capture must **not**
use `-nographics` — rendering needs a graphics device.

**Tests-lane scratch worktree:** a fresh worktree triggers a full `Library/`
reimport (minutes to hours). After creating the scratch worktree per
`dev-loop/references/tree-snapshot.md`, the lead copies `Library/` from the
main tree into it. `Library/` is gitignored and does not affect the tree digest.

## `dev-loop-unity` — changes to `dev-loop`

1. **Phase 0.** Read `references/unity-batchmode.md`. Definition of done must
   include compile check + EditMode + PlayMode passing (PlayMode may be recorded
   as `none present` only if the project has no PlayMode assembly).
2. **Phase 1 / Phase 6.** Sidekick briefs name the batchmode commands as the
   validation loop and forbid editing `.unity`/`.prefab` YAML by hand where an
   editor script or the component API would do (hand edits break fileID refs).
3. **Phase 2.** Tests use the Unity Test Framework. Pure logic → EditMode;
   anything needing frames, physics, or a loaded scene → PlayMode.
4. **Phase 3.** Add one lane to the table:

   | Agent | Lane | Applicable when |
   | --- | --- | --- |
   | `reviewer-unity` | Unity | Anything under `Assets/`, `Packages/`, or `ProjectSettings/` changed. |

   When spawning `reviewer-artifacts`, the lead appends to its prompt:
   "`.meta`, `.unity`, `.prefab`, `.asset`, and `.asmdef` files are owned by the
   Unity lane. You keep `Packages/manifest.json`, `packages-lock.json`, and CI."
5. **Escalation.** Where `dev-loop` escalates to `dev-loop-ultra`, carry this
   file's changes into it. The Unity lane runs as a single reviewer there (no
   adversarial pair exists for it).

## `dev-loop-greybox` — changes to `dev-loop-lite`

1. **Phase 0 — art brief.** `brief.md` additionally records: mood and
   reference in words; scale (player height, key dimensions); palette and
   lighting intent; and **named shots** — each with camera position, look
   target, and what the shot must show. Definition of done: compile check
   passes and every named shot renders.
2. **Phase 1.** Sidekick builds with ProBuilder or primitives, placeholder
   materials and lighting. For each named shot it places a disabled camera
   named `Shot_<name>`. If `Assets/Editor/ShotCapture.cs` is absent it copies
   it in from this skill's `references/` (editor-only; excluded from builds).
3. **Capture (new step, after Phase 2 and after every Phase 6).** The lead runs
   the shot-capture command into `round-N/shots/`. A missing PNG is a failed
   definition-of-done item, not a review finding.
4. **Phase 3.** Lite lanes apply as normal (Tests is typically
   `skipped — no logic added`; Security typically `skipped — no input,
   secrets, or I/O`). Add two lanes:

   | Agent | Lane | Model | Applicable when |
   | --- | --- | --- | --- |
   | `reviewer-unity` | Unity | `sonnet` (passed) | Always in this loop. |
   | `reviewer-visual` | Visual | its own (opus) | Always in this loop. |

   Unity lane card is the same card as `dev-loop-unity`'s. Correctness lane's
   artifact concerns cede `.meta`/`.unity`/`.prefab`/`.asset` to the Unity
   lane via the same spawn-prompt addendum.
5. **Escalation.** Where `dev-loop-lite` escalates to `dev-loop`, escalate to
   `dev-loop-unity` instead.
6. **Phase 8b.** Final-round shots are copied to
   `docs/walkthroughs/<slug>/shots/` and embedded in the walkthrough.

## `ShotCapture.cs`

One editor-only static class, no dependencies beyond `UnityEngine`/`UnityEditor`:

- Parses `-scene` and `-shotsOut` from `Environment.GetCommandLineArgs()`;
  missing either → log error, `EditorApplication.Exit(1)`.
- Opens the scene, finds every `Camera` whose GameObject name starts with
  `Shot_` (including inactive), renders each to a 1920×1080 `RenderTexture`,
  reads back, `EncodeToPNG`, writes `<shotsOut>/<name-without-prefix>.png`.
- Zero `Shot_` cameras → exit 1. Any exception → exit 1. Otherwise exit 0.

## Lane cards (`review-lanes-unity.md`)

Same three-part shape as `review-lanes.md`.

**Unity**

- **Owns:** serialized data loss (renamed/moved `[SerializeField]` or public
  field without `[FormerlySerializedAs]`, changed type of a serialized field);
  asset-database integrity (missing `.meta`, GUID changed on move, orphaned
  `.meta`); broken fileID/GUID references in `.unity`/`.prefab`/`.asset` YAML;
  `.asmdef` references and platform constraints; lifecycle-order dependence
  (`Awake`/`OnEnable`/`Start`, script execution order); Unity API calls off the
  main thread; per-frame allocations and `Find`/`GetComponent` in
  `Update`/`FixedUpdate`/`LateUpdate`; `UnityEditor` APIs in runtime assemblies;
  `== null` misuse on destroyed `UnityEngine.Object`s.
- **Does not own:** general logic defects (technical / correctness), naming
  (standards), visual result (visual), package manifests and CI (artifacts).
- **Quality brake:** a per-frame allocation is only a finding if the code runs
  every frame in a shipping path — not in an editor tool, a one-off `Start`, or
  a greybox placeholder script. Serialized-field findings must name the asset
  that would lose data, or be marked `low`.

**Visual**

- **Owns:** a brief element missing or wrong in a shot; scale contradicting the
  brief; a shot whose framing does not show what the brief says it must;
  lighting or palette contradicting stated intent; a shot that failed to
  communicate its purpose (e.g. key object occluded, unlit, off-frame).
- **Does not own:** code, assets' internal structure, anything not visible in
  the PNGs.
- **Quality brake:** every finding quotes the brief line it violates. "Would
  look better", taste, and polish beyond greybox fidelity are not findings. A
  brief that never stated the thing you want is a finding against the brief,
  not the shot.

## Agents

| Agent | Model | Effort | Tools | Notes |
| --- | --- | --- | --- | --- |
| `reviewer-unity` | opus | high | as other lane reviewers | Same `disallowedTools` block as `reviewer-technical`. Reads its card from `dev-loop-unity/references/review-lanes-unity.md`. |
| `reviewer-visual` | opus | high | Read, Grep, Glob, Write | Reads PNGs with `Read`. Needs no shell. Writes only findings/log in the run dir. |

Both write the standard findings and log format, so runs stay comparable.

## Testing

- Contract tests: counts updated; phase-heading assertion added and shown to
  fail when a referenced heading is renamed, then pass.
- `ShotCapture.cs` cannot be exercised without a Unity install in CI. It is
  verified manually once against a scratch Unity project and the result is
  recorded in the walkthrough. Stated as a known gap.

## Risks

- **Batchmode GPU:** headless machines without a GPU cannot capture shots. The
  greybox loop stops and reports rather than skipping the Visual lane.
- **Editor lock:** handled by the lockfile check; costs one user prompt.
- **Base-loop drift:** covered by the heading assertion; content drift inside a
  phase is not caught and is accepted.
