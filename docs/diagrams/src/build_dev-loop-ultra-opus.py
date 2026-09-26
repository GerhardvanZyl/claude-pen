#!/usr/bin/env python3
"""Layout generator for the dev-loop-ultra-opus flowchart (light + dark).
Extends _build.py's engine; do not hand-write SVG here.

This loop is a delta on dev-loop-ultra (two changes only), so the diagram
shows the inheritance — one compressed node for "everything ultra does" —
rather than redrawing ultra's nine-node spine in full, mirroring how the
source .drawio itself compresses phases 0-2 and phases 3-9 into a single
'Follow dev-loop-ultra in full' node.
"""
import html
from _build import Layout, LIGHT, DARK, wrap_html, CENTER, SMALL_SIZE, FONT_MONO

W = 1280


def esc(s):
    return html.escape(s, quote=True)


def custom_legend(t, y_ref):
    """This diagram uses only 4 of the stock 6 shapes (no diamond, no dashed
    terminal — see build()), and its one accent element is the 'becomes'
    edge, not a loop-back. render()'s legend is hardcoded to the stock 6
    (rule 5 calls for showing only what's used), so rather than touching
    _build.py we replay its exact row/baseline math here and splice a
    replacement legend over the default one post-render."""
    hairline_y = y_ref + 40
    row_y = hairline_y + 30
    text_baseline = row_y + int(SMALL_SIZE * 0.32)
    legend_word = 'LEGEND'
    char_w = SMALL_SIZE * 0.62
    parts = [
        f'<line x1="40" y1="{hairline_y}" x2="{W-40}" y2="{hairline_y}" stroke="{t["rule"]}" stroke-width="0.8"/>',
        f'<text x="40" y="{text_baseline}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" '
        f'font-family="{FONT_MONO}" letter-spacing="0.1em">{esc(legend_word)}</text>',
    ]
    lx = 40 + len(legend_word) * char_w * 1.1 + 32
    items = [
        ('rect', 'Phase / step'),
        ('lane', 'Agent (model tier)'),
        ('oval', 'Entry / exit'),
        ('accentline', 'Becomes'),
    ]
    for kind, text in items:
        cy = row_y
        if kind in ('rect', 'lane'):
            parts.append(f'<rect x="{lx}" y="{cy-8}" width="20" height="16" rx="3" fill="{t["paper"]}" '
                          f'stroke="{t["ink"]}" stroke-width="1"/>')
        elif kind == 'oval':
            parts.append(f'<rect x="{lx}" y="{cy-8}" width="20" height="16" rx="8" fill="{t["paper"]}" '
                          f'stroke="{t["ink"]}" stroke-width="1"/>')
        elif kind == 'accentline':
            parts.append(f'<line x1="{lx}" y1="{cy}" x2="{lx+20}" y2="{cy}" '
                          f'stroke="{t["accent"]}" stroke-width="1.4"/>')
        parts.append(f'<text x="{lx+30}" y="{text_baseline}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" '
                      f'font-family="{FONT_MONO}">{esc(text)}</text>')
        lx = lx + 30 + len(text) * char_w + 26
    if lx > W - 40:
        raise ValueError(f'legend overflows right margin: ends at {lx}, limit {W-40}')
    return '\n'.join(parts)


