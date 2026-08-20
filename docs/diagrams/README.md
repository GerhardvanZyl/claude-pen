# Development-loop diagrams

One draw.io diagram per loop, each showing that loop end to end: entry criteria,
every phase, the review lanes and their model tiers, the integrity checks, the
termination bounds, and the escalation exits.

| File | Loop | What the diagram is mostly about |
| --- | --- | --- |
| `dev-loop-ultralight.drawio` | `/dev-loop-ultralight` | The eligibility list, and the nine-item sweep one reviewer makes in a single pass |
| `dev-loop-lite.drawio` | `/dev-loop-lite` | How nine concerns compress into four consolidated lanes, and what that costs |
| `dev-loop.drawio` | `/dev-loop` | The nine gated lanes, one owner per concern, and the triage gates |
| `dev-loop-ultra.drawio` | `/dev-loop-ultra` | The prosecution / defence / adjudicator triple, and the ratio it produces |
| `dev-loop-ultra-opus.drawio` | `/dev-loop-ultra-opus` | The two deltas on ultra: model on every agent, and concurrency |

`dev-loops.pdf` is all five as one booklet, ordered the way you choose between
them: the default loop first, then the two heavier ones, then the two lighter
ones. `dev-loops.drawio` is the multi-page source it is exported from — each
page is spliced verbatim from the single-loop file beside it, so edit the
single-loop file and re-splice rather than editing the booklet.

They are drawn from the skill files in `user/.claude/skills/`, and they share the
colour vocabulary of `../dev-loop-flow.mmd`: dark blue for a phase the lead owns,
pale blue for an agent's work or an artifact, yellow for a gate or decision, red
for a stop or an escalation, green for a pass.

## Viewing and editing

Open a `.drawio` in the draw.io desktop app, at <https://app.diagrams.net>, or
with the Draw.io Integration extension in VS Code.

To render one:

```bash
drawio -x -f png -e -b 20 --width 1900 -o dev-loop.png dev-loop.drawio
```

To rebuild the booklet after editing any single-loop diagram — `--crop` gives
each page its own size, which is what keeps one loop on one page:

```bash
drawio -x -a --crop -b 20 -f pdf -o dev-loops.pdf dev-loops.drawio
```

Rendered images are deliberately not committed — at a width where the lane
detail stays readable each PNG is well over a megabyte, and SVG is worse still,
since draw.io emits a raster fallback for every HTML label. The PDF is the
exception: vector throughout, and 300 KB for all five.
