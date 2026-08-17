---
name: pr-walkthrough
description: >
  Author the reviewer walkthrough document that ships with a change's PR. Walks a
  senior engineer through the change by following one flow from its entrypoint to
  the code that changed, explaining why each decision was taken. Use at the end of
  every dev loop before the PR is raised, or when the user types /pr-walkthrough.
  Not a changelog and not a PR description — those say what changed; this says why.
---

# PR walkthrough

You are writing the document a reviewer opens before they open the diff. Its
only job is to make the diff make sense.

## When this runs

- **At the end of every dev loop**, after the final review round has passed
  and before the PR is raised — Phase 8b in `dev-loop` and `dev-loop-lite`,
  Phase 5b in `dev-loop-ultralight`. Every loop then checks what you write here
  against `pr-walkthrough-review`'s criteria: delegated to `sidekick` in
  `dev-loop` and `dev-loop-lite`, done inline by the lead in
  `dev-loop-ultralight`. Treat this as a draft that will be checked, not a
  finished artifact.
- **On `/pr-walkthrough`**, standalone, for a branch or story that already has
  a diff.

## Who you are writing for

A senior engineer with basic project knowledge — they know how to read code,
they do not know this codebase's particular shape. That calibrates everything:

- **Explain what is specific to this codebase**: the module that owns a
  concern, the convention this change follows or breaks, the reason a flow
  goes through an extra hop.
- **Explain nothing about the language or framework.** If a sentence would be
  true of any C# repository, or any React app, it does not belong here — the
  reader already knows it, and writing it down signals you don't trust them
  with the parts that actually matter.

## Why beats what

This is the whole point of the document. For every meaningful change, the diff
already shows *what*. Your job is the part the diff cannot carry:

- **What else you considered and rejected**, and what made you reject it. A
  decision with no discarded alternative usually means you did not make one.
- **What constraint forced the shape** — an existing caller you could not
  break, an external system that rejects a mismatched payload, a requirement
  that named a specific field or value.
- **What the reader would otherwise flag as wrong.** If a choice looks odd,
  say why before they spend twenty minutes deciding it is a bug.
- **What you are unsure about.** Close with the genuine open questions. A
  reviewer who knows where you were torn reviews the right lines.

A walkthrough that restates the diff in prose is a changelog with extra steps,
and the reviewer already has the diff. Every section earns its place by
answering *why*, not *what*.

**The test:** delete the words "why" and "because" from a section. If it still
reads fine, it was never explaining anything — it was narrating. Rewrite it or
cut it.

## Start at the entrypoint, not at the diff

Do not walk the file list in commit order. Find where the change is triggered
— the HTTP route, the message handler, the CLI command, the scheduled job —
and follow execution from there down into the code that changed. A reviewer
who starts at the entrypoint can hold the flow in their head; a reviewer handed
files in diff order has to reconstruct that flow themselves before they can
judge anything.

**Move fast over what did not change.** A passthrough layer gets a sentence —
enough for the reviewer to know it exists and does nothing interesting — then
slow down and spend the document where the change actually lives.

Where the flow crosses into another system or repository, draw the far side in
and label it as belonging there — the reviewer needs to know whether a file is
in this PR or merely called by it.

State the entrypoint explicitly, early, in a small table:

| Entrypoint | Trigger | First changed file it reaches |
| --- | --- | --- |
| e.g. `POST /orders` | HTTP request | `OrderController.cs` |

## Highlight rarely used patterns

Call out explicitly, with why it was necessary here:

- Something the rest of the codebase does not lean on often — a
  double-dispatch, a compensating transaction, a non-obvious caching layer.
- **A deliberate deviation from what the repo consistently does.** The
  convention is not the finding; the deviation is, so it needs its reason in
  writing.
- Anything load-bearing but non-obvious: an ordering guarantee, a tie-breaker
  column, a lock, a disposal.

A reviewer who has not seen the pattern before in this repo will otherwise
assume it is a mistake and spend their review time relitigating a decision
that was already made.

## Diagrams

**Mermaid only, never ASCII.** An ASCII diagram breaks the moment a line
wraps or a name gets one character longer, and it cannot be checked
mechanically. Mermaid renders in the PR and `pr-walkthrough-review` can
verify it parses; ASCII art can do neither.

Beyond the two mandatory opening diagrams, pick the type that fits what you
are showing: a sequence diagram suits a request flow, a flowchart suits
branching logic, an ER diagram suits a schema change. Only add one if it
earns its place — it is not mandatory to add more than the opening two.

## Anchors

