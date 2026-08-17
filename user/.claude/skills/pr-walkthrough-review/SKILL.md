---
name: pr-walkthrough-review
description: >
  Review the walkthrough document that ships with a change's PR and correct it in
  place. Checks that it explains why the change landed the way it did rather than
  restating what changed, that it is calibrated to a senior engineer with basic
  project knowledge, and that it reads well aloud. Use after the walkthrough is
  authored and before the PR is raised, or when the user types
  /pr-walkthrough-review.
---

# PR walkthrough review

You check the document `pr-walkthrough` produced, and you fix what is wrong
with it directly rather than reporting it back for someone else to fix.

## When it runs

After `pr-walkthrough` has authored the draft, before the PR is raised. It is
not part of the review lanes that ran earlier against the code — the code has
already passed those. This is the last check on the one artifact the loop
produces after the code is done.

Every loop except `dev-loop-ultralight` runs this skill delegated to
`sidekick`, not invoked directly by the lead — that keeps the document out of
the lead's context, which the return contract below depends on. In
`ultralight` the lead checks the draft inline against the same criteria
instead — one reviewer covering nine concerns already has no budget for a
tenth agent over a document that loop's own eligibility rules keep short.

## Write-capable on the walkthrough file only

Every other reviewer in these loops is read-only, and for good reason: the
read-only convention protects the code under review from a reviewer that
"corrects" the very thing it is supposed to be judging. That reason does not
apply here. The walkthrough is authored *after* every review lane has
drained — there is nothing left under review for a write to contaminate — it
is not code, and the phase that follows this one retakes the tree baseline
regardless of what you do to it. So "correct it if it doesn't [meet the bar]"
is safe to implement literally, and you should: fix the document in place
rather than writing findings for someone else to apply.

**You may not touch any other file.** The write permission exists for this
one document; using it anywhere else defeats the reason it was granted.

## The checks

Judge the draft against the same worked example `pr-walkthrough` resolves —
its Exemplar resolution section defines the order — not from memory of the
format.

Work through these in order:

1. **Calibrated to a senior engineer with basic project knowledge.** It
   explains what is specific to this codebase — a convention, a module
   boundary, a reason a flow takes an extra hop. It explains nothing about
   the language, the framework, or a standard pattern any senior engineer
   already knows. Cut sentences that would be true of any repository written
   in this stack.
2. **Explains reasoning, not changes.** Apply the same test `pr-walkthrough`
   is held to: delete the words "why" and "because" from a section. If it
   still reads fine, it was narrating the diff, not explaining it — rewrite
   it to say why the decision was made, or cut it if there is nothing to say.
3. **Concise; no tangents.** A section that wanders into unrelated context or
   restates something already said elsewhere gets trimmed.
4. **Reads well aloud, for a voice model.** Read each paragraph as if
   speaking it. Long parenthetical asides, stacked abbreviations, and
   sentences that only work visually (bullet fragments read as if they were
   full sentences) all fail this — smooth them out.
5. **Naming.** `.sln` files are called "solution files", `.csproj` files are
   called "project files". Not "the sln" or "the csproj" — those are
   filesystem shorthand, not what you'd say out loud to a colleague.
6. **Well structured, entrypoint-first, following execution flow.** The
   walkthrough should read the same order the request actually executes in,
   not commit order or alphabetical file order.
7. **Every cited anchor is real.** Spot-check line numbers against the actual
   files at the commit the walkthrough claims to anchor against. A walkthrough
   with invented or stale line numbers is worse than no walkthrough — it sends
   the reviewer to the wrong place with false confidence. Fix or remove any
   anchor you cannot verify.
8. **Every Mermaid block parses, and both diagrams are present.** Check the
   architecture diagram and the sequence diagram both exist and are valid
   Mermaid syntax. A diagram that fails to render defeats the entire reason
   `pr-walkthrough` mandates Mermaid over ASCII.

## The return contract

Return **one line** to the lead: the path to the walkthrough, whether you
edited it, and the issues you corrected, grouped by category (for example:
"2 anchor fixes, 1 reasoning rewrite, 1 naming fix"). The lead does not read
the whole document into context to judge whether it is good — that is what
this skill exists to do instead, and a one-line return is what keeps that
division of labour cheap.
