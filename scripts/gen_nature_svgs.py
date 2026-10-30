#!/usr/bin/env python3
"""
Procedural generator for the Nature of Waikiki biome illustrations.

Generates standalone SVG files in icons/nature/ and injects localized inline
SVGs into en/nature.html and hu/nature.html. Every illustration container in
the pages is marked with data-nature-svg="KEY"; the <svg> inside it is replaced.

Scenes
  transect     Sea-to-summit cross-section through eight biomes of the nation
  reef         Split-level Caribbean mangrove coast and Jardines coral reef
  rainforest   Amazonian river, canopy strata, emergent kapok trees
  highlands    Brazilia highlands: glacier, paramo, cloud forest, cataract
  mogotes      Atlas vignette: Vinales karst towers and tobacco valley
  enriquillo   Atlas vignette: hypersaline Lago Enriquillo with flamingos
  pantanal     Atlas vignette: flooded Pantanal savanna wetland
  cerrado      Atlas vignette: Cerrado savanna with flowering ipe trees
  lencois      Atlas vignette: white dunes and rain lagoons of Lencois
  caatinga     Atlas vignette: dry Caatinga thorn forest with mandacaru
  bluehole     Atlas vignette: Columbus Deep submarine karst sinkhole
  tepui        Atlas vignette: Monte Roraima sandstone tabletop tepui
  cataracts    Atlas vignette: Rio Esmeralda multi-tiered basalt cataracts

Usage
  python3 scripts/gen_nature_svgs.py
"""

from __future__ import annotations

import html
import math
import random
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "icons" / "nature"
TAU = math.tau


# ==============================================================================
# FORMAT HELPERS
# ==============================================================================
def n(v: float) -> str:
    """Format a number compactly with one decimal place."""
    r = round(float(v), 1)
    if r == int(r):
        return str(int(r))
    return "0" if f"{r:.1f}" == "-0.0" else f"{r:.1f}"


def P(points, close: bool = True) -> str:
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in points)
    return d + ("Z" if close else "")


def smooth(points, closed: bool = False, k: float = 1 / 6) -> str:
    """Catmull-Rom spline through points as a cubic Bezier path."""
    p = list(points)
    if len(p) < 3:
        return P(p, closed)
    p = ([p[-1]] + p + [p[0], p[1]]) if closed else ([p[0]] + p + [p[-1]])
    d = [f"M{n(p[1][0])},{n(p[1][1])}"]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        d.append(f"C{n(c1[0])},{n(c1[1])} {n(c2[0])},{n(c2[1])} {n(p2[0])},{n(p2[1])}")
    if closed:
        d.append("Z")
    return " ".join(d)


def el(tag: str, body: str | None = None, **a) -> str:
    parts = []
    for key, val in a.items():
        if val is None:
            continue
        name = key.rstrip("_").replace("_", "-")
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            val = n(val)
        parts.append(f'{name}="{val}"')
    attrs = (" " + " ".join(parts)) if parts else ""
    if body is None:
        return f"<{tag}{attrs}/>"
    return f"<{tag}{attrs}>{body}</{tag}>"


def g(items, **a) -> str:
    if isinstance(items, str):
        items = [items]
    flat = []
    for it in items:
        if isinstance(it, (list, tuple)):
            flat.extend(it)
        elif it:
            flat.append(it)
    return el("g", "".join(flat), **a)


def hx(c: str):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    ra, rb = hx(a), hx(b)
    return "#%02x%02x%02x" % tuple(round(ra[i] + (rb[i] - ra[i]) * t) for i in range(3))


def quad(p0, p1, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def quad_tan(p0, p1, p2, t):
    dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
    dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    m = math.hypot(dx, dy) or 1
    return dx / m, dy / m


def interp(points):
    """Return y(x) for a polyline sorted by x."""
    pts = sorted(points, key=lambda p: p[0])
    xs = [p[0] for p in pts]

    def f(x):
        if x <= xs[0]:
            return pts[0][1]
        if x >= xs[-1]:
            return pts[-1][1]
        lo, hi = 0, len(xs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        t = (x - xs[lo]) / ((xs[hi] - xs[lo]) or 1)
        return pts[lo][1] + (pts[hi][1] - pts[lo][1]) * t

    return f


# ==============================================================================
# SCENE BUILDER
# ==============================================================================
class Scene:
    def __init__(self, key: str, w: int, h: int, seed: int):
        self.key, self.w, self.h = key, w, h
        self.rng = random.Random(seed)
        self.defs: list[str] = []
        self.body: list[str] = []

    def id(self, name: str) -> str:
        return f"nt-{self.key}-{name}"

    def url(self, name: str) -> str:
        return f"url(#{self.id(name)})"

    def add(self, *items):
        for it in items:
            if isinstance(it, (list, tuple)):
                self.add(*it)
            elif it:
                self.body.append(it)

    @staticmethod
    def _stops(stops) -> str:
        out = []
        for st in stops:
            op = f' stop-opacity="{st[2]}"' if len(st) > 2 else ""
            out.append(f'<stop offset="{st[0]}" stop-color="{st[1]}"{op}/>')
        return "".join(out)

    def linear(self, name, stops, x1=0, y1=0, x2=0, y2=1) -> str:
        self.defs.append(
            f'<linearGradient id="{self.id(name)}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{self._stops(stops)}</linearGradient>'
        )
        return self.url(name)

    def radial(self, name, stops, cx=0.5, cy=0.5, r=0.5) -> str:
        self.defs.append(
            f'<radialGradient id="{self.id(name)}" cx="{cx}" cy="{cy}" r="{r}">{self._stops(stops)}</radialGradient>'
        )
        return self.url(name)

    def blur(self, name, sd) -> str:
        self.defs.append(
            f'<filter id="{self.id(name)}" x="-50%" y="-50%" width="200%" height="200%">'
            f'<feGaussianBlur stdDeviation="{sd}"/></filter>'
        )
        return self.url(name)

    def clip(self, name, d) -> str:
        self.defs.append(f'<clipPath id="{self.id(name)}"><path d="{d}"/></clipPath>')
        return self.url(name)

    def render(self, label: str) -> str:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" class="nature-ill" viewBox="0 0 {self.w} {self.h}" '
            f'role="img" aria-label="{html.escape(label, quote=True)}">'
        )
        lines = [head, "<defs>", *self.defs, "</defs>", *self.body, "</svg>"]
        return "\n".join(lines)


# ==============================================================================
# ATMOSPHERE & LANDSCAPE PRIMITIVES
# ==============================================================================
def ridge(rng, keys, rough, depth=5):
    out = [keys[0]]
    for a, b in zip(keys, keys[1:]):
        seg = [a, b]
        d = rough
        for _ in range(depth):
            new = [seg[0]]
            for p, q in zip(seg, seg[1:]):
                new += [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + rng.uniform(-d, d)), q]
            seg = new
            d *= 0.52
        out += seg[1:]
    return out


def mountain(s: Scene, name, keys, base, fill, shade="#1f3348", shade_op=0.38, snow=None,
             snow_col="#f4f8fc", rough=14, depth=5, gullies=True, tongue=0.22):
    """Realistic multi-faceted mountain massif with arête ridges, rock strata, snow fields, and couloirs."""
    rng = s.rng
    r = ridge(rng, keys, rough, depth)
    poly = r + [(r[-1][0], base), (r[0][0], base)]
    d = P(poly)
    clip = s.clip(name, d)
    lit_col = mix(fill, "#fff8eb", 0.18)
    mid_shade = mix(fill, shade, 0.45)
    inner = [
        # Sunlit base rock tone
        el("path", d=d, fill=lit_col, opacity=0.32),
    ]

    # Identify peaks and valleys for 3D ridge facets
    peaks = [i for i in range(1, len(r) - 1) if r[i][1] <= r[i - 1][1] and r[i][1] <= r[i + 1][1]]
    sig = [i for i in peaks if r[i][1] == min(p[1] for p in r[max(0, i - 5):i + 6])]

    # Stepped geological rock strata bands across the massif
    for band in range(5):
        sy_off = 18 + band * 28
        pts = [(px, py + sy_off + 4 * math.sin(px * 0.025 + band * 1.3)) for px, py in r[::2]]
        if len(pts) > 2:
            band_poly = pts + [(pts[-1][0], pts[-1][1] + 9), (pts[0][0], pts[0][1] + 9)]
            inner.append(el("path", d=P(band_poly), fill=mid_shade, opacity=0.16))

    # Right-flank 3D shadow facets from every prominent peak with irregular arête spines and secondary spurs
    for idx, i in enumerate(sig):
        nxt = sig[idx + 1] if idx + 1 < len(sig) else len(r) - 1
        j = max(range(i, nxt + 1), key=lambda k: r[k][1])
        if j <= i:
            continue
        px, py = r[i]
        vx, vy = r[j]
        foot = px + (base - py) * rng.uniform(0.16, 0.32)
        spine = [(px, py)]
        for st in range(1, 8):
            t = st / 7
            sx = px + (foot - px) * t + rng.uniform(-8, 8) * (1 - abs(2 * t - 1))
            sy = py + (base - py) * t
            spine.append((sx, sy))
        v_foot = vx + (base - vy) * 0.20
        shadow_poly = r[i:j + 1] + [(v_foot, base)] + spine[::-1]
        inner.append(el("path", d=P(shadow_poly), fill=shade, opacity=shade_op))
        # Secondary mid-tone rock facet inside the shadow face for 3D relief
        mid_spine = [(px + (vx - px) * 0.35, py + (vy - py) * 0.35)]
        for st in range(1, 5):
            t = st / 4
            mid_spine.append((px + (v_foot - px) * (0.35 + 0.45 * t) + rng.uniform(-5, 5), py + (base - py) * (0.25 + 0.75 * t)))
        inner.append(el("path", d=P(mid_spine + [(v_foot, base), spine[-1]]), fill=shade, opacity=shade_op * 0.45))
        # Sunlit arête highlight along the left of the main spine
        lit_spine = [(px, py)] + [(sx - rng.uniform(7, 18), sy) for sx, sy in spine[1:-1]] + [(foot - 16, base)]
        inner.append(el("path", d=P(spine + lit_spine[::-1]), fill=mix(fill, "#ffffff", 0.26), opacity=0.32))

    # Snow cap with sunlit and shadowed facets and couloir fingers (strictly clipped to snow_d!)
    if snow is not None:
        xs, xe = r[0][0], r[-1][0]
        steps = max(10, int((xe - xs) / 5.0))
        line = []
        for i in range(steps + 1):
            x = xs + (xe - xs) * i / steps
            y = snow + rng.uniform(-6, 6) + 5 * math.sin(x * 0.04)
            if rng.random() < tongue:
                y += rng.uniform(18, 52)
            line.append((x, y))
        snow_d = P([(xs, -20), (xe, -20)] + line[::-1])
        snow_clip = s.clip(f"{name}-snow", snow_d)
        snow_shades = [el("path", d=snow_d, fill=snow_col)]
        for idx, i in enumerate(sig):
            nxt = sig[idx + 1] if idx + 1 < len(sig) else len(r) - 1
            j = max(range(i, nxt + 1), key=lambda k: r[k][1])
            if j <= i or r[i][1] > snow + 40:
                continue
            px, py = r[i]
            vx, vy = r[j]
            sh_snow = r[i:j + 1] + [(vx + 22, snow + 65), (px + 6, snow + 65)]
            snow_shades.append(el("path", d=P(sh_snow), fill="#a8c2dc", opacity=0.62))
        inner.append(g(snow_shades, clip_path=snow_clip))

    # Realistic rock couloirs & talus chutes (short, natural rock fractures following slope)
    if gullies:
        chutes_dark, chutes_lit = [], []
        for k in range(2, len(r) - 2, 3):
            if rng.random() < 0.42:
                continue
            x, y = r[k]
            length = min(55, (base - y) * rng.uniform(0.22, 0.48))
            if length < 10:
                continue
            dx = rng.uniform(-8, 10)
            chutes_dark.append(f"M{n(x)},{n(y + 3)} l{n(dx * 0.45)},{n(length * 0.5)} l{n(dx * 0.55)},{n(length * 0.5)}")
            if snow is not None and y < snow + 20:
                chutes_lit.append(f"M{n(x - 1.2)},{n(y + 3)} l{n(dx * 0.4)},{n(length * 0.45)}")
        if chutes_dark:
            inner.append(el("path", d=" ".join(chutes_dark), fill="none", stroke=shade, stroke_width=1.0, opacity=0.26))
        if chutes_lit:
            inner.append(el("path", d=" ".join(chutes_lit), fill="none", stroke="#ffffff", stroke_width=0.9, opacity=0.48))

    # Rim highlight along sunlit ridge segments
    rim = []
    for k in range(len(r) - 1):
        if r[k + 1][1] < r[k][1]:
            rim.append(f"M{n(r[k][0])},{n(r[k][1])} L{n(r[k + 1][0])},{n(r[k + 1][1])}")
    if rim:
        inner.append(el("path", d=" ".join(rim), fill="none", stroke="#fffdf7", stroke_width=1.2, opacity=0.45))

    return [el("path", d=d, fill=fill), g(inner, clip_path=clip)], r


def hill(s: Scene, keys, base, fill, rough=6, depth=4):
    r = ridge(s.rng, keys, rough, depth)
    d = smooth(r) + f" L{n(r[-1][0])},{n(base)} L{n(r[0][0])},{n(base)}Z"
    hi = smooth([(x, y + 3) for x, y in r])
    return g([
        el("path", d=d, fill=fill),
        el("path", d=hi, fill="none", stroke=mix(fill, "#fff8e0", 0.25), stroke_width=1.5, opacity=0.45),
    ]), r


def sky(s: Scene, stops, h=None):
    s.add(el("rect", width=s.w, height=h or s.h, fill=s.linear("sky", stops)))


def sun(s: Scene, x, y, r, glow="#fff1c9"):
    s.add(el("circle", cx=x, cy=y, r=r * 6.5, fill=s.radial("sun", [
        (0, "#fffdf2", 0.98),
        (0.14, glow, 0.68),
        (0.42, glow, 0.22),
        (1, glow, 0),
    ])))
    s.add(el("circle", cx=x, cy=y, r=r * 1.45, fill="#fffdf5", opacity=0.55))
    s.add(el("circle", cx=x, cy=y, r=r, fill="#fffef9"))


def cloud(rng, x, y, w, col="#ffffff", shade="#d4e0ec", op=0.94, cls="drift"):
    """Realistic multi-layered cumulus cloud bank with sculpted billowy silhouette and shaded underbelly."""
    h = w * 0.26
    k = max(7, int(w / 14))
    # Build billowy upper contour and flat-ish base contour
    top_pts = [(x - w * 0.52, y + h * 0.18)]
    for i in range(k):
        t = (i + 0.5) / k
        env = math.sin(math.pi * t) ** 0.75
        px = x + (t - 0.5) * w * 0.96 + rng.uniform(-w * 0.02, w * 0.02)
        py = y - h * env * rng.uniform(0.75, 1.12)
        top_pts.append((px, py))
    top_pts.append((x + w * 0.52, y + h * 0.18))
    bot_pts = [
        (x + w * 0.46, y + h * 0.25),
        (x + w * 0.18, y + h * 0.30),
        (x - w * 0.18, y + h * 0.29),
        (x - w * 0.46, y + h * 0.24),
    ]
    main_d = smooth(top_pts + bot_pts, closed=True, k=0.18)

    # Shaded lower billow layer
    shade_pts = [(px, py * 0.35 + (y + h * 0.18) * 0.65) for px, py in top_pts[1:-1]]
    shade_d = smooth([(x - w * 0.48, y + h * 0.18)] + shade_pts + [(x + w * 0.48, y + h * 0.18)] + bot_pts, closed=True, k=0.18)

    # Internal volume puffs for 3D cumulus texture
    puffs_mid, puffs_lit = [], []
    for i in range(k + 2):
        t = i / (k + 1)
        env = math.sin(math.pi * t)
        cx_ = x + (t - 0.5) * w * 0.82 + rng.uniform(-4, 4)
        cy_ = y - h * env * rng.uniform(0.25, 0.72)
        rr = w * (0.065 + 0.085 * env) * rng.uniform(0.85, 1.15)
        puffs_mid.append(el("ellipse", cx=cx_, cy=cy_ + rr * 0.22, rx=rr * 1.18, ry=rr * 0.82))
        puffs_lit.append(el("ellipse", cx=cx_ - rr * 0.12, cy=cy_ - rr * 0.08, rx=rr * 0.95, ry=rr * 0.68))

    # Wispy trailing anvil/cirrus tendrils at edges
    wisps = [
        el("ellipse", cx=x - w * 0.46, cy=y + h * 0.2, rx=w * 0.16, ry=h * 0.11, fill=col, opacity=0.65),
        el("ellipse", cx=x + w * 0.46, cy=y + h * 0.19, rx=w * 0.18, ry=h * 0.11, fill=col, opacity=0.65),
    ]
    return g([
        *wisps,
        el("path", d=main_d, fill=col),
        el("path", d=shade_d, fill=shade, opacity=0.65),
        g(puffs_mid, fill=mix(col, shade, 0.32), opacity=0.55),
        g(puffs_lit, fill=col),
    ], opacity=op, class_=cls, style=f"animation-delay:{n(-rng.uniform(0, 14))}s")


def mist(s: Scene, x, y, rx, ry, op=0.55, col="#ffffff", blur="mist", cls="drift"):
    return el("ellipse", cx=x, cy=y, rx=rx, ry=ry, fill=col, opacity=op, filter=s.url(blur), class_=cls,
              style=f"animation-delay:{n(-s.rng.uniform(0, 16))}s")


# ==============================================================================
# VEGETATION PRIMITIVES
# ==============================================================================
def _foliage_blob(rng, cx, cy, rx, ry, lobes=8):
    """Compact scalloped botanical foliage cluster path using quadratic Bezier lobes."""
    anchors = []
    ctrl = []
    for i in range(lobes):
        a0 = TAU * i / lobes
        am = TAU * (i + 0.5) / lobes
        r0 = rng.uniform(0.76, 0.88)
        rm = rng.uniform(1.06, 1.22)
        anchors.append((cx + math.cos(a0) * rx * r0, cy + math.sin(a0) * ry * r0))
        ctrl.append((cx + math.cos(am) * rx * rm, cy + math.sin(am) * ry * rm))
    segs = [f"M{n(anchors[0][0])},{n(anchors[0][1])}"]
    for i in range(lobes):
        nxt = anchors[(i + 1) % lobes]
        c = ctrl[i]
        segs.append(f"Q{n(c[0])},{n(c[1])} {n(nxt[0])},{n(nxt[1])}")
    segs.append("Z")
    return " ".join(segs)


