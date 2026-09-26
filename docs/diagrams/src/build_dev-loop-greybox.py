#!/usr/bin/env python3
"""dev-loop-greybox — thin override of dev-loop-lite.

Reuses the _build.py engine and dev-loop's exact zone/shape grammar. The only
thing Layout has no primitive for is the "CHANGED" tag on an overridden
phase; `chip()` below draws it and is spliced into the rendered SVG string,
same technique as build_dev-loop-unity.py. Unlike the Unity diagram this one
needs no split-node trick — dev-loop-lite's spine is short enough that even
after the greybox additions (a capture gate, a no-GPU exit, two new lanes)
the node count stays under the 24-node cap without merging any phase.

Run: python build_dev-loop-greybox.py <out_dir>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _build import (  # noqa: E402
    Layout, LIGHT, DARK, wrap_html, esc,
    CENTER, ZONE_X, ZONE_W, LEFT_CH, RIGHT_CH,
    NAME_SIZE, SMALL_SIZE, FONT_SANS, FONT_MONO,
)

SLUG = 'dev-loop-greybox'
TITLE = 'dev-loop-greybox — in-engine blockouts, judged by shot'
DESC = ('Flowchart of dev-loop-greybox, a thin override of dev-loop-lite: an art brief '
        'with named shots gates Phase 0; Shot_<name> cameras and ShotCapture.cs are built '
        'in Phase 1; a ShotCapture batchmode step after Phase 2 and after every Phase 6 '
        'renders every shot to PNG, or the run stops — for a missing shot as a failed '
        'definition-of-done item, or for no GPU as a hard stop that is never a reason to '
        'skip the Visual lane; two more lanes, Unity (Sonnet) and Visual (Opus), run in a '
        'second wave after the four lite lanes drain; the loop-or-exit gate is where those '
        'shots are judged against the brief; final-round shots ship in the walkthrough; and '
        'escalation goes to dev-loop-unity instead of dev-loop. Changed phases are tagged '
        'CHANGED against the unmodified dev-loop-lite spine.')


def dashed_oval(t, cx, cy, w, h, text):
    """Layout's `oval()` has no y-override (only diamond() does, for the
    focal gate), so it can't sit level with a diamond drawn beside it in the
    flow. Written locally and spliced in, like `chip()`, rather than
    touching _build.py's oval() signature that every other node relies on."""
    x0, y0 = cx - w / 2, cy - h / 2
    rxx = h / 2
    svg = (
        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{rxx}" fill="{t["paper"]}"/>'
        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{rxx}" fill="{t["paper"]}" '
        f'stroke="{t["muted"]}" stroke-width="1" stroke-dasharray="5,4"/>'
        f'<text x="{cx}" y="{cy + 6}" fill="{t["ink"]}" font-size="{NAME_SIZE}" font-weight="600" '
        f'font-family="{FONT_SANS}" text-anchor="middle">{esc(text)}</text>'
    )
    anchor = {'cx': cx, 'cy': cy, 'top': y0, 'bottom': y0 + h, 'left': x0, 'right': x0 + w}
    return svg, anchor


def chip(t, right, top, label='CHANGED'):
    """Small bordered tag, top-right inside a rect — horizontally clear of the
    centered title text, so it never collides even though it sits above it."""
    w, h = 76, 18
    x = right - w - 10
    y = top + 6
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{t["paper"]}" '
        f'stroke="{t["soft"]}" stroke-width="0.8"/>'
        f'<text x="{x + w / 2}" y="{y + 13}" fill="{t["soft"]}" font-size="{SMALL_SIZE}" '
        f'font-family="{FONT_MONO}" text-anchor="middle" letter-spacing="0.04em">{esc(label)}</text>'
    )


LEGEND_ITEMS_BASE = [
    ('rect', 'Phase / step'),
    ('diamond', 'Gate / decision'),
    ('lane', 'Review lane'),
    ('oval', 'Entry / exit'),
    ('dashterm', 'Blocked / escalate'),
    ('accentline', 'Loop-back'),
]


def legend_extra(t, L, text='Changed'):
    """Append a 7th legend item (the CHANGED tag), replaying render()'s own
    legend math so it lands on the same row/baseline without touching
    _build.py. Same items/math as build_dev-loop-unity.py, so the same
    right-margin proof applies."""
    char_w = SMALL_SIZE * 0.62
    legend_word = 'LEGEND'
    lx = 40 + len(legend_word) * char_w * 1.1 + 32
    for _, item_text in LEGEND_ITEMS_BASE:
        lx += 30 + len(item_text) * char_w + 26
    hairline_y = L.y + 40
    row_y = hairline_y + 30
    text_baseline = row_y + int(SMALL_SIZE * 0.32)
    end_x = lx + 30 + len(text) * char_w + 26
    if end_x > 1280 - 40:
        raise ValueError(f'legend overflows right margin: ends at {end_x}, limit 1240')
    w, h = 20, 16
    return (
        f'<rect x="{lx}" y="{row_y - h / 2}" width="{w}" height="{h}" rx="3" '
        f'fill="{t["paper"]}" stroke="{t["soft"]}" stroke-width="1"/>'
        f'<text x="{lx + w / 2}" y="{row_y + 13}" fill="{t["soft"]}" font-size="9" '
        f'font-family="{FONT_MONO}" text-anchor="middle" letter-spacing="0.02em">C</text>'
        f'<text x="{lx + 30}" y="{text_baseline}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" '
        f'font-family="{FONT_MONO}">{esc(text)}</text>'
    )


