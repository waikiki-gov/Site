#!/usr/bin/env python3
"""
Pure-Python procedural texture baking for the site's SVG illustrations.

SVG files linked through <img> cannot load external resources, and live
feTurbulence filters are re-rasterized on every animation frame. These helpers
therefore bake small, tileable PNG textures (and lit planet discs) once and
return them as base64 data URIs that can be embedded in an SVG <pattern> or
<image>.
"""

from __future__ import annotations

import base64
import math
import random
import struct
import zlib
from functools import lru_cache


# ==============================================================================
# PNG ENCODER
# ==============================================================================
def _png(width: int, height: int, rows: list[bytes], color_type: int) -> bytes:
    """Encode raw scanlines (without filter bytes) as a PNG using the Sub filter."""
    bpp = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    raw = bytearray()
    for row in rows:
        raw.append(1)  # Sub filter compresses smooth gradients far better than None
        prev = [0] * bpp
        for i, v in enumerate(row):
            raw.append((v - prev[i % bpp]) & 0xFF)
            prev[i % bpp] = v
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")


def data_uri(png: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png).decode("ascii")


def _clamp(v: float) -> int:
    return 0 if v < 0 else 255 if v > 255 else int(v)


# ==============================================================================
# NOISE
# ==============================================================================
def _fade(t: float) -> float:
    return t * t * (3 - 2 * t)


class TileNoise:
    """Tileable 2D value noise (lattice wraps with the given period)."""

    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.cache: dict[int, list[float]] = {}

    def lattice(self, period: int) -> list[float]:
        if period not in self.cache:
            self.cache[period] = [self.rng.random() for _ in range(period * period)]
        return self.cache[period]

    def sample(self, u: float, v: float, px: int, py: int | None = None) -> float:
        """u, v in [0, 1); px/py lattice periods."""
        py = py or px
        lat = self.lattice(max(px, py))
        p = max(px, py)
        x, y = u * px, v * py
        x0, y0 = int(x), int(y)
        fx, fy = _fade(x - x0), _fade(y - y0)
        x0 %= px
        y0 %= py
        x1, y1 = (x0 + 1) % px, (y0 + 1) % py
        a = lat[y0 * p + x0]
        b = lat[y0 * p + x1]
        c = lat[y1 * p + x0]
        d = lat[y1 * p + x1]
        return (a + (b - a) * fx) + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fy

    def fbm(self, u, v, base_x, base_y=None, octaves=5, gain=0.5):
        base_y = base_y or base_x
        amp, tot, norm = 1.0, 0.0, 0.0
        fx, fy = base_x, base_y
        for _ in range(octaves):
            tot += amp * self.sample(u, v, fx, fy)
            norm += amp
            amp *= gain
            fx *= 2
            fy *= 2
        return tot / norm


class Noise3:
    """3D value noise used to texture spheres without seams."""

    def __init__(self, seed: int):
        rng = random.Random(seed)
        perm = list(range(256))
        rng.shuffle(perm)
        self.perm = perm + perm
        self.vals = [rng.random() for _ in range(256)]

    def noise(self, x: float, y: float, z: float) -> float:
        p, vals = self.perm, self.vals
        xi, yi, zi = math.floor(x), math.floor(y), math.floor(z)
        fx, fy, fz = _fade(x - xi), _fade(y - yi), _fade(z - zi)
        xi &= 255
        yi &= 255
        zi &= 255
        a = p[xi] + yi
        b = p[xi + 1] + yi
        aa, ab, ba, bb = p[a] + zi, p[a + 1] + zi, p[b] + zi, p[b + 1] + zi
        v000, v100 = vals[p[aa]], vals[p[ba]]
        v010, v110 = vals[p[ab]], vals[p[bb]]
        v001, v101 = vals[p[aa + 1]], vals[p[ba + 1]]
        v011, v111 = vals[p[ab + 1]], vals[p[bb + 1]]
        x00 = v000 + (v100 - v000) * fx
        x10 = v010 + (v110 - v010) * fx
        x01 = v001 + (v101 - v001) * fx
        x11 = v011 + (v111 - v011) * fx
        y0 = x00 + (x10 - x00) * fy
        y1 = x01 + (x11 - x01) * fy
        return y0 + (y1 - y0) * fz

    def fbm(self, x, y, z, octaves=5, gain=0.5, lac=2.03):
        amp, tot, norm = 1.0, 0.0, 0.0
        for _ in range(octaves):
            tot += amp * self.noise(x, y, z)
            norm += amp
            amp *= gain
            x, y, z = x * lac, y * lac, z * lac
        return tot / norm


