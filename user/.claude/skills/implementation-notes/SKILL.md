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

# Implementation notes

You are recording, not writing prose. Every entry answers "why", because "why"
is the one thing the rest of the run directory never captures.

## What this is for

The run directory already records *what happened*: `brief.md`, per-round
`plan.md`, findings JSON, `triage.md`, `run.md`. None of it records *why*, and
two gaps matter enough to fix:

1. **The implementer's rejected alternatives.** A sidekick weighs approaches and
   returns a summary of what it built. Nobody asks what it discarded, so those
   approaches are lost the moment the agent returns.
2. **Requirements-lane findings that were rejected at triage.** Triage records
   the rejection and moves on — but a rejected requirements finding still says
   something true about the brief: it was ambiguous here, or the reviewer read
   it differently than the implementer did. That is exactly the kind of "why" a
   reviewer needs later, and it is just as informative rejected as accepted.

Everything else this skill records is aggregation of material that already
exists elsewhere in the run. These two are not — skip this skill and both are
gone for good.

## Where it lives

`.claude/review/runs/<run-id>/notes.md`.

That location is deliberate: `.claude/review/runs/` is `.gitignore`d, so notes
never affect the working-tree digest the loop checks before every commit, and
they never ship. They are working material for `pr-walkthrough`, not a shipped
artifact. If you put notes anywhere else, the digest check will flag the
change it caused and the loop will stop to investigate a phantom.

## Append-only

Never rewrite an earlier entry. A note written at Phase 1, while a decision was
live, must still read that way after triage has second-guessed it — hindsight
belongs in a new entry, not edited into the old one. Rewriting collapses the
record of how the decision actually unfolded into how it looks now, which is
the one thing a walkthrough reader cannot get anywhere else.

## The five sections

`notes.md` has exactly five H2 sections, in this order. Use these headings
verbatim — `pr-walkthrough` reads the file by name, and a renamed heading is
invisible to it.

```markdown
## Frame
## Decisions
## Reviewers
## Interesting finds
## Open questions
```

What goes in each, and when it is written:

| Section | Written at | Contents |
| --- | --- | --- |
| Frame | Phase 0 | Requirement, non-goals, hard constraints, which loop was chosen and the specific eligibility criterion that chose it. Append the trigger here on any mid-run escalation. |
| Decisions | Phases 1, 2, 6 | One entry per meaningful decision, using the template below. |
| Reviewers | Phases 3–4 | Lanes run, lanes skipped with the diff-based reason, the model tier each ran at. For the ultra loops, also the prosecution/defence/kept counts. |
| Interesting finds | Phase 5 | See below. |
| Open questions | any phase | What the lead is genuinely unsure about. Carried into the walkthrough's closing section verbatim. |

## The decision entry template

```markdown
### <short title>
- **Decided:** what was done
- **Why:** the reason
- **Alternatives considered:** each one, and why it was rejected
- **Forced by:** the constraint that dictated the shape, or "nothing — free choice"
```

## The empty-alternatives rule

If *Alternatives considered* is genuinely empty, write `none considered`
explicitly. Do not leave it blank. A blank line is indistinguishable from a
decision nobody actually made — the walkthrough skill reads this file
mechanically and cannot tell "nothing to say" from "nobody filled this in".

## Interesting finds

Three kinds, in this order. The first is the point of the section:

1. **Requirements-lane findings, recorded whether accepted or rejected.** Every
   other lane's rejected findings are correctly dropped at triage. Requirements
   findings are not — record the finding, the triage decision, and the reason,
   because a rejected one is still a true statement about the brief.
2. **Accepted defect, rejected remedy.** Where triage agreed something was
   wrong but chose a smaller fix than the one suggested, record both and why.
   This is the single most useful thing to put in front of a reviewer who is
   about to ask "why not just wrap it".
3. **`conventions.md` entries created this run**, with the reasoning.

## Escalation

When a loop escalates mid-run — ultralight to lite, lite to full, and so on —
append the trigger to `## Frame`, not to a new section. A walkthrough for an
escalated change must be able to say plainly what forced the heavier loop, and
Frame is where the loop-choice reasoning already lives.
