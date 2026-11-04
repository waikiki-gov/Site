import re
import xml.etree.ElementTree as ET
import sys
import os
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# ==============================================================================
# CONST ARRAY OF CITIES
# Position (x, y px), Name, Type ('Capital', 'Large', 'Small')
# ==============================================================================
CITIES = [
    {
        "name": "Nova Aurelia",
        "pos": (412, 330),
        "type": "Capital",
        "label": {"anchor": "middle", "offset": (0, 30), "size": 14, "weight": 700}
    },
    {
        "name": "Miami",
        "pos": (451, 105),
        "type": "Large",
        "label": {"anchor": "start", "offset": (15, 0), "size": 12, "weight": 600}
    },
    {
        "name": "Key West",
        "pos": (412, 160),
        "type": "Small",
        "label": {"anchor": "end", "offset": (-10, 5), "size": 10, "weight": 400}
    },
    {
        "name": "Havana",
        "pos": (396, 260),
        "type": "Large",
        "label": {"anchor": "end", "offset": (-10, -10), "size": 12, "weight": 600}
    },
    {
        "name": "Mega Pyramid City",
        "pos": (446, 294),
        "type": "Small",
        "has_pyramid": True,
        "label": {"anchor": "start", "offset": (15, -5), "size": 10, "weight": 400}
    },
    {
        "name": "Morón",
        "pos": (658, 348),
        "type": "Large",
        "label": {"anchor": "middle", "offset": (0, -15), "size": 12, "weight": 600}
    },
    {
        "name": "Port Royal",
        "pos": (742, 397),
        "type": "Small",
        "label": {"anchor": "start", "offset": (15, -5), "size": 10, "weight": 400}
    },
    {
        "name": "Santiago",
        "pos": (824, 508),
        "type": "Large",
        "label": {"anchor": "end", "offset": (-15, 15), "size": 12, "weight": 600}
    },
    {
        "name": "Carib City",
        "pos": (980, 510),
        "type": "Small",
        "label": {"anchor": "middle", "offset": (0, -20), "size": 10, "weight": 400}
    },
    {
        "name": "Blue Bay",
        "pos": (1000, 540),
        "type": "Small",
        "label": {"anchor": "middle", "offset": (0, 20), "size": 10, "weight": 400}
    },
    {
        "name": "Cap-Haïtien",
        "pos": (1123, 448),
        "type": "Large",
        "label": {"anchor": "middle", "offset": (0, -15), "size": 12, "weight": 600}
    },
    {
        "name": "Port-au-Prince",
        "pos": (1115, 540),
        "type": "Large",
        "label": {"anchor": "middle", "offset": (0, 25), "size": 12, "weight": 600}
    },
    {
        "name": "Kingston",
        "pos": (860, 605),
        "type": "Large",
        "label": {"anchor": "start", "offset": (15, 15), "size": 12, "weight": 600}
    },
    {
        "name": "Montego Bay",
        "pos": (786, 578),
        "type": "Small",
        "label": {"anchor": "end", "offset": (-10, -5), "size": 10, "weight": 400}
    },
    {
        "name": "Pinar del Río",
        "pos": (220, 310),
        "type": "Small",
        "label": {"anchor": "end", "offset": (-10, 0), "size": 10, "weight": 400}
    },
    {
        "name": "Santo Domingo",
        "pos": (1304, 540),
        "type": "Large",
        "label": {"anchor": "middle", "offset": (0, 25), "size": 12, "weight": 600}
    },
    {
        "name": "Punta Cana",
        "pos": (1410, 532),
        "type": "Small",
        "label": {"anchor": "middle", "offset": (0, -14), "size": 10, "weight": 400}
    },
    {
        "name": "Santa Cruz del Sur",
        "pos": (634, 448),
        "type": "Small",
        "label": {"anchor": "middle", "offset": (0, 20), "size": 10, "weight": 400}
    }
]

