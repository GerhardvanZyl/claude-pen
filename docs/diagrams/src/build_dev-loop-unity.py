#!/usr/bin/env python3
"""dev-loop-unity — thin override of dev-loop.

Reuses the _build.py engine and dev-loop's exact zone/shape grammar. Adds two
things _build.py's Layout has no primitive for, both written locally rather
than touching the shared engine:

  * `chip()` — a small "CHANGED" tag drawn in the top-right corner of a rect,
    for the phases dev-loop-unity overrides. Post-rendered by string-splice
    since Layout has no per-node badge primitive.
  * `rect_dual()` — a rect split by a hairline into two independently labeled
    phase halves (Phase 8b / Phase 9), the same "two things that always
    travel together share one node" trick CONVENTIONS.md already sanctions
    for `terminal_dual`'s Blocked/Escalate halves. Used once, to buy back the
    one node the extra Unity lane costs, without merging two phase names
    into one paraphrased title (which would break "phase names use the
    skill file's exact heading text").

Run: python build_dev-loop-unity.py <out_dir>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _build import (  # noqa: E402
    Layout, LIGHT, DARK, wrap_html, esc,
    CENTER, ZONE_X, ZONE_W, LEFT_CH, RIGHT_CH,
    NAME_SIZE, SUB_SIZE, SMALL_SIZE, FONT_SANS, FONT_MONO,
)

SLUG = 'dev-loop-unity'
TITLE = 'dev-loop-unity — Unity code at full-loop depth'
DESC = ('Flowchart of dev-loop-unity, a thin override of dev-loop: Unity batchmode '
        'validation (compile check, EditMode tests, PlayMode tests, and the '
        'Editor-lock precondition) gates Phase 1 and Phase 6; a tenth review lane, '
        'Unity (Opus, High effort), joins the nine dev-loop lanes and Artifacts '
        'cedes .meta/.unity/.prefab/.asset/.asmdef to it; and escalation to '
        'dev-loop-ultra carries all five Unity changes forward. Changed phases are '
        'tagged CHANGED against the unmodified dev-loop spine.')


def chip(t, right, top, label='CHANGED'):
    """Small bordered tag, top-right inside a rect. Horizontally clear of the
    centered title text (box is 640 wide; title text never reaches this far
    right), so it never collides even though it sits above the title's y."""
    w, h = 76, 18
    x = right - w - 10
    y = top + 6
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{t["paper"]}" '
        f'stroke="{t["soft"]}" stroke-width="0.8"/>'
        f'<text x="{x + w / 2}" y="{y + 13}" fill="{t["soft"]}" font-size="{SMALL_SIZE}" '
        f'font-family="{FONT_MONO}" text-anchor="middle" letter-spacing="0.04em">{esc(label)}</text>'
    )


def rect_dual(t, x0, y0, w, h, top_title, top_sub, bot_title, bot_sub):
    """A solid-border phase rect split by a hairline into two labeled halves —
    same shape idea as `terminal_dual`, applied to an ordinary (non-terminal)
    phase node so two always-adjacent, unchanged phases (8b, 9) can share one
    node without concatenating their headings into one paraphrased title."""
    midy = y0 + h / 2
    cx = x0 + w / 2
    parts = [
        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="6" fill="{t["paper"]}"/>',
        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="6" fill="{t["paper"]}" '
        f'stroke="{t["ink"]}" stroke-width="1"/>',
        f'<line x1="{x0 + 16}" y1="{midy}" x2="{x0 + w - 16}" y2="{midy}" '
        f'stroke="{t["rule"]}" stroke-width="0.8"/>',
        f'<text x="{cx}" y="{y0 + 30}" fill="{t["ink"]}" font-size="{NAME_SIZE}" font-weight="600" '
        f'font-family="{FONT_SANS}" text-anchor="middle">{esc(top_title)}</text>',
        f'<text x="{cx}" y="{y0 + 48}" fill="{t["muted"]}" font-size="{SUB_SIZE}" '
        f'font-family="{FONT_SANS}" text-anchor="middle">{esc(top_sub)}</text>',
        f'<text x="{cx}" y="{midy + 26}" fill="{t["ink"]}" font-size="{NAME_SIZE}" font-weight="600" '
        f'font-family="{FONT_SANS}" text-anchor="middle">{esc(bot_title)}</text>',
        f'<text x="{cx}" y="{midy + 44}" fill="{t["muted"]}" font-size="{SUB_SIZE}" '
        f'font-family="{FONT_SANS}" text-anchor="middle">{esc(bot_sub)}</text>',
    ]
    anchor = {'cx': cx, 'cy': midy, 'top': y0, 'bottom': y0 + h,
              'left': x0, 'right': x0 + w, 'y0': y0, 'h': h}
    return '\n'.join(parts), anchor


