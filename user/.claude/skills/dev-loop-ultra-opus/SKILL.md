---
name: dev-loop-ultra-opus
description: >
  The adversarial review loop with every subagent on Opus. Identical to
  dev-loop-ultra in structure — nine review lanes, each reviewed by an opposed
  pair and reconciled by an adjudicator — but no lane is tiered down to Sonnet. Use when
  asked for an ultra-opus run, or when the user types /dev-loop-ultra-opus. The
  most expensive loop available; reserve it for changes where being wrong is
  worse than being slow.
---

# Development and review loop — ultra, all Opus

**Follow the `dev-loop-ultra` skill in full.** Every phase, bound, format, and
rule is the same. This file changes two things and nothing else.

Read `dev-loop-ultra/SKILL.md` now and work from it. Do not reimplement its
phases from this file. That includes Phase 0's `implementation-notes` and Phase
8b's walkthrough — both are inherited unchanged.

## Change 1 — Every subagent runs on Opus

Override the per-invocation model for **all** agents in the loop, not only the
review lanes:

| Agent | Model | Effort — and where it comes from |
| --- | --- | --- |
| `reviewer-ultra-prosecution` | opus (passed) | `high`, declared in the agent file |
| `reviewer-ultra-defence` | opus (passed) | `high`, declared in the agent file |
| `reviewer-ultra-adjudicator` | opus (passed) | `high`, declared in the agent file |
| `reviewer-verify` | opus (its own default) | `high`, declared in the agent file |
| Implementation sidekick | `sidekick-heavy` | `xhigh`, declared in that agent file |
| Test-writing sidekick | `sidekick-heavy` | `xhigh` |
| Fix sidekick | `sidekick-heavy` | `xhigh` |

The lane table in `dev-loop-ultra` is superseded in one respect only: **no lane
drops to Sonnet.** Every reviewer runs on Opus.

**Effort is not raised, because it cannot be passed.** The Agent tool has a
`model` parameter and no `effort` parameter, so a lane's effort is whatever its
agent file declares — `high` for all three ultra reviewers. This loop buys a
uniformly higher *model* tier, not a higher effort tier. Say that in `run.md`
rather than reporting `xhigh` lanes the run did not have.

The sidekicks are the exception, and not by accident: `sidekick-heavy` is a
distinct agent file that declares `effort: xhigh` itself, so routing to it gets
you both. That is the pattern to follow if xhigh reviewers are ever wanted —
dedicated agent files, not a parameter that does not exist.

**Implementation is on Opus here too**, unlike every other loop. If you are
paying for adversarial review at this tier, having the code written a tier below
the reviewers is a false economy.

If you cannot pass a model per invocation, **stop and say so.** Silently running
this loop at default tiers gives the user the cost profile they did not ask for
and the scrutiny they did.

## Change 2 — Concurrency drops to one lane at a time

Two Opus reviewers at `xhigh` plus an adjudicator is already a heavy concurrent
load. Run **one lane at a time**: prosecution and defence in parallel, then that
lane's adjudicator, then the next lane.

This makes ultra-opus considerably slower in wall-clock than `dev-loop-ultra`.
That is the trade being made; do not widen the concurrency to recover it.

## When this loop is justified

`dev-loop-ultra` already covers changes where a missed defect is expensive. Reach
past it to this one only when the cost of being wrong is severe and largely
irreversible:

- A migration that alters or destroys production data.
- Auth or tenant-isolation logic where a defect exposes other people's data.
- Money movement, settlement, or anything with a regulatory consequence.
- A contract other organisations build against and cannot easily be asked to
  change.
- Code being handed to someone who will not be able to fix it.

For anything less, `dev-loop-ultra` is the honest choice, and `dev-loop` is the
honest default. Escalating past the point where the loop changes the outcome is
spending, not diligence.

## Index line

`"loop":"ultra-opus"`. Keep the same per-lane `raised_p` / `raised_d` / `kept`
counts and the same `"walkthrough"` field — comparing those against `ultra` runs
is how you find out whether the Opus lanes actually change the findings or only
the bill. That is worth knowing, and nobody can tell you without the data.
