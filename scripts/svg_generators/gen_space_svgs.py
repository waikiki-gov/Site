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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

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


# ==============================================================================
# 1. WNSS ORBITAL COMPLEX SVG (1160 x 520)
# ==============================================================================
def build_station_svg(lang="en") -> str:
    clip_id = "sr-clip1" if lang == "en" else "sr-hu-clip1"

    # Localized text labels
    if lang == "hu":
        hud_alt = "MAGASSÁG: 420.4 KM"
        hud_vel = "SEBESSÉG: 7.66 KM/S"
        hud_crew = "12 FŐ AKTÍV"
        hud_badge_l1 = "WSA ŰRÁLLOMÁS LOGISZTIKA"
        hud_badge_l2 = "NAPELEMES TELJESÍTMÉNY: 140 KW"
        hud_badge_r1 = "DOKKOLÓKAPUK: 6 AKTÍV"
        hud_badge_r2 = "AUTOMATIKUS KÖZELÍTÉSRE KÉSZ"
    else:
        hud_alt = "ALT: 420.4 KM"
        hud_vel = "VEL: 7.66 KM/S"
        hud_crew = "CREW: 12 NOMINAL"
        hud_badge_l1 = "WSA ORBITAL LOGISTICS"
        hud_badge_l2 = "SOLAR OUTPUT: 140 KW"
        hud_badge_r1 = "DOCKING PORTS: 6 ACTIVE"
        hud_badge_r2 = "RENDEZVOUS APPROACH READY"

    rng = random.Random(42)

    defs = f"""    <defs>
        <clipPath id="{clip_id}">
            <rect width="1160" height="520" />
        </clipPath>
        <clipPath id="{clip_id}-earth-limb">
            <path d="M-80,560 C250,395 910,395 1240,560 L1240,600 L-80,600 Z" />
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
        <linearGradient id="sr-earth-surface" x1="0%" y1="0%" x2="100%" y2="50%">
            <stop offset="0%" stop-color="#0284c7" />
            <stop offset="25%" stop-color="#0369a1" />
            <stop offset="55%" stop-color="#0c4a6e" />
            <stop offset="78%" stop-color="#082f49" />
            <stop offset="100%" stop-color="#020617" />
        </linearGradient>
        <linearGradient id="sr-earth-terminator" x1="45%" y1="0%" x2="90%" y2="0%">
            <stop offset="0%" stop-color="#020617" stop-opacity="0" />
            <stop offset="40%" stop-color="#020617" stop-opacity="0.65" />
            <stop offset="100%" stop-color="#020617" stop-opacity="0.98" />
        </linearGradient>
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

    # 3. Realistic Pure Vector Earth Curvature Below
    body.append('<!-- Pure Vector Earth Limb from LEO Orbit -->')
    limb_clip = f"url(#{clip_id}-earth-limb)"
    earth_limb_elements = f"""    <g clip-path="{limb_clip}">
        <rect x="-80" y="380" width="1320" height="200" fill="url(#sr-earth-surface)" />
        <!-- Coastal Waters and Reefs -->
        <path d="M40,490 C120,440 220,430 310,460 C260,490 140,510 40,490 Z" fill="#38bdf8" opacity="0.35" />
        <path d="M380,455 C460,425 560,430 640,470 C580,495 480,495 380,455 Z" fill="#38bdf8" opacity="0.35" />
        <!-- Landmasses and Continents -->
        <path d="M60,500 C130,450 200,445 290,470 C250,495 150,515 60,500 Z" fill="#166534" opacity="0.75" />
        <path d="M90,495 C140,465 190,460 250,480 C220,495 150,505 90,495 Z" fill="#22c55e" opacity="0.5" />
        <path d="M410,465 C480,440 550,442 620,478 C570,495 490,495 410,465 Z" fill="#15803d" opacity="0.7" />
        <path d="M430,468 C490,450 530,452 580,480 C540,490 480,490 430,468 Z" fill="#4ade80" opacity="0.45" />
        <path d="M660,475 C720,455 800,460 880,495 C820,510 740,505 660,475 Z" fill="#1e3a24" opacity="0.65" />
        <!-- Weather Patterns and Swirling Cloud Bands -->
        <path d="M-40,480 C120,420 280,425 460,460 C380,475 220,455 80,485 C20,495 -20,500 -40,480 Z" fill="#ffffff" opacity="0.6" />
        <path d="M180,450 C320,410 490,420 680,465 C590,480 440,450 290,465 C230,472 190,465 180,450 Z" fill="#ffffff" opacity="0.55" />
        <path d="M480,460 C620,430 780,445 960,490 C880,500 740,475 600,480 C530,482 490,475 480,460 Z" fill="#ffffff" opacity="0.45" />
        <path d="M310,445 C350,432 390,435 420,450 C390,458 350,455 310,445 Z" fill="#f8fafc" opacity="0.75" />
        <path d="M720,470 C770,458 830,462 890,485 C840,492 780,488 720,470 Z" fill="#f8fafc" opacity="0.4" />
        <path d="M140,465 Q165,455 190,465 T215,480 Q190,485 165,475 Z" fill="#ffffff" opacity="0.7" />
        <ellipse cx="178" cy="468" rx="8" ry="4" fill="#0369a1" opacity="0.6" />
        <!-- Terminator Shadow Overlay -->
        <rect x="-80" y="380" width="1320" height="200" fill="url(#sr-earth-terminator)" />
    </g>"""
    body.append(earth_limb_elements)
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

    prefix = "sr-" if lang == "en" else "sr-hu-"
    port_assembly_id = f"{prefix}port-solar-assembly"
    starboard_assembly_id = f"{prefix}starboard-solar-assembly"

    sw_port_top = "\n".join("    " + line for line in solar_wing(150, 136, 80, 84).splitlines())
    sw_port_bot = "\n".join("    " + line for line in solar_wing(150, 244, 80, 84).splitlines())
    sw_stbd_top = "\n".join("    " + line for line in solar_wing(930, 136, 80, 84).splitlines())
    sw_stbd_bot = "\n".join("    " + line for line in solar_wing(930, 244, 80, 84).splitlines())

    body.append(f"""<!-- Port Solar Array Wings (Left) -->