# ==============================================================================
# CONST ARRAY OF CONNECTIONS
# From, To, Type ('Maglev', 'Hyperloop', 'Tunnel', 'Main Line', 'Maritime', 'Elevated')
# ==============================================================================
CONNECTIONS = [
    {
        "from": "Morón",
        "to": "Santa Cruz del Sur",
        "type": "Main Line",
        "bend": 0.05,
        "dur": "3.0s"
    },
    {
        "from": "Havana",
        "to": "Pinar del Río",
        "type": "Main Line",
        "bend": -0.1,
        "dur": "3.5s"
    },
    {
        "from": "Port-au-Prince",
        "to": "Santo Domingo",
        "type": "Main Line",
        "bend": 0.05,
        "dur": "3.5s"
    },
    {
        "from": "Santo Domingo",
        "to": "Punta Cana",
        "type": "Main Line",
        "bend": 0.05,
        "dur": "2.2s"
    },
    {
        "from": "Miami",
        "to": "Key West",
        "type": "Tunnel",
        "bend": 0.15,
        "dur": "2.5s"
    },
    {
        "from": "Key West",
        "to": "Havana",
        "type": "Tunnel",
        "bend": 0.1,
        "dur": "4.0s"
    },
    {
        "from": "Havana",
        "to": "Nova Aurelia",
        "type": "Main Line",
        "bend": -0.1,
        "dur": "2.5s"
    },
    {
        "from": "Nova Aurelia",
        "to": "Morón",
        "type": "Maglev",
        "bend": 0.08,
        "dur": "4.5s"
    },
    {
        "from": "Nova Aurelia",
        "to": "Mega Pyramid City",
        "type": "Hyperloop",
        "bend": 0.0,
        "dur": "1.8s"
    },
    {
        "from": "Morón",
        "to": "Port Royal",
        "type": "Maglev",
        "bend": -0.1,
        "dur": "2.2s"
    },
    {
        "from": "Port Royal",
        "to": "Santiago",
        "type": "Maglev",
        "bend": 0.04,
        "dur": "2.0s"
    },
    {
        "from": "Santiago",
        "to": "Carib City",
        "type": "Maglev",
        "bend": -0.08,
        "dur": "5.5s"
    },
    {
        "from": "Carib City",
        "to": "Blue Bay",
        "type": "Tunnel",
        "bend": -0.08,
        "dur": "0.5s"
    },
    {
        "from": "Blue Bay",
        "to": "Port-au-Prince",
        "type": "Maglev",
        "bend": -0.08,
        "dur": "5.5s"
    },
    {
        "from": "Port-au-Prince",
        "to": "Cap-Haïtien",
        "type": "Main Line",
        "bend": -0.8,
        "dur": "3.6s"
    },
    {
        "from": "Santiago",
        "to": "Kingston",
        "type": "Maritime",
        "bend": -0.06,
        "animated": False
    },
    {
        "from": "Kingston",
        "to": "Blue Bay",
        "type": "Maritime",
        "bend": -0.2,
        "animated": False
    },
    {
        "from": "Nova Aurelia",
        "to": "Montego Bay",
        "type": "Maritime",
        "bend": -0.15,
        "animated": False
    }
]

CITY_BY_NAME = {c["name"].upper(): c for c in CITIES}

def get_city_pos(name_or_point):
    """Returns (x, y) coordinates for a city name or a direct (x, y) tuple."""
    if isinstance(name_or_point, (tuple, list)):
        return name_or_point
    key = str(name_or_point).upper()
    if key in CITY_BY_NAME:
        return CITY_BY_NAME[key]["pos"]
    raise KeyError(f"City '{name_or_point}' not found in CITIES")

