#!/usr/bin/env python3
"""Redraw of docs/dev-loop-flow.mmd (the full loop flow), reusing the pilot's
Layout engine, tokens and zone/spine grammar from _build.py.

This overlaps heavily with the pilot's own dev-loop.html — both draw the
same nine-phase loop — but it is redrawn from dev-loop-flow.mmd specifically.
See the FIDELITY LEDGER at the bottom of this file for what differs and why.
"""
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _build import Layout, LIGHT, DARK, FONT_SANS, FONT_MONO

CENTER = 640
RIGHT_CH = 1180


class FlowLayout(Layout):
    """Same as Layout, except the legend's dashed-oval item: this diagram has
    two distinct abnormal exits (blocked, staging-mismatch) and no escalate
    branch (this .mmd predates that edge — see FIDELITY LEDGER), so the
    pilot's "Blocked / escalate" legend text would promise a branch that
    isn't drawn and omit one that is.
    """

    def render(self):
        svg = super().render()
        return svg.replace('>Blocked / escalate<', '>Blocked / halt<')


def esc(s):
    return html.escape(s, quote=True)


def wrap_html(svg, dark, slug, title, eyebrow, h1):
    """Same page chrome as _build.py's wrap_html, but with its own H1 —
    the shared helper hardcodes dev-loop's title, which doesn't apply here.
    """
    tokens = DARK if dark else LIGHT
    bg = tokens['paper']
    ink = tokens['ink']
    muted = tokens['muted']
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --color-paper: {bg};
  --color-ink: {ink};
  --color-muted: {muted};
  --font-sans: {FONT_SANS};
  --font-mono: {FONT_MONO};
}}
body {{
  font-family: var(--font-sans);
  background: var(--color-paper);
  color: var(--color-ink);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}}
