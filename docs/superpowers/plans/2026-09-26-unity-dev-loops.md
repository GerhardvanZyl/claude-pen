# Unity dev loops Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `dev-loop-unity` and `dev-loop-greybox` as thin overrides of `dev-loop` and `dev-loop-lite`, with two new reviewer agents and a batchmode shot-capture script.

**Architecture:** Each new skill says "follow `<base>` in full" and lists only its changes, the pattern `dev-loop-ultra-opus/SKILL.md` already uses. Shared Unity knowledge (batchmode commands, the two lane cards) lives under `dev-loop-unity/references/`; greybox references it by path. Base loops are not edited.

**Tech Stack:** Markdown skills/agents for Claude Code; one C# editor script (Unity 6, `UnityEditor` only); bash test.

**Spec:** `docs/superpowers/specs/2026-09-26-unity-dev-loops-design.md` — every task reads the spec section it names; content lives there, not duplicated here.

## Global Constraints

- `user/.claude/skills/dev-loop/`, `user/.claude/skills/dev-loop-lite/`, and `dev-loop/references/review-lanes.md` are **not modified**. `git diff main -- user/.claude/skills/dev-loop user/.claude/skills/dev-loop-lite` must be empty at the end.
- Overrides quote every base-loop heading they refer to as a backticked literal line, e.g. `` `## Phase 3 — Plan the review round` ``. That is the contract the heading test checks.
- New agents copy the frontmatter shape of `user/.claude/agents/reviewer-technical.md`, including its full `disallowedTools` list (reviewer-unity) — reviewer-visual has `tools: Read, Grep, Glob, Write` and `disallowedTools: [Edit, NotebookEdit]`.
- Findings and log formats: the base loop's, unchanged. File names `round-N/unity.json`, `round-N/unity.log.md`, `round-N/visual.json`, `round-N/visual.log.md`.
- No new dependencies. Tests are plain bash per `tests/install-contract.sh` header convention.
- Agent count 22 → 24. Skill label "5 loops" → "7 loops".
- Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

**Deviation from spec (deliberate):** the heading assertion goes in a new `tests/override-headings.sh` rather than inside the install-contract scripts — it checks skill content, not installer behaviour, and the install contract's temp-HOME setup is irrelevant to it. One bash script; Git Bash covers Windows.

## Review Focus

1. **Disabled camera vs inactive GameObject** — a `Shot_` camera whose *GameObject* is inactive may not render; ShotCapture must render cameras whose component is disabled, and the greybox Phase 1 brief must say "Camera component disabled, GameObject active". Pinned in Task 4 verification (scene contains one disabled-component camera).
2. **Duplicate shot names** — two `Shot_Hero` cameras would silently overwrite one PNG. ShotCapture fails with exit 1. Pinned in Task 4.
3. **Prefab-asset cameras** — `Resources.FindObjectsOfTypeAll` returns cameras inside prefab assets too; only scene objects count. Pinned in Task 4 (filter on `gameObject.scene.IsValid()`).
4. **Heading test false pass** — a test that finds zero quoted headings passes vacuously. It must fail when an override quotes no headings. Pinned in Task 1.
5. **Editor already open** — batchmode against a locked project fails with an obscure log. `unity-batchmode.md` must put the `Temp/UnityLockfile` check before every command. Pinned by Task 2's content checklist.

---

### Task 1: Override heading contract test

**Files:**
- Create: `tests/override-headings.sh`

**Interfaces:**
- Produces: the convention every later task follows — each override `SKILL.md` quotes base headings as `` `## …` `` lines.

- [ ] **Step 1: Write the test**

```bash
#!/usr/bin/env bash
# Every base-loop heading an override skill quotes (as a backticked `## ...`
# literal) must exist verbatim in the base skill. Catches a renamed phase in
# dev-loop / dev-loop-lite silently orphaning dev-loop-unity / dev-loop-greybox.
# Convention: plain bash, one line per assertion, exit non-zero on first failure.
set -euo pipefail
SKILLS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/user/.claude/skills"
ASSERTIONS=0