def get_connection_style(conn_type):
    """Returns the SVG styling attributes and animation parameters for each connection type."""
    t = conn_type.strip().lower()
    if "maglev" in t:
        return {
            "attrs": 'class="k-coral" stroke-width="5.5" stroke-linecap="round"',
            "dot_r": 5.0,
            "default_dur": "4.5s"
        }
    elif "hyperloop" in t:
        return {
            "attrs": 'class="k-gold" stroke-width="5.5" stroke-linecap="round"',
            "dot_r": 4.0,
            "default_dur": "1.8s"
        }
    elif "tunnel" in t:
        return {
            "attrs": 'class="k-ink" stroke-width="4.5" stroke-dasharray="2 7" stroke-linecap="round"',
            "dot_r": 4.5,
            "default_dur": "2.5s"
        }
    elif "main" in t:
        return {
            "attrs": 'class="k-ink2" stroke-width="4.5" stroke-linecap="round"',
            "dot_r": 5.0,
            "default_dur": "4.0s"
        }
    elif "maritime" in t or "sea" in t:
        return {
            "attrs": 'class="k-sea" stroke-width="3.5" stroke-dasharray="6 4" stroke-linecap="round"',
            "dot_r": 4.0,
            "default_dur": "6.0s"
        }
    elif "elevated" in t:
        return {
            "attrs": 'class="k-ink2" stroke-width="2.8" stroke-dasharray="4 4" stroke-linecap="round"',
            "dot_r": 0,
            "default_dur": "4.0s"
        }
    else:
        return {
            "attrs": 'class="k-ink" stroke-width="3.5" stroke-linecap="round"',
            "dot_r": 4.0,
            "default_dur": "4.0s"
        }

def make_curved_path(p1, p2, bend=0.0):
    """
    Dynamically generates an SVG path (straight or cubic Bezier) between two positions.
    bend: relative deflection perpendicular to travel direction.
    Positive deflects to the right, negative deflects to the left.
    """
    x1, y1 = get_city_pos(p1)
    x2, y2 = get_city_pos(p2)
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)

    if dist < 1e-4 or abs(bend) < 1e-4:
        return f"M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}"

    # Right-hand normal (dy/dist, -dx/dist)
    nx = dy / dist
    ny = -dx / dist
    offset = bend * dist

    cx1 = x1 + dx * 0.35 + nx * offset
    cy1 = y1 + dy * 0.35 + ny * offset
    cx2 = x1 + dx * 0.65 + nx * offset
    cy2 = y1 + dy * 0.65 + ny * offset

    return f"M{x1:.0f} {y1:.0f} C{cx1:.0f} {cy1:.0f}, {cx2:.0f} {cy2:.0f}, {x2:.0f} {y2:.0f}"

def merge_path_d(d_list):
    """Normalizes and combines multiple SVG path d strings into one compound path."""
    res = []
    for d in d_list:
        d = d.strip()
        if not d:
            continue
        # Convert initial relative moveto 'm X,Y' to absolute 'M X,Y l '
        # so multiple subpaths can be cleanly concatenated without offsetting each other
        d_norm = re.sub(r'^[mM]\s*([-\d.]+)[,\s]+([-\d.]+)\s*', r'M \1,\2 l ', d)
        res.append(d_norm)
    return ' '.join(res)

def get_cuba_group():
    tree = ET.parse('content/Maps/cuba.svg')
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    paths = tree.findall('.//svg:path', ns) or tree.findall('.//path')
    d_list = [p.attrib.get('d', '') for p in paths]
    merged_d = merge_path_d(d_list)
    return (
        '                        <!-- ==================== CUBA ARCHIPELAGO ==================== -->\n'
        '                        <g class="cuba-archipelago" transform="translate(90, 240) scale(1.15)">\n'
        f'                            <path class="f-sand province-path" vector-effect="non-scaling-stroke" d="{merged_d}" />\n'
        '                        </g>'
    )

