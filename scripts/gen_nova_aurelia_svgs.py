#!/usr/bin/env python3
"""
Procedural generator for the Nova Aurelia imperial metropolis illustrations.

Generates standalone SVG files in icons/nova-aurelia/ and injects localized inline
SVGs into en/nova-aurelia.html and hu/nova-aurelia.html. Every illustration container
in the pages is marked with data-city-svg="KEY"; the <svg> inside it is replaced.
"""

from __future__ import annotations

import html
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gen_nature_svgs as NT  # noqa: E402
from gen_nature_svgs import (  # noqa: E402
    P, bird_v, branch_coral, brain_coral, cloud, el, g, manta, mix, n, palm, school,
    sea_fan, seagrass, smooth, tube_sponge, turtle, water_lines,
)

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "icons" / "nova-aurelia"
TAU = math.tau


class Scene(NT.Scene):
    """Nature scene builder with a city id prefix and city illustration class."""

    def id(self, name: str) -> str:
        return f"na-{self.key}-{name}"

    def raw(self, markup: str) -> None:
        self.defs.append(markup)

    def render(self, label: str) -> str:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" class="city-ill" viewBox="0 0 {self.w} {self.h}" '
            f'role="img" aria-label="{html.escape(label, quote=True)}">'
        )
        return "\n".join([head, "<defs>", *self.defs, "</defs>", *self.body, "</svg>"])


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def line(a, b) -> str:
    return f"M{n(a[0])},{n(a[1])} L{n(b[0])},{n(b[1])}"


def ripple(s: Scene, name: str, fx=0.004, fy=0.09, scale=9, seed=4) -> str:
    s.raw(
        f'<filter id="{s.id(name)}" x="-3%" y="-3%" width="106%" height="106%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="{fx} {fy}" numOctaves="2" seed="{seed}" result="t"/>'
        f'<feDisplacementMap in="SourceGraphic" in2="t" scale="{scale}" xChannelSelector="R" yChannelSelector="G"/>'
        f'</filter>'
    )
    return s.url(name)


def glow(s: Scene, name: str, sd: float) -> str:
    s.raw(
        f'<filter id="{s.id(name)}" x="-60%" y="-60%" width="220%" height="220%">'
        f'<feGaussianBlur stdDeviation="{sd}" result="b"/>'
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    )
    return s.url(name)


def caustics(s: Scene, name: str, freq="0.018 0.045") -> str:
    s.raw(
        f'<filter id="{s.id(name)}" x="0" y="0" width="100%" height="100%">'
        f'<feTurbulence type="turbulence" baseFrequency="{freq}" numOctaves="2" seed="11"/>'
        f'<feColorMatrix type="matrix" values="0 0 0 0 0.85  0 0 0 0 1  0 0 0 0 1  -5 0 0 0 1.15"/>'
        f'</filter>'
    )
    return s.url(name)


def fade_mask(s: Scene, name: str, x, y, w, h, top=0.6, bottom=0.0) -> str:
    grad = s.linear(name + "-g", [(0, "#ffffff", top), (1, "#ffffff", bottom)])
    s.raw(
        f'<mask id="{s.id(name)}" maskUnits="userSpaceOnUse" x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}">'
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="{grad}"/></mask>'
    )
    return s.url(name)


def reflection(s: Scene, src: str, axis: float, mask=None, filt=None, op=1.0, clip=None) -> str:
    use = el("use", href=f"#{s.id(src)}", transform=f"matrix(1 0 0 -1 0 {n(2 * axis)})")
    return g(use, mask=mask, filter=filt, opacity=op, clip_path=clip)


PATS = {
    "curtain": (5, 6, 0.9, 1.3, 3.4, 3.9),
    "punched": (7, 8, 1.6, 2.0, 3.8, 4.4),
    "ribbon": (9, 7, 0.4, 2.4, 8.2, 2.8),
}


def patterns(s: Scene, col="#0a1424") -> None:
    s.raw(
        f'<pattern id="{s.id("pat-curtain")}" width="5" height="6" patternUnits="userSpaceOnUse">'
        f'<path d="M0,0.6H5" stroke="{col}" stroke-width="1.2" opacity="0.75"/>'
        f'<path d="M0.4,0V6" stroke="{col}" stroke-width="0.7" opacity="0.5"/></pattern>'
    )
    s.raw(
        f'<pattern id="{s.id("pat-punched")}" width="7" height="8" patternUnits="userSpaceOnUse">'
        f'<rect x="1.6" y="2" width="3.8" height="4.4" fill="{col}" opacity="0.72"/>'
        f'<path d="M0,7.6H7" stroke="{col}" stroke-width="0.5" opacity="0.4"/></pattern>'
    )
    s.raw(
        f'<pattern id="{s.id("pat-ribbon")}" width="9" height="7" patternUnits="userSpaceOnUse">'
        f'<rect x="0" y="2.4" width="9" height="2.8" fill="{col}" opacity="0.7"/>'
        f'<path d="M4.5,2.4v2.8" stroke="#ffffff" stroke-width="0.4" opacity="0.25"/></pattern>'
    )


def lit_windows(rng, x0, y0, x1, y1, pat, prob, col="#ffd68a", op=0.9) -> str:
    cw, ch, ox, oy, ww, wh = PATS[pat]
    c0, c1 = math.ceil((x0 - ox) / cw), math.floor((x1 - ww - ox) / cw)
    r0, r1 = math.ceil((y0 - oy) / ch), math.floor((y1 - wh - oy) / ch)
    cmds = []
    for r in range(r0, r1 + 1):
        row_p = prob * rng.uniform(0.2, 1.8)
        for c in range(c0, c1 + 1):
            if rng.random() < row_p:
                cmds.append(f"M{n(c * cw + ox)},{n(r * ch + oy)}h{n(ww)}v{n(wh)}h{n(-ww)}Z")
    return el("path", d="".join(cmds), fill=col, opacity=op) if cmds else ""


def glass_gradients(s: Scene, face, side, far=None) -> None:
    s.linear("glass-face", face)
    s.linear("glass-side", side)
    if far:
        s.linear("glass-far", far)


def crown(s: Scene, kind, x, top, w, d, face, side, beacon=True, metal="#c9d2dc"):
    W = w + d
    cx = x + W / 2
    out = []
    if kind == "flat":
        out += [
            el("rect", x=x - 0.8, y=top - 2.2, width=W + 1.6, height=2.6, fill="#1a2433"),
            el("rect", x=x + W * 0.18, y=top - 7.5, width=W * 0.36, height=5.4, fill="#2a374a"),
            el("rect", x=x + W * 0.6, y=top - 5, width=W * 0.22, height=2.9, fill="#344458"),
            el("line", x1=x + W * 0.72, y1=top - 2, x2=x + W * 0.72, y2=top - 16, stroke=metal, stroke_width=0.8),
        ]
        if beacon:
            out.append(el("circle", cx=x + W * 0.72, cy=top - 16, r=1.4, fill="#ff4040", class_="city-anim-beacon"))
    elif kind == "spire":
        sh = max(18, w * 1.5)
        out += [
            el("path", d=P([(x, top), (x + w, top), (x + w * 0.62, top - sh * 0.22), (x + w * 0.38, top - sh * 0.22)]), fill=face),
            el("path", d=P([(x + w, top), (x + W, top), (x + w * 0.62, top - sh * 0.22)]), fill=side),
            el("path", d=P([(cx - 1.4, top - sh * 0.2), (cx + 1.4, top - sh * 0.2), (cx + 0.4, top - sh), (cx - 0.4, top - sh)]), fill=metal),
        ]
        if beacon:
            out.append(el("circle", cx=cx, cy=top - sh, r=1.5, fill="#ff4040", class_="city-anim-beacon"))
    elif kind == "slant":
        rise = W * 0.7
        ys = top - rise * w / W
        out += [
            el("path", d=P([(x, top), (x + w, top), (x + w, ys)]), fill=face),
            el("path", d=P([(x + w, top), (x + W, top), (x + W, top - rise), (x + w, ys)]), fill=side),
            el("path", d=P([(x, top), (x + w, ys), (x + W, top - rise)], close=False), stroke="#ffe9c4", stroke_width=0.9, fill="none", opacity=0.8),
        ]
    elif kind == "diamond":
        hgt = W * 1.05
        out += [
            el("path", d=P([(x, top), (x + w, top), (x + w * 0.78, top - hgt)]), fill=face),
            el("path", d=P([(x + w, top), (x + W, top), (x + w * 0.78, top - hgt)]), fill=side),
            el("line", x1=x + w * 0.78, y1=top - hgt, x2=x + w * 0.78, y2=top - hgt - 14, stroke=metal, stroke_width=0.9),
        ]
        if beacon:
            out.append(el("circle", cx=x + w * 0.78, cy=top - hgt - 14, r=1.4, fill="#ff4040", class_="city-anim-beacon"))
    elif kind == "helipad":
        out += [
            el("rect", x=x + W * 0.1, y=top - 4, width=W * 0.8, height=4, fill="#243246"),
            el("ellipse", cx=cx, cy=top - 4.5, rx=W * 0.55, ry=1.8, fill="#3a4a5e"),
            el("ellipse", cx=cx, cy=top - 4.6, rx=W * 0.3, ry=0.9, fill="none", stroke="#f3d36b", stroke_width=0.5),
        ]
    elif kind == "stepped":
        out += [
            el("rect", x=x + W * 0.1, y=top - 8, width=W * 0.8, height=8, fill=face),
            el("rect", x=x + W * 0.25, y=top - 14, width=W * 0.5, height=6, fill=face),
            el("rect", x=x + W * 0.1, y=top - 8.6, width=W * 0.8, height=0.9, fill="#ffe2a0", opacity=0.9),
            el("line", x1=cx, y1=top - 14, x2=cx, y2=top - 26, stroke=metal, stroke_width=0.8),
        ]
    elif kind == "garden":
        out.append(el("rect", x=x - 0.6, y=top - 2, width=W + 1.2, height=2.2, fill="#2a3a2c"))
        for i in range(max(3, int(W / 5))):
            tx = x + 2 + i * (W - 4) / max(1, int(W / 5) - 1)
            r = 2.4 + (i % 3) * 0.7
            out += [el("circle", cx=tx, cy=top - 2 - r * 0.6, r=r, fill="#2e6a34"),
                    el("circle", cx=tx - r * 0.25, cy=top - 2 - r * 0.85, r=r * 0.6, fill="#5c9f4a")]
    return out


def tower(s: Scene, x, base, w, h, d=8, pat="curtain", lit=0.08, crown_kind="flat", beacon=True,
          face=None, side=None, lit_col="#ffd68a", glint=True, pat_op=0.5):
    rng = s.rng
    face = face or s.url("glass-face")
    side = side or s.url("glass-side")
    top = base - h
    out = [
        el("rect", x=x, y=top, width=w, height=h, fill=face),
        el("rect", x=x + w, y=top, width=d, height=h, fill=side) if d else "",
        el("rect", x=x, y=top, width=w + d, height=h, fill=s.url(f"pat-{pat}"), opacity=pat_op),
        lit_windows(rng, x + 1, top + 3, x + w + d - 1, base - 2, pat, lit, lit_col),
        el("line", x1=x + 0.4, y1=top, x2=x + 0.4, y2=base, stroke="#fff4dc", stroke_width=0.8, opacity=0.45),
    ]
    if glint:
        gx = x + w * rng.uniform(0.15, 0.5)
        out.append(el("path", d=P([(gx, top), (gx + w * 0.22, top), (gx + w * 0.02, base), (gx - w * 0.2, base)]),
                      fill="#ffffff", opacity=0.07))
    for k in range(1, int(h / 70) + 1):
        by = base - k * 70
        if by > top + 6:
            out.append(el("rect", x=x, y=by, width=w + d, height=1.6, fill="#0d1726", opacity=0.55))
    out += crown(s, crown_kind, x, top, w, d, face, side, beacon)
    return g(out)


def far_city(rng, x0, x1, base, hmin, hmax, col, wmin=8, wmax=24, lights=0, light_col="#ffd9a0"):
    cmds, dots = [], []
    x = x0
    while x < x1:
        w = rng.uniform(wmin, wmax)
        h = hmin + (hmax - hmin) * rng.random() ** 1.6
        cmds.append(f"M{n(x)},{n(base)}V{n(base - h)}H{n(x + w)}V{n(base)}Z")
        roll = rng.random()
        if roll < 0.25:
            cmds.append(f"M{n(x + w * 0.2)},{n(base - h)}V{n(base - h - h * 0.12)}H{n(x + w * 0.8)}V{n(base - h)}Z")
        elif roll < 0.35:
            cmds.append(f"M{n(x + w * 0.45)},{n(base - h)}V{n(base - h - h * 0.35)}H{n(x + w * 0.55)}V{n(base - h)}Z")
        for _ in range(int(lights * w * h / 400)):
            dots.append(f"M{n(x + rng.uniform(1, w - 2))},{n(base - rng.uniform(2, h - 2))}h1.3v1.1h-1.3Z")
        x += w * rng.uniform(0.55, 1.0)
    out = [el("path", d="".join(cmds), fill=col)]
    if dots:
        out.append(el("path", d="".join(dots), fill=light_col, opacity=0.75))
    return g(out)


def twisted_tower(s: Scene, cx, base, r, h, twist=math.pi / 2, floors=60, light=0.6,
                  cols=("#f6d8ae", "#8796b0", "#26344c"), lit=0.12, crown_h=24):
    rng = s.rng
    polys, floor_lines, lamps = [], [], []

    def corners(th):
        return [cx + r * math.cos(th + math.pi / 4 + k * math.pi / 2) for k in range(4)]

    for i in range(floors):
        y0 = base - h * i / floors
        y1 = base - h * (i + 1) / floors
        t0, t1 = twist * i / floors, twist * (i + 1) / floors
        c0, c1 = corners(t0), corners(t1)
        xs = []
        for k in range(4):
            nrm = t0 + math.pi / 2 + k * math.pi / 2
            if math.sin(nrm) <= 0.01:
                continue
            b = 0.5 + 0.5 * math.cos(nrm - light)
            col = mix(cols[2], cols[1], b / 0.6) if b < 0.6 else mix(cols[1], cols[0], (b - 0.6) / 0.4)
            k2 = (k + 1) % 4
            poly = [(c0[k], y0), (c0[k2], y0), (c1[k2], y1), (c1[k], y1)]
            polys.append(el("path", d=P(poly), fill=col, stroke=col, stroke_width=0.5))
            xs += [c0[k], c0[k2]]
            if rng.random() < lit * 3:
                a, b2 = sorted((c0[k], c0[k2]))
                for _ in range(rng.randint(1, 3)):
                    wx = rng.uniform(a + 1, max(a + 1.5, b2 - 3))
                    lamps.append(f"M{n(wx)},{n(y1 + 1)}h2.2v{n(max(1.2, (y0 - y1) - 2))}h-2.2Z")
        if xs:
            floor_lines.append(f"M{n(min(xs))},{n(y0)}H{n(max(xs))}")
    top_y = base - h
    return g([
        g(polys),
        el("path", d="".join(floor_lines), stroke="#0b1424", stroke_width=0.6, opacity=0.45),
        el("path", d="".join(lamps), fill="#ffd68a", opacity=0.85) if lamps else "",
        el("path", d=P([(cx - r * 0.5, top_y), (cx + r * 0.5, top_y), (cx + 1, top_y - crown_h), (cx - 1, top_y - crown_h)]), fill=cols[1]),
        el("line", x1=cx, y1=top_y - crown_h, x2=cx, y2=top_y - crown_h - 10, stroke="#c9d2dc", stroke_width=0.8),
        el("circle", cx=cx, cy=top_y - crown_h - 10, r=1.4, fill="#ff4040", class_="city-anim-beacon"),
    ])