<g id="{port_assembly_id}">
    <!-- Port Outrigger Extension Boom -->
    <rect x="188" y="227" width="52" height="10" rx="2" fill="#2d424b" stroke="#6BA4D9" stroke-width="1.2" />
    <line x1="188" y1="232" x2="240" y2="232" stroke="#d5ede9" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.85" />
    <path d="M188,227 L200,237 M200,227 L188,237 M200,227 L212,237 M212,227 L200,237 M212,227 L224,237 M224,227 L212,237 M224,227 L236,237 M236,227 L224,237" stroke="#466570" stroke-width="1.0" opacity="0.75" />
    <!-- Structural Support Struts -->
    <line x1="234" y1="227" x2="194" y2="221" stroke="#8faeb6" stroke-width="1.6" stroke-linecap="round" />
    <line x1="234" y1="237" x2="194" y2="243" stroke="#8faeb6" stroke-width="1.6" stroke-linecap="round" />
    <!-- Solar Blanket Deployment Canisters and Spreaders -->
    <rect x="148" y="218" width="84" height="4" rx="1" fill="#1b2a30" stroke="#6BA4D9" stroke-width="1" />
    <rect x="148" y="242" width="84" height="4" rx="1" fill="#1b2a30" stroke="#6BA4D9" stroke-width="1" />
    <line x1="149" y1="136" x2="231" y2="136" stroke="#8faeb6" stroke-width="1.6" stroke-linecap="round" />
    <line x1="149" y1="328" x2="231" y2="328" stroke="#8faeb6" stroke-width="1.6" stroke-linecap="round" />
    <!-- Continuous Central Mast -->
    <line x1="190" y1="218" x2="190" y2="246" stroke="#ffffff" stroke-width="2" />
    <!-- Beta Gimbal Assembly (BGA) Hub -->
    <rect x="182" y="224" width="16" height="16" rx="2.5" fill="url(#sr-hull-cyl)" stroke="#003366" stroke-width="1.2" />
    <circle cx="190" cy="232" r="4.5" fill="#f5c46e" stroke="#003366" stroke-width="0.8" />
    <circle cx="190" cy="232" r="2" fill="#42d0f5" />
    <!-- Solar Array Wings (Photovoltaic Blankets) -->
{sw_port_top}
{sw_port_bot}
    <!-- Solar Alpha Rotary Joint (SARJ) -->
    <rect x="228" y="228" width="24" height="8" rx="1" fill="#cbe0dc" stroke="#486872" stroke-width="1" />
    <circle cx="240" cy="232" r="5" fill="#f5c46e" />
    <circle cx="240" cy="232" r="2.2" fill="#1a3b68" />
