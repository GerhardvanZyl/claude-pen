# Walkthrough Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three skills — `implementation-notes`, `pr-walkthrough`, `pr-walkthrough-review` — and wire them into all five dev loops so every run ships a document explaining why the change landed the way it did.

**Architecture:** Notes accumulate during the run in the gitignored run directory. A new lettered sub-phase before the commit phase turns them into `docs/walkthroughs/<slug>.md`, reviews it, and retakes the tree baseline. No existing phase number moves.

**Tech Stack:** Markdown only. Claude Code skill and agent files. No runtime, no build, no dependencies.

**Spec:** `docs/superpowers/specs/2026-08-17-dev-loop-walkthroughs-design.md`

## Global Constraints

Every task's requirements implicitly include these. Values are verbatim from the spec.

- **No existing phase number in any loop may change.** `dev-loop-ultra` and `dev-loop-ultra-opus` cross-reference "`dev-loop` Phase 9" by number. New work goes in a lettered sub-phase: **8b** in `dev-loop`, `dev-loop-lite`, `dev-loop-ultra`, `dev-loop-ultra-opus`; **5b** in `dev-loop-ultralight`.
- Notes file path: `.claude/review/runs/<run-id>/notes.md`. Gitignored, never committed.
- Walkthrough path: `docs/walkthroughs/<slug>.md`. Committed on the story branch.
- Index field, all five loops, identical: `"walkthrough": "docs/walkthroughs/<slug>.md"` or `"walkthrough": "skipped:<reason>"`.
- `dev-loop-ultralight` does **not** invoke `pr-walkthrough-review`; its lead checks the draft inline against the same criteria.
- Skill frontmatter requires `name` and `description`. **`name` must exactly match the containing directory name.**
- All edits go to `user/.claude/` in this repo. `~/.claude/` is updated only by Task 9, via the installer.
- Skill files must be named `SKILL.md`.
- Branch: `feature/walkthrough-skills`. Do not merge or push.

---

### Task 1: `implementation-notes` skill

**Files:**
- Create: `user/.claude/skills/implementation-notes/SKILL.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the `notes.md` contract that Tasks 2, 4, 5 and 6 depend on — file at `.claude/review/runs/<run-id>/notes.md`, with H2 sections named exactly `## Frame`, `## Decisions`, `## Reviewers`, `## Interesting finds`, `## Open questions`. Task 2's authoring skill reads these names.

- [ ] **Step 1: Write the verification check**

Create `/tmp/check-task1.sh` in the scratchpad and run it — it must FAIL now.

```bash
S=user/.claude/skills/implementation-notes/SKILL.md
test -f "$S" || { echo "FAIL: no SKILL.md"; exit 1; }
head -1 "$S" | grep -qx -- '---' || { echo "FAIL: no frontmatter"; exit 1; }
grep -qx 'name: implementation-notes' "$S" || { echo "FAIL: name must match dir"; exit 1; }
for h in '## Frame' '## Decisions' '## Reviewers' '## Interesting finds' '## Open questions'; do
  grep -qxF "$h" "$S" || { echo "FAIL: missing section $h"; exit 1; }
done
grep -q 'none considered' "$S" || { echo "FAIL: missing the empty-alternatives rule"; exit 1; }
grep -q 'review/runs' "$S" || { echo "FAIL: notes path not stated"; exit 1; }
echo PASS
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `bash /tmp/check-task1.sh`
Expected: `FAIL: no SKILL.md`

- [ ] **Step 3: Write the skill**

Frontmatter verbatim:

```markdown
---
name: implementation-notes
description: >
  Keep a running record of why a change was built the way it was — decisions,
  the alternatives rejected and why, which loop and reviewers ran, and the
  findings worth explaining. Invoked at the start of every dev loop and appended
  to as it runs; the notes are the raw material the pr-walkthrough skill turns
  into the reviewer walkthrough. Use when a dev loop starts, or when the user
  types /implementation-notes.
