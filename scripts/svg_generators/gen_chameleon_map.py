#!/usr/bin/env python3
"""Generator for Chameleon Islands infrastructure SVG map."""

import math
import sys
from pathlib import Path

try:
    from map_common import n, pt, poly_path, smooth_island, hotspot, map_header, update_island_map
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from map_common import n, pt, poly_path, smooth_island, hotspot, map_header, update_island_map


# ==========================================================================
# CHAMELEON ISLANDS (CHAMELEON ON A BRANCH: TIGHTLY GROUPED ARCHIPELAGO)
# ==========================================================================

CH_GAP = 12  # width of the dredged channels between neighbouring islands

def _catmull_dense(knots, step=3.0):
    pad = [knots[0]] + list(knots) + [knots[-1]]
    out = []
    for i in range(1, len(pad) - 2):
        p0, p1, p2, p3 = pad[i - 1], pad[i], pad[i + 1], pad[i + 2]
        m = max(2, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step))
        for j in range(m):
            u = j / m

            def cr(a, b, c, d):
                return 0.5 * (2 * b + (c - a) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (3 * b - a - 3 * c + d) * u ** 3)

            out.append((
                cr(p0[0], p1[0], p2[0], p3[0]),
                cr(p0[1], p1[1], p2[1], p3[1]),
                p1[2] + (p2[2] - p1[2]) * u,
                p1[3] + (p2[3] - p1[3]) * u,
            ))
    out.append(tuple(knots[-1]))
    return out


