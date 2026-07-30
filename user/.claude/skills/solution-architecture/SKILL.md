---
name: solution-architecture
description: >
  How to establish and apply a solution's architecture — separation of concerns,
  dependency direction, and responsibility placement — in any repository, by
  discovering or inferring the architecture that is actually in force rather than
  assuming one. Use when writing code, deciding where a new type belongs, or
  reviewing structure and placement.
---

# Solution architecture

This skill is repository-agnostic. It does not describe any particular
solution's architecture — it tells you how to find out what a solution's
architecture is, and how to judge code against it.

**Never apply a remembered or textbook architecture to a repository you have not
established the architecture of.** Doing so produces confident, wrong findings
that propose restructuring working code.

## The rule that outranks the rest

**Separation of concerns.** One type, one kind of work. When a structural
finding conflicts with a separation-of-concerns finding, separation of concerns
wins.

Concerns worth keeping apart, in roughly the order that violations hurt:

- Business rules versus everything else.
- Persistence versus domain.
- Presentation and transport versus both.
- Orchestration and sequencing versus the work being sequenced.
- Cross-cutting concerns — logging, retries, caching, auth, validation — versus
  the code they wrap.

This part is universal. Everything below it is discovered per repository.

## Establishing the architecture in force

Work through these in order and stop at the first that gives you a clear answer.
Record which tier you reached — it determines how strongly you may state a
finding.

### Tier 1 — Documented

Search for, in this order:

- `ARCHITECTURE.md`, `docs/architecture*.md`, `docs/adr/**`, `doc/**/*arch*`
- `policies/**/*.md`, excluding `README.md` and `policy-template.md`
- A `## Architecture` section in the root `README.md` or `CONTRIBUTING.md`
- Any architecture description in `CLAUDE.md` or `AGENTS.md`

A discovered repository document **supersedes** anything in this skill that
governs substantially the same concern, even where names and wording differ. A
narrower local document supplements rather than replaces. Where two local
documents disagree, the more specific and more recently modified wins; say that
you had to choose.

### Tier 2 — Structurally evident

For .NET solutions the dependency graph is a fact, not an opinion. Derive it:

```bash
# Projects in the solution
dotnet sln list

# The actual dependency graph — this is the layering, whatever any doc claims
grep -r "ProjectReference" --include=*.csproj .
```

From that graph, read off: which project depends on which, which project depends
on nothing (that is the domain, whatever it is named), and which sit at the
edges. Then confirm against the folder structure inside each project, the
namespace layout, and the package references — a project referencing an ORM or
an HTTP client is infrastructure regardless of its name.

For other stacks the equivalents are the module or package manifests, the
import graph, and the build targets.

**Where a document and the reference graph disagree, the graph is what is in
force.** Report the conflict; do not silently pick one.

### Tier 3 — Inferred from convention

No document, no clear structure. Read three to five existing examples of the
same kind of thing the diff adds — three existing controllers, three existing
handlers, three existing repositories — and derive the convention from what they
consistently do.

Three consistent examples is a convention. Two is a coincidence. One is not
evidence of anything.

### Tier 4 — Nothing establishable

Say so and review separation of concerns only. Do not invent a layering to
judge against.

## How the tier constrains your findings

This maps onto the `evidence` field the review loop already uses, and it is the
main safeguard against confident nonsense:

| Tier | `evidence` | Strongest severity |
| ---- | ---------- | ------------------ |
| 1 — documented | `policy` | Critical |
| 2 — structurally evident | `direct` | Critical |
| 3 — inferred from convention | `inferred` | **Minor** — inferred evidence alone is never a blocker |
| 4 — nothing establishable | `inferred` | Minor, and separation of concerns only |

A repository that documents its architecture gets its architecture enforced. One
that does not gets advice. That gradient is deliberate — it is also the cheapest
argument for writing the document.

## Applying it

Once the architecture is established:

- **Dependencies point inward.** Whatever project depends on nothing is the
  core; nothing in it may reference outward. A new reference that reverses an
  existing direction is a finding at the tier's maximum severity.
- **Placement follows the convention you found**, not the one you would have
  chosen. A new type that sits somewhere the three examples would not have put
  it is the finding.
- **Deviation is the finding; the convention is not.** If the repository
  consistently does something in a way you consider suboptimal, that is not a
  review finding. Note it once in your log and move on.
- **Never propose introducing a new pattern, layer, or abstraction** to fix a
  local problem. Say what is misplaced and where it belongs. Restructuring
  beyond the touched slice is out of scope.
- **Pre-existing structural debt the diff merely sits beside** is `cause: stale`.
  Record it; do not fix it here.

## Known-accepted deviations

Before raising anything, read `.claude/review/conventions.md` in the repository
under review, if it exists. It records deviations already examined and
deliberately accepted — decisions, not oversights.

Anything listed there is **not a finding**, in any run, at any severity.

That file is not authored up front. The review loop appends to it whenever the
lead rejects an architectural finding as intentional, so it accumulates from
real decisions rather than from someone's guess about what a reviewer might
complain about. If you find yourself raising the same concern the lead rejected
last run, that file is where it should have been recorded — say so in your log.

## Record what you established

Always log, before your findings:

- Which tier you reached and how.
- The dependency graph or convention you derived, in two or three lines.
- Anything ambiguous you resolved by choosing.

If a finding later turns out to be wrong, this is what shows whether the lane
misread the architecture or misapplied it. Those are different problems with
different fixes.
