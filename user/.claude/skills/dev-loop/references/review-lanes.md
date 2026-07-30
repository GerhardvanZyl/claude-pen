# Review lanes

One card per lane. A reviewer reads **only its own card** — never the whole
file — plus the slice context the lead provides.

The point of these cards is that every concern has exactly one owner. If a lane
finds something owned by another lane, it does not raise it. Duplicate findings
across lanes cost the lead triage time and inflate the round's finding count,
which makes the termination condition harder to reach.

Each card has three parts:

- **Owns** — raise these.
- **Does not own** — you will notice some of these. Say nothing; another lane has
  them.
- **Quality brake** — the specific way this lane goes wrong. Read it twice.

---

## Requirements

- **Owns:** Mismatch between the change and the brief — missing requirements,
  unmet definition-of-done items, unrequested scope, and interpretations taken
  on the user's behalf where the brief was ambiguous. Contradiction between the
  letter of a requirement and its evident purpose.
- **Does not own:** How well the code is written, whether it is correct in the
  abstract, test structure, or anything the brief did not ask about.
- **Quality brake:** Form your expectation from the brief *before* reading the
  diff, or you will rationalise whatever you find. Point at the line that
  implements each requirement — a requirement you cannot point at is missing,
  regardless of how complete the change looks. When the brief itself is
  incomplete or self-contradictory, raise that against the brief; it is a
  legitimate finding and often the most valuable one.

## Technical

- **Owns:** Demonstrable incorrect behaviour caused by this diff — logic errors,
  state and lifetime bugs, concurrency and cancellation defects, boundary
  handling, error paths, and performance problems that will actually bite.
- **Does not own:** Where responsibility sits (architecture), style (standards),
  whether tests exist (tests), attack surface (security), surplus code
  (dead code, minimalism).
- **Quality brake:** State the defect and its trigger separately from the
  remedy. If you cannot describe how to trigger it, it is a suspicion — mark
  confidence `low` or drop it. Prefer the narrowest fix: a boundary, type, or
  transaction change over a new validator, cache, retry, or state field. Do not
  propose a persistent mechanism without explaining why a narrower fix fails.

## Architecture

- **Owns:** **Separation of concerns first and above everything else in this
  card** — a type or method holding responsibilities that belong apart,
  business logic in a controller, handler, or view, persistence concerns leaking
  into domain code, presentation concerns leaking downward, cross-cutting
  concerns hand-rolled inline. Then: dependency direction between projects and
  layers, placement of new types, coupling and cohesion, abstraction levels
  mixed within one unit, and conformance to the architecture already
  established in this solution.
- **Does not own:** Whether the code works (technical), naming and formatting
  (standards), whether the abstraction is *unnecessary* rather than
  *misplaced* (minimalism), unreachable code (dead code), test structure (tests).
- **Quality brake:** Establish the architecture in force before judging anything
  against it, using the tier procedure in the `solution-architecture` skill, and
  set `evidence` to the tier you reached. A convention inferred from examples is
  `inferred` and can never be a blocker; a documented or structurally evident
  rule can. **Never apply a remembered or textbook architecture to a repository
  you have not established the architecture of.** Deviation from what the
  repository consistently does is the finding — the convention itself is not,
  however suboptimal you consider it. Best practice that contradicts the
  established pattern is Minor at most and must name the tradeoff explicitly.
  **Never propose introducing a new architectural pattern, layer, or abstraction
  to fix a local problem.** Restructuring beyond the touched slice is out of
  scope; say what is misplaced and where it belongs, not how you would redesign
  the module. Check `.claude/review/conventions.md` first — anything recorded
  there is an accepted decision and is not a finding. Pre-existing architectural
  debt the diff merely sits next to is `cause: stale` and is not fixed here.

## Standards

- **Owns:** Violations of rules written in the `coding-standards` skill.
- **Does not own:** Anything not written in that document, anything under its
  "Explicitly not standards" section, and anything the formatter or analyser
  fixes automatically.
- **Quality brake:** You are matching against a document, not exercising taste.
  A rule you feel strongly about but cannot quote is not a finding — raise it
  as a suggestion that the standards document be amended instead. MUST
  violations are Major, or Critical where they cause data loss, a security hole,
  or a crash. SHOULD violations are Minor.

## Security

