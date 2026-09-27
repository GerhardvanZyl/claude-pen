# Diagrams

One HTML diagram per skill that has a workflow worth drawing — the seven dev
loops, the two tracker skills — plus the loop-selection decision tree. The
reference skills (`coding-standards`, `solution-architecture`,
`implementation-notes`, `pr-walkthrough`, `pr-walkthrough-review`) have none:
they are rule sets and sub-steps, not loops.

| File | Skill | Mostly about |
| --- | --- | --- |
| `loop-selection.html` | — | Which loop a change goes to, and the escalation ladder |
| `dev-loop-ultralight.html` | `/dev-loop-ultralight` | The eligibility list, and the nine-item sweep one reviewer makes in a single pass |
| `dev-loop-lite.html` | `/dev-loop-lite` | How nine concerns compress into four consolidated lanes, and what that costs |
| `dev-loop.html` | `/dev-loop` | The nine gated lanes, one owner per concern, and the triage gates |
| `dev-loop-ultra.html` | `/dev-loop-ultra` | The prosecution / defence / adjudicator triple, and the ratio it produces |
| `dev-loop-ultra-opus.html` | `/dev-loop-ultra-opus` | The two deltas on ultra: model on every agent, and concurrency |
| `dev-loop-unity-lite.html` | `/dev-loop-unity-lite` | The lite limits, and the gated Visual lane on Fable |
| `dev-loop-unity.html` | `/dev-loop-unity` | Fable art direction, build and visual review; six gated lanes; capture-level acceptance |
| `backlog-refinement.drawio` | `/backlog-refinement` | The selector, the per-item cycle, the `grill-me` handover, and the two gates that stop a write |
| `implement-sprint.drawio` | `/implement-sprint` | Skip sources, ordering by supersession, and the six checkpoints that are not configurable |

`png/` holds a render of each, quantized to a 128-colour palette — these are flat
diagrams, so it is lossless in practice and about a quarter the size. Those are
what the root README embeds. Regenerate them whenever you edit a diagram.

`dev-loops.pdf` is the seven loops as one booklet, ordered the way you choose
between them. Rebuild it with `export.py --booklet` (below) after you regenerate any loop PNG.

The loop diagrams use the diagram-design default skin, where coral marks each
diagram's one or two focal elements.

## Rendering

Open a `.html` in a browser to view it. To export to PNG, run:

```bash
python export.py <name>.html
```

This uses headless Chrome to render the diagram and 128-colour quantize the result.

For the two tracker diagrams (`.drawio` files), open them in the draw.io desktop
app, at <https://app.diagrams.net>, or with the Draw.io Integration extension
in VS Code:

```bash
drawio -x -f png -b 20 --width 2000 -o png/<name>.png <name>.drawio
```

Then quantize with Pillow:

```python
from PIL import Image
for path in [...]:
    im = Image.open(path).convert("RGB").quantize(colors=128)
    im.save(path, optimize=True)
```

Rebuild the booklet after regenerating any loop PNG — headless Chrome prints the
PNGs one per A4 page, which keeps them compressed:

```bash
python export.py --booklet dev-loop-ultralight dev-loop-lite dev-loop dev-loop-ultra dev-loop-ultra-opus dev-loop-unity-lite dev-loop-unity
```

## A gotcha

In the two `.drawio` tracker diagrams, a placeholder written `&lt;run-id&gt;` in
the XML reaches the renderer as `<run-id>` and is swallowed as an unknown HTML
tag. Double-escape it (`&amp;lt;run-id&amp;gt;`) to make it render, and check
it in the PNG rather than in the editor.
