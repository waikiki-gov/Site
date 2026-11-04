#!/usr/bin/env python3
"""
Alias entry point for scripts/svg_generators/gen_site_svgs.py.

Runs the master SVG generation and page injection orchestrator.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen_site_svgs import main  # noqa: E402

if __name__ == "__main__":
    main()

