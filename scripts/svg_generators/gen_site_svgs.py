#!/usr/bin/env python3
"""
Master SVG Generation and Page Injection Orchestrator for Sovereign Nation of Waikiki.

Coordinates procedural generation of site illustrations and card artwork across pages:
  - Ski Paradise (ski-paradise.html): Summit elevation chart and 5 alpine resort cards
  - Travel Guide (travel-guide.html): 15 luxury hotel and sanctuary cards
  - Infrastructure (infrastructure.html): Tallest structures chart and 10 landmark cards
  - Nova Aurelia (nova-aurelia.html): 4 imperial metropolis district cards

Hero SVGs are canonical standalone files in icons/*/hero-art.svg and are NOT generated here.

Usage:
  python3 scripts/svg_generators/gen_site_svgs.py                 # Generate all 4 page suites
  python3 scripts/svg_generators/gen_site_svgs.py --site ski      # Generate ski paradise only
  python3 scripts/svg_generators/gen_site_svgs.py --site travel   # Generate travel guide only
  python3 scripts/svg_generators/gen_site_svgs.py --site infra    # Generate infrastructure only
  python3 scripts/svg_generators/gen_site_svgs.py --site nova-aurelia  # Generate Nova Aurelia only
  python3 scripts/svg_generators/gen_site_svgs.py --include-maps  # Also generate linked maps
  python3 scripts/svg_generators/gen_site_svgs.py --everything    # Generate pages, maps, and other SVGs
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gen_infrastructure_svgs
import gen_nova_aurelia_svgs
import gen_ski_svgs
import gen_travel_svgs

PAGE_GENERATORS = {
    "ski": ("Ski Paradise (ski-paradise.html)", gen_ski_svgs.main),
    "travel": ("Travel Guide (travel-guide.html)", gen_travel_svgs.main),
    "infra": ("Infrastructure (infrastructure.html)", gen_infrastructure_svgs.main),
    "nova-aurelia": ("Nova Aurelia (nova-aurelia.html)", gen_nova_aurelia_svgs.main),
}

PAGE_ALIASES = {
    "ski-paradise": "ski",
    "travel-guide": "travel",
    "infrastructure": "infra",
    "nova_aurelia": "nova-aurelia",
    "nova": "nova-aurelia",
}


def run_maps() -> None:
    """Generate procedural linked vector maps."""
    import gen_chameleon_map
    import gen_infrastructure_map
    import gen_palm_map
    import gen_ski_maps
    import gen_world_map

    print("\n--- Generating Linked Maps ---")
    gen_ski_maps.main()
    gen_infrastructure_map.main()
    gen_palm_map.main()
    gen_world_map.main()
    gen_chameleon_map.main()


def run_other() -> None:
    """Generate other procedural SVGs."""
    import gen_banking_svgs
    import gen_nature_svgs
    import gen_plane
    import gen_space_svgs

    print("\n--- Generating Other Localized & Nature SVGs ---")
    gen_banking_svgs.main()
    gen_space_svgs.main()
    gen_plane.main()
    gen_nature_svgs.main()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Master SVG generator for Sovereign Nation of Waikiki pages."
    )
    parser.add_argument(
        "--site",
        "--page",
        dest="target",
        default="all",
        help="Target site/page to generate: all, ski, travel, infra, nova-aurelia (default: all)",
    )
    parser.add_argument(
        "--include-maps",
        action="store_true",
        help="Also run procedural map generators (ski, mobility, palm, world, chameleon)",
    )
    parser.add_argument(
        "--include-other",
        action="store_true",
        help="Also run other procedural SVG generators (banking, space, plane deck, nature)",
    )
    parser.add_argument(
        "--everything",
        action="store_true",
        help="Run all site page illustrations, maps, and other procedural SVGs",
    )
    args = parser.parse_args()

    target = args.target.strip().lower()
    target = PAGE_ALIASES.get(target, target)

    start_time = time.time()
    print("=" * 65)
    print("Sovereign Nation of Waikiki — SVG Generation Pipeline")
    print("Note: Hero SVGs are canonical standalone files and are NOT procedurally generated.")
    print("=" * 65)

    if target == "all":
        selected_pages = list(PAGE_GENERATORS.keys())
    elif target in PAGE_GENERATORS:
        selected_pages = [target]
    else:
        valid_targets = ", ".join(["all"] + list(PAGE_GENERATORS.keys()))
        sys.exit(f"Unknown target '{args.target}'. Valid targets: {valid_targets}")

    for page_key in selected_pages:
        label, func = PAGE_GENERATORS[page_key]
        print(f"\n[Site Suite: {label}]")
        t0 = time.time()
        func()
        print(f"Completed in {time.time() - t0:.2f}s")

    if args.include_maps or args.everything:
        run_maps()

    if args.include_other or args.everything:
        run_other()

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f"All requested SVG generation finished successfully in {elapsed:.2f}s.")
    print("=" * 65)


if __name__ == "__main__":
    main()
