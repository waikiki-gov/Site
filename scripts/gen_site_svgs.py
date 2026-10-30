#!/usr/bin/env python3
"""
Generate detailed, realistic, and seamless inline SVG illustrations for:
  - ski-paradise.html (Hero 640x540, Summit Elevation Comparison 960x390, 5 Resort Cards 320x200)
  - travel-guide.html (Hero 640x480, 15 Luxury Hotel & Sanctuary Cards 320x200)
  - infrastructure.html (Hero 640x480, Tallest Structures Chart 1120x420, 10 Landmark Cards 320x200)

Preserves all localized attributes and text labels across English (en/) and Hungarian (hu/).
Formats all updated HTML files with 4-space indentation and zero blank lines.
"""

from __future__ import annotations

import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def n(val: float) -> str:
    return f"{val:.1f}".rstrip("0").rstrip(".")


def rnd(i: int, seed: float = 1.0) -> float:
    return (math.sin(i * 12.9898 + seed * 78.233) * 43758.5453) % 1.0


def poly(pts: list[tuple[float, float]], close: bool = True) -> str:
    body = " ".join(f"{'L' if idx else 'M'}{n(x)},{n(y)}" for idx, (x, y) in enumerate(pts))
    return f"{body} Z" if close else body


def subdiv_ridge(p1: tuple[float, float], p2: tuple[float, float], roughness: float = 8.0, seed: float = 1.0, steps: int = 8):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = p1[0] + (p2[0] - p1[0]) * t
        y = p1[1] + (p2[1] - p1[1]) * t
        if 0 < i < steps:
            env = math.sin(math.pi * t)
            off = roughness * env * (0.62 * math.sin(i * 2.7 + seed * 1.3) + 0.38 * math.cos(i * 4.9 + seed * 2.1))
            y += off
            x += off * 0.25 * math.cos(i * 3.1 + seed)
        pts.append((x, y))
    return pts


def draw_mountain_3d(
    apex: tuple[float, float],
    w_left: float,
    w_right: float,
    base_y: float,
    lit_col: str,
    shade_col: str,
    snow_lit: str,
    snow_shade: str,
    snow_frac: float = 0.55,
    seed: float = 1.0,
    spine_shift: float = 0.12,
    rock_col: str = "#1e3a5f",
) -> list[str]:
    """Render a realistic 3D faceted mountain with jagged snowcap, rock crags, and arête highlights."""
    px, py = apex
    lb = (px - w_left, base_y)
    rb = (px + w_right, base_y)
    sb = (px + (w_right - w_left) * 0.3 + (w_left + w_right) * 0.5 * spine_shift, base_y)
    rough = (w_left + w_right) * 0.038
    left = subdiv_ridge(lb, apex, rough, seed, 8)
    right = subdiv_ridge(apex, rb, rough, seed + 3.1, 8)
    spine = subdiv_ridge(apex, sb, rough * 0.8, seed + 7.3, 8)
    left_fa = list(reversed(left))

    out = [
        f'<path d="{poly(left + spine[1:])}" fill="{lit_col}" />',
        f'<path d="{poly(right + list(reversed(spine[:-1])))}" fill="{shade_col}" />',
    ]

    # Rock crags on lower faces
    for k in (4, 6):
        a, b = spine[k], spine[k + 1]
        m_r = (a[0] * 0.55 + right[k][0] * 0.45, a[1] * 0.55 + right[k][1] * 0.45 + 5)
        m_l = (a[0] * 0.65 + left_fa[k][0] * 0.35, a[1] * 0.65 + left_fa[k][1] * 0.35 + 4)
        out.append(f'<path d="{poly([a, m_r, b])}" fill="{rock_col}" opacity="0.45" />')
        out.append(f'<path d="{poly([a, m_l, b])}" fill="{rock_col}" opacity="0.28" />')

    # Jagged snow cap
    idx_s = max(2, min(7, int(round(snow_frac * 8))))
    l_snow = left_fa[: idx_s + 1]
    s_snow = spine[: idx_s + 1]
    r_snow = right[: idx_s + 1]
    lp, sp, rp = l_snow[-1], s_snow[-1], r_snow[-1]
    depth = (base_y - py) * 0.075

    fringe_l = []
    for j in range(1, 6):
        t = j / 6.0
        fx = lp[0] + (sp[0] - lp[0]) * t
        fy = lp[1] + (sp[1] - lp[1]) * t + (depth * (0.6 + 0.4 * rnd(j, seed)) if j % 2 else -depth * 0.22)
        fringe_l.append((fx, fy))

    fringe_r = []
    for j in range(1, 6):
        t = j / 6.0
        fx = sp[0] + (rp[0] - sp[0]) * t
        fy = sp[1] + (rp[1] - sp[1]) * t + (depth * (0.6 + 0.4 * rnd(j + 9, seed)) if j % 2 else -depth * 0.22)
        fringe_r.append((fx, fy))

    out.append(f'<path d="{poly(l_snow + fringe_l + list(reversed(s_snow)))}" fill="{snow_lit}" />')
    out.append(f'<path d="{poly(s_snow + fringe_r + list(reversed(r_snow)))}" fill="{snow_shade}" />')
    out.append(f'<path d="{poly(l_snow, close=False)}" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.88" />')
    out.append(f'<path d="{poly(s_snow, close=False)}" fill="none" stroke="#ffffff" stroke-width="1.3" opacity="0.92" />')
    return out


def draw_spruce(x: float, y: float, scale: float = 1.0, snow: bool = True) -> list[str]:
    """3-tiered alpine spruce with shadow, trunk, and optional snow frost."""
    h = 22.0 * scale
    w = 7.8 * scale
    out = [
        f'<ellipse cx="{n(x + 1.8 * scale)}" cy="{n(y + 1)}" rx="{n(w * 0.9)}" ry="{n(w * 0.28)}" fill="#09192c" opacity="0.32" />',
        f'<rect x="{n(x - 0.9 * scale)}" y="{n(y - h * 0.18)}" width="{n(1.8 * scale)}" height="{n(h * 0.22)}" fill="#4a2c18" />',
        f'<path d="M{n(x)},{n(y - h * 0.72)} L{n(x - w)},{n(y - h * 0.08)} Q{n(x)},{n(y + h * 0.04)} {n(x + w)},{n(y - h * 0.08)} Z" fill="#0d3b3e" />',
        f'<path d="M{n(x)},{n(y - h * 0.92)} L{n(x - w * 0.8)},{n(y - h * 0.36)} Q{n(x)},{n(y - h * 0.26)} {n(x + w * 0.8)},{n(y - h * 0.36)} Z" fill="#145354" />',
        f'<path d="M{n(x)},{n(y - h * 1.08)} L{n(x - w * 0.58)},{n(y - h * 0.62)} Q{n(x)},{n(y - h * 0.54)} {n(x + w * 0.58)},{n(y - h * 0.62)} Z" fill="#1d6e6a" />',
    ]
    if snow:
        out.append(
            f'<path d="M{n(x)},{n(y - h * 1.08)} L{n(x - w * 0.45)},{n(y - h * 0.68)} Q{n(x - w * 0.08)},{n(y - h * 0.61)} {n(x + w * 0.25)},{n(y - h * 0.72)} Z" fill="#f0f9ff" opacity="0.92" />'
        )
        out.append(
            f'<path d="M{n(x - w * 0.62)},{n(y - h * 0.4)} Q{n(x - w * 0.2)},{n(y - h * 0.34)} {n(x + w * 0.3)},{n(y - h * 0.42)}" fill="none" stroke="#e0f2fe" stroke-width="{n(1.3 * scale)}" stroke-linecap="round" opacity="0.8" />'
        )
    return out


def draw_palm(x: float, y: float, scale: float = 1.0, tilt: float = 1.0) -> list[str]:
    """Detailed tropical coconut palm with curved ringed trunk, coconuts, and 8 layered fronds."""
    tx = x + 9.0 * tilt * scale
    ty = y - 34.0 * scale
    cx = x + 3.5 * tilt * scale
    cy = y - 17.0 * scale
    out = [
        f'<ellipse cx="{n(x + 3 * scale)}" cy="{n(y + 1)}" rx="{n(10 * scale)}" ry="{n(3 * scale)}" fill="#0f172a" opacity="0.22" />',
        f'<path d="M{n(x - 1.8 * scale)},{n(y)} Q{n(cx - 1.1 * scale)},{n(cy)} {n(tx - 0.8 * scale)},{n(ty)} L{n(tx + 0.8 * scale)},{n(ty)} Q{n(cx + 1.2 * scale)},{n(cy)} {n(x + 1.8 * scale)},{n(y)} Z" fill="#6b4226" />',
        f'<path d="M{n(x)},{n(y)} Q{n(cx)},{n(cy)} {n(tx)},{n(ty)}" fill="none" stroke="#8c5834" stroke-width="{n(1.3 * scale)}" stroke-dasharray="2 2.4" opacity="0.75" />',
    ]
    fronds = [
        (-21, 3, -11, -7, "#14532d"),
        (-18, 10, -10, 0, "#166534"),
        (21, 3, 11, -7, "#15803d"),
        (18, 10, 10, 0, "#166534"),
        (-16, -8, -8, -12, "#16a34a"),
        (16, -8, 8, -12, "#22c55e"),
        (-6, -16, -3, -11, "#4ade80"),
        (7, -15, 4, -11, "#22c55e"),
    ]
    for dx, dy, qx_o, qy_o, col in fronds:
        fx, fy = tx + dx * scale, ty + dy * scale
        qx, qy = tx + qx_o * scale, ty + qy_o * scale
        out.append(
            f'<path d="M{n(tx)},{n(ty)} Q{n(qx)},{n(qy)} {n(fx)},{n(fy)} Q{n(qx + (0.6 if dx > 0 else -0.6) * scale)},{n(qy + 3.4 * scale)} {n(tx)},{n(ty + 1.2 * scale)} Z" fill="{col}" opacity="0.95" />'
        )
    out.append(f'<circle cx="{n(tx - 1.4 * scale)}" cy="{n(ty + 1.6 * scale)}" r="{n(1.8 * scale)}" fill="#451a03" />')
    out.append(f'<circle cx="{n(tx + 1.4 * scale)}" cy="{n(ty + 1.8 * scale)}" r="{n(1.7 * scale)}" fill="#5c2d0c" />')
    return out


def window_grid(x0: float, y0: float, w: float, h: float, cols: int, rows: int, col: str = "#fde68a", op: float = 0.75) -> str:
    """Generate a crisp grid of illuminated windows inside a facade rectangle."""
    out = [f'<g fill="{col}" opacity="{n(op)}">']
    dx = w / cols
    dy = h / rows
    ww = max(1.2, dx * 0.56)
    wh = max(1.2, dy * 0.52)
    for r in range(rows):
        for c in range(cols):
            wx = x0 + c * dx + (dx - ww) * 0.5
            wy = y0 + r * dy + (dy - wh) * 0.5
            out.append(f'<rect x="{n(wx)}" y="{n(wy)}" width="{n(ww)}" height="{n(wh)}" rx="0.5" />')
    out.append("</g>")
    return "".join(out)


