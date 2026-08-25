# Item triage

How to decide, from a work item alone, whether to implement it, which dev loop
to use, and where it belongs in the run order.

You are triaging from a description, not a diff. Every judgment here is a
prediction, and predictions from work item text run optimistic — items always
sound smaller than they are. **Bias heavy.** The item runner can escalate its
loop when reality turns out worse; it cannot de-escalate.

This file uses the vocabulary table in `SKILL.md`. Where it says *item*, *state*,
*type* or *tag*, read your tracker's equivalent — Azure DevOps work items,
GitHub issues, Jira issues. The rules are the same on all of them.

## Automatic skips

Skip and record the reason. Do not attempt these.

### By type

- Spike, Research, Investigation, Analysis — the output is knowledge, not a diff.
- Design, Architecture, Discovery — the output is a decision.
- Meeting, Ceremony, Admin, Documentation-only where no code changes.
- Epic and Feature — containers. Implement their children, not them.

On trackers that have no type field, the type is whatever the labels and the
title say it is. A GitHub issue labelled `spike` is a spike; so is one titled
"Investigate why exports time out". Do not implement it because the field was
missing.

### By state

- Closed, resolved, removed, or done.
- In review, or anything with an open PR already linked.
- Blocked, or tagged as blocked.
- Assigned to someone other than the user, unless the user said otherwise.
  Someone else may already be working it.

State names differ per tracker and per team; match on meaning, not on spelling.
`Closed`, `Done`, `Complete` and a closed GitHub issue are the same signal. When
a state's meaning is genuinely unclear — a custom workflow with states like
`Ready` or `Committed` — ask once and record the answer in the skill's
Configuration section rather than guessing each run.

### By content

- No description and no acceptance criteria. There is nothing to implement
  against, and a brief invented from a title is how the wrong thing gets built.
- Acceptance criteria that are entirely non-functional or subjective with no
  measurable target ("improve performance", "make it cleaner").
- The item asks for a decision, an estimate, or an opinion rather than a change.
- The item depends on an external system, credential, or environment you cannot
  reach.

### By dependency

- A linked predecessor is in this sprint and has not completed successfully in
  this run. Skip for now and report it as deferred, not blocked.

### By supersession

- Another item in this run would delete, rewrite, or move everything this item
  produces, and reordering cannot avoid it. Report it as
  `superseded by <id>` — a proposal, not a decision. See below.

## Supersession

Two items in one sprint often touch the same code, and the order decides whether
the sprint pays for that work once or twice. Before the plan is confirmed, and
again before each item runs, read every pending item against every later one and
ask a single question:

> **Would doing this one first mean writing code the later one deletes,
> rewrites, or moves?**

### Signals

In rough order of how often each turns out to be real:

- Two items name the same component, screen, table, endpoint, or job.
- One item says *replace*, *rewrite*, *migrate*, *consolidate*, *retire*, or
  *redesign* something another item extends, fixes, or adds to.
- One item adds a field, column, or case to a structure another item reshapes.
- One item hardens, validates, or tests behaviour whose shape another item is
  about to change.
- Two items touch the same wiring point — DI registration, route table, migration
  chain, feature flag set, config schema.
- One item is described as cleanup or tech debt on code another item is building
  on. This one runs both ways: find out which is meant to land first.

Two items sharing a *noun* is a signal, not a verdict. "Both mention orders" is
common in a sprint about orders. What matters is whether one changes the shape of
what the other assumes.

### What to do about each case

| Situation | Do this |
| --- | --- |
| Reordering resolves it | Reorder, and record `order_reason` on the item that moved. |
| The earlier item is entirely contained in the later one | Propose skipping it as `superseded by <id>`. The user decides, not you. |
| They conflict outright — both change the same thing incompatibly | Run neither. Report both and ask which one is current. |
| Reordering would break a dependency | Dependency wins. Say in the plan that rework is expected, and where. |
| You cannot tell whether they collide | Treat it as supersession. Put the structural item first. |

**Never merge two items into one implementation.** They are tracked, reviewed,
and reverted separately. If they truly are one piece of work, say so and let a
human close one.

### Detecting it late

After an item completes you have `files_changed` — real paths, not a prediction.
Compare them against what the remaining items are expected to touch. A completed
item whose paths sit inside the area a pending item is about to restructure is a
supersession the plan missed, and the remaining order should change.

A supersession caught here rather than at plan time is worth recording in the
run summary. The signal that caught it late was almost always present in the item
text at plan time, and knowing which one was missed is how the list above gets
better.

## Loop assignment

Read the description and acceptance criteria for what the change will **touch**,
not for how big it sounds.

### Full `dev-loop` — assign if any of these appear

- Authentication, authorization, permissions, roles, or access rules.
- Secrets, credentials, tokens, connection strings, or certificates.
- Any input arriving from outside the application.
- A database migration, schema change, or new table or column.
- A public API contract, an integration surface, or a message or event schema.
- Concurrency, async ordering, locking, retries, idempotency, or transaction
  boundaries.
- More than one project in the solution.
- A new package or dependency.
- Anything described as a rewrite, a redesign, or a cross-cutting change.
- The item is a bug whose cause is not yet understood. Root-cause hunting is a
  chain of judgments; give it the full loop.

### `dev-loop-lite` — assign when

The change is contained within one project, none of the full-loop triggers are
present, but it is more than trivial: new behaviour, a new type, a refactor of
several call sites, or a bug with a known cause and a non-obvious fix.

**This is the default.** When in doubt between lite and ultralight, choose lite.

### `dev-loop-ultralight` — assign only when all of these hold

- One project, and you can name the roughly five or fewer files involved.
- No full-loop trigger anywhere in the item.
- The behaviour change is described precisely enough that you could write the
  acceptance test from the item alone.
- It is easy to roll back.

Typical: a copy or label change, a validation message, a config default, a
single-method bug with an obvious fix, adding a field that is already plumbed
through.

**If you find yourself reasoning about why an item is *probably* fine for
ultralight, it is not.** Ultralight's safety comes entirely from its eligibility
being obvious. An eligibility argument is a disqualification.

## Re-triaging mid-run

An item's text can change after the plan is confirmed. When the re-poll reports
that a not-yet-run item was edited, run it through this file again from the new
text — do not carry the old assignment forward on the grounds that the item is
"the same item". It has the same ID and a different specification.

Two outcomes force a checkpoint before that item runs: the loop assignment
changed, or the brief you would now build differs materially from the one the
user confirmed.

## Recording the decision

For each item record: the loop assigned, the specific trigger that decided it,
its position and — where that position is not simply rank — the ordering reason.
A triage you cannot justify in one line is a triage to re-do at the heavier tier.

When the item runner escalates a loop mid-run, that is a triage miss worth
noticing. One or two across a sprint is normal. A pattern means the criteria
above are being read too loosely — most often the "more than one project" and
"input from outside the application" triggers, which are easy to miss in an
item that does not mention them explicitly.
