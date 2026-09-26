#!/usr/bin/env python3
"""Redraw of the README "which loop" decision tree (first mermaid block,
around line 78), with the Unity fork added per user/CLAUDE.md's
"Development loop" section: an early "Unity project?" gate leading to the
two Unity loops by kind of work.

Not a spine-and-phases flow like dev-loop.html — a branching decision tree,
so this writes its own build() rather than reusing dev-loop's. Reuses the
Layout primitives, tokens and wrap_html conventions from _build.py; the
legend is different enough (no lanes, no loop-back, two focal outcomes
instead of one focal gate) that TreeLayout overrides render()/_legend_item()
rather than touching the shared file.
"""
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _build import Layout, LIGHT, DARK, FONT_MONO, FONT_SANS, SMALL_SIZE, SUB_SIZE, W as CANVAS_W

CENTER = 640


def esc(s):
    return html.escape(s, quote=True)


class TreeLayout(Layout):
    """Layout variant for loop-choice: a branching decision tree, not a
    spine-and-zones flow. No zones, no loop-back corridors, and a legend
    that reflects the shapes this diagram actually uses (gate, outcome,
    focal outcome) instead of dev-loop's (phase, lane, blocked/escalate,
    loop-back).
    """

    def render(self):
        t = self.t
        H = self.y + 40 + 100
        H = ((H + 3) // 4) * 4
        parts = []
        parts.append(f'<svg viewBox="0 0 {CANVAS_W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
                      f'aria-labelledby="{self.slug}-title {self.slug}-desc">')
        parts.append(f'<title id="{self.slug}-title">{esc(self.title)}</title>')
        parts.append(f'<desc id="{self.slug}-desc">{esc(self.desc)}</desc>')
        parts.append('<defs>')
        parts.append(f'<marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
                      f'<polygon points="0 0, 8 3, 0 6" fill="{t["muted"]}"/></marker>')
        parts.append(f'<marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
                      f'<polygon points="0 0, 8 3, 0 6" fill="{t["accent"]}"/></marker>')
        parts.append('</defs>')
        parts.append(f'<rect width="100%" height="100%" fill="{t["paper"]}"/>')

        # No zones for this diagram (see build_dev-loop-flow / build_loop-choice
        # ledger note): a compact branching tree reads fine from position and
        # shape alone, and framing every branch would add chrome the brief
        # asked to avoid ("keep it compact").

        for a in self.arrows:
            stroke = t['accent'] if a['accent'] else t['muted']
            marker = 'arrow-accent' if a['accent'] else 'arrow'
            dash = ' stroke-dasharray="5,4"' if a['dashed'] else ''
            sw = '1.4' if a['accent'] else '1'
            if a['kind'] == 'v':
                x, y1, y2 = a['x'], a['y1'], a['y2']
                parts.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2 - 8}" stroke="{stroke}" '
                              f'stroke-width="{sw}"{dash} marker-end="url(#{marker})"/>')
                if a['label']:
                    mid = (y1 + y2) / 2
                    self._label_at(parts, x, mid, a['label'], vertical=True, bg=a['bg'])
            elif a['kind'] == 'h':
                y, x1, x2 = a['y'], a['x1'], a['x2']
                end = x2 - 8 if x2 > x1 else x2 + 8
                parts.append(f'<line x1="{x1}" y1="{y}" x2="{end}" y2="{y}" stroke="{stroke}" '
                              f'stroke-width="{sw}"{dash} marker-end="url(#{marker})"/>')
                if a['label']:
                    mid = (x1 + x2) / 2
                    self._label_at(parts, mid, y - 14, a['label'], vertical=False, bg=a['bg'])
            else:
                pts = a['points']
                d = self._elbow_path(pts)
                parts.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{dash} '
                              f'marker-end="url(#{marker})"/>')
                if a['label']:
                    lx, ly = a['label_pos']
                    self._label_at(parts, lx, ly, a['label'], vertical=False, bg=a['bg'])

        for n in self.nodes:
            parts.append(self._draw_node(n))

        for (cx, cy, text) in self.captions:
            parts.append(f'<text x="{cx}" y="{cy}" fill="{t["muted"]}" font-size="{SUB_SIZE}" '
                          f'font-family="{FONT_MONO}" text-anchor="middle">{esc(text)}</text>')

        hairline_y = self.y + 40
        row_y = hairline_y + 30
        text_baseline = row_y + int(SMALL_SIZE * 0.32)
        parts.append(f'<line x1="40" y1="{hairline_y}" x2="{CANVAS_W-40}" y2="{hairline_y}" '
                      f'stroke="{t["rule"]}" stroke-width="0.8"/>')
        legend_word = 'LEGEND'
        parts.append(f'<text x="40" y="{text_baseline}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" '
                      f'font-family="{FONT_MONO}" letter-spacing="0.1em">{legend_word}</text>')
        legend_items = [
            ('diamond', 'Gate / decision'),
            ('oval', 'Loop outcome'),
            ('focal', 'Default / highest-stakes'),
        ]
        char_w = SMALL_SIZE * 0.62
        lx = 40 + len(legend_word) * char_w * 1.1 + 32
        for kind, text in legend_items:
            lx = self._legend_item(parts, lx, row_y, text_baseline, kind, text)
        if lx > CANVAS_W - 40:
            raise ValueError(f'legend overflows right margin: ends at {lx}, limit {CANVAS_W-40}')

        parts.append('</svg>')
        return '\n'.join(parts)

    def _legend_item(self, parts, x, row_y, text_baseline, kind, text):
        t = self.t
        cy = row_y
        if kind == 'diamond':
            cx = x + 10
            parts.append(f'<polygon points="{cx},{cy-9} {cx+11},{cy} {cx},{cy+9} {cx-11},{cy}" '
                          f'fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="1"/>')
        elif kind == 'oval':
            parts.append(f'<rect x="{x}" y="{cy-8}" width="20" height="16" rx="8" '
                          f'fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="1"/>')
        elif kind == 'focal':
            parts.append(f'<rect x="{x}" y="{cy-8}" width="20" height="16" rx="8" '
                          f'fill="{t["accent_tint"]}" stroke="{t["accent"]}" stroke-width="1"/>')
        parts.append(f'<text x="{x+30}" y="{text_baseline}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" '
                      f'font-family="{FONT_MONO}">{esc(text)}</text>')
        char_w = SMALL_SIZE * 0.62
        return x + 30 + len(text) * char_w + 26


