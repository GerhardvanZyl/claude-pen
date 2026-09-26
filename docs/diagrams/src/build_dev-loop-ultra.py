#!/usr/bin/env python3
"""Layout generator for the dev-loop-ultra flowchart (light + dark).
Extends _build.py's engine; do not hand-write SVG here.
"""
import html
from _build import Layout, LIGHT, DARK, wrap_html, CENTER, ZONE_X, LEFT_CH, RIGHT_CH, SMALL_SIZE, FONT_MONO


def esc(s):
    return html.escape(s, quote=True)


class ULayout(Layout):
    """Only the accent-line legend swatch differs from the base engine: this
    diagram's swatch was reading as muted at the base 1.4 stroke-width, so it
    is drawn heavier here to actually read as the accent colour (rule 5).
    Everything else in render()/_legend_item() is inherited unchanged."""

    def _legend_item(self, parts, x, row_y, text_baseline, kind, text):
        if kind != 'accentline':
            return super()._legend_item(parts, x, row_y, text_baseline, kind, text)
        t = self.t
        parts.append(f'<line x1="{x}" y1="{row_y}" x2="{x+20}" y2="{row_y}" '
                      f'stroke="{t["accent"]}" stroke-width="2.6"/>')
        parts.append(f'<text x="{x+30}" y="{text_baseline}" fill="{t["muted"]}" font-size="{SMALL_SIZE}" '
                      f'font-family="{FONT_MONO}">{esc(text)}</text>')
        char_w = SMALL_SIZE * 0.62
        return x + 30 + len(text) * char_w + 26


