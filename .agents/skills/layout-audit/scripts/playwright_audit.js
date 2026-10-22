#!/usr/bin/env node
/**
 * Playwright Multi-Viewport & Contrast Layout Auditor
 * Part of the 'layout-audit' skill.
 *
 * Checks:
 *   1. Horizontal Viewport Spill (scrollWidth > clientWidth)
 *   2. Container & Text Clipping (text overflowing containers with overflow:hidden/clip)
 *   3. Element Collisions & Overlaps (non-background sibling cards colliding)
 *   4. WCAG Color Contrast (text vs effective background color)
 *   5. Broken Media (images with 0 natural width/height)
 *
 * Viewports: 2560x1440 (Ultra-wide), 1280x800 (Standard), 430x932 (Mobile)
 * Themes: Light Mode, Dark Mode (body-dark)
 */

let playwright;
try {
    playwright = require('/usr/local/lib/node_modules/playwright');
} catch (e) {
    try {
        playwright = require('playwright');
    } catch (e2) {
        console.error(JSON.stringify({ error: "Playwright not found. Install via: npm install -g playwright" }));
        process.exit(1);
    }
}

const { chromium } = playwright;
const path = require('path');
const fs = require('fs');

const VIEWPORTS = {
    '2560': { width: 2560, height: 1440, label: '2560px Desktop (Ultra-wide)' },
    '1280': { width: 1280, height: 800, label: '1280px Desktop (Standard)' },
    '430':  { width: 430,  height: 932, label: '430px Mobile (Phone)' }
};

const THEMES = ['light', 'dark'];

function evaluatePage(isDark) {
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

    // 1. Horizontal Viewport Overflow Check
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

    // 3. Sibling Overlaps
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
        if (document.body) {
            const bodyBg = parseRgb(window.getComputedStyle(document.body).backgroundColor);
            if (bodyBg && bodyBg.a >= 0.85) return bodyBg;
        }
        return isDark ? { r: 10, g: 25, b: 40, a: 1 } : { r: 251, g: 247, b: 240, a: 1 };
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

    // 5. Broken Media Check
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
}

async function runAudit(filePath, requestedWidths, requestedModes) {
    const absPath = path.resolve(filePath);
    const fileUrl = 'file://' + absPath;

    const browser = await chromium.launch({ headless: true });
    const results = { file: path.basename(filePath), path: filePath, runs: [] };

    try {
        for (const wKey of requestedWidths) {
            if (!VIEWPORTS[wKey]) continue;
            const vp = VIEWPORTS[wKey];

            for (const mode of requestedModes) {
                const isDark = (mode === 'dark');
                const context = await browser.newContext({
                    viewport: { width: vp.width, height: vp.height },
                    colorScheme: isDark ? 'dark' : 'light'
                });
                const page = await context.newPage();

                // Inject no-transition style
                await page.addInitScript(() => {
                    const style = document.createElement('style');
                    style.innerHTML = '* { transition: none !important; animation-duration: 0.001s !important; }';
                    document.head.appendChild(style);
                });

                await page.goto(fileUrl, { waitUntil: 'domcontentloaded' });
                // Force all lazy images to load eagerly and wait for them to finish
                await page.evaluate(async () => {
                    document.querySelectorAll('img[loading="lazy"]').forEach(img => {
                        img.loading = 'eager';
                    });
                    await Promise.all(Array.from(document.querySelectorAll('img')).map(img => {
                        if (img.complete) return Promise.resolve();
                        return new Promise(resolve => {
                            img.addEventListener('load', resolve, { once: true });
                            img.addEventListener('error', resolve, { once: true });
                            setTimeout(resolve, 2500);
                        });
                    }));
                });
                await page.waitForTimeout(150);

                const auditData = await page.evaluate(evaluatePage, isDark);

                const issues = [];
                if (auditData.horizontalOverflow) {
                    const hov = auditData.horizontalOverflow;
                    issues.push(`Horizontal Scroll Overflow: +${hov.excess}px (Scroll: ${hov.scrollWidth}px vs Viewport: ${hov.docWidth}px)`);
                }
                if (auditData.clippedElements) {
                    auditData.clippedElements.forEach(cl => {
                        issues.push(`Text Clipped (${cl.axis}): ${cl.selector} "${cl.textSnippet}"`);
                    });
                }
                if (auditData.overlappingElements) {
                    auditData.overlappingElements.forEach(ov => {
                        issues.push(`Element Collision: ${ov.el1} overlaps with ${ov.el2} (${ov.overlapArea}px²)`);
                    });
                }
                if (auditData.contrastIssues) {
                    auditData.contrastIssues.slice(0, 4).forEach(ct => {
                        issues.push(`Low Contrast: ${ct.selector} ratio ${ct.ratio}:1 (fg: ${ct.color}, bg: ${ct.bgColor}) "${ct.sampleText}"`);
                    });
                }
                if (auditData.brokenMedia) {
                    auditData.brokenMedia.forEach(bm => {
                        issues.push(`Broken Image: ${bm.selector} (src: ${bm.src})`);
                    });
                }

                results.runs.push({
                    width: vp.width,
                    label: vp.label,
                    mode: mode,
                    issues: issues,
                    raw: auditData
                });

                await context.close();
            }
        }
    } finally {
        await browser.close();
    }

    return results;
}

// CLI Execution
if (require.main === module) {
    const args = process.argv.slice(2);
    const targetFile = args.find(a => !a.startsWith('--')) || 'hu/space-research.html';
    const widthsArg = (args.find(a => a.startsWith('--widths=')) || '').replace('--widths=', '') || '2560,1280,430';
    const modesArg = (args.find(a => a.startsWith('--modes=')) || '').replace('--modes=', '') || 'light,dark';

    const reqWidths = widthsArg.split(',').map(s => s.trim());
    const reqModes = modesArg.split(',').map(s => s.trim().toLowerCase());

    runAudit(targetFile, reqWidths, reqModes).then(res => {
        console.log(JSON.stringify(res, null, 2));
    }).catch(err => {
        console.error(JSON.stringify({ error: err.message }));
        process.exit(1);
    });
}

module.exports = { runAudit };
