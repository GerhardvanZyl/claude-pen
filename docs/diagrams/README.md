# Diagrams

One draw.io diagram per skill that has a workflow worth drawing — the five dev
loops, the two tracker skills — plus the loop-selection decision tree. The
reference skills (`coding-standards`, `solution-architecture`,
`implementation-notes`, `pr-walkthrough`, `pr-walkthrough-review`) have none:
they are rule sets and sub-steps, not loops.

| File | Skill | Mostly about |
| --- | --- | --- |
| `loop-selection.drawio` | — | Which loop a change goes to, and the escalation ladder |
| `dev-loop-ultralight.drawio` | `/dev-loop-ultralight` | The eligibility list, and the nine-item sweep one reviewer makes in a single pass |
| `dev-loop-lite.drawio` | `/dev-loop-lite` | How nine concerns compress into four consolidated lanes, and what that costs |
| `dev-loop.drawio` | `/dev-loop` | The nine gated lanes, one owner per concern, and the triage gates |
| `dev-loop-ultra.drawio` | `/dev-loop-ultra` | The prosecution / defence / adjudicator triple, and the ratio it produces |
| `dev-loop-ultra-opus.drawio` | `/dev-loop-ultra-opus` | The two deltas on ultra: model on every agent, and concurrency |
| `backlog-refinement.drawio` | `/backlog-refinement` | The selector, the per-item cycle, the `grill-me` handover, and the two gates that stop a write |
| `implement-sprint.drawio` | `/implement-sprint` | Skip sources, ordering by supersession, and the six checkpoints that are not configurable |

`png/` holds a render of each, quantized to a 128-colour palette — these are flat
diagrams, so it is lossless in practice and about a quarter the size. Those are
what the root README embeds. Regenerate them whenever you edit a `.drawio`.

`dev-loops.pdf` is the five loops as one booklet, ordered the way you choose
between them. `dev-loops.drawio` is its multi-page source — each page is spliced
verbatim from the single-loop file beside it, so edit the single-loop file and
re-splice rather than editing the booklet. The selection and tracker diagrams are
not in the booklet.

Colour vocabulary, shared with `../dev-loop-flow.mmd`: dark blue for a phase the
lead owns, pale blue for an agent's work or an artifact, yellow for a gate or
decision, red for a stop or escalation, green for a pass.

## Rendering

Open a `.drawio` in the draw.io desktop app, at <https://app.diagrams.net>, or
with the Draw.io Integration extension in VS Code.

```bash
# one PNG
drawio -x -f png -b 20 --width 2000 -o png/dev-loop.png dev-loop.drawio

# the booklet — --crop gives each page its own size, keeping one loop per page
drawio -x -a --crop -b 20 -f pdf -o dev-loops.pdf dev-loops.drawio
```

Then quantize, or the PNGs are four times bigger than they need to be:

```python
from PIL import Image
im = Image.open(path).convert("RGB").quantize(colors=128)
im.save(path, optimize=True)
```

SVG is not offered: draw.io emits a raster fallback for every HTML label, which
makes it larger than the PNG and no sharper.

## A gotcha

A placeholder written `&lt;run-id&gt;` in the XML reaches the renderer as
`<run-id>` and is swallowed as an unknown HTML tag — `runs/<run-id>/` displays as
`runs//`. Double-escape it (`&amp;lt;run-id&amp;gt;`) to make it render. Every
diagram here does this now. If you add a placeholder, double-escape it, and
check it in the PNG rather than in the editor — the editor shows it either way.