---
```

Body must cover, in this order:

1. **What this is for** — the two gaps it closes, from the spec's "The problem the notes skill actually solves": the implementer's rejected alternatives (lost when the agent returns) and requirements-lane findings that were rejected at triage (dropped, but still true about the brief).
2. **Where it lives** — `.claude/review/runs/<run-id>/notes.md`, and *why there*: the run directory is gitignored, so notes never affect the working-tree digest and never ship.
3. **Append-only** — a note written at Phase 1 must still read as it did when the decision was live, not as it looks with hindsight after triage. Never rewrite earlier entries.
4. **The five sections**, with the H2 headings spelled exactly as in the check above, and the phase each is written at (Frame → Phase 0; Decisions → Phases 1, 2, 6; Reviewers → Phases 3–4; Interesting finds → Phase 5; Open questions → any).
5. **The decision entry template**, verbatim:

```markdown
### <short title>
- **Decided:** what was done
- **Why:** the reason
- **Alternatives considered:** each one, and why it was rejected
- **Forced by:** the constraint that dictated the shape, or "nothing — free choice"
```

6. **The empty-alternatives rule** — an entry with no alternatives must say `none considered` explicitly. A blank is indistinguishable from a decision nobody made, and the walkthrough skill cannot tell the difference later.
7. **Interesting finds** — the three kinds from the spec, requirements-lane findings first, recorded *whether accepted or rejected*, with the reason.
8. **Escalation** — when a loop escalates mid-run, append the trigger to Frame. A walkthrough for an escalated change must be able to say so.

- [ ] **Step 4: Run the check and confirm it passes**

Run: `bash /tmp/check-task1.sh`
Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add user/.claude/skills/implementation-notes
git commit -m "Add implementation-notes skill"
```

---

### Task 2: `pr-walkthrough` skill and bundled exemplar

**Files:**
- Create: `user/.claude/skills/pr-walkthrough/SKILL.md`
- Create: `user/.claude/skills/pr-walkthrough/references/example-walkthrough.md`

**Interfaces:**
- Consumes: the `notes.md` section names from Task 1.
- Produces: the walkthrough contract Task 3 reviews and Tasks 4–6 invoke — output at `docs/walkthroughs/<slug>.md`, opening with an architecture Mermaid diagram then a sequence Mermaid diagram, then the eight numbered sections.

- [ ] **Step 1: Write the verification check**

```bash
S=user/.claude/skills/pr-walkthrough/SKILL.md
E=user/.claude/skills/pr-walkthrough/references/example-walkthrough.md
test -f "$S" || { echo "FAIL: no SKILL.md"; exit 1; }
test -f "$E" || { echo "FAIL: no bundled exemplar"; exit 1; }
grep -qx 'name: pr-walkthrough' "$S" || { echo "FAIL: name must match dir"; exit 1; }
grep -q 'dev.azure.com' "$S" || { echo "FAIL: ADO host not covered"; exit 1; }
grep -q 'github.com' "$S" || { echo "FAIL: GitHub host not covered"; exit 1; }
grep -qi 'no repository' "$S" || { echo "FAIL: no-repo host not covered"; exit 1; }
grep -q 'example-walkthrough.md' "$S" || { echo "FAIL: exemplar fallback not referenced"; exit 1; }
grep -q 'notes.md' "$S" || { echo "FAIL: notes not named as the brief"; exit 1; }
# the exemplar must be generic, not the GMS one
grep -qiE 'GMS|Gateway|InCell|PrisonerLink|Ravenhall' "$E" && { echo "FAIL: exemplar is not generic"; exit 1; }
grep -q '```mermaid' "$E" || { echo "FAIL: exemplar has no mermaid diagram"; exit 1; }
grep -qi 'rejected' "$E" || { echo "FAIL: exemplar has no rejected alternative"; exit 1; }
echo PASS
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `bash /tmp/check-task2.sh`
Expected: `FAIL: no SKILL.md`

- [ ] **Step 3: Write the skill**

Base it on the user-supplied draft reproduced in the spec. Frontmatter verbatim:

```markdown
---
name: pr-walkthrough
description: >
  Author the reviewer walkthrough document that ships with a change's PR. Walks a
  senior engineer through the change by following one flow from its entrypoint to
  the code that changed, explaining why each decision was taken. Use at the end of
  every dev loop before the PR is raised, or when the user types /pr-walkthrough.
  Not a changelog and not a PR description — those say what changed; this says why.
---
```

Keep from the draft, unchanged in substance: *When this runs*; *Who you are writing for* (senior engineer, basic project knowledge — explain what is specific to this codebase, explain nothing about the language or framework); *Why beats what*, including the test that a section surviving the deletion of "why" and "because" is a changelog entry; *Start at the entrypoint, not at the diff*, with the entrypoint table; *Highlight rarely used patterns*; *Diagrams* (Mermaid only, never ASCII); *Anchors*; *What this is not*.

