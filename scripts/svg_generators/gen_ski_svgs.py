#!/usr/bin/env python3
"""
Generate inline SVG illustrations for ski-paradise.html:
  - Summit Elevation Comparison Chart (960x390)
  - 5 Alpine Resort Cards (320x200)

Hero art is a canonical standalone file in icons/ski/hero-art.svg and is NOT generated here.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from site_common import (  # noqa: E402
    draw_mountain_3d,
    draw_palm,
    draw_spruce,
    update_page_cards,
    update_page_chart,
    window_grid,
)


def build_ski_height_chart(lang: str) -> str:
    """Summit Elevation Comparison Chart (viewBox 0 0 960 390) with 6 realistic 3D peaks."""
    ticks = (
        [("5,000 m", 54), ("3,750 m", 124), ("2,500 m", 194), ("1,250 m", 264), ("0 m", 334)]
        if lang == "en"
        else [("5000 m", 54), ("3750 m", 124), ("2500 m", 194), ("1250 m", 264), ("0 m", 334)]
    )
    peaks_meta = (
        [
            (145, 58, "4,850 m", 40, "Pico Soberano", "Waikiki Andes", False),
            (295, 82, "4,420 m", 68, "Condor Glacier", "Waikiki Andes", False),
            (445, 112, "3,883 m", 98, "Zermatt Glacier", "Switzerland (Ref.)", True),
            (595, 150, "3,200 m", 130, "Monte Rosa Dome", "Waikiki Andes", False),
            (745, 152, "3,180 m", 136, "Haiti Glacier Crown", "Haiti Island", False),
            (870, 176, "2,738 m", 162, "Courchevel", "France (Ref.)", True),
        ]
        if lang == "en"
        else [
            (145, 58, "4850 m", 40, "Pico Soberano", "Waikiki Andok", False),
            (295, 82, "4420 m", 68, "Condor Gleccser", "Waikiki Andok", False),
            (445, 112, "3883 m", 98, "Zermatt Gleccser", "Svájc (Ref.)", True),
            (595, 150, "3200 m", 130, "Monte Rosa Kupola", "Waikiki Andok", False),
            (745, 152, "3180 m", 136, "Haiti Gleccserkorona", "Haiti-sziget", False),
            (870, 176, "2738 m", 162, "Courchevel", "Franciaország (Ref.)", True),
        ]
    )

    o = [
        '<svg class="ill height-chart" viewBox="0 0 960 390" data-reveal>',
        "<defs>",
        '<linearGradient id="hcPeakAndesLit" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#3b82f6" />',
        '<stop offset="100%" stop-color="#1d4ed8" />',
        "</linearGradient>",
        '<linearGradient id="hcPeakAndesShade" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#1e3a8a" />',
        '<stop offset="100%" stop-color="#0f172a" />',
        "</linearGradient>",
        '<linearGradient id="hcPeakHaitiLit" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#10b981" />',
        '<stop offset="55%" stop-color="#047857" />',
        '<stop offset="100%" stop-color="#064e3b" />',
        "</linearGradient>",
        '<linearGradient id="hcPeakHaitiShade" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#065f46" />',
        '<stop offset="100%" stop-color="#022c22" />',
        "</linearGradient>",
        '<linearGradient id="hcPeakRefLit" x1="0" y1="0" x2="1" y2="1">',
        '<stop offset="0%" stop-color="#94a3b8" />',
        '<stop offset="100%" stop-color="#475569" />',
        "</linearGradient>",
        "</defs>",
        '<g class="k-line" stroke-dasharray="3 6">',
        '<line x1="60" y1="50" x2="925" y2="50" />',
        '<line x1="60" y1="120" x2="925" y2="120" />',
        '<line x1="60" y1="190" x2="925" y2="190" />',
        '<line x1="60" y1="260" x2="925" y2="260" />',
        "</g>",
    ]
    for label, ty in ticks:
        o.append(f'<text x="50" y="{ty}" text-anchor="end" font-size="10" class="h-ref">{label}</text>')

    for idx, (cx, py, val_s, val_y, name_s, sub_s, is_ref) in enumerate(peaks_meta):
        op = ' opacity="0.68"' if is_ref else ""
        o.append(f'<g class="tower" style="--d: {idx}"{op}>')
        if is_ref:
            o += draw_mountain_3d(
                (cx, py), 52, 52, 330, "url(#hcPeakRefLit)", "#334155", "#f1f5f9", "#cbd5e1", 0.52, seed=idx * 3.7 + 1
            )
        elif idx == 4:
            o += draw_mountain_3d(
                (cx, py), 58, 58, 330, "url(#hcPeakHaitiLit)", "url(#hcPeakHaitiShade)", "#ffffff", "#bae6fd", 0.48, seed=19.2, rock_col="#064e3b"
            )
            o.append(f'<path d="M{cx - 58},330 Q{cx},323 {cx + 58},330 Z" fill="#fbbf24" opacity="0.85" />')
            o.append(f'<polygon points="{cx - 8},{py} {cx},{py - 10} {cx + 8},{py}" fill="#f59e0b" />')
        else:
            o += draw_mountain_3d(
                (cx, py), 60, 60, 330, "url(#hcPeakAndesLit)", "url(#hcPeakAndesShade)", "#ffffff", "#bfdbfe", 0.58, seed=idx * 5.1 + 2, rock_col="#172554"
            )
            if idx == 0:
                o.append(f'<polygon points="{cx - 14},{py + 28} {cx},{py} {cx + 14},{py + 28}" fill="#fbbf24" opacity="0.85" />')
                o.append(f'<circle cx="{cx}" cy="{py - 6}" r="4" class="f-coral pulse" />')
            elif idx == 1:
                o.append(f'<rect x="{cx - 9}" y="{py - 3}" width="18" height="3.5" rx="1" fill="#fbbf24" />')
            elif idx == 3:
                o.append(f'<ellipse cx="{cx}" cy="{py}" rx="12" ry="3.5" fill="#0f172a" />')
                o.append(f'<path d="M{cx - 10},{py} A10,9 0 0,1 {cx + 10},{py} Z" fill="#38bdf8" stroke="#fde68a" stroke-width="1.2" />')
        o.append("</g>")

        val_cls = "h-val h-ref" if is_ref else "h-val"
        name_cls = "h-name h-ref" if is_ref else "h-name"
        o.append(f'<text x="{cx}" y="{val_y}" text-anchor="middle" class="{val_cls}">{val_s}</text>')
        o.append(f'<text x="{cx}" y="352" text-anchor="middle" class="{name_cls}">{name_s}</text>')
        o.append(f'<text x="{cx}" y="368" text-anchor="middle" font-size="9" class="h-ref">{sub_s}</text>')

    o.append('<line x1="60" y1="330" x2="925" y2="330" class="k-ink" stroke-width="1.8" />')
    o.append("</svg>")
    return "".join(o)


def build_ski_resort_card(idx: int) -> str:
    """
    Build the 5 Alpine Resort cards (viewBox 0 0 320 200) on ski-paradise.html:
      0: Grand Palace Val d'Aurelia
      1: Ski Paradise Royal Chalets
      2: Monte Rosa Sky Observatory
      3: Haiti Glacier Crown Resort
      4: Edelweiss Thermal Village
    """
    o = ['<svg class="ill" viewBox="0 0 320 200">']
    if idx == 0:
        o += [
            '<defs><linearGradient id="spCard0Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0c2340"/><stop offset="65%" stop-color="#1e4e79"/><stop offset="100%" stop-color="#e5c185"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#spCard0Sky)" />',
            '<circle cx="265" cy="42" r="22" fill="#fef08a" opacity="0.85" />',
            *draw_mountain_3d((85, 32), 110, 120, 148, "#2b5c8f", "#102a4c", "#ffffff", "#bfdbfe", 0.62, seed=1.4),
            *draw_mountain_3d((235, 38), 115, 110, 148, "#336699", "#13335c", "#ffffff", "#bfdbfe", 0.58, seed=4.2),
            '<path d="M0,142 Q160,132 320,144 L320,200 L0,200 Z" fill="#e2e8f0" />',
            '<rect x="58" y="96" width="204" height="52" fill="#6b4423" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="52,98 160,64 268,98" fill="#1e293b" stroke="#e2e8f0" stroke-width="1.2" />',
            '<rect x="64" y="76" width="26" height="72" fill="#7c4d28" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="60,78 77,50 94,78" fill="#0f172a" stroke="#f8fafc" stroke-width="1" />',
            '<rect x="230" y="76" width="26" height="72" fill="#7c4d28" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="226,78 243,50 260,78" fill="#0f172a" stroke="#f8fafc" stroke-width="1" />',
            '<rect x="122" y="82" width="76" height="66" fill="#85522b" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="116,84 160,46 204,84" fill="#0f172a" stroke="#ffffff" stroke-width="1.4" />',
            '<path d="M144,148 L144,108 A16,15 0 0,1 176,108 L176,148 Z" fill="#fef08a" stroke="#d97706" stroke-width="1" />',
            window_grid(94, 104, 24, 36, 2, 3, "#fde68a", 0.92),
            window_grid(202, 104, 24, 36, 2, 3, "#fde68a", 0.92),
            window_grid(68, 84, 18, 52, 2, 4, "#fde68a", 0.9),
            window_grid(234, 84, 18, 52, 2, 4, "#fde68a", 0.9),
            '<polygon points="88,158 232,158 244,182 76,182" fill="#38bdf8" stroke="#f8fafc" stroke-width="1.5" />',
            '<path d="M115,156 Q118,142 114,136 M160,156 Q164,140 159,134 M205,156 Q209,142 204,136" fill="none" stroke="#ffffff" stroke-width="1.3" opacity="0.65" stroke-linecap="round" />',
            *draw_spruce(26, 158, 0.95), *draw_spruce(44, 164, 0.8), *draw_spruce(282, 162, 0.9), *draw_spruce(298, 156, 1.05),
        ]
    elif idx == 1:
        o += [
            '<defs><linearGradient id="spCard1Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0f2947"/><stop offset="60%" stop-color="#2c5e8a"/><stop offset="100%" stop-color="#f3d5a0"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#spCard1Sky)" />',
            *draw_mountain_3d((160, 26), 150, 150, 145, "#285582", "#102a49", "#ffffff", "#cbd5e1", 0.65, seed=3.3),
            '<path d="M0,140 Q160,128 320,142 L320,200 L0,200 Z" fill="#f1f5f9" />',
            '<path d="M160,34 C140,72 178,98 148,138" fill="none" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round" opacity="0.8" />',
            *draw_spruce(28, 148, 1.0), *draw_spruce(52, 154, 0.85), *draw_spruce(268, 152, 0.9), *draw_spruce(292, 146, 1.05),
            '<g transform="translate(88, 132)">',
            '<rect x="-26" y="-8" width="52" height="32" fill="#5c3418" />',
            '<polygon points="-34,-6 0,-42 34,-6" fill="#1e293b" stroke="#f8fafc" stroke-width="2" />',
            '<polygon points="-18,-6 0,-28 18,-6" fill="#fef08a" stroke="#b45309" stroke-width="1" />',
            '<line x1="0" y1="-28" x2="0" y2="24" stroke="#78350f" stroke-width="1.2" />',
            window_grid(-18, -2, 36, 20, 3, 2, "#fde68a", 0.95),
            "</g>",
            '<g transform="translate(198, 126)">',
            '<rect x="18" y="-44" width="7" height="18" fill="#475569" />',
            '<path d="M21.5,-46 Q26,-56 20,-64" fill="none" stroke="#e2e8f0" stroke-width="1.8" stroke-linecap="round" opacity="0.7" />',
            '<rect x="-36" y="-8" width="72" height="38" fill="#6b3e1e" stroke="#3b2313" stroke-width="1" />',
            '<polygon points="-46,-6 0,-52 46,-6" fill="#0f172a" stroke="#ffffff" stroke-width="2.4" />',
            '<polygon points="-24,-6 0,-34 24,-6" fill="#fef08a" stroke="#b45309" stroke-width="1.2" />',
            '<line x1="0" y1="-34" x2="0" y2="30" stroke="#78350f" stroke-width="1.4" />',
            window_grid(-28, -2, 56, 26, 4, 2, "#fde68a", 0.95),
            "</g>",
            *draw_spruce(138, 158, 0.92),
        ]
    elif idx == 2:
        o += [
            '<defs><linearGradient id="spCard2Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#050d1a"/><stop offset="55%" stop-color="#0f294a"/><stop offset="100%" stop-color="#1e4b7a"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#spCard2Sky)" />',
            '<path d="M0,48 Q85,22 165,44 T320,32 L320,62 Q240,74 160,52 T0,68 Z" fill="#2dd4bf" opacity="0.22" />',
            '<g fill="#ffffff">',
            '<circle cx="38" cy="26" r="1.4" class="twinkle" /><circle cx="92" cy="18" r="1.8" class="twinkle" />',
            '<circle cx="148" cy="32" r="1.2" class="twinkle" /><circle cx="218" cy="22" r="1.6" class="twinkle" />',
            '<circle cx="284" cy="36" r="1.5" class="twinkle" /><circle cx="64" cy="58" r="1.2" class="twinkle" />',
            "</g>",
            *draw_mountain_3d((65, 92), 95, 95, 200, "#1e3a5f", "#0b192c", "#e0f2fe", "#64748b", 0.55, seed=6.1),
            *draw_mountain_3d((185, 86), 135, 135, 200, "#254b7c", "#0f2442", "#ffffff", "#93c5fd", 0.68, seed=9.4),
            '<path d="M0,165 Q92,126 155,88" fill="none" stroke="#94a3b8" stroke-width="1.2" />',
            '<g class="bob" transform="translate(84, 122)">',
            '<line x1="0" y1="-8" x2="0" y2="0" stroke="#e2e8f0" stroke-width="1.2" />',
            '<rect x="-8" y="0" width="16" height="10" rx="3" fill="#c95a41" stroke="#ffffff" stroke-width="0.9" />',
            '<rect x="-5" y="2" width="10" height="4.5" rx="1" fill="#bae6fd" />',
            "</g>",
            '<g transform="translate(185, 84)">',
            '<polygon points="-52,6 48,6 38,18 -64,18" fill="#1e293b" stroke="#fbbf24" stroke-width="1.2" />',
            '<rect x="-46" y="-4" width="84" height="10" rx="2" fill="#38bdf8" opacity="0.85" stroke="#ffffff" stroke-width="0.9" />',
            '<path d="M-32,-4 A32,28 0 0,1 32,-4 Z" fill="#7dd3fc" opacity="0.88" stroke="#ffffff" stroke-width="1.4" />',
            '<path d="M-22,-4 A22,28 0 0,1 22,-4 M-10,-4 A10,28 0 0,1 10,-4 M-28,-14 L28,-14 M-18,-24 L18,-24" fill="none" stroke="#0f172a" stroke-width="0.9" opacity="0.55" />',
            '<line x1="0" y1="-32" x2="0" y2="-46" stroke="#fbbf24" stroke-width="1.8" />',
            '<circle cx="0" cy="-47" r="3" fill="#f97316" class="pulse" />',
            "</g>",
        ]
    elif idx == 3:
        o += [
            '<defs><linearGradient id="spCard3Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0284c7"/><stop offset="65%" stop-color="#7dd3fc"/><stop offset="100%" stop-color="#fef3c7"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#spCard3Sky)" />',
            '<circle cx="62" cy="42" r="20" fill="#fde68a" opacity="0.92" />',
            *draw_mountain_3d((175, 24), 145, 145, 152, "#15803d", "#064e3b", "#ffffff", "#bae6fd", 0.56, seed=12.3, rock_col="#052e16"),
            '<g transform="translate(175, 24)">',
            '<rect x="-16" y="-2" width="32" height="7" rx="1.5" fill="#0f172a" stroke="#fbbf24" stroke-width="1" />',
            '<path d="M-11,-2 A11,9 0 0,1 11,-2 Z" fill="#38bdf8" stroke="#ffffff" stroke-width="1" />',
            "</g>",
            '<path d="M175,32 C162,56 186,74 168,98" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity="0.88" />',
            '<path d="M0,136 Q28,122 56,134 Q84,120 112,132 Q140,118 168,132 Q196,120 224,134 Q252,122 280,134 Q302,124 320,136 L320,162 L0,162 Z" fill="#166534" />',
            '<path d="M0,146 Q32,134 64,146 Q96,134 128,146 Q160,134 192,146 Q224,134 256,146 Q288,134 320,146 L320,164 L0,164 Z" fill="#15803d" />',
            '<path d="M0,158 Q160,150 320,160 L320,200 L0,200 Z" fill="#fde68a" />',
            '<path d="M0,166 Q160,158 320,168 L320,200 L0,200 Z" fill="#0ea5e9" />',
            '<path d="M0,168 Q160,160 320,170 L320,184 Q160,176 0,182 Z" fill="#2dd4bf" opacity="0.55" />',
            *draw_palm(38, 162, 0.85, 1.0),
            *draw_palm(72, 160, 0.72, -0.8),
            *draw_palm(278, 162, 0.82, -1.0),
            '<g class="bob" transform="translate(195, 182)">',
            '<polygon points="-22,0 22,0 16,7 -18,7" fill="#ffffff" stroke="#0f172a" stroke-width="0.9" />',
            '<rect x="-12" y="-5" width="18" height="5" rx="1.5" fill="#e0f2fe" stroke="#0284c7" stroke-width="0.7" />',
            "</g>",
        ]
    else:
        o += [
            '<defs><linearGradient id="spCard4Sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#0f2537"/><stop offset="65%" stop-color="#2e5a78"/><stop offset="100%" stop-color="#e8c89b"/></linearGradient></defs>',
            '<rect width="320" height="200" fill="url(#spCard4Sky)" />',
            *draw_mountain_3d((95, 36), 115, 115, 142, "#2c5882", "#122b47", "#ffffff", "#cbd5e1", 0.58, seed=7.7),
            *draw_mountain_3d((235, 42), 110, 110, 142, "#356694", "#163557", "#ffffff", "#cbd5e1", 0.54, seed=10.2),
            '<path d="M0,136 Q160,126 320,138 L320,200 L0,200 Z" fill="#e2e8f0" />',
            '<path d="M168,134 C142,150 188,168 145,200 L198,200 C222,168 175,150 192,134 Z" fill="#38bdf8" stroke="#f8fafc" stroke-width="2" />',
            '<path d="M158,152 Q162,138 157,130 M182,168 Q186,154 181,146 M168,184 Q172,170 167,162" fill="none" stroke="#ffffff" stroke-width="1.5" opacity="0.7" stroke-linecap="round" />',
            '<path d="M142,168 Q176,152 210,168 L210,175 Q176,160 142,175 Z" fill="#64748b" stroke="#334155" stroke-width="1" />',
            '<g transform="translate(76, 134)">',
            '<rect x="-34" y="-8" width="68" height="26" rx="3" fill="#475569" stroke="#1e293b" stroke-width="1" />',
            '<path d="M-26,-8 A26,20 0 0,1 26,-8 Z" fill="#2dd4bf" opacity="0.82" stroke="#fbbf24" stroke-width="1.2" />',
            window_grid(-26, -2, 52, 16, 4, 2, "#fde68a", 0.9),
            "</g>",
            '<g transform="translate(248, 134)">',
            '<rect x="-28" y="-10" width="56" height="28" fill="#6b4226" />',
            '<polygon points="-34,-8 0,-34 34,-8" fill="#1e293b" stroke="#ffffff" stroke-width="1.8" />',
            window_grid(-22, -4, 44, 18, 3, 2, "#fde68a", 0.92),
            "</g>",
            *draw_spruce(22, 152, 0.9),
            *draw_spruce(300, 154, 0.95),
        ]
    o.append("</svg>")
    return "".join(o)


def main() -> None:
    cards = [build_ski_resort_card(i) for i in range(5)]
    for lang in ("en", "hu"):
        path = ROOT / lang / "ski-paradise.html"
        chart_svg = build_ski_height_chart(lang)
        update_page_chart(path, chart_svg)
        update_page_cards(path, "hotel-art", cards)


if __name__ == "__main__":
    main()