# ==============================================================================
# 1. SKI PARADISE SVGS
# ==============================================================================
def build_ski_hero() -> str:
    """Hero 640x540: Twilight Alpine Panorama of Pico Soberano, Cryo-Dome, Gondola & Grand Palace."""
    o = [
        '<svg class="ill" viewBox="0 0 640 540">',
        "<defs>",
        '<linearGradient id="skiHeroSky" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#07162c" />',
        '<stop offset="38%" stop-color="#133a6c" />',
        '<stop offset="72%" stop-color="#3b6ea5" />',
        '<stop offset="92%" stop-color="#e5b879" />',
        '<stop offset="100%" stop-color="#fdf4e3" />',
        "</linearGradient>",
        '<linearGradient id="skiPeakLit" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#ffffff" />',
        '<stop offset="55%" stop-color="#e0f2fe" />',
        '<stop offset="100%" stop-color="#93c5fd" />',
        "</linearGradient>",
        '<linearGradient id="skiPeakShade" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#25578a" />',
        '<stop offset="100%" stop-color="#0c2544" />',
        "</linearGradient>",
        '<linearGradient id="skiSlopeGrad" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#f8fafc" />',
        '<stop offset="55%" stop-color="#dbeafe" />',
        '<stop offset="100%" stop-color="#93c5fd" />',
        "</linearGradient>",
        '<radialGradient id="skiSunGlow" cx="0.5" cy="0.5" r="0.5">',
        '<stop offset="0%" stop-color="#fef08a" stop-opacity="0.95" />',
        '<stop offset="45%" stop-color="#f59e0b" stop-opacity="0.45" />',
        '<stop offset="100%" stop-color="#f59e0b" stop-opacity="0" />',
        "</radialGradient>",
        "</defs>",
        '<rect width="640" height="540" rx="28" fill="url(#skiHeroSky)" />',
        # Stars and aurora glow
        '<g fill="#ffffff" opacity="0.8">',
        '<circle cx="64" cy="48" r="1.4" class="twinkle" />',
        '<circle cx="142" cy="34" r="1.8" class="twinkle" />',
        '<circle cx="235" cy="62" r="1.2" class="twinkle" />',
        '<circle cx="318" cy="28" r="1.6" class="twinkle" />',
        '<circle cx="412" cy="44" r="1.3" class="twinkle" />',
        '<circle cx="568" cy="52" r="1.7" class="twinkle" />',
        '<circle cx="515" cy="26" r="1.2" class="twinkle" />',
        "</g>",
        # Alpenglow sun disk behind eastern col
        '<circle cx="485" cy="158" r="95" fill="url(#skiSunGlow)" />',
        '<circle cx="485" cy="158" r="28" fill="#fffbeb" opacity="0.95" />',
    ]
    # Distant range
    o += draw_mountain_3d((115, 168), 125, 135, 360, "#4a78a6", "#1e3f66", "#f1f5f9", "#93c5fd", 0.55, seed=2.1)
    o += draw_mountain_3d((535, 152), 145, 125, 360, "#4a78a6", "#1b3a5c", "#fff7ed", "#93c5fd", 0.58, seed=5.4)
    # Main Pico Soberano (center-left) & Monte Rosa (center-right)
    o += draw_mountain_3d(
        (265, 76), 195, 205, 375, "#2b5c8f", "#0f2c52", "url(#skiPeakLit)", "url(#skiPeakShade)", 0.68, seed=8.2, rock_col="#091d36"
    )
    o += draw_mountain_3d(
        (435, 118), 155, 185, 375, "#31669d", "#12325c", "url(#skiPeakLit)", "url(#skiPeakShade)", 0.64, seed=11.7, rock_col="#0c2240"
    )
    # Summit Observatory & Cryo-Beacon on Pico Soberano (265, 76)
    o += [
        '<g transform="translate(265, 76)">',
        '<rect x="-14" y="-4" width="28" height="6" rx="1.5" fill="#1e293b" stroke="#fbbf24" stroke-width="0.9" />',
        '<path d="M-10,-4 A10,9 0 0,1 10,-4 Z" fill="#38bdf8" stroke="#ffffff" stroke-width="1" />',
        '<line x1="0" y1="-13" x2="0" y2="-24" stroke="#fbbf24" stroke-width="1.6" />',
        '<circle cx="0" cy="-25" r="3" fill="#f97316" class="pulse" />',
        "</g>",
        # Monte Rosa Glass Dome on (435, 118)
        '<g transform="translate(435, 118)">',
        '<ellipse cx="0" cy="0" rx="16" ry="4" fill="#0f172a" />',
        '<path d="M-13,-1 A13,11 0 0,1 13,-1 Z" fill="#7dd3fc" opacity="0.88" stroke="#fde68a" stroke-width="1" />',
        "</g>",
        # Sweeping snow slopes & groomed pistes in mid/foreground
        '<path d="M0,345 Q165,318 335,342 T640,332 L640,540 L0,540 Z" fill="url(#skiSlopeGrad)" />',
        '<path d="M0,415 Q210,382 420,412 T640,398 L640,540 L0,540 Z" fill="#e2e8f0" opacity="0.85" />',
        '<path d="M0,468 Q260,442 640,465 L640,540 L0,540 Z" fill="#cbd5e1" opacity="0.7" />',
        # Carved ski pistes from summit to valley
        '<path d="M265,86 C235,148 288,210 232,278 C178,342 268,395 195,468" fill="none" stroke="#ffffff" stroke-width="7" stroke-linecap="round" opacity="0.78" />',
        '<path d="M265,86 C235,148 288,210 232,278 C178,342 268,395 195,468" fill="none" stroke="#38bdf8" stroke-width="1.6" stroke-dasharray="5 5" class="dash" />',
        '<path d="M435,124 C405,178 448,235 395,295 C345,352 418,405 375,462" fill="none" stroke="#ffffff" stroke-width="5.5" stroke-linecap="round" opacity="0.72" />',
        '<path d="M435,124 C405,178 448,235 395,295 C345,352 418,405 375,462" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="5 5" />',
        # Aerial Gondola Cableway & Pylons
        '<path d="M82,428 Q262,258 432,120" fill="none" stroke="#0f172a" stroke-width="1.6" opacity="0.8" />',
        '<path d="M82,432 Q262,262 432,124" fill="none" stroke="#334155" stroke-width="1.1" opacity="0.65" />',
        # Support pylon at (228, 304)
        '<g stroke="#1e293b" stroke-width="1.6" fill="none">',
        '<line x1="224" y1="332" x2="228" y2="286" />',
        '<line x1="232" y1="332" x2="228" y2="286" />',
        '<line x1="218" y1="286" x2="238" y2="286" />',
        "</g>",
        # Gondola Cabins
        '<g class="bob" transform="translate(168, 344)">',
        '<line x1="0" y1="-12" x2="0" y2="0" stroke="#0f172a" stroke-width="1.5" />',
        '<rect x="-11" y="0" width="22" height="14" rx="4" fill="#c95a41" stroke="#ffffff" stroke-width="1" />',
        '<rect x="-7" y="3" width="14" height="6" rx="1.5" fill="#e0f2fe" />',
        "</g>",
        '<g class="bob" transform="translate(318, 212)">',
        '<line x1="0" y1="-11" x2="0" y2="0" stroke="#0f172a" stroke-width="1.4" />',
        '<rect x="-9" y="0" width="18" height="12" rx="3.5" fill="#0f2c52" stroke="#fbbf24" stroke-width="1" />',
        '<rect x="-6" y="2.5" width="12" height="5" rx="1" fill="#bae6fd" />',
        "</g>",
    ]
    # Grand Alpine Palace & Thermal Infinity Pool in foreground right (x=370..575, y=385..475)
    o += [
        '<g transform="translate(385, 388)">',
        # Stone terrace & steaming infinity pool
        '<path d="M-25,62 L185,62 L198,84 L-38,84 Z" fill="#475569" stroke="#94a3b8" stroke-width="1" />',
        '<polygon points="-18,66 115,66 122,79 -24,79" fill="#38bdf8" stroke="#e0f2fe" stroke-width="1.2" />',
        '<path d="M0,62 Q4,-8 0,-14 M28,62 Q32,4 28,-4 M58,62 Q62,2 58,-6 M88,62 Q92,6 88,-2" fill="none" stroke="#ffffff" stroke-width="1.5" opacity="0.55" stroke-linecap="round" />',
        # Left wing
        '<rect x="-8" y="22" width="52" height="40" fill="#5c3a21" stroke="#3b2313" stroke-width="1" />',
        '<polygon points="-14,24 18,-2 50,24" fill="#1e293b" stroke="#cbd5e1" stroke-width="1.2" />',
        '<path d="M-12,23 L18,0 L48,23" fill="none" stroke="#f8fafc" stroke-width="2.5" stroke-linecap="round" />',
        window_grid(-2, 28, 40, 28, 4, 3, "#fde68a", 0.9),
        # Right wing
        '<rect x="112" y="22" width="52" height="40" fill="#5c3a21" stroke="#3b2313" stroke-width="1" />',
        '<polygon points="106,24 138,-2 170,24" fill="#1e293b" stroke="#cbd5e1" stroke-width="1.2" />',
        '<path d="M108,23 L138,0 L168,23" fill="none" stroke="#f8fafc" stroke-width="2.5" stroke-linecap="round" />',
        window_grid(118, 28, 40, 28, 4, 3, "#fde68a", 0.9),
        # Central Grand Gable & Panoramic Atrium
        '<rect x="38" y="8" width="80" height="54" fill="#6b4423" stroke="#3b2313" stroke-width="1.2" />',
        '<polygon points="30,12 78,-26 126,12" fill="#0f172a" stroke="#e2e8f0" stroke-width="1.4" />',
        '<path d="M32,11 L78,-24 L124,11" fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round" />',
        # Arched golden glass atrium
        '<path d="M58,62 L58,24 A20,18 0 0,1 98,24 L98,62 Z" fill="#fef08a" stroke="#d97706" stroke-width="1.2" />',
        '<line x1="78" y1="6" x2="78" y2="62" stroke="#b45309" stroke-width="1.2" />',
        '<line x1="58" y1="34" x2="98" y2="34" stroke="#b45309" stroke-width="1.2" />',
        '<line x1="58" y1="48" x2="98" y2="48" stroke="#b45309" stroke-width="1.2" />',
        window_grid(42, 16, 12, 38, 2, 4, "#fde68a", 0.92),
        window_grid(102, 16, 12, 38, 2, 4, "#fde68a", 0.92),
        "</g>",
    ]
    # Layered Alpine Spruce Forest across mid-ground and foreground
    for sx, sy, sc in [
        (42, 388, 0.85), (68, 396, 1.05), (96, 392, 0.9), (128, 404, 1.15), (156, 398, 0.95),
        (292, 412, 0.9), (322, 418, 1.1), (348, 414, 0.85),
        (578, 402, 1.0), (606, 412, 1.2), (28, 465, 1.35), (62, 478, 1.5), (105, 472, 1.25),
        (595, 475, 1.4),
    ]:
        o += draw_spruce(sx, sy, sc, snow=True)

    o.append("</svg>")
    return "".join(o)


def build_ski_height_chart(lang: str) -> str:
    """Summit Elevation Comparison Chart (viewBox 0 0 960 390) with 6 realistic 3D peaks."""
    aria = (
        "Alpine summit elevation comparison chart"
        if lang == "en"
        else "Alpesi csúcsmagasságok összehasonlító diagramja"
    )
    ticks = (
        [("5,000 m", 54), ("3,750 m", 124), ("2,500 m", 194), ("1,250 m", 264), ("0 m", 334)]
        if lang == "en"
        else [("5000 m", 54), ("3750 m", 124), ("2500 m", 194), ("1250 m", 264), ("0 m", 334)]
    )
    peaks_meta = (
        [
            (145, 58, "4,850 m", 40, "Pico Soberano", "Waikiki Andes", False),
            (295, 82, "4,420 m", 68, "Condor Glacier", "Waikiki Andes", False),
            (445, 112, "3,883 m", 98, "Zermatt Glacier", "Switzerland (Ref.)", True),
            (595, 150, "3,200 m", 130, "Monte Rosa Dome", "Waikiki Andes", False),
            (745, 152, "3,180 m", 136, "Haiti Glacier Crown", "Haiti Island", False),
            (870, 176, "2,738 m", 162, "Courchevel", "France (Ref.)", True),
        ]
        if lang == "en"
        else [
            (145, 58, "4850 m", 40, "Pico Soberano", "Waikiki Andok", False),
            (295, 82, "4420 m", 68, "Condor Gleccser", "Waikiki Andok", False),
            (445, 112, "3883 m", 98, "Zermatt Gleccser", "Svájc (Ref.)", True),
            (595, 150, "3200 m", 130, "Monte Rosa Kupola", "Waikiki Andok", False),
            (745, 152, "3180 m", 136, "Haiti Gleccserkorona", "Haiti-sziget", False),
            (870, 176, "2738 m", 162, "Courchevel", "Franciaország (Ref.)", True),
        ]
    )

    o = [
        f'<svg class="ill height-chart" viewBox="0 0 960 390" data-reveal aria-label="{aria}">',
        "<defs>",
        '<linearGradient id="hcPeakAndesLit" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#3b82f6" />',
        '<stop offset="100%" stop-color="#1d4ed8" />',
        "</linearGradient>",
        '<linearGradient id="hcPeakAndesShade" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#1e3a8a" />',
        '<stop offset="100%" stop-color="#0f172a" />',
        "</linearGradient>",
        '<linearGradient id="hcPeakHaitiLit" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#10b981" />',
        '<stop offset="55%" stop-color="#047857" />',
        '<stop offset="100%" stop-color="#064e3b" />',
        "</linearGradient>",
        '<linearGradient id="hcPeakHaitiShade" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#065f46" />',
        '<stop offset="100%" stop-color="#022c22" />',
        "</linearGradient>",
        '<linearGradient id="hcPeakRefLit" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#94a3b8" />',
        '<stop offset="100%" stop-color="#475569" />',
        "</linearGradient>",
        "</defs>",
        '<g class="k-line" stroke-dasharray="3 6">',
        '<line x1="60" y1="50" x2="925" y2="50" />',
        '<line x1="60" y1="120" x2="925" y2="120" />',
        '<line x1="60" y1="190" x2="925" y2="190" />',
        '<line x1="60" y1="260" x2="925" y2="260" />',
        "</g>",
    ]
    for label, ty in ticks:
        o.append(f'<text x="50" y="{ty}" text-anchor="end" font-size="10" class="h-ref">{label}</text>')

    # Render each of the 6 peaks with realistic 3D facets, snowcaps, and summit landmarks
    for idx, (cx, py, val_s, val_y, name_s, sub_s, is_ref) in enumerate(peaks_meta):
        op = ' opacity="0.68"' if is_ref else ""
        o.append(f'<g class="tower" style="--d: {idx}"{op}>')
        if is_ref:
            o += draw_mountain_3d(
                (cx, py), 52, 52, 330, "url(#hcPeakRefLit)", "#334155", "#f1f5f9", "#cbd5e1", 0.52, seed=idx * 3.7 + 1
            )
        elif idx == 4:
            # Haiti Glacier Crown: emerald rainforest base + golden coastal beach strip + snow crown
            o += draw_mountain_3d(
                (cx, py), 58, 58, 330, "url(#hcPeakHaitiLit)", "url(#hcPeakHaitiShade)", "#ffffff", "#bae6fd", 0.48, seed=19.2, rock_col="#064e3b"
            )
            o.append(f'<path d="M{cx - 58},330 Q{cx},323 {cx + 58},330 Z" fill="#fbbf24" opacity="0.85" />')
            o.append(f'<polygon points="{cx - 8},{py} {cx},{py - 10} {cx + 8},{py}" fill="#f59e0b" />')
        else:
            o += draw_mountain_3d(
                (cx, py), 60, 60, 330, "url(#hcPeakAndesLit)", "url(#hcPeakAndesShade)", "#ffffff", "#bfdbfe", 0.58, seed=idx * 5.1 + 2, rock_col="#172554"
            )
            if idx == 0:
                # Pico Soberano summit beacon & golden crown
                o.append(f'<polygon points="{cx - 14},{py + 28} {cx},{py} {cx + 14},{py + 28}" fill="#fbbf24" opacity="0.85" />')
                o.append(f'<circle cx="{cx}" cy="{py - 6}" r="4" class="f-coral pulse" />')
            elif idx == 1:
                # Condor Glacier helicopter pad & glacial cirque
                o.append(f'<rect x="{cx - 9}" y="{py - 3}" width="18" height="3.5" rx="1" fill="#fbbf24" />')
            elif idx == 3:
                # Monte Rosa Sky Observatory glass dome
                o.append(f'<ellipse cx="{cx}" cy="{py}" rx="12" ry="3.5" fill="#0f172a" />')
                o.append(f'<path d="M{cx - 10},{py} A10,9 0 0,1 {cx + 10},{py} Z" fill="#38bdf8" stroke="#fde68a" stroke-width="1.2" />')
        o.append("</g>")

        val_cls = "h-val h-ref" if is_ref else "h-val"
        name_cls = "h-name h-ref" if is_ref else "h-name"
        o.append(f'<text x="{cx}" y="{val_y}" text-anchor="middle" class="{val_cls}">{val_s}</text>')
        o.append(f'<text x="{cx}" y="352" text-anchor="middle" class="{name_cls}">{name_s}</text>')
        o.append(f'<text x="{cx}" y="368" text-anchor="middle" font-size="9" class="h-ref">{sub_s}</text>')

    o.append('<line x1="60" y1="330" x2="925" y2="330" class="k-ink" stroke-width="1.8" />')
    o.append("</svg>")
    return "".join(o)