def sky_city(s: Scene, cx, base, top, face=None, side=None):
    rng = s.rng
    face = face or s.url("glass-face")
    side = side or s.url("glass-side")
    H = base - top
    tiers = [(0.0, 0.3, 46), (0.3, 0.52, 37), (0.52, 0.68, 29), (0.68, 0.8, 21), (0.8, 0.88, 13), (0.88, 0.92, 7)]
    out = []
    for f0, f1, hw in tiers:
        y0, y1 = base - H * f0, base - H * f1
        split = cx + hw * 0.3
        out += [
            el("rect", x=cx - hw, y=y1, width=split - (cx - hw), height=y0 - y1, fill=face),
            el("rect", x=split, y=y1, width=cx + hw - split, height=y0 - y1, fill=side),
            el("rect", x=cx - hw, y=y1, width=hw * 2, height=y0 - y1, fill=s.url("pat-curtain"), opacity=0.45),
            lit_windows(rng, cx - hw + 1, y1 + 3, cx + hw - 1, y0 - 2, "curtain", 0.05),
            el("rect", x=cx - hw - 1.5, y=y1 - 1.2, width=hw * 2 + 3, height=2.4, fill="#e9eef4"),
            el("rect", x=cx - hw - 1.5, y=y1 + 1.2, width=hw * 2 + 3, height=1.2, fill="#0d1726", opacity=0.5),
            el("path", d="".join(f"M{n(cx - hw + k * hw / 3)},{n(y1)}V{n(y0)}" for k in range(1, 6)),
               stroke="#f4f7fb", stroke_width=0.7, opacity=0.35),
        ]
    spire_base = base - H * 0.92
    out += [
        el("path", d=P([(cx - 4, spire_base), (cx + 4, spire_base), (cx + 0.6, top), (cx - 0.6, top)]), fill="#dfe6ee"),
        el("path", d=P([(cx, spire_base), (cx + 4, spire_base), (cx + 0.6, top), (cx, top)]), fill="#8a97a8"),
        el("line", x1=cx - 0.6, y1=base, x2=cx - 0.6, y2=spire_base, stroke="#bff6ff", stroke_width=1.4, opacity=0.7),
        el("ellipse", cx=cx, cy=base - H * 0.74, rx=24, ry=2.2, fill="#ffe7a6", opacity=0.9),
        el("circle", cx=cx, cy=top, r=1.8, fill="#ff4040", class_="city-anim-beacon"),
    ]
    return g(out)



def clock_tower(s: Scene, cx, base, h):
    stone = s.linear("ct-stone", [(0, "#f2dfbb"), (0.7, "#d9bd8e"), (1, "#b8976a")], x1=0, y1=0, x2=1, y2=0)
    gold = s.linear("ct-gold", [(0, "#fff1b8"), (0.45, "#e5b443"), (1, "#8f6316")], x1=0, y1=0, x2=1, y2=0)
    w = h * 0.19
    x0 = cx - w / 2
    shaft_top = base - h * 0.56
    out = [
        el("rect", x=x0 - w * 0.12, y=base - h * 0.08, width=w * 1.24, height=h * 0.08, fill=stone),
        el("rect", x=x0, y=shaft_top, width=w, height=base - shaft_top, fill=stone),
        el("rect", x=x0 + w * 0.66, y=shaft_top, width=w * 0.34, height=base - shaft_top, fill="#6b4c2c", opacity=0.28),
        el("path", d="".join(f"M{n(x0)},{n(y)}H{n(x0 + w)}" for y in [base - k * h * 0.028 for k in range(3, 20)]),
           stroke="#8f704a", stroke_width=0.35, opacity=0.5),
        el("rect", x=x0, y=shaft_top, width=w * 0.12, height=base - shaft_top, fill="#fff6e2", opacity=0.45),
        el("rect", x=x0 + w * 0.88, y=shaft_top, width=w * 0.12, height=base - shaft_top, fill="#5a3e22", opacity=0.3),
    ]
    for k in range(3):
        wy = shaft_top + h * 0.08 + k * h * 0.14
        ww, wh = w * 0.26, h * 0.08
        out.append(el("path", d=f"M{n(cx - ww / 2)},{n(wy + wh)}V{n(wy + ww / 2)}A{n(ww / 2)},{n(ww / 2)} 0 0 1 {n(cx + ww / 2)},{n(wy + ww / 2)}V{n(wy + wh)}Z",
                      fill="#3a2a1c"))
        out.append(el("rect", x=cx - ww / 2, y=wy + wh * 0.55, width=ww, height=wh * 0.45, fill="#ffcf7a", opacity=0.55))
    cs_h = w * 1.15
    cs_top = shaft_top - cs_h
    cy = cs_top + cs_h / 2
    ticks = [f"M{n(cx + math.cos(TAU * k / 12) * w * 0.27)},{n(cy + math.sin(TAU * k / 12) * w * 0.27)}"
             f"L{n(cx + math.cos(TAU * k / 12) * w * 0.32)},{n(cy + math.sin(TAU * k / 12) * w * 0.32)}" for k in range(12)]
    bel_top = cs_top - w * 0.75
    dome_r = w * 0.48
    out += [
        el("rect", x=x0 - w * 0.12, y=shaft_top - 2, width=w * 1.24, height=3.2, fill="#efe1c4"),
        el("rect", x=x0 - w * 0.04, y=cs_top, width=w * 1.08, height=cs_h, fill=stone),
        el("rect", x=x0 + w * 0.7, y=cs_top, width=w * 0.34, height=cs_h, fill="#6b4c2c", opacity=0.25),
        el("circle", cx=cx, cy=cy, r=w * 0.4, fill=gold),
        el("circle", cx=cx, cy=cy, r=w * 0.34, fill="#fff8e4"),
        el("path", d="".join(ticks), stroke="#3a2a1c", stroke_width=0.6),
        el("path", d=f"M{n(cx)},{n(cy)}L{n(cx + w * 0.16)},{n(cy - w * 0.12)}M{n(cx)},{n(cy)}L{n(cx - w * 0.04)},{n(cy - w * 0.26)}",
           stroke="#1a120a", stroke_width=0.9, stroke_linecap="round"),
        el("rect", x=x0 - w * 0.1, y=cs_top - 2, width=w * 1.2, height=2.6, fill="#efe1c4"),
        el("rect", x=x0 + w * 0.08, y=bel_top, width=w * 0.84, height=w * 0.75, fill=stone),
        el("path", d=f"M{n(cx - dome_r)},{n(bel_top)}A{n(dome_r)},{n(dome_r * 1.15)} 0 0 1 {n(cx + dome_r)},{n(bel_top)}Z", fill=gold),
        el("rect", x=cx - w * 0.08, y=bel_top - dome_r * 1.15 - w * 0.22, width=w * 0.16, height=w * 0.22, fill=gold),
        el("line", x1=cx, y1=bel_top - dome_r * 1.15 - w * 0.22, x2=cx, y2=bel_top - dome_r * 1.15 - w * 0.6, stroke="#e5b443", stroke_width=0.8),
        el("circle", cx=cx, cy=bel_top - dome_r * 1.15 - w * 0.6, r=1.2, fill="#fff1b8"),
    ]
    return g(out)


def pyramid(s: Scene, apex, L, F, R, tiers=6, cap=0.12, scale=1.0, cutaway=None, waterfall_u=None, lights=False):
    rng = s.rng
    stone = s.linear("pyr-stone", [(0, "#f7e8c8"), (0.55, "#e4c894"), (1, "#c79d64")])
    glass = s.linear("pyr-glass", [(0, "#1d3f63"), (0.5, "#365f8a"), (0.85, "#7fa6c8"), (1, "#c9b79a")])
    gold = s.linear("pyr-gold", [(0, "#fff4c8"), (0.5, "#ecbc4c"), (1, "#a8741c")], x1=0, y1=0, x2=1, y2=1)
    water = s.linear("pyr-water", [(0, "#d9f4ff"), (1, "#5fc0e6")])

    def pl(t, u):
        return lerp(lerp(apex, L, t), lerp(apex, F, t), u)

    def pr(t, u):
        return lerp(lerp(apex, F, t), lerp(apex, R, t), u)

    def tier_t(i):
        return cap + (1 - cap) * i / (tiers + 0.3)

    out = [el("path", d=P([apex, L, F]), fill=stone), el("path", d=P([apex, F, R]), fill=glass)]
    nc = int(42 * scale) + 8
    courses = [line(pl(cap + (1 - cap) * i / nc, 0), pl(cap + (1 - cap) * i / nc, 1)) for i in range(1, nc)]
    grid = [line(pr(cap + (1 - cap) * i / nc, 0), pr(cap + (1 - cap) * i / nc, 1)) for i in range(1, nc)]
    m = int(28 * scale) + 6
    grid += [line(pr(cap, j / m), pr(1, j / m)) for j in range(1, m)]
    out += [
        el("path", d=" ".join(courses), stroke="#8a6a3e", stroke_width=0.25 + 0.35 * scale, opacity=0.38, fill="none"),
        el("path", d=" ".join(grid), stroke="#cfe6f8", stroke_width=0.15 + 0.35 * scale, opacity=0.4, fill="none"),
        el("path", d=P([pr(0.25, 0.05), pr(0.25, 0.28), pr(1, 0.62), pr(1, 0.34)]), fill="#ffffff", opacity=0.11),
        el("path", d=P([pl(0.2, 0.0), pl(0.2, 0.3), pl(1, 0.15), pl(1, 0.0)]), fill="#fff8ea", opacity=0.18),
    ]
    if lights:
        out.append(lit_windows(rng, min(F[0], R[0]), apex[1] + 20, max(F[0], R[0]), max(F[1], R[1]), "punched", 0.04))

    greens = ["#24552a", "#3a7f39", "#57a248", "#86c463"]
    for i in range(1, tiers + 1):
        t = tier_t(i)
        dt = 0.014 + 0.004 * scale
        out += [
            el("path", d=P([pl(t, 0), pl(t, 1), pl(t + dt, 1), pl(t + dt, 0)]), fill="#5e4122", opacity=0.5),
            el("path", d=line(pl(t, 0), pl(t, 1)), stroke="#fff6dc", stroke_width=0.5 + 0.8 * scale, opacity=0.85),
            el("path", d=P([pr(t, 0), pr(t, 1), pr(t + dt, 1), pr(t + dt, 0)]), fill="#0a1a2c", opacity=0.55),
            el("path", d=line(pr(t, 0), pr(t, 1)), stroke="#e3f2ff", stroke_width=0.4 + 0.6 * scale, opacity=0.8),
        ]
        foliage, vines = [], []
        k = int(32 * scale * t) + 4
        for j in range(k):
            u = (j + rng.uniform(0.1, 0.9)) / k
            if waterfall_u is not None and abs(u - waterfall_u) < 0.04:
                continue
            if cutaway and cutaway[0] - 0.02 <= t <= cutaway[1] and cutaway[2] <= u <= cutaway[3]:
                continue
            px, py = pl(t, u)
            r = (1.6 + 3.6 * t) * scale * rng.uniform(0.7, 1.3)
            foliage.append((px, py - r * 0.35, r))
            if rng.random() < 0.65:
                vines.append(f"M{n(px)},{n(py)} q{n(rng.uniform(-1, 1))},{n(r * 1.6)} {n(rng.uniform(-1.5, 1.5))},{n(r * rng.uniform(2, 4.2))}")
        out.append(el("path", d=" ".join(vines), stroke="#3c7a36", stroke_width=0.4 + 0.7 * scale, fill="none", opacity=0.85))
        for gi, col in enumerate(greens):
            out.append(g([el("circle", cx=px - gi * r * 0.16, cy=py - gi * r * 0.2, r=r * (1 - 0.2 * gi)) for px, py, r in foliage], fill=col))

    if waterfall_u is not None:
        for i in range(tiers + 1):
            t0 = tier_t(i) + 0.02
            t1 = tier_t(i + 1) if i < tiers else 1.0
            wdt = 0.012 + 0.012 * t0
            sheet = [pl(t0, waterfall_u - wdt), pl(t0, waterfall_u + wdt), pl(t1, waterfall_u + wdt * 1.15), pl(t1, waterfall_u - wdt * 1.15)]
            streaks = [line(pl(t0, waterfall_u + wdt * f), pl(t1, waterfall_u + wdt * f * 1.1)) for f in (-0.5, 0.0, 0.5)]
            bx, by = pl(t1, waterfall_u)
            out += [
                el("path", d=P(sheet), fill=water, opacity=0.9),
                el("path", d=" ".join(streaks), stroke="#ffffff", stroke_width=0.4 + 0.5 * scale, opacity=0.85, class_="flow", fill="none"),
                el("ellipse", cx=bx, cy=by - 1, rx=(4 + 6 * t1) * scale, ry=(1.2 + 1.6 * t1) * scale, fill="#ffffff", opacity=0.9),
            ]

    if cutaway:
        t0, t1, u0, u1 = cutaway
        frame = [pl(t0, u0), pl(t0, u1), pl(t1, u1), pl(t1, u0)]
        inner = s.linear("pyr-inner", [(0, "#3a2a1a"), (1, "#120c08")])
        c = lerp(pl(t1, u0), pl(t1, u1), 0.5)
        span = abs(pl(t1, u1)[0] - pl(t1, u0)[0]) * 0.46
        depth_h = abs(c[1] - lerp(pl(t0, u0), pl(t0, u1), 0.5)[1])
        seats = [f"M{n(c[0] - span * k / 7.5)},{n(c[1] - 4)} A{n(span * k / 7.5)},{n(min(depth_h * 0.8, span * k / 7.5 * 0.45))} 0 0 1 {n(c[0] + span * k / 7.5)},{n(c[1] - 4)}"
                 for k in range(1, 8)]
        clip = s.clip("cut", P(frame))
        out += [
            el("path", d=P(frame), fill=inner),
            g([
                el("path", d=" ".join(seats), stroke="#b8894a", stroke_width=2.6, fill="none", opacity=0.9),
                el("path", d=" ".join(seats), stroke="#e9c27a", stroke_width=0.6, fill="none"),
                el("ellipse", cx=c[0], cy=c[1] - 5, rx=8, ry=2.6, fill="#ffd86b"),
                el("ellipse", cx=c[0], cy=c[1] - 5, rx=30, ry=9, fill=s.radial("dais", [(0, "#ffe9a8", 0.7), (1, "#ffe9a8", 0)])),
            ], clip_path=clip),
            el("path", d=P(frame), fill="none", stroke="#e8b54a", stroke_width=1.6),
        ]

    out += [
        el("path", d=P([apex, pl(cap, 0), pl(cap, 1)]), fill=gold),
        el("path", d=P([apex, pr(cap, 0), pr(cap, 1)]), fill="#9c6c1e"),
        el("path", d=P([apex, pr(cap, 0), pr(cap, 0.45)]), fill="#ffe7a0", opacity=0.35),
        el("path", d=line(apex, F), stroke="#fff8e6", stroke_width=0.6 + 0.8 * scale, opacity=0.7),
    ]
    return out


def person(x, y, h, col="#1c2533", rng=None):
    sway = rng.uniform(-0.12, 0.12) * h if rng else 0
    hr = h * 0.12
    return g([
        el("circle", cx=x, cy=y - h + hr, r=hr),
        el("path", d=f"M{n(x - h * 0.13)},{n(y - h * 0.45)} L{n(x - h * 0.12)},{n(y - h * 0.74)} Q{n(x)},{n(y - h * 0.82)} {n(x + h * 0.12)},{n(y - h * 0.74)} L{n(x + h * 0.13)},{n(y - h * 0.45)}Z"),
        el("path", d=f"M{n(x - h * 0.06)},{n(y - h * 0.46)} L{n(x - h * 0.08 + sway)},{n(y)} M{n(x + h * 0.06)},{n(y - h * 0.46)} L{n(x + h * 0.08 - sway)},{n(y)}",
           stroke=col, stroke_width=max(0.5, h * 0.09), stroke_linecap="round"),
    ], fill=col)


def crowd(rng, x0, x1, y0, y1, count, h, cols=("#1c2533", "#5b3a2e", "#2f4a6b", "#7a2f3a", "#e8e2d6")):
    people = []
    for _ in range(count):
        y = rng.uniform(y0, y1)
        sc = 0.7 + 0.3 * (y - y0) / max(1, y1 - y0)
        people.append((y, person(rng.uniform(x0, x1), y, h * sc * rng.uniform(0.9, 1.1), rng.choice(cols), rng)))
    return g([p for _, p in sorted(people)])


def lamp_post(x, y, h, glow_fill=None, col="#2a3340"):
    out = [
        el("line", x1=x, y1=y, x2=x, y2=y - h, stroke=col, stroke_width=max(0.8, h * 0.05)),
        el("path", d=f"M{n(x)},{n(y - h)} q{n(h * 0.12)},{n(-h * 0.08)} {n(h * 0.24)},0", stroke=col, stroke_width=max(0.6, h * 0.035), fill="none"),
        el("rect", x=x + h * 0.18, y=y - h, width=h * 0.12, height=h * 0.05, fill="#fff1c4"),
    ]
    if glow_fill:
        out.insert(0, el("circle", cx=x + h * 0.24, cy=y - h + h * 0.03, r=h * 0.35, fill=glow_fill))
    return g(out)