check() {
  local override="$SKILLS/$1/SKILL.md" base="$SKILLS/$2/SKILL.md" found=0
  [ -f "$override" ] || { echo "FAIL: $1 -- missing $override" >&2; exit 1; }
  while IFS= read -r heading; do
    found=$((found + 1))
    if grep -qxF "$heading" "$base"; then
      ASSERTIONS=$((ASSERTIONS + 1)); echo "PASS: $1 -> $2: $heading"
    else
      echo "FAIL: $1 quotes '$heading', not a heading in $2/SKILL.md" >&2; exit 1
    fi
  done < <(grep -oE '`##+ [^`]+`' "$override" | tr -d '`' | tr -d '\r' | sort -u)
  [ "$found" -gt 0 ] || { echo "FAIL: $1 quotes no $2 headings -- test would pass vacuously" >&2; exit 1; }
}

check dev-loop-unity dev-loop
check dev-loop-greybox dev-loop-lite
echo "OK: $ASSERTIONS assertions"
```

- [ ] **Step 2: Run it, expect FAIL**

Run: `bash tests/override-headings.sh`
Expected: `FAIL: dev-loop-unity -- missing .../dev-loop-unity/SKILL.md`, exit 1.

- [ ] **Step 3: Commit**

```bash
git add tests/override-headings.sh
git commit -m "Add override heading contract test"
```

### Task 2: Shared Unity references and the two reviewer agents

**Files:**
- Create: `user/.claude/skills/dev-loop-unity/references/unity-batchmode.md`
- Create: `user/.claude/skills/dev-loop-unity/references/review-lanes-unity.md`
- Create: `user/.claude/agents/reviewer-unity.md`
- Create: `user/.claude/agents/reviewer-visual.md`

**Interfaces:**
- Produces: card headings `## Unity` and `## Visual` in `review-lanes-unity.md`; agent names `reviewer-unity`, `reviewer-visual`; batchmode command table rows named *Compile check*, *EditMode tests*, *PlayMode tests*, *Shot capture*.

- [ ] **Step 1: Write `unity-batchmode.md`** from spec section "`unity-batchmode.md` (shared reference)", complete: Editor lookup order (env var, `ProjectVersion.txt` → Hub path for Windows and macOS, else stop and ask), the lockfile check stated as a precondition of **every** command, the four-row command table with pass conditions, the `-runTests`/`-quit` and `-nographics` warnings, and the Tests-lane `Library/` copy (`cp -r <main>/Library <scratch>/Library` after the scratch worktree is created). Add: on non-zero exit, the lead reads the tail of the named log file and hands the error lines to the fix sidekick — never retries blind.

- [ ] **Step 2: Write `review-lanes-unity.md`** — header paragraph copied in spirit from `dev-loop/references/review-lanes.md` lines 1–17 (one card per lane, read only your own, Owns / Does not own / Quality brake), then the **Unity** and **Visual** cards verbatim from spec section "Lane cards".

- [ ] **Step 3: Write `reviewer-unity.md`** — copy `reviewer-technical.md` exactly, then change: `name`, `description` ("Review lane \"Unity\" for dev-loop-unity and dev-loop-greybox. Engine-specific defects: serialization, asset-database integrity, scene/prefab references, lifecycle, threading, per-frame cost. …"), `model: opus`, `effort: high`, lane name everywhere, card path `dev-loop-unity/references/review-lanes-unity.md` section `## Unity`, output files `unity.json` / `unity.log.md`. Step 4 of its procedure becomes: for each changed `.cs` field with serialization attributes, grep `Assets/` for assets whose YAML references that field name; for each added/moved asset, check the `.meta` exists and its `guid:` is unchanged (`git diff -M` shows rename pairs).