- **Owns:** Injection of every kind, authentication and authorization gaps
  (especially object-level: a valid user reaching another user's data), secret
  handling and leakage, unsafe deserialization and parsing, weak or home-rolled
  cryptography, data exposure through DTOs, logs, or error detail, dependency
  risk, and transport or storage protection.
- **Does not own:** Where the authz check *lives* structurally — that is
  architecture. You own whether it is present, correct, and before the effect.
  Also not: general correctness, test coverage, style.
- **Quality brake:** Check reachability before raising. A dangerous-looking
  pattern that cannot be reached in this codebase is not a finding. Distinguish
  what you verified from what you suspect and set `evidence` honestly. Severity
  is determined by who can exploit it: unauthenticated caller or authenticated
  caller reaching data they should not is Critical; requires an
  already-compromised host is Minor. Say which applies. Security theatre buries
  the real finding when one exists.

## Tests

- **Owns:** Whether the tests would fail if the code were wrong. Coverage of the
  behaviours and edge cases named in the brief, assertion quality, test level
  fit (unit / integration / UI), error-path coverage, flakiness, over-mocking,
  and missing negative cases.
- **Does not own:** The underlying defect the tests fail to catch — raise the
  missing proof, and let technical own the defect. Also not: coverage
  percentages, a test per branch, or assertions about internal call sequences
  unless that sequence is the contract.
- **Quality brake:** Admit a request for a new test only when you can answer all
  three: (1) what realistic regression passes today, (2) what stable public or
  owned boundary detects it, (3) why extending an existing test, table, or
  fixture will not do. Prefer one representative test per invariant over one per
  case.
- **Mutation testing, and where it happens.** Proving a test is decorative by
  breaking the code it covers and showing it still passes is the strongest
  finding this lane produces — a Critical, naming the line changed. **Do that
  only in the scratch worktree the lead gives you**, never in the working tree
  under review: other lanes are reading that tree concurrently and the lead is
  about to commit it. Run the suite there, make the edit there, record the
  result, and leave it — the worktree is discarded whole, so there is nothing to
  restore. If no scratch path was provided, judge the assertions by reading them
  and record `mutation testing: unavailable` in your log. Do not improvise a
  mutation anywhere else.

## Dead code

- **Owns:** Proven-unreachable branches, unused private members, orphaned
  compatibility paths, duplicate APIs left after a cut, and members whose owning
  workflow this diff removed.
- **Does not own:** Generated output, naming cleanup, speculative code that is
  reachable but unnecessary (minimalism), or pre-existing dead code the diff did
  not touch.
- **Quality brake:** Before flagging a public or exported symbol as dead,
  require evidence: private or module-local status, an explicit hard cut, or an
  authorized breaking change. "Repository search finds no consumer" is not
  sufficient for a public API. Deduplicate by family — one finding for the
  obsolete workflow, not one per member it already names.

## Minimalism

- **Owns:** Code this diff added that nothing requires — speculative guards and
  fallbacks, defensive checks for conditions that cannot occur, configuration
  and feature flags nobody asked for, wrappers and indirection with a single
  implementation, error handling for impossible errors, and tests written to
  satisfy a rule rather than to catch a regression.
- **Does not own:** Code that is misplaced rather than surplus (architecture),
  unreachable existing code (dead code), or anything the brief explicitly asked
  for.
- **Quality brake:** Check the brief before raising. A guard the brief requested
  is not bloat, however defensive it looks. **Never recommend removing a
  permission check, security control, idempotency guard, lock ordering,
  migration safety check, or durable-integrity check** unless you can state what
  else establishes that invariant and for how long it holds. Removal findings
  carry more risk than addition findings; hold them to a higher bar.

## Artifacts

- **Owns:** Generated code out of sync with its source, migrations (missing,
  irreversible, or destructive without an explicit decision), schema changes,
  lockfiles inconsistent with manifests, new or bumped dependencies, project
  file and build configuration changes, and CI surface changes.
- **Does not own:** The application logic that consumes these artifacts, or the
  security posture of a dependency version — flag an unexpected dependency and
  let security own whether the version is vulnerable.
- **Quality brake:** Run the generate-and-diff or restore check where one exists
  rather than reasoning about whether the artifact is current. A migration that
  drops or alters a column is Critical unless the brief explicitly authorised
  it. An unexplained transitive dependency addition is Major.