def superyacht(x, y, L, flip=False, hull="#f7f8fa", glass="#16222f", accent="#c9a24e"):
    sx = -1 if flip else 1
    u = L
    return g([
        el("path", d=f"M{n(-0.5 * u)},{n(-0.035 * u)} L{n(0.36 * u)},{n(-0.035 * u)} Q{n(0.47 * u)},{n(-0.06 * u)} {n(0.53 * u)},{n(-0.13 * u)} "
                     f"L{n(-0.47 * u)},{n(-0.11 * u)} Q{n(-0.52 * u)},{n(-0.08 * u)} {n(-0.5 * u)},{n(-0.035 * u)}Z", fill=hull),
        el("path", d=f"M{n(-0.5 * u)},{n(-0.035 * u)} L{n(0.36 * u)},{n(-0.035 * u)} Q{n(0.43 * u)},{n(-0.045 * u)} {n(0.46 * u)},{n(-0.06 * u)} L{n(-0.5 * u)},{n(-0.055 * u)}Z", fill="#1b2633"),
        el("path", d=f"M{n(-0.5 * u)},{n(-0.08 * u)} L{n(0.48 * u)},{n(-0.095 * u)}", stroke=accent, stroke_width=max(0.4, u * 0.006)),
        el("path", d=P([(-0.44 * u, -0.11 * u), (0.3 * u, -0.115 * u), (0.22 * u, -0.17 * u), (-0.4 * u, -0.17 * u)]), fill=hull),
        el("path", d=P([(-0.38 * u, -0.128 * u), (0.24 * u, -0.13 * u), (0.2 * u, -0.155 * u), (-0.38 * u, -0.155 * u)]), fill=glass),
        el("path", d=P([(-0.34 * u, -0.17 * u), (0.16 * u, -0.17 * u), (0.08 * u, -0.22 * u), (-0.32 * u, -0.22 * u)]), fill=hull),
        el("path", d=P([(-0.3 * u, -0.183 * u), (0.11 * u, -0.183 * u), (0.07 * u, -0.207 * u), (-0.3 * u, -0.207 * u)]), fill=glass),
        el("path", d=P([(-0.2 * u, -0.22 * u), (0.04 * u, -0.22 * u), (-0.02 * u, -0.26 * u), (-0.19 * u, -0.26 * u)]), fill=hull),
        el("path", d=f"M{n(-0.16 * u)},{n(-0.26 * u)} Q{n(-0.1 * u)},{n(-0.33 * u)} {n(-0.04 * u)},{n(-0.26 * u)}", stroke=hull, stroke_width=max(0.8, u * 0.02), fill="none"),
        el("circle", cx=-0.1 * u, cy=-0.31 * u, r=max(0.6, u * 0.012), fill="#ffffff"),
    ], transform=f"translate({n(x)} {n(y)}) scale({sx} 1)")


def sailboat(x, y, s, flip=False, sail="#fbfbf8", hull="#f2f4f6"):
    sx = -1 if flip else 1
    return g([
        el("path", d=f"M{n(-s * 0.5)},{n(-s * 0.04)} L{n(s * 0.45)},{n(-s * 0.04)} L{n(s * 0.55)},{n(-s * 0.13)} L{n(-s * 0.52)},{n(-s * 0.12)}Z", fill=hull),
        el("line", x1=0, y1=-s * 0.12, x2=0, y2=-s * 1.25, stroke="#5a6470", stroke_width=max(0.5, s * 0.015)),
        el("path", d=f"M{n(-s * 0.02)},{n(-s * 1.2)} Q{n(-s * 0.32)},{n(-s * 0.7)} {n(-s * 0.4)},{n(-s * 0.18)} L{n(-s * 0.02)},{n(-s * 0.18)}Z", fill=sail),
        el("path", d=f"M{n(s * 0.02)},{n(-s * 1.12)} Q{n(s * 0.26)},{n(-s * 0.62)} {n(s * 0.45)},{n(-s * 0.16)} L{n(s * 0.02)},{n(-s * 0.16)}Z", fill=mix(sail, "#9aa8b8", 0.25)),
    ], transform=f"translate({n(x)} {n(y)}) scale({sx} 1)", class_="bob")


def glitter(rng, cx, y0, y1, spread, count, col="#ffe2a8", w=1.3):
    segs = []
    for _ in range(count):
        y = rng.uniform(y0, y1)
        t = (y - y0) / max(1, y1 - y0)
        L = rng.uniform(3, 22) * (0.4 + t)
        x = cx + rng.gauss(0, spread * (0.25 + t))
        segs.append(f"M{n(x - L / 2)},{n(y)}h{n(L)}")
    return el("path", d="".join(segs), stroke=col, stroke_width=w, opacity=0.85, stroke_linecap="round", class_="shimmer")


def wake(x, y, L, flip=False, op=0.7):
    sx = -1 if flip else 1
    return el("path", d=f"M{n(x - sx * L * 0.5)},{n(y)} q{n(-sx * L * 0.6)},{n(L * 0.04)} {n(-sx * L * 1.4)},{n(L * 0.1)} "
                       f"M{n(x - sx * L * 0.5)},{n(y)} q{n(-sx * L * 0.6)},{n(-L * 0.01)} {n(-sx * L * 1.3)},{n(-L * 0.02)}",
              stroke="#ffffff", stroke_width=1, fill="none", opacity=op)


def callouts(s: Scene, items, accent="#e8b54a", bg="#0d1b2a"):
    return


def vignette_badge(s: Scene, title: str, accent="#e8b54a", bg="#0c192b") -> None:
    return


# ==============================================================================
# 1. SCENE: SKYLINE (Imperial Lagoon Panorama - 1600 x 600)
# ==============================================================================
def build_skyline(t: dict[str, str]) -> str:
    s = Scene("skyline", 1600, 600, 101)
    rng = s.rng
    patterns(s, "#091526")
    glass_gradients(
        s,
        [(0, "#ffe4ba"), (0.35, "#a3c4dc"), (0.7, "#4d789e"), (1, "#1e3a56")],
        [(0, "#3a5c7e"), (0.5, "#1f3854"), (1, "#0f2035")],
        [(0, "#6c5978"), (1, "#2a2740")],
    )
    rip = ripple(s, "rip", fx=0.005, fy=0.085, scale=10)
    rmask = fade_mask(s, "rmask", 0, 412, 1600, 188, top=0.58, bottom=0.05)

    NT.sky(s, [
        (0.0, "#0b162c"),
        (0.26, "#1c2d52"),
        (0.50, "#423a64"),
        (0.68, "#7e485c"),
        (0.84, "#c96f53"),
        (0.95, "#f0a663"),
        (1.0, "#ffe19c"),
    ], h=420)
    NT.sun(s, 1180, 345, 34, glow="#ffd584")

    for cx, cy, cw, col, sh, op in [
        (240, 130, 310, "#f5c29d", "#7a4a5e", 0.55),
        (610, 155, 380, "#fad1a8", "#875162", 0.60),
        (1020, 120, 340, "#ffe4be", "#9e5c58", 0.68),
        (1390, 150, 320, "#ffd9ab", "#8f535a", 0.58),
    ]:
        s.add(cloud(rng, cx, cy, cw, col=col, shade=sh, op=op, cls="city-anim-cloud"))

    NT.mountain(s, "mtn-far", [(-20, 375), (180, 315), (390, 355), (620, 295), (880, 350), (1140, 320), (1380, 360), (1620, 330)],
                412, "#352744", shade="#1d1429", shade_op=0.45, rough=12, depth=5)
    NT.mountain(s, "mtn-mid", [(-20, 390), (130, 350), (310, 372), (510, 340), (760, 380), (1440, 355), (1620, 375)],
                412, "#261d38", shade="#140e22", shade_op=0.5, rough=9, depth=5)

    s.add(el("path", d="M1210,408 Q1380,398 1575,408 L1590,412 L1195,412Z", fill="#1c2235"))
    s.add(el("path", d="M1395,408 V358 L1405,346 L1415,358 V378 H1427 V358 L1437,346 L1447,358 V408 M1415,384 Q1421,374 1427,384Z",
             fill="#252c42", stroke="#e8b464", stroke_width=0.6))
    s.add(lit_windows(rng, 1397, 362, 1445, 405, "curtain", 0.18, "#ffd996"))

    s.add(far_city(rng, 30, 1360, 410, 35, 135, "#23253d", wmin=10, wmax=24, lights=0.35))
    s.add(far_city(rng, 60, 1320, 410, 50, 175, "#192238", wmin=12, wmax=28, lights=0.55))

    city_items = []
    highrises = [
        (55, 145, 26, 7, "curtain", "flat"),
        (92, 185, 30, 8, "punched", "stepped"),
        (134, 160, 24, 7, "ribbon", "slant"),
        (170, 215, 32, 9, "curtain", "spire"),
        (215, 175, 28, 8, "punched", "flat"),
        (256, 240, 34, 9, "curtain", "diamond"),
        (304, 195, 28, 7, "ribbon", "helipad"),
        (344, 165, 26, 7, "curtain", "garden"),
        (560, 190, 26, 7, "curtain", "flat"),
        (782, 225, 28, 8, "punched", "slant"),
        (1002, 195, 26, 7, "curtain", "stepped"),
        (1105, 230, 32, 8, "curtain", "spire"),
        (1150, 185, 28, 7, "ribbon", "flat"),
        (1190, 210, 30, 8, "punched", "diamond"),
        (1232, 165, 26, 7, "curtain", "garden"),
        (1270, 140, 24, 6, "curtain", "flat"),
    ]
    for tx, th, tw, td, pat, ck in highrises:
        city_items.append(tower(s, tx, 410, tw, th, d=td, pat=pat, lit=0.09, crown_kind=ck))

    city_items.extend(pyramid(s, (465, 220), (385, 410), (472, 410), (548, 410), tiers=5, cap=0.14, scale=0.65, waterfall_u=0.52, lights=True))
    city_items.append(el("path", d=P([(462, 220), (468, 220), (478, 80), (452, 80)]),
                         fill=s.linear("pyr-beam", [(0, "#fff4b8", 0.65), (1, "#fff4b8", 0)]), class_="city-anim-beacon"))

    for gx, gh in [(602, 255), (656, 278), (712, 255)]:
        city_items.append(tower(s, gx, 410, 34, gh, d=9, pat="curtain", lit=0.11, crown_kind="garden", beacon=False))
    sb_d = "M592,176 Q674,158 762,176 L756,186 Q674,170 598,186Z"
    city_items.extend([
        el("path", d=sb_d, fill=s.linear("sb-hull", [(0, "#fff2c6"), (0.5, "#d8a43a"), (1, "#7d5614")])),
        el("path", d="M600,174 Q674,158 754,174", stroke="#7ef6ff", stroke_width=2.8, fill="none", opacity=0.9),
        g([el("circle", cx=608 + k * 9, cy=171 - 6 * math.sin(math.pi * k / 15), r=2.6, fill="#2e7d32") for k in range(16)]),
        el("circle", cx=677, cy=122, r=1.6, fill="#ff4040", class_="city-anim-beacon"),
    ])

    city_items.append(sky_city(s, 855, 410, 18))
    city_items.append(twisted_tower(s, 948, 410, 22, 268, twist=math.pi / 2, floors=56, lit=0.1))
    city_items.append(clock_tower(s, 1062, 410, 215))

    for ox, ow, oh in [(772, 22, 28), (786, 26, 34), (802, 22, 26)]:
        city_items.append(el("path", d=f"M{ox},410 Q{ox + ow * 0.35},{410 - oh} {ox + ow},410Z",
                             fill=s.linear("op-shell", [(0, "#fff8eb"), (1, "#c9b393")]), stroke="#8a7356", stroke_width=0.6))

    s.add(g(city_items, id=s.id("skyline-grp")))

    viaduct = [
        el("rect", x=0, y=394, width=1340, height=3.5, fill="#2d425c"),
        el("rect", x=0, y=393.2, width=1340, height=1.0, fill="#ffd996", opacity=0.7),
        el("line", x1=0, y1=395.5, x2=1340, y2=395.5, stroke="#6ff7ff", stroke_width=1.1, opacity=0.8),
    ]
    for px in range(40, 1340, 68):
        viaduct.append(el("path", d=P([(px - 3, 397.5), (px + 3, 397.5), (px + 4.5, 414), (px - 4.5, 414)]), fill="#1e2f44"))
    tx = 520
    viaduct.extend([
        el("path", d=f"M{tx},393 L{tx + 12},388 H{tx + 118} L{tx + 130},393Z", fill="#f6f9fc"),
        el("path", d=f"M{tx + 14},389.5 H{tx + 116}", stroke="#0e2238", stroke_width=2.2),
        el("path", d=f"M{tx + 8},392.2 H{tx + 122}", stroke="#00e5ff", stroke_width=0.9),
    ])
    s.add(g(viaduct))

    s.add(el("rect", x=0, y=408, width=1600, height=7, fill="#2a3342"))
    s.add(el("rect", x=0, y=407, width=1600, height=1.6, fill="#e4c280"))
    lamp_glow = s.radial("lglow", [(0, "#ffe8a6", 0.85), (0.4, "#ffbe5c", 0.35), (1, "#ffbe5c", 0)])
    prom = [lamp_post(lx, 408, 12, glow_fill=lamp_glow) for lx in range(30, 1350, 42)]
    for px in range(48, 1340, 56):
        prom.append(palm(rng, px + rng.uniform(-6, 6), 409, rng.uniform(26, 38), rng.uniform(-5, 5), rng.uniform(14, 19),
                         cols=("#1b4724", "#3c7a38"), nfr=10, royal=True, coconuts=False, sway=False))
    s.add(g(prom))

    s.add(el("rect", x=0, y=414, width=1600, height=186, fill=s.linear("sea", [
        (0.0, "#183958"), (0.22, "#143350"), (0.55, "#0d263e"), (1.0, "#071525"),
    ])))
    s.add(reflection(s, "skyline-grp", 412, mask=rmask, filt=rip, op=0.62))
    s.add(glitter(rng, 1180, 416, 595, 95, 190, col="#ffd88e", w=1.4))
    s.add(glitter(rng, 855, 416, 585, 38, 85, col="#aef4ff", w=1.1))
    s.add(water_lines(rng, 20, 1580, 420, 592, 160, col="#9ed8f5", op=0.28, w=1.0))

    s.add(wake(255, 505, 135, flip=False, op=0.55))
    s.add(superyacht(255, 505, 135, flip=False))
    s.add(wake(1090, 535, 155, flip=True, op=0.55))
    s.add(superyacht(1090, 535, 155, flip=True))
    s.add(sailboat(620, 475, 34, flip=False))
    s.add(sailboat(740, 492, 28, flip=True))
    s.add(sailboat(1370, 468, 30, flip=False))

    for bx, by, bs in [(310, 160, 5), (324, 152, 4), (336, 164, 4.5), (1110, 190, 5), (1126, 182, 4)]:
        s.add(bird_v(bx, by, bs, col="#3b2638"))

    callouts(s, [
        (t["pyramid_monument"], 465, 175, 465, 220),
        (t["gov_center"], 677, 92, 677, 132),
        (t["sky_city"], 855, 46, 855, 22),
        (t["infinity_tower"], 955, 108, 948, 142),
        (t["clock_tower"], 1068, 162, 1062, 195),
        (t["monorail_line"], 310, 365, 310, 393),
        (t["marina_aurelia"], 255, 552, 255, 505),
    ])
    return s.render(t["skyline_title"])


