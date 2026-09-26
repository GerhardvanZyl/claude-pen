#!/usr/bin/env python3
"""One-off layout generator for the dev-loop flowchart (light + dark).
Not a deliverable -- used only to keep coordinates grid-aligned and to avoid
hand-arithmetic errors. The committed output is the static HTML it writes.
"""
import html

W = 1280
COL_X, COL_W = 320, 640          # single-column node band (centered)
ZONE_X, ZONE_W = 160, 960        # zone frame band
LEFT_CH, RIGHT_CH = 100, 1180    # loop-back corridor centers (in side margins)
CENTER = 640

# Type ramp. GitHub displays a README image at ~880px wide; this diagram's
# viewBox is 1280 wide, so the display scale is ~880/1280 = 0.6875. Chosen so
# every tier clears the floor with margin at that scale (not exactly at it):
#   NAME_SIZE  17 -> 11.7px displayed (floor: node names  >= 11px)
#   SUB_SIZE   14 ->  9.6px displayed (body text, no explicit floor, kept
#                      above SMALL_SIZE for hierarchy)
#   SMALL_SIZE 13 ->  8.9px displayed (floor: chips/triggers/eyebrows/
#                      arrow labels/legend >= 8px)
NAME_SIZE = 17
SUB_SIZE = 14
SMALL_SIZE = 13