class Tube:
    """A centre-line with dorsal (wt) and ventral (wb) half-widths, addressable by arc length."""
    def __init__(self, knots):
        self.p = _catmull_dense(knots)
        self.s = [0.0]
        for a, b in zip(self.p, self.p[1:]):
            self.s.append(self.s[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        self.L = self.s[-1]
        k = len(self.p)
        self.nrm = []
        for i in range(k):
            a, b = self.p[max(0, i - 1)], self.p[min(k - 1, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(tx, ty) or 1.0
            self.nrm.append((-ty / ln, tx / ln))  # points to the dorsal side

    def at(self, s):
        s = min(max(s, 0.0), self.L)
        lo, hi = 0, len(self.s) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.s[mid] <= s:
                lo = mid
            else:
                hi = mid
        seg = (self.s[hi] - self.s[lo]) or 1.0
        u = (s - self.s[lo]) / seg
        a, b = self.p[lo], self.p[hi]
        na, nb = self.nrm[lo], self.nrm[hi]
        nx, ny = na[0] + (nb[0] - na[0]) * u, na[1] + (nb[1] - na[1]) * u
        ln = math.hypot(nx, ny) or 1.0
        return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u,
                a[2] + (b[2] - a[2]) * u, a[3] + (b[3] - a[3]) * u, nx / ln, ny / ln)

    def off(self, s, f):
        x, y, wt, wb, nx, ny = self.at(s)
        d = f(wt, wb) if callable(f) else f
        return (x + nx * d, y + ny * d)

    def s_at_x(self, x_target):
        """First arc length where the (westward running) centre-line crosses x_target."""
        for i in range(1, len(self.p)):
            x0, x1 = self.p[i - 1][0], self.p[i][0]
            if (x0 - x_target) * (x1 - x_target) <= 0 and x0 != x1:
                return self.s[i - 1] + (self.s[i] - self.s[i - 1]) * (x0 - x_target) / (x0 - x1)
        return self.L

    def piece(self, s0, s1, lo=None, hi=None, inset=0.0, step=8.0):
        """Closed outline of the tube between s0..s1 and lateral offsets lo..hi (functions of wt, wb)."""
        lo = lo or (lambda wt, wb: -wb)
        hi = hi or (lambda wt, wb: wt)
        s0, s1 = s0 + inset, s1 - inset
        if s1 - s0 < 2:
            return None
        flo = (lambda wt, wb: lo(wt, wb) + inset)
        fhi = (lambda wt, wb: hi(wt, wb) - inset)
        _, _, wt, wb, _, _ = self.at((s0 + s1) / 2)
        if fhi(wt, wb) - flo(wt, wb) < 3:
            return None
        n_s = max(2, int((s1 - s0) / step))
        ss = [s0 + (s1 - s0) * i / n_s for i in range(n_s + 1)]
        top = [self.off(s, fhi) for s in ss]
        bot = [self.off(s, flo) for s in reversed(ss)]

        def cap(s, f_from, f_to):
            x, y, wt, wb, nx, ny = self.at(s)
            a, b = f_from(wt, wb), f_to(wt, wb)
            k = max(1, int(abs(b - a) / step))
            return [(x + nx * (a + (b - a) * j / k), y + ny * (a + (b - a) * j / k)) for j in range(1, k)]

        return top + cap(s1, fhi, flo) + bot + cap(s0, flo, fhi)


def _chaikin(pts, it=1):
    for _ in range(it):
        q = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            q.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            q.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        pts = q
    return pts


def smooth_closed(pts, rounds=1):
    """Round the corners (Chaikin) and emit a smooth closed cubic Bezier path."""
    pts = _chaikin(pts, rounds)
    k = len(pts)
    d = [f"M{pt(pts[0])}"]
    for i in range(k):
        p0, p1, p2, p3 = pts[(i - 1) % k], pts[i], pts[(i + 1) % k], pts[(i + 2) % k]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(f"C{pt(c1)} {pt(c2)} {pt(p2)}")
    return " ".join(d) + " Z"


def catmull_rom_open(knots, n_per_seg=25, alpha=0.5):
    """Centripetal Catmull-Rom spline sampling for open paths."""
    pts = []
    for i in range(1, len(knots) - 2):
        p0, p1, p2, p3 = knots[i - 1], knots[i], knots[i + 1], knots[i + 2]

        def dist(pa, pb):
            return max(1e-4, math.hypot(pb[0] - pa[0], pb[1] - pa[1]) ** alpha)

        t0 = 0.0
        t1 = t0 + dist(p0, p1)
        t2 = t1 + dist(p1, p2)
        t3 = t2 + dist(p2, p3)
        for s in range(n_per_seg):
            t = t1 + (t2 - t1) * (s / float(n_per_seg))
            a1_x = (t1 - t) / (t1 - t0) * p0[0] + (t - t0) / (t1 - t0) * p1[0]
            a1_y = (t1 - t) / (t1 - t0) * p0[1] + (t - t0) / (t1 - t0) * p1[1]
            a2_x = (t2 - t) / (t2 - t1) * p1[0] + (t - t1) / (t2 - t1) * p2[0]
            a2_y = (t2 - t) / (t2 - t1) * p1[1] + (t - t1) / (t2 - t1) * p2[1]
            a3_x = (t3 - t) / (t3 - t2) * p2[0] + (t - t2) / (t3 - t2) * p3[0]
            a3_y = (t3 - t) / (t3 - t2) * p2[1] + (t - t2) / (t3 - t2) * p3[1]
            b1_x = (t2 - t) / (t2 - t0) * a1_x + (t - t0) / (t2 - t0) * a2_x
            b1_y = (t2 - t) / (t2 - t0) * a1_y + (t - t0) / (t2 - t0) * a2_y
            b2_x = (t3 - t) / (t3 - t1) * a2_x + (t - t1) / (t3 - t1) * a3_x
            b2_y = (t3 - t) / (t3 - t1) * a2_y + (t - t1) / (t3 - t1) * a3_y
            cx = (t2 - t) / (t2 - t1) * b1_x + (t - t1) / (t2 - t1) * b2_x
            cy = (t2 - t) / (t2 - t1) * b1_y + (t - t1) / (t2 - t1) * b2_y
            pts.append((round(cx, 2), round(cy, 2)))
    pts.append(knots[-2])
    return pts


def circle_d(cx, cy, r):
    return f"M{n(cx - r)},{n(cy)} a{n(r)},{n(r)} 0 1 0 {n(2 * r)},0 a{n(r)},{n(r)} 0 1 0 {n(-2 * r)},0 Z"


def _spiral_knots(cx, cy, r0, r1, w0, w1, turns_rad, step=0.26):
    """Logarithmic spiral starting due north of (cx, cy), heading west and curling inward (ventrally)."""
    k_r = math.log(r0 / r1) / turns_rad
    k_w = math.log(w0 / w1) / turns_rad
    out = []
    phi = 0.0
    while phi <= turns_rad + 1e-6:
        th = 1.5 * math.pi - phi
        r = r0 * math.exp(-k_r * phi)
        w = w0 * math.exp(-k_w * phi)
        out.append((cx + r * math.cos(th), cy + r * math.sin(th), w, w))
        phi += step
    return out


# Head -> body -> tail centre-line knots (x, y, dorsal half-width, ventral half-width)
CH_SPIRAL = (368, 418)
CH_BODY_KNOTS = [
    (962, 269, 7, 8),      # blunt snout tip
    (946, 264, 17, 20),
    (908, 255, 30, 35),
    (868, 252, 36, 44),    # head (turret eye)
    (826, 257, 36, 44),    # back of the head
    (786, 267, 31, 38),    # neck
    (742, 262, 44, 51),    # shoulder
    (682, 248, 54, 58),
    (612, 242, 58, 60),    # crest of the arched back
    (542, 250, 55, 57),
    (476, 270, 45, 48),    # hip
    (428, 288, 30, 31),    # tail base
] + _spiral_knots(CH_SPIRAL[0], CH_SPIRAL[1], 124, 24, 28, 6, 7.2)

# Limbs (shoulder / hip -> elbow / knee -> wrist / ankle): thigh and shin are separate islands
CH_LIMBS = {
    "hind": [(520, 320, 16, 16), (566, 394, 13, 13), (536, 476, 10, 10)],
    "fore": [(744, 326, 16, 16), (704, 400, 13, 13), (746, 476, 10, 10)],
}


def chameleon_svg():
    g = CH_GAP
    body = Tube(CH_BODY_KNOTS)
    sx = body.s_at_x

    sand, green = [], []
    seed_counter = 1

    def add(poly, name, kind="sand", green_poly=None, hole=None, rounds=1):
        if not poly:
            return
        d = smooth_closed(poly, rounds=rounds)
        if hole:
            d += " " + circle_d(*hole)
        sand.append((name, d, kind, hole is not None))
        if green_poly:
            dg = smooth_closed(green_poly, rounds=rounds)
            if hole:
                dg += " " + circle_d(hole[0], hole[1], hole[2] + 6)
            green.append((name, dg, hole is not None))

    def organic_piece(tube, s0, s1, lo=None, hi=None, inset=0.0, step=5.0, seed=None):
        nonlocal seed_counter
        if seed is None:
            seed = seed_counter
            seed_counter += 1
        lo = lo or (lambda wt, wb: -wb)
        hi = hi or (lambda wt, wb: wt)
        s0, s1 = s0 + inset, s1 - inset
        if s1 - s0 < 2:
            return None
        flo = (lambda wt, wb: lo(wt, wb) + inset)
        fhi = (lambda wt, wb: hi(wt, wb) - inset)
        _, _, wt, wb, _, _ = tube.at((s0 + s1) / 2)
        if fhi(wt, wb) - flo(wt, wb) < 2.5:
            return None
        n_s = max(4, int((s1 - s0) / step))
        ss = [s0 + (s1 - s0) * i / n_s for i in range(n_s + 1)]

        top = []
        for idx, s in enumerate(ss):
            rel = (s - s0) / (s1 - s0)
            w = 2.2 * math.sin(math.pi * rel) * (0.6 * math.sin(2.5 * math.pi * rel + seed) + 0.4 * math.cos(4 * math.pi * rel))
            top.append(tube.off(s, lambda wt, wb: fhi(wt, wb) + w))

        bot = []
        for idx, s in enumerate(reversed(ss)):
            rel = (s - s0) / (s1 - s0)
            w = 2.0 * math.sin(math.pi * rel) * (0.6 * math.cos(2.5 * math.pi * rel + seed * 2) - 0.4 * math.sin(3.5 * math.pi * rel))
            bot.append(tube.off(s, lambda wt, wb: flo(wt, wb) - w))

        def cap(s, f_from, f_to, is_end=False):
            x, y, wt, wb, nx, ny = tube.at(s)
            a, b = f_from(wt, wb), f_to(wt, wb)
            k = max(2, int(abs(b - a) / step))
            pts = []
            for j in range(1, k):
                u = j / float(k)
                bow = 1.8 * math.sin(math.pi * u) * (-1 if is_end else 1)
                d = a + (b - a) * u
                pts.append((x + nx * d + (-ny) * bow, y + ny * d + nx * bow))
            return pts

        return top + cap(s1, fhi, flo, is_end=True) + bot + cap(s0, flo, fhi, is_end=False)

    lateral = lambda frac: (lambda wt, wb: wt - frac * (wt + wb))  # noqa: E731
    split_mouth = lateral(0.55)
    split_belly = lateral(0.58)
    hg = g / 2.0

    def above(f):
        return lambda wt, wb: f(wt, wb) + hg

    def below(f):
        return lambda wt, wb: f(wt, wb) - hg

    eye = (858, 242, 12)
    hole = (eye[0], eye[1], eye[2] + 6)
    road_ranges = []
    bridge_lines = []

    # 1. Jaws: split into 2 cuts (Snout and Mid-Jaw) -> 4 islands
    s_j0 = 0.0
    s_j1 = 36.0
    s_j2 = sx(886)
    for a, b, tag in [(s_j0, s_j1 - hg, "Snout"), (s_j1 + hg, s_j2 - hg, "Mid-Jaw")]:
        poly_upper = organic_piece(body, a, b, lo=above(split_mouth))
        if poly_upper:
            poly_upper = [(x, y + 7) for x, y in poly_upper]
        gp_upper = organic_piece(body, a, b, lo=above(split_mouth), inset=6)
        if gp_upper:
            gp_upper = [(x, y + 7) for x, y in gp_upper]
        add(poly_upper, f"Upper {tag} Isle", green_poly=gp_upper)
        add(organic_piece(body, a, b, hi=below(split_mouth)), f"Lower {tag} Isle")
        road_ranges.append((a, b))

    # 2. Head Crown around Eye: 2 islands
    s_c0 = sx(886)
    s_c1 = (sx(886) + sx(806)) / 2
    s_c2 = sx(806)
    add(organic_piece(body, s_c0 + hg, s_c1 - hg), "Head Crown Isle East", green_poly=organic_piece(body, s_c0 + hg, s_c1 - hg, inset=8), hole=hole)
    add(organic_piece(body, s_c1 + hg, s_c2 - hg), "Head Crown Isle West", green_poly=organic_piece(body, s_c1 + hg, s_c2 - hg, inset=8))
    road_ranges.extend([(s_c0 + hg, s_c1 - hg), (s_c1 + hg, s_c2 - hg)])

    # 3. Neck: 2 islands
    s_n0 = sx(806)
    s_n1 = (sx(806) + sx(754)) / 2
    s_n2 = sx(754)
    add(organic_piece(body, s_n0 + hg, s_n1 - hg), "Neck Isle 1", green_poly=organic_piece(body, s_n0 + hg, s_n1 - hg, inset=7))
    add(organic_piece(body, s_n1 + hg, s_n2 - hg), "Neck Isle 2", green_poly=organic_piece(body, s_n1 + hg, s_n2 - hg, inset=7))
    road_ranges.extend([(s_n0 + hg, s_n1 - hg), (s_n1 + hg, s_n2 - hg)])

    # 4. Shoulder (sx 754 to 682): 2 dorsal + 2 belly = 4 islands
    s_sh0 = sx(754)
    s_sh1 = (sx(754) + sx(682)) / 2
    s_sh2 = sx(682)
    sh_cuts = [(s_sh0 + hg, s_sh1 - hg), (s_sh1 + hg, s_sh2 - hg)]
    for idx, (a, b) in enumerate(sh_cuts, 1):
        add(organic_piece(body, a, b, lo=above(split_belly)), f"Shoulder Dorsal Isle {idx}", green_poly=organic_piece(body, a, b, lo=above(split_belly), inset=8))
        add(organic_piece(body, a, b, hi=below(split_belly)), f"Shoulder Belly Isle {idx}")
        road_ranges.append((a, b))
        m = (a + b) / 2
        bridge_lines.append((body.off(m, lambda wt, wb: split_belly(wt, wb) + hg + 4),
                             body.off(m, lambda wt, wb: split_belly(wt, wb) - hg - 4)))

    # 5. Mid-Back (Pavilion, sx 682 to 546): 3 dorsal + 3 belly = 6 islands
    s_mb0 = sx(682)
    s_mb1 = s_mb0 + (sx(546) - s_mb0) / 3.0
    s_mb2 = s_mb0 + (sx(546) - s_mb0) * 2.0 / 3.0
    s_mb3 = sx(546)
    mb_cuts = [(s_mb0 + hg, s_mb1 - hg), (s_mb1 + hg, s_mb2 - hg), (s_mb2 + hg, s_mb3 - hg)]
    for idx, (a, b) in enumerate(mb_cuts, 1):
        add(organic_piece(body, a, b, lo=above(split_belly)), f"Pavilion Dorsal Isle {idx}", green_poly=organic_piece(body, a, b, lo=above(split_belly), inset=8))
        add(organic_piece(body, a, b, hi=below(split_belly)), f"Pavilion Belly Isle {idx}")
        road_ranges.append((a, b))
        m = (a + b) / 2
        bridge_lines.append((body.off(m, lambda wt, wb: split_belly(wt, wb) + hg + 4),
                             body.off(m, lambda wt, wb: split_belly(wt, wb) - hg - 4)))

    # 6. Rump (sx 546 to 470): 2 dorsal + 2 belly = 4 islands
    s_r0 = sx(546)
    s_r1 = (sx(546) + sx(470)) / 2
    s_r2 = sx(470)
    r_cuts = [(s_r0 + hg, s_r1 - hg), (s_r1 + hg, s_r2 - hg)]
    for idx, (a, b) in enumerate(r_cuts, 1):
        add(organic_piece(body, a, b, lo=above(split_belly)), f"Rump Dorsal Isle {idx}", green_poly=organic_piece(body, a, b, lo=above(split_belly), inset=8))
        add(organic_piece(body, a, b, hi=below(split_belly)), f"Rump Belly Isle {idx}")
        road_ranges.append((a, b))
        m = (a + b) / 2
        bridge_lines.append((body.off(m, lambda wt, wb: split_belly(wt, wb) + hg + 4),
                             body.off(m, lambda wt, wb: split_belly(wt, wb) - hg - 4)))

    # 7. Spiral Tail: 24 finely segmented organic pebble islands
    s = sx(470) + hg
    t_idx = 1
    t_seg_len = 38.0
    while s < body.L - 20:
        a = s
        b = min(body.L, s + t_seg_len - g)
        mid = (a + b) / 2
        _, _, wt, wb, _, _ = body.at(mid)
        gp = organic_piece(body, a, b, inset=7) if wt + wb > 24 else None
        add(organic_piece(body, a, b), f"Spiral Tail Isle {t_idx}", green_poly=gp)
        road_ranges.append((a, b))
        s += t_seg_len
        t_seg_len = max(22.0, t_seg_len * 0.94)
        t_idx += 1

    # 8. Casque Helmet: 2 graceful sweeping crest islands
    s_c0, s_c1 = sx(880), sx(796)
    sc_m = (s_c0 + s_c1) / 2
    arc1 = [body.off(s_c0 + (sc_m - s_c0) * j / 6, lambda wt, wb: wt + g) for j in range(7)]
    add(arc1 + [(838, 204), (826, 186), (820, 196)], "Casque Crown Isle East")
    arc2 = [body.off(sc_m + (s_c1 - sc_m) * j / 6, lambda wt, wb: wt + g) for j in range(7)]
    add(arc2 + [(804, 176), (794, 178), (808, 198)], "Casque Peak Isle West")
    green.append(("Casque Helmet Core", smooth_closed([(828, 208), (810, 190), (842, 210)], 3), False))

    # 9. Dorsal Crest Islets: 16 rounded tooth islets
    for k, xc in enumerate(range(768, 465, -19), 1):
        sc = sx(xc)
        base_l = body.off(sc - 6, lambda wt, wb: wt + g)
        base_r = body.off(sc + 6, lambda wt, wb: wt + g)
        tip_h = 12 + 3 * math.sin(k * 1.1)
        tip = body.off(sc, lambda wt, wb: wt + g + tip_h)
        add([base_r, tip, base_l], f"Dorsal Crest Islet {k}", kind="crest", rounds=2)

    # 10. Limbs: Upper limb and Lower limb each split into 2 smaller articulated islands
    limb_meta = {}
    for limb, knots in CH_LIMBS.items():
        tube = Tube(knots)
        knee = tube.s[min(range(len(tube.p)), key=lambda q: math.hypot(tube.p[q][0] - knots[1][0], tube.p[q][1] - knots[1][1]))]
        upper_name = "Hindlimb Thigh" if limb == "hind" else "Forelimb Upper Arm"
        lower_name = "Hindlimb Shin" if limb == "hind" else "Forelimb Forearm"

        u_mid = knee / 2.0
        add(organic_piece(tube, 0, u_mid - hg), f"{upper_name} Isle 1", green_poly=organic_piece(tube, 0, u_mid - hg, inset=6))
        add(organic_piece(tube, u_mid + hg, knee - hg), f"{upper_name} Isle 2", green_poly=organic_piece(tube, u_mid + hg, knee - hg, inset=6))
        bridge_lines.append((tube.off(u_mid - hg - 3, 0), tube.off(u_mid + hg + 3, 0)))

        l_mid = (knee + tube.L) / 2.0
        add(organic_piece(tube, knee + hg, l_mid - hg), f"{lower_name} Isle 1")
        add(organic_piece(tube, l_mid + hg, tube.L), f"{lower_name} Isle 2")
        bridge_lines.append((tube.off(knee - hg - 4, 0), tube.off(knee + hg + 4, 0)))
        bridge_lines.append((tube.off(l_mid - hg - 3, 0), tube.off(l_mid + hg + 3, 0)))

        p_limb = tube.off(12, 0)
        p_belly = body.off(sx(p_limb[0]), lambda wt, wb: -wb + 6)
        bridge_lines.append((p_limb, p_belly))
        ax, ay = knots[-1][0], knots[-1][1]
        for side in (-1, 1):
            ck = [(ax + side * 6, ay + 6, 5, 5), (ax + side * 18, ay + 12, 4.5, 4.5), (ax + side * 27, ay + 19, 2.5, 2.5)]
            ct = Tube(ck)
            add(organic_piece(ct, 0, ct.L), f"{lower_name} Claw {'East' if side > 0 else 'West'}")
        limb_meta[limb] = {"upper_mid": tube.off(knee / 2, 0)}

    # 11. Curved tongue: 5 stepping-stone islets to Paradise Atoll
    tongue = [
        (965, 292, 10, 5, 30),
        (968, 318, 10, 5, 55),
        (964, 344, 9.5, 5, 75),
        (952, 368, 9.5, 5.2, 95),
        (936, 386, 9.5, 5.5, 115),
    ]
    for k, (x, y, rx, ry, rot) in enumerate(tongue):
        sand.append((f"Tongue Stepping Islet {k + 1}", smooth_island(x, y, rx, ry, rot=rot, seed=k + 2), "sand", False))
    villas = (920, 410)
    sand.append(("Paradise Atoll", smooth_island(villas[0], villas[1], 25, 23, rot=10, seed=4) + " " + circle_d(villas[0], villas[1], 12), "sand", True))

    # 12. Marine biology and renewable power satellite islets
    leaf_r = (912, 492)
    sand.append(("Marine Station Leaf Isle", smooth_island(leaf_r[0], leaf_r[1], 22, 11, rot=-30, seed=5), "sand", False))
    green.append(("Marine Station Leaf Isle", smooth_island(leaf_r[0], leaf_r[1], 13, 5, rot=-30, seed=9), False))
    leaf_l = (268, 486)
    sand.append(("Power Hub Leaf Isle", smooth_island(leaf_l[0], leaf_l[1], 22, 11, rot=40, seed=7), "sand", False))
    green.append(("Power Hub Leaf Isle", smooth_island(leaf_l[0], leaf_l[1], 13, 5, rot=40, seed=11), False))

    # ---------------------------------------------------------------------------------------
    # SVG OUTPUT
    # ---------------------------------------------------------------------------------------
    o = map_header()
    o += [
        "<!-- Shallow Lagoon -->",
        '<ellipse cx="600" cy="345" rx="540" ry="290" fill="url(#lagoon-glow)" />',
        "<!-- Chameleon Archipelago Group (enlarged to fit full area like other islands) -->",
        '<g id="chameleon-group" transform="translate(585, 350) scale(1.45) translate(-585, -350)">',
        "<!-- Shallow Reef Halo hugging the Archipelago -->",
        '<g fill="none" stroke="#2ba29e" stroke-linecap="round" stroke-linejoin="round" opacity="0.35">',
        f'<path d="{poly_path([body.off(s, lambda wt, wb: wt + 4) for s in [body.L * q / 120 for q in range(121)]], close=False)}" stroke-width="16" />',
        "</g>",
    ]

    o.append(f"<!-- {len(sand)} DISTINCT ISLANDS FORMING A CHAMELEON (ZERO OVERLAPS) -->")
    o.append('<g id="chameleon-islands-group">')
    for name, d, kind, has_hole in sand:
        cls = "map-reef" if kind == "crest" else "map-sand"
        rule = ' fill-rule="evenodd"' if has_hole else ""
        o.append(f"<!-- {name} -->")
        o.append(f'<path class="{cls}" d="{d}"{rule} />')
    o.append("</g>")
    o.append("<!-- Island Greenery Cores -->")
    o.append('<g id="chameleon-greenery-group">')
    for name, d, has_hole in green:
        rule = ' fill-rule="evenodd"' if has_hole else ""
        o.append(f'<path class="map-greenery" d="{d}"{rule} />')
    o.append("</g>")

    # Waterfront villas dotted along the outer coast of the spiral tail
    villa_paths = []
    for a, b in road_ranges[13:]:
        _, _, wt, wb, _, _ = body.at((a + b) / 2)
        if wt < 9:
            continue
        pts = [body.off(a + (b - a) * q / 8, lambda wt, wb: wt - 4) for q in range(1, 8)]
        villa_paths.append(poly_path(pts, close=False))
    o += [
        "<!-- Spiral Tail Waterfront Villas -->",
        f'<path class="map-frond-villas" d="{" ".join(villa_paths)}" stroke-width="2.6" stroke-dasharray="0.1 7" />',
    ]

    # Chameleon Boulevard and Overwater Tongue Road: continuous road from Paradise Atoll
    # across the Tongue Islets, Snout, Head, Body and through every channel to the Spiral Tail tip
    s_road_end = body.L - 26
    spine_road = [body.off(s_road_end * q / 180, lambda wt, wb: 0.28 * wt * (q / 180)**0.5 if q > 0 else 0) for q in range(181)]
    atoll_pier = (villas[0], villas[1] - 20)
    tongue_knots = [
        atoll_pier,
        (936, 386),
        (952, 368),
        (964, 344),
        (968, 318),
        (965, 292),
        (962, 269),
        spine_road[2],
        spine_road[5],
        spine_road[9],
    ]
    tongue_spline = catmull_rom_open(tongue_knots, n_per_seg=25, alpha=0.5)
    idx_junc = min(range(len(tongue_spline)), key=lambda k: math.hypot(tongue_spline[k][0] - spine_road[5][0], tongue_spline[k][1] - spine_road[5][1]))
    road_pts = tongue_spline[:idx_junc] + spine_road[5:]
    o += [
        "<!-- Chameleon Boulevard and Overwater Tongue Road (bridges every channel from Paradise Atoll to the spiral tail) -->",
        f'<path class="map-road" d="{poly_path(road_pts, close=False)}" />',
        "<!-- Inter-Island Footbridges (belly channel, knees and limb causeways) -->",
        '<g stroke="#ffffff" stroke-width="2.2" stroke-linecap="round">',
    ]
    for p1, p2 in bridge_lines:
        o.append(f'<line x1="{n(p1[0])}" y1="{n(p1[1])}" x2="{n(p2[0])}" y2="{n(p2[1])}" />')
    p_head = body.off(sx(835), lambda wt, wb: wt - 4)
    p_casque = body.off(sx(835), lambda wt, wb: wt + g + 6)
    o.append(f'<line x1="{n(p_head[0])}" y1="{n(p_head[1])}" x2="{n(p_casque[0])}" y2="{n(p_casque[1])}" />')
    o.append("</g>")

    # Spiral Tail Marina inside the coil
    mar = (CH_SPIRAL[0] + 4, CH_SPIRAL[1] + 2)

    pav_s = (sx(682) + sx(546)) / 2
    pav = body.off(pav_s, lambda wt, wb: 0.3 * wt)
    pav = (int(round(pav[0])), int(round(pav[1])))
    o += [
        "<!-- Glass-Domed Central Grand Pavilion -->",
        f'<g transform="translate({n(pav[0])}, {n(pav[1])})">',
        '<ellipse cx="0" cy="0" rx="36" ry="20" fill="#002244" opacity="0.8" />',
        '<ellipse cx="0" cy="0" rx="30" ry="16" fill="#38bdf8" filter="url(#glass-glow)" opacity="0.85" />',
        '<ellipse cx="0" cy="0" rx="20" ry="11" fill="none" stroke="#ffffff" stroke-width="1.4" />',
        '<line x1="-30" y1="0" x2="30" y2="0" stroke="#ffffff" stroke-width="1.6" />',
        '<line x1="0" y1="-16" x2="0" y2="16" stroke="#ffffff" stroke-width="1.6" />',
        '<circle cx="0" cy="0" r="4.5" fill="#f5c46e" class="twinkle" />',
        "</g>",
    ]

    # Revolving 360 Degree Observation Eye Dome inside its ringed lagoon
    o += [
        "<!-- Revolving 360 Degree Observation Eye Dome (Turret Eye Islet) -->",
        f'<circle cx="{eye[0]}" cy="{eye[1]}" r="{eye[2]}" class="map-sand" />',
        f'<g transform="translate({eye[0]}, {eye[1]})">',
        '<circle cx="0" cy="0" r="9" fill="#0f172a" stroke="#ffffff" stroke-width="1.5" />',
        '<circle cx="0" cy="0" r="6" fill="#38bdf8" opacity="0.9" />',
        '<circle cx="2" cy="-2" r="2.2" fill="#ffffff" />',
        "</g>",
    ]

    # International Youth Innovation Center on the forelimb
    youth = limb_meta["fore"]["upper_mid"]
    youth = (int(round(youth[0])), int(round(youth[1])))
    o += [
        "<!-- International Youth Innovation Center Campus -->",
        f'<rect x="{n(youth[0] - 9)}" y="{n(youth[1] - 12)}" width="18" height="24" rx="3" class="map-urban" />',
    ]

    # Marine Biology and Dolphin Station on the east leaf islet
    bio = leaf_r
    o += [
        "<!-- Marine Biology and Dolphin Station -->",
        f'<circle cx="{bio[0]}" cy="{bio[1]}" r="9" class="map-sea-lagoon" stroke="#ffffff" stroke-width="1.6" />',
        f'<path d="M{bio[0] - 3},{bio[1] - 2} C{bio[0] + 3},{bio[1] - 5} {bio[0] + 5},{bio[1] + 3} {bio[0]},{bio[1] + 4}" stroke="#0284c7" stroke-width="2" fill="none" />',
    ]

    # Floating Eco-District moored in the sheltered lagoon between the legs
    eco = (632, 420)
    o += ["<!-- Experimental Floating Eco-Communities (Sheltered Belly Lagoon) -->", '<g fill="#2dd4bf" stroke="#ffffff" stroke-width="1">']
    for dx, dy in ((-30, -22), (-12, -30), (8, -24), (26, -12), (-24, 2), (22, 10), (-8, 24), (12, 30)):
        o.append(f'<rect x="{eco[0] + dx - 5}" y="{eco[1] + dy - 5}" width="10" height="10" rx="2" />')
    o.append("</g>")

    # Tidal Power Hub on the west leaf islet
    o += [
        "<!-- Renewable Marine Power Hub -->",
        f'<g transform="translate({leaf_l[0]}, {leaf_l[1]})">',
        '<circle cx="0" cy="0" r="8" fill="#0284c7" stroke="#ffffff" stroke-width="1.4" />',
        '<path d="M0,-6 L0,6 M-6,0 L6,0" stroke="#ffffff" stroke-width="1.8" class="spin" />',
        "</g>",
    ]

    # Paradise Islands Overwater Villas on the tongue-tip atoll
    o += [
        "<!-- Paradise Islands Overwater Bungalows and Coral Nursery -->",
        f'<circle cx="{villas[0]}" cy="{villas[1]}" r="18" fill="none" stroke="#c29a57" stroke-width="2.5" stroke-dasharray="3 4" />',
        f'<circle cx="{villas[0]}" cy="{villas[1]}" r="12" class="map-sea-lagoon" stroke="#2dd4bf" stroke-width="1.6" />',
        f'<circle cx="{villas[0]}" cy="{villas[1]}" r="3.5" fill="#38bdf8" class="bob" />',
    ]

    # Sub-Sea Metro Tunnel
    metro = body.off((sx(682) + sx(546)) / 2 + 30, lambda wt, wb: split_belly(wt, wb) - 0.5 * (split_belly(wt, wb) + wb))
    metro = (int(round(metro[0])), int(round(metro[1])))
    o += [
        "<!-- Sub-Sea Metro Tunnel (Nova Aurelia to Portal, Pavilion, Eye Dome and Spiral Marina) -->",
        '<g fill="none" stroke="#f5c46e" stroke-dasharray="8 4">',
        f'<path d="M{n(metro[0])},670 L{n(metro[0])},{n(metro[1])} L{n(pav[0])},{n(pav[1])}" stroke-width="3" />',
        "</g>",
    ]
    for x, y in (metro, pav, (eye[0], eye[1]), mar):
        o.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="5" fill="#f5c46e" stroke="#ffffff" stroke-width="2" />')

    # Interactive Hotspots
    spots = [
        (1, pav[0], pav[1], "#38bdf8", "Glass-Domed Central Grand Pavilion", 12),
        (2, eye[0], eye[1], "#f5c46e", "Revolving 360 Degree Eye Dome", 11),
        (3, youth[0], youth[1], "#38bdf8", "Youth Innovation Center", 11),
        (4, mar[0], mar[1], "#0284c7", "Spiral Tail Marina", 11),
        (5, villas[0], villas[1], "#c29a57", "Paradise Islands Overwater Villas", 11),
        (6, bio[0], bio[1], "#22c55e", "Marine Biology and Dolphin Station", 11),
        (7, eco[0], eco[1], "#2dd4bf", "Floating Eco-District", 11),
        (8, metro[0], metro[1], "#f5c46e", "Sub-Sea Metro Tunnel Portal", 11),
    ]
    o.append("<!-- 8 INTERACTIVE HOTSPOT PINS -->")
    for i, x, y, col, name, r in spots:
        o.append(f"<!-- Hotspot {i}: {name} -->")
        o += hotspot(i, x, y, col, r)
    o.append("</g>")
    o.append("</svg>")
    return o

def main():
    update_island_map(2, chameleon_svg)

if __name__ == "__main__":
    main()
