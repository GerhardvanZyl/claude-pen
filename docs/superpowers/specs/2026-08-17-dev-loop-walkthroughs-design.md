# Walkthrough skills for the dev loops — design

**Date:** 2026-08-17
**Branch:** `feature/walkthrough-skills`
**Status:** approved, ready to plan

## Goal

Every dev loop currently ends at a PR whose description says *what* changed. The
reasoning that produced the change — the alternatives weighed and discarded, the
constraint that forced a shape, the reviewer finding that changed the design — is
never written down and dies with the run.

Add three skills that capture it, turn it into a reviewer-facing document, and
check that document is worth reading. Wire them into all five loops.

## The problem the notes skill actually solves

The run directory already records a great deal: `brief.md`, per-round `plan.md`,
findings JSON, `triage.md`, `run.md`. All of it answers *what happened*.

Two things it does not record, and both are the walkthrough's raw material:

1. **The implementer's rejected alternatives.** A sidekick weighs approaches and
   returns a summary of what it built. The approaches it discarded are never
   asked for, so they are lost the moment the agent returns.
2. **Requirements-lane findings that were rejected.** Triage records the
   rejection and its reason, then the finding is dropped. But a requirements
   finding is a statement that the brief was ambiguous, or that the change
   over- or under-reached — which is precisely the "why" a reviewer needs, and it
   is just as informative when rejected as when accepted.

The notes skill exists to close both gaps. Everything else it records is
aggregation of material that already exists.

---

## Skill 1 — `implementation-notes`

**Trigger:** invoked at Phase 0 by every loop; also `/implementation-notes`.

**Writes:** `.claude/review/runs/<run-id>/notes.md`.

That location is deliberate. `.claude/review/runs/` is `.gitignore`d, so the
notes are invisible to the working-tree digest (see *Tree-digest collision*
below) and are never committed. They are working material for the walkthrough,
not a shipped artifact.

**Append-only**, at defined points across the phases. Never rewritten wholesale —
a note added at Phase 1 must still read as it did when the decision was live,
not as it looks with hindsight after triage.

### Sections

| Section | Written at | Contents |
| --- | --- | --- |
| Frame | Phase 0 | Requirement, non-goals, hard constraints, **which loop was chosen and the specific eligibility criterion that chose it**. Appended to on any mid-run escalation, recording the trigger. |
| Decisions | Phases 1, 2, 6 | One entry per meaningful decision. |
| Reviewers | Phases 3–4 | Lanes run, lanes skipped with the diff-based reason, the model tier each ran at. For ultra loops, also the prosecution/defence/kept counts. |
| Interesting finds | Phase 5 | See below. |
| Open questions | any phase | What the lead is genuinely unsure about. Carried into the walkthrough's closing section verbatim. |

### A decision entry

```markdown
### <short title>
- **Decided:** what was done
- **Why:** the reason
- **Alternatives considered:** each one, and why it was rejected
- **Forced by:** the constraint that dictated the shape, or "nothing — free choice"
```

**Rule:** an entry whose *Alternatives considered* is empty must say
`none considered` explicitly. A blank line is indistinguishable from a decision
nobody actually made, and the walkthrough skill cannot tell the difference later.

### Interesting finds

Three kinds, and the first is the point of the section:

1. **Requirements-lane findings — recorded whether accepted or rejected.** Every
   other lane's rejected findings are correctly dropped at triage. Requirements
   findings are not, because a rejected one still says something true about the
   brief: it was ambiguous here, or the reviewer read it differently than the
   implementer did. Record the finding, the triage decision, and the reason.
2. **Accepted defect, rejected remedy.** Where triage agreed something was wrong
   but chose a smaller fix than the one suggested, record both and why. This is
   the single most useful thing to put in front of a reviewer who is about to ask
   "why not just wrap it".
3. **`conventions.md` entries created this run**, with the reasoning.

---

## Skill 2 — `pr-walkthrough`

**Trigger:** the new walkthrough phase in every loop; also `/pr-walkthrough`.

The user-supplied draft of this skill is the base. Two changes make it
repo-agnostic, and one makes it delegable.

### Change 1 — the exemplar

The draft points at one internal repository's walkthrough as a mandatory-read
worked example. That file exists in one repository; this skill runs in any.
Resolution, in order:

1. The most recently modified file in this repo's `docs/walkthroughs/`, if any.
2. Otherwise the bundled `references/example-walkthrough.md`, shipped with the
   skill.

The bundled exemplar must be written against a **fictional, generic** codebase —
not an internal one. Its job is to demonstrate the format and the density of
"why", so it must contain real rejected alternatives and a real open question,
not lorem-ipsum standing in for them.

### Change 2 — authoring is delegated

