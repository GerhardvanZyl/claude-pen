---
name: dev-loop-ultra
description: >
  The adversarial review loop. Same nine review lanes as dev-loop, but every lane
  is reviewed twice by opposed reviewers — one optimised for recall, one for
  precision — and reconciled by a third that produces the lane's single
  authoritative finding set. Same model tiers as dev-loop. Use when asked for an
  ultra run, or when the user types /dev-loop-ultra. Roughly three times the
  review cost of dev-loop; reserve it for changes where a missed defect is
  expensive.
---

# Development and review loop — ultra

You are the lead. Same shape as `dev-loop`, with every review lane run as an
adversarial triple instead of a single pass.

Lane definitions live in `dev-loop/references/review-lanes.md`. The cards are
shared — ultra changes who reads them and how many times, not what they say.

`dev-loop/references/tree-snapshot.md` is shared too: the working-tree digest,
the integrity check, and the scratch worktree the Tests lane's pair needs. You
run those commands; reviewers never do.

## Why three agents per lane

A single reviewer has one error profile: whatever it is disposed to miss, it
misses consistently, and running it again changes nothing. Two reviewers on
**opposed assumptions** have different profiles — prosecution assumes the code is
broken and optimises for recall; defence assumes it is correct and optimises for
precision. Their disagreements are where the real information is, and the
adjudicator's job is to extract it by checking the code itself.

Both reviewers run blind to each other. Neither output is ever used directly.

## When to use this loop

Ultra costs roughly three times a full run's review. Use it when a missed defect
is expensive rather than merely annoying:

- Changes to payment, billing, or anything that moves money or goods.
- Auth, permissions, or data isolation between tenants or users.
- Migrations that alter or destroy existing data.
- Integration contracts other systems depend on.
- Anything shipping where rollback is slow or costly.
- Code you are handing over and will not maintain.

For everything else, `dev-loop` is the right default. Ultra applied everywhere is
not thoroughness, it is expense.

## Phases 0 to 2 — Frame, implement, test

Identical to `dev-loop`. Frame the slice, record the source branch, write
`brief.md`, then implement and test in two handoffs at the normal sidekick tiers.
**Implementation is not changed by this loop** — ultra buys scrutiny, not code.

Phase 0 also invokes the `implementation-notes` skill and creates `notes.md`, as
`dev-loop` specifies. The implement and test briefs in Phases 1 and 2 ask for the
decisions taken and the alternatives rejected back, and the lead appends what
comes back to `notes.md` — same requirement, same file, same two handoffs.

## Phase 3 — Plan the round

Set `ROUND`, starting at 1. Create `round-N/`. Classify each lane applicable or
skipped with a diff-based reason and write `round-N/plan.md`, using the same
applicability table as `dev-loop`.

**Then snapshot the tree and set up the scratch worktree**, per
`dev-loop/references/tree-snapshot.md` — digest into `plan.md` as `tree: <sha>`.
Then make the round snapshot commit, every round regardless of the Tests lane,
and record it in `plan.md` as `snapshot: <sha>` — this is the round base the
next round hands every lane. Set up the scratch worktree at `round-N/scratch`,
from that commit, for the Tests lane's pair. Retake and compare **after each
pair of lanes drains**, not only at the end of the round: with eighteen-plus
agent runs against one tree, finding out at the end that it moved means
re-running far more than one lane.

The two scopes work exactly as `dev-loop` Phase 3 defines them: the **change
base** is the Phase 0 diff base and is what findings are raised against; the
**round base**, from round 2, is the previous round's snapshot commit and
shows what the last round's fixes changed. Applicability is still computed
from the fix delta alone; scope is the whole change plus the round base,
regardless of why a lane was rerun. Here that applies per agent, not per lane:
**all three agents in a lane get both bases, the adjudicator included.** An
adjudicator reconciling from a narrower diff than its reviewers used would
discard a true finding about earlier-round code as out of scope, on the
mistaken assumption that the reviewers were bounded to the delta.

## Phase 4 — Adversarial review

For each applicable lane, three agents in sequence:

1. `reviewer-ultra-prosecution` and `reviewer-ultra-defence` **in parallel**.
2. When both have returned, `reviewer-ultra-adjudicator` for that lane.

Pass each agent the lane card name and path, the run directory and round,
**both scopes** — the change base and, from round 2, the round base — and the
brief path. Pass the adjudicator both reviewers' output paths, and the same two
scopes.

### Model per lane, passed per invocation

The agent files carry a neutral default. **Override the model per invocation** so
each lane runs at the tier `dev-loop` gives it. All three agents in a lane use
the same tier.

| Lane | Model | Effort |
| --- | --- | --- |
| requirements | opus | high |
| technical | opus | xhigh |
| architecture | opus | xhigh |
| security | opus | xhigh |
| standards | sonnet | high |
| tests | sonnet | high |
| deadcode | sonnet | high |
| minimalism | sonnet | high |
| artifacts | sonnet | high |

**Model is overridable per invocation; effort is not.** The Agent tool takes a
`model` parameter and has no `effort` parameter, so the effort column above is
not something you can pass — it is the value that must be *declared in the agent
file* for the lane to run as specified. Two consequences, and you need both:

