#!/usr/bin/env python3
"""
Procedural generator for the Nova Aurelia imperial metropolis vector illustrations.

Generates standalone SVG files in icons/nova-aurelia/ and injects localized inline
SVGs into en/nova-aurelia.html and hu/nova-aurelia.html. Every illustration container in
the pages is marked with data-city-svg="KEY"; the <svg> inside it is replaced.

Scenes:
  skyline          Wide panoramic view of Nova Aurelia across the lagoon
  pyramid          The Grand Sovereign Pyramid and Imperial Palace cutaway/perspective
  undersea-hub     Trans-Lagoon Maglev and underwater marine concourse cross-section
  archipelago-map  Cartographic masterplan of Palm Island, World Isles, and Chameleon Atolls
  marina           Marina Aurelia yacht harbor and lighthouse pavilion vignette
  boulevard        Via Aurelia ceremonial avenue and imperial colonnade vignette
  aerotropolis     Aurelia Spaceport and stratospheric airship terminal vignette
  night-lagoon     Nocturnal smart lagoon with neon water glow and bioluminescence vignette

Usage:
  python3 scripts/gen_nova_aurelia_svgs.py
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
OUT_DIR = ROOT / "icons" / "nova-aurelia"


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


# ==============================================================================
# SCENE BUILDER
# ==============================================================================
class Scene:
    def __init__(self, key: str, w: int, h: int):
        self.key, self.w, self.h = key, w, h
        self.defs: list[str] = []
        self.body: list[str] = []

    def id(self, name: str) -> str:
        return f"na-{self.key}-{name}"

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

    def linear(self, name: str, stops, x1=0, y1=0, x2=0, y2=1) -> str:
        self.defs.append(
            f'<linearGradient id="{self.id(name)}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{self._stops(stops)}</linearGradient>'
        )
        return self.url(name)

    def radial(self, name: str, stops, cx=0.5, cy=0.5, r=0.5) -> str:
        self.defs.append(
            f'<radialGradient id="{self.id(name)}" cx="{cx}" cy="{cy}" r="{r}">{self._stops(stops)}</radialGradient>'
        )
        return self.url(name)

    def blur(self, name: str, sd: float) -> str:
        self.defs.append(
            f'<filter id="{self.id(name)}" x="-30%" y="-30%" width="160%" height="160%">'
            f'<feGaussianBlur stdDeviation="{sd}"/></filter>'
        )
        return self.url(name)

    def clip(self, name: str, d: str) -> str:
        self.defs.append(f'<clipPath id="{self.id(name)}"><path d="{d}"/></clipPath>')
        return self.url(name)

    def render(self, label: str) -> str:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" class="city-ill" viewBox="0 0 {self.w} {self.h}" '
            f'role="img" aria-label="{html.escape(label, quote=True)}">'
        )
        lines = [head, "<defs>", *self.defs, "</defs>", *self.body, "</svg>"]
        return "\n".join(lines)


# ==============================================================================
# LOCALIZED DICTIONARY
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
        "lighthouse_pavilion": "Helical Lighthouse Pavilion",
        "yacht_berths": "Zero-Emission Superyacht Slips",
        "harbor_promenade": "Harbor Esplanade and Cafes",
        "boulevard_title": "Via Aurelia and Ceremonial Forum",
        "corinthian_colonnade": "Imperial Marble Colonnades",
        "royal_palms": "Royal Date Palms and Fountains",
        "transit_pods": "Autonomous Electric Transit",
        "aerotropolis_title": "Aurelia Spaceport and Stratospheric Skyport",
        "suborbital_shuttle": "Suborbital Trans-Atmospheric Shuttle",
        "hydrogen_cruiser": "Stratospheric Hydrogen Cruiser",
        "telemetry_dome": "Orbital Telemetry Array",
        "night_title": "The Bioluminescent Smart Lagoon",
        "biolum_canal": "Bioluminescent Lagoon Waters",
        "smart_barriers": "Illuminated Flood Defenses",
        "skyline_night": "Nocturnal Metropolis Skyline",
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
        "lighthouse_pavilion": "Spirális Világítótorony Pavilon",
        "yacht_berths": "Zéró Emissziós Jachtkikötő",
        "harbor_promenade": "Kikötői Sétány és Kávézók",
        "boulevard_title": "Via Aurelia és Ceremoniális Fórum",
        "corinthian_colonnade": "Császári Márvány Kolonnádok",
        "royal_palms": "Királyi Pálmasor és Szökőkutak",
        "transit_pods": "Autonóm Elektromos Tranzit",
        "aerotropolis_title": "Aurelia Űrkikötő és Sztratoszférikus Repülőtér",
        "suborbital_shuttle": "Szuborbitális Transzatmoszférikus Sikló",
        "hydrogen_cruiser": "Sztratoszférikus Hidrogén Léghajó",
        "telemetry_dome": "Orbitális Telemetriai Dóm",
        "night_title": "A Biolumineszcens Okos Lagúna",
        "biolum_canal": "Biolumineszcens Lagúnavizek",
        "smart_barriers": "Megvilágított Árvízvédelmi Gátak",
        "skyline_night": "Éjszakai Metropolisz Látkép",
    },
}


# ==============================================================================
# 1. SCENE: SKYLINE (Imperial Lagoon Panorama - 1600 x 600)
# ==============================================================================
def build_skyline(t: dict[str, str]) -> str:
    s = Scene("skyline", 1600, 600)

    # Gradients
    sky_grad = s.linear(
        "sky",
        [
            (0.0, "#081427"),
            (0.35, "#182a4d"),
            (0.65, "#3b3659"),
            (0.82, "#734358"),
            (0.94, "#c26d52"),
            (1.0, "#f2a864"),
        ],
    )
    sun_glow = s.radial(
        "sunglow",
        [
            (0.0, "#fff5d0", 0.95),
            (0.2, "#ffc66e", 0.75),
            (0.5, "#d96541", 0.35),
            (1.0, "#081427", 0.0),
        ],
        cx=0.72,
        cy=0.62,
        r=0.45,
    )
    water_grad = s.linear(
        "water",
        [
            (0.0, "#0a2238"),
            (0.25, "#0b2c45"),
            (0.6, "#0d3753"),
            (1.0, "#091929"),
        ],
    )
    glass_spire = s.linear(
        "glass-spire",
        [
            (0.0, "#d5edff", 0.95),
            (0.3, "#78aed4", 0.8),
            (0.7, "#245277", 0.85),
            (1.0, "#10293d", 0.9),
        ],
        x1=0,
        y1=0,
        x2=1,
        y2=0,
    )
    gold_grad = s.linear(
        "gold",
        [
            (0.0, "#fff0b3"),
            (0.4, "#f0be50"),
            (0.8, "#b38222"),
            (1.0, "#7a5310"),
        ],
    )

    # 1. Sky backdrop
    s.add(el("rect", width=1600, height=600, fill=sky_grad))
    s.add(el("rect", width=1600, height=600, fill=sun_glow))

    # Sun disk low on horizon behind Palm Island silhouette
    s.add(el("circle", cx=1152, cy=370, r=42, fill="#fff2c2", opacity=0.9))

    # Distant clouds
    for y_pos, x_off, op, scale in [(180, 0, 0.22, 1.0), (220, 240, 0.18, 0.8), (280, -120, 0.15, 1.2)]:
        s.add(
            el(
                "ellipse",
                cx=600 + x_off,
                cy=y_pos,
                rx=260 * scale,
                ry=24 * scale,
                fill="#ffffff",
                opacity=op,
                class_="city-anim-cloud",
            )
        )
        s.add(
            el(
                "ellipse",
                cx=1200 + x_off,
                cy=y_pos + 30,
                rx=320 * scale,
                ry=28 * scale,
                fill="#ffddaa",
                opacity=op * 1.3,
                class_="city-anim-cloud",
            )
        )

    # Distant mountain silhouettes (Waikiki Range)
    mtn_pts = [
        (0, 390),
        (120, 360),
        (260, 375),
        (420, 335),
        (560, 365),
        (720, 320),
        (880, 355),
        (1040, 310),
        (1200, 360),
        (1360, 325),
        (1500, 350),
        (1600, 330),
        (1600, 420),
        (0, 420),
    ]
    s.add(el("polygon", points=" ".join(f"{x},{y}" for x, y in mtn_pts), fill="#1f1830", opacity=0.6))

    # Distant Archipelago and Palm Island silhouette in the far right
    s.add(el("ellipse", cx=1380, cy=405, rx=180, ry=14, fill="#121824", opacity=0.85))
    # Hotel Khalifa silhouette at the apex of Palm Island
    s.add(
        el(
            "path",
            d="M1365,405 C1368,360 1375,340 1380,310 C1385,340 1392,360 1395,405 Z",
            fill="#121824",
            opacity=0.9,
        )
    )
    s.add(el("line", x1=1380, y1=310, x2=1380, y2=295, stroke="#f0be50", stroke_width=1.5))

    # Midground skyline buildings (silhouettes with illuminated window bands)
    mid_bldgs = [
        (40, 280, 50, 130),
        (100, 240, 65, 170),
        (180, 260, 70, 150),
        (270, 210, 55, 200),
        (340, 270, 80, 140),
        (1240, 250, 75, 160),
        (1330, 230, 60, 180),
        (1420, 270, 80, 140),
        (1520, 290, 60, 120),
    ]
    for bx, by, bw, bh in mid_bldgs:
        s.add(el("rect", x=bx, y=by, width=bw, height=bh, fill="#122033", opacity=0.88))
        # subtle window grid
        for wy in range(by + 15, by + bh - 10, 14):
            for wx in range(bx + 8, bx + bw - 8, 10):
                if (wx + wy) % 7 != 0:
                    s.add(el("rect", x=wx, y=wy, width=5, height=6, fill="#ffe8aa", opacity=0.45))

    # FOREGROUND ICONIC ARCHITECTURE
    # 1. Grand Sovereign Pyramid (Left-center: x=440..580, base=410, apex=230)
    pyr_pts = [(430, 410), (510, 230), (590, 410)]
    s.add(el("polygon", points=" ".join(f"{x},{y}" for x, y in pyr_pts), fill="#1a2e47"))
    # Terraced facets
    for step in range(1, 5):
        y_step = 230 + step * 40
        w_step = step * 38
        s.add(el("line", x1=510 - w_step, y1=y_step, x2=510 + w_step, y2=y_step, stroke="#f0be50", stroke_width=2, opacity=0.85))
        # hanging garden green band
        s.add(el("rect", x=510 - w_step + 4, y=y_step - 5, width=(w_step - 4) * 2, height=5, fill="#2b8c5a", opacity=0.85))
    # Pyramid Apex Beacon
    s.add(el("circle", cx=510, cy=226, r=6, fill="#fff2a1", class_="city-anim-beacon"))
    s.add(el("line", x1=510, y1=220, x2=510, y2=140, stroke="#fff5b8", stroke_width=2.5, opacity=0.75, class_="city-anim-beacon"))

    # 2. World Government Center (Three towers connected by skybridge: x=610..770)
    # Left tower (620..660, y=140..410)
    s.add(el("rect", x=620, y=150, width=40, height=260, fill="#17314d"))
    # Center tower (670..710, y=120..410)
    s.add(el("rect", x=670, y=130, width=42, height=280, fill="#1d3d61"))
    # Right tower (720..760, y=150..410)
    s.add(el("rect", x=722, y=150, width=40, height=260, fill="#17314d"))
    # High-Altitude Skybridge Oasis spanning all three at y=170..195
    s.add(el("path", d="M610,195 Q690,175 770,195 L770,180 Q690,160 610,180 Z", fill=gold_grad))
    s.add(el("rect", x=630, y=172, width=120, height=5, fill="#00ffff", opacity=0.8))  # skybridge infinity pool glow
    # Tower windows
    for tx in (626, 676, 728):
        for ty in range(160, 400, 12):
            s.add(el("line", x1=tx, y1=ty, x2=tx + 28, y2=ty, stroke="#aadeff", stroke_width=2.5, opacity=0.55))

    # 3. Sky City (956 m) — World's Tallest Building (Center-right: x=820..880, soaring to y=40!)
    # Tower base to pinnacle
    sky_city_poly = [
        (810, 410),
        (835, 260),
        (842, 160),
        (847, 80),
        (849, 45),
        (850, 20),  # antenna spire tip
        (851, 45),
        (853, 80),
        (858, 160),
        (865, 260),
        (890, 410),
    ]
    s.add(el("polygon", points=" ".join(f"{x},{y}" for x, y in sky_city_poly), fill=glass_spire))
    # Stepped setbacks and illuminated rings
    for sby, sbw in [(260, 32), (180, 22), (120, 14), (70, 8)]:
        s.add(el("line", x1=850 - sbw, y1=sby, x2=850 + sbw, y2=sby, stroke="#ffffff", stroke_width=2.5, opacity=0.9))
    # Vertical illuminated spine
    s.add(el("line", x1=850, y1=45, x2=850, y2=410, stroke="#00e5ff", stroke_width=2.5, opacity=0.85))
    # Aircraft warning beacon at peak
    s.add(el("circle", cx=850, cy=20, r=4.5, fill="#ff2244", class_="city-anim-beacon"))
    # Observatory halo
    s.add(el("ellipse", cx=850, cy=140, rx=16, ry=4, fill="#ffea9f", opacity=0.95))

    # 4. Infinity Tower (90-degree twist: x=930..985, y=140..410)
    # Sweeping helical spline curves
    s.add(
        el(
            "path",
            d="M935,410 C930,330 965,240 945,160 L975,150 C960,230 985,320 980,410 Z",
            fill="#204060",
            stroke="#a1d8f7",
            stroke_width=1.5,
        )
    )
    # Torsion facet lines
    for i in range(12):
        ty = 160 + i * 20
        tx1 = 945 - math.sin(i * 0.4) * 8
        tx2 = 975 + math.sin(i * 0.4) * 8
        s.add(el("line", x1=tx1, y1=ty, x2=tx2, y2=ty + 6, stroke="#d4eeff", stroke_width=1.8, opacity=0.6))

    # 5. Royal Clock Tower (Historic Stone Landmark: x=1030..1075, y=210..410)
    # Stone shaft
    s.add(el("rect", x=1030, y=240, width=42, height=170, fill="#4a3b32", stroke="#b38222", stroke_width=1.5))
    # Clock stage and Golden Cupola
    s.add(el("rect", x=1026, y=210, width=50, height=32, fill="#382c25"))
    s.add(el("path", d="M1026,210 Q1051,180 1076,210 Z", fill=gold_grad))  # cupola dome
    s.add(el("line", x1=1051, y1=180, x2=1051, y2=165, stroke="#f0be50", stroke_width=2))
    # Illuminated golden clock face
    s.add(el("circle", cx=1051, cy=226, r=10, fill="#fff2a1", stroke="#916515", stroke_width=2))
    s.add(el("line", x1=1051, y1=226, x2=1051, y2=219, stroke="#332211", stroke_width=1.5))
    s.add(el("line", x1=1051, y1=226, x2=1057, y2=226, stroke="#332211", stroke_width=1.5))

    # Trans-Lagoon Monorail Viaduct crossing from x=300 to x=1250 at y=385
    s.add(el("line", x1=260, y1=385, x2=1280, y2=385, stroke="#40658a", stroke_width=4))
    s.add(el("line", x1=260, y1=387, x2=1280, y2=387, stroke="#00e5ff", stroke_width=1.5, opacity=0.8))  # magnetic rail glow
    # Viaduct pylons into the water
    for px in range(320, 1260, 90):
        s.add(el("rect", x=px, y=385, width=6, height=35, fill="#2b4766"))
    # Sleek aerotrain gliding on viaduct (x=730..810)
    s.add(el("rect", x=730, y=378, width=75, height=7, rx=3, fill="#ffffff"))
    s.add(el("rect", x=735, y=379, width=65, height=2.5, fill="#00ffff"))

    # Waterfront Esplanade and Harbor Quay (y=410)
    s.add(el("rect", x=0, y=410, width=1600, height=14, fill="#182333"))
    s.add(el("line", x1=0, y1=410, x2=1600, y2=410, stroke="#f0be50", stroke_width=2))  # promenade brass rail

    # Promenade Royal Palms
    for palm_x in [80, 160, 240, 380, 600, 780, 910, 1010, 1120, 1220, 1460, 1540]:
        # Trunk
        s.add(el("path", d=f"M{palm_x},410 Q{palm_x-4},385 {palm_x+2},365", stroke="#544031", stroke_width=3, fill="none"))
        # Fronds
        for fx, fy in [(-18, -4), (18, -4), (-12, 10), (12, 10), (0, -14)]:
            s.add(
                el(
                    "path",
                    d=f"M{palm_x+2},365 Q{palm_x+2+fx*0.6},{365+fy*0.4} {palm_x+2+fx},{365+fy}",
                    stroke="#1f7a4d",
                    stroke_width=2.2,
                    fill="none",
                )
            )

    # 2. Lagoon Water Body (y=424..600)
    s.add(el("rect", x=0, y=424, width=1600, height=176, fill=water_grad))

    # Water shimmer and tower reflections
    # Sky City luminous reflection
    s.add(
        el(
            "polygon",
            points="845,424 855,424 868,590 832,590",
            fill="#00e5ff",
            opacity=0.22,
            class_="city-anim-water",
        )
    )
    # Infinity Tower reflection
    s.add(
        el(
            "polygon",
            points="940,424 970,424 985,570 930,570",
            fill="#ffcc66",
            opacity=0.18,
            class_="city-anim-water",
        )
    )
    # Gov Center reflection
    s.add(
        el(
            "polygon",
            points="630,424 750,424 760,560 620,560",
            fill="#aaddff",
            opacity=0.15,
            class_="city-anim-water",
        )
    )
    # Pyramid reflection
    s.add(
        el(
            "polygon",
            points="460,424 560,424 580,540 440,540",
            fill="#f0be50",
            opacity=0.2,
            class_="city-anim-water",
        )
    )

    # Water ripple wavelets
    for ry in range(435, 595, 12):
        r_op = 0.15 + (ry - 435) / 160 * 0.25
        s.add(
            el(
                "line",
                x1=40,
                y1=ry,
                x2=1560,
                y2=ry,
                stroke="#66bbee",
                stroke_width=1.2,
                stroke_dasharray="24 16 60 20 40 30",
                opacity=r_op,
            )
        )

    # Electric Superyachts and Catamarans on the Lagoon
    # Yacht 1 (Left foreground: x=180..290, y=490)
    s.add(el("path", d="M180,505 L275,505 L290,492 L210,492 Z", fill="#fdfdfd", stroke="#122538", stroke_width=1.5))
    s.add(el("rect", x=215, y=480, width=50, height=12, rx=3, fill="#e8f4fc", stroke="#003366", stroke_width=1))
    s.add(el("line", x1=235, y1=480, x2=235, y2=450, stroke="#8899aa", stroke_width=1.5))  # mast
    # Yacht 2 (Center-right: x=1080..1180, y=520)
    s.add(el("path", d="M1080,530 L1165,530 L1185,518 L1110,518 Z", fill="#ffffff", stroke="#122538", stroke_width=1.5))
    s.add(el("rect", x=1115, y=508, width=45, height=10, rx=2, fill="#e8f4fc"))
    s.add(el("line", x1=1130, y1=508, x2=1130, y2=475, stroke="#8899aa", stroke_width=1.5))

    # LOCALIZED OVERLAY LABELS and HOTSPOTS
    labels_data = [
        (t["pyramid_monument"], 510, 205, 510, 226),
        (t["gov_center"], 690, 105, 690, 130),
        (t["sky_city"], 850, 12, 850, 30),
        (t["infinity_tower"], 960, 130, 960, 150),
        (t["clock_tower"], 1051, 150, 1051, 175),
        (t["monorail_line"], 360, 365, 360, 385),
        (t["marina_aurelia"], 240, 530, 240, 505),
    ]
    for text, lx, ly, px, py in labels_data:
        # Leader line
        s.add(el("line", x1=lx, y1=ly + 8, x2=px, y2=py, stroke="#f0be50", stroke_width=1.2, stroke_dasharray="3 3", opacity=0.8))
        # Label pill background
        text_w = len(text) * 7.5 + 16
        s.add(
            el(
                "rect",
                x=lx - text_w / 2,
                y=ly - 12,
                width=text_w,
                height=22,
                rx=11,
                fill="#0d1b2a",
                stroke="#c28a29",
                stroke_width=1.2,
                opacity=0.92,
            )
        )
        s.add(
            el(
                "text",
                text,
                x=lx,
                y=ly + 3,
                fill="#ffffff",
                font_size=11,
                font_weight="bold",
                font_family="system-ui, -apple-system, sans-serif",
                text_anchor="middle",
            )
        )

    return s.render(t["skyline_title"])


# ==============================================================================
# 2. SCENE: PYRAMID (The Grand Sovereign Pyramid - 1200 x 700)
# ==============================================================================
def build_pyramid(t: dict[str, str]) -> str:
    s = Scene("pyramid", 1200, 700)

    # Gradients
    sky_grad = s.linear("pyr-sky", [(0.0, "#0e1e36"), (0.5, "#1a365d"), (0.85, "#2a5584"), (1.0, "#487ba8")])
    gold_grad = s.linear("pyr-gold", [(0.0, "#fff5cf"), (0.35, "#f7c858"), (0.8, "#b8831e"), (1.0, "#7a5310")])
    basalt_grad = s.linear("pyr-basalt", [(0.0, "#334155"), (0.5, "#1e293b"), (1.0, "#0f172a")])
    glass_grad = s.linear(
        "pyr-glass",
        [(0.0, "#c2e5ff", 0.9), (0.4, "#60a5fa", 0.75), (0.8, "#2563eb", 0.85), (1.0, "#1e3a8a", 0.9)],
        x1=0,
        y1=0,
        x2=1,
        y2=1,
    )
    water_grad = s.linear("pyr-water", [(0.0, "#0284c7"), (0.5, "#0369a1"), (1.0, "#075985")])

    # 1. Sky backdrop
    s.add(el("rect", width=1200, height=700, fill=sky_grad))

    # Sunburst behind pyramid apex
    s.add(el("circle", cx=600, cy=150, r=260, fill=gold_grad, opacity=0.15))

    # Stepped Terraces Geometry
    # Base: 600 center, y=560. Apex: y=130.
    # 4 distinct monumental tiers:
    # Tier 1 (Base): y=460..560, w=960 (x=120..1080)
    # Tier 2: y=360..460, w=760 (x=220..980)
    # Tier 3: y=260..360, w=540 (x=330..870)
    # Tier 4: y=160..260, w=320 (x=440..760)
    # Apex Capstone: y=110..160, w=140 (x=530..670)

    # Tier 1 (Base)
    s.add(el("polygon", points="120,560 220,460 980,460 1080,560", fill=basalt_grad))
    s.add(el("polygon", points="220,460 600,460 600,560 120,560", fill="#243447", opacity=0.4))  # left shadow
    # Tier 2
    s.add(el("polygon", points="220,460 330,360 870,360 980,460", fill=basalt_grad))
    # Tier 3
    s.add(el("polygon", points="330,360 440,260 760,260 870,360", fill=basalt_grad))
    # Tier 4
    s.add(el("polygon", points="440,260 530,160 670,160 760,260", fill=basalt_grad))

    # Right face solar photovoltaic crystalline skin
    s.add(el("polygon", points="600,160 670,160 760,260 870,360 980,460 1080,560 600,560", fill=glass_grad))
    # Photovoltaic grid mesh on right face
    for y_val in [200, 250, 300, 350, 400, 450, 500]:
        s.add(el("line", x1=600, y1=y_val, x2=600 + (y_val - 120) * 0.95, y2=y_val, stroke="#bae6fd", stroke_width=1.4, opacity=0.55))

    # Hanging Gardens and Waterfalls on Terraces
    # Left Terraces: Lush vegetation bands
    for tx, ty, tw in [(230, 452, 360), (340, 352, 250), (450, 252, 140)]:
        s.add(el("rect", x=tx, y=ty, width=tw, height=12, rx=4, fill="#166534"))
        # Tropical palm trees and orchids along terrace
        for px in range(tx + 10, tx + tw - 10, 28):
            s.add(el("circle", cx=px, cy=ty - 4, r=8, fill="#22c55e", opacity=0.9))
            s.add(el("circle", cx=px + 6, cy=ty - 7, r=6, fill="#4ade80", opacity=0.85))

    # Central Cascading Waterfalls down the center axis (x=590..610)
    for wy1, wy2 in [(160, 260), (260, 360), (360, 460), (460, 560)]:
        # Sluice chute
        s.add(el("rect", x=590, y=wy1, width=20, height=wy2 - wy1, fill="#38bdf8", opacity=0.9))
        # Foam splash
        s.add(el("ellipse", cx=600, cy=wy2, rx=24, ry=6, fill="#ffffff", opacity=0.9))

    # Apex Beacon and Hall of Nations (y=100..160)
    s.add(el("polygon", points="530,160 600,100 670,160", fill=gold_grad))
    s.add(el("circle", cx=600, cy=100, r=8, fill="#ffffff", class_="city-anim-beacon"))
    # Stratospheric light beam shooting up
    s.add(
        el(
            "polygon",
            points="596,100 604,100 625,0 575,0",
            fill="#fef08a",
            opacity=0.65,
            class_="city-anim-beacon",
        )
    )

    # Cutaway section on Left Wing (Assembly Amphitheater inside Tier 1 and 2: x=240..460, y=390..530)
    s.add(el("rect", x=240, y=410, width=220, height=120, rx=8, fill="#0f172a", stroke="#f59e0b", stroke_width=2))
    # Concentric seating tiers
    for r in range(25, 95, 16):
        s.add(el("path", d=f"M{350-r},{510} A{r},{r*0.6} 0 0 1 {350+r},{510}", stroke="#94a3b8", stroke_width=3, fill="none"))
    # Central sovereign dais
    s.add(el("circle", cx=350, cy=510, r=8, fill="#f59e0b"))

    # Ceremonial Plaza, Colonnade, and Reflecting Pools (y=560..700)
    s.add(el("rect", x=0, y=560, width=1200, height=140, fill="#1e293b"))
    # Grand Colonnade (14 columns at entrance)
    for cx in range(400, 820, 30):
        s.add(el("rect", x=cx, y=535, width=8, height=35, fill="#f8fafc", stroke="#cbd5e1", stroke_width=1))
    s.add(el("rect", x=390, y=530, width=430, height=6, fill="#f8fafc"))  # entablature
    # Reflecting pools (Left and Right)
    s.add(el("rect", x=80, y=590, width=420, height=80, rx=6, fill=water_grad, stroke="#f59e0b", stroke_width=1.5))
    s.add(el("rect", x=700, y=590, width=420, height=80, rx=6, fill=water_grad, stroke="#f59e0b", stroke_width=1.5))

    # Diplomatic VIP electric shuttles on the central causeway
    s.add(el("rect", x=540, y=620, width=45, height=18, rx=5, fill="#ffffff", stroke="#0284c7", stroke_width=1.5))
    s.add(el("rect", x=615, y=635, width=45, height=18, rx=5, fill="#ffffff", stroke="#0284c7", stroke_width=1.5))

    # LOCALIZED OVERLAY LABELS
    labels_data = [
        (t["apex_beacon"], 600, 75, 600, 100),
        (t["hanging_gardens"], 220, 290, 330, 350),
        (t["solar_skin"], 980, 290, 870, 360),
        (t["amphitheater"], 180, 480, 240, 480),
        (t["colonnade"], 600, 515, 600, 532),
    ]
    for text, lx, ly, px, py in labels_data:
        s.add(el("line", x1=lx, y1=ly + 8, x2=px, y2=py, stroke="#f59e0b", stroke_width=1.2, stroke_dasharray="3 3"))
        text_w = len(text) * 7.5 + 16
        s.add(el("rect", x=lx - text_w / 2, y=ly - 12, width=text_w, height=22, rx=11, fill="#0f172a", stroke="#f59e0b", stroke_width=1.2))
        s.add(el("text", text, x=lx, y=ly + 3, fill="#ffffff", font_size=11, font_weight="bold", font_family="system-ui, sans-serif", text_anchor="middle"))

    return s.render(t["pyramid_title"])


# ==============================================================================
# 3. SCENE: UNDERSEA-HUB (Trans-Lagoon Maglev - 1200 x 700)
# ==============================================================================
def build_undersea_hub(t: dict[str, str]) -> str:
    s = Scene("undersea-hub", 1200, 700)

    # Gradients
    sky_grad = s.linear("uh-sky", [(0.0, "#0284c7"), (0.6, "#38bdf8"), (1.0, "#bae6fd")])
    sea_grad = s.linear(
        "uh-sea",
        [(0.0, "#0284c7", 0.8), (0.2, "#0369a1"), (0.5, "#075985"), (0.8, "#0c4a6e"), (1.0, "#082f49")],
    )
    tube_glass = s.linear(
        "uh-glass",
        [(0.0, "#ffffff", 0.6), (0.3, "#38bdf8", 0.3), (0.7, "#0284c7", 0.4), (1.0, "#ffffff", 0.7)],
        x1=0,
        y1=0,
        x2=0,
        y2=1,
    )
    train_grad = s.linear("uh-train", [(0.0, "#ffffff"), (0.4, "#e0f2fe"), (0.8, "#0284c7"), (1.0, "#0369a1")])

    # 1. Surface Upper Realm (y=0..240)
    s.add(el("rect", width=1200, height=240, fill=sky_grad))
    # Terminal Building on the Quay (x=100..500, y=70..240)
    s.add(el("rect", x=120, y=140, width=360, height=100, fill="#f8fafc", stroke="#0369a1", stroke_width=2))
    # Curving glass aerodynamic roof
    s.add(el("path", d="M100,140 Q300,50 500,140 Z", fill="#bae6fd", opacity=0.85, stroke="#0284c7", stroke_width=2))
    # Marina quay wall
    s.add(el("rect", x=0, y=230, width=1200, height=15, fill="#334155"))

    # Solar Catamaran at Surface Dock (x=680..860, y=210)
    s.add(el("path", d="M680,230 L840,230 L860,205 L720,205 Z", fill="#ffffff", stroke="#0369a1", stroke_width=1.5))
    s.add(el("rect", x=730, y=185, width=80, height=20, rx=4, fill="#38bdf8", opacity=0.8))

    # 2. Water Surface Line and Waves (y=240)
    s.add(
        el(
            "path",
            d="M0,240 Q150,234 300,240 T600,240 T900,240 T1200,240 L1200,700 L0,700 Z",
            fill=sea_grad,
        )
    )
    # Sunlight crepuscular rays piercing underwater
    for rx in range(150, 1100, 180):
        s.add(
            el(
                "polygon",
                points=f"{rx},240 {rx+40},240 {rx+140},700 {rx-60},700",
                fill="#ffffff",
                opacity=0.08,
            )
        )

    # 3. Subsea Realm (y=245..700)
    # Seafloor bedrock and reef substrate (y=620..700)
    s.add(el("path", d="M0,640 Q250,610 500,635 T900,615 T1200,645 L1200,700 L0,700 Z", fill="#1e293b"))

    # Living Coral Formations
    for cx, ch, col in [(80, 70, "#f43f5e"), (180, 50, "#ec4899"), (480, 60, "#a855f7"), (920, 80, "#f97316"), (1080, 65, "#10b981")]:
        s.add(el("ellipse", cx=cx, cy=630, rx=35, ry=ch * 0.4, fill=col, opacity=0.85))
        # Brain coral ridges
        s.add(el("path", d=f"M{cx-20},{630} Q{cx},{630-ch*0.3} {cx+20},{630}", stroke="#ffffff", stroke_width=1.5, fill="none", opacity=0.5))

    # Subsea Observation Dome (Connected to terminal: x=240..420, y=360..480)
    s.add(el("circle", cx=330, cy=420, r=60, fill="#bae6fd", opacity=0.45, stroke="#38bdf8", stroke_width=3))
    s.add(el("rect", x=322, y=240, width=16, height=125, fill="#64748b"))  # elevator access column
    # Scientists/observers inside dome
    s.add(el("circle", cx=325, cy=415, r=4, fill="#f8fafc"))
    s.add(el("circle", cx=340, cy=415, r=4, fill="#f8fafc"))

    # The Acrylic Vacuum Maglev Tube (Spanning horizontally: y=460..570)
    # Pylons anchored to seabed
    for px in [140, 480, 780, 1060]:
        s.add(el("rect", x=px, y=550, width=28, height=85, fill="#475569", stroke="#0f172a", stroke_width=1.5))
        s.add(el("polygon", points=f"{px-12},635 {px+40},635 {px+28},590 {px},590", fill="#334155"))
    # Tube Cylindrical Shell (y=470..550, height=80)
    s.add(el("rect", x=0, y=470, width=1200, height=80, rx=40, fill=tube_glass, stroke="#38bdf8", stroke_width=2.5))
    # Magnetic levitation track rail inside tube
    s.add(el("line", x1=0, y1=535, x2=1200, y2=535, stroke="#0284c7", stroke_width=4))
    s.add(el("line", x1=0, y1=537, x2=1200, y2=537, stroke="#00ffff", stroke_width=1.8))  # magnetic glow

    # Futuristic High-Speed Maglev Train speeding inside the tube (x=520..880)
    # Aerodynamic nose and body
    s.add(el("path", d="M520,530 L800,530 Q870,530 880,520 Q870,490 800,490 L520,490 Z", fill=train_grad))
    # Passenger panoramic windows
    for wx in range(540, 780, 32):
        s.add(el("rect", x=wx, y=498, width=22, height=14, rx=3, fill="#fef08a", opacity=0.95))
    s.add(el("line", x1=520, y1=524, x2=870, y2=524, stroke="#38bdf8", stroke_width=2))

    # Marine Life Swimming
    # Manta Ray gliding above tube (x=680, y=340)
    s.add(
        el(
            "path",
            d="M680,340 Q710,300 750,335 Q710,345 680,340 M680,340 Q650,300 610,335 Q650,345 680,340 M680,340 L680,380",
            fill="#1e293b",
            stroke="#0f172a",
            stroke_width=1.5,
        )
    )
    # Sea Turtle (Honu: x=980, y=380)
    s.add(el("ellipse", cx=980, cy=380, rx=18, ry=14, fill="#15803d", stroke="#166534", stroke_width=1.5))
    s.add(el("circle", cx=1000, cy=378, r=5, fill="#166534"))
    # Bioluminescent Jellyfish
    for jx, jy in [(180, 320), (840, 420), (1050, 280)]:
        s.add(el("path", d=f"M{jx-12},{jy} A12,10 0 0 1 {jx+12},{jy} Z", fill="#00ffff", opacity=0.75, class_="city-anim-biolum"))
        s.add(el("path", d=f"M{jx-8},{jy} Q{jx-10},{jy+20} {jx-6},{jy+35}", stroke="#00ffff", stroke_width=1.2, fill="none", opacity=0.7))
        s.add(el("path", d=f"M{jx+8},{jy} Q{jx+10},{jy+20} {jx+6},{jy+35}", stroke="#00ffff", stroke_width=1.2, fill="none", opacity=0.7))

    # LOCALIZED OVERLAY LABELS
    labels_data = [
        (t["surface_terminal"], 300, 110, 300, 140),
        (t["obs_dome"], 180, 420, 270, 420),
        (t["acrylic_tube"], 1020, 435, 1020, 470),
        (t["maglev_train"], 700, 460, 700, 490),
        (t["coral_sanctuary"], 920, 675, 920, 630),
    ]
    for text, lx, ly, px, py in labels_data:
        s.add(el("line", x1=lx, y1=ly + 8, x2=px, y2=py, stroke="#00ffff", stroke_width=1.2, stroke_dasharray="3 3"))
        text_w = len(text) * 7.5 + 16
        s.add(el("rect", x=lx - text_w / 2, y=ly - 12, width=text_w, height=22, rx=11, fill="#082f49", stroke="#00ffff", stroke_width=1.2))
        s.add(el("text", text, x=lx, y=ly + 3, fill="#ffffff", font_size=11, font_weight="bold", font_family="system-ui, sans-serif", text_anchor="middle"))

    return s.render(t["undersea_title"])


# ==============================================================================
# 4. SCENE: ARCHIPELAGO-MAP (Cartographic Masterplan - 1100 x 600)
# ==============================================================================
def build_archipelago_map(t: dict[str, str]) -> str:
    s = Scene("archipelago-map", 1100, 600)

    # Gradients
    ocean_grad = s.linear(
        "map-ocean",
        [(0.0, "#082f49"), (0.4, "#0c4a6e"), (0.7, "#075985"), (1.0, "#0284c7")],
    )
    land_grad = s.linear("map-land", [(0.0, "#334155"), (1.0, "#1e293b")])
    island_grad = s.linear("map-island", [(0.0, "#fde68a"), (0.5, "#d97706"), (1.0, "#b45309")])

    # 1. Ocean Background
    s.add(el("rect", width=1100, height=600, fill=ocean_grad))

    # Bathymetric depth contour lines
    for r, op in [(180, 0.2), (280, 0.16), (420, 0.12), (580, 0.08)]:
        s.add(el("ellipse", cx=550, cy=300, rx=r * 1.5, ry=r, stroke="#38bdf8", stroke_width=1.5, fill="none", opacity=op))

    # Cartographic coordinate grid ticks
    for gx in range(100, 1050, 150):
        s.add(el("line", x1=gx, y1=20, x2=gx, y2=580, stroke="#38bdf8", stroke_width=0.8, stroke_dasharray="4 8", opacity=0.2))
    for gy in range(80, 560, 100):
        s.add(el("line", x1=40, y1=gy, x2=1060, y2=gy, stroke="#38bdf8", stroke_width=0.8, stroke_dasharray="4 8", opacity=0.2))

    # 2. Mainland Nova Aurelia Coastline (Left edge: x=0..180)
    s.add(el("path", d="M0,0 L140,0 Q180,200 120,380 Q190,500 130,600 L0,600 Z", fill=land_grad, stroke="#f59e0b", stroke_width=2))
    # Mainland urban district textures
    for ux, uy in [(40, 80), (60, 160), (45, 260), (70, 360), (50, 480)]:
        s.add(el("rect", x=ux, y=uy, width=45, height=28, rx=2, fill="#475569", opacity=0.7))

    # 3. Outer Bio-Calcified Coral Barrier Reef (Crescent barrier reef enclosing the archipelago: x=850..960)
    s.add(
        el(
            "path",
            d="M820,60 C980,180 980,420 820,540",
            stroke="#2dd4bf",
            stroke_width=16,
            stroke_dasharray="35 12 60 15",
            fill="none",
            opacity=0.7,
        )
    )

    # 4. PALM ISLAND (Center-left: cx=380, cy=320)
    # Palm Trunk and Crescent Breakwater
    s.add(el("circle", cx=380, cy=320, r=85, stroke=island_grad, stroke_width=6, stroke_dasharray="140 25 140 25", fill="none"))
    # Trunk causeway
    s.add(el("line", x1=160, y1=320, x2=380, y2=320, stroke=island_grad, stroke_width=8))
    # Palm fronds (16 distinct fronds branching outward)
    for fa in range(16):
        angle = -1.2 + fa * 0.16
        fx2 = 380 + math.cos(angle) * 72
        fy2 = 320 + math.sin(angle) * 72
        s.add(el("line", x1=380, y1=320, x2=fx2, y2=fy2, stroke=island_grad, stroke_width=4))
    # Hotel Khalifa at the outer crescent apex (x=465, y=320)
    s.add(el("circle", cx=465, cy=320, r=9, fill="#fef08a", stroke="#b45309", stroke_width=2))

    # 5. WORLD ISLANDS (Archipelago of continent-shaped islands: cx=680, cy=240)
    # Cluster of 24 representative islands depicting the world continents
    continents = [
        # North America cluster
        (600, 180, 14, 10),
        (618, 165, 12, 8),
        (610, 200, 16, 12),
        # South America cluster
        (630, 240, 14, 18),
        (635, 275, 11, 14),
        # Europe cluster
        (670, 180, 12, 10),
        (685, 175, 14, 9),
        # Africa cluster
        (675, 220, 18, 22),
        (680, 260, 16, 18),
        # Asia cluster
        (720, 180, 22, 16),
        (745, 175, 20, 14),
        (760, 210, 18, 14),
        (735, 225, 15, 12),
        # Oceania cluster
        (765, 270, 16, 12),
        (785, 290, 10, 8),
    ]
    for ix, iy, irx, iry in continents:
        s.add(el("ellipse", cx=ix, cy=iy, rx=irx, ry=iry, fill=island_grad, stroke="#78350f", stroke_width=1))

    # 6. CHAMELEON ATOLLS (Marine Biology Labs: cx=660, cy=440)
    for atoll_x, atoll_y, ar in [(600, 440, 28), (660, 460, 34), (730, 430, 26)]:
        s.add(el("circle", cx=atoll_x, cy=atoll_y, r=ar, fill="#075985", stroke="#10b981", stroke_width=5))
        # Research pods
        s.add(el("circle", cx=atoll_x + ar * 0.7, cy=atoll_y, r=4, fill="#ffffff"))

    # 7. Subsea Maglev Transit Network (Cyan glowing vectors connecting mainland to islands)
    # Line 1: Mainland to Palm Island
    s.add(el("line", x1=140, y1=320, x2=465, y2=320, stroke="#00ffff", stroke_width=3, stroke_dasharray="8 4"))
    # Line 2: Mainland to World Islands
    s.add(el("path", d="M140,240 Q380,180 670,220", stroke="#00ffff", stroke_width=2.5, stroke_dasharray="8 4", fill="none"))
    # Line 3: World Islands to Chameleon Atolls
    s.add(el("line", x1=670, y1=280, x2=660, y2=430, stroke="#00ffff", stroke_width=2, stroke_dasharray="8 4"))

    # Compass Rose (Top Right: x=980, y=90)
    s.add(el("circle", cx=980, cy=90, r=26, fill="#0f172a", stroke="#f59e0b", stroke_width=1.5))
    s.add(el("polygon", points="980,68 985,88 980,85 975,88", fill="#f59e0b"))
    s.add(el("polygon", points="980,112 985,92 980,95 975,92", fill="#94a3b8"))
    s.add(el("text", "N", x=980, y=64, fill="#f59e0b", font_size=11, font_weight="bold", text_anchor="middle"))

    # LOCALIZED OVERLAY LABELS
    labels_data = [
        (t["mainland_aurelia"], 90, 310, 140, 310),
        (t["palm_island"], 380, 220, 380, 250),
        (t["hotel_khalifa"], 470, 355, 465, 330),
        (t["world_islands"], 700, 125, 700, 160),
        (t["chameleon_atolls"], 660, 520, 660, 480),
        (t["coral_barrier"], 940, 400, 910, 400),
        (t["subsea_maglev"], 300, 270, 300, 290),
    ]
    for text, lx, ly, px, py in labels_data:
        s.add(el("line", x1=lx, y1=ly + 8, x2=px, y2=py, stroke="#f59e0b", stroke_width=1.2, stroke_dasharray="3 3"))
        text_w = len(text) * 7.5 + 16
        s.add(el("rect", x=lx - text_w / 2, y=ly - 12, width=text_w, height=22, rx=11, fill="#0f172a", stroke="#f59e0b", stroke_width=1.2))
        s.add(el("text", text, x=lx, y=ly + 3, fill="#ffffff", font_size=11, font_weight="bold", font_family="system-ui, sans-serif", text_anchor="middle"))

    return s.render(t["archipelago_title"])


# ==============================================================================
# 5. VIGNETTE 1: MARINA AURELIA (640 x 420)
# ==============================================================================
def build_marina(t: dict[str, str]) -> str:
    s = Scene("marina", 640, 420)

    sky_grad = s.linear("mar-sky", [(0.0, "#0369a1"), (0.5, "#38bdf8"), (1.0, "#fde68a")])
    water_grad = s.linear("mar-water", [(0.0, "#0284c7"), (0.5, "#0369a1"), (1.0, "#082f49")])
    gold_grad = s.linear("mar-gold", [(0.0, "#fef08a"), (0.5, "#f59e0b"), (1.0, "#b45309")])

    s.add(el("rect", width=640, height=420, fill=sky_grad))

    # Spiral Lighthouse Pavilion (Left side: x=60..140, y=70..270)
    s.add(el("rect", x=70, y=120, width=50, height=150, fill="#f8fafc", stroke="#0284c7", stroke_width=1.5))
    # Helical observation ramp winding up
    for ry in range(130, 260, 20):
        s.add(el("line", x1=65, y1=ry, x2=125, y2=ry + 10, stroke="#f59e0b", stroke_width=3))
    # Lantern room and golden cupola
    s.add(el("circle", cx=95, cy=105, r=18, fill="#fef08a", stroke="#b45309", stroke_width=2, class_="city-anim-beacon"))
    s.add(el("path", d="M75,95 Q95,70 115,95 Z", fill=gold_grad))

    # Harbor Promenade and Quays (y=260..290)
    s.add(el("rect", x=0, y=260, width=640, height=30, fill="#334155"))
    # Promenade Palms and Streetlamps
    for px in [160, 230, 300, 560]:
        s.add(el("path", d=f"M{px},260 Q{px-3},235 {px+2},215", stroke="#544031", stroke_width=2.5, fill="none"))
        s.add(el("circle", cx=px + 2, cy=215, r=14, fill="#15803d", opacity=0.9))

    # Water Basin (y=290..420)
    s.add(el("rect", x=0, y=290, width=640, height=130, fill=water_grad))

    # Floating Teak Docks (x=180..620)
    for dy in [320, 375]:
        s.add(el("rect", x=200, y=dy, width=420, height=12, fill="#b45309", stroke="#78350f", stroke_width=1))

    # Zero-Emission Electric Superyachts berthed
    # Yacht 1 (x=240..370, y=300)
    s.add(el("path", d="M240,320 L350,320 L370,305 L260,305 Z", fill="#ffffff", stroke="#0284c7", stroke_width=1.2))
    s.add(el("rect", x=270, y=295, width=60, height=10, rx=2, fill="#38bdf8", opacity=0.8))
    # Yacht 2 (x=410..560, y=355)
    s.add(el("path", d="M410,375 L540,375 L565,358 L435,358 Z", fill="#ffffff", stroke="#0284c7", stroke_width=1.2))
    s.add(el("rect", x=445, y=348, width=70, height=10, rx=2, fill="#38bdf8", opacity=0.8))

    # Localized Title Badge
    s.add(el("rect", x=20, y=20, width=len(t["marina_title"]) * 7.5 + 24, height=28, rx=14, fill="#0f172a", stroke="#f59e0b", stroke_width=1.2))
    s.add(el("text", t["marina_title"], x=32, y=38, fill="#ffffff", font_size=12, font_weight="bold", font_family="system-ui, sans-serif"))

    return s.render(t["marina_title"])


# ==============================================================================
# 6. VIGNETTE 2: VIA AURELIA (640 x 420)
# ==============================================================================
def build_boulevard(t: dict[str, str]) -> str:
    s = Scene("boulevard", 640, 420)

    sky_grad = s.linear("bld-sky", [(0.0, "#1e3a8a"), (0.6, "#3b82f6"), (1.0, "#93c5fd")])
    pave_grad = s.linear("bld-pave", [(0.0, "#475569"), (0.5, "#334155"), (1.0, "#1e293b")])
    gold_grad = s.linear("bld-gold", [(0.0, "#fef08a"), (0.5, "#f59e0b"), (1.0, "#b45309")])

    s.add(el("rect", width=640, height=420, fill=sky_grad))

    # Triumphal Imperial Roman Arch in the distant axis (center: cx=320, cy=180)
    s.add(el("rect", x=280, y=140, width=80, height=75, fill="#f8fafc", stroke="#b45309", stroke_width=2))
    s.add(el("path", d="M305,215 A15,25 0 0 1 335,215 Z", fill="#1e3a8a"))
    s.add(el("rect", x=275, y=134, width=90, height=8, fill=gold_grad))

    # Perspective Boulevard Floor
    s.add(el("polygon", points="290,215 350,215 580,420 60,420", fill=pave_grad))

    # Corinthian Marble Colonnades on left and right
    for i in range(5):
        scale = 0.5 + i * 0.15
        cy_bot = 220 + i * 45
        # Left columns
        lx = 270 - i * 45
        s.add(el("rect", x=lx, y=cy_bot - 80 * scale, width=12 * scale, height=80 * scale, fill="#f8fafc", stroke="#cbd5e1", stroke_width=1))
        # Right columns
        rx = 360 + i * 45
        s.add(el("rect", x=rx, y=cy_bot - 80 * scale, width=12 * scale, height=80 * scale, fill="#f8fafc", stroke="#cbd5e1", stroke_width=1))

    # Central Median with Dancing Fountains and Royal Date Palms
    s.add(el("polygon", points="315,215 325,215 335,420 305,420", fill="#166534"))
    # Synchronized Dancing Fountains
    for fy in [250, 310, 380]:
        s.add(el("line", x1=320, y1=fy, x2=320, y2=fy - 25, stroke="#38bdf8", stroke_width=2.5, class_="city-anim-water"))
        s.add(el("ellipse", cx=320, cy=fy, rx=12, ry=4, fill="#bae6fd", opacity=0.8))

    # Autonomous Electric Pod Shuttles on Boulevard Lanes
    s.add(el("rect", x=200, y=340, width=55, height=28, rx=8, fill="#ffffff", stroke="#0284c7", stroke_width=1.5))
    s.add(el("rect", x=208, y=346, width=38, height=12, rx=3, fill="#38bdf8", opacity=0.7))
    s.add(el("circle", cx=210, cy=368, r=5, fill="#0f172a"))
    s.add(el("circle", cx=245, cy=368, r=5, fill="#0f172a"))

    # Localized Title Badge
    s.add(el("rect", x=20, y=20, width=len(t["boulevard_title"]) * 7.5 + 24, height=28, rx=14, fill="#0f172a", stroke="#f59e0b", stroke_width=1.2))
    s.add(el("text", t["boulevard_title"], x=32, y=38, fill="#ffffff", font_size=12, font_weight="bold", font_family="system-ui, sans-serif"))

    return s.render(t["boulevard_title"])


# ==============================================================================
# 7. VIGNETTE 3: AEROTROPOLIS (640 x 420)
# ==============================================================================
def build_aerotropolis(t: dict[str, str]) -> str:
    s = Scene("aerotropolis", 640, 420)

    sky_grad = s.linear("aero-sky", [(0.0, "#020617"), (0.5, "#0f172a"), (0.8, "#1e293b"), (1.0, "#334155")])
    runway_grad = s.linear("aero-rwy", [(0.0, "#1e293b"), (1.0, "#0f172a")])

    s.add(el("rect", width=640, height=420, fill=sky_grad))

    # High Altitude Cirrus and Sunset Rim
    s.add(el("ellipse", cx=320, cy=240, rx=380, ry=20, fill="#f59e0b", opacity=0.25))

    # Orbital Launch Telemetry Dish (Left: cx=120, cy=180)
    s.add(el("path", d="M80,170 Q120,130 160,170 Z", fill="#e2e8f0", stroke="#0284c7", stroke_width=2))
    s.add(el("line", x1=120, y1=150, x2=120, y2=210, stroke="#64748b", stroke_width=3))
    s.add(el("polygon", points="105,210 135,210 120,185", fill="#334155"))

    # Stratospheric Hydrogen Dirigible / Air Cruiser moored to mast (x=380..580, y=70..150)
    s.add(el("ellipse", cx=480, cy=100, rx=90, ry=28, fill="#f8fafc", stroke="#38bdf8", stroke_width=1.8))
    s.add(el("rect", x=440, y=125, width=60, height=12, rx=3, fill="#0284c7"))  # passenger observation car
    # Mooring mast
    s.add(el("line", x1=560, y1=100, x2=560, y2=260, stroke="#f59e0b", stroke_width=3))

    # Runway Apron (y=260..420)
    s.add(el("rect", x=0, y=260, width=640, height=160, fill=runway_grad))
    # Runway centerline glowing cyan dashes
    s.add(el("line", x1=40, y1=340, x2=600, y2=340, stroke="#00ffff", stroke_width=3, stroke_dasharray="25 15"))

    # Delta-Wing Trans-Atmospheric Shuttle on Runway Apron (x=240..420, y=300..380)
    s.add(el("polygon", points="330,290 410,360 380,365 330,355 280,365 250,360", fill="#ffffff", stroke="#0284c7", stroke_width=2))
    s.add(el("polygon", points="330,305 342,330 318,330", fill="#0f172a"))  # cockpit canopy
    # Ion engine glow
    s.add(el("circle", cx=330, cy=360, r=6, fill="#00ffff", class_="city-anim-beacon"))

    # Localized Title Badge
    s.add(el("rect", x=20, y=20, width=len(t["aerotropolis_title"]) * 7.5 + 24, height=28, rx=14, fill="#0f172a", stroke="#f59e0b", stroke_width=1.2))
    s.add(el("text", t["aerotropolis_title"], x=32, y=38, fill="#ffffff", font_size=12, font_weight="bold", font_family="system-ui, sans-serif"))

    return s.render(t["aerotropolis_title"])


# ==============================================================================
# 8. VIGNETTE 4: NIGHT-LAGOON (640 x 420)
# ==============================================================================
def build_night_lagoon(t: dict[str, str]) -> str:
    s = Scene("night-lagoon", 640, 420)

    sky_grad = s.linear("nl-sky", [(0.0, "#050b14"), (0.5, "#0b172a"), (1.0, "#0d223a")])
    water_grad = s.linear("nl-water", [(0.0, "#031526"), (0.6, "#042036"), (1.0, "#020e1a")])

    s.add(el("rect", width=640, height=420, fill=sky_grad))

    # Crescent Moon and Stars
    s.add(el("path", d="M540,60 A18,18 0 0 1 558,78 A18,18 0 1 0 540,60 Z", fill="#fef08a"))
    for sx, sy in [(80, 50), (140, 80), (220, 40), (320, 70), (420, 50), (490, 90), (600, 45)]:
        s.add(el("circle", cx=sx, cy=sy, r=1.5, fill="#ffffff", opacity=0.8))

    # Distant Illuminated Skyline (y=140..250)
    for bx, by, bw, bh in [(60, 160, 40, 90), (110, 130, 35, 120), (155, 170, 50, 80), (440, 140, 45, 110), (495, 160, 55, 90)]:
        s.add(el("rect", x=bx, y=by, width=bw, height=bh, fill="#09131f", stroke="#00e5ff", stroke_width=0.8))
        # Window glow dots
        for wy in range(by + 10, by + bh - 10, 12):
            s.add(el("rect", x=bx + 8, y=wy, width=bw - 16, height=4, fill="#fef08a", opacity=0.7))

    # Night Lagoon Water Surface (y=250..420)
    s.add(el("rect", x=0, y=250, width=640, height=170, fill=water_grad))

    # Bioluminescent Waters and Canal Margins (Cyan and Emerald glowing trails)
    for wy in [270, 310, 350, 390]:
        s.add(
            el(
                "path",
                d=f"M0,{wy} Q160,{wy-8} 320,{wy} T640,{wy}",
                stroke="#00ffff",
                stroke_width=3,
                fill="none",
                opacity=0.65,
                class_="city-anim-biolum",
            )
        )
        s.add(
            el(
                "path",
                d=f"M40,{wy+8} Q220,{wy+14} 400,{wy+6} T620,{wy+10}",
                stroke="#10b981",
                stroke_width=2,
                fill="none",
                opacity=0.5,
                class_="city-anim-biolum",
            )
        )

    # Illuminated Floating Boardwalk Pontoon (Crossing from left to right: y=310..340)
    s.add(el("rect", x=80, y=320, width=480, height=14, rx=4, fill="#1e293b", stroke="#f59e0b", stroke_width=1.5))
    # Glowing orb lanterns along boardwalk
    for lx in range(110, 550, 45):
        s.add(el("circle", cx=lx, cy=312, r=4, fill="#fef08a", stroke="#f59e0b", stroke_width=1, class_="city-anim-beacon"))

    # Solar Electric Water Taxi gliding across with glowing wake
    s.add(el("path", d="M260,370 L340,370 L355,360 L280,360 Z", fill="#f8fafc", stroke="#00ffff", stroke_width=1.2))
    s.add(el("rect", x=285, y=353, width=35, height=7, rx=2, fill="#00e5ff", opacity=0.9))
    # Glowing bioluminescent wake behind boat
    s.add(el("line", x1=210, y1=370, x2=260, y2=370, stroke="#00ffff", stroke_width=2.5, opacity=0.8, class_="city-anim-biolum"))

    # Localized Title Badge
    s.add(el("rect", x=20, y=20, width=len(t["night_title"]) * 7.5 + 24, height=28, rx=14, fill="#0f172a", stroke="#00ffff", stroke_width=1.2))
    s.add(el("text", t["night_title"], x=32, y=38, fill="#ffffff", font_size=12, font_weight="bold", font_family="system-ui, sans-serif"))

    return s.render(t["night_title"])


# ==============================================================================
# DISPATCH and INJECTION
# ==============================================================================
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
    sys.path.insert(0, str(Path(__file__).resolve().parent))
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
                print(f"  ! no data-city-svg=\"{key}\" container in {path.relative_to(ROOT)}")
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
