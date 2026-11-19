# Accepted conventions

Deviations examined by a review lane and deliberately accepted. Anything recorded
here is never a finding again. This file accumulates from triage decisions only —
do not author entries speculatively.

Each entry names the lane whose card it answers, so a future reviewer can see
which rule is being excused.

## One-line `if` bodies in the shell and PowerShell scripts

**Lane: Standards.** `install.sh`, `install.ps1` and both `tests/install-contract.*`
suites write single-statement `if` bodies on the condition's own line
(`if [ -n "$DRY" ]; then echo ...; return 0; fi`). The baseline coding-standards
rule says SHOULD NOT place an `if` body on the same line as its condition.

`if cond; then cmd; fi` is idiomatic POSIX shell, the rule as written addresses
brace languages, and all four files do this throughout. The convention itself is
not the finding — only new code that deviates from the surrounding file is.

Raised and rejected as `remedy` in run `20261014-1052-feat-dev-loop-inspector`.

## `docs/walkthroughs/` is this repository's architecture decision record

**Lane: Standards.** The baseline requires architectural decisions to be recorded
under `/docs/architecture-decision-record/[major|minor]`. This repository has no
such directory and never has.

Every dev loop here mandates a walkthrough before the PR, authored from the run's
`notes.md` and reviewed, and that document carries the decisions, the alternatives
rejected and the reasoning — which is what an ADR is for. A second parallel tree
would duplicate it and go stale. A missing ADR is therefore not a finding in this
repository; a missing or thin walkthrough is.

Raised and rejected as `remedy` in run `20261014-1052-feat-dev-loop-inspector`.

## README.md and INSTALL.md deliberately duplicate install-facing material

**Lane: Minimalism.** The two files repeat the From/To table, the non-overwrite
rules, and the plugin enablement commands.

`INSTALL.md` opens with "Read this file only. Everything else is reference", so it
has to stand alone for someone who reads nothing else. `README.md` is the
browsable overview and has to make sense to someone who never opens `INSTALL.md`.
Duplication between them is the point. Drift between the two copies is a finding;
the duplication is not.

Raised and rejected as `remedy` in run `20261014-1052-feat-dev-loop-inspector`.
