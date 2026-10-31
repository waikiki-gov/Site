#!/usr/bin/env python3
"""
Generate museum-grade realistic SVG illustrations for space-research.html.
Generates:
1. icons/space/station-en.svg & station-hu.svg (1160x520) - WNSS Orbital Complex
2. icons/space/corridor-en.svg & corridor-hu.svg (1160x480) - Earth-Moon-Mars Interplanetary Corridor
Links standalone SVGs into en/space-research.html and hu/space-research.html via <img> tags.
"""

from __future__ import annotations

import math
import random
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import svg_textures

OUT_DIR = ROOT / "icons" / "space"


def n(val):
    if isinstance(val, (int,)):
        return str(val)
    return f"{val:.1f}".rstrip("0").rstrip(".")


def el(tag, **attrs):
    kvs = []
    for k, v in attrs.items():
        if v is None:
            continue
        attr_name = k.rstrip("_").replace("_", "-")
        kvs.append(f'{attr_name}="{v}"')
    attr_str = " " + " ".join(kvs) if kvs else ""
    return f"<{tag}{attr_str} />"


def g(children, **attrs):
    kvs = []
    for k, v in attrs.items():
        if v is None:
            continue
        attr_name = k.rstrip("_").replace("_", "-")
        kvs.append(f'{attr_name}="{v}"')
    attr_str = " " + " ".join(kvs) if kvs else ""
    inner = "\n".join(children) if isinstance(children, list) else str(children)
    return f"<g{attr_str}>\n{inner}\n</g>"


@lru_cache(maxsize=1)
def get_earth_limb_uri() -> str:
    return svg_textures.render_earth_limb(580, 250, 950, seed=42)


@lru_cache(maxsize=1)
def get_planets_uris() -> tuple[str, str, str]:
    earth = svg_textures.render_planet("earth", 130, seed=42, halo=0.18)
    moon = svg_textures.render_planet("moon", 76, seed=7, halo=0.0)
    mars = svg_textures.render_planet("mars", 124, seed=19, halo=0.12)
    return earth, moon, mars