The draft warns that a delegated draft comes back as a narrated diff. That is
true when the brief is the diff. It is not true when the brief is `notes.md`,
which is nothing but reasons.

So: **delegate the draft to `sidekick`**, passing the notes path, the diff base,
and the changed-file list. The lead then reads the draft for "why" content before
it ships. This keeps the work inside the delegation policy instead of fighting
it, and it is the thing that makes skill 1 load-bearing rather than decorative.

If `notes.md` is missing or thin, the walkthrough cannot be delegated — the lead
writes it, and records in `run.md` that the notes were inadequate. That is a
defect in the run worth seeing.

### Change 3 — opening diagrams

Per the user's addendum: the document opens with a Mermaid **architecture**
diagram showing where the change sits in the system, then the **sequence**
diagram of the changed flow. Both before the change table.

### Structure

Unchanged from the draft, with the diagrams prepended:

1. Opening paragraph — story, branch/PR/commit, explicit out-of-scope.
2. Architecture diagram + sequence diagram.
3. Change table — one row per file, with noise rows marked "ignore this".
4. The flow, entrypoint down to the changed code.
5. The decisions, file by file, ordered by the flow.
6. Where to look to review this — priority order, line ranges, commit-anchored.
7. Tests.
8. Open questions.

### Where it goes, per hosting

| Host | Path | Link |
| --- | --- | --- |
| GitHub | `docs/walkthroughs/<slug>.md`, committed on the story branch | Relative link in the PR body |
| Azure DevOps | same | ADO does not render bare relative paths in a PR description. Use the full form: `<org>/<project>/_git/<repo>?path=/docs/walkthroughs/<slug>.md&version=GB<branch>` |
| No repository | `docs/walkthroughs/<slug>.md` in the working folder | No PR exists. Report the absolute path to the user in chat and record it in `run.md`. Anchors carry file+line with no commit hash, and the opening paragraph says so, because line numbers will drift with nothing to pin them to. |

Detect the host from the remote: `github.com` → GitHub, `dev.azure.com` or
`visualstudio.com` → ADO, no remote or no repository → the third row.

### Skip rule

A purely mechanical change — a rename, a dependency bump, a formatting sweep —
has no "why" worth a document. Skipping is permitted and must be **reported** in
the PR description and in `run.md`, never silent.

---

## Skill 3 — `pr-walkthrough-review`

**Trigger:** the walkthrough phase in `dev-loop`, `dev-loop-lite`,
`dev-loop-ultra`, `dev-loop-ultra-opus`. **Not `dev-loop-ultralight`** — there
the lead checks the draft inline against the same criteria.

**Write-capable on the walkthrough file only.** The read-only reviewer convention
exists to protect the code under review; this document is authored after every
lane has drained, is not code, and the phase retakes the tree baseline afterwards
regardless. So the draft's "correct it if it doesn't" is safe to implement
literally.

### Checks

From the user's draft:

- Written for a senior engineer with basic project knowledge — explains what is
  specific to this codebase, explains nothing about the language or framework.
- Explains reasoning, not changes. A section that survives deleting the words
  "why" and "because" is a changelog entry and gets rewritten.
- Concise; no tangents.
- Reads well aloud, for a voice model.
- Calls `.sln` files "solution files" and `.csproj` files "project files".
- Well structured, entrypoint-first, following execution flow.

Added, because they are cheap and catch real breakage:

- **Every cited anchor is real.** Spot-check the line numbers against the files.
  A walkthrough with invented line numbers is worse than none.
- **Every Mermaid block parses**, and the architecture and sequence diagrams are
  both present.

**Returns one line** to the lead: path, whether it edited, and the count of
issues corrected by category. The lead does not read the whole document into
context to find out whether it is good.

---

## Loop integration

Identical in all five loops. **No existing phase number changes** — `dev-loop-ultra`
and `dev-loop-ultra-opus` both cross-reference "`dev-loop` Phase 9" by number, and
renumbering would silently break those references. The new work goes in a lettered
sub-phase.

| Loop | New phase | Sits between |
| --- | --- | --- |
| `dev-loop` | 8b | Phase 8 verification and Phase 9 commit |
| `dev-loop-lite` | 8b | Phase 8 verification and Phase 9 commit |
| `dev-loop-ultra` | 8b | inherited from `dev-loop`, stated explicitly |
| `dev-loop-ultra-opus` | 8b | inherited from `dev-loop-ultra`, stated explicitly |
| `dev-loop-ultralight` | 5b | Phase 5 exit and Phase 6 commit |

### Edits per loop

**Phase 0** — invoke `implementation-notes`; create `notes.md`; record the loop
chosen and the eligibility criterion that chose it.

