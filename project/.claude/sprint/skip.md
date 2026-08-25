# Sprint skip list

Items listed here are skipped by `implement-sprint` on every run, in every
sprint, until removed. IDs are whatever the tracker calls them — an Azure DevOps
work item ID, a GitHub issue number, a Jira key. Use it for items you have decided an agent should not
touch — not for items that are merely done, since state is already checked.

**This file ships empty, and an empty skip list is the intended default** — not
a failure state. Add an entry only when you have an item to withhold.

## Format

One entry per line, under the **Entries** heading below:

`<id> — <reason>`

The reason is required. An entry without one gets reported as an unexplained
skip, because a skip list that accumulates bare IDs becomes a place work goes to
die quietly. Write the reason for whoever reads it three sprints from now: say
what would have to change for the item to be picked up, not merely that it is
blocked today.

## Entries

No entries yet.

## Other ways to skip

You do not need this file for one-off skips:

- **Inline** — `/implement-sprint skip <id>, <id>`
- **Tag in the tracker** — `no-auto`, `manual`, or `spike` on the item, whether
  that is an Azure DevOps tag, a GitHub label, or a Jira label
- **Automatic** — wrong type, wrong state, no acceptance criteria, unmet
  dependency, or work another item in the same run would throw away. See
  `references/item-triage.md`.

Use the tag when the item should never be automated regardless of who runs it;
use this file when the reason is local to your working copy or is temporary.

## Removing entries

Review this file at sprint start. An entry whose reason has gone stale silently
withholds work from the sprint, and nothing else will remind you.

The list is re-read before every item, not only at the start, so adding an entry
mid-run withholds an item that has not run yet. It does not recall one whose PR
is already open.