# ==============================================================================
# TILEABLE SURFACE TEXTURES (grayscale, centred on mid-grey for blend modes)
# ==============================================================================
@lru_cache(maxsize=None)
def grain_tile(size: int = 112, seed: int = 7, strength: float = 46) -> str:
    """Photographic film grain: mid-grey with per-pixel gaussian deviation."""
    rng = random.Random(seed)
    rows = [bytes(_clamp(128 + rng.gauss(0, strength)) for _ in range(size)) for _ in range(size)]
    return data_uri(_png(size, size, rows, 0))


@lru_cache(maxsize=None)
def relief_tile(size: int = 160, seed: int = 11, base: int = 5, octaves: int = 5,
                aniso: float = 1.0, contrast: float = 3.2) -> str:
    """Embossed fBm height field lit from the upper left (rock, soil, bark grain)."""
    nz = TileNoise(seed)
    bx, by = base, max(1, int(round(base * aniso)))
    h = [[nz.fbm(x / size, y / size, bx, by, octaves) for x in range(size)] for y in range(size)]
    rows = []
    lx, ly, lz = -0.62, -0.62, 0.48
    for y in range(size):
        row = bytearray()
        for x in range(size):
            dx = (h[y][(x + 1) % size] - h[y][(x - 1) % size]) * size * 0.5 / base
            dy = (h[(y + 1) % size][x] - h[(y - 1) % size][x]) * size * 0.5 / base
            nx, ny, nzv = -dx * contrast, -dy * contrast, 1.0
            m = math.sqrt(nx * nx + ny * ny + nzv * nzv)
            shade = (nx * lx + ny * ly + nzv * lz) / m
            row.append(_clamp(128 + (shade - lz) * 260 + (h[y][x] - 0.5) * 70))
        rows.append(bytes(row))
    return data_uri(_png(size, size, rows, 0))


@lru_cache(maxsize=None)
def ripple_tile(w: int = 192, h: int = 64, seed: int = 21) -> str:
    """Horizontally stretched shimmering ripple field for open water."""
    nz = TileNoise(seed)
    rows = []
    for y in range(h):
        row = bytearray()
        for x in range(w):
            v = nz.fbm(x / w, y / h, 3, 6, 4)
            band = math.sin((y / h) * math.tau * 6 + v * 7.5)
            row.append(_clamp(128 + band * 58 + (v - 0.5) * 60))
        rows.append(bytes(row))
    return data_uri(_png(w, h, rows, 0))


# ==============================================================================
# LIT PLANET DISCS (RGBA)
# ==============================================================================
def _lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _ramp(stops, t):
    t = max(0.0, min(1.0, t))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            return _lerp(c0, c1, (t - t0) / ((t1 - t0) or 1))
    return stops[-1][1]


def _norm(v):
    m = math.sqrt(sum(c * c for c in v)) or 1
    return tuple(c / m for c in v)