**Phases 1, 2 and 6 (implement, test, fix)** — the brief must require the
sidekick to return, alongside its summary, the decisions it took, the
alternatives it rejected and why, and any constraint that forced a shape. The
lead appends what comes back to `notes.md`. State this in the phase text, not
only in the agent files.

**Phases 3–4** — append lanes run and skipped, with tiers, to the Reviewers
section.

**Phase 5 (triage)** — append the Interesting finds, including
requirements-lane findings that were rejected.

**New walkthrough phase** — three steps, in order:

1. Invoke `pr-walkthrough`. Delegate the draft to `sidekick` with `notes.md`.
2. Invoke `pr-walkthrough-review` (all loops except ultralight; there the lead
   checks inline).
3. **Retake the working-tree snapshot and record it as the new baseline** for the
   commit phase's digest check. The only legitimate delta from the previous
   baseline is the walkthrough file itself; anything else is the same failure the
   digest check has always been for, and is treated the same way.

**Commit phase** — the walkthrough is staged and committed with the change
(unlike the run directory, which stays excluded). The digest comparison uses the
baseline from the walkthrough phase, not the one from the last fix round. The PR
description links the walkthrough, per the hosting table.

**`run.md` and `index.jsonl`** — one new field:

```json
"walkthrough": "docs/walkthroughs/<slug>.md"
```

or `"walkthrough": "skipped:<reason>"`. All five loops write it identically; the
loops are emphatic that a shared format is what makes runs comparable.

### Tree-digest collision — the reason step 3 exists

`references/tree-snapshot.md` computes the digest over tracked *and untracked*
files, honouring `.gitignore`. `.claude/review/runs/` is ignored, so `notes.md`
never affects it.

`docs/walkthroughs/<slug>.md` is **not** ignored. Authoring it after the final
round changes the digest, and the commit phase's rule — *"if they differ,
something changed the tree between the last review and the commit. Stop and find
out what moved"* — would halt on every single run. Retaking the baseline in the
walkthrough phase is not bookkeeping; without it the loops do not complete.

---

## Sidekick agent files

`sidekick.md`, `sidekick-heavy.md`, `sidekick-lite.md` each gain one short
clause: report back, alongside the summary, the decisions taken, the alternatives
rejected and why, and any constraint that forced a shape.

Belt and braces with the phase text: the obligation survives a terse brief, and
it improves handoffs outside the dev loops too.

`sidekick-lite.md` gets a proportionate version — mechanical work usually has no
alternatives, and it should say `none considered` rather than manufacture some.

---

## File manifest

New:

```
user/.claude/skills/implementation-notes/SKILL.md
user/.claude/skills/pr-walkthrough/SKILL.md
user/.claude/skills/pr-walkthrough/references/example-walkthrough.md
user/.claude/skills/pr-walkthrough-review/SKILL.md
```

Modified:

```
user/.claude/skills/dev-loop/SKILL.md
user/.claude/skills/dev-loop-lite/SKILL.md
user/.claude/skills/dev-loop-ultralight/SKILL.md
user/.claude/skills/dev-loop-ultra/SKILL.md
user/.claude/skills/dev-loop-ultra-opus/SKILL.md
user/.claude/agents/sidekick.md
user/.claude/agents/sidekick-heavy.md
user/.claude/agents/sidekick-lite.md
README.md
install.ps1
install.sh
```

`README.md` needs the three skills in its layout section and a short section on
the walkthrough.

Both installers need two edits each, and the second is easy to miss:

- The post-install assertion `-lt 6` (`install.ps1:95`, `install.sh:99`) rises
  to 9 — six existing folders plus three new ones.
- The label string `skills (5 loops + solution-architecture)`
  (`install.ps1:60`, `install.sh:67`) is printed to the user during install and
  would otherwise keep describing a payload that no longer matches.

## Definition of done

- The three skills exist with valid frontmatter and are discoverable by name.
- All five loops invoke notes at Phase 0, carry the reporting obligation in their
  implement/test/fix phases, and have the walkthrough sub-phase including the
  baseline retake.
- No existing phase number in any loop has changed.
- The hosting table appears in `pr-walkthrough` and covers GitHub, ADO and no
  repository.
- The bundled exemplar is generic, and contains genuine rejected alternatives.
- Installer counts updated; `install.ps1` and `install.sh` agree.
- README layout and skill list match what is on disk.

## Out of scope

The loops are git-based end to end — snapshot, scratch worktree, commit, push,
PR. **A project with no repository cannot run them as written today**, and fixing
that is a much larger change than this one. The no-repository row in the hosting
table governs where the walkthrough is written and how it is delivered; it does
not make the loops themselves runnable without git.

The project layer (`project/.claude/`: `sprint-item-runner`, `coding-standards`,
`implement-sprint`, the hook script) is missing from this repo and is not
restorable from `~/.claude`. Left alone.
