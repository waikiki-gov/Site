#!/usr/bin/env python3
"""
Script to safely replace or insert .aircraft-watermark watermark <img> tags in hu/space-research.html and en/space-research.html.
Ensures watermarks are placed strictly inside each <div class="card"> without moving any tags or adding empty lines.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAP = [
    ("Delta III A", "rocket-delta-3a.svg"),
    ("Space Shuttle", "rocket-shuttle.svg"),
    ("Saturn X", "rocket-saturn-x.svg"),
    ("Falcon Heavy", "rocket-falcon-heavy.svg"),
    ("Falcon", "rocket-falcon.svg"),
    ("Delta III B", "rocket-delta-3b.svg"),
    ("Space Shuttle v2", "rocket-shuttle-v2.svg"),
    ("Saturn Nova", "rocket-saturn-nova.svg"),
    ("Falcon v2", "rocket-falcon-v2.svg"),
    ("Big Falcon Rocket", "rocket-bfr.svg"),
    ("Delta IV", "rocket-delta-4.svg"),
    ("Bolygóközi Űrsikló", "rocket-interplanetary-shuttle.svg"),
    ("Interplanetary Shuttle", "rocket-interplanetary-shuttle.svg"),
]

CARD_PATTERN = re.compile(r'(<div class="card">[\s\S]*?</ul>)\s*(?:<img\b[^>]*rocket-[^>]*>\s*)?(</div>)')

def repl_card(m):
    card_body = m.group(1).rstrip()
    h3_match = re.search(r'<h3>(.*?)</h3>', card_body)
    if not h3_match:
        return m.group(0)

    h3_title = h3_match.group(1).strip()
    matched_svg = next((svg for title, svg in MAP if title == h3_title), None)
    if not matched_svg:
        raise ValueError(f"No matching SVG for '{h3_title}'")

    return (
        f'{card_body}\n'
        f'                    <img src="../icons/rockets/{matched_svg}" alt="" class="aircraft-watermark aircraft-watermark--plane" aria-hidden="true" />\n'
        f'                </div>'
    )

def process_file(filepath: Path):
    content = filepath.read_text(encoding="utf-8")

    # Clean legacy wireframe blocks if present
    content = re.sub(r'\s*<div class="rocket-wireframe-wrapper">.*?</div>\s*</div>', '', content, flags=re.DOTALL)

    fleet_start = content.find('<section id="fleet"')
    if fleet_start == -1:
        print(f"Could not find #fleet in {filepath}")
        return

    fleet_end = content.find('</section>', fleet_start)
    if fleet_end == -1:
        print(f"Could not find </section> for #fleet in {filepath}")
        return

    fleet_html = content[fleet_start:fleet_end]
    new_fleet_html, count = CARD_PATTERN.subn(repl_card, fleet_html)

    if count != 12:
        raise ValueError(f"{filepath}: Expected 12 cards in #fleet, but matched {count}")

    new_content = content[:fleet_start] + new_fleet_html + content[fleet_end:]

    # Ensure no empty lines
    cleaned_lines = [line for line in new_content.splitlines() if line.strip() or line == ""]
    final_content = "\n".join(l for l in cleaned_lines if l.strip()) + "\n"

    filepath.write_text(final_content, encoding="utf-8")
    print(f"Successfully updated {filepath}: {count} cards processed, 0 empty lines, all watermarks inside cards.")

def main():
    for loc in ["hu", "en"]:
        process_file(ROOT / loc / "space-research.html")

if __name__ == "__main__":
    main()
