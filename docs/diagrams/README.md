# Diagrams

One draw.io diagram per skill that has a workflow worth drawing — the seven dev
loops, the two tracker skills — plus the loop-selection decision tree and an
overview of how every skill hands off to the next. The reference skills
(`coding-standards`, `solution-architecture`, `implementation-notes`,
`pr-walkthrough`, `pr-walkthrough-review`) have no diagram of their own: they
are rule sets and sub-steps, not loops, and appear in the overview.

| File | Skill | Mostly about |
| --- | --- | --- |
| `skills-overview.drawio` | — | How the skills hand off: refinement → sprint → a loop → notes and walkthrough → PR |
| `loop-selection.drawio` | — | Which loop a change goes to, and the escalation ladder |
| `dev-loop-ultralight.drawio` | `/dev-loop-ultralight` | The eligibility list, and the nine-item sweep one reviewer makes in a single pass |
| `dev-loop-lite.drawio` | `/dev-loop-lite` | How nine concerns compress into four consolidated lanes, and what that costs |
| `dev-loop.drawio` | `/dev-loop` | The nine gated lanes, one owner per concern, and the triage gates |
| `dev-loop-ultra.drawio` | `/dev-loop-ultra` | The prosecution / defence / adjudicator triple, and the ratio it produces |
| `dev-loop-ultra-opus.drawio` | `/dev-loop-ultra-opus` | The two deltas on ultra: model on every agent, and concurrency |
| `dev-loop-unity-lite.drawio` | `/dev-loop-unity-lite` | The lite limits, and the gated Visual lane on Fable |
| `dev-loop-unity.drawio` | `/dev-loop-unity` | Fable art direction, build and visual review; six gated lanes; capture-level acceptance |
| `backlog-refinement.drawio` | `/backlog-refinement` | The selector, the per-item cycle, the `grill-me` handover, and the two gates that stop a write |
| `implement-sprint.drawio` | `/implement-sprint` | Skip sources, ordering by supersession, and the six checkpoints that are not configurable |

`png/` holds a render of each, quantized to a 128-colour palette — these are flat
diagrams, so it is lossless in practice and about a quarter the size. Those are
what the root README embeds. Regenerate them whenever you edit a diagram.

`dev-loops.pdf` is the seven loops as one booklet, ordered the way you choose
between them. Rebuild it with `export.py --booklet` (below) after you regenerate any loop PNG.

Lines never cross a shape and should not cross each other. Check both after an
edit with the drawio skill's validator, and look at the PNG as well: the
validator only sees routes that carry explicit waypoints, so a crossing
involving an auto-routed edge shows up only in the render.

## Rendering

Open a `.drawio` in the draw.io desktop app, at <https://app.diagrams.net>, or
with the Draw.io Integration extension in VS Code. To export to PNG:

```bash
python export.py <name>.drawio [more.drawio ...]
```

This calls the draw.io CLI and 128-colour quantizes the result.

Rebuild the booklet after regenerating any loop PNG — headless Chrome prints the
PNGs one per A4 page, which keeps them compressed:

```bash
python export.py --booklet dev-loop-ultralight dev-loop-lite dev-loop dev-loop-ultra dev-loop-ultra-opus dev-loop-unity-lite dev-loop-unity
```

## A gotcha

In the `.drawio` sources, a placeholder written `&lt;run-id&gt;` in
the XML reaches the renderer as `<run-id>` and is swallowed as an unknown HTML
tag. Double-escape it (`&amp;lt;run-id&amp;gt;`) to make it render, and check
it in the PNG rather than in the editor.
