#!/usr/bin/env python3
"""
Generate museum-grade realistic SVG illustrations for space-research.html.
Generates:
1. #station WNSS Orbital Complex (1160x520)
2. #lunar-mars Earth-Moon-Mars Interplanetary Transfer Corridor (1160x480)
Injects inline into en/space-research.html and hu/space-research.html while preserving
all animations (animateMotion, spin, spin-rev, pulse, twinkle, dash) and localized labels.
"""

import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

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
def build_station_svg(lang="en"):
    clip_id = "sr-clip1" if lang == "en" else "sr-hu-clip1"
    
    # Localized text labels
    if lang == "hu":
        aria_label = "Waikiki Nemzeti Űrállomás pályamenti felépítése és telemetriai ábrája"
        hud_alt = "MAGASSÁG: 420.4 KM"
        hud_vel = "SEBESSÉG: 7.66 KM/S"
        hud_crew = "12 FŐ AKTÍV"
        hud_badge_l1 = "WSA ŰRÁLLOMÁS LOGISZTIKA"
        hud_badge_l2 = "NAPELEMES TELJESÍTMÉNY: 140 KW (100%)"
        hud_badge_r1 = "DOKKOLÓKAPUK: 6 AKTÍV"
        hud_badge_r2 = "AUTOMATIKUS KÖZELÍTÉSRE KÉSZ"
    else:
        aria_label = "Waikiki National Space Station Orbital Complex and Telemetry Diagram"
        hud_alt = "ALT: 420.4 KM"
        hud_vel = "VEL: 7.66 KM/S"
        hud_crew = "CREW: 12 NOMINAL"
        hud_badge_l1 = "WSA ORBITAL LOGISTICS"
        hud_badge_l2 = "SOLAR OUTPUT: 140 KW (100%)"
        hud_badge_r1 = "DOCKING PORTS: 6 ACTIVE"
        hud_badge_r2 = "RENDEZVOUS APPROACH READY"

    rng = random.Random(42)

    # Defs: gradients & filters
    defs = f"""                    <defs>
                        <clipPath id="{clip_id}">
                            <rect width="1160" height="520" />
                        </clipPath>
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
                        <linearGradient id="sr-earth-ocean" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stop-color="#0d3f66" />
                            <stop offset="30%" stop-color="#092d4a" />
                            <stop offset="70%" stop-color="#051c2e" />
                            <stop offset="100%" stop-color="#020d17" />
                        </linearGradient>
                        <linearGradient id="sr-atmo-limb" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stop-color="#70d6ff" stop-opacity="0.85" />
                            <stop offset="25%" stop-color="#38b6ff" stop-opacity="0.65" />
                            <stop offset="65%" stop-color="#0066cc" stop-opacity="0.30" />
                            <stop offset="100%" stop-color="#002244" stop-opacity="0" />
                        </linearGradient>
                        <linearGradient id="sr-solar-wafer" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#1a3b68" />
                            <stop offset="30%" stop-color="#0d2448" />
                            <stop offset="70%" stop-color="#081832" />
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
    body.append(f'<rect width="1160" height="520" fill="url(#sr-space-bg)" />')
    # Nebulae
    body.append(f'<ellipse cx="340" cy="120" rx="360" ry="100" fill="url(#sr-nebula-teal)" />')
    body.append(f'<ellipse cx="880" cy="140" rx="320" ry="110" fill="url(#sr-nebula-blue)" />')
    body.append(f'<ellipse cx="580" cy="70" rx="260" ry="60" fill="#6BA4D9" opacity="0.08" />')

    # 2. Multi-magnitude Realistic Starfield with Twinkle
    stars = []
    # Fixed bright stars
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
    # Fainter background stars
    faint_stars = []
    for _ in range(85):
        fx = rng.uniform(10, 1150)
        fy = rng.uniform(10, 260)
        fr = rng.uniform(0.6, 1.0)
        faint_stars.append(f'<circle cx="{n(fx)}" cy="{n(fy)}" r="{n(fr)}" />')
    body.append(f'<g fill="#ffffff" opacity="0.65">\n' + "\n".join(faint_stars) + "\n</g>")
    body.append(f'<g>\n' + "\n".join(stars) + "\n</g>")

    # 3. Realistic Photorealistic Earth Curvature Below
    # Earth Horizon: arc from (-80, 560) through (580, 412) to (1240, 560)
    # Ocean mass
    body.append(f'<path d="M-80,620 L-80,560 C250,395 910,395 1240,560 L1240,620Z" fill="url(#sr-earth-ocean)" />')
    
    # Atmospheric Limb Layers (Scattering & Rayleigh effect)
    body.append(f'<path d="M-80,560 C250,395 910,395 1240,560" fill="none" stroke="#003366" stroke-width="28" opacity="0.45" />')
    body.append(f'<path d="M-80,560 C250,395 910,395 1240,560" fill="none" stroke="#1d8cf8" stroke-width="16" opacity="0.38" />')
    body.append(f'<path d="M-80,560 C250,395 910,395 1240,560" fill="none" stroke="#62d6ff" stroke-width="8" opacity="0.65" />')
    body.append(f'<path d="M-80,560 C250,395 910,395 1240,560" fill="none" stroke="#dcf8ff" stroke-width="2.2" opacity="0.95" />')

    # Earth Pacific & Tropical Archipelagos below (shimmering turquoise coral shelf & emerald landmasses)
    body.append(f'<path d="M160,505 C240,465 340,460 410,482 C460,496 520,490 570,468 C620,446 710,444 760,465 C820,490 920,480 980,455 C1020,438 1080,442 1120,470" '
                f'fill="none" stroke="#1fb8a8" stroke-width="14" stroke-linecap="round" opacity="0.45" />')
    body.append(f'<path d="M140,510 C220,470 320,464 390,486 C440,500 500,494 550,472 C600,450 690,448 740,469 C800,494 900,484 960,459 C1000,442 1060,446 1100,474" '
                f'fill="none" stroke="#368c56" stroke-width="8" stroke-linecap="round" opacity="0.75" />')

    # Realistic Swirling Cyclonic Cloud Systems with Soft Volumetric Shading
    cloud_paths = [
        # Cloud swirl 1
        "M220,485 C250,465 295,470 325,482 C345,490 380,482 400,474 C360,470 310,458 260,470 C235,476 215,482 220,485Z",
        # Cloud swirl 2
        "M460,475 C510,450 570,452 610,468 C645,482 690,478 725,462 C680,454 625,444 565,450 C515,456 475,468 460,475Z",
        # Cloud swirl 3 (cyclone spiral)
        "M780,480 C820,460 880,458 925,474 C960,486 1010,476 1045,458 C995,450 940,446 885,452 C835,458 795,472 780,480Z",
    ]
    for cp in cloud_paths:
        # Shadow on ocean
        body.append(f'<path d="{cp}" fill="#051c2e" opacity="0.4" transform="translate(4, 4)" />')
        # White cloud layer
        body.append(f'<path d="{cp}" fill="#f0faff" opacity="0.82" />')

    # Sparkling City Night Lights on the shadowed limb (right side)
    city_lights = [
        (720, 482, 1.4), (755, 488, 1.8), (790, 478, 1.6), (840, 474, 2.0),
        (875, 468, 1.8), (910, 462, 1.5), (945, 472, 1.7), (990, 465, 1.9),
        (1030, 472, 1.5), (1070, 480, 1.8), (815, 492, 1.3), (860, 484, 1.4)
    ]
    city_els = []
    for cx_, cy_, cr_ in city_lights:
        city_els.append(f'<circle cx="{cx_}" cy="{cy_}" r="{cr_}" />')
    body.append(f'<g fill="#ffcf70" opacity="0.85" filter="url(#sr-glow)">\n' + "\n".join(city_els) + "\n</g>")

    # 4. Docking Approach Flight Corridor
    body.append(f'<path id="sr-docking-path" d="M60,310 C320,180 840,180 1100,310" fill="none" stroke="#f5c46e" stroke-width="1.8" stroke-dasharray="6 8" opacity="0.75" class="dash" />')
    
    # Approaching Autonomous Spacecraft
    craft = f"""                        <g>
                            <path d="M-14,-5 L6,-5 L14,0 L6,5 L-14,5 L-10,0Z" fill="#ffffff" stroke="#003366" stroke-width="1.2" />
                            <polygon points="-14,-5 -19,-10 -9,-5" fill="#c95a41" />
                            <polygon points="-14,5 -19,10 -9,5" fill="#c95a41" />
                            <rect x="-8" y="-3" width="8" height="6" rx="1.5" fill="#1a528f" />
                            <circle cx="9" cy="0" r="2.2" fill="#6BA4D9" />
                            <animateMotion dur="18s" repeatCount="indefinite" rotate="auto">
                                <mpath href="#sr-docking-path" />
                            </animateMotion>
                        </g>"""
    body.append(craft)

    # 5. WNSS STATION COMPLEX STRUCTURE
    # Primary Structural Truss Backbone (Integrated Truss System)
    body.append(f'<!-- Integrated Truss System (ITS) -->')
    body.append(f'<rect x="250" y="226" width="660" height="12" rx="2" fill="#2d424b" stroke="#6BA4D9" stroke-width="1.2" />')
    body.append(f'<line x1="250" y1="232" x2="910" y2="232" stroke="#d5ede9" stroke-width="2" stroke-dasharray="8 6" opacity="0.85" />')
    # Truss cross-bracing bays
    truss_braces = []
    for tx in range(260, 900, 24):
        truss_braces.append(f"M{tx},226 L{tx + 12},238 M{tx + 12},226 L{tx},238")
    body.append(f'<path d="{" ".join(truss_braces)}" stroke="#466570" stroke-width="1.0" opacity="0.75" />')

    # Port & Starboard Thermal Control Radiators (Deployable Heat Rejection Panels)
    # Port Radiator (Left)
    body.append(f"""<!-- Port Thermal Radiators -->
    <g transform="translate(365, 172)">
        <rect x="0" y="0" width="56" height="42" rx="2" fill="url(#sr-radiator)" stroke="#527882" stroke-width="1.0" />
        <line x1="14" y1="0" x2="14" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="28" y1="0" x2="28" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="42" y1="0" x2="42" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="28" y1="42" x2="28" y2="54" stroke="#8faeb6" stroke-width="2.5" />
    </g>""")
    # Starboard Radiator (Right)
    body.append(f"""<!-- Starboard Thermal Radiators -->
    <g transform="translate(738, 250)">
        <rect x="0" y="0" width="56" height="42" rx="2" fill="url(#sr-radiator)" stroke="#527882" stroke-width="1.0" />
        <line x1="14" y1="0" x2="14" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="28" y1="0" x2="28" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="42" y1="0" x2="42" y2="42" stroke="#789ea8" stroke-width="0.8" />
        <line x1="28" y1="-12" x2="28" y2="0" stroke="#8faeb6" stroke-width="2.5" />
    </g>""")

    # Port Solar Array Wings (Left: 2 double wings)
    def solar_wing(x, y, w, h):
        # 3D Solar Array with realistic wafer texture & mast
        items = [
            f'<rect x="0" y="0" width="{w}" height="{h}" rx="2" fill="url(#sr-solar-wafer)" stroke="#8c6218" stroke-width="1.4" />',
            f'<rect x="0" y="0" width="{w}" height="{h}" rx="2" fill="url(#sr-solar-gold)" opacity="0.38" />',
        ]
        # Fine grid lines (photovoltaic cells)
        for gx in (w * 0.25, w * 0.5, w * 0.75):
            items.append(f'<line x1="{n(gx)}" y1="0" x2="{n(gx)}" y2="{h}" stroke="#ffcc66" stroke-width="0.7" opacity="0.65" />')
        for gy in range(8, int(h), 12):
            items.append(f'<line x1="0" y1="{gy}" x2="{w}" y2="{gy}" stroke="#ffcc66" stroke-width="0.6" opacity="0.45" />')
        # Central deployer mast spine
        items.append(f'<line x1="{w / 2}" y1="0" x2="{w / 2}" y2="{h}" stroke="#ffffff" stroke-width="1.2" opacity="0.8" />')
        return g(items, transform=f"translate({x}, {y})", class_="pulse-glow")

    body.append(f'<!-- Port Solar Array Wings (Left) -->')
    body.append(solar_wing(150, 136, 80, 84))
    body.append(solar_wing(150, 244, 80, 84))
    # Gimbal mounting & mast connecting to truss
    body.append(f'<rect x="228" y="228" width="24" height="8" rx="1" fill="#cbe0dc" stroke="#486872" stroke-width="1" />')
    body.append(f'<circle cx="240" cy="232" r="5" fill="#f5c46e" />')

    # Starboard Solar Array Wings (Right: 2 double wings)
    body.append(f'<!-- Starboard Solar Array Wings (Right) -->')
    body.append(solar_wing(930, 136, 80, 84))
    body.append(solar_wing(930, 244, 80, 84))
    # Gimbal mounting & mast connecting to truss
    body.append(f'<rect x="908" y="228" width="24" height="8" rx="1" fill="#cbe0dc" stroke="#486872" stroke-width="1" />')
    body.append(f'<circle cx="920" cy="232" r="5" fill="#f5c46e" />')

    # Central Rotating Artificial-Gravity Ring Complex (x=580, y=232)
    ring_svg = f"""<!-- Central Artificial-Gravity Rotating Torus Ring -->
    <g transform="translate(580, 232)">
        <g class="spin-rev">
            <!-- Outer Torus Shadow Ring -->
            <circle cx="0" cy="0" r="92" fill="none" stroke="#16383c" stroke-width="22" opacity="0.5" />
            <!-- Main Pressurized Torus Hull -->
            <circle cx="0" cy="0" r="92" fill="none" stroke="#dff0ec" stroke-width="16" />
            <!-- Outer & Inner Hull Armor Ribs -->
            <circle cx="0" cy="0" r="100.5" fill="none" stroke="#f5c46e" stroke-width="1.5" />
            <circle cx="0" cy="0" r="83.5" fill="none" stroke="#6BA4D9" stroke-width="1.5" />
            <!-- Segmented Torus Modules with Expansion Joints -->
            <circle cx="0" cy="0" r="92" fill="none" stroke="#003366" stroke-width="16" stroke-dasharray="2 18" opacity="0.6" />
            <!-- Torus Observation Windows (Illuminated Cyan) -->
            <circle cx="0" cy="0" r="92" fill="none" stroke="#42d0f5" stroke-width="3" stroke-dasharray="10 10" opacity="0.85" />
            
            <!-- 8 Pressurized Transit Spokes connecting to Central Spindle Hub -->
            <line x1="0" y1="-92" x2="0" y2="92" stroke="#b4d6d0" stroke-width="3.5" />
            <line x1="-92" y1="0" x2="92" y2="0" stroke="#b4d6d0" stroke-width="3.5" />
            <line x1="-65" y1="-65" x2="65" y2="65" stroke="#90b8b2" stroke-width="2.5" />
            <line x1="-65" y1="65" x2="65" y2="-65" stroke="#90b8b2" stroke-width="2.5" />

            <!-- Elevator Transit Cars & Peripheral Pods -->
            <rect x="-5" y="-97" width="10" height="10" rx="2" fill="#ffffff" stroke="#003366" stroke-width="1.5" />
            <rect x="-5" y="87" width="10" height="10" rx="2" fill="#ffffff" stroke="#003366" stroke-width="1.5" />
            <rect x="-97" y="-5" width="10" height="10" rx="2" fill="#ffffff" stroke="#003366" stroke-width="1.5" />
            <rect x="87" y="-5" width="10" height="10" rx="2" fill="#ffffff" stroke="#003366" stroke-width="1.5" />
            <circle cx="0" cy="-92" r="2.5" fill="#2ecc71" />
            <circle cx="0" cy="92" r="2.5" fill="#2ecc71" />
            <circle cx="-92" cy="0" r="2.5" fill="#2ecc71" />
            <circle cx="92" cy="0" r="2.5" fill="#2ecc71" />
        </g>
        
        <!-- Non-Rotating Central Spindle & Docking Node Hub -->
        <circle cx="0" cy="0" r="34" fill="url(#sr-hull-cyl)" stroke="#003366" stroke-width="2.5" />
        <circle cx="0" cy="0" r="24" fill="#031d36" stroke="#6BA4D9" stroke-width="1.8" />
        <circle cx="0" cy="0" r="10" fill="#f5c46e" />
        <!-- Optical Docking Crosshairs -->
        <line x1="-18" y1="0" x2="-6" y2="0" stroke="#6BA4D9" stroke-width="1.5" />
        <line x1="6" y1="0" x2="18" y2="0" stroke="#6BA4D9" stroke-width="1.5" />
        <line x1="0" y1="-18" x2="0" y2="-6" stroke="#6BA4D9" stroke-width="1.5" />
        <line x1="0" y1="6" x2="0" y2="18" stroke="#6BA4D9" stroke-width="1.5" />
    </g>"""
    body.append(ring_svg)

    # Pressurized Laboratory & Habitation Modules (Left & Right of Hub)
    # Left Module Stack (Destiny / Columbus style, x=420..525)
    body.append(f"""<!-- Port Primary Research Laboratory Stack -->
    <g transform="translate(420, 216)">
        <rect x="0" y="0" width="100" height="32" rx="6" fill="url(#sr-hull-cyl)" stroke="#003366" stroke-width="1.6" />
        <!-- Hull insulation seams & micrometeoroid armor plates -->
        <line x1="25" y1="0" x2="25" y2="32" stroke="#003366" stroke-width="1.2" />
        <line x1="50" y1="0" x2="50" y2="32" stroke="#003366" stroke-width="1.2" />
        <line x1="75" y1="0" x2="75" y2="32" stroke="#003366" stroke-width="1.2" />
        <!-- Yellow EVA Grab Handrails -->
        <line x1="8" y1="5" x2="92" y2="5" stroke="#f5c46e" stroke-width="1.0" />
        <line x1="8" y1="27" x2="92" y2="27" stroke="#f5c46e" stroke-width="1.0" />
        <!-- Panoramic Viewing Windows -->
        <circle cx="37" cy="16" r="3.2" fill="#42d0f5" stroke="#003366" stroke-width="0.8" />
        <circle cx="63" cy="16" r="3.2" fill="#42d0f5" stroke="#003366" stroke-width="0.8" />
    </g>""")

    # Right Module Stack (Kibo / Service Module style, x=640..745)
    body.append(f"""<!-- Starboard Habitation and Engineering Stack -->
    <g transform="translate(640, 216)">
        <rect x="0" y="0" width="100" height="32" rx="6" fill="url(#sr-hull-cyl)" stroke="#003366" stroke-width="1.6" />
        <line x1="25" y1="0" x2="25" y2="32" stroke="#003366" stroke-width="1.2" />
        <line x1="50" y1="0" x2="50" y2="32" stroke="#003366" stroke-width="1.2" />
        <line x1="75" y1="0" x2="75" y2="32" stroke="#003366" stroke-width="1.2" />
        <!-- Yellow EVA Grab Handrails -->
        <line x1="8" y1="5" x2="92" y2="5" stroke="#f5c46e" stroke-width="1.0" />
        <line x1="8" y1="27" x2="92" y2="27" stroke="#f5c46e" stroke-width="1.0" />
        <!-- External Exposed Experiment Facility (JEM-EF) Platform -->
        <rect x="70" y="32" width="26" height="12" fill="#607d8b" stroke="#003366" stroke-width="1.0" />
        <rect x="74" y="34" width="7" height="8" fill="#ffd54f" />
        <rect x="85" y="34" width="7" height="8" fill="#81d4fa" />
    </g>""")

    # Articulated Canadian-style Robotic Manipulator Arm (SSRMS / Canadarm)
    body.append(f"""<!-- Articulated Robotic Manipulator Arm (SSRMS) -->
    <g transform="translate(485, 216)">
        <!-- Mobile base cart on truss -->
        <rect x="-8" y="-7" width="16" height="7" rx="1.5" fill="#78909c" stroke="#37474f" stroke-width="0.9" />
        <!-- Shoulder, elbow, & boom links -->
        <path d="M0,-7 L-18,-28 L-42,-18 L-65,-36" fill="none" stroke="#cfd8dc" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />
        <path d="M0,-7 L-18,-28 L-42,-18 L-65,-36" fill="none" stroke="#263238" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" />
        <!-- Rotary joints -->
        <circle cx="0" cy="-7" r="3.5" fill="#f5c46e" stroke="#37474f" stroke-width="0.8" />
        <circle cx="-18" cy="-28" r="3.2" fill="#f5c46e" stroke="#37474f" stroke-width="0.8" />
        <circle cx="-42" cy="-18" r="3.2" fill="#f5c46e" stroke="#37474f" stroke-width="0.8" />
        <!-- Latching End Effector (LEE) inspecting external module -->
        <circle cx="-65" cy="-36" r="3.8" fill="#ffffff" stroke="#c95a41" stroke-width="1.2" />
        <line x1="-65" y1="-36" x2="-72" y2="-42" stroke="#42d0f5" stroke-width="1.2" />
    </g>""")

    # Docked Vehicles:
    # 1. Docked Explorer Spaceplane (Left axial port, x=375, y=232)
    body.append(f"""<!-- Docked Crew Transport Spaceplane -->
    <g transform="translate(378, 232)">
        <!-- Pressurized Docking Adaptor Tunnel -->
        <rect x="30" y="-7" width="12" height="14" rx="2" fill="#90a4ae" stroke="#37474f" stroke-width="1.0" />
        <!-- Aerodynamic Lifting Body Fuselage -->
        <path d="M-4,-12 L30,-5 L30,5 L-4,12 L-10,0Z" fill="#ffffff" stroke="#003366" stroke-width="1.4" />
        <!-- Thermal Protection Black Underside / Tiles -->
        <path d="M-4,0 L30,2 L30,5 L-4,12 L-10,0Z" fill="#212121" opacity="0.65" />
        <!-- Cantilevering Delta Wings with Crimson WSA Wingtips -->
        <polygon points="10,-5 30,-22 30,-5" fill="#c95a41" />
        <polygon points="10,5 30,22 30,5" fill="#c95a41" />
        <!-- Cockpit Glass Canopy -->
        <ellipse cx="6" cy="0" r="3.2" rx="4.5" ry="2.2" fill="#42d0f5" />
    </g>""")

    # 2. Docked Commercial Cargo Capsule (Right radial port, x=690, y=260)
    body.append(f"""<!-- Docked Autonomous Cargo Capsule (Dragon / Cygnus style) -->
    <g transform="translate(690, 248)">
        <!-- Berthed docking collar -->
        <rect x="-6" y="0" width="12" height="8" fill="#90a4ae" stroke="#37474f" stroke-width="0.9" />
        <!-- Conical capsule trunk -->
        <path d="M-12,8 L12,8 L16,28 L-16,28Z" fill="#ffffff" stroke="#003366" stroke-width="1.3" />
        <line x1="-12" y1="18" x2="12" y2="18" stroke="#003366" stroke-width="1.0" />
        <!-- Miniature solar arrays on cargo trunk -->
        <rect x="-32" y="16" width="16" height="10" fill="#1a3b68" stroke="#ffc107" stroke-width="0.8" />
        <rect x="16" y="16" width="16" height="10" fill="#1a3b68" stroke="#ffc107" stroke-width="0.8" />
    </g>""")

    # High-Gain Telemetry Antenna with animated transmission pulses (x=580, y=105)
    body.append(f"""<!-- High-Gain Deep Space Telemetry Antenna -->
    <g transform="translate(580, 105)">
        <line x1="0" y1="40" x2="0" y2="14" stroke="#b0bec5" stroke-width="2.5" />
        <!-- Parabolic dish reflector with 3D gradient -->
        <path d="M-22,8 C-12,-8 12,-8 22,8" fill="none" stroke="#f5c46e" stroke-width="3.2" stroke-linecap="round" />
        <line x1="0" y1="14" x2="0" y2="-4" stroke="#ffffff" stroke-width="1.8" />
        <circle cx="0" cy="-4" r="2.5" fill="#f5c46e" />
        <!-- Pulsing radar/telemetry waves -->
        <circle class="pulse" cx="0" cy="-6" r="14" fill="none" stroke="#6BA4D9" stroke-width="1.8" />
        <circle class="pulse" cx="0" cy="-6" r="28" fill="none" stroke="#6BA4D9" stroke-width="1.2" style="animation-delay: 1.2s;" />
    </g>""")

    # 6. TOP HUD TELEMETRY BAR
    hud_bar = f"""<!-- TOP HUD TELEMETRY BAR -->
    <g font-family="Manrope, sans-serif" font-size="11" font-weight="700" letter-spacing="1.5">
        <rect x="330" y="18" width="500" height="32" rx="16" fill="#04121a" stroke="#6BA4D9" stroke-width="1.2" opacity="0.95" />
        <text x="355" y="38" fill="#6BA4D9">{hud_alt}</text>
        <text x="520" y="38" fill="#f5c46e">{hud_vel}</text>
        <text x="680" y="38" fill="#2ecc71">{hud_crew}</text>
    </g>"""
    body.append(hud_bar)

    # 7. Corner Badges
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
    return f"""                <svg class="ill" viewBox="0 0 1160 520" role="img" aria-label="{aria_label}">
{defs}
                    <g clip-path="url(#{clip_id})">
{inner_content}
                    </g>
                </svg>"""


# ==============================================================================
# 2. EARTH-MOON-MARS INTERPLANETARY CORRIDOR SVG (1160 x 480)
# ==============================================================================
def build_lunar_mars_svg(lang="en"):
    clip_id = "sr-clip2" if lang == "en" else "sr-hu-clip2"

    if lang == "hu":
        aria_label = "Föld, Hold és Mars bolygóközi közlekedési folyosók térképe"
        hud_header = "HOLDBÁZIS ÉS MARSI BOLYGÓKÖZI FOLYOSÓ"
        lbl_earth_title = "FÖLD"
        lbl_earth_sub = "ELSŐDLEGES BÁZIS"
        lbl_moon_title = "HOLD-KÜLDETÉS"
        lbl_moon_sub = "2026-2030"
        lbl_mars_title = "MARS-KÜLDETÉS"
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

    defs = f"""                    <defs>
                        <clipPath id="{clip_id}">
                            <rect width="1160" height="480" />
                        </clipPath>
                        <radialGradient id="sr-deep-space" cx="50%" cy="40%" r="65%">
                            <stop offset="0%" stop-color="#0a1d28" />
                            <stop offset="45%" stop-color="#051018" />
                            <stop offset="85%" stop-color="#02080e" />
                            <stop offset="100%" stop-color="#010408" />
                        </radialGradient>
                        <radialGradient id="sr-earth-3d" cx="35%" cy="30%" r="70%">
                            <stop offset="0%" stop-color="#80d0ff" />
                            <stop offset="35%" stop-color="#1e70c8" />
                            <stop offset="75%" stop-color="#0a3275" />
                            <stop offset="100%" stop-color="#021438" />
                        </radialGradient>
                        <radialGradient id="sr-moon-3d" cx="35%" cy="30%" r="70%">
                            <stop offset="0%" stop-color="#f2f8f8" />
                            <stop offset="40%" stop-color="#cbd8d8" />
                            <stop offset="75%" stop-color="#7c9292" />
                            <stop offset="100%" stop-color="#3c4c4c" />
                        </radialGradient>
                        <radialGradient id="sr-mars-3d" cx="35%" cy="30%" r="70%">
                            <stop offset="0%" stop-color="#f89078" />
                            <stop offset="35%" stop-color="#d6583e" />
                            <stop offset="75%" stop-color="#8a2a16" />
                            <stop offset="100%" stop-color="#420f05" />
                        </radialGradient>
                        <filter id="sr-planet-glow" x="-20%" y="-20%" width="140%" height="140%">
                            <feGaussianBlur stdDeviation="4" result="blur" />
                            <feComposite in="SourceGraphic" in2="blur" operator="over" />
                        </filter>
                    </defs>"""

    body = []
    # 1. Deep Space Field
    body.append(f'<rect width="1160" height="480" fill="url(#sr-deep-space)" />')

    # Faint Interplanetary Astrodynamics Grid (Heliocentric Reference Planes)
    grid_lines = []
    for y_g in (120, 240, 360):
        grid_lines.append(f'<line x1="40" y1="{y_g}" x2="1120" y2="{y_g}" stroke="#1e405a" stroke-width="0.8" stroke-dasharray="4 8" opacity="0.35" />')
    for x_g in (180, 540, 960):
        grid_lines.append(f'<line x1="{x_g}" y1="40" x2="{x_g}" y2="440" stroke="#1e405a" stroke-width="0.8" stroke-dasharray="4 8" opacity="0.35" />')
    body.append(f'<g>\n' + "\n".join(grid_lines) + "\n</g>")

    # Distant Starfield
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
    for _ in range(70):
        fx = rng.uniform(20, 1140)
        fy = rng.uniform(20, 460)
        fr = rng.uniform(0.6, 1.0)
        faint_stars.append(f'<circle cx="{n(fx)}" cy="{n(fy)}" r="{n(fr)}" />')
    body.append(f'<g fill="#ffffff" opacity="0.6">\n' + "\n".join(faint_stars) + "\n</g>")
    body.append(f'<g>\n' + "\n".join(stars) + "\n</g>")

    # 2. Interplanetary Transfer Trajectory Paths (SVG animation targets)
    # Earth-to-Moon Orbit Corridor
    path_moon_id = "sr-path-moon" if lang == "en" else "sr-hu-path-moon"
    path_mars_id = "sr-path-mars" if lang == "en" else "sr-hu-path-mars"

    body.append(f'<!-- Interplanetary Transfer Trajectories -->')
    # Earth to Moon TLI Corridor
    body.append(f'<path id="{path_moon_id}" d="M180,240 C300,130 440,140 540,190" fill="none" stroke="#f5c46e" stroke-width="2.5" stroke-dasharray="8 6" class="dash" />')
    # Earth to Mars Hohmann Transfer Arc
    body.append(f'<path id="{path_mars_id}" d="M180,240 C420,35 780,35 960,240" fill="none" stroke="#e3735a" stroke-width="2.6" stroke-dasharray="10 8" class="dash" />')
    # Moon to Mars Deep Relay Line
    body.append(f'<path d="M540,190 C680,175 840,195 960,240" fill="none" stroke="#6BA4D9" stroke-width="1.6" stroke-dasharray="4 6" opacity="0.65" />')

    # Gravitational Halo Orbits / Lagrange Point Indicators
    # Earth-Moon L1 & L2 points
    body.append(f'<circle cx="430" cy="205" r="7" fill="none" stroke="#f5c46e" stroke-width="1" stroke-dasharray="2 3" opacity="0.7" />')
    body.append(f'<circle cx="430" cy="205" r="2" fill="#f5c46e" opacity="0.85" />')
    body.append(f'<text x="430" y="222" fill="#f5c46e" font-family="Manrope, sans-serif" font-size="9" font-weight="600" text-anchor="middle" opacity="0.8">L1</text>')

    # 3. PLANET EARTH NODE (x=180, y=240, r=64)
    earth_group = f"""<!-- 1. PLANET EARTH NODE -->
    <g transform="translate(180, 240)">
        <!-- Orbital Coordinate Tracking Rings -->
        <circle cx="0" cy="0" r="76" fill="none" stroke="#6BA4D9" stroke-width="1.4" stroke-dasharray="6 4" class="spin" />
        <!-- Earth 3D Sphere -->
        <circle cx="0" cy="0" r="62" fill="url(#sr-earth-3d)" />
        <!-- Atmospheric Scattering Limb Glow -->
        <circle cx="0" cy="0" r="62" fill="none" stroke="#6BA4D9" stroke-width="7" opacity="0.38" />
        <circle cx="0" cy="0" r="62" fill="none" stroke="#e0f8ff" stroke-width="1.8" opacity="0.9" />
        <!-- Realistic Continents (Americas & Pacific Basin) -->
        <path d="M-28,-32 C-15,-42 12,-35 22,-20 C28,-8 18,12 2,24 C-12,32 -26,18 -32,-4Z" fill="#328254" opacity="0.85" />
        <path d="M-6,8 C14,12 24,32 12,42 C0,48 -14,36 -8,18Z" fill="#328254" opacity="0.85" />
        <!-- Swirling Cloud Systems -->
        <path d="M-36,-14 C-18,-24 16,-18 34,-6 C42,-2 32,4 18,2 C-4,-2 -24,8 -38,2Z" fill="#ffffff" opacity="0.75" />
        <path d="M-22,18 C-8,12 18,22 32,32 C24,36 4,28 -14,30Z" fill="#ffffff" opacity="0.75" />
        <!-- WNSS Station LEO Orbit Ring -->
        <circle cx="0" cy="0" r="84" fill="none" stroke="#f5c46e" stroke-width="1.1" stroke-dasharray="4 4" />
        <circle cx="59" cy="-60" r="4.5" fill="#ffffff" stroke="#003366" stroke-width="1.3" />
        <text x="0" y="106" fill="#fbf7f0" font-family="Manrope, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1.5">{lbl_earth_title}</text>
        <text x="0" y="123" fill="#6BA4D9" font-family="Manrope, sans-serif" font-size="10" font-weight="600" text-anchor="middle">{lbl_earth_sub}</text>
    </g>"""
    body.append(earth_group)

    # 4. MOON NODE & LUNAR BASE (x=540, y=190, r=36)
    moon_group = f"""<!-- 2. MOON NODE AND LUNAR BASE -->
    <g transform="translate(540, 190)">
        <!-- Near-Rectilinear Halo Orbit Ring -->
        <circle cx="0" cy="0" r="46" fill="none" stroke="#d5ede9" stroke-width="1.1" stroke-dasharray="4 4" class="spin-rev" />
        <!-- Moon 3D Sphere -->
        <circle cx="0" cy="0" r="35" fill="url(#sr-moon-3d)" />
        <circle cx="0" cy="0" r="35" fill="none" stroke="#e8f4f4" stroke-width="1.2" opacity="0.7" />
        <!-- Lunar Maria Basalt Plains (Mare Tranquillitatis, Oceanus Procellarum) -->
        <ellipse cx="-12" cy="-9" rx="8" ry="6" fill="#586c6c" opacity="0.65" />
        <ellipse cx="11" cy="7" rx="10" ry="8" fill="#586c6c" opacity="0.55" />
        <ellipse cx="-6" cy="15" rx="6" ry="4.5" fill="#586c6c" opacity="0.65" />
        <!-- Tycho / Copernicus Impact Crater Ray System -->
        <circle cx="-14" cy="12" r="2.2" fill="#ffffff" opacity="0.85" />
        <line x1="-14" y1="12" x2="-26" y2="4" stroke="#ffffff" stroke-width="0.6" opacity="0.6" />
        <line x1="-14" y1="12" x2="-8" y2="24" stroke="#ffffff" stroke-width="0.6" opacity="0.6" />
        <line x1="-14" y1="12" x2="-2" y2="10" stroke="#ffffff" stroke-width="0.6" opacity="0.6" />
        <!-- Planned Aitken Basin Landing Zone Beacon -->
        <circle cx="9" cy="-15" r="3.2" fill="#2ecc71" />
        <circle class="pulse" cx="9" cy="-15" r="13" fill="none" stroke="#2ecc71" stroke-width="1.6" />
        <text x="0" y="66" fill="#fbf7f0" font-family="Manrope, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1.5">{lbl_moon_title}</text>
        <text x="0" y="83" fill="#f5c46e" font-family="Manrope, sans-serif" font-size="10" font-weight="600" text-anchor="middle">{lbl_moon_sub}</text>
    </g>"""
    body.append(moon_group)

    # 5. MARS NODE & EXPEDITION CORRIDOR (x=960, y=240, r=60)
    mars_group = f"""<!-- 3. MARS NODE AND EXPEDITION TARGET -->
    <g transform="translate(960, 240)">
        <!-- Mars Orbital Tracking Rings -->
        <circle cx="0" cy="0" r="78" fill="none" stroke="#e3735a" stroke-width="1.4" stroke-dasharray="6 4" class="spin" />
        <!-- Mars 3D Sphere -->
        <circle cx="0" cy="0" r="60" fill="url(#sr-mars-3d)" />
        <!-- Thin Dusty Martian Atmosphere Limb Glow -->
        <circle cx="0" cy="0" r="60" fill="none" stroke="#e3735a" stroke-width="6" opacity="0.35" />
        <circle cx="0" cy="0" r="60" fill="none" stroke="#ffdcd3" stroke-width="1.6" opacity="0.85" />
        <!-- Martian Dark Surface Albedo & Valles Marineris Canyon Chasm -->
        <path d="M-36,2 C-18,-8 18,-4 38,12 C28,26 -4,28 -28,18Z" fill="#521508" opacity="0.65" />
        <path d="M-18,6 Q8,4 28,14" stroke="#2b0a04" stroke-width="2.2" fill="none" />
        <!-- Olympus Mons Shield Volcano & Tharsis Montes -->
        <ellipse cx="-24" cy="-14" rx="7" ry="5.5" fill="#752212" opacity="0.8" />
        <circle cx="-24" cy="-14" r="2.0" fill="#2b0a04" />
        <!-- North Polar Carbon-Dioxide Ice Cap -->
        <ellipse cx="-2" cy="-56" rx="14" ry="4.5" fill="#ffffff" opacity="0.95" />
        
        <!-- Mars Orbital Base Station (Forward Outpost) -->
        <g transform="translate(0, -78)">
            <circle cx="0" cy="0" r="6.5" fill="#ffffff" stroke="#c95a41" stroke-width="1.6" />
            <line x1="-15" y1="0" x2="15" y2="0" stroke="#f5c46e" stroke-width="2.2" />
            <circle class="pulse" cx="0" cy="0" r="14" fill="none" stroke="#e3735a" stroke-width="1.3" />
        </g>
        <!-- Spirit II Landing Site Marker -->
        <polygon points="-8,-12 0,-24 8,-12" fill="#f5c46e" />
        <circle cx="0" cy="-14" r="2" fill="#003366" />
        <text x="0" y="106" fill="#fbf7f0" font-family="Manrope, sans-serif" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1.5">{lbl_mars_title}</text>
        <text x="0" y="123" fill="#e3735a" font-family="Manrope, sans-serif" font-size="10" font-weight="600" text-anchor="middle">{lbl_mars_sub}</text>
    </g>"""
    body.append(mars_group)

    # 6. Interplanetary Ships in Transit:
    # 1. Mars Interplanetary Starship (Cruising along #sr-path-mars)
    mars_ship = f"""<!-- Interplanetary Starship (Mars Cycler) -->
    <g>
        <path d="M-16,-6 L8,-6 L18,0 L8,6 L-16,6 L-12,0Z" fill="#ffffff" stroke="#c95a41" stroke-width="1.3" />
        <!-- Nuclear-thermal / Ion Engine Glow -->
        <polygon points="-16,-6 -24,-12 -10,-6" fill="#f5c46e" />
        <polygon points="-16,6 -24,12 -10,6" fill="#f5c46e" />
        <!-- Radiator wings -->
        <rect x="-6" y="-12" width="12" height="4" fill="#64b5f6" />
        <rect x="-6" y="8" width="12" height="4" fill="#64b5f6" />
        <circle cx="8" cy="0" r="3" fill="#2ecc71" />
        <animateMotion dur="14s" repeatCount="indefinite" rotate="auto">
            <mpath href="#{path_mars_id}" />
        </animateMotion>
    </g>"""
    body.append(mars_ship)

    # 2. Cislunar Crew Transfer Vessel (Cruising along #sr-path-moon)
    moon_ship = f"""<!-- Cislunar Crew Transport Vessel -->
    <g>
        <polygon points="12,0 -9,-8 -5,0 -9,8" fill="#ffffff" stroke="#003366" stroke-width="1.2" />
        <rect x="-7" y="-3" width="6" height="6" fill="#ffd54f" />
        <animateMotion dur="9s" repeatCount="indefinite" rotate="auto">
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
    return f"""                <svg class="ill" viewBox="0 0 1160 480" role="img" aria-label="{aria_label}">
{defs}
                    <g clip-path="url(#{clip_id})">
{inner_content}
                    </g>
                </svg>"""