def is_florida_county_visible(d, tx=88, ty=-157.4, scale=4.0, vw=1800, vh=650):
    tokens = re.findall(r'([a-zA-Z])|([-+]?(?:\d*\.\d+|\d+))', d)
    cmd = None
    cur_x, cur_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t[0]:
            cmd = t[0]; i += 1; continue
        if not cmd:
            i += 1; continue
        if cmd in ['m', 'M']:
            if cmd == 'm':
                cur_x += float(t[1]); i += 1
                cur_y += float(tokens[i][1]); i += 1
            else:
                cur_x = float(t[1]); i += 1
                cur_y += float(tokens[i][1]); i += 1
            start_x, start_y = cur_x, cur_y
            cmd = 'l' if cmd == 'm' else 'L'
        elif cmd == 'l':
            cur_x += float(t[1]); i += 1
            cur_y += float(tokens[i][1]); i += 1
        elif cmd == 'L':
            cur_x = float(t[1]); i += 1
            cur_y += float(tokens[i][1]); i += 1
        elif cmd == 'c':
            coords = [float(tokens[i+k][1]) for k in range(6)]
            i += 6
            cur_x += coords[4]
            cur_y += coords[5]
        elif cmd in ['z', 'Z']:
            cur_x, cur_y = start_x, start_y
        else:
            i += 1
        gx = tx + cur_x * scale
        gy = ty + cur_y * scale
        if gx < min_x: min_x = gx
        if gx > max_x: max_x = gx
        if gy < min_y: min_y = gy
        if gy > max_y: max_y = gy
    return max_x >= 0 and min_x <= vw and max_y >= 0 and min_y <= vh

def get_florida_group():
    tree = ET.parse('content/Maps/usa-fl.svg')
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    paths = tree.findall('.//svg:path', ns) or tree.findall('.//path')
    d_list = [
        p.attrib.get('d', '')
        for p in paths
        if is_florida_county_visible(p.attrib.get('d', ''))
    ]
    merged_d = merge_path_d(d_list)
    return (
        '                        <!-- ==================== FLORIDA ==================== -->\n'
        '                        <g transform="translate(88, -157.4) scale(4.0)">\n'
        f'                            <path class="f-sand florida-path" d="{merged_d}" />\n'
        '                        </g>'
    )

def get_jamaica_group():
    tree = ET.parse('content/Maps/jamaica.svg')
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    paths = tree.findall('.//svg:path', ns) or tree.findall('.//path')
    d_list = [p.attrib.get('d', '') for p in paths]
    merged_d = merge_path_d(d_list)
    return (
        '                        <!-- ==================== JAMAICA ==================== -->\n'
        '                        <g transform="translate(752.5, 566.3) scale(0.1915)">\n'
        f'                            <path class="f-sand province-path" vector-effect="non-scaling-stroke" d="{merged_d}" />\n'
        '                        </g>'
    )

def transform_path_d(d, tx=0.0, ty=0.0, sx=1.0, sy=1.0):
    """Transforms coordinates in an SVG path d string by translation and scaling."""
    tokens = re.findall(r'([a-zA-Z])|([-+]?(?:\d*\.\d+|\d+))', d)
    out = []
    cmd = None
    is_relative = False
    coord_idx = 0
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t[0]:
            cmd = t[0]
            out.append(cmd)
            is_relative = cmd.islower()
            coord_idx = 0
            i += 1
            continue
        num = float(t[1])
        if cmd in ['H', 'h']:
            new_num = (num * sx) if is_relative else (tx + num * sx)
        elif cmd in ['V', 'v']:
            new_num = (num * sy) if is_relative else (ty + num * sy)
        else:
            if coord_idx == 0:
                new_num = (num * sx) if is_relative else (tx + num * sx)
                coord_idx = 1
            else:
                new_num = (num * sy) if is_relative else (ty + num * sy)
                coord_idx = 0
        s = f'{new_num:.2f}'.rstrip('0').rstrip('.')
        if s == '-0' or s == '':
            s = '0'
        out.append(s)
        i += 1
    return ' '.join(out)

