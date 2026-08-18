# Accepted conventions

Deviations examined by a review lane and deliberately accepted. Anything recorded
here is never a finding again. This file accumulates from triage decisions only —
do not author entries speculatively.

---

## `graphify-out/` is not regenerated per change

**Recorded:** 2026-08-18, run `20260818-standards-override` (lite), from `corr-005`.

`graphify-out/` is a committed, machine-generated knowledge-graph cache. It goes
stale whenever a file it indexed moves or is deleted, and this repository does not
regenerate it as part of any change.

**A reviewer must not raise stale paths inside `graphify-out/` as a finding.**
Regenerating it produces a large diff tangential to whatever change is under
review, and the cache is rebuilt on demand by the `graphify` skill rather than
maintained by hand.

This does not extend to other generated artifacts. It is specific to
`graphify-out/`, and specific to path staleness — a lane may still raise the
directory for anything else, such as secrets captured into the cache.