- [ ] **Step 4: Write `reviewer-visual.md`** — same body structure, `model: opus`, `effort: high`, `tools: Read, Grep, Glob, Write`, `disallowedTools: [Edit, NotebookEdit]`. Procedure: read card `## Visual`; read `<run>/brief.md` art-brief section **before** opening any PNG; `Read` each `round-N/shots/*.png`; for each named shot in the brief, one verdict line in the log (meets / finding / missing PNG); write `visual.json` / `visual.log.md`. Every finding's `evidence` quotes the brief line. Same "Rules for every lane" block and one-line return.

- [ ] **Step 5: Verify content** — `grep -n "UnityLockfile" unity-batchmode.md` shows it before the command table; `grep -c "^## " review-lanes-unity.md` → 2; `diff <(sed -n '/disallowedTools/,/^color/p' user/.claude/agents/reviewer-technical.md) <(sed -n '/disallowedTools/,/^color/p' user/.claude/agents/reviewer-unity.md)` empty.

- [ ] **Step 6: Commit** — `git add` the four files; message "Add Unity batchmode reference, Unity and Visual lanes".

### Task 3: `dev-loop-unity` skill

**Files:**
- Create: `user/.claude/skills/dev-loop-unity/SKILL.md`

**Interfaces:**
- Consumes: Task 2's reference paths and agent names; base headings from `user/.claude/skills/dev-loop/SKILL.md`.

- [ ] **Step 1: Write the skill.** Frontmatter `name: dev-loop-unity`, description: "The full dev loop for Unity projects — dev-loop plus Unity batchmode validation and a Unity review lane. Use when asked for a Unity run, or when the user types /dev-loop-unity. For in-engine blockouts and visual prototypes use dev-loop-greybox." Body opens like `dev-loop-ultra-opus`: "**Follow the `dev-loop` skill in full.** … This file changes five things and nothing else. Read `dev-loop/SKILL.md` now." Then one `## Change N` section per spec item in "`dev-loop-unity` — changes to `dev-loop`", each naming the base heading it modifies as a backticked literal line:
  - Change 1 → `` `## Phase 0 — Frame the slice` ``
  - Change 2 → `` `## Phase 1 — Implement` `` and `` `## Phase 6 — Fix` ``
  - Change 3 → `` `## Phase 2 — Tests` ``
  - Change 4 → `` `## Phase 3 — Plan the review round` `` (lane table row + the exact Artifacts addendum sentence from the spec) and `` `## Phase 4 — Delegate` `` (reviewer-unity counts toward the four-at-a-time wave limit)
  - Change 5 → escalation, citing `` `## Phase 5 — Triage` ``
  Plus: notes.md records "loop: dev-loop-unity"; the run's `loop` field in findings/index is `dev-loop-unity`.

- [ ] **Step 2: Run heading test** — `bash tests/override-headings.sh`. Expected: PASS lines for dev-loop-unity, then `FAIL: dev-loop-greybox -- missing …` (Task 4 not done). That partial pass is correct.

- [ ] **Step 3: Prove the test catches drift** — temporarily change one quoted heading in the new SKILL.md to `` `## Phase 3 — Plan the round` ``, run the test, expect `FAIL: dev-loop-unity quotes '## Phase 3 — Plan the round'`. Revert.

- [ ] **Step 4: Commit** — "Add dev-loop-unity override skill".

### Task 4: `ShotCapture.cs` and `dev-loop-greybox` skill, verified in a real Unity project

**Files:**
- Create: `user/.claude/skills/dev-loop-greybox/references/ShotCapture.cs`
- Create: `user/.claude/skills/dev-loop-greybox/SKILL.md`
- Scratch (not committed): a throwaway Unity project in the session scratchpad.

**Interfaces:**
- Consumes: Task 2's `unity-batchmode.md` (*Shot capture* row) and agents; base headings from `dev-loop-lite/SKILL.md`.
- Produces: `ShotCapture.Run()` reading `-scene <Assets/…unity>` and `-shotsOut <dir>`; writes `<dir>/<name without Shot_>.png`; exit 0 on success, 1 on any failure.

- [ ] **Step 1: Write `ShotCapture.cs`**