def get_hispaniola_group():
    tree_ht = ET.parse('content/Maps/haiti.svg')
    tree_do = ET.parse('content/Maps/dominican-republic.svg')
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    ht_paths = tree_ht.findall('.//svg:path', ns) or tree_ht.findall('.//path')
    ht_d = merge_path_d([p.attrib.get('d', '') for p in ht_paths])

    do_paths = tree_do.findall('.//svg:path', ns) or tree_do.findall('.//path')
    do_d = merge_path_d([p.attrib.get('d', '') for p in do_paths])
    do_d_transformed = transform_path_d(do_d, tx=670.97, ty=45.06, sx=1.25826, sy=1.26938)
    hispaniola_d = f"{ht_d} {do_d_transformed}"

    return (
        '                        <!-- ==================== HISPANIOLA ==================== -->\n'
        '                        <g transform="translate(1000, 425) scale(0.247)">\n'
        f'                            <path class="f-sand province-path" vector-effect="non-scaling-stroke" d="{hispaniola_d}" />\n'
        '                        </g>'
    )

def generate_transport_corridors():
    """Generates all transport corridor lines and animated traffic dots solely based on CONNECTIONS."""
    line_paths = []
    anim_dots = []

    for conn in CONNECTIONS:
        if isinstance(conn, (tuple, list)):
            c_from = conn[0]
            c_to = conn[1]
            c_type = conn[2]
            bend = conn[3] if len(conn) > 3 else 0.0
            anim = True
            dur = None
        else:
            c_from = conn["from"]
            c_to = conn["to"]
            c_type = conn["type"]
            bend = conn.get("bend", 0.0)
            anim = conn.get("animated", True)
            dur = conn.get("dur")

        path_d = make_curved_path(c_from, c_to, bend=bend)
        style = get_connection_style(c_type)

        line_paths.append(f'                        <!-- {c_type}: {c_from} to {c_to} -->\n                        <path d="{path_d}" {style["attrs"]} />')

        if anim and style.get("dot_r", 0) > 0:
            anim_dur = dur or style.get("default_dur", "4.0s")
            dot_r = style["dot_r"]
            anim_dots.append(f'''                        <circle r="{dot_r}" class="f-white">
                            <animateMotion dur="{anim_dur}" repeatCount="indefinite" path="{path_d}" />
                        </circle>''')

    return (
        "                        <!-- ==================== TRANSPORT CORRIDORS ==================== -->\n"
        + "\n".join(line_paths)
        + "\n                        <!-- Animated Traffic Dots -->\n"
        + "\n".join(anim_dots)
    )