def build_ski_resort_card(idx: int) -> str:
    """
    Build the 5 Alpine Resort cards (viewBox 0 0 320 200) on ski-paradise.html:
      0: Grand Palace Val d'Aurelia
      1: Ski Paradise Royal Chalets
      2: Monte Rosa Sky Observatory
      3: Haiti Glacier Crown Resort
      4: Edelweiss Thermal Village
    """
    o = [f'<svg class="ill" viewBox="0 0 320 200">']
    if idx == 0:
        # Grand Palace Val d'Aurelia: Belle-Epoque palace with twin turrets, warm lit windows & steaming pool
        o += [
            '<defs><linearGradient id="spCard0Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0c2340"/><stop offset="65%" stop-color="#1e4e79"/><stop offset="100%" stop-color="#e5c185"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#spCard0Sky)" />',
            '<circle cx="265" cy="42" r="22" fill="#fef08a" opacity="0.85" />',
            *draw_mountain_3d((85, 32), 110, 120, 148, "#2b5c8f", "#102a4c", "#ffffff", "#bfdbfe", 0.62, seed=1.4),
            *draw_mountain_3d((235, 38), 115, 110, 148, "#336699", "#13335c", "#ffffff", "#bfdbfe", 0.58, seed=4.2),
            '<path d="M0,142 Q160,132 320,144 L320,200 L0,200 Z" fill="#e2e8f0" />',
            # Palace wings and twin turrets
            '<rect x="58" y="96" width="204" height="52" fill="#6b4423" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="52,98 160,64 268,98" fill="#1e293b" stroke="#e2e8f0" stroke-width="1.2" />',
            '<rect x="64" y="76" width="26" height="72" fill="#7c4d28" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="60,78 77,50 94,78" fill="#0f172a" stroke="#f8fafc" stroke-width="1" />',
            '<rect x="230" y="76" width="26" height="72" fill="#7c4d28" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="226,78 243,50 260,78" fill="#0f172a" stroke="#f8fafc" stroke-width="1" />',
            '<rect x="122" y="82" width="76" height="66" fill="#85522b" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="116,84 160,46 204,84" fill="#0f172a" stroke="#ffffff" stroke-width="1.4" />',
            # Arched golden atrium & windows
            '<path d="M144,148 L144,108 A16,15 0 0,1 176,108 L176,148 Z" fill="#fef08a" stroke="#d97706" stroke-width="1" />',
            window_grid(94, 104, 24, 36, 2, 3, "#fde68a", 0.92),
            window_grid(202, 104, 24, 36, 2, 3, "#fde68a", 0.92),
            window_grid(68, 84, 18, 52, 2, 4, "#fde68a", 0.9),
            window_grid(234, 84, 18, 52, 2, 4, "#fde68a", 0.9),
            # Steaming outdoor thermal pool
            '<polygon points="88,158 232,158 244,182 76,182" fill="#38bdf8" stroke="#f8fafc" stroke-width="1.5" />',
            '<path d="M115,156 Q118,142 114,136 M160,156 Q164,140 159,134 M205,156 Q209,142 204,136" fill="none" stroke="#ffffff" stroke-width="1.3" opacity="0.65" stroke-linecap="round" />',
            *draw_spruce(26, 158, 0.95), *draw_spruce(44, 164, 0.8), *draw_spruce(282, 162, 0.9), *draw_spruce(298, 156, 1.05),
        ]
    elif idx == 1:
        # Ski Paradise Royal Chalets: Timber-and-glass A-frame chalets nestled in snow-draped pines
        o += [
            '<defs><linearGradient id="spCard1Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0f2947"/><stop offset="60%" stop-color="#2c5e8a"/><stop offset="100%" stop-color="#f3d5a0"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#spCard1Sky)" />',
            *draw_mountain_3d((160, 26), 150, 150, 145, "#285582", "#102a49", "#ffffff", "#cbd5e1", 0.65, seed=3.3),
            '<path d="M0,140 Q160,128 320,142 L320,200 L0,200 Z" fill="#f1f5f9" />',
            '<path d="M160,34 C140,72 178,98 148,138" fill="none" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round" opacity="0.8" />',
            *draw_spruce(28, 148, 1.0), *draw_spruce(52, 154, 0.85), *draw_spruce(268, 152, 0.9), *draw_spruce(292, 146, 1.05),
            # Left Chalet
            '<g transform="translate(88, 132)">',
            '<rect x="-26" y="-8" width="52" height="32" fill="#5c3418" />',
            '<polygon points="-34,-6 0,-42 34,-6" fill="#1e293b" stroke="#f8fafc" stroke-width="2" />',
            '<polygon points="-18,-6 0,-28 18,-6" fill="#fef08a" stroke="#b45309" stroke-width="1" />',
            '<line x1="0" y1="-28" x2="0" y2="24" stroke="#78350f" stroke-width="1.2" />',
            window_grid(-18, -2, 36, 20, 3, 2, "#fde68a", 0.95),
            "</g>",
            # Right Master Royal Chalet
            '<g transform="translate(198, 126)">',
            '<rect x="18" y="-44" width="7" height="18" fill="#475569" />',
            '<path d="M21.5,-46 Q26,-56 20,-64" fill="none" stroke="#e2e8f0" stroke-width="1.8" stroke-linecap="round" opacity="0.7" />',
            '<rect x="-36" y="-8" width="72" height="38" fill="#6b3e1e" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="-46,-6 0,-52 46,-6" fill="#0f172a" stroke="#ffffff" stroke-width="2.4" />',
            '<polygon points="-24,-6 0,-34 24,-6" fill="#fef08a" stroke="#b45309" stroke-width="1.2" />',
            '<line x1="0" y1="-34" x2="0" y2="30" stroke="#78350f" stroke-width="1.4" />',
            window_grid(-28, -2, 56, 26, 4, 2, "#fde68a", 0.95),
            "</g>",
            *draw_spruce(138, 158, 0.92),
        ]
    elif idx == 2:
        # Monte Rosa Sky Observatory: Starry cosmos, geodesic glass dome on a 3,200m ridge + cable car
        o += [
            '<defs><linearGradient id="spCard2Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#050d1a"/><stop offset="55%" stop-color="#0f294a"/><stop offset="100%" stop-color="#1e4b7a"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#spCard2Sky)" />',
            # Aurora borealis / high-altitude airglow ribbon
            '<path d="M0,48 Q85,22 165,44 T320,32 L320,62 Q240,74 160,52 T0,68 Z" fill="#2dd4bf" opacity="0.22" />',
            '<g fill="#ffffff">',
            '<circle cx="38" cy="26" r="1.4" class="twinkle" /><circle cx="92" cy="18" r="1.8" class="twinkle" />',
            '<circle cx="148" cy="32" r="1.2" class="twinkle" /><circle cx="218" cy="22" r="1.6" class="twinkle" />',
            '<circle cx="284" cy="36" r="1.5" class="twinkle" /><circle cx="64" cy="58" r="1.2" class="twinkle" />',
            "</g>",
            *draw_mountain_3d((65, 92), 95, 95, 200, "#1e3a5f", "#0b192c", "#e0f2fe", "#64748b", 0.55, seed=6.1),
            *draw_mountain_3d((185, 86), 135, 135, 200, "#254b7c", "#0f2442", "#ffffff", "#93c5fd", 0.68, seed=9.4),
            # Cable car wire from left valley to summit observatory
            '<path d="M0,165 Q92,126 155,88" fill="none" stroke="#94a3b8" stroke-width="1.2" />',
            '<g class="bob" transform="translate(84, 122)">',
            '<line x1="0" y1="-8" x2="0" y2="0" stroke="#e2e8f0" stroke-width="1.2" />',
            '<rect x="-8" y="0" width="16" height="10" rx="3" fill="#c95a41" stroke="#ffffff" stroke-width="0.9" />',
            '<rect x="-5" y="2" width="10" height="4.5" rx="1" fill="#bae6fd" />',
            "</g>",
            # Geodesic Sky Observatory & cantilevered glass skywalk on (185, 86)
            '<g transform="translate(185, 84)">',
            '<polygon points="-52,6 48,6 38,18 -64,18" fill="#1e293b" stroke="#fbbf24" stroke-width="1.2" />',
            '<rect x="-46" y="-4" width="84" height="10" rx="2" fill="#38bdf8" opacity="0.85" stroke="#ffffff" stroke-width="0.9" />',
            '<path d="M-32,-4 A32,28 0 0,1 32,-4 Z" fill="#7dd3fc" opacity="0.88" stroke="#ffffff" stroke-width="1.4" />',
            # Geodesic truss ribs
            '<path d="M-22,-4 A22,28 0 0,1 22,-4 M-10,-4 A10,28 0 0,1 10,-4 M-28,-14 L28,-14 M-18,-24 L18,-24" fill="none" stroke="#0f172a" stroke-width="0.9" opacity="0.55" />',
            '<line x1="0" y1="-32" x2="0" y2="-46" stroke="#fbbf24" stroke-width="1.8" />',
            '<circle cx="0" cy="-47" r="3" fill="#f97316" class="pulse" />',
            "</g>",
        ]
    elif idx == 3:
        # Haiti Glacier Crown Resort: Sea-to-Summit peak rising over emerald rainforest, golden beach & Caribbean lagoon
        o += [
            '<defs><linearGradient id="spCard3Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0284c7"/><stop offset="65%" stop-color="#7dd3fc"/><stop offset="100%" stop-color="#fef3c7"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#spCard3Sky)" />',
            '<circle cx="62" cy="42" r="20" fill="#fde68a" opacity="0.92" />',
            *draw_mountain_3d((175, 24), 145, 145, 152, "#15803d", "#064e3b", "#ffffff", "#bae6fd", 0.56, seed=12.3, rock_col="#052e16"),
            # Cryo-Dome & Summit Crown Hotel
            '<g transform="translate(175, 24)">',
            '<rect x="-16" y="-2" width="32" height="7" rx="1.5" fill="#0f172a" stroke="#fbbf24" stroke-width="1" />',
            '<path d="M-11,-2 A11,9 0 0,1 11,-2 Z" fill="#38bdf8" stroke="#ffffff" stroke-width="1" />',
            "</g>",
            # Ski piste down the snow crown
            '<path d="M175,32 C162,56 186,74 168,98" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity="0.88" />',
            # Scalloped tropical cloud forest & rainforest canopy belt
            '<path d="M0,136 Q28,122 56,134 Q84,120 112,132 Q140,118 168,132 Q196,120 224,134 Q252,122 280,134 Q302,124 320,136 L320,162 L0,162 Z" fill="#166534" />',
            '<path d="M0,146 Q32,134 64,146 Q96,134 128,146 Q160,134 192,146 Q224,134 256,146 Q288,134 320,146 L320,164 L0,164 Z" fill="#15803d" />',
            # Golden sand beach & turquoise Caribbean sea with yacht
            '<path d="M0,158 Q160,150 320,160 L320,200 L0,200 Z" fill="#fde68a" />',
            '<path d="M0,166 Q160,158 320,168 L320,200 L0,200 Z" fill="#0ea5e9" />',
            '<path d="M0,168 Q160,160 320,170 L320,184 Q160,176 0,182 Z" fill="#2dd4bf" opacity="0.55" />',
            *draw_palm(38, 162, 0.85, 1.0),
            *draw_palm(72, 160, 0.72, -0.8),
            *draw_palm(278, 162, 0.82, -1.0),
            # Superyacht in foreground lagoon
            '<g class="bob" transform="translate(195, 182)">',
            '<polygon points="-22,0 22,0 16,7 -18,7" fill="#ffffff" stroke="#0f172a" stroke-width="0.9" />',
            '<rect x="-12" y="-5" width="18" height="5" rx="1.5" fill="#e0f2fe" stroke="#0284c7" stroke-width="0.7" />',
            "</g>",
        ]
    else:
        # Edelweiss Thermal Village: Car-free alpine hamlet, arched stone bridge, steaming geothermal river & domes
        o += [
            '<defs><linearGradient id="spCard4Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0f2537"/><stop offset="65%" stop-color="#2e5a78"/><stop offset="100%" stop-color="#e8c89b"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#spCard4Sky)" />',
            *draw_mountain_3d((95, 36), 115, 115, 142, "#2c5882", "#122b47", "#ffffff", "#cbd5e1", 0.58, seed=7.7),
            *draw_mountain_3d((235, 42), 110, 110, 142, "#356694", "#163557", "#ffffff", "#cbd5e1", 0.54, seed=10.2),
            '<path d="M0,136 Q160,126 320,138 L320,200 L0,200 Z" fill="#e2e8f0" />',
            # Winding steaming geothermal river through snow banks
            '<path d="M168,134 C142,150 188,168 145,200 L198,200 C222,168 175,150 192,134 Z" fill="#38bdf8" stroke="#f8fafc" stroke-width="2" />',
            '<path d="M158,152 Q162,138 157,130 M182,168 Q186,154 181,146 M168,184 Q172,170 167,162" fill="none" stroke="#ffffff" stroke-width="1.5" opacity="0.7" stroke-linecap="round" />',
            # Arched stone footbridge over thermal river
            '<path d="M142,168 Q176,152 210,168 L210,175 Q176,160 142,175 Z" fill="#64748b" stroke="#334155" stroke-width="1" />',
            # Copper-domed thermal bath pavilions (left) & alpine chalets (right)
            '<g transform="translate(76, 134)">',
            '<rect x="-34" y="-8" width="68" height="26" rx="3" fill="#475569" stroke="#1e293b" stroke-width="1" />',
            '<path d="M-26,-8 A26,20 0 0,1 26,-8 Z" fill="#2dd4bf" opacity="0.82" stroke="#fbbf24" stroke-width="1.2" />',
            window_grid(-26, -2, 52, 16, 4, 2, "#fde68a", 0.9),
            "</g>",
            '<g transform="translate(248, 134)">',
            '<rect x="-28" y="-10" width="56" height="28" fill="#6b4226" />',
            '<polygon points="-34,-8 0,-34 34,-8" fill="#1e293b" stroke="#ffffff" stroke-width="1.8" />',
            window_grid(-22, -4, 44, 18, 3, 2, "#fde68a", 0.92),
            "</g>",
            *draw_spruce(22, 152, 0.9), *draw_spruce(300, 154, 0.95),
        ]
    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 2. TRAVEL GUIDE SVGS