</g>""")

    body.append(f"""<!-- Starboard Solar Array Wings (Right) -->
<g id="{starboard_assembly_id}">
    <!-- Starboard Outrigger Extension Boom -->
    <rect x="920" y="227" width="52" height="10" rx="2" fill="#2d424b" stroke="#6BA4D9" stroke-width="1.2" />
    <line x1="920" y1="232" x2="972" y2="232" stroke="#d5ede9" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.85" />
    <path d="M924,227 L936,237 M936,227 L924,237 M936,227 L948,237 M948,227 L936,237 M948,227 L960,237 M960,227 L948,237 M960,227 L972,237 M972,227 L960,237" stroke="#466570" stroke-width="1.0" opacity="0.75" />
    <!-- Structural Support Struts -->
    <line x1="926" y1="227" x2="966" y2="221" stroke="#8faeb6" stroke-width="1.6" stroke-linecap="round" />
    <line x1="926" y1="237" x2="966" y2="243" stroke="#8faeb6" stroke-width="1.6" stroke-linecap="round" />
    <!-- Solar Blanket Deployment Canisters and Spreaders -->
    <rect x="928" y="218" width="84" height="4" rx="1" fill="#1b2a30" stroke="#6BA4D9" stroke-width="1" />
    <rect x="928" y="242" width="84" height="4" rx="1" fill="#1b2a30" stroke="#6BA4D9" stroke-width="1" />
    <line x1="929" y1="136" x2="1011" y2="136" stroke="#8faeb6" stroke-width="1.6" stroke-linecap="round" />
    <line x1="929" y1="328" x2="1011" y2="328" stroke="#8faeb6" stroke-width="1.6" stroke-linecap="round" />
    <!-- Continuous Central Mast -->
    <line x1="970" y1="218" x2="970" y2="246" stroke="#ffffff" stroke-width="2" />
    <!-- Beta Gimbal Assembly (BGA) Hub -->
    <rect x="962" y="224" width="16" height="16" rx="2.5" fill="url(#sr-hull-cyl)" stroke="#003366" stroke-width="1.2" />
    <circle cx="970" cy="232" r="4.5" fill="#f5c46e" stroke="#003366" stroke-width="0.8" />
    <circle cx="970" cy="232" r="2" fill="#42d0f5" />
    <!-- Solar Array Wings (Photovoltaic Blankets) -->
{sw_stbd_top}
{sw_stbd_bot}
    <!-- Solar Alpha Rotary Joint (SARJ) -->
    <rect x="908" y="228" width="24" height="8" rx="1" fill="#cbe0dc" stroke="#486872" stroke-width="1" />
    <circle cx="920" cy="232" r="5" fill="#f5c46e" />
    <circle cx="920" cy="232" r="2.2" fill="#1a3b68" />