- **Pass `model` on every spawn.** If you cannot — the tool is unavailable, the
  parameter is rejected — **stop and say so** rather than running every lane at
  the agent file's default. A technical lane silently reviewed at Sonnet is not
  the loop the user asked for.
- **Effort comes from the agent file, and the three ultra agents declare
  `high`.** So the four Opus lanes in the table above get Opus at `high`, not at
  `xhigh`. Say this plainly in `run.md` rather than reporting a tier the run did
  not have. If a lane genuinely needs Opus at `xhigh`, that is what
  `dev-loop-ultra-opus` is for — it raises the declared effort rather than
  pretending the parameter exists.

Do not attempt to work around this by editing the agent files mid-run. A loop
that rewrites its own reviewers between lanes is not comparable to any other
run, which defeats the point of the index line.

### Concurrency

**Two lanes at a time, four reviewers in flight.** Run both reviewers for two
lanes, let them drain, run those two adjudicators, then the next pair of lanes.
Nine lanes at once would put eighteen agents in flight and hit concurrency
limits long before it saved wall-clock.

### What you read

Only the adjudicator's output. Never the prosecution or defence files — they are
inputs to adjudication, not to you, and reading them re-introduces into your
context exactly the noise the adjudicator was paid to remove.

## Phase 5 — Triage

Identical to `dev-loop` — cluster by locator, gate on evidence and cause,
separate defect from remedy, check `wontfix.json`, record durable decisions in
`.claude/review/conventions.md`, write `round-N/triage.md`.

One addition: read each lane's adjudication log for its **coverage** line. A lane
reported as "both thin" was not really reviewed, whatever its findings file says.
Rerun that lane before trusting the round.

The Interesting finds appended to `notes.md` are also as `dev-loop` specifies.
Ultra has a source the single-pass loops do not: **the adjudication logs**. A
finding prosecution raised and the adjudicator dropped, with its reason, is
exactly the kind of near-miss worth telling a reviewer about — append it.

## Phase 6 — Fix

Identical to `dev-loop`. Accepted findings to a sidekick, regression test written
and confirmed failing before each fix that would have been a bug.

## Phase 7 — Loop or exit

Identical bounds to `dev-loop`: three rounds maximum, stop on a concern raised
and fixed twice, on no material progress, or when completion needs clarification
or redesign.

In round 2 and later, rerun only lanes that owned accepted findings, plus any the
fixes newly made applicable — as full triples, not single passes. A lane worth
rerunning is worth rerunning properly.

**`dev-loop`'s rule that the technical lane always reruns after a
behaviour-changing fix applies here too**, as a full triple like any other. It is
easy to lose when the reasoning is about which lane owned which finding: a fix
can break something no lane raised, which is exactly the case that rule exists
for, and the adversarial pair does not make it less likely.

## Phase 8 — Verification

Spawn `reviewer-verify` as `dev-loop` specifies. Adversarial review does not
replace it: the pair checks the code, verification checks that the accumulated
fixes still do what was asked.

## Phase 8b — Walkthrough

As `dev-loop` Phase 8b in full: invoke `pr-walkthrough` off `notes.md`, invoke
`pr-walkthrough-review`, then retake the snapshot and record it as the new
baseline whether or not a walkthrough was written. One addition: the per-lane
prosecution/defence/kept counts go into the notes' Reviewers section, alongside
the lanes run, lanes skipped, and model tiers `dev-loop` already puts there.

## Phase 9 — Commit, push, pull request

As `dev-loop` Phase 9 in full — **including the staging and commit-verification
steps.** Stage untracked files explicitly, confirm the committed diff matches the
reviewed file list, push, and confirm the PR's file list matches. Three agents per
lane approved a working tree; none of them approved a commit.

Use `"loop":"ultra"` and `"walkthrough"` — the committed path, or
`skipped:<reason>` — in the index line, and state in the PR description that this
was an adversarial run.

The work-tracker rule in `dev-loop` applies unchanged: no item creation, state
change, or merge unless the user asked for it, and a specific instruction covers
one run only.

## Formats and logging

Findings, logs, and the index line use exactly the `dev-loop` formats.

Per lane you get **six files** — three findings files and three logs:

| File | Written by | Read by |
| --- | --- | --- |
| `<lane>.prosecution.json` | prosecution | the adjudicator, never you |
| `<lane>.defence.json` | defence | the adjudicator, never you |
| `<lane>.json` | adjudicator | **your triage — the lane's authoritative set** |
| `<lane>.prosecution.log.md` | prosecution | the adjudicator |
| `<lane>.defence.log.md` | defence | the adjudicator (its dismissals decide keeps) |
| `<lane>.adjudication.log.md` | adjudicator | you, for the coverage line |

Add to the index line, per lane: `{"raised_p":n,"raised_d":n,"kept":n}`. That
ratio is the health signal for this loop:

- Prosecution raising many and few surviving → it is running hot, or defence's
  dismissals are being accepted too readily.
- Defence raising almost nothing across several runs → it has drifted into
  agreeableness, which is the pair's most common failure and the hardest to see,
  because it looks like clean code.
- Both agreeing on nearly everything → the stances are not actually opposed and
  you are paying three times for one reviewer's opinion.