# ==============================================================================
def build_travel_hero(lang: str) -> str:
    """Hero 640x480: Golden-hour Caribbean arrival panorama with widebody jetliner, Nova Aurelia skyline, lagoon & palms."""
    aria = (
        "Illustration of a flight route arriving on Waikiki's Caribbean coast"
        if lang == "en"
        else "Illusztráció: Waikiki karibi partjára érkező repülőútvonal"
    )
    o = [
        f'<svg class="ill" viewBox="0 0 640 480" role="img" aria-label="{aria}">',
        "<defs>",
        '<linearGradient id="tgHeroSky" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#1e3a8a" />',
        '<stop offset="35%" stop-color="#3b82f6" />',
        '<stop offset="68%" stop-color="#f59e0b" />',
        '<stop offset="100%" stop-color="#fef3c7" />',
        "</linearGradient>",
        '<linearGradient id="tgHeroSea" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#0284c7" />',
        '<stop offset="50%" stop-color="#0ea5e9" />',
        '<stop offset="100%" stop-color="#2dd4bf" />',
        "</linearGradient>",
        '<radialGradient id="tgSunGlow" cx="0.5" cy="0.5" r="0.5">',
        '<stop offset="0%" stop-color="#fffbeb" stop-opacity="1" />',
        '<stop offset="35%" stop-color="#fde047" stop-opacity="0.85" />',
        '<stop offset="70%" stop-color="#f97316" stop-opacity="0.35" />',
        '<stop offset="100%" stop-color="#f97316" stop-opacity="0" />',
        "</radialGradient>",
        "</defs>",
        '<rect width="640" height="480" rx="28" fill="url(#tgHeroSky)" />',
        # Radiant sunset orb over the bay
        '<circle cx="445" cy="242" r="145" fill="url(#tgSunGlow)" />',
        '<circle cx="445" cy="242" r="46" fill="#fffbeb" opacity="0.95" />',
        # Soft sunlit cumulus clouds
        '<g fill="#fff7ed" opacity="0.55" class="drift">',
        '<ellipse cx="145" cy="112" rx="52" ry="12" /><ellipse cx="128" cy="104" rx="28" ry="11" /><ellipse cx="164" cy="102" rx="32" ry="12" />',
        '<ellipse cx="525" cy="96" rx="46" ry="10" /><ellipse cx="512" cy="88" rx="24" ry="9" />',
        "</g>",
        # Distant volcanic & karst island mountains + Nova Aurelia skyline on the horizon (y=268)
        '<path d="M0,268 Q65,208 135,236 Q195,184 265,232 Q325,204 385,248 L640,268 Z" fill="#1e3a5f" opacity="0.72" />',
        # Distant skyline silhouettes (Sky City, Mega Pyramid, Princess Tower, Royal Clock Tower, Atlantis)
        '<g fill="#0f294a" stroke="#fbbf24" stroke-width="0.6">',
        '<polygon points="242,268 268,214 294,268" fill="#1e3a5f" />',  # Mega Pyramid
        '<polygon points="312,268 315,172 321,172 324,268" />',  # Sky City
        '<line x1="318" y1="172" x2="318" y2="156" stroke="#fbbf24" stroke-width="1.4" />',
        '<rect x="336" y="198" width="12" height="70" />',  # Princess Tower
        '<path d="M335,198 A7,6 0 0,1 349,198 Z" fill="#fbbf24" />',
        '<rect x="358" y="212" width="14" height="56" />',  # Exchange Tower
        '<rect x="382" y="204" width="16" height="64" />',  # Royal Clock Tower
        '<circle cx="390" cy="216" r="4" fill="#fde68a" />',
        '<rect x="408" y="220" width="12" height="48" />',
        "</g>",
        # Flight route arc & departure/arrival pins
        '<path d="M58,148 Q265,28 518,162" fill="none" stroke="#fffbeb" stroke-width="2.2" stroke-dasharray="7 7" class="dash" />',
        '<circle cx="58" cy="148" r="5" fill="#fbbf24" stroke="#ffffff" stroke-width="1.5" />',
        '<circle cx="518" cy="162" r="6" fill="#ef4444" stroke="#ffffff" stroke-width="1.8" class="pulse" />',
        # Detailed Widebody Jetliner Banking Along Flight Route
        '<g transform="translate(295, 84) rotate(12)">',
        # Swept far wing
        '<polygon points="-8,-2 -28,-28 -16,-28 12,-2" fill="#cbd5e1" stroke="#475569" stroke-width="0.8" />',
        # Tail fin with royal gold emblem
        '<polygon points="-38,0 -52,-22 -38,-22 -24,0" fill="#0f294a" stroke="#fbbf24" stroke-width="1" />',
        '<circle cx="-41" cy="-11" r="3" fill="#fbbf24" />',
        # Fuselage with cockpit and cabin windows
        '<path d="M-44,0 C-44,-6 -20,-7 24,-6 C38,-6 48,-2 50,1 C48,4 38,5 24,5 C-20,5 -44,4 -44,0 Z" fill="#ffffff" stroke="#1e3a8a" stroke-width="1.1" />',
        '<path d="M36,-4.5 C41,-4 45,-2 47,0 L35,0 Z" fill="#0284c7" />',
        '<path d="M-26,-1.5 L26,-1.5" stroke="#0284c7" stroke-width="1.8" stroke-dasharray="2 3" />',
        '<path d="M-40,2.5 L42,2.5" stroke="#d97706" stroke-width="1.2" />',
        # Swept near wing & twin turbofan nacelles
        '<polygon points="-6,2 -32,32 -18,32 16,2" fill="#f8fafc" stroke="#1e3a8a" stroke-width="0.9" />',
        '<rect x="-10" y="13" width="13" height="5" rx="2" fill="#1e3a8a" stroke="#fbbf24" stroke-width="0.7" />',
        '<rect x="-18" y="22" width="11" height="4.5" rx="2" fill="#1e3a8a" stroke="#fbbf24" stroke-width="0.7" />',
        "</g>",
        # Caribbean Sea, Turquoise Coral Lagoon & Sun Shimmer Path
        '<rect x="0" y="268" width="640" height="212" fill="url(#tgHeroSea)" />',
        '<path d="M0,318 Q210,298 420,324 T640,312 L640,480 L0,480 Z" fill="#14b8a6" opacity="0.45" />',
        # Sun shimmer on water
        '<g fill="#fef08a" opacity="0.75">',
        '<ellipse cx="445" cy="282" rx="38" ry="2.5" /><ellipse cx="445" cy="294" rx="32" ry="2.2" />',
        '<ellipse cx="445" cy="308" rx="26" ry="2" /><ellipse cx="445" cy="324" rx="20" ry="1.8" />',
        '<ellipse cx="445" cy="342" rx="15" ry="1.5" />',
        "</g>",
        # Catamaran yacht & sailboat in the lagoon
        '<g class="bob" transform="translate(495, 326)">',
        '<polygon points="-24,4 24,4 18,11 -20,11" fill="#ffffff" stroke="#0f172a" stroke-width="1" />',
        '<polygon points="-2,-34 -2,2 -18,2" fill="#fffbeb" stroke="#f59e0b" stroke-width="0.8" />',
        '<polygon points="1,-30 1,2 16,2" fill="#fef3c7" stroke="#f59e0b" stroke-width="0.8" />',
        "</g>",
        '<g class="bob" transform="translate(275, 344)">',
        '<polygon points="-28,2 28,2 21,9 -23,9" fill="#ffffff" stroke="#0f172a" stroke-width="1" />',
        '<rect x="-14" y="-4" width="22" height="6" rx="1.5" fill="#e0f2fe" stroke="#0284c7" stroke-width="0.8" />',
        "</g>",
        # Foreground Golden Sand Beach & Foaming Surf Line
        '<path d="M0,368 Q185,358 365,402 Q495,434 640,422 L640,480 L0,480 Z" fill="#ffffff" opacity="0.85" />',
        '<path d="M0,376 Q180,366 360,410 Q490,442 640,430 L640,480 L0,480 Z" fill="#f6e3ba" />',
        '<path d="M0,402 Q175,392 355,432 Q485,460 640,448 L640,480 L0,480 Z" fill="#e8c98e" />',
        # Multi-frond Coconut Palms & Luxury Beach Cabana/Parasol on Left Shore
        *draw_palm(78, 422, 2.4, 1.1),
        *draw_palm(42, 436, 1.8, -0.7),
        *draw_palm(132, 438, 1.5, 1.3),
        # Beach loungers & striped resort parasol
        '<g transform="translate(208, 434)">',
        '<ellipse cx="0" cy="8" rx="28" ry="5" fill="#bfa06a" opacity="0.45" />',
        '<line x1="0" y1="6" x2="6" y2="-28" stroke="#5c3a21" stroke-width="2.4" />',
        '<path d="M-26,-18 Q6,-42 36,-14 Z" fill="#c95a41" stroke="#fffbeb" stroke-width="1.2" />',
        '<path d="M-10,-20 Q6,-38 20,-16 Z" fill="#fffbeb" />',
        '<rect x="-24" y="2" width="20" height="5" rx="1.5" fill="#ffffff" stroke="#94a3b8" stroke-width="0.8" />',
        '<rect x="6" y="3" width="20" height="5" rx="1.5" fill="#ffffff" stroke="#94a3b8" stroke-width="0.8" />',
        "</g>",
        "</svg>",
    ]
    return "".join(o)