def generate_cities_xml(g_florida, g_bahamas, g_jamaica):
    """Generates capital markers, station nodes, white inner dots and labels dynamically from CITIES."""
    capital_xml = []
    ink_nodes = []
    white_dots = []
    pyramid_xml = []
    labels = []
    
    for c in CITIES:
        if c.get("hide_marker") and c.get("hide_label"):
            continue
            
        x, y = c["pos"]
        ctype = c["type"]
        name = c["name"].upper()
        lbl = c.get("label", {})
        dx, dy = lbl.get("offset", (0, 0))
        anchor = lbl.get("anchor", "start")
        size = lbl.get("size", 11)
        weight = lbl.get("weight", 400)
        
        if not c.get("hide_label"):
            anchor_attr = f' text-anchor="{anchor}"' if anchor != "start" else ""
            labels.append(f'                            <text x="{x + dx}" y="{y + dy}" font-size="{size}" font-weight="{weight}"{anchor_attr}>{name}</text>')
        
        if not c.get("hide_marker"):
            if ctype == "Capital":
                capital_xml.append(f'''                        <!-- Capital City Marker: {c['name']} -->
                        <g>
                            <circle cx="{x}" cy="{y}" r="16" class="f-coral pulse" />
                            <circle cx="{x}" cy="{y}" r="11" class="f-coral" />
                            <path d="M{x} {y-7} l2 4.2 4.6.6 -3.4 3.2 .9 4.5 -4.1 -2.2 -4.1 2.2 .9 -4.5 -3.4 -3.2 4.6 -.6 z" class="f-white" />
                        </g>''')
            else:
                r_ink = 7 if ctype == "Large" else (6 if c.get("has_pyramid") else 5.5)
                r_white = 2.8 if ctype == "Large" else (2.4 if name == "KINGSTON" else 2.2)
                ink_nodes.append(f'                            <circle cx="{x}" cy="{y}" r="{r_ink}" />')
                white_dots.append(f'                            <circle cx="{x}" cy="{y}" r="{r_white}" />')
                if c.get("has_pyramid"):
                    pyramid_xml.append(f'''                        <!-- Mega Pyramid Mark -->
                        <path d="M{x} {y-9} l4 7 h-8 z" class="f-gold" />''')
                
    territory_labels = f'''                            <!-- Major Territories -->
                            <text x="380" y="45" font-size="13" font-weight="600" opacity=".6" letter-spacing=".15em">{g_florida}</text>
                            <text x="530" y="70" font-size="11" font-weight="600" opacity=".45" letter-spacing=".15em">{g_bahamas}</text>
                            <text x="825" y="600" font-size="11" opacity=".55" letter-spacing=".15em" text-anchor="middle">{g_jamaica}</text>'''

    return f'''                        <!-- ==================== CAPITAL AND STATIONS ==================== -->
{chr(10).join(capital_xml)}
                        <!-- Station Network Nodes -->
                        <g class="f-ink">
{chr(10).join(ink_nodes)}
                        </g>
{chr(10).join(pyramid_xml)}
                        <g class="f-white">
{chr(10).join(white_dots)}
                        </g>
                        <!-- ==================== TYPOGRAPHY AND LABELS ==================== -->
                        <g font-size="11.5">
{chr(10).join(labels)}
{territory_labels}
                        </g>'''