</g>""")

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
    return f"""<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 1160 520">
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
        hud_header = "HOLD-BÁZIS ÉS MARS KÖZI TRANSZFERFOLYOSÓ"
        lbl_earth_title = "FÖLD"
        lbl_earth_sub = "BÁZISÁLLOMÁS"
        lbl_moon_title = "HOLD PROGRAM"
        lbl_moon_sub = "2026-2030"
        lbl_mars_title = "MARS EXPEDÍCIÓ"
        lbl_mars_sub = "2035-2040"
    else:
        hud_header = "MOON BASE AND MARS INTERPLANETARY CORRIDOR"
        lbl_earth_title = "EARTH"
        lbl_earth_sub = "PRIMARY BASE"
        lbl_moon_title = "LUNAR MISSION"
        lbl_moon_sub = "2026-2030"
        lbl_mars_title = "MARS EXPEDITION"
        lbl_mars_sub = "2035-2040"

    rng = random.Random(108)

    defs = f"""    <defs>
        <clipPath id="{clip_id}">
            <rect width="1160" height="480" />
        </clipPath>
        <clipPath id="{clip_id}-earth">
            <circle cx="0" cy="0" r="65" />
        </clipPath>
        <clipPath id="{clip_id}-moon">
            <circle cx="0" cy="0" r="38" />
        </clipPath>
        <clipPath id="{clip_id}-mars">
            <circle cx="0" cy="0" r="62" />
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
        <radialGradient id="sr-earth-ocean-rad" cx="32%" cy="28%" r="68%">
            <stop offset="0%" stop-color="#38bdf8" />
            <stop offset="30%" stop-color="#0284c7" />
            <stop offset="65%" stop-color="#0369a1" />
            <stop offset="100%" stop-color="#082f49" />
        </radialGradient>
        <radialGradient id="sr-moon-rad" cx="32%" cy="28%" r="68%">
            <stop offset="0%" stop-color="#f8fafc" />
            <stop offset="35%" stop-color="#cbd5e1" />
            <stop offset="70%" stop-color="#94a3b8" />
            <stop offset="100%" stop-color="#475569" />
        </radialGradient>
        <radialGradient id="sr-mars-rad" cx="32%" cy="28%" r="68%">
            <stop offset="0%" stop-color="#fb923c" />
            <stop offset="35%" stop-color="#ea580c" />
            <stop offset="70%" stop-color="#c2410c" />
            <stop offset="90%" stop-color="#7c2d12" />
            <stop offset="100%" stop-color="#431407" />
        </radialGradient>
        <radialGradient id="sr-planet-shadow" cx="32%" cy="28%" r="68%">
            <stop offset="0%" stop-color="#020617" stop-opacity="0" />
            <stop offset="48%" stop-color="#020617" stop-opacity="0" />
            <stop offset="78%" stop-color="#020617" stop-opacity="0.65" />
            <stop offset="100%" stop-color="#020617" stop-opacity="0.95" />
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

    # 3. PLANET EARTH NODE (x=180, y=240, r=65) - Orbit ring & satellite rotate rock-solid around planet center (0, 0)
    earth_clip_url = f"url(#{clip_id}-earth)"
    earth_group = f"""<!-- 3D Pure Vector Earth Node -->
    <g transform="translate(180, 240)">
        <g>
            <circle cx="0" cy="0" r="76" fill="none" stroke="#6BA4D9" stroke-width="1.2" stroke-dasharray="6 6" opacity="0.8" />
            <circle cx="0" cy="-76" r="3.5" fill="#2ecc71" />
            <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="24s" repeatCount="indefinite" />
        </g>
        <g clip-path="{earth_clip_url}">
            <circle cx="0" cy="0" r="65" fill="url(#sr-earth-ocean-rad)" />
            <!-- Continents -->
            <path d="M-42,-38 C-36,-44 -26,-36 -28,-24 C-30,-12 -22,-6 -18,2 C-14,10 -22,22 -26,35 C-30,46 -36,40 -40,30 C-36,22 -32,15 -35,5 C-38,-4 -48,-10 -52,-22 C-55,-32 -48,-34 -42,-38 Z" fill="#15803d" opacity="0.85" />
            <path d="M-30,-22 C-26,-28 -20,-24 -22,-16 C-24,-10 -30,-12 -30,-22 Z" fill="#65a30d" opacity="0.6" />
            <path d="M-24,12 C-18,18 -20,28 -26,32 C-28,24 -24,18 -24,12 Z" fill="#22c55e" opacity="0.65" />
            <path d="M2,-36 C12,-40 22,-34 26,-26 C28,-20 22,-16 26,-10 C32,-2 38,12 34,26 C30,40 18,48 10,42 C8,34 14,24 16,14 C18,4 12,-4 8,-12 C6,-20 0,-26 2,-36 Z" fill="#166534" opacity="0.85" />
            <path d="M12,-2 C20,6 24,18 20,28 C16,22 14,12 12,-2 Z" fill="#a16207" opacity="0.5" />
            <ellipse cx="-20" cy="-56" rx="24" ry="8" fill="#f8fafc" opacity="0.9" />
            <ellipse cx="0" cy="58" rx="28" ry="7" fill="#f8fafc" opacity="0.85" />
            <!-- Cloud Swirls -->
            <path d="M-55,-15 C-35,-25 -10,-10 15,-20 C35,-28 50,-15 62,-5 C52,2 35,-10 15,-5 C-10,0 -35,-8 -55,-15 Z" fill="#ffffff" opacity="0.65" />
            <path d="M-45,15 C-20,5 5,20 30,10 C45,5 55,18 60,25 C50,28 35,22 15,28 C-5,32 -30,25 -45,15 Z" fill="#ffffff" opacity="0.55" />
            <path d="M-30,-42 C-10,-48 15,-40 40,-45 C30,-38 10,-35 -15,-38 Z" fill="#ffffff" opacity="0.5" />
            <!-- 3D Shadow -->
            <circle cx="0" cy="0" r="65" fill="url(#sr-planet-shadow)" />
        </g>
        <circle cx="0" cy="0" r="65" fill="none" stroke="#38bdf8" stroke-width="2.2" opacity="0.75" filter="url(#sr-planet-glow)" />
        <circle cx="0" cy="0" r="66" fill="none" stroke="#bae6fd" stroke-width="0.9" opacity="0.8" />
        <text x="0" y="88" fill="#fbf7f0" font-family="Manrope, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1.5">{lbl_earth_title}</text>
        <text x="0" y="105" fill="#6BA4D9" font-family="Manrope, sans-serif" font-size="10" font-weight="600" text-anchor="middle">{lbl_earth_sub}</text>
    </g>"""
    body.append(earth_group)

    # 4. MOON NODE & LUNAR BASE (x=540, y=190, r=38) - Orbit ring & base rotate rock-solid around Moon center (0, 0)
    moon_clip_url = f"url(#{clip_id}-moon)"
    moon_group = f"""<!-- 3D Pure Vector Moon Node -->
    <g transform="translate(540, 190)">
        <g>
            <circle cx="0" cy="0" r="48" fill="none" stroke="#f5c46e" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.8" />
            <circle cx="0" cy="-48" r="3" fill="#ffd54f" />
            <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="16s" repeatCount="indefinite" />
        </g>
        <g clip-path="{moon_clip_url}">
            <circle cx="0" cy="0" r="38" fill="url(#sr-moon-rad)" />
            <!-- Lunar Maria Basalt Plains -->
            <path d="M-15,-22 C-5,-28 8,-24 14,-15 C18,-5 12,5 4,8 C-4,10 -14,6 -18,-2 C-22,-10 -20,-18 -15,-22 Z" fill="#334155" opacity="0.75" />
            <path d="M-26,-10 C-18,-14 -12,-8 -15,0 C-18,6 -26,4 -28,-2 Z" fill="#475569" opacity="0.65" />
            <path d="M-8,12 C2,10 12,16 10,24 C8,28 -2,30 -6,24 Z" fill="#334155" opacity="0.6" />
            <path d="M12,-8 C20,-12 28,-6 26,2 C24,8 16,6 12,-2 Z" fill="#1e293b" opacity="0.55" />
            <!-- Impact Craters -->
            <circle cx="12" cy="22" r="3" fill="#f8fafc" stroke="#64748b" stroke-width="0.8" />
            <circle cx="12" cy="22" r="1.2" fill="#0f172a" />
            <line x1="12" y1="22" x2="28" y2="30" stroke="#f8fafc" stroke-width="0.6" opacity="0.5" stroke-dasharray="2 3" />
            <line x1="12" y1="22" x2="-4" y2="28" stroke="#f8fafc" stroke-width="0.6" opacity="0.5" stroke-dasharray="2 3" />
            <line x1="12" y1="22" x2="16" y2="6" stroke="#f8fafc" stroke-width="0.6" opacity="0.5" stroke-dasharray="2 3" />
            <circle cx="-12" cy="-6" r="2.5" fill="#f8fafc" stroke="#475569" stroke-width="0.7" />
            <circle cx="-12" cy="-6" r="1" fill="#1e293b" />
            <circle cx="-4" cy="-26" r="1.8" fill="#cbd5e1" stroke="#334155" stroke-width="0.6" />
            <circle cx="20" cy="-14" r="2" fill="#cbd5e1" stroke="#334155" stroke-width="0.6" />
            <circle cx="-22" cy="14" r="1.5" fill="#cbd5e1" stroke="#334155" stroke-width="0.5" />
            <!-- 3D Shadow -->
            <circle cx="0" cy="0" r="38" fill="url(#sr-planet-shadow)" />
        </g>
        <circle cx="0" cy="0" r="38" fill="none" stroke="#e2e8f0" stroke-width="1" opacity="0.75" />
        <text x="0" y="62" fill="#fbf7f0" font-family="Manrope, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1.5">{lbl_moon_title}</text>
        <text x="0" y="79" fill="#f5c46e" font-family="Manrope, sans-serif" font-size="10" font-weight="600" text-anchor="middle">{lbl_moon_sub}</text>
    </g>"""
    body.append(moon_group)

    # 5. MARS NODE & EXPEDITION CORRIDOR (x=960, y=240, r=62) - Orbit ring & base rotate rock-solid around Mars center (0, 0)
    mars_clip_url = f"url(#{clip_id}-mars)"
    mars_group = f"""<!-- 3D Pure Vector Mars Node -->
    <g transform="translate(960, 240)">
        <g>
            <circle cx="0" cy="0" r="74" fill="none" stroke="#e3735a" stroke-width="1.2" stroke-dasharray="6 6" opacity="0.8" />
            <circle cx="0" cy="-74" r="3.5" fill="#ff7043" />
            <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="28s" repeatCount="indefinite" />
        </g>
        <g clip-path="{mars_clip_url}">
            <circle cx="0" cy="0" r="62" fill="url(#sr-mars-rad)" />
            <!-- Dark Basalt Regions -->
            <path d="M-25,-15 C-15,-28 5,-22 15,-12 C25,2 18,18 5,24 C-10,28 -28,20 -35,5 C-38,-6 -30,-10 -25,-15 Z" fill="#451a03" opacity="0.7" />
            <path d="M8,-32 C20,-38 34,-30 38,-18 C40,-8 32,-4 26,-8 C20,-14 12,-24 8,-32 Z" fill="#3c1404" opacity="0.65" />
            <path d="M-42,-5 C-32,-12 -25,-5 -28,5 C-32,15 -44,12 -45,2 Z" fill="#451a03" opacity="0.6" />
            <!-- Valles Marineris Canyon -->
            <path d="M-28,4 Q-5,8 18,2 T42,-4" fill="none" stroke="#260c02" stroke-width="2.4" stroke-linecap="round" opacity="0.8" />
            <path d="M-26,5 Q-4,9 18,3 T40,-3" fill="none" stroke="#78350f" stroke-width="1" stroke-linecap="round" opacity="0.6" />
            <!-- Olympus Mons -->
            <ellipse cx="-34" cy="-16" rx="9" ry="6" fill="#78350f" opacity="0.6" />
            <ellipse cx="-34" cy="-16" rx="3.5" ry="2" fill="#260c02" opacity="0.8" />
            <ellipse cx="-34" cy="-16" rx="1.5" ry="1" fill="#ea580c" opacity="0.7" />
            <!-- Polar Ice Cap -->
            <ellipse cx="4" cy="-56" rx="22" ry="7" fill="#f0fdfa" opacity="0.95" />
            <ellipse cx="4" cy="-56" rx="14" ry="4.5" fill="#ffffff" opacity="0.8" />
            <!-- Dust Storms -->
            <path d="M-50,22 C-30,15 0,32 30,24 C45,20 54,30 58,35 C48,38 25,32 -5,38 C-30,42 -45,32 -50,22 Z" fill="#fed7aa" opacity="0.32" />
            <!-- 3D Shadow -->
            <circle cx="0" cy="0" r="62" fill="url(#sr-planet-shadow)" />
        </g>
        <circle cx="0" cy="0" r="62" fill="none" stroke="#fb923c" stroke-width="2" opacity="0.6" filter="url(#sr-planet-glow)" />
        <circle cx="0" cy="0" r="63" fill="none" stroke="#fdba74" stroke-width="0.8" opacity="0.75" />
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
    return f"""<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 1160 480">
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

    alt_station = (
        "Waikiki National Space Station Orbital Complex and Telemetry Diagram"
        if lang == "en"
        else "Waikiki Nemzeti Űrállomás pályamenti komplexum és telemetriai diagram"
    )
    station_img = f'<img class="ill" src="../icons/space/station-{lang}.svg" alt="{alt_station}" width="1160" height="520" loading="lazy" />'

    alt_corridor = (
        "Earth Moon and Mars Interplanetary Transfer Corridor Map"
        if lang == "en"
        else "Föld, Hold és Mars bolygóközi transzferfolyosó térkép"
    )
    corridor_img = f'<img class="ill" src="../icons/space/corridor-{lang}.svg" alt="{alt_corridor}" width="1160" height="480" loading="lazy" />'

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
        station_svg = "\n".join(line for line in station_svg.splitlines() if line.strip())
        station_file = OUT_DIR / f"station-{lang}.svg"
        station_file.write_text(station_svg + "\n", encoding="utf-8")
        print(f"  Saved {station_file.relative_to(ROOT)} ({len(station_svg)/1024:.1f} KB)")

        corridor_svg = build_lunar_mars_svg(lang)
        corridor_svg = "\n".join(line for line in corridor_svg.splitlines() if line.strip())
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
