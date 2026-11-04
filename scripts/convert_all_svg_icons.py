#!/usr/bin/env python3
"""
Convert and verify all SVG icons across the site linked to icons/mdi/.
Idempotent script: converts any inline <svg> icons to <img> tags, or verifies already converted <img> icons.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def replace_svgs_in_sights(path: Path):
    text = path.read_text(encoding="utf-8")
    orig_text = text
    icons = [
        "bank.svg",
        "pyramid.svg",
        "clock-outline.svg",
        "music.svg",
        "office-building.svg",
        "city.svg",
        "currency-usd.svg",
        "city-variant.svg",
        "temple-buddhist.svg",
        "pyramid.svg",
        "wall.svg",
        "crown.svg",
        "castle.svg",
        "palm-tree.svg",
        "earth.svg",
        "chameleon.svg",
        "bank-outline.svg",
        "stadium.svg",
        "theater.svg",
        "ferris-wheel.svg",
    ]
    
    idx = 0
    converted = 0
    def repl(m):
        nonlocal idx, converted
        icon = icons[idx]
        idx += 1
        if "<svg" in m.group(0):
            converted += 1
        return f'<span class="card-icon"><img src="../icons/mdi/{icon}" alt="" /></span>'

    text, n = re.subn(r'<span class="card-icon">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/[^>]*>)\s*</span>', repl, text)
    if n != len(icons):
        raise ValueError(f"{path}: Expected {len(icons)} card-icons, but found {n}")
    if text != orig_text:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}: converted {converted} card icons to MDI links")
    else:
        print(f"Verified {path}: all {n} card icons correctly linked to MDI")

def replace_svgs_in_infrastructure(path: Path):
    text = path.read_text(encoding="utf-8")
    orig_text = text
    
    # 8 card icons
    card_icons = [
        "train-variant.svg",
        "flash.svg",
        "wifi.svg",
        "ferry.svg",
        "atom.svg",
        "water.svg",
        "transmission-tower.svg",
        "leaf.svg",
    ]
    idx = 0
    def repl_card(m):
        nonlocal idx
        icon = card_icons[idx]
        idx += 1
        return f'<span class="card-icon"><img src="../icons/mdi/{icon}" alt="" /></span>'

    text, n_cards = re.subn(r'<span class="card-icon">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/[^>]*>)\s*</span>', repl_card, text)
    if n_cards != len(card_icons):
        raise ValueError(f"{path}: Expected {len(card_icons)} card icons, found {n_cards}")

    # 10 building-loc icons
    text, n_locs = re.subn(r'<span class="building-loc">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/map-marker\.svg[^>]*>)\s*',
                           r'<span class="building-loc"><img src="../icons/mdi/map-marker.svg" alt="" />',
                           text)
    if n_locs != 10:
        raise ValueError(f"{path}: Expected 10 building-loc icons, found {n_locs}")

    # 3 island tabs
    tab_map = [
        (r'(<button class="island-tab-btn[^"]*" id="tab-btn-palm"[^>]*>)\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/palm-tree\.svg[^>]*>)\s*',
         r'\1<img src="../icons/mdi/palm-tree.svg" alt="" />\n                    '),
        (r'(<button class="island-tab-btn[^"]*" id="tab-btn-world"[^>]*>)\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/earth\.svg[^>]*>)\s*',
         r'\1<img src="../icons/mdi/earth.svg" alt="" />\n                    '),
        (r'(<button class="island-tab-btn[^"]*" id="tab-btn-chameleon"[^>]*>)\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/chameleon\.svg[^>]*>)\s*',
         r'\1<img src="../icons/mdi/chameleon.svg" alt="" />\n                    '),
    ]
    for pattern, repl in tab_map:
        text, n = re.subn(pattern, repl, text)
        if n != 1:
            raise ValueError(f"{path}: Expected 1 match for {pattern}, got {n}")

    if text != orig_text:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}: {n_cards} cards, {n_locs} locs, 3 tabs")
    else:
        print(f"Verified {path}: {n_cards} cards, {n_locs} locs, 3 tabs correctly linked to MDI")

def replace_svgs_in_visa(path: Path):
    text = path.read_text(encoding="utf-8")
    orig_text = text
    customs_icons = [
        "briefcase.svg",
        "currency-usd.svg",
        "shield-check.svg",
    ]
    idx = 0
    def repl_customs(m):
        nonlocal idx
        icon = customs_icons[idx]
        idx += 1
        return f'<div class="customs-icon"><img src="../icons/mdi/{icon}" alt="" /></div>'

    text, n = re.subn(r'<div class="customs-icon">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/[^>]*>)\s*</div>', repl_customs, text)
    if n != len(customs_icons):
        raise ValueError(f"{path}: Expected {len(customs_icons)} customs icons, found {n}")
    if text != orig_text:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}: {n} customs icons")
    else:
        print(f"Verified {path}: {n} customs icons correctly linked to MDI")

def replace_svgs_in_nova_aurelia(path: Path):
    text = path.read_text(encoding="utf-8")
    orig_text = text
    pillar_icons = [
        "currency-usd.svg",
        "flash.svg",
        "web.svg",
    ]
    idx = 0
    def repl_pillar(m):
        nonlocal idx
        icon = pillar_icons[idx]
        idx += 1
        return f'<div class="city-pillar-badge"><img src="../icons/mdi/{icon}" alt="" /></div>'

    text, n = re.subn(r'<div class="city-pillar-badge">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/[^>]*>)\s*</div>', repl_pillar, text)
    if n != len(pillar_icons):
        raise ValueError(f"{path}: Expected {len(pillar_icons)} pillar badges, found {n}")
    if text != orig_text:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}: {n} pillar badges")
    else:
        print(f"Verified {path}: {n} pillar badges correctly linked to MDI")

def replace_svgs_in_family_tree(path: Path):
    text = path.read_text(encoding="utf-8")
    orig_text = text
    # 1 heirs icon
    text, n_heirs = re.subn(r'<span class="heirs-icon" aria-hidden="true">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/crown\.svg[^>]*>)\s*</span>',
                            r'<span class="heirs-icon" aria-hidden="true"><img src="../icons/mdi/crown.svg" alt="" /></span>',
                            text)
    if n_heirs != 1:
        raise ValueError(f"{path}: Expected 1 heirs icon, found {n_heirs}")

    matrix_icons = [
        "shield-check.svg",
        "bank.svg",
        "earth.svg",
        "leaf.svg",
        "flash.svg",
        "handshake.svg",
    ]
    idx = 0
    def repl_matrix(m):
        nonlocal idx
        icon = matrix_icons[idx]
        idx += 1
        return f'<div class="matrix-icon-wrap" aria-hidden="true"><img src="../icons/mdi/{icon}" alt="" /></div>'

    text, n_matrix = re.subn(r'<div class="matrix-icon-wrap" aria-hidden="true">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/[^>]*>)\s*</div>', repl_matrix, text)
    if n_matrix != len(matrix_icons):
        raise ValueError(f"{path}: Expected {len(matrix_icons)} matrix icons, found {n_matrix}")

    if text != orig_text:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}: {n_heirs} heirs, {n_matrix} matrix icons")
    else:
        print(f"Verified {path}: {n_heirs} heirs, {n_matrix} matrix icons correctly linked to MDI")

def replace_svgs_in_ski_paradise(path: Path):
    text = path.read_text(encoding="utf-8")
    orig_text = text
    # 10 facts
    fact_icons = [
        "ski.svg",
        "snowflake.svg",
        "image-filter-hdr.svg",
        "gondola.svg",
        "waves.svg",
        "shield-check.svg",
        "crown.svg",
        "silverware.svg",
        "flash.svg",
        "qrcode.svg",
    ]
    idx_fact = 0
    def repl_fact(m):
        nonlocal idx_fact
        icon = fact_icons[idx_fact]
        idx_fact += 1
        return f'<div class="fact">\n                    <img src="../icons/mdi/{icon}" alt="" />'

    text, n_facts = re.subn(r'<div class="fact">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/[^>]*>)', repl_fact, text)
    if n_facts != len(fact_icons):
        raise ValueError(f"{path}: Expected {len(fact_icons)} facts, found {n_facts}")

    # 3 tabs
    tab_map = [
        (r'(<button [^>]*id="tab-andes"[^>]*>)\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/image-filter-hdr\.svg[^>]*>)\s*',
         r'\1<img src="../icons/mdi/image-filter-hdr.svg" alt="" />\n                    '),
        (r'(<button [^>]*id="tab-haiti"[^>]*>)\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/snowflake\.svg[^>]*>)\s*',
         r'\1<img src="../icons/mdi/snowflake.svg" alt="" />\n                    '),
        (r'(<button [^>]*id="tab-telemetry"[^>]*>)\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/chart-line\.svg[^>]*>)\s*',
         r'\1<img src="../icons/mdi/chart-line.svg" alt="" />\n                    '),
    ]
    for pattern, repl in tab_map:
        text, n = re.subn(pattern, repl, text)
        if n != 1:
            raise ValueError(f"{path}: Expected 1 match for {pattern}, got {n}")

    # 5 hotel locs
    text, n_locs = re.subn(r'<p class="hotel-loc">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/map-marker\.svg[^>]*>)\s*',
                           r'<p class="hotel-loc"><img src="../icons/mdi/map-marker.svg" alt="" />',
                           text)
    if n_locs != 5:
        raise ValueError(f"{path}: Expected 5 hotel-loc icons, found {n_locs}")

    # 6 experience cards
    exp_icons = [
        "weather-sunny.svg",
        "helicopter.svg",
        "silverware-fork-knife.svg",
        "hot-tub.svg",
        "weather-night.svg",
        "bag-personal.svg",
    ]
    idx_exp = 0
    def repl_exp(m):
        nonlocal idx_exp
        icon = exp_icons[idx_exp]
        idx_exp += 1
        return f'<div class="card-icon"><img src="../icons/mdi/{icon}" alt="" /></div>'

    text, n_exp = re.subn(r'<div class="card-icon">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/[^>]*>)\s*</div>', repl_exp, text)
    if n_exp != len(exp_icons):
        raise ValueError(f"{path}: Expected {len(exp_icons)} experience card icons, found {n_exp}")

    # 1 travel callout
    text, n_callout = re.subn(r'<div class="travel-callout-icon" aria-hidden="true">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/crown\.svg[^>]*>)\s*</div>',
                             r'<div class="travel-callout-icon" aria-hidden="true"><img src="../icons/mdi/crown.svg" alt="" /></div>',
                             text)
    if n_callout != 1:
        raise ValueError(f"{path}: Expected 1 travel callout icon, found {n_callout}")

    if text != orig_text:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}: {n_facts} facts, 3 tabs, {n_locs} locs, {n_exp} exp cards, {n_callout} callout")
    else:
        print(f"Verified {path}: {n_facts} facts, 3 tabs, {n_locs} locs, {n_exp} exp cards, {n_callout} callout correctly linked to MDI")

def replace_svgs_in_travel_guide(path: Path):
    text = path.read_text(encoding="utf-8")
    orig_text = text
    # 10 facts
    fact_icons = [
        "city.svg",
        "translate.svg",
        "passport.svg",
        "currency-usd.svg",
        "clock-outline.svg",
        "weather-partly-cloudy.svg",
        "train-variant.svg",
        "credit-card.svg",
        "medical-bag.svg",
        "power-plug.svg",
    ]
    idx_fact = 0
    def repl_fact(m):
        nonlocal idx_fact
        icon = fact_icons[idx_fact]
        idx_fact += 1
        return f'<div class="fact">\n                    <img src="../icons/mdi/{icon}" alt="" />'

    text, n_facts = re.subn(r'<div class="fact">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/[^>]*>)', repl_fact, text)
    if n_facts != len(fact_icons):
        raise ValueError(f"{path}: Expected {len(fact_icons)} facts, found {n_facts}")

    # 11 transit/planner cards + 8 tips cards = 19 span.card-icon
    transit_tips_icons = [
        # 11 transit & planner
        "airplane.svg",
        "train-variant.svg",
        "ferry.svg",
        "bus.svg",
        "train-variant.svg",
        "gondola.svg",
        "ferry.svg",
        "cellphone.svg",
        "credit-card.svg",
        "wifi.svg",
        "ticket.svg",
        # 8 tips
        "silverware-fork-knife.svg",
        "hanger.svg",
        "currency-usd.svg",
        "water.svg",
        "tree.svg",
        "bag-personal.svg",
        "camera.svg",
        "phone-alert.svg",
    ]
    idx_tt = 0
    def repl_tt(m):
        nonlocal idx_tt
        icon = transit_tips_icons[idx_tt]
        idx_tt += 1
        return f'<span class="card-icon"><img src="../icons/mdi/{icon}" alt="" /></span>'

    text, n_tt = re.subn(r'<span class="card-icon">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/[^>]*>)\s*</span>', repl_tt, text)
    if n_tt != len(transit_tips_icons):
        raise ValueError(f"{path}: Expected {len(transit_tips_icons)} transit/tips icons, found {n_tt}")

    # 1 travel callout
    text, n_callout = re.subn(r'<div class="travel-callout-icon">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/passport\.svg[^>]*>)\s*</div>',
                             r'<div class="travel-callout-icon"><img src="../icons/mdi/passport.svg" alt="" /></div>',
                             text)
    if n_callout != 1:
        raise ValueError(f"{path}: Expected 1 travel callout, found {n_callout}")

    # 15 hotel locs
    text, n_locs = re.subn(r'<span class="hotel-loc">\s*(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/map-marker\.svg[^>]*>)\s*',
                           r'<span class="hotel-loc"><img src="../icons/mdi/map-marker.svg" alt="" />',
                           text)
    if n_locs != 15:
        raise ValueError(f"{path}: Expected 15 hotel locs, found {n_locs}")

    if text != orig_text:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path}: {n_facts} facts, {n_tt} cards, {n_callout} callout, {n_locs} hotel locs")
    else:
        print(f"Verified {path}: {n_facts} facts, {n_tt} cards, {n_callout} callout, {n_locs} hotel locs correctly linked to MDI")

def replace_svgs_in_gallery(path: Path):
    text = path.read_text(encoding="utf-8")
    orig_text = text
    
    # 3 view buttons
    btn_map = [
        (r'(<button id="btn-grid-mini" class="view-btn[^"]*">\s*)(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/view-compact\.svg[^>]*>)\s*',
         r'\1<img src="../icons/mdi/view-compact.svg" alt="" /> '),
        (r'(<button id="btn-grid-small" class="view-btn[^"]*">\s*)(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/view-grid\.svg[^>]*>)\s*',
         r'\1<img src="../icons/mdi/view-grid.svg" alt="" /> '),
        (r'(<button id="btn-grid-large" class="view-btn[^"]*">\s*)(?:<svg\b[^>]*>[\s\S]*?</svg>|<img\b[^>]*\/icons\/mdi\/view-module\.svg[^>]*>)\s*',
         r'\1<img src="../icons/mdi/view-module.svg" alt="" /> '),
    ]
    for pattern, repl in btn_map:
        text, n = re.subn(pattern, repl, text)
        if n != 1:
            raise ValueError(f"{path}: Expected 1 match for {pattern}, got {n}")

    if text != orig_text:
        path.write_text(text, encoding="utf-8")
        print(f"Updated gallery {path}")
    else:
        print(f"Verified gallery {path}: view buttons correctly linked to MDI")

def main():
    for loc in ["hu", "en"]:
        replace_svgs_in_sights(ROOT / loc / "sights.html")
        replace_svgs_in_infrastructure(ROOT / loc / "infrastructure.html")
        replace_svgs_in_visa(ROOT / loc / "visa.html")
        replace_svgs_in_nova_aurelia(ROOT / loc / "nova-aurelia.html")
        replace_svgs_in_family_tree(ROOT / loc / "family-tree.html")
        replace_svgs_in_ski_paradise(ROOT / loc / "ski-paradise.html")
        replace_svgs_in_travel_guide(ROOT / loc / "travel-guide.html")

    gallery_files = [
        "angelina-and-taylor-gallery.html",
        "chease-and-jessica-gallery.html",
        "jennifer-and-tyler-gallery.html",
        "raimondo-and-selena-gallery.html",
    ]
    for loc in ["hu", "en"]:
        for g in gallery_files:
            replace_svgs_in_gallery(ROOT / loc / g)

    print("\nAll files verified/updated successfully!")

if __name__ == "__main__":
    main()