def build_svg(lang="en", cuba_xml=""):
    is_hu = (lang == "hu")
    
    fl_xml = get_florida_group()
    jm_xml = get_jamaica_group()
    hi_xml = get_hispaniola_group()
    cuba_xml = cuba_xml or get_cuba_group()
    
    # Legend labels
    lbl_maglev = "MAGLEV"
    lbl_hyperloop = "HYPERLOOP"
    lbl_tunnel = "ALAGÚT" if is_hu else "TUNNEL"
    lbl_mainline = "FŐVONAL" if is_hu else "MAIN LINE"
    lbl_maritime = "TENGERI ÚTVONAL" if is_hu else "MARITIME ROUTE"
    
    # Geographic labels
    g_florida = "FLORIDA"
    g_bahamas = "BAHAMA-SZIGETEK" if is_hu else "BAHAMAS"
    g_jamaica = "JAMAICA"

    # Corridors and nodes generated dynamically
    corridors_xml = generate_transport_corridors()
    cities_xml = generate_cities_xml(g_florida, g_bahamas, g_jamaica)

    # Artificial islands position dynamically aligned with Nova Aurelia
    na_x, na_y = get_city_pos("Nova Aurelia")
    art_tx = na_x - 255
    art_ty = na_y - 292

    # Assemble SVG text
    svg = f'''<svg class="ill" viewBox="0 0 1800 650">
                    <defs>
                        <clipPath id="rm-clip">
                            <rect width="1800" height="650" rx="28" />
                        </clipPath>
                    </defs>
                    <g clip-path="url(#rm-clip)">
                        <rect width="1800" height="650" class="f-sea3" />
                        <!-- Geographic Coordinate Grid -->
                        <g class="k-white" stroke-width="1" opacity=".3">
                            <path d="M0 130h1800M0 260h1800M0 390h1800M0 520h1800M300 0v650M600 0v650M900 0v650M1200 0v650M1500 0v650" />
                        </g>
{fl_xml}
                        <!-- ==================== BAHAMAS ARCHIPELAGO ==================== -->
                        <g class="f-sand" opacity=".88" transform="translate(200, -45) scale(1.15)">
                            <path d="M294 72 c16 -5 36 -6 49 -2 c4 2 2 6 -3 7 c-16 3 -36 2 -48 -2 c-4 -1 -2 -5 2 -5 z" />
                            <path d="M352 62 c8 2 13 10 11 18 c-2 9 -10 15 -14 12 c-3 -2 -1 -7 2 -12 c3 -5 3 -14 1 -18 z" />
                            <ellipse cx="292" cy="154" rx="4.5" ry="2.8" />
                            <circle cx="328" cy="118" r="3.2" />
                            <path d="M318 152 c9 -6 22 -4 26 5 c4 10 2 26 -4 37 c-6 11 -16 15 -21 9 c-5 -7 -3 -24 1 -35 c2 -8 1 -12 -2 -16 z" />
                            <circle cx="370" cy="176" r="3" />
                            <path d="M382 192 c12 -4 26 -2 32 4 c3 3 0 7 -4 7 c-12 1 -24 -2 -28 -6 z" />
                            <circle cx="430" cy="226" r="2.8" />
                        </g>
{cuba_xml}
{jm_xml}
{hi_xml}
{corridors_xml}
{cities_xml}
                        <!-- ==================== MAP LEGEND BOX ==================== -->
                        <g transform="translate(1460 550)" font-size="10">
                            <rect x="-14" y="-12" width="314" height="70" rx="12" class="f-white" opacity=".92" />
                            <path d="M0 2h26" class="k-coral" stroke-width="5" stroke-linecap="round" /><text x="34" y="5.5" font-weight="600">{lbl_maglev}</text>
                            <path d="M125 2h26" class="k-gold" stroke-width="5" stroke-linecap="round" /><text x="159" y="5.5" font-weight="600">{lbl_hyperloop}</text>
                            <path d="M0 26h26" class="k-ink" stroke-width="4" stroke-dasharray="2 7" stroke-linecap="round" /><text x="34" y="29.5" font-weight="600">{lbl_tunnel}</text>
                            <path d="M125 26h26" class="k-ink2" stroke-width="4" stroke-linecap="round" /><text x="159" y="29.5" font-weight="600">{lbl_mainline}</text>
                            <path d="M0 46h26" class="k-sea" stroke-width="3.5" stroke-dasharray="5 3" stroke-linecap="round" /><text x="34" y="49.5" font-weight="600">{lbl_maritime}</text>
                        </g>
                    </g>
                </svg>'''
    return svg

def main():
    cuba_group = get_cuba_group()
    print("Found Cuba group, size:", len(cuba_group))
    
    for lang, rel_path in [("en", "en/infrastructure.html"), ("hu", "hu/infrastructure.html")]:
        filepath = ROOT / rel_path
        svg_content = build_svg(lang, cuba_group)
        
        # Validate XML parsing
        try:
            ET.fromstring(svg_content)
            print(f"[{lang}] SVG parsed successfully as valid XML!")
        except Exception as e:
            print(f"[{lang}] XML parse error:", e)
            sys.exit(1)
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Locate figure inside #mobility
        mob_idx = content.find('id="mobility"')
        fig_str = '<figure class="ill-panel" data-reveal="zoom">'
        fig_idx = content.find(fig_str, mob_idx)
        cap_str = '<figcaption class="ill-caption">'
        cap_idx = content.find(cap_str, fig_idx)
        
        if mob_idx == -1 or fig_idx == -1 or cap_idx == -1:
            raise ValueError(f"Could not locate mobility figure boundaries in {filepath}")
            
        # Replace the SVG inside figure
        before = content[:fig_idx + len(fig_str)]
        after = content[cap_idx:]
        
        new_content = before + "\n                " + svg_content + "\n                " + after
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath} successfully!")
        
        subprocess.run(["python3", str(ROOT / "scripts" / "build_pages.py"), "--format", str(filepath)], check=False)

if __name__ == '__main__':
    main()