Apply these three changes:

- **Exemplar resolution.** Replace the hard reference to `docs/walkthroughs/device-log-gms.md` with: read the most recently modified file in this repo's `docs/walkthroughs/` if any exists; otherwise read the bundled `references/example-walkthrough.md`.
- **Authoring is delegated.** Delegate the draft to `sidekick`, passing `notes.md`, the diff base and the changed-file list. State why: the notes are nothing but reasons, so a draft briefed on them cannot come back as a narrated diff — which is what happens when the brief is the diff. If `notes.md` is missing or thin, the lead writes it and records in `run.md` that the notes were inadequate.
- **Opening diagrams.** The document opens with a Mermaid architecture diagram showing where the change sits in the system, then the Mermaid sequence diagram of the changed flow, both before the change table.

Structure section lists eight items: opening paragraph (story, branch/PR/commit, explicit out-of-scope); architecture + sequence diagrams; change table with noise rows marked "ignore this"; the flow; the decisions file by file ordered by the flow; where to look to review this; tests; open questions.

Include the hosting table verbatim:

```markdown
| Host | Path | Link |
| --- | --- | --- |
| GitHub | `docs/walkthroughs/<slug>.md`, committed on the story branch | Relative link in the PR body |
| Azure DevOps | same | ADO does not render bare relative paths in a PR description. Use the full form: `<org>/<project>/_git/<repo>?path=/docs/walkthroughs/<slug>.md&version=GB<branch>` |
| No repository | `docs/walkthroughs/<slug>.md` in the working folder | No PR exists. Report the absolute path to the user in chat and record it in `run.md`. Anchors carry file+line with no commit hash, and the opening paragraph says so, because line numbers will drift with nothing to pin them to. |
```

Detect the host from the git remote: `github.com` → GitHub; `dev.azure.com` or `visualstudio.com` → ADO; no remote or no repository → the third row.

Close with the skip rule: a purely mechanical change may skip the walkthrough, and the skip is reported in the PR description and `run.md`, never silent.

- [ ] **Step 4: Write the bundled exemplar**

`references/example-walkthrough.md`, against a **fictional generic** codebase. Do not mention GMS, Gateway, InCell, PrisonerLink or Ravenhall — the check greps for them.

Use a fictional order-processing service. It must demonstrate the format at full density, so it must contain: an opening paragraph with an explicit out-of-scope line; a Mermaid architecture diagram; a Mermaid sequence diagram from HTTP entrypoint to the changed repository method; a change table with at least one row marked "ignore this"; at least two decision sections each with a genuinely rejected alternative and the reason it was rejected; one "rarely used pattern" callout; a review-order section with line ranges; a tests section; and a closing open-questions section with a real uncertainty. Roughly 150–250 lines.

- [ ] **Step 5: Run the check and confirm it passes**

Run: `bash /tmp/check-task2.sh`
Expected: `PASS`

- [ ] **Step 6: Commit**

```bash
git add user/.claude/skills/pr-walkthrough
git commit -m "Add pr-walkthrough skill and generic exemplar"
```

---

### Task 3: `pr-walkthrough-review` skill

**Files:**
- Create: `user/.claude/skills/pr-walkthrough-review/SKILL.md`

**Interfaces:**
- Consumes: the walkthrough contract from Task 2.
- Produces: a one-line return to the lead — path, whether it edited, issues corrected by category. Tasks 4, 5 and 6 rely on that being one line.

- [ ] **Step 1: Write the verification check**

```bash
S=user/.claude/skills/pr-walkthrough-review/SKILL.md
test -f "$S" || { echo "FAIL: no SKILL.md"; exit 1; }
grep -qx 'name: pr-walkthrough-review' "$S" || { echo "FAIL: name must match dir"; exit 1; }
grep -q 'solution files' "$S" || { echo "FAIL: missing .sln naming rule"; exit 1; }
grep -q 'project files' "$S" || { echo "FAIL: missing .csproj naming rule"; exit 1; }
grep -qi 'voice' "$S" || { echo "FAIL: missing voice-model readability check"; exit 1; }
grep -qi 'anchor' "$S" || { echo "FAIL: missing anchor verification check"; exit 1; }
grep -qi 'one line' "$S" || { echo "FAIL: return contract not stated"; exit 1; }
echo PASS
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `bash /tmp/check-task3.sh`
Expected: `FAIL: no SKILL.md`

- [ ] **Step 3: Write the skill**

Frontmatter verbatim:

```markdown
---
name: pr-walkthrough-review
description: >
  Review the walkthrough document that ships with a change's PR and correct it in
  place. Checks that it explains why the change landed the way it did rather than
  restating what changed, that it is calibrated to a senior engineer with basic
  project knowledge, and that it reads well aloud. Use after the walkthrough is
  authored and before the PR is raised, or when the user types
  /pr-walkthrough-review.