LEGEND_ITEMS_BASE = [
    ('rect', 'Phase / step'),
    ('diamond', 'Gate / decision'),
    ('lane', 'Review lane'),
    ('oval', 'Entry / exit'),
    ('dashterm', 'Blocked / escalate'),
    ('accentline', 'Loop-back'),
]


def legend_extra(t, L, text='Changed'):
    """Append a 7th legend item (the CHANGED tag) after dev-loop's stock six,
    replaying render()'s own legend math so it lands on the same row/baseline
    without touching _build.py. Verified to clear the 40px right margin."""
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
    changed_anchors = []  # (right, top) pairs to receive the CHANGED chip

    # ---- Zone 1: Entry, Implement, Test --------------------------------
    L.zone_start('Entry · implement · test',
                 'Unity code, full-loop depth — dev-loop plus batchmode validation & a Unity lane')
    L.gap(52)
    entry = L.oval('entry', 200, 60, '/dev-loop-unity')
    L.gap(40)
    p0 = L.rect(640, 100, 'Phase 0 — Frame the slice',
                'DoD adds: compile + EditMode + PlayMode passing (PlayMode: "none present" only if no asmdef)')
    changed_anchors.append(p0)
    L.gap(32)
    p1 = L.rect(640, 100, 'Phase 1 — Implement',
                'Batchmode = validation loop, Editor-lock gates every run; no hand-edited .unity/.prefab YAML')
    changed_anchors.append(p1)
    L.gap(32)
    p2 = L.rect(640, 100, 'Phase 2 — Tests',
                'Unity Test Framework — pure logic in EditMode, frames/physics/scene in PlayMode')
    changed_anchors.append(p2)
    L.zone_end()
    L.gap(40)

    # ---- Zone 2: Plan & delegate ---------------------------------------
    L.zone_start('Plan the review round · delegate',
                 'The Unity lane joins the nine')
    L.gap(52)
    p3 = L.rect(640, 100, 'Phase 3 — Plan the review round',
                '+1 lane: Unity — applicable when Assets/, Packages/, or ProjectSettings/ changed')
    changed_anchors.append(p3)
    L.gap(32)
    p4 = L.rect(640, 100, 'Phase 4 — Delegate',
                'Artifacts keeps manifest.json/lockfile/CI; Unity owns .meta/.unity/.prefab/.asset/.asmdef')
    changed_anchors.append(p4)
    L.zone_end()
    L.gap(40)

    # ---- Zone 3: Ten review lanes ----------------------------------------
    L.zone_start('Ten review lanes — one owner per concern')
    L.gap(48)
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
        ('Unity', 'Opus · High', 'Assets/, Packages/, ProjectSettings/'),
    ]
    tile_w, tile_h, gapx, gapy = 280, 100, 24, 24
    start_x = ZONE_X + (ZONE_W - (tile_w * 3 + gapx * 2)) // 2
    # Unity's trigger names real Unity paths and must not be shortened, so it
    # doesn't fit the stock 280px tile at SMALL_SIZE (the trigger is a single
    # line — lane_tile has no wrap primitive). It's alone in row 3 (col 0),
    # so widening only this one tile doesn't disturb the 3-column grid above.
    UNITY_TILE_W = 400
    for i, (name, tier, trig) in enumerate(lane_defs):
        row, col = divmod(i, 3)
        w = UNITY_TILE_W if name == 'Unity' else tile_w
        tx = start_x + col * (tile_w + gapx)
        ty = lanes_top + row * (tile_h + gapy)
        L.lane_tile(tx, ty, w, tile_h, name, tier, trig)
    lanes_bottom = lanes_top + 4 * tile_h + 3 * gapy
    L.y = lanes_bottom
    L.zone_end()
    L.gap(40)

    # ---- Zone 4: Integrity, triage, fix ---------------------------------
    L.zone_start('Integrity check · triage · fix')
    L.gap(52)
    integ = L.diamond(260, 150, 'Tree moved since\nround start?')
    L.gap(32)
    p5 = L.rect(640, 100, 'Phase 5 — Triage',
                'Escalation to dev-loop-ultra carries all 5 Unity changes + the Unity lane forward')
    changed_anchors.append(p5)
    L.gap(32)
    p6 = L.rect(640, 100, 'Phase 6 — Fix',
                'Same batchmode loop as Phase 1 (Editor-lock gates every run); no hand-edited YAML')
    changed_anchors.append(p6)
    L.zone_end()
    L.gap(40)

    # ---- Zone 5: Loop, verify, ship --------------------------------------
    L.zone_start('Loop or exit · verify · ship')
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
                            'BLOCKED — stop & report', 'round>3 · same fix twice · no progress',
                            'ESCALATE → dev-loop-ultra', 'carries the Unity lane + all 5 changes')
    L.y = p7_y + p7_h
    L.gap(32)
    p8 = L.rect(640, 100, 'Phase 8 — Independent verification',
                'Spawned once when risky/uncertain — checks intent, coverage, deferrals')
    L.gap(32)
    dual_y0 = L.y
    dual_h = 130
    dual_svg, p89 = rect_dual(
        tokens, CENTER - 320, dual_y0, 640, dual_h,
        'Phase 8b — Walkthrough', 'Draft from notes.md → review → snapshot = Phase 9 baseline',
        'Phase 9 — Commit, push, pull request', 'Stage incl. untracked · PR targets source branch',
    )
    L.y = dual_y0 + dual_h
    L.gap(32)
    end = L.oval('end', 200, 60, 'PR opened')
    L.zone_end()

    # ---- connectors -----------------------------------------------------
    L.straight_v(CENTER, entry['bottom'], p0['top'])
    L.straight_v(CENTER, p0['bottom'], p1['top'])
    L.straight_v(CENTER, p1['bottom'], p2['top'])
    L.straight_v(CENTER, p2['bottom'], p3['top'])
    L.straight_v(CENTER, p3['bottom'], p4['top'])
    L.straight_v(CENTER, p4['bottom'], lanes_top - 6, bg='paper2')
    L.straight_v(CENTER, lanes_bottom + 6, integ['top'], bg='paper2')
    L.straight_v(CENTER, integ['bottom'], p5['top'], label='clean', bg='paper2')
    L.straight_v(CENTER, p5['bottom'], p6['top'])
    L.straight_v(CENTER, p6['bottom'], p7['top'])
    L.straight_v(CENTER, p7['bottom'], p8['top'], label='pass', bg='paper2')
    L.straight_v(CENTER, p8['bottom'], p89['top'])
    L.straight_v(CENTER, p89['bottom'], end['top'])

    L.elbow([
        (integ['left'], integ['cy']),
        (LEFT_CH, integ['cy']),
        (LEFT_CH, p4['cy']),
        (p4['left'], p4['cy']),
    ], dashed=True, label='rerun lane', label_pos=(LEFT_CH, (integ['cy'] + p4['cy']) / 2))

    L.elbow([
        (p7['right'], p7['cy']),
        (RIGHT_CH, p7['cy']),
        (RIGHT_CH, p3['cy']),
        (p3['right'], p3['cy']),
    ], accent=True, label='next round', label_pos=(RIGHT_CH, (p7['cy'] + p3['cy']) / 2))

    L.straight_h(top_attach_y, p7['left'], term['right'], label='blocked', bg='paper2')
    L.straight_h(bot_attach_y, p7['left'], term['right'], label='escalate', bg='paper2')

    svg = L.render()

    # Post-render splice: the rect_dual node (drawn after arrows, so its
    # opaque fill still masks the two connectors that terminate at its edges)
    # plus the CHANGED chips and the 7th legend item.
    extra = [dual_svg]
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