def build(tokens, slug):
    L = Layout(tokens, slug, TITLE, DESC)
    L.gap(40)
    changed_anchors = []

    # ---- Zone 1: Entry, Implement, Test, Capture -------------------------
    L.zone_start('Entry · implement · test',
                 'In-engine blockouts — dev-loop-lite plus named shots & ShotCapture')
    L.gap(52)
    entry = L.oval('entry', 200, 60, '/dev-loop-greybox')
    L.gap(40)
    p0 = L.rect(640, 100, 'Phase 0 — Frame the slice',
                'Art brief: mood/ref, scale, palette/lighting + named shots (camera, look, must-show)')
    changed_anchors.append(p0)
    L.gap(32)
    p1 = L.rect(640, 100, 'Phase 1 — Implement',
                'ProBuilder/primitives + placeholder lighting; Shot_<name> camera per shot, disabled')
    changed_anchors.append(p1)
    L.gap(32)
    p2 = L.rect(640, 100, 'Phase 2 — Tests',
                'Unit / integration / UI — typically skipped: no logic added')
    L.gap(32)
    cap_y = L.y
    cap_h = 140
    cap = L.diamond(260, cap_h, 'All Shot_* →\nPNG rendered?', x=CENTER, y=cap_y)
    cap_cy = cap['cy']
    nogpu_svg, nogpu = dashed_oval(tokens, ZONE_X + 16 + 100, cap_cy, 200, 70, 'STOP — no shots')
    L.y = cap_y + cap_h
    L.zone_end()
    L.gap(40)

    # ---- Zone 2: Plan & delegate ------------------------------------------
    L.zone_start('Plan the round · delegate',
                 "Two waves — lite's four, then Unity + Visual")
    L.gap(52)
    p3 = L.rect(640, 100, 'Phase 3 — Plan the round',
                '+2 lanes, always applicable: Unity (Sonnet) · Visual (Opus)')
    changed_anchors.append(p3)
    L.gap(32)
    p4 = L.rect(640, 100, 'Phase 4 — Delegate',
                'Wave 1: 4 lite lanes drain; wave 2: Unity + Visual, then snapshot compared')
    changed_anchors.append(p4)
    L.zone_end()
    L.gap(40)

    # ---- Zone 3: Six review lanes, two waves ------------------------------
    L.zone_start('Six review lanes — two waves')
    L.gap(48)
    lanes_top = L.y
    lane_defs = [
        ('Correctness', 'Sonnet · High', 'always — wave 1'),
        ('Structure', 'Sonnet · High', 'always — wave 1'),
        ('Tests', 'Haiku · High', 'always — wave 1'),
        ('Security', 'Sonnet · High', 'input/I-O/deps — wave 1'),
        ('Unity', 'Sonnet · High', 'always — wave 2'),
        ('Visual', 'Opus · High', 'always — wave 2'),
    ]
    tile_w, tile_h, gapx, gapy = 280, 100, 24, 24
    start_x = ZONE_X + (ZONE_W - (tile_w * 3 + gapx * 2)) // 2
    for i, (name, tier, trig) in enumerate(lane_defs):
        row, col = divmod(i, 3)
        tx = start_x + col * (tile_w + gapx)
        ty = lanes_top + row * (tile_h + gapy)
        L.lane_tile(tx, ty, tile_w, tile_h, name, tier, trig)
    lanes_bottom = lanes_top + 2 * tile_h + gapy
    L.y = lanes_bottom
    L.zone_end()
    L.gap(40)

    # ---- Zone 4: Integrity, triage, fix -----------------------------------
    L.zone_start('Integrity check · triage · fix',
                 'checked after wave 1 and after wave 2 drains')
    L.gap(52)
    integ = L.diamond(260, 150, 'Tree moved since\nround start?')
    L.gap(32)
    p5 = L.rect(640, 100, 'Phase 5 — Triage',
                'Any Critical in round 1 → escalate to dev-loop-unity, not dev-loop')
    changed_anchors.append(p5)
    L.gap(32)
    p6 = L.rect(640, 100, 'Phase 6 — Fix',
                'ShotCapture re-runs here too, into round-N/shots/ — missing PNG still fails DoD')
    changed_anchors.append(p6)
    L.zone_end()
    L.gap(40)

    # ---- Zone 5: Loop, verify, ship ----------------------------------------
    L.zone_start('Loop or exit · verify · ship',
                 'shots judged against the brief — via Visual lane')
    L.gap(52)
    p7_y = L.y
    p7_h = 160
    p7 = L.diamond(160, p7_h, 'Loop or\nexit?', focal=True, x=CENTER, y=p7_y)
    p7_cy = p7_y + p7_h / 2
    top_attach_y = p7_cy - 34
    bot_attach_y = p7_cy + 34
    term_h = 148
    term_y0 = top_attach_y - 32
    term = L.terminal_dual(ZONE_X + 16, term_y0, 280, term_h,
                            'BLOCKED — stop & report', 'round>2 · same fix twice · no progress',
                            'ESCALATE → dev-loop-unity', 'full depth + Unity lane — misjudged size')
    L.y = p7_y + p7_h
    L.gap(32)
    p8 = L.rect(640, 100, 'Phase 8 — Verification',
                'Spawned only if a Critical/would-have-been-bug Major was fixed, or artifacts changed')
    L.gap(32)
    p8b = L.rect(640, 100, 'Phase 8b — Walkthrough',
                 'Final round\'s shots → docs/walkthroughs/<slug>/shots/; snapshot AFTER copying them')
    changed_anchors.append(p8b)
    L.gap(32)
    p9 = L.rect(640, 100, 'Phase 9 — Commit, push, pull request',
                'Stage incl. untracked · loop:"greybox" · PR targets source branch')
    L.gap(32)
    end = L.oval('end', 200, 60, 'PR opened')
    L.zone_end()

    # ---- connectors ---------------------------------------------------
    L.straight_v(CENTER, entry['bottom'], p0['top'])
    L.straight_v(CENTER, p0['bottom'], p1['top'])
    L.straight_v(CENTER, p1['bottom'], p2['top'])
    L.straight_v(CENTER, p2['bottom'], cap['top'])
    L.straight_v(CENTER, cap['bottom'], p3['top'], label='all render', bg='paper2')
    L.straight_v(CENTER, p3['bottom'], p4['top'])
    L.straight_v(CENTER, p4['bottom'], lanes_top - 6, bg='paper2')
    L.straight_v(CENTER, lanes_bottom + 6, integ['top'], bg='paper2')
    L.straight_v(CENTER, integ['bottom'], p5['top'], label='clean', bg='paper2')
    L.straight_v(CENTER, p5['bottom'], p6['top'])
    L.straight_v(CENTER, p6['bottom'], p7['top'])
    L.straight_v(CENTER, p7['bottom'], p8['top'], label='pass', bg='paper2')
    L.straight_v(CENTER, p8['bottom'], p8b['top'])
    L.straight_v(CENTER, p8b['bottom'], p9['top'])
    L.straight_v(CENTER, p9['bottom'], end['top'])

    # capture gate -> no-GPU/no-shots stop: a same-row exit, direct straight_h
    # (like phase7 -> term below), not the reserved loop-back corridor
    L.straight_h(cap_cy, cap['left'], nogpu['right'], dashed=True, label='missing', bg='paper2')

    # integrity -> phase4 recovery loop-back, left corridor (shared with
    # dev-loop's full loop; confined to zone 2-4, well below the capture
    # gate's local dashed line in zone 1, so the two never share a path)
    L.elbow([
        (integ['left'], integ['cy']),
        (LEFT_CH, integ['cy']),
        (LEFT_CH, p4['cy']),
        (p4['left'], p4['cy']),
    ], dashed=True, label='rerun lane', label_pos=(LEFT_CH, (integ['cy'] + p4['cy']) / 2))

    # phase7 -> phase3 accent loop-back, the defining edge
    L.elbow([
        (p7['right'], p7['cy']),
        (RIGHT_CH, p7['cy']),
        (RIGHT_CH, p3['cy']),
        (p3['right'], p3['cy']),
    ], accent=True, label='next round', label_pos=(RIGHT_CH, (p7['cy'] + p3['cy']) / 2))

    L.straight_h(top_attach_y, p7['left'], term['right'], label='blocked', bg='paper2')
    L.straight_h(bot_attach_y, p7['left'], term['right'], label='escalate', bg='paper2')

    svg = L.render()

    extra = [nogpu_svg]
    for a in changed_anchors:
        extra.append(chip(tokens, a['right'], a['top']))
    extra.append(legend_extra(tokens, L))
    svg = svg.replace('</svg>', '\n'.join(extra) + '\n</svg>')
    return svg


if __name__ == '__main__':
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    light_svg = build(LIGHT, SLUG)
    dark_svg = build(DARK, f'{SLUG}-dark')

    with open(os.path.join(out_dir, f'{SLUG}.html'), 'w', encoding='utf-8') as f:
        f.write(wrap_html(light_svg, False, SLUG, TITLE, 'Flowchart · Dev-Loop Diagrams')
                .replace('dev-loop — the full development loop', TITLE))
    with open(os.path.join(out_dir, f'{SLUG}-dark.html'), 'w', encoding='utf-8') as f:
        f.write(wrap_html(dark_svg, True, f'{SLUG}-dark', f'{TITLE} (dark)', 'Flowchart · Dev-Loop Diagrams')
                .replace('dev-loop — the full development loop', TITLE))
    print('wrote', out_dir)