# ==============================================================================
# 2. SCENE: PYRAMID (The Grand Sovereign Pyramid - 1200 x 700)
# ==============================================================================
def build_pyramid(t: dict[str, str]) -> str:
    s = Scene("pyramid", 1200, 700, 202)
    rng = s.rng
    patterns(s, "#0b1728")
    glass_gradients(
        s,
        [(0, "#d4ecff"), (0.5, "#6ea3cc"), (1, "#274c70")],
        [(0, "#274c70"), (1, "#10243a")],
    )
    s.blur("mist", 6)
    rip = ripple(s, "rip", fx=0.006, fy=0.09, scale=7)
    pmask = fade_mask(s, "pmask", 0, 548, 1200, 152, top=0.55, bottom=0.05)

    NT.sky(s, [
        (0.0, "#0c1d38"), (0.38, "#1d3f6e"), (0.70, "#4a78a6"), (0.92, "#b8c7be"), (1.0, "#f5deb0"),
    ], h=525)
    NT.sun(s, 600, 108, 42, glow="#ffe6a3")

    rays = []
    for k in range(-6, 7):
        a = -math.pi / 2 + k * 0.14
        x2, y2 = 600 + math.cos(a) * 680, 108 + math.sin(a) * 420
        x3, y3 = 600 + math.cos(a + 0.055) * 680, 108 + math.sin(a + 0.055) * 420
        rays.append(el("path", d=P([(600, 108), (x2, y2), (x3, y3)]), fill="#fff3c4", opacity=0.07))
    s.add(g(rays))

    for cx, cy, cw in [(190, 135, 260), (980, 120, 290), (410, 95, 210), (820, 165, 230)]:
        s.add(cloud(rng, cx, cy, cw, col="#fff7ea", shade="#b9c8d8", op=0.82, cls="city-anim-cloud"))

    s.add(far_city(rng, 20, 320, 500, 45, 140, "#385678", wmin=12, wmax=26, lights=0.15))
    s.add(far_city(rng, 880, 1180, 500, 45, 145, "#385678", wmin=12, wmax=26, lights=0.15))
    for bx, bh, bw in [(48, 175, 28), (88, 210, 32), (1055, 195, 30), (1098, 165, 26)]:
        s.add(tower(s, bx, 500, bw, bh, d=8, pat="curtain", lit=0.05, crown_kind="flat", beacon=False))

    s.add(el("path", d=P([(592, 108), (608, 108), (642, 0), (558, 0)]),
             fill=s.linear("beam", [(0, "#fff8c8", 0.85), (0.5, "#ffe680", 0.35), (1, "#ffe680", 0)]),
             class_="city-anim-beacon"))

    pyr_grp = pyramid(
        s,
        apex=(600, 96),
        L=(95, 500),
        F=(618, 522),
        R=(1105, 500),
        tiers=6,
        cap=0.13,
        scale=1.35,
        cutaway=(0.64, 0.94, 0.14, 0.62),
        waterfall_u=0.78,
        lights=True,
    )
    L_pt, F_pt, apex = (95, 500), (618, 522), (600, 96)
    for ti in range(2, 7):
        t_val = 0.13 + 0.87 * ti / 6.3
        for u_val in (0.08, 0.22, 0.38, 0.54, 0.68, 0.90):
            if ti in (4, 5, 6) and 0.12 <= u_val <= 0.64:
                continue
            px, py = lerp(lerp(apex, L_pt, t_val), lerp(apex, F_pt, t_val), u_val)
            ph = (10 + 18 * t_val) * rng.uniform(0.85, 1.15)
            pyr_grp.append(palm(rng, px, py, ph, rng.uniform(-3, 3), ph * 0.55,
                                cols=("#1f5a28", "#489640"), nfr=9, royal=True, coconuts=False, sway=False))

    col_x0, col_x1, col_top, col_bot = 465, 775, 476, 522
    pyr_grp.extend([
        el("rect", x=col_x0 - 8, y=col_top + 4, width=col_x1 - col_x0 + 16, height=col_bot - col_top - 4, fill="#1a1410"),
        el("polygon", points=f"{col_x0 - 14},{col_top} {(col_x0 + col_x1) / 2},{col_top - 18} {col_x1 + 14},{col_top}",
           fill="#f3e2c3", stroke="#b59461", stroke_width=1),
        el("rect", x=col_x0 - 12, y=col_top, width=col_x1 - col_x0 + 24, height=5, fill="#e6cfa4"),
    ])
    for cx in range(col_x0, col_x1 + 1, 22):
        pyr_grp.extend([
            el("rect", x=cx - 3.2, y=col_top + 5, width=6.4, height=col_bot - col_top - 8, fill="#f7ebd2"),
            el("rect", x=cx + 0.5, y=col_top + 5, width=2.7, height=col_bot - col_top - 8, fill="#b89b6c", opacity=0.55),
            el("rect", x=cx - 4.5, y=col_top + 4, width=9, height=2.5, fill="#d8b46c"),
            el("rect", x=cx - 4.5, y=col_bot - 3, width=9, height=3, fill="#d8b46c"),
        ])
    s.add(g(pyr_grp, id=s.id("pyr-main")))

    s.add(el("rect", x=0, y=500, width=1200, height=200, fill=s.linear("plaza", [
        (0.0, "#e9d8b8"), (0.45, "#d8c29d"), (1.0, "#b59b73"),
    ])))
    pave = [f"M{n(600 + k * 22)},500 L{n(600 + k * 95)},700" for k in range(-14, 15)]
    pave += [f"M0,{n(500 + 200 * (r / 11) ** 1.45)}H1200" for r in range(1, 12)]
    s.add(el("path", d=" ".join(pave), stroke="#9e825a", stroke_width=0.7, opacity=0.45, fill="none"))

    steps = [el("rect", x=618 - (92 + st * 6), y=520 + st * 4.5, width=(92 + st * 6) * 2, height=4.2,
                fill="#f4e5c8" if st % 2 == 0 else "#dcc69e", stroke="#9e825a", stroke_width=0.5) for st in range(9)]
    s.add(g(steps))

    pool_water = s.linear("pool-w", [(0, "#1c5a85"), (0.5, "#134266"), (1, "#0b2942")])
    for px0, px1 in [(55, 495), (735, 1145)]:
        p_pts = [(px0 + 35, 548), (px1 - 15, 548), (px1 + 10, 678), (px0 - 20, 678)]
        p_clip = s.clip(f"pclip-{px0}", P(p_pts))
        s.add(el("path", d=P(p_pts), fill=pool_water))
        s.add(reflection(s, "pyr-main", 520, mask=pmask, filt=rip, op=0.55, clip=p_clip))
        s.add(water_lines(rng, px0, px1, 554, 672, 36, col="#b8ebff", op=0.35, w=0.9))
        s.add(el("path", d=P(p_pts), fill="none", stroke="#c99c42", stroke_width=2.2))
        for fj in range(5):
            fx = px0 + 55 + fj * (px1 - px0 - 110) / 4
            fy = 612
            s.add(el("path", d=f"M{n(fx)},{fy} C{n(fx - 4)},{fy - 34} {n(fx - 8)},{fy - 42} {n(fx - 12)},{fy - 8} "
                               f"M{n(fx)},{fy} V{fy - 44} "
                               f"M{n(fx)},{fy} C{n(fx + 4)},{fy - 34} {n(fx + 8)},{fy - 42} {n(fx + 12)},{fy - 8}",
                     stroke="#e6f9ff", stroke_width=1.4, fill="none", opacity=0.85, class_="flow"))
            s.add(el("ellipse", cx=fx, cy=fy, rx=10, ry=2.8, fill="#ffffff", opacity=0.85))

    for py_row, sc in [(555, 0.78), (605, 0.95), (658, 1.15)]:
        for side_x in (512, 720):
            s.add(palm(rng, side_x, py_row, 48 * sc, (-4 if side_x < 600 else 4), 24 * sc,
                       cols=("#1e5628", "#468f3e"), nfr=12, royal=True, coconuts=False))
    s.add(crowd(rng, 525, 705, 565, 685, 42, 16))

    for sx, sy in [(555, 642), (645, 666)]:
        s.add(g([
            el("ellipse", cx=sx + 26, cy=sy + 17, rx=28, ry=4, fill="#000000", opacity=0.22),
            el("rect", x=sx, y=sy, width=52, height=15, rx=7, fill="#f8fafc", stroke="#c99c42", stroke_width=1.1),
            el("rect", x=sx + 7, y=sy + 3, width=38, height=6.5, rx=3, fill="#16324f"),
            el("line", x1=sx + 4, y1=sy + 11, x2=sx + 48, y2=sy + 11, stroke="#00d8ff", stroke_width=1.0),
            el("circle", cx=sx + 11, cy=sy + 15, r=3.2, fill="#1e293b"),
            el("circle", cx=sx + 41, cy=sy + 15, r=3.2, fill="#1e293b"),
        ]))

    callouts(s, [
        (t["apex_beacon"], 600, 56, 600, 96),
        (t["hanging_gardens"], 235, 250, 345, 295),
        (t["solar_skin"], 965, 250, 845, 305),
        (t["amphitheater"], 205, 430, 355, 435),
        (t["colonnade"], 618, 452, 618, 485),
    ])
    return s.render(t["pyramid_title"])