---
```

Body must cover:

1. **When it runs** — after `pr-walkthrough` has authored the draft, before the PR is raised.
2. **Write-capable on the walkthrough file only**, with the reason stated: the read-only reviewer convention protects the code under review; this document is authored after every lane has drained, is not code, and the invoking phase retakes the tree baseline afterwards regardless. So "correct it if it doesn't" is safe to implement literally. It must not touch any other file.
3. **The checks**, as a list it works through:
   - Written for a senior engineer with basic project knowledge — explains what is specific to this codebase, explains nothing about the language, framework or standard patterns.
   - Explains reasoning, not changes. Apply the test: a section that survives deleting the words "why" and "because" is a changelog entry — rewrite it.
   - Concise; no tangents.
   - Reads well aloud, for a voice model.
   - Calls `.sln` files "solution files" and `.csproj` files "project files".
   - Well structured, entrypoint-first, following execution flow.
   - **Every cited anchor is real** — spot-check line numbers against the files. A walkthrough with invented line numbers is worse than none.
   - **Every Mermaid block parses**, and both the architecture and sequence diagrams are present.
4. **The return contract** — one line to the lead: path, whether it edited, and issues corrected by category. State explicitly that the lead does not read the whole document into context to judge it.

- [ ] **Step 4: Run the check and confirm it passes**

Run: `bash /tmp/check-task3.sh`
Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add user/.claude/skills/pr-walkthrough-review
git commit -m "Add pr-walkthrough-review skill"
```

---

### Task 4: Wire `dev-loop` (reference implementation)

**Files:**
- Modify: `user/.claude/skills/dev-loop/SKILL.md`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: the canonical Phase 8b text and the Phase 9 edits that Tasks 5 and 6 mirror.

- [ ] **Step 1: Write the verification check**

```bash
S=user/.claude/skills/dev-loop/SKILL.md
grep -qF '## Phase 8b — Walkthrough' "$S" || { echo "FAIL: no Phase 8b"; exit 1; }
grep -q 'implementation-notes' "$S" || { echo "FAIL: notes skill not invoked"; exit 1; }
grep -q 'pr-walkthrough-review' "$S" || { echo "FAIL: review skill not invoked"; exit 1; }
grep -q '"walkthrough"' "$S" || { echo "FAIL: index field missing"; exit 1; }
grep -q 'rejected' "$S" || { echo "FAIL: briefs do not ask for rejected alternatives"; exit 1; }
# no existing phase number moved
for p in '## Phase 0' '## Phase 1' '## Phase 2' '## Phase 3' '## Phase 4' '## Phase 5' '## Phase 6' '## Phase 7' '## Phase 8 ' '## Phase 9'; do
  grep -qF "$p" "$S" || { echo "FAIL: phase moved or lost: $p"; exit 1; }
done
echo PASS
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `bash /tmp/check-task4.sh`
Expected: `FAIL: no Phase 8b`

- [ ] **Step 3: Add the notes invocation to Phase 0**

In `## Phase 0 — Frame the slice`, after the paragraph beginning "Create the run directory", append:

```markdown
Then invoke the `implementation-notes` skill and create `notes.md` in the same
directory. Record the requirement, the non-goals, the constraints, and **which
loop you chose and the specific eligibility criterion that chose it**. You are
appending to this file for the rest of the run; Phase 8b turns it into the
walkthrough that ships with the PR.
```

- [ ] **Step 4: Add the reporting obligation to Phases 1, 2 and 6**

Append to `## Phase 1 — Implement`:

```markdown
**The brief must ask for the reasoning back.** Require the sidekick to return,
alongside its summary, the decisions it took, the alternatives it rejected and
why, and any constraint that forced a shape. Append what comes back to
`notes.md`. Without this the reasoning dies when the agent returns, and the
walkthrough in Phase 8b has nothing to work from but the diff.
```

Append to `## Phase 2 — Tests` and to `## Phase 6 — Fix` the same requirement, one sentence each: the brief asks for decisions and rejected alternatives back, and the lead appends them to `notes.md`.