def build_travel_card(idx: int) -> str:
    """
    Build all 15 Luxury Hotel & Sanctuary Cards (viewBox 0 0 320 200) for travel-guide.html:
      0: Hotel President
      1: Hotel Atlantis
      2: Hotel Khalifa
      3: Starlight Grand
      4: Royal Towers Residences
      5: Paradise Islands Water Villas
      6: Ski Paradise Chalets
      7: Amazonia Canopy Lodge
      8: Copacabana Imperial Palace
      9: Aurelia Cloud Suites
      10: Laguna Azul Coral Resort
      11: Monte Rosa Sky Observatory
      12: Solaris Marina and Yacht Club
      13: Amazonia Floating River Palace
      14: Grand Riviera Palace
    """
    o = ['<svg class="ill" viewBox="0 0 320 200" preserveAspectRatio="xMidYMid slice">']
    if idx == 0:
        # 0: Hotel President — Twin royal waterfront towers with skybridge, rooftop helipad & superyacht marina
        o += [
            '<defs><linearGradient id="tgC0Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0a192f"/><stop offset="58%" stop-color="#1e3a8a"/><stop offset="100%" stop-color="#f59e0b"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC0Sky)" />',
            '<circle cx="255" cy="48" r="24" fill="#fde68a" opacity="0.85" />',
            # Twin Presidential Glass Towers & Skybridge
            '<rect x="86" y="34" width="44" height="118" fill="#0f294a" stroke="#60a5fa" stroke-width="1" />',
            '<rect x="172" y="24" width="46" height="128" fill="#0f294a" stroke="#60a5fa" stroke-width="1" />',
            '<rect x="130" y="64" width="42" height="14" fill="#1e3a8a" stroke="#fbbf24" stroke-width="1.2" />',
            '<polygon points="82,34 108,16 134,34" fill="#fbbf24" />',
            '<polygon points="168,24 195,8 222,24" fill="#fbbf24" />',
            '<line x1="195" y1="8" x2="195" y2="1" stroke="#fde68a" stroke-width="1.6" />',
            window_grid(91, 40, 34, 102, 4, 10, "#fde68a", 0.85),
            window_grid(177, 30, 36, 112, 4, 11, "#bae6fd", 0.85),
            # Waterfront promenade & superyacht harbor
            '<rect x="0" y="148" width="320" height="8" fill="#cbd5e1" />',
            '<rect x="0" y="156" width="320" height="44" fill="#0284c7" />',
            '<g fill="#fde68a" opacity="0.45"><rect x="92" y="160" width="32" height="36" /><rect x="178" y="160" width="34" height="36" /></g>',
            *draw_palm(42, 150, 0.9, 1.0), *draw_palm(274, 150, 0.95, -1.0),
            '<g class="bob" transform="translate(148, 176)"><polygon points="-28,0 28,0 20,8 -22,8" fill="#ffffff" stroke="#0f172a" stroke-width="0.9"/><rect x="-14" y="-5" width="22" height="5" rx="1.5" fill="#e0f2fe"/></g>',
        ]
    elif idx == 1:
        # 1: Hotel Atlantis — Sail-shaped twin oceanfront towers connected by royal skybridge & coral lagoon
        o += [
            '<defs><linearGradient id="tgC1Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0284c7"/><stop offset="65%" stop-color="#7dd3fc"/><stop offset="100%" stop-color="#fef3c7"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC1Sky)" />',
            '<circle cx="65" cy="46" r="22" fill="#fffbeb" opacity="0.9" />',
            # Curved sail towers & central arch bridge
            '<path d="M92,150 C92,78 118,28 142,18 L148,150 Z" fill="#0f294a" stroke="#38bdf8" stroke-width="1.2" />',
            '<path d="M228,150 C228,84 204,34 182,24 L174,150 Z" fill="#1e3a8a" stroke="#38bdf8" stroke-width="1.2" />',
            '<rect x="136" y="68" width="50" height="18" rx="3" fill="#fbbf24" stroke="#ffffff" stroke-width="1" />',
            '<path d="M144,150 L144,104 A16,18 0 0,1 176,104 L176,150 Z" fill="#bae6fd" opacity="0.6" />',
            window_grid(108, 48, 32, 92, 3, 9, "#e0f2fe", 0.82),
            window_grid(180, 52, 32, 88, 3, 9, "#fde68a", 0.82),
            # Turquoise lagoon & coral beach podium
            '<path d="M24,150 Q160,140 296,150 Z" fill="#fde68a" />',
            '<rect x="0" y="150" width="320" height="50" fill="#0ea5e9" />',
            '<ellipse cx="160" cy="172" rx="95" ry="14" fill="#2dd4bf" opacity="0.55" />',
            *draw_palm(54, 150, 0.85, 0.9), *draw_palm(266, 150, 0.85, -0.9),
        ]
    elif idx == 2:
        # 2: Hotel Khalifa — Grand Arabian-Royal palace at the apex of Palm Island with Aquaventure waterpark
        o += [
            '<defs><linearGradient id="tgC2Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1e1b4b"/><stop offset="55%" stop-color="#be185d"/><stop offset="100%" stop-color="#fbbf24"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC2Sky)" />',
            '<circle cx="160" cy="62" r="36" fill="#fef08a" opacity="0.65" />',
            # Royal Twin Palace Towers linked by Grand Moorish Keyhole Arch & Golden Domes
            '<rect x="64" y="88" width="192" height="62" fill="#d97706" stroke="#78350f" stroke-width="1" />',
            '<rect x="92" y="48" width="38" height="102" fill="#f59e0b" stroke="#78350f" stroke-width="1" />',
            '<rect x="190" y="48" width="38" height="102" fill="#f59e0b" stroke="#78350f" stroke-width="1" />',
            '<rect x="130" y="54" width="60" height="26" fill="#fbbf24" stroke="#78350f" stroke-width="1" />',
            # Central Moorish arch opening
            '<path d="M138,150 L138,104 A22,22 0 0,1 182,104 L182,150 Z" fill="#be185d" stroke="#fef08a" stroke-width="1.5" />',
            # Onion domes & spires
            '<path d="M98,48 Q111,26 124,48 Z" fill="#fef08a" /><line x1="111" y1="26" x2="111" y2="16" stroke="#fef08a" stroke-width="1.5"/>',
            '<path d="M196,48 Q209,26 222,48 Z" fill="#fef08a" /><line x1="209" y1="26" x2="209" y2="16" stroke="#fef08a" stroke-width="1.5"/>',
            '<path d="M146,54 Q160,30 174,54 Z" fill="#fef08a" /><line x1="160" y1="30" x2="160" y2="18" stroke="#fef08a" stroke-width="1.8"/>',
            window_grid(98, 56, 26, 84, 3, 7, "#fffbeb", 0.9),
            window_grid(196, 56, 26, 84, 3, 7, "#fffbeb", 0.9),
            # Waterpark slides on right & turquoise lagoon
            '<path d="M256,102 Q278,118 264,134 T292,150" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round" />',
            '<path d="M262,106 Q284,122 270,138 T298,150" fill="none" stroke="#ef4444" stroke-width="2.2" stroke-linecap="round" />',
            '<rect x="0" y="150" width="320" height="50" fill="#0284c7" />',
            '<path d="M20,150 L300,150" stroke="#fde68a" stroke-width="3" />',
            *draw_palm(38, 150, 0.8, 1.0), *draw_palm(285, 150, 0.8, -1.0),
        ]
    elif idx == 3:
        # 3: Starlight Grand — Art-Deco stepped skyscraper under starry night sky with rooftop infinity pool & searchlights
        o += [
            '<defs><linearGradient id="tgC3Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#050b14"/><stop offset="65%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e3a8a"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC3Sky)" />',
            # Searchlight beams
            '<polygon points="115,44 35,0 75,0" fill="#fde68a" opacity="0.16" />',
            '<polygon points="205,44 245,0 285,0" fill="#38bdf8" opacity="0.16" />',
            '<g fill="#ffffff"><circle cx="42" cy="28" r="1.4" class="twinkle"/><circle cx="96" cy="18" r="1.6" class="twinkle"/><circle cx="228" cy="24" r="1.5" class="twinkle"/><circle cx="282" cy="40" r="1.3" class="twinkle"/></g>',
            # Stepped Art-Deco Grand Hotel with cantilevered sky-pool
            '<rect x="78" y="96" width="164" height="68" fill="#1e293b" stroke="#fbbf24" stroke-width="1" />',
            '<rect x="102" y="56" width="116" height="108" fill="#0f172a" stroke="#fbbf24" stroke-width="1.2" />',
            '<rect x="128" y="28" width="64" height="136" fill="#1e3a8a" stroke="#fde68a" stroke-width="1.2" />',
            # Glowing cyan rooftop infinity pool
            '<rect x="92" y="50" width="136" height="7" rx="2" fill="#38bdf8" stroke="#e0f2fe" stroke-width="1" />',
            '<circle cx="160" cy="18" r="4" fill="#fbbf24" class="pulse" />',
            window_grid(134, 36, 52, 120, 4, 10, "#fde68a", 0.92),
            window_grid(106, 64, 18, 92, 2, 8, "#bae6fd", 0.85),
            window_grid(196, 64, 18, 92, 2, 8, "#bae6fd", 0.85),
            '<rect x="0" y="164" width="320" height="36" fill="#091326" />',
            '<ellipse cx="160" cy="178" rx="85" ry="8" fill="#fde68a" opacity="0.3" />',
        ]
    elif idx == 4:
        # 4: Royal Towers Residences — Three slender residential crystal towers with sky-gardens & private yacht basin
        o += [
            '<defs><linearGradient id="tgC4Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0f294a"/><stop offset="60%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#fde68a"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC4Sky)" />',
            # Three slender crystal residential towers with green sky-terraces
            '<rect x="74" y="48" width="38" height="106" fill="#1e3a8a" stroke="#93c5fd" stroke-width="1" />',
            '<rect x="140" y="24" width="42" height="130" fill="#0f294a" stroke="#93c5fd" stroke-width="1.2" />',
            '<rect x="208" y="40" width="38" height="114" fill="#1e3a8a" stroke="#93c5fd" stroke-width="1" />',
            '<polygon points="74,48 112,32 112,48" fill="#38bdf8" />',
            '<polygon points="140,24 182,8 182,24" fill="#fbbf24" />',
            '<polygon points="208,40 246,24 246,40" fill="#38bdf8" />',
            window_grid(79, 54, 28, 92, 3, 9, "#e0f2fe", 0.85),
            window_grid(145, 30, 32, 116, 3, 11, "#fde68a", 0.88),
            window_grid(213, 46, 28, 100, 3, 10, "#e0f2fe", 0.85),
            # Landscaped podium & yacht basin
            '<rect x="48" y="148" width="224" height="8" rx="2" fill="#22c55e" />',
            '<rect x="0" y="156" width="320" height="44" fill="#0284c7" />',
            *draw_palm(54, 152, 0.85, 0.8), *draw_palm(268, 152, 0.85, -0.8),
        ]
    elif idx == 5:
        # 5: Paradise Islands Water Villas — Thatch-roof overwater bungalows along a curved timber boardwalk over coral lagoon
        o += [
            '<defs><linearGradient id="tgC5Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0ea5e9"/><stop offset="50%" stop-color="#7dd3fc"/><stop offset="100%" stop-color="#fef9c3"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC5Sky)" />',
            '<rect x="0" y="96" width="320" height="104" fill="#06b6d4" />',
            '<ellipse cx="95" cy="148" rx="68" ry="22" fill="#2dd4bf" opacity="0.65" />',
            '<ellipse cx="235" cy="156" rx="72" ry="24" fill="#5eead4" opacity="0.55" />',
            # Curved timber overwater boardwalk
            '<path d="M160,200 Q145,148 215,112" fill="none" stroke="#92400e" stroke-width="8" stroke-linecap="round" />',
            '<path d="M160,200 Q145,148 215,112" fill="none" stroke="#fde68a" stroke-width="5" stroke-dasharray="3 3" />',
            # 3 Overwater thatch-roof villas on stilts with private plunge pools
            '<g transform="translate(88, 134)">',
            '<line x1="-18" y1="8" x2="-18" y2="20" stroke="#78350f" stroke-width="2" /><line x1="18" y1="8" x2="18" y2="20" stroke="#78350f" stroke-width="2" />',
            '<rect x="-26" y="4" width="52" height="6" rx="1" fill="#d97706" />',
            '<rect x="14" y="5" width="10" height="4" fill="#38bdf8" stroke="#ffffff" stroke-width="0.6" />',
            '<rect x="-18" y="-10" width="34" height="14" fill="#fef3c7" stroke="#92400e" stroke-width="0.9" />',
            '<polygon points="-26,-8 0,-26 26,-8" fill="#b45309" stroke="#fde68a" stroke-width="1" />',
            '<rect x="-8" y="-6" width="16" height="10" fill="#fde68a" />',
            "</g>",
            '<g transform="translate(228, 142)">',
            '<line x1="-20" y1="8" x2="-20" y2="22" stroke="#78350f" stroke-width="2" /><line x1="20" y1="8" x2="20" y2="22" stroke="#78350f" stroke-width="2" />',
            '<rect x="-28" y="4" width="56" height="6" rx="1" fill="#d97706" />',
            '<rect x="-20" y="-12" width="40" height="16" fill="#fef3c7" stroke="#92400e" stroke-width="0.9" />',
            '<polygon points="-30,-10 0,-30 30,-10" fill="#b45309" stroke="#fde68a" stroke-width="1" />',
            '<rect x="-10" y="-8" width="20" height="12" fill="#fde68a" />',
            "</g>",
            '<g transform="translate(178, 104) scale(0.75)">',
            '<rect x="-24" y="4" width="48" height="6" fill="#d97706" />',
            '<rect x="-16" y="-10" width="32" height="14" fill="#fef3c7" />',
            '<polygon points="-24,-8 0,-24 24,-8" fill="#b45309" stroke="#fde68a" stroke-width="1" />',
            "</g>",
            *draw_palm(28, 102, 0.85, 1.1),
        ]
    elif idx == 6:
        # 6: Ski Paradise Chalets — Warm timber-and-stone alpine chalet under snow-capped Andean peaks
        o += [
            '<defs><linearGradient id="tgC6Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0f2947"/><stop offset="62%" stop-color="#2c5e8a"/><stop offset="100%" stop-color="#f3d5a0"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC6Sky)" />',
            *draw_mountain_3d((105, 28), 120, 120, 142, "#285582", "#102a49", "#ffffff", "#cbd5e1", 0.62, seed=4.5),
            *draw_mountain_3d((235, 36), 110, 110, 142, "#326496", "#143459", "#ffffff", "#cbd5e1", 0.58, seed=8.1),
            '<path d="M0,138 Q160,126 320,140 L320,200 L0,200 Z" fill="#f1f5f9" />',
            *draw_spruce(36, 150, 1.0), *draw_spruce(62, 156, 0.85), *draw_spruce(264, 154, 0.9), *draw_spruce(288, 148, 1.05),
            '<g transform="translate(160, 132)">',
            '<rect x="20" y="-42" width="7" height="18" fill="#475569" />',
            '<rect x="-42" y="-8" width="84" height="38" fill="#6b3e1e" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="-52,-6 0,-52 52,-6" fill="#0f172a" stroke="#ffffff" stroke-width="2.4" />',
            '<polygon points="-26,-6 0,-34 26,-6" fill="#fef08a" stroke="#b45309" stroke-width="1.2" />',
            window_grid(-32, -2, 64, 26, 4, 2, "#fde68a", 0.95),
            "</g>",
        ]
    elif idx == 7:
        # 7: Amazonia Canopy Lodge — Elevated eco-luxury treehouse pavilions connected by suspension bridges in lush rainforest
        o += [
            '<defs><linearGradient id="tgC7Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#064e3b"/><stop offset="55%" stop-color="#059669"/><stop offset="100%" stop-color="#fde68a"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC7Sky)" />',
            # Sunbeams filtering through canopy mist
            '<polygon points="95,0 135,0 195,200 125,200" fill="#fef08a" opacity="0.14" />',
            '<polygon points="205,0 245,0 295,200 235,200" fill="#fef08a" opacity="0.12" />',
            # Giant Ceiba trunks & multi-layered rainforest foliage
            '<path d="M0,156 Q40,140 80,154 T160,150 T240,156 T320,148 L320,200 L0,200 Z" fill="#064e3b" />',
            '<rect x="64" y="54" width="14" height="130" fill="#451a03" />',
            '<rect x="232" y="46" width="16" height="138" fill="#451a03" />',
            # Lush emerald tree crowns
            '<ellipse cx="71" cy="48" rx="58" ry="26" fill="#14532d" /><ellipse cx="76" cy="44" rx="44" ry="18" fill="#16a34a" />',
            '<ellipse cx="240" cy="42" rx="62" ry="28" fill="#14532d" /><ellipse cx="234" cy="38" rx="46" ry="20" fill="#22c55e" />',
            '<ellipse cx="155" cy="168" rx="75" ry="22" fill="#15803d" />',
            # Rope suspension skybridge between treehouse lodges
            '<path d="M98,106 Q155,124 212,98" fill="none" stroke="#fde68a" stroke-width="2.2" />',
            '<path d="M98,98 Q155,116 212,90" fill="none" stroke="#b45309" stroke-width="1.2" />',
            # Left & Right Canopy Treehouse Lodges with warm lantern glow
            '<g transform="translate(71, 96)">',
            '<rect x="-26" y="-8" width="52" height="22" rx="2" fill="#78350f" stroke="#fbbf24" stroke-width="1" />',
            '<polygon points="-32,-8 0,-28 32,-8" fill="#92400e" stroke="#fde68a" stroke-width="1" />',
            window_grid(-20, -4, 40, 14, 3, 1, "#fef08a", 0.95),
            "</g>",
            '<g transform="translate(240, 88)">',
            '<rect x="-28" y="-8" width="56" height="24" rx="2" fill="#78350f" stroke="#fbbf24" stroke-width="1" />',
            '<polygon points="-34,-8 0,-30 34,-8" fill="#92400e" stroke="#fde68a" stroke-width="1" />',
            window_grid(-22, -4, 44, 16, 3, 1, "#fef08a", 0.95),
            "</g>",
        ]
    elif idx == 8:
        # 8: Copacabana Imperial Palace — Neoclassical white oceanfront palace with arched colonnade & iconic wave promenade
        o += [
            '<defs><linearGradient id="tgC8Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1d4ed8"/><stop offset="65%" stop-color="#93c5fd"/><stop offset="100%" stop-color="#fef3c7"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC8Sky)" />',
            # Dramatic Sugarloaf-style coastal karst peak in background
            '<path d="M215,138 Q255,28 292,138 Z" fill="#1e3a5f" opacity="0.65" />',
            # White Neoclassical Imperial Palace
            '<rect x="34" y="68" width="212" height="72" fill="#fffbeb" stroke="#d97706" stroke-width="1.2" />',
            '<rect x="96" y="48" width="88" height="92" fill="#ffffff" stroke="#d97706" stroke-width="1.2" />',
            '<polygon points="90,48 140,24 190,48" fill="#f59e0b" stroke="#fffbeb" stroke-width="1" />',
            window_grid(42, 76, 48, 36, 4, 3, "#38bdf8", 0.85),
            window_grid(104, 56, 72, 56, 5, 4, "#fbbf24", 0.9),
            window_grid(190, 76, 48, 36, 4, 3, "#38bdf8", 0.85),
            # Iconic Portuguese black-and-white wave promenade + golden beach + sea
            '<rect x="0" y="140" width="320" height="14" fill="#f8fafc" />',
            '<path d="M0,145 Q20,139 40,145 T80,145 T120,145 T160,145 T200,145 T240,145 T280,145 T320,145" fill="none" stroke="#0f172a" stroke-width="2.5" />',
            '<path d="M0,151 Q20,145 40,151 T80,151 T120,151 T160,151 T200,151 T240,151 T280,151 T320,151" fill="none" stroke="#0f172a" stroke-width="2.5" />',
            '<rect x="0" y="154" width="320" height="16" fill="#fde68a" />',
            '<rect x="0" y="170" width="320" height="30" fill="#0284c7" />',
            *draw_palm(22, 146, 0.85, 0.9), *draw_palm(272, 146, 0.85, -0.9),
        ]
    elif idx == 9:
        # 9: Aurelia Cloud Suites — Supertall Sky City pinnacle rising above a sea of sunset clouds with glass sky-pods
        o += [
            '<defs><linearGradient id="tgC9Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0f172a"/><stop offset="55%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#f97316"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC9Sky)" />',
            '<circle cx="72" cy="54" r="24" fill="#fef08a" opacity="0.85" />',
            # Supertall tapered glass tower with cantilevered sky-pods
            '<polygon points="122,200 132,96 188,96 198,200" fill="#1e3a8a" stroke="#93c5fd" stroke-width="1" />',
            '<polygon points="136,96 144,38 176,38 184,96" fill="#0f294a" stroke="#bae6fd" stroke-width="1.2" />',
            '<ellipse cx="160" cy="96" rx="38" ry="7" fill="#38bdf8" stroke="#fbbf24" stroke-width="1.4" />',
            '<ellipse cx="160" cy="58" rx="28" ry="5.5" fill="#7dd3fc" stroke="#fbbf24" stroke-width="1.2" />',
            '<line x1="160" y1="38" x2="160" y2="8" stroke="#fbbf24" stroke-width="2.2" />',
            '<circle cx="160" cy="8" r="3.5" fill="#ef4444" class="pulse" />',
            window_grid(146, 44, 28, 46, 3, 5, "#fde68a", 0.9),
            window_grid(136, 104, 48, 60, 4, 6, "#e0f2fe", 0.85),
            # Billowing sea of sunset clouds below the upper suites
            '<g fill="#fff7ed" opacity="0.92">',
            '<ellipse cx="55" cy="182" rx="68" ry="24" /><ellipse cx="145" cy="188" rx="76" ry="22" /><ellipse cx="265" cy="180" rx="72" ry="26" />',
            '<ellipse cx="95" cy="172" rx="48" ry="16" fill="#fed7aa" opacity="0.7" />',
            '<ellipse cx="215" cy="174" rx="52" ry="16" fill="#fed7aa" opacity="0.7" />',
            "</g>",
        ]
    elif idx == 10:
        # 10: Laguna Azul Coral Resort — Split-level coral reef sanctuary showing overwater pavilion & underwater reef world
        o += [
            '<defs><linearGradient id="tgC10Sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#06b6d4"/><stop offset="100%" stop-color="#0f294a"/></linearGradient></defs>',
            '<rect width="320" height="92" fill="#bae6fd" />',
            '<circle cx="268" cy="34" r="18" fill="#fef08a" />',
            # Overwater glass-floor reef pavilion
            '<rect x="98" y="64" width="124" height="28" rx="3" fill="#fffbeb" stroke="#d97706" stroke-width="1.2" />',
            '<polygon points="88,66 160,38 232,66" fill="#d97706" stroke="#fde68a" stroke-width="1" />',
            window_grid(108, 70, 104, 18, 6, 1, "#38bdf8", 0.85),
            # Split waterline & luminous underwater coral garden + underwater suite dome
            '<rect x="0" y="92" width="320" height="108" fill="url(#tgC10Sea)" />',
            '<path d="M0,92 Q80,87 160,92 T320,92" fill="none" stroke="#ffffff" stroke-width="2.5" />',
            # Submerged glass bedroom dome
            '<path d="M124,148 A36,28 0 0,1 196,148 Z" fill="#7dd3fc" opacity="0.55" stroke="#ffffff" stroke-width="1.5" />',
            '<rect x="142" y="138" width="36" height="10" rx="2" fill="#fde68a" opacity="0.9" />',
            # Vibrant coral reef formations & tropical fish
            '<path d="M0,200 L0,156 Q45,142 95,168 Q160,154 225,168 Q275,140 320,158 L320,200 Z" fill="#0f172a" opacity="0.45" />',
            '<g fill="#f43f5e"><circle cx="48" cy="166" r="14"/><circle cx="62" cy="172" r="10"/><circle cx="264" cy="164" r="15"/></g>',
            '<g fill="#f59e0b"><circle cx="82" cy="176" r="11"/><circle cx="242" cy="174" r="12"/></g>',
            '<g fill="#2dd4bf"><circle cx="32" cy="178" r="10"/><circle cx="288" cy="176" r="12"/></g>',
            '<g fill="#fde047"><polygon points="75,124 85,120 85,128"/><polygon points="225,118 215,114 215,122"/><polygon points="245,132 235,128 235,136"/></g>',
        ]
    elif idx == 11:
        # 11: Monte Rosa Sky Observatory — High-Andes astronomical dome & glass ridge suites under the Milky Way
        return build_ski_resort_card(2).replace('<svg class="ill" viewBox="0 0 320 200">', '<svg class="ill" viewBox="0 0 320 200" preserveAspectRatio="xMidYMid slice">')
    elif idx == 12:
        # 12: Solaris Marina and Yacht Club — Curved glass yacht clubhouse, lighthouse & superyachts moored at golden piers
        o += [
            '<defs><linearGradient id="tgC12Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1e3a8a"/><stop offset="55%" stop-color="#f97316"/><stop offset="100%" stop-color="#fde68a"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC12Sky)" />',
            '<circle cx="245" cy="64" r="28" fill="#fffbeb" opacity="0.9" />',
            # Curved wing-roof Yacht Clubhouse & Harbour Lighthouse
            '<path d="M28,118 Q95,78 168,114 L168,124 L28,124 Z" fill="#0f294a" stroke="#fbbf24" stroke-width="1.4" />',
            '<rect x="42" y="102" width="112" height="22" fill="#38bdf8" opacity="0.85" />',
            '<rect x="184" y="68" width="12" height="56" fill="#ffffff" stroke="#0f172a" stroke-width="0.9" />',
            '<rect x="182" y="62" width="16" height="6" fill="#ef4444" />',
            '<circle cx="190" cy="58" r="4" fill="#fef08a" class="pulse" />',
            # Marina basin & moored superyachts
            '<rect x="0" y="124" width="320" height="76" fill="#0284c7" />',
            '<rect x="0" y="122" width="215" height="6" fill="#cbd5e1" />',
            '<g class="bob" transform="translate(86, 152)"><polygon points="-38,0 38,0 28,11 -30,11" fill="#ffffff" stroke="#0f172a" stroke-width="1"/><rect x="-20" y="-7" width="32" height="7" rx="2" fill="#e0f2fe" stroke="#0284c7" stroke-width="0.8"/><rect x="-8" y="-12" width="16" height="5" rx="1" fill="#ffffff"/></g>',
            '<g class="bob" transform="translate(238, 164)"><polygon points="-44,0 44,0 32,12 -36,12" fill="#ffffff" stroke="#0f172a" stroke-width="1"/><rect x="-24" y="-8" width="38" height="8" rx="2" fill="#e0f2fe" stroke="#0284c7" stroke-width="0.8"/><rect x="-10" y="-14" width="20" height="6" rx="1.5" fill="#ffffff"/></g>',
        ]
    elif idx == 13:
        # 13: Amazonia Floating River Palace — Multi-deck glass-and-teak river cruiser anchored on the mirror-calm Amazon
        o += [
            '<defs><linearGradient id="tgC13Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#311042"/><stop offset="52%" stop-color="#c2410c"/><stop offset="100%" stop-color="#fbbf24"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC13Sky)" />',
            '<circle cx="160" cy="68" r="32" fill="#fef08a" opacity="0.85" />',
            # Lush rainforest riverbanks
            '<path d="M0,118 Q35,96 75,112 Q115,98 155,116 L320,116 L320,98 Q275,88 235,104 Q195,92 155,112 Z" fill="#064e3b" />',
            '<rect x="0" y="116" width="320" height="84" fill="#0f294a" />',
            '<ellipse cx="160" cy="156" rx="110" ry="22" fill="#f59e0b" opacity="0.28" />',
            # Multi-deck Floating River Palace
            '<g class="bob" transform="translate(160, 134)">',
            '<polygon points="-86,6 86,6 72,20 -76,20" fill="#451a03" stroke="#fbbf24" stroke-width="1.2" />',
            '<rect x="-72" y="-8" width="144" height="14" rx="2" fill="#78350f" stroke="#fde68a" stroke-width="1" />',
            '<rect x="-58" y="-22" width="116" height="14" rx="2" fill="#92400e" stroke="#fde68a" stroke-width="1" />',
            '<rect x="-36" y="-32" width="72" height="10" rx="2" fill="#b45309" stroke="#fef08a" stroke-width="1" />',
            window_grid(-66, -6, 132, 10, 10, 1, "#fef08a", 0.95),
            window_grid(-52, -20, 104, 10, 8, 1, "#fef08a", 0.95),
            # Golden water reflection
            '<rect x="-64" y="22" width="128" height="10" fill="#fde68a" opacity="0.35" />',
            "</g>",
        ]
    else:
        # 14: Grand Riviera Palace — Mediterranean-Caribbean terraced cliffside palace with cascading pools & cypress/palms
        o += [
            '<defs><linearGradient id="tgC14Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0284c7"/><stop offset="65%" stop-color="#bae6fd"/><stop offset="100%" stop-color="#fef3c7"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#tgC14Sky)" />',
            '<circle cx="265" cy="42" r="22" fill="#fef08a" opacity="0.9" />',
            # Terraced coastal headland on left
            '<path d="M0,78 L195,78 L228,154 L0,154 Z" fill="#15803d" />',
            # Grand Riviera Palace with terracotta roofs, arched loggias & cascading infinity pools
            '<rect x="32" y="42" width="136" height="44" fill="#fffbeb" stroke="#d97706" stroke-width="1.1" />',
            '<polygon points="26,42 100,18 174,42" fill="#c95a41" stroke="#fde68a" stroke-width="1" />',
            window_grid(40, 48, 120, 32, 6, 2, "#0284c7", 0.85),
            # Cascading infinity pool terraces down the cliff
            '<polygon points="48,86 184,86 194,104 42,104" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1" />',
            '<polygon points="56,90 176,90 182,100 52,100" fill="#38bdf8" />',
            '<polygon points="64,108 204,108 214,126 58,126" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1" />',
            '<polygon points="72,112 196,112 202,122 68,122" fill="#0ea5e9" />',
            '<rect x="0" y="150" width="320" height="50" fill="#0284c7" />',
            '<path d="M0,150 L232,150" stroke="#fde68a" stroke-width="4" />',
            *draw_palm(222, 150, 0.9, 1.0), *draw_palm(256, 152, 0.78, -0.8),
        ]
    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 3. INFRASTRUCTURE SVGS