# ==============================================================================
# INJECTION INTO HTML
# ==============================================================================
def update_space_page(file_path, lang="en"):
    content = file_path.read_text(encoding="utf-8")

    # Replace SVG in #station section: <div class="ill-panel">\s*<svg ...</svg>\s*<div class="ill-caption">
    station_svg = build_station_svg(lang)
    station_pattern = re.compile(r'(<section id="station"[^>]*>.*?<div class="ill-panel">\s*)<svg.*?</svg>(\s*<div class="ill-caption">)', re.DOTALL)
    if not station_pattern.search(content):
        raise ValueError(f"Could not find #station SVG pattern in {file_path}")
    content = station_pattern.sub(r'\1' + station_svg.strip() + r'\2', content)

    # Replace SVG in #lunar-mars section
    lunar_mars_svg = build_lunar_mars_svg(lang)
    lunar_pattern = re.compile(r'(<section id="lunar-mars"[^>]*>.*?<div class="ill-panel">\s*)<svg.*?</svg>(\s*<div class="ill-caption">)', re.DOTALL)
    if not lunar_pattern.search(content):
        raise ValueError(f"Could not find #lunar-mars SVG pattern in {file_path}")
    content = lunar_pattern.sub(r'\1' + lunar_mars_svg.strip() + r'\2', content)

    file_path.write_text(content, encoding="utf-8")
    print(f"Updated {file_path.relative_to(ROOT)}")


def main():
    en_file = ROOT / "en" / "space-research.html"
    hu_file = ROOT / "hu" / "space-research.html"
    update_space_page(en_file, "en")
    update_space_page(hu_file, "hu")
    print("Space research SVGs successfully updated!")


if __name__ == "__main__":
    main()