- [ ] **Step 5: Add the triage capture to Phase 5**

At the end of `## Phase 5 — Triage`, before "You are the arbiter", append:

```markdown
Then append the **Interesting finds** to `notes.md`: any finding worth explaining
to a reviewer, every accepted-defect-but-rejected-remedy pair, and every
`conventions.md` entry created this run.

**Requirements-lane findings go in whether you accepted them or rejected them.**
Every other lane's rejected findings are correctly dropped here. A rejected
requirements finding is not noise — it is a statement that the brief was
ambiguous, or that the reviewer read it differently from the implementer, and
that is exactly what a reviewer of the change needs to be told. Record the
finding, the decision, and the reason.
```

- [ ] **Step 6: Insert Phase 8b between Phase 8 and Phase 9**

Insert verbatim, immediately before `## Phase 9 — Commit, push, pull request`:

```markdown
## Phase 8b — Walkthrough

The change has been reviewed, but the reasoning behind it still exists only in
`notes.md`. This phase turns it into the document that ships with the PR.

1. **Author it.** Invoke the `pr-walkthrough` skill. Delegate the draft to
   `sidekick`, passing the `notes.md` path, the diff base, and the changed-file
   list. **The notes are the brief, not the diff** — a draft briefed on the diff
   comes back as a narrated changelog, which is the one failure this phase
   exists to prevent. If `notes.md` is missing or thin, write the walkthrough
   yourself and record in `run.md` that the notes were inadequate; that is a
   defect in the run worth seeing.

2. **Review it.** Invoke the `pr-walkthrough-review` skill. It is write-capable
   on the walkthrough file only and returns one line — path, whether it edited,
   and issues corrected by category. Do not read the document into your own
   context to judge it.

3. **Retake the working-tree snapshot and record it as the new baseline** for
   Phase 9, per `references/tree-snapshot.md`. **This is not bookkeeping.** The
   walkthrough is a new file under `docs/`, which is not `.gitignore`d, so it
   changes the digest — and Phase 9 step 4 stops the run when the digest differs
   from the recorded baseline. Without this step, every run halts there. The only
   legitimate delta is the walkthrough file itself; anything else is the failure
   that check has always been for, and is handled the same way.

Skipping the walkthrough is permitted only for a purely mechanical change — a
rename, a dependency bump, a formatting sweep. A skip is stated in the PR
description and in `run.md`. It is never silent.
```

- [ ] **Step 7: Update Phase 9**

Three edits inside `## Phase 9`:

- In step 2, after "Exclude the run directory", add: `The walkthrough at docs/walkthroughs/ **is** committed — it is part of the change and the PR description links it.`
- In step 4's second bullet, change "the digest recorded after the final round's fixes (Phase 7)" to "the digest recorded at the end of Phase 8b".
- In step 8, add to the description list: `a link to the walkthrough, per the hosting table in the pr-walkthrough skill`.

- [ ] **Step 8: Add the index field**

In the `## Run log` section, add `"walkthrough"` to the example index line and document it below the table:

```markdown
`walkthrough` is the committed path, or `skipped:<reason>`. All five loops write
it identically.
```

- [ ] **Step 9: Run the check and confirm it passes**

Run: `bash /tmp/check-task4.sh`
Expected: `PASS`

- [ ] **Step 10: Commit**

```bash
git add user/.claude/skills/dev-loop/SKILL.md
git commit -m "Wire walkthrough skills into dev-loop"
```

---

### Task 5: Wire `dev-loop-lite` and `dev-loop-ultralight`

**Files:**
- Modify: `user/.claude/skills/dev-loop-lite/SKILL.md`
- Modify: `user/.claude/skills/dev-loop-ultralight/SKILL.md`

**Interfaces:**
- Consumes: the Phase 8b text from Task 4.
- Produces: nothing later tasks depend on.

- [ ] **Step 1: Write the verification check**

