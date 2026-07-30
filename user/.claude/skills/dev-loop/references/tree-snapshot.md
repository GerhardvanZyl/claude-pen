# Working-tree snapshot and integrity check

Every loop reviews a **working tree**, not a commit. Nothing is on the branch
until Phase 9 puts it there. Two consequences follow, and this file is the
mechanism for both:

1. Reviewers run in parallel against the tree the lead is about to commit. If
   one of them writes to it, the diff that ships is not the diff that was
   reviewed, and a file-list comparison will not notice.
2. The Tests lane needs to mutate code to prove a test is not decorative. It
   must do that somewhere that is not the tree under review.

The lead owns both. Reviewers never run these commands.

---

## The snapshot

This produces a git tree object covering the working tree — tracked changes and
untracked files, honouring `.gitignore` — **without touching the index, the
working tree, or HEAD.**

```bash
IDX="$(git rev-parse --git-dir)/review-snapshot.index"
rm -f "$IDX"
GIT_INDEX_FILE="$IDX" git add -A
TREE=$(GIT_INDEX_FILE="$IDX" git write-tree)
rm -f "$IDX"
echo "$TREE"
```

PowerShell:

```powershell
$idx = Join-Path (git rev-parse --git-dir) 'review-snapshot.index'
Remove-Item $idx -ErrorAction SilentlyContinue
$env:GIT_INDEX_FILE = $idx; git add -A
$tree = (git write-tree).Trim()
Remove-Item $idx -ErrorAction SilentlyContinue; $env:GIT_INDEX_FILE = $null
$tree
```

The temporary index is why this is safe: `git add -A` writes to `$IDX`, never to
`.git/index`, so a staged-or-not state you had before is exactly the state you
have after.

`$TREE` is a content digest of everything under review. Two snapshots with the
same tree hash are the same tree, byte for byte.

**Append `2>/dev/null` to the `git add` and `git write-tree` calls on any
repository with `core.autocrlf` enabled.** Otherwise each snapshot prints a
`LF will be replaced by CRLF` warning per file — on a repository of any size
that is hundreds of lines of noise per check, three checks per round, and you
will stop running it. The warnings are harmless and say nothing about the
digest, which is computed from normalised content and is stable across
line-ending settings.

`.gitignore` is respected, which is what keeps the run directory — and the
scratch worktree inside it — out of the digest. Verify `.claude/review/runs/` is
actually ignored before relying on that; the installer adds it, but a repository
that predates the installer may not have it.

## The integrity check

**Phase 3, before spawning any reviewer:** take the snapshot and record it in
`round-N/plan.md` as `tree: <sha>`.

**Phase 4, after every reviewer has drained and before triage:** take it again
and compare.

```
same    → proceed to triage.
differs → a reviewer wrote to the tree under review. STOP.
```

This is not a formality. Reviewers are prevented from calling `Edit`, and their
`disallowedTools` blocks the obvious mutating shell commands, but a shell
redirect inside an otherwise-permitted command can still write, and no
permission rule catches every spelling. The digest catches the result rather
than trying to enumerate the causes, which is why it is the check that matters.

If it differs:

```bash
git status --porcelain          # what moved
git diff                        # against the pre-review state, if committed
```

Identify which lane did it from `round-N/*.log.md` timestamps, record it in
`triage.md`, restore the tree, and **rerun that lane's round from the restored
tree.** Do not reason about whether the mutation was harmless. A reviewer that
edited the code it was reviewing produced findings about a tree that no longer
exists.

Recompute the digest after Phase 6 fixes too — that change is expected and
legitimate, and the new value is the baseline for the next round.

## The scratch worktree

The Tests lane proves a test is decorative by breaking the code it covers and
showing the test still passes. That requires mutation. It happens here and
nowhere else.

**Phase 3, when the Tests lane is applicable**, after taking the snapshot:

```bash
SNAP=$(git commit-tree "$TREE" -p HEAD -m "review snapshot <run-id> round N")
git worktree add --detach ".claude/review/runs/<run-id>/round-N/scratch" "$SNAP"
```

The scratch worktree is an exact copy of the tree under review, including
uncommitted and untracked files, on a detached commit that is not on any branch
and will never be pushed. It sits inside the run directory, which is
`.gitignore`d, so it does not appear in `git status` and cannot be staged by
Phase 9.

Pass the path to the Tests lane. It is the **only** location outside the run
directory's own files that any reviewer may write to.

**Teardown — Phase 7 at the end of each round, and unconditionally at Phase 9,
including on a blocked exit:**

```bash
git worktree remove --force ".claude/review/runs/<run-id>/round-N/scratch"
git worktree prune
```

A left-behind worktree holds a commit object alive and will confuse the next
run's `git worktree list`. Remove it even when the round went badly — especially
then.

## What the Tests lane is told

- Run the test suite in the scratch worktree, not the primary tree.
- Make the breaking edit there, run the covering test, record the result and the
  line changed.
- Do not restore the mutation — the worktree is discarded whole.
- Never write to the primary working tree. If the scratch path was not provided,
  say so in the log and fall back to reading the assertions; do not improvise a
  mutation somewhere else.

## If worktrees are unavailable

Some environments cannot add a worktree — a bare or restricted checkout, a
sandbox without the disk, a repository already at its worktree limit. In that
case:

- **Do not fall back to mutating the primary tree.** There is no version of that
  which is acceptable.
- Take the snapshot and run the integrity check anyway; it does not depend on
  worktrees.
- Tell the Tests lane that mutation testing is unavailable this run. It reviews
  assertions by reading, and records `mutation testing: unavailable` in its log
  so the lead knows the strongest check did not run.
