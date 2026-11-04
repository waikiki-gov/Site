#!/usr/bin/env python3
"""Shared vector drawing utilities and HTML card/chart injection helpers for site SVGs."""

from __future__ import annotations

import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def n(val: float) -> str:
    """Format float cleanly with at most one decimal place, stripping trailing zeros."""
    return f"{val:.1f}".rstrip("0").rstrip(".")


def rnd(i: int, seed: float = 1.0) -> float:
    """Deterministic pseudo-random float in [0, 1)."""
    return (math.sin(i * 12.9898 + seed * 78.233) * 43758.5453) % 1.0


def poly(pts: list[tuple[float, float]], close: bool = True) -> str:
    """Format list of (x, y) coordinates into SVG path data."""
    body = " ".join(f"{'L' if idx else 'M'}{n(x)},{n(y)}" for idx, (x, y) in enumerate(pts))
    return f"{body} Z" if close else body


def subdiv_ridge(
    p1: tuple[float, float],
    p2: tuple[float, float],
    roughness: float = 8.0,
    seed: float = 1.0,
    steps: int = 8,
) -> list[tuple[float, float]]:
    """Subdivide a straight segment into a jagged, natural mountain ridge."""
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


def validate_svg(svg_str: str, label: str) -> None:
    """Validate that the SVG string parses cleanly as valid XML."""
    xml_ready = re.sub(r"\bdata-reveal(?!=)", 'data-reveal=""', svg_str)
    try:
        ET.fromstring(xml_ready)
    except ET.ParseError as exc:
        sys.exit(f"XML ParseError in {label}: {exc}")


def update_page_cards(html_path: Path, container_class: str, card_svgs: list[str]) -> None:
    """Replace all card <svg> elements inside container_class with generated card_svgs."""
    try:
        from build_pages import format_and_remove_empty_lines
    except ImportError:
        sys.path.insert(0, str(ROOT / "scripts"))
        from build_pages import format_and_remove_empty_lines

    for idx, svg in enumerate(card_svgs):
        validate_svg(svg, f"{html_path.name} card {idx}")

    text = html_path.read_text(encoding="utf-8")
    pattern = re.compile(rf'(<div class="{container_class}"[^>]*>\s*)<svg\b[^>]*>[\s\S]*?</svg>', re.S)
    matches = list(pattern.finditer(text))

    if len(matches) != len(card_svgs):
        sys.exit(f"Error in {html_path.name}: expected {len(card_svgs)} <div class=\"{container_class}\"> cards, found {len(matches)}")

    # Replace from back to front to preserve character indices
    for match, svg in reversed(list(zip(matches, card_svgs))):
        start = match.start(0)
        end = match.end(0)
        prefix = match.group(1)
        text = text[:start] + prefix + svg + text[end:]

    formatted = format_and_remove_empty_lines(text)
    html_path.write_text(formatted, encoding="utf-8")
    print(f"Updated {len(card_svgs)} cards in {html_path.resolve().relative_to(ROOT)}")


def update_page_chart(html_path: Path, chart_svg: str) -> None:
    """Replace the height chart <svg class="ill height-chart" ...> in html_path."""
    try:
        from build_pages import format_and_remove_empty_lines
    except ImportError:
        sys.path.insert(0, str(ROOT / "scripts"))
        from build_pages import format_and_remove_empty_lines

    validate_svg(chart_svg, f"{html_path.name} height chart")
    text = html_path.read_text(encoding="utf-8")
    pattern = re.compile(r'<svg class="ill height-chart"[\s\S]*?</svg>', re.S)
    match = pattern.search(text)
    if not match:
        sys.exit(f"Error in {html_path.name}: height-chart <svg> not found")

    text = text[: match.start()] + chart_svg + text[match.end() :]
    formatted = format_and_remove_empty_lines(text)
    html_path.write_text(formatted, encoding="utf-8")
    print(f"Updated height chart in {html_path.resolve().relative_to(ROOT)}")