```bash
L=user/.claude/skills/dev-loop-lite/SKILL.md
U=user/.claude/skills/dev-loop-ultralight/SKILL.md
grep -qF '## Phase 8b — Walkthrough' "$L" || { echo "FAIL: lite has no Phase 8b"; exit 1; }
grep -q 'pr-walkthrough-review' "$L" || { echo "FAIL: lite missing review skill"; exit 1; }
grep -qF '## Phase 5b — Walkthrough' "$U" || { echo "FAIL: ultralight has no Phase 5b"; exit 1; }
grep -q 'pr-walkthrough-review' "$U" && { echo "FAIL: ultralight must NOT invoke the review skill"; exit 1; }
for f in "$L" "$U"; do
  grep -q 'implementation-notes' "$f" || { echo "FAIL: $f missing notes skill"; exit 1; }
  grep -q '"walkthrough"' "$f" || { echo "FAIL: $f missing index field"; exit 1; }
done
grep -qF '## Phase 9' "$L" || { echo "FAIL: lite phase 9 moved"; exit 1; }
grep -qF '## Phase 6' "$U" || { echo "FAIL: ultralight phase 6 moved"; exit 1; }
echo PASS
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `bash /tmp/check-task5.sh`
Expected: `FAIL: lite has no Phase 8b`

- [ ] **Step 3: Edit `dev-loop-lite`**

Apply the same five edits as Task 4, adapted:

- Phase 0: invoke `implementation-notes`, create `notes.md`, record loop and eligibility criterion.
- Phases 1, 2, 6: briefs ask for decisions and rejected alternatives back; append to `notes.md`.
- Phase 5: append Interesting finds, with the requirements-findings rule. In this loop the correctness lane owns requirements — say so, and apply the rule to `reviewer-lite-correctness` findings about the brief.
- Insert `## Phase 8b — Walkthrough` verbatim from Task 4 step 6, immediately before `## Phase 9`.
- Phase 9: same three edits, plus `"loop":"lite"` keeps its existing meaning and the new `"walkthrough"` field is added alongside it.

- [ ] **Step 4: Edit `dev-loop-ultralight`**

Same shape, with two differences:

- The phase is `## Phase 5b — Walkthrough`, inserted immediately before `## Phase 6 — Commit, push, pull request`.
- **Step 2 of the phase is not a subagent.** Replace it with:

```markdown
2. **Check it yourself.** This loop does not spawn `pr-walkthrough-review` — a
   change small enough for ultralight does not justify another agent. Read the
   draft against that skill's criteria: does it explain why rather than what, is
   it calibrated to a senior engineer, are the cited line anchors real, do both
   Mermaid diagrams parse, and does it call `.sln` files solution files and
   `.csproj` files project files. Correct it in place.
```

Phase 1 in this loop is a single implement-and-test handoff, so the reporting obligation goes there once, not twice. Phase 4 is the fix phase. The index line keeps `"loop":"ultralight"` and gains `"walkthrough"`.

- [ ] **Step 5: Run the check and confirm it passes**

Run: `bash /tmp/check-task5.sh`
Expected: `PASS`

- [ ] **Step 6: Commit**

```bash
git add user/.claude/skills/dev-loop-lite/SKILL.md user/.claude/skills/dev-loop-ultralight/SKILL.md
git commit -m "Wire walkthrough skills into lite and ultralight loops"
```

---

### Task 6: Wire `dev-loop-ultra` and `dev-loop-ultra-opus`

**Files:**
- Modify: `user/.claude/skills/dev-loop-ultra/SKILL.md`
- Modify: `user/.claude/skills/dev-loop-ultra-opus/SKILL.md`

**Interfaces:**
- Consumes: the Phase 8b text from Task 4.
- Produces: nothing later tasks depend on.

These two loops delegate most phases to `dev-loop` by reference rather than restating them. Follow that existing style — do not paste Phase 8b in full where the file's convention is to reference it.

- [ ] **Step 1: Write the verification check**

```bash
A=user/.claude/skills/dev-loop-ultra/SKILL.md
B=user/.claude/skills/dev-loop-ultra-opus/SKILL.md
for f in "$A" "$B"; do
  grep -q '8b' "$f" || { echo "FAIL: $f does not mention Phase 8b"; exit 1; }
  grep -q 'walkthrough' "$f" || { echo "FAIL: $f does not mention the walkthrough"; exit 1; }
done
grep -q 'implementation-notes' "$A" || { echo "FAIL: ultra missing notes skill"; exit 1; }
grep -qF '## Phase 9' "$A" || { echo "FAIL: ultra phase 9 heading moved"; exit 1; }
echo PASS
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `bash /tmp/check-task6.sh`
Expected: `FAIL: ... does not mention Phase 8b`

- [ ] **Step 3: Edit `dev-loop-ultra`**

- In `## Phases 0 to 2 — Frame, implement, test`, add that Phase 0 invokes `implementation-notes` and that the implement and test briefs ask for decisions and rejected alternatives back, as `dev-loop` specifies.
- In `## Phase 5 — Triage`, add that the Interesting finds are appended to `notes.md` as in `dev-loop`, and add one ultra-specific line: **the adjudication logs are a source of interesting finds** — a finding prosecution raised and the adjudicator dropped, with its reason, is exactly the kind of near-miss a reviewer benefits from seeing.
- Insert a short `## Phase 8b — Walkthrough` section before `## Phase 9`, referencing `dev-loop` Phase 8b in full rather than restating it, and noting that the per-lane prosecution/defence/kept counts go into the notes' Reviewers section.
- In `## Phase 9`, add the `"walkthrough"` field alongside `"loop":"ultra"`.

