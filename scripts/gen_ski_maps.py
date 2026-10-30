#!/usr/bin/env python3
"""
Procedural generator for Waikiki Ski Paradise realistic 3D panoramic alpine trail maps:
  - Tab 1: Grand Andes Massif (icons/ski/andes-map.svg)
  - Tab 2: Haiti Highland Glacier (icons/ski/haiti-map.svg)

Generates standalone SVG files in icons/ski/ and injects localized inline SVGs
into en/ski-paradise.html and hu/ski-paradise.html.

Design notes:
  - Distant panoramic view: several layered ranges (far haze range, mid range,
    main ski massif) with atmospheric mist between them.
  - The only text on the maps is the peak names (plus the numbered interactive
    hotspot pins that link to the cards below the map).
  - Every lift tower stands on the straight lift corridor (ground line) between
    its two stations and its top carries the sagging haul cable, so no tower
    floats. Peak-to-peak aerial trams are free spans with no towers at all.
"""

import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKI_ICONS_DIR = ROOT / "icons" / "ski"
ANDES_SVG_PATH = SKI_ICONS_DIR / "andes-map.svg"
HAITI_SVG_PATH = SKI_ICONS_DIR / "haiti-map.svg"

BLUE = "#2563eb"
RED = "#e11d48"
BLACK = "#0f172a"
HELI = "heli"


# ==============================================================================
# GEOMETRY HELPERS
# ==============================================================================
def n(v: float) -> str:
    """Format number compactly to 1 decimal place."""
    if isinstance(v, int):
        return str(v)
    rv = round(v, 1)
    if rv == int(rv):
        return str(int(rv))
    s = f"{rv:.1f}"
    return "0" if s == "-0.0" else s


def pt(p) -> str:
    return f"{n(p[0])},{n(p[1])}"


def poly(points, close=True) -> str:
    d = "M" + " L".join(pt(p) for p in points)
    return d + (" Z" if close else "")


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def rnd(i: int, seed: float) -> float:
    """Deterministic pseudo-random value in [0, 1)."""
    return (math.sin(i * 12.9898 + seed * 78.233) * 43758.5453) % 1.0


def catmull_rom_svg(points, closed=False) -> str:
    """Convert a list of (x, y) points into a smooth cubic Bezier SVG path."""
    if len(points) < 2:
        return ""
    if len(points) == 2:
        return f"M{pt(points[0])} L{pt(points[1])}"
    pts = list(points)
    if closed:
        pts = [pts[-1]] + pts + [pts[0], pts[1]]
    else:
        pts = [pts[0]] + pts + [pts[-1]]
    d = [f"M{pt(pts[1])}"]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1x = p1[0] + (p2[0] - p0[0]) / 6.0
        c1y = p1[1] + (p2[1] - p0[1]) / 6.0
        c2x = p2[0] - (p3[0] - p1[0]) / 6.0
        c2y = p2[1] - (p3[1] - p1[1]) / 6.0
        d.append(f"C{n(c1x)},{n(c1y)} {n(c2x)},{n(c2y)} {pt(p2)}")
    if closed:
        d.append("Z")
    return " ".join(d)


