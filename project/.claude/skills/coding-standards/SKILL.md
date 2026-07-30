---
name: coding-standards
description: >
  The coding standards implementation and review must conform to. Preloaded into
  sidekick agents and reviewer-standards. Invoke when writing, reviewing, or
  refactoring code in this repository, or when asked "what are our standards".
---

# Coding standards

> **These are scaffold defaults. Replace every section with the real rules
> before relying on this file.** A standards document nobody has edited produces
> reviewers that flag plausible-sounding non-issues.

Rules are marked **MUST** (a reviewer raises this as Major or Critical) or
**SHOULD** (Minor — a suggestion, not a blocker). If a rule is not marked, it is
SHOULD. Do not invent rules that are not written here.

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

## Explicitly not standards

The following are **not** rules here, and a reviewer must not raise them:

- Preference between `var` and explicit types.
- Brace style, line length, or anything the formatter already fixes.
- File-scoped versus block namespaces.

If the formatter or analyser can catch it, it is not a review finding. Fix the
analyser configuration instead.