# ==============================================================================
# 3. SCENE: UNDERSEA-HUB (Trans-Lagoon Maglev - 1200 x 700)
# ==============================================================================
def build_undersea_hub(t: dict[str, str]) -> str:
    s = Scene("undersea-hub", 1200, 700, 303)
    rng = s.rng
    patterns(s, "#0d2138")
    caust = caustics(s, "caust")
    b_glow = glow(s, "bglow", 4)

    NT.sky(s, [(0.0, "#0b5fa5"), (0.55, "#42a5dc"), (1.0, "#c8eefb")], h=225)
    NT.sun(s, 1040, 78, 28, glow="#fff3c4")
    for cx, cy, cw in [(220, 72, 220), (640, 58, 260), (920, 92, 190)]:
        s.add(cloud(rng, cx, cy, cw, col="#ffffff", shade="#c9dff0", op=0.9, cls="city-anim-cloud"))

    s.add(far_city(rng, 560, 1180, 214, 24, 95, "#6ba0c4", wmin=10, wmax=22))

    term = [
        el("rect", x=55, y=206, width=495, height=12, fill="#d8c7a8", stroke="#8f7c5e", stroke_width=0.8),
        el("path", d="M85,206 V142 Q295,88 505,142 V206Z",
           fill=s.linear("term-g", [(0, "#e6f7ff", 0.9), (0.6, "#7ac5eb", 0.8), (1, "#1e6494", 0.88)])),
        el("path", d="".join(
            f"M{85 + k * 30},206 L{115 + k * 30},135 M{115 + k * 30},206 L{85 + k * 30},135"
            for k in range(13)
        ), stroke="#ffffff", stroke_width=1.1, opacity=0.55, fill="none"),
        el("path", d="M55,146 Q190,92 310,122 Q425,148 535,126 L525,136 Q420,158 308,132 Q190,104 65,154Z",
           fill=s.linear("term-roof", [(0, "#ffffff"), (0.5, "#d8e6f2"), (1, "#8fa8be")]), stroke="#2c5278", stroke_width=1),
    ]
    for px in range(105, 505, 45):
        term.append(el("rect", x=px - 2, y=145, width=4, height=61, fill="#e2ebf2"))
    term.append(crowd(rng, 110, 485, 202, 206, 22, 11))
    for px in (68, 520, 542):
        term.append(palm(rng, px, 206, 36, 4 if px > 300 else -4, 18, cols=("#1f5e2b", "#4aa043"), nfr=10, royal=True, coconuts=False))
    s.add(g(term))

    s.add(superyacht(760, 214, 145, flip=False))
    s.add(sailboat(985, 212, 36, flip=True))

    wave_top = "M0,214 Q150,206 300,214 T600,214 T900,214 T1200,214"
    wave_bot = "L1200,226 Q1050,234 900,226 T600,226 T300,226 T0,226Z"
    s.add(el("path", d=f"{wave_top} L1200,700 L0,700Z", fill=s.linear("sea-col", [
        (0.0, "#1ca3cf"), (0.18, "#0f78a8"), (0.48, "#094e7a"), (0.78, "#062f52"), (1.0, "#03182e"),
    ])))
    s.add(el("path", d=f"{wave_top} {wave_bot}", fill=s.linear("menisc", [
        (0, "#ffffff", 0.85), (0.4, "#9eeeff", 0.75), (1, "#0f78a8", 0.0),
    ])))
    s.add(el("path", d=wave_top, stroke="#ffffff", stroke_width=2.0, fill="none", opacity=0.9))

    s.add(NT.light_rays(s, 40, 1120, 220, 660, 16, op=0.16))
    s.add(el("rect", x=0, y=220, width=1200, height=120, filter=caust, opacity=0.18))

    s.add(el("path", d="M0,585 Q180,535 380,565 T760,545 T1200,575 L1200,700 L0,700Z", fill="#07385c", opacity=0.7))
    s.add(el("path", d="M0,618 Q220,575 460,605 T920,582 T1200,612 L1200,700 L0,700Z", fill="#062844", opacity=0.85))

    dome_cx, dome_cy, dome_r = 235, 405, 68
    shaft = [
        el("rect", x=dome_cx - 14, y=218, width=28, height=dome_cy - dome_r - 210, fill="#38546e", stroke="#8ec5e6", stroke_width=1),
        el("rect", x=dome_cx - 8, y=222, width=16, height=dome_cy - dome_r - 218, fill="#9ee8ff", opacity=0.45),
        el("rect", x=dome_cx - 7, y=268, width=14, height=22, rx=2, fill="#fff3c4", stroke="#d99b26", stroke_width=1),
    ]
    for sy in range(230, int(dome_cy - dome_r), 16):
        shaft.append(el("line", x1=dome_cx - 14, y1=sy, x2=dome_cx + 14, y2=sy, stroke="#1b3148", stroke_width=1.2))
    s.add(g(shaft))

    dome_clip = s.clip("dclip", f"M{dome_cx - dome_r},{dome_cy + 18} A{dome_r},{dome_r} 0 1 1 {dome_cx + dome_r},{dome_cy + 18}Z")
    dome_int = [
        el("circle", cx=dome_cx, cy=dome_cy, r=dome_r, fill=s.radial("d-glow", [
            (0, "#fff2c2", 0.85), (0.65, "#f5be58", 0.55), (1, "#164e78", 0.7)
        ])),
        el("rect", x=dome_cx - dome_r, y=dome_cy - 4, width=dome_r * 2, height=5, fill="#24384d"),
        el("rect", x=dome_cx - dome_r, y=dome_cy + 16, width=dome_r * 2, height=10, fill="#1a2a3a"),
        el("rect", x=dome_cx - 38, y=dome_cy - 24, width=22, height=13, rx=1.5, fill="#5ceeff", opacity=0.85),
        el("rect", x=dome_cx + 14, y=dome_cy - 24, width=24, height=13, rx=1.5, fill="#5ceeff", opacity=0.85),
        person(dome_cx - 22, dome_cy - 4, 15, col="#142234", rng=rng),
        person(dome_cx - 8, dome_cy - 4, 14.5, col="#2c3e50", rng=rng),
        person(dome_cx + 22, dome_cy - 4, 15, col="#142234", rng=rng),
        person(dome_cx - 30, dome_cy + 16, 15, col="#1e2d3d", rng=rng),
        person(dome_cx + 8, dome_cy + 16, 14, col="#34495e", rng=rng),
    ]
    struts = [f"M{n(dome_cx + k * dome_r * 0.28)},{dome_cy + 18} Q{n(dome_cx + k * dome_r * 0.12)},{dome_cy - dome_r} {dome_cx},{dome_cy - dome_r}"
              for k in range(-3, 4)]
    struts += [f"M{dome_cx - dome_r},{ry} Q{dome_cx},{ry - 10} {dome_cx + dome_r},{ry}" for ry in (dome_cy - 38, dome_cy - 18, dome_cy + 2)]
    s.add(g([
        el("path", d=P([(dome_cx - 52, dome_cy + 18), (dome_cx + 52, dome_cy + 18),
                        (dome_cx + 68, 608), (dome_cx - 68, 608)]), fill="#24384c", opacity=0.7),
        g(dome_int, clip_path=dome_clip),
        el("path", d=" ".join(struts), stroke="#b8ecff", stroke_width=1.1, fill="none", opacity=0.65, clip_path=dome_clip),
        el("path", d=f"M{dome_cx - dome_r},{dome_cy + 18} A{dome_r},{dome_r} 0 1 1 {dome_cx + dome_r},{dome_cy + 18}Z",
           fill="none", stroke="#9ee8ff", stroke_width=2.4),
    ]))

    ty0, ty1 = 462, 546
    th = ty1 - ty0
    for px in range(95, 1180, 175):
        s.add(g([
            el("path", d=P([(px - 16, ty1 - 4), (px + 16, ty1 - 4), (px + 26, 642), (px - 26, 642)]),
               fill=s.linear(f"pyl-{px}", [(0, "#4a6580"), (0.5, "#2b4259"), (1, "#162636")], x1=0, y1=0, x2=1, y2=0)),
            el("rect", x=px - 20, y=ty1 - 6, width=40, height=8, rx=2, fill="#6c8aa6"),
            el("ellipse", cx=px, cy=640, rx=34, ry=8, fill="#385269"),
        ]))

    s.add(el("rect", x=0, y=ty0, width=1200, height=th,
             fill=s.linear("tube-bg", [(0, "#0a3556", 0.55), (0.5, "#072640", 0.35), (1, "#0a3556", 0.65)])))
    s.add(el("rect", x=0, y=ty1 - 14, width=1200, height=8, fill="#1c3147"))
    s.add(el("line", x1=0, y1=ty1 - 13, x2=1200, y2=ty1 - 13, stroke="#00f2ff", stroke_width=1.8, filter=b_glow))
    s.add(el("path", d="".join(f"M{x},{ty1 - 11}h10v4h-10Z" for x in range(8, 1195, 18)), fill="#eab308", opacity=0.8))

    tr_x0, tr_x1, tr_y0, tr_y1 = 420, 990, 480, 531
    train_d = (
        f"M{tr_x0},{tr_y1} L{tr_x0 + 18},{tr_y0 + 6} Q{tr_x0 + 30},{tr_y0} {tr_x0 + 55},{tr_y0} "
        f"H{tr_x1 - 95} C{tr_x1 - 45},{tr_y0} {tr_x1 - 12},{tr_y0 + 18} {tr_x1},{tr_y1 - 4} "
        f"Q{tr_x1 + 2},{tr_y1} {tr_x1 - 10},{tr_y1} Z"
    )
    train_items = [
        el("path", d=f"M290,{tr_y0 + 10}H{tr_x0} M240,{tr_y0 + 24}H{tr_x0} M310,{tr_y0 + 38}H{tr_x0}",
           stroke="#7ef6ff", stroke_width=1.6, stroke_dasharray="28 14", opacity=0.65, class_="flow"),
        el("path", d=train_d, fill=s.linear("tr-body", [(0, "#ffffff"), (0.45, "#e6f2fa"), (0.78, "#8fb3cf"), (1, "#274968")])),
        el("path", d=f"M{tr_x0 + 6},{tr_y1 - 14} H{tr_x1 - 18}", stroke="#eab308", stroke_width=2.5),
        el("path", d=f"M{tr_x0 + 4},{tr_y1 - 11} H{tr_x1 - 10}", stroke="#00f2ff", stroke_width=1.4),
        el("path", d=f"M{tr_x1 - 88},{tr_y0 + 5} C{tr_x1 - 52},{tr_y0 + 6} {tr_x1 - 24},{tr_y0 + 18} {tr_x1 - 12},{tr_y0 + 30} H{tr_x1 - 88}Z",
           fill="#0c2238", stroke="#7ef6ff", stroke_width=0.9),
        el("path", d=P([(tr_x1, tr_y1 - 6), (tr_x1 + 160, tr_y1 - 32), (tr_x1 + 160, tr_y1 + 18)]),
           fill=s.linear("hl-beam", [(0, "#fffbe0", 0.75), (1, "#7ef6ff", 0)], x1=0, y1=0, x2=1, y2=0)),
    ]
    for cx_car in range(tr_x0 + 32, tr_x1 - 105, 34):
        train_items.extend([
            el("rect", x=cx_car, y=tr_y0 + 9, width=26, height=15, rx=3.5, fill="#fff1bf", stroke="#386182", stroke_width=0.9),
            el("circle", cx=cx_car + 8, cy=tr_y0 + 18, r=2.6, fill="#24374a"),
            el("circle", cx=cx_car + 18, cy=tr_y0 + 18, r=2.6, fill="#24374a"),
        ])
    for jx in (tr_x0 + 170, tr_x0 + 340):
        train_items.append(el("rect", x=jx, y=tr_y0 + 1, width=4, height=tr_y1 - tr_y0 - 2, fill="#334e68"))
    s.add(g(train_items))

    flanges = []
    for fx in range(50, 1200, 88):
        flanges.extend([
            el("rect", x=fx - 2.5, y=ty0 - 3, width=5, height=th + 6, rx=2,
               fill=s.linear(f"fl-{fx}", [(0, "#9ab6ce"), (0.3, "#eef7fc"), (0.7, "#52738f"), (1, "#1e354a")])),
            el("circle", cx=fx, cy=ty0 + 4, r=1.2, fill="#162838"),
            el("circle", cx=fx, cy=ty1 - 4, r=1.2, fill="#162838"),
        ])
    s.add(g([
        el("rect", x=0, y=ty0 + 3, width=1200, height=10, fill="#ffffff", opacity=0.32),
        el("rect", x=0, y=ty0 + 16, width=1200, height=4, fill="#bef4ff", opacity=0.18),
        el("rect", x=0, y=ty1 - 7, width=1200, height=5, fill="#7ee8ff", opacity=0.25),
        el("line", x1=0, y1=ty0, x2=1200, y2=ty0, stroke="#c7f4ff", stroke_width=2.2),
        el("line", x1=0, y1=ty1, x2=1200, y2=ty1, stroke="#67c7eb", stroke_width=2.2),
        *flanges,
    ]))

    seabed_pts = [(0, 628), (110, 608), (240, 625), (390, 602), (540, 632), (710, 605), (870, 618), (1030, 596), (1200, 622)]
    s.add(el("path", d=smooth(seabed_pts) + " L1200,700 L0,700Z",
             fill=s.linear("bed", [(0, "#1c4b6b"), (0.4, "#10324c"), (1, "#071a2b")])))
    s.add(el("path", d=smooth(seabed_pts) + " L1200,700 L0,700Z", filter=caust, opacity=0.22))

    s.add(g([
        seagrass(rng, 20, 1180, 648, 85, 34, col="#2e8b57"),
        sea_fan(rng, 68, 625, 58, col="#b84fd1"),
        sea_fan(rng, 315, 622, 52, col="#e0569c"),
        sea_fan(rng, 650, 628, 62, col="#9b4dca"),
        sea_fan(rng, 985, 612, 56, col="#d94f8c"),
        branch_coral(rng, 138, 624, 34, 4, "#ff6b6b", 4.2),
        branch_coral(rng, 455, 628, 38, 4, "#ff9f43", 4.5),
        branch_coral(rng, 795, 622, 36, 4, "#f368e0", 4.2),
        branch_coral(rng, 1115, 618, 40, 4, "#ff6b6b", 4.5),
        brain_coral(rng, 215, 632, 28, col="#e0a938"),
        brain_coral(rng, 575, 636, 32, col="#d48c32"),
        brain_coral(rng, 915, 626, 30, col="#55b884"),
        tube_sponge(365, 624, 42, col="#c556cf"),
        tube_sponge(735, 625, 46, col="#e8647c"),
        tube_sponge(1045, 612, 44, col="#9c56cf"),
    ]))

    s.add(manta(635, 322, 1.35))
    s.add(manta(825, 278, 0.85))
    s.add(turtle(985, 372, 1.25, flip=True))
    s.add(turtle(120, 340, 0.95, flip=False))
    s.add(school(rng, 455, 355, 18, 65, 9, "#ffbe2e", stripe="#1e3a5f", flip=False))
    s.add(school(rng, 1065, 415, 16, 55, 8, "#38d9f5", stripe="#f5d138", flip=True))
    s.add(school(rng, 160, 568, 12, 45, 7.5, "#ff6b8b", stripe="#ffffff", flip=False))

    for jx, jy, js in [(88, 425, 1.0), (885, 392, 1.15), (1135, 310, 0.85)]:
        tent = " ".join(
            f"M{n(jx + (k - 3) * 3.5 * js)},{n(jy)} Q{n(jx + (k - 3) * 5 * js)},{n(jy + 22 * js)} {n(jx + (k - 3) * 2.5 * js)},{n(jy + 44 * js)}"
            for k in range(7)
        )
        s.add(g([
            el("path", d=tent, stroke="#7ef9ff", stroke_width=1.1, fill="none", opacity=0.75),
            el("path", d=f"M{n(jx - 16 * js)},{n(jy)} C{n(jx - 16 * js)},{n(jy - 20 * js)} {n(jx + 16 * js)},{n(jy - 20 * js)} {n(jx + 16 * js)},{n(jy)} "
                         f"Q{n(jx)},{n(jy - 4 * js)} {n(jx - 16 * js)},{n(jy)}Z",
               fill=s.radial(f"jel-{jx}", [(0, "#ffffff", 0.95), (0.55, "#5ceeff", 0.75), (1, "#a855f7", 0.35)])),
        ], filter=b_glow, class_="city-anim-biolum"))

    callouts(s, [
        (t["surface_terminal"], 295, 78, 295, 120),
        (t["obs_dome"], 125, 395, 168, 405),
        (t["maglev_train"], 710, 432, 710, 480),
        (t["acrylic_tube"], 1045, 432, 1045, 464),
        (t["coral_sanctuary"], 915, 668, 915, 626),
    ], accent="#5ceeff", bg="#062238")
    return s.render(t["undersea_title"])


# ==============================================================================
# 4. SCENE: ARCHIPELAGO-MAP (Cartographic Masterplan - 1100 x 600)
# ==============================================================================
def build_archipelago_map(t: dict[str, str]) -> str:
    s = Scene("archipelago-map", 1100, 600, 404)
    rng = s.rng

    s.add(el("rect", width=1100, height=600, fill=s.linear("ocean", [
        (0.0, "#051e36"), (0.45, "#083358"), (0.82, "#0c4f7d"), (1.0, "#126b9c"),
    ], x1=1, y1=0, x2=0, y2=0)))

    for d_path, col, op in [
        ("M0,0 H780 Q980,140 965,310 Q950,480 760,600 H0Z", "#0a3f68", 0.65),
        ("M0,0 H690 Q890,150 885,310 Q880,465 680,600 H0Z", "#0f5687", 0.65),
        ("M0,0 H560 Q790,175 790,310 Q790,445 555,600 H0Z", "#1674ab", 0.55),
    ]:
        s.add(el("path", d=d_path, fill=col, opacity=op, stroke="#5cc8f2", stroke_width=0.7, stroke_dasharray="6 4"))

    grid = [f"M{gx},0V600" for gx in range(100, 1050, 100)] + [f"M0,{gy}H1100" for gy in range(75, 600, 75)]
    s.add(el("path", d="".join(grid), stroke="#7ad7ff", stroke_width=0.5, stroke_dasharray="3 6", opacity=0.28))

    coast = "M0,0 H155 Q172,70 148,135 L182,152 L175,195 L138,202 Q152,258 168,318 L192,326 L165,355 Q138,425 162,495 Q175,548 145,600 H0Z"
    s.add(el("path", d=coast, fill="#35efc8", opacity=0.28))
    s.add(el("path", d=coast, fill=s.linear("main-land", [(0, "#e6d8be"), (1, "#c8b490")]), stroke="#8c7248", stroke_width=1.8))
    blocks = []
    for by in range(18, 575, 22):
        for bx in range(12, 128, 26):
            if rng.random() < 0.18:
                blocks.append(el("rect", x=bx, y=by, width=20, height=16, rx=2, fill="#579c5a", opacity=0.75))
            else:
                blocks.append(el("rect", x=bx, y=by, width=20, height=16, rx=1, fill="#9e8c70", stroke="#78664c", stroke_width=0.5))
    s.add(g(blocks))

    reef_arc = "M815,48 C975,165 975,435 815,552"
    s.add(el("path", d=reef_arc, stroke="#22d3ee", stroke_width=26, fill="none", opacity=0.28, stroke_linecap="round"))
    s.add(el("path", d=reef_arc, stroke="#34d399", stroke_width=12, stroke_dasharray="42 10 26 8 54 12", fill="none", opacity=0.75, stroke_linecap="round"))
    s.add(el("path", d=reef_arc, stroke="#ffffff", stroke_width=2.2, stroke_dasharray="18 8 10 6", fill="none", opacity=0.85))

    pcx, pcy, pr = 375, 325, 112
    s.add(el("circle", cx=pcx, cy=pcy, r=pr + 18, fill="#2dd4bf", opacity=0.25))
    s.add(el("circle", cx=pcx, cy=pcy, r=pr + 4, fill="#0e7490", opacity=0.45))
    for a0, a1 in [(-1.28, -0.46), (-0.36, 0.36), (0.46, 1.28)]:
        x0, y0 = pcx + math.cos(a0) * pr, pcy + math.sin(a0) * pr
        x1, y1 = pcx + math.cos(a1) * pr, pcy + math.sin(a1) * pr
        s.add(el("path", d=f"M{n(x0)},{n(y0)} A{pr},{pr} 0 0 1 {n(x1)},{n(y1)}", stroke="#efe0be", stroke_width=11, fill="none", stroke_linecap="round"))
        s.add(el("path", d=f"M{n(x0)},{n(y0)} A{pr},{pr} 0 0 1 {n(x1)},{n(y1)}", stroke="#65a34e", stroke_width=4.5, fill="none", stroke_linecap="round"))
    s.add(el("rect", x=168, y=pcy - 6, width=pcx - 168 + 18, height=12, rx=4, fill="#e8d5b0", stroke="#9e8252", stroke_width=1))
    s.add(el("ellipse", cx=pcx - 18, cy=pcy, rx=34, ry=16, fill="#e8d5b0", stroke="#9e8252", stroke_width=1))
    fronds = []
    for side in (-1, 1):
        for fi in range(8):
            ang = side * (0.22 + fi * 0.145)
            base_x = pcx - 42 + fi * 11
            base_y = pcy + side * 6
            L_fr = 82 - abs(fi - 3.5) * 7
            tip_x, tip_y = base_x + math.cos(ang) * L_fr, base_y + math.sin(ang) * L_fr
            ctrl_x, ctrl_y = base_x + math.cos(ang - side * 0.18) * L_fr * 0.55, base_y + math.sin(ang - side * 0.18) * L_fr * 0.55
            fronds.append(el("path", d=f"M{n(base_x)},{n(base_y)} Q{n(ctrl_x)},{n(ctrl_y)} {n(tip_x)},{n(tip_y)}",
                             stroke="#f2e2be", stroke_width=6.2, fill="none", stroke_linecap="round"))
            fronds.append(el("path", d=f"M{n(base_x)},{n(base_y)} Q{n(ctrl_x)},{n(ctrl_y)} {n(tip_x)},{n(tip_y)}",
                             stroke="#4d9a46", stroke_width=2.0, fill="none", stroke_linecap="round"))
    s.add(g(fronds))
    s.add(el("circle", cx=pcx + pr, cy=pcy, r=11, fill="#fbbf24", stroke="#78350f", stroke_width=1.8))
    s.add(el("circle", cx=pcx + pr, cy=pcy, r=4.5, fill="#fef08a"))

    s.add(el("ellipse", cx=690, cy=205, rx=165, ry=105, fill="#2dd4bf", opacity=0.22))
    s.add(el("ellipse", cx=690, cy=205, rx=158, ry=98, fill="none", stroke="#cbd5e1", stroke_width=3.5, stroke_dasharray="28 8 44 10"))
    world_clusters = [
        [(565, 155, 11, 7), (582, 145, 13, 8), (598, 158, 10, 6), (574, 172, 14, 8), (592, 178, 9, 6), (608, 142, 8, 5)],
        [(606, 215, 10, 8), (616, 232, 12, 11), (612, 252, 9, 10), (608, 270, 6, 8)],
        [(632, 128, 12, 6), (652, 136, 6, 4)],
        [(665, 152, 9, 6), (680, 146, 11, 7), (694, 155, 10, 6), (672, 166, 12, 6), (688, 168, 9, 5)],
        [(668, 192, 14, 9), (686, 198, 13, 10), (678, 216, 14, 11), (684, 236, 11, 10), (688, 254, 9, 8), (706, 248, 5, 6)],
        [(716, 148, 15, 8), (738, 144, 16, 9), (762, 150, 15, 8), (784, 158, 12, 7),
         (724, 168, 16, 9), (748, 170, 18, 10), (772, 175, 15, 9), (792, 180, 11, 7),
         (736, 190, 12, 8), (760, 194, 14, 8), (780, 198, 10, 6), (804, 172, 7, 9)],
        [(768, 216, 7, 5), (782, 222, 8, 5), (796, 218, 7, 4), (782, 246, 16, 10), (802, 252, 12, 8), (822, 266, 7, 5)],
    ]
    isles = []
    for cluster in world_clusters:
        for ix, iy, rx, ry in cluster:
            isles.append(el("ellipse", cx=ix, cy=iy, rx=rx + 2.5, ry=ry + 2, fill="#38bdf8", opacity=0.35))
            isles.append(el("ellipse", cx=ix, cy=iy, rx=rx, ry=ry, fill="#f1dfb8", stroke="#9e8252", stroke_width=0.7))
            isles.append(el("ellipse", cx=ix, cy=iy, rx=rx * 0.62, ry=ry * 0.58, fill="#529e49"))
            for _ in range(2):
                ang = rng.uniform(0, TAU)
                isles.append(el("circle", cx=ix + math.cos(ang) * (rx + 4.5), cy=iy + math.sin(ang) * (ry + 3.5),
                                r=rng.uniform(1.8, 3.2), fill="#f1dfb8", stroke="#9e8252", stroke_width=0.4))
    s.add(g(isles))

    for ax, ay, ar in [(585, 455, 36), (672, 472, 44), (758, 442, 34)]:
        s.add(g([
            el("circle", cx=ax, cy=ay, r=ar + 10, fill="#2dd4bf", opacity=0.28),
            el("circle", cx=ax, cy=ay, r=ar, fill="#084c61", stroke="#e8d8b4", stroke_width=7, stroke_dasharray="52 10 68 12"),
            el("circle", cx=ax, cy=ay, r=ar, fill="none", stroke="#34d399", stroke_width=3, stroke_dasharray="48 14 62 16"),
            el("circle", cx=ax, cy=ay, r=ar * 0.52, fill="#22d3ee", opacity=0.35),
            el("line", x1=ax - ar * 0.45, y1=ay, x2=ax + ar * 0.45, y2=ay, stroke="#e2e8f0", stroke_width=1.4),
            el("line", x1=ax, y1=ay - ar * 0.45, x2=ax, y2=ay + ar * 0.45, stroke="#e2e8f0", stroke_width=1.4),
            el("circle", cx=ax, cy=ay, r=6.5, fill="#f8fafc", stroke="#0284c7", stroke_width=1.5),
            el("circle", cx=ax - ar * 0.42, cy=ay, r=4, fill="#f8fafc", stroke="#0284c7", stroke_width=1.2),
            el("circle", cx=ax + ar * 0.42, cy=ay, r=4, fill="#f8fafc", stroke="#0284c7", stroke_width=1.2),
        ]))

    transit = [
        el("path", d="M150,325 H487 M148,200 Q395,145 678,198 M678,248 L672,428 M375,325 Q510,410 585,455",
           stroke="#00f2ff", stroke_width=4.5, opacity=0.28, fill="none"),
        el("path", d="M150,325 H487 M148,200 Q395,145 678,198 M678,248 L672,428 M375,325 Q510,410 585,455",
           stroke="#00f2ff", stroke_width=2.2, stroke_dasharray="9 5", fill="none"),
        el("path", d="M162,485 Q380,520 585,455 Q672,472 758,442",
           stroke="#fbbf24", stroke_width=1.5, stroke_dasharray="3 4", fill="none"),
    ]
    for sx, sy in [(150, 325), (375, 325), (487, 325), (148, 200), (678, 198), (585, 455), (672, 472), (758, 442)]:
        transit.append(el("circle", cx=sx, cy=sy, r=4.2, fill="#0b192c", stroke="#00f2ff", stroke_width=1.8))
    s.add(g(transit))

    rcx, rcy, rr = 995, 88, 36
    rose = [
        el("circle", cx=rcx, cy=rcy, r=rr + 5, fill="#071a2e", stroke="#d4a238", stroke_width=1.4, opacity=0.92),
        el("circle", cx=rcx, cy=rcy, r=rr, fill="none", stroke="#d4a238", stroke_width=0.8, stroke_dasharray="2 3"),
    ]
    for k in range(8):
        a = k * math.pi / 4 - math.pi / 2
        L_pt = rr if k % 2 == 0 else rr * 0.65
        w_pt = 6.5 if k % 2 == 0 else 4.2
        tip = (rcx + math.cos(a) * L_pt, rcy + math.sin(a) * L_pt)
        left = (rcx + math.cos(a - 0.35) * w_pt, rcy + math.sin(a - 0.35) * w_pt)
        right = (rcx + math.cos(a + 0.35) * w_pt, rcy + math.sin(a + 0.35) * w_pt)
        rose.append(el("polygon", points=f"{rcx},{rcy} {n(left[0])},{n(left[1])} {n(tip[0])},{n(tip[1])}", fill="#f6d365"))
        rose.append(el("polygon", points=f"{rcx},{rcy} {n(right[0])},{n(right[1])} {n(tip[0])},{n(tip[1])}", fill="#a16e18"))
    s.add(g(rose))

    callouts(s, [
        (t["mainland_aurelia"], 88, 268, 148, 268),
        (t["palm_island"], 375, 178, 375, 222),
        (t["hotel_khalifa"], 492, 375, 487, 336),
        (t["world_islands"], 690, 72, 690, 118),
        (t["chameleon_atolls"], 672, 558, 672, 516),
        (t["coral_barrier"], 955, 305, 922, 305),
        (t["subsea_maglev"], 285, 132, 335, 168),
    ])
    return s.render(t["archipelago_title"])



