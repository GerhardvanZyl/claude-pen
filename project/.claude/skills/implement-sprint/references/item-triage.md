# Item triage

How to decide, from a work item alone, whether to implement it and which dev
loop to use.

You are triaging from a description, not a diff. Every judgment here is a
prediction, and predictions from work item text run optimistic — items always
sound smaller than they are. **Bias heavy.** The item runner can escalate its
loop when reality turns out worse; it cannot de-escalate.

## Automatic skips

Skip and record the reason. Do not attempt these.

### By type

- Spike, Research, Investigation, Analysis — the output is knowledge, not a diff.
- Design, Architecture, Discovery — the output is a decision.
- Meeting, Ceremony, Admin, Documentation-only where no code changes.
- Epic and Feature — containers. Implement their children, not them.

### By state

- Closed, Resolved, Removed, Done.
- In Review, or anything with an open PR already linked.
- Blocked, or tagged as blocked.
- Assigned to someone other than the user, unless the user said otherwise.
  Someone else may already be working it.

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

## Recording the decision

For each item record: the loop assigned, the specific trigger that decided it,
and your confidence. A triage you cannot justify in one line is a triage to
re-do at the heavier tier.

When the item runner escalates a loop mid-run, that is a triage miss worth
noticing. One or two across a sprint is normal. A pattern means the criteria
above are being read too loosely — most often the "more than one project" and
"input from outside the application" triggers, which are easy to miss in an
item that does not mention them explicitly.
