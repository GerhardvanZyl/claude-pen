# Architecture

> **Template.** Copy to your repository root as `ARCHITECTURE.md` and replace
> every section with what is actually true of this codebase. Delete this note.
>
> **Do not fill it in from a preferred design.** Derive it from the module or
> project graph and from the code that exists. An architecture document that
> describes an aspiration turns the architecture lane into a generator of
> restructuring proposals, which is worse than having no document at all.

The `solution-architecture` skill discovers this file and treats it as **Tier 1**
evidence, which means findings against it can be stated at full severity rather
than capped at Minor. That is the entire reason to write it.

Where this file and the dependency graph disagree, **the graph is what is in
force.** Update the document, not the code.

## Solutions / modules in this repository

Replace with the real list. Include anything that looks shared but is not —
vendored copies, forks, and parallel implementations cause more bad findings than
anything else, because a reviewer will try to deduplicate across them.

| Solution / module | Contains | Notes |
| --- | --- | --- |
| `<name>` | `<projects>` | `<framework, and what it may not touch>` |

State plainly which parts are independent of which. That fact is what makes
scoped validation defensible later.

## Layering

Dependencies point inward. Name the project that depends on nothing — that is
the core, whatever it is called.

| Project | Contains | May reference |
| --- | --- | --- |
| `<Dto>` | DTOs, BCL types only | nothing |
| `<Domain>` | Entities, domain rules | `<Dto>` |
| `<Application>` | Use cases, orchestration, ports | `<Domain>` |
| `<Infrastructure>` | Persistence, external clients | `<Application>`, `<Domain>` |
| `<Host>` | Wiring, controllers, workers | all of the above |

Name what sits at the top and is referenced by nothing.

State whether a **package** reference is preferred over a project reference when
only an abstraction is needed.

## Namespace and placement conventions

Record conventions that are **enforced by something**, not merely tidy — a
collision with a vendor SDK, a build rule, a wholesale namespace import. A
convention with a hard reason behind it is one a reviewer can state at full
severity; one without is a preference.

## Configuration

- Where configuration comes from, and the precedence between sources.
- What "not configured" looks like, and how it falls through.
- **Which layers may read configuration directly.** State this explicitly. If
  layers below the host already read it, say so — otherwise a reviewer will
  infer a rule from one example and raise it every run.

## Data and schema

- What counts as schema (needs a migration) versus seed or reference data.
- Which file or table is **authoritative** when two disagree.
- Any guard that must not be removed — insert-only-if-absent, idempotency,
  ordering.

## Validation scoping

- The commands the loops must run.
- If the full suite cannot be run, **the blocker**, and the evidence that the
  narrower scope is sufficient — a reference-graph fact, not an assertion.
- Expected test count and known pre-existing warnings, so a change is judged by
  what it *adds* rather than by totals.

## Known defects that constrain new work

Defects that are real, deferred, and that new code must work around. Each with
what it forbids until fixed. This section is why a reviewer will not re-discover
the same trap every sprint.

## Not architecture

Naming, formatting, file layout within a project, and language-feature choice
belong to `coding-standards`. Do not raise them under this heading.