# ==============================================================================
# 1. WNSS ORBITAL COMPLEX SVG (1160 x 520)
# ==============================================================================
def build_station_svg(lang="en") -> str:
    clip_id = "sr-clip1" if lang == "en" else "sr-hu-clip1"

    # Localized text labels
    if lang == "hu":
        aria_label = "Waikiki Nemzeti Űrállomás pályamenti felépítése és telemetriai ábrája"
        hud_alt = "MAGASSÁG: 420.4 KM"
        hud_vel = "SEBESSÉG: 7.66 KM/S"
        hud_crew = "12 FŐ AKTÍV"
        hud_badge_l1 = "WSA ŰRÁLLOMÁS LOGISZTIKA"
        hud_badge_l2 = "NAPELEMES TELJESÍTMÉNY: 140 KW"
        hud_badge_r1 = "DOKKOLÓKAPUK: 6 AKTÍV"
        hud_badge_r2 = "AUTOMATIKUS KÖZELÍTÉSRE KÉSZ"
    else:
        aria_label = "Waikiki National Space Station Orbital Complex and Telemetry Diagram"
        hud_alt = "ALT: 420.4 KM"
        hud_vel = "VEL: 7.66 KM/S"
        hud_crew = "CREW: 12 NOMINAL"
        hud_badge_l1 = "WSA ORBITAL LOGISTICS"
        hud_badge_l2 = "SOLAR OUTPUT: 140 KW"
        hud_badge_r1 = "DOCKING PORTS: 6 ACTIVE"
        hud_badge_r2 = "RENDEZVOUS APPROACH READY"

    rng = random.Random(42)
    earth_limb_uri = get_earth_limb_uri()

    defs = f"""    <defs>
        <clipPath id="{clip_id}">
            <rect width="1160" height="520" />
        </clipPath>
        <style>
            @keyframes pulse-glow {{ 0%, 100% {{ opacity: 0.85; filter: drop-shadow(0 0 2px rgba(245, 196, 110, 0.4)); }} 50% {{ opacity: 1; filter: drop-shadow(0 0 10px rgba(245, 196, 110, 0.9)); }} }}
            @keyframes twinkle {{ 0%, 100% {{ opacity: 0.25; }} 50% {{ opacity: 1; }} }}
            @keyframes dash {{ to {{ stroke-dashoffset: -40; }} }}
            .twinkle {{ animation: twinkle 3.2s ease-in-out infinite; }}
            .twinkle:nth-of-type(2n) {{ animation-duration: 4.5s; animation-delay: 0.8s; }}
            .twinkle:nth-of-type(3n) {{ animation-duration: 2.8s; animation-delay: 1.5s; }}
            .pulse-glow {{ animation: pulse-glow 4s ease-in-out infinite; }}
            .dash {{ animation: dash 2.5s linear infinite; }}
            text {{ font-family: "Manrope", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        </style>
        <radialGradient id="sr-space-bg" cx="50%" cy="25%" r="75%">
            <stop offset="0%" stop-color="#0a1d2e" />
            <stop offset="35%" stop-color="#05101a" />
            <stop offset="70%" stop-color="#02080e" />
            <stop offset="100%" stop-color="#010408" />
        </radialGradient>
        <radialGradient id="sr-nebula-teal" cx="35%" cy="20%" r="55%">
            <stop offset="0%" stop-color="#145258" stop-opacity="0.32" />
            <stop offset="50%" stop-color="#0c3238" stop-opacity="0.15" />
            <stop offset="100%" stop-color="#02080e" stop-opacity="0" />
        </radialGradient>
        <radialGradient id="sr-nebula-blue" cx="75%" cy="30%" r="50%">
            <stop offset="0%" stop-color="#183e68" stop-opacity="0.28" />
            <stop offset="60%" stop-color="#0d2440" stop-opacity="0.12" />
            <stop offset="100%" stop-color="#02080e" stop-opacity="0" />
        </radialGradient>
        <linearGradient id="sr-solar-wafer" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#1e3b6e" />
            <stop offset="30%" stop-color="#13264b" />
            <stop offset="70%" stop-color="#0b1730" />
            <stop offset="100%" stop-color="#040c1c" />
        </linearGradient>
        <linearGradient id="sr-solar-gold" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffd57a" />
            <stop offset="35%" stop-color="#dfa438" />
            <stop offset="70%" stop-color="#b27a20" />
            <stop offset="100%" stop-color="#6e460e" />
        </linearGradient>
        <linearGradient id="sr-radiator" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" />
            <stop offset="45%" stop-color="#d4e6e6" />
            <stop offset="85%" stop-color="#9eb6b6" />
            <stop offset="100%" stop-color="#789292" />
        </linearGradient>
        <linearGradient id="sr-hull-cyl" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" />
            <stop offset="35%" stop-color="#e2eff2" />
            <stop offset="75%" stop-color="#a4c2c8" />
            <stop offset="100%" stop-color="#5a7a82" />
        </linearGradient>
        <linearGradient id="sr-hull-shadow" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#688a94" />
            <stop offset="100%" stop-color="#18262a" />
        </linearGradient>
        <filter id="sr-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>"""

    body = []
    # 1. Deep Space Canvas
    body.append('<rect width="1160" height="520" fill="url(#sr-space-bg)" />')
    body.append('<ellipse cx="340" cy="120" rx="360" ry="100" fill="url(#sr-nebula-teal)" />')
    body.append('<ellipse cx="880" cy="140" rx="320" ry="110" fill="url(#sr-nebula-blue)" />')
    body.append('<ellipse cx="580" cy="70" rx="260" ry="60" fill="#6BA4D9" opacity="0.08" />')

    # 2. Multi-magnitude Realistic Starfield with Twinkle
    stars = []
    bright_stars = [
        (45, 42, 1.6, "#ffffff"), (115, 110, 1.3, "#aed8f2"), (185, 55, 1.8, "#ffe8b8"),
        (275, 92, 1.2, "#ffffff"), (365, 38, 1.6, "#b8e2f8"), (455, 78, 1.4, "#ffffff"),
        (545, 32, 2.0, "#ffe0a0"), (635, 82, 1.3, "#ffffff"), (725, 36, 1.7, "#a8d8f8"),
        (815, 88, 1.2, "#ffffff"), (905, 45, 1.9, "#ffffff"), (995, 72, 1.4, "#ffdca0"),
        (1085, 40, 1.8, "#ffffff"), (75, 175, 1.3, "#aed8f2"), (235, 155, 1.5, "#ffffff"),
        (945, 165, 1.4, "#ffffff"), (1055, 185, 1.3, "#ffe2b0"), (1125, 120, 1.5, "#ffffff")
    ]
    for sx, sy, sr, scol in bright_stars:
        stars.append(f'<circle class="twinkle" cx="{sx}" cy="{sy}" r="{sr}" fill="{scol}" />')
    faint_stars = []
    for _ in range(95):
        fx = rng.uniform(10, 1150)
        fy = rng.uniform(10, 260)
        fr = rng.uniform(0.6, 1.0)
        faint_stars.append(f'<circle cx="{n(fx)}" cy="{n(fy)}" r="{n(fr)}" />')
    body.append('<g fill="#ffffff" opacity="0.65">\n' + "\n".join(faint_stars) + "\n</g>")
    body.append('<g>\n' + "\n".join(stars) + "\n</g>")

    # 3. Realistic Photorealistic Earth Curvature Below
    body.append('<!-- Photorealistic Earth Limb from LEO Orbit -->')
    body.append(f'<image href="{earth_limb_uri}" x="0" y="270" width="1160" height="250" preserveAspectRatio="none" opacity="0.96" />')
    # Atmospheric Limb Scattering Overlay
    body.append('<path d="M-80,560 C250,395 910,395 1240,560" fill="none" stroke="#003366" stroke-width="26" opacity="0.4" />')
    body.append('<path d="M-80,560 C250,395 910,395 1240,560" fill="none" stroke="#1d8cf8" stroke-width="14" opacity="0.35" />')
    body.append('<path d="M-80,560 C250,395 910,395 1240,560" fill="none" stroke="#62d6ff" stroke-width="7" opacity="0.6" />')
    body.append('<path d="M-80,560 C250,395 910,395 1240,560" fill="none" stroke="#dcf8ff" stroke-width="2" opacity="0.9" />')

    # Sparkling City Night Lights on the shadowed limb (right side)
    city_lights = [
        (720, 482, 1.4), (755, 488, 1.8), (790, 478, 1.6), (840, 474, 2.0),
        (875, 468, 1.8), (910, 462, 1.5), (945, 472, 1.7), (990, 465, 1.9),
        (1030, 472, 1.5), (1070, 480, 1.8), (815, 492, 1.3), (860, 484, 1.4)
    ]
    city_els = [f'<circle cx="{cx_}" cy="{cy_}" r="{cr_}" />' for cx_, cy_, cr_ in city_lights]
    body.append('<g fill="#ffcf70" opacity="0.85" filter="url(#sr-glow)">\n' + "\n".join(city_els) + "\n</g>")

    # 4. Docking Approach Flight Corridor (Smooth orbital overflight clearing the station)
    dock_path_id = "sr-docking-path" if lang == "en" else "sr-hu-docking-path"
    body.append(f'<path id="{dock_path_id}" d="M-40,110 C320,65 840,65 1200,110" fill="none" stroke="#f5c46e" stroke-width="1.8" stroke-dasharray="6 8" opacity="0.65" class="dash" />')

    # Approaching Autonomous Spacecraft
    craft = f"""<!-- Approaching Autonomous Spacecraft -->
    <g>
        <path d="M-14,-5 L6,-5 L14,0 L6,5 L-14,5 L-10,0Z" fill="#ffffff" stroke="#003366" stroke-width="1.2" />
        <polygon points="-14,-5 -19,-10 -9,-5" fill="#c95a41" />
        <polygon points="-14,5 -19,10 -9,5" fill="#c95a41" />
        <rect x="-8" y="-3" width="8" height="6" rx="1.5" fill="#1a528f" />
        <circle cx="9" cy="0" r="2.2" fill="#6BA4D9" />
        <animateMotion dur="20s" repeatCount="indefinite" rotate="auto">
            <mpath href="#{dock_path_id}" />
        </animateMotion>
    </g>"""
    body.append(craft)

    # 5. WNSS STATION COMPLEX STRUCTURE
    body.append('<!-- Integrated Truss System (ITS) -->')
    body.append('<rect x="250" y="226" width="660" height="12" rx="2" fill="#2d424b" stroke="#6BA4D9" stroke-width="1.2" />')
    body.append('<line x1="250" y1="232" x2="910" y2="232" stroke="#d5ede9" stroke-width="2" stroke-dasharray="8 6" opacity="0.85" />')
    truss_braces = []
    for tx in range(260, 900, 24):
        truss_braces.append(f"M{tx},226 L{tx + 12},238 M{tx + 12},226 L{tx},238")
    body.append(f'<path d="{" ".join(truss_braces)}" stroke="#466570" stroke-width="1.0" opacity="0.75" />')

    # Port & Starboard Thermal Control Radiators
    body.append("""<!-- Port Thermal Radiators -->
    <g transform="translate(365, 172)">
        <rect x="0" y="0" width="56" height="42" rx="2" fill="url(#sr-radiator)" stroke="#527882" stroke-width="1.0" />
        <line x1="14" y1="0" x2="14" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="28" y1="0" x2="28" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="42" y1="0" x2="42" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="28" y1="42" x2="28" y2="54" stroke="#8faeb6" stroke-width="2.5" />
    </g>""")
    body.append("""<!-- Starboard Thermal Radiators -->
    <g transform="translate(738, 250)">
        <rect x="0" y="0" width="56" height="42" rx="2" fill="url(#sr-radiator)" stroke="#527882" stroke-width="1.0" />
        <line x1="14" y1="0" x2="14" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="28" y1="0" x2="28" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="42" y1="0" x2="42" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="28" y1="-12" x2="28" y2="0" stroke="#8faeb6" stroke-width="2.5" />
    </g>""")

    # Solar Array Wings
    def solar_wing(x, y, w, h):
        items = [
            f'<rect x="0" y="0" width="{w}" height="{h}" rx="2" fill="url(#sr-solar-wafer)" stroke="#8c6218" stroke-width="1.4" />',
            f'<rect x="0" y="0" width="{w}" height="{h}" rx="2" fill="url(#sr-solar-gold)" opacity="0.38" />',
        ]
        for gx in (w * 0.25, w * 0.5, w * 0.75):
            items.append(f'<line x1="{n(gx)}" y1="0" x2="{n(gx)}" y2="{h}" stroke="#ffcc66" stroke-width="0.7" opacity="0.65" />')
        for gy in range(8, int(h), 12):
            items.append(f'<line x1="0" y1="{gy}" x2="{w}" y2="{gy}" stroke="#ffcc66" stroke-width="0.6" opacity="0.45" />')
        items.append(f'<line x1="{w / 2}" y1="0" x2="{w / 2}" y2="{h}" stroke="#ffffff" stroke-width="1.2" opacity="0.8" />')
        return g(items, transform=f"translate({x}, {y})", class_="pulse-glow")

    body.append('<!-- Port Solar Array Wings (Left) -->')
    body.append(solar_wing(150, 136, 80, 84))
    body.append(solar_wing(150, 244, 80, 84))
    body.append('<rect x="228" y="228" width="24" height="8" rx="1" fill="#cbe0dc" stroke="#486872" stroke-width="1" />')
    body.append('<circle cx="240" cy="232" r="5" fill="#f5c46e" />')

    body.append('<!-- Starboard Solar Array Wings (Right) -->')
    body.append(solar_wing(930, 136, 80, 84))
    body.append(solar_wing(930, 244, 80, 84))
    body.append('<rect x="908" y="228" width="24" height="8" rx="1" fill="#cbe0dc" stroke="#486872" stroke-width="1" />')
    body.append('<circle cx="920" cy="232" r="5" fill="#f5c46e" />')

    # Central Rotating Torus Ring (Rock-solid exact rotation around its local center 0, 0)
    ring_svg = """<!-- Central Artificial-Gravity Rotating Torus Ring -->
    <g transform="translate(580, 232)">
        <g>
            <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="-360 0 0" dur="32s" repeatCount="indefinite" />
            <circle cx="0" cy="0" r="92" fill="none" stroke="#16383c" stroke-width="22" opacity="0.5" />
            <circle cx="0" cy="0" r="92" fill="none" stroke="#dff0ec" stroke-width="16" />
            <circle cx="0" cy="0" r="100.5" fill="none" stroke="#f5c46e" stroke-width="1.5" />
            <circle cx="0" cy="0" r="83.5" fill="none" stroke="#6BA4D9" stroke-width="1.5" />
            <circle cx="0" cy="0" r="92" fill="none" stroke="#003366" stroke-width="16" stroke-dasharray="2 18" opacity="0.6" />
            <circle cx="0" cy="0" r="92" fill="none" stroke="#42d0f5" stroke-width="3" stroke-dasharray="10 10" opacity="0.85" />
            <line x1="0" y1="-92" x2="0" y2="92" stroke="#b4d6d0" stroke-width="3.5" />
            <line x1="-92" y1="0" x2="92" y2="0" stroke="#b4d6d0" stroke-width="3.5" />
            <line x1="-65" y1="-65" x2="65" y2="65" stroke="#90b8b2" stroke-width="2.5" />
            <line x1="-65" y1="65" x2="65" y2="-65" stroke="#90b8b2" stroke-width="2.5" />
            <rect x="-5" y="-97" width="10" height="10" rx="2" fill="#ffffff" stroke="#003366" stroke-width="1.5" />
            <rect x="-5" y="87" width="10" height="10" rx="2" fill="#ffffff" stroke="#003366" stroke-width="1.5" />
            <rect x="-97" y="-5" width="10" height="10" rx="2" fill="#ffffff" stroke="#003366" stroke-width="1.5" />
            <rect x="87" y="-5" width="10" height="10" rx="2" fill="#ffffff" stroke="#003366" stroke-width="1.5" />
            <circle cx="0" cy="-92" r="2.5" fill="#2ecc71" />
            <circle cx="0" cy="92" r="2.5" fill="#2ecc71" />
        </g>
        <circle cx="0" cy="0" r="26" fill="url(#sr-hull-cyl)" stroke="#003366" stroke-width="2" />
        <circle cx="0" cy="0" r="14" fill="#04121a" stroke="#f5c46e" stroke-width="1.5" />
        <circle cx="0" cy="0" r="6" fill="#42d0f5" />
    </g>"""
    body.append(ring_svg)

    # Pressurized Modules & Cupola
    body.append("""<!-- Primary Science and Habitation Spine -->
    <g transform="translate(415, 216)">
        <rect x="0" y="0" width="100" height="32" rx="6" fill="url(#sr-hull-cyl)" stroke="#003366" stroke-width="1.6" />
        <line x1="25" y1="0" x2="25" y2="32" stroke="#003366" stroke-width="1.2" />
        <line x1="50" y1="0" x2="50" y2="32" stroke="#003366" stroke-width="1.2" />
        <line x1="75" y1="0" x2="75" y2="32" stroke="#003366" stroke-width="1.2" />
        <rect x="12" y="8" width="76" height="4" fill="#ffd54f" opacity="0.65" />
        <rect x="12" y="20" width="76" height="4" fill="#ffd54f" opacity="0.65" />
        <!-- Nadir Multi-pane Sapphire Glass Observation Cupola -->
        <path d="M25,32 L35,46 L65,46 L75,32Z" fill="#1565c0" stroke="#003366" stroke-width="1.4" />
        <polygon points="38,44 62,44 58,34 42,34" fill="#64b5f6" opacity="0.9" />
        <circle cx="37" cy="16" r="3.2" fill="#42d0f5" stroke="#003366" stroke-width="0.8" />
        <circle cx="63" cy="16" r="3.2" fill="#42d0f5" stroke="#003366" stroke-width="0.8" />
    </g>""")

    # Starboard Habitation & Engineering Stack
    body.append("""<!-- Starboard Habitation and Engineering Stack -->
    <g transform="translate(640, 216)">
        <rect x="0" y="0" width="100" height="32" rx="6" fill="url(#sr-hull-cyl)" stroke="#003366" stroke-width="1.6" />
        <line x1="25" y1="0" x2="25" y2="32" stroke="#003366" stroke-width="1.2" />
        <line x1="50" y1="0" x2="50" y2="32" stroke="#003366" stroke-width="1.2" />
        <line x1="75" y1="0" x2="75" y2="32" stroke="#003366" stroke-width="1.2" />
        <line x1="8" y1="5" x2="92" y2="5" stroke="#f5c46e" stroke-width="1.0" />
        <line x1="8" y1="27" x2="92" y2="27" stroke="#f5c46e" stroke-width="1.0" />
        <rect x="70" y="32" width="26" height="12" fill="#607d8b" stroke="#003366" stroke-width="1.0" />
        <rect x="74" y="34" width="7" height="8" fill="#ffd54f" />
        <rect x="85" y="34" width="7" height="8" fill="#81d4fa" />
    </g>""")

    # Robotic Manipulator Arm (Canadarm)
    body.append("""<!-- Articulated Robotic Manipulator Arm (Canadarm3) -->
    <g transform="translate(485, 216)">
        <rect x="-8" y="-7" width="16" height="7" rx="1.5" fill="#78909c" stroke="#37474f" stroke-width="0.9" />
        <path d="M0,-7 L-18,-28 L-42,-18 L-65,-36" fill="none" stroke="#cfd8dc" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />
        <path d="M0,-7 L-18,-28 L-42,-18 L-65,-36" fill="none" stroke="#263238" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" />
        <circle cx="0" cy="-7" r="3.5" fill="#f5c46e" stroke="#37474f" stroke-width="0.8" />
        <circle cx="-18" cy="-28" r="3.2" fill="#f5c46e" stroke="#37474f" stroke-width="0.8" />
        <circle cx="-42" cy="-18" r="3.2" fill="#f5c46e" stroke="#37474f" stroke-width="0.8" />
        <circle cx="-65" cy="-36" r="3.8" fill="#ffffff" stroke="#c95a41" stroke-width="1.2" />
        <line x1="-65" y1="-36" x2="-72" y2="-42" stroke="#42d0f5" stroke-width="1.2" />
    </g>""")

    # Docked Vehicles
    body.append("""<!-- Docked Crew Transport Spaceplane -->
    <g transform="translate(378, 232)">
        <rect x="30" y="-7" width="12" height="14" rx="2" fill="#90a4ae" stroke="#37474f" stroke-width="1.0" />
        <path d="M-4,-12 L30,-5 L30,5 L-4,12 L-10,0Z" fill="#ffffff" stroke="#003366" stroke-width="1.4" />
        <path d="M-4,0 L30,2 L30,5 L-4,12 L-10,0Z" fill="#212121" opacity="0.65" />
        <polygon points="10,-5 30,-22 30,-5" fill="#c95a41" />
        <polygon points="10,5 30,22 30,5" fill="#c95a41" />
        <ellipse cx="6" cy="0" rx="4.5" ry="2.2" fill="#42d0f5" />
    </g>""")

    body.append("""<!-- Docked Autonomous Cargo Capsule -->
    <g transform="translate(690, 248)">
        <rect x="-6" y="0" width="12" height="8" fill="#90a4ae" stroke="#37474f" stroke-width="0.9" />
        <path d="M-12,8 L12,8 L16,28 L-16,28Z" fill="#ffffff" stroke="#003366" stroke-width="1.3" />
        <line x1="-12" y1="18" x2="12" y2="18" stroke="#003366" stroke-width="1.0" />
        <rect x="-32" y="16" width="16" height="10" fill="#1a3b68" stroke="#ffc107" stroke-width="0.8" />
        <rect x="16" y="16" width="16" height="10" fill="#1a3b68" stroke="#ffc107" stroke-width="0.8" />
    </g>""")

    # Telemetry Dish (expanding radio ripples without position shift)
    body.append("""<!-- High-Gain Deep Space Telemetry Antenna -->
    <g transform="translate(580, 105)">
        <line x1="0" y1="40" x2="0" y2="14" stroke="#b0bec5" stroke-width="2.5" />
        <path d="M-22,8 C-12,-8 12,-8 22,8" fill="none" stroke="#f5c46e" stroke-width="3.2" stroke-linecap="round" />
        <line x1="0" y1="14" x2="0" y2="-4" stroke="#ffffff" stroke-width="1.8" />
        <circle cx="0" cy="-4" r="2.5" fill="#f5c46e" />
        <circle cx="0" cy="-6" r="8" fill="none" stroke="#6BA4D9" stroke-width="1.8">
            <animate attributeName="r" values="6;26" dur="2.4s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.9;0" dur="2.4s" repeatCount="indefinite" />
        </circle>
        <circle cx="0" cy="-6" r="8" fill="none" stroke="#6BA4D9" stroke-width="1.8">
            <animate attributeName="r" values="6;26" dur="2.4s" begin="1.2s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.9;0" dur="2.4s" begin="1.2s" repeatCount="indefinite" />
        </circle>
    </g>""")

    # HUD Telemetry Overlays
    hud_bar = f"""<!-- TOP HUD TELEMETRY BAR -->
    <g font-family="Manrope, sans-serif" font-size="11" font-weight="700" letter-spacing="1.5">
        <rect x="330" y="18" width="500" height="32" rx="16" fill="#04121a" stroke="#6BA4D9" stroke-width="1.2" opacity="0.95" />
        <text x="355" y="38" fill="#6BA4D9">{hud_alt}</text>
        <text x="520" y="38" fill="#f5c46e">{hud_vel}</text>
        <text x="680" y="38" fill="#2ecc71">{hud_crew}</text>
    </g>"""
    body.append(hud_bar)

    badges = f"""<!-- Bottom-left corner telemetry badge -->
    <g font-family="Manrope, sans-serif" font-size="10" font-weight="600" letter-spacing="1">
        <rect x="30" y="445" width="245" height="50" rx="8" fill="#04121a" stroke="rgba(107, 164, 217, 0.45)" stroke-width="1" opacity="0.95" />
        <text x="44" y="468" fill="#f5c46e">{hud_badge_l1}</text>
        <text x="44" y="484" fill="#bedbd6">{hud_badge_l2}</text>
    </g>
    <!-- Bottom-right corner telemetry badge -->
    <g font-family="Manrope, sans-serif" font-size="10" font-weight="600" letter-spacing="1" text-anchor="end">
        <rect x="885" y="445" width="245" height="50" rx="8" fill="#04121a" stroke="rgba(107, 164, 217, 0.45)" stroke-width="1" opacity="0.95" />
        <text x="1116" y="468" fill="#6BA4D9">{hud_badge_r1}</text>
        <text x="1116" y="484" fill="#bedbd6">{hud_badge_r2}</text>
    </g>"""
    body.append(badges)

    inner_content = "\n".join(body)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 1160 520" role="img" aria-label="{aria_label}">
{defs}
    <g clip-path="url(#{clip_id})">
{inner_content}
    </g>
