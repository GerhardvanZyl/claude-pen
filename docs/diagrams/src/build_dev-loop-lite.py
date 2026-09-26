#!/usr/bin/env python3
"""Layout for dev-loop-lite: nine full-loop concerns compressed into four
consolidated lanes, two rounds max, conditional verification, and the
round-1-Critical escalation to the full dev-loop. Reuses the _build.py
engine's shapes as-is (lane_tile, diamond, oval, elbow all already fit); the
only override is `render()`'s legend, whose accent-line item this diagram
relabels — the one accent edge here is an escalation exit (round-1
Critical → full loop), not a loop-back like the pilot's.
"""
import html
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _build import Layout, LIGHT, DARK, wrap_html, CENTER, ZONE_X, ZONE_W, LEFT_CH, RIGHT_CH


def esc(s):
    return html.escape(s, quote=True)


class LLayout(Layout):
    """Only the accent-line legend label differs from the base engine: this
    diagram's one accent edge is the round-1-Critical escalation to the full
    dev-loop, not a loop-back like the pilot's (see build_dev-loop-ultra.py's
    `_legend_item` override and build_dev-loop-flow.py's `render()` for the
    same targeted-override pattern used here)."""

    def render(self):
        svg = super().render()
        return svg.replace('>Loop-back<', '>Escalation exit<')


TITLE = 'dev-loop-lite — the lightweight development loop'
DESC = ('Flowchart of dev-loop-lite: the wrong-loop check; implement, tests, and round '
        'planning; four consolidated review lanes covering all nine full-loop concerns; '
        'the tree-integrity recovery loop; the round-1 Critical that escalates to the '
        'full dev-loop; the two-round cap with its loop-back and blocked exit; '
        'conditional verification; and the walkthrough and PR that close it out.')

LANES = [
    ('Correctness', 'Sonnet · High', 'req + technical + artifacts'),
    ('Structure', 'Sonnet · High', 'arch + standards + dead code'),
    ('Tests', 'Haiku · High', 'tests + validation'),
    ('Security', 'Sonnet · High', 'gated: I/O, queries, deps'),
]


