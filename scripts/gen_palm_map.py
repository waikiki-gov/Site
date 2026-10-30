#!/usr/bin/env python3
"""Generator for Palm Island infrastructure SVG map."""

import math
import sys
from pathlib import Path

try:
    from map_common import n, pt, poly_path, hotspot, map_header, L, update_island_map
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from map_common import n, pt, poly_path, hotspot, map_header, L, update_island_map


def palm_svg(t):
    cx, cy = 600, 380
    R_CRES = 315
    o = map_header(t["palm_aria"])
    o += [
        "<!-- Shallow Lagoon inside the Crescent -->",
        f'<circle cx="{cx}" cy="{cy}" r="310" fill="url(#lagoon-glow)" />',
        "<!-- Bathymetric and Navigational Grid Lines -->",
        '<g stroke="rgba(255,255,255,0.08)" stroke-width="1" stroke-dasharray="3 6" fill="none">',
        f'<circle cx="{cx}" cy="{cy}" r="200" />',
        f'<circle cx="{cx}" cy="{cy}" r="380" />',
        f'<circle cx="{cx}" cy="{cy}" r="470" />',
        '<line x1="150" y1="380" x2="1050" y2="380" />',
        "</g>",
    ]

    # Crescent Breakwater with two navigation channels
    def arc_d(deg1, deg2, r):
        a1, a2 = math.radians(deg1), math.radians(deg2)
        p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        p2 = (cx + r * math.cos(a2), cy + r * math.sin(a2))
        large_arc = 1 if abs(deg2 - deg1) > 180 else 0
        return f"M{pt(p1)} A{r},{r} 0 {large_arc} 1 {pt(p2)}"

    west_cres = arc_d(150, 264, R_CRES)
    east_cres = arc_d(276, 390, R_CRES)
    cres_all = f"{west_cres} {east_cres}"

    outer_r = R_CRES + 34
    outer_reef = arc_d(146, 394, outer_r)

    # 18 CURVED PALM LEAVES
    palm_frond_paths = []
    frond_roads = []
    frond_villas = []

    tips = [
        (360, 510),  # 0
        (350, 470),  # 1
        (340, 430),  # 2
        (330, 390),  # 3
        (340, 350),  # 4
        (350, 310),  # 5
        (360, 270),  # 6
        (370, 230),  # 7
        (400, 180),  # 8
        (480, 130),   # 9
    ]

    y_bases = [495, 460, 425, 390, 355, 320, 285, 250, 210, 180]

    w_mid_spot = (410, 350)
    e_mid_spot = (790, 350)

    for k in range(len(tips)):
        y0 = y_bases[k]
        tx_l, ty_l = tips[k]

        # Merged single control point for smooth quadratic arch
        cp_lx = (600 + tx_l) // 2 + 3
        cp_ly = (y0 + ty_l) // 2 - 68

        tx_r = 2 * cx - tx_l
        ty_r = ty_l
        cp_rx = 2 * cx - cp_lx
        cp_ry = cp_ly

        d_l = f"M600,{y0} Q{cp_lx},{cp_ly} {tx_l},{ty_l}"
        d_r = f"M600,{y0} Q{cp_rx},{cp_ry} {tx_r},{ty_r}"

        palm_frond_paths.append(d_l)
        palm_frond_paths.append(d_r)
        frond_roads.append(d_l)
        frond_roads.append(d_r)
        frond_villas.append(d_l)
        frond_villas.append(d_r)

    fronds_d = " ".join(palm_frond_paths)
    roads_d = " ".join(frond_roads)
    villas_d = " ".join(frond_villas)

    # Hotel platform at crescent apex
    hx, hy = cx, cy - R_CRES
    wx, wy = cx + 80, cy - R_CRES + 6

    # --------------------------------------------------------------------------
    # LAYER 0: WATER AND CORAL REEF
    # --------------------------------------------------------------------------
    o += [
        "<!-- Outer Coral Reef outside the Crescent Breakwater -->",
        f'<path d="{outer_reef}" fill="none" stroke="#14b8a6" stroke-width="18" stroke-linecap="round" opacity="0.22" />',
        f'<path d="{outer_reef}" fill="none" stroke="#2ba29e" stroke-width="2.5" stroke-dasharray="8 6" opacity="0.65" />',
        f'<path d="{cres_all}" fill="none" stroke="#2ba29e" stroke-width="44" stroke-linecap="round" opacity="0.45" />',
        # Inner lagoon bathymetry and coral shoals
        '<g opacity="0.32" fill="#2dd4bf">',
        '<ellipse cx="380" cy="180" rx="45" ry="18" transform="rotate(-28 380 180)" />',
        '<ellipse cx="820" cy="180" rx="45" ry="18" transform="rotate(28 820 180)" />',
        '<ellipse cx="330" cy="490" rx="52" ry="20" transform="rotate(22 330 490)" />',
        '<ellipse cx="870" cy="490" rx="52" ry="20" transform="rotate(-22 870 490)" />',
        "</g>",
    ]

    # --------------------------------------------------------------------------
    # LAYER 1: SAND (All Landmasses: Breakwater, Trunk to Barrier, Fronds, Mainland)
    # --------------------------------------------------------------------------
    o += [
        "<!-- === LAYER 1: SAND === -->",
        "<!-- Crescent Breakwater Sand -->",
        f'<path class="map-frond-edge" d="{cres_all}" stroke-width="28" />',
        f'<path class="map-frond" d="{cres_all}" stroke-width="22" />',
        "<!-- Crescent Apex Crown Platform Sand -->",
        f'<ellipse cx="{hx}" cy="{hy}" rx="58" ry="25" class="map-sand" />',
        f'<ellipse cx="{wx}" cy="{wy + 4}" rx="34" ry="15" class="map-sand" />',
        "<!-- Central Trunk Sand reaching all the way to the barrier -->",
        '<path class="map-sand" d="M570,678 L570,495 Q572,270 582,68 L618,68 Q628,270 630,495 L630,678 Z" />',
        "<!-- Gateway Marina Lobe (West) and Golden Mile Lobe (East) on Trunk -->",
        '<path class="map-sand" d="M572,580 L532,580 C514,580 506,592 506,608 L506,628 C506,642 516,648 532,648 L572,648 Z" />',
        '<path class="map-sand" d="M628,580 L668,580 C686,580 694,592 694,608 L694,628 C694,642 684,648 668,648 L628,648 Z" />',
        '<rect x="518" y="590" width="44" height="48" rx="6" class="map-sea-deep" />',
        '<g stroke="#ffffff" stroke-width="1.6">',
        '<line x1="524" y1="602" x2="556" y2="602" />',
        '<line x1="524" y1="614" x2="556" y2="614" />',
        '<line x1="524" y1="626" x2="556" y2="626" />',
        "</g>",
        "<!-- Docked Yachts in Gateway Marina and Lagoon Cruising Yachts -->",
        '<g fill="#ffffff" stroke="#0284c7" stroke-width="0.6">',
        '<rect x="528" y="598" width="7" height="2.8" rx="1.2" />',
        '<rect x="539" y="598" width="8" height="2.8" rx="1.2" />',
        '<rect x="528" y="610" width="8" height="2.8" rx="1.2" />',
        '<rect x="541" y="610" width="7" height="2.8" rx="1.2" />',
        '<rect x="530" y="622" width="9" height="2.8" rx="1.2" />',
        '<polygon points="445,565 456,568 445,571" />',
        '<polygon points="748,555 759,558 748,561" />',
        '<polygon points="420,165 431,168 420,171" />',
        "</g>",
        "<!-- 16 Palm Fronds Sand -->",
        f'<path class="map-frond-edge" d="{fronds_d}" stroke-width="21" />',
        f'<path class="map-frond" d="{fronds_d}" stroke-width="17" />',
        "<!-- Mainland Nova Aurelia Coastline Sand -->",
        '<path class="map-sand" d="M0,680 Q300,664 600,668 Q900,664 1200,680 L1200,700 L0,700 Z" />',
    ]

    # --------------------------------------------------------------------------
    # LAYER 2: GREEN (All Vegetation, Parks, and Leaf Cores)
    # --------------------------------------------------------------------------
    o += [
        "<!-- === LAYER 2: GREEN === -->",
        "<!-- Crescent Breakwater Greenery -->",
        f'<path class="map-frond-core" d="{cres_all}" stroke-width="4.5" />',
        "<!-- Crescent Apex Crown Platform Greenery -->",
        f'<ellipse cx="{hx}" cy="{hy}" rx="42" ry="16" class="map-greenery" />',
        f'<ellipse cx="{wx}" cy="{wy + 4}" rx="25" ry="10" class="map-greenery" />',
        "<!-- Central Trunk Green Park Spine reaching to the barrier -->",
        '<rect x="588" y="68" width="24" height="610" rx="8" class="map-greenery" />',
        "<!-- 16 Palm Fronds Green Core -->",
        f'<path class="map-frond-core" d="{fronds_d}" stroke-width="4.5" />',
    ]

    # --------------------------------------------------------------------------
    # LAYER 3: ROAD (All Roads, Rails, Villas, and Built Structures)
    # --------------------------------------------------------------------------
    o += [
        "<!-- === LAYER 3: ROAD === -->",
        "<!-- Palm Fronds Waterfront Villas -->",
        f'<path class="map-frond-villas" d="{villas_d}" stroke-width="2.6" stroke-dasharray="0.1 7" />',
        "<!-- Crescent Waterfront Villas -->",
        f'<path class="map-frond-villas" d="{cres_all}" stroke-width="2.6" stroke-dasharray="0.1 7" />',
        "<!-- Connected Road Network (Mainland through Trunk to Barrier and Fronds) -->",
        '<path class="map-road" d="M592,694 L592,72 M608,694 L608,72" />',
        '<path class="map-road" d="M592,72 C592,60 608,60 608,72" />',
        f'<path class="map-road" d="{roads_d}" stroke-width="2.2" />',
        "<!-- The Elevated Monorail Line along the central spine to the barrier -->",
        '<path class="map-rail" d="M600,700 L600,72" />',
    ]
    for y in (694, 610, 495, 355, 240, 72):
        o.append(f'<circle cx="600" cy="{y}" r="5" fill="#c29a57" stroke="#ffffff" stroke-width="1.8" />')

    o += [
        "<!-- Solar Canopy and Seawater Cooling Hub -->",
        '<g fill="#1f4f7a" stroke="#9fd3f5" stroke-width="0.8">',
    ]
    for r in range(3):
        for c in range(3):
            o.append(f'<rect x="{640 + c * 14}" y="{596 + r * 14}" width="11" height="11" rx="1.5" />')
    o.append("</g>")

    o += [
        "<!-- Aquaventure Waterpark Pools & Slides on East Apex Lobe -->",
        f'<g transform="translate({wx}, {wy + 3})">',
        '<ellipse cx="-6" cy="2" rx="11" ry="5" fill="#38bdf8" stroke="#bae6fd" stroke-width="0.8" />',
        '<ellipse cx="9" cy="0" rx="8" ry="4" fill="#0ea5e9" stroke="#bae6fd" stroke-width="0.8" />',
        '<path d="M-12,-4 Q-4,-10 4,-2 T14,3" fill="none" stroke="#f59e0b" stroke-width="1.6" stroke-linecap="round" />',
        '<path d="M-8,-5 Q0,-12 8,-3" fill="none" stroke="#ef4444" stroke-width="1.4" stroke-linecap="round" />',
        "</g>",
        "<!-- Crescent Apex Hotel Architecture (Hotel Khalifa Royal Twin Arch & Spire) -->",
        f'<g transform="translate({hx}, {hy})">',
        '<ellipse cx="0" cy="3" rx="28" ry="10" fill="#002244" opacity="0.75" />',
        '<path d="M-24,5 L-18,-10 L-8,-10 L-8,5 Z" fill="#d4af37" />',
        '<path d="M8,5 L8,-10 L18,-10 L24,5 Z" fill="#d4af37" />',
        '<path d="M-15,5 L0,-26 L15,5 Z" fill="#c29a57" filter="url(#glow-gold)" />',
        '<path d="M-7,5 L0,-20 L7,5 Z" fill="#ffffff" />',
        '<rect x="-6" y="-6" width="12" height="5" rx="1" fill="#0284c7" />',
        '<circle cx="0" cy="-26" r="3" fill="#e3735a" class="twinkle" />',
        "</g>",
    ]

    # Navigation beacons at the crescent tips
    p1 = (cx + R_CRES * math.cos(math.radians(150)), cy + R_CRES * math.sin(math.radians(150)))
    p2 = (cx + R_CRES * math.cos(math.radians(390)), cy + R_CRES * math.sin(math.radians(390)))
    o += [
        "<!-- Marine Navigation Beacons at the Crescent Passages -->",
        f'<circle cx="{n(p1[0])}" cy="{n(p1[1])}" r="4.5" fill="#22c55e" class="twinkle" />',
        f'<circle cx="{n(p2[0])}" cy="{n(p2[1])}" r="4.5" fill="#ef4444" class="twinkle" />',
    ]

    # Hotspots
    a4 = math.radians(205)
    spots = [
        (1, hx, hy, "#c29a57", "Hotel Khalifa"),
        (2, wx, wy, "#38bdf8", "Waterpark"),
        (3, 600, 510, "#c29a57", "Elevated Monorail Spine"),
        (4, cx + R_CRES * math.cos(a4), cy + R_CRES * math.sin(a4), "#2ba29e", "Crescent Barrier Reef"),
        (5, w_mid_spot[0], w_mid_spot[1], "#c29a57", "West Fronds Estates"),
        (6, e_mid_spot[0], e_mid_spot[1], "#c29a57", "East Fronds Villas"),
        (7, 540, 612, "#38bdf8", "Gateway Marina"),
        (8, 660, 612, "#22c55e", "Solar and Seawater Cooling Hub"),
    ]
    o.append("<!-- 8 INTERACTIVE HOTSPOT PINS -->")
    for i, x, y, col, name in spots:
        o.append(f"<!-- Hotspot {i}: {name} -->")
        o += hotspot(i, x, y, col)
    o.append("</svg>")
    return o

def main():
    update_island_map(0, palm_svg)

if __name__ == "__main__":
    main()