class Layout:
    def __init__(self, tokens, slug, title, desc):
        self.t = tokens
        self.slug = slug
        self.title = title
        self.desc = desc
        self.els = []      # drawn after defs/bg, before labels-on-top handling not needed (we order manually)
        self.arrows = []
        self.nodes = []
        self.zones = []
        self.labels = []
        self.captions = []
        self.y = 0

    # ---- primitives -------------------------------------------------
    def zone_start(self, label, subtitle=None):
        self._zone_label = label
        self._zone_subtitle = subtitle
        self._zone_top = self.y

    def zone_end(self):
        pad_bottom = 24
        bottom = self.y + pad_bottom
        top = self._zone_top
        self.zones.append((ZONE_X, top, ZONE_W, bottom - top, self._zone_label, self._zone_subtitle))
        self.y = bottom

    def gap(self, n):
        self.y += n

    def caption(self, x, y, text):
        self.captions.append((x, y, text))

    def oval(self, key, w, h, text, focal=False, dashed=False, sub_lines=None, x=None):
        t = self.t
        cx = x if x is not None else CENTER
        x0 = cx - w // 2
        y0 = self.y
        fill = t['accent_tint'] if focal else t['paper']
        stroke = t['accent'] if focal else t['ink']
        dash = ' stroke-dasharray="5,4"' if dashed else ''
        self.nodes.append({
            'shape': 'oval', 'x': x0, 'y': y0, 'w': w, 'h': h,
            'fill': fill, 'stroke': stroke, 'dash': dash,
            'text': text, 'sub': sub_lines or [], 'cx': cx, 'cy': y0 + h / 2,
        })
        self.y = y0 + h
        return {'cx': cx, 'cy': y0 + h / 2, 'top': y0, 'bottom': y0 + h, 'left': x0, 'right': x0 + w, 'y0': y0, 'h': h}

    def rect(self, w, h, title, sub, x=None):
        t = self.t
        cx = x if x is not None else CENTER
        x0 = cx - w // 2
        y0 = self.y
        self.nodes.append({
            'shape': 'rect', 'x': x0, 'y': y0, 'w': w, 'h': h,
            'fill': t['paper'], 'stroke': t['ink'], 'dash': '',
            'title': title, 'sub': sub, 'cx': cx, 'cy': y0 + h / 2,
        })
        self.y = y0 + h
        return {'cx': cx, 'cy': y0 + h / 2, 'top': y0, 'bottom': y0 + h, 'left': x0, 'right': x0 + w, 'y0': y0, 'h': h}

    def diamond(self, w, h, title, focal=False, x=None, y=None):
        t = self.t
        cx = x if x is not None else CENTER
        y0 = y if y is not None else self.y
        fill = t['accent_tint'] if focal else t['paper']
        stroke = t['accent'] if focal else t['ink']
        self.nodes.append({
            'shape': 'diamond', 'x': cx - w // 2, 'y': y0, 'w': w, 'h': h,
            'fill': fill, 'stroke': stroke, 'dash': '', 'focal': focal,
            'title': title, 'cx': cx, 'cy': y0 + h / 2,
        })
        if y is None:
            self.y = y0 + h
        return {
            'cx': cx, 'cy': y0 + h / 2, 'top': y0, 'bottom': y0 + h,
            'left': cx - w // 2, 'right': cx + w // 2, 'y0': y0, 'h': h,
        }

    def lane_tile(self, x, y, w, h, name, tier, trigger):
        t = self.t
        self.nodes.append({
            'shape': 'lane', 'x': x, 'y': y, 'w': w, 'h': h,
            'fill': t['paper'], 'stroke': t['ink'], 'dash': '',
            'name': name, 'tier': tier, 'trigger': trigger, 'cx': x + w / 2, 'cy': y + h / 2,
        })
        return {'cx': x + w / 2, 'top': y, 'bottom': y + h, 'left': x, 'right': x + w}

    def terminal_dual(self, x, y, w, h, top_title, top_sub, bot_title, bot_sub, dashed=True):
        t = self.t
        self.nodes.append({
            'shape': 'terminal', 'x': x, 'y': y, 'w': w, 'h': h,
            'fill': t['paper'], 'stroke': t['muted'], 'dash': ' stroke-dasharray="4,3"' if dashed else '',
            'top_title': top_title, 'top_sub': top_sub, 'bot_title': bot_title, 'bot_sub': bot_sub,
            'cx': x + w / 2, 'cy': y + h / 2,
        })
        return {'cx': x + w / 2, 'top': y, 'bottom': y + h, 'left': x, 'right': x + w, 'y0': y, 'h': h}

    # ---- connectors ---------------------------------------------------
    def straight_v(self, x, y1, y2, accent=False, label=None, dashed=False, bg='paper'):
        self.arrows.append({'kind': 'v', 'x': x, 'y1': y1, 'y2': y2,
                             'accent': accent, 'label': label, 'dashed': dashed, 'bg': bg})

    def elbow(self, points, accent=False, label=None, dashed=False, label_pos=None, bg='paper'):
        self.arrows.append({'kind': 'elbow', 'points': points, 'accent': accent,
                             'label': label, 'dashed': dashed, 'label_pos': label_pos, 'bg': bg})

    def straight_h(self, y, x1, x2, accent=False, label=None, dashed=False, bg='paper'):
        # Right-to-left or left-to-right; arrowhead always lands at x2.
        self.arrows.append({'kind': 'h', 'y': y, 'x1': x1, 'x2': x2,
                             'accent': accent, 'label': label, 'dashed': dashed, 'bg': bg})

    # ---- render ---------------------------------------------------
    def render(self):
        t = self.t
        H = self.y + 40 + 100  # bottom margin + taller legend row (bigger type ramp)
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

        # zones (painted first, so labels/arrows/nodes can sit on top safely)
        for (zx, zy, zw, zh, zlabel, zsub) in self.zones:
            parts.append(f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" rx="8" '
                          f'fill="{t["paper2"]}" stroke="{t["rule_solid"]}" stroke-width="1"/>')
            parts.append(f'<text x="{zx+20}" y="{zy+28}" fill="{t["soft"]}" font-size="{SMALL_SIZE}" '
                          f'font-family="{FONT_MONO}" letter-spacing="0.1em">{esc(zlabel.upper())}</text>')
            if zsub:
                parts.append(f'<text x="{zx+20}" y="{zy+46}" fill="{t["muted"]}" font-size="{SUB_SIZE}" '
                              f'font-family="{FONT_MONO}">{esc(zsub)}</text>')

        # arrows (before nodes)
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

        # nodes
        for n in self.nodes:
            parts.append(self._draw_node(n))

        # captions (small mono context text, no box, not near any connector)
        for (cx, cy, text) in self.captions:
            parts.append(f'<text x="{cx}" y="{cy}" fill="{t["muted"]}" font-size="{SUB_SIZE}" '
                          f'font-family="{FONT_MONO}" text-anchor="middle">{esc(text)}</text>')

        # legend — hairline above, then "LEGEND" + every item on one shared
        # baseline/row beneath it (SKILL.md §6: never split label from items).
        hairline_y = self.y + 40
        row_y = hairline_y + 30          # icon vertical center AND text baseline anchor
        text_baseline = row_y + int(SMALL_SIZE * 0.32)
        parts.append(f'<line x1="40" y1="{hairline_y}" x2="{W-40}" y2="{hairline_y}" '
                      f'stroke="{t["rule"]}" stroke-width="0.8"/>')
        legend_word = 'LEGEND'
        parts.append(f'<text x="40" y="{text_baseline}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" '
                      f'font-family="{FONT_MONO}" letter-spacing="0.1em">{legend_word}</text>')
        # Short enough, at 8px/char (13px mono) x 6 items, to clear the 40px
        # right margin on a 1280-wide canvas — verified by _audit_legend_width.
        legend_items = [
            ('rect', 'Phase / step'),
            ('diamond', 'Gate / decision'),
            ('lane', 'Review lane'),
            ('oval', 'Entry / exit'),
            ('dashterm', 'Blocked / escalate'),
            ('accentline', 'Loop-back'),
        ]
        char_w = SMALL_SIZE * 0.62  # mono advance, matches style-guide's width budget
        lx = 40 + len(legend_word) * char_w * 1.1 + 32  # 1.1 ~= the tracked letter-spacing
        for kind, text in legend_items:
            lx = self._legend_item(parts, lx, row_y, text_baseline, kind, text)
        if lx > W - 40:
            raise ValueError(f'legend overflows right margin: ends at {lx}, limit {W-40}')

        parts.append('</svg>')
        return '\n'.join(parts)

    def _legend_item(self, parts, x, row_y, text_baseline, kind, text):
        t = self.t
        cy = row_y
        if kind == 'rect':
            parts.append(f'<rect x="{x}" y="{cy-8}" width="20" height="16" rx="3" '
                          f'fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="1"/>')
        elif kind == 'diamond':
            cx = x + 10
            parts.append(f'<polygon points="{cx},{cy-9} {cx+11},{cy} {cx},{cy+9} {cx-11},{cy}" '
                          f'fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="1"/>')
        elif kind == 'lane':
            parts.append(f'<rect x="{x}" y="{cy-8}" width="20" height="16" rx="3" '
                          f'fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="1"/>')
        elif kind == 'oval':
            parts.append(f'<rect x="{x}" y="{cy-8}" width="20" height="16" rx="8" '
                          f'fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="1"/>')
        elif kind == 'dashterm':
            parts.append(f'<rect x="{x}" y="{cy-8}" width="20" height="16" rx="8" fill="{t["paper"]}" '
                          f'stroke="{t["muted"]}" stroke-width="1" stroke-dasharray="3,2"/>')
        elif kind == 'accentline':
            parts.append(f'<line x1="{x}" y1="{cy}" x2="{x+20}" y2="{cy}" stroke="{t["accent"]}" stroke-width="1.4"/>')
        parts.append(f'<text x="{x+30}" y="{text_baseline}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" '
                      f'font-family="{FONT_MONO}">{esc(text)}</text>')
        char_w = SMALL_SIZE * 0.62  # mono advance
        return x + 30 + len(text) * char_w + 26

    def _elbow_path(self, pts, r=8):
        # pts: list of (x,y). Build rounded orthogonal path.
        d = f'M {pts[0][0]} {pts[0][1]} '
        for i in range(1, len(pts) - 1):
            x0, y0 = pts[i - 1]
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            # direction into corner
            dx1 = 1 if x1 > x0 else (-1 if x1 < x0 else 0)
            dy1 = 1 if y1 > y0 else (-1 if y1 < y0 else 0)
            dx2 = 1 if x2 > x1 else (-1 if x2 < x1 else 0)
            dy2 = 1 if y2 > y1 else (-1 if y2 < y1 else 0)
            ax, ay = x1 - dx1 * r, y1 - dy1 * r
            bx, by = x1 + dx2 * r, y1 + dy2 * r
            d += f'L {ax} {ay} Q {x1} {y1} {bx} {by} '
        last = pts[-1]
        # shorten final segment by 8 for the marker
        px, py = pts[-2]
        lx, ly = last
        if lx == px:
            ly = ly - 8 if ly > py else ly + 8
        else:
            lx = lx - 8 if lx > px else lx + 8
        d += f'L {lx} {ly}'
        return d

    def _label_at(self, parts, x, y, text, vertical, bg):
        t = self.t
        bgc = t['paper'] if bg == 'paper' else t['paper2']
        w = max(32, len(text) * 8 + 16)
        h = 18
        rx0 = x - w / 2
        ry0 = y - h / 2
        parts.append(f'<rect x="{rx0}" y="{ry0}" width="{w}" height="{h}" rx="3" fill="{bgc}"/>')
        parts.append(f'<text x="{x}" y="{y+4}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" font-family="{FONT_MONO}" '
                      f'text-anchor="middle" letter-spacing="0.03em">{esc(text.upper())}</text>')

    def _draw_node(self, n):
        t = self.t
        parts = []
        x, y, w, h = n['x'], n['y'], n['w'], n['h']
        # opaque mask so crossing lines never bleed through a transparent fill
        if n['shape'] in ('oval',):
            rxx = h / 2
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rxx}" fill="{t["paper"]}"/>')
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rxx}" fill="{n["fill"]}" '
                          f'stroke="{n["stroke"]}" stroke-width="1"{n["dash"]}/>')
            parts.append(f'<text x="{n["cx"]}" y="{n["cy"]+6}" fill="{t["ink"]}" '
                          f'font-size="{NAME_SIZE}" font-weight="600" '
                          f'font-family="{FONT_SANS}" text-anchor="middle">{esc(n["text"])}</text>')
        elif n['shape'] == 'rect':
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{t["paper"]}"/>')
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{n["fill"]}" '
                          f'stroke="{n["stroke"]}" stroke-width="1"{n["dash"]}/>')
            parts.append(f'<text x="{n["cx"]}" y="{y+34}" fill="{t["ink"]}" font-size="{NAME_SIZE}" font-weight="600" '
                          f'font-family="{FONT_SANS}" text-anchor="middle">{esc(n["title"])}</text>')
            if n['sub']:
                parts.append(f'<text x="{n["cx"]}" y="{y+62}" fill="{t["muted"]}" font-size="{SUB_SIZE}" '
                              f'font-family="{FONT_SANS}" text-anchor="middle">{esc(n["sub"])}</text>')
        elif n['shape'] == 'diamond':
            cx, cy = n['cx'], n['cy']
            hw, hh = w / 2, h / 2
            parts.append(f'<polygon points="{cx},{y} {cx+hw},{cy} {cx},{y+h} {cx-hw},{cy}" fill="{t["paper"]}"/>')
            parts.append(f'<polygon points="{cx},{y} {cx+hw},{cy} {cx},{y+h} {cx-hw},{cy}" fill="{n["fill"]}" '
                          f'stroke="{n["stroke"]}" stroke-width="1.2"/>')
            lines = n['title'].split('\n')
            if len(lines) == 1:
                parts.append(f'<text x="{cx}" y="{cy+6}" fill="{t["ink"]}" font-size="{NAME_SIZE}" font-weight="600" '
                              f'font-family="{FONT_SANS}" text-anchor="middle">{esc(lines[0])}</text>')
            else:
                start_y = cy - (len(lines) - 1) * 10 + 6
                for i, line in enumerate(lines):
                    parts.append(f'<text x="{cx}" y="{start_y + i*20}" fill="{t["ink"]}" '
                                  f'font-size="{NAME_SIZE}" font-weight="600" '
                                  f'font-family="{FONT_SANS}" text-anchor="middle">{esc(line)}</text>')
        elif n['shape'] == 'lane':
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{t["paper"]}"/>')
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{n["fill"]}" '
                          f'stroke="{n["stroke"]}" stroke-width="1"/>')
            parts.append(f'<text x="{n["cx"]}" y="{y+28}" fill="{t["ink"]}" font-size="{NAME_SIZE}" font-weight="600" '
                          f'font-family="{FONT_SANS}" text-anchor="middle">{esc(n["name"])}</text>')
            parts.append(f'<rect x="{n["cx"]-60}" y="{y+38}" width="120" height="20" rx="3" fill="transparent" '
                          f'stroke="{t["soft"]}" stroke-width="0.8"/>')
            parts.append(f'<text x="{n["cx"]}" y="{y+52}" fill="{t["soft"]}" font-size="{SMALL_SIZE}" '
                          f'font-family="{FONT_MONO}" text-anchor="middle" '
                          f'letter-spacing="0.03em">{esc(n["tier"].upper())}</text>')
            parts.append(f'<text x="{n["cx"]}" y="{y+h-14}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" '
                          f'font-family="{FONT_MONO}" text-anchor="middle">{esc(n["trigger"])}</text>')
        elif n['shape'] == 'terminal':
            rxx = 16
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rxx}" fill="{t["paper"]}"/>')
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rxx}" fill="{n["fill"]}" '
                          f'stroke="{n["stroke"]}" stroke-width="1"{n["dash"]}/>')
            midy = y + h / 2
            parts.append(f'<line x1="{x+16}" y1="{midy}" x2="{x+w-16}" y2="{midy}" '
                          f'stroke="{t["rule"]}" stroke-width="0.8"/>')
            cx = n['cx']
            parts.append(f'<text x="{cx}" y="{y+28}" fill="{t["ink"]}" font-size="{NAME_SIZE}" font-weight="600" '
                          f'font-family="{FONT_SANS}" text-anchor="middle">{esc(n["top_title"])}</text>')
            parts.append(f'<text x="{cx}" y="{y+48}" fill="{t["muted"]}" font-size="{SUB_SIZE}" '
                          f'font-family="{FONT_SANS}" text-anchor="middle">{esc(n["top_sub"])}</text>')
            parts.append(f'<text x="{cx}" y="{midy+26}" fill="{t["ink"]}" font-size="{NAME_SIZE}" font-weight="600" '
                          f'font-family="{FONT_SANS}" text-anchor="middle">{esc(n["bot_title"])}</text>')
            parts.append(f'<text x="{cx}" y="{midy+46}" fill="{t["muted"]}" font-size="{SUB_SIZE}" '
                          f'font-family="{FONT_SANS}" text-anchor="middle">{esc(n["bot_sub"])}</text>')
        return '\n'.join(parts)