# ==============================================================================
def build_infra_hero(lang: str) -> str:
    """Hero 640x480: Nova Aurelia bayfront panorama with Mega Pyramid, supertall skyline, offshore wind farm, port & maglev."""
    aria = (
        "Illustration of Nova Aurelia's maglev, port, wind farm and Mega Pyramid"
        if lang == "en"
        else "Illusztráció: Nova Aurelia maglev vonala, kikötője, szélerőműparkja és a Mega Piramis"
    )
    o = [
        f'<svg class="ill" viewBox="0 0 640 480" role="img" aria-label="{aria}">',
        "<defs>",
        '<linearGradient id="infHeroSky" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#0a192f" />',
        '<stop offset="48%" stop-color="#1e3a8a" />',
        '<stop offset="82%" stop-color="#f59e0b" />',
        '<stop offset="100%" stop-color="#fef3c7" />',
        "</linearGradient>",
        '<linearGradient id="infHeroSea" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#0369a1" />',
        '<stop offset="55%" stop-color="#0284c7" />',
        '<stop offset="100%" stop-color="#0f294a" />',
        "</linearGradient>",
        '<linearGradient id="infPyrLit" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#38bdf8" stop-opacity="0.88" />',
        '<stop offset="100%" stop-color="#1e3a8a" stop-opacity="0.95" />',
        "</linearGradient>",
        '<linearGradient id="infPyrShade" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#1e3a8a" />',
        '<stop offset="100%" stop-color="#0a192f" />',
        "</linearGradient>",
        "</defs>",
        '<rect width="640" height="480" rx="28" fill="url(#infHeroSky)" />',
        '<circle cx="515" cy="128" r="48" fill="#fef08a" opacity="0.85" />',
        # Offshore Wind Farm on right horizon (3 rotating turbines)
        '<g stroke="#e2e8f0" stroke-width="2" fill="none">',
        '<line x1="518" y1="292" x2="518" y2="218" /><line x1="564" y1="292" x2="564" y2="206" /><line x1="606" y1="292" x2="606" y2="222" />',
        "</g>",
        '<g class="spin" transform="translate(518, 218)" stroke="#ffffff" stroke-width="1.8"><line x1="0" y1="0" x2="0" y2="-22"/><line x1="0" y1="0" x2="19" y2="11"/><line x1="0" y1="0" x2="-19" y2="11"/><circle r="2.5" fill="#fbbf24"/></g>',
        '<g class="spin slow" transform="translate(564, 206)" stroke="#ffffff" stroke-width="2"><line x1="0" y1="0" x2="0" y2="-25"/><line x1="0" y1="0" x2="22" y2="12"/><line x1="0" y1="0" x2="-22" y2="12"/><circle r="2.8" fill="#fbbf24"/></g>',
        '<g class="spin" transform="translate(606, 222)" stroke="#ffffff" stroke-width="1.8"><line x1="0" y1="0" x2="0" y2="-20"/><line x1="0" y1="0" x2="17" y2="10"/><line x1="0" y1="0" x2="-17" y2="10"/><circle r="2.5" fill="#fbbf24"/></g>',
        # Supertall Skyline of Nova Aurelia (x=35..345, base y=292)
        # Miapolis (x=52..92)
        '<polygon points="52,292 58,195 64,132 70,84 76,84 82,132 88,195 94,292" fill="#1e3a8a" stroke="#60a5fa" stroke-width="1" />',
        '<path d="M56,260 L90,210 M58,210 L86,160 M62,160 L82,115" stroke="#93c5fd" stroke-width="0.9" opacity="0.7" />',
        # Sky City (x=112..148, pinnacle y=46)
        '<polygon points="112,292 118,200 123,138 127,82 133,82 137,138 142,200 148,292" fill="#0f294a" stroke="#93c5fd" stroke-width="1.1" />',
        '<line x1="130" y1="82" x2="130" y2="46" stroke="#fbbf24" stroke-width="2.2" />',
        '<circle cx="130" cy="46" r="3.5" fill="#ef4444" class="pulse" />',
        window_grid(122, 92, 16, 185, 2, 16, "#bae6fd", 0.8),
        # Princess Tower (x=166..196)
        '<rect x="166" y="114" width="30" height="178" fill="#172554" stroke="#60a5fa" stroke-width="1" />',
        '<path d="M166,114 A15,12 0 0,1 196,114 Z" fill="#fbbf24" />',
        '<line x1="181" y1="102" x2="181" y2="86" stroke="#fbbf24" stroke-width="1.8" />',
        window_grid(170, 122, 22, 160, 3, 14, "#fde68a", 0.85),
        # Royal Clock Tower (x=212..252)
        '<rect x="216" y="142" width="32" height="150" fill="#0f294a" stroke="#fbbf24" stroke-width="1" />',
        '<rect x="213" y="116" width="38" height="28" rx="2" fill="#fef3c7" stroke="#d97706" stroke-width="1.2" />',
        '<circle cx="232" cy="130" r="9" fill="#fbbf24" stroke="#0f172a" stroke-width="1.2" />',
        '<path d="M232,130 L232,124 M232,130 L237,130" stroke="#0f172a" stroke-width="1.4" />',
        '<polygon points="213,116 232,92 251,116" fill="#0f294a" stroke="#fbbf24" stroke-width="1" />',
        window_grid(220, 150, 24, 132, 3, 11, "#fde68a", 0.85),
        # Mega Pyramid City (x=265..475, apex at 370, 134)
        '<polygon points="265,292 370,134 370,292" fill="url(#infPyrShade)" stroke="#60a5fa" stroke-width="1.1" />',
        '<polygon points="370,134 475,292 370,292" fill="url(#infPyrLit)" stroke="#bae6fd" stroke-width="1.1" />',
        # Diagrid structural lattice & sky-garden terraces on Mega Pyramid
        '<g stroke="#93c5fd" stroke-width="0.9" opacity="0.65">',
        '<line x1="335" y1="186" x2="405" y2="186" /><line x1="305" y1="232" x2="435" y2="232" /><line x1="280" y1="268" x2="460" y2="268" />',
        '<line x1="370" y1="134" x2="315" y2="292" /><line x1="370" y1="134" x2="425" y2="292" />',
        "</g>",
        '<polygon points="362,146 370,134 378,146" fill="#fbbf24" />',
        # Deepwater Harbour & Container Port on Left Shore
        '<rect x="0" y="292" width="640" height="188" fill="url(#infHeroSea)" />',
        '<rect x="0" y="286" width="505" height="8" fill="#cbd5e1" />',
        # Port Gantry Cranes & Container Ship
        '<g stroke="#f97316" stroke-width="2" fill="none">',
        '<path d="M26,286 L26,248 L58,248 M36,286 L36,248" />',
        '<path d="M68,286 L68,248 L100,248 M78,286 L78,248" />',
        "</g>",
        '<g class="bob" transform="translate(115, 326)">',
        '<polygon points="-58,4 58,4 48,18 -50,18" fill="#0f172a" stroke="#cbd5e1" stroke-width="1" />',
        '<rect x="-42" y="-6" width="16" height="10" fill="#ef4444" /><rect x="-24" y="-6" width="16" height="10" fill="#3b82f6" />',
        '<rect x="-6" y="-6" width="16" height="10" fill="#eab308" /><rect x="12" y="-6" width="16" height="10" fill="#22c55e" />',
        '<rect x="30" y="-12" width="14" height="16" fill="#f8fafc" />',
        "</g>",
        # Foreground Cable-Stayed Maglev Sea Viaduct & High-Speed Maglev Train
        '<g stroke="#94a3b8" stroke-width="1.2" opacity="0.75">',
        '<line x1="185" y1="312" x2="95" y2="392" /><line x1="185" y1="324" x2="125" y2="394" />',
        '<line x1="185" y1="312" x2="275" y2="402" /><line x1="185" y1="324" x2="245" y2="400" />',
        '<line x1="455" y1="318" x2="365" y2="406" /><line x1="455" y1="330" x2="395" y2="408" />',
        '<line x1="455" y1="318" x2="545" y2="402" /><line x1="455" y1="330" x2="515" y2="404" />',
        "</g>",
        # Twin bridge towers & piers
        '<g fill="#cbd5e1" stroke="#475569" stroke-width="1">',
        '<rect x="180" y="302" width="10" height="145" rx="2" />',
        '<rect x="450" y="308" width="10" height="142" rx="2" />',
        "</g>",
        # Curved Viaduct Deck
        '<path d="M0,388 Q320,418 640,392 L640,406 Q320,432 0,402 Z" fill="#e2e8f0" stroke="#475569" stroke-width="1.2" />',
        '<path d="M0,395 Q320,425 640,399" fill="none" stroke="#38bdf8" stroke-width="2" stroke-dasharray="10 8" class="dash" />',
        # Aerodynamic White-and-Gold Maglev Train Gliding Across Viaduct
        '<g transform="translate(310, 396) rotate(1.5)">',
        '<path d="M-95,2 L72,2 C88,2 98,6 102,10 L-95,10 Z" fill="#ffffff" stroke="#0f294a" stroke-width="1" />',
        '<path d="M-92,5 L84,5" stroke="#0284c7" stroke-width="2.4" stroke-dasharray="6 3" />',
        '<path d="M-95,8.5 L98,8.5" stroke="#fbbf24" stroke-width="1.5" />',
        "</g>",
        "</svg>",
    ]
    return "".join(o)