- [ ] **Step 4: Edit `dev-loop-ultra-opus`**

This file's whole convention is "follow `dev-loop-ultra` in full; this file changes two things". Do not add a phase. Add one line to the opening paragraph confirming that the notes and walkthrough phases are inherited unchanged, and set the index field alongside `"loop":"ultra-opus"`.

- [ ] **Step 5: Run the check and confirm it passes**

Run: `bash /tmp/check-task6.sh`
Expected: `PASS`

- [ ] **Step 6: Commit**

```bash
git add user/.claude/skills/dev-loop-ultra/SKILL.md user/.claude/skills/dev-loop-ultra-opus/SKILL.md
git commit -m "Wire walkthrough skills into the ultra loops"
```

---

### Task 7: Sidekick agent files

**Files:**
- Modify: `user/.claude/agents/sidekick.md`
- Modify: `user/.claude/agents/sidekick-heavy.md`
- Modify: `user/.claude/agents/sidekick-lite.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the reporting behaviour Tasks 4–6 rely on in their briefs.

- [ ] **Step 1: Write the verification check**

```bash
for f in sidekick sidekick-heavy sidekick-lite; do
  p="user/.claude/agents/$f.md"
  grep -qi 'alternative' "$p" || { echo "FAIL: $f does not report alternatives"; exit 1; }
done
grep -q 'none considered' user/.claude/agents/sidekick-lite.md || { echo "FAIL: lite lacks the none-considered allowance"; exit 1; }
echo PASS
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `bash /tmp/check-task7.sh`
Expected: `FAIL: sidekick does not report alternatives`

- [ ] **Step 3: Add the clause to `sidekick.md` and `sidekick-heavy.md`**

Append to the section describing what the agent returns:

```markdown
**Report your reasoning, not only your result.** Alongside the summary of what
you changed, return the decisions you took, the alternatives you considered and
why you rejected them, and any constraint that forced a shape. The lead records
these; they become the walkthrough that ships with the PR, and a decision whose
alternatives were never written down cannot be explained to a reviewer later.
```

- [ ] **Step 4: Add the proportionate clause to `sidekick-lite.md`**

```markdown
**Report your reasoning, not only your result.** Return the decisions you took
and any alternative you considered and rejected. Mechanical work usually has
none — say `none considered` rather than inventing one. An honest "none" is
useful; a manufactured alternative is worse than silence.
```

- [ ] **Step 5: Run the check and confirm it passes**

Run: `bash /tmp/check-task7.sh`
Expected: `PASS`

- [ ] **Step 6: Commit**

```bash
git add user/.claude/agents/sidekick.md user/.claude/agents/sidekick-heavy.md user/.claude/agents/sidekick-lite.md
git commit -m "Ask sidekicks to report rejected alternatives"
```

---

### Task 8: README and installers

**Files:**
- Modify: `README.md`
- Modify: `install.ps1:60,95`
- Modify: `install.sh:67,99`

**Interfaces:**
- Consumes: the final skill folder count from Tasks 1–3 (9 folders).
- Produces: nothing.

- [ ] **Step 1: Write the verification check**

