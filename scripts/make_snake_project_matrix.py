#!/usr/bin/env python3
"""
Generate an animated retro arcade Snake Game Project Matrix SVG (`projects-matrix.svg`)
for Aaron Francis (@Niklaus2003).

Features:
- Dark terminal / CRT arcade cabinet theme
- Real animated slithering 8-bit snake winding through the grid
- Project targets / food items with pulsing glows
- Application Matrix showcasing Aaron's 4 core domains (Vision AI, Voice Tech, ML, Full-Stack)
- 100% self-contained SVG with pure CSS/SMIL animations (works in GitHub README <img> tags).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "projects-matrix.svg")

W, H = 860, 430
TITLEBAR_H = 32
PAD = 20

BG = "#0a0e14"
BG2 = "#0f172a"
FRAME = "#1e293b"
FRAME_BRIGHT = "#334155"
MUTED = "#64748b"
INK = "#e2e8f0"
GREEN = "#22c55e"
GREEN_GLOW = "#4ade80"
SNAKE_HEAD = "#86efac"
ACCENT = "#38bdf8"
YELLOW = "#facc15"
PURPLE = "#c084fc"
RED = "#f43f5e"

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">
  <defs>
    <linearGradient id="matrix-bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{BG2}"/>
      <stop offset="100%" stop-color="{BG}"/>
    </linearGradient>

    <linearGradient id="card-glow" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#0f172a" stop-opacity="0.8"/>
    </linearGradient>

    <!-- CRT scanline overlay -->
    <pattern id="scanlines" width="100" height="4" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="100" y2="0" stroke="#000" stroke-width="1.2" opacity="0.25"/>
    </pattern>

    <!-- Grid pattern for the snake arena -->
    <pattern id="arcade-grid" width="18" height="18" patternUnits="userSpaceOnUse">
      <path d="M 18 0 L 0 0 0 18" fill="none" stroke="#1e293b" stroke-width="0.8" opacity="0.6"/>
    </pattern>

    <filter id="glow-green" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="glow-amber" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <style>
      @keyframes pulse-fruit {{
        0%, 100% {{ transform: scale(1); opacity: 0.9; }}
        50% {{ transform: scale(1.22); opacity: 1; }}
      }}
      @keyframes snake-crawl {{
        0% {{ stroke-dashoffset: 480; }}
        100% {{ stroke-dashoffset: 0; }}
      }}
      @keyframes crt-flicker {{
        0%, 100% {{ opacity: 0.97; }}
        50% {{ opacity: 1; }}
      }}
      @keyframes score-blink {{
        0%, 49% {{ opacity: 1; }}
        50%, 100% {{ opacity: 0.3; }}
      }}
      .fruit-pulse {{ transform-origin: center; animation: pulse-fruit 1.8s ease-in-out infinite; }}
      .snake-body {{ stroke-dasharray: 60 420; animation: snake-crawl 6s linear infinite; }}
      .cursor-blink {{ animation: score-blink 1s steps(2, start) infinite; }}
      .card-hover {{ transition: transform 0.2s ease; }}
    </style>
  </defs>

  <!-- Main Window Frame -->
  <rect width="{W}" height="{H}" rx="12" fill="url(#matrix-bg)"/>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME_BRIGHT}" stroke-width="1" stroke-opacity="0.4"/>
  <line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME_BRIGHT}" stroke-opacity="0.3"/>

  <!-- Title bar dots -->
  <circle cx="{PAD}" cy="{TITLEBAR_H/2}" r="5" fill="#ef4444"/>
  <circle cx="{PAD + 16}" cy="{TITLEBAR_H/2}" r="5" fill="#f59e0b"/>
  <circle cx="{PAD + 32}" cy="{TITLEBAR_H/2}" r="5" fill="#10b981"/>

  <!-- Title text -->
  <text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" font-weight="600" text-anchor="middle">
    aaron@github: ~/arcade/snake-project-matrix.sh --play
  </text>

  <!-- Arcade HUD Scorebar -->
  <g transform="translate({PAD}, {TITLEBAR_H + 12})">
    <rect width="{W - PAD*2}" height="32" rx="6" fill="#0b1120" stroke="{FRAME}" stroke-width="1"/>
    
    <text x="14" y="21" fill="{GREEN}" font-size="11" font-weight="700" letter-spacing="1">
      🎮 SNAKE_MATRIX::v2.4
    </text>

    <text x="210" y="21" fill="{MUTED}" font-size="11">
      SCORE: <tspan fill="{YELLOW}" font-weight="700">9,840</tspan>
    </text>

    <text x="340" y="21" fill="{MUTED}" font-size="11">
      TARGETS: <tspan fill="{GREEN_GLOW}" font-weight="700">4 / 4 CONSUMED</tspan>
    </text>

    <text x="540" y="21" fill="{MUTED}" font-size="11">
      ENERGY: <tspan fill="{ACCENT}">99.8%</tspan>
    </text>

    <text x="{W - PAD*2 - 14}" y="21" fill="{RED}" font-size="11" font-weight="700" text-anchor="end">
      LIVES: ♥ ♥ ♥
    </text>
  </g>

  <!-- LEFT: Snake Game Arena (340px wide) -->
  <g transform="translate({PAD}, {TITLEBAR_H + 54})">
    <!-- Arena Background & Grid -->
    <rect width="330" height="305" rx="8" fill="#040810" stroke="{FRAME}" stroke-width="1.2"/>
    <rect width="330" height="305" rx="8" fill="url(#arcade-grid)"/>

    <!-- CRT Corner Brackets -->
    <path d="M 10 24 L 10 10 L 24 10" fill="none" stroke="{GREEN}" stroke-width="1.5" opacity="0.6"/>
    <path d="M 320 24 L 320 10 L 306 10" fill="none" stroke="{GREEN}" stroke-width="1.5" opacity="0.6"/>
    <path d="M 10 281 L 10 295 L 24 295" fill="none" stroke="{GREEN}" stroke-width="1.5" opacity="0.6"/>
    <path d="M 320 281 L 320 295 L 306 295" fill="none" stroke="{GREEN}" stroke-width="1.5" opacity="0.6"/>

    <!-- Arena Header Label -->
    <text x="165" y="24" fill="{MUTED}" font-size="10" font-weight="700" letter-spacing="2" text-anchor="middle">
      ARENA // 53x7 RUNTIME
    </text>

    <!-- Animated Snake Track Path -->
    <path id="snake-run"
          d="M 36 60 L 294 60 L 294 120 L 36 120 L 36 185 L 294 185 L 294 250 L 72 250"
          fill="none" stroke="#166534" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" opacity="0.25"/>

    <!-- Animated Glowing Snake Body -->
    <path class="snake-body"
          d="M 36 60 L 294 60 L 294 120 L 36 120 L 36 185 L 294 185 L 294 250 L 72 250"
          fill="none" stroke="{GREEN_GLOW}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"
          filter="url(#glow-green)"/>

    <!-- Target 1 Food (Vision) at (165, 60) -->
    <g class="fruit-pulse" transform="translate(165, 60)">
      <circle r="7" fill="{RED}" filter="url(#glow-amber)"/>
      <circle r="2.5" fill="#fff"/>
      <text x="14" y="4" fill="{RED}" font-size="9" font-weight="700">T1:CV</text>
    </g>

    <!-- Target 2 Food (Voice) at (294, 150) -->
    <g class="fruit-pulse" transform="translate(294, 150)" style="animation-delay: -0.4s;">
      <circle r="7" fill="{YELLOW}" filter="url(#glow-amber)"/>
      <circle r="2.5" fill="#fff"/>
      <text x="-48" y="4" fill="{YELLOW}" font-size="9" font-weight="700">T2:VOICE</text>
    </g>

    <!-- Target 3 Food (AI/ML) at (130, 185)" -->
    <g class="fruit-pulse" transform="translate(130, 185)" style="animation-delay: -0.8s;">
      <circle r="7" fill="{PURPLE}" filter="url(#glow-amber)"/>
      <circle r="2.5" fill="#fff"/>
      <text x="14" y="4" fill="{PURPLE}" font-size="9" font-weight="700">T3:AGENTS</text>
    </g>

    <!-- Target 4 Food (FullStack) at (190, 250) -->
    <g class="fruit-pulse" transform="translate(190, 250)" style="animation-delay: -1.2s;">
      <circle r="7" fill="{ACCENT}" filter="url(#glow-amber)"/>
      <circle r="2.5" fill="#fff"/>
      <text x="14" y="4" fill="{ACCENT}" font-size="9" font-weight="700">T4:STACK</text>
    </g>

    <!-- Arena Footer Legend -->
    <text x="165" y="284" fill="{GREEN}" font-size="10" text-anchor="middle" font-weight="600">
      ● RETRO-SNAKE NAVIGATING LIVE PROJECTS
    </text>
  </g>

  <!-- RIGHT: Project Matrix Cards (450px wide) -->
  <g transform="translate({PAD + 350}, {TITLEBAR_H + 54})">

    <!-- Card 1: Computer Vision & Pose -->
    <g transform="translate(0, 0)">
      <rect width="470" height="68" rx="8" fill="url(#card-glow)" stroke="#ef4444" stroke-width="1" stroke-opacity="0.35"/>
      <circle cx="22" cy="24" r="8" fill="#ef4444" fill-opacity="0.2"/>
      <text x="22" y="28" fill="#ef4444" font-size="12" font-weight="700" text-anchor="middle">1</text>
      
      <text x="40" y="24" fill="{INK}" font-size="13" font-weight="700">
        Computer Vision &amp; Pose Estimation
      </text>
      <text x="455" y="24" fill="#ef4444" font-size="10" font-weight="700" text-anchor="end">
        [CLEARED / 98%]
      </text>

      <text x="40" y="42" fill="{MUTED}" font-size="11">
        Real-time tracking, edge detection, pose analysis &amp; gesture mapping.
      </text>
      <text x="40" y="58" fill="{YELLOW}" font-size="10.5">
        Stack: <tspan fill="{INK}">Python · OpenCV · MediaPipe · NumPy · Deep Learning</tspan>
      </text>
    </g>

    <!-- Card 2: Voice Tech & Autonomous Agents -->
    <g transform="translate(0, 78)">
      <rect width="470" height="68" rx="8" fill="url(#card-glow)" stroke="#facc15" stroke-width="1" stroke-opacity="0.35"/>
      <circle cx="22" cy="24" r="8" fill="#facc15" fill-opacity="0.2"/>
      <text x="22" y="28" fill="#facc15" font-size="12" font-weight="700" text-anchor="middle">2</text>
      
      <text x="40" y="24" fill="{INK}" font-size="13" font-weight="700">
        Voice AI Assistants &amp; Agent Systems
      </text>
      <text x="455" y="24" fill="#facc15" font-size="10" font-weight="700" text-anchor="end">
        [ACTIVE / ONLINE]
      </text>

      <text x="40" y="42" fill="{MUTED}" font-size="11">
        Speech recognition, conversational bots, tool-calling agents &amp; LLMs.
      </text>
      <text x="40" y="58" fill="{YELLOW}" font-size="10.5">
        Stack: <tspan fill="{INK}">Voice AI · STT / TTS · LangChain · OpenAI · FastAPI</tspan>
      </text>
    </g>

    <!-- Card 3: AI & Machine Learning Experiments -->
    <g transform="translate(0, 156)">
      <rect width="470" height="68" rx="8" fill="url(#card-glow)" stroke="#c084fc" stroke-width="1" stroke-opacity="0.35"/>
      <circle cx="22" cy="24" r="8" fill="#c084fc" fill-opacity="0.2"/>
      <text x="22" y="28" fill="#c084fc" font-size="12" font-weight="700" text-anchor="middle">3</text>
      
      <text x="40" y="24" fill="{INK}" font-size="13" font-weight="700">
        Applied AI &amp; Neural Architecture
      </text>
      <text x="455" y="24" fill="#c084fc" font-size="10" font-weight="700" text-anchor="end">
        [OPTIMIZED]
      </text>

      <text x="40" y="42" fill="{MUTED}" font-size="11">
        Model training, inference benchmarking, multimodal embeddings.
      </text>
      <text x="40" y="58" fill="{YELLOW}" font-size="10.5">
        Stack: <tspan fill="{INK}">PyTorch · Transformers · Scikit-Learn · Vector DBs</tspan>
      </text>
    </g>

    <!-- Card 4: Full-Stack Web Experiments -->
    <g transform="translate(0, 234)">
      <rect width="470" height="68" rx="8" fill="url(#card-glow)" stroke="#38bdf8" stroke-width="1" stroke-opacity="0.35"/>
      <circle cx="22" cy="24" r="8" fill="#38bdf8" fill-opacity="0.2"/>
      <text x="22" y="28" fill="#38bdf8" font-size="12" font-weight="700" text-anchor="middle">4</text>
      
      <text x="40" y="24" fill="{INK}" font-size="13" font-weight="700">
        Full-Stack &amp; Embedded I/O Platforms
      </text>
      <text x="455" y="24" fill="#38bdf8" font-size="10" font-weight="700" text-anchor="end">
        [EXPANDING]
      </text>

      <text x="40" y="42" fill="{MUTED}" font-size="11">
        Interactive web applications connecting ML inference to sleek UIs.
      </text>
      <text x="40" y="58" fill="{YELLOW}" font-size="10.5">
        Stack: <tspan fill="{INK}">Embedded C · Microcontrollers · React · REST APIs · IoT</tspan>
      </text>
    </g>

  </g>

  <!-- Console Footer Prompt -->
  <g transform="translate({PAD}, {H - 22})">
    <text x="0" y="10" fill="{MUTED}" font-size="11">
      <tspan fill="{GREEN}">aaron@github</tspan>:<tspan fill="{ACCENT}">~/projects</tspan>$ ./slither.sh --status=ready
    </text>
    <rect x="360" y="0" width="7" height="12" fill="{GREEN}" class="cursor-blink"/>
    <text x="{W - PAD*2}" y="10" fill="{MUTED}" font-size="10.5" text-anchor="end">
      ENGINE: ELECTRONICS + AI + SOFTWARE · JACK OF ALL TRADES
    </text>
  </g>

</svg>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg.strip())

print(f"wrote {OUT} ({len(svg)} bytes; {W} x {H})")