# ==============================================================================
# 5. VIGNETTE 1: MARINA AURELIA (640 x 420)
# ==============================================================================
def build_marina(t: dict[str, str]) -> str:
    s = Scene("marina", 640, 420, 505)
    rng = s.rng
    patterns(s, "#0a1729")
    glass_gradients(
        s,
        [(0, "#ffe6be"), (0.45, "#8db8d9"), (1, "#244b6e")],
        [(0, "#2c4d6e"), (1, "#12263c")],
    )
    rip = ripple(s, "rip", fx=0.006, fy=0.09, scale=7)
    mmask = fade_mask(s, "mmask", 0, 262, 640, 158, top=0.55, bottom=0.05)

    NT.sky(s, [
        (0.0, "#102848"), (0.42, "#2b5885"), (0.76, "#8a7a8c"), (0.92, "#e09a6c"), (1.0, "#ffe09e"),
    ], h=268)
    NT.sun(s, 535, 198, 26, glow="#ffd88a")
    for cx, cy, cw in [(165, 76, 175), (390, 62, 210), (545, 95, 160)]:
        s.add(cloud(rng, cx, cy, cw, col="#fff1dc", shade="#9c7888", op=0.78, cls="city-anim-cloud"))

    NT.mountain(s, "m-mtn", [(-10, 245), (140, 205), (310, 232), (490, 198), (650, 235)],
                262, "#383252", shade="#1e1932", shade_op=0.45, rough=8, depth=4)
    s.add(far_city(rng, 220, 625, 258, 28, 92, "#24304c", wmin=9, wmax=20, lights=0.35))

    top_grp = []
    for bx, bh, bw, ck in [(265, 118, 22, "flat"), (298, 145, 24, "spire"), (332, 108, 20, "slant"), (575, 112, 22, "diamond")]:
        top_grp.append(tower(s, bx, 258, bw, bh, d=6, pat="curtain", lit=0.08, crown_kind=ck))

    lcx, lbase = 108, 258
    stone = s.linear("lh-st", [(0, "#fff6e4"), (0.6, "#e6d2b0"), (1, "#b89b6e")], x1=0, y1=0, x2=1, y2=0)
    gold = s.linear("lh-gd", [(0, "#fff3be"), (0.5, "#e6b43c"), (1, "#8f6214")], x1=0, y1=0, x2=1, y2=0)
    top_grp.extend([
        el("rect", x=lcx - 36, y=lbase - 24, width=72, height=24, rx=3, fill=stone, stroke="#9e8256", stroke_width=0.8),
        el("rect", x=lcx - 28, y=lbase - 18, width=56, height=12, fill="#1b3a59"),
        el("path", d=P([(lcx - 20, lbase - 24), (lcx + 20, lbase - 24), (lcx + 14, 92), (lcx - 14, 92)]), fill=stone),
        el("path", d=P([(lcx - 9, lbase - 24), (lcx + 9, lbase - 24), (lcx + 6, 92), (lcx - 6, 92)]),
           fill=s.linear("lh-core", [(0, "#9ad8f5"), (0.5, "#2b6994"), (1, "#12324d")], x1=0, y1=0, x2=1, y2=0)),
    ])
    for k in range(5):
        y0 = lbase - 32 - k * 28
        y1 = y0 - 20
        w0, w1 = 24 - k * 1.4, 22.5 - k * 1.4
        top_grp.extend([
            el("path", d=f"M{n(lcx - w0)},{n(y0)} Q{n(lcx)},{n(y0 - 6)} {n(lcx + w1)},{n(y1)} "
                         f"L{n(lcx + w1)},{n(y1 + 5)} Q{n(lcx)},{n(y0 - 1)} {n(lcx - w0)},{n(y0 + 5)}Z",
               fill=gold, stroke="#7a5210", stroke_width=0.6),
            el("path", d=f"M{n(lcx - w0)},{n(y0 - 2)} Q{n(lcx)},{n(y0 - 8)} {n(lcx + w1)},{n(y1 - 2)}",
               stroke="#fff7d6", stroke_width=0.8, fill="none"),
        ])
    top_grp.extend([
        el("rect", x=lcx - 18, y=88, width=36, height=5, rx=1.5, fill="#d8b97a"),
        el("rect", x=lcx - 13, y=68, width=26, height=20, fill="#162c42", stroke="#e6b43c", stroke_width=1),
        el("circle", cx=lcx, cy=78, r=7.5, fill="#fff9c4", class_="city-anim-beacon"),
        el("path", d=P([(lcx, 78), (lcx - 105, 42), (lcx - 105, 68)]),
           fill=s.linear("lbeam-l", [(0, "#fff6b8", 0.55), (1, "#fff6b8", 0)], x1=1, y1=0, x2=0, y2=0), class_="city-anim-beacon"),
        el("path", d=P([(lcx, 78), (lcx + 165, 38), (lcx + 165, 72)]),
           fill=s.linear("lbeam-r", [(0, "#fff6b8", 0.55), (1, "#fff6b8", 0)], x1=0, y1=0, x2=1, y2=0), class_="city-anim-beacon"),
        el("path", d=f"M{lcx - 15},68 A15,14 0 0 1 {lcx + 15},68Z", fill=gold),
        el("line", x1=lcx, y1=54, x2=lcx, y2=40, stroke="#fff3be", stroke_width=1.2),
        el("circle", cx=lcx, cy=40, r=1.8, fill="#ff4040", class_="city-anim-beacon"),
        el("rect", x=0, y=256, width=640, height=10, fill="#d8c6a4"),
        el("rect", x=0, y=254.5, width=640, height=2, fill="#f5e6c8"),
    ])
    for ux in (168, 196, 224, 392, 420):
        top_grp.extend([
            el("line", x1=ux, y1=256, x2=ux, y2=244, stroke="#5c4938", stroke_width=1.0),
            el("path", d=f"M{ux - 10},246 Q{ux},239 {ux + 10},246Z", fill="#fbf8f0", stroke="#c99c42", stroke_width=0.6),
        ])
    for px in (36, 152, 248, 372, 455, 545, 612):
        top_grp.append(palm(rng, px, 256, rng.uniform(34, 46), rng.uniform(-5, 5), rng.uniform(16, 22),
                            cols=("#1c5226", "#428c3b"), nfr=11, royal=True, coconuts=False))
    top_grp.append(crowd(rng, 155, 520, 252, 256, 18, 10))
    s.add(g(top_grp, id=s.id("mar-top")))

    s.add(el("rect", x=0, y=264, width=640, height=156, fill=s.linear("mar-sea", [
        (0.0, "#1c5478"), (0.35, "#133f5e"), (0.75, "#0b2940"), (1.0, "#061829"),
    ])))
    s.add(reflection(s, "mar-top", 262, mask=mmask, filt=rip, op=0.55))
    s.add(glitter(rng, 535, 266, 412, 55, 95, col="#ffd98e", w=1.2))
    s.add(water_lines(rng, 10, 630, 268, 414, 90, col="#9edaf5", op=0.3, w=0.9))

    for dy, dx0, dx1 in [(312, 165, 640), (376, 115, 640)]:
        s.add(g([
            el("rect", x=dx0, y=dy, width=dx1 - dx0, height=7, rx=2, fill="#8c5828", stroke="#4a2c11", stroke_width=0.8),
            el("line", x1=dx0, y1=dy + 1.5, x2=dx1, y2=dy + 1.5, stroke="#cfa068", stroke_width=1.0),
            g([el("rect", x=bx, y=dy - 4, width=3, height=5, rx=0.8, fill="#e2e8f0") for bx in range(dx0 + 20, dx1 - 10, 48)]),
            g([el("circle", cx=bx + 1.5, cy=dy - 3, r=0.9, fill="#00f2ff") for bx in range(dx0 + 20, dx1 - 10, 48)]),
        ]))

    s.add(superyacht(275, 310, 128, flip=False))
    s.add(superyacht(475, 310, 118, flip=True))
    s.add(superyacht(235, 374, 148, flip=False))
    s.add(superyacht(465, 374, 155, flip=True))
    s.add(sailboat(68, 342, 34, flip=False))

    vignette_badge(s, t["marina_title"])
    return s.render(t["marina_title"])