def build_infra_height_chart(lang: str) -> str:
    """Tallest Structures Height Comparison Chart (viewBox 0 0 1120 420) with 10 architectural silhouettes."""
    aria = (
        "Height comparison of Waikiki's tallest structures"
        if lang == "en"
        else "Waikiki legmagasabb építményeinek magasság-összehasonlítása"
    )
    ref_word = "reference" if lang == "en" else "viszonyítás"
    m_1000 = "~1,000 m" if lang == "en" else "~1000 m"
    burj_name = "Burj Khalifa" if lang == "en" else "Burdzs Kalifa"
    princess_1, princess_2 = ("Princess", "Tower")
    exchange_name = "Exchange Tower"
    clock_1, clock_2 = ("Royal", "Clock Tower") if lang == "en" else ("Királyi", "Óratorony")
    pyramid_name = "Mega Pyramid" if lang == "en" else "Mega Piramis"
    eiffel_name = "Eiffel Tower" if lang == "en" else "Eiffel-torony"

    o = [
        f'<svg class="ill height-chart" data-reveal="fade" viewBox="0 0 1120 420" role="img" aria-label="{aria}">',
        '<g class="k-line" stroke-width="1">',
        '<path d="M30 70H1090M30 140H1090M30 210H1090M30 280H1090" stroke-dasharray="3 6" />',
        "</g>",
        '<g font-size="9" class="h-name h-ref">',
        '<text x="30" y="66">1000 m</text>',
        '<text x="30" y="136">750 m</text>',
        '<text x="30" y="206">500 m</text>',
        '<text x="30" y="276">250 m</text>',
        "</g>",
        # 0: Miapolis (~1,000 m) — Proposed Megatall Diagrid Bionic Spire
        '<g class="tower" style="--d:0">',
        '<polygon points="74,350 78,240 84,170 90,110 96,70 104,70 110,110 116,170 122,240 126,350" fill="#1e3a8a" fill-opacity="0.45" stroke="#60a5fa" stroke-width="1.5" stroke-dasharray="5 3" />',
        '<path d="M78,320 L122,260 M80,260 L120,200 M84,200 L116,140 M90,140 L110,85 M122,320 L78,260 M120,260 L80,200 M116,200 L84,140 M110,140 L90,85" stroke="#93c5fd" stroke-width="0.9" opacity="0.75" />',
        '<line x1="100" y1="70" x2="100" y2="58" stroke="#fbbf24" stroke-width="1.8" stroke-dasharray="2 2" />',
        "</g>",
        f'<text class="h-val" x="100" y="52" text-anchor="middle">{m_1000}</text>',
        '<text class="h-name" x="100" y="374" text-anchor="middle">Miapolis*</text>',
        # 1: Sky City (956 m) — Tiered Supertall Spire with Sky-Lobbies
        '<g class="tower" style="--d:1">',
        '<polygon points="181,350 185,250 190,250 193,180 198,180 201,122 204,82 206,82 209,122 212,180 217,180 220,250 225,250 229,350" fill="#1d4ed8" stroke="#93c5fd" stroke-width="1.1" />',
        '<rect x="185" y="248" width="40" height="4" fill="#fbbf24" />',
        '<rect x="193" y="178" width="24" height="3.5" fill="#fbbf24" />',
        '<rect x="200" y="120" width="10" height="3" fill="#fbbf24" />',
        '<line x1="205" y1="82" x2="205" y2="64" stroke="#fbbf24" stroke-width="2.2" />',
        '<circle cx="205" cy="64" r="2.5" fill="#ef4444" />',
        '<path d="M205,82 L205,350" stroke="#e0f2fe" stroke-width="0.9" opacity="0.6" />',
        "</g>",
        '<text class="h-val" x="205" y="52" text-anchor="middle">956 m</text>',
        '<text class="h-name" x="205" y="374" text-anchor="middle">Sky City</text>',
        # 2: Burj Khalifa (828 m reference) — Stepped Y-plan reference silhouette
        '<g class="tower" style="--d:2">',
        '<polygon points="288,350 291,285 295,285 298,230 302,230 305,178 308,140 310,118 312,140 315,178 318,230 322,230 325,285 329,285 332,350" class="f-sand" stroke="#94a3b8" stroke-width="0.9" />',
        '<line x1="310" y1="118" x2="310" y2="350" stroke="#64748b" stroke-width="0.8" opacity="0.6" />',
        "</g>",
        '<text class="h-val h-ref" x="310" y="104" text-anchor="middle">828 m</text>',
        f'<text class="h-name h-ref" x="310" y="374" text-anchor="middle">{burj_name}</text>',
        f'<text class="h-name h-ref" x="310" y="388" text-anchor="middle" font-size="8.5">{ref_word}</text>',
        # 3: Princess Tower (720 m) — Slender Residential Supertall with Crown Dome & Finial
        '<g class="tower" style="--d:3">',
        '<polygon points="396,350 398,225 402,225 404,175 408,152 422,152 426,175 428,225 432,225 434,350" fill="#1e40af" stroke="#93c5fd" stroke-width="1.1" />',
        '<path d="M406,152 C406,138 424,138 424,152 Z" fill="#fbbf24" stroke="#fef08a" stroke-width="1" />',
        '<line x1="415" y1="140" x2="415" y2="128" stroke="#fbbf24" stroke-width="2" />',
        '<path d="M400,295 H430 M400,255 H430 M402,215 H428 M404,180 H426" stroke="#60a5fa" stroke-width="1" opacity="0.7" />',
        "</g>",
        '<text class="h-val" x="415" y="118" text-anchor="middle">720 m</text>',
        f'<text class="h-name" x="415" y="374" text-anchor="middle">{princess_1}</text>',
        f'<text class="h-name" x="415" y="390" text-anchor="middle">{princess_2}</text>',
        # 4: Exchange Tower (650 m) — Faceted Obelisk Financial Center with Diamond Crown
        '<g class="tower" style="--d:4">',
        '<polygon points="500,350 502,225 510,190 520,174 530,190 538,225 540,350" fill="#1e3a8a" stroke="#60a5fa" stroke-width="1.1" />',
        '<polygon points="510,190 520,174 530,190 520,206" fill="#38bdf8" stroke="#fbbf24" stroke-width="1" />',
        '<line x1="520" y1="174" x2="520" y2="152" stroke="#fbbf24" stroke-width="2" />',
        '<line x1="520" y1="206" x2="520" y2="350" stroke="#fbbf24" stroke-width="1" opacity="0.65" />',
        "</g>",
        '<text class="h-val" x="520" y="140" text-anchor="middle">650 m</text>',
        f'<text class="h-name" x="520" y="374" text-anchor="middle">{exchange_name}</text>',
        # 5: Hotel Atlantis (600 m) — Triple-Sail Oceanfront Resort Complex with Skybridge
        '<g class="tower" style="--d:5">',
        '<path d="M610,350 C610,255 616,198 625,180 L629,350 Z" fill="#0284c7" stroke="#bae6fd" stroke-width="1" />',
        '<path d="M632,350 C632,272 637,228 643,214 L646,350 Z" fill="#0ea5e9" stroke="#bae6fd" stroke-width="0.9" />',
        '<path d="M600,350 C600,292 604,258 608,248 L608,350 Z" fill="#38bdf8" />',
        '<rect x="621" y="238" width="18" height="6" rx="1.5" fill="#fbbf24" stroke="#ffffff" stroke-width="0.8" />',
        "</g>",
        '<text class="h-val" x="625" y="168" text-anchor="middle">600 m</text>',
        '<text class="h-name" x="625" y="374" text-anchor="middle">Hotel</text>',
        '<text class="h-name" x="625" y="390" text-anchor="middle">Atlantis</text>',
        # 6: Royal Clock Tower (580 m) — Classical Ensemble with Illuminated Golden Clock Face
        '<g class="tower" style="--d:6">',
        '<rect x="676" y="278" width="16" height="72" fill="#1e3a8a" stroke="#60a5fa" stroke-width="0.8" />',
        '<polygon points="674,278 684,264 694,278" fill="#fbbf24" />',
        '<rect x="695" y="244" width="18" height="106" fill="#1d4ed8" stroke="#60a5fa" stroke-width="0.9" />',
        '<polygon points="693,244 704,226 715,244" fill="#fbbf24" />',
        '<rect x="716" y="240" width="28" height="110" fill="#1e3a8a" stroke="#93c5fd" stroke-width="1" />',
        '<rect x="712" y="206" width="36" height="34" rx="2" fill="#fef3c7" stroke="#d97706" stroke-width="1.2" />',
        '<circle cx="730" cy="223" r="10" fill="#fbbf24" stroke="#0f172a" stroke-width="1.2" />',
        '<path d="M730,223 V217 M730,223 H734" stroke="#0f172a" stroke-width="1.4" />',
        '<polygon points="712,206 730,186 748,206" fill="#1d4ed8" stroke="#fbbf24" stroke-width="1.2" />',
        '<line x1="730" y1="186" x2="730" y2="172" stroke="#fbbf24" stroke-width="2" />',
        '<rect x="747" y="244" width="18" height="106" fill="#1d4ed8" stroke="#60a5fa" stroke-width="0.9" />',
        '<polygon points="745,244 756,226 767,244" fill="#fbbf24" />',
        '<rect x="768" y="278" width="16" height="72" fill="#1e3a8a" stroke="#60a5fa" stroke-width="0.8" />',
        '<polygon points="766,278 776,264 786,278" fill="#fbbf24" />',
        "</g>",
        '<text class="h-val" x="730" y="160" text-anchor="middle">580 m</text>',
        f'<text class="h-name" x="730" y="374" text-anchor="middle">{clock_1}</text>',
        f'<text class="h-name" x="730" y="390" text-anchor="middle">{clock_2}</text>',
        # 7: Infinity Tower (480 m) — 90-Degree Helical Twisting Glass Tower
        '<g class="tower" style="--d:7">',
        '<path d="M819,350 C821,300 825,255 829,214 L841,214 C845,255 849,300 851,350 Z" fill="#1e40af" stroke="#93c5fd" stroke-width="1.1" />',
        '<path d="M819,350 C838,300 842,255 829,214" fill="none" stroke="#fbbf24" stroke-width="1.8" />',
        '<path d="M851,350 C832,300 828,255 841,214" fill="none" stroke="#38bdf8" stroke-width="1.6" />',
        '<rect x="828" y="210" width="14" height="4" rx="1" fill="#fbbf24" />',
        "</g>",
        '<text class="h-val" x="835" y="198" text-anchor="middle">480 m</text>',
        '<text class="h-name" x="835" y="374" text-anchor="middle">Infinity Tower</text>',
        # 8: Mega Pyramid City (450 m) — Faceted Glass Arcology Pyramid with Diagrid
        '<g class="tower" style="--d:8">',
        '<polygon points="912,350 945,224 945,350" fill="#1e3a8a" stroke="#60a5fa" stroke-width="1" />',
        '<polygon points="945,224 978,350 945,350" fill="#38bdf8" fill-opacity="0.78" stroke="#bae6fd" stroke-width="1" />',
        '<path d="M922,312 H968 M932,274 H958 M945,224 L928,350 M945,224 L962,350" stroke="#e0f2fe" stroke-width="0.9" opacity="0.7" />',
        '<polygon points="941,238 945,224 949,238" fill="#fbbf24" />',
        "</g>",
        '<text class="h-val" x="945" y="210" text-anchor="middle">450 m</text>',
        f'<text class="h-name" x="945" y="374" text-anchor="middle">{pyramid_name}</text>',
        # 9: Eiffel Tower (330 m reference) — Lattice Iron Reference Silhouette
        '<g class="tower" style="--d:9">',
        '<polygon points="1038,350 1046,310 1064,310 1072,350 1065,350 1060,315 1050,315 1045,350" class="f-sand" />',
        '<path d="M1045,350 Q1055,328 1065,350" class="k-line" stroke-width="1.2" fill="none" />',
        '<rect x="1044" y="306" width="22" height="4" class="f-sand" />',
        '<polygon points="1047,306 1052,282 1058,282 1063,306" class="f-sand" />',
        '<rect x="1050" y="278" width="10" height="4" class="f-sand" />',
        '<polygon points="1053,278 1055,256 1057,278" class="f-sand" />',
        "</g>",
        '<text class="h-val h-ref" x="1055" y="244" text-anchor="middle">330 m</text>',
        f'<text class="h-name h-ref" x="1055" y="374" text-anchor="middle">{eiffel_name}</text>',
        f'<text class="h-name h-ref" x="1055" y="388" text-anchor="middle" font-size="8.5">{ref_word}</text>',
        '<path d="M20 350H1100" class="k-ink" stroke-width="2" />',
        "</svg>",
    ]
    return "".join(o)