</svg>"""


# ==============================================================================
# 2. EARTH-MOON-MARS INTERPLANETARY CORRIDOR SVG (1160 x 480)
# ==============================================================================
def build_lunar_mars_svg(lang="en") -> str:
    clip_id = "sr-clip2" if lang == "en" else "sr-hu-clip2"

    if lang == "hu":
        aria_label = "Föld, Hold és Mars bolygóközi transzferfolyosó térkép"
        hud_header = "HOLD-BÁZIS ÉS MARS KÖZI TRANSZFERFOLYOSÓ"
        lbl_earth_title = "FÖLD"
        lbl_earth_sub = "BÁZISÁLLOMÁS"
        lbl_moon_title = "HOLD PROGRAM"
        lbl_moon_sub = "2026-2030"
        lbl_mars_title = "MARS EXPEDÍCIÓ"
        lbl_mars_sub = "2035-2040"
    else:
        aria_label = "Earth Moon and Mars Interplanetary Transfer Corridor Map"
        hud_header = "MOON BASE AND MARS INTERPLANETARY CORRIDOR"
        lbl_earth_title = "EARTH"
        lbl_earth_sub = "PRIMARY BASE"
        lbl_moon_title = "LUNAR MISSION"
        lbl_moon_sub = "2026-2030"
        lbl_mars_title = "MARS EXPEDITION"
        lbl_mars_sub = "2035-2040"

    rng = random.Random(108)
    earth_uri, moon_uri, mars_uri = get_planets_uris()

    defs = f"""    <defs>
        <clipPath id="{clip_id}">
            <rect width="1160" height="480" />
        </clipPath>
        <style>
            @keyframes twinkle {{ 0%, 100% {{ opacity: 0.25; }} 50% {{ opacity: 1; }} }}
            @keyframes dash {{ to {{ stroke-dashoffset: -40; }} }}
            .twinkle {{ animation: twinkle 3.2s ease-in-out infinite; }}
            .twinkle:nth-of-type(2n) {{ animation-duration: 4.5s; animation-delay: 0.8s; }}
            .twinkle:nth-of-type(3n) {{ animation-duration: 2.8s; animation-delay: 1.5s; }}
            .dash {{ animation: dash 2.5s linear infinite; }}
            text {{ font-family: "Manrope", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        </style>
        <radialGradient id="sr-deep-space" cx="50%" cy="40%" r="65%">
            <stop offset="0%" stop-color="#0a1d28" />
            <stop offset="45%" stop-color="#051018" />
            <stop offset="85%" stop-color="#02080e" />
            <stop offset="100%" stop-color="#010408" />
        </radialGradient>
        <filter id="sr-planet-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>"""

    body = []
    # 1. Deep Space Field
    body.append('<rect width="1160" height="480" fill="url(#sr-deep-space)" />')

    # Faint Interplanetary Astrodynamics Grid
    grid_lines = []
    for y_g in (120, 240, 360):
        grid_lines.append(f'<line x1="40" y1="{y_g}" x2="1120" y2="{y_g}" stroke="#1e405a" stroke-width="0.8" stroke-dasharray="4 8" opacity="0.35" />')
    for x_g in (180, 540, 960):
        grid_lines.append(f'<line x1="{x_g}" y1="40" x2="{x_g}" y2="440" stroke="#1e405a" stroke-width="0.8" stroke-dasharray="4 8" opacity="0.35" />')
    body.append('<g>\n' + "\n".join(grid_lines) + "\n</g>")

    # Starfield
    stars = []
    bright_stars = [
        (80, 70, 1.4), (220, 110, 1.6), (380, 50, 1.3), (490, 90, 1.7),
        (620, 60, 1.2), (740, 120, 1.5), (860, 70, 1.8), (1020, 110, 1.4),
        (1110, 50, 1.6), (140, 410, 1.5), (320, 380, 1.3), (680, 420, 1.6),
        (820, 390, 1.4), (1080, 420, 1.7)
    ]
    for sx, sy, sr in bright_stars:
        stars.append(f'<circle class="twinkle" cx="{sx}" cy="{sy}" r="{sr}" fill="#ffffff" />')
    faint_stars = []
    for _ in range(80):
        fx = rng.uniform(20, 1140)
        fy = rng.uniform(20, 460)
        fr = rng.uniform(0.6, 1.0)
        faint_stars.append(f'<circle cx="{n(fx)}" cy="{n(fy)}" r="{n(fr)}" />')
    body.append('<g fill="#ffffff" opacity="0.6">\n' + "\n".join(faint_stars) + "\n</g>")
    body.append('<g>\n' + "\n".join(stars) + "\n</g>")

    # 2. Interplanetary Transfer Trajectory Paths (Smooth continuous closed cyclic loops)
    path_moon_id = "sr-path-moon" if lang == "en" else "sr-hu-path-moon"
    path_mars_id = "sr-path-mars" if lang == "en" else "sr-hu-path-mars"

    # Gravitational Well Contours
    body.append('<ellipse cx="180" cy="240" rx="90" ry="80" fill="none" stroke="#2563eb" stroke-width="0.8" stroke-dasharray="2 6" opacity="0.35" />')
    body.append('<ellipse cx="540" cy="190" rx="60" ry="52" fill="none" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="2 6" opacity="0.35" />')
    body.append('<ellipse cx="960" cy="240" rx="85" ry="75" fill="none" stroke="#ea580c" stroke-width="0.8" stroke-dasharray="2 6" opacity="0.35" />')

    # Earth-Moon Cislunar Corridor Loop (Starts outside Earth LEO at 245, 215, curves to Moon L1/Gateway at 495, 175, and returns)
    body.append(f'<path id="{path_moon_id}" d="M245,215 C330,135 440,135 495,175 C440,205 330,225 245,215" fill="none" stroke="#f5c46e" stroke-width="2.2" stroke-dasharray="6 6" class="dash" />')
    body.append(f'<path d="M245,215 C330,135 440,135 495,175 C440,205 330,225 245,215" fill="none" stroke="#f5c46e" stroke-width="8" opacity="0.2" filter="url(#sr-planet-glow)" />')

    # Earth-Mars Interplanetary Corridor Loop (Starts outside Earth LEO at 245, 265, Hohmann transfer arc to Mars at 895, 265, and returns)
    body.append(f'<path id="{path_mars_id}" d="M245,265 C380,405 760,405 895,265 C760,340 380,340 245,265" fill="none" stroke="#e3735a" stroke-width="2.5" stroke-dasharray="8 8" class="dash" />')
    body.append(f'<path d="M245,265 C380,405 760,405 895,265 C760,340 380,340 245,265" fill="none" stroke="#e3735a" stroke-width="10" opacity="0.2" filter="url(#sr-planet-glow)" />')

    # Delta-v Burn Vectors & Lagrange Point Markers (pulse in place without position drift)
    burn_points = [
        (295, 162, "TLI Δv: 3.1 km/s", "#f5c46e"),
        (370, 375, "TMI Δv: 3.8 km/s", "#e3735a"),
        (770, 375, "MOI Δv: 2.1 km/s", "#e3735a"),
        (470, 185, "L1 GATEWAY", "#6BA4D9"),
    ]
    for bx, by, btxt, bcol in burn_points:
        body.append(f"""<g transform="translate({bx}, {by})">
            <circle cx="0" cy="0" r="4" fill="{bcol}" />
            <circle cx="0" cy="0" r="7" fill="none" stroke="{bcol}" stroke-width="1.2">
                <animate attributeName="r" values="5;11;5" dur="3s" repeatCount="indefinite" />
                <animate attributeName="opacity" values="0.9;0.25;0.9" dur="3s" repeatCount="indefinite" />
            </circle>
            <text x="0" y="-12" fill="{bcol}" font-family="Manrope, sans-serif" font-size="9" font-weight="700" text-anchor="middle" letter-spacing="1">{btxt}</text>
        </g>""")

    # 3. PLANET EARTH NODE (x=180, y=240, r=65) - Orbit ring & satellite rotate rock-solid around planet center (0, 0)
    earth_group = f"""<!-- 3D Photorealistic Earth Node -->
    <g transform="translate(180, 240)">
        <g>
            <circle cx="0" cy="0" r="76" fill="none" stroke="#6BA4D9" stroke-width="1.2" stroke-dasharray="6 6" opacity="0.8" />
            <circle cx="0" cy="-76" r="3.5" fill="#2ecc71" />
            <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="24s" repeatCount="indefinite" />
        </g>
        <image href="{earth_uri}" x="-65" y="-65" width="130" height="130" preserveAspectRatio="none" />
        <text x="0" y="88" fill="#fbf7f0" font-family="Manrope, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1.5">{lbl_earth_title}</text>
        <text x="0" y="105" fill="#6BA4D9" font-family="Manrope, sans-serif" font-size="10" font-weight="600" text-anchor="middle">{lbl_earth_sub}</text>
    </g>"""
    body.append(earth_group)

    # 4. MOON NODE & LUNAR BASE (x=540, y=190, r=38) - Orbit ring & base rotate rock-solid around Moon center (0, 0)
    moon_group = f"""<!-- 3D Photorealistic Moon Node -->
    <g transform="translate(540, 190)">
        <g>
            <circle cx="0" cy="0" r="48" fill="none" stroke="#f5c46e" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.8" />
            <circle cx="0" cy="-48" r="3" fill="#ffd54f" />
            <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="16s" repeatCount="indefinite" />
        </g>
        <image href="{moon_uri}" x="-38" y="-38" width="76" height="76" preserveAspectRatio="none" />
        <text x="0" y="62" fill="#fbf7f0" font-family="Manrope, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1.5">{lbl_moon_title}</text>
        <text x="0" y="79" fill="#f5c46e" font-family="Manrope, sans-serif" font-size="10" font-weight="600" text-anchor="middle">{lbl_moon_sub}</text>
    </g>"""
    body.append(moon_group)

    # 5. MARS NODE & EXPEDITION CORRIDOR (x=960, y=240, r=62) - Orbit ring & base rotate rock-solid around Mars center (0, 0)
    mars_group = f"""<!-- 3D Photorealistic Mars Node -->
    <g transform="translate(960, 240)">
        <g>
            <circle cx="0" cy="0" r="74" fill="none" stroke="#e3735a" stroke-width="1.2" stroke-dasharray="6 6" opacity="0.8" />
            <circle cx="0" cy="-74" r="3.5" fill="#ff7043" />
            <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="28s" repeatCount="indefinite" />
        </g>
        <image href="{mars_uri}" x="-62" y="-62" width="124" height="124" preserveAspectRatio="none" />
        <polygon points="-8,-12 0,-24 8,-12" fill="#f5c46e" />
        <circle cx="0" cy="-14" r="2" fill="#003366" />
        <text x="0" y="88" fill="#fbf7f0" font-family="Manrope, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1.5">{lbl_mars_title}</text>
        <text x="0" y="105" fill="#e3735a" font-family="Manrope, sans-serif" font-size="10" font-weight="600" text-anchor="middle">{lbl_mars_sub}</text>
    </g>"""
    body.append(mars_group)

    # 6. Interplanetary Ships in Transit (Cruising along cyclic loops outside planets)
    mars_ship = f"""<!-- Interplanetary Starship (Mars Cycler) -->
    <g>
        <path d="M-16,-6 L8,-6 L18,0 L8,6 L-16,6 L-12,0Z" fill="#ffffff" stroke="#c95a41" stroke-width="1.3" />
        <polygon points="-16,-6 -24,-12 -10,-6" fill="#f5c46e" />
        <polygon points="-16,6 -24,12 -10,6" fill="#f5c46e" />
        <rect x="-6" y="-12" width="12" height="4" fill="#64b5f6" />
        <rect x="-6" y="8" width="12" height="4" fill="#64b5f6" />
        <circle cx="8" cy="0" r="3" fill="#2ecc71" />
        <animateMotion dur="22s" repeatCount="indefinite" rotate="auto">
            <mpath href="#{path_mars_id}" />
        </animateMotion>
    </g>"""
    body.append(mars_ship)

    moon_ship = f"""<!-- Cislunar Crew Transport Vessel -->
    <g>
        <polygon points="12,0 -9,-8 -5,0 -9,8" fill="#ffffff" stroke="#003366" stroke-width="1.2" />
        <rect x="-7" y="-3" width="6" height="6" fill="#ffd54f" />
        <animateMotion dur="12s" repeatCount="indefinite" rotate="auto">
            <mpath href="#{path_moon_id}" />
        </animateMotion>
    </g>"""
    body.append(moon_ship)

    # 7. HUD Mission Status Header
    hud_header_svg = f"""<!-- HUD Mission Status Header -->
    <g font-family="Manrope, sans-serif" font-size="11" font-weight="700" letter-spacing="1.5">
        <rect x="310" y="20" width="540" height="32" rx="16" fill="#04121a" stroke="#e3735a" stroke-width="1.2" opacity="0.95" />
        <text x="580" y="41" fill="#fbf7f0" text-anchor="middle">{hud_header}</text>
    </g>"""
    body.append(hud_header_svg)

    inner_content = "\n".join(body)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 1160 480" role="img" aria-label="{aria_label}">
{defs}
    <g clip-path="url(#{clip_id})">
{inner_content}
    </g>
</svg>"""


# ==============================================================================
# INJECTION AND LINKING INTO HTML
# ==============================================================================
def update_space_page(file_path: Path, lang: str = "en") -> None:
    content = file_path.read_text(encoding="utf-8")

    aria_station = (
        "Waikiki National Space Station Orbital Complex and Telemetry Diagram"
        if lang == "en"
        else "Waikiki Nemzeti Űrállomás pályamenti komplexum és telemetriai diagram"
    )
    station_img = f'<img class="ill" src="../icons/space/station-{lang}.svg" alt="{aria_station}" width="1160" height="520" loading="lazy" />'

    aria_corridor = (
        "Earth Moon and Mars Interplanetary Transfer Corridor Map"
        if lang == "en"
        else "Föld, Hold és Mars bolygóközi transzferfolyosó térkép"
    )
    corridor_img = f'<img class="ill" src="../icons/space/corridor-{lang}.svg" alt="{aria_corridor}" width="1160" height="480" loading="lazy" />'

    # Replace SVG or existing img in #station section
    station_pattern = re.compile(
        r'(<section id="station"[^>]*>.*?<div class="ill-panel">\s*)(?:<svg.*?</svg>|<img[^>]*class="ill"[^>]*>)?(\s*<div class="ill-caption">)',
        re.DOTALL,
    )
    if not station_pattern.search(content):
        raise ValueError(f"Could not find #station pattern in {file_path}")
    content = station_pattern.sub(r'\1' + station_img + r'\2', content)

    # Replace SVG or existing img in #lunar-mars section
    lunar_pattern = re.compile(
        r'(<section id="lunar-mars"[^>]*>.*?<div class="ill-panel">\s*)(?:<svg.*?</svg>|<img[^>]*class="ill"[^>]*>)?(\s*<div class="ill-caption">)',
        re.DOTALL,
    )
    if not lunar_pattern.search(content):
        raise ValueError(f"Could not find #lunar-mars pattern in {file_path}")
    content = lunar_pattern.sub(r'\1' + corridor_img + r'\2', content)

    # Clean formatting
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_pages import format_and_remove_empty_lines

    formatted = format_and_remove_empty_lines(content)
    file_path.write_text(formatted, encoding="utf-8")
    print(f"Updated and formatted {file_path.relative_to(ROOT)}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating standalone Space Research SVGs...")
    for lang in ("en", "hu"):
        station_svg = build_station_svg(lang)
        station_file = OUT_DIR / f"station-{lang}.svg"
        station_file.write_text(station_svg + "\n", encoding="utf-8")
        print(f"  Saved {station_file.relative_to(ROOT)} ({len(station_svg)/1024:.1f} KB)")

        corridor_svg = build_lunar_mars_svg(lang)
        corridor_file = OUT_DIR / f"corridor-{lang}.svg"
        corridor_file.write_text(corridor_svg + "\n", encoding="utf-8")
        print(f"  Saved {corridor_file.relative_to(ROOT)} ({len(corridor_svg)/1024:.1f} KB)")

    en_file = ROOT / "en" / "space-research.html"
    hu_file = ROOT / "hu" / "space-research.html"
    update_space_page(en_file, "en")
    update_space_page(hu_file, "hu")
    print("Space research SVGs successfully generated and linked!")


if __name__ == "__main__":
    main()