def build(tokens, slug):
    L = Layout(tokens, slug,
               'dev-loop-ultra-opus — adversarial review, every agent on Opus',
               'Flowchart of dev-loop-ultra-opus: structurally identical to dev-loop-ultra — the same '
               'frame/implement/test, plan, nine prosecution/defence/adjudicator triples, triage, fix, '
               'loop, verify, walkthrough and PR. It changes exactly two things: every agent including '
               'implementation runs on Opus, and concurrency drops from two lanes at a time to one.')
    L.gap(40)

    # ---- Zone 1: Inherits dev-loop-ultra in full ---------------------------
    L.zone_start('Inherits dev-loop-ultra',
                 'same phases, bounds, formats and rules — this file changes exactly two things')
    L.gap(52)
    entry = L.oval('entry', 260, 60, '/dev-loop-ultra-opus')
    L.gap(40)
    base = L.rect(760, 130, 'Follow dev-loop-ultra, in full',
                  'Frame → implement → test → plan+snapshot → 9 lanes (triple) → triage → fix → '
                  'loop (3×) → verify → walkthrough → PR')
    L.zone_end()
    L.gap(44)

    # ---- Zone 2: Change 1 — every agent on Opus (content focus) -----------
    L.zone_start('Change 1 — every agent runs on Opus',
                 'no lane tiered to Sonnet; effort is per agent file')
    L.gap(64)

    row1 = [
        ('reviewer-ultra-prosecution', 'Opus · High', 'model passed'),
        ('reviewer-ultra-defence', 'Opus · High', 'model passed'),
        ('reviewer-ultra-adjudicator', 'Opus · High', 'model passed'),
        ('reviewer-verify', 'Opus · High', 'its own default'),
    ]
    row2 = [
        ('Implementation sidekick', 'Heavy · xHigh', 'declares xhigh itself'),
        ('Test-writing sidekick', 'Heavy · xHigh', 'declares xhigh itself'),
        ('Fix sidekick', 'Heavy · xHigh', 'declares xhigh itself'),
    ]

    tile_w, tile_h, gapx, gapy = 220, 82, 18, 20
    row1_w = tile_w * 4 + gapx * 3
    row1_x = CENTER - row1_w // 2
    row1_y = L.y
    for i, (name, tier, trig) in enumerate(row1):
        L.lane_tile(row1_x + i * (tile_w + gapx), row1_y, tile_w, tile_h, name, tier, trig)
    row2_w = tile_w * 3 + gapx * 2
    row2_x = CENTER - row2_w // 2
    row2_y = row1_y + tile_h + gapy
    for i, (name, tier, trig) in enumerate(row2):
        L.lane_tile(row2_x + i * (tile_w + gapx), row2_y, tile_w, tile_h, name, tier, trig)
    L.y = row2_y + tile_h
    L.gap(24)
    L.zone_end()
    L.gap(44)

    # ---- Zone 3: Change 2 — concurrency (content focus) --------------------
    L.zone_start('Change 2 — concurrency drops to one lane at a time',
                 'already a heavy concurrent load')
    L.gap(52)
    conc_y = L.y
    # centered on 400/880 rather than 440/900 so neither box's edge sits on
    # CENTER (640) — the zone-entry/exit spine at x=640 must pass through the
    # gap between the two boxes, not along either one's border (rule 4).
    ultra_box = L.rect(400, 110, 'dev-loop-ultra',
                       '2 lanes at a time — 4 reviewers in flight', x=400)
    L.y = conc_y
    opus_box = L.rect(400, 110, 'dev-loop-ultra-opus',
                       '1 lane at a time — pair, then its adjudicator, then next', x=880)
    # rect() has no focal kwarg (only oval/diamond do); this is the one node
    # this diagram treats as focal — the delta's own defining consequence —
    # so hand-tint it the same accent/accent_tint pair oval()/diamond() use.
    L.nodes[-1]['fill'] = tokens['accent_tint']
    L.nodes[-1]['stroke'] = tokens['accent']
    L.y = max(ultra_box['bottom'], opus_box['bottom'])
    L.zone_end()
    L.gap(40)

    # ---- Zone 4: When justified · index line · exit ------------------------
    L.zone_start('When this loop is justified · index line')
    L.gap(52)
    just = L.rect(760, 100, 'Reach past dev-loop-ultra only when being wrong is severe and irreversible',
                  'Data-destroying migration · tenant-isolation defect · '
                  'regulated money movement · unfixable handoff')
    L.gap(32)
    idx = L.rect(760, 100, 'Index line — loop:"ultra-opus"',
                 'Same raised_p/raised_d/kept + walkthrough fields, compared against ultra runs')
    L.gap(32)
    end = L.oval('end', 220, 60, 'PR opened')
    L.zone_end()

    # ---- connectors ---------------------------------------------------
    L.straight_v(CENTER, entry['bottom'], base['top'])
    L.straight_v(CENTER, base['bottom'], row1_y - 6, bg='paper2')
    L.straight_v(CENTER, row2_y + tile_h + 6, conc_y, bg='paper2')

    # ultra -> ultra-opus, the loop's own defining transformation (accent)
    mid_y = ultra_box['cy']
    L.straight_h(mid_y, ultra_box['right'], opus_box['left'], accent=True, label='becomes')

    L.straight_v(CENTER, max(ultra_box['bottom'], opus_box['bottom']), just['top'], bg='paper2')
    L.straight_v(CENTER, just['bottom'], idx['top'])
    L.straight_v(CENTER, idx['bottom'], end['top'])

    y_ref = L.y
    svg = L.render()

    # Splice: replace render()'s stock 6-item legend with our 4-item one.
    hairline_y = y_ref + 40
    marker = f'<line x1="40" y1="{hairline_y}"'
    idx = svg.index(marker)
    svg = svg[:idx] + custom_legend(tokens, y_ref) + '\n</svg>'
    return svg, L


if __name__ == '__main__':
    import sys, os
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    title = 'dev-loop-ultra-opus — every agent on Opus'
    old_h1 = '<h1>dev-loop — the full development loop</h1>'

    light_svg, _ = build(LIGHT, 'dev-loop-ultra-opus')
    dark_svg, _ = build(DARK, 'dev-loop-ultra-opus-dark')

    light_html = wrap_html(light_svg, False, 'dev-loop-ultra-opus', title, 'Flowchart · Dev-Loop Diagrams')
    light_html = light_html.replace(old_h1, f'<h1>{esc(title)}</h1>')
    dark_html = wrap_html(dark_svg, True, 'dev-loop-ultra-opus-dark', title + ' (dark)',
                           'Flowchart · Dev-Loop Diagrams')
    dark_html = dark_html.replace(old_h1, f'<h1>{esc(title)}</h1>')

    with open(os.path.join(out_dir, 'dev-loop-ultra-opus.html'), 'w', encoding='utf-8') as f:
        f.write(light_html)
    with open(os.path.join(out_dir, 'dev-loop-ultra-opus-dark.html'), 'w', encoding='utf-8') as f:
        f.write(dark_html)
    print('wrote', out_dir)