def build_infra_card(idx: int) -> str:
    """
    Build all 10 Landmark Architecture & Transport Cards (viewBox 0 0 320 200) for infrastructure.html:
      0: Sky City (956 m)
      1: Princess Tower (720 m)
      2: Commercial Center / Exchange Tower (650 m)
      3: Hotel Atlantis (600 m)
      4: Royal Clock Tower (580 m)
      5: Infinity Tower (480 m)
      6: Mega Pyramid City (450 m)
      7: Miapolis (~1,000 m)
      8: Ducal Palace
      9: Nova Aurelia Airport
    """
    o = ['<svg class="ill" viewBox="0 0 320 200" preserveAspectRatio="xMidYMid slice">']
    if idx == 0:
        # 0: Sky City (956 m) — Supertall tiered glass needle piercing golden-hour clouds above waterfront fountain plaza
        o += [
            '<defs><linearGradient id="infC0Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#071326"/><stop offset="55%" stop-color="#1e3a8a"/><stop offset="100%" stop-color="#f59e0b"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#infC0Sky)" />',
            '<circle cx="248" cy="56" r="26" fill="#fef08a" opacity="0.85" />',
            # Flanking skyline silhouettes
            '<rect x="44" y="108" width="28" height="58" fill="#0f294a" opacity="0.75" />',
            '<rect x="242" y="114" width="32" height="52" fill="#0f294a" opacity="0.75" />',
            # Sky City 956m tiered supertall needle
            '<polygon points="124,166 130,118 190,118 196,166" fill="#1e3a8a" stroke="#93c5fd" stroke-width="1" />',
            '<polygon points="134,118 140,76 180,76 186,118" fill="#1d4ed8" stroke="#93c5fd" stroke-width="1" />',
            '<polygon points="143,76 149,40 171,40 177,76" fill="#2563eb" stroke="#bae6fd" stroke-width="1.1" />',
            '<polygon points="152,40 157,18 163,18 168,40" fill="#38bdf8" stroke="#ffffff" stroke-width="1" />',
            '<line x1="160" y1="18" x2="160" y2="3" stroke="#fbbf24" stroke-width="2" />',
            '<circle cx="160" cy="3" r="3" fill="#ef4444" class="pulse" />',
            window_grid(136, 122, 48, 40, 4, 4, "#fde68a", 0.85),
            window_grid(143, 80, 34, 34, 3, 4, "#e0f2fe", 0.85),
            window_grid(150, 44, 20, 28, 2, 3, "#fde68a", 0.9),
            # High-altitude cloud band drifting past mid-tower
            '<g fill="#fff7ed" opacity="0.55"><ellipse cx="115" cy="84" rx="36" ry="7"/><ellipse cx="208" cy="72" rx="34" ry="6"/></g>',
            # Waterfront reflecting lagoon & dancing fountain jets
            '<rect x="0" y="166" width="320" height="34" fill="#0284c7" />',
            '<path d="M115,166 Q125,146 135,166 M148,166 Q160,140 172,166 M185,166 Q195,146 205,166" fill="none" stroke="#e0f2fe" stroke-width="1.6" />',
        ]
    elif idx == 1:
        # 1: Princess Tower (720 m) — Slender luxury residential supertall with ornate golden crown dome & palm boulevard
        o += [
            '<defs><linearGradient id="infC1Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0f294a"/><stop offset="60%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#fde68a"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#infC1Sky)" />',
            '<rect x="64" y="112" width="34" height="54" fill="#1e3a8a" opacity="0.65" />',
            '<rect x="224" y="104" width="36" height="62" fill="#1e3a8a" opacity="0.65" />',
            # Princess Tower shaft, balcony bands & ornate golden crown dome
            '<rect x="130" y="42" width="60" height="124" fill="#172554" stroke="#93c5fd" stroke-width="1.2" />',
            '<rect x="136" y="32" width="48" height="10" fill="#1e40af" stroke="#fbbf24" stroke-width="1" />',
            '<path d="M136,32 C136,12 184,12 184,32 Z" fill="#fbbf24" stroke="#fffbeb" stroke-width="1.2" />',
            '<line x1="160" y1="16" x2="160" y2="4" stroke="#fbbf24" stroke-width="2" />',
            '<circle cx="160" cy="4" r="2.8" fill="#fef08a" class="pulse" />',
            window_grid(136, 48, 48, 110, 4, 11, "#e0f2fe", 0.88),
            '<rect x="0" y="166" width="320" height="34" fill="#0369a1" />',
            *draw_palm(48, 166, 0.85, 0.9), *draw_palm(272, 166, 0.85, -0.9),
        ]
    elif idx == 2:
        # 2: Commercial Center / Exchange Tower (650 m) — Faceted diamond-crown financial obelisk with trading floor atrium
        o += [
            '<defs><linearGradient id="infC2Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#091526"/><stop offset="60%" stop-color="#1e3a8a"/><stop offset="100%" stop-color="#38bdf8"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#infC2Sky)" />',
            # Faceted obelisk tower with illuminated diamond crown
            '<polygon points="116,168 122,52 160,24 198,52 204,168" fill="#0f294a" stroke="#60a5fa" stroke-width="1.2" />',
            '<polygon points="160,24 198,52 204,168 160,168" fill="#1e3a8a" opacity="0.85" />',
            '<polygon points="136,52 160,24 184,52 160,72" fill="#38bdf8" stroke="#fbbf24" stroke-width="1.4" />',
            '<line x1="160" y1="24" x2="160" y2="6" stroke="#fbbf24" stroke-width="2.2" />',
            window_grid(130, 76, 60, 84, 5, 8, "#fde68a", 0.88),
            # Financial Plaza Podium
            '<rect x="76" y="152" width="168" height="16" rx="2" fill="#1e293b" stroke="#fbbf24" stroke-width="1" />',
            '<rect x="0" y="168" width="320" height="32" fill="#0f172a" />',
        ]
    elif idx == 3:
        # 3: Hotel Atlantis (600 m) — Reuse high-detail triple-sail oceanfront resort illustration
        return build_travel_card(1)
    elif idx == 4:
        # 4: Royal Clock Tower (580 m) — Grand classical ensemble with 40m illuminated golden clock faces & flanking spires
        o += [
            '<defs><linearGradient id="infC4Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0a192f"/><stop offset="55%" stop-color="#1e3a8a"/><stop offset="100%" stop-color="#f59e0b"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#infC4Sky)" />',
            # Flanking companion towers
            '<rect x="56" y="106" width="28" height="62" fill="#172554" stroke="#60a5fa" stroke-width="0.9" />',
            '<polygon points="52,106 70,86 88,106" fill="#fbbf24" />',
            '<rect x="88" y="82" width="32" height="86" fill="#1e3a8a" stroke="#60a5fa" stroke-width="1" />',
            '<polygon points="84,82 104,60 124,82" fill="#fbbf24" />',
            '<rect x="200" y="82" width="32" height="86" fill="#1e3a8a" stroke="#60a5fa" stroke-width="1" />',
            '<polygon points="196,82 216,60 236,82" fill="#fbbf24" />',
            '<rect x="236" y="106" width="28" height="62" fill="#172554" stroke="#60a5fa" stroke-width="0.9" />',
            '<polygon points="232,106 250,86 268,106" fill="#fbbf24" />',
            # Central 580m Royal Clock Tower
            '<rect x="124" y="68" width="72" height="100" fill="#0f294a" stroke="#fbbf24" stroke-width="1.2" />',
            '<rect x="118" y="34" width="84" height="36" rx="3" fill="#fef3c7" stroke="#d97706" stroke-width="1.5" />',
            '<circle cx="160" cy="52" r="14" fill="#fbbf24" stroke="#0f172a" stroke-width="1.5" />',
            '<circle cx="160" cy="52" r="11" fill="#fffbeb" />',
            '<path d="M160,52 V43 M160,52 L167,52" stroke="#0f172a" stroke-width="1.8" stroke-linecap="round" />',
            '<polygon points="118,34 160,12 202,34" fill="#0f294a" stroke="#fbbf24" stroke-width="1.2" />',
            '<line x1="160" y1="12" x2="160" y2="2" stroke="#fbbf24" stroke-width="2.2" />',
            window_grid(132, 76, 56, 84, 4, 7, "#fde68a", 0.9),
            window_grid(92, 88, 24, 72, 2, 6, "#bae6fd", 0.8),
            window_grid(204, 88, 24, 72, 2, 6, "#bae6fd", 0.8),
            '<rect x="0" y="168" width="320" height="32" fill="#0284c7" />',
        ]
    elif idx == 5:
        # 5: Infinity Tower (480 m) — Helical 90-degree twisting glass tower with curved structural ribbons
        o += [
            '<defs><linearGradient id="infC5Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#071326"/><stop offset="60%" stop-color="#1d4ed8"/><stop offset="100%" stop-color="#7dd3fc"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#infC5Sky)" />',
            # Helical twisting body & sine-wave structural ribs
            '<path d="M118,168 C122,120 132,72 126,20 L194,20 C188,72 198,120 202,168 Z" fill="#1e3a8a" stroke="#93c5fd" stroke-width="1.2" />',
            '<path d="M118,168 C178,120 188,72 126,20" fill="none" stroke="#fbbf24" stroke-width="2.5" />',
            '<path d="M202,168 C142,120 132,72 194,20" fill="none" stroke="#38bdf8" stroke-width="2.5" />',
            '<path d="M140,168 C185,120 165,72 148,20" fill="none" stroke="#e0f2fe" stroke-width="1.2" opacity="0.75" />',
            # Horizontal floorplates rotating with height
            '<g stroke="#bae6fd" stroke-width="1" opacity="0.65">',
            '<line x1="126" y1="36" x2="192" y2="36" /><line x1="128" y1="54" x2="190" y2="54" />',
            '<line x1="129" y1="72" x2="191" y2="72" /><line x1="127" y1="90" x2="193" y2="90" />',
            '<line x1="125" y1="108" x2="195" y2="108" /><line x1="122" y1="126" x2="198" y2="126" />',
            '<line x1="120" y1="144" x2="200" y2="144" />',
            "</g>",
            '<rect x="124" y="15" width="72" height="5" rx="1.5" fill="#fbbf24" />',
            '<rect x="0" y="168" width="320" height="32" fill="#0f294a" />',
        ]
    elif idx == 6:
        # 6: Mega Pyramid City (450 m) — Monumental glass-and-steel arcology pyramid with diagrid & sky-gardens
        o += [
            '<defs><linearGradient id="infC6Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0f172a"/><stop offset="58%" stop-color="#2563eb"/><stop offset="100%" stop-color="#fde68a"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#infC6Sky)" />',
            '<circle cx="255" cy="48" r="24" fill="#fffbeb" opacity="0.9" />',
            # 3D Faceted Mega Pyramid (apex at 160, 22; base y=162, x=28..292)
            '<polygon points="28,162 160,22 160,162" fill="#1e3a8a" stroke="#60a5fa" stroke-width="1.2" />',
            '<polygon points="160,22 292,162 160,162" fill="#38bdf8" fill-opacity="0.82" stroke="#e0f2fe" stroke-width="1.2" />',
            # Diagrid structural lattice & verdant sky-garden terraces
            '<g stroke="#bae6fd" stroke-width="1" opacity="0.7">',
            '<line x1="118" y1="66" x2="202" y2="66" /><line x1="84" y1="102" x2="236" y2="102" /><line x1="52" y1="136" x2="268" y2="136" />',
            '<line x1="160" y1="22" x2="94" y2="162" /><line x1="160" y1="22" x2="226" y2="162" />',
            "</g>",
            '<rect x="86" y="100" width="148" height="4" fill="#22c55e" />',
            '<rect x="54" y="134" width="212" height="4" fill="#22c55e" />',
            '<polygon points="150,34 160,22 170,34" fill="#fbbf24" />',
            '<rect x="0" y="162" width="320" height="38" fill="#0284c7" />',
        ]
    elif idx == 7:
        # 7: Miapolis (~1,000 m) — Proposed kilometer-high bionic megatall city-within-a-city with blueprint grid
        o += [
            '<defs><linearGradient id="infC7Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#050d1a"/><stop offset="60%" stop-color="#172554"/><stop offset="100%" stop-color="#1e40af"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#infC7Sky)" />',
            # Architectural blueprint coordinate grid
            '<g stroke="#3b82f6" stroke-width="0.5" opacity="0.28">',
            '<path d="M0,40 H320 M0,80 H320 M0,120 H320 M0,160 H320 M64,0 V200 M128,0 V200 M192,0 V200 M256,0 V200" />',
            "</g>",
            # Bionic tapered megatall with external diagrid exoskeleton
            '<polygon points="104,172 114,118 124,72 136,28 184,28 196,72 206,118 216,172" fill="#1e3a8a" fill-opacity="0.55" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="6 3" />',
            '<path d="M108,162 L208,122 M114,122 L200,82 M122,82 L190,42 M212,162 L112,122 M206,122 L120,82 M198,82 L130,42" stroke="#7dd3fc" stroke-width="1.1" opacity="0.8" />',
            '<line x1="160" y1="28" x2="160" y2="6" stroke="#fbbf24" stroke-width="2" stroke-dasharray="3 2" />',
            '<circle cx="160" cy="6" r="3.5" fill="#fbbf24" class="pulse" />',
            '<rect x="0" y="172" width="320" height="28" fill="#091526" />',
        ]
    elif idx == 8:
        # 8: Ducal Palace — Classical sovereign palace with colonnade, central rotunda dome, royal standard & gardens
        o += [
            '<defs><linearGradient id="infC8Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1e3a8a"/><stop offset="65%" stop-color="#93c5fd"/><stop offset="100%" stop-color="#fef3c7"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#infC8Sky)" />',
            # Golden Rotunda Dome & Sovereign Flag
            '<path d="M122,68 A38,32 0 0,1 198,68 Z" fill="#fbbf24" stroke="#fffbeb" stroke-width="1.4" />',
            '<line x1="160" y1="36" x2="160" y2="16" stroke="#fbbf24" stroke-width="1.8" />',
            '<rect x="160" y="16" width="16" height="10" rx="1" fill="#ef4444" stroke="#fde68a" stroke-width="0.8" />',
            # Neoclassical Palace Wings, Portico Pediment & Marble Columns
            '<rect x="36" y="68" width="248" height="76" fill="#fffbeb" stroke="#d97706" stroke-width="1.2" />',
            '<polygon points="104,68 160,42 216,68" fill="#fef3c7" stroke="#d97706" stroke-width="1.4" />',
            # Colonnade pillars
            '<g fill="#ffffff" stroke="#cbd5e1" stroke-width="0.9">',
            '<rect x="114" y="68" width="6" height="76" /><rect x="132" y="68" width="6" height="76" />',
            '<rect x="150" y="68" width="6" height="76" /><rect x="164" y="68" width="6" height="76" />',
            '<rect x="182" y="68" width="6" height="76" /><rect x="200" y="68" width="6" height="76" />',
            "</g>",
            window_grid(44, 78, 60, 56, 4, 3, "#1e3a8a", 0.85),
            window_grid(216, 78, 60, 56, 4, 3, "#1e3a8a", 0.85),
            # Manicured Emerald Palace Gardens & Reflecting Fountain Basin
            '<rect x="0" y="144" width="320" height="56" fill="#15803d" />',
            '<polygon points="118,144 202,144 228,200 92,200" fill="#fde68a" />',
            '<ellipse cx="160" cy="172" rx="34" ry="10" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />',
            '<path d="M160,172 Q154,154 146,166 M160,172 Q166,154 174,166 M160,172 V150" fill="none" stroke="#ffffff" stroke-width="1.6" />',
            *draw_palm(26, 152, 0.85, 0.8), *draw_palm(294, 152, 0.85, -0.8),
        ]
    else:
        # 9: Nova Aurelia Airport — Sweeping gull-wing glass terminal, air-traffic control tower, runway & jetliner taking off
        o += [
            '<defs><linearGradient id="infC9Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0f294a"/><stop offset="55%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#fde68a"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#infC9Sky)" />',
            # Air Traffic Control Tower on right
            '<rect x="248" y="44" width="8" height="96" fill="#e2e8f0" stroke="#475569" stroke-width="0.9" />',
            '<polygon points="236,44 268,44 262,28 242,28" fill="#0284c7" stroke="#ffffff" stroke-width="1.2" />',
            '<rect x="240" y="24" width="24" height="4" rx="1" fill="#ffffff" />',
            '<line x1="252" y1="24" x2="252" y2="12" stroke="#fbbf24" stroke-width="1.6" />',
            '<circle cx="252" cy="12" r="2.8" fill="#22c55e" class="pulse" />',
            # Sweeping Aerodynamic Gull-Wing Glass Terminal
            '<path d="M16,140 L232,140 L220,108 Q124,84 28,108 Z" fill="#38bdf8" fill-opacity="0.82" stroke="#ffffff" stroke-width="1.2" />',
            '<path d="M10,110 Q72,82 124,98 Q176,82 238,110" fill="none" stroke="#f8fafc" stroke-width="3.5" stroke-linecap="round" />',
            '<g stroke="#0f294a" stroke-width="1" opacity="0.65">',
            '<line x1="48" y1="100" x2="42" y2="140" /><line x1="86" y1="95" x2="82" y2="140" />',
            '<line x1="124" y1="98" x2="124" y2="140" /><line x1="162" y1="95" x2="166" y2="140" /><line x1="200" y1="100" x2="206" y2="140" />',
            "</g>",
            # Widebody Jetliner Climbing After Takeoff
            '<g transform="translate(118, 52) rotate(-14)">',
            '<polygon points="-24,0 -34,-14 -24,-14 -14,0" fill="#0f294a" stroke="#fbbf24" stroke-width="0.8" />',
            '<path d="M-28,0 H26 C34,0 40,3 42,5 C40,7 34,8 26,8 H-28 Z" fill="#ffffff" stroke="#1e3a8a" stroke-width="0.9" />',
            '<polygon points="-4,5 -22,22 -12,22 10,5" fill="#e2e8f0" stroke="#1e3a8a" stroke-width="0.8" />',
            "</g>",
            # Tarmac & Illuminated Runway Centerline
            '<rect x="0" y="140" width="320" height="60" fill="#1e293b" />',
            '<path d="M0,170 L320,170" stroke="#fde047" stroke-width="2.2" stroke-dasharray="12 8" class="dash" />',
            '<path d="M0,150 L320,150 M0,190 L320,190" stroke="#94a3b8" stroke-width="1" />',
        ]
    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# HTML INJECTION & VALIDATION PIPELINE
# ==============================================================================
def validate_svg(svg_str: str, label: str) -> None:
    xml_ready = svg_str.replace(" data-reveal ", ' data-reveal="" ')
    try:
        ET.fromstring(xml_ready)
    except ET.ParseError as exc:
        sys.exit(f"XML ParseError in {label}: {exc}")


def replace_svgs_by_index(html: str, replacements: dict[int, str], page_label: str) -> str:
    """Replace large inline <svg> blocks (len > 600) by their 0-based index in the HTML file."""
    matches = [m for m in re.finditer(r"<svg\b[^>]*>.*?</svg>", html, re.S) if len(m.group(0)) > 600]
    for idx, new_svg in sorted(replacements.items(), reverse=True):
        if idx >= len(matches):
            sys.exit(f"Error: index {idx} out of range for {page_label} (found {len(matches)} large SVGs)")
        validate_svg(new_svg, f"{page_label}[{idx}]")
        m = matches[idx]
        html = html[: m.start()] + new_svg + html[m.end() :]
    return html


def main() -> None:
    try:
        from build_pages import format_and_remove_empty_lines
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from build_pages import format_and_remove_empty_lines

    for lang in ("en", "hu"):
        # 1. ski-paradise.html (indices: [1] Hero, [4] Height Chart, [5..9] 5 Resort Cards)
        ski_path = ROOT / lang / "ski-paradise.html"
        ski_repl = {
            1: build_ski_hero(),
            4: build_ski_height_chart(lang),
            **{5 + i: build_ski_resort_card(i) for i in range(5)},
        }
        ski_html = replace_svgs_by_index(ski_path.read_text(encoding="utf-8"), ski_repl, f"{lang}/ski-paradise.html")
        ski_path.write_text(format_and_remove_empty_lines(ski_html), encoding="utf-8")
        print(f"Updated {ski_path.relative_to(ROOT)} (Hero + Height Chart + 5 Resort Cards)")

        # 2. travel-guide.html (indices: [1] Hero, [2..16] 15 Luxury Hotel & Sanctuary Cards)
        tg_path = ROOT / lang / "travel-guide.html"
        tg_repl = {
            1: build_travel_hero(lang),
            **{2 + i: build_travel_card(i) for i in range(15)},
        }
        tg_html = replace_svgs_by_index(tg_path.read_text(encoding="utf-8"), tg_repl, f"{lang}/travel-guide.html")
        tg_path.write_text(format_and_remove_empty_lines(tg_html), encoding="utf-8")
        print(f"Updated {tg_path.relative_to(ROOT)} (Hero + 15 Hotel & Sanctuary Cards)")

        # 3. infrastructure.html (indices: [1] Hero, [3] Height Chart, [4..13] 10 Landmark Architecture Cards)
        inf_path = ROOT / lang / "infrastructure.html"
        inf_repl = {
            1: build_infra_hero(lang),
            3: build_infra_height_chart(lang),
            **{4 + i: build_infra_card(i) for i in range(10)},
        }
        inf_html = replace_svgs_by_index(inf_path.read_text(encoding="utf-8"), inf_repl, f"{lang}/infrastructure.html")
        inf_path.write_text(format_and_remove_empty_lines(inf_html), encoding="utf-8")
        print(f"Updated {inf_path.relative_to(ROOT)} (Hero + Height Chart + 10 Landmark Cards)")


if __name__ == "__main__":
    main()
