# Sprint skip list

Items listed here are skipped by `implement-sprint` on every run, in every
sprint, until removed. Use it for items you have decided an agent should not
touch — not for items that are merely done, since state is already checked.

One item per line: `<id> — <reason>`

The reason is required. An entry without one gets reported as an unexplained
skip, because a skip list that accumulates bare IDs becomes a place work goes to
die quietly.

```
4712 — Owned by Chris, coordinating with the vendor
4755 — Needs a product decision on the retention window first
4801 — Deliberately manual: touches the PEXA integration credentials
```

## Other ways to skip

You do not need this file for one-off skips:

- **Inline** — `/implement-sprint skip 4821, 4830`
- **Tag in ADO** — `no-auto`, `manual`, or `spike` on the work item
- **Automatic** — wrong type, wrong state, no acceptance criteria, unmet
  dependency. See `references/item-triage.md`.

Use the tag when the item should never be automated regardless of who runs it;
use this file when the reason is local to your working copy or is temporary.

## Removing entries

Review this file at sprint start. An entry whose reason has gone stale silently
withholds work from the sprint, and nothing else will remind you.