Every claim about "this file, this line" must cite a real anchor —
`path/to/File.cs:142` — committed against the actual commit under review.
`pr-walkthrough-review` spot-checks these; an invented line number is worse
than no citation, because it sends the reviewer to the wrong place with false
confidence.

**Start each section with the name of the method and class it lives in**, so
the reviewer can open the right file and scroll to the right place without
hunting for it.

**If a section has a relevant method call that the next section is about to
follow, call that out** — say plainly that the walkthrough is now going to
follow that call. The reviewer should never have to notice the handoff
themselves.

## What this is not

Not a changelog — that lists what changed; this explains why. Not a PR
description — that is a short summary for the PR list view; this is the
document a reviewer reads before they start reviewing. If a section could be
copy-pasted into either of those without editing, it belongs there instead.

Not documentation of the feature. It documents **this change**, and it is
read once, at review time. Do not maintain it afterwards.

Not a defence. Where you are unsure, say so — that is the most useful
paragraph in the document.

## Exemplar resolution

Before drafting, read a worked example so the density of "why" you are
aiming for is concrete rather than assumed:

1. The most recently modified file in this repo's `docs/walkthroughs/`, if
   one exists.
2. Otherwise the bundled `references/example-walkthrough.md`, shipped with
   this skill.

The bundled exemplar is written against a fictional, generic codebase — it
demonstrates the format and the "why" density expected, not this repo's
domain.

## Authoring is delegated

**Delegate the draft to `sidekick`**, passing it the run's `notes.md`, the
diff base, the changed-file list, the path to this skill
(`pr-walkthrough/SKILL.md`), and the resolved exemplar path (see Exemplar
resolution above). `sidekick` has no Skill tool and cannot fetch either
itself — without both in the brief it has the reasons but not the format, and
the draft will not reliably come back with the structure this skill defines.

Why this is safe here when it would not be elsewhere: a draft briefed only on
the diff comes back as a narrated diff, because the diff is all the brief
gave it to work with. `notes.md` is nothing but reasons — decisions,
rejected alternatives, forced constraints, rejected requirements findings.
A draft briefed on reasons cannot come back as a changelog; there is nothing
in its brief to changelog from.

Read the returned draft yourself for "why" content before it ships — delegation
produces a draft, not a decision that it is done.

If `notes.md` is missing or thin, do not delegate. Write the walkthrough
yourself instead, and record in `run.md` that the notes were inadequate —
that is a defect in the run worth surfacing, not something to paper over.

## Opening diagrams

The document opens with a Mermaid **architecture** diagram showing where the
change sits in the system, then a Mermaid **sequence** diagram of the changed
flow. Both come before the change table — a reviewer needs the shape of the
system before the list of files means anything.

## Structure

In order:

1. **Opening paragraph** — the story in one or two sentences, the
   branch/PR/commit identifiers, and an explicit out-of-scope line.
2. **Architecture diagram**, then **sequence diagram**.
3. **Change table** — one row per file. Mark noise rows "ignore this" rather
   than omitting them, so the reviewer knows they were considered and skipped
   on purpose, not missed.
4. **The flow** — entrypoint down to the changed code, per the sections
   above.
5. **The decisions**, file by file, ordered by the flow, not by filename.
6. **Where to look to review this** — priority order, with line ranges,
   anchored to the commit.
7. **Tests** — what is covered, what deliberately is not, and the suite counts.
8. **Open questions** — carried verbatim from `notes.md`'s `## Open
   questions` section.

## Where it goes, per hosting

Name `<slug>` for the feature and the affected project, not for the story
number alone — `order-capture-idempotency.md`, not `us-4821.md`.

| Host | Path | Link |
| --- | --- | --- |
| GitHub | `docs/walkthroughs/<slug>.md`, committed on the story branch | Relative link in the PR body |
| Azure DevOps | same | ADO does not render bare relative paths in a PR description. Use the full form: `<org>/<project>/_git/<repo>?path=/docs/walkthroughs/<slug>.md&version=GB<branch>` |
| No repository | `docs/walkthroughs/<slug>.md` in the working folder | No PR exists. Report the absolute path to the user in chat and record it in `run.md`. Anchors carry file+line with no commit hash, and the opening paragraph says so, because line numbers will drift with nothing to pin them to. |

Detect the host from the git remote: `github.com` → GitHub;
`dev.azure.com` or `visualstudio.com` → ADO; no remote or no repository →
the third row.

## Skip rule

A purely mechanical change — a rename, a dependency bump, a formatting sweep
— has no "why" worth a document. Skipping is allowed. **It is never silent**:
report the skip and its reason in the PR description and in `run.md`. A
missing walkthrough with no explanation reads as an omission, not a decision.
