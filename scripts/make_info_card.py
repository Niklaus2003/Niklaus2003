#!/usr/bin/env python3
"""
Build a neofetch-style info card SVG tailored for Aaron Francis (@Niklaus2003)
to sit to the RIGHT of the ASCII portrait in the GitHub README.

Static content with staggered SMIL fade + slide animations that run smoothly
inside GitHub's <img> renderer.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

W, H = 480, 360
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 94
LINE_H = 18.5

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
KEY = "#ffa657"      # warm orange keys
SECTION = "#58a6ff"  # electric blue headers
GREEN = "#3fb950"    # terminal green
ACCENT = "#22d3ee"   # cyan highlight

ROWS = [
    ("host",),
    ("kv", "Role", "Electronics & AI Systems Engineer"),
    ("kv", "Degree", "B.Tech in Electronics & Communication"),
    ("kv", "Focus", "Vision AI · Voice Tech · Agents"),
    ("gap",),
    ("sec", "Tech Stack"),
    ("kv", "Languages", "Python, JavaScript, TypeScript, C/C++"),
    ("kv", "Vision & AI", "OpenCV, PyTorch, MediaPipe, Deep Learning"),
    ("kv", "Voice & Agts", "Voice AI, STT / TTS, LLMs, LangChain, FastAPI"),
    ("kv", "Full Stack", "React, Node.js, Express, Tailwind, REST APIs"),
    ("gap",),
    ("sec", "Highlights"),
    ("bul", "Real-time Object Detection & Pose Estimation"),
    ("bul", "Voice-Enabled Interactive AI Assistants & Bots"),
    ("bul", "Jack of all trades, forever curious builder"),
]


def esc(s):
    return html.escape(s)


def rise(inner, i):
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.12 + i * 0.04
    return (
        f'<g opacity="0" transform="translate(0,4)">{inner}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 4" to="0 0" '
        f'begin="{delay:.2f}s" dur="0.35s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>'
    )


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]

for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">aaron@github: ~$ neofetch --profile</text>')

y = TITLEBAR_H + 24
for i, row in enumerate(ROWS):
    kind = row[0]
    if kind == "gap":
        y += LINE_H * 0.45
        continue
    if kind == "host":
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" font-size="13.5" font-weight="700">'
                 f'<tspan fill="{GREEN}">aaron</tspan><tspan fill="{MUTED}">@</tspan>'
                 f'<tspan fill="{ACCENT}">github</tspan></text>'
                 f'<line x1="{KEY_X+105}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "sec":
        title = esc(row[1])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="11.5" font-weight="700">'
                 f'&#8212; {title}</text>'
                 f'<line x1="{KEY_X + 16 + len(row[1])*7.2}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "kv":
        key, val = esc(row[1]), esc(row[2])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="11.5" font-weight="700">{key}</text>'
                 f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="11.5">{val}</text>')
    elif kind == "bul":
        txt = esc(row[1])
        inner = (f'<circle cx="{KEY_X+4}" cy="{y-4:.1f}" r="2.5" fill="{GREEN}"/>'
                 f'<text x="{KEY_X+16}" y="{y:.1f}" fill="{INK}" font-size="11.5">{txt}</text>')
    else:
        continue
    parts.append(rise(inner, i))
    y += LINE_H

parts.append("</svg>")
svg = "".join(parts)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"Wrote {OUT} ({len(svg)} bytes; {W} x {H})")
