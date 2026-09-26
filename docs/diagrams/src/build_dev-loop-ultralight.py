#!/usr/bin/env python3
"""Layout for dev-loop-ultralight: eligibility gate, single-pass nine-item
sweep, and the mandatory one-way escalation exits. Reuses the _build.py
engine; adds one small primitive (`chip`) this diagram needs that the base
Layout does not have (a compact, unconnected list item for the sweep), and
overrides `render()`'s legend so it only lists shapes this diagram actually
uses (no lane tiles here) and labels the accent edge for what it is in this
loop — an escalation exit, not a loop-back.
"""
import html
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _build import (
    Layout, LIGHT, DARK, wrap_html, CENTER, ZONE_X, ZONE_W, W,
    SUB_SIZE, SMALL_SIZE, FONT_SANS, FONT_MONO,
)


def esc(s):
    return html.escape(s, quote=True)


class ULayout(Layout):
    """Adds `chip`: a small unconnected list item (used for the nine-item
    sweep) — not part of the flow graph, purely a grouped-content primitive,
    same spirit as the base engine's lane_tile but simpler (title only)."""

    def chip(self, x, y, w, h, text):
        t = self.t
        self.nodes.append({
            'shape': 'chip', 'x': x, 'y': y, 'w': w, 'h': h,
            'fill': t['paper'], 'stroke': t['ink'], 'dash': '',
            'text': text, 'cx': x + w / 2, 'cy': y + h / 2,
        })
        return {'cx': x + w / 2, 'top': y, 'bottom': y + h, 'left': x, 'right': x + w}

    def _draw_node(self, n):
        if n['shape'] != 'chip':
            return super()._draw_node(n)
        t = self.t
        x, y, w, h = n['x'], n['y'], n['w'], n['h']
        parts = [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{t["paper"]}"/>',
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{n["fill"]}" '
            f'stroke="{n["stroke"]}" stroke-width="1"/>',
            f'<text x="{n["cx"]}" y="{n["cy"]+5}" fill="{t["ink"]}" font-size="{SUB_SIZE}" '
            f'font-family="{FONT_SANS}" text-anchor="middle">{esc(n["text"])}</text>',
        ]
        return '\n'.join(parts)

    # ---- render: identical to the base engine except the legend, which is
    # this diagram's own set of shapes actually used (no lane tiles here) and
    # the correct label for its single accent edge (an escalation exit, not a
    # loop-back — this loop never revisits an earlier phase). Duplicated
    # from Layout.render() rather than parameterising the base, per the
    # brief's "do not modify _build.py".
    def render(self):
        t = self.t
        H = self.y + 40 + 100
        H = ((H + 3) // 4) * 4
        parts = []
        parts.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
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

        for (zx, zy, zw, zh, zlabel, zsub) in self.zones:
            parts.append(f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" rx="8" '
                          f'fill="{t["paper2"]}" stroke="{t["rule_solid"]}" stroke-width="1"/>')
            parts.append(f'<text x="{zx+20}" y="{zy+28}" fill="{t["soft"]}" font-size="{SMALL_SIZE}" '
                          f'font-family="{FONT_MONO}" letter-spacing="0.1em">{esc(zlabel.upper())}</text>')
            if zsub:
                parts.append(f'<text x="{zx+20}" y="{zy+46}" fill="{t["muted"]}" font-size="{SUB_SIZE}" '
                              f'font-family="{FONT_MONO}">{esc(zsub)}</text>')

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
        parts.append(f'<line x1="40" y1="{hairline_y}" x2="{W-40}" y2="{hairline_y}" '
                      f'stroke="{t["rule"]}" stroke-width="0.8"/>')
        legend_word = 'LEGEND'
        parts.append(f'<text x="40" y="{text_baseline}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" '
                      f'font-family="{FONT_MONO}" letter-spacing="0.1em">{legend_word}</text>')
        # This diagram has no parallel review lanes (one reviewer sweeps all
        # nine concerns), so the base engine's "Review lane" swatch is
        # dropped — CONVENTIONS.md: one swatch per shape actually used.
        legend_items = [
            ('rect', 'Phase / step'),
            ('diamond', 'Gate / decision'),
            ('oval', 'Entry / exit'),
            ('dashterm', 'Blocked / escalate'),
            ('accentline', 'Escalation exit'),
        ]
        char_w = SMALL_SIZE * 0.62
        lx = 40 + len(legend_word) * char_w * 1.1 + 32
        for kind, text in legend_items:
            lx = self._legend_item(parts, lx, row_y, text_baseline, kind, text)
        if lx > W - 40:
            raise ValueError(f'legend overflows right margin: ends at {lx}, limit {W-40}')

        parts.append('</svg>')
        return '\n'.join(parts)


TITLE = 'dev-loop-ultralight — the minimal loop'
DESC = ('Flowchart of dev-loop-ultralight: the six-point eligibility gate that is the '
        'loop\'s entire safety mechanism; a single handoff for implement-and-test; one '
        'reviewer sweeping all nine review concerns in one pass; triage; the mandatory, '
        'one-way escalation exits to dev-loop-lite and the full dev-loop; a single fix '
        'round with no second round and no verification phase; and the walkthrough and '
        'PR that close it out.')

ELIG_CRITERIA = [
    '1 project, ≤ 5 files',
    'no auth/secrets/PII',
    'no migration/schema/contract',
    'no concurrency/tx change',
    'no new dependency',
    'easy to roll back',
]

SWEEP_ITEMS = [
    '1 — Requirements: brief, nothing more',
    '2 — Correctness: logic, boundaries',
    '3 — Error paths: throws, timeouts',
    '4 — Separation of concerns',
    '5 — Placement vs. repo convention',
    '6 — Standards: coding-standards + repo',
    '7 — Security: authz/untrusted input',
    '8 — Tests: would they catch a bug?',
    '9 — Surplus: guards nothing needs',
]


def build(tokens, slug):
    L = ULayout(tokens, slug, TITLE, DESC)
    L.gap(40)

    # ---- Zone 1: Eligibility gate ----------------------------------------
    L.zone_start('Eligibility — checked before anything else',
                  'the entire safety mechanism of this loop — nothing downstream catches '
                  'what should not have been here')
    L.gap(52)
    entry = L.oval('entry', 220, 60, '/dev-loop-ultralight')
    L.gap(40)
    elig = L.diamond(360, 280, '\n'.join(ELIG_CRITERIA))
    elig_bottom = elig['bottom']
    L.y = elig['cy'] - 78
    eligTerm = L.terminal_dual(ZONE_X + 16, L.y, 200, 156,
                                '→ lite', 'any ONE criterion fails',
                                '→ full', 'several fail, or unsure')
    L.y = elig_bottom
    L.zone_end()
    L.gap(40)

    # ---- Zone 2: Frame, implement & test ----------------------------------
    L.zone_start('Frame · implement & test',
                  'one handoff — too small to split')
    L.gap(52)
    p0 = L.rect(640, 100, 'Phase 0 — Frame',
                'Requirement, DoD, files, source branch → brief.md + notes.md')
    L.gap(32)
    p1 = L.rect(640, 100, 'Phase 1 — Implement and test',
                'sidekick by default; tests must fail if behaviour regresses')
    L.zone_end()
    L.gap(40)

    # ---- Zone 3: One reviewer, nine-item sweep ----------------------------
    L.zone_start('One reviewer — nine concerns, one pass',
                  'reviewer-ultralight — Sonnet · High')
    L.gap(52)
    p2 = L.rect(640, 90, 'Phase 2 — Review',
                'Snapshot tree first; spawn once, read-only → round-1/ultralight.json + .log.md')
    L.gap(28)
    sweep_top = L.y
    chip_w, chip_h, gapx, gapy = 300, 44, 20, 16
    start_x = ZONE_X + (ZONE_W - (chip_w * 3 + gapx * 2)) // 2
    for i, text in enumerate(SWEEP_ITEMS):
        row, col = divmod(i, 3)
        cx = start_x + col * (chip_w + gapx)
        cy = sweep_top + row * (chip_h + gapy)
        L.chip(cx, cy, chip_w, chip_h, text)
    L.y = sweep_top + 3 * chip_h + 2 * gapy
    L.zone_end()
    L.gap(40)

    # ---- Zone 4: Triage, escalate, fix ------------------------------------
    L.zone_start('Triage · mandatory one-way escalation · fix')
    L.gap(52)
    p3 = L.rect(640, 130, 'Phase 3 — Triage',
                'evidence gate · cause gate · defect ≠ remedy · wontfix.json · conventions.md')
    L.gap(32)
    esc_d = L.diamond(280, 140, 'Any escalation\ntrigger?', focal=True)
    esc_d_bottom = esc_d['bottom']
    L.y = esc_d['cy'] - 68
    escTerm = L.terminal_dual(ZONE_X + 16, L.y, 220, 136,
                               '→ full', 'security/arch/concurrency',
                               '→ lite', 'other major risk')
    L.y = esc_d_bottom
    L.gap(32)
    p4 = L.rect(640, 100, 'Phase 4 — Fix',
                'would_have_been_bug → failing test first, then fix, then passing')
    L.zone_end()
    L.gap(40)

    # ---- Zone 5: Exit — no second round, no verification --------------
    L.zone_start('Exit — one round only, no verification phase')
    L.gap(52)
    p5 = L.diamond(280, 130, 'Fixes cleared\nit?')
    p5_bottom = p5['bottom']
    L.y = p5['cy'] - 30
    p5Term = L.oval('p5exit', 220, 60, '→ lite', dashed=True,
                     x=ZONE_X + 16 + 110)
    L.y = p5_bottom
    L.gap(32)
    p5b = L.rect(640, 100, 'Phase 5b — Walkthrough',
                 'sidekick drafts from notes.md; the lead checks it inline (no separate reviewer)')
    L.gap(32)
    p6 = L.rect(640, 110, 'Phase 6 — Commit, push, pull request',
                'stage untracked · verify --stat + tree digest · PR targets source branch')
    L.gap(32)
    end = L.oval('end', 200, 60, 'PR opened')
    L.zone_end()

    # ---- connectors --------------------------------------------------------
    L.straight_v(CENTER, entry['bottom'], elig['top'])
    L.straight_v(CENTER, elig['bottom'], p0['top'], label='all hold', bg='paper2')
    L.straight_v(CENTER, p0['bottom'], p1['top'])
    L.straight_v(CENTER, p1['bottom'], p2['top'])
    L.straight_v(CENTER, p2['bottom'], p3['top'], bg='paper2')
    L.straight_v(CENTER, p3['bottom'], esc_d['top'])
    L.straight_v(CENTER, esc_d['bottom'], p4['top'], label='no trigger', bg='paper2')
    L.straight_v(CENTER, p4['bottom'], p5['top'])
    L.straight_v(CENTER, p5['bottom'], p5b['top'], label='yes', bg='paper2')
    L.straight_v(CENTER, p5b['bottom'], p6['top'])
    L.straight_v(CENTER, p6['bottom'], end['top'])

    # eligibility fail exits — two fanned, non-accent
    top_y = eligTerm['top'] + eligTerm['h'] * 0.28
    bot_y = eligTerm['top'] + eligTerm['h'] * 0.72
    L.straight_h(top_y, elig['left'], eligTerm['right'], label='one', bg='paper2')
    L.straight_h(bot_y, elig['left'], eligTerm['right'], label='many', bg='paper2')

    # escalation exits — one accent (defining edge), one muted
    e_top_y = escTerm['top'] + escTerm['h'] * 0.28
    e_bot_y = escTerm['top'] + escTerm['h'] * 0.72
    L.straight_h(e_top_y, esc_d['left'], escTerm['right'], accent=True, label='critical', bg='paper2')
    L.straight_h(e_bot_y, esc_d['left'], escTerm['right'], label='major', bg='paper2')

    # phase-5 no-clear exit — single, muted, dashed
    L.straight_h(p5['cy'], p5['left'], p5Term['right'], label='no', bg='paper2')

    # Placed inside the zone frame (clear of the left corridor, which is the
    # only corridor this diagram's connectors use), not at RIGHT_CH — the
    # right corridor is outside every zone's frame.
    CAP_X = 1040
    L.caption(CAP_X, p2['cy'] - 11, 'no scratch')
    L.caption(CAP_X, p2['cy'] + 11, 'worktree')
    L.caption(CAP_X, p3['cy'] - 11, 'wontfix.json')
    L.caption(CAP_X, p3['cy'] + 11, 'dies here')
    L.caption(CAP_X, p5b['cy'] - 11, 'no verification')
    L.caption(CAP_X, p5b['cy'] + 11, 'phase')

    svg = L.render()
    return svg, L


_PILOT_H1 = '<h1>dev-loop — the full development loop</h1>'


def _wrap(svg, dark, slug, title, eyebrow):
    out = wrap_html(svg, dark, slug, title, eyebrow)
    return out.replace(_PILOT_H1, f'<h1>{esc(title)}</h1>')


if __name__ == '__main__':
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    light_svg, _ = build(LIGHT, 'dev-loop-ultralight')
    dark_svg, _ = build(DARK, 'dev-loop-ultralight-dark')

    with open(os.path.join(out_dir, 'dev-loop-ultralight.html'), 'w', encoding='utf-8') as f:
        f.write(_wrap(light_svg, False, 'dev-loop-ultralight', TITLE,
                       'Flowchart · Dev-Loop Diagrams'))
    with open(os.path.join(out_dir, 'dev-loop-ultralight-dark.html'), 'w', encoding='utf-8') as f:
        f.write(_wrap(dark_svg, True, 'dev-loop-ultralight-dark', TITLE + ' (dark)',
                       'Flowchart · Dev-Loop Diagrams'))
    print('wrote', out_dir)
