# Development-loop diagrams

Two diagram sets live here: a generated SVG set covering all seven loops plus
two overview diagrams, embedded directly in the root `README.md`; and the
original draw.io set, the detailed editable diagrams for the five loops that
predate the Unity loops.

## The SVG set

Nine diagrams, each with a light and dark variant (`<slug>.svg` /
`<slug>-dark.svg`, plus a standalone `<slug>.html` / `<slug>-dark.html` viewer
page):

| Slug | What it shows |
| --- | --- |
| `loop-choice` | The flowchart for choosing a loop, embedded at the top of "The loops" in the root README |
| `dev-loop-flow` | The full loop redrawn from `docs/dev-loop-flow.mmd` — see below |
| `dev-loop-ultralight` | The eligibility list and the single-reviewer nine-item sweep |
| `dev-loop-lite` | Nine concerns compressed into four consolidated lanes |
| `dev-loop` | The nine gated lanes, one owner per concern, and the triage gates |
| `dev-loop-unity` | `dev-loop` overridden for Unity game code |
| `dev-loop-ultra` | The prosecution / defence / adjudicator triple |
| `dev-loop-ultra-opus` | The two deltas on ultra: model on every agent, and concurrency |
| `dev-loop-greybox` | `dev-loop-lite` overridden for in-engine blockouts and visual prototypes |

`docs/dev-loop-flow.mmd` remains the Mermaid source for the full-flow diagram;
`dev-loop-flow.svg`/`dev-loop-flow.html` is its redraw in this set's visual
style, not a replacement for the `.mmd` — edit the `.mmd` first, then redraw.

These are generated from `src/` with the diagram-design skill's `github`
profile (see `.diagram-design` at the repo root). They are committed as plain
SVG rather than regenerated on demand: each file is 16–31 KB, pure vector with
no raster fallback, so the size cost of committing them is negligible next to
the convenience of GitHub rendering them directly with no build step.

### Regenerating

Each diagram has its own `build_<slug>.py` in `src/`, except `dev-loop`
itself, which `_build.py` generates directly (`_build.py` is also the shared
layout engine every `build_*.py` imports — see `src/CONVENTIONS.md`).

```bash
cd docs/diagrams/src
python build_<slug>.py ..          # e.g. build_dev-loop-lite.py, build_loop-choice.py
python export.py ../<slug>.html
python export.py ../<slug>-dark.html
```

For the `dev-loop` slug itself:

```bash
cd docs/diagrams/src
python _build.py ..
python export.py ../dev-loop.html
python export.py ../dev-loop-dark.html
```

`export.py` extracts the `<svg>` block from the generated HTML and writes the
standalone `.svg` next to it — see the module docstring in `src/export.py` for
the exact normalisation it applies.

## The draw.io set

One draw.io diagram per loop, each showing that loop end to end: entry criteria,
every phase, the review lanes and their model tiers, the integrity checks, the
termination bounds, and the escalation exits. This is the detailed, editable
set — it predates the Unity loops and covers only the original five;
**`dev-loop-unity` and `dev-loop-greybox` have no draw.io version.**

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

### Viewing and editing

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

Rendered PNGs from this set are deliberately not committed — at a width where
the lane detail stays readable each PNG is well over a megabyte, and SVG is
worse still, since draw.io emits a raster fallback for every HTML label. The
PDF is the exception: vector throughout, and 300 KB for all five. This is
unlike the SVG set above, which is small enough (pure vector, no raster
fallback) that committing it costs nothing.