# ==============================================================================
# 6. VIGNETTE 2: VIA AURELIA (640 x 420)
# ==============================================================================
def build_boulevard(t: dict[str, str]) -> str:
    s = Scene("boulevard", 640, 420, 606)
    rng = s.rng
    patterns(s, "#0d1b2e")
    glass_gradients(
        s,
        [(0, "#d8eeff"), (0.5, "#74aad4"), (1, "#295278")],
        [(0, "#295278"), (1, "#122940")],
    )

    NT.sky(s, [(0.0, "#123566"), (0.52, "#3572ad"), (0.86, "#96c3e6"), (1.0, "#f3e3c6")], h=235)
    for cx, cy, cw in [(125, 64, 165), (510, 58, 185), (320, 48, 145)]:
        s.add(cloud(rng, cx, cy, cw, col="#ffffff", shade="#c2d6e8", op=0.86, cls="city-anim-cloud"))

    s.add(far_city(rng, 40, 600, 224, 30, 95, "#6c96bd", wmin=10, wmax=22))
    for bx, bh, bw in [(165, 115, 22), (202, 138, 24), (415, 135, 24), (452, 112, 22)]:
        s.add(tower(s, bx, 224, bw, bh, d=6, pat="curtain", lit=0.04, crown_kind="spire", beacon=False))

    marble = s.linear("arch-m", [(0, "#fff8eb"), (0.6, "#e8d6b5"), (1, "#bfa478")], x1=0, y1=0, x2=1, y2=0)
    gold = s.linear("arch-g", [(0, "#fff4c2"), (0.5, "#e5b23a"), (1, "#8f6214")])
    s.add(g([
        el("rect", x=258, y=122, width=124, height=22, fill=marble, stroke="#9e8256", stroke_width=0.9),
        el("rect", x=254, y=118, width=132, height=5, fill=gold),
        el("rect", x=272, y=127, width=96, height=11, fill="#efe0c2", stroke="#b59868", stroke_width=0.6),
        el("ellipse", cx=320, cy=115, rx=18, ry=4, fill=gold),
        el("path", d="M306,115 L310,103 L314,115 M315,115 L320,98 L325,115 M326,115 L330,103 L334,115",
           stroke="#e5b23a", stroke_width=2.2, fill="none"),
        el("circle", cx=320, cy=94, r=3.5, fill="#fff4c2"),
        el("rect", x=262, y=144, width=116, height=80, fill=marble, stroke="#9e8256", stroke_width=0.9),
        el("rect", x=258, y=142, width=124, height=4, fill=gold),
        el("path", d="M302,224 V178 A18,18 0 0 1 338,178 V224Z", fill="#2b5580"),
        el("path", d="M272,224 V192 A9,9 0 0 1 290,192 V224Z M350,224 V192 A9,9 0 0 1 368,192 V224Z", fill="#2b5580"),
        g([el("rect", x=cx - 2, y=146, width=4, height=76, fill="#fffaf0", stroke="#b59868", stroke_width=0.5)
           for cx in (267, 296, 344, 373)]),
    ]))

    s.add(el("rect", x=0, y=224, width=640, height=196, fill=s.linear("road", [
        (0.0, "#cfc2ab"), (0.35, "#9c9182"), (1.0, "#56524c"),
    ])))
    s.add(el("polygon", points="0,224 245,224 75,420 0,420", fill=s.linear("walk-l", [(0, "#efe3ca"), (1, "#cbb894")])))
    s.add(el("polygon", points="395,224 640,224 640,420 565,420", fill=s.linear("walk-r", [(0, "#efe3ca"), (1, "#cbb894")])))
    s.add(el("path", d="M278,224 L145,420 M292,224 L195,420 M348,224 L445,420 M362,224 L495,420",
             stroke="#38e8ff", stroke_width=1.4, stroke_dasharray="10 6", opacity=0.75, fill="none"))

    colonnade = [
        el("polygon", points="0,78 248,168 248,182 0,104", fill=marble, stroke="#9e8256", stroke_width=0.8),
        el("polygon", points="0,72 248,164 248,168 0,78", fill=gold),
        el("polygon", points="640,78 392,168 392,182 640,104", fill=marble, stroke="#9e8256", stroke_width=0.8),
        el("polygon", points="640,72 392,164 392,168 640,78", fill=gold),
    ]
    for i in range(8):
        t_p = (i / 7) ** 1.35
        yb, yt = 228 + t_p * 182, 172 - t_p * 82
        col_h, col_w = yb - yt, 5 + t_p * 14
        for side_x in (242 - t_p * 195, 398 + t_p * 195):
            x0 = side_x - col_w / 2
            colonnade.extend([
                el("rect", x=x0 - col_w * 0.22, y=yb - col_h * 0.06, width=col_w * 1.44, height=col_h * 0.06,
                   fill="#d8c5a0", stroke="#8c7248", stroke_width=0.6),
                el("rect", x=x0, y=yt + col_h * 0.06, width=col_w, height=col_h * 0.88, fill=marble, stroke="#9e8256", stroke_width=0.6),
                el("rect", x=x0 + col_w * 0.62, y=yt + col_h * 0.06, width=col_w * 0.38, height=col_h * 0.88, fill="#8c7248", opacity=0.25),
                el("polygon", points=f"{n(x0 - col_w * 0.25)},{n(yt)} {n(x0 + col_w * 1.25)},{n(yt)} "
                                     f"{n(x0 + col_w)},{n(yt + col_h * 0.06)} {n(x0)},{n(yt + col_h * 0.06)}",
                   fill=gold, stroke="#7a5210", stroke_width=0.5),
            ])
    s.add(g(colonnade))

    s.add(el("polygon", points="314,224 326,224 352,420 288,420", fill="#d8c5a0", stroke="#c99c42", stroke_width=1.2))
    s.add(el("polygon", points="316,224 324,224 344,420 296,420", fill="#195e78"))
    for i in range(5):
        t_m = (i + 0.3) / 5
        my, sc = 232 + t_m * 172, 0.45 + 0.75 * t_m
        s.add(palm(rng, 320, my - 4, 52 * sc, rng.uniform(-3, 3), 24 * sc,
                   cols=("#1c5626", "#46943e"), nfr=11, royal=True, coconuts=False))
        fh = 34 * sc
        s.add(g([
            el("path", d=f"M320,{n(my + 8)} V{n(my + 8 - fh)} "
                         f"M320,{n(my + 8)} Q{n(320 - 8 * sc)},{n(my + 8 - fh * 0.85)} {n(320 - 14 * sc)},{n(my + 8)} "
                         f"M320,{n(my + 8)} Q{n(320 + 8 * sc)},{n(my + 8 - fh * 0.85)} {n(320 + 14 * sc)},{n(my + 8)}",
               stroke="#e0f8ff", stroke_width=1.5 * sc, fill="none", opacity=0.9, class_="flow"),
            el("ellipse", cx=320, cy=my + 8, rx=13 * sc, ry=3.2 * sc, fill="#ffffff", opacity=0.85),
        ]))

    for px, py, sc in [(205, 342, 1.0), (255, 276, 0.58), (412, 318, 0.82)]:
        pw, ph = 64 * sc, 30 * sc
        s.add(g([
            el("ellipse", cx=px, cy=py + ph * 0.52, rx=pw * 0.55, ry=ph * 0.16, fill="#000000", opacity=0.28),
            el("rect", x=px - pw / 2, y=py - ph / 2, width=pw, height=ph, rx=ph * 0.42,
               fill=s.linear(f"pod-{px}", [(0, "#ffffff"), (0.6, "#e6f0f8"), (1, "#9bb4cc")]), stroke="#c99c42", stroke_width=1.0 * sc),
            el("rect", x=px - pw * 0.38, y=py - ph * 0.34, width=pw * 0.76, height=ph * 0.46, rx=ph * 0.18,
               fill=s.linear(f"pwin-{px}", [(0, "#102a45"), (0.5, "#23537d"), (1, "#0d2238")])),
            el("line", x1=px - pw * 0.42, y1=py + ph * 0.25, x2=px + pw * 0.42, y2=py + ph * 0.25, stroke="#00f2ff", stroke_width=1.6 * sc),
            el("circle", cx=px - pw * 0.3, cy=py + ph * 0.36, r=3.2 * sc, fill="#fff6b8"),
            el("circle", cx=px + pw * 0.3, cy=py + ph * 0.36, r=3.2 * sc, fill="#fff6b8"),
        ]))

    s.add(crowd(rng, 55, 165, 285, 395, 14, 22))
    s.add(crowd(rng, 475, 585, 285, 395, 14, 22))

    vignette_badge(s, t["boulevard_title"])
    return s.render(t["boulevard_title"])


# ==============================================================================
# 7. VIGNETTE 3: AEROTROPOLIS (640 x 420)
# ==============================================================================
def build_aerotropolis(t: dict[str, str]) -> str:
    s = Scene("aerotropolis", 640, 420, 707)
    rng = s.rng
    patterns(s, "#091526")
    glass_gradients(
        s,
        [(0, "#ffe4b5"), (0.5, "#6b9bc3"), (1, "#1e3f60")],
        [(0, "#244669"), (1, "#0f2238")],
    )
    b_glow = glow(s, "aglow", 3.5)

    NT.sky(s, [
        (0.0, "#040b1a"), (0.32, "#0d1f3d"), (0.62, "#24436e"), (0.84, "#7d5a68"), (0.95, "#e08b58"), (1.0, "#ffda8a"),
    ], h=258)
    NT.sun(s, 175, 242, 28, glow="#ffcf78")
    s.add(el("path", d="".join(f"M{n(rng.uniform(15, 625))},{n(rng.uniform(10, 95))}h1.2v1.2h-1.2Z" for _ in range(48)),
             fill="#ffffff", opacity=0.65))
    for cx, cy, cw in [(115, 72, 165), (285, 58, 175), (540, 148, 145)]:
        s.add(cloud(rng, cx, cy, cw, col="#ffe9cf", shade="#7a5870", op=0.68, cls="city-anim-cloud"))

    NT.mountain(s, "aero-mtn", [(-10, 248), (115, 198), (245, 232), (420, 188), (565, 224), (650, 242)],
                256, "#2c2846", shade="#161328", shade_op=0.45, rough=8, depth=4)
    s.add(far_city(rng, 18, 622, 256, 22, 68, "#1e2942", wmin=9, wmax=18, lights=0.45))

    acx, acy, arx, ary = 455, 98, 118, 34
    hull_g = s.linear("air-hull", [(0.0, "#ffffff"), (0.35, "#e4eff7"), (0.72, "#9bb5cc"), (1.0, "#3b5875")])
    ribs = " ".join(
        f"M{n(acx + (k - 5) * 19)},{n(acy - ary * math.sqrt(max(0.0, 1 - ((k - 5) * 19 / arx) ** 2)))} "
        f"Q{n(acx + (k - 5) * 21)},{acy} "
        f"{n(acx + (k - 5) * 19)},{n(acy + ary * math.sqrt(max(0.0, 1 - ((k - 5) * 19 / arx) ** 2)))}"
        for k in range(1, 10)
    )
    s.add(g([
        el("polygon", points=f"{acx - arx + 18},{acy - 6} {acx - arx - 14},{acy - 28} {acx - arx + 4},{acy - 28} {acx - arx + 32},{acy - 8}",
           fill="#cbd8e6", stroke="#47627d", stroke_width=0.8),
        el("polygon", points=f"{acx - arx + 18},{acy + 6} {acx - arx - 14},{acy + 26} {acx - arx + 4},{acy + 26} {acx - arx + 32},{acy + 8}",
           fill="#647f99", stroke="#334b63", stroke_width=0.8),
        el("ellipse", cx=acx, cy=acy, rx=arx, ry=ary, fill=hull_g, stroke="#64829e", stroke_width=0.9),
        el("path", d=ribs, stroke="#7a96b0", stroke_width=0.6, fill="none", opacity=0.55),
        el("path", d=f"M{acx - arx + 6},{acy + 3} Q{acx},{acy + 8} {acx + arx - 6},{acy + 2}", stroke="#eab308", stroke_width=2.0, fill="none"),
        el("path", d=f"M{acx - arx + 8},{acy + 6} Q{acx},{acy + 11} {acx + arx - 8},{acy + 5}", stroke="#00f2ff", stroke_width=1.0, fill="none"),
        el("path", d=P([(acx - 48, acy + ary - 3), (acx + 42, acy + ary - 3), (acx + 34, acy + ary + 11), (acx - 40, acy + ary + 11)]),
           fill="#1e344d", stroke="#9bb5cc", stroke_width=0.8),
        el("path", d="".join(f"M{acx - 34 + k * 9},{acy + ary + 1}h6v5h-6Z" for k in range(8)), fill="#ffe89e"),
        el("ellipse", cx=acx - 22, cy=acy + ary - 1, rx=7, ry=3, fill="#334b63", stroke="#00f2ff", stroke_width=0.9),
        el("ellipse", cx=acx + 28, cy=acy + ary - 2, rx=7, ry=3, fill="#334b63", stroke="#00f2ff", stroke_width=0.9),
    ], class_="city-anim-cloud"))

    mx = 578
    s.add(g([
        el("path", d=P([(mx - 9, 256), (mx + 9, 256), (mx + 3, 96), (mx - 3, 96)]), fill="none", stroke="#cbd5e1", stroke_width=1.3),
        el("path", d="".join(
            f"M{mx - 8 + k * 0.5},{252 - k * 14}L{mx + 8 - k * 0.5},{238 - k * 14}"
            f"M{mx + 8 - k * 0.5},{252 - k * 14}L{mx - 8 + k * 0.5},{238 - k * 14}"
            for k in range(11)
        ), stroke="#94a3b8", stroke_width=0.8, fill="none"),
        el("circle", cx=mx, cy=96, r=3.5, fill="#f59e0b"),
        el("line", x1=acx + arx, y1=acy, x2=mx, y2=96, stroke="#f59e0b", stroke_width=1.4),
    ]))

    for dx, dy, dr in [(68, 198, 30), (142, 210, 22)]:
        s.add(g([
            el("path", d=P([(dx - dr * 0.35, 256), (dx + dr * 0.35, 256), (dx + 4, dy + 4), (dx - 4, dy + 4)]), fill="#334155"),
            el("path", d=f"M{n(dx - dr)},{n(dy - dr * 0.35)} Q{n(dx - dr * 0.15)},{n(dy + dr * 0.65)} {n(dx + dr * 0.85)},{n(dy - dr * 0.65)} "
                         f"L{n(dx + dr * 0.72)},{n(dy - dr * 0.78)} Q{n(dx - dr * 0.1)},{n(dy + dr * 0.25)} {n(dx - dr * 0.88)},{n(dy - dr * 0.48)}Z",
               fill=s.linear(f"dish-{dx}", [(0, "#f8fafc"), (0.6, "#cbd5e1"), (1, "#64748b")]), stroke="#475569", stroke_width=0.9),
            el("path", d=f"M{n(dx - dr * 0.6)},{n(dy - dr * 0.35)} L{n(dx - dr * 0.1)},{n(dy - dr * 0.95)} L{n(dx + dr * 0.55)},{n(dy - dr * 0.55)}",
               stroke="#94a3b8", stroke_width=1.0, fill="none"),
            el("circle", cx=dx - dr * 0.1, cy=dy - dr * 0.95, r=2.4, fill="#00f2ff", class_="city-anim-beacon"),
        ]))
    s.add(g([
        el("rect", x=182, y=238, width=32, height=18, fill="#334155"),
        el("path", d="M180,238 A18,18 0 1 1 216,238Z", fill=s.radial("radome", [(0, "#ffffff"), (0.7, "#cbd5e1"), (1, "#64748b")])),
        el("path", d=P([(258, 256), (270, 256), (267, 168), (261, 168)]), fill="#cbd5e1"),
        el("polygon", points="252,168 276,168 280,156 248,156", fill="#0f2942", stroke="#e2e8f0", stroke_width=1.0),
        el("rect", x=246, y=153, width=36, height=3, rx=1, fill="#f8fafc"),
        el("line", x1=264, y1=153, x2=264, y2=136, stroke="#e2e8f0", stroke_width=1.0),
        el("circle", cx=264, cy=136, r=1.6, fill="#ff4040", class_="city-anim-beacon"),
        el("path", d="M235,256 V222 Q375,198 515,222 V256Z",
           fill=s.linear("sp-glass", [(0, "#ffd89b", 0.85), (0.5, "#386b94", 0.85), (1, "#122b45", 0.92)])),
        el("path", d="M235,256 V222 Q375,198 515,222 V256Z", fill=s.url("curtain"), opacity=0.7),
        el("path", d="M220,225 Q305,196 375,212 Q445,196 530,225 L522,231 Q445,204 375,218 Q305,204 228,231Z",
           fill=s.linear("sp-roof", [(0, "#f8fafc"), (0.5, "#cbd5e1"), (1, "#64748b")])),
    ]))
    for px in (22, 108, 224, 532, 608):
        s.add(palm(rng, px, 256, rng.uniform(32, 44), rng.uniform(-5, 5), rng.uniform(15, 20),
                   cols=("#184522", "#387832"), nfr=10, royal=True, coconuts=False))

    s.add(el("rect", x=0, y=256, width=640, height=164, fill=s.linear("apron", [
        (0.0, "#1e293b"), (0.45, "#151f30"), (1.0, "#0b111d"),
    ])))
    rwy = [f"M{n(320 + k * 36)},256 L{n(320 + k * 145)},420" for k in range(-6, 7)]
    rwy += [f"M0,{n(256 + 164 * (r / 7) ** 1.4)}H640" for r in range(1, 8)]
    s.add(el("path", d=" ".join(rwy), stroke="#334155", stroke_width=0.7, opacity=0.65, fill="none"))
    s.add(el("path", d="M250,256 L45,420 M390,256 L595,420", stroke="#00f2ff", stroke_width=1.8, stroke_dasharray="4 10", opacity=0.85))
    s.add(el("path", d="M320,258 L320,420", stroke="#fbbf24", stroke_width=2.6, stroke_dasharray="18 12", opacity=0.9))
    s.add(crowd(rng, 255, 495, 258, 266, 9, 14))

    scx, scy = 320, 336
    shuttle_body = s.linear("sh-body", [(0, "#ffffff"), (0.55, "#e2edf7"), (0.85, "#94afc9"), (1, "#3b5570")])
    s.add(g([
        el("ellipse", cx=scx, cy=scy + 34, rx=132, ry=16, fill="#020617", opacity=0.65),
        el("polygon", points=f"{scx},{scy - 56} {scx + 42},{scy - 14} {scx + 132},{scy + 24} {scx + 122},{scy + 30} "
                             f"{scx},{scy + 20} {scx - 122},{scy + 30} {scx - 132},{scy + 24} {scx - 42},{scy - 14}",
           fill="#111827", stroke="#374151", stroke_width=0.8),
        el("polygon", points=f"{scx},{scy - 52} {scx + 36},{scy - 12} {scx + 124},{scy + 23} {scx + 76},{scy + 26} "
                             f"{scx},{scy + 22} {scx - 76},{scy + 26} {scx - 124},{scy + 23} {scx - 36},{scy - 12}",
           fill=shuttle_body, stroke="#64829e", stroke_width=0.9),
        el("path", d=f"M{scx},{scy - 52} L{scx + 18},{scy + 22} L{scx - 18},{scy + 22}Z",
           fill=s.linear("sh-spine", [(0, "#ffffff"), (1, "#cbd8e6")])),
        el("path", d=f"M{scx - 24},{scy - 2} L{scx - 108},{scy + 22} M{scx + 24},{scy - 2} L{scx + 108},{scy + 22}",
           stroke="#eab308", stroke_width=2.2),
        el("polygon", points=f"{scx - 26},{scy + 18} {scx - 42},{scy - 16} {scx - 32},{scy - 16} {scx - 18},{scy + 18}",
           fill="#dbe7f3", stroke="#47627d", stroke_width=0.8),
        el("polygon", points=f"{scx + 26},{scy + 18} {scx + 42},{scy - 16} {scx + 32},{scy - 16} {scx + 18},{scy + 18}",
           fill="#94afc9", stroke="#47627d", stroke_width=0.8),
        el("polygon", points=f"{scx},{scy - 36} {scx + 11},{scy - 22} {scx + 7},{scy - 17} {scx - 7},{scy - 17} {scx - 11},{scy - 22}",
           fill="#0c2238", stroke="#7ef6ff", stroke_width=0.8),
        el("rect", x=scx - 1.5, y=scy + 18, width=3, height=14, fill="#94a3b8"),
        el("circle", cx=scx, cy=scy + 33, r=3.5, fill="#0f172a", stroke="#64748b", stroke_width=1),
        el("rect", x=scx - 44, y=scy + 22, width=3, height=11, fill="#94a3b8"),
        el("circle", cx=scx - 42.5, cy=scy + 33, r=3.8, fill="#0f172a", stroke="#64748b", stroke_width=1),
        el("rect", x=scx + 41, y=scy + 22, width=3, height=11, fill="#94a3b8"),
        el("circle", cx=scx + 42.5, cy=scy + 33, r=3.8, fill="#0f172a", stroke="#64748b", stroke_width=1),
        el("ellipse", cx=scx - 10, cy=scy + 22, rx=4.5, ry=2.5, fill="#00f2ff", filter=b_glow, class_="city-anim-beacon"),
        el("ellipse", cx=scx, cy=scy + 22, rx=5.5, ry=3.0, fill="#ffffff", filter=b_glow, class_="city-anim-beacon"),
        el("ellipse", cx=scx + 10, cy=scy + 22, rx=4.5, ry=2.5, fill="#00f2ff", filter=b_glow, class_="city-anim-beacon"),
    ]))

    vignette_badge(s, t["aerotropolis_title"])
    return s.render(t["aerotropolis_title"])