FONT_SANS = "system-ui, -apple-system, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

LIGHT = dict(
    paper='#ffffff', paper2='#f6f8fa', ink='#1f2328', muted='#59636e', soft='#818b98',
    rule='rgba(31,35,40,0.15)', rule_solid='#d1d9e0', accent='#0969da',
    accent_tint='rgba(9,105,218,0.08)',
)
DARK = dict(
    paper='#0d1117', paper2='#151b23', ink='#f0f6fc', muted='#9198a1', soft='#656c76',
    rule='rgba(240,246,252,0.15)', rule_solid='#3d444d', accent='#4493f8',
    accent_tint='rgba(68,147,248,0.12)',
)


def build(tokens, slug):
    L = Layout(tokens, slug,
               'dev-loop — the full development loop',
               'Flowchart of the full dev-loop: nine phases from framing through implementation, '
               'tests and shipping; a nine-lane parallel review round with model tiers; a tree-integrity '
               'check with recovery; and the blocked, escalate, and loop-back-to-Phase-3 exits that bound it.')
    L.gap(40)

    # ---- Zone 1: Entry, Implement, Test --------------------------------
    L.zone_start('Entry · implement · test',
                 'full loop when: auth/secrets · schema or contract change · multi-project · hard rollback')
    L.gap(52)
    entry = L.oval('entry', 200, 60, '/dev-loop')
    L.gap(40)
    p0 = L.rect(640, 100, 'Phase 0 — Frame the slice',
                'Requirement, constraints, DoD, source branch → brief.md + notes.md')
    L.gap(32)
    p1 = L.rect(640, 100, 'Phase 1 — Implement',
                'Sidekick tier; conforms to coding-standards + solution-architecture')
    L.gap(32)
    p2 = L.rect(640, 100, 'Phase 2 — Tests',
                'Unit / integration / UI — must fail if the behaviour regresses')
    L.zone_end()
    L.gap(40)

    # ---- Zone 2: Plan & delegate ---------------------------------------
    L.zone_start('Plan the round · delegate')
    L.gap(52)
    p3 = L.rect(640, 100, 'Phase 3 — Plan the review round',
                'Classify every lane applicable/skipped (diff-based) · snapshot tree')
    L.gap(32)
    p4 = L.rect(640, 100, 'Phase 4 — Delegate',
                'Spawn applicable lanes in parallel, max 4 at a time; card-only briefing')
    L.zone_end()
    L.gap(40)

    # ---- Zone 3: Nine review lanes --------------------------------------
    L.zone_start('Nine review lanes — one owner per concern')
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
    ]
    tile_w, tile_h, gapx, gapy = 280, 100, 24, 24
    start_x = ZONE_X + (ZONE_W - (tile_w * 3 + gapx * 2)) // 2
    lane_anchors = []
    for i, (name, tier, trig) in enumerate(lane_defs):
        row, col = divmod(i, 3)
        tx = start_x + col * (tile_w + gapx)
        ty = lanes_top + row * (tile_h + gapy)
        a = L.lane_tile(tx, ty, tile_w, tile_h, name, tier, trig)
        lane_anchors.append(a)
    lanes_bottom = lanes_top + 3 * tile_h + 2 * gapy
    L.y = lanes_bottom
    L.zone_end()
    L.gap(40)

    # ---- Zone 4: Integrity, triage, fix ---------------------------------
    L.zone_start('Integrity check · triage · fix')
    L.gap(52)
    integ = L.diamond(260, 150, 'Tree moved since\nround start?')
    L.gap(32)
    p5 = L.rect(640, 100, 'Phase 5 — Triage',
                'Cluster by cause · gate on evidence & cause · defect ≠ remedy')
    L.gap(32)
    p6 = L.rect(640, 100, 'Phase 6 — Fix',
                'One brief; regression test fails → fix → passes; smallest validation')
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
                            'ESCALATE → dev-loop-ultra', 'Critical in unexpected lane, or recurs')
    L.y = p7_y + p7_h
    L.gap(32)
    p8 = L.rect(640, 100, 'Phase 8 — Independent verification',
                'Spawned once when risky/uncertain — checks intent, coverage, deferrals')
    L.gap(32)
    p8b = L.rect(640, 100, 'Phase 8b — Walkthrough',
                 'Draft from notes.md (not diff) → review → snapshot = Phase 9 baseline')
    L.gap(32)
    p9 = L.rect(640, 100, 'Phase 9 — Commit, push, pull request',
                'Stage incl. untracked · verify diff by content · PR targets source branch')
    L.gap(32)
    end = L.oval('end', 200, 60, 'PR opened')
    L.zone_end()

    # ---- connectors -----------------------------------------------------
    bg1 = 'paper2'
    L.straight_v(CENTER, entry['bottom'], p0['top'])
    L.straight_v(CENTER, p0['bottom'], p1['top'])
    L.straight_v(CENTER, p1['bottom'], p2['top'])
    L.straight_v(CENTER, p2['bottom'], p3['top'])
    L.straight_v(CENTER, p3['bottom'], p4['top'])
    L.straight_v(CENTER, p4['bottom'], lanes_top - 6, bg=bg1)
    L.straight_v(CENTER, lanes_bottom + 6, integ['top'], bg=bg1)
    L.straight_v(CENTER, integ['bottom'], p5['top'], label='clean', bg='paper2')
    L.straight_v(CENTER, p5['bottom'], p6['top'])
    L.straight_v(CENTER, p6['bottom'], p7['top'])
    L.straight_v(CENTER, p7['bottom'], p8['top'], label='pass', bg='paper2')
    L.straight_v(CENTER, p8['bottom'], p8b['top'])
    L.straight_v(CENTER, p8b['bottom'], p9['top'])
    L.straight_v(CENTER, p9['bottom'], end['top'])

    # integrity -> phase4 (dashed recovery loop-back), left corridor
    L.elbow([
        (integ['left'], integ['cy']),
        (LEFT_CH, integ['cy']),
        (LEFT_CH, p4['cy']),
        (p4['left'], p4['cy']),
    ], dashed=True, label='rerun lane', label_pos=(LEFT_CH, (integ['cy'] + p4['cy']) / 2))

    # phase7 -> phase3 (accent loop-back, the defining edge), right corridor
    L.elbow([
        (p7['right'], p7['cy']),
        (RIGHT_CH, p7['cy']),
        (RIGHT_CH, p3['cy']),
        (p3['right'], p3['cy']),
    ], accent=True, label='next round', label_pos=(RIGHT_CH, (p7['cy'] + p3['cy']) / 2))

    # phase7 -> terminal (blocked / escalate) — straight horizontal, two fanned
    # attach points on phase7's left edge (>=12px apart), landing on term's right edge.
    L.straight_h(top_attach_y, p7['left'], term['right'], label='blocked', bg='paper2')
    L.straight_h(bot_attach_y, p7['left'], term['right'], label='escalate', bg='paper2')

    svg = L.render()
    return svg, L


def wrap_html(svg, dark, slug, title, eyebrow):
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
<h1>dev-loop — the full development loop</h1>
{svg}
</div>
</body>
</html>
'''


def esc(s):
    return html.escape(s, quote=True)


if __name__ == '__main__':
    import sys, os
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    light_svg, Ll = build(LIGHT, 'dev-loop')
    dark_svg, Ld = build(DARK, 'dev-loop-dark')

    with open(os.path.join(out_dir, 'dev-loop.html'), 'w', encoding='utf-8') as f:
        f.write(wrap_html(light_svg, False, 'dev-loop', 'dev-loop — the full development loop',
                           'Flowchart · Dev-Loop Diagrams'))
    with open(os.path.join(out_dir, 'dev-loop-dark.html'), 'w', encoding='utf-8') as f:
        f.write(wrap_html(dark_svg, True, 'dev-loop-dark', 'dev-loop — the full development loop (dark)',
                           'Flowchart · Dev-Loop Diagrams'))
    print('wrote', out_dir)