```bash
grep -q 'skills -lt 9' install.ps1 || { echo "FAIL: ps1 count not raised"; exit 1; }
grep -q '"$SKILLS" -lt 9' install.sh || { echo "FAIL: sh count not raised"; exit 1; }
grep -q '5 loops + solution-architecture' install.ps1 && { echo "FAIL: ps1 label stale"; exit 1; }
grep -q '5 loops + solution-architecture' install.sh && { echo "FAIL: sh label stale"; exit 1; }
grep -q 'pr-walkthrough' README.md || { echo "FAIL: README does not list the new skills"; exit 1; }
echo PASS
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `bash /tmp/check-task8.sh`
Expected: `FAIL: ps1 count not raised`

- [ ] **Step 3: Update both installers**

- `install.ps1:95` — `if ($skills -lt 6)` becomes `if ($skills -lt 9)`, and the message becomes "expected at least 9 skill folders".
- `install.sh:99` — `if [ "$SKILLS" -lt 6 ]` becomes `-lt 9`, same message change.
- `install.ps1:60` and `install.sh:67` — replace the label `skills (5 loops + solution-architecture)` with `skills (5 loops + solution-architecture + 3 walkthrough)`.

- [ ] **Step 4: Update the README**

- In the Layout block, add the three new skill folders under `user/.claude/skills/`.
- Change the agents/skills counts in that block's comment if it states one.
- Add a short subsection under *How a loop works* — four or five sentences — covering: notes accumulate through the run in the gitignored run directory; Phase 8b turns them into `docs/walkthroughs/<slug>.md`; the walkthrough explains why rather than what; and it is committed with the change and linked from the PR.
- Add `walkthrough` to the "What a run leaves behind" tree, showing `notes.md` inside the run directory and `docs/walkthroughs/` outside it.

- [ ] **Step 5: Run the check and confirm it passes**

Run: `bash /tmp/check-task8.sh`
Expected: `PASS`

- [ ] **Step 6: Commit**

```bash
git add README.md install.ps1 install.sh
git commit -m "Document walkthrough skills and raise installer counts"
```

---

### Task 9: Install and verify live

**Files:**
- No repo files modified. Writes to `~/.claude/`.

**Interfaces:**
- Consumes: Tasks 1–8.
- Produces: nothing.

- [ ] **Step 1: Run every earlier check together**

Run all eight check scripts. Expected: eight `PASS` lines. Do not install if any fails.

- [ ] **Step 2: Confirm no phase number regressed anywhere**

```bash
for f in dev-loop dev-loop-lite dev-loop-ultralight dev-loop-ultra dev-loop-ultra-opus; do
  echo "== $f"; grep -oE '^## Phase [0-9]+[a-z]?' "user/.claude/skills/$f/SKILL.md"
done
```

Expected: `dev-loop` and `dev-loop-lite` show 0–9 with 8b between 8 and 9; `dev-loop-ultralight` shows 0–6 with 5b between 5 and 6; the ultra files show their existing headings plus the new one. **No number that existed before may have changed.** Compare against `git show 11dbed4:user/.claude/skills/<f>/SKILL.md`.

- [ ] **Step 3: Run the installer**

```powershell
pwsh -NoProfile -File install.ps1
```

Expected: reports 22 agent files and 9 skill folders, no warnings.

- [ ] **Step 4: Confirm the live tree matches the repo**

```bash
for s in implementation-notes pr-walkthrough pr-walkthrough-review; do
  diff -r "user/.claude/skills/$s" "$HOME/.claude/skills/$s" && echo "OK $s"
done
```

Expected: three `OK` lines, no diff output.

- [ ] **Step 5: Report, do not merge or push**

Summarise what landed and leave the branch for review. The user has not asked for a merge or a push.

---

## Self-Review

**Spec coverage.** Skill 1 → Task 1. Skill 2 and exemplar → Task 2. Skill 3 → Task 3. Loop integration → Tasks 4, 5, 6, covering all five loops with ultralight's no-review-agent exception explicit and checked negatively. Tree-digest collision → Task 4 step 6 item 3, repeated in 5 and 6, and re-checked in Task 9 step 2. Sidekick files → Task 7. README and installers → Task 8. Hosting matrix → Task 2 step 3, checked for all three rows. Index field → checked in Tasks 4 and 5.

**Placeholder scan.** No TBDs. Every check step carries a runnable script; every insertion carries its exact text or an exact anchor plus the content required.

**Type consistency.** The `notes.md` H2 section names are fixed in Task 1 and consumed by name in Tasks 2 and 4–6. Phase heading strings are fixed as `## Phase 8b — Walkthrough` and `## Phase 5b — Walkthrough` and grepped with those exact strings, em dash included, in Tasks 4, 5 and 6.

**One known gap, deliberate.** Task 9 step 2 compares against commit `11dbed4`. If tasks are executed out of order or the baseline commit changes, substitute the SHA of the "Restore user-layer payload" commit.