def render_planet(kind: str, size: int, seed: int, light=(-0.62, -0.48, 0.62), halo: float = 0.0,
                  spin: float = 0.0) -> str:
    """
    Render an orthographic, Lambert-lit planet disc of the given pixel size.
    kind: 'earth' | 'moon' | 'mars'. halo adds an atmospheric glow ring (fraction of radius).
    """
    lx, ly, lz = _norm(light)
    n3 = Noise3(seed)
    n3c = Noise3(seed + 101)
    rng = random.Random(seed)
    craters = []
    if kind == "moon":
        for _ in range(70):
            u, v = rng.uniform(-1, 1), rng.uniform(-1, 1)
            w = rng.uniform(-1, 1)
            c = _norm((u, v, w))
            craters.append((c, rng.uniform(0.03, 0.16) * (rng.random() ** 1.6) + 0.025))
    total = size * (1 + halo)
    W = int(round(total))
    R = size / 2
    C = W / 2
    cs, sn = math.cos(spin), math.sin(spin)
    rows = []
    for py in range(W):
        row = bytearray()
        for px in range(W):
            x = (px + 0.5 - C) / R
            y = (py + 0.5 - C) / R
            d2 = x * x + y * y
            if d2 > 1.0:
                # Atmospheric halo glow outside the limb
                if halo > 0:
                    dist = math.sqrt(d2) - 1
                    a = max(0.0, 1 - dist / halo) ** 2.4
                    face = max(0.0, (x * lx + y * ly) / math.sqrt(d2) * 0.7 + 0.45)
                    col = {"earth": (110, 190, 255), "mars": (240, 170, 140), "moon": (220, 230, 235)}[kind]
                    alpha = a * face * (0.85 if kind == "earth" else 0.45)
                    row += bytes((col[0], col[1], col[2], _clamp(alpha * 255)))
                else:
                    row += b"\x00\x00\x00\x00"
                continue
            z = math.sqrt(1 - d2)
            # Rotate the sampling point around the vertical axis
            sx, sz = x * cs - z * sn, x * sn + z * cs
            sy = y
            lam = x * lx + y * ly + z * lz
            # Soft terminator
            day = max(0.0, min(1.0, (lam + 0.12) / 0.5))
            if kind == "earth":
                wx = n3.fbm(sx * 1.4 + 9, sy * 1.4, sz * 1.4, 3) * 1.2
                h = n3.fbm(sx * 1.55 + wx, sy * 1.55 + wx, sz * 1.55, 6)
                lat = abs(sy)
                if h > 0.53:
                    t = (h - 0.53) / 0.2
                    base = _ramp([(0, (58, 112, 58)), (0.35, (88, 128, 62)), (0.6, (150, 132, 88)), (1, (120, 98, 72))], t)
                    if lat < 0.35 and n3c.noise(sx * 4, sy * 4, sz * 4) > 0.58:
                        base = _lerp(base, (196, 168, 112), 0.6)  # deserts
                    spec = 0.0
                else:
                    t = max(0.0, (0.53 - h) / 0.12)
                    base = _ramp([(0, (52, 160, 178)), (0.25, (22, 96, 150)), (1, (8, 42, 96))], t)
                    spec = 1.0
                if lat > 0.86 - n3c.noise(sx * 3, sy * 3, sz * 3) * 0.12:
                    base, spec = (236, 242, 248), 0.0
                # Clouds with domain warping
                cw = n3c.fbm(sx * 2.2, sy * 2.2 + 4, sz * 2.2, 3)
                cl = n3c.fbm(sx * 3.1 + cw * 1.8, sy * 5.0 + cw * 1.4, sz * 3.1, 5)
                cloud = max(0.0, min(1.0, (cl - 0.5) / 0.16))
                col = _lerp(base, (250, 252, 255), cloud * 0.92)
                shade = 0.12 + 0.95 * max(0.0, lam)
                col = tuple(c * shade for c in col)
                # Ocean specular glint
                if spec and cloud < 0.4:
                    hx_, hy_, hz_ = _norm((lx, ly, lz + 1))
                    sp = max(0.0, x * hx_ + y * hy_ + z * hz_) ** 60
                    col = tuple(c + 255 * sp * 0.75 for c in col)
                # Night-side city lights
                if lam < -0.05 and h > 0.55 and cloud < 0.3 and n3.noise(sx * 40, sy * 40, sz * 40) > 0.78:
                    col = _lerp(col, (255, 200, 110), 0.85)
                # Fresnel atmosphere rim
                rim = (1 - z) ** 3
                col = _lerp(col, (120, 190, 255), min(1.0, rim * 1.6) * (0.25 + 0.75 * day))
            elif kind == "mars":
                h = n3.fbm(sx * 2.0, sy * 2.0, sz * 2.0, 6)
                dark = n3c.fbm(sx * 1.3 + 3, sy * 1.6, sz * 1.3, 4)
                base = _ramp([(0, (122, 48, 26)), (0.45, (192, 92, 54)), (0.7, (222, 132, 86)), (1, (238, 170, 120))], h)
                if dark > 0.56:
                    base = _lerp(base, (86, 36, 22), min(1.0, (dark - 0.56) / 0.1) * 0.75)
                # Valles Marineris style rift
                rift = abs(sy - 0.08 - 0.12 * math.sin(sx * 3)) 
                if rift < 0.035 and -0.55 < sx < 0.45 and sz > 0:
                    base = _lerp(base, (70, 26, 14), (1 - rift / 0.035) * 0.8)
                if sy < -0.84 + n3c.noise(sx * 4, sy * 4, sz * 4) * 0.08:
                    base = (248, 240, 236)
                shade = 0.06 + 1.0 * max(0.0, lam)
                col = tuple(c * shade for c in base)
                rim = (1 - z) ** 3
                col = _lerp(col, (255, 186, 150), min(1.0, rim * 1.3) * 0.5 * day)
            else:  # moon
                h = n3.fbm(sx * 3.0, sy * 3.0, sz * 3.0, 6)
                mare = n3c.fbm(sx * 1.1 + 2, sy * 1.1, sz * 1.1, 4)
                g = 150 + (h - 0.5) * 120
                if mare > 0.55:
                    g -= min(1.0, (mare - 0.55) / 0.08) * 62
                nx_, ny_, nz_ = sx, sy, sz
                for (cx_, cy_, cz_), cr in craters:
                    dd = math.sqrt((nx_ - cx_) ** 2 + (ny_ - cy_) ** 2 + (nz_ - cz_) ** 2)
                    if dd < cr * 1.25:
                        t = dd / cr
                        # Bowl shading toward light, bright rim
                        tilt = ((cx_ - nx_) * lx + (cy_ - ny_) * ly) / (cr or 1)
                        if t < 1:
                            g += tilt * 55 - 10
                        else:
                            g += (1.25 - t) * 4 * 18
                base = (g * 1.0, g * 1.0, g * 1.02)
                shade = 0.04 + 1.0 * max(0.0, lam)
                col = tuple(c * shade for c in base)
            row += bytes((_clamp(col[0]), _clamp(col[1]), _clamp(col[2]), 255))
        rows.append(bytes(row))
    return data_uri(_png(W, W, rows, 6))