def build(tokens, slug):
    L = LLayout(tokens, slug, TITLE, DESC)
    L.gap(40)

    # ---- Zone 1: Entry · wrong-loop check -------------------------------
    L.zone_start('Entry · is this the wrong loop?',
                  'stop and use the full dev-loop if any holds: auth/secrets/untrusted input · '
                  'migration/schema/contract · >1 project · hard rollback')
    L.gap(52)
    entry = L.oval('entry', 220, 60, '/dev-loop-lite')
    L.gap(40)
    wrong = L.diamond(300, 140, 'Any wrong-loop\ncriterion holds?')
    wrong_bottom = wrong['bottom']
    L.y = wrong['cy'] - 30
    wrongTerm = L.oval('wrongterm', 220, 60, '→ dev-loop (full)', dashed=True,
                        x=ZONE_X + 16 + 110)
    L.y = wrong_bottom
    L.zone_end()
    L.gap(40)

    # ---- Zone 2: Implement · tests · plan the round ------------------
    L.zone_start('Implement · tests · plan the round',
                  'implementation and fixes are NOT downgraded')
    L.gap(52)
    p0 = L.rect(640, 100, 'Phase 0 — Frame the slice',
                'requirement, non-goals, constraints, source branch → brief.md + notes.md')
    L.gap(28)
    p1 = L.rect(640, 90, 'Phase 1 — Implement',
                'sidekick by default · same tiering as the full loop')
    L.gap(28)
    p2 = L.rect(640, 90, 'Phase 2 — Tests',
                'unit · integration · UI — each must fail if behaviour regresses')
    L.gap(28)
    p3 = L.rect(640, 120, 'Phase 3 — Plan the round',
                'classify every lane applicable/skipped, diff-based · snapshot tree (round N)')
    L.zone_end()
    L.gap(40)

    # ---- Zone 3: Four consolidated lanes -----------------------------------
    L.zone_start('Four consolidated lanes — nine full-loop concerns, compressed')
    L.gap(48)
    p4 = L.rect(640, 90, 'Phase 4 — Delegate',
                'spawn all four in parallel, one turn — no waves needed')
    L.gap(32)
    lanes_top = L.y
    tile_w, tile_h, gapx, gapy = 210, 130, 20, 0
    start_x = ZONE_X + (ZONE_W - (tile_w * 4 + gapx * 3)) // 2
    lane_anchors = []
    for i, (name, tier, trig) in enumerate(LANES):
        tx = start_x + i * (tile_w + gapx)
        a = L.lane_tile(tx, lanes_top, tile_w, tile_h, name, tier, trig)
        lane_anchors.append(a)
    lanes_bottom = lanes_top + tile_h
    L.y = lanes_bottom
    L.zone_end()
    L.gap(40)

    # ---- Zone 4: Integrity · triage · escalate · fix ----------------
    L.zone_start('Integrity check · triage · the round-1 Critical · fix')
    L.gap(52)
    integ = L.diamond(280, 130, 'Tree moved\nsince round start?')
    L.gap(32)
    p5 = L.rect(640, 130, 'Phase 5 — Triage',
                'cluster by cause · evidence + cause gates · defect ≠ remedy · conventions.md')
    L.gap(32)
    esc_d = L.diamond(280, 130, 'Any Critical\nin round 1?', focal=True)
    esc_d_bottom = esc_d['bottom']
    L.y = esc_d['cy'] - 30
    escTerm = L.oval('escterm', 220, 60, '→ dev-loop (full)', dashed=True,
                      x=ZONE_X + 16 + 110)
    L.y = esc_d_bottom
    L.gap(32)
    p6 = L.rect(640, 100, 'Phase 6 — Fix',
                'would_have_been_bug → failing test first, then fix, then passing')
    L.zone_end()
    L.gap(40)

    # ---- Zone 5: Loop or exit · verify · ship -------------------------
    L.zone_start('Loop or exit (2 rounds max) · conditional verification · ship')
    L.gap(52)
    p7 = L.diamond(280, 150, 'Loop or\nexit?', x=CENTER)
    p7_bottom = p7['bottom']
    L.y = p7['cy'] - 30
    p7Blocked = L.oval('p7blocked', 260, 60, 'BLOCKED — stop', dashed=True,
                        x=ZONE_X + 16 + 130)
    L.y = p7_bottom
    L.gap(32)
    p8 = L.diamond(340, 150, 'Critical/Major fixed,\nor artifacts changed?')
    p8_bottom = p8['bottom']
    L.y = p8['cy'] - 55
    verify = L.lane_tile(ZONE_X + 16, L.y, 260, 110,
                          'reviewer-verify', 'Opus · High', 'last gate before a human sees it')
    L.y = p8_bottom
    L.gap(32)
    p8b = L.rect(640, 100, 'Phase 8b — Walkthrough',
                 'author from notes.md, not the diff → review → snapshot = Phase 9 baseline')
    L.gap(32)
    p9 = L.rect(640, 110, 'Phase 9 — Commit, push, pull request',
                'stage incl. untracked · verify --stat + tree digest · PR targets source branch')
    L.gap(32)
    end = L.oval('end', 200, 60, 'PR opened')
    L.zone_end()

    # ---- connectors -----------------------------------------------------
    bg1 = 'paper2'
    L.straight_v(CENTER, entry['bottom'], wrong['top'])
    L.straight_v(CENTER, wrong['bottom'], p0['top'], label='none hold', bg='paper2')
    L.straight_v(CENTER, p0['bottom'], p1['top'])
    L.straight_v(CENTER, p1['bottom'], p2['top'])
    L.straight_v(CENTER, p2['bottom'], p3['top'])
    L.straight_v(CENTER, p3['bottom'], p4['top'])
    L.straight_v(CENTER, p4['bottom'], lanes_top - 6, bg=bg1)
    L.straight_v(CENTER, lanes_bottom + 6, integ['top'], bg=bg1)
    L.straight_v(CENTER, integ['bottom'], p5['top'], label='clean', bg='paper2')
    L.straight_v(CENTER, p5['bottom'], esc_d['top'])
    L.straight_v(CENTER, esc_d['bottom'], p6['top'], label='no critical', bg='paper2')
    L.straight_v(CENTER, p6['bottom'], p7['top'])
    L.straight_v(CENTER, p7['bottom'], p8['top'], label='pass', bg='paper2')
    L.straight_v(CENTER, p8['bottom'], p8b['top'], label='no: skip', bg='paper2')
    L.straight_v(CENTER, p8b['bottom'], p9['top'])
    L.straight_v(CENTER, p9['bottom'], end['top'])

    # wrong-loop exit — single, muted
    L.straight_h(wrong['cy'], wrong['left'], wrongTerm['right'], label='holds', bg='paper2')

    # integrity recovery — dashed elbow loop-back, muted, left corridor
    # (mirrors the pilot's own integ -> delegate recovery loop-back)
    L.elbow([
        (integ['left'], integ['cy']),
        (LEFT_CH, integ['cy']),
        (LEFT_CH, p4['cy']),
        (p4['left'], p4['cy']),
    ], dashed=True, label='rerun lane', label_pos=(LEFT_CH, (integ['cy'] + p4['cy']) / 2))

    # round-1 Critical — THE defining exit of this loop: focal diamond + its
    # single accent edge (the escalation to the full loop).
    L.straight_h(esc_d['cy'], esc_d['left'], escTerm['right'], accent=True, label='critical', bg='paper2')

    # phase7 -> phase3, dashed elbow loop-back, muted, right corridor
    # (2-round cap: the structural bound, not the defining risk edge)
    L.elbow([
        (p7['right'], p7['cy']),
        (RIGHT_CH, p7['cy']),
        (RIGHT_CH, p3['cy']),
        (p3['right'], p3['cy']),
    ], dashed=True, label='round 2', label_pos=(RIGHT_CH, (p7['cy'] + p3['cy']) / 2))

    # phase7 -> blocked, single, muted
    L.straight_h(p7['cy'] + 40, p7['left'], p7Blocked['right'], label='blocked', bg='paper2')

    # conditional verification
    L.straight_h(p8['cy'], p8['left'], verify['right'], label='yes', bg='paper2')
    L.elbow([
        (verify['left'] + 130, verify['bottom']),
        (verify['left'] + 130, p8b['cy']),
        (p8b['left'], p8b['cy']),
    ], dashed=True)

    # Placed inside the zone frame (clear of both side corridors, which carry
    # the two loop-back edges) rather than at RIGHT_CH. The p3 pair sits above
    # p3['cy'] rather than straddling it — the ROUND 2 loop-back's final
    # horizontal approach into p3 runs exactly at p3['cy'], so a caption
    # centered there collides with the arrowhead.
    CAP_X = 1040
    L.caption(CAP_X, p3['top'] + 18, 'lead’s job,')
    L.caption(CAP_X, p3['top'] + 36, 'not a reviewer’s')
    L.caption(CAP_X, p5['cy'] - 11, 'wontfix.json')
    L.caption(CAP_X, p5['cy'] + 11, 'dies here')

    svg = L.render()
    return svg, L


_PILOT_H1 = '<h1>dev-loop — the full development loop</h1>'


def _wrap(svg, dark, slug, title, eyebrow):
    out = wrap_html(svg, dark, slug, title, eyebrow)
    return out.replace(_PILOT_H1, f'<h1>{esc(title)}</h1>')


if __name__ == '__main__':
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    light_svg, _ = build(LIGHT, 'dev-loop-lite')
    dark_svg, _ = build(DARK, 'dev-loop-lite-dark')

    with open(os.path.join(out_dir, 'dev-loop-lite.html'), 'w', encoding='utf-8') as f:
        f.write(_wrap(light_svg, False, 'dev-loop-lite', TITLE,
                       'Flowchart · Dev-Loop Diagrams'))
    with open(os.path.join(out_dir, 'dev-loop-lite-dark.html'), 'w', encoding='utf-8') as f:
        f.write(_wrap(dark_svg, True, 'dev-loop-lite-dark', TITLE + ' (dark)',
                       'Flowchart · Dev-Loop Diagrams'))
    print('wrote', out_dir)