def build(tokens, slug):
    L = TreeLayout(tokens, slug,
                    'Which loop — choosing a dev-loop for a change',
                    'Decision tree for picking a development loop: a Unity project goes straight to '
                    'dev-loop-unity or dev-loop-greybox by kind of work; otherwise auth/secrets, a '
                    'migration or contract change, or a multi-project change routes to dev-loop, which '
                    'can escalate to dev-loop-ultra and then dev-loop-ultra-opus; everything else is '
                    'ultralight or lite by how contained the change is.')
    L.gap(40)

    # ---- row 0: entry ----------------------------------------------------
    entry = L.oval('entry', 260, 60, 'Change to implement')

    # ---- row 1: Unity gate (new, per user/CLAUDE.md) ----------------------
    L.gap(40)
    U = L.diamond(190, 110, 'Unity\nproject?', x=CENTER)

    # ---- row 2: risk-surface gates + Unity kind-of-work fork ---------------
    row2_top = U['bottom'] + 60
    L.y = row2_top
    B = L.diamond(200, 140, 'Auth, secrets, or\nuntrusted input?', x=230)
    L.y = row2_top
    C = L.diamond(220, 140, 'Migration, schema,\nor public contract?', x=520)
    L.y = row2_top
    D = L.diamond(200, 140, 'More than\none project?', x=810)
    L.y = row2_top
    Wk = L.diamond(170, 110, 'Kind of\nwork?', x=1080)
    row2_bottom = max(B['bottom'], C['bottom'], D['bottom'], Wk['bottom'])

    # ---- row 3: dev-loop (focal) + Unity outcomes + contained-check --------
    row3_top = row2_bottom + 90
    L.y = row3_top
    F = L.oval('F', 200, 60, 'dev-loop', focal=True, x=CENTER)
    L.y = row3_top
    unity_out = L.oval('unity', 170, 60, 'dev-loop-unity', x=910)
    L.y = row3_top
    greybox_out = L.oval('greybox', 190, 60, 'dev-loop-greybox', x=1110)
    L.y = row3_top
    K = L.diamond(300, 210, 'Contained, ≤5 files,\nno concurrency,\nno new dependency?', x=230)
    row3_bottom = max(F['bottom'], unity_out['bottom'], greybox_out['bottom'], K['bottom'])

    # ---- row 4: escalation gate + ultralight/lite outcomes ------------------
    row4_top = row3_bottom + 40
    L.y = row4_top
    G = L.diamond(320, 210, 'Expensive to miss?\nmoney, tenant isolation,\ndestructive migration', x=CENTER)
    L.y = row4_top
    Lo = L.oval('Lo', 210, 60, 'dev-loop-ultralight', x=110)
    L.y = row4_top
    M = L.oval('M', 170, 60, 'dev-loop-lite', x=350)
    row4_bottom = max(G['bottom'], Lo['bottom'], M['bottom'])

    # ---- rows 5-7: single-spine escalation tail ------------------------------
    L.y = row4_bottom + 40
    H = L.oval('H', 220, 60, 'dev-loop-ultra', x=CENTER)
    L.gap(32)
    I = L.diamond(190, 130, 'Severe and\nirreversible?', x=CENTER)
    L.gap(32)
    J = L.oval('J', 230, 60, 'dev-loop-ultra-opus', focal=True, x=CENTER)

    # ---- connectors ----------------------------------------------------------
    L.straight_v(CENTER, entry['bottom'], U['top'])

    u_right = (U['right'], U['cy'])
    L.elbow([u_right, (1080, U['cy']), (1080, Wk['top'])], label='YES',
            label_pos=((U['right'] + 1080) / 2, U['cy'] - 14))

    # Unity gate -> B/C/D (no): fanned exit points on the lower edges plus a
    # staggered bus row each, so none of the three shares a stroke segment.
    u_hw = U['right'] - U['cx']
    exit_b = (U['cx'] - u_hw * 0.4, U['cy'] + (U['bottom'] - U['cy']) * 0.4)
    exit_c = (U['cx'], U['bottom'])
    exit_d = (U['cx'] + u_hw * 0.4, U['cy'] + (U['bottom'] - U['cy']) * 0.4)
    # NO labels sit on each branch's own horizontal bus segment, near its
    # destination diamond, rather than near the shared exit off U -- the
    # three exit points are only ~40-75px apart (all close to U's own
    # width), so labelling there stacks all three NOs on top of each other.
    # The bus rows fan out to B/C/D, which are far apart in x, so labelling
    # each bus segment keeps the three legible and unambiguous.
    L.elbow([exit_b, (exit_b[0], row2_top - 52), (B['cx'], row2_top - 52), (B['cx'], B['top'])],
            label='NO', label_pos=((exit_b[0] + B['cx']) / 2, row2_top - 60))
    L.elbow([exit_c, (exit_c[0], row2_top - 40), (C['cx'], row2_top - 40), (C['cx'], C['top'])],
            label='NO', label_pos=((exit_c[0] + C['cx']) / 2, row2_top - 48))
    L.elbow([exit_d, (exit_d[0], row2_top - 28), (D['cx'], row2_top - 28), (D['cx'], D['top'])],
            label='NO', label_pos=((exit_d[0] + D['cx']) / 2, row2_top - 36))

    # Kind-of-work -> Unity outcomes, opposite vertices so neither shares a segment.
    w_left = (Wk['left'], Wk['cy'])
    w_right = (Wk['right'], Wk['cy'])
    L.elbow([w_left, (w_left[0], row2_bottom + 20), (unity_out['cx'], row2_bottom + 20),
             (unity_out['cx'], unity_out['top'])], label='GAME CODE',
            label_pos=((w_left[0] + unity_out['cx']) / 2, row2_bottom + 6))
    L.elbow([w_right, (w_right[0], row2_bottom + 40), (greybox_out['cx'], row2_bottom + 40),
             (greybox_out['cx'], greybox_out['top'])], label='BLOCKOUT',
            label_pos=((w_right[0] + greybox_out['cx']) / 2, row2_bottom + 54))

    # B/C/D -> dev-loop (yes). B exits its right vertex (its bottom vertex is
    # reserved for the no-edge straight down to K) and detours right of K's
    # column before dropping to F's left edge — a straight drop from the
    # vertex would cut through K, which sits directly under B. C and D are
    # close enough to F's x that they attach to its top edge directly, each
    # on its own bus row so the three fan-ins never cross.
    b_right = (B['right'], B['cy'])
    detour_x = K['right'] + 60
    L.elbow([b_right, (detour_x, b_right[1]), (detour_x, F['cy']), (F['left'], F['cy'])],
            label='YES', label_pos=((b_right[0] + detour_x) / 2, b_right[1] - 14))
    L.elbow([(C['cx'], C['bottom']), (C['cx'], row3_top - 50), (F['cx'], row3_top - 50), (F['cx'], F['top'])],
            label='YES', label_pos=((C['cx'] + F['cx']) / 2, row3_top - 64))
    L.elbow([(D['cx'], D['bottom']), (D['cx'], row3_top - 25), (F['cx'] + 40, row3_top - 25), (F['cx'] + 40, F['top'])],
            label='YES', label_pos=((D['cx'] + F['cx'] + 40) / 2, row3_top - 39))

    L.straight_v(B['cx'], B['bottom'], K['top'], label='NO', bg='paper2')
    L.straight_v(F['cx'], F['bottom'], G['top'])

    k_left = (K['left'], K['cy'])
    k_right = (K['right'], K['cy'])
    L.elbow([k_left, (k_left[0] - 10, K['cy']), (Lo['cx'], K['cy']), (Lo['cx'], Lo['top'])],
            label='YES', label_pos=(k_left[0] - 40, K['cy'] - 14))
    L.elbow([k_right, (k_right[0] + 10, K['cy']), (M['cx'], K['cy']), (M['cx'], M['top'])],
            label='NO', label_pos=(k_right[0] + 40, K['cy'] - 14))

    L.straight_v(G['cx'], G['bottom'], H['top'], label='YES', bg='paper2')
    L.straight_v(H['cx'], H['bottom'], I['top'])
    L.straight_v(I['cx'], I['bottom'], J['top'], label='YES', bg='paper2')

    L.y = J['bottom']
    svg = L.render()
    return svg, L


def wrap_loop_choice_html(svg, dark, slug, title, eyebrow, h1):
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


if __name__ == '__main__':
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    light_svg, _ = build(LIGHT, 'loop-choice')
    dark_svg, _ = build(DARK, 'loop-choice-dark')

    h1 = 'Which loop — choosing a dev-loop for a change'
    with open(os.path.join(out_dir, 'loop-choice.html'), 'w', encoding='utf-8') as f:
        f.write(wrap_loop_choice_html(light_svg, False, 'loop-choice', h1,
                                       'Flowchart · Dev-Loop Diagrams', h1))
    with open(os.path.join(out_dir, 'loop-choice-dark.html'), 'w', encoding='utf-8') as f:
        f.write(wrap_loop_choice_html(dark_svg, True, 'loop-choice-dark', h1 + ' (dark)',
                                       'Flowchart · Dev-Loop Diagrams', h1))
    print('wrote', out_dir)
