#!/usr/bin/env python3
"""Export a diagram-design HTML file to png/<name>.png.

Follows the diagram-design export procedure (diagram only, the first <svg>),
but renders with headless Chrome instead of Playwright:

    python export.py dev-loop.html [more.html ...]
    python export.py --booklet dev-loop-ultralight dev-loop-lite ...   # PNGs -> dev-loops.pdf

Needs Chrome (or Edge) and Pillow. Output is quantized to 128 colours.
"""
import os
import re
import subprocess
import sys
import tempfile

from PIL import Image

SCALE = 2
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome",
    "chromium",
]
FONTS = ("@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&amp;family=Geist:wght@400;500;600&amp;family=Geist+Mono:wght@400;500;600&amp;display=swap');")


def browser():
    for candidate in BROWSERS:
        if os.path.isfile(candidate) or not os.path.isabs(candidate):
            return candidate
    sys.exit("No Chrome or Edge found")


def export(html_path):
    html = open(html_path, encoding="utf-8").read()
    svg = re.search(r"<svg\b.*?</svg>", html, re.S).group(0)
    width, height = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    page = ("<!doctype html><html><head><style>" + FONTS.replace("&amp;", "&")
            + "html,body{margin:0;background:#f5f5f5}svg{display:block;width:%dpx;height:%dpx}"
            % (width, height) + "</style></head><body>" + svg + "</body></html>")

    out = os.path.join(os.path.dirname(os.path.abspath(html_path)), "png",
                       os.path.splitext(os.path.basename(html_path))[0] + ".png")
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "page.html")
        open(src, "w", encoding="utf-8").write(page)
        subprocess.run([browser(), "--headless=new", "--hide-scrollbars", "--virtual-time-budget=5000",
                        "--force-device-scale-factor=%d" % SCALE,
                        "--window-size=%d,%d" % (width, height),
                        "--screenshot=" + out, "file:///" + src.replace("\\", "/")],
                       check=True, capture_output=True)
    image = Image.open(out).convert("RGB").quantize(colors=128)
    image.save(out, optimize=True)
    print(out)


def booklet(names):
    """Print the named PNGs, one per A4 landscape page, to dev-loops.pdf beside this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    pages = "".join('<div><img src="file:///%s"></div>'
                    % os.path.join(here, "png", name + ".png").replace("\\", "/") for name in names)
    page = ("<style>@page{size:A4 landscape;margin:8mm}body{margin:0}"
            "div{break-after:page;height:190mm;display:flex;align-items:center;justify-content:center}"
            "div:last-child{break-after:auto}img{max-width:100%;max-height:100%}</style>" + pages)
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "booklet.html")
        open(src, "w", encoding="utf-8").write(page)
        out = os.path.join(here, "dev-loops.pdf")
        subprocess.run([browser(), "--headless=new", "--no-pdf-header-footer", "--print-to-pdf=" + out,
                        "file:///" + src.replace("\\", "/")], check=True, capture_output=True)
    print(out)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--booklet"]:
        booklet(sys.argv[2:])
    else:
        for path in sys.argv[1:]:
            export(path)