def subdiv_ridge(p1, p2, roughness=12.0, seed=1, steps=8):
    """Create a craggy mountain arête between p1 and p2 (from p1 to p2)."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = p1[0] + (p2[0] - p1[0]) * t
        y = p1[1] + (p2[1] - p1[1]) * t
        if 0 < i < steps:
            env = math.sin(math.pi * t)
            off = roughness * env * (
                0.62 * math.sin(i * 2.7 + seed * 1.3) + 0.38 * math.cos(i * 4.9 + seed * 2.1)
            )
            y += off
            x += off * 0.28 * math.cos(i * 3.1 + seed)
        pts.append((x, y))
    return pts


def at_frac(ridge, f):
    pos = f * (len(ridge) - 1)
    i = min(int(pos), len(ridge) - 2)
    return lerp(ridge[i], ridge[i + 1], pos - i)


def head(ridge, f):
    """Points of a ridge from its start down to fraction f (inclusive end point)."""
    pos = f * (len(ridge) - 1)
    pts = list(ridge[: int(pos) + 1])
    pts.append(at_frac(ridge, f))
    return pts


def snow_fringe(a, b, teeth, depth, seed):
    """Jagged lower snow edge with couloir fingers reaching downhill."""
    out = []
    for j in range(1, 2 * teeth):
        p = lerp(a, b, j / (2 * teeth))
        if j % 2:
            dy = depth * (0.55 + 0.45 * abs(math.sin(j * 1.9 + seed)))
        else:
            dy = -depth * 0.2
        out.append((p[0], p[1] + dy))
    return out


# ==============================================================================
# TERRAIN
# ==============================================================================
def draw_peak(apex, w, base_y, c, snow_y, seed=1, detail=False):
    """
    Solid 3D mountain: sunlit western face, shadowed eastern face, jagged
    snow cap down to snow_y, optional rock bands, couloirs and arête highlights.
    """
    px, py = apex
    left_base = (px - w, base_y)
    right_base = (px + w, base_y)
    spine_base = (px + w * 0.18, base_y)
    rough = w * 0.07
    left = subdiv_ridge(left_base, apex, rough, seed, 8)
    right = subdiv_ridge(apex, right_base, rough, seed + 3, 8)
    spine = subdiv_ridge(apex, spine_base, rough * 0.8, seed + 7, 8)
    left_fa = list(reversed(left))

    out = [
        f'<path d="{poly(left + spine[1:])}" fill="{c["lit"]}" />',
        f'<path d="{poly(right + list(reversed(spine[:-1])))}" fill="{c["shade"]}" />',
    ]

    f = max(0.08, min(0.97, (snow_y - py) / (base_y - py)))
    depth = (base_y - py) * 0.08
    lp, sp, rp = at_frac(left_fa, f), at_frac(spine, f), at_frac(right, f)
    lit_snow = head(left_fa, f) + snow_fringe(lp, sp, 4, depth, seed) + list(reversed(head(spine, f)))
    shade_snow = head(spine, f) + snow_fringe(sp, rp, 3, depth, seed + 2) + list(reversed(head(right, f)))
    out.append(f'<path d="{poly(lit_snow)}" fill="{c["snow_lit"]}" />')
    out.append(f'<path d="{poly(shade_snow)}" fill="{c["snow_shade"]}" />')

    if detail:
        # Granite bands and couloirs on the shadowed face
        for k in range(1, 8, 2):
            a, b = spine[k], spine[k + 1]
            cc = lerp(b, right[k + 1], 0.5)
            dd = lerp(a, right[k], 0.36)
            out.append(f'<path d="{poly([a, b, (cc[0], cc[1] + 4), dd])}" fill="{c["rock"]}" opacity="0.5" />')
            out.append(
                f'<path d="M{pt(a)} Q{n((a[0] + cc[0]) / 2)},{n((a[1] + cc[1]) / 2 + 5)} {pt(cc)}" fill="none" stroke="#dbeafe" stroke-width="1" opacity="0.55" />'
            )
        # Sunlit crags just below the spine and secondary sub-ridges
        for k in (2, 4, 6):
            a, b = spine[k], spine[k + 1]
            m = lerp(a, left_fa[k], 0.34)
            out.append(f'<path d="{poly([a, (m[0], m[1] + 9), b])}" fill="{c["rock"]}" opacity="0.34" />')
            # Secondary sunlit snow facet rib
            if k <= 4:
                rib_end = lerp(left_fa[min(k + 2, 7)], spine[min(k + 2, 7)], 0.45)
                out.append(
                    f'<path d="M{pt(a)} Q{n((a[0] + rib_end[0]) / 2 - 4)},{n((a[1] + rib_end[1]) / 2)} {pt(rib_end)}" fill="none" stroke="#ffffff" stroke-width="0.9" opacity="0.55" />'
                )
        out.append(
            f'<path d="{poly(head(left_fa, min(f, 0.65)), close=False)}" fill="none" stroke="#ffffff" stroke-width="1.3" opacity="0.88" />'
        )
        out.append(
            f'<path d="{poly(head(spine, min(f, 0.78)), close=False)}" fill="none" stroke="#ffffff" stroke-width="1.5" opacity="0.92" />'
        )
    return out


def range_peaks(x0, x1, step, ymin, ymax, wmin, wmax, base, seed):
    peaks = []
    x, i = x0, 0
    while x <= x1:
        r1, r2 = rnd(i, seed), rnd(i + 31, seed + 1.7)
        peaks.append(((x + (r2 - 0.5) * step * 0.4, ymin + (ymax - ymin) * r1), wmin + (wmax - wmin) * r2, base))
        x += step
        i += 1
    return peaks


def draw_range(peaks, colors, snow_y, seed, detail=False):
    out = []
    # Lower summits first so taller summits overlap them
    for i, (apex, w, base) in enumerate(sorted(peaks, key=lambda p: -p[0][1])):
        out += draw_peak(apex, w, base, colors, snow_y, seed=seed + i * 3.1, detail=detail)
    return out


def draw_glacier_bowl(points, ice_fill):
    """Concave glacial cirque with transverse crevasse arcs."""
    out = [f'<path d="{catmull_rom_svg(points, closed=True)}" fill="{ice_fill}" opacity="0.42" />']
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    cx = sum(xs) / len(xs)
    min_y, max_y = min(ys), max(ys)
    w = (max(xs) - min(xs)) * 0.3
    out.append('<g fill="none" stroke="#ffffff" stroke-width="0.9" opacity="0.6">')
    for i in range(1, 5):
        yy = min_y + (max_y - min_y) * (i / 5.5)
        ww = w * math.sin(math.pi * (i / 5.0))
        out.append(f'<path d="M{n(cx - ww)},{n(yy)} Q{n(cx)},{n(yy + 6)} {n(cx + ww)},{n(yy - 1)}" />')
    out.append("</g>")
    return out


def draw_conifer_forest(clusters):
    """Layered 3-tier alpine spruce trees with trunks, shadows, and snow-draped boughs (depth sorted)."""
    out = ['<g class="alpine-forest">']
    for cx, cy, count, spread_x, spread_y, scale_base, seed in clusters:
        trees = []
        for i in range(count):
            ang = (i * 2.39996) + seed
            r = math.sqrt((i + 0.5) / count)
            tx = cx + math.cos(ang) * spread_x * r
            ty = cy + math.sin(ang) * spread_y * r
            sc = scale_base * (0.74 + 0.48 * ((i * 37 + seed * 13) % 10) / 10.0)
            trees.append((ty, tx, sc))
        trees.sort()
        for ty, tx, sc in trees:
            h = 18.5 * sc
            w = 6.6 * sc
            out.append(
                f'<ellipse cx="{n(tx + 2.2 * sc)}" cy="{n(ty + 1)}" rx="{n(w * 0.98)}" ry="{n(w * 0.32)}" fill="#0b1f38" opacity="0.32" />'
            )
            out.append(
                f'<rect x="{n(tx - 0.8 * sc)}" y="{n(ty - h * 0.18)}" width="{n(1.6 * sc)}" height="{n(h * 0.22)}" fill="#4a2c18" />'
            )
            # Bottom bough tier
            out.append(
                f'<path d="M{n(tx)},{n(ty - h * 0.72)} L{n(tx - w)},{n(ty - h * 0.08)} Q{n(tx)},{n(ty + h * 0.04)} {n(tx + w)},{n(ty - h * 0.08)} Z" fill="#0d3538" />'
            )
            # Middle bough tier
            out.append(
                f'<path d="M{n(tx)},{n(ty - h * 0.92)} L{n(tx - w * 0.82)},{n(ty - h * 0.36)} Q{n(tx)},{n(ty - h * 0.26)} {n(tx + w * 0.82)},{n(ty - h * 0.36)} Z" fill="#154c4e" />'
            )
            # Top crown tier
            out.append(
                f'<path d="M{n(tx)},{n(ty - h * 1.08)} L{n(tx - w * 0.6)},{n(ty - h * 0.62)} Q{n(tx)},{n(ty - h * 0.54)} {n(tx + w * 0.6)},{n(ty - h * 0.62)} Z" fill="#1e6663" />'
            )
            # Snow cap & bough frost
            out.append(
                f'<path d="M{n(tx)},{n(ty - h * 1.08)} L{n(tx - w * 0.48)},{n(ty - h * 0.68)} Q{n(tx - w * 0.1)},{n(ty - h * 0.62)} {n(tx + w * 0.24)},{n(ty - h * 0.72)} Z" fill="#f0f8ff" opacity="0.92" />'
            )
    out.append("</g>")
    return out


def draw_palm_tree(x, y, scale=1.0, tilt=1.0):
    """Realistic multi-frond tropical coconut palm with ringed curved trunk and coconuts."""
    tx = x + 7.5 * tilt * scale
    ty = y - 26 * scale
    ctrl_x = x + 2.8 * tilt * scale
    ctrl_y = y - 13 * scale
    out = [
        f'<ellipse cx="{n(x + 3 * scale)}" cy="{n(y + 1)}" rx="{n(8.5 * scale)}" ry="{n(2.6 * scale)}" fill="#a3834c" opacity="0.45" />',
        f'<path d="M{n(x - 1.4 * scale)},{n(y)} Q{n(ctrl_x - 0.9 * scale)},{n(ctrl_y)} {n(tx - 0.6 * scale)},{n(ty)} L{n(tx + 0.7 * scale)},{n(ty)} Q{n(ctrl_x + 1.0 * scale)},{n(ctrl_y)} {n(x + 1.4 * scale)},{n(y)} Z" fill="#6b4423" />',
        f'<path d="M{n(x)},{n(y)} Q{n(ctrl_x)},{n(ctrl_y)} {n(tx)},{n(ty)}" fill="none" stroke="#8c5a32" stroke-width="{n(1.1 * scale)}" stroke-dasharray="1.8 2.2" opacity="0.75" />',
    ]
    fronds = [
        (-17, 2, -9, -6, "#14532d"),
        (-15, 8, -8, 0, "#166534"),
        (17, 2, 9, -6, "#15803d"),
        (15, 8, 8, 0, "#166534"),
        (-13, -6, -7, -10, "#16a34a"),
        (13, -6, 7, -10, "#22c55e"),
        (-5, -13, -2, -9, "#4ade80"),
        (6, -12, 3, -9, "#22c55e"),
    ]
    for dx, dy, cx_off, cy_off, fcol in fronds:
        fx, fy = tx + dx * scale, ty + dy * scale
        qx, qy = tx + cx_off * scale, ty + cy_off * scale
        out.append(
            f'<path d="M{n(tx)},{n(ty)} Q{n(qx)},{n(qy)} {n(fx)},{n(fy)} Q{n(qx + (0.5 if dx > 0 else -0.5) * scale)},{n(qy + 2.8 * scale)} {n(tx)},{n(ty + 1.0 * scale)} Z" fill="{fcol}" opacity="0.94" />'
        )
    out.append(f'<circle cx="{n(tx - 1.2 * scale)}" cy="{n(ty + 1.4 * scale)}" r="{n(1.5 * scale)}" fill="#451a03" />')
    out.append(f'<circle cx="{n(tx + 1.2 * scale)}" cy="{n(ty + 1.6 * scale)}" r="{n(1.4 * scale)}" fill="#5c2d0c" />')
    return out


def mist_band(y, h, grad_id="mist"):
    return [f'<rect x="0" y="{n(y)}" width="1200" height="{n(h)}" fill="url(#{grad_id})" />']


def cloud(x, y, s, dx, dur):
    return [
        f'<g transform="translate({n(x)}, {n(y)})" opacity="0.55">',
        f'<animateTransform attributeName="transform" type="translate" values="{n(x)},{n(y)}; {n(x + dx)},{n(y)}; {n(x)},{n(y)}" dur="{dur}" repeatCount="indefinite" />',
        f'<g transform="scale({s})" fill="#ffffff">',
        '<ellipse cx="0" cy="0" rx="34" ry="7" />',
        '<ellipse cx="-14" cy="-4" rx="16" ry="7" />',
        '<ellipse cx="10" cy="-6" rx="18" ry="8" />',
        "</g>",
        "</g>",
    ]


def hamlet(x, y, count, seed=1):
    """Tiny cluster of snow-roofed chalets with lit windows."""
    out = ["<g>"]
    for i in range(count):
        hx = x + i * 9 - count * 4.5
        hy = y + (rnd(i, seed) - 0.5) * 6
        out += [
            f'<rect x="{n(hx - 3.5)}" y="{n(hy - 5)}" width="7" height="5" fill="#5c2d0c" />',
            f'<path d="M{n(hx - 4.5)},{n(hy - 5)} L{n(hx)},{n(hy - 9)} L{n(hx + 4.5)},{n(hy - 5)} Z" fill="#c95a41" />',
            f'<path d="M{n(hx - 3.5)},{n(hy - 5.8)} L{n(hx)},{n(hy - 8.6)} L{n(hx + 3.5)},{n(hy - 5.8)}" fill="none" stroke="#ffffff" stroke-width="1" />',
            f'<rect x="{n(hx - 1)}" y="{n(hy - 3.6)}" width="2" height="2" fill="#fde68a" />',
        ]
    out.append("</g>")
    return out


# ==============================================================================
# PISTES
# ==============================================================================
def piste(a, b, amp, phase, freq=2.0, steps=10):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        p = lerp(a, b, t)
        off = amp * math.sin(math.pi * t) * math.sin(freq * math.pi * t + phase)
        pts.append((p[0] + off, p[1]))
    return pts


def draw_pistes(specs):
    """specs: list of (start, end, amp, phase, color)."""
    runs = [(piste(a, b, amp, ph), col) for a, b, amp, ph, col in specs]
    out = ['<g fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity="0.7">']
    out += [f'<path d="{catmull_rom_svg(p)}" />' for p, col in runs if col != HELI]
    out.append("</g>")
    for col in (BLUE, RED, BLACK):
        out.append(f'<g fill="none" stroke="{col}" stroke-width="1.8" stroke-linecap="round">')
        out += [f'<path d="{catmull_rom_svg(p)}" />' for p, c in runs if c == col]
        out.append("</g>")
    out.append('<g fill="none" stroke="#d97706" stroke-width="1.6" stroke-dasharray="4 4" stroke-linecap="round">')
    out += [f'<path d="{catmull_rom_svg(p)}" />' for p, c in runs if c == HELI]
    out.append("</g>")
    return out, runs


# ==============================================================================
# LIFTS
# ==============================================================================
def sag_path(supports, ratio=0.04):
    d = f"M{pt(supports[0])}"
    for p, q in zip(supports, supports[1:]):
        m = lerp(p, q, 0.5)
        sag = max(0.8, math.dist(p, q) * ratio)
        d += f" Q{n(m[0])},{n(m[1] + sag * 2)} {pt(q)}"
    return d


GONDOLA = (
    '<line x1="0" y1="0" x2="0" y2="3" stroke="#e2e8f0" stroke-width="0.8" />'
    '<rect x="-3.5" y="3" width="7" height="5.5" rx="1.5" fill="{c}" stroke="#fcedc7" stroke-width="0.6" />'
    '<rect x="-2.2" y="4" width="4.4" height="2" rx="0.5" fill="#e0f2fe" />'
)
CHAIR = (
    '<line x1="0" y1="0" x2="0" y2="4.5" stroke="#e2e8f0" stroke-width="0.8" />'
    '<path d="M-3,2.5 L-3,5.5 L3,5.5" fill="none" stroke="{c}" stroke-width="1.4" />'
)
TRAM = (
    '<line x1="0" y1="0" x2="0" y2="3" stroke="#e2e8f0" stroke-width="1" />'
    '<rect x="-6" y="3" width="12" height="8" rx="2" fill="{c}" stroke="#fcedc7" stroke-width="0.8" />'
    '<rect x="-4" y="4.5" width="8" height="3" rx="0.8" fill="#e0f2fe" />'
)


def cabins(up, down, shape, colors, dur, count):
    out = []
    for k in range(count):
        for path, col, extra in ((up, colors[0], 0.0), (down, colors[1], 0.5)):
            begin = -dur * (k + extra) / count
            out += [
                "<g>",
                f'<animateMotion dur="{n(dur)}s" begin="{n(begin)}s" repeatCount="indefinite" path="{path}" />',
                shape.format(c=col),
                "</g>",
            ]
    return out


def draw_lift(a, b, kind="gondola", colors=("#c95a41", "#0b2342"), dur=10.0, spacing=40, tower_h=11, col="#dfba76"):
    """
    Grounded lift: towers stand on the straight corridor a -> b, their tops carry
    the sagging cable, and the cable ends inside the station buildings.
    """
    length = math.dist(a, b)
    nt = max(1, int(length // spacing))
    ground = [lerp(a, b, k / (nt + 1)) for k in range(1, nt + 1)]
    supports = [(a[0], a[1] - 7)] + [(g[0], g[1] - tower_h) for g in ground] + [(b[0], b[1] - 7)]
    up = sag_path(supports)
    down = sag_path(list(reversed(supports)))
    out = [
        f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="#3d5f88" stroke-width="2.4" opacity="0.2" />',
        '<g stroke-linecap="round">',
    ]
    for g in ground:
        top = (g[0], g[1] - tower_h)
        out += [
            f'<line x1="{n(g[0] - 2.5)}" y1="{n(g[1])}" x2="{n(g[0] + 2.5)}" y2="{n(g[1])}" stroke="#1e293b" stroke-width="1.8" />',
            f'<line x1="{n(g[0])}" y1="{n(g[1])}" x2="{n(top[0])}" y2="{n(top[1])}" stroke="#e5e7eb" stroke-width="1.3" />',
            f'<line x1="{n(top[0] - 3.5)}" y1="{n(top[1])}" x2="{n(top[0] + 3.5)}" y2="{n(top[1])}" stroke="{col}" stroke-width="1.5" />',
        ]
    out.append("</g>")
    out += [
        f'<path d="{up}" fill="none" stroke="#0b2342" stroke-width="1.8" opacity="0.55" />',
        f'<path d="{up}" fill="none" stroke="{col}" stroke-width="0.9" />',
    ]
    shape = CHAIR if kind == "chair" else GONDOLA
    out += cabins(up, down, shape, colors, dur, 2 if length < 260 else 3)
    return out


def draw_span(supports, colors=("#c95a41", "#0b2342"), dur=14.0, col="#5ce1cf"):
    """Peak-to-peak aerial tram: free cable spans, no intermediate towers."""
    up = sag_path(supports, ratio=0.06)
    down = sag_path(list(reversed(supports)), ratio=0.06)
    out = [
        f'<path d="{up}" fill="none" stroke="#0b2342" stroke-width="2" opacity="0.5" />',
        f'<path d="{up}" fill="none" stroke="{col}" stroke-width="1" stroke-dasharray="6 3" />',
    ]
    out += cabins(up, down, TRAM, colors, dur, 1)
    return out


def draw_funicular(a, b, dur=9.0):
    """Ground-level funicular track with sleepers and animated cars."""
    length = math.dist(a, b)
    dx, dy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    px, py = -dy * 3.2, dx * 3.2
    out = [
        f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="#0f172a" stroke-width="5" opacity="0.6" />',
        '<g stroke="#8a6a44" stroke-width="1.2">',
    ]
    steps = int(length // 7)
    for k in range(1, steps):
        c = lerp(a, b, k / steps)
        out.append(f'<line x1="{n(c[0] - px)}" y1="{n(c[1] - py)}" x2="{n(c[0] + px)}" y2="{n(c[1] + py)}" />')
    out.append("</g>")
    out.append(
        f'<line x1="{n(a[0])}" y1="{n(a[1])}" x2="{n(b[0])}" y2="{n(b[1])}" stroke="#dfba76" stroke-width="1.2" stroke-dasharray="8 4" />'
    )
    up = f"M{pt(a)} L{pt(b)}"
    down = f"M{pt(b)} L{pt(a)}"
    for path, fill, stroke, begin in ((up, "#c95a41", "#fcedc7", 0), (down, "#0b2342", "#5ce1cf", -dur / 2)):
        out += [
            "<g>",
            f'<animateMotion dur="{n(dur)}s" begin="{n(begin)}s" repeatCount="indefinite" rotate="auto" path="{path}" />',
            f'<rect x="-8" y="-4" width="16" height="8" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1" />',
            '<rect x="-5" y="-2" width="10" height="3" rx="1" fill="#fef08a" />',
            "</g>",
        ]
    return out


# ==============================================================================
# LABELS, PINS AND COMPASS
# ==============================================================================
def peak_label(x, y, en_name, hu_name, accent="#dfba76"):
    """Peak name pill (the only text on the maps). Width fits EN and HU."""
    w = max(len(en_name), len(hu_name)) * 6.4 + 30
    return [
        f'<rect x="{n(x - w / 2)}" y="{n(y - 9)}" width="{n(w)}" height="18" rx="9" fill="#071930" opacity="0.88" stroke="{accent}" stroke-width="1" />',
        f'<text x="{n(x)}" y="{n(y + 3.3)}" fill="#fcedc7" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle">▲ {en_name}</text>',
    ]


def hotspot_pin(idx, x, y, pin_dx=0, pin_dy=-26, active=False):
    """Numbered interactive pin offset from the landmark with a leader line."""
    px = x + pin_dx
    py = y + pin_dy
    cls = "map-hotspot is-active" if active else "map-hotspot"
    return [
        f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(px)}" y2="{n(py)}" stroke="#fcedc7" stroke-width="1.2" stroke-dasharray="2 2" opacity="0.85" />',
        f'<circle cx="{n(x)}" cy="{n(y)}" r="2.6" fill="#fcedc7" stroke="#0b2342" stroke-width="1" />',
        f'<g class="{cls}" data-spot="{idx}" transform="translate({n(px)}, {n(py)})">',
        '<circle class="hotspot-pulse" r="13" fill="#e3735a" opacity="0.45" />',
        '<circle class="hotspot-core" r="9.5" fill="#003366" stroke="#ffffff" stroke-width="2" />',
        f'<text fill="#ffffff" font-family="sans-serif" font-size="9.5" font-weight="800" text-anchor="middle" dominant-baseline="central">{idx}</text>',
        "</g>",
    ]


COMPASS = [
    '<g transform="translate(1158, 42)">',
    '<circle r="20" fill="#071930" opacity="0.8" stroke="#dfba76" stroke-width="1" />',
    '<polygon points="0,-15 3.5,-3 0,-6 -3.5,-3" fill="#e3735a" />',
    '<polygon points="0,15 3.5,3 0,6 -3.5,3" fill="#93c5fd" />',
    '<polygon points="-15,0 -3,-3.5 -6,0 -3,3.5" fill="#93c5fd" />',
    '<polygon points="15,0 3,-3.5 6,0 3,3.5" fill="#93c5fd" />',
    "</g>",
]


def place(x, y, scale, inner, comment):
    return [f"<!-- {comment} -->", f'<g transform="translate({n(x)}, {n(y)}) scale({scale})">'] + inner + ["</g>"]


# ==============================================================================
# LANDMARK BUILDINGS (local origin = station point)
# ==============================================================================
PICO_STATION = [
    '<polygon points="-32,6 32,6 22,18 -22,18" fill="#0f2542" stroke="#dfba76" stroke-width="1.2" />',
    '<rect x="-26" y="-6" width="52" height="12" rx="4" fill="#1e3a5f" stroke="#fcedc7" stroke-width="1.4" />',
    '<path d="M-18,-6 A18,13 0 0,1 18,-6 Z" fill="#38bdf8" stroke="#dfba76" stroke-width="1.4" />',
    '<line x1="0" y1="-19" x2="0" y2="-30" stroke="#fcedc7" stroke-width="1.8" />',
    '<circle cx="0" cy="-30" r="3" fill="#e3735a" class="pulse" />',
]
ROSA_OBSERVATORY = [
    '<ellipse cx="0" cy="6" rx="38" ry="9" fill="#0f2542" stroke="#dfba76" stroke-width="1.2" />',
    '<path d="M-26,4 A15,15 0 0,1 4,4 Z" fill="#38bdf8" stroke="#ffffff" stroke-width="1.3" />',
    '<path d="M2,4 A12,12 0 0,1 26,4 Z" fill="#f5c46e" stroke="#ffffff" stroke-width="1.2" />',
    '<ellipse cx="20" cy="10" rx="13" ry="4.5" fill="#2dd4bf" stroke="#fcedc7" stroke-width="1" />',
]
CONDOR_HELIPORT = [
    '<ellipse cx="0" cy="4" rx="28" ry="9" fill="#1e293b" stroke="#dfba76" stroke-width="1.5" />',
    '<ellipse cx="0" cy="4" rx="19" ry="6" fill="none" stroke="#5ce1cf" stroke-width="1.2" stroke-dasharray="3 2" />',
    '<path d="M-5,1 L-5,7 M5,1 L5,7 M-5,4 L5,4" stroke="#fcedc7" stroke-width="1.5" />',
    '<g class="bob" transform="translate(-36, -20)">',
    '<ellipse cx="0" cy="0" rx="12" ry="4.5" fill="#0b2342" stroke="#dfba76" stroke-width="1.2" />',
    '<line x1="-16" y1="-5" x2="16" y2="-5" stroke="#ffffff" stroke-width="1.4" />',
    '<line x1="0" y1="-5" x2="0" y2="-2" stroke="#dfba76" stroke-width="1.4" />',
    "</g>",
]
CHALETS = [
    '<ellipse cx="0" cy="6" rx="44" ry="12" fill="#c3def4" opacity="0.7" />',
    '<rect x="-32" y="-4" width="18" height="11" rx="1.5" fill="#5c2d0c" stroke="#fcedc7" stroke-width="1" />',
    '<polygon points="-35,-4 -23,-14 -11,-4" fill="#c95a41" stroke="#ffffff" stroke-width="1.2" />',
    '<rect x="-9" y="-8" width="22" height="14" rx="1.5" fill="#5c2d0c" stroke="#fcedc7" stroke-width="1" />',
    '<polygon points="-12,-8 2,-19 16,-8" fill="#dfba76" stroke="#ffffff" stroke-width="1.2" />',
    '<rect x="16" y="-3" width="18" height="11" rx="1.5" fill="#5c2d0c" stroke="#fcedc7" stroke-width="1" />',
    '<polygon points="13,-3 25,-12 37,-3" fill="#c95a41" stroke="#ffffff" stroke-width="1.2" />',
]
GRAND_PALACE = [
    '<ellipse cx="0" cy="14" rx="62" ry="13" fill="#2dd4bf" stroke="#fcedc7" stroke-width="1.6" />',
    '<rect x="-48" y="-14" width="96" height="24" rx="3" fill="#0b2342" stroke="#dfba76" stroke-width="1.6" />',
    '<rect x="-28" y="-26" width="56" height="14" rx="2" fill="#163b68" stroke="#dfba76" stroke-width="1.4" />',
    '<path d="M-16,-26 A16,14 0 0,1 16,-26 Z" fill="#dfba76" stroke="#ffffff" stroke-width="1.2" />',
    '<polygon points="-48,-14 -36,-24 -24,-14" fill="#c95a41" />',
    '<polygon points="24,-14 36,-24 48,-14" fill="#c95a41" />',
    '<g fill="#fde68a">',
    '<rect x="-40" y="-7" width="5" height="9" rx="1" />',
    '<rect x="-30" y="-7" width="5" height="9" rx="1" />',
    '<rect x="-20" y="-7" width="5" height="9" rx="1" />',
    '<rect x="-8" y="-9" width="16" height="14" rx="2" />',
    '<rect x="15" y="-7" width="5" height="9" rx="1" />',
    '<rect x="25" y="-7" width="5" height="9" rx="1" />',
    '<rect x="35" y="-7" width="5" height="9" rx="1" />',
    "</g>",
]
MAGLEV_TERMINAL = [
    '<path d="M-40,4 Q0,-24 40,4 Z" fill="#1e3a5f" stroke="#5ce1cf" stroke-width="1.6" />',
    '<rect x="-36" y="4" width="72" height="12" rx="3" fill="#0b2342" stroke="#dfba76" stroke-width="1.4" />',
    '<rect x="-24" y="7" width="48" height="5" rx="2" fill="#5ce1cf" />',
]
OLYMPIC_ARENA = [
    '<path d="M-30,2 A30,15 0 0,0 30,2 L22,12 A22,10 0 0,1 -22,12 Z" fill="#1e293b" stroke="#dfba76" stroke-width="1.4" />',
    '<rect x="-18" y="-16" width="36" height="7" rx="2" fill="#e11d48" stroke="#ffffff" stroke-width="1.1" />',
    '<line x1="-15" y1="-9" x2="-15" y2="4" stroke="#ffffff" stroke-width="1.6" />',
    '<line x1="15" y1="-9" x2="15" y2="4" stroke="#ffffff" stroke-width="1.6" />',
]
EDELWEISS_VILLAGE = [
    '<ellipse cx="0" cy="8" rx="38" ry="10" fill="#38bdf8" stroke="#bae6fd" stroke-width="1.4" />',
    '<rect x="-28" y="-12" width="18" height="14" fill="#1e3a5f" stroke="#dfba76" stroke-width="1" />',
    '<polygon points="-30,-12 -19,-22 -8,-12" fill="#c95a41" />',
    '<rect x="-5" y="-24" width="10" height="26" fill="#0b2342" stroke="#dfba76" stroke-width="1" />',
    '<polygon points="-7,-24 0,-36 7,-24" fill="#dfba76" />',
    '<rect x="10" y="-10" width="18" height="12" fill="#1e3a5f" stroke="#dfba76" stroke-width="1" />',
    '<polygon points="8,-10 19,-19 30,-10" fill="#c95a41" />',
]
CROWN_RESORT = [
    '<polygon points="-34,6 34,6 24,18 -24,18" fill="#0f2542" stroke="#dfba76" stroke-width="1.2" />',
    '<rect x="-28" y="-8" width="56" height="14" rx="7" fill="#1e3a5f" stroke="#fcedc7" stroke-width="1.4" />',
    '<rect x="18" y="-4" width="26" height="6" rx="3" fill="#38bdf8" stroke="#ffffff" stroke-width="1.1" />',
    '<path d="M-16,-8 A16,12 0 0,1 16,-8 Z" fill="#dfba76" />',
]
CRYO_DOME = [
    '<ellipse cx="0" cy="6" rx="44" ry="11" fill="#0f2542" stroke="#5ce1cf" stroke-width="1.4" />',
    '<path d="M-38,6 A38,32 0 0,1 38,6 Z" fill="#38bdf8" fill-opacity="0.55" stroke="#ffffff" stroke-width="1.5" />',
    '<path d="M-22,6 A22,30 0 0,1 22,6 M-38,6 H38 M0,-26 V6" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.8" />',
]
HORIZON_TERRACE = [
    '<ellipse cx="0" cy="2" rx="28" ry="9" fill="#0b2342" stroke="#dfba76" stroke-width="1.4" />',
    '<ellipse cx="0" cy="0" rx="22" ry="6" fill="#fde68a" />',
]
CRYO_VAULT = [
    '<rect x="-24" y="-12" width="48" height="18" rx="4" fill="#0f2542" stroke="#5ce1cf" stroke-width="1.5" />',
    '<circle cx="-12" cy="-3" r="4" fill="#2dd4bf" class="pulse" />',
    '<circle cx="0" cy="-3" r="4" fill="#2dd4bf" />',
    '<circle cx="12" cy="-3" r="4" fill="#2dd4bf" />',
]
SNOWPARK = [
    '<path d="M-26,-10 L-14,8 L18,8 L28,-10 Z" fill="#bae6fd" stroke="#0284c7" stroke-width="1.5" />',
    '<path d="M-20,-8 Q0,4 22,-8" fill="none" stroke="#ffffff" stroke-width="2.5" />',
]
FOREST_LODGE = [
    '<rect x="-26" y="-10" width="52" height="16" rx="3" fill="#14532d" stroke="#dfba76" stroke-width="1.4" />',
    '<rect x="-18" y="-6" width="36" height="8" rx="2" fill="#7dd3fc" />',
]
FOUNDERS_PAVILION = [
    '<rect x="-26" y="-8" width="52" height="16" rx="2" fill="#fef3c7" stroke="#b45309" stroke-width="1.3" />',
    '<polygon points="-30,-8 0,-23 30,-8" fill="#dfba76" stroke="#0b2342" stroke-width="1.2" />',
]
CORAL_MARINA = [
    '<path d="M-85,0 L65,0 L85,28 L-75,28 Z" fill="#0c4a6e" stroke="#dfba76" stroke-width="1.8" />',
    '<g stroke="#fcedc7" stroke-width="2">',
    '<line x1="-55" y1="0" x2="-55" y2="22" />',
    '<line x1="-20" y1="0" x2="-20" y2="22" />',
    '<line x1="15" y1="0" x2="15" y2="22" />',
    '<line x1="50" y1="0" x2="50" y2="22" />',
    "</g>",
    '<g fill="#ffffff" stroke="#0284c7" stroke-width="1">',
    '<polygon points="-48,6 -28,6 -31,18 -45,18" />',
    '<polygon points="-12,6 8,6 5,18 -9,18" />',
    '<polygon points="22,6 42,6 39,18 25,18" />',
    "</g>",
    '<path d="M-24,0 A24,16 0 0,1 24,0 Z" fill="#0b2342" stroke="#5ce1cf" stroke-width="1.6" />',
]
SMALL_LODGE = [
    '<rect x="-12" y="-8" width="24" height="10" rx="1.5" fill="#5c2d0c" stroke="#fcedc7" stroke-width="1" />',
    '<polygon points="-15,-8 0,-18 15,-8" fill="#c95a41" stroke="#ffffff" stroke-width="1.2" />',
    '<rect x="-3" y="-5" width="6" height="4" fill="#fde68a" />',
]


# ==============================================================================
# MAP 1: GRAND ANDES MASSIF (1200 x 700)
# ==============================================================================
def build_andes_svg() -> str:
    o = [
        '<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 1200 700" role="img" aria-label="Detailed 3D panoramic ski trail map of the Grand Andes Massif in Waikiki">',
        "<defs>",
        '<linearGradient id="andes-sky" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="420">',
        '<stop offset="0" stop-color="#06162e" />',
        '<stop offset="0.45" stop-color="#173f74" />',
        '<stop offset="0.8" stop-color="#4b84bd" />',
        '<stop offset="1" stop-color="#f3d5a0" />',
        "</linearGradient>",
        '<linearGradient id="andes-snow-lit" gradientUnits="userSpaceOnUse" x1="0" y1="120" x2="0" y2="480">',
        '<stop offset="0" stop-color="#ffffff" />',
        '<stop offset="0.6" stop-color="#e8f2fb" />',
        '<stop offset="1" stop-color="#c6dbef" />',
        "</linearGradient>",
        '<linearGradient id="andes-snow-shade" gradientUnits="userSpaceOnUse" x1="0" y1="120" x2="0" y2="480">',
        '<stop offset="0" stop-color="#bcd2ea" />',
        '<stop offset="0.6" stop-color="#93b2d5" />',
        '<stop offset="1" stop-color="#7498c2" />',
        "</linearGradient>",
        '<linearGradient id="andes-glacier-ice" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0" stop-color="#e0f7fe" />',
        '<stop offset="0.55" stop-color="#7dd3fc" />',
        '<stop offset="1" stop-color="#2563eb" />',
        "</linearGradient>",
        '<linearGradient id="andes-valley" gradientUnits="userSpaceOnUse" x1="0" y1="440" x2="0" y2="700">',
        '<stop offset="0" stop-color="#eef6fd" />',
        '<stop offset="0.5" stop-color="#dcebf8" />',
        '<stop offset="1" stop-color="#bcd6ee" />',
        "</linearGradient>",
        '<linearGradient id="andes-mist" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0" />',
        '<stop offset="0.7" stop-color="#e6f0fa" stop-opacity="0.6" />',
        '<stop offset="1" stop-color="#e6f0fa" stop-opacity="0.15" />',
        "</linearGradient>",
        "</defs>",
        "<!-- 1. Sky, stars and low sun -->",
        '<rect width="1200" height="700" fill="url(#andes-sky)" />',
    ]
    o.append('<g fill="#ffffff">')
    for i in range(34):
        sx = (i * 139 + 43) % 1160 + 20
        sy = (i * 53 + 11) % 100 + 8
        sr = 1.0 if i % 3 else 1.5
        cls = ' class="twinkle"' if i % 4 == 0 else ' opacity="0.5"'
        o.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}"{cls} />')
    o.append("</g>")
    o += [
        '<g transform="translate(990, 168)">',
        '<circle r="70" fill="#fef3c7" opacity="0.18" />',
        '<circle r="40" fill="#fde68a" opacity="0.32" />',
        '<circle r="20" fill="#fffbeb" opacity="0.95" />',
        "</g>",
    ]

    # 2. Far haze range and mid range for depth
    far_c = dict(lit="#b4cbe5", shade="#93b0d2", snow_lit="#eef5fc", snow_shade="#c8d9ed")
    mid_c = dict(lit="#6d8fb8", shade="#47678f", snow_lit="#f4f8fd", snow_shade="#a9c2df", rock="#3b5a80")
    o.append("<!-- 2. Far haze range -->")
    o.append('<g opacity="0.9">')
    o += draw_range(range_peaks(-20, 1230, 82, 150, 222, 70, 100, 330, 3.3), far_c, 245, 40)
    o.append("</g>")
    o += mist_band(250, 90, "andes-mist")
    o.append("<!-- 3. Mid range -->")
    o += draw_range(range_peaks(-40, 1240, 118, 205, 268, 95, 130, 410, 7.1), mid_c, 300, 70)
    o += mist_band(320, 100, "andes-mist")

    # 4. Main ski massif (eight summits)
    main_c = dict(
        lit="#55779f", shade="#28466d", snow_lit="url(#andes-snow-lit)", snow_shade="url(#andes-snow-shade)", rock="#1f3a5e"
    )
    main_peaks = [
        ((80, 215), 140, 480),
        ((395, 205), 130, 480),
        ((1025, 210), 150, 480),
        ((715, 200), 140, 485),
        ((1150, 190), 130, 485),
        ((240, 165), 170, 490),
        ((870, 160), 170, 495),
        ((560, 130), 200, 500),
    ]
    o.append("<!-- 4. Main ski massif -->")
    for i, (apex, w, base) in enumerate(main_peaks):
        o += draw_peak(apex, w, base, main_c, 470, seed=2 + i * 4, detail=True)
    for g in (
        [(560, 150), (530, 210), (528, 290), (568, 295), (578, 215)],
        [(240, 185), (215, 240), (218, 305), (252, 308), (258, 245)],
        [(870, 180), (845, 235), (848, 300), (884, 302), (890, 240)],
    ):
        o += draw_glacier_bowl(g, "url(#andes-glacier-ice)")

    # 5. Foothills, valley floor, forests, river
    def ft(x):
        return 452 + 12 * math.sin(x / 85 + 1) + 6 * math.sin(x / 31)

    foot = [(x, ft(x)) for x in range(0, 1201, 25)] + [(1200, 700), (0, 700)]
    band = [(x, 528 + 8 * math.sin(x / 120)) for x in range(0, 1201, 40)] + [(1200, 700), (0, 700)]
    floor = [(x, 596 + 5 * math.sin(x / 90)) for x in range(0, 1201, 40)] + [(1200, 700), (0, 700)]
    o += [
        "<!-- 5. Foothills and valley floor -->",
        f'<path d="{poly(foot)}" fill="url(#andes-valley)" />',
        f'<path d="{poly(band)}" fill="#dcebf8" opacity="0.8" />',
        f'<path d="{poly(floor)}" fill="#c9def2" />',
    ]
    o += draw_conifer_forest(
        [
            (300, 452, 10, 30, 8, 0.5, 21),
            (655, 458, 10, 30, 8, 0.5, 22),
            (1090, 455, 10, 30, 8, 0.5, 23),
            (55, 492, 22, 45, 20, 0.62, 1),
            (130, 535, 16, 36, 14, 0.66, 2),
            (320, 488, 22, 46, 20, 0.62, 3),
            (395, 540, 16, 36, 14, 0.66, 4),
            (470, 505, 18, 40, 16, 0.62, 5),
            (685, 495, 20, 44, 18, 0.62, 6),
            (800, 528, 16, 36, 14, 0.66, 7),
            (850, 485, 18, 40, 16, 0.62, 8),
            (1065, 495, 22, 46, 20, 0.62, 9),
            (1135, 545, 16, 36, 14, 0.66, 10),
        ]
    )
    river = [(0, 618), (160, 610), (320, 602), (470, 606), (620, 598), (780, 606), (940, 600), (1090, 607), (1200, 602)]
    o += [
        f'<path d="{catmull_rom_svg(river)}" fill="none" stroke="#1e4e79" stroke-width="10" stroke-linecap="round" opacity="0.5" />',
        f'<path d="{catmull_rom_svg(river)}" fill="none" stroke="#38bdf8" stroke-width="6" stroke-linecap="round" />',
        f'<path d="{catmull_rom_svg(river)}" fill="none" stroke="#e0f2fe" stroke-width="1.4" stroke-dasharray="8 7" stroke-linecap="round" class="dash" />',
    ]

    # 6. Pistes
    p1, condor, p3, pico = (80, 222), (240, 172), (395, 212), (560, 137)
    p5, rosa, p7, p8 = (715, 207), (870, 167), (1025, 217), (1150, 197)
    chalets, olympic = (420, 390), (735, 400)
    maglev, palace, village = (210, 580), (585, 565), (950, 565)
    specs = [
        (condor, maglev, 40, 0.0, BLUE), (condor, maglev, 25, 2.0, RED), (condor, maglev, 14, 4.0, BLACK),
        (condor, chalets, 30, 1.0, BLUE),
        (p1, maglev, 30, 0.5, RED), (p1, maglev, 35, 3.0, BLUE),
        (p3, chalets, 18, 0.0, RED), (p3, chalets, 24, 1.5, BLUE),
        (chalets, maglev, 30, 0.7, BLUE), (chalets, palace, 25, 1.0, BLUE), (chalets, palace, 20, 3.2, RED),
        (pico, chalets, 20, 0.0, BLACK), (pico, chalets, 30, 1.0, RED),
        (pico, palace, 45, 0.3, BLUE), (pico, palace, 30, 2.0, RED), (pico, palace, 12, 5.0, BLACK),
        (pico, olympic, 25, 1.2, RED),
        (p5, olympic, 22, 0.0, BLUE), (p5, olympic, 14, 2.0, BLACK),
        (olympic, palace, 30, 2.0, BLUE),
        (rosa, olympic, 20, 0.5, RED),
        (rosa, village, 40, 0.0, BLUE), (rosa, village, 28, 2.0, RED), (rosa, village, 14, 4.0, BLACK),
        (p7, village, 30, 0.4, BLUE), (p7, village, 22, 3.0, RED),
        (p8, village, 35, 0.8, RED), (p8, village, 18, 2.4, BLACK),
        (olympic, village, 30, 1.0, BLUE),
        (p1, (40, 520), 20, 1.0, HELI), (p8, (1180, 525), 22, 2.0, HELI), (pico, (470, 470), 26, 0.6, HELI),
    ]
    piste_svg, runs = draw_pistes(specs)
    o.append("<!-- 6. Piste network -->")
    o += piste_svg
    # Slalom gates on the Olympic downhill (Monte Rosa to the finish arena)
    downhill = runs[20][0]
    for idx, (gx, gy) in enumerate(downhill[2:-1]):
        gcol = RED if idx % 2 == 0 else BLUE
        o.append(
            f'<g transform="translate({n(gx + (-5 if idx % 2 == 0 else 5))}, {n(gy)})">'
            f'<line x1="0" y1="0" x2="0" y2="-6" stroke="{gcol}" stroke-width="1.1" />'
            f'<rect x="0" y="-6" width="4" height="2.6" fill="{gcol}" /></g>'
        )

    # 7. Lifts (grounded towers) and peak-to-peak trams (free spans)
    o.append("<!-- 7. Lift network -->")
    lifts = [
        (maglev, condor, "gondola", 12),
        (maglev, chalets, "chair", 10),
        (maglev, p1, "chair", 11),
        (chalets, pico, "gondola", 11),
        (chalets, p3, "chair", 8),
        (palace, pico, "gondola", 12),
        (palace, olympic, "chair", 9),
        (palace, p5, "chair", 12),
        (olympic, rosa, "gondola", 11),
        (village, rosa, "gondola", 12),
        (village, p7, "chair", 11),
        (village, p8, "chair", 12),
    ]
    for i, (a, b, kind, dur) in enumerate(lifts):
        colors = ("#c95a41", "#0b2342") if i % 2 == 0 else ("#165953", "#dfba76")
        o += draw_lift(a, b, kind=kind, colors=colors, dur=dur)
    o += draw_span([(condor[0], condor[1] - 8), (pico[0], pico[1] - 8)], dur=13)
    o += draw_span([(pico[0], pico[1] - 8), (rosa[0], rosa[1] - 8)], colors=("#0b2342", "#c95a41"), dur=14)

    # 8. Maglev viaduct
    o += ['<g fill="#64748b" stroke="#1e293b" stroke-width="1">']
    for vx in range(30, 1200, 50):
        o.append(f'<rect x="{vx - 3}" y="655" width="6" height="45" rx="1.5" />')
    o += [
        "</g>",
        '<path d="M0,655 L1200,655" stroke="#0f172a" stroke-width="7" />',
        '<path d="M0,655 L1200,655" stroke="#5ce1cf" stroke-width="1.6" stroke-dasharray="12 8" class="dash" />',
        "<g>",
        '<animateMotion dur="11s" repeatCount="indefinite" path="M-140,655 L1340,655" />',
        '<rect x="-60" y="-6" width="120" height="10" rx="5" fill="#0b2342" stroke="#dfba76" stroke-width="1.3" />',
        '<path d="M50,-6 L68,-1 L50,4 Z" fill="#c95a41" />',
        '<rect x="-48" y="-3.5" width="92" height="3.5" rx="1.75" fill="#5ce1cf" />',
        "</g>",
    ]

    # 9. Landmarks and hamlets
    o += place(*pico, 0.72, PICO_STATION, "Hub 1: Pico Soberano Crown Station")
    o += place(*rosa, 0.72, ROSA_OBSERVATORY, "Hub 2: Monte Rosa Sky Observatory")
    o += place(*condor, 0.72, CONDOR_HELIPORT, "Hub 3: Condor Royal Heliport")
    o += place(*chalets, 0.72, CHALETS, "Hub 4: Royal Chalets Hamlet")
    o += place(*palace, 0.72, GRAND_PALACE, "Hub 5: Grand Palace Val d'Aurelia")
    o += place(*maglev, 0.72, MAGLEV_TERMINAL, "Hub 6: Andes Maglev Grand Terminal")
    o += place(*olympic, 0.72, OLYMPIC_ARENA, "Hub 7: Olympic Downhill Finish Arena")
    o += place(*village, 0.72, EDELWEISS_VILLAGE, "Hub 8: Edelweiss Thermal Grotto Village")
    for i, (sx, sy) in enumerate((p1, p3, p5, p7, p8)):
        o += place(sx, sy, 0.6, SMALL_LODGE, f"Summit hut {i + 1}")
    o += hamlet(330, 585, 5, 1) + hamlet(470, 580, 4, 2) + hamlet(1090, 585, 5, 3) + hamlet(760, 590, 4, 4)

    # 10. Drifting clouds, peak names, compass, hotspots
    o += cloud(140, 300, 1.0, 50, "40s") + cloud(660, 270, 0.8, -40, "46s") + cloud(1050, 320, 1.1, 45, "52s")
    o += peak_label(pico[0], 92, "PICO SOBERANO", "PICO SOBERANO")
    o += peak_label(condor[0], 127, "CONDOR PEAK", "CONDOR-CSÚCS", "#5ce1cf")
    o += peak_label(rosa[0], 122, "MONTE ROSA", "MONTE ROSA")
    o += COMPASS
    spots = [
        (1, pico, 40, -14, True),
        (2, rosa, 44, -8, False),
        (3, condor, -44, -8, False),
        (4, chalets, -44, -16, False),
        (5, palace, 58, -22, False),
        (6, maglev, -50, -16, False),
        (7, olympic, 40, -18, False),
        (8, village, 46, -20, False),
    ]
    o.append("<!-- Interactive hotspot pins -->")
    for idx, (sx, sy), dx, dy, act in spots:
        o += hotspot_pin(idx, sx, sy, pin_dx=dx, pin_dy=dy, active=act)
    o.append("</svg>")
    return "\n".join(o)


# ==============================================================================
# MAP 2: HAITI HIGHLAND GLACIER (1200 x 700)
# ==============================================================================
def build_haiti_svg() -> str:
    o = [
        '<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 1200 700" role="img" aria-label="Detailed 3D panoramic Sea-to-Summit ski map of Haiti Highland Glacier rising from the Caribbean Sea">',
        "<defs>",
        '<linearGradient id="haiti-sky" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="410">',
        '<stop offset="0" stop-color="#0a2547" />',
        '<stop offset="0.5" stop-color="#2468a8" />',
        '<stop offset="0.85" stop-color="#7cc0e3" />',
        '<stop offset="1" stop-color="#fae5b8" />',
        "</linearGradient>",
        '<linearGradient id="haiti-snow-lit" gradientUnits="userSpaceOnUse" x1="0" y1="150" x2="0" y2="380">',
        '<stop offset="0" stop-color="#ffffff" />',
        '<stop offset="1" stop-color="#dcebf8" />',
        "</linearGradient>",
        '<linearGradient id="haiti-snow-shade" gradientUnits="userSpaceOnUse" x1="0" y1="150" x2="0" y2="380">',
        '<stop offset="0" stop-color="#bcd3ea" />',
        '<stop offset="1" stop-color="#8eb0d4" />',
        "</linearGradient>",
        '<linearGradient id="haiti-jungle" gradientUnits="userSpaceOnUse" x1="0" y1="430" x2="0" y2="560">',
        '<stop offset="0" stop-color="#22805c" />',
        '<stop offset="1" stop-color="#0e4632" />',
        "</linearGradient>",
        '<linearGradient id="haiti-back-sea" gradientUnits="userSpaceOnUse" x1="0" y1="405" x2="0" y2="560">',
        '<stop offset="0" stop-color="#5fb3d9" />',
        '<stop offset="1" stop-color="#1679b5" />',
        "</linearGradient>",
        '<linearGradient id="haiti-carib-sea" gradientUnits="userSpaceOnUse" x1="0" y1="550" x2="0" y2="700">',
        '<stop offset="0" stop-color="#38d6e8" />',
        '<stop offset="0.35" stop-color="#0ea5e9" />',
        '<stop offset="0.75" stop-color="#0369a1" />',
        '<stop offset="1" stop-color="#083a5c" />',
        "</linearGradient>",
        '<linearGradient id="haiti-glacier-ice" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0" stop-color="#e0f7fe" />',
        '<stop offset="1" stop-color="#38bdf8" />',
        "</linearGradient>",
        '<linearGradient id="haiti-mist" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0" />',
        '<stop offset="0.7" stop-color="#eef6fb" stop-opacity="0.55" />',
        '<stop offset="1" stop-color="#eef6fb" stop-opacity="0.1" />',
        "</linearGradient>",
        "</defs>",
        "<!-- 1. Sky, sun, distant sea and islands -->",
        '<rect width="1200" height="700" fill="url(#haiti-sky)" />',
        '<g transform="translate(150, 115)">',
        '<circle r="70" fill="#fef3c7" opacity="0.24" />',
        '<circle r="42" fill="#fde68a" opacity="0.4" />',
        '<circle r="22" fill="#fffbeb" opacity="0.96" />',
        "</g>",
        '<rect x="0" y="405" width="1200" height="295" fill="url(#haiti-back-sea)" />',
        '<g fill="#6f9fb8" opacity="0.65">',
        '<path d="M0,406 Q30,388 70,394 Q100,398 125,406 Z" />',
        '<path d="M1040,406 Q1080,384 1120,392 Q1165,396 1200,404 L1200,406 Z" />',
        '<path d="M1000,406 Q1015,398 1030,406 Z" />',
        "</g>",
    ]

    # 2. Distant highland range behind the island summits
    far_c = dict(lit="#8dbdb0", shade="#6a9d92", snow_lit="#eef6fb", snow_shade="#c6dbe9")
    o.append("<!-- 2. Distant highland range -->")
    o += draw_range(
        [((300, 235), 110, 430), ((470, 200), 120, 430), ((650, 190), 120, 430), ((790, 215), 110, 430), ((960, 225), 120, 430)],
        far_c,
        285,
        90,
    )
    o += mist_band(300, 120, "haiti-mist")

    # 3. Main island massif: jungle-clad lower slopes, glacier summits
    main_c = dict(
        lit="#2e8a63", shade="#175a43", snow_lit="url(#haiti-snow-lit)", snow_shade="url(#haiti-snow-shade)", rock="#0f3f2e"
    )
    main_peaks = [
        ((385, 215), 150, 470),
        ((710, 225), 140, 470),
        ((1010, 245), 160, 475),
        ((170, 320), 110, 480),
        ((235, 250), 160, 480),
        ((1060, 305), 110, 480),
        ((860, 190), 190, 485),
        ((560, 160), 230, 490),
    ]
    o.append("<!-- 3. Main island massif -->")
    for i, (apex, w, base) in enumerate(main_peaks):
        o += draw_peak(apex, w, base, main_c, 370, seed=5 + i * 4, detail=True)
    o += draw_glacier_bowl([(560, 180), (535, 230), (538, 290), (570, 292), (580, 235)], "url(#haiti-glacier-ice)")
    o += draw_glacier_bowl([(860, 210), (840, 250), (843, 300), (872, 302), (880, 255)], "url(#haiti-glacier-ice)")
    o += [
        "<!-- Sub-surface Cryo-Grid 3.0 cooling matrix -->",
        '<g stroke="#0ea5e9" stroke-width="0.9" stroke-dasharray="3 3" opacity="0.45" fill="none">',
        '<path d="M590,300 L690,300 M585,312 L695,312 M580,324 L700,324 M575,336 L705,336" />',
        '<path d="M605,292 L590,344 M635,292 L628,344 M665,292 L668,344 M690,292 L702,344" />',
        "</g>",
    ]
    o += mist_band(370, 80, "haiti-mist")

    # 4. Seamless Montane Cloud Forest & Tropical Rainforest Canopy Belt
    def coast(x):
        return 542 + 5 * math.sin(x / 90)

    o.append("<!-- 4. Seamless Montane Cloud Forest and Tropical Rainforest Canopy -->")
    # Sub-alpine krummholz / montane transition ridge (y ~ 396..445)
    montane_pts = [
        (0, 445),
        *[
            (
                x,
                404
                + 10 * math.sin(x / 72 + 0.5)
                + 6 * math.cos(x / 29)
                - 14 * math.exp(-((x - 560) / 360) ** 2),
            )
            for x in range(0, 1201, 24)
        ],
        (1200, 555),
        (0, 555),
    ]
    o.append(f'<path d="{poly(montane_pts)}" fill="#134e3a" opacity="0.92" />')

    # 5 layered scalloped organic rainforest canopy waves (back-to-front from y=418 to y=536)
    canopy_tiers = [
        (422, 9.0, 26, "#165b41", "#227a56", 11),
        (444, 10.5, 24, "#1b6b4c", "#298f63", 23),
        (468, 11.5, 22, "#1f7a55", "#34a873", 37),
        (494, 12.0, 20, "#196748", "#2d9666", 53),
        (518, 11.0, 22, "#14533a", "#25855a", 71),
    ]
    for base_y, crown_h, step_x, fill_col, rim_col, cseed in canopy_tiers:
        d_parts = [f"M0,{n(base_y + 18)}"]
        rim_parts = []
        cx = 0
        idx = 0
        while cx < 1200:
            nx = min(1200, cx + step_x + int((rnd(idx, cseed) - 0.5) * 8))
            mx = (cx + nx) * 0.5
            arch = base_y - crown_h * (0.65 + 0.55 * rnd(idx + 17, cseed)) + 5 * math.sin(cx / 85.0 + cseed)
            valley = base_y + 3 * (rnd(idx + 31, cseed) - 0.3) + 5 * math.sin(nx / 85.0 + cseed)
            d_parts.append(f"Q{n(mx)},{n(arch)} {n(nx)},{n(valley)}")
            if idx % 2 == 0 and 40 < cx < 1160:
                rim_parts.append(f"M{n(cx + 2)},{n(valley - 1)} Q{n(mx)},{n(arch - 1.2)} {n(nx - 2)},{n(valley - 1)}")
            cx = nx
            idx += 1
        d_parts.append("L1200,556 L0,556 Z")
        o.append(f'<path d="{" ".join(d_parts)}" fill="{fill_col}" />')
        o.append(
            f'<path d="{" ".join(rim_parts)}" fill="none" stroke="{rim_col}" stroke-width="1.4" stroke-linecap="round" opacity="0.65" />'
        )

    # Emergent ceiba & mahogany tree crowns rising out of the rainforest canopy
    o.append('<g class="emergent-crowns">')
    for ex, ey, erx, ery, ecol, elcol in [
        (145, 452, 22, 11, "#166534", "#4ade80"),
        (265, 476, 25, 12, "#14532d", "#22c55e"),
        (395, 448, 24, 11, "#15803d", "#4ade80"),
        (515, 488, 26, 12, "#166534", "#34d399"),
        (615, 458, 23, 11, "#14532d", "#4ade80"),
        (735, 482, 25, 12, "#15803d", "#22c55e"),
        (885, 456, 24, 11, "#166534", "#4ade80"),
        (985, 492, 22, 11, "#14532d", "#34d399"),
        (1095, 466, 23, 11, "#15803d", "#4ade80"),
    ]:
        o.append(f'<ellipse cx="{ex}" cy="{ey + 3}" rx="{erx + 2}" ry="{ery}" fill="#0a2e1f" opacity="0.45" />')
        o.append(f'<ellipse cx="{ex}" cy="{ey}" rx="{erx}" ry="{ery}" fill="{ecol}" />')
        o.append(f'<ellipse cx="{ex - 4}" cy="{ey - 3}" rx="{erx * 0.65:.1f}" ry="{ery * 0.6:.1f}" fill="{elcol}" opacity="0.45" />')
    o.append("</g>")

    # Glacial meltwater rivers & multi-tier jungle waterfalls with misty plunge pools
    o += [
        '<path d="M454,368 C452,398 446,422 444,448 C442,478 441,504 438,536" fill="none" stroke="#0f3f2e" stroke-width="6.5" stroke-linecap="round" opacity="0.55" />',
        '<path d="M454,368 C452,398 446,422 444,448 C442,478 441,504 438,536" fill="none" stroke="#7dd3fc" stroke-width="3.4" stroke-linecap="round" opacity="0.92" />',
        '<path d="M454,368 C452,398 446,422 444,448 C442,478 441,504 438,536" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-dasharray="6 4" stroke-linecap="round" opacity="0.85" />',
        '<ellipse cx="445" cy="448" rx="9" ry="3.2" fill="#e0f2fe" opacity="0.78" />',
        '<ellipse cx="438" cy="536" rx="14" ry="4.2" fill="#38bdf8" opacity="0.85" />',
        '<ellipse cx="438" cy="536" rx="8" ry="2.2" fill="#ffffff" opacity="0.75" />',
        '<path d="M788,370 C794,402 798,428 801,456 C804,484 805,508 808,538" fill="none" stroke="#0f3f2e" stroke-width="6.0" stroke-linecap="round" opacity="0.55" />',
        '<path d="M788,370 C794,402 798,428 801,456 C804,484 805,508 808,538" fill="none" stroke="#7dd3fc" stroke-width="3.2" stroke-linecap="round" opacity="0.9" />',
        '<path d="M788,370 C794,402 798,428 801,456 C804,484 805,508 808,538" fill="none" stroke="#ffffff" stroke-width="1.2" stroke-dasharray="5 4" stroke-linecap="round" opacity="0.85" />',
        '<ellipse cx="801" cy="456" rx="8.5" ry="3.0" fill="#e0f2fe" opacity="0.78" />',
        '<ellipse cx="808" cy="538" rx="13" ry="4.0" fill="#38bdf8" opacity="0.85" />',
        '<ellipse cx="808" cy="538" rx="7.5" ry="2.0" fill="#ffffff" opacity="0.75" />',
    ]
    # Sub-alpine spruce & cloud-forest pine clusters along the snowline ecotone (y ~ 368..412)
    o += draw_conifer_forest(
        [
            (195, 396, 14, 38, 12, 0.52, 10),
            (285, 390, 16, 42, 12, 0.55, 11),
            (465, 384, 16, 42, 12, 0.56, 12),
            (615, 388, 14, 38, 11, 0.52, 15),
            (775, 380, 16, 42, 12, 0.56, 13),
            (915, 392, 14, 36, 11, 0.52, 16),
            (1045, 396, 14, 36, 11, 0.52, 14),
        ]
    )
    o += mist_band(392, 52, "haiti-mist")

    # 5. Golden beach, turquoise coral lagoon, and barrier reef
    beach_top = [(x, coast(x) - 6 + 2 * math.sin(x / 35)) for x in range(0, 1201, 30)]
    beach = beach_top + [(1200, 700), (0, 700)]
    wet_sand = [(x, coast(x) + 6 + 2.5 * math.sin(x / 45)) for x in range(0, 1201, 30)] + [(1200, 700), (0, 700)]
    sea = [(x, coast(x) + 12 + 3 * math.sin(x / 50)) for x in range(0, 1201, 30)] + [(1200, 700), (0, 700)]
    o += [
        "<!-- 5. Golden beach and Caribbean Sea -->",
        f'<path d="{poly(beach)}" fill="#f6e3ba" />',
        f'<path d="{poly(wet_sand)}" fill="#dfbe82" opacity="0.7" />',
        f'<path d="{poly(sea)}" fill="url(#haiti-carib-sea)" />',
        '<path d="M0,564 Q300,578 600,568 T1200,573 L1200,618 Q900,606 600,616 T0,608 Z" fill="#2dd4bf" opacity="0.38" />',
        # Submerged coral reef heads & turquoise sandbars
        '<g opacity="0.48">',
        '<ellipse cx="140" cy="592" rx="46" ry="9" fill="#0d9488" />',
        '<ellipse cx="145" cy="590" rx="28" ry="5" fill="#5eead4" />',
        '<ellipse cx="380" cy="602" rx="58" ry="11" fill="#0f766e" />',
        '<ellipse cx="385" cy="600" rx="34" ry="6" fill="#5eead4" />',
        '<ellipse cx="675" cy="596" rx="52" ry="10" fill="#0d9488" />',
        '<ellipse cx="670" cy="594" rx="30" ry="5.5" fill="#99f6e4" />',
        '<ellipse cx="980" cy="598" rx="64" ry="11" fill="#0f766e" />',
        '<ellipse cx="985" cy="596" rx="36" ry="6" fill="#5eead4" />',
        "</g>",
        '<path d="M0,556 Q300,565 600,558 T1200,563" fill="none" stroke="#ffffff" stroke-width="2.0" stroke-dasharray="14 6" opacity="0.88" class="dash" />',
        '<path d="M50,646 Q380,626 680,640 T1150,632" fill="none" stroke="#5eead4" stroke-width="9" stroke-linecap="round" opacity="0.32" />',
        '<path d="M50,646 Q380,626 680,640 T1150,632" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-dasharray="6 6" opacity="0.78" />',
    ]
    for px, py, psc, ptilt in [
        (52, 546, 0.78, -1), (88, 548, 0.85, 1), (125, 545, 0.72, 0.6),
        (285, 546, 0.8, -0.8), (320, 548, 0.86, 1), (355, 547, 0.74, -1),
        (495, 542, 0.82, -0.9), (530, 544, 0.76, 1), (635, 544, 0.8, -1), (670, 546, 0.74, 0.8),
        (885, 547, 0.82, 1), (922, 548, 0.76, -1), (955, 546, 0.7, 0.7),
        (1090, 544, 0.84, -1), (1130, 546, 0.78, 1), (1162, 545, 0.7, -0.7),
    ]:
        o += draw_palm_tree(px, py, scale=psc, tilt=ptilt)

    # 6. Pistes on the glacier zone
    h2, h3, crown, h5, dome, h7 = (235, 257), (385, 222), (560, 167), (710, 232), (860, 197), (1010, 252)
    terrace, vault, snowpark = (505, 290), (635, 310), (825, 320)
    lodge, founders, east, marina = (330, 405), (700, 410), (965, 400), (215, 592)
    specs = [
        (crown, terrace, 22, 0.0, BLUE), (crown, vault, 18, 1.0, RED), (crown, vault, 10, 3.0, BLACK),
        (crown, founders, 40, 1.0, BLUE), (crown, founders, 28, 4.0, RED), (crown, founders, 12, 2.0, BLACK),
        (crown, lodge, 30, 0.6, RED),
        (terrace, lodge, 24, 0.0, BLUE), (terrace, lodge, 16, 2.0, RED),
        (h3, lodge, 24, 0.5, BLUE), (h3, lodge, 12, 3.0, BLACK),
        (h2, lodge, 24, 1.0, RED), (h2, lodge, 28, 3.0, BLUE),
        (vault, founders, 18, 0.5, BLUE),
        (h5, founders, 18, 0.0, RED), (h5, founders, 22, 2.0, BLUE),
        (dome, snowpark, 18, 0.0, BLUE), (dome, founders, 30, 1.0, RED), (snowpark, founders, 24, 2.0, BLUE),
        (dome, east, 14, 0.5, BLACK), (dome, east, 32, 2.0, BLUE),
        (h7, east, 20, 0.0, RED), (h7, east, 26, 1.0, BLUE),
    ]
    piste_svg, _ = draw_pistes(specs)
    o.append("<!-- 6. Piste network -->")
    o += piste_svg

    # 7. Funicular, lifts and skylink
    o.append("<!-- 7. Lift network -->")
    o += draw_funicular(marina, lodge)
    lifts = [
        (lodge, terrace, "gondola", 9),
        (terrace, crown, "gondola", 9),
        (lodge, h2, "chair", 10),
        (lodge, h3, "chair", 11),
        (founders, vault, "gondola", 8),
        (vault, crown, "gondola", 9),
        (founders, h5, "chair", 10),
        (founders, snowpark, "gondola", 9),
        (snowpark, dome, "gondola", 9),
        (east, dome, "chair", 10),
        (east, h7, "chair", 9),
    ]
    for i, (a, b, kind, dur) in enumerate(lifts):
        colors = ("#c95a41", "#0b2342") if i % 2 == 0 else ("#165953", "#dfba76")
        o += draw_lift(a, b, kind=kind, colors=colors, dur=dur)
    o += draw_span([(crown[0], crown[1] - 8), (dome[0], dome[1] - 8)], dur=12)

    # 8. Landmarks and boats
    o += place(*crown, 0.75, CROWN_RESORT, "Hub 1: Haiti Glacier Crown Resort")
    o += place(*dome, 0.75, CRYO_DOME, "Hub 2: Cryo-Dome Snowsphere")
    o += place(*terrace, 0.75, HORIZON_TERRACE, "Hub 3: Caribbean Horizon Terrace")
    o += place(*vault, 0.75, CRYO_VAULT, "Hub 4: Cryo-Grid 3.0 Command Vault")
    o += place(*snowpark, 0.75, SNOWPARK, "Hub 5: Royal Halfpipe and Snowpark")
    o += place(*lodge, 0.75, FOREST_LODGE, "Hub 6: Cloud Forest Transition Lodge")
    o += place(*founders, 0.75, FOUNDERS_PAVILION, "Hub 7: 2011 Founders Pavilion")
    o += place(*marina, 0.75, CORAL_MARINA, "Hub 8: Coral Bay Superyacht Marina")
    o += place(*east, 0.7, SMALL_LODGE, "East Ridge Lodge")
    for i, (sx, sy) in enumerate((h2, h3, h5, h7)):
        o += place(sx, sy, 0.6, SMALL_LODGE, f"Summit hut {i + 1}")
    o += [
        '<g class="bob" transform="translate(540, 628)">',
        '<polygon points="-34,3 34,3 24,13 -28,13" fill="#ffffff" stroke="#0b2342" stroke-width="1.3" />',
        '<rect x="-18" y="-4" width="30" height="7" rx="2" fill="#e0f2fe" stroke="#0284c7" stroke-width="0.9" />',
        '<rect x="-8" y="-9" width="16" height="5" rx="1.2" fill="#ffffff" />',
        "</g>",
        '<g class="bob" transform="translate(880, 612)">',
        '<polygon points="-16,5 16,5 11,11 -13,11" fill="#ffffff" stroke="#0b2342" stroke-width="1" />',
        '<polygon points="0,-20 0,3 -11,3" fill="#fef3c7" />',
        '<polygon points="2,-18 2,3 12,3" fill="#f8fafc" />',
        "</g>",
        '<g class="bob" transform="translate(1010, 660)">',
        '<polygon points="-12,4 12,4 8,9 -10,9" fill="#ffffff" stroke="#0b2342" stroke-width="0.9" />',
        '<polygon points="0,-15 0,2 -9,2" fill="#fde68a" />',
        "</g>",
    ]

    # 9. Clouds, peak names, compass, hotspots
    o += cloud(320, 330, 0.9, 45, "44s") + cloud(760, 300, 1.0, -40, "50s") + cloud(1080, 350, 0.8, 35, "38s")
    o += peak_label(crown[0], 120, "GLACIER CROWN", "GLECCSERKORONA")
    o += peak_label(dome[0], 146, "CRYO-DOME PEAK", "KRIO-KUPOLA CSÚCS", "#5ce1cf")
    o += COMPASS
    spots = [
        (1, crown, -50, -6, True),
        (2, dome, 52, -6, False),
        (3, terrace, -40, -14, False),
        (4, vault, 42, -12, False),
        (5, snowpark, 42, -12, False),
        (6, lodge, -42, -16, False),
        (7, founders, 42, -16, False),
        (8, marina, -60, -12, False),
    ]
    o.append("<!-- Interactive hotspot pins -->")
    for idx, (sx, sy), dx, dy, act in spots:
        o += hotspot_pin(idx, sx, sy, pin_dx=dx, pin_dy=dy, active=act)
    o.append("</svg>")
    return "\n".join(o)


# ==============================================================================
# LOCALIZATION & HTML INJECTION
# ==============================================================================
EN_TO_HU = [
    (
        'aria-label="Detailed 3D panoramic ski trail map of the Grand Andes Massif in Waikiki"',
        'aria-label="A Magas-Andok Masszívum részletes 3D panoráma sítérképe"',
    ),
    (
        'aria-label="Detailed 3D panoramic Sea-to-Summit ski map of Haiti Highland Glacier rising from the Caribbean Sea"',
        'aria-label="A Karib-tengerből kiemelkedő Haiti Gleccserfennsík részletes 3D panoráma sítérképe"',
    ),
    (">▲ CONDOR PEAK<", ">▲ CONDOR-CSÚCS<"),
    (">▲ GLACIER CROWN<", ">▲ GLECCSERKORONA<"),
    (">▲ CRYO-DOME PEAK<", ">▲ KRIO-KUPOLA CSÚCS<"),
]


def localize_svg(raw_svg: str, lang: str) -> str:
    try:
        ET.fromstring(raw_svg)
    except ET.ParseError as exc:
        sys.exit(f"Error: generated SVG is invalid XML: {exc}")

    inline_svg = re.sub(r'\s+xmlns="http://www\.w3\.org/2000/svg"', "", raw_svg, count=1)
    if lang == "hu":
        for en_s, hu_s in EN_TO_HU:
            inline_svg = inline_svg.replace(en_s, hu_s)
    return inline_svg


PANEL_SVG_RE_TEMPLATE = (
    r'(<div class="island-panel[^"]*" id="{panel_id}"[^>]*>.*?<div class="island-map-canvas">\s*)'
    r"<svg\b[^>]*>.*?</svg>"
    r"(\s*</div>)"
)


def update_ski_pages(andes_raw: str, haiti_raw: str) -> None:
    try:
        from build_pages import format_and_remove_empty_lines
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from build_pages import format_and_remove_empty_lines

    for lang in ("en", "hu"):
        html_path = ROOT / lang / "ski-paradise.html"
        html = html_path.read_text(encoding="utf-8")

        html = re.sub(r'data-spot="(?:andes|haiti)-(\d+)"', r'data-spot="\1"', html)

        for panel_id, raw_svg in (("panel-andes", andes_raw), ("panel-haiti", haiti_raw)):
            pattern = re.compile(PANEL_SVG_RE_TEMPLATE.format(panel_id=panel_id), re.S)
            match = pattern.search(html)
            if not match:
                sys.exit(f"Error: could not find <svg> inside #{panel_id} in {html_path}")
            svg_inline = localize_svg(raw_svg, lang)
            html = html[: match.start()] + f"{match.group(1)}{svg_inline}{match.group(2)}" + html[match.end() :]

        cleaned = format_and_remove_empty_lines(html)
        html_path.write_text(cleaned, encoding="utf-8")
        print(f"Updated {html_path.relative_to(ROOT)} with realistic Andes and Haiti SVG maps")


def main() -> None:
    SKI_ICONS_DIR.mkdir(parents=True, exist_ok=True)
    andes_svg = build_andes_svg()
    haiti_svg = build_haiti_svg()

    ANDES_SVG_PATH.write_text(andes_svg + "\n", encoding="utf-8")
    HAITI_SVG_PATH.write_text(haiti_svg + "\n", encoding="utf-8")
    print(f"Generated {ANDES_SVG_PATH.relative_to(ROOT)} ({len(andes_svg) / 1024:.1f} KB)")
    print(f"Generated {HAITI_SVG_PATH.relative_to(ROOT)} ({len(haiti_svg) / 1024:.1f} KB)")

    update_ski_pages(andes_svg, haiti_svg)


if __name__ == "__main__":
    main()