def build(tokens, slug):
    L = ULayout(tokens, slug,
               'dev-loop-ultra — the adversarial review loop',
               'Flowchart of dev-loop-ultra: identical framing, implementation and test phases to '
               'dev-loop, but each of the nine review lanes is run as a prosecution/defence/adjudicator '
               'triple instead of a single reviewer, two lanes at a time. Verification always runs, and '
               'triage escalates to dev-loop-ultra-opus when a lane’s coverage is reported thin twice.')
    L.gap(40)

    # ---- Zone 1: Entry, implement, test (identical to dev-loop) ---------
    L.zone_start('Entry · implement · test',
                 'identical to dev-loop — implementation is not changed by this loop')
    L.gap(52)
    entry = L.oval('entry', 220, 60, '/dev-loop-ultra')
    L.gap(40)
    p02 = L.rect(640, 100, 'Phases 0 to 2 — Frame, implement, test',
                 'Same brief.md + notes.md, same sidekick tiers — ultra buys scrutiny, not code')
    L.zone_end()
    L.gap(40)

    # ---- Zone 2: Plan & delegate -----------------------------------------
    L.zone_start('Plan the round · delegate')
    L.gap(52)
    p3 = L.rect(640, 100, 'Phase 3 — Plan the round',
                'Classify lanes · snapshot tree · scratch worktree for the Tests pair')
    L.gap(32)
    p4 = L.rect(640, 100, 'Phase 4 — Adversarial review',
                'Each applicable lane, three agents in sequence — 2 lanes/4 reviewers at a time')
    L.zone_end()
    L.gap(44)

    # ---- Zone 3: THE TRIPLE — the loop's defining shape ------------------
    L.zone_start('One lane, three agents — all nine lanes run this way',
                 'blind to each other')
    L.gap(52)

    row_y = L.y
    pros = L.rect(300, 100, 'reviewer-ultra-prosecution',
                  'Recall — assumes the code is broken', x=470)
    L.y = row_y
    defe = L.rect(300, 100, 'reviewer-ultra-defence',
                  'Precision — assumes the code is correct', x=810)
    row_bottom = max(pros['bottom'], defe['bottom'])
    L.y = row_bottom
    L.gap(46)

    adj_y = L.y
    adj = L.rect(320, 110, 'reviewer-ultra-adjudicator',
                 'Produces the lane’s authoritative set', x=590)
    L.y = adj_y
    reads = L.rect(280, 110, 'What the lead reads',
                   'Only .json + coverage line', x=955)
    triple_bottom = max(adj['bottom'], reads['bottom'])
    L.y = triple_bottom

    # Ratio captions — the loop's health signal — sit beside the triple, in
    # the left margin of this zone (between the zone frame and the
    # prosecution tile, clear of both the CENTER spine and the elbows
    # converging into the adjudicator), not down beside Phase 9.
    cap_x = 245
    cap_y0 = row_y + 24
    L.caption(cap_x, cap_y0, 'PROSECUTION HOT →')
    L.caption(cap_x, cap_y0 + 18, 'FEW SURVIVE')
    L.caption(cap_x, cap_y0 + 54, 'DEFENCE QUIET →')
    L.caption(cap_x, cap_y0 + 72, 'DRIFTS AGREEABLE')
    L.caption(cap_x, cap_y0 + 108, 'BOTH AGREE →')
    L.caption(cap_x, cap_y0 + 126, 'NOT OPPOSING')

    L.gap(40)

    tile_w, tile_h, gapx = 460, 90, 20
    tiles_start_x = CENTER - (tile_w * 2 + gapx) // 2
    tiles_y = L.y
    t_opus = L.lane_tile(tiles_start_x, tiles_y, tile_w, tile_h,
                          '4 lanes', 'Opus · High', 'requirements · technical · architecture · security')
    t_sonnet = L.lane_tile(tiles_start_x + tile_w + gapx, tiles_y, tile_w, tile_h,
                            '5 lanes', 'Sonnet · High', 'standards · tests · deadcode · minimal · artifacts')
    L.y = tiles_y + tile_h
    L.zone_end()
    L.gap(40)

    # ---- Zone 4: Triage, fix ----------------------------------------------
    L.zone_start('Triage · fix')
    L.gap(52)
    p5 = L.rect(640, 100, 'Phase 5 — Triage',
                'Cluster by cause · gate on evidence & cause · read each lane’s coverage line')
    L.gap(32)
    p6 = L.rect(640, 100, 'Phase 6 — Fix',
                'One brief; regression test fails → fix → passes; technical always reruns')
    L.zone_end()
    L.gap(40)

    # ---- Zone 5: Loop, verify, ship ----------------------------------------
    L.zone_start('Loop or exit · verify · ship')
    L.gap(52)
    p7_y = L.y
    p7_h = 160
    p7 = L.diamond(160, p7_h, 'Loop or\nexit?', focal=True, x=CENTER, y=p7_y)
    p7_cy = p7_y + p7_h / 2
    L.y = p7_y + p7_h
    L.gap(32)
    p8 = L.rect(640, 100, 'Phase 8 — Verification',
                'reviewer-verify, opus — spawned every round, always, not only when risky')
    L.gap(32)
    p8b = L.rect(640, 100, 'Phase 8b — Walkthrough',
                 'From notes.md · adds raised_p/raised_d/kept per lane to Reviewers section')
    L.gap(32)
    p9 = L.rect(640, 100, 'Phase 9 — Commit, push, pull request',
                'Stage incl. untracked · verify diff · PR states this was an adversarial run')
    L.gap(32)
    end = L.oval('end', 220, 60, 'PR opened')
    L.zone_end()

    # ---- terminal: escalate (from Phase 5) / blocked (from Phase 7) ------
    term_h = 158
    term_top_attach = p7_cy - 40
    term_bot_attach = p7_cy + 40
    term_y0 = term_top_attach - 40
    term = L.terminal_dual(ZONE_X + 16, term_y0, 300, term_h,
                            'ESCALATE → dev-loop-ultra-opus', 'coverage: both thin, twice, on a Critical lane',
                            'BLOCKED — stop & report', 'round>3 · same fix twice · no progress')

    # ---- connectors ---------------------------------------------------
    L.straight_v(CENTER, entry['bottom'], p02['top'])
    L.straight_v(CENTER, p02['bottom'], p3['top'])
    L.straight_v(CENTER, p3['bottom'], p4['top'])
    L.straight_v(CENTER, p4['bottom'], row_y)

    # phase4 fans to prosecution / defence (shared bottom edge, fanned)
    L.straight_v(470, p4['bottom'], pros['top'])
    L.straight_v(810, p4['bottom'], defe['top'])

    # prosecution / defence converge into the adjudicator (fanned attach)
    bend_y = pros['bottom'] + 23
    L.elbow([(470, pros['bottom']), (470, bend_y), (600, bend_y), (600, adj['top'])])
    L.elbow([(810, defe['bottom']), (810, bend_y), (680, bend_y), (680, adj['top'])])

    L.straight_v(CENTER, triple_bottom, tiles_y - 6)
    L.straight_v(CENTER, tiles_y + tile_h + 6, p5['top'], bg='paper2')
    L.straight_v(CENTER, p5['bottom'], p6['top'])
    L.straight_v(CENTER, p6['bottom'], p7['top'])
    L.straight_v(CENTER, p7['bottom'], p8['top'], label='pass', bg='paper2')
    L.straight_v(CENTER, p8['bottom'], p8b['top'])
    L.straight_v(CENTER, p8b['bottom'], p9['top'])
    L.straight_v(CENTER, p9['bottom'], end['top'])

    # phase7 -> phase3 (accent loop-back, the defining edge), right corridor
    L.elbow([
        (p7['right'], p7['cy']),
        (RIGHT_CH, p7['cy']),
        (RIGHT_CH, p3['cy']),
        (p3['right'], p3['cy']),
    ], accent=True, label='round + 1', label_pos=(RIGHT_CH, (p7['cy'] + p3['cy']) / 2))

    # phase5 -> terminal (escalate), left corridor. Targets term['left'], not
    # term['right']: the corridor at LEFT_CH-12 is to the left of the
    # terminal's own left edge, so entering at the right edge would tunnel
    # the final segment through the box's own opaque fill, hiding the
    # arrowhead. Entering at the left edge is a plain approach-from-outside,
    # matching how the rerun-lane elbow enters Phase 4's left edge.
    L.elbow([
        (p5['left'], p5['cy']),
        (LEFT_CH - 12, p5['cy']),
        (LEFT_CH - 12, term_top_attach),
        (term['left'], term_top_attach),
    ], label='escalate', label_pos=(LEFT_CH - 12, (p5['cy'] + term_top_attach) / 2))

    # phase7 -> terminal (blocked) — straight, at the terminal's own bottom
    # attach row throughout (as the pilot routes its phase7 -> terminal
    # exits): the previous elbow bent through p7['cy'] first, which sits
    # inside the terminal's vertical span, so the line ran behind the
    # ESCALATE half before correcting down into BLOCKED — a straight line
    # at the target row's own y never enters the box until its own edge.
    L.straight_h(term_bot_attach, p7['left'], term['right'], label='blocked', bg='paper2')

    svg = L.render()
    return svg, L


if __name__ == '__main__':
    import sys, os
    out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    title = 'dev-loop-ultra — the adversarial review loop'
    old_h1 = '<h1>dev-loop — the full development loop</h1>'

    light_svg, _ = build(LIGHT, 'dev-loop-ultra')
    dark_svg, _ = build(DARK, 'dev-loop-ultra-dark')

    light_html = wrap_html(light_svg, False, 'dev-loop-ultra', title, 'Flowchart · Dev-Loop Diagrams')
    light_html = light_html.replace(old_h1, f'<h1>{esc(title)}</h1>')
    dark_html = wrap_html(dark_svg, True, 'dev-loop-ultra-dark', title + ' (dark)', 'Flowchart · Dev-Loop Diagrams')
    dark_html = dark_html.replace(old_h1, f'<h1>{esc(title)}</h1>')

    with open(os.path.join(out_dir, 'dev-loop-ultra.html'), 'w', encoding='utf-8') as f:
        f.write(light_html)
    with open(os.path.join(out_dir, 'dev-loop-ultra-dark.html'), 'w', encoding='utf-8') as f:
        f.write(dark_html)
    print('wrote', out_dir)