svg text {{
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}
.frame {{ max-width: 1280px; width: 100%; }}
.eyebrow {{
  font-family: var(--font-mono);
  font-size: 0.66rem;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-muted);
  margin-bottom: 0.5rem;
}}
h1 {{
  font-family: var(--font-sans);
  font-size: clamp(1.5rem, 2.4vw + 0.75rem, 1.75rem);
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.15;
  color: var(--color-ink);
  margin-bottom: 1.5rem;
}}
svg {{ width: 100%; min-width: 900px; display: block; }}
</style>
</head>
<body>
<div class="frame">
<p class="eyebrow">{esc(eyebrow)}</p>
<h1>{esc(h1)}</h1>
{svg}
</div>
</body>
</html>
'''


def build(tokens, slug):
    L = FlowLayout(tokens, slug,
               'dev-loop-flow — the full loop, redrawn from source',
               'Flowchart of dev-loop-flow.mmd: nine phases from framing through implementation, '
               'tests and shipping; a nine-lane parallel review round split into always-applicable '
               'and diff-gated lanes; a triage gate that skips the fix phase entirely when nothing '
               'was accepted; the loop-or-exit gate bounding the round; and a staging-integrity gate '
               'in Phase 9 that halts before a mismatched diff is ever pushed.')
    L.gap(40)

    # ---- Zone 1: Entry, Implement, Test --------------------------------
    L.zone_start('Entry · implement · test')
    L.gap(52)
    entry = L.oval('entry', 200, 60, '/dev-loop')
    L.gap(40)
    p0 = L.rect(640, 100, 'Phase 0 — Frame the slice',
                'Requirement, non-goals, constraints, DoD, source branch → run dir + brief.md')
    L.gap(32)
    p1 = L.rect(640, 100, 'Phase 1 — Implement',
                'Sidekick tier; conforms to coding-standards + solution-architecture')
    L.gap(32)
    p2 = L.rect(640, 100, 'Phase 2 — Tests',
                'Separate handoff · unit / integration / UI — must fail if behaviour regresses')
    L.zone_end()
    L.gap(40)

    # ---- Zone 2: Plan & delegate ---------------------------------------
    L.zone_start('Plan the round · delegate')
    L.gap(52)
    p3 = L.rect(640, 100, 'Phase 3 — Plan the review round',
                'Round N → round-N/ · classify every lane applicable/skipped → plan.md')
    L.gap(32)
    p4 = L.rect(640, 100, 'Phase 4 — Delegate',
                'Parallel, max 4 at a time, drain each wave · card-only briefing')
    L.zone_end()
    L.gap(40)

    # ---- Zone 3: Nine review lanes --------------------------------------
    L.zone_start('Nine review lanes',
                 'Read-only · 3 always-applicable + 6 diff-gated lanes')
    L.gap(60)
    lanes_top = L.y
    lane_defs = [
        ('Requirements', 'Opus · High', 'always'),
        ('Technical', 'Opus · xHigh', 'always'),
        ('Tests', 'Sonnet · High', 'always'),
        ('Architecture', 'Opus · xHigh', 'types/resp. moved'),
        ('Standards', 'Sonnet · High', 'any source file changed'),
        ('Security', 'Opus · xHigh', 'auth/authz, secrets, I/O, deps'),
        ('Dead code', 'Sonnet · High', 'paths removed or refactored'),
        ('Minimalism', 'Sonnet · High', 'guards/wrappers/config added'),
        ('Artifacts', 'Sonnet · High', 'schema/lockfile/CI changed'),
    ]
    tile_w, tile_h, gapx, gapy = 280, 100, 24, 24
    start_x = 160 + (960 - (tile_w * 3 + gapx * 2)) // 2
    for i, (name, tier, trig) in enumerate(lane_defs):
        row, col = divmod(i, 3)
        tx = start_x + col * (tile_w + gapx)
        ty = lanes_top + row * (tile_h + gapy)
        L.lane_tile(tx, ty, tile_w, tile_h, name, tier, trig)
    lanes_bottom = lanes_top + 3 * tile_h + 2 * gapy
    L.y = lanes_bottom
    L.zone_end()
    L.gap(40)

    # ---- Zone 4: Triage · fix ---------------------------------------------
    # Phase 6 (Fix) sits off the centre spine so the triage gate's "no" branch
    # (nothing accepted -> skip the fix entirely) can be a plain straight line
    # instead of an elbow through the reserved loop-back corridors.
    L.zone_start('Triage · fix')
    L.gap(52)
    p5 = L.rect(640, 100, 'Phase 5 — Triage',
                'Lead is the arbiter — cluster by cause · evidence/cause · defect≠remedy → conventions.md')
    L.gap(40)
    d1 = L.diamond(190, 110, 'Any accepted\nfindings?')
    d1_bottom_y = d1['bottom']
    L.gap(40)
    p6_top = L.y
    L.y = p6_top
    p6 = L.rect(450, 100, 'Phase 6 — Fix',
                'would_have_been_bug? yes: failing test→fix→passes; no: smallest fix', x=396)
    zone4_bottom = max(d1_bottom_y, p6['bottom'])
    L.y = zone4_bottom
    L.zone_end()
    L.gap(40)

    # ---- Zone 5: Loop, verify, ship --------------------------------------
    L.zone_start('Loop or exit · verify · ship')
    L.gap(52)
    p7_y = L.y
    p7_h = 160
    p7 = L.diamond(170, p7_h, 'Loop or\nexit?', focal=True, x=CENTER, y=p7_y)
    p7_cy = p7_y + p7_h / 2

    cur_y = L.y
    L.y = p7_cy - 30
    stop = L.oval('stop', 240, 60, 'Stop — no PR', dashed=True, x=340)
    L.y = cur_y

    L.y = p7_y + p7_h
    L.gap(32)
    p8 = L.rect(640, 100, 'Phase 8 — Independent verification',
                'reviewer-verify · runs if uncertain, risky, artifacts changed, or a Critical fixed')
    L.gap(32)
    p9 = L.rect(640, 100, 'Phase 9 — Commit, push, pull request',
                'Stage untracked · commit · diff must match plan · push · PR → source branch')

    L.gap(32)
    end_top = L.y
    L.y = end_top
    halt = L.oval('halt', 200, 60, 'Halt — mismatch', dashed=True, x=260)
    L.y = end_top
    end = L.oval('end', 160, 60, 'done')
    L.zone_end()

    # ---- connectors -----------------------------------------------------
    L.straight_v(CENTER, entry['bottom'], p0['top'])
    L.straight_v(CENTER, p0['bottom'], p1['top'])
    L.straight_v(CENTER, p1['bottom'], p2['top'])
    L.straight_v(CENTER, p2['bottom'], p3['top'])
    L.straight_v(CENTER, p3['bottom'], p4['top'])
    L.straight_v(CENTER, p4['bottom'], lanes_top - 6, bg='paper2')
    L.straight_v(CENTER, lanes_bottom + 6, p5['top'], bg='paper2')
    L.straight_v(CENTER, p5['bottom'], d1['top'])

    # d1 "yes" -> p6 (off-spine, left): exit d1's left vertex, drop into p6's top.
    L.elbow([(d1['left'], d1['cy']), (p6['cx'], d1['cy']), (p6['cx'], p6['top'])],
            label='yes', label_pos=((d1['left'] + p6['cx']) / 2, d1['cy'] - 14))

    # p6 -> p7, rejoining the spine on its upper-left slope (not the exact
    # top vertex, which the "no" edge below uses) so the two never cross.
    rejoin_x, rejoin_y = CENTER - 30, p7_y + 30
    L.elbow([(p6['cx'] + 150, p6['bottom']), (p6['cx'] + 150, rejoin_y), (rejoin_x, rejoin_y)])

    # d1 "no" -> p7: straight down the centre spine — valid because p6 is
    # off-spine, so nothing sits between d1 and p7 on the x=640 column.
    L.straight_v(CENTER, d1['bottom'], p7['top'], label='no', bg='paper2')

    L.straight_v(CENTER, p7['bottom'], p8['top'], label='pass', bg='paper2')
    L.straight_v(CENTER, p8['bottom'], p9['top'])
    L.straight_v(CENTER, p9['bottom'], end['top'])

    # p7 -> p3 (accent loop-back, the defining edge), right corridor.
    L.elbow([
        (p7['right'], p7['cy']),
        (RIGHT_CH, p7['cy']),
        (RIGHT_CH, p3['cy']),
        (p3['right'], p3['cy']),
    ], accent=True, label='round+1', label_pos=(RIGHT_CH, (p7['cy'] + p3['cy']) / 2))

    # p7 -> stop (blocked) — same row, straight horizontal; this .mmd draws
    # only one abnormal exit here (no separate escalate branch — see ledger).
    L.arrows.append({'kind': 'h', 'y': p7_cy, 'x1': p7['left'], 'x2': stop['right'],
                      'accent': False, 'label': 'blocked', 'dashed': False, 'bg': 'paper2'})

    # p9 -> halt (staging mismatch): halt sits beside "done", not beside the
    # full-width Phase 9 rect (no room there), so this exits from a point on
    # p9's bottom edge distinct from the centre (which continues to "done").
    L.elbow([(p9['cx'] - 180, p9['bottom']), (p9['cx'] - 180, halt['cy']), (halt['right'], halt['cy'])],
            label='mismatch', label_pos=(p9['cx'] - 180, (p9['bottom'] + halt['cy']) / 2))

    L.y = end['bottom']
    svg = L.render()
    return svg, L


if __name__ == '__main__':
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    light_svg, Ll = build(LIGHT, 'dev-loop-flow')
    dark_svg, Ld = build(DARK, 'dev-loop-flow-dark')

    h1 = 'dev-loop-flow — the full loop, redrawn from source'
    with open(os.path.join(out_dir, 'dev-loop-flow.html'), 'w', encoding='utf-8') as f:
        f.write(wrap_html(light_svg, False, 'dev-loop-flow', h1, 'Flowchart · Dev-Loop Diagrams', h1))
    with open(os.path.join(out_dir, 'dev-loop-flow-dark.html'), 'w', encoding='utf-8') as f:
        f.write(wrap_html(dark_svg, True, 'dev-loop-flow-dark', h1 + ' (dark)', 'Flowchart · Dev-Loop Diagrams', h1))
    print('wrote', out_dir)

# ---- FIDELITY LEDGER --------------------------------------------------
# Kept from dev-loop-flow.mmd, absent from the pilot dev-loop.html:
#  - Phase 0 subtitle keeps "non-goals" (mmd) which the pilot's own
#    dev-loop.html drops.
#  - Phase 3/4 subtitles keep "round-N/", "plan.md" and "drain each wave".
#  - The 9 review lanes: mmd groups them into two named subgraphs (AL:
#    always-applicable, GL: diff-gated); kept as a zone subtitle rather than
#    two zones, since splitting the grid would cost node/zone budget without
#    adding information the per-lane trigger tags don't already carry.
#  - Phase 5's subtitle keeps mmd's "check wontfix.json" and "durable ->
#    conventions.md" steps (T5/T6), which the pilot's dev-loop.html omits.
#  - A real "any accepted findings?" gate (D1 in the mmd) that can skip
#    Phase 6 (Fix) entirely when the round is clean. The pilot's dev-loop.html
#    has no equivalent — its Phase 5/6 always run in sequence.
#  - Phase 9 gets a genuine staging-integrity exit (the mmd's S4 gate + HALT
#    terminal: "does git diff match plan.md?" -> no -> stop). The pilot's
#    dev-loop.html compresses Phase 9 to a single subtitle line and has no
#    abnormal exit there at all.
#
# Dropped relative to the pilot (present in dev-loop.html, absent from this
# .mmd, so out of scope for a faithful redraw of dev-loop-flow.mmd):
#  - The tree-integrity check ("tree moved since round start?") diamond and
#    its dashed recovery loop-back to Phase 4. Not in this .mmd at all.
#  - Phase 8b (Walkthrough). Not in this .mmd; the mmd goes Phase 8 straight
#    to Phase 9.
#  - The "escalate -> dev-loop-ultra" exit paired with "blocked" on Phase 7.
#    This .mmd's P7 only has three edges (loop-back, pass, blocked) — no
#    escalate branch — so the terminal here is a single dashed oval, not the
#    pilot's split dual-terminal.
#  - The end node is labelled "done" (mmd's DONE(["done"])), not the pilot's
#    "PR opened".
#
# Compressed to a subtitle rather than drawn as its own diamond (kept the
# 24-node budget for the two structurally central gates — D1 and the
# staging-integrity check — which change the round's shape; these two do
# not):
#  - Phase 6's would_have_been_bug? branch (mmd's BUG gate) — an in-phase
#    mechanism, same class as the triage sub-steps (T1-T6) and the commit
#    sub-steps (S1-S9), all of which the pilot itself already compresses.
#  - Phase 8's gate ("validation uncertain, risky slice, artifacts changed,
#    or a Critical fixed?") — both branches reconverge at Phase 9 immediately
#    after, so it refines Phase 8 rather than forking the round.
#
# Connector-grammar note: CONVENTIONS.md reserves the two side corridors for
# loop-back edges only. D1's "no" branch is a forward skip, not a loop-back,
# so routing it through a corridor would be off-label; instead Phase 6 was
# moved off the centre spine (to x=380) so the "no" edge is a plain
# straight_v down the now-unobstructed x=640 column, and Phase 6's own
# in/out edges are ordinary elbows outside both reserved corridors.