def crown(rng, cx, cy, r, cols, k=7, flat=0.76, detail=True):
    """Realistic multi-tiered botanical tree crown with deep shadow, mid-foliage, sunlit boughs, and leaf highlights."""
    dark, mid, light = cols
    deep = mix(dark, "#08140c", 0.38)
    spec = mix(light, "#f6f7b0", 0.32)
    d_lobes = 7 if detail else 6
    paths = [[], [], [], []]

    # Tier 0: Deep shadow underside boughs
    for i in range(max(2, k // 2 + 1)):
        a = math.pi * (0.1 + 0.8 * i / max(1, k // 2)) + rng.uniform(-0.2, 0.2)
        d = r * rng.uniform(0.32, 0.62)
        rr = r * rng.uniform(0.45, 0.62)
        paths[0].append(_foliage_blob(rng, cx + math.cos(a) * d * 1.15, cy + abs(math.sin(a)) * d * flat + r * 0.14,
                                      rr * 1.15, rr * flat, lobes=d_lobes))

    # Tier 1: Dark structural canopy masses
    for _ in range(k):
        a, d = rng.uniform(0, TAU), rng.uniform(0, r * 0.58)
        rr = r * rng.uniform(0.42, 0.58)
        paths[1].append(_foliage_blob(rng, cx + math.cos(a) * d * 1.18, cy + math.sin(a) * d * flat + r * 0.04,
                                      rr * 1.12, rr * flat, lobes=d_lobes))

    # Tier 2: Mid-tone sunlit leaf clusters
    for _ in range(max(3, k - 1)):
        a, d = rng.uniform(-math.pi * 0.95, math.pi * 0.35), rng.uniform(0, r * 0.48)
        rr = r * rng.uniform(0.32, 0.48)
        paths[2].append(_foliage_blob(rng, cx + math.cos(a) * d * 1.1 - r * 0.08,
                                      cy + math.sin(a) * d * flat - r * 0.08,
                                      rr * 1.1, rr * flat, lobes=d_lobes))

    # Tier 3: Upper canopy highlights
    for _ in range(max(2, k // 2 + 1)):
        hx_ = cx - r * 0.22 + rng.uniform(-r * 0.38, r * 0.38)
        hy_ = cy - r * 0.24 + rng.uniform(-r * 0.18, r * 0.14)
        rr = r * rng.uniform(0.18, 0.30)
        paths[3].append(_foliage_blob(rng, hx_, hy_, rr * 1.15, rr * flat, lobes=6))

    out = [
        el("path", d=" ".join(paths[0]), fill=deep),
        el("path", d=" ".join(paths[1]), fill=dark),
        el("path", d=" ".join(paths[2]), fill=mid),
        el("path", d=" ".join(paths[3]), fill=light),
    ]
    if detail:
        sprays = []
        for _ in range(max(3, k - 1)):
            a = rng.uniform(-math.pi * 1.05, math.pi * 0.15)
            px = cx + math.cos(a) * r * rng.uniform(0.55, 0.92)
            py = cy + math.sin(a) * r * flat * rng.uniform(0.55, 0.92)
            sprays.append(el("ellipse", cx=px, cy=py, rx=max(1.5, r * 0.08), ry=max(1.0, r * 0.045),
                             transform=f"rotate({n(math.degrees(a))} {n(px)} {n(py)})"))
        out.append(g(sprays, fill=spec, opacity=0.75))
    return g(out)


def trunk(x, yb, yt, wb, wt, col, bend=0.0, buttress=False):
    shade = mix(col, "#000000", 0.32)
    lit = mix(col, "#d8c3a5", 0.22)
    d = (f"M{n(x - wb / 2)},{n(yb)} Q{n(x - wb / 2 + bend * 0.5)},{n((yb + yt) / 2)} {n(x - wt / 2 + bend)},{n(yt)} "
         f"L{n(x + wt / 2 + bend)},{n(yt)} Q{n(x + wb / 2 + bend * 0.5)},{n((yb + yt) / 2)} {n(x + wb / 2)},{n(yb)}Z")
    d_shade = (f"M{n(x)},{n(yb)} Q{n(x + bend * 0.5)},{n((yb + yt) / 2)} {n(x + bend)},{n(yt)} "
               f"L{n(x + wt / 2 + bend)},{n(yt)} Q{n(x + wb / 2 + bend * 0.5)},{n((yb + yt) / 2)} {n(x + wb / 2)},{n(yb)}Z")
    out = [el("path", d=d, fill=col), el("path", d=d_shade, fill=shade, opacity=0.55)]
    # Bark vertical texture grooves
    for f in (-0.25, 0.05, 0.28):
        out.append(el("path", d=f"M{n(x + wb * f)},{n(yb)} Q{n(x + wb * f + bend * 0.5)},{n((yb + yt) / 2)} {n(x + wt * f + bend)},{n(yt)}",
                      stroke=lit if f < 0 else shade, stroke_width=0.9, fill="none", opacity=0.45))
    if buttress:
        # Multi-fin tropical tabular buttress roots
        out.append(el("path", fill=col, d=(
            f"M{n(x - wb * 2.6)},{n(yb)} Q{n(x - wb * 0.85)},{n(yb - wb * 0.5)} {n(x - wb * 0.38)},{n(yb - wb * 3.4)} "
            f"L{n(x + wb * 0.38)},{n(yb - wb * 3.4)} Q{n(x + wb * 0.85)},{n(yb - wb * 0.5)} {n(x + wb * 2.6)},{n(yb)}Z")))
        out.append(el("path", fill=shade, opacity=0.5, d=(
            f"M{n(x - wb * 0.2)},{n(yb)} Q{n(x - wb * 0.1)},{n(yb - wb * 1.5)} {n(x + wb * 0.15)},{n(yb - wb * 3.2)} "
            f"L{n(x + wb * 0.38)},{n(yb - wb * 3.4)} Q{n(x + wb * 0.85)},{n(yb - wb * 0.5)} {n(x + wb * 2.6)},{n(yb)}Z")))
        out.append(el("path", fill=lit, opacity=0.35, d=(
            f"M{n(x - wb * 2.5)},{n(yb)} Q{n(x - wb * 1.1)},{n(yb - wb * 0.6)} {n(x - wb * 0.38)},{n(yb - wb * 3.2)} "
            f"L{n(x - wb * 0.15)},{n(yb - wb * 2.8)} Q{n(x - wb * 0.6)},{n(yb - wb * 0.4)} {n(x - wb * 1.2)},{n(yb)}Z")))
    return out


def broadleaf_tree(rng, x, yb, h, r, cols, trunk_col="#5b4632", flat=0.76, k=8, emergent=False):
    top = yb - h
    bend = rng.uniform(-r * 0.18, r * 0.18)
    out = trunk(x, yb, top + r * 0.38, max(3.5, r * 0.22), max(2.2, r * 0.11), trunk_col, bend=bend, buttress=emergent)
    if emergent:
        subs = [(-0.85, 0.18, 0.58), (0.85, 0.15, 0.56), (-0.42, -0.12, 0.65), (0.45, -0.10, 0.62), (0.0, -0.26, 0.68)]
        tx = x + bend
        ty = top + r * 0.42
        for dx, dy, sc in subs:
            ex, ey = x + dx * r, top + dy * r + r * 0.12
            cx_, cy_ = tx + dx * r * 0.38, ty - r * 0.08
            w_b = max(2.0, r * 0.08 * sc)
            out.append(el("path", d=f"M{n(tx)},{n(ty)} Q{n(cx_)},{n(cy_)} {n(ex)},{n(ey)}",
                          fill="none", stroke=trunk_col, stroke_width=w_b, stroke_linecap="round"))
            out.append(el("path", d=f"M{n(tx)},{n(ty - 1)} Q{n(cx_)},{n(cy_ - 1.5)} {n(ex)},{n(ey - 1)}",
                          fill="none", stroke=mix(trunk_col, "#dfd0b8", 0.25), stroke_width=w_b * 0.4, stroke_linecap="round"))
        # Hanging aerial roots / vines from emergent boughs
        vines = []
        for dx, dy, _ in subs[:2]:
            vx = x + dx * r * 0.72
            vy = top + dy * r + r * 0.2
            vines.append(f"M{n(vx)},{n(vy)} q{n(rng.uniform(-4, 4))},{n(h * 0.22)} {n(rng.uniform(-6, 6))},{n(h * 0.45)}")
        out.append(el("path", d=" ".join(vines), stroke="#2f4d27", stroke_width=1.1, fill="none", opacity=0.7))
        for dx, dy, sc in subs:
            out.append(crown(rng, x + dx * r, top + dy * r, r * sc, cols, k=k, flat=0.52))
    else:
        out.append(crown(rng, x + bend, top, r, cols, k=k, flat=flat))
    return g(out)


def palm(rng, x, y, h, lean, L, cols=("#26582c", "#4b8c3f"), trunk_col="#8b6b4c", nfr=12, royal=False,
         coconuts=True, sway=True, wb=None):
    """Realistic coconut or Cuban royal palm with ringed 3D trunk, crownshaft, and pinnate fronds."""
    dark, light = cols
    hl_leaf = mix(light, "#d8e874", 0.28)
    tx, ty = x + lean, y - h
    ctrl = (x + lean * 0.18, y - h * 0.55)
    wb = wb or max(3.2, h * 0.048)
    wt = wb * (0.58 if royal else 0.68)
    left, right, mid_line, rings = [], [], [], []
    steps = 18
    for i in range(steps + 1):
        t = i / steps
        bx, by = quad((x, y), ctrl, (tx, ty), t)
        w = wb * (1 - t) + wt * t
        if royal:
            w += wb * 0.38 * math.sin(math.pi * min(1, t * 1.55)) * (1 - t)
        left.append((bx - w / 2, by))
        right.append((bx + w / 2, by))
        mid_line.append((bx + w * 0.08, by))
        if 0 < i < steps:
            rings.append(f"M{n(bx - w / 2)},{n(by)} Q{n(bx)},{n(by + 1.2)} {n(bx + w / 2)},{n(by + 0.5)}")
    out = [
        # Flared root base
        el("ellipse", cx=x, cy=y + 1, rx=wb * 0.72, ry=wb * 0.25, fill=mix(trunk_col, "#000000", 0.35)),
        el("path", d=P(left + right[::-1]), fill=trunk_col),
        el("path", d=P(mid_line + right[::-1]), fill="#000000", opacity=0.22),
        el("path", d=" ".join(rings), stroke=mix(trunk_col, "#000000", 0.35), stroke_width=0.75, opacity=0.55, fill="none"),
    ]
    if royal:
        cs = h * 0.14
        out.append(el("path", fill="#6c9a42", d=P([
            (tx - wt * 0.55, ty), (tx + wt * 0.55, ty),
            (tx + wt * 0.42, ty - cs), (tx - wt * 0.42, ty - cs)
        ])))
        out.append(el("path", fill="#4a732b", opacity=0.45, d=P([
            (tx, ty), (tx + wt * 0.55, ty),
            (tx + wt * 0.42, ty - cs), (tx, ty - cs)
        ])))
        ty -= cs

    fronds_back, fronds_mid, fronds_front = [], [], []
    for i in range(nfr):
        a = math.radians(-200 + 220 * i / max(1, nfr - 1) + rng.uniform(-7, 7))
        dx, dy = math.cos(a), math.sin(a)
        Lf = L * rng.uniform(0.84, 1.12)
        end = (tx + dx * Lf, ty + dy * Lf * 0.48 + Lf * 0.58 * (1 - abs(dy)) + (Lf * 0.26 if dy > 0 else 0))
        c = (tx + dx * Lf * 0.54, ty + dy * Lf * 0.52 - Lf * 0.18)
        rachis = f"M{n(tx)},{n(ty)} Q{n(c[0])},{n(c[1])} {n(end[0])},{n(end[1])}"
        leaf_polys = []
        n_leaflets = 16
        for j in range(n_leaflets):
            t = 0.08 + 0.89 * j / (n_leaflets - 1)
            px, py = quad((tx, ty), c, end, t)
            ux, uy = quad_tan((tx, ty), c, end, t)
            nx_, ny_ = -uy, ux
            ln = Lf * 0.26 * math.sin(math.pi * min(1.0, 0.2 + t * 0.85))
            for side in (1, -1):
                tip_x = px + nx_ * side * ln * 0.85 + ux * ln * 0.35
                tip_y = py + ny_ * side * ln * 0.7 + ln * 0.62
                mid_x = (px + tip_x) * 0.5 + ux * 1.4
                mid_y = (py + tip_y) * 0.5 - 1.1
                leaf_polys.append(f"M{n(px)},{n(py)} Q{n(mid_x)},{n(mid_y)} {n(tip_x)},{n(tip_y)}")
        layer_idx = i % 3
        col_f = dark if layer_idx == 0 else (light if layer_idx == 1 else hl_leaf)
        frond = [
            el("path", d=" ".join(leaf_polys), stroke=col_f, stroke_width=1.45, fill="none", stroke_linecap="round"),
            el("path", d=rachis, stroke=mix(col_f, "#1a2810", 0.35), stroke_width=1.5, fill="none", stroke_linecap="round"),
        ]
        if layer_idx == 0:
            fronds_back.extend(frond)
        elif layer_idx == 1:
            fronds_mid.extend(frond)
        else:
            fronds_front.extend(frond)

    crown_g = [g(fronds_back), g(fronds_mid)]
    if coconuts and not royal:
        c_items = []
        for ox, oy in ((-wb * 0.55, 1), (wb * 0.55, 1.5), (0, wb * 0.65), (-wb * 0.2, wb * 0.3), (wb * 0.25, wb * 0.35)):
            c_items.append(el("circle", cx=tx + ox, cy=ty + 3.5 + oy, r=wb * 0.48, fill="#5c3d1b"))
            c_items.append(el("circle", cx=tx + ox - 0.6, cy=ty + 3.0 + oy, r=wb * 0.22, fill="#8a6234"))
        crown_g.append(g(c_items))
    crown_g.append(g(fronds_front))
    style = f"transform-origin:{n(tx)}px {n(ty)}px;animation-delay:{n(-rng.uniform(0, 6))}s"
    out.append(g(crown_g, class_="sway" if sway else None, style=style) if sway else g(crown_g))
    return g(out)


def tufts(rng, x0, x1, ground, count, h, col, width=1.1, op=1.0):
    segs = []
    segs_hi = []
    hi_col = mix(col, "#fff6c8", 0.32)
    for idx in range(count):
        x = rng.uniform(x0, x1)
        y = ground(x) + 1
        for b in range(rng.randint(4, 7)):
            dx = rng.uniform(-h * 0.55, h * 0.55)
            hh = h * rng.uniform(0.5, 1.15)
            cmd = f"M{n(x)},{n(y)} q{n(dx * 0.25)},{n(-hh * 0.62)} {n(dx)},{n(-hh)}"
            if b == 0 and idx % 2 == 0:
                segs_hi.append(cmd)
            else:
                segs.append(cmd)
    return g([
        el("path", d=" ".join(segs), stroke=col, stroke_width=width, fill="none", stroke_linecap="round", opacity=op),
        el("path", d=" ".join(segs_hi), stroke=hi_col, stroke_width=width * 0.85, fill="none", stroke_linecap="round", opacity=op * 0.85),
    ])


def canopy_band(s: Scene, x0, x1, ground, count, rmin, rmax, cols, lift=0.0, flat=0.76, k=5, detail=False):
    rng = s.rng
    trees = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        r = rng.uniform(rmin, rmax)
        trees.append((ground(x) - lift - r * 0.38 + rng.uniform(-r * 0.18, r * 0.18), x, r))
    trees.sort()
    return [crown(rng, x, y, r, cols, k=k, flat=flat, detail=detail) for y, x, r in trees]


def fern(rng, x, y, L, col, n_fronds=7, droop=0.48):
    segs_dark, segs_light = [], []
    dark = mix(col, "#0d2612", 0.3)
    light = mix(col, "#b8e068", 0.25)
    for i in range(n_fronds):
        a = math.radians(-165 + 150 * i / max(1, n_fronds - 1) + rng.uniform(-5, 5))
        Lf = L * rng.uniform(0.78, 1.08)
        end = (x + math.cos(a) * Lf, y + math.sin(a) * Lf * 0.58 + Lf * droop * (1 - abs(math.sin(a))))
        c = (x + math.cos(a) * Lf * 0.5, y + math.sin(a) * Lf * 0.68 - Lf * 0.12)
        target = segs_dark if i % 2 == 0 else segs_light
        target.append(f"M{n(x)},{n(y)} Q{n(c[0])},{n(c[1])} {n(end[0])},{n(end[1])}")
        for j in range(11):
            t = 0.12 + 0.82 * j / 10
            px, py = quad((x, y), c, end, t)
            ux, uy = quad_tan((x, y), c, end, t)
            ln = Lf * 0.15 * math.sin(math.pi * (0.2 + 0.75 * (1 - t)))
            for side in (1, -1):
                target.append(f"M{n(px)},{n(py)} l{n(-uy * side * ln + ux * ln * 0.28)},{n(ux * side * ln + ln * 0.25)}")
    return g([
        el("path", d=" ".join(segs_dark), stroke=dark, stroke_width=1.35, fill="none", stroke_linecap="round"),
        el("path", d=" ".join(segs_light), stroke=light, stroke_width=1.2, fill="none", stroke_linecap="round"),
    ])


def heliconia(x, y, h, stem="#2f5e25", bract="#d93824", tip="#f5c72c"):
    """Detailed tropical Heliconia rostrata / bihai with broad paddle leaves and layered claw bracts."""
    out = [
        # Broad banana-like paddle leaves with central midribs
        el("path", fill="#2b5e24", d=(
            f"M{n(x)},{n(y - h * 0.15)} Q{n(x - h * 0.52)},{n(y - h * 0.45)} {n(x - h * 0.72)},{n(y - h * 0.18)} "
            f"Q{n(x - h * 0.38)},{n(y - h * 0.02)} {n(x)},{n(y - h * 0.12)}Z")),
        el("path", fill="#428236", d=(
            f"M{n(x)},{n(y - h * 0.25)} Q{n(x + h * 0.55)},{n(y - h * 0.58)} {n(x + h * 0.74)},{n(y - h * 0.30)} "
            f"Q{n(x + h * 0.38)},{n(y - h * 0.10)} {n(x)},{n(y - h * 0.22)}Z")),
        el("path", fill="#549842", d=(
            f"M{n(x)},{n(y - h * 0.32)} Q{n(x - h * 0.38)},{n(y - h * 0.72)} {n(x - h * 0.48)},{n(y - h * 0.52)} "
            f"Q{n(x - h * 0.22)},{n(y - h * 0.28)} {n(x)},{n(y - h * 0.30)}Z")),
        el("path", d=f"M{n(x)},{n(y)} Q{n(x - 3)},{n(y - h * 0.5)} {n(x + 2)},{n(y - h)}", stroke=stem, stroke_width=2.2, fill="none"),
    ]
    bracts_red, bracts_tip = [], []
    for i in range(6):
        by = y - h * 0.42 - i * h * 0.095
        side = 1 if i % 2 else -1
        bx = x + 1 + (i * 0.2)
        bracts_red.append(f"M{n(bx)},{n(by)} Q{n(bx + side * 8)},{n(by - 1)} {n(bx + side * 12)},{n(by - 5)} Q{n(bx + side * 5)},{n(by - 7)} {n(bx)},{n(by - 4.5)}Z")
        bracts_tip.append(f"M{n(bx + side * 7)},{n(by - 3.2)} L{n(bx + side * 12)},{n(by - 5)} L{n(bx + side * 8)},{n(by - 5.8)}Z")
    out.append(el("path", d=" ".join(bracts_red), fill=bract))
    out.append(el("path", d=" ".join(bracts_tip), fill=tip))
    return g(out)


def bromeliad(rng, x, y, s, col="#689a38", flower="#e63e2b"):
    leaves_back, leaves_front = [], []
    for i in range(11):
        a = math.radians(-175 + 170 * i / 10)
        ex, ey = x + math.cos(a) * s * 1.15, y + math.sin(a) * s * 0.65
        cx_, cy_ = x + math.cos(a) * s * 0.55, y + math.sin(a) * s * 1.05
        d = f"M{n(x - 1.5)},{n(y)} Q{n(cx_)},{n(cy_)} {n(ex)},{n(ey)} Q{n(cx_)},{n(cy_ + 2.5)} {n(x + 1.5)},{n(y)}Z"
        (leaves_back if i % 2 == 0 else leaves_front).append(el("path", d=d, fill=mix(col, "#1e3d14", 0.25) if i % 2 == 0 else col))
    spike = [
        el("path", d=f"M{n(x - 2.5)},{n(y - 1)} Q{n(x - 3)},{n(y - s * 0.6)} {n(x)},{n(y - s * 1.05)} Q{n(x + 3)},{n(y - s * 0.6)} {n(x + 2.5)},{n(y - 1)}Z", fill=flower),
        el("circle", cx=x, cy=y - s * 0.95, r=1.4, fill="#ffdf4f"),
    ]
    return g([*leaves_back, *spike, *leaves_front])


def ipe(rng, x, y, h, bloom="#f4c424", bloom2="#d99412", trunk_col="#473628"):
    """Twisted Cerrado Handroanthus (Ipê-amarelo / Ipê-rosa) with gnarled bark, forked boughs, and trumpet-flower crown."""
    tx = x + rng.uniform(-h * 0.08, h * 0.08)
    ty = y - h * 0.56
    lit_bark = mix(trunk_col, "#c8b294", 0.28)
    out = [el("ellipse", cx=x, cy=y + 1, rx=h * 0.24, ry=h * 0.035, fill="#000000", opacity=0.2)]
    out += trunk(x, y, ty, max(4.2, h * 0.09), max(2.8, h * 0.05), trunk_col, bend=tx - x)
    subs = [
        (-0.48, -0.26, 0.56),
        (0.46, -0.24, 0.54),
        (-0.20, -0.40, 0.66),
        (0.22, -0.36, 0.62),
        (0.0, -0.44, 0.58),
    ]
    for dx, dy, sc in subs:
        bx, by = tx + dx * h, ty + dy * h
        c1x, c1y = tx + dx * h * 0.25 + rng.uniform(-5, 5), ty - h * 0.14
        c2x, c2y = tx + dx * h * 0.72 + rng.uniform(-5, 5), by + h * 0.08
        wb = max(1.8, h * 0.042 * sc)
        d_b = f"M{n(tx)},{n(ty + 3)} C{n(c1x)},{n(c1y)} {n(c2x)},{n(c2y)} {n(bx)},{n(by)}"
        out.append(el("path", d=d_b, stroke=trunk_col, stroke_width=wb, fill="none", stroke_linecap="round"))
        out.append(el("path", d=d_b, stroke=lit_bark, stroke_width=wb * 0.35, fill="none", stroke_linecap="round", opacity=0.55))
        # Secondary twig fork
        tx2, ty2 = bx + dx * h * 0.18, by - h * 0.08
        out.append(el("path", d=f"M{n(( tx + bx ) * 0.5)},{n(( ty + by ) * 0.5)} Q{n(bx)},{n(by)} {n(tx2)},{n(ty2)}",
                      stroke=trunk_col, stroke_width=wb * 0.55, fill="none", stroke_linecap="round"))
    for dx, dy, sc in subs:
        out.append(crown(rng, tx + dx * h, ty + dy * h, h * 0.25 * sc,
                         (mix(bloom2, "#6e3400", 0.28), bloom2, mix(bloom, "#ffffff", 0.38)), k=7, flat=0.60))
    # Fallen golden/pink blossoms carpeting the ground beneath the tree
    petals = [el("ellipse", cx=x + rng.uniform(-h * 0.44, h * 0.44), cy=y + rng.uniform(-2, 5),
                 rx=rng.uniform(1.6, 2.8), ry=rng.uniform(0.7, 1.2), fill=bloom if i % 2 == 0 else bloom2)
              for i in range(14)]
    out.append(g(petals, opacity=0.85))
    return g(out)


def gnarled_tree(rng, x, y, h, leaf=("#2f4f22", "#4c7232", "#789e4c"), trunk_col="#3d2f24"):
    """Tortuous fire-adapted Cerrado tree (Qualea / Caryocar) with corky S-curved trunk and umbrella crown."""
    tx = x + rng.uniform(-h * 0.14, h * 0.14)
    ty = y - h * 0.54
    lit_bark = mix(trunk_col, "#ccb89e", 0.28)
    out = [el("ellipse", cx=x, cy=y + 1, rx=h * 0.22, ry=h * 0.035, fill="#000000", opacity=0.2)]
    out += trunk(x, y, ty, max(3.8, h * 0.085), max(2.4, h * 0.048), trunk_col, bend=tx - x)
    branches = [
        (-0.46, -0.82, 0.21),
        (0.42, -0.84, 0.20),
        (-0.14, -0.96, 0.23),
        (0.18, -0.93, 0.19),
    ]
    for dx, dy, r_sc in branches:
        cx, cy = tx + dx * h, y + dy * h
        c1x = tx - dx * h * 0.15 + rng.uniform(-6, 6)
        c1y = ty + (cy - ty) * 0.35
        c2x = tx + dx * h * 0.78 + rng.uniform(-6, 6)
        c2y = ty + (cy - ty) * 0.72
        wb = max(1.6, h * 0.038)
        d_b = f"M{n(tx)},{n(ty + 3)} C{n(c1x)},{n(c1y)} {n(c2x)},{n(c2y)} {n(cx)},{n(cy)}"
        out.append(el("path", d=d_b, stroke=trunk_col, stroke_width=wb, fill="none", stroke_linecap="round"))
        out.append(el("path", d=d_b, stroke=lit_bark, stroke_width=wb * 0.35, fill="none", stroke_linecap="round", opacity=0.5))
    for dx, dy, r_sc in branches:
        cx, cy = tx + dx * h, y + dy * h
        out.append(crown(rng, cx, cy, h * r_sc, leaf, k=6, flat=0.58))
    return g(out)


def cactus(x, y, h, col="#4f7d52", rib="#2f5236"):
    """Realistic Mandacaru / Cereus columnar cactus with distinct multi-height arms, fluted ribs, spines, and blooms."""
    w = max(5.0, h * 0.125)
    lit = mix(col, "#b8d89a", 0.28)
    shade = mix(col, "#182e1d", 0.35)
    out = [
        # Ground shadow
        el("ellipse", cx=x + 2, cy=y + 1, rx=w * 1.4, ry=w * 0.32, fill="#000000", opacity=0.22),
    ]
    # Arms with distinct horizontal offsets so they never overlap into a ladder
    arms = [
        (-1, 0.38, 0.38, 2.15),
        (1, 0.48, 0.36, 1.95),
        (-1, 0.66, 0.25, 1.35),
        (1, 0.74, 0.20, 1.25),
    ]
    arm_w = w * 0.76
    for side, at, ah, reach in arms:
        ay = y - h * at
        ax = x + side * w * reach
        top_y = ay - h * ah
        # Outer dark shadow stroke, main arm fill stroke, inner highlight stroke
        d_arm = f"M{n(x + side * w * 0.2)},{n(ay)} Q{n(ax)},{n(ay)} {n(ax)},{n(ay - arm_w * 0.8)} L{n(ax)},{n(top_y)}"
        out.append(el("path", d=d_arm, stroke=shade, stroke_width=arm_w + 1.2, fill="none", stroke_linecap="round"))
        out.append(el("path", d=d_arm, stroke=col, stroke_width=arm_w, fill="none", stroke_linecap="round"))
        out.append(el("path", d=d_arm, stroke=lit, stroke_width=arm_w * 0.32, fill="none", stroke_linecap="round", opacity=0.55))
        # Rib line along arm
        out.append(el("path", d=f"M{n(ax)},{n(ay - arm_w * 0.5)} L{n(ax)},{n(top_y + 2)}",
                      stroke=rib, stroke_width=0.75, fill="none", opacity=0.65))

    # Main central stem with 3D cylindrical shading
    out.append(el("rect", x=x - w / 2, y=y - h, width=w, height=h, rx=w / 2, fill=col))
    out.append(el("rect", x=x, y=y - h, width=w / 2, height=h, rx=w / 4, fill=shade, opacity=0.38))
    out.append(el("rect", x=x - w * 0.36, y=y - h + 2, width=w * 0.22, height=h - 4, rx=w * 0.1, fill=lit, opacity=0.45))
    # Fluted vertical ribs and spine areoles on main stem
    ribs, spines = [], []
    for f in (-0.28, 0.0, 0.28):
        rx_ = x + w * f
        ribs.append(f"M{n(rx_)},{n(y - h + w * 0.45)} L{n(rx_)},{n(y - 2)}")
        for sy in range(int(y - h + w * 0.7), int(y - 4), max(6, int(h * 0.09))):
            spines.append(f"M{n(rx_ - 2)},{n(sy - 1)} L{n(rx_ + 2)},{n(sy + 1)} M{n(rx_ - 2)},{n(sy + 1)} L{n(rx_ + 2)},{n(sy - 1)}")
    out.append(el("path", d=" ".join(ribs), stroke=rib, stroke_width=0.85, fill="none", opacity=0.7))
    out.append(el("path", d=" ".join(spines), stroke="#e8dec8", stroke_width=0.65, fill="none", opacity=0.75))
    # White Mandacaru night-blooming flower on crown
    out.append(el("circle", cx=x - w * 0.15, cy=y - h + 1, r=w * 0.28, fill="#fffdf5"))
    out.append(el("circle", cx=x - w * 0.15, cy=y - h + 1, r=w * 0.12, fill="#f2c938"))
    return g(out)


def thorn_bush(rng, x, y, s, col="#786b56", leaf="#9aa66e"):
    segs_main, segs_twigs = [], []
    dots = []
    for _ in range(10):
        a = math.radians(rng.uniform(-168, -12))
        L = s * rng.uniform(0.55, 1.08)
        ex, ey = x + math.cos(a) * L, y + math.sin(a) * L * 0.78
        cx_, cy_ = (x + ex) * 0.5 + rng.uniform(-4, 4), (y + ey) * 0.5 - rng.uniform(1, 5)
        segs_main.append(f"M{n(x)},{n(y)} Q{n(cx_)},{n(cy_)} {n(ex)},{n(ey)}")
        for _ in range(3):
            t = rng.uniform(0.35, 0.92)
            px, py = quad((x, y), (cx_, cy_), (ex, ey), t)
            tx_, ty_ = px + rng.uniform(-s * 0.28, s * 0.28), py - rng.uniform(2, s * 0.28)
            segs_twigs.append(f"M{n(px)},{n(py)} L{n(tx_)},{n(ty_)}")
            dots.append(el("circle", cx=tx_, cy=ty_, r=rng.uniform(1.1, 2.2)))
    return g([
        el("ellipse", cx=x, cy=y + 1, rx=s * 0.65, ry=s * 0.14, fill="#000000", opacity=0.18),
        el("path", d=" ".join(segs_main), stroke=col, stroke_width=1.35, fill="none", stroke_linecap="round"),
        el("path", d=" ".join(segs_twigs), stroke=mix(col, "#3b3228", 0.3), stroke_width=0.8, fill="none", stroke_linecap="round"),
        g(dots, fill=leaf, opacity=0.85),
    ])


def termite_mound(x, y, h, col="#a85d34"):
    """Sculpted cathedral termite mound with buttressed flutes, vents, and warm laterite shading."""
    w = h * 0.58
    lit = mix(col, "#f0b478", 0.28)
    shade = mix(col, "#2e1508", 0.42)
    return g([
        el("ellipse", cx=x + 2, cy=y + 1, rx=w * 1.15, ry=w * 0.22, fill="#000000", opacity=0.24),
        # Main multi-spired silhouette
        el("path", d=(
            f"M{n(x - w)},{n(y)} Q{n(x - w * 0.85)},{n(y - h * 0.45)} {n(x - w * 0.52)},{n(y - h * 0.72)} "
            f"Q{n(x - w * 0.35)},{n(y - h * 0.62)} {n(x - w * 0.14)},{n(y - h)} "
            f"Q{n(x + w * 0.12)},{n(y - h * 0.96)} {n(x + w * 0.25)},{n(y - h * 0.68)} "
            f"Q{n(x + w * 0.48)},{n(y - h * 0.78)} {n(x + w * 0.58)},{n(y - h * 0.48)} "
            f"Q{n(x + w * 0.82)},{n(y - h * 0.22)} {n(x + w)},{n(y)}Z"), fill=col),
        # Sunlit left buttress ridges
        el("path", d=(
            f"M{n(x - w * 0.88)},{n(y)} Q{n(x - w * 0.7)},{n(y - h * 0.42)} {n(x - w * 0.52)},{n(y - h * 0.72)} "
            f"Q{n(x - w * 0.3)},{n(y - h * 0.35)} {n(x - w * 0.35)},{n(y)}Z"), fill=lit, opacity=0.55),
        # Shadowed right face
        el("path", d=(
            f"M{n(x - w * 0.05)},{n(y)} Q{n(x + w * 0.05)},{n(y - h * 0.55)} {n(x - w * 0.14)},{n(y - h)} "
            f"Q{n(x + w * 0.12)},{n(y - h * 0.96)} {n(x + w * 0.25)},{n(y - h * 0.68)} "
            f"Q{n(x + w * 0.48)},{n(y - h * 0.78)} {n(x + w * 0.58)},{n(y - h * 0.48)} "
            f"Q{n(x + w * 0.82)},{n(y - h * 0.22)} {n(x + w)},{n(y)}Z"), fill=shade, opacity=0.52),
        # Ventilation pores
        el("ellipse", cx=x - w * 0.18, cy=y - h * 0.45, rx=w * 0.08, ry=h * 0.05, fill=shade, opacity=0.7),
        el("ellipse", cx=x + w * 0.15, cy=y - h * 0.32, rx=w * 0.09, ry=h * 0.055, fill=shade, opacity=0.7),
        el("ellipse", cx=x - w * 0.42, cy=y - h * 0.24, rx=w * 0.07, ry=h * 0.045, fill=shade, opacity=0.7),
    ])


def water_lily(rng, x, y, r, flower=False):
    """Giant Amazonian Victoria amazonica water lily pad with upturned crimson rim and radiating venation."""
    notch = rng.uniform(0, TAU)
    ry = r * 0.32
    veins = []
    for k in range(10):
        a = TAU * k / 10
        if abs((a - notch + math.pi) % TAU - math.pi) < 0.25:
            continue
        veins.append(f"M{n(x)},{n(y - 1)} L{n(x + math.cos(a) * r * 0.88)},{n(y - 1 + math.sin(a) * ry * 0.88)}")
    out = [
        # Drop shadow on water
        el("ellipse", cx=x + 1, cy=y + 2.2, rx=r * 1.03, ry=ry * 1.06, fill="#0c1f14", opacity=0.38),
        # Crimson-bronze outer upturned rim wall
        el("ellipse", cx=x, cy=y + 0.8, rx=r, ry=ry, fill="#8c322b"),
        el("ellipse", cx=x, cy=y - 0.5, rx=r, ry=ry, fill="#a84438"),
        # Lush green inner tray
        el("ellipse", cx=x, cy=y - 1.0, rx=r * 0.92, ry=ry * 0.86, fill="#3c7d36"),
        el("ellipse", cx=x - r * 0.08, cy=y - 1.2, rx=r * 0.78, ry=ry * 0.72, fill="#5ca044"),
        # Radial rib veins
        el("path", d=" ".join(veins), stroke="#7ec258", stroke_width=0.75, opacity=0.75),
        # Drainage notch
        el("path", d=f"M{n(x)},{n(y - 1)} L{n(x + math.cos(notch) * r * 1.02)},{n(y + math.sin(notch) * ry * 1.02)}",
           stroke="#2a4d24", stroke_width=1.2),
    ]
    if flower or r > 25:
        fx, fy = x + r * 0.25, y - 2
        out.append(g([
            el("ellipse", cx=fx, cy=fy, rx=r * 0.22, ry=r * 0.11, fill="#f7e6ee"),
            el("ellipse", cx=fx, cy=fy - 1, rx=r * 0.16, ry=r * 0.08, fill="#fff7fa"),
            el("circle", cx=fx, cy=fy - 1.2, r=r * 0.06, fill="#e87ca8"),
        ]))
    return g(out)


def water_lines(rng, x0, x1, y0, y1, count, col="#ffffff", op=0.35, w=1.0):
    segs = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        t = (y - y0) / max(1, (y1 - y0))
        L = rng.uniform(10, 44) * (0.45 + 0.75 * t)
        segs.append(f"M{n(x)},{n(y)} q{n(L * 0.25)},{n(-0.8)} {n(L * 0.5)},0 t{n(L * 0.5)},0")
    return el("path", d=" ".join(segs), stroke=col, stroke_width=w, fill="none", opacity=op, stroke_linecap="round", class_="shimmer")


def waterfall(s: Scene, x, y_top, y_bot, w, col="#e8f6fc"):
    """Multi-tiered cascading waterfall with rock step ledges, turbulent water ribbons, foam plumes, and base spray."""
    rng = s.rng
    h = y_bot - y_top
    wb = w * 1.48
    out = [
        # Deep wet rock recess behind waterfall
        el("path", d=P([
            (x - w * 0.58, y_top), (x + w * 0.58, y_top),
            (x + wb * 0.62, y_bot), (x - wb * 0.62, y_bot)
        ]), fill="#182630", opacity=0.52),
        # Translucent cyan-white water curtain
        el("path", d=P([
            (x - w * 0.50, y_top), (x + w * 0.50, y_top),
            (x + wb * 0.55, y_bot), (x - wb * 0.55, y_bot)
        ]), fill=col, opacity=0.72),
    ]
    # Mid-cliff terrace step foam ledges (where water rebounds off horizontal rock shelves)
    for frac in (0.36, 0.66):
        ly = y_top + h * frac + rng.uniform(-3, 3)
        lw = (w * (1 - frac) + wb * frac) * 0.52
        out.append(el("ellipse", cx=x + rng.uniform(-2, 2), cy=ly, rx=lw, ry=max(2.5, w * 0.08),
                      fill="#ffffff", opacity=0.58))

    # Cascading water ribbons (background soft + foreground crisp animated)
    ribbons_bg, strands_fg = [], []
    n_strands = int(w / 2.2) + 5
    for i in range(n_strands):
        t = (i / max(1, n_strands - 1)) - 0.5
        sx = x + t * w * 0.92 + rng.uniform(-1.5, 1.5)
        ex = x + t * wb * 0.98 + rng.uniform(-4, 4)
        mx1 = sx + (ex - sx) * 0.33 + rng.uniform(-3, 3)
        mx2 = sx + (ex - sx) * 0.68 + rng.uniform(-4, 4)
        path_d = f"M{n(sx)},{n(y_top)} C{n(mx1)},{n(y_top + h * 0.32)} {n(mx2)},{n(y_top + h * 0.68)} {n(ex)},{n(y_bot)}"
        if i % 2 == 0:
            ribbons_bg.append(path_d)
        else:
            strands_fg.append(path_d)

    out.append(el("path", d=" ".join(ribbons_bg), stroke="#bfe6f8", stroke_width=2.4, opacity=0.72, fill="none", stroke_linecap="round"))
    out.append(el("path", d=" ".join(strands_fg), stroke="#ffffff", stroke_width=1.5, opacity=0.92, fill="none",
                  stroke_linecap="round", class_="flow", stroke_dasharray="14 8"))

    # Lip foam crest and base boiling whitewater
    lip_bubbles = [el("circle", cx=x + (i / 6 - 0.5) * w * 0.9, cy=y_top + rng.uniform(-1, 2), r=rng.uniform(2, 4.2))
                   for i in range(7)]
    base_bubbles = [el("circle", cx=x + (i / 10 - 0.5) * wb * 1.1, cy=y_bot + rng.uniform(-4, 3), r=rng.uniform(3.5, 8.5))
                    for i in range(11)]
    out.append(g(lip_bubbles, fill="#ffffff", opacity=0.88))
    out.append(g(base_bubbles, fill="#ffffff", opacity=0.80))
    out.append(mist(s, x, y_bot, wb * 1.25, max(8, w * 0.48), op=0.85, blur="mist"))
    return out


# ==============================================================================
# FAUNA PRIMITIVES (ANATOMICALLY DETAILED)
# ==============================================================================
def fish(x, y, s, body, fin=None, stripe=None, flip=False, tall=0.45):
    """Detailed tropical reef fish with dorsal/pectoral/caudal fins, gill operculum, and countershading."""
    fin = fin or mix(body, "#001428", 0.28)
    belly = mix(body, "#ffffff", 0.42)
    sx = -1 if flip else 1
    parts = [
        # Dorsal and anal fins
        el("path", d=f"M{n(-s * 0.45)},{n(-s * tall * 0.45)} Q{n(s * 0.05)},{n(-s * tall * 1.45)} {n(s * 0.48)},{n(-s * tall * 0.35)}Z", fill=fin),
        el("path", d=f"M{n(-s * 0.1)},{n(s * tall * 0.45)} Q{n(s * 0.25)},{n(s * tall * 1.3)} {n(s * 0.52)},{n(s * tall * 0.3)}Z", fill=fin),
        # Forked caudal fin
        el("path", d=f"M{n(s * 0.58)},0 L{n(s * 1.24)},{n(-s * 0.44)} Q{n(s * 0.96)},0 {n(s * 1.24)},{n(s * 0.44)}Z", fill=fin),
        # Main fusiform body + belly countershading
        el("path", d=f"M{n(-s)},0 Q{n(-s * 0.25)},{n(-s * tall * 1.2)} {n(s * 0.72)},0 Q{n(-s * 0.25)},{n(s * tall * 1.2)} {n(-s)},0Z", fill=body),
        el("path", d=f"M{n(-s * 0.92)},{n(s * 0.05)} Q{n(-s * 0.2)},{n(s * tall * 1.1)} {n(s * 0.65)},{n(s * 0.04)} Q{n(-s * 0.2)},{n(s * tall * 0.4)} {n(-s * 0.92)},{n(s * 0.05)}Z", fill=belly, opacity=0.55),
    ]
    if stripe:
        parts.append(el("path", d=f"M{n(-s * 0.65)},{n(s * 0.02)} Q{n(0)},{n(-s * 0.08)} {n(s * 0.75)},0",
                        stroke=stripe, stroke_width=max(0.9, s * 0.15), fill="none", stroke_linecap="round"))
        parts.append(el("path", d=f"M{n(-s * 0.15)},{n(-s * tall * 0.68)} Q{n(-s * 0.05)},0 {n(-s * 0.15)},{n(s * tall * 0.68)}",
                        stroke=stripe, stroke_width=max(0.7, s * 0.11), fill="none", opacity=0.75))
    # Gill arch, pectoral fin, and eye with iris ring
    parts += [
        el("path", d=f"M{n(-s * 0.42)},{n(-s * tall * 0.45)} Q{n(-s * 0.32)},0 {n(-s * 0.42)},{n(s * tall * 0.45)}",
           stroke=mix(body, "#000000", 0.38), stroke_width=max(0.6, s * 0.06), fill="none"),
        el("path", d=f"M{n(-s * 0.28)},{n(s * 0.08)} L{n(-s * 0.02)},{n(s * 0.26)} L{n(-s * 0.08)},{n(s * 0.04)}Z", fill=fin, opacity=0.85),
        el("circle", cx=-s * 0.64, cy=-s * 0.07, r=max(0.8, s * 0.11), fill="#f4f7f9"),
        el("circle", cx=-s * 0.65, cy=-s * 0.07, r=max(0.5, s * 0.065), fill="#0c1824"),
    ]
    return g(parts, transform=f"translate({n(x)} {n(y)}) scale({sx} 1)")


def school(rng, cx, cy, count, spread, s, body, stripe=None, flip=False, cls="swim"):
    fishes = [fish(cx + rng.uniform(-spread, spread), cy + rng.uniform(-spread * 0.35, spread * 0.35), s * rng.uniform(0.8, 1.15),
                   body, stripe=stripe, flip=flip) for _ in range(count)]
    return g(fishes, class_=cls, style=f"animation-delay:{n(-rng.uniform(0, 10))}s")


def turtle(x, y, s, flip=False):
    """Hawksbill / Green sea turtle with detailed hexagonal carapace scutes, scaled flippers, and beak."""
    sx = -1 if flip else 1
    scutes = [
        # Central vertebral scutes
        "M-9,-3 L-3,-5 L3,-3 L3,3 L-3,5 L-9,3Z",
        "M3,-3 L8,-5 L13,-2 L13,2 L8,5 L3,3Z",
        "M-14,-1 L-9,-3 L-9,3 L-14,1Z",
        # Costal scutes (upper & lower)
        "M-8,-4 L-3,-9 L4,-9 L3,-3 L-3,-5Z",
        "M4,-9 L11,-8 L13,-2 L8,-5 L3,-3Z",
        "M-8,4 L-3,9 L4,9 L3,3 L-3,5Z",
        "M4,9 L11,8 L13,2 L8,5 L3,3Z",
    ]
    return g([
        # Rear flippers
        el("path", d="M-12,-4 Q-22,-11 -26,-8 Q-22,-3 -14,-1Z M-12,4 Q-22,11 -26,8 Q-22,3 -14,1Z", fill="#56693a"),
        # Front wing-like flippers with leading-edge scales
        el("path", d="M10,-6 C16,-19 26,-25 32,-22 C28,-13 20,-7 14,-3Z", fill="#667b44"),
        el("path", d="M10,6 C16,19 26,25 32,22 C28,13 20,7 14,3Z", fill="#56693a"),
        el("path", d="M14,-9 L17,-11 M18,-14 L21,-15 M23,-18 L26,-19 M14,9 L17,11 M18,14 L21,15", stroke="#3d4b28", stroke_width=1, fill="none"),
        # Head and neck
        el("path", d="M15,-3 Q24,-5 28,-1 Q29,2 25,4 Q20,5 15,3Z", fill="#73874f"),
        el("path", d="M18,-2 L22,-3 L24,-1", stroke="#4d5c33", stroke_width=0.7, fill="none"),
        el("circle", cx=24.5, cy=-1.4, r=1.1, fill="#121810"),
        el("circle", cx=24.8, cy=-1.7, r=0.35, fill="#ffffff"),
        # Carapace dome with golden-amber scute pattern
        el("ellipse", cx=0, cy=0, rx=17.5, ry=11.8, fill="#4b3a1e"),
        el("ellipse", cx=0, cy=-0.4, rx=16.5, ry=10.8, fill="#876633"),
        g([el("path", d=sd, fill="#6b4c21", stroke="#cfa658", stroke_width=0.75) for sd in scutes]),
        # Sunlit dorsal highlight on shell
        el("ellipse", cx=-1, cy=-4, rx=11, ry=4, fill="#e6c47a", opacity=0.28),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def manta(x, y, s):
    """Giant oceanic manta ray with cephalic lobes, countershaded pectoral wings, and whip tail."""
    return g([
        # Whip tail
        el("path", d="M0,12 Q-1,26 -4,38", stroke="#172636", stroke_width=1.4, fill="none", stroke_linecap="round"),
        # Main diamond wings
        el("path", d=(
            "M-5,-7 C-8,-14 -10,-18 -8,-20 C-5,-19 -4,-13 -2,-9 "
            "C0,-9 0,-9 2,-9 C4,-13 5,-19 8,-20 C10,-18 8,-14 5,-7 "
            "C18,-6 38,-18 58,-12 C42,-4 24,5 7,12 L0,16 L-7,12 C-24,5 -42,-4 -58,-12 C-38,-18 -18,-6 -5,-7Z"
        ), fill="#1c2f42"),
        # Pale ventral underbelly edge & white shoulder patches
        el("path", d="M-54,-11 C-36,-4 -20,4 -6,10 L0,13 L6,10 C20,4 36,-4 54,-11 C36,-6 18,2 0,8 C-18,2 -36,-6 -54,-11Z",
           fill="#cfdce6", opacity=0.65),
        el("path", d="M-4,-6 C-14,-5 -24,-9 -30,-8 C-22,-3 -12,-1 -3,-2Z M4,-6 C14,-5 24,-9 30,-8 C22,-3 12,-1 3,-2Z",
           fill="#dbe7f0", opacity=0.55),
        # Gill slits
        el("path", d="M-5,-1 L-2,0 M-5,1 L-2,2 M-5,3 L-2,4 M5,-1 L2,0 M5,1 L2,2 M5,3 L2,4",
           stroke="#0d1824", stroke_width=0.7, fill="none", opacity=0.6),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


def shark(x, y, s, flip=False):
    """Caribbean reef shark (Carcharhinus perezi) with streamlined countershading, gill slits, and heterocercal tail."""
    sx = -1 if flip else 1
    return g([
        # Pectoral fin (far side)
        el("path", d="M8,3 C12,13 18,18 22,17 C19,10 15,5 12,3Z", fill="#132c47"),
        # First & second dorsal fins
        el("path", d="M-2,-5 C3,-21 11,-24 14,-22 C11,-14 9,-8 7,-5Z", fill="#193859"),
        el("path", d="M-24,-3 L-21,-9 L-18,-3Z", fill="#193859"),
        # Heterocercal caudal fin
        el("path", d="M-36,0 C-44,-8 -52,-18 -56,-17 C-52,-9 -46,-3 -43,0 C-47,4 -51,10 -53,13 C-47,10 -41,4 -36,1Z", fill="#15314f"),
        # Torpedo body
        el("path", d="M-40,0 C-24,-7 6,-9 28,-4 C39,-2 46,1 48,2.5 C43,5 32,7 14,7.5 C-8,8 -24,4 -40,0Z", fill="#1e446b"),
        # White ventral countershading
        el("path", d="M-36,1 C-18,4 10,5 28,2.5 C38,1.5 44,2 47,3 C41,5.5 30,7.5 14,7.5 C-8,8 -22,5 -36,1Z", fill="#d4e3ed", opacity=0.88),
        # Near pectoral fin
        el("path", d="M12,4 C16,17 24,22 29,21 C26,13 21,6 17,4Z", fill="#193859"),
        # Five gill slits, eye, and mouth line
        el("path", d="M22,-1 L21,4 M24,-1 L23,4 M26,-1 L25,4 M28,-1 L27,4 M30,-0.5 L29,3.5",
           stroke="#0c2036", stroke_width=0.75, fill="none", opacity=0.75),
        el("path", d="M34,4.2 Q39,3.2 43,4.5", stroke="#0c2036", stroke_width=0.8, fill="none"),
        el("circle", cx=38, cy=0.6, r=1.3, fill="#08121e"),
        el("circle", cx=38.3, cy=0.3, r=0.4, fill="#ffffff"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})", class_="swim")


def macaw(x, y, s, flip=False, palette=("#d62828", "#1d56b8", "#f5c428")):
    """Detailed Scarlet or Hyacinth Macaw in flight with layered wing coverts, primaries, tail streamers, and facial patch."""
    red, blue, yellow = palette
    sx = -1 if flip else 1
    return g([
        # Far wing (upbeat/downbeat)
        el("path", d="M-2,2 C-8,14 -18,22 -28,24 C-20,16 -12,8 4,2Z", fill=mix(blue, "#081838", 0.32)),
        el("path", d="M-1,1 C-5,9 -11,14 -17,15 C-11,9 -6,4 3,1Z", fill=mix(yellow, "#8a6800", 0.2)),
        # Long graduated tail streamers
        el("path", d="M-10,1 L-52,11 L-50,13.5 L-9,4Z", fill=red),
        el("path", d="M-12,2.5 L-44,13 L-42,14.8 L-10,4.5Z", fill=blue),
        # Streamlined body and breast
        el("path", d="M-14,0 C-8,-5 6,-6 15,-2 C18,0 16,5 10,5 C2,6 -8,4 -14,0Z", fill=red),
        # Near wing: primaries (blue), median coverts (yellow), lesser coverts (red)
        el("path", d="M-3,-2 C-10,-20 -24,-30 -36,-33 C-28,-22 -18,-10 5,-2Z", fill=blue),
        el("path", d="M-12,-14 L-33,-30 M-9,-11 L-28,-24 M-6,-8 L-23,-19", stroke=mix(blue, "#000000", 0.35), stroke_width=0.75, fill="none"),
        el("path", d="M-2,-2 C-7,-13 -15,-20 -22,-22 C-15,-13 -8,-6 5,-2Z", fill=yellow),
        el("path", d="M0,-2 C-4,-8 -9,-12 -14,-13 C-8,-7 -3,-3 5,-2Z", fill=red),
        # Head, bare white facial patch with feather lines, and hooked maxilla/mandible
        el("circle", cx=14.5, cy=-2.2, r=5.2, fill=red),
        el("path", d="M13.5,-4.8 C16.5,-5.2 18.8,-3.5 18.2,-0.5 C16.5,0.2 14,-0.5 13.5,-2.5Z", fill="#faf5eb"),
        el("circle", cx=16.0, cy=-2.8, r=1.0, fill="#1a1a1a"),
        el("path", d="M18.2,-4.5 C23,-4.2 25.5,-1.2 23.5,2.5 C21.5,1.2 19.5,0 18.2,-1.2Z", fill="#f2ead8"),
        el("path", d="M17.5,-1.2 C19.5,1.2 21,1.8 21.8,0.5 C20.2,-0.5 18.8,-1 17.5,-1.2Z", fill="#222222"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})", class_="fly")


def toucan(x, y, s):
    """Ramphastos toco toucan perched with serrated gradient bill, blue periorbital ring, and crimson tail."""
    return g([
        # Long squared tail and crimson undertail coverts
        el("path", d="M-1,6 L-7,30 L1,31 L5,8Z", fill="#101216"),
        el("ellipse", cx=3, cy=11, rx=4, ry=3, fill="#d62828"),
        # Glossy black body & folded wing with blue-grey sheen
        el("path", d="M-3,2 C-5,-6 2,-10 7,-7 C11,-2 11,10 6,15 C1,16 -3,10 -3,2Z", fill="#14171c"),
        el("path", d="M-1,1 C2,-2 6,1 6,9 C3,11 -1,7 -1,1Z", fill="#252c38"),
        # Golden-white throat bib with scarlet border
        el("path", d="M2,-6 C6,-7 9,-4 8,2 C5,4 1,2 2,-6Z", fill="#fff8e6"),
        el("path", d="M2,-5 C5,-6 8,-3 7,1 C5,2 2,1 2,-5Z", fill="#f7c838", opacity=0.45),
        el("path", d="M2,2 Q5,4 8,2", stroke="#d62828", stroke_width=1.2, fill="none"),
        # Blue eye ring and dark eye
        el("circle", cx=5.2, cy=-4.2, r=2.0, fill="#2978d8"),
        el("circle", cx=5.2, cy=-4.2, r=1.1, fill="#111111"),
        el("circle", cx=5.5, cy=-4.5, r=0.35, fill="#ffffff"),
        # Enormous curved orange-yellow bill with black base band and terminal spot
        el("path", d="M8,-7.5 C18,-9.5 27,-6.5 30,0.5 C22,2 14,1.5 8,0.5Z", fill="#f27d16"),
        el("path", d="M8,-7.5 C16,-9 23,-7 26,-3 C19,-2.5 13,-3 8,-3.5Z", fill="#f9c62c"),
        el("path", d="M25,-5.2 C28,-3.8 29.5,-1.5 30,0.5 C27.5,1 26,0.5 24.5,-1Z", fill="#141414"),
        el("path", d="M8,-7.5 L8,0.5", stroke="#141414", stroke_width=1.4),
        el("path", d="M8,-2.2 L29,0.2", stroke="#b84a08", stroke_width=0.6, opacity=0.7),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


def condor(x, y, s, cls="fly"):
    """Soaring Andean Condor (Vultur gryphus) with slotted primary feathers, white wing panels, and neck ruff."""
    return g([
        # Broad wings with slotted primary fingertips
        el("path", d=(
            "M0,0 C-14,-6 -32,-8 -46,-5 L-58,-4 L-51,-1.5 L-60,0.5 L-51,2 L-58,4.5 L-48,4.8 L-53,7 L-42,6.5 "
            "C-26,6 -12,5 -5,6.5 L-8,12 L0,10.5 L8,12 L5,6.5 C12,5 26,6 42,6.5 "
            "L53,7 L48,4.8 L58,4.5 L51,2 L60,0.5 L51,-1.5 L58,-4 L46,-5 C32,-8 14,-6 0,0Z"
        ), fill="#17181f"),
        # Silvery-white secondary wing panels
        el("path", d="M-38,-2.5 C-25,-4.5 -12,-3.5 -5,-0.5 C-14,1.5 -26,1.5 -38,-2.5Z", fill="#e9edf2", opacity=0.9),
        el("path", d="M38,-2.5 C25,-4.5 12,-3.5 5,-0.5 C14,1.5 26,1.5 38,-2.5Z", fill="#e9edf2", opacity=0.9),
        # Downy white neck collar and carunculated head
        el("ellipse", cx=0, cy=-1.2, rx=3.8, ry=2.0, fill="#f5f7fa"),
        el("ellipse", cx=0, cy=-4.2, rx=2.2, ry=2.6, fill="#b5544a"),
        el("path", d="M-0.8,-6.5 L0,-8.5 L0.8,-6.5Z", fill="#d9c8b2"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})", class_=cls)


def bird_v(x, y, s, col="#2b3440"):
    return el("path", d=(
        f"M{n(x - s)},{n(y - s * 0.28)} Q{n(x - s * 0.45)},{n(y - s * 0.65)} {n(x)},{n(y)} "
        f"Q{n(x + s * 0.45)},{n(y - s * 0.65)} {n(x + s)},{n(y - s * 0.28)} "
        f"Q{n(x + s * 0.45)},{n(y - s * 0.42)} {n(x)},{n(y + s * 0.14)} "
        f"Q{n(x - s * 0.45)},{n(y - s * 0.42)} {n(x - s)},{n(y - s * 0.28)}Z"
    ), fill=col)


def flamingo(x, y, s, flip=False, pose="stand"):
    """American/Caribbean Flamingo (Phoenicopterus ruber) with S-neck or filter-feeding pose, two-tone bill, and water ripples."""
    sx = -1 if flip else 1
    parts = [
        # Water ripple ring around legs
        el("ellipse", cx=1, cy=28, rx=9.5, ry=2.2, fill="none", stroke="#ffffff", stroke_width=0.8, opacity=0.55),
        # Long slender wading legs with pink tarsal joints
        el("path", d="M2,0 L2.5,15 L3,28 M-2,0 L-3.5,14 L2.5,19" if pose == "stand" else "M2,0 L3,15 L3.5,28 M-2,0 L-3,15 L-3.5,28",
           stroke="#d46a70", stroke_width=1.3, fill="none", stroke_linecap="round"),
        el("circle", cx=2.5 if pose == "stand" else 3.0, cy=15, r=1.3, fill="#b84850"),
        el("circle", cx=-3.5 if pose == "stand" else -3.0, cy=14.5, r=1.3, fill="#b84850"),
        # Sculpted body, crimson wing coverts, and black primary tips
        el("path", d="M-14,-2 C-12,-11 -2,-13 8,-8 C12,-6 11,0 5,1.5 C-2,2.5 -9,1 -14,-2Z", fill="#f57c73"),
        el("path", d="M-9,-6.5 C-3,-10.5 4,-9.5 6,-4 C2,-1 -5,-1 -9,-6.5Z", fill="#ff9e94"),
        el("path", d="M-11,-3.5 C-6,-4.5 -1,-3.5 3,-1.5 L-13,-1.5Z", fill="#d94b43", opacity=0.7),
        el("path", d="M-14,-2 L-18,2.5 L-11,0.5Z", fill="#1c1c1c"),
    ]
    if pose == "feed":
        # Arching neck dipping bill into the water for filter-feeding
        parts += [
            el("path", d="M8,-6 C16,-4 19,10 16,23 C15,26 13,27 11,26", stroke="#f57c73", stroke_width=3.1, fill="none", stroke_linecap="round"),
            el("path", d="M8,-6.5 C15,-4.5 18,9 15.2,22", stroke="#ffb2a8", stroke_width=1.0, fill="none", stroke_linecap="round"),
            el("circle", cx=12.5, cy=25.5, r=2.7, fill="#f57c73"),
            el("path", d="M11,26.5 C8,27.5 6.5,26 7.5,24 C9,24.5 10.5,25.5 11.5,26Z", fill="#181818"),
            el("ellipse", cx=11, cy=27.5, rx=6.5, ry=1.5, fill="none", stroke="#ffffff", stroke_width=0.7, opacity=0.6),
        ]
    else:
        # Classic S-curved neck
        parts += [
            el("path", d="M7,-6 C15,-14 7,-24 6,-31 C5,-35 8,-37 10,-36", stroke="#f57c73", stroke_width=3.0, fill="none", stroke_linecap="round"),
            el("path", d="M6.2,-6.5 C13.5,-14 6,-24 5.2,-31", stroke="#ffb2a8", stroke_width=1.0, fill="none", stroke_linecap="round"),
            el("circle", cx=10, cy=-35.5, r=2.9, fill="#f57c73"),
            el("circle", cx=10.8, cy=-36, r=0.65, fill="#f7e248"),
            el("path", d="M12.2,-36.5 C15.5,-36 16.8,-33.5 15.5,-30.5 C14,-31.5 13,-33.5 11.8,-34.5Z", fill="#fce8e6"),
            el("path", d="M14.2,-34 C16.2,-33 16.5,-31.5 15.5,-30.5 C14.2,-31.2 13.8,-32.5 14.2,-34Z", fill="#181818"),
        ]
    return g(parts, transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def jabiru(x, y, s, flip=False):
    """Pantanal Jabiru Stork (Jabiru mycteria) with sculpted plumage, black neck, scarlet throat band, and heavy upturned bill."""
    sx = -1 if flip else 1
    return g([
        el("ellipse", cx=1, cy=26, rx=10.5, ry=2.2, fill="none", stroke="#fff5dc", stroke_width=0.8, opacity=0.55),
        # Long stilt legs with tarsal joints
        el("path", d="M-2,0 L-2.5,13 L-3,26 M3,0 L3.5,13 L4,26", stroke="#1c1c1e", stroke_width=1.5, fill="none", stroke_linecap="round"),
        el("circle", cx=-2.5, cy=13, r=1.1, fill="#2e2e32"),
        el("circle", cx=3.5, cy=13, r=1.1, fill="#2e2e32"),
        # Sculpted white plumage body with layered wing coverts and black tail tip
        el("path", d="M-15,-4 L-19,-1.5 L-12,-0.5Z", fill="#18181a"),
        el("path", d="M-15,-4 C-12,-14 -1,-16 9,-10 C13,-7 12,0 5,1.5 C-3,2.5 -11,0.5 -15,-4Z", fill="#faf8f0"),
        el("path", d="M-13,-3 C-8,0 2,1 8,-2 C4,1.5 -5,2 -13,-3Z", fill="#dedbd0"),
        el("path", d="M-10,-7 C-4,-11 4,-10 7,-4 C1,-1 -6,-2 -10,-7Z", fill="#f0eee4", stroke="#d4d0c2", stroke_width=0.6),
        # Sculpted black neck, inflatable scarlet basal collar, head, and heavy upturned bill
        el("path", d="M5,-9 C7.5,-17 7,-25 6,-32 L9.5,-32 C11,-24 11.5,-16 9.5,-8Z", fill="#18181a"),
        el("path", d="M5,-8.5 C9,-8 11.5,-11 10.5,-15.5 C7.5,-15 5.2,-12 5,-8.5Z", fill="#d9261e"),
        el("path", d="M6.5,-9.5 C9,-9.5 10.5,-11.5 9.8,-14.5", stroke="#ff6359", stroke_width=0.9, fill="none"),
        # Skull & wispy white occipital crown feathers
        el("path", d="M5,-31.5 C4.5,-35 7,-36.8 10,-35.5 C11.5,-34.5 11.5,-31.5 9,-31Z", fill="#18181a"),
        el("path", d="M5,-35 Q2.5,-36.5 3.5,-33.5 M5.5,-35.8 Q3.5,-37.5 4.5,-34.5", stroke="#e2e0d5", stroke_width=1.0, fill="none"),
        el("circle", cx=8.8, cy=-33.8, r=0.65, fill="#2b2018"),
        el("circle", cx=9.0, cy=-34.0, r=0.25, fill="#ffffff"),
        # Massive slightly recurved (upturned) black stork bill
        el("path", d="M10.2,-35 C16,-34.8 22,-34.2 26.5,-33.2 C22,-31.2 15.5,-31.2 9.8,-31.5Z", fill="#141416"),
        el("path", d="M10.5,-33.2 Q18,-33 25.5,-33.1", stroke="#38383d", stroke_width=0.6, fill="none"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def egret(x, y, s, flip=False):
    """Great Egret (Ardea alba) with breeding plumes, S-neck, and dagger yellow bill."""
    sx = -1 if flip else 1
    return g([
        el("path", d="M0,0 L-1,21 M3,0 L4,21", stroke="#1e2022", stroke_width=1.1),
        el("path", d="M-11,-3 C-9,-9 -1,-10 6,-6 C9,-4 8,0 3,1 C-3,1 -8,0 -11,-3Z", fill="#ffffff"),
        # Delicate aigrette back plumes
        el("path", d="M-6,-6 Q-12,-5 -15,-1 M-5,-5 Q-11,-3 -14,1", stroke="#f0f4f8", stroke_width=0.9, fill="none"),
        el("path", d="M6,-5 C11,-13 5,-20 6,-26 C6.5,-28 8,-28 9,-27", stroke="#ffffff", stroke_width=2.2, fill="none", stroke_linecap="round"),
        el("circle", cx=8.8, cy=-27, r=2.1, fill="#ffffff"),
        el("circle", cx=9.5, cy=-27.2, r=0.5, fill="#f2d024"),
        el("path", d="M10.5,-27.8 L18.5,-25.5 L10.5,-25.8Z", fill="#e8ae24"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def capybara(x, y, s, flip=False):
    """Anatomically realistic Capybara (Hydrochoerus hydrochaeris) with sculpted haunches, neck, blunt snout, and coarse fur."""
    sx = -1 if flip else 1
    return g([
        el("ellipse", cx=0, cy=5.2, rx=16.5, ry=2.2, fill="#000000", opacity=0.22),
        # Far-side legs (darker)
        el("path", d="M-9,-2 L-11,4.8 L-9,4.8 L-6.5,-1Z M8.5,-2 L7.5,4.8 L9.5,4.8 L11,-1Z", fill="#422814"),
        # Sculpted barrel torso, rounded rump, shoulder hump, and broad rectangular head
        el("path", d=(
            "M-16,-2 C-17,-9 -12,-14.5 -4,-14.5 C2,-14.5 6,-13 9.5,-10.5 "
            "C11.5,-12.5 15,-13.2 18.5,-12.2 C21.5,-11.2 22.5,-8.5 22,-5.5 "
            "C21.5,-3 18.5,-2.5 15.5,-3.2 C13.5,-2 12,-0.5 11,0.5 "
            "C4,1.2 -6,1.2 -13.5,0.5 C-15.5,0 -16,-1 -16,-2Z"
        ), fill="#8c5832"),
        # Warm sunlit dorsal fur coat & shaded underbelly/haunch
        el("path", d="M-13,-10 C-8,-14 2,-14 9,-10 C12,-12 16,-12.5 19,-11.2 C14,-9 4,-8 -13,-10Z", fill="#b57b4e", opacity=0.65),
        el("path", d="M-15.5,-1.5 C-10,-4.5 4,-4.5 12,-0.5 C14.5,-2.5 18,-3 21,-4.5 C19,-2.5 15,-2 11,0.5 C3,1.2 -8,1.2 -15.5,-1.5Z",
           fill="#59361b", opacity=0.65),
        # Near-side jointed hind leg and foreleg
        el("path", d="M-13.5,-4 C-10.5,-4 -9.5,-1 -10.5,5.2 L-13,5.2 L-12.5,0.5 C-14,0 -14.5,-2 -13.5,-4Z", fill="#6e4324"),
        el("path", d="M9.5,-4 C12,-4 12.8,-1 12.2,5.2 L9.8,5.2 L10.2,0 Z", fill="#6e4324"),
        # Coarse fur hatch strokes
        el("path", d="M-9,-9 l3,1 M-4,-10 l3,1 M2,-9 l3,1 M-6,-6 l3,0.8 M1,-6 l3,0.8", stroke="#59361b", stroke_width=0.75, opacity=0.55),
        # Blunt muzzle plane, dark morrillo scent gland on snout bridge, small rounded ear, eye, and nostril
        el("path", d="M17.5,-11.5 C20.5,-11 22.2,-8.8 22,-5.5 C20,-4.5 17.8,-5.2 17,-7.5Z", fill="#6e4324"),
        el("ellipse", cx=17.5, cy=-11.8, rx=1.6, ry=0.9, fill="#382110"),
        el("path", d="M11.2,-11.5 C10.5,-14.2 12.5,-15 13.5,-12.2Z", fill="#543219"),
        el("circle", cx=15.2, cy=-9.5, r=1.0, fill="#14100c"),
        el("circle", cx=15.5, cy=-9.8, r=0.35, fill="#ffffff"),
        el("circle", cx=20.4, cy=-7.8, r=0.65, fill="#29170b"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def caiman(x, y, s, flip=False):
    """Partially submerged Black Caiman / American Crocodile with osteoderm scutes, periscopic eyes, and water wake."""
    sx = -1 if flip else 1
    return g([
        # Water wake lines
        el("path", d="M-34,1 L28,1 M-26,2.5 L20,2.5", stroke="#ffffff", stroke_width=0.75, opacity=0.45),
        # Armored back, tail crest, and long jaws
        el("path", d="M-34,0 C-22,-4 -6,-5 8,-3 C14,-6 18,-6 20,-3 C26,-3.5 31,-2.5 32,0.5 L-34,0.5Z", fill="#343b26"),
        el("path", d="M-30,0 L-26,-3.5 L-23,0 L-19,-4 L-16,0 L-12,-4 L-9,0 L-5,-3.5 L-2,0 L2,-3 L5,0", fill="#222818"),
        # Jaw line & teeth glint
        el("path", d="M18,-0.5 Q25,-1 31,0", stroke="#1a1f12", stroke_width=0.8, fill="none"),
        el("path", d="M21,-0.6 L21.5,-1.3 M24,-0.7 L24.5,-1.4 M27,-0.6 L27.5,-1.2", stroke="#e8e2ce", stroke_width=0.6),
        # Raised brow ridge and golden slit eye
        el("circle", cx=16.5, cy=-4.0, r=1.8, fill="#454d33"),
        el("circle", cx=16.7, cy=-4.2, r=0.85, fill="#e8c438"),
        el("path", d="M16.7,-4.9 L16.7,-3.5", stroke="#111111", stroke_width=0.45),
        el("circle", cx=29.5, cy=-1.8, r=0.7, fill="#222818"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def dolphin(x, y, s):
    """Amazon Pink River Dolphin (Inia geoffrensis) breaching with bulbous melon, long beak, and low dorsal ridge."""
    return g([
        # Surface splash rings
        el("ellipse", cx=0, cy=1, rx=24, ry=2.6, fill="none", stroke="#f4f7ec", stroke_width=0.9, opacity=0.55),
        # Arched body, low keel-like dorsal fin, and beak
        el("path", d=(
            "M-22,1 C-14,-10 -2,-13 10,-8 C13,-9 16,-7 17,-4 C21,-3.5 25,-2.5 26,-1 "
            "C22,-0.5 18,-1 15,-1.5 C6,-4 -8,-3 -22,1Z"
        ), fill="#e898a2"),
        # Lighter rose highlight along melon and back
        el("path", d="M-16,-2 C-8,-9 2,-10 11,-6 C3,-6 -7,-5 -16,-2Z", fill="#f7c2c9", opacity=0.75),
        # Characteristic long low dorsal ridge
        el("path", d="M-6,-8.5 C-1,-13.5 4,-12.5 7,-7.5Z", fill="#d47b86"),
        # Flipper & eye
        el("path", d="M8,-3 C10,1 13,2 14,1 C13,-1 11,-2 10,-3Z", fill="#cf7480"),
        el("circle", cx=14.5, cy=-4.8, r=0.65, fill="#1f1418"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})", class_="bob")


def maned_wolf(x, y, s, flip=False):
    """Anatomically sculpted Cerrado Maned Wolf (Chrysocyon brachyurus) with stilt legs, black mane, tucked waist, and fox head."""
    sx = -1 if flip else 1
    return g([
        el("ellipse", cx=0, cy=6.5, rx=16.5, ry=2.2, fill="#000000", opacity=0.22),
        # Far-side stilt legs (upper rufous thigh/arm + black lower stocking)
        el("path", d="M-9.5,-13 L-11,-3.5 L-11.5,5.8", stroke="#17120e", stroke_width=1.9, fill="none", stroke_linecap="round"),
        el("path", d="M7.5,-12.5 L8.5,-3.5 L9,5.8", stroke="#17120e", stroke_width=1.9, fill="none", stroke_linecap="round"),
        # Bushy tail with white terminal brush
        el("path", d="M-14,-18 C-21,-17.5 -26,-12.5 -27.5,-5.5 C-23,-6.5 -18.5,-11 -14,-14.5Z", fill="#c96428"),
        el("path", d="M-23.5,-10 C-26,-7.5 -27.5,-5.5 -27.5,-5.5 C-24,-6 -21.5,-8 -20.5,-9.8Z", fill="#f7f4eb"),
        # Sculpted canid torso with deep chest, tucked flank waist, and muscular hindquarter haunch
        el("path", d=(
            "M-15.5,-15 C-16,-19.5 -12,-22 -6,-21.5 C0,-21 5,-21.5 10,-22.5 "
            "C13,-20 14.5,-15 12.5,-11.5 C9.5,-10.5 6.5,-11 3.5,-12.5 "
            "C-2,-14 -7,-13.5 -10.5,-11.5 C-13.5,-11.5 -15,-13 -15.5,-15Z"
        ), fill="#c96428"),
        el("path", d="M-11,-12 C-6,-14 2,-13.5 7,-11.2 C10,-11 12,-11.5 12.5,-12.5 C7,-13.5 -3,-14.5 -11,-12Z", fill="#964316", opacity=0.55),
        # Near-side jointed hind leg and foreleg (rufous upper + black stocking)
        el("path", d="M-13,-14 L-14.5,-4 L-13.5,6.2", stroke="#1c1612", stroke_width=2.1, fill="none", stroke_linecap="round"),
        el("path", d="M-12.5,-14.5 L-14.2,-5", stroke="#c96428", stroke_width=3.0, fill="none", stroke_linecap="round"),
        el("path", d="M10.5,-12.5 L11.8,-3.5 L12.8,6.2", stroke="#1c1612", stroke_width=2.1, fill="none", stroke_linecap="round"),
        el("path", d="M10.5,-13 L11.5,-4.5", stroke="#c96428", stroke_width=2.8, fill="none", stroke_linecap="round"),
        # Neck, black erectile mane, slender fox-like muzzle, white throat patch, and tall ears
        el("path", d="M8.5,-20.5 C12,-25.5 15.5,-29.5 19,-30.5 L26.5,-27.5 C25,-25 21,-24.2 18,-23.5 C16,-19 14,-15 11,-13Z", fill="#d46c2c"),
        el("path", d="M3.5,-21.2 C8,-24.5 12.5,-28 17,-30 C16,-26 13,-23 9.5,-20.5Z", fill="#1a1410"),
        el("path", d="M17.5,-25.2 C21,-25 24,-25.5 25.5,-26.5 C23.5,-24 20,-23.2 17,-23.5Z", fill="#f7f4eb"),
        el("circle", cx=25.8, cy=-27.2, r=1.0, fill="#1a1410"),
        # Tall upright ears with white inner pinnae
        el("path", d="M15.8,-29.2 L15.2,-36.8 L19.2,-30.2Z M18.8,-29.8 L20.2,-36.2 L22.2,-29.2Z", fill="#c96428"),
        el("path", d="M16.3,-30.2 L16.0,-34.8 L18.4,-30.2Z", fill="#f5ede0"),
        el("circle", cx=20.5, cy=-28.2, r=0.8, fill="#1a1410"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def iguana(x, y, s):
    """Hispaniolan Rhinoceros Iguana (Cyclura cornuta) with dorsal spine crest, dewlap, nasal horns, and banded tail."""
    return g([
        el("ellipse", cx=2, cy=5.5, rx=20, ry=2.4, fill="#000000", opacity=0.22),
        # Muscular legs and clawed toes
        el("path", d="M-4,1 L-8,5.5 L-11,5.5 M9,0 L12,5.5 L15,5.5", stroke="#58563e", stroke_width=2.4, fill="none", stroke_linecap="round"),
        # Heavy tapering tail with dark bands and robust scaly body
        el("path", d="M-34,2.5 C-22,3.5 -12,2 -6,-1 C1,-6 10,-6 16,-3 C20,-4 24,-2 25,1 C20,3 14,2 10,1 C3,3 -10,5 -34,2.5Z", fill="#737052"),
        el("path", d="M-24,2.5 L-22,1 M-18,2.2 L-16,0.2 M-12,1.5 L-10,-0.5", stroke="#454230", stroke_width=1.6),
        el("path", d="M-6,-1 C1,-4 9,-4 14,-1 C8,2 -1,2 -6,-1Z", fill="#94906b", opacity=0.7),
        # Gular dewlap pouch and nasal horn tubercles
        el("path", d="M15,0 Q19,4.8 22.5,1.5Z", fill="#615e44"),
        el("path", d="M21,-2.8 L22,-4.8 L22.8,-2.5 L23.6,-4.2 L24.2,-2.0", fill="#4a4834"),
        # Serrated dorsal crest spines
        el("path", d="M-14,0.5 L-12,-2.5 L-10,0 L-8,-3.5 L-6,-0.5 L-4,-4.5 L-2,-1.5 L0,-5.5 L2,-2 L4,-6 L6,-2.5 L8,-5.5 L10,-2 L12,-4.5 L14,-1.5",
           stroke="#4d4a35", stroke_width=1.1, fill="none", stroke_linejoin="round"),
        el("circle", cx=19.5, cy=-1.5, r=0.85, fill="#1a1812"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


def morpho(x, y, s):
    """Iridescent Blue Morpho butterfly (Morpho menelaus) with black wing margins and white marginal spots."""
    return g([
        # Forewings and hindwings with dark border and iridescent blue interior
        el("path", d="M0,0 C-3,-6 -9,-8 -11,-3 C-11,1 -6,3 -1,1 C-5,4 -7,8 -4,9 C-1,9 0,5 0,1Z", fill="#182232"),
        el("path", d="M0,0 C3,-6 9,-8 11,-3 C11,1 6,3 1,1 C5,4 7,8 4,9 C1,9 0,5 0,1Z", fill="#182232"),
        el("path", d="M-0.5,0 C-3,-5 -8,-6.5 -9.5,-2.5 C-9.5,0.5 -5,2 -1,0.8 C-4,3.5 -5.5,6.5 -3.5,7.5 C-1.5,7.5 -0.5,4 -0.5,0.8Z", fill="#1f82e8"),
        el("path", d="M0.5,0 C3,-5 8,-6.5 9.5,-2.5 C9.5,0.5 5,2 1,0.8 C4,3.5 5.5,6.5 3.5,7.5 C1.5,7.5 0.5,4 0.5,0.8Z", fill="#46a8ff"),
        el("ellipse", cx=0, cy=1, rx=0.8, ry=3.5, fill="#121820"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})", class_="fly")


def hummingbird(x, y, s):
    """Glittering emerald hummingbird hovering with iridescent gorget, blurred wings, and needle bill."""
    return g([
        # Motion-blurred upper and lower wing beats
        el("path", d="M-1,-1 C-6,-10 -12,-12 -14,-9 C-12,-4 -6,-1 -1,0Z", fill="#88d4be", opacity=0.72),
        el("path", d="M-2,-1 C-8,-7 -13,-6 -14,-3 C-10,-1 -5,0 -2,0Z", fill="#54a890", opacity=0.55),
        # Forked tail
        el("path", d="M-5,0.5 L-13,4.5 L-11,1.5 L-13,-0.5 L-5,-0.5Z", fill="#114d3b"),
        # Emerald body, ruby-magenta gorget, and needle bill
        el("path", d="M-6,0 C-4,-3 2,-3.5 5,-1.5 C6,0 4,2.5 0,2.5 C-3,2.5 -5,1.5 -6,0Z", fill="#188c68"),
        el("path", d="M1.5,-1.2 C4,-1.5 5.5,-0.2 4.5,1.2 C2.8,1.5 1.2,0.5 1.5,-1.2Z", fill="#e02b68"),
        el("path", d="M5,-1.0 L14,-2.2", stroke="#181818", stroke_width=0.85, stroke_linecap="round"),
        el("circle", cx=3.5, cy=-1.2, r=0.65, fill="#111111"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})", class_="fly")


def pitcher_plant(x, y, s, flower=False):
    """Endemic Tepui sun pitcher plant (Heliamphora nutans) with S-curved crimson-flushed pitchers and nodding bloom."""
    tubes = [el("ellipse", cx=0, cy=1, rx=14, ry=3.2, fill="#1b1410", opacity=0.45)]
    specs = [
        (-9, 20, -18, "#638f3c", "#9c3228"),
        (-3, 27, -5, "#78a648", "#b5382c"),
        (4, 24, 9, "#6d9942", "#a83428"),
        (9, 18, 20, "#568034", "#8c2b22"),
    ]
    for dx, h, rot, col, rim_col in specs:
        tubes.append(g([
            # S-curved tubular funnel with ventricose base and flared mouth
            el("path", d=(
                f"M-1.2,0 C-3.2,{-h * 0.28} -2.2,{-h * 0.52} -4.6,{-h * 0.92} "
                f"C-2.5,{-h * 1.04} 2.5,{-h * 1.04} 4.6,{-h * 0.92} "
                f"C2.2,{-h * 0.52} 3.2,{-h * 0.28} 1.2,0Z"
            ), fill=col),
            # Crimson upper flushing & shaded right side
            el("path", d=(
                f"M-3.2,{-h * 0.55} C-3.8,{-h * 0.72} -4.6,{-h * 0.92} -4.6,{-h * 0.92} "
                f"C-2.5,{-h * 1.04} 2.5,{-h * 1.04} 4.6,{-h * 0.92} "
                f"C4.6,{-h * 0.92} 3.8,{-h * 0.72} 3.2,{-h * 0.55}Z"
            ), fill=rim_col, opacity=0.62),
            # Dark interior throat & rolled crimson peristome lip
            el("ellipse", cx=0, cy=-h * 0.90, rx=3.6, ry=1.8, fill="#421010"),
            el("path", d=f"M-4.6,{-h * 0.92} Q0,{-h * 1.05} 4.6,{-h * 0.92}", stroke="#7a1818", stroke_width=1.1, fill="none"),
            # Small concave apical nectar spoon
            el("path", d=f"M-1.2,{-h * 0.98} C-1.6,{-h * 1.10} 1.6,{-h * 1.10} 1.2,{-h * 0.98}Z", fill="#b82424"),
        ], transform=f"translate({n(dx)} 0) rotate({n(rot)})"))
    if flower:
        tubes.append(g([
            el("path", d="M2,0 Q6,-22 3,-38 Q1,-42 -2,-39", stroke="#8c3228", stroke_width=0.9, fill="none"),
            el("path", d="M-2,-39 C-5,-37 -5,-34 -2,-33 C1,-34 1,-37 -2,-39Z", fill="#fceef2"),
            el("path", d="M-2,-39 C-4,-37 -3,-34 -1,-34", stroke="#e89cb0", stroke_width=0.6, fill="none"),
        ]))
    return g(tubes, transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


# ==============================================================================
# REEF PRIMITIVES
# ==============================================================================
def branch_coral(rng, x, y, L, depth, col, width, spread=0.55, up=-math.pi / 2):
    """Detailed Staghorn / Elkhorn coral (Acropora) with 3D shaded branches and pale growing polyp tips."""
    segs = []
    tips = []

    def rec(px, py, ang, ln, d):
        ex, ey = px + math.cos(ang) * ln, py + math.sin(ang) * ln
        segs.append(f"M{n(px)},{n(py)} L{n(ex)},{n(ey)}")
        if d > 0:
            for k in (-1, 1):
                rec(ex, ey, ang + k * spread * rng.uniform(0.5, 1.08), ln * rng.uniform(0.64, 0.82), d - 1)
        else:
            tips.append(el("circle", cx=ex, cy=ey, r=width * 0.48))

    for k in range(3):
        rec(x + (k - 1) * width, y, up + (k - 1) * 0.42 + rng.uniform(-0.08, 0.08), L * rng.uniform(0.82, 1.02), depth)
    d = " ".join(segs)
    return g([
        el("path", d=d, stroke=mix(col, "#08101c", 0.38), stroke_width=width + 1.8, fill="none", stroke_linecap="round"),
        el("path", d=d, stroke=col, stroke_width=width, fill="none", stroke_linecap="round"),
        el("path", d=d, stroke=mix(col, "#fff8e8", 0.35), stroke_width=width * 0.38, fill="none", stroke_linecap="round", opacity=0.7),
        g(tips, fill=mix(col, "#ffffff", 0.55)),
    ])


def brain_coral(rng, x, y, r, col="#cfa344"):
    """Grooved Diploria labyrinthiformis brain coral dome with 3D shading and meandering gyri ridges."""
    lines_dark, lines_light = [], []
    for i in range(1, 6):
        rr = r * i / 5.5
        pts = []
        pts_hi = []
        for j in range(17):
            a = math.pi + math.pi * j / 16
            wob = rr + math.sin(j * 1.9 + i) * r * 0.055 + rng.uniform(-r * 0.025, r * 0.025)
            px, py = x + math.cos(a) * wob, y + math.sin(a) * wob * 0.76
            pts.append((px, py))
            pts_hi.append((px, py - 0.9))
        lines_dark.append(smooth(pts))
        lines_light.append(smooth(pts_hi))
    return g([
        el("ellipse", cx=x, cy=y + 1, rx=r * 1.04, ry=r * 0.22, fill="#081826", opacity=0.35),
        el("path", d=f"M{n(x - r)},{n(y)} A{n(r)},{n(r * 0.78)} 0 0 1 {n(x + r)},{n(y)}Z", fill=col),
        el("path", d=f"M{n(x - r * 0.75)},{n(y - r * 0.15)} A{n(r * 0.65)},{n(r * 0.52)} 0 0 1 {n(x + r * 0.35)},{n(y - r * 0.15)}Z",
           fill=mix(col, "#fff8d6", 0.32), opacity=0.45),
        el("path", d=f"M{n(x - r)},{n(y)} A{n(r)},{n(r * 0.78)} 0 0 1 {n(x + r)},{n(y)}Z", fill="#000000", opacity=0.18,
           transform=f"translate({n(r * 0.25)} 0) scale(0.75 1)", style=f"transform-origin:{n(x)}px {n(y)}px"),
        el("path", d=" ".join(lines_dark), stroke=mix(col, "#1a1000", 0.45), stroke_width=1.25, fill="none", opacity=0.8),
        el("path", d=" ".join(lines_light), stroke=mix(col, "#fff8d6", 0.42), stroke_width=0.75, fill="none", opacity=0.65),
    ])


def sea_fan(rng, x, y, h, col="#9448b0"):
    """Reticulated Gorgonia ventalina sea fan with branching main veins and delicate meshwork."""
    segs_main, segs_mesh = [], []
    for i in range(15):
        a = math.radians(-152 + 124 * i / 14)
        L = h * rng.uniform(0.74, 1.02)
        ex, ey = x + math.cos(a) * L * 0.82, y + math.sin(a) * L
        cx_, cy_ = x + math.cos(a) * L * 0.35, y + math.sin(a) * L * 0.62
        segs_main.append(f"M{n(x)},{n(y)} Q{n(cx_)},{n(cy_)} {n(ex)},{n(ey)}")
        for t in (0.4, 0.7, 0.9):
            px, py = quad((x, y), (cx_, cy_), (ex, ey), t)
            segs_mesh.append(f"M{n(px)},{n(py)} l{n(rng.uniform(-4, 4))},{n(rng.uniform(-4, 1))}")
    fan = el("path", d=(
        f"M{n(x)},{n(y)} Q{n(x - h * 0.92)},{n(y - h * 0.78)} {n(x - h * 0.22)},{n(y - h * 1.02)} "
        f"Q{n(x + h * 0.42)},{n(y - h * 1.06)} {n(x + h * 0.78)},{n(y - h * 0.48)}Z"
    ), fill=col, opacity=0.32)
    return g([
        fan,
        el("path", d=" ".join(segs_mesh), stroke=mix(col, "#ffc8f0", 0.3), stroke_width=0.65, fill="none", opacity=0.7),
        el("path", d=" ".join(segs_main), stroke=col, stroke_width=1.15, fill="none", opacity=0.92),
    ], class_="sway", style=f"transform-origin:{n(x)}px {n(y)}px;animation-delay:{n(-rng.uniform(0, 5))}s")


def tube_sponge(x, y, h, col="#b552bd"):
    """Cluster of Caribbean stove-pipe / tube sponges (Aplysina archeri) with ridged walls and oscula."""
    out = []
    lit = mix(col, "#ffd6ff", 0.3)
    shade = mix(col, "#1a0624", 0.45)
    for dx, hh, w in ((-6.5, 0.95, 7.0), (0, 1.25, 8.0), (6.5, 0.82, 6.5)):
        th = h * hh
        tx = x + dx
        out.append(el("rect", x=tx - w / 2, y=y - th, width=w, height=th, rx=w * 0.45, fill=col))
        out.append(el("rect", x=tx, y=y - th, width=w / 2, height=th, rx=w * 0.22, fill=shade, opacity=0.35))
        out.append(el("rect", x=tx - w * 0.35, y=y - th + 2, width=w * 0.22, height=th - 4, rx=w * 0.1, fill=lit, opacity=0.4))
        out.append(el("ellipse", cx=tx, cy=y - th + 2, rx=w * 0.36, ry=1.5, fill=shade))
    return g(out)


def seagrass(rng, x0, x1, y, count, h, col="#569844"):
    segs_dark, segs_light = [], []
    dark = mix(col, "#183d1c", 0.32)
    light = mix(col, "#a8e06c", 0.28)
    for i in range(count):
        x = rng.uniform(x0, x1)
        hh = h * rng.uniform(0.5, 1.15)
        cmd = f"M{n(x)},{n(y)} q{n(rng.uniform(-6, 6))},{n(-hh * 0.52)} {n(rng.uniform(-8, 8))},{n(-hh)}"
        (segs_dark if i % 2 == 0 else segs_light).append(cmd)
    return g([
        el("path", d=" ".join(segs_dark), stroke=dark, stroke_width=1.9, fill="none", stroke_linecap="round"),
        el("path", d=" ".join(segs_light), stroke=light, stroke_width=1.6, fill="none", stroke_linecap="round"),
    ], class_="sway", style=f"transform-origin:{n((x0 + x1) / 2)}px {n(y)}px")


def light_rays(s: Scene, x0, x1, y0, y1, count, op=0.18):
    rng = s.rng
    grad = s.linear("ray", [(0, "#ffffff", op), (0.6, "#ffffff", op * 0.45), (1, "#ffffff", 0)])
    rays = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        w = rng.uniform(16, 48)
        sk = rng.uniform(42, 115)
        rays.append(el("path", d=P([(x, y0), (x + w, y0), (x + w + sk * 1.45, y1), (x + sk, y1)])))
    return g(rays, fill=grad, class_="shimmer")


# ==============================================================================
# SCENE: SEA-TO-SUMMIT TRANSECT
# ==============================================================================
def build_transect(labels):
    s = Scene("transect", 1600, 600, 1999)
    rng = s.rng
    W, H = s.w, s.h
    s.blur("mist", 9)
    s.blur("soft", 3)
    sky(s, [(0, "#6ba8d9"), (0.42, "#b4d9ef"), (0.78, "#dfeef5"), (1, "#f6efe1")])
    sun(s, 1180, 92, 26)
    for cx, cy, w in ((175, 88, 175), (555, 68, 145), (900, 118, 200), (1355, 58, 160)):
        s.add(cloud(rng, cx, cy, w))

    # Distant cordillera across the right half
    far, _ = mountain(s, "far", [(620, 365), (700, 322), (760, 295), (830, 266), (925, 296), (1055, 226), (1175, 276),
                                 (1285, 186), (1415, 146), (1500, 168), (1600, 136)],
                      425, "#9cb5cc", shade="#5f7996", shade_op=0.35, snow=212, rough=11)
    s.add(far)
    s.add(mist(s, 1080, 310, 260, 18, op=0.45))

    # Continuous topographic ground profile from sea floor (x=0) to Andean summit foothills (x=1600)
    # Recessed basins for the Caribbean Sea (0..368), Amazon River (685..805), Pantanal (855..1045), and Cataract Pool (1260..1295)
    keys = [
        (0, 556), (70, 546), (150, 552), (235, 534), (295, 502),
        (335, 452), (368, 412), (402, 392), (430, 385), (560, 385),
        (620, 382), (682, 383), (712, 395), (750, 397), (785, 394), (808, 383),
        (852, 384), (882, 396), (950, 399), (1018, 396), (1048, 384),
        (1110, 372), (1175, 360), (1228, 352), (1258, 354), (1285, 354),
        (1302, 304), (1345, 302), (1415, 294), (1505, 284), (1600, 276),
    ]
    terrain = interp(keys)

    # Andes massif on the right with cirque glacier seated in the high saddle and blending into the alpine páramo
    andes, _ = mountain(s, "andes", [(1310, 320), (1362, 244), (1405, 178), (1438, 142), (1475, 96), (1512, 146), (1548, 114), (1600, 162)],
                        325, "#786454", shade="#24202c", shade_op=0.44, snow=168, rough=10)
    s.add(andes)
    # Mid-ground vegetated Yungas / cloud-forest foothill ridge bridging Cerrado -> Cataracts -> Andes massif
    foothill, _ = hill(s, [(1165, 366), (1225, 336), (1275, 298), (1328, 268), (1372, 256), (1425, 294)],
                       370, "#4f6e48", rough=6)
    s.add(foothill)
    # Valley glacier ribbon descending from the cirque saddle into a high alpine tarn & meltwater stream
    glac_l = [(1476, 134), (1466, 178), (1452, 224), (1434, 268), (1418, 294)]
    glac_r = [(1504, 142), (1490, 184), (1474, 228), (1458, 270), (1444, 293)]
    s.add(el("path", d=smooth(glac_l) + " " + " ".join(f"L{n(x)},{n(y)}" for x, y in reversed(glac_r)) + "Z",
             fill="#dceef8", opacity=0.92))
    s.add(el("path", d="M1462,182 Q1476,188 1488,184 M1448,224 Q1462,230 1472,226 M1434,262 Q1446,268 1456,264",
             stroke="#6b9ebc", stroke_width=1.2, fill="none", opacity=0.65))
    s.add(mist(s, 1465, 242, 135, 16, op=0.58))

    # Caribbean Sea water column (x=0..368, bounded smoothly by the sloping beach shoreline)
    sea_top = 412
    sea_poly = [(0, sea_top), (368, sea_top)] + [(x, terrain(x)) for x in range(365, -1, -15)]
    s.add(el("path", d=P(sea_poly),
             fill=s.linear("sea", [(0, "#35b8d4"), (0.35, "#1b89b0"), (0.75, "#105882"), (1, "#083152")])))
    s.add(el("path", d=smooth([(x, sea_top + 2 * math.sin(x / 18)) for x in range(0, 369, 14)]) + f" L368,{sea_top - 3} L0,{sea_top - 3}Z",
             fill="#a8e8f2", opacity=0.78))
    s.add(light_rays(s, 0, 310, sea_top, 545, 8, op=0.20))

    # Continuous continental & marine lithosphere cross-section (zero vertical cut between sea and land!)
    land_pts = [(x, terrain(x)) for x in range(0, 1601, 8)]
    s.add(el("path", d=smooth(land_pts) + f" L1600,{H} L0,{H}Z", fill=s.linear("land", [(0, "#8f6e48"), (1, "#4d3826")])))

    # Smooth subsurface geological strata following a damped baseline so surface cliffs don't create spikes
    def base_prof(x):
        if x < 368:
            return 556 - 156 * ((x / 368) ** 1.4)
        if x < 1050:
            return 400 - 12 * math.sin((x - 368) / 682 * math.pi)
        return 400 - 110 * (((x - 1050) / 550) ** 1.25)

    strata = []
    for k, (col, amp) in enumerate((("#75573a", 6), ("#634830", 8), ("#523a27", 6), ("#402c1e", 5))):
        pts = [(x, max(terrain(x) + 14 + k * 8, base_prof(x) + 26 + k * 36 + amp * math.sin(x / 75 + k * 1.1)))
               for x in range(0, 1601, 20)]
        strata.append(el("path", d=smooth(pts) + f" L1600,{H} L0,{H}Z", fill=col))
    # Karst limestone subterranean cave system & stalactites under mogotes (x=440..555)
    strata.append(el("path", d="M442,425 Q468,412 495,422 Q525,410 548,426 Q535,442 495,438 Q460,442 442,425Z", fill="#2a1f18", opacity=0.65))
    strata.append(el("path", d="M458,418 l2,9 l2,-9 M480,419 l2,11 l2,-11 M518,416 l2,10 l2,-10 M534,420 l1.5,8 l1.5,-8", fill="#9c9684", opacity=0.6))
    s.add(g(strata, opacity=0.92))

    # ==========================================================================
    # CONTINUOUS BIOME SURFACE BELTS & ECOTONE TRANSITIONS (Left -> Right)
    # ==========================================================================

    # 1. Reef carbonate sand bed & sloping coastal beach berm (x=0..432, tapering smoothly into karst valley)
    sand_top = [(x, terrain(x)) for x in range(0, 433, 12)]
    sand_bot = [(432, terrain(432) + 2), (395, terrain(395) + 12), (355, terrain(355) + 18),
                (295, terrain(295) + 22), (180, 578), (0, 585)]
    s.add(el("path", d=smooth(sand_top) + " " + " ".join(f"L{n(x)},{n(y)}" for x, y in sand_bot) + "Z",
             fill=s.linear("reefbed", [(0, "#f0dfb4"), (0.45, "#dfd0a6"), (1, "#a89467")])))

    # 2. Karst terra-rossa valley floor & green pasture transition (x=415..575)
    karst_top = [(x, terrain(x)) for x in range(415, 576, 10)]
    karst_bot = [(575, terrain(575) + 3), (540, terrain(540) + 10), (445, terrain(445) + 10), (415, terrain(415) + 2)]
    s.add(el("path", d=smooth(karst_top) + " " + " ".join(f"L{n(x)},{n(y)}" for x, y in karst_bot) + "Z", fill="#7a4428"))

    # 3. Amazon rainforest humus & mossy floor belt (x=555..875)
    rf_top = [(x, terrain(x)) for x in range(555, 876, 10)]
    rf_bot = [(875, terrain(875) + 3), (840, terrain(840) + 11), (585, terrain(585) + 11), (555, terrain(555) + 2)]
    s.add(el("path", d=smooth(rf_top) + " " + " ".join(f"L{n(x)},{n(y)}" for x, y in rf_bot) + "Z", fill="#34592c"))

    # 4. Pantanal marsh sedge & wetland mud belt (x=850..1060)
    pan_top = [(x, terrain(x)) for x in range(850, 1061, 10)]
    pan_bot = [(1060, terrain(1060) + 2), (1025, terrain(1025) + 10), (880, terrain(880) + 10), (850, terrain(850) + 2)]
    s.add(el("path", d=smooth(pan_top) + " " + " ".join(f"L{n(x)},{n(y)}" for x, y in pan_bot) + "Z", fill="#56783a"))

    # 5. Cerrado golden-ochre savanna topsoil belt (x=1038..1245)
    cer_top = [(x, terrain(x)) for x in range(1038, 1246, 10)]
    cer_bot = [(1245, terrain(1245) + 3), (1210, terrain(1210) + 11), (1070, terrain(1070) + 11), (1038, terrain(1038) + 2)]
    s.add(el("path", d=smooth(cer_top) + " " + " ".join(f"L{n(x)},{n(y)}" for x, y in cer_bot) + "Z", fill="#ab8e44"))

    # 6. Cataracts basalt rock cliff escarpment (x=1235..1345)
    basalt_pts = [
        (1235, terrain(1235) + 4), (1258, 355), (1285, 355), (1302, 304), (1345, 302),
        (1345, 326), (1312, 336), (1292, 366), (1255, 364), (1235, terrain(1235) + 4),
    ]
    s.add(el("path", d=P(basalt_pts), fill="#4a433d"))
    s.add(el("path", d="M1285,355 L1302,304 L1328,303 L1312,336 L1292,366Z", fill="#332e2a"))
    s.add(el("path", d="M1292,318 L1338,316 M1288,334 L1325,332", stroke="#24201d", stroke_width=1.4, opacity=0.6))

    # 7. Andean alpine páramo & cloud-forest turf belt (x=1320..1600)
    and_top = [(x, terrain(x)) for x in range(1320, 1601, 12)]
    and_bot = [(1600, terrain(1600) + 14), (1350, terrain(1350) + 12), (1320, terrain(1320) + 2)]
    s.add(el("path", d=smooth(and_top) + " " + " ".join(f"L{n(x)},{n(y)}" for x, y in and_bot) + "Z", fill="#7d8548"))
    # Meltwater stream connecting the glacier toe (1430, 293) along the páramo to the cataract rim (1302, 304)
    s.add(el("path", d=smooth([(1432, 293), (1395, 298), (1350, 302), (1300, 304)]),
             stroke="#8ad4e6", stroke_width=3.2, fill="none", stroke_linecap="round", opacity=0.85))

    # ==========================================================================
    # ZONE DETAILS & ECOTONE FLORA/FAUNA
    # ==========================================================================

    # Zone 0: Coral Reef Shelf & Seagrass Slope (0-335)
    s.add(seagrass(rng, 255, 332, 520, 28, 16, "#4d8f3c"))
    for x, c in ((28, "#e06d53"), (88, "#d4a43c"), (148, "#e89c48"), (208, "#d65c82"), (268, "#e06d53")):
        s.add(branch_coral(rng, x, terrain(x) + 2, 17, 3, c, 2.6))
    s.add(brain_coral(rng, 118, terrain(118) + 3, 14), brain_coral(rng, 242, terrain(242) + 3, 12, "#c29438"))
    s.add(sea_fan(rng, 58, terrain(58) + 2, 28), sea_fan(rng, 182, terrain(182) + 2, 24, "#9e4895"))
    s.add(tube_sponge(168, terrain(168) + 2, 18, "#b552bd"), tube_sponge(45, terrain(45) + 2, 15, "#e08238"))
    s.add(school(rng, 125, 476, 11, 32, 4.2, "#38a6e2", stripe="#f5d438"))
    s.add(school(rng, 232, 496, 7, 24, 5.0, "#f5c428", stripe="#182636", flip=True))
    s.add(manta(195, 446, 0.52))
    s.add(turtle(68, 458, 0.75))
    s.add(water_lines(rng, 0, 355, sea_top + 2, sea_top + 22, 28, op=0.52))

    # Zone 1: Intertidal Mangroves & Coastal Palms (335-425)
    # Mangroves rooted across the shoreline (prop roots arching into the shallow water & wet sand)
    for x in (342, 356, 370, 384):
        y = terrain(x)
        yc = min(y - 22, sea_top - 16)
        roots = " ".join(f"M{n(x)},{n(yc + 6)} Q{n(x + d * 0.65)},{n((yc + y) * 0.5 + 4)} {n(x + d)},{n(y + 6)}"
                         for d in (-14, -8, -3, 3, 8, 14))
        s.add(el("path", d=roots, stroke="#523f2b", stroke_width=1.6, fill="none"))
        s.add(crown(rng, x, yc - 2, 15, ("#24522a", "#387436", "#609c4a"), k=6, flat=0.62))
    s.add(egret(362, sea_top - 42, 0.55))
    for x, h, lean in ((398, 68, 9), (414, 56, -7)):
        s.add(palm(rng, x, terrain(x) + 2, h, lean, 24, nfr=10))

    # Zone 2: Mogotes Karst (425-565) with realistic sheer limestone cliffs & piedmont vegetation transitions
    for keys_m, r_lit, r_sh in (
        ([(426, 386), (430, 312), (445, 294), (462, 298), (474, 386)], "#c2beb0", "#858173"),
        ([(504, 386), (509, 296), (529, 282), (548, 290), (562, 386)], "#c8c4b4", "#8a8677"),
    ):
        x0, x1 = keys_m[0][0], keys_m[-1][0]
        top = min(p[1] for p in keys_m)
        mw = x1 - x0
        d = smooth(keys_m) + "Z"
        s.add(el("path", d=d, fill=r_lit))
        cid = s.clip(f"mog{x0}", d)
        m_in = [
            el("path", d=f"M{n(x0 + mw * 0.50)},{n(top)} L{n(x1)},{n(top)} L{n(x1)},388 L{n(x0 + mw * 0.55)},388Z",
               fill=r_sh, opacity=0.92),
        ]
        for b in range(1, 7):
            fx = x0 + mw * (0.10 + 0.80 * b / 7)
            m_in.append(el("path", d=f"M{n(fx)},{n(top + 10)} L{n(fx + 3)},{n(top + 12)} L{n(fx + 2)},385 L{n(fx - 1)},385Z",
                           fill="#595c52", opacity=0.45))
        m_in.append(el("path", d=f"M{n(x0)},{n(top + 38)} Q{n((x0 + x1) * 0.5)},{n(top + 42)} {n(x1)},{n(top + 37)} "
                                 f"M{n(x0)},{n(top + 64)} Q{n((x0 + x1) * 0.5)},{n(top + 68)} {n(x1)},{n(top + 63)}",
                       stroke="#3e4238", stroke_width=0.9, opacity=0.45, fill="none"))
        m_in.append(el("path", d=f"M{n(x0 + mw * 0.32)},386 Q{n(x0 + mw * 0.42)},370 {n(x0 + mw * 0.52)},386Z",
                       fill="#182214", opacity=0.85))
        # Overhanging jungle cap & basal piedmont shrub skirt inside clip
        m_in.append(el("path", d=f"M{n(x0)},{n(top + 22)} Q{n((x0 + x1) * 0.5)},{n(top + 12)} {n(x1)},{n(top + 22)} L{n(x1)},{n(top)} L{n(x0)},{n(top)}Z",
                       fill="#24471e"))
        s.add(g(m_in, clip_path=cid))
        # Lush overhanging summit dome cap following the curved top contour naturally
        for i in range(11):
            t_ = i / 10
            vx = x0 + mw * (0.06 + 0.88 * t_)
            arch = ((t_ - 0.5) * 2) ** 2
            vy = top - 2 + arch * 13 + rng.uniform(-1.2, 1.5)
            s.add(crown(rng, vx, vy, rng.uniform(7.0, 9.5),
                        ("#20481e", "#3c6e2e", "#6ea044"), k=5, detail=False))
        # Basal piedmont shrubs blending the mogote base smoothly into the valley & adjacent biomes
        for i in range(6):
            bx = x0 + mw * (0.05 + 0.90 * i / 5)
            s.add(crown(rng, bx, 381 + rng.uniform(-2, 3), rng.uniform(5.5, 8.0),
                        ("#1e441c", "#346428", "#5c8e3c"), k=5, detail=False))
    # Tobacco valley rows & curing bohío between mogotes
    rows = " ".join(f"M{n(474 + i * 4.5)},384 l2,3" for i in range(7))
    s.add(el("path", d=rows, stroke="#6ca338", stroke_width=2.6, stroke_linecap="round"))
    s.add(el("rect", x=480, y=378, width=14, height=6, fill="#6e5230"),
          el("path", d="M477,379 L487,368 L497,379Z", fill="#a67e46"),
          el("path", d="M487,368 L497,379 L489,379Z", fill="#75562e"))
    s.add(palm(rng, 499, 384, 48, 2, 16, royal=True, nfr=10, trunk_col="#d4ccb8"))

    # Zone 3: Amazon Rainforest (555-865) with recessed meandering river channel & gallery transition
    # Recessed Amazon river water filling the concave channel (x=682..808) BEFORE foreground bank foliage
    s.add(el("path", d=smooth([(680, 384), (745, 385), (810, 384)]) +
                       " " + " ".join(f"L{n(x)},{n(terrain(x) + 1)}" for x in range(810, 679, -10)) + "Z",
             fill=s.linear("amz_riv", [(0, "#8fa472"), (1, "#586e44")])))
    s.add(water_lines(rng, 692, 798, 386, 394, 8, op=0.48))
    s.add(dolphin(746, 388, 0.55))

    # Continuous multi-tier rainforest canopy bridging smoothly from the second mogote (x=552) to the Pantanal edge (x=868)
    s.add(g(canopy_band(s, 552, 868, lambda x: min(terrain(x), 383), 30, 14, 22, ("#194224", "#296432", "#4b8c42"), lift=10, k=6)))
    s.add(g(canopy_band(s, 558, 692, terrain, 11, 14, 21, ("#204f2b", "#367838", "#64a44c"), lift=2, k=6)))
    s.add(g(canopy_band(s, 798, 865, terrain, 7, 13, 19, ("#204f2b", "#367838", "#64a44c"), lift=2, k=6)))
    s.add(broadleaf_tree(rng, 636, terrain(636), 96, 32, ("#1f4a27", "#387838", "#72ae50"), emergent=True))
    s.add(broadleaf_tree(rng, 792, terrain(792), 88, 28, ("#24542c", "#40823e", "#78b456"), emergent=True))
    s.add(macaw(700, 268, 0.58), macaw(742, 252, 0.52, flip=True))
    s.add(toucan(812, 328, 0.52))
    s.add(mist(s, 712, 332, 125, 14, op=0.52))

    # Zone 4: Pantanal Wetland (855-1048) nestled in its concave floodplain basin with tapering shorelines
    pan_water = [(854, 385), (950, 386), (1046, 385)] + [(x, terrain(x) + 1) for x in range(1046, 853, -10)]
    s.add(el("path", d=P(pan_water), fill=s.linear("pan_w", [(0, "#5ea0bd"), (1, "#38728c")])))
    s.add(water_lines(rng, 868, 1034, 387, 396, 15, op=0.55))
    for lx, ly, lr in ((895, 393, 6.5), (930, 395, 8.0), (972, 394, 7.0)):
        s.add(water_lily(rng, lx, ly, lr))
    # Ecotone sedges & gallery palms bridging Rainforest -> Pantanal (850..885) and Pantanal -> Cerrado (1020..1055)
    s.add(tufts(rng, 850, 1052, lambda x: min(terrain(x), 387), 32, 9, "#6e9438"))
    for x in (866, 1028):
        s.add(palm(rng, x, terrain(x) + 1, 48, rng.uniform(-4, 4), 15, nfr=9, coconuts=False, trunk_col="#6c5a46"))
    s.add(jabiru(946, 382, 0.58), caiman(992, 391, 0.55), capybara(912, 386, 0.58))

    # Zone 5: Cerrado Savanna (1045-1230) rising smoothly toward the Atlantic Forest escarpment
    s.add(tufts(rng, 1042, 1235, terrain, 64, 10, "#c4ab50"))
    for x in (1068, 1122, 1192):
        s.add(gnarled_tree(rng, x, terrain(x), 42))
    s.add(ipe(rng, 1152, terrain(1152), 48))
    s.add(termite_mound(1096, terrain(1096), 16), termite_mound(1210, terrain(1210), 13))
    s.add(maned_wolf(1170, terrain(1170) - 5, 0.58))

    # Zone 6: Atlantic Forest Escarpment and Cataracts (1225-1345)
    # Foothill shrubs & upper rim gallery forest clothing the basalt cliff transition on both sides
    s.add(g(canopy_band(s, 1225, 1272, terrain, 7, 9, 14, ("#1d4828", "#2f6a35", "#5a9846"), lift=2, k=5)))
    s.add(g(canopy_band(s, 1298, 1362, terrain, 9, 10, 15, ("#1b4628", "#2b6834", "#589846"), lift=3, k=5)))
    s.add(waterfall(s, 1290, 303, 353, 14))
    s.add(el("ellipse", cx=1286, cy=355, rx=23, ry=4.8, fill=s.linear("cat_pool", [(0, "#72cce0"), (1, "#3b8da8")])))
    s.add(water_lines(rng, 1268, 1302, 353, 357, 5, op=0.65))
    # Mossy basalt bank stones framing the plunge pool transition
    for bx, by, br in ((1262, 356, 5.5), (1306, 356, 6.0)):
        s.add(el("path", d=f"M{n(bx - br)},{n(by)} Q{n(bx)},{n(by - br * 0.9)} {n(bx + br)},{n(by)}Z", fill="#3d3834"))

    # Zone 7: Andes Alpine Páramo & Cordillera (1340-1600)
    s.add(tufts(rng, 1345, 1595, terrain, 58, 9, "#b8a854"))
    # Puya raimondii spikes & Espeletia frailejón rosettes on the high Andean páramo slope
    for x in (1382, 1445, 1518, 1565):
        y = terrain(x) + 1
        s.add(el("path", d=f"M{n(x - 5)},{n(y)} L{n(x)},{n(y - 5)} L{n(x + 5)},{n(y)}", stroke="#4d6b42", stroke_width=1.4, fill="none"))
        s.add(el("ellipse", cx=x, cy=y - 10, rx=2.2, ry=7.5, fill="#c4bc72"))
    for x, r in ((1368, 7), (1492, 9), (1545, 8)):
        y = terrain(x) + 2
        s.add(el("path", d=f"M{n(x - r)},{n(y)} L{n(x - r * 0.6)},{n(y - r * 0.7)} L{n(x + r * 0.5)},{n(y - r * 0.65)} L{n(x + r)},{n(y)}Z",
                 fill="#7a7b75"))
    s.add(condor(1420, 118, 0.75))

    # Interactive Biome Badges
    lab = []
    zones = [
        (165, 0, "waikiki"),
        (375, 1, "waikiki"),
        (500, 2, "waikiki"),
        (712, 3, "amazonia"),
        (950, 4, "amazonia"),
        (1130, 5, "brazilia"),
        (1280, 6, "brazilia"),
        (1480, 7, "brazilia"),
    ]
    for (x, idx, realm) in zones:
        txt = labels["transect"][idx]
        w = len(txt) * 6.4 + 24
        lab.append(g([
            el("rect", x=x - w / 2, y=H - 46, width=w, height=24, rx=12, fill="#001830", stroke="#f5c46e", stroke_width=0.7, opacity=0.88),
            el("text", txt, x=x, y=H - 30, text_anchor="middle", fill="#fbf7f0", font_family="Manrope, sans-serif",
               font_size=11, font_weight=700, letter_spacing="0.08em"),
        ], class_="nat-zone-badge", data_realm=realm))
        lab.append(el("path", d=f"M{n(x)},{n(H - 46)} L{n(x)},{n(H - 64)}", stroke="#f5c46e", stroke_width=1, opacity=0.55))
        lab.append(el("circle", cx=x, cy=H - 64, r=2.2, fill="#f5c46e", opacity=0.8))
    s.add(g(lab))
    return s.render(labels["aria"]["transect"])


# ==============================================================================
# SCENE: CORAL REEF AND MANGROVE COAST (SPLIT LEVEL)
# ==============================================================================
def build_reef(labels):
    s = Scene("reef", 1200, 720, 2021)
    rng = s.rng
    W, H = s.w, s.h
    WL = 210  # water line
    s.blur("mist", 8)
    s.blur("soft", 2.5)
    sky(s, [(0, "#5ea8dc"), (0.55, "#b3ddf2"), (1, "#e8f4f8")], h=WL + 4)
    sun(s, 980, 68, 23)
    s.add(cloud(rng, 260, 68, 185), cloud(rng, 690, 52, 135), cloud(rng, 1080, 82, 110, op=0.8))

    # Distant coral cay with beach berm and coconut palms
    s.add(el("path", d=smooth([(765, WL), (835, WL - 15), (930, WL - 22), (1015, WL - 12), (1075, WL)]) + "Z", fill="#eeddb0"))
    s.add(el("path", d=smooth([(800, WL - 6), (880, WL - 18), (970, WL - 15), (1035, WL - 5)]) + "Z", fill="#5b8e3e", opacity=0.65))
    for x, h, lean in ((865, 66, 9), (898, 82, -7), (938, 72, 11), (982, 58, -9), (1012, 48, 8)):
        s.add(palm(rng, x, WL - 13, h * 0.82, lean, 23, nfr=10))

    # Red Mangrove (Rhizophora mangle) island on the left with dense arching prop roots
    for x in range(-10, 425, 30):
        cx = x + rng.uniform(-5, 5)
        cy = WL - rng.uniform(68, 98)
        roots_back, roots_front = [], []
        for idx, d in enumerate((-38, -26, -15, -4, 7, 18, 29, 38)):
            end_y = WL + rng.uniform(55, 140)
            cmd = f"M{n(cx + d * 0.22)},{n(cy + 18)} Q{n(cx + d * 0.82)},{n(WL - 24)} {n(cx + d)},{n(end_y)}"
            (roots_back if idx % 2 == 0 else roots_front).append(cmd)
        s.add(el("path", d=" ".join(roots_back), stroke="#3d2f20", stroke_width=2.4, fill="none"))
        s.add(el("path", d=" ".join(roots_front), stroke="#5c4732", stroke_width=2.0, fill="none"))
    s.add(g(canopy_band(s, -25, 445, lambda x: WL - 72, 24, 28, 42, ("#1c4424", "#2e6632", "#589644"), flat=0.58, k=7)))
    s.add(egret(250, WL - 108, 0.92), egret(118, WL - 96, 0.82, flip=True))
    s.add(g([bird_v(555, 88, 9), bird_v(588, 78, 7.5), bird_v(620, 94, 8)], class_="drift"))

    # Underwater column & Snell's window surface meniscus
    s.add(el("rect", x=0, y=WL, width=W, height=H - WL,
             fill=s.linear("water", [(0, "#35bfd6"), (0.28, "#1b92b8"), (0.68, "#0e5e8a"), (1, "#063254")])))
    surf = [(x, WL + 3.5 * math.sin(x / 24) + 1.5 * math.cos(x / 11)) for x in range(0, W + 1, 16)]
    s.add(el("path", d=smooth(surf) + f" L{W},{WL - 5} L0,{WL - 5}Z", fill="#a8eaf2", opacity=0.78))
    s.add(el("path", d=smooth([(x, y + 3) for x, y in surf]), stroke="#ffffff", stroke_width=1.4, fill="none", opacity=0.65))
    s.add(water_lines(rng, 0, W, WL + 5, WL + 46, 68, op=0.48))
    s.add(light_rays(s, 360, 1160, WL, H - 50, 14, op=0.19))

    # Caustic light network near surface
    caust = " ".join(f"M{n(x)},{n(WL + 18 + rng.uniform(0, 42))} q12,-7 24,0 t24,0" for x in range(400, W, 42))
    s.add(el("path", d=caust, stroke="#c8f6fa", stroke_width=1.1, fill="none", opacity=0.38, class_="shimmer"))

    # Mangrove root shadow and juvenile fish nursery
    s.add(el("ellipse", cx=205, cy=WL + 95, rx=235, ry=65, fill="#083d4f", opacity=0.32, filter=s.url("mist")))
    s.add(school(rng, 175, WL + 72, 16, 62, 4.2, "#d0dee6", stripe="#f2d43b"))
    s.add(school(rng, 305, WL + 122, 10, 42, 4.8, "#f5c428", stripe="#182430", flip=True))

    # Distant background reef ridge for underwater depth
    bg_reef = [(350, 610), (460, 520), (590, 495), (740, 510), (900, 475), (1080, 485), (1200, 465), (1200, 620)]
    s.add(el("path", d=smooth(bg_reef[:-1]) + " L1200,620 L350,620Z", fill="#0c4c73", opacity=0.55))

    # Sandy lagoon floor & current ripples
    floor = [(0, 600), (150, 610), (330, 590), (520, 560), (700, 575), (880, 545), (1050, 560), (1200, 540)]
    fl = interp(floor)
    s.add(el("path", d=smooth(floor) + f" L{W},{H} L0,{H}Z", fill=s.linear("sand", [(0, "#e8d7aa"), (1, "#b89f6d")])))
    ripples = " ".join(f"M{n(x)},{n(fl(x) + 18 + (x * 7) % 62)} q14,-4 28,0" for x in range(12, W, 32))
    s.add(el("path", d=ripples, stroke="#9e8756", stroke_width=1.1, fill="none", opacity=0.52))
    # Starfish on the sandy lagoon floor
    for sx_, sy_ in ((140, 655), (275, 635)):
        pts_star = []
        for k in range(10):
            ang = TAU * k / 10 - math.pi / 2
            rr = 8.5 if k % 2 == 0 else 3.5
            pts_star.append((sx_ + math.cos(ang) * rr, sy_ + math.sin(ang) * rr * 0.55))
        s.add(el("path", d=P(pts_star), fill="#d95338", stroke="#a63620", stroke_width=0.6))

    s.add(seagrass(rng, 0, 340, 642, 130, 36, "#549640"))
    s.add(seagrass(rng, 35, 310, 662, 85, 28, "#74ae4e"))

    # Primary limestone coral reef wall with 3D rock ledges
    reef = [(395, 720), (428, 598), (480, 558), (560, 538), (640, 550), (700, 528), (780, 518),
            (860, 498), (940, 510), (1020, 488), (1120, 502), (1200, 492), (1200, 720)]
    s.add(el("path", d=smooth(reef[:-1]) + " L1200,720Z", fill=s.linear("reefrock", [(0, "#8c7b68"), (0.5, "#6b5c4d"), (1, "#4a3e34")])))
    rf = interp(reef[1:-1])
    # Rock crevices and coralline algae patches on reef substrate
    for rx_ in range(440, 1180, 55):
        ry_ = rf(rx_) + rng.uniform(25, 85)
        s.add(el("ellipse", cx=rx_, cy=ry_, rx=rng.uniform(18, 36), ry=rng.uniform(5, 10), fill="#524438", opacity=0.55))
        s.add(el("ellipse", cx=rx_ - 4, cy=ry_ - 2, rx=rng.uniform(10, 20), ry=rng.uniform(3, 6), fill="#9c5278", opacity=0.35))

    # Rich Coral Garden
    coral_cols = ["#e26d52", "#e8b24c", "#d95b82", "#cfa240", "#f28452", "#9662c4", "#e5c670"]
    for i, x in enumerate(range(436, 1200, 42)):
        y = rf(x) + 6
        kind = i % 5
        c = coral_cols[(i * 3) % len(coral_cols)]
        if kind == 0:
            s.add(branch_coral(rng, x, y, 28, 3, c, 3.5))
        elif kind == 1:
            s.add(brain_coral(rng, x, y, 25, c))
        elif kind == 2:
            s.add(sea_fan(rng, x, y, 52, "#984cb5" if i % 2 else "#c94886"))
        elif kind == 3:
            s.add(tube_sponge(x, y, 32, "#b552bd" if i % 2 else "#e68235"))
        else:
            s.add(branch_coral(rng, x, y, 35, 3, "#dba242", 4.8, spread=0.88, up=-math.pi / 2))
    for x in range(465, 1190, 60):
        s.add(brain_coral(rng, x + 18, rf(x + 18) + 32, 17, "#c29238"))
        s.add(tube_sponge(x - 6, rf(x) + 42, 20, "#d9534f"))

    # Marine Fauna
    s.add(manta(820, 298, 1.45))
    s.add(turtle(558, 378, 1.35))
    s.add(school(rng, 960, 418, 20, 72, 6.2, "#327cd6", stripe="#16346e"))
    s.add(school(rng, 700, 458, 12, 42, 6.8, "#f5d236", stripe="#141e2b", flip=True))
    for x, y, c, st in ((638, 468, "#26b8a8", "#e8689c"), (1042, 448, "#f58432", "#ffffff"),
                        (898, 468, "#4ec4e6", "#f5d236"), (518, 498, "#ebca34", "#2e72d4")):
        s.add(g(fish(x, y, 12, c, stripe=st, flip=rng.random() < 0.5), class_="swim"))
    s.add(g([el("circle", cx=562 + rng.uniform(-8, 8), cy=358 - i * 18, r=rng.uniform(1.8, 3.8), fill="#ffffff",
                fill_opacity=0.2, stroke="#e8fbff", stroke_width=0.9, opacity=0.75) for i in range(7)], class_="bob"))

    # Queen Jessica Coral Nursery Frames (with tagged fragments & mooring floats)
    nurs = []
    for k in range(3):
        bx = 1008 + k * 56
        by = rf(bx) - 32
        nurs.append(el("path", d=(
            f"M{n(bx)},{n(by + 42)} L{n(bx)},{n(by)} L{n(bx + 42)},{n(by)} L{n(bx + 42)},{n(by + 42)} "
            f"M{n(bx)},{n(by + 14)} L{n(bx + 42)},{n(by + 14)} M{n(bx)},{n(by + 28)} L{n(bx + 42)},{n(by + 28)}"
        ), stroke="#dce6ed", stroke_width=1.7, fill="none", opacity=0.82))
        for j in range(4):
            fx = bx + 6 + j * 10
            nurs.append(el("path", d=f"M{n(fx)},{n(by + 14)} l0,9 M{n(fx - 2.5)},{n(by + 20)} l2.5,-3 l2.5,3",
                           stroke="#f28452", stroke_width=2.2, stroke_linecap="round", fill="none"))
    s.add(g(nurs))
    s.add(el("rect", x=0, y=H - 36, width=W, height=36, fill="#062844", opacity=0.28))
    return s.render(labels["aria"]["reef"])


# ==============================================================================
# SCENE: AMAZONIAN RAINFOREST
# ==============================================================================
def build_rainforest(labels):
    s = Scene("rainforest", 1200, 720, 2006)
    rng = s.rng
    W, H = s.w, s.h
    s.blur("mist", 12)
    s.blur("haze", 4)
    sky(s, [(0, "#9ec8d2"), (0.45, "#d4e6de"), (0.8, "#ebf0e4"), (1, "#f6f2e4")])
    sun(s, 900, 108, 30, glow="#fff5cf")
    s.add(cloud(rng, 320, 82, 190, op=0.78), cloud(rng, 680, 68, 150, op=0.72))

    haze = "#c6dcd2"
    # Four receding atmospheric canopy strata (using step=40 so x reaches 1200 cleanly)
    layers = [(296, 11, 17, 0.76), (346, 15, 23, 0.58), (396, 19, 29, 0.40), (448, 23, 35, 0.22)]
    base_cols = ("#184224", "#2b6634", "#589848")
    for li, (gy, rmin, rmax, hz) in enumerate(layers):
        cols = tuple(mix(c, haze, hz) for c in base_cols)
        ground = lambda x, gy=gy, li=li: gy + 15 * math.sin(x / (88 + li * 22) + li)
        s.add(el("path", d=P([(0, ground(0))] + [(x, ground(x)) for x in range(0, W + 1, 40)] + [(W, H), (0, H)]), fill=cols[0]))
        s.add(g(canopy_band(s, -35, W + 35, ground, int(W / (rmin + rmax) * 1.45), rmin, rmax, cols, k=5, detail=False)))
        s.add(mist(s, rng.uniform(120, 1080), gy + 12, rng.uniform(280, 440), 19, op=0.48 - li * 0.07))

    # Crepuscular sunbeams piercing the canopy
    s.add(light_rays(s, 580, 1020, 115, 650, 7, op=0.24))

    # Giant Emergent Kapok (Ceiba pentandra) trees with tabular buttress roots
    s.add(broadleaf_tree(rng, 248, 562, 365, 95, ("#1c4826", "#357838", "#74b052"), emergent=True, k=8))
    s.add(broadleaf_tree(rng, 982, 582, 335, 86, ("#1f4d29", "#3c803e", "#7cb658"), emergent=True, k=8))

    # Draped woody lianas & epiphytes
    lianas = []
    for x0, x1 in ((176, 208), (220, 238), (298, 338), (928, 958), (1028, 1078)):
        lianas.append(f"M{n(x0)},242 C{n(x0 - 12)},355 {n(x1 + 12)},422 {n(x1)},558")
    s.add(el("path", d=" ".join(lianas), stroke="#355224", stroke_width=2.2, fill="none", opacity=0.88))

    # Near canopy layer framing the river banks
    near_cols = ("#12361d", "#20542b", "#46863e")
    s.add(g(canopy_band(s, -45, 425, lambda x: 520 - x * 0.1, 15, 35, 54, near_cols, k=6, detail=True)))
    s.add(g(canopy_band(s, 795, 1245, lambda x: 470 + (x - 800) * 0.15, 15, 35, 54, near_cols, k=6, detail=True)))

    # Winding Amazonian river with smooth alluvial clay banks, canopy reflections, and sun shimmer
    river = s.linear("river", [(0, "#a8ba90"), (0.35, "#878c5c"), (0.72, "#6c6842"), (1, "#544c30")])
    rpts_l = [(520, 520), (468, 560), (378, 610), (228, 660), (36, 720)]
    rpts_r = [(1200, 720), (998, 690), (818, 630), (688, 570), (600, 520)]
    bank_l = [(x - 12, y - 5) for x, y in rpts_l]
    bank_r = [(x + 12, y - 5) for x, y in rpts_r]
    s.add(el("path", d=smooth(bank_l) + " L1200,720 " + smooth(bank_r)[1:] + "Z", fill="#6b5035"))
    s.add(el("path", d=smooth(rpts_l) + " L1200,720 " + smooth(rpts_r)[1:] + "Z", fill=river))
    # Deep green canopy reflections along both riverbanks
    s.add(el("path", d=smooth(rpts_l) + " L300,720 L545,520Z", fill="#1a381f", opacity=0.35, filter=s.url("haze")))
    s.add(el("path", d="M575,520 L920,720 " + smooth(rpts_r)[1:] + "Z", fill="#1a381f", opacity=0.35, filter=s.url("haze")))
    s.add(el("path", d=smooth([(520, 520), (560, 512), (600, 520)]), stroke="#cbd6b8", stroke_width=2, fill="none", opacity=0.65))
    s.add(water_lines(rng, 280, 960, 550, 706, 58, col="#e8eed8", op=0.45))

    # Giant Victoria amazonica water lilies with flowers
    for x, y, r, flw in ((298, 668, 32, True), (362, 640, 23, True), (246, 692, 27, False),
                         (422, 618, 17, False), (848, 660, 25, False), (912, 692, 33, True), (778, 632, 19, False)):
        s.add(water_lily(rng, x, y, r, flower=flw))

    # Foreground botanical details: Tree ferns, Heliconia, Bromeliads, Açaí/Euterpe palms
    for x, y, L in ((38, 642, 64), (112, 612, 52), (1122, 642, 64), (1058, 602, 48), (182, 592, 42)):
        s.add(fern(rng, x, y, L, "#387830"))
    for x, y, h in ((72, 654, 64), (150, 636, 48), (1148, 662, 68), (1096, 632, 54)):
        s.add(heliconia(x, y, h))
    s.add(bromeliad(rng, 236, 298, 16), bromeliad(rng, 272, 316, 13), bromeliad(rng, 1002, 328, 15))
    for x, y, h, lean in ((138, 602, 145, 13), (1082, 612, 155, -15), (478, 522, 114, 7), (702, 542, 104, -5)):
        s.add(palm(rng, x, y, h, lean, 42, cols=("#24582a", "#407d36"), coconuts=False, trunk_col="#665540", nfr=12))

    # Fauna: Boto river dolphin, Caiman, Scarlet Macaws, Toco Toucan, Blue Morpho butterflies
    s.add(dolphin(608, 610, 1.65))
    s.add(caiman(465, 596, 0.85))
    s.add(macaw(558, 198, 1.15), macaw(642, 178, 0.98, flip=True), macaw(722, 218, 0.85))
    s.add(toucan(1018, 298, 1.15))
    s.add(morpho(538, 448, 1.5), morpho(762, 478, 1.25), morpho(330, 540, 1.3))
    s.add(mist(s, 600, 502, 310, 24, op=0.45))
    return s.render(labels["aria"]["rainforest"])


# ==============================================================================
# SCENE: BRAZILIA HIGHLANDS
# ==============================================================================
def build_highlands(labels):
    s = Scene("highlands", 1200, 700, 2890)
    rng = s.rng
    W, H = s.w, s.h
    s.blur("mist", 14)
    sky(s, [(0, "#4f8cc4"), (0.48, "#9ec6e2"), (0.82, "#dcebf2"), (1, "#eff4f1")])
    sun(s, 260, 98, 24)
    s.add(cloud(rng, 825, 88, 175, op=0.88), cloud(rng, 515, 58, 125, op=0.82))

    # Distant snow-capped cordillera
    r1, _ = mountain(s, "r1", [(0, 330), (120, 246), (240, 288), (360, 186), (470, 238), (600, 146),
                               (720, 208), (860, 126), (980, 198), (1100, 156), (1200, 218)],
                     460, "#9ab2ca", shade="#5c7694", shade_op=0.36, snow=214, rough=10)
    s.add(r1)
    s.add(mist(s, 600, 298, 530, 26, op=0.58))

    # Main Andean / Brazilia Massif
    r2, _ = mountain(s, "r2", [(375, 420), (498, 296), (578, 226), (638, 156), (690, 114), (742, 166),
                               (802, 136), (872, 206), (962, 256), (1062, 326), (1200, 378)],
                     560, "#75685e", shade="#24222e", shade_op=0.45, snow=212, rough=11, tongue=0.28)
    s.add(r2)

    # Sculpted valley glacier nestled inside the cirque saddle between peaks (690,114) and (802,136)
    glac_pts_l = [(708, 162), (716, 212), (728, 265), (746, 314), (766, 352), (782, 366)]
    glac_pts_r = [(834, 358), (812, 330), (788, 286), (768, 236), (754, 192), (742, 166)]
    s.add(el("path", d=smooth(glac_pts_l) + " L" + " L".join(f"{n(x)},{n(y)}" for x, y in glac_pts_r) + "Z",
             fill=s.linear("glacier", [(0, "#f4f9fd"), (0.55, "#d8ebf6"), (1, "#9cc9e2")])))
    # Shadowed ice margin, lateral moraine ridges, and crevasse arcs
    s.add(el("path", d="M742,166 L754,192 L768,236 L788,286 L812,330 L834,358 L814,362 L772,300 L746,225Z",
             fill="#7eaec9", opacity=0.48))
    s.add(el("path", d=smooth(glac_pts_l), stroke="#5a4f47", stroke_width=3.2, fill="none", opacity=0.65))
    crev = [
        "M718,212 Q738,220 756,210",
        "M725,240 Q748,250 768,238",
        "M735,270 Q760,282 782,268",
        "M748,302 Q774,314 798,298",
        "M762,332 Q790,344 816,328",
    ]
    s.add(el("path", d=" ".join(crev), stroke="#3b7ca1", stroke_width=1.4, fill="none", opacity=0.75))
    s.add(el("path", d=" ".join(crev), stroke="#ffffff", stroke_width=0.8, fill="none", opacity=0.85, transform="translate(0 -1.2)"))

    # Turquoise glacial moraine lake with shoreline boulders and reflection
    s.add(el("ellipse", cx=816, cy=373, rx=76, ry=15, fill="#58524a"))
    s.add(el("ellipse", cx=816, cy=372, rx=72, ry=13.5, fill=s.linear("lake", [(0, "#68d2d8"), (0.5, "#36aebf"), (1, "#1d7a94")])))
    s.add(el("ellipse", cx=812, cy=369, rx=56, ry=6, fill="#c8f4f6", opacity=0.48))
    s.add(water_lines(rng, 755, 875, 366, 379, 14, op=0.55))

    # Mid slope: Páramo alpine grassland band
    paramo = [(0, 470), (200, 430), (420, 420), (600, 400), (820, 390), (1000, 410), (1200, 430)]
    pf = interp(paramo)
    s.add(el("path", d=smooth(paramo) + f" L{W},{H} L0,{H}Z", fill=s.linear("paramo", [(0, "#a6a25e"), (0.55, "#87914c"), (1, "#6b7a3e")])))
    s.add(tufts(rng, 0, W, pf, 155, 13, "#c7b868", op=0.92))

    # Giant Puya raimondii bromeliad spikes and Espeletia frailejón rosettes on the páramo
    for x in (518, 592, 902, 962):
        y = pf(x) + 6
        spiky_base = " ".join(f"M{n(x)},{n(y)} q{n(d * 0.55)},-8 {n(d * 1.15)},{n(-10 + abs(d) * 0.22)}" for d in range(-16, 17, 3))
        spike_clusters = [el("ellipse", cx=x + (k % 2 - 0.5) * 2.5, cy=y - 18 - k * 4.5, rx=4.8 - k * 0.18, ry=2.2,
                             fill="#cfc87e" if k % 2 else "#a8a158") for k in range(12)]
        s.add(g([
            el("path", d=spiky_base, stroke="#4d6b42", stroke_width=1.8, fill="none", stroke_linecap="round"),
            el("rect", x=x - 2, y=y - 22, width=4, height=22, fill="#6b5d42"),
            *spike_clusters,
        ]))
    for x in (640, 682, 722, 1040, 1082):
        y = pf(x) + 8
        rosette = [el("ellipse", cx=x + math.cos(a) * 5.5, cy=y - 23 + math.sin(a) * 3.5, rx=5.5, ry=1.6,
                      fill="#c8d2b4" if i % 2 else "#9aa888",
                      transform=f"rotate({n(math.degrees(a))} {n(x + math.cos(a) * 5.5)} {n(y - 23 + math.sin(a) * 3.5)})")
                   for i, a in enumerate([k * TAU / 14 for k in range(14)])]
        s.add(g([
            el("rect", x=x - 2.5, y=y - 22, width=5, height=22, rx=1.5, fill="#5c4a38"),
            el("path", d=f"M{n(x - 3.5)},{n(y - 14)} L{n(x + 3.5)},{n(y - 14)} M{n(x - 3.2)},{n(y - 9)} L{n(x + 3.2)},{n(y - 9)}",
               stroke="#8a7964", stroke_width=1.2),
            *rosette,
            el("circle", cx=x, cy=y - 23, r=2.2, fill="#e6c84a"),
        ]))

    # Cloud forest on the left cliff with multi-tiered cataract waterfall
    cliff = [(0, 330), (60, 320), (150, 340), (230, 345), (302, 380), (362, 565), (0, 565)]
    s.add(el("path", d=smooth(cliff[:-1]) + " L0,565Z", fill="#4d4c44"))
    s.add(el("path", d="M20,380 L285,395 M10,425 L318,440 M35,472 L338,485 M15,518 L348,530", stroke="#36352f", stroke_width=2.2, opacity=0.55))
    cf = interp(cliff[:5])
    s.add(g(canopy_band(s, -25, 312, cf, 24, 17, 27, ("#22452e", "#36663d", "#649658"), k=5)))
    s.add(waterfall(s, 290, 358, 560, 25))

    # Lower cloud-forest bank sweeping smoothly into the foreground alpine meadow (no vertical cut!)
    lower = [(0, 560), (200, 545), (360, 560), (485, 608), (620, 680), (650, H)]
    lf = interp(lower[:5])
    s.add(el("path", d=smooth(lower) + f" L0,{H}Z", fill="#345430"))
    s.add(el("ellipse", cx=300, cy=575, rx=94, ry=17, fill=s.linear("pool", [(0, "#7ad0dc"), (1, "#2f829c")])))
    s.add(water_lines(rng, 215, 385, 565, 586, 18, op=0.62))
    s.add(g(canopy_band(s, -30, 232, lf, 15, 21, 33, ("#1c3e26", "#2e5c38", "#588c52"), k=6, detail=True)))
    s.add(g(canopy_band(s, 358, 515, lf, 8, 19, 29, ("#1c3e26", "#2e5c38", "#588c52"), k=6, detail=True)))
    for x, y in ((58, 522), (148, 502), (418, 562)):
        s.add(fern(rng, x, y, 42, "#468640"))
    s.add(heliconia(105, 545, 44))
    s.add(mist(s, 180, 340, 240, 26, op=0.65))
    s.add(mist(s, 300, 452, 165, 20, op=0.58))

    # Foreground alpine meadow overlapping the lower slope naturally with mossy boulders & ferns
    fg = [(380, H), (455, 632), (550, 592), (660, 582), (820, 598), (1000, 585), (1200, 600)]
    s.add(el("path", d=smooth(fg) + f" L{W},{H} L380,{H}Z", fill="#63753c"))
    s.add(tufts(rng, 420, W, interp(fg), 115, 18, "#bda956", width=1.35))
    for x, y, r in ((465, 648, 26), (522, 668, 18), (620, 642, 30), (702, 662, 19), (1060, 652, 36), (1132, 672, 23)):
        s.add(el("ellipse", cx=x + 2, cy=y + 2, rx=r * 1.08, ry=r * 0.2, fill="#000000", opacity=0.25))
        s.add(el("path", d=f"M{n(x - r)},{n(y)} L{n(x - r * 0.75)},{n(y - r * 0.78)} L{n(x - r * 0.1)},{n(y - r * 0.92)} L{n(x + r * 0.68)},{n(y - r * 0.72)} L{n(x + r)},{n(y)}Z",
                 fill="#858680"))
        s.add(el("path", d=f"M{n(x - r * 0.1)},{n(y - r * 0.92)} L{n(x + r * 0.68)},{n(y - r * 0.72)} L{n(x + r)},{n(y)} L{n(x + r * 0.05)},{n(y)}Z",
                 fill="#52534e"))
        s.add(el("path", d=f"M{n(x - r * 0.75)},{n(y - r * 0.78)} Q{n(x - r * 0.35)},{n(y - r * 0.95)} {n(x + r * 0.2)},{n(y - r * 0.82)}",
                 stroke="#6b8c42", stroke_width=2.5, fill="none", stroke_linecap="round", opacity=0.75))
    s.add(fern(rng, 442, 656, 38, "#468640"))

    # Fauna: Soaring Andean Condors and hovering Emerald Hummingbird
    s.add(condor(640, 228, 1.55), condor(902, 258, 0.95))
    s.add(hummingbird(248, 468, 1.65))
    s.add(g([bird_v(1000, 120, 8), bird_v(1032, 110, 6.5)], class_="drift"))
    return s.render(labels["aria"]["highlands"])


# ==============================================================================
# ATLAS VIGNETTES (480 x 300)
# ==============================================================================
def vignette(key, seed):
    s = Scene(key, 480, 300, seed)
    s.blur("mist", 7)
    s.blur("soft", 2.5)
    return s


def build_mogotes(labels):
    s = vignette("mogotes", 101)
    rng = s.rng
    sky(s, [(0, "#6faad9"), (0.55, "#b8daf0"), (1, "#f4ecdc")])
    sun(s, 385, 58, 15)
    s.add(cloud(rng, 118, 54, 105), cloud(rng, 290, 42, 78, op=0.82))

    # Distant hazy karst hills
    h_far, _ = hill(s, [(0, 195), (90, 165), (210, 185), (340, 158), (480, 180)], 240, "#9ab5a2", rough=5)
    s.add(h_far)

    # Four sculpted limestone mogote haystack towers with realistic craggy rock faces & jungle caps
    mogote_specs = [
        (-25, 142, 116, "#6b8f6e", "#466349", "#b0ada0", "#7d7a6e"),
        (296, 505, 106, "#628765", "#3f5c43", "#bab7a8", "#827f72"),
        (106, 294, 72, "#467336", "#26451e", "#c8c4b4", "#8a8677"),
        (356, 474, 122, "#3a662d", "#1e3b16", "#bebaa8", "#7d796b"),
    ]
    for x0, x1, top, col, shade, rock_lit, rock_sh in mogote_specs:
        mw = x1 - x0
        keys = [
            (x0, 240), (x0 + mw * 0.05, top + 46), (x0 + mw * 0.14, top + 12),
            (x0 + mw * 0.34, top + 2), (x0 + mw * 0.56, top), (x0 + mw * 0.78, top + 8),
            (x1 - mw * 0.07, top + 44), (x1, 240),
        ]
        d = smooth(keys) + "Z"
        s.add(el("path", d=d, fill=rock_lit))
        cid = s.clip(f"m{x0}", d)
        inner = [
            # 3D right-flank shadow across the sheer limestone face
            el("path", d=f"M{n(x0 + mw * 0.48)},{n(top)} L{n(x1)},{n(top)} L{n(x1)},240 L{n(x0 + mw * 0.54)},240Z",
               fill=rock_sh, opacity=0.92),
        ]
        # Vertical karst solution flutes, faceted limestone ribs, and horizontal bedding joints across the cliff
        for b in range(1, 9):
            fx = x0 + mw * (0.08 + 0.84 * b / 9) + rng.uniform(-2, 2)
            fw = mw * rng.uniform(0.04, 0.08)
            f_col = mix(rock_lit if b < 5 else rock_sh, "#252922", 0.28)
            inner.append(el("path", d=f"M{n(fx)},{n(top + 14)} L{n(fx + fw)},{n(top + 18)} L{n(fx + fw * 0.7)},236 L{n(fx - fw * 0.2)},236Z",
                            fill=f_col, opacity=0.55))
            inner.append(el("path", d=f"M{n(fx)},{n(top + 12)} Q{n(fx - 2)},{n((top + 236) * 0.5)} {n(fx + 1)},235",
                            stroke="#2b3026", stroke_width=1.0, opacity=0.55, fill="none"))
        for hy in (top + (235 - top) * 0.38, top + (235 - top) * 0.66):
            inner.append(el("path", d=f"M{n(x0)},{n(hy)} Q{n((x0 + x1) * 0.5)},{n(hy + 6)} {n(x1)},{n(hy - 2)}",
                            stroke="#3b4035", stroke_width=1.1, opacity=0.45, fill="none"))
        # Dark karst cavern mouths at cliff base
        inner.append(el("path", d=f"M{n(x0 + mw * 0.30)},238 Q{n(x0 + mw * 0.39)},212 {n(x0 + mw * 0.48)},238Z",
                        fill="#162012", opacity=0.86))
        # Vegetated cliff-face ledges clinging to karst crevices
        for lx, ly, lr in ((x0 + mw * 0.26, top + (235 - top) * 0.52, 7.5),
                           (x0 + mw * 0.64, top + (235 - top) * 0.46, 8.0),
                           (x0 + mw * 0.44, top + (235 - top) * 0.70, 7.0)):
            inner.append(crown(rng, lx, ly, lr, (mix(col, "#0d240c", 0.38), col, mix(col, "#a8cc62", 0.22)), k=5, detail=False))
        # Talus piedmont jungle skirt at base
        for i in range(14):
            vx = x0 + mw * (0.04 + 0.92 * i / 13)
            inner.append(crown(rng, vx, rng.uniform(215, 232), rng.uniform(9, 14),
                               (mix(col, "#0d240c", 0.38), col, mix(col, "#a8cc62", 0.22)), k=5, detail=False))
        # Dense overhanging summit dome jungle cap
        inner.append(el("path", d=f"M{n(x0)},{n(top + 38)} Q{n((x0 + x1) * 0.5)},{n(top + 18)} {n(x1)},{n(top + 38)} L{n(x1)},{n(top)} L{n(x0)},{n(top)}Z",
                        fill=shade))
        for i in range(20):
            vx = x0 + mw * (0.05 + 0.90 * i / 19) + rng.uniform(-3, 3)
            vy = top + rng.uniform(4, 22) + abs(vx - (x0 + x1) / 2) * 0.14
            inner.append(crown(rng, vx, vy, rng.uniform(8.5, 13.5),
                               (mix(col, "#0d240c", 0.35), col, mix(col, "#c4e078", 0.28)), k=5, detail=False))
        s.add(g(inner, clip_path=cid))
        s.add(mist(s, (x0 + x1) / 2, 234, mw * 0.62, 11, op=0.58))

    # Rich terra-rossa red soil valley floor & lush furrowed tobacco plantation rows in perspective
    s.add(el("rect", x=0, y=232, width=480, height=68, fill=s.linear("soil", [(0, "#8f4e2c"), (1, "#5c2e16")])))
    furrows_sh, ridges_soil, plants_dark, plants_lit = [], [], [], []
    for i in range(-1, 16):
        bx = -35 + i * 35
        tx = 135 + i * 15
        furrows_sh.append(f"M{n(bx - 4)},300 L{n(tx - 1.5)},235")
        ridges_soil.append(f"M{n(bx)},300 L{n(tx)},235")
        # Continuous leafy tobacco hedges along each raised ridge
        for st in range(11):
            t = st / 10
            px = bx + (tx - bx) * t + rng.uniform(-1.2, 1.2)
            py = 299 + (236 - 299) * t
            sc = 1.05 - 0.58 * t
            rw, rh = 6.2 * sc, 3.4 * sc
            plants_dark.append(f"M{n(px - rw)},{n(py)} Q{n(px)},{n(py - rh * 1.6)} {n(px + rw)},{n(py)} Q{n(px)},{n(py + rh * 0.6)} {n(px - rw)},{n(py)}Z")
            plants_lit.append(f"M{n(px - rw * 0.7)},{n(py - 0.5)} Q{n(px - rw * 0.2)},{n(py - rh * 1.4)} {n(px + rw * 0.5)},{n(py - 0.5)}Z")
    s.add(el("path", d=" ".join(furrows_sh), stroke="#3b1b0a", stroke_width=4.5, opacity=0.7, fill="none"))
    s.add(el("path", d=" ".join(ridges_soil), stroke="#a6603a", stroke_width=3.0, opacity=0.65, fill="none"))
    s.add(el("path", d=" ".join(plants_dark), fill="#3d6e24"))
    s.add(el("path", d=" ".join(plants_lit), fill="#6ca338"))

    # Traditional thatched tobacco curing barn (bohío) with timber framing, overhang eaves, and palm thatch
    s.add(el("polygon", points="288,268 372,268 382,273 296,273", fill="#000000", opacity=0.28))
    s.add(el("rect", x=298, y=247, width=36, height=21, fill="#8a623a"))
    s.add(el("rect", x=334, y=247, width=26, height=21, fill="#593d22"))
    # Vertical timber wall planks & open curing doorway
    s.add(el("path", d="M306,247 L306,268 M314,247 L314,268 M326,247 L326,268 M342,247 L342,268 M350,247 L350,268",
             stroke="#422c16", stroke_width=0.8, opacity=0.55))
    s.add(el("rect", x=314, y=253, width=10, height=15, fill="#26170a"))
    # Steeply pitched guano palm-thatch hipped roof with layered thatch courses
    s.add(el("polygon", points="290,250 328,216 368,250", fill="#b58b52"))
    s.add(el("polygon", points="328,216 368,250 336,250", fill="#7d5d34"))
    s.add(el("path", d="M295,245 L363,245 M301,239 L357,239 M308,233 L350,233 M315,227 L343,227",
             stroke="#5e4424", stroke_width=1.1, opacity=0.65))
    s.add(el("path", d="M322,216 L334,216", stroke="#4a3419", stroke_width=2.0, stroke_linecap="round"))

    # Cuban Royal Palms (Roystonea regia)
    for x, y, h, lean in ((58, 266, 116, 4), (422, 268, 126, -5), (248, 256, 94, 3), (185, 246, 68, -2)):
        s.add(palm(rng, x, y, h, lean, 25 * (h / 110), royal=True, nfr=11, trunk_col="#d6cfc0"))
    s.add(g([bird_v(210, 72, 6.5), bird_v(228, 65, 5.5)], class_="drift"))
    return s.render(labels["aria"]["mogotes"])


def build_enriquillo(labels):
    s = vignette("enriquillo", 102)
    rng = s.rng
    sky(s, [(0, "#68a6d8"), (0.55, "#b8daf0"), (1, "#f7ead0")])
    sun(s, 88, 58, 16)
    s.add(cloud(rng, 250, 48, 95, op=0.85), cloud(rng, 400, 62, 75, op=0.75))

    # Arid Sierra de Bahoruco / Neiba mountain ranges
    m_far, _ = mountain(s, "mf", [(0, 175), (140, 128), (260, 152), (390, 108), (480, 138)], 205,
                        "#ccb494", shade="#8c7358", shade_op=0.3, rough=6)
    s.add(m_far)
    m, _ = mountain(s, "m", [(0, 168), (92, 116), (182, 148), (292, 86), (382, 128), (480, 106)], 206,
                    "#b5956e", shade="#664e3a", shade_op=0.38, rough=8)
    s.add(m)

    # Hypersaline Lago Enriquillo water body with mineral salt-crust shoreline
    s.add(el("rect", x=0, y=198, width=480, height=64,
             fill=s.linear("lake", [(0, "#64ced0"), (0.45, "#38aab8"), (1, "#1e748c")])))
    salt_far = [(0, 198), (80, 201), (190, 199), (310, 202), (420, 199), (480, 201)]
    s.add(el("path", d=smooth(salt_far) + " L480,196 L0,196Z", fill="#f7f5ed", opacity=0.92))
    s.add(water_lines(rng, 0, 480, 204, 256, 38, op=0.48))

    # Sun-baked arid shoreline & fossil coral limestone outcrops
    shore = [(0, 262), (120, 253), (260, 261), (390, 252), (480, 249)]
    s.add(el("path", d=smooth([(x, y - 3) for x, y in shore]) + " L480,265 L0,265Z", fill="#f2efe4"))
    s.add(el("path", d=smooth(shore) + " L480,300 L0,300Z", fill=s.linear("sand", [(0, "#decb9e"), (1, "#bfa674")])))
    # Bleached salt-encrusted dead tree snags emerging from hypersaline lake
    s.add(el("path", d="M38,242 Q58,239 76,243 L84,237 M62,241 L68,234 M425,218 L425,196 L418,188 M425,204 L433,195",
             stroke="#e0d8c6", stroke_width=2.2, fill="none", stroke_linecap="round"))

    # Dry scrub & columnar cacti
    s.add(thorn_bush(rng, 85, 272, 16), thorn_bush(rng, 305, 270, 15))
    for x, y, h in ((36, 276, 52), (418, 272, 54), (452, 278, 44)):
        s.add(cactus(x, y, h, "#588252", rib="#355432"))

    # Flock of Caribbean Flamingos in varied wading and filter-feeding poses with water reflections
    flamingo_specs = [
        (146, 222, 0.94, False, "stand"),
        (178, 228, 0.90, False, "feed"),
        (210, 220, 0.96, True, "stand"),
        (238, 227, 0.88, False, "stand"),
        (268, 223, 0.92, True, "feed"),
        (300, 226, 0.90, False, "stand"),
    ]
    for fx, fy, fs, flp, pose in flamingo_specs:
        s.add(el("ellipse", cx=fx, cy=fy + 28 * fs, rx=7.5 * fs, ry=2.4 * fs, fill="#f58a82", opacity=0.35))
        s.add(flamingo(fx, fy, fs, flip=flp, pose=pose))

    # Stratified limestone basking slab & Rhinoceros Iguana + American Crocodile
    s.add(el("path", d="M328,284 L338,274 L364,270 L392,275 L402,284Z", fill="#a6957a"))
    s.add(el("path", d="M364,270 L392,275 L402,284 L368,284Z", fill="#786952"))
    s.add(iguana(364, 271, 1.18))
    s.add(caiman(108, 236, 0.92))
    return s.render(labels["aria"]["enriquillo"])


def build_pantanal(labels):
    s = vignette("pantanal", 103)
    rng = s.rng
    sky(s, [(0, "#d97b48"), (0.38, "#eea862"), (0.72, "#f7d294"), (1, "#faeed2")])
    sun(s, 330, 142, 22, glow="#ffcf7c")
    s.add(cloud(rng, 110, 52, 105, col="#ffe6be", shade="#d99b6c", op=0.78))
    s.add(cloud(rng, 390, 44, 85, col="#ffe6be", shade="#d99b6c", op=0.72))

    # Distant mountain/gallery horizon
    s.add(el("path", d=smooth([(0, 168), (120, 162), (260, 166), (480, 160)]) + " L480,174 L0,174Z", fill="#9c7a5c", opacity=0.55))

    # Flooded Pantanal wetland mirror water with golden sun-path reflection
    s.add(el("rect", x=0, y=168, width=480, height=132,
             fill=s.linear("water", [(0, "#e3b276"), (0.42, "#b0966e"), (0.78, "#6a8888"), (1, "#446870")])))
    s.add(el("ellipse", cx=330, cy=215, rx=56, ry=44, fill="#ffeab8", opacity=0.35, filter=s.url("mist")))
    s.add(water_lines(rng, 0, 480, 174, 296, 48, col="#fff3d6", op=0.52))

    # Flooded savanna cordilheira islands & marsh reeds
    for x0, x1, y in ((-10, 184, 172), (256, 490, 168), (104, 388, 214)):
        cx_, rx_ = (x0 + x1) / 2, (x1 - x0) / 2
        s.add(el("ellipse", cx=cx_, cy=y + 2.5, rx=rx_, ry=9, fill="#2e401b", opacity=0.48))
        s.add(el("ellipse", cx=cx_, cy=y, rx=rx_, ry=8, fill="#5f7d34"))
        s.add(tufts(rng, max(4, x0 + 10), min(476, x1 - 10), lambda x, y=y: y - 2, 38, 11, "#869e44"))

    # Gallery forest and Carandá palms (Copernicia alba)
    s.add(g(canopy_band(s, 276, 476, lambda x: 158, 10, 13, 22, ("#2f4a20", "#4b6b2f", "#789648"), k=5)))
    for x, h, lean in ((56, 74, -4), (98, 90, 5), (208, 64, -3)):
        s.add(palm(rng, x, 173, h, lean, 21, cols=("#3d5c28", "#628438"), coconuts=False, trunk_col="#544434", nfr=10))

    # Giant Victoria amazonica water lilies & blooming purple Eichhornia water hyacinths in foreground marsh
    for x in range(24, 468, 38):
        s.add(water_lily(rng, x, 270 + (x % 15), 11 + (x % 5), flower=(x % 76 == 24)))
    for hx_ in (215, 295, 348):
        hy_ = 220
        s.add(g([
            el("ellipse", cx=hx_, cy=hy_, rx=8, ry=3, fill="#4e7d2e"),
            el("ellipse", cx=hx_, cy=hy_ - 5, rx=2.5, ry=4.5, fill="#9b6bd4"),
            el("circle", cx=hx_, cy=hy_ - 6, r=1.2, fill="#d8b8ff"),
        ]))

    # Fauna: Jabiru storks, Capybara family, Yacare Caiman, and flying wetland birds
    s.add(jabiru(328, 200, 1.22), jabiru(374, 205, 1.02, flip=True))
    s.add(capybara(154, 212, 1.24), capybara(116, 214, 0.94, flip=True), capybara(184, 214, 0.68))
    s.add(caiman(242, 250, 1.32))
    s.add(g([bird_v(178, 78, 7.5), bird_v(198, 72, 6.5), bird_v(215, 84, 6.5), bird_v(232, 76, 5.5)], class_="drift"))
    return s.render(labels["aria"]["pantanal"])


def build_cerrado(labels):
    s = vignette("cerrado", 104)
    rng = s.rng
    sky(s, [(0, "#5e9ed4"), (0.55, "#b0d4ec"), (1, "#f5ead0")])
    sun(s, 72, 58, 15)
    s.add(cloud(rng, 358, 58, 118), cloud(rng, 118, 76, 78))

    # Distant Chapada mesa and rolling Cerrado hills
    s.add(el("path", d="M260,175 L285,138 L395,136 L425,175Z", fill="#a8946e", opacity=0.7))
    h1, r_h1 = hill(s, [(0, 190), (140, 158), (300, 174), (480, 148)], 240, "#b8a264")
    s.add(h1)
    # Gallery forest along the valley depression
    s.add(g(canopy_band(s, 220, 360, interp(r_h1), 9, 8, 13, ("#2f4f24", "#486e34", "#6e9248"), lift=-4, k=5)))

    # Golden savanna grassland foreground
    ground = interp([(0, 228), (240, 218), (480, 226)])
    s.add(el("path", d=smooth([(0, 228), (240, 218), (480, 226)]) + " L480,300 L0,300Z",
             fill=s.linear("sav", [(0, "#cca856"), (1, "#a68238")])))
    s.add(tufts(rng, 0, 480, ground, 135, 12, "#dec26a"))
    s.add(tufts(rng, 0, 480, lambda x: 268 + (x % 19), 90, 16, "#8f722e"))

    # Tortuous Cerrado trees, blooming yellow and pink Ipê trees, and cathedral termite mounds
    for x in (58, 178, 396):
        s.add(gnarled_tree(rng, x, ground(x), 62))
    s.add(ipe(rng, 290, ground(290), 82), ipe(rng, 442, ground(442) + 10, 66, bloom="#e86ca6", bloom2="#c44b84"))
    s.add(termite_mound(118, 264, 36), termite_mound(352, 252, 26))

    # Fauna: Maned Wolf (Chrysocyon brachyurus) and Hyacinth Macaw (Anodorhynchus hyacinthinus)
    s.add(maned_wolf(228, 268, 1.25))
    s.add(macaw(152, 108, 0.78, palette=("#2452b5", "#193b8a", "#f5c428")))
    return s.render(labels["aria"]["cerrado"])


def build_lencois(labels):
    """Realistic sweeping barchan quartz sand dunes with S-curved slip-faces and recessed inter-dunal rainwater lagoons."""
    s = vignette("lencois", 105)
    rng = s.rng
    sky(s, [(0, "#3d88cc"), (0.55, "#8cc4e8"), (1, "#def0f8")], h=145)
    sun(s, 82, 52, 16)
    s.add(cloud(rng, 310, 56, 130), cloud(rng, 135, 68, 85, op=0.82))

    # Base quartz sand desert floor
    s.add(el("rect", x=0, y=132, width=480, height=168, fill="#f5f0e2"))
    lag_turq = s.linear("lag1", [(0, "#4ce0d8"), (0.45, "#1fb5c2"), (1, "#0f7894")])
    lag_em = s.linear("lag2", [(0, "#44d8b4"), (0.45, "#1aa898"), (1, "#0c6e72")])

    # Helper to draw a realistic 3D barchan dune sheet extending down to y_bot (eliminates horizontal seam lines!)
    def barchan_dune(x0, x_crest, x1, y_base, h_crest, y_bot=300, lit="#fcfaf2", shade="#d8d0be"):
        ym = y_base - h_crest
        x_toe = x_crest + (x1 - x_crest) * 0.32
        # Windward sunlit slope (left to S-curved crest ridge, extending smoothly to y_bot)
        lit_d = (
            f"M{n(x0)},{n(y_base)} C{n(x0 + (x_crest - x0) * 0.45)},{n(y_base - h_crest * 0.18)} "
            f"{n(x_crest - (x_crest - x0) * 0.24)},{n(ym)} {n(x_crest)},{n(ym)} "
            f"C{n(x_crest + (x1 - x_crest) * 0.16)},{n(ym + h_crest * 0.38)} "
            f"{n(x_crest + (x1 - x_crest) * 0.10)},{n(y_base - h_crest * 0.08)} "
            f"{n(x_toe)},{n(y_bot)} L{n(x0)},{n(y_bot)}Z"
        )
        # Leeward shadowed slip-face (steeply curving all the way into the inter-dunal trough with no vertical step)
        sh_d = (
            f"M{n(x_crest)},{n(ym)} C{n(x_crest + (x1 - x_crest) * 0.42)},{n(ym + h_crest * 0.08)} "
            f"{n(x1 - (x1 - x_crest) * 0.18)},{n(y_base - h_crest * 0.06)} {n(x1)},{n(y_bot)} "
            f"L{n(x_toe)},{n(y_bot)} "
            f"C{n(x_crest + (x1 - x_crest) * 0.10)},{n(y_base - h_crest * 0.08)} "
            f"{n(x_crest + (x1 - x_crest) * 0.16)},{n(ym + h_crest * 0.38)} {n(x_crest)},{n(ym)}Z"
        )
        # Sharp wind-blown sand ridge highlight along the S-crest
        ridge_hi = (
            f"M{n(x_crest)},{n(ym)} C{n(x_crest + (x1 - x_crest) * 0.16)},{n(ym + h_crest * 0.38)} "
            f"{n(x_crest + (x1 - x_crest) * 0.10)},{n(y_base - h_crest * 0.08)} {n(x_toe)},{n(y_bot)}"
        )
        return g([
            el("path", d=lit_d, fill=lit),
            el("path", d=sh_d, fill=shade),
            el("path", d=ridge_hi, stroke="#ffffff", stroke_width=1.1, fill="none", opacity=0.85),
        ])

    # Helper to draw an organic inter-dunal rainwater lagoon with wet golden-sand beach margin & shallow sandbar
    def dune_lagoon(pts, fill_url, bar_cx=None, bar_cy=None, bar_rx=35):
        wet_margin = [(x, y - 1.8) for x, y in pts]
        out = [
            el("path", d=smooth(wet_margin, closed=True), fill="#d4c79e"),
            el("path", d=smooth(pts, closed=True), fill=fill_url),
        ]
        if bar_cx is not None:
            out.append(el("ellipse", cx=bar_cx, cy=bar_cy, rx=bar_rx, ry=4.2, fill="#80ede2", opacity=0.38))
        return g(out)

    # Layer 1: Far horizon dunes & recessed inter-dunal lagoons (drawn BEFORE Layer 2 dunes so Layer 2 overlaps them!)
    s.add(barchan_dune(-30, 55, 175, 160, 26, y_bot=220, lit="#f7f4ea", shade="#dfd7c4"))
    s.add(barchan_dune(110, 215, 335, 162, 30, y_bot=220, lit="#f7f4ea", shade="#dfd7c4"))
    s.add(barchan_dune(265, 380, 510, 160, 28, y_bot=220, lit="#f7f4ea", shade="#dfd7c4"))
    s.add(dune_lagoon([(30, 160), (98, 154), (168, 160), (145, 176), (50, 175)], lag_turq, 98, 163, 28))
    s.add(dune_lagoon([(235, 161), (310, 155), (382, 162), (355, 178), (255, 176)], lag_em, 310, 164, 30))

    # Layer 2: Mid-ground sweeping dunes overlapping the far lagoons, followed by mid-ground crescent lagoons
    s.add(barchan_dune(-40, 82, 235, 206, 44, y_bot=275, lit="#faf7ef", shade="#dbd2be"))
    s.add(barchan_dune(165, 312, 465, 210, 48, y_bot=275, lit="#faf7ef", shade="#dbd2be"))
    s.add(barchan_dune(360, 458, 540, 206, 36, y_bot=275, lit="#faf7ef", shade="#dbd2be"))
    s.add(dune_lagoon([(52, 204), (148, 194), (252, 202), (275, 224), (175, 232), (72, 222)], lag_em, 165, 210, 48))
    s.add(water_lines(rng, 85, 240, 200, 220, 12, op=0.52))
    s.add(dune_lagoon([(288, 206), (376, 198), (462, 206), (445, 228), (335, 230)], lag_turq, 378, 212, 42))
    s.add(water_lines(rng, 315, 435, 204, 222, 10, op=0.52))

    # Layer 3: Near prominent dunes overlapping the lower shores of the mid-ground lagoons
    s.add(barchan_dune(-50, 118, 315, 268, 60, y_bot=300, lit="#fdfbf5", shade="#d4cbb6"))
    s.add(barchan_dune(215, 385, 530, 270, 56, y_bot=300, lit="#fdfbf5", shade="#d4cbb6"))
    # Wind-sculpted sand ripples on foreground windward slopes
    ripples = " ".join(f"M{n(18 + i * 14)},{n(252 - i * 2.4)} q20,-3.5 40,0.8" for i in range(6))
    ripples += " " + " ".join(f"M{n(258 + i * 15)},{n(256 - i * 2.1)} q20,-3.5 40,0.8" for i in range(6))
    s.add(el("path", d=ripples, stroke="#dfd6c0", stroke_width=1.15, fill="none", opacity=0.8))

    # Layer 4: Foreground crystal rainwater lagoon & white quartz sand spit
    fg_lag = [(28, 272), (135, 258), (265, 256), (398, 263), (458, 276), (420, 295), (250, 298), (85, 295)]
    s.add(dune_lagoon(fg_lag, lag_turq, 245, 276, 110))
    s.add(water_lines(rng, 70, 420, 264, 292, 24, op=0.68))
    s.add(g([bird_v(210, 88, 6.5), bird_v(232, 80, 5.5), bird_v(250, 90, 5.5)], class_="drift"))
    return s.render(labels["aria"]["lencois"])


def build_caatinga(labels):
    s = vignette("caatinga", 106)
    rng = s.rng
    sky(s, [(0, "#8eb8d9"), (0.55, "#d8d4be"), (1, "#f6dfc0")])
    sun(s, 400, 68, 19, glow="#ffdfa2")

    # Distant Sertão inselbergs and dry hills
    s.add(el("path", d="M40,175 L65,136 L115,132 L145,175Z", fill="#bfa082", opacity=0.65))
    h1, _ = hill(s, [(0, 170), (120, 148), (260, 174), (360, 138), (480, 164)], 232, "#c4986e")
    s.add(h1)

    # Baked ochre-terracotta soil with granite lajedo outcrops and dry riverbed cracks
    ground = interp([(0, 232), (240, 220), (480, 228)])
    s.add(el("path", d=smooth([(0, 232), (240, 220), (480, 228)]) + " L480,300 L0,300Z",
             fill=s.linear("caat", [(0, "#c28e5c"), (1, "#8f5e36")])))
    cracks = "M140,265 l18,4 l12,-3 l15,5 M158,269 l6,9 M210,280 l22,3 l14,-4 M330,272 l19,5 l15,-2"
    s.add(el("path", d=cracks, stroke="#5e3b1e", stroke_width=0.9, fill="none", opacity=0.55))

    # Gnarled silvery-grey Caatinga trees (Umbuzeiro / Catingueira)
    for tx, ty, th in ((195, 232, 54), (368, 228, 48)):
        s.add(gnarled_tree(rng, tx, ty, th, leaf=("#828260", "#9ea078", "#bcc096"), trunk_col="#6e6254"))

    # Dry thorn bushes & Macambira bromeliad rosettes
    for _ in range(14):
        x = rng.uniform(10, 470)
        s.add(thorn_bush(rng, x, ground(x) + rng.uniform(2, 42), rng.uniform(14, 25)))

    # Prickly-pear (Opuntia palmadora) & Turk's-cap cactus (Melocactus zehntneri) on rocky soil
    for ox, oy in ((142, 258), (338, 262)):
        s.add(g([
            el("ellipse", cx=ox, cy=oy + 1, rx=9, ry=2, fill="#000000", opacity=0.2),
            el("ellipse", cx=ox, cy=oy - 5, rx=5.5, ry=7, fill="#4e7a48"),
            el("ellipse", cx=ox - 6, cy=oy - 12, rx=4.5, ry=6, fill="#5c8c54", transform=f"rotate(-24 {ox - 6} {oy - 12})"),
            el("ellipse", cx=ox + 6, cy=oy - 11, rx=4.5, ry=5.5, fill="#5c8c54", transform=f"rotate(22 {ox + 6} {oy - 11})"),
            el("circle", cx=ox - 8, cy=oy - 17, r=2.0, fill="#e85d24"),
        ]))
    # Melocactus (coroa-de-frade) with crimson cephalium cap
    s.add(g([
        el("ellipse", cx=222, cy=278, rx=8, ry=6.5, fill="#4d7a49"),
        el("path", d="M218,272 L217,283 M222,271 L222,284 M226,272 L227,283", stroke="#2f5230", stroke_width=0.8, fill="none"),
        el("ellipse", cx=222, cy=271.5, rx=4.2, ry=2.6, fill="#c92e2e"),
        el("circle", cx=222, cy=269.5, r=1.1, fill="#f78ca2"),
    ]))

    # Iconic Mandacaru columnar cacti (with distinct arms and white night blooms)
    for x, h in ((88, 112), (298, 132), (422, 84)):
        s.add(cactus(x, ground(x) + 32, h, "#527d56", rib="#305236"))

    # Weathered exfoliating granite boulders & pebbles
    for rx_, ry_, rr in ((42, 282, 16), (252, 276, 15), (362, 286, 18)):
        s.add(el("path", d=f"M{rx_ - rr},{ry_} Q{rx_ - rr * 0.6},{ry_ - rr * 0.8} {rx_ + rr * 0.2},{ry_ - rr * 0.7} Q{rx_ + rr},{ry_ - rr * 0.4} {rx_ + rr},{ry_}Z",
                 fill="#8c7258"))
        s.add(el("path", d=f"M{rx_},{ry_ - rr * 0.72} Q{rx_ + rr},{ry_ - rr * 0.4} {rx_ + rr},{ry_} L{rx_},{ry_}Z",
                 fill="#5c4734", opacity=0.55))
    s.add(g([el("ellipse", cx=rng.uniform(0, 480), cy=rng.uniform(248, 296), rx=rng.uniform(3.5, 8.5), ry=2.0, fill="#785434")
             for _ in range(26)]))

    # Fauna: Pair of Indigo / Lear's Macaws (Anodorhynchus leari) in flight
    s.add(macaw(198, 98, 0.82, palette=("#2255a8", "#173c7d", "#f5c428")))
    s.add(macaw(145, 114, 0.62, flip=True, palette=("#2255a8", "#173c7d", "#f5c428")))
    return s.render(labels["aria"]["caatinga"])


def build_bluehole(labels):
    s = vignette("bluehole", 107)
    rng = s.rng
    sky(s, [(0, "#4e9ad2"), (0.6, "#98cde8"), (1, "#e6f4f8")], h=96)
    sun(s, 400, 44, 14)
    s.add(cloud(rng, 138, 40, 95), cloud(rng, 308, 48, 76))

    # Distant coral keys, coastal vegetation berm, and coconut palms on horizon
    s.add(el("path", d="M-10,92 Q70,85 160,90 Q280,83 410,90 L490,92 L490,96 L-10,96Z", fill="#e6dab4"))
    s.add(el("path", d="M10,91 Q70,84 140,90 Z M330,90 Q395,83 465,91 Z", fill="#4a7d3a", opacity=0.75))
    for x, h, lean in ((34, 25, -4), (52, 29, 5), (68, 24, -2), (104, 26, 6),
                       (354, 26, -5), (382, 31, 4), (402, 25, -3), (440, 27, 5)):
        s.add(palm(rng, x, 92, h, lean, 11, cols=("#285c30", "#488440"), nfr=9, coconuts=False, trunk_col="#826b4e"))

    # Turquoise shallow coral lagoon surrounding the sinkhole
    s.add(el("rect", x=0, y=94, width=480, height=206,
             fill=s.linear("water", [(0, "#45d0d8"), (0.38, "#20a8ba"), (1, "#10748c")])))
    s.add(water_lines(rng, 0, 480, 96, 122, 28, op=0.48))
    s.add(el("path", d="M0,118 Q64,116 104,140 Q114,182 82,242 Q42,282 0,300Z", fill="#82d4ce", opacity=0.78))
    s.add(el("path", d="M480,118 Q416,116 376,140 Q366,182 398,242 Q438,282 480,300Z", fill="#82d4ce", opacity=0.78))

    # The Great Blue Hole circular karst sinkhole with stepped limestone ledges & stalactites
    cx, cy = 240, 196
    chasm_grad = s.radial("chasm", [
        (0, "#010610", 1),
        (0.42, "#051530", 1),
        (0.68, "#0b2e5e", 1),
        (0.86, "#145c8c", 0.96),
        (0.95, "#249cb5", 0.85),
        (1, "#38c6d4", 0.15),
    ])
    s.add(el("ellipse", cx=cx, cy=cy, rx=158, ry=90, fill=chasm_grad))
    # Stepped submerged karst cliff terraces & drowned cave stalactites inside rim
    s.add(el("ellipse", cx=cx, cy=cy + 2, rx=138, ry=76, fill="#041126", opacity=0.88))
    stal = " ".join(f"M{n(cx - 120 + i * 16)},{n(cy - 62 + abs(i - 7.5) * 4)} l2,{n(rng.uniform(8, 18))} l2,{n(-rng.uniform(8, 18))}"
                    for i in range(16))
    s.add(el("path", d=stal, fill="#0c2b4f", opacity=0.65))
    s.add(el("ellipse", cx=cx, cy=cy + 4, rx=98, ry=52, fill="#010714", opacity=0.96))

    # Shallow carbonate sand & irregular coral rim ring around the sinkhole
    s.add(el("path", d=(
        f"M{cx - 152},{cy} C{cx - 142},{cy - 82} {cx + 142},{cy - 82} {cx + 152},{cy} "
        f"C{cx + 142},{cy + 82} {cx - 142},{cy + 82} {cx - 152},{cy}Z"
    ), stroke="#a8e6df", stroke_width=5.5, fill="none", opacity=0.68))
    s.add(el("path", d=(
        f"M{cx - 156},{cy} C{cx - 146},{cy - 85} {cx + 146},{cy - 85} {cx + 156},{cy}"
    ), stroke="#e4faf7", stroke_width=2.0, fill="none", opacity=0.55))

    # Diagonal sunbeams piercing into the abyss
    s.add(light_rays(s, 135, 345, 108, 286, 8, op=0.20))

    # Naturalistic asymmetrical coral gardens along the sinkhole rim
    for x, y, Lc, c in ((84, 152, 18, "#e26d52"), (108, 178, 15, "#cfa240"), (368, 154, 19, "#d95b82"),
                        (394, 182, 14, "#e8b24c"), (128, 240, 17, "#f08452"), (342, 246, 16, "#e26d52"),
                        (165, 266, 13, "#d95b82"), (312, 264, 14, "#e8b24c")):
        s.add(branch_coral(rng, x, y, Lc, 2, c, 2.2))
    for bx, by, br, bc in ((102, 206, 14, "#c29238"), (148, 254, 11, "#cfa240"),
                           (376, 212, 15, "#cfa240"), (328, 256, 12, "#b8862d")):
        s.add(brain_coral(rng, bx, by, br, bc))
    s.add(sea_fan(rng, 74, 192, 26, "#8c48a8"), sea_fan(rng, 404, 172, 24, "#c94886"), sea_fan(rng, 362, 238, 20, "#8c48a8"))
    s.add(tube_sponge(122, 224, 16, "#b552bd"), tube_sponge(356, 226, 18, "#e68235"), tube_sponge(94, 168, 13, "#e68235"))

    # Marine Fauna: Reef Sharks, Manta Ray, Sea Turtle, Schooling Fish
    s.add(shark(232, 194, 0.98))
    s.add(shark(282, 232, 0.68, flip=True))
    s.add(manta(195, 156, 0.52))
    s.add(turtle(142, 144, 0.68))
    s.add(school(rng, 332, 144, 11, 34, 3.8, "#dff6f5", stripe="#1e948b"))

    # Electric Eco-Research Catamaran on the surface with reflection
    s.add(g([
        el("ellipse", cx=212, cy=115, rx=22, ry=2.5, fill="#0c4c66", opacity=0.35),
        el("path", d="M192,107 L232,107 L227,113.5 L195,113.5Z", fill="#ffffff"),
        el("path", d="M194,110.5 L229,110.5", stroke="#1a528f", stroke_width=1.2),
        el("path", d="M200,107 L203,102 L221,102 L224,107Z", fill="#1a528f"),
        el("rect", x=204, y=103, width=15, height=2.5, rx=0.8, fill="#8cd2f0"),
        el("line", x1=212, y1=102, x2=212, y2=96, stroke="#444444", stroke_width=0.9),
    ], class_="bob"))
    return s.render(labels["aria"]["bluehole"])


def build_tepui(labels):
    """Majestic flat-topped sandstone Tepui (Monte Roraima style) with sheer fluted cliffs, twin waterfalls, cloud sea, and Heliamphora."""
    s = vignette("tepui", 108)
    rng = s.rng
    sky(s, [(0, "#d9885b"), (0.36, "#f2bfa0"), (0.72, "#cde2ee"), (1, "#a2cae0")])
    sun(s, 86, 58, 16, glow="#ffdfb0")
    s.add(cloud(rng, 390, 48, 90, col="#fff2e2", shade="#d4b29c", op=0.8))

    # Distant sister tepui silhouette on the left horizon shrouded in mist
    s.add(el("path", d="M-20,128 L86,126 L94,142 L106,215 L-20,215Z", fill="#9c8588", opacity=0.52))
    s.add(mist(s, 40, 195, 90, 18, op=0.65))

    # Main Tepui Tabletop Fortress with craggy sandstone battlements (no geometric mushroom row!)
    tabletop = [
        (112, 88), (126, 83), (144, 85), (165, 81), (185, 86), (204, 80),
        (232, 81), (258, 85), (284, 79), (316, 81), (345, 85), (372, 80),
        (398, 82), (418, 86),
    ]
    cliff_l = [(112, 88), (109, 118), (114, 152), (104, 192), (92, 238)]
    cliff_r = [(418, 86), (422, 122), (416, 158), (424, 198), (434, 238)]
    tepui_pts = tabletop + cliff_r[1:] + [(456, 262), (72, 262)] + list(reversed(cliff_l))
    tepui_d = P(tepui_pts)
    s.add(el("path", d=tepui_d, fill="#6e5046"))
    cid = s.clip("tepui_body", tepui_d)

    # Detailed geological strata, 3D sunlit/shadowed cliff facets, and vertical quartzite fissures
    strata = [
        # Right-flank deep shadow face
        el("path", d="M275,78 L460,78 L460,265 L295,265Z", fill="#2b1d19", opacity=0.45),
        # Left-flank warm sunlit face
        el("path", d="M90,78 L215,78 L195,265 L90,265Z", fill="#a87664", opacity=0.32),
    ]
    for k, col in enumerate(("#4f3830", "#826054", "#9c7464", "#3d2a24", "#8c685a", "#583e35", "#3b2822")):
        y_b = 88 + k * 23
        pts_b = [(x, y_b + 2.5 * math.sin(x * 0.05 + k)) for x in range(70, 460, 30)]
        strata.append(el("path", d=smooth(pts_b) + f" L460,{y_b + 14} L70,{y_b + 14}Z", fill=col, opacity=0.62))

    # Vertical columnar fractures & dark water-stained rock chimneys
    fissures_dark, fissures_lit = [], []
    for i, x in enumerate(range(118, 418, 8)):
        top_y = rng.uniform(80, 92)
        bot_y = rng.uniform(225, 250)
        cmd = f"M{n(x)},{n(top_y)} L{n(x + rng.uniform(-2.5, 2.5))},{n(bot_y)}"
        (fissures_dark if i % 2 == 0 else fissures_lit).append(cmd)
    strata.append(el("path", d=" ".join(fissures_dark), stroke="#241612", stroke_width=1.8, fill="none", opacity=0.75))
    strata.append(el("path", d=" ".join(fissures_lit), stroke="#b58976", stroke_width=0.9, fill="none", opacity=0.45))

    # Natural emerald Bonnetia cushion vegetation mats along the summit plateau ledges
    for vx, vy, vr in ((135, 84, 14), (168, 82, 12), (218, 81, 18), (248, 84, 13),
                       (298, 80, 19), (328, 83, 12), (382, 81, 16), (406, 84, 11)):
        strata.append(el("ellipse", cx=vx, cy=vy, rx=vr, ry=3.5, fill="#2d5426"))
        strata.append(el("ellipse", cx=vx - 2, cy=vy - 1, rx=vr * 0.7, ry=2.2, fill="#4b7d3c"))

    # Talus slope ramp at base of sheer wall
    strata.append(el("path", d="M72,262 L115,195 L180,222 L265,202 L355,220 L418,192 L456,262Z", fill="#3d2f2a", opacity=0.68))
    s.add(g(strata, clip_path=cid))

    # Twin horsetail waterfalls (Angel Falls / Kukenán style) plunging from tabletop into mist
    s.add(waterfall(s, 185, 86, 244, 9))
    s.add(waterfall(s, 345, 85, 246, 10))

    # Soft drifting valley mist & cloud sea around the base of the tepui (no hard-edged sky clouds!)
    s.add(mist(s, 175, 232, 130, 18, op=0.78))
    s.add(mist(s, 355, 230, 135, 18, op=0.75))
    s.add(mist(s, 250, 244, 240, 20, op=0.82))

    # Cloud forest canopy at base of Tepui
    s.add(g(canopy_band(s, -20, 500, lambda x: 250 + 6 * math.sin(x / 30), 22, 14, 26, ("#173d1e", "#285929", "#4f8a3e"), k=5)))

    # Foreground sandstone boulder terrace with endemic Heliamphora pitcher plants & Oreophrynella pebble toad
    fg_rock = [(0, 238), (95, 240), (142, 248), (162, 278), (135, 300), (0, 300)]
    s.add(el("path", d=smooth(fg_rock) + "Z", fill="#453832"))
    s.add(el("path", d="M0,238 Q70,239 140,248 L125,256 Q60,248 0,248Z", fill="#69554c", opacity=0.65))
    # Mossy cushion patches on the sandstone terrace
    s.add(el("ellipse", cx=55, cy=268, rx=42, ry=7, fill="#335428", opacity=0.65))
    s.add(el("ellipse", cx=105, cy=276, rx=28, ry=5, fill="#335428", opacity=0.6))
    s.add(bromeliad(rng, 18, 252, 11))
    s.add(pitcher_plant(44, 268, 1.15, flower=True))
    s.add(pitcher_plant(78, 274, 0.92, flower=False))
    s.add(pitcher_plant(108, 278, 1.05, flower=True))

    # Detailed endemic Roraima Black Pebble Toad (Oreophrynella quelchii) on mossy rock
    fx, fy = 136, 264
    s.add(g([
        el("ellipse", cx=fx, cy=fy + 3.2, rx=7.5, ry=2.0, fill="#000000", opacity=0.35),
        el("path", d=f"M{fx - 4},{fy + 1} L{fx - 8},{fy + 3} L{fx - 5},{fy + 3.5} M{fx + 4},{fy + 1} L{fx + 7},{fy + 3.5}",
           stroke="#1e1c1a", stroke_width=1.6, fill="none", stroke_linecap="round"),
        el("path", d=f"M{fx - 6},{fy + 1} C{fx - 6},{fy - 4} {fx + 2},{fy - 5} {fx + 6},{fy - 1} C{fx + 7},{fy + 2} {fx - 5},{fy + 3} {fx - 6},{fy + 1}Z",
           fill="#1c1b1a"),
        el("circle", cx=fx - 2, cy=fy - 1.5, r=0.8, fill="#383532"),
        el("circle", cx=fx + 1, cy=fy - 2.0, r=0.7, fill="#383532"),
        el("circle", cx=fx - 0.5, cy=fy, r=0.7, fill="#383532"),
        el("circle", cx=fx + 3.8, cy=fy - 2.2, r=1.3, fill="#e8b828"),
        el("circle", cx=fx + 4.0, cy=fy - 2.2, r=0.6, fill="#111111"),
    ]))
    s.add(condor(290, 48, 0.62))
    return s.render(labels["aria"]["tepui"])


def build_cataracts(labels):
    """Multi-tiered roaring basalt cataracts (Iguazú / Rio Esmeralda style) with rock steps, spray cauldron, rainbow, and toucan."""
    s = vignette("cataracts", 109)
    rng = s.rng
    sky(s, [(0, "#468cc8"), (0.55, "#94c6e4"), (1, "#dcf0f6")], h=118)
    s.add(cloud(rng, 108, 44, 88), cloud(rng, 362, 48, 98))

    # Distant subtropical rainforest canopy along the upper river rim
    s.add(g(canopy_band(s, -10, 490, lambda x: 88 + 3 * math.sin(x / 25), 24, 9, 15, ("#1c4624", "#2e6832", "#569444"), k=5)))

    # Upper emerald river approaching the precipice
    s.add(el("rect", x=0, y=88, width=480, height=26, fill=s.linear("upriv", [(0, "#2f6359"), (1, "#488c7e")])))
    s.add(water_lines(rng, 0, 480, 91, 110, 26, col="#e0f4f0", op=0.55))

    # Columnar flood-basalt canyon wall with stepped horizontal terrace ledges
    canyon_lip = [(0, 112), (90, 115), (180, 110), (270, 114), (370, 110), (480, 114)]
    s.add(el("path", d=smooth(canyon_lip) + " L480,242 L0,242Z", fill="#2d2623"))
    basalt_cols = " ".join(f"M{n(x)},114 L{n(x)},238" for x in range(12, 475, 14))
    s.add(el("path", d=basalt_cols, stroke="#1c1715", stroke_width=1.4, opacity=0.65))
    s.add(el("path", d="M0,168 Q120,174 250,166 Q370,172 480,168 L480,182 L0,182Z", fill="#3d3430"))
    # Craggy 3D basalt rock shelves & hanging cliff vegetation between the waterfalls (no flat ovals!)
    for rx_, ry_, rw_ in ((108, 170, 28), (208, 172, 32), (322, 170, 30), (412, 173, 24)):
        s.add(el("path", d=f"M{rx_ - rw_ * 0.5},{ry_} L{rx_ - rw_ * 0.35},{ry_ - 5} L{rx_ + rw_ * 0.38},{ry_ - 4} L{rx_ + rw_ * 0.5},{ry_} L{rx_ + rw_ * 0.3},{ry_ + 6} L{rx_ - rw_ * 0.3},{ry_ + 5}Z",
                 fill="#4a3f3a"))
        s.add(crown(rng, rx_, ry_ - 4, rw_ * 0.32, ("#1d4422", "#346e34", "#5c9c46"), k=4, flat=0.55, detail=False))

    # Five thundering multi-tiered waterfall curtains across the amphitheater
    s.add(waterfall(s, 64, 113, 236, 36))
    s.add(waterfall(s, 155, 112, 238, 44))
    s.add(waterfall(s, 262, 108, 242, 68))
    s.add(waterfall(s, 375, 111, 236, 42))
    s.add(waterfall(s, 446, 113, 234, 30))

    # Lush emerald rock islands along the canyon brink dividing the falls
    for x, w in ((102, 22), (202, 26), (318, 28), (412, 18)):
        s.add(el("path", d=f"M{x},118 L{x + 3},106 L{x + w - 3},106 L{x + w},118Z", fill="#3b322c"))
        s.add(crown(rng, x + w / 2, 106, 11, ("#1b4622", "#326e32", "#609e48"), k=5, detail=False))

    # Boiling mist cauldron at base of gorge
    s.add(mist(s, 260, 230, 235, 26, op=0.88))
    s.add(mist(s, 140, 226, 155, 22, op=0.78))
    s.add(mist(s, 380, 226, 155, 22, op=0.78))

    # Luminous optical double rainbow arching through the cataract spray
    rainbow_colors = ["#ff5e5e", "#ffa502", "#f6e58d", "#2ed573", "#1e90ff", "#5352ed"]
    for i, col in enumerate(rainbow_colors):
        r = 138 - i * 2.8
        s.add(el("path", d=f"M{260 - r},240 A{r},{r * 0.84} 0 0 1 {260 + r},240",
                 stroke=col, stroke_width=3.2, fill="none", opacity=0.36, filter=s.url("soft")))

    # Lower emerald plunge pool river with turbulent foam lines
    s.add(el("rect", x=0, y=236, width=480, height=64,
             fill=s.linear("pool", [(0, "#429688"), (0.45, "#368073"), (1, "#1e5248")])))
    s.add(water_lines(rng, 0, 480, 240, 296, 42, col="#dcf6f0", op=0.58))

    # Foreground basalt cliff promontory with overarching mossy tree limb, ferns, Heliconia, and perched Toucan
    fg_bank = [(0, 206), (56, 222), (88, 258), (64, 300), (0, 300)]
    s.add(el("path", d=smooth(fg_bank) + "Z", fill="#26201d"))
    s.add(el("path", d="M0,206 C22,210 44,216 56,222 L42,232 C25,222 10,216 0,214Z", fill="#453a34", opacity=0.85))
    # Sunlit mossy branch extending out over the mist cauldron as a perch for the Toucan
    s.add(el("path", d="M0,192 Q42,190 92,198 Q106,200 116,195", stroke="#4d3928", stroke_width=5.0, fill="none", stroke_linecap="round"))
    s.add(el("path", d="M0,190 Q42,188 92,196", stroke="#759c44", stroke_width=2.0, fill="none", stroke_linecap="round"))
    s.add(fern(rng, 22, 232, 38, "#387c34"))
    s.add(fern(rng, 52, 250, 44, "#4da048"))
    s.add(heliconia(18, 274, 44))
    s.add(bromeliad(rng, 82, 196, 10))
    # Toco Toucan perched high on the branch, clearly silhouetted against the bright waterfall mist
    s.add(toucan(52, 182, 0.98))

    # White-collared swifts (Streptoprocne zonaris) darting across the falls
    for bx, by, bs in ((208, 164, 5.8), (244, 152, 4.8), (282, 168, 5.8), (312, 158, 4.5)):
        s.add(bird_v(bx, by, bs, "#ffffff"))
    return s.render(labels["aria"]["cataracts"])


def cuban_trogon(x, y, s, flip=False):
    """Endemic Cuban Trogon / Tocororo (Priotelus temnurus) perched with scalloped tail, metallic green back, white breast, crimson belly, and blue crown."""
    sx = -1 if flip else 1
    return g([
        # Distinctive scalloped/toothed long tail feathers (dark blue-green with white-edged lateral rectrices)
        el("path", d="M-2,6 L-9,33 L-6,31 L-4,34 L-1,31 L2,34 L4,8Z", fill="#193b52"),
        el("path", d="M-5.5,14 L-8.5,31 L-6,30 L-3.5,14Z M1.5,14 L2,31 L0,30 L-0.5,14Z", fill="#eef4f8", opacity=0.88),
        # Crimson-scarlet lower belly and undertail coverts
        el("path", d="M-2,3 C0,1 6,2 7.5,8 C6.5,14 2.5,16 -1,13 C-3,10 -3,6 -2,3Z", fill="#d92626"),
        # Pure white throat and upper breast collar
        el("path", d="M0,-4 C4,-5 8,-2 7.5,4 C4,5.5 -0.5,4.5 -1.5,1 C-2,-2 -1,-3.5 0,-4Z", fill="#f7f9fc"),
        # Iridescent bronze-emerald back & folded wing with fine white tertial vermiculations
        el("path", d="M-4,-3 C-5,2 -4,10 0,13 C2,8 2.5,1 0,-4Z", fill="#1d7848"),
        el("path", d="M-3.5,-1 C-1,0 1,4 0,10 C-2.5,9 -4,4 -3.5,-1Z", fill="#2da060"),
        el("path", d="M-2.5,2 L0,3 M-2.8,4.5 L0,5.5 M-2.5,7 L-0.2,8", stroke="#e8f2ee", stroke_width=0.75, opacity=0.8),
        # Violet-blue crown and nape, dark mask, crimson iris with white orbital ring, and stout coral-red bill
        el("path", d="M-3.5,-4 C-4,-9 1,-11.5 5,-9.5 C6.5,-8 6,-4.5 3.5,-3.5 C0.5,-3 -2.5,-3 -3.5,-4Z", fill="#1f448c"),
        el("path", d="M0.5,-7.5 C3.5,-8 5.8,-6.5 5.5,-4 C3.5,-3.5 1,-4 0.5,-7.5Z", fill="#161c24"),
        el("circle", cx=3.2, cy=-6.0, r=1.35, fill="#ffffff"),
        el("circle", cx=3.2, cy=-6.0, r=0.85, fill="#b81d1d"),
        el("path", d="M5.2,-7.2 C8.5,-7.0 9.8,-5.5 8.8,-4.2 C7.2,-4.0 5.8,-4.2 5.2,-4.8Z", fill="#e03c32"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def build_elnicho(labels):
    """El Nicho Travertine Cascades (Topes de Collantes, Escambray Mountains, Cuba): stepped turquoise travertine pools, lacy veil cascades, royal palms, tree ferns, and Cuban trogon."""
    s = vignette("elnicho", 110)
    rng = s.rng
    sky(s, [(0, "#4f97c9"), (0.5, "#9ed2e6"), (1, "#e6f5ec")], h=110)
    sun(s, 395, 42, 16, glow="#fff2c2")

    # Misty Sierra del Escambray mountain ridges in the background
    m_far, _ = hill(s, [(0, 86), (95, 54), (205, 74), (320, 48), (425, 68), (480, 58)], 125, "#6b998b")
    s.add(m_far)
    s.add(mist(s, 240, 82, 210, 14, op=0.55))

    # Lush Escambray cloud-forest canopy & Cuban royal palms along the upper canyon rim
    s.add(g(canopy_band(s, -15, 495, lambda x: 96 + 4 * math.sin(x / 28), 24, 11, 18, ("#174223", "#2b6933", "#589c49"), k=5)))
    for px, py, ph, plean in ((88, 96, 52, -5), (124, 98, 44, 4), (358, 94, 54, 6), (402, 96, 46, -4)):
        s.add(palm(rng, px, py, ph, plean, 18, cols=("#1f5727", "#488e3e"), trunk_col="#cfc9bc", royal=True, coconuts=False))

    # Upper emerald stream feeding the travertine ledges
    s.add(el("rect", x=45, y=96, width=390, height=22, fill=s.linear("uppool", [(0, "#1d6b63"), (1, "#359c8e")])))
    s.add(water_lines(rng, 65, 415, 99, 114, 18, col="#dcf7f2", op=0.55))

    # Stepped limestone & calcified travertine canyon walls (organic craggy profile, no flat horizontal top bar)
    canyon_top = [(0, 102), (35, 96), (72, 112), (175, 110), (245, 113), (315, 110), (408, 112), (445, 98), (480, 104)]
    s.add(el("path", d=smooth(canyon_top) + " L480,235 L0,235Z", fill="#3d342b"))
    # Upper travertine dam rim (y ~ 112..156) with natural scalloped tufa lobes
    for tx, tw, th, col in ((68, 112, 42, "#8c7b65"), (168, 148, 46, "#9e8c74"), (304, 116, 42, "#877660")):
        s.add(el("path", d=(
            f"M{tx},112 Q{tx + tw * 0.25},108 {tx + tw * 0.5},111 Q{tx + tw * 0.75},108 {tx + tw},112 "
            f"Q{tx + tw + 8},{112 + th * 0.5} {tx + tw - 4},{112 + th} "
            f"L{tx + 4},{112 + th} Q{tx - 8},{112 + th * 0.5} {tx},112Z"
        ), fill=col))
        # Vertical fluted tufa stalactite ribs on travertine face
        flutes = " ".join(f"M{n(x)},113 Q{n(x + rng.uniform(-1.5, 1.5))},{112 + th * 0.5} {n(x)},{110 + th}"
                          for x in range(tx + 8, tx + tw - 6, 6))
        s.add(el("path", d=flutes, stroke="#5e5040", stroke_width=1.2, fill="none", opacity=0.6))
        # Natural botanical moss & fern clusters along the travertine lip
        s.add(crown(rng, tx + tw * 0.24, 111, 12, ("#1d4720", "#316e2d", "#5c9e48"), k=4, flat=0.45, detail=False))
        s.add(crown(rng, tx + tw * 0.78, 112, 11, ("#1d4720", "#316e2d", "#5c9e48"), k=4, flat=0.45, detail=False))

    # Tier 1 lacy white-water veil cascades plunging into the middle travertine pool
    for wx, ww in ((115, 22), (195, 28), (248, 34), (298, 22), (355, 24)):
        s.add(waterfall(s, wx, 111, 158, ww))

    # Middle turquoise-jade travertine terrace basin (y = 152..188)
    mid_pool_d = "M52,156 Q145,149 245,152 Q345,149 428,156 Q442,174 418,188 Q245,195 62,188 Q38,174 52,156Z"
    s.add(el("path", d=mid_pool_d, fill=s.linear("midpool", [(0, "#3fd4c0"), (0.55, "#1ea898"), (1, "#12736a")])))
    s.add(water_lines(rng, 72, 405, 158, 184, 24, col="#e4fcf8", op=0.62))
    s.add(mist(s, 245, 156, 145, 10, op=0.58))

    # Scalloped calcified travertine rim dam of the middle pool (y = 182..224) with multi-stepped tufa shelves
    for sx_, sw_, sy_, sh_ in ((58, 125, 183, 40), (168, 154, 185, 42), (308, 120, 183, 40)):
        s.add(el("path", d=(
            f"M{sx_},{sy_} Q{sx_ + sw_ * 0.5},{sy_ + 6} {sx_ + sw_},{sy_} "
            f"Q{sx_ + sw_ + 10},{sy_ + sh_ * 0.6} {sx_ + sw_ - 6},{sy_ + sh_} "
            f"L{sx_ + 6},{sy_ + sh_} Q{sx_ - 10},{sy_ + sh_ * 0.6} {sx_},{sy_}Z"
        ), fill="#a8947a"))
        s.add(el("path", d=f"M{sx_},{sy_} Q{sx_ + sw_ * 0.5},{sy_ + 6} {sx_ + sw_},{sy_}",
                 stroke="#dfd2be", stroke_width=2.6, fill="none", opacity=0.8))
        flutes2 = " ".join(f"M{n(x)},{sy_ + 2} L{n(x + rng.uniform(-1.5, 1.5))},{sy_ + sh_ - 2}"
                           for x in range(sx_ + 9, sx_ + sw_ - 8, 6))
        s.add(el("path", d=flutes2, stroke="#695947", stroke_width=1.15, fill="none", opacity=0.6))
        s.add(crown(rng, sx_ + sw_ * 0.5, sy_ + 2, 13, ("#1d4720", "#316e2d", "#5c9e48"), k=4, flat=0.42, detail=False))

    # Tier 2 bridal-veil travertine cascades spilling into the crystal lower swimming lagoon
    for wx, ww in ((96, 20), (148, 26), (212, 32), (268, 30), (324, 24), (382, 18)):
        s.add(waterfall(s, wx, 185, 226, ww))
    s.add(mist(s, 240, 224, 165, 12, op=0.62))

    # Lower crystal-clear emerald-turquoise natural swimming lagoon (y = 220..300)
    s.add(el("rect", x=0, y=220, width=480, height=80,
             fill=s.linear("lowpool", [(0, "#4ce0cc"), (0.38, "#22b5a4"), (0.78, "#0f7d73"), (1, "#084f4a")])))
    # Submerged cream travertine shelves visible through the crystal water
    s.add(el("ellipse", cx=195, cy=252, rx=78, ry=12, fill="#8cebe0", opacity=0.32))
    s.add(el("ellipse", cx=310, cy=268, rx=65, ry=10, fill="#8cebe0", opacity=0.25))
    s.add(water_lines(rng, 25, 455, 226, 294, 38, col="#e8fffb", op=0.65))

    # Framing limestone grotto banks with giant Cuban tree ferns, heliconias, mariposa orchids, and perched Cuban Trogon
    left_bank = [(0, 128), (48, 146), (68, 196), (82, 248), (64, 300), (0, 300)]
    right_bank = [(480, 134), (432, 152), (416, 202), (404, 254), (422, 300), (480, 300)]
    s.add(el("path", d=smooth(left_bank) + "Z", fill="#29241e"))
    s.add(el("path", d=smooth(right_bank) + "Z", fill="#29241e"))
    s.add(crown(rng, 24, 142, 32, ("#153b1e", "#28612e", "#4e8f42"), k=6))
    s.add(crown(rng, 456, 148, 30, ("#153b1e", "#28612e", "#4e8f42"), k=6))
    s.add(fern(rng, 32, 218, 44, "#3b8236"))
    s.add(fern(rng, 58, 256, 48, "#52a348"))
    s.add(fern(rng, 442, 228, 44, "#3b8236"))
    s.add(fern(rng, 418, 264, 42, "#52a348"))
    s.add(heliconia(22, 286, 46))
    s.add(heliconia(454, 288, 42))

    # Mossy overhanging branch on the left with white Cuban Mariposa (Hedychium) blossom & perched Cuban Trogon (Tocororo)
    s.add(el("path", d="M0,174 Q48,170 98,178 Q114,180 124,175", stroke="#4a3727", stroke_width=4.8, fill="none", stroke_linecap="round"))
    s.add(el("path", d="M0,172 Q48,168 96,176", stroke="#6c963e", stroke_width=1.8, fill="none", stroke_linecap="round"))
    s.add(bromeliad(rng, 88, 176, 9.5))
    s.add(cuban_trogon(56, 166, 0.96))
    return s.render(labels["aria"]["elnicho"])


def build_anavilhanas(labels):
    """Anavilhanas Fluvial Archipelago and Encontro das Águas (Amazonas): emerald igapó islands in dark mirror Rio Negro channels meeting golden-ochre Solimões water with pink river dolphins."""
    s = vignette("anavilhanas", 111)
    rng = s.rng
    sky(s, [(0, "#3b7cb8"), (0.45, "#88bee0"), (0.82, "#dfeef2"), (1, "#f7e6c4")], h=96)
    sun(s, 392, 42, 16, glow="#ffebb5")
    s.add(cloud(rng, 118, 38, 92), cloud(rng, 275, 44, 82))

    # Distant continuous Amazonian rainforest horizon line
    s.add(g(canopy_band(s, -15, 495, lambda x: 92 + 2.5 * math.sin(x / 35), 28, 8, 13, ("#1c4228", "#2d6136", "#4a8244"), k=4)))

    # Base river water: deep tea-black Rio Negro mirror water across upper/left channels
    negro_grad = s.linear("negro", [(0, "#1d2e3a"), (0.45, "#122028"), (1, "#0a141a")])
    s.add(el("rect", x=0, y=92, width=480, height=208, fill=negro_grad))

    # Encontro das Águas (Meeting of Waters): sandy golden-ochre Solimões current sweeping across the right/lower basin
    solimoes_grad = s.linear("solimoes", [(0, "#c99b56"), (0.5, "#b88642"), (1, "#9c6d2e")])
    encontro_pts = [
        (480, 148), (415, 156), (348, 168), (295, 184),
        (258, 204), (218, 226), (168, 252), (112, 278), (68, 300), (480, 300),
    ]
    s.add(el("path", d=smooth(encontro_pts) + "Z", fill=solimoes_grad))

    # Swirling two-tone current eddies, sediment plumes, and foam line along the sinuous Rio Negro / Solimões interface
    seam_pts = encontro_pts[:-1]
    s.add(el("path", d=smooth(seam_pts), stroke="#dfb572", stroke_width=5.5, fill="none", opacity=0.55, filter=s.url("soft")))
    s.add(el("path", d=smooth([(x - 5, y - 1.5) for x, y in seam_pts]), stroke="#162830", stroke_width=3.2, fill="none", opacity=0.7))
    s.add(el("path", d=smooth([(x + 2, y + 0.5) for x, y in seam_pts]), stroke="#f7e6c4", stroke_width=1.6, fill="none", opacity=0.75))
    # Small interlocking current tongues along the confluence seam
    for cx_, cy_, rx_, col_ in ((365, 166, 16, "#16262e"), (312, 179, 18, "#d4a660"),
                                (272, 196, 15, "#16262e"), (232, 218, 19, "#d4a660"),
                                (185, 242, 16, "#16262e"), (138, 266, 18, "#d4a660")):
        s.add(el("ellipse", cx=cx_, cy=cy_, rx=rx_, ry=3.2, fill=col_, opacity=0.72))

    # Helper to draw an elongated Anavilhanas flooded igapó forest island with dark water reflection & Mauritia palms
    def igapo_island(x0, x1, y_base, h_canopy, n_crowns, palms=()):
        w = x1 - x0
        # Submerged dark reflection in the mirror Rio Negro water
        refl_d = (f"M{n(x0 + 4)},{n(y_base)} L{n(x1 - 4)},{n(y_base)} "
                  f"Q{n(x1 - w * 0.12)},{n(y_base + h_canopy * 0.65)} {n((x0 + x1) * 0.5)},{n(y_base + h_canopy * 0.72)} "
                  f"Q{n(x0 + w * 0.12)},{n(y_base + h_canopy * 0.65)} {n(x0 + 4)},{n(y_base)}Z")
        items = [
            el("path", d=refl_d, fill="#091614", opacity=0.68),
            # Flooded igapó root & sedge bank
            el("path", d=f"M{n(x0)},{n(y_base)} Q{n((x0 + x1) * 0.5)},{n(y_base - 6)} {n(x1)},{n(y_base)} "
                         f"Q{n((x0 + x1) * 0.5)},{n(y_base + 3)} {n(x0)},{n(y_base)}Z", fill="#2b2118"),
        ]
        # Dense rounded emerald archipelago canopy
        for i in range(n_crowns):
            t = (i + 0.5) / n_crowns
            cx_ = x0 + w * (0.1 + 0.8 * t)
            arch = math.sin(math.pi * t)
            r_ = h_canopy * (0.45 + 0.45 * arch) * rng.uniform(0.9, 1.08)
            cy_ = y_base - r_ * 0.52 - arch * h_canopy * 0.22
            items.append(crown(rng, cx_, cy_, r_, ("#143b20", "#26632e", "#529944"), k=6, flat=0.72))
        for px_, ph_, plean_ in palms:
            items.append(palm(rng, px_, y_base - 2, ph_, plean_, 14, cols=("#1f5727", "#4c9140"),
                              trunk_col="#6e5842", coconuts=False))
        # Shoreline water ripple lines strictly inside island width
        rip_d = (f"M{n(x0 + w * 0.08)},{n(y_base + 1.5)} Q{n((x0 + x1) * 0.5)},{n(y_base + 2.8)} {n(x1 - w * 0.08)},{n(y_base + 1.5)} "
                 f"M{n(x0 + w * 0.22)},{n(y_base + 3.8)} L{n(x1 - w * 0.22)},{n(y_base + 3.8)}")
        items.append(el("path", d=rip_d, stroke="#7ab8b0", stroke_width=0.85, fill="none", opacity=0.42))
        return g(items)

    # Four layered Anavilhanas archipelago islands threading the Rio Negro channels
    s.add(igapo_island(25, 165, 124, 24, 6, palms=((72, 34, -4), (128, 30, 3))))
    s.add(igapo_island(215, 378, 120, 22, 7, palms=((268, 32, 4), (332, 28, -3))))
    s.add(igapo_island(375, 472, 138, 22, 5, palms=((425, 30, -4),)))
    s.add(igapo_island(-10, 198, 174, 30, 7, palms=((58, 42, 5), (144, 38, -4))))
    s.add(igapo_island(195, 312, 162, 24, 5, palms=((248, 34, 3),)))

    # Shimmering water lines on both the dark Rio Negro and golden Solimões currents
    s.add(water_lines(rng, 10, 260, 180, 275, 26, col="#6fa8a4", op=0.35))
    s.add(water_lines(rng, 220, 470, 175, 292, 30, col="#fae3b4", op=0.52))

    # Giant Victoria amazonica water lilies floating in the calm blackwater bay on the lower left
    for lx, ly, lr, fl in ((42, 246, 16, False), (88, 258, 22, True), (36, 278, 26, True), (104, 284, 18, False)):
        s.add(water_lily(rng, lx, ly, lr, flower=fl))

    # Pair of Amazonian Pink River Dolphins (Boto / Inia geoffrensis) breaching across the Encontro das Águas boundary!
    s.add(dolphin(258, 224, 1.05))
    s.add(dolphin(338, 252, 0.82))

    # Scarlet Macaws flying over the archipelago channels
    s.add(macaw(168, 62, 0.72))
    s.add(macaw(212, 74, 0.56))
    return s.render(labels["aria"]["anavilhanas"])


def build_chapada(labels):
    """Chapada Diamantina Mesas and Poço Encantado Crystal Grotto (Brazil): flat-topped Morro do Pai Inácio tablelands above and subterranean cobalt cavern lake pierced by a diagonal sunbeam below."""
    s = vignette("chapada", 112)
    rng = s.rng
    sky(s, [(0, "#4384bf"), (0.5, "#8ec2e2"), (1, "#f5dec0")], h=128)
    sun(s, 96, 46, 15, glow="#ffeaad")
    s.add(cloud(rng, 362, 38, 86))

    # Upper Vista: Iconic flat-topped sandstone mesas of Chapada Diamantina (Morro do Pai Inácio & Morro do Camelo)
    # Far mesa on left with stratified caprock and talus apron
    s.add(el("path", d="M8,108 L22,68 L30,65 L108,64 L116,68 L132,108Z", fill="#9e7462", opacity=0.82))
    s.add(el("path", d="M22,68 L30,65 L108,64 L116,68 L120,78 L18,78Z", fill="#c49378", opacity=0.68))
    s.add(el("path", d="M68,65 L108,64 L116,68 L132,108 L82,108Z", fill="#69483b", opacity=0.42))

    # Main Morro do Pai Inácio tableland on center-right with craggy battlements, 3D sunlit/shadow facets, and strata
    mesa_top = [(186, 47), (202, 43), (228, 44), (256, 42), (288, 44), (316, 43), (332, 47)]
    mesa_pts = [(162, 108), (178, 74)] + mesa_top + [(346, 74), (364, 108)]
    mesa_d = P(mesa_pts)
    s.add(el("path", d=mesa_d, fill="#7d5243"))
    mcid = s.clip("pai_inacio", mesa_d)
    mesa_details = [
        # Sunlit left cliff face & shadowed right cliff flank
        el("path", d="M160,40 L256,40 L242,110 L160,110Z", fill="#b87e63", opacity=0.48),
        el("path", d="M272,40 L370,40 L370,110 L285,110Z", fill="#3d241c", opacity=0.45),
        # Horizontal sandstone strata bands
        el("path", d="M160,54 L365,54 L365,63 L160,63Z", fill="#c98e70", opacity=0.55),
        el("path", d="M160,72 L365,72 L365,81 L160,81Z", fill="#59362b", opacity=0.52),
        # Basal talus cones
        el("path", d="M162,108 L195,78 L232,96 L275,76 L318,95 L344,80 L364,108Z", fill="#4a2e24", opacity=0.65),
    ]
    mesa_flutes = " ".join(f"M{n(x)},43 L{n(x + rng.uniform(-2, 2))},102" for x in range(188, 332, 8))
    mesa_details.append(el("path", d=mesa_flutes, stroke="#3d241c", stroke_width=1.25, fill="none", opacity=0.65))
    s.add(g(mesa_details, clip_path=mcid))
    # Organic campos rupestres cushion mats along the summit plateau
    for vx, vr in ((204, 14), (236, 18), (272, 16), (308, 15)):
        s.add(crown(rng, vx, 43.5, vr * 0.65, ("#244a1e", "#3b6e30", "#62994a"), k=4, flat=0.35, detail=False))

    # Undulating campos rupestres highland ridge above the cavern
    ridge_pts = [(0, 102), (45, 96), (92, 100), (155, 98), (225, 92), (310, 96), (395, 90), (480, 98)]
    s.add(el("path", d=smooth(ridge_pts) + " L480,126 L0,126Z", fill="#4d6932"))
    s.add(tufts(rng, 0, 480, interp(ridge_pts), 42, 7, "#769c48", op=0.75))

    # Lower Cutaway: Vaulted Quartzite Cavern of Poço Encantado (y = 104..300)
    s.add(el("rect", x=0, y=106, width=480, height=194, fill="#0e1018"))
    # Back cavern wall with stratified quartzite ledges above the subterranean lake
    s.add(el("path", d="M45,114 L445,114 L455,214 L35,214Z", fill="#221e28"))
    for k, col in enumerate(("#382e3b", "#4a3b48", "#2d2533", "#423542", "#251f2b")):
        yb = 122 + k * 17
        pts_w = [(x, yb + 3.2 * math.sin(x * 0.045 + k)) for x in range(40, 455, 32)]
        s.add(el("path", d=smooth(pts_w) + f" L450,{yb + 13} L40,{yb + 13}Z", fill=col, opacity=0.78))
    # Vertical cavern wall fractures
    wall_cracks = " ".join(f"M{n(x)},118 L{n(x + rng.uniform(-6, 6))},206" for x in range(75, 415, 24))
    s.add(el("path", d=wall_cracks, stroke="#141118", stroke_width=1.3, fill="none", opacity=0.65))

    # Subterranean Crystal-Clear Cobalt Lake (Poço Encantado, y = 206..300)
    lake_grad = s.radial("poco", [
        (0, "#42eeff", 1),
        (0.26, "#189cf7", 1),
        (0.56, "#0b4ec4", 1),
        (0.82, "#062570", 1),
        (1, "#031033", 1),
    ], cx=0.52, cy=0.42, r=0.62)
    s.add(el("rect", x=0, y=206, width=480, height=94, fill=lake_grad))

    # 3D Faceted Submerged Quartzite Rock Slabs & Boulders visible 60m below through the crystal-clear cobalt water!
    def submerged_rock(rx, ry, rw, rh, lit_c="#38bdf8", mid_c="#1368cc", dark_c="#083375"):
        p_top = [(rx - rw * 0.48, ry), (rx - rw * 0.22, ry - rh * 0.65), (rx + rw * 0.28, ry - rh * 0.55), (rx + rw * 0.5, ry)]
        p_front = [(rx - rw * 0.48, ry), (rx + rw * 0.5, ry), (rx + rw * 0.38, ry + rh * 0.45), (rx - rw * 0.35, ry + rh * 0.42)]
        p_shade = [(rx + rw * 0.05, ry - rh * 0.6), (rx + rw * 0.28, ry - rh * 0.55), (rx + rw * 0.5, ry),
                   (rx + rw * 0.38, ry + rh * 0.45), (rx + rw * 0.02, ry + rh * 0.2)]
        return g([
            el("path", d=P(p_front), fill=mid_c, opacity=0.72),
            el("path", d=P(p_top), fill=lit_c, opacity=0.55),
            el("path", d=P(p_shade), fill=dark_c, opacity=0.68),
        ])

    for rx_, ry_, rw_, rh_ in ((145, 276, 46, 15), (195, 264, 52, 17), (255, 278, 64, 20),
                               (318, 262, 50, 16), (282, 248, 38, 12), (368, 276, 44, 14)):
        s.add(submerged_rock(rx_, ry_, rw_, rh_))
    # Submerged fallen trunk on the lake bed
    s.add(el("path", d="M188,286 Q248,274 312,287", stroke="#0a3b87", stroke_width=5.5, fill="none", stroke_linecap="round", opacity=0.78))
    s.add(el("path", d="M188,285 Q248,273 312,286", stroke="#5ce4ff", stroke_width=1.6, fill="none", stroke_linecap="round", opacity=0.48))

    # Iconic Diagonal Shaft of Sunlight piercing from the upper-left cave skylight (x=94..150, y=104) into the cobalt pool
    beam_grad = s.linear("poco_beam", [
        (0, "#fff9de", 0.66),
        (0.35, "#aef0ff", 0.40),
        (0.75, "#38b6ff", 0.25),
        (1, "#1678f0", 0.0),
    ], x1=0.2, y1=0, x2=0.65, y2=1)
    s.add(el("path", d="M92,102 L152,102 L368,288 L175,288Z", fill=beam_grad, filter=s.url("soft")))
    s.add(el("path", d="M106,102 L138,102 L322,278 L208,278Z", fill=beam_grad))
    # Individual diagonal sunbeam rays inside the shaft
    s.add(light_rays(s, 96, 142, 102, 272, 6, op=0.22))
    # Brilliant turquoise-white surface caustic reflection where the sunbeam enters the water
    s.add(el("ellipse", cx=238, cy=218, rx=66, ry=8.5, fill="#8cf4ff", opacity=0.52, filter=s.url("soft")))
    s.add(el("ellipse", cx=238, cy=218, rx=40, ry=4.2, fill="#e6ffff", opacity=0.75))
    s.add(water_lines(rng, 90, 400, 210, 294, 30, col="#a8f0ff", op=0.54))

    # Vaulted Cavern Roof Arch & Framing Quartzite Walls with Natural Skylight Window at x=92..152
    left_arch = [
        (0, 102), (45, 96), (94, 100), (98, 114), (86, 136), (72, 168),
        (78, 206), (62, 248), (74, 300), (0, 300),
    ]
    right_arch = [
        (148, 100), (225, 92), (310, 96), (395, 90), (480, 98), (480, 300),
        (402, 300), (418, 258), (396, 214), (408, 172), (376, 140),
        (322, 126), (255, 122), (195, 116), (162, 112), (148, 106),
    ]
    s.add(el("path", d=P(left_arch), fill="#2e201d"))
    s.add(el("path", d=P(right_arch), fill="#261a18"))
    # Organic 3D sunlit sandstone facets along the skylight rim & cavern walls (no rectangular planks!)
    s.add(el("path", d="M94,100 L98,114 L86,136 L72,168 L58,156 L72,126 L80,104Z", fill="#8c563e", opacity=0.72))
    s.add(el("path", d="M72,168 L78,206 L62,248 L48,236 L62,198 L58,156Z", fill="#5e3929", opacity=0.65))
    s.add(el("path", d="M148,100 L162,112 L195,116 L255,122 L222,108 L175,104Z", fill="#7d4c36", opacity=0.68))
    s.add(el("path", d="M408,172 L396,214 L418,258 L434,242 L416,204 L424,168Z", fill="#472c22", opacity=0.65))
    # Stalactites and craggy rock pendants hanging from the cavern ceiling arch
    stal_d = " ".join(f"M{n(x)},{n(114 + (x - 165) * 0.06)} l3,{n(rng.uniform(9, 20))} l3.5,{n(-rng.uniform(9, 20))}"
                      for x in range(175, 385, 20))
    s.add(el("path", d=stal_d, fill="#1a1211"))

    # Upper rim foliage, Vellozia rosettes, ferns, and magenta Chapada rock orchids along the skylight & foreground ledges
    s.add(crown(rng, 42, 98, 16, ("#1f471e", "#366b2d", "#5e9646"), k=5, flat=0.55, detail=False))
    s.add(crown(rng, 435, 96, 18, ("#1f471e", "#366b2d", "#5e9646"), k=5, flat=0.55, detail=False))
    s.add(fern(rng, 80, 102, 26, "#3e8438"))
    s.add(fern(rng, 160, 102, 26, "#4d9844"))
    s.add(fern(rng, 38, 252, 36, "#2e6b2b"))
    s.add(fern(rng, 438, 254, 36, "#2e6b2b"))
    s.add(bromeliad(rng, 62, 100, 9.5, col="#5c8f36", flower="#e0367a"))
    s.add(bromeliad(rng, 184, 98, 9.5, col="#5c8f36", flower="#e0367a"))
    s.add(condor(405, 56, 0.55))
    return s.render(labels["aria"]["chapada"])


# ==============================================================================
# LOCALIZATION & INJECTION
# ==============================================================================
LABELS = {
    "en": {
        "transect": ["CORAL REEF", "MANGROVES", "KARST", "RAINFOREST", "PANTANAL", "CERRADO", "CATARACTS", "ANDES"],
        "aria": {
            "transect": "Sea-to-summit cross-section of Waikiki: coral reef, mangrove coast, karst towers, Amazon rainforest, Pantanal wetland, Cerrado savanna, cataract forest and the snow-capped highlands",
            "reef": "Split-level view of a Waikiki mangrove coast and the coral reef beneath it, with sea turtle, manta ray, reef fish and coral nursery frames",
            "rainforest": "Amazonian river scene with layered canopy, emergent kapok trees, giant water lilies, pink river dolphin, macaws and a toucan",
            "highlands": "Brazilia highlands with glacier, turquoise glacial lake, paramo grassland, cloud forest waterfall and soaring Andean condors",
            "mogotes": "Karst mogote towers rising over a tobacco valley with royal palms",
            "enriquillo": "Hypersaline Lago Enriquillo with flamingos, cacti, a rhinoceros iguana and an American crocodile",
            "pantanal": "Flooded Pantanal savanna at sunset with jabiru storks, capybaras and a caiman",
            "cerrado": "Cerrado savanna with flowering ipe trees, termite mounds and a maned wolf",
            "lencois": "White sand dunes with turquoise rain lagoons",
            "caatinga": "Dry Caatinga thorn forest with mandacaru cacti and a hyacinth macaw",
            "bluehole": "Submarine blue hole sinkhole dropping into deep indigo water surrounded by turquoise coral flats with a reef shark and sea turtle",
            "tepui": "Flat-topped sandstone tepui mesa with sheer vertical cliffs, waterfalls plunging into cloud forest and endemic pitcher plants",
            "cataracts": "Multi-tiered roaring waterfalls cascading over dark basalt cliffs with a mist rainbow, lush subtropical ferns and toucan",
            "elnicho": "Stepped turquoise travertine waterfall pools in the Escambray cloud forest of Cuba with royal palms, giant tree ferns and a perched Cuban trogon",
            "anavilhanas": "Flooded emerald igapo forest islands of the Anavilhanas Archipelago above the Meeting of Waters where dark Rio Negro and golden Solimoes currents flow side by side with pink river dolphins",
            "chapada": "Flat-topped sandstone mesas of Chapada Diamantina above the subterranean Poco Encantado cavern lake illuminated in glowing cobalt blue by a diagonal shaft of sunlight",
        },
    },
    "hu": {
        "transect": ["KORALLZÁTONY", "MANGROVE", "KARSZT", "ESŐERDŐ", "PANTANAL", "CERRADO", "ZUHATAGOK", "ANDOK"],
        "aria": {
            "transect": "Waikiki keresztmetszete a tengertől a csúcsokig: korallzátony, mangrovepart, karszttornyok, amazóniai esőerdő, Pantanal vizes élőhely, Cerrado szavanna, zuhatagerdő és a havas hegyvidék",
            "reef": "Waikiki mangrovepartja és az alatta húzódó korallzátony osztott nézetben, tengeri teknőssel, ördögrájával, zátonyhalakkal és korallkertekkel",
            "rainforest": "Amazóniai folyó rétegzett lombkoronával, kiemelkedő kapokfákkal, óriás tündérrózsákkal, rózsaszín folyami delfinnel, arákkal és tukánnal",
            "highlands": "Brazilia hegyvidéke gleccserrel, türkiz gleccsertóval, páramo füves pusztával, köderdei vízeséssel és köröző andoki kondorokkal",
            "mogotes": "Dohányvölgy fölé magasodó karsztos mogote-tornyok királypálmákkal",
            "enriquillo": "A sós Enriquillo-tó flamingókkal, kaktuszokkal, orrszarvúleguánnal és hegyesorrú krokodillal",
            "pantanal": "Elárasztott Pantanal szavanna naplementében jabiru gólyákkal, vízidisznókkal és kajmánnal",
            "cerrado": "Cerrado szavanna virágzó ipéfákkal, termeszvárakkal és sörényes farkassal",
            "lencois": "Fehér homokdűnék türkiz esővíz-lagúnákkal",
            "caatinga": "Száraz Caatinga tüskeerdő mandacaru kaktuszokkal és jácintarával",
            "bluehole": "Mély kobaltkékbe vesző tenger alatti víznyelő türkiz korallzátonyokkal, szirti cápával és tengeri teknőssel",
            "tepui": "Függőleges homokkősziklákkal a felhők fölé magasodó lapos tetejű tepui vízesésekkel és húsevő növényekkel",
            "cataracts": "Bazaltsziklákon lezúduló hatalmas vízesésrendszer szivárvánnyal, szubtrópusi páfrányokkal és tukánnal",
            "elnicho": "Lépcsőzetes türkizkék mésztufa-vízesések és medencék a kubai Escambray-hegység köderdejében királypálmákkal, páfrányfákkal és kubai trogonnal",
            "anavilhanas": "Az Anavilhanas folyami szigetvilág smaragdzöld ártéri szigetei és a fekete Rio Negro, valamint az okkersárga Solimões folyók találkozása rózsaszín folyami delfinekkel",
            "chapada": "A Chapada Diamantina lapos tetejű homokkő táblahegyei és a beszűrődő napsugártól kobaltkéken ragyogó földalatti Poço Encantado barlangi tó",
        },
    },
}

BUILDERS = {
    "transect": build_transect,
    "reef": build_reef,
    "rainforest": build_rainforest,
    "highlands": build_highlands,
    "mogotes": build_mogotes,
    "enriquillo": build_enriquillo,
    "pantanal": build_pantanal,
    "cerrado": build_cerrado,
    "lencois": build_lencois,
    "caatinga": build_caatinga,
    "bluehole": build_bluehole,
    "tepui": build_tepui,
    "cataracts": build_cataracts,
    "elnicho": build_elnicho,
    "anavilhanas": build_anavilhanas,
    "chapada": build_chapada,
}

CONTAINER_RE = r'(<div[^>]*\bdata-nature-svg="{key}"[^>]*>\s*)<svg\b.*?</svg>(\s*</div>)'


def validate(svg: str, key: str) -> None:
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        sys.exit(f"Error: generated SVG '{key}' is invalid XML: {exc}")


def inline(svg: str) -> str:
    return re.sub(r'\s+xmlns="http://www\.w3\.org/2000/svg"', "", svg, count=1)


def update_pages(rendered: dict[str, dict[str, str]]) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_pages import format_and_remove_empty_lines

    for lang in ("en", "hu"):
        path = ROOT / lang / "nature.html"
        text = path.read_text(encoding="utf-8")
        for key, svg in rendered[lang].items():
            pattern = re.compile(CONTAINER_RE.format(key=key), re.S)
            match = pattern.search(text)
            if not match:
                print(f"  ! no data-nature-svg=\"{key}\" container in {path.relative_to(ROOT)}")
                continue
            text = text[: match.start()] + match.group(1) + inline(svg) + match.group(2) + text[match.end():]
        path.write_text(format_and_remove_empty_lines(text), encoding="utf-8")
        print(f"Updated {path.relative_to(ROOT)}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rendered: dict[str, dict[str, str]] = {"en": {}, "hu": {}}
    for key, builder in BUILDERS.items():
        for lang in ("en", "hu"):
            svg = builder(LABELS[lang])
            validate(svg, key)
            rendered[lang][key] = svg
        out = OUT_DIR / f"{key}.svg"
        out.write_text(rendered["en"][key] + "\n", encoding="utf-8")
        print(f"Generated {out.relative_to(ROOT)} ({len(rendered['en'][key]) / 1024:.1f} KB)")
    if "--no-inject" not in sys.argv:
        update_pages(rendered)


if __name__ == "__main__":
    main()
