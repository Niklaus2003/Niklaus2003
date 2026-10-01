#!/usr/bin/env python3
"""
Convert Aaron Francis's full avatar image faithfully into a mathematically
aligned monochrome ASCII-art SVG that preserves the exact composition of the
original image without distortion, inversion, or missing sections.
"""
from PIL import Image, ImageEnhance
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "aaron-ascii.svg")

# Grid dimensions matching the 1536 x 1024 (1.5 aspect ratio) exactly:
COLS = 96
ROWS = 36
CELL_W = 8.5
CELL_H = 15.5
FONT_SIZE = 14.16  # In Consolas / Courier New, 0.6 * font_size = 8.5px exact width

# Light-on-dark ramp: index 0 (black background) -> space, high values -> dense glyphs
RAMP = " .:-=+*#%@"

PAD = 20
TITLEBAR_H = 32
STATUS_H = 32
ART_W = int(COLS * CELL_W)
ART_H = int(ROWS * CELL_H)
CANVAS_W = int(ART_W + PAD * 2)
CANVAS_H = int(TITLEBAR_H + ART_H + STATUS_H + PAD)

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#58a6ff"

ROW_DUR = 0.06
STAGGER = 0.06

if not os.path.exists(SRC):
    print(f"Error: {SRC} not found. Run prep_photo.py first.")
    sys.exit(1)

# Sample image into grayscale COLS x ROWS grid
im = Image.open(SRC).convert("L")
im = ImageEnhance.Contrast(im).enhance(1.2)
im = ImageEnhance.Brightness(im).enhance(1.05)
im = im.resize((COLS, ROWS), Image.Resampling.LANCZOS)
px = im.load()

STATIC = bool(os.environ.get("STATIC"))

rows_txt = []
for y in range(ROWS):
    chars = []
    for x in range(COLS):
        val = px[x, y]
        if val < 24:
            chars.append(" ")
        else:
            idx = int(((val - 24) / (255 - 24)) * (len(RAMP) - 1))
            idx = max(0, min(len(RAMP) - 1, idx))
            chars.append(RAMP[idx])
    rows_txt.append("".join(chars))

art_top = TITLEBAR_H + 12

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
    f'viewBox="0 0 {CANVAS_W} {CANVAS_H}">',
    '<defs>'
    f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
    '</linearGradient>'
    '<style>'
    '  .mono-text { '
    '    font-family: ui-monospace, SFMono-Regular, Consolas, "Courier New", monospace; '
    '    letter-spacing: 0px; '
    '    word-spacing: 0px; '
    '    white-space: pre; '
    '  }'
    '</style>'
    '</defs>',
    f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>'
]

# Window buttons
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')

parts.append(f'<text class="mono-text" x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" '
             f'font-size="12" text-anchor="middle">aaron@github: ~$ ./portrait.sh</text>')

# Rows of ASCII text with strict vertical column alignment
for ry, line in enumerate(rows_txt):
    y = art_top + ry * CELL_H + CELL_H * 0.78
    row_y = art_top + ry * CELL_H
    delay = ry * STAGGER
    safe = html.escape(line)
    
    # Exact character width advance: strictly aligned columns
    text = (f'<text class="mono-text" xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{FONT_SIZE:.2f}px">{safe}</text>')

    if STATIC:
        parts.append(text)
        continue

    parts.append(
        f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
        f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
    )
    parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
    parts.append(
        f'<rect y="{row_y+1:.1f}" width="{CELL_W}" height="{CELL_H-2}" fill="{CURSOR}" opacity="0">'
        f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
        f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
        f'<set attributeName="opacity" to="0.9" begin="{delay:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
    )

# Status bar
status_line_y = TITLEBAR_H + ART_H + 18
status_y = status_line_y + 20
parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
parts.append(f'<text class="mono-text" x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="12.5">'
             f'aaron@github:~$ whoami <tspan fill="{INK}">Aaron Francis</tspan></text>')
parts.append(f'<rect x="{PAD+208}" y="{status_y-11:.1f}" width="8" height="13" fill="{CURSOR}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
             f'dur="1s" repeatCount="indefinite"/></rect>')

parts.append("</svg>")
svg = "".join(parts)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"Wrote faithful aligned ASCII SVG to {OUT} ({len(svg)} bytes; {CANVAS_W} x {CANVAS_H})")


if __name__ == "__main__":
    pass
