#!/usr/bin/env python3
"""
Generate an animated GitHub Contribution Matrix SVG that plays like the classic
Snake Game eating each contribution cell one by one in an infinite loop!

Features:
- Pure self-contained SVG SMIL animation (100% compatible with GitHub profile READMEs)
- Real 53-week x 7-day contribution data from data/contributions.json
- Slithering 8-bit retro snake that moves cell-by-cell across the calendar
- Each contribution cell pops and gets eaten into an empty slot when the snake reaches it
- Resets seamlessly near the end of each cycle and loops indefinitely
- Retro arcade HUD with live statistics
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

# Green contribution palette (empty -> max intensity)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

W, H = 860, 275
PAD_X = 40
PAD_Y = 56
CELL = 11.5
GAP = 3
STEP = CELL + GAP  # 14.5px
TITLEBAR_H = 32

BG = "#0a0e14"
BG2 = "#0f172a"
FRAME = "#30363d"
FRAME_BRIGHT = "#334155"
MUTED = "#64748b"
INK = "#e2e8f0"
GREEN = "#22c55e"
GREEN_GLOW = "#4ade80"
SNAKE_HEAD = "#86efac"
ACCENT = "#38bdf8"
YELLOW = "#facc15"


def level_for(count):
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 10:
        return 3
    if count <= 20:
        return 4
    return 5


def build_grid(days):
    if not days:
        return []
    first = datetime.date.fromisoformat(days[0]["date"])
    lead_pad = (first.weekday() + 1) % 7
    grid = []
    col = [None] * lead_pad
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        while len(col) < weekday:
            col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"])))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        while len(col) < 7:
            col.append(None)
        grid.append(col)
    return grid


def generate_snake_heatmap():
    if not os.path.exists(IN_PATH):
        print(f"Error: {IN_PATH} not found. Run fetch_contributions.py first.")
        return

    with open(IN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    grid = build_grid(days)
    n_cols = len(grid)
    if n_cols > 53:
        grid = grid[-53:]
        n_cols = 53

    # Generate boustrophedon snake path through all cells
    # Col 0: r 0..6, Col 1: r 6..0, etc.
    # Then loop back to (0, 0)
    path = []
    for c in range(n_cols):
        rows = range(7) if c % 2 == 0 else range(6, -1, -1)
        for r in rows:
            path.append((c, r))

    # Return path along the top/perimeter to close the loop
    last_c, last_r = path[-1]
    # Move up to row 0 if not already
    cur_r = last_r
    while cur_r > 0:
        cur_r -= 1
        path.append((last_c, cur_r))
    # Move left back to col 0
    cur_c = last_c
    while cur_c > 0:
        cur_c -= 1
        path.append((cur_c, 0))

    total_steps = len(path)
    step_dur = 0.038  # seconds per cell step
    total_dur = round(total_steps * step_dur, 2)  # ~16.5s loop

    # Map each (c, r) cell to the time it gets eaten
    eaten_times = {}
    for step_idx, (c, r) in enumerate(path):
        if (c, r) not in eaten_times and step_idx < n_cols * 7:
            eaten_times[(c, r)] = step_idx * step_dur

    # Months labels
    seen_months = set()
    month_labels = []
    for ci, col in enumerate(grid):
        for cell in col:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                month_labels.append((ci, date.strftime("%b")))
            break

    # SVG Construction
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">',
        '<defs>',
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{BG2}"/><stop offset="100%" stop-color="{BG}"/></linearGradient>',
        '<filter id="glow-head" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="2" result="blur"/>'
        '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>',
        '</defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.4"/>',
    ]

    # Window titlebar dots & prompt
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{20 + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')

    parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" font-weight="600" text-anchor="middle">'
                 f'aaron@github: ~/arcade/snake-contributions --loop</text>')

    # Month Labels
    for ci, label in month_labels:
        mx = PAD_X + ci * STEP
        parts.append(f'<text x="{mx}" y="{PAD_Y - 8}" fill="{MUTED}" font-size="9.5">{label}</text>')

    # Weekday Labels
    for wi, wname in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        wy = PAD_Y + wi * STEP + CELL * 0.75
        parts.append(f'<text x="{PAD_X - 26}" y="{wy:.1f}" fill="{MUTED}" font-size="9">{wname}</text>')

    # Contribution Grid Cells & Animated Food
    for ci, col in enumerate(grid):
        cx = PAD_X + ci * STEP
        for ri, cell in enumerate(col):
            if cell is None:
                continue
            date_s, count, lvl = cell
            cy = PAD_Y + ri * STEP
            base_color = PALETTE[lvl]

            if count == 0:
                # Empty slot: static dark rect
                parts.append(f'<rect x="{cx}" y="{cy}" width="{CELL}" height="{CELL}" rx="2" fill="{base_color}"/>')
            else:
                # FOOD SLOT: Starts active, gets eaten when snake arrives, respawns at loop end
                t_eat = eaten_times.get((ci, ri), 0.0)
                t_eat_ratio = round(t_eat / total_dur, 4)
                t_eat_next = round(min(0.95, t_eat_ratio + 0.005), 4)

                parts.append(f'<g transform="translate({cx}, {cy})">')
                # Underneath empty base
                parts.append(f'<rect width="{CELL}" height="{CELL}" rx="2" fill="{PALETTE[0]}"/>')
                # Animated food overlay
                parts.append(
                    f'<rect width="{CELL}" height="{CELL}" rx="2" fill="{base_color}">'
                    f'<animate attributeName="fill" '
                    f'values="{base_color};{base_color};{PALETTE[0]};{PALETTE[0]};{base_color}" '
                    f'keyTimes="0;{t_eat_ratio};{t_eat_next};0.96;1" '
                    f'dur="{total_dur}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" '
                    f'values="1;1;0;0;1" '
                    f'keyTimes="0;{t_eat_ratio};{t_eat_next};0.96;1" '
                    f'dur="{total_dur}s" repeatCount="indefinite"/>'
                    f'<title>{date_s}: {count} contribution(s) [Food Node]</title>'
                    f'</rect>'
                )
                parts.append('</g>')

    # Build discrete trajectory for snake head & body segments
    # Snake length = 5 segments
    snake_len = 5
    body_colors = [SNAKE_HEAD, "#4ade80", "#22c55e", "#16a34a", "#15803d"]

    key_times_str = ";".join(f"{i / (total_steps - 1):.4f}" for i in range(total_steps))

    for seg_idx in range(snake_len):
        # The segment lags behind the head by seg_idx steps
        x_vals = []
        y_vals = []
        for step_idx in range(total_steps):
            lagged_idx = (step_idx - seg_idx) % total_steps
            sc, sr = path[lagged_idx]
            x_vals.append(str(round(PAD_X + sc * STEP + 0.5, 1)))
            y_vals.append(str(round(PAD_Y + sr * STEP + 0.5, 1)))

        x_str = ";".join(x_vals)
        y_str = ";".join(y_vals)
        col = body_colors[seg_idx]
        radius = 2.5 if seg_idx == 0 else 2.0
        filter_attr = ' filter="url(#glow-head)"' if seg_idx == 0 else ''

        # Segment rect with animated position
        first_x = x_vals[0]
        first_y = y_vals[0]
        parts.append(
            f'<rect x="{first_x}" y="{first_y}" width="{CELL-1}" height="{CELL-1}" rx="{radius}" '
            f'fill="{col}"{filter_attr}>'
            f'<animate attributeName="x" values="{x_str}" keyTimes="{key_times_str}" dur="{total_dur}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{y_str}" keyTimes="{key_times_str}" dur="{total_dur}s" repeatCount="indefinite"/>'
            f'</rect>'
        )

    # Footer HUD & Stats
    stats_y = PAD_Y + 7 * STEP + 24
    parts.append(f'<line x1="0" y1="{stats_y - 12}" x2="{W}" y2="{stats_y - 12}" stroke="{FRAME}" stroke-opacity="0.3"/>')

    total_contrib = data.get("total_contributions", 0)
    cur_streak = data.get("current_streak", {}).get("length", 0)
    long_streak = data.get("longest_streak", {}).get("length", 0)
    rng = data.get("range", {"start": "-", "end": "-"})

    # Left: Total and Streak
    parts.append(
        f'<text x="{PAD_X}" y="{stats_y + 8}" font-size="12" fill="{GREEN}">'
        f'<tspan font-weight="700">🎮 SNAKE EATING {total_contrib} CONTRIBUTIONS</tspan>'
        f'<tspan fill="{MUTED}">  &#183;  streak </tspan>'
        f'<tspan fill="{ACCENT}" font-weight="700">{cur_streak}d</tspan>'
        f'<tspan fill="{MUTED}">  &#183;  longest </tspan>'
        f'<tspan fill="{ACCENT}" font-weight="700">{long_streak}d</tspan>'
        f'</text>'
    )

    # Right: Legend (Less -> More)
    leg_x = W - PAD_X - 110
    parts.append(f'<text x="{leg_x - 8}" y="{stats_y + 8}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>')
    for li, lcol in enumerate(PALETTE):
        parts.append(f'<rect x="{leg_x + li * 13}" y="{stats_y - 2}" width="10" height="10" rx="2" fill="{lcol}"/>')
    parts.append(f'<text x="{leg_x + len(PALETTE) * 13 + 6}" y="{stats_y + 8}" fill="{MUTED}" font-size="10">More</text>')

    parts.append("</svg>")
    svg = "".join(parts)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote snake heatmap SVG to {OUT_PATH} ({len(svg)} bytes; {W} x {H})")


if __name__ == "__main__":
    generate_snake_heatmap()