# ==============================================================================
# 8. VIGNETTE 4: NIGHT-LAGOON (640 x 420)
# ==============================================================================
def build_night_lagoon(t: dict[str, str]) -> str:
    s = Scene("night-lagoon", 640, 420, 808)
    rng = s.rng
    patterns(s, "#040914")
    glass_gradients(
        s,
        [(0, "#142c4c"), (0.5, "#0d2038"), (1, "#071324")],
        [(0, "#0a182c"), (1, "#040c18")],
    )
    rip = ripple(s, "rip", fx=0.006, fy=0.09, scale=8)
    nmask = fade_mask(s, "nmask", 0, 238, 640, 182, top=0.65, bottom=0.06)
    b_glow = glow(s, "nglow", 4.5)

    NT.sky(s, [(0.0, "#030712"), (0.45, "#081428"), (0.78, "#102544"), (1.0, "#193860")], h=242)
    s.add(el("path", d="".join(f"M{n(rng.uniform(10, 630))},{n(rng.uniform(8, 165))}h1.3v1.3h-1.3Z" for _ in range(75)),
             fill="#e2f1ff", opacity=0.8))
    s.add(el("circle", cx=548, cy=64, r=42, fill=s.radial("m-halo", [(0, "#fef3c7", 0.32), (0.5, "#7dd3fc", 0.1), (1, "#081428", 0)])))
    s.add(el("path", d="M540,46 A19,19 0 1 0 562,76 A15,15 0 1 1 540,46Z", fill="#fef9c3"))

    night_city = [far_city(rng, 10, 630, 238, 35, 110, "#081526", wmin=10, wmax=22, lights=1.1, light_col="#ffd88a")]
    for bx, bh, bw, ck in [
        (28, 125, 22, "flat"), (58, 152, 26, "spire"), (92, 118, 22, "slant"), (185, 138, 24, "diamond"),
        (218, 168, 26, "stepped"), (365, 145, 24, "garden"), (438, 162, 26, "spire"), (472, 128, 22, "flat"),
        (502, 148, 24, "diamond"), (585, 118, 22, "slant"),
    ]:
        night_city.append(tower(s, bx, 238, bw, bh, d=6, pat="curtain", lit=0.26, crown_kind=ck, lit_col="#ffdc8a"))
        night_city.append(el("rect", x=bx, y=238 - bh, width=bw, height=bh, fill="none", stroke="#00f2ff", stroke_width=0.5, opacity=0.55))

    night_city.extend(pyramid(s, (150, 142), (118, 238), (152, 238), (182, 238), tiers=4, cap=0.15, scale=0.45, lights=True))
    night_city.append(el("path", d=P([(148, 142), (152, 142), (158, 20), (142, 20)]),
                         fill=s.linear("n-beam", [(0, "#fef08a", 0.7), (1, "#fef08a", 0)]), class_="city-anim-beacon"))
    night_city.append(sky_city(s, 292, 238, 24))
    night_city.append(twisted_tower(s, 335, 238, 14, 165, twist=math.pi / 2, floors=38,
                                    cols=("#1e3f66", "#122844", "#081526"), lit=0.22, crown_h=14))
    night_city.append(el("rect", x=0, y=234, width=640, height=6, fill="#0f2136"))
    night_city.append(el("path", d="".join(f"M{x},235.5h14v2.5h-14Z" for x in range(12, 630, 24)), fill="#00f2ff", opacity=0.9))
    s.add(g(night_city, id=s.id("ncity")))

    s.add(el("rect", x=0, y=240, width=640, height=180, fill=s.linear("n-sea", [
        (0.0, "#071d33"), (0.4, "#051628"), (0.8, "#030e1c"), (1.0, "#020812"),
    ])))
    s.add(reflection(s, "ncity", 239, mask=nmask, filt=rip, op=0.68))

    bio_grp = []
    for path_d, col, sw, op in [
        ("M-10,258 C110,248 210,272 340,256 C460,242 545,268 650,254", "#00f7ff", 3.2, 0.75),
        ("M-10,286 C135,302 255,274 395,292 C505,306 575,282 650,294", "#10b981", 2.6, 0.65),
        ("M-10,322 C95,308 230,338 360,318 C485,298 565,332 650,316", "#00f7ff", 4.0, 0.85),
        ("M-10,364 C140,382 285,348 430,372 C535,388 595,358 650,374", "#2dd4bf", 3.4, 0.72),
        ("M-10,398 C165,384 325,412 475,392 C555,382 605,404 650,396", "#00f7ff", 4.5, 0.88),
    ]:
        bio_grp.append(el("path", d=path_d, stroke=col, stroke_width=sw * 2.8, fill="none", opacity=op * 0.32))
        bio_grp.append(el("path", d=path_d, stroke=col, stroke_width=sw, fill="none", opacity=op, stroke_linecap="round"))
    sparks = "".join(
        f"M{n(rng.uniform(8, 632))},{n(rng.uniform(246, 414))}h{n(rng.uniform(1.5, 4.5))}v1.4h-{n(rng.uniform(1.5, 4.5))}Z"
        for _ in range(140)
    )
    bio_grp.append(el("path", d=sparks, fill="#7ef9ff", opacity=0.85))
    s.add(g(bio_grp, filter=b_glow, class_="city-anim-biolum"))

    tx, ty = 215, 302
    s.add(g([
        el("path", d=f"M{tx - 32},{ty + 2} Q{tx - 95},{ty - 6} {tx - 165},{ty - 14} M{tx - 32},{ty + 2} Q{tx - 95},{ty + 12} {tx - 175},{ty + 24}",
           stroke="#00f7ff", stroke_width=2.4, fill="none", filter=b_glow, class_="city-anim-biolum"),
        el("path", d=f"M{tx - 34},{ty + 2} L{tx + 28},{ty + 2} L{tx + 38},{ty - 6} L{tx - 28},{ty - 6}Z",
           fill="#f1f5f9", stroke="#00f7ff", stroke_width=1.0),
        el("path", d=f"M{tx - 18},{ty - 6} L{tx + 18},{ty - 6} L{tx + 12},{ty - 13} L{tx - 14},{ty - 13}Z",
           fill="#0f2942", stroke="#7ef9ff", stroke_width=0.8),
        el("rect", x=tx - 12, y=ty - 11, width=20, height=3.5, rx=1, fill="#fef08a"),
    ]))

    bw_top = "M-10,368 Q180,328 365,348 T650,336"
    bw_bot = "L650,358 Q465,370 365,368 Q180,348 -10,392Z"
    orb_glow = s.radial("orb-g", [(0, "#fffbeb", 0.95), (0.4, "#fbbf24", 0.45), (1, "#fbbf24", 0)])
    boardwalk = [
        el("path", d=bw_top, stroke="#00f7ff", stroke_width=5, fill="none", opacity=0.55, filter=b_glow),
        el("path", d=f"{bw_top} {bw_bot}", fill=s.linear("bw-wood", [(0, "#5c3a21"), (0.5, "#3d2616"), (1, "#24150b")]),
           stroke="#eab308", stroke_width=1.2),
        el("path", d="M-10,356 Q180,316 365,336 T650,324", stroke="#eab308", stroke_width=1.1, fill="none", opacity=0.85),
    ]
    for i in range(9):
        lx = 32 + i * 72
        ly = 358 - 18 * math.sin(math.pi * lx / 640) - (lx / 640) * 16
        boardwalk.extend([
            el("line", x1=lx, y1=ly + 8, x2=lx, y2=ly - 10, stroke="#d97706", stroke_width=1.2),
            el("circle", cx=lx, cy=ly - 12, r=14, fill=orb_glow),
            el("circle", cx=lx, cy=ly - 12, r=3.8, fill="#fffbeb", stroke="#f59e0b", stroke_width=0.8, class_="city-anim-beacon"),
        ])
    for px, py in [(112, 355), (124, 354), (278, 344), (290, 345), (465, 348), (478, 347)]:
        boardwalk.append(person(px, py, 16, col="#091322", rng=rng))
    s.add(g(boardwalk))

    vignette_badge(s, t["night_title"], accent="#00f7ff", bg="#061528")
    return s.render(t["night_title"])


# ==============================================================================
# LOCALIZED DICTIONARY AND PAGE INJECTION
# ==============================================================================
LABELS = {
    "en": {
        "skyline_title": "Nova Aurelia Imperial Lagoon Panorama",
        "sky_city": "Sky City (956 m)",
        "infinity_tower": "Infinity Tower",
        "gov_center": "World Government Center",
        "clock_tower": "Royal Clock Tower",
        "pyramid_monument": "Grand Sovereign Pyramid",
        "marina_aurelia": "Marina Aurelia",
        "monorail_line": "Trans-Lagoon Monorail",
        "pyramid_title": "The Grand Sovereign Pyramid and Royal Court",
        "apex_beacon": "Apex Beacon and Hall of Nations",
        "hanging_gardens": "Cascading Terraces and Waterfalls",
        "solar_skin": "Solar-Glass Photovoltaic Skin",
        "amphitheater": "Sovereign Assembly Amphitheater",
        "colonnade": "Ceremonial Colonnade and Pools",
        "undersea_title": "Trans-Lagoon Maglev and Marine Concourse",
        "surface_terminal": "Surface Harbor Terminal",
        "acrylic_tube": "Acrylic Vacuum Transit Tube",
        "maglev_train": "High-Speed Maglev Train",
        "coral_sanctuary": "Protected Living Coral Sanctuary",
        "obs_dome": "Subsea Observation Concourse",
        "archipelago_title": "Archipelago Masterplan: Palm Island, World Isles and Chameleon Atolls",
        "palm_island": "Palm Island",
        "hotel_khalifa": "Hotel Khalifa and Waterpark",
        "world_islands": "World Islands (130 Isles)",
        "chameleon_atolls": "Chameleon Research Atolls",
        "subsea_maglev": "Subsea Transit Conduits",
        "mainland_aurelia": "Mainland Nova Aurelia",
        "coral_barrier": "Bio-Calcified Barrier Reef",
        "marina_title": "Marina Aurelia and Royal Yacht Basin",
        "boulevard_title": "Via Aurelia and Ceremonial Forum",
        "aerotropolis_title": "Aurelia Spaceport and Stratospheric Skyport",
        "night_title": "The Bioluminescent Smart Lagoon",
    },
    "hu": {
        "skyline_title": "Nova Aurelia Császári Lagúna Panoráma",
        "sky_city": "Sky City (956 m)",
        "infinity_tower": "Infinity Torony",
        "gov_center": "Világkormányzati Központ",
        "clock_tower": "Királyi Óratorony",
        "pyramid_monument": "Nagy Szuverén Piramis",
        "marina_aurelia": "Marina Aurelia",
        "monorail_line": "Lagúna Egysínű Vasút",
        "pyramid_title": "A Nagy Szuverén Piramis és Királyi Udvar",
        "apex_beacon": "Csúcsfényszóró és Nemzetek Csarnoka",
        "hanging_gardens": "Lépcsős Függőkertek és Vízesések",
        "solar_skin": "Napelemes Üveghomlokzat",
        "amphitheater": "Szuverén Nemzetgyűlési Amfiteátrum",
        "colonnade": "Díszkolonnád és Tükörmedencék",
        "undersea_title": "Lagúna alatti Maglev és Tenger alatti Terminál",
        "surface_terminal": "Felszíni Kikötői Terminál",
        "acrylic_tube": "Akril Vákuumcsöves Pályatest",
        "maglev_train": "Nagysebességű Maglev Vonat",
        "coral_sanctuary": "Védett Élő Korallzátony",
        "obs_dome": "Tenger alatti Megfigyelő Dóm",
        "archipelago_title": "Szigetvilág Mesterterv: Palm Island, Világszigetek és Kaméleon Atollok",
        "palm_island": "Palm Island",
        "hotel_khalifa": "Hotel Khalifa és Vízipark",
        "world_islands": "Világszigetek (130 Sziget)",
        "chameleon_atolls": "Kaméleon Kutatóatollok",
        "subsea_maglev": "Tenger alatti Tranzitcsövek",
        "mainland_aurelia": "Nova Aurelia Szárazföld",
        "coral_barrier": "Biokalcit Védőzátony",
        "marina_title": "Marina Aurelia és Királyi Jachtkikötő",
        "boulevard_title": "Via Aurelia és Ceremoniális Fórum",
        "aerotropolis_title": "Aurelia Űrkikötő és Sztratoszférikus Repülőtér",
        "night_title": "A Biolumineszcens Okos Lagúna",
    },
}

BUILDERS = {
    "skyline": build_skyline,
    "pyramid": build_pyramid,
    "undersea-hub": build_undersea_hub,
    "archipelago-map": build_archipelago_map,
    "marina": build_marina,
    "boulevard": build_boulevard,
    "aerotropolis": build_aerotropolis,
    "night-lagoon": build_night_lagoon,
}

CONTAINER_RE = r'(<div[^>]*\bdata-city-svg="{key}"[^>]*>\s*)<svg\b.*?</svg>(\s*</div>)'


def validate(svg: str, key: str) -> None:
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        sys.exit(f"Error: generated SVG '{key}' is invalid XML: {exc}")


def inline(svg: str) -> str:
    return re.sub(r'\s+xmlns="http://www\.w3\.org/2000/svg"', "", svg, count=1)


def update_pages(rendered: dict[str, dict[str, str]]) -> None:
    from build_pages import format_and_remove_empty_lines

    for lang in ("en", "hu"):
        path = ROOT / lang / "nova-aurelia.html"
        if not path.exists():
            print(f"  ! {path.relative_to(ROOT)} does not exist yet, skipping injection")
            continue
        text = path.read_text(encoding="utf-8")
        for key, svg in rendered[lang].items():
            pattern = re.compile(CONTAINER_RE.format(key=key), re.S)
            match = pattern.search(text)
            if not match:
                print(f'  ! no data-city-svg="{key}" container in {path.relative_to(ROOT)}')
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
