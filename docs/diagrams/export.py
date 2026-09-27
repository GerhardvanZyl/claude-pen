#!/usr/bin/env python3
"""Export .drawio diagrams to png/<name>.png, or bind the loop PNGs into a booklet.

    python export.py dev-loop.drawio [more.drawio ...]
    python export.py --booklet dev-loop-ultralight dev-loop-lite ...   # PNGs -> dev-loops.pdf

Needs the draw.io desktop app, Chrome (or Edge) for the booklet, and Pillow.
PNGs are quantized to 128 colours.
"""
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

DRAWIO = [
    r"C:\Program Files\draw.io\draw.io.exe",
    "/Applications/draw.io.app/Contents/MacOS/draw.io",
    "drawio",
    "draw.io",
]
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome",
    "chromium",
]


def find(candidates, what):
    for candidate in candidates:
        if os.path.isfile(candidate) or shutil.which(candidate):
            return candidate
    sys.exit("No %s found" % what)


def browser():
    return find(BROWSERS, "Chrome or Edge")


def export(drawio_path):
    out = os.path.join(os.path.dirname(os.path.abspath(drawio_path)), "png",
                       os.path.splitext(os.path.basename(drawio_path))[0] + ".png")
    subprocess.run([find(DRAWIO, "draw.io"), "-x", "-f", "png", "-b", "20", "--width", "2000",
                    "-o", out, drawio_path], check=True, capture_output=True)
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
