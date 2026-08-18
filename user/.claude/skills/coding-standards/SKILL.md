---
name: coding-standards
description: >
  The coding standards implementation and review must conform to. Preloaded into
  sidekick agents and reviewer-standards. Invoke when writing, reviewing, or
  refactoring code, or when asked "what are our standards".
---

# Coding standards

> **The rule sections below are scaffold defaults. Replace them with the real
> rules before relying on this file.** A standards document nobody has edited
> produces reviewers that flag plausible-sounding non-issues.

## Precedence with the per-project override

*Not a scaffold.* This section is the contract that makes the baseline and the
per-repository file combine. Replace the rules below it; leave this as written.

This skill installs once, at user level (`~/.claude/skills/coding-standards/`),
and its rules below are the **baseline** — they apply in every repository. A
repository may narrow or extend that baseline with `.claude/standards.md`, a
plain committed markdown file rather than a skill, so it cannot collide with or
shadow this one.

Before applying any rule below, check whether the current repository has
`.claude/standards.md`. If it does not exist, the baseline below applies alone.
If it exists, combine the two files under this contract:

- A rule in `.claude/standards.md` **wins** over a baseline rule below on the
  same subject; the baseline rule on that subject does not apply.
  **Matching is by subject, not by heading** — a project rule about naming
  overrides the baseline naming rule wherever the project file files it.
- A baseline rule below whose subject `.claude/standards.md` does not address
  **still applies in full** — the project file narrows or extends the
  baseline, it does not replace it.
- A subject `.claude/standards.md` lists under its own *Explicitly not
  standards* section is **removed outright**: do not raise it, even where the
  baseline below carries a rule for it.
- A rule present in **neither** file must never be raised. Do not invent one.

A `.claude/standards.md` shipped unedited from its scaffold carries no rules at
all, so it combines to no-op automatically — a repository that has not
customised it behaves exactly as if the file were absent.

**State the source of every rule you apply or raise.** Whoever is applying
these rules — implementer or reviewer — names which file a rule came from:
this skill (baseline) or `.claude/standards.md` (project). A rule that
generates noise is only fixable if the file that needs editing is known.

Rules are marked **MUST** (a reviewer raises this as Major or Critical) or
**SHOULD** (Minor — a suggestion, not a blocker). If a rule is not marked, it is
SHOULD. Do not invent rules that are not written in either file.

## Naming

- **MUST** use PascalCase for types, methods, properties, events, and constants.
- **MUST** use camelCase for locals and parameters; `_camelCase` for private fields.
- **MUST NOT** abbreviate beyond well-known domain terms. `customerRepository`,
  not `custRepo`.
- **SHOULD** name async methods with an `Async` suffix.

## Structure

- **MUST** keep one public type per file, filename matching the type.
- **MUST NOT** exceed one level of nesting in LINQ query chains without an
  intermediate named variable.
- **MUST NOT** exceed **120 characters** per line, in code and in comments.
  Wrap at a boundary that carries meaning — before a `&&`/`||`, before a `.` in
  a fluent chain, or after a comma in an argument list — so the break shows the
  structure rather than just fitting the width. A predicate or chain that still
  reads badly once wrapped is telling you it wants an intermediate named
  variable (see the rule above), not a narrower window. Applies to lines this
  change touches; do not reformat surrounding lines to comply.
- **SHOULD** keep methods under 40 lines and types under 400.
- **SHOULD** prefer composition over inheritance; seal classes not designed for
  extension.

## Nullability and defensive coding

- **MUST** enable nullable reference types and resolve warnings rather than
  suppressing them. `!` requires a comment justifying it.
- **MUST** validate public API arguments and throw `ArgumentNullException` /
  `ArgumentException` with the parameter name.
- **MUST NOT** catch `Exception` without rethrowing or logging with context.

## Async

- **MUST NOT** use `.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` on a
  Task in application code.
- **MUST** accept and honour a `CancellationToken` on any method doing I/O.
- **MUST NOT** use `async void` except in event handlers.
- **SHOULD** use `ConfigureAwait(false)` in library code.

## Dependencies and lifetime

- **MUST** inject dependencies via constructor; no service-locator lookups.
- **MUST NOT** capture a scoped service in a singleton.
- **MUST** dispose or pool anything implementing `IDisposable`; prefer `using`
  declarations.

## Logging and configuration

- **MUST** use structured logging with named placeholders, never string
  interpolation into the message template.
- **MUST NOT** log secrets, credentials, tokens, or personally identifying data.
- **MUST** read configuration through strongly-typed options, not raw indexers.

## Data access

- **MUST** parameterise every query. No string concatenation into SQL.
- **SHOULD** keep queries out of controllers and handlers.

## Comments

- **SHOULD** explain why, not what. Delete commented-out code rather than
  shipping it.
- **MUST** put XML doc comments on public API surface.
- **MUST** be concise. State the reason and stop. A comment that restates what
  the code already says, narrates steps the reader can follow unaided, or
  carries change history belonging in git is not concise — and unlike code,
  nothing compiles it, so it goes stale silently and misleads the next reader.
- **SHOULD** fit in one or two lines. A comment substantially longer than the
  code it explains usually means the code needs changing, not that it needs
  more explanation.

## Explicitly not standards

The following are **not** rules here, and a reviewer must not raise them:

- Preference between `var` and explicit types.
- Brace style, or anything else the formatter rewrites on save.
- Preferred line width **other than** the 120-character limit under *Structure*,
  which is a MUST and is raised like any other rule. A line already inside 120
  characters is not a finding however you would have wrapped it, and neither is
  a line this change did not touch.
- File-scoped versus block namespaces.
- Comment **length on its own**, where the comment carries a genuinely
  non-obvious why — an invariant, a workaround and its ticket, an ordering
  guarantee, a field number a device expects. Raise the redundancy, never the
  line count. The conciseness rule above exists to kill comments that say
  nothing, not to ration the ones that earn their space.

Anything on this list that is worth enforcing here belongs in the formatter or
analyser configuration rather than in review — fix it there instead. That is an
argument about the subjects listed above, not a general exemption: a rule this
document states is raised whether or not a tool could also have caught it.
