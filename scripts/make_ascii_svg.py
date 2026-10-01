#!/usr/bin/env python3
"""
Convert Aaron Francis's helmet character avatar into a mathematically aligned
ASCII-art SVG wrapped in a terminal window card with typewriter animation.

Reads ascii_helmet (1).svg (or source-prepped.png), applies tone-mapping / shadow lift,
and wraps it in a styled terminal window with traffic-light buttons and status bar.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_SVG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "ascii-helmet.svg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "aaron-ascii.svg")


def generate():
    if not os.path.exists(SRC_SVG):
        print(f"Error: {SRC_SVG} not found.")
        sys.exit(1)

    with open(SRC_SVG, "r", encoding="utf-8", errors="ignore") as f:
        raw_svg = f.read()

    g_match = re.search(r'(<g font-family=[^>]+xml:space="preserve">)(.*?)(</g>)', raw_svg, re.DOTALL)
    if not g_match:
        print("Could not parse glyph group from input SVG.")
        sys.exit(1)

    inner_group_header = g_match.group(1)
    inner_content = g_match.group(2)

    def boost_color(match):
        r = int(match.group(1), 16)
        g = int(match.group(2), 16)
        b = int(match.group(3), 16)

        if max(r, g, b) < 6:
            return 'fill="#05070a"'

        def lift(c):
            val = (c / 255.0) ** 0.62 * 255.0
            return max(0, min(255, int(val * 1.08)))

        return f'fill="#{lift(r):02x}{lift(g):02x}{lift(b):02x}"'

    boosted_content = re.sub(r'fill="#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})"', boost_color, inner_content)

    PAD_X = 20
    TITLE_H = 46
    ART_W = 1560
    ART_H = 1044
    STATUS_H = 46
    CANVAS_W = ART_W + PAD_X * 2
    CANVAS_H = TITLE_H + ART_H + STATUS_H

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" width="100%" '
        f'preserveAspectRatio="xMidYMid meet">\n',
        '<defs>\n',
        '  <linearGradient id="term_bg" x1="0" y1="0" x2="0" y2="1">\n',
        '    <stop offset="0%" stop-color="#111722"/>\n',
        '    <stop offset="100%" stop-color="#090d14"/>\n',
        '  </linearGradient>\n',
        '  <clipPath id="portrait_wipe">\n',
        f'    <rect x="0" y="0" width="{ART_W}" height="0">\n',
        '      <animate attributeName="height" from="0" to="1044" dur="2.2s" fill="freeze" calcMode="linear"/>\n',
        '    </rect>\n',
        '  </clipPath>\n',
        '  <style>\n',
        '    .term-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Courier New", monospace; }\n',
        '  </style>\n',
        '</defs>\n',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="14" fill="url(#term_bg)"/>\n',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="14" fill="none" stroke="#30363d" stroke-width="1.5"/>\n',
        f'<line x1="0" y1="{TITLE_H}" x2="{CANVAS_W}" y2="{TITLE_H}" stroke="#30363d" stroke-width="1.5"/>\n',
        f'<circle cx="{PAD_X + 16}" cy="{TITLE_H/2}" r="6.5" fill="#ff5f56"/>\n',
        f'<circle cx="{PAD_X + 38}" cy="{TITLE_H/2}" r="6.5" fill="#ffbd2e"/>\n',
        f'<circle cx="{PAD_X + 60}" cy="{TITLE_H/2}" r="6.5" fill="#27c93f"/>\n',
        f'<text class="term-mono" x="{CANVAS_W/2}" y="{TITLE_H/2 + 5}" fill="#8b949e" font-size="16" font-weight="600" text-anchor="middle">'
        f'aaron@github: ~$ whoami --portrait</text>\n',
        f'<g transform="translate({PAD_X}, {TITLE_H})">\n',
        f'  <rect width="{ART_W}" height="{ART_H}" fill="#030308"/>\n',
        '  <g clip-path="url(#portrait_wipe)">\n',
        f'    {inner_group_header}\n',
        f'    {boosted_content}\n',
        '    </g>\n',
        '  </g>\n',
        f'  <line x1="0" y1="0" x2="{ART_W}" y2="0" stroke="#58a6ff" stroke-width="3" opacity="0">\n',
        '    <animate attributeName="y1" from="0" to="1044" dur="2.2s" fill="freeze" calcMode="linear"/>\n',
        '    <animate attributeName="y2" from="0" to="1044" dur="2.2s" fill="freeze" calcMode="linear"/>\n',
        '    <set attributeName="opacity" to="0.9" begin="0s"/>\n',
        '    <set attributeName="opacity" to="0" begin="2.2s"/>\n',
        '  </line>\n',
        '</g>\n',
        f'<line x1="0" y1="{TITLE_H + ART_H}" x2="{CANVAS_W}" y2="{TITLE_H + ART_H}" stroke="#30363d" stroke-width="1.5"/>\n',
        f'<text class="term-mono" x="{PAD_X + 10}" y="{TITLE_H + ART_H + 28}" fill="#8b949e" font-size="16">'
        f'aaron@github:~$ whoami <tspan fill="#58a6ff" font-weight="700">Aaron Francis</tspan> '
        f'<tspan fill="#3fb950">[Electronics &amp; AI Systems Engineer]</tspan></text>\n',
        f'<rect x="{PAD_X + 630}" y="{TITLE_H + ART_H + 13}" width="10" height="18" fill="#58a6ff">\n',
        '  <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>\n',
        '</rect>\n',
        '</svg>'
    ]

    final_svg = "".join(svg_parts)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(final_svg)
    print(f"Generated {OUT} ({CANVAS_W}x{CANVAS_H}, {len(final_svg)} bytes)")


if __name__ == "__main__":
    generate()
