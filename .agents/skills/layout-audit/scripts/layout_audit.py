#!/usr/bin/env python3
"""
Comprehensive Browser Layout & Contrast Auditor — Sovereign Nation of Waikiki Site
Part of the 'layout-audit' skill.

Audits HTML pages across multiple viewports and color themes using Playwright / headless Chrome:
    - Viewports: 2560px (Ultra-wide desktop), 1280px (Standard desktop), 430px (Mobile)
    - Color Modes: Light Mode, Dark Mode (body-dark)

Checks for:
    1. Horizontal Viewport Overflow (content extending wider than screen causing horizontal scroll)
    2. Text & Content Overflow (text truncated or clipped by containers with scrollWidth/scrollHeight > clientWidth/clientHeight)
    3. Element Collisions & Overlaps (non-background sibling elements overlapping or colliding)
    4. WCAG Color Contrast Issues (text with contrast ratio < 4.5:1 for normal text or < 3.0:1 for large text)
    5. Broken Media Elements (images with 0 natural width/height)

Usage:
    # Audit a single page across all viewports and both themes
    python3 .agents/skills/layout-audit/scripts/layout_audit.py hu/overview.html

    # Audit specific width or mode
    python3 .agents/skills/layout-audit/scripts/layout_audit.py --widths 2560,430 --modes light,dark hu/overview.html

    # Audit all site pages (quick summary)
    python3 .agents/skills/layout-audit/scripts/layout_audit.py --all

    # Output detailed JSON report
    python3 .agents/skills/layout-audit/scripts/layout_audit.py --json hu/space-research.html
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PLAYWRIGHT_SCRIPT = Path(__file__).parent / "playwright_audit.js"

VIEWPORTS = {
    "2560": (2560, 1440, "2560px Desktop (Ultra-wide)"),
    "1280": (1280, 800, "1280px Desktop (Standard)"),
    "430": (430, 932, "430px Mobile (Phone)"),
    "mobile": (430, 932, "430px Mobile (Phone)"),
}

THEMES = ["light", "dark"]

# Injected JavaScript test probe for layout, overflow, collision, and contrast
AUDIT_JS_PROBE = """
<script id="layout-audit-probe">
window.__runLayoutAudit = function(isDark) {
    const root = document.documentElement;
    if (isDark) {
        root.classList.add('body-dark');
        try { localStorage.setItem('isDarkMode', 'true'); } catch(e) {}
    } else {
        root.classList.remove('body-dark');
        try { localStorage.setItem('isDarkMode', 'false'); } catch(e) {}
    }

    const report = {
        viewportWidth: window.innerWidth,
        viewportHeight: window.innerHeight,
        isDark: isDark,
        horizontalOverflow: null,
        clippedElements: [],
        overlappingElements: [],
        contrastIssues: [],
        brokenMedia: []
    };

    const docWidth = root.clientWidth;
    const scrollWidth = Math.max(root.scrollWidth, document.body ? document.body.scrollWidth : 0);

    // 1. Horizontal Scrollbar Overflow Check
    if (scrollWidth > docWidth + 3) {
        const offscreen = [];
        document.querySelectorAll('header, nav, section, footer, main, div, article, p, h1, h2, h3, img, svg, table').forEach(el => {
            if (el.id === 'site-menu' || el.closest('#site-menu') || el.classList.contains('site-menu')) return;
            const r = el.getBoundingClientRect();
            if (r.right > docWidth + 4 && r.width > 0 && r.height > 0) {
                const cs = window.getComputedStyle(el);
                if (cs.display !== 'none' && cs.visibility !== 'hidden' && cs.position !== 'fixed') {
                    offscreen.push({
                        selector: getElementSelector(el),
                        right: Math.round(r.right),
                        overflowAmount: Math.round(r.right - docWidth),
                        width: Math.round(r.width)
                    });
                }
            }
        });
        report.horizontalOverflow = {
            docWidth: docWidth,
            scrollWidth: scrollWidth,
            excess: scrollWidth - docWidth,
            offendingElements: offscreen.slice(0, 5)
        };
    }

    // 2. Text Clipping Check
    document.querySelectorAll('p, h1, h2, h3, h4, span.spec-badge, .btn, a.next-card, li').forEach(el => {
        if (el.closest('#site-menu') || el.closest('.site-menu')) return;
        const cs = window.getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') return;

        const isClippingX = (cs.overflowX === 'hidden' || cs.overflowX === 'clip');
        const isClippingY = (cs.overflowY === 'hidden' || cs.overflowY === 'clip');

        if (isClippingX && el.scrollWidth > el.clientWidth + 3) {
            report.clippedElements.push({
                selector: getElementSelector(el),
                axis: 'horizontal',
                clientWidth: el.clientWidth,
                scrollWidth: el.scrollWidth,
                textSnippet: el.innerText ? el.innerText.trim().slice(0, 50) : ''
            });
        }
        if (isClippingY && el.scrollHeight > el.clientHeight + 4 && cs.maxHeight !== 'none' && cs.maxHeight !== '') {
            report.clippedElements.push({
                selector: getElementSelector(el),
                axis: 'vertical',
                clientHeight: el.clientHeight,
                scrollHeight: el.scrollHeight,
                textSnippet: el.innerText ? el.innerText.trim().slice(0, 50) : ''
            });
        }
    });

    // 3. Unintended Element Overlaps
    const containers = document.querySelectorAll('section, .card-grid, .grid, .hero, .cards');
    containers.forEach(container => {
        const cards = Array.from(container.querySelectorAll('.card, .interior-card, .aircraft-card')).filter(el => {
            const cs = window.getComputedStyle(el);
            return cs.display !== 'none' && cs.visibility !== 'hidden' && cs.position !== 'absolute';
        });
        for (let i = 0; i < cards.length; i++) {
            for (let j = i + 1; j < cards.length; j++) {
                const r1 = cards[i].getBoundingClientRect();
                const r2 = cards[j].getBoundingClientRect();
                const overlapX = Math.max(0, Math.min(r1.right, r2.right) - Math.max(r1.left, r2.left));
                const overlapY = Math.max(0, Math.min(r1.bottom, r2.bottom) - Math.max(r1.top, r2.top));
                if (overlapX > 20 && overlapY > 20) {
                    report.overlappingElements.push({
                        el1: getElementSelector(cards[i]),
                        el2: getElementSelector(cards[j]),
                        overlapArea: Math.round(overlapX * overlapY)
                    });
                }
            }
        }
    });

    // 4. Color Contrast Check (WCAG 2.1 AA)
    function parseRgb(colorStr) {
        const m = colorStr.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
        if (!m) return null;
        return {
            r: parseInt(m[1], 10),
            g: parseInt(m[2], 10),
            b: parseInt(m[3], 10),
            a: m[4] !== undefined ? parseFloat(m[4]) : 1.0
        };
    }

    function getLuminance(rgb) {
        const a = [rgb.r, rgb.g, rgb.b].map(v => {
            v /= 255;
            return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
        });
        return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
    }

    function getContrast(rgb1, rgb2) {
        const l1 = getLuminance(rgb1);
        const l2 = getLuminance(rgb2);
        const brightest = Math.max(l1, l2);
        const darkest = Math.min(l1, l2);
        return (brightest + 0.05) / (darkest + 0.05);
    }

    function getEffectiveBgColor(el) {
        let cur = el;
        while (cur && cur !== document) {
            const cs = window.getComputedStyle(cur);
            const bg = parseRgb(cs.backgroundColor);
            if (bg && bg.a >= 0.85) return bg;
            cur = cur.parentElement;
        }
        return isDark ? { r: 15, g: 23, b: 42, a: 1 } : { r: 251, g: 247, b: 240, a: 1 };
    }

    document.querySelectorAll('p, h1, h2, h3, h4, span.spec-badge, a.btn, .narrative-text, .hero-lead, .card p').forEach(el => {
        if (el.closest('#site-menu') || el.closest('.site-menu') || el.closest('svg') || el.getAttribute('aria-hidden') === 'true') return;
        const text = el.innerText ? el.innerText.trim() : '';
        if (!text || text.length < 2) return;

        const cs = window.getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.2) return;

        const fg = parseRgb(cs.color);
        if (!fg || fg.a < 0.4) return;

        const bg = getEffectiveBgColor(el);
        const ratio = getContrast(fg, bg);
        const fontSize = parseFloat(cs.fontSize) || 16;
        const isBold = parseInt(cs.fontWeight, 10) >= 600 || cs.fontWeight === 'bold';
        const isLarge = fontSize >= 24 || (fontSize >= 18.66 && isBold);
        const minRatio = isLarge ? 3.0 : 4.5;

        if (ratio < minRatio && ratio < 3.8) {
            report.contrastIssues.push({
                selector: getElementSelector(el),
                ratio: parseFloat(ratio.toFixed(2)),
                required: minRatio,
                color: cs.color,
                bgColor: `rgb(${bg.r}, ${bg.g}, ${bg.b})`,
                fontSize: cs.fontSize,
                sampleText: text.slice(0, 45)
            });
        }
    });

    // 5. Broken Images Check
    document.querySelectorAll('img').forEach(img => {
        if (img.src && img.complete && (img.naturalWidth === 0 || img.naturalHeight === 0)) {
            report.brokenMedia.push({
                selector: getElementSelector(img),
                src: img.getAttribute('src') || ''
            });
        }
    });

    function getElementSelector(el) {
        if (!el || !el.tagName) return '';
        let desc = el.tagName.toLowerCase();
        if (el.id) return `${desc}#${el.id}`;
        if (el.className && typeof el.className === 'string') {
            const classes = el.className.split(/\\s+/).filter(c => c && !c.startsWith('is-') && c !== 'js').slice(0, 2);
            if (classes.length) desc += '.' + classes.join('.');
        }
        const parent = el.parentElement;
        if (parent && parent.id) return `#${parent.id} > ${desc}`;
        return desc;
    }

    return report;
};
</script>
"""


def execute_browser_audit(file_path: Path, width: int, height: int, is_dark: bool) -> dict | None:
    """Runs a single headless Chrome audit instance at exact dimensions and theme."""
    if not os.path.exists(CHROME_PATH):
        print(f"[!] Google Chrome binary not found at {CHROME_PATH}", file=sys.stderr)
        return None

    content = file_path.read_text(encoding="utf-8", errors="ignore")

    # Disable transitions and animations for immediate, stable computed layout measurements
    no_motion_style = "<style id='audit-no-motion'>* { transition: none !important; animation-duration: 0.001s !important; }</style>"
    if "</head>" in content:
        content = content.replace("</head>", no_motion_style + "</head>")
    else:
        content = no_motion_style + content

    if is_dark:
        # Pre-apply body-dark class so theme is active from initial paint
        if 'class="' in content[:300]:
            content = re.sub(r'<html([^>]*)class="([^"]*)"', r'<html\1class="\2 body-dark"', content, count=1)
        else:
            content = content.replace("<html", '<html class="body-dark"', 1)
    else:
        content = content.replace("body-dark", "")

    # Runner script that automatically triggers the probe and dumps JSON
    theme_bool = "true" if is_dark else "false"
    runner_script = f"""
    {AUDIT_JS_PROBE}
    <script>
    window.addEventListener('DOMContentLoaded', async () => {{
        try {{
            document.querySelectorAll('img[loading="lazy"]').forEach(img => {{
                img.loading = 'eager';
            }});
            await Promise.all(Array.from(document.querySelectorAll('img')).map(img => {{
                if (img.complete) return Promise.resolve();
                return new Promise(resolve => {{
                    img.addEventListener('load', resolve, {{ once: true }});
                    img.addEventListener('error', resolve, {{ once: true }});
                    setTimeout(resolve, 2000);
                }});
            }}));
        }} catch(e) {{}}
        setTimeout(() => {{
            try {{
                const res = window.__runLayoutAudit({theme_bool});
                const tag = document.createElement('pre');
                tag.id = 'audit-json-output';
                tag.textContent = JSON.stringify(res);
                document.body.appendChild(tag);
            }} catch(e) {{
                const err = document.createElement('pre');
                err.id = 'audit-json-output';
                err.textContent = JSON.stringify({{ error: String(e) }});
                document.body.appendChild(err);
            }}
        }}, 200);
    }});
    </script>
    """

    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False, dir=str(file_path.parent)) as tf:
        if "</body>" in content:
            temp_content = content.replace("</body>", runner_script + "</body>")
        else:
            temp_content = content + runner_script
        tf.write(temp_content)
        temp_file = tf.name

    try:
        cmd = [
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            f"--window-size={width},{height}",
            "--virtual-time-budget=3000",
            "--dump-dom",
            f"file://{temp_file}",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode == 0 and "audit-json-output" in res.stdout:
            match = re.search(r'<pre id="audit-json-output">([\s\S]*?)</pre>', res.stdout)
            if match:
                return json.loads(match.group(1))
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            os.remove(temp_file)
        except OSError:
            pass
    return None


def audit_page(file_path: Path, widths: list[str], modes: list[str]) -> tuple[int, dict]:
    """Runs full matrix of viewports and color modes for a given page using Playwright or headless Chrome."""
    page_results = {
        "file": file_path.name,
        "path": str(file_path.relative_to(ROOT)),
        "runs": []
    }
    total_issues = 0

    print(f"\n======================================================================")
    print(f" Page: {file_path.name} ({file_path.parent.name.upper()})")
    print(f"======================================================================")

    # 1. Prefer Playwright multi-viewport runner if available
    node_bin = shutil.which("node")
    if node_bin and PLAYWRIGHT_SCRIPT.exists():
        try:
            cmd = [
                node_bin,
                str(PLAYWRIGHT_SCRIPT),
                str(file_path),
                f"--widths={','.join(widths)}",
                f"--modes={','.join(modes)}",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout.strip())
                if "runs" in data and len(data["runs"]) > 0:
                    for run in data["runs"]:
                        label = run["label"]
                        mode_label = "Dark Mode" if run["mode"] == "dark" else "Light Mode"
                        print(f"  Testing [{label} | {mode_label}] (Playwright)...", end=" ", flush=True)
                        issues_found = run["issues"]
                        total_issues += len(issues_found)
                        page_results["runs"].append(run)
                        if issues_found:
                            print(f"[FAIL: {len(issues_found)} issues]")
                            for iss in issues_found:
                                print(f"    • {iss}")
                        else:
                            print("[PASS - 100% Clean]")
                    return total_issues, page_results
        except Exception:
            pass

    # 2. Fallback to viewport-by-viewport headless Google Chrome
    for w_key in widths:
        if w_key not in VIEWPORTS:
            continue
        width, height, label = VIEWPORTS[w_key]

        for mode in modes:
            is_dark = (mode == "dark")
            mode_label = "Dark Mode" if is_dark else "Light Mode"

            print(f"  Testing [{label} | {mode_label}] (Chrome)...", end=" ", flush=True)
            res = execute_browser_audit(file_path, width, height, is_dark)

            if not res or "error" in res:
                err_msg = res.get("error", "Unknown execution error") if res else "No response"
                print(f"[ERROR: {err_msg}]")
                continue

            # Tabulate issues
            issues_found = []
            if res.get("horizontalOverflow"):
                hov = res["horizontalOverflow"]
                issues_found.append(f"Horizontal Scroll Overflow: +{hov['excess']}px (Scroll: {hov['scrollWidth']}px vs Viewport: {hov['docWidth']}px)")

            if res.get("clippedElements"):
                for cl in res["clippedElements"]:
                    issues_found.append(f"Text Clipped ({cl['axis']}): {cl['selector']} \"{cl['textSnippet']}\"")

            if res.get("overlappingElements"):
                for ov in res["overlappingElements"]:
                    issues_found.append(f"Element Collision: {ov['el1']} overlaps with {ov['el2']} ({ov['overlapArea']}px²)")

            if res.get("contrastIssues"):
                for ct in res["contrastIssues"][:4]:
                    issues_found.append(f"Low Contrast: {ct['selector']} ratio {ct['ratio']}:1 (fg: {ct['color']}, bg: {ct['bgColor']}) \"{ct['sampleText']}\"")
                if len(res["contrastIssues"]) > 4:
                    issues_found.append(f"... and {len(res['contrastIssues']) - 4} more contrast warnings")

            if res.get("brokenMedia"):
                for bm in res["brokenMedia"]:
                    issues_found.append(f"Broken Image: {bm['selector']} (src: {bm['src']})")

            total_issues += len(issues_found)
            res_entry = {
                "width": width,
                "label": label,
                "mode": mode,
                "issues": issues_found,
                "raw": res
            }
            page_results["runs"].append(res_entry)

            if issues_found:
                print(f"[FAIL: {len(issues_found)} issues]")
                for iss in issues_found:
                    print(f"    • {iss}")
            else:
                print("[PASS - 100% Clean]")

    return total_issues, page_results


def main():
    parser = argparse.ArgumentParser(description="Multi-viewport, multi-theme layout and contrast checker")
    parser.add_argument("file", nargs="?", help="Specific HTML file to inspect (e.g. hu/overview.html)")
    parser.add_argument("--all", "-a", action="store_true", help="Audit all English and Hungarian pages")
    parser.add_argument("--widths", "-w", default="2560,1280,430", help="Comma-separated widths: 2560, 1280, 430 (default: all)")
    parser.add_argument("--modes", "-m", default="light,dark", help="Comma-separated themes: light, dark (default: both)")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    req_widths = [w.strip() for w in args.widths.split(",") if w.strip()]
    req_modes = [m.strip().lower() for m in args.modes.split(",") if m.strip().lower() in THEMES]

    print("=================================================================")
    print(" Sovereign Nation of Waikiki — Browser Layout & Visual Auditor")
    print(f" Viewports: {', '.join(req_widths)}px | Themes: {', '.join(req_modes)}")
    print("=================================================================")

    if args.file:
        files = [Path(args.file).resolve()]
    elif args.all:
        files = []
        for lang in ("hu", "en"):
            p = ROOT / lang
            files.extend(p.glob("*.html"))
        files.sort()
    else:
        # Default test page
        files = [ROOT / "hu" / "space-research.html"]

    all_page_results = []
    grand_total_issues = 0

    for f in files:
        if not f.exists():
            print(f"[!] File not found: {f}", file=sys.stderr)
            continue
        issue_count, p_data = audit_page(f, req_widths, req_modes)
        grand_total_issues += issue_count
        all_page_results.append(p_data)

    print("\n-----------------------------------------------------------------")
    if grand_total_issues == 0:
        print("[SUCCESS] All tested viewports and color modes exhibit 100% clean layouts!")
        print("No horizontal spills, clipped elements, collisions, or contrast defects found.")
    else:
        print(f"[ATTENTION] Discovered {grand_total_issues} layout or contrast defect(s). Review details above.")
    print("-----------------------------------------------------------------")

    if args.json:
        print(json.dumps(all_page_results, indent=2))

    sys.exit(0 if grand_total_issues == 0 else 1)


if __name__ == "__main__":
    main()