```csharp
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

// Batchmode shot renderer for the dev-loop-greybox skill. Renders every camera
// named Shot_<name> in the given scene to <shotsOut>/<name>.png.
// ponytail: fixed 1920x1080, no settings asset; add args if a brief ever needs another size.
public static class ShotCapture
{
    const string Prefix = "Shot_";
    const int Width = 1920;
    const int Height = 1080;

    public static void Run()
    {
        try
        {
            var args = Environment.GetCommandLineArgs();
            var scene = Arg(args, "-scene") ?? throw new ArgumentException("missing -scene <Assets/...unity>");
            var outDir = Arg(args, "-shotsOut") ?? throw new ArgumentException("missing -shotsOut <dir>");

            EditorSceneManager.OpenScene(scene, OpenSceneMode.Single);
            var cameras = Resources.FindObjectsOfTypeAll<Camera>()
                .Where(c => c.gameObject.scene.IsValid() && c.name.StartsWith(Prefix, StringComparison.Ordinal))
                .ToArray();
            if (cameras.Length == 0)
                throw new InvalidOperationException($"no {Prefix}* cameras in {scene}");
            var duplicate = cameras.GroupBy(c => c.name).FirstOrDefault(g => g.Count() > 1);
            if (duplicate != null)
                throw new InvalidOperationException($"duplicate shot camera name {duplicate.Key}");

            Directory.CreateDirectory(outDir);
            foreach (var camera in cameras)
                Render(camera, Path.Combine(outDir, camera.name.Substring(Prefix.Length) + ".png"));
            Debug.Log($"ShotCapture: wrote {cameras.Length} shots to {outDir}");
            EditorApplication.Exit(0);
        }
        catch (Exception e)
        {
            Debug.LogException(e);
            EditorApplication.Exit(1);
        }
    }

    static void Render(Camera camera, string path)
    {
        var target = new RenderTexture(Width, Height, 24);
        var image = new Texture2D(Width, Height, TextureFormat.RGB24, false);
        var previousTarget = camera.targetTexture;
        var previousActive = RenderTexture.active;
        try
        {
            camera.targetTexture = target;
            camera.Render();
            RenderTexture.active = target;
            image.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
            image.Apply();
            File.WriteAllBytes(path, image.EncodeToPNG());
        }
        finally
        {
            camera.targetTexture = previousTarget;
            RenderTexture.active = previousActive;
            UnityEngine.Object.DestroyImmediate(target);
            UnityEngine.Object.DestroyImmediate(image);
        }
    }

    static string Arg(string[] args, string name)
    {
        var i = Array.IndexOf(args, name);
        return i >= 0 && i + 1 < args.Length ? args[i + 1] : null;
    }
}
```

- [ ] **Step 2: Build a scratch project** (Unity at `C:\Program Files\Unity\Hub\Editor\6000.6.3f1\Editor\Unity.exe`, referred to as `$U`):
  `"$U" -batchmode -quit -createProject "$SCRATCH/shotproj" -logFile "$SCRATCH/create.log"`; copy `ShotCapture.cs` to `Assets/Editor/`; add `Assets/Editor/MakeTestScene.cs` with a static `Make()` that creates a new scene containing a cube, a directional light, `Shot_Front` (Camera component **disabled**, GameObject active, looking at the cube), `Shot_Top` (enabled), and saves it as `Assets/Test.unity`; plus `MakeDuplicate()` that saves `Assets/Dup.unity` with two `Shot_A` cameras, and `MakeEmpty()` that saves `Assets/Empty.unity` with none. Run each via `-executeMethod`.

- [ ] **Step 3: Verify success path** — run the *Shot capture* command against `Assets/Test.unity` into `$SCRATCH/shots`. Expected: exit 0, `Front.png` and `Top.png` exist, each 1920×1080 (check PNG header bytes 16–23 or `file`), and `Read` both images to confirm the cube is visible (not a black frame).

