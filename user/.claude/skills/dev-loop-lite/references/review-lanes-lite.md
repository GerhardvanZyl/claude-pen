# Review lanes — lite

Four consolidated lanes. A reviewer reads **only its own card**.

These merge the ten full-loop lanes. The merge is real consolidation, not
relabelling: each lane below owns several concerns that the full loop separates,
so its reviewer must actively switch between them rather than settling into the
one it finds most interesting. Each card names the concerns it must cover.

Ownership still holds. A lane that notices something owned by another lane says
nothing.

---

## Correctness

*Merges: requirements, technical, artifacts.*

- **Owns:**
  - **Requirements** — missing requirements, unmet definition-of-done items,
    unrequested scope, and interpretations taken on the user's behalf where the
    brief was ambiguous.
  - **Technical** — logic errors, state and lifetime bugs, concurrency and
    cancellation defects, boundary handling, error paths.
  - **Artifacts** — generated code out of sync with its source, migrations,
    schema changes, lockfiles inconsistent with manifests, unexpected dependency
    additions.
- **Does not own:** Where responsibility sits or how the code is shaped
  (structure), attack surface (security), whether tests would catch a regression
  (tests).
- **Quality brake:** Cover all three concerns before writing anything — the
  common failure is finding one interesting logic bug and stopping. Form your
  expectation from the brief *before* reading the diff; point at the line
  implementing each requirement, since one you cannot point at is missing. State
  each defect and its trigger separately from the remedy; a defect with no
  describable trigger is a suspicion, so mark confidence `low` or drop it. For
  artifacts, run the generate-and-diff or restore check where one exists rather
  than reasoning about whether output is current. Prefer the narrowest fix — a
  boundary or type change over a new validator, cache, or state field.

## Structure

*Merges: architecture, standards, minimalism, dead code.*

- **Owns:**
  - **Separation of concerns — first and above everything else in this card.** A
    type or method holding responsibilities that belong apart; business logic in
    a controller, handler, or view; persistence leaking into domain code;
    presentation leaking downward; cross-cutting concerns hand-rolled inline.
  - **Architecture** — dependency direction, placement of new types, coupling,
    conformance to the architecture established in this solution.
  - **Standards** — violations of rules written in the `coding-standards`
    skill or `.claude/standards.md`, combined per the skill's precedence
    section.
  - **Minimalism** — speculative guards, fallbacks, wrappers, configuration, and
    error handling for impossible errors that this diff added and nothing needs.
  - **Dead code** — unreachable branches, unused private members, and orphaned
    paths this diff left behind.
- **Does not own:** Whether the code works (correctness), attack surface
  (security), test structure (tests).
- **Quality brake:** Separation of concerns outranks everything else here; when
  a finding under another heading conflicts with one about separation of
  concerns, separation of concerns wins. Establish the architecture in force
  using the tier procedure in the `solution-architecture` skill before judging
  placement, and set `evidence` to the tier you reached — a convention inferred
  from examples can never be a blocker. **Never apply a remembered or textbook
  architecture to a repository you have not established the architecture of, and
  never propose introducing a new pattern, layer, or abstraction to fix a local
  problem.** For standards, raise only rules written in the `coding-standards`
  skill or `.claude/standards.md`, naming which file; a rule written in neither
  is not a finding. How the two combine — precedence, narrowing, and exclusion
  — is the skill's own precedence section; apply it, do not restate it here.
  Check `.claude/review/conventions.md` — anything recorded there is an
  accepted decision. Hold removal findings to a
  higher bar than addition findings, and **never recommend removing a permission
  check, security control, idempotency guard, lock ordering, or migration safety
  check** unless you can state what else establishes that invariant. Pre-existing
  structural debt the diff sits beside is `cause: stale`.

## Security

*Not merged. Kept whole.*

- **Owns:** Injection of every kind, authentication and authorization gaps
  (especially object-level: a valid user reaching another user's data), secret
  handling and leakage, unsafe deserialization and parsing, weak or home-rolled
  cryptography, data exposure through DTOs, logs, or error detail, dependency
  risk, transport and storage protection.
- **Does not own:** Where the authz check structurally lives — that is
  structure. You own whether it is present, correct, and before the effect.
- **Quality brake:** Check reachability before raising; a dangerous-looking
  pattern that cannot be reached is not a finding. Distinguish what you verified
  from what you suspect and set `evidence` honestly. Severity follows who can
  exploit it: unauthenticated caller, or authenticated caller reaching data they
  should not, is Critical; requires an already-compromised host is Minor. Say
  which applies. **If you find a Critical, say so plainly in your one-line return
  to the lead** — the lite loop escalates to the full loop on a Critical, and
  that decision depends on your report.

## Tests

*Merges: tests, validation sufficiency.*

- **Owns:** Whether the tests would fail if the code were wrong. Coverage of the
  behaviours and edge cases named in the brief, assertion quality, test level fit
  (unit / integration / UI), error-path coverage, flakiness, over-mocking,
  missing negative cases, and whether the validation commands that were run
  actually exercise what changed.
- **Does not own:** The underlying defect the tests fail to catch — raise the
  missing proof and let correctness own the defect. Also not: coverage
  percentages, a test per branch, or assertions about internal call sequences
  unless that sequence is the contract.
- **Quality brake:** The question is never "is there a test" but "would it fail
  if the code were wrong". A test that asserts no exception was thrown, asserts
  on a mock it configured itself, or asserts a value it just set is decorative —
  raise it as Major. Admit a request for a new test only when you can answer all
  three: what realistic regression passes today, what stable boundary detects
  it, and why extending an existing test will not do.
- **Mutation testing, and where it happens.** Breaking the code a test covers
  and showing it still passes is Critical, and you name the line changed.
  **Do that only in the scratch worktree the lead gives you** — never in the
  working tree under review, which other lanes are reading and the lead is about
  to commit. Leave the mutation; the worktree is discarded whole. With no
  scratch path, read the assertions instead and record `mutation testing:
  unavailable` in your log.
