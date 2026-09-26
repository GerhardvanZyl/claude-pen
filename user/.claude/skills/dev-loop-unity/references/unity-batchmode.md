# Unity batchmode reference

Shared by `dev-loop-unity` and `dev-loop-greybox`. The lead reads this file
directly and runs every command in it; reviewers never do.

## Locate the Editor

In order, stop at the first that resolves:

1. `$UNITY_EDITOR` if set.
2. Read `m_EditorVersion` from `ProjectSettings/ProjectVersion.txt`, then look
   for `<Unity Hub editor root>/<version>/Editor/Unity.exe` — Windows default
   `C:\Program Files\Unity\Hub\Editor\`; macOS
   `/Applications/Unity/Hub/Editor/<version>/Unity.app/Contents/MacOS/Unity`.
3. Otherwise **stop and ask the user.** Never guess a different version —
   batchmode against the wrong Editor version can silently reimport or
   upgrade the project.

## Before any batchmode run — the lockfile check

**Every command below has this as a precondition.** If
`Temp/UnityLockfile` exists, the project is already open in an Editor and
batchmode will fail, often with an obscure log rather than a clear error.
Check for the lockfile before every invocation and, if present, ask the user
to close the open Editor before proceeding.

## Commands

All write their logs into the run directory.

| Purpose | Command | Pass condition |
| --- | --- | --- |
| Compile check | `-batchmode -quit -projectPath <p> -logFile <run>/compile.log` | exit 0 |
| EditMode tests | `-batchmode -runTests -testPlatform EditMode -projectPath <p> -testResults <run>/editmode.xml -logFile <run>/editmode.log` | exit 0 |
| PlayMode tests | same with `PlayMode` / `playmode.xml` | exit 0 |
| Shot capture | `-batchmode -quit -projectPath <p> -executeMethod ShotCapture.Run -scene <path> -shotsOut <dir> -logFile <run>/capture.log` | exit 0, one PNG per `Shot_*` camera |

`-runTests` exits the process by itself; **never add `-quit` to it** — the two
together race and the run can terminate before results are written.

Shot capture must **not** use `-nographics` — rendering a camera needs a
graphics device. A headless machine without a GPU cannot run this command; see
the risk note in the design spec.

## On non-zero exit

Never retry blind. Read the tail of the named log file (`compile.log`,
`editmode.log`, `playmode.log`, or `capture.log`) and hand the error lines to
the fix sidekick as part of its brief.

## Tests-lane scratch worktree

A fresh worktree triggers a full `Library/` reimport, which can take minutes to
hours on a Unity project. After creating the scratch worktree per
`dev-loop/references/tree-snapshot.md`, copy `Library/` from the main tree into
it before running any batchmode command there:

```bash
cp -r <main>/Library <scratch>/Library
```

`Library/` is gitignored and does not affect the tree digest, so this copy has
no effect on the integrity check.