- [ ] **Step 4: Verify failure paths** — `Dup.unity` → exit 1, log contains `duplicate shot camera name Shot_A`; `Empty.unity` → exit 1, `no Shot_* cameras`; omit `-shotsOut` → exit 1, `missing -shotsOut`. If the default template is URP and `camera.Render()` produces black frames, switch to `RenderPipeline.SubmitRenderRequest` with a `Camera.RenderRequest`… only on evidence; record which ran in the commit message.

- [ ] **Step 5: Write `dev-loop-greybox/SKILL.md`.** Frontmatter `name: dev-loop-greybox`, description: "The lite dev loop for in-engine Unity concept work — greybox/ProBuilder blockouts, placeholder materials, lighting mood — with rendered camera shots reviewed against an art brief. Use when asked for a greybox run, or when the user types /dev-loop-greybox. For Unity gameplay code use dev-loop-unity." Body: "**Follow the `dev-loop-lite` skill in full.** … This file changes six things and nothing else." One `## Change N` per spec item in "`dev-loop-greybox` — changes to `dev-loop-lite`", quoting base headings from `dev-loop-lite/SKILL.md`:
  - Change 1 (art brief, shot table template with columns *Name, Camera position, Look target, Must show*) → `` `## Phase 0 — Frame the slice` ``
  - Change 2 (build + `Shot_<name>` cameras, **Camera component disabled, GameObject active**, copy ShotCapture.cs from this skill's references if absent) → `` `## Phase 1 — Implement` ``
  - Change 3 (capture after Phase 2 and every Phase 6, using `dev-loop-unity/references/unity-batchmode.md`; missing PNG = failed DoD) → `` `## Phase 2 — Tests` `` and `` `## Phase 6 — Fix` ``
  - Change 4 (lanes: reviewer-unity with `model: sonnet`, reviewer-visual, the addendum to the Correctness lane) → `` `## Phase 3 — Plan the round` `` and `` `## Phase 4 — Delegate` ``
  - Change 5 (escalate to `dev-loop-unity`) → `` `### Escalation to the full loop` ``
  - Change 6 (shots into `docs/walkthroughs/<slug>/shots/`, embedded; retake the snapshot after copying — they change the digest) → `` `## Phase 8b — Walkthrough` ``
  Plus the no-GPU rule: capture failing for lack of a graphics device stops the run and reports; the Visual lane is never skipped.

- [ ] **Step 6: Run heading test** — `bash tests/override-headings.sh` → all PASS, `OK: N assertions`, exit 0.

- [ ] **Step 7: Commit** — the two files only (scratch project stays in the scratchpad); message records the Unity version verified against and which render path worked.

### Task 5: Wiring — CLAUDE.md, README, installers

**Files:**
- Modify: `user/CLAUDE.md` (Development loop section, after the "**When unsure, go heavier.**" paragraph)
- Modify: `README.md` (loops table ~line 63–67; add a short "Unity loops" section before `## How a loop works`)
- Modify: `install.sh:82,137`, `install.ps1:66,67,132`

- [ ] **Step 1: CLAUDE.md** — add exactly: `**Unity repos:** \`/dev-loop-unity\` for code, \`/dev-loop-greybox\` for blockouts and visual prototypes. Both follow a base loop and override only what differs.`
- [ ] **Step 2: README** — two table rows: `dev-loop-greybox` | 4 consolidated + Unity + Visual | 2 | — | Unity blockouts and visual prototypes; `dev-loop-unity` | 9 + Unity, gated | 3 | — | Unity game code. Cost column `—` (not modelled in `docs/cost-model.py`; say so in the section). Section: ≤15 lines — what each is, the override pattern, batchmode requirement, `$UNITY_EDITOR`, close the Editor first.
- [ ] **Step 3: Installers** — `22` → `24` in all four places; skills label `5 loops` → `7 loops` in both.
- [ ] **Step 4: Verify** — `bash tests/install-contract.sh` passes; `bash tests/override-headings.sh` passes; `git diff main --stat -- user/.claude/skills/dev-loop user/.claude/skills/dev-loop-lite` empty.
- [ ] **Step 5: Commit** — "Wire Unity loops into CLAUDE.md, README, installers".
