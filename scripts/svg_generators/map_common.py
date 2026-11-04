#!/usr/bin/env python3
"""Shared utilities, constants and HTML update helpers for island maps."""

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# Regex to find island SVG blocks in infrastructure.html
SVG_RE = re.compile(r'<svg class="ill" viewBox="0 0 1200 700".*?</svg>', re.S)
SCRIPT_RE = re.compile(r'(<script src="\.\./js/common\.js"></script>)\s*<script>.*?</script>', re.S)


def n(v):
    if isinstance(v, int):
        return str(v)
    rv = round(v, 1)
    if rv == int(rv):
        return str(int(rv))
    s = f"{rv:.1f}"
    return "0" if s == "-0" else s


def pt(p):
    return f"{n(p[0])},{n(p[1])}"


def poly_path(points, close=True):
    d = "M" + " L".join(pt(p) for p in points)
    return d + (" Z" if close else "")


def smooth_island(cx, cy, rx, ry, rot=0, seed=1, shape="organic", n_pts=16, iters=2):
    """Generate rich, varied organic dredged islands with natural coastlines."""
    rad = math.radians(rot)
    cr, sr = math.cos(rad), math.sin(rad)
    pts = []
    for i in range(n_pts):
        ang = 2 * math.pi * i / n_pts
        c_a = math.cos(ang)
        s_a = math.sin(ang)

        # Multi-harmonic variation for natural sand bank curves
        rf = 1.0 + 0.07 * math.sin(2 * ang + seed) + 0.05 * math.cos(3 * ang + seed * 2) + 0.03 * math.sin(5 * ang + seed)

        lx = rx * c_a * rf
        ly = ry * s_a * rf

        if shape == "taper":  # Tapers along +y (like South America, India, Snout)
            taper_factor = max(0.28, 1.0 - 0.45 * (s_a + 0.2)) if s_a > -0.2 else 1.0 + 0.15 * s_a
            lx *= taper_factor
        elif shape == "arc":  # Curves along y axis
            lx += (ly * ly) / (ry * 3.6)
        elif shape == "casque":  # Swept back casque crest
            if s_a < 0:
                lx -= (ly * ly) / (ry * 2.6)
                rf *= 1.2
        elif shape == "spine":  # Triangular dorsal crest spike
            if s_a < 0:
                ly *= 1.35
                lx *= 0.65

        # Rotate and translate
        gx = cx + (lx * cr - ly * sr)
        gy = cy + (lx * sr + ly * cr)
        pts.append((gx, gy))

    # Chaikin smoothing
    smoothed = pts
    for _ in range(iters):
        n_p = len(smoothed)
        s2 = []
        for j in range(n_p):
            p0 = smoothed[j]
            p1 = smoothed[(j + 1) % n_p]
            s2.append((0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]))
            s2.append((0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]))
        smoothed = s2

    # Quadratic Bezier Path
    d_parts = [f"M{pt(smoothed[0])}"]
    m = len(smoothed)
    for i in range(0, m, 2):
        p1 = smoothed[(i + 1) % m]
        p2 = smoothed[(i + 2) % m]
        d_parts.append(f"Q{pt(p1)} {pt(p2)}")
    d_parts.append("Z")
    return " ".join(d_parts)


def hotspot(i, x, y, color, r=11):
    return [
        f'<g class="map-hotspot" data-spot="{i}" transform="translate({n(x)}, {n(y)})">',
        f'<circle class="hotspot-pulse" r="{r + 5}" fill="{color}" opacity="0.6" />',
        f'<circle class="hotspot-core" r="{r}" />',
        f"<text>{i}</text>",
        "</g>",
    ]

MAP_NAMES = {
    0: "Palm Island",
    1: "World Islands",
    2: "Chameleon Islands",
}


def map_header():
    return [
        '<svg class="ill" viewBox="0 0 1200 700">',
        "<defs>",
        '<linearGradient id="island-sea" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#0c3461" />',
        '<stop offset="40%" stop-color="#185694" />',
        '<stop offset="100%" stop-color="#2c7ebd" />',
        "</linearGradient>",
        '<radialGradient id="lagoon-glow" cx="50%" cy="50%" r="50%">',
        '<stop offset="0%" stop-color="#73c7ea" stop-opacity="0.5" />',
        '<stop offset="100%" stop-color="#19558e" stop-opacity="0" />',
        "</radialGradient>",
        '<filter id="glow-gold" x="-20%" y="-20%" width="140%" height="140%">',
        '<feGaussianBlur stdDeviation="3" result="blur" />',
        '<feComposite in="SourceGraphic" in2="blur" operator="over" />',
        "</filter>",
        '<filter id="glass-glow" x="-20%" y="-20%" width="140%" height="140%">',
        '<feGaussianBlur stdDeviation="4" result="blur" />',
        '<feComposite in="SourceGraphic" in2="blur" operator="over" />',
        "</filter>",
        "</defs>",
        "<!-- Deep Ocean Water Base -->",
        '<rect width="1200" height="700" fill="url(#island-sea)" />',
    ]


def update_island_map(map_index: int, svg_generator):
    """Update a single island map (0: Palm, 1: World, 2: Chameleon) in both en and hu infrastructure pages."""
    try:
        from build_pages import format_and_remove_empty_lines
    except ImportError:
        sys.path.insert(0, str(ROOT / "scripts"))
        from build_pages import format_and_remove_empty_lines

    map_name = MAP_NAMES.get(map_index, f"map {map_index}")
    new_svg = "\n".join(svg_generator())
    for lang in ("en", "hu"):
        path = ROOT / lang / "infrastructure.html"
        html = path.read_text(encoding="utf-8")
        matches = list(SVG_RE.finditer(html))
        if len(matches) != 3:
            sys.exit(f"{lang}: expected 3 island maps, found {len(matches)}")
        target = matches[map_index]
        start, end = target.span()
        updated_html = html[:start] + new_svg + html[end:]
        updated_html, _ = SCRIPT_RE.subn(r'\1\n<script src="../js/infrastructure.js"></script>', updated_html)
        cleaned = format_and_remove_empty_lines(updated_html)
        path.write_text(cleaned, encoding="utf-8")
        rel_path = path.relative_to(ROOT)
        size_kb = len(new_svg.encode("utf-8")) / 1024
        print(f"Updated map {map_index} ({map_name}) in {rel_path} ({size_kb:.1f} KB)")
