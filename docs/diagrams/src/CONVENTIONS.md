# dev-loop diagram conventions (reference for the other 8)

**Layout.** Flowchart, top-down, single center spine at x=640. Two side
corridors (x=100 left, x=1180 right) are reserved for loop-back edges only, so
a loop-back never crosses the forward spine or a box. 5 zones group nodes by
concern, not by phase number: paper-2 fill, rule-solid border, rx=8, mono
uppercase eyebrow top-left, optional muted one-line subtitle beneath it.
viewBox width is fixed at 1280 (doc-wide preset); height grows to fit content
(2232 here) plus the 40px margin and 60px legend strip — only width is preset.

**Node shapes.** Oval (pill, rx=h/2): start/end. A *dashed* oval is an
abnormal/terminal exit; two related exits (blocked/escalate) share one dashed
oval split by a hairline divider into labeled halves, rather than two nodes —
this is what keeps the 24-node faithful cap. Rectangle (rx=6): a lead-owned
phase — title (12px 600) + one compressed sublabel (9px muted), one line only.
Diamond: a gate/decision; exactly one is focal (accent) — whichever gate owns
the diagram's defining loop-back. Lane tile: same rectangle treatment, smaller
— name (11px) + a bordered mono tier tag (8px) + one trigger line (8px muted).

**Connectors.** Straight `<line>` only where endpoints share x or y (spine,
and same-row exits). Rounded elbow (r=8) only for loop-backs, each confined to
its own side corridor. Exactly 2 accent elements per diagram: the focal
diamond + its loop-back arrow; everything else is ink/muted. Arrow labels:
≤14 chars, uppercase, mask bg matched to local background (paper vs paper-2),
6–10px gap to the stroke.

**Model tiers.** "Name — Tier · Effort" (e.g. "Opus · xHigh") in the tier tag.

**Legend.** Bottom strip, one swatch per shape/treatment actually used. LEGEND
word and every item icon+label share one row/baseline below the hairline —
never split across two rows. Keep legend item labels short (2-3 words): six
items at 13px mono is already close to the 1280-wide, 40px-margin budget.

**Type ramp (GitHub embeds README images at ~880px wide; viewBox is 1280, so
display scale ≈0.6875).** `NAME_SIZE=17` (phase/lane/oval/terminal/diamond
titles, →11.7px displayed, floor 11px), `SUB_SIZE=14` (descriptive sublabels,
→9.6px), `SMALL_SIZE=13` (tier chips, lane triggers, eyebrows, arrow labels,
legend, →8.9px displayed, floor 8px). All three sizes clear their floor with
margin rather than sitting exactly on it — browser font-metric rounding at
these very small sizes is not worth cutting close. Box heights, gaps, and
label-mask sizes are all sized off these three constants, not off the old
8/9/11/12px ramp — if you add a new node/label kind, size text from
`NAME_SIZE`/`SUB_SIZE`/`SMALL_SIZE`, never a bare number.

## Reusing `_build.py`

`Layout` is a generic small SVG-flowchart engine: `zone_start/zone_end`,
`oval/rect/diamond/lane_tile/terminal_dual`, `straight_v/straight_h/elbow`,
`render()`. `LIGHT`/`DARK` are the github profile tokens. `build(tokens, slug)`
is dev-loop-specific — for each other loop, write a new `build_<slug>()`
function calling the same primitives, then pass its output to `wrap_html()`.
Run `python _build.py <out_dir>` to regenerate both light/dark HTML in one
pass. Do not hand-write SVG for the remaining 8 diagrams; extend this engine
instead (e.g. add a primitive here if a new shape is needed, don't inline it).