def render_earth_limb(width: int, height: int, radius: float, seed: int = 5) -> str:
    """
    Earth seen from 420 km: a band of a very large lit sphere whose limb arcs across
    the top of the image, with Caribbean shallows, islands, cloud fields and a
    glowing atmospheric limb. Returns an RGBA data URI.
    """
    n3 = Noise3(seed)
    n3c = Noise3(seed + 77)
    cx, cy = width / 2, radius + height * 0.22
    lx, ly, lz = _norm((-0.5, -0.65, 0.58))
    rows = []
    for py in range(height):
        row = bytearray()
        for px in range(width):
            dx, dy = (px + 0.5 - cx) / radius, (py + 0.5 - cy) / radius
            d2 = dx * dx + dy * dy
            if d2 > 1:
                dist = (math.sqrt(d2) - 1) * radius
                a = max(0.0, 1 - dist / (height * 0.16)) ** 2.2
                row += bytes((120, 200, 255, _clamp(a * 220)))
                continue
            z = math.sqrt(1 - d2)
            sx, sy, sz = dx * 3.2, dy * 3.2, z * 3.2
            wx = n3.fbm(sx + 5, sy, sz, 3)
            h = n3.fbm(sx * 1.2 + wx, sy * 1.6 + wx, sz, 6)
            if h > 0.6:
                t = (h - 0.6) / 0.15
                base = _ramp([(0, (196, 186, 140)), (0.15, (70, 120, 64)), (1, (36, 82, 46))], t)
            elif h > 0.54:
                base = _ramp([(0, (18, 92, 150)), (1, (64, 196, 196))], (h - 0.54) / 0.06)
            else:
                base = _ramp([(0, (14, 70, 130)), (1, (6, 34, 82))], (0.54 - h) / 0.14)
            cw = n3c.fbm(sx * 1.5, sy * 3 + 2, sz, 3)
            cl = n3c.fbm(sx * 2.4 + cw * 2, sy * 6.0 + cw, sz * 2, 5)
            cloud = max(0.0, min(1.0, (cl - 0.52) / 0.14))
            col = _lerp(base, (248, 251, 255), cloud * 0.95)
            lam = dx * lx + dy * ly + z * lz
            col = tuple(c * (0.25 + 0.85 * max(0.0, lam)) for c in col)
            rim = (1 - z) ** 2.2
            col = _lerp(col, (130, 200, 255), min(1.0, rim * 2.2))
            fade = min(1.0, py / (height * 0.95)) ** 1.0
            col = tuple(c * (1 - fade * 0.35) for c in col)
            row += bytes((_clamp(col[0]), _clamp(col[1]), _clamp(col[2]), 255))
        rows.append(bytes(row))
    return data_uri(_png(width, height, rows, 6))

