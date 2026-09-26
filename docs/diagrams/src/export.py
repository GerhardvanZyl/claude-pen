#!/usr/bin/env python3
"""Export a diagram-design HTML file to a standalone .svg next to it.

Usage:
    python export.py <file.html> [output.svg]

Follows the SVG export procedure in the diagram-design skill's
references/export.md, with one deliberate deviation for this project's
GitHub profile (see ~/.diagram-design/profiles/github.md):
no Google Fonts <style>@import is injected. GitHub renders README SVGs
through <img>, which cannot load web fonts, and the profile's typography is
already GitHub's native system-font stacks, so there is nothing to import.

Steps (diagram-only export; editorial wrapper such as header/cards is
dropped by design):
  1. Read the source HTML.
  2. Extract the first <svg ...>...</svg> block.
  3. Ensure xmlns and viewBox are present; keep role/aria-labelledby/title/desc
     exactly as authored.
  4. Normalize rgba(...)/transparent presentation-attribute colors to
     hex + fill-opacity/stroke-opacity, so strict SVG 1.1 / PowerPoint-style
     consumers don't paint them opaque black.
  5. Prepend the XML prolog and write <basename>.svg next to the source
     (or to an explicit output path).

This script is intentionally source-agnostic: it does not know or care which
diagram it is exporting, so the same file can be reused unchanged for every
diagram this run produces.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SVG_BLOCK_RE = re.compile(r"<svg\b.*?</svg>", re.DOTALL)
RGBA_RE = re.compile(
    r'(fill|stroke)="rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d*\.?\d+)\s*\)"'
)
TRANSPARENT_RE = re.compile(r'(fill|stroke)="transparent"')


def normalize_colors(svg: str) -> str:
    def rgba_to_hex(match: "re.Match[str]") -> str:
        attr, r, g, b, a = match.groups()
        return '{0}="#{1:02x}{2:02x}{3:02x}" {0}-opacity="{4}"'.format(
            attr, int(r), int(g), int(b), a
        )

    svg = RGBA_RE.sub(rgba_to_hex, svg)
    svg = TRANSPARENT_RE.sub(r'\1="none"', svg)
    return svg


def extract_svg(html: str) -> str:
    match = SVG_BLOCK_RE.search(html)
    if not match:
        raise SystemExit("No <svg>...</svg> block found in source HTML")
    svg = match.group(0)

    if "xmlns=" not in svg.split(">", 1)[0]:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)

    opening_tag = svg.split(">", 1)[0]
    if "viewBox=" not in opening_tag:
        print("warning: source <svg> has no viewBox; output may not size correctly",
              file=sys.stderr)

    return svg


def export(src_path: Path, out_path: Path) -> None:
    html = src_path.read_text(encoding="utf-8")
    svg = extract_svg(html)
    svg = normalize_colors(svg)
    document = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg + "\n"
    out_path.write_text(document, encoding="utf-8")
    print(f"wrote {out_path}")


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    src_path = Path(argv[0]).resolve()
    if not src_path.is_file():
        print(f"error: {src_path} not found", file=sys.stderr)
        return 1
    if len(argv) > 1:
        out_path = Path(argv[1]).resolve()
    else:
        out_path = src_path.with_suffix(".svg")
    export(src_path, out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
