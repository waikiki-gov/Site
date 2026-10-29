#!/usr/bin/env node
/**
 * Playwright Text Balance & Line Counter
 * Part of the 'text-balance' skill.
 *
 * Measures exact rendered line counts, heights, and characters of cards in multi-card
 * section rows using Range.getClientRects() and computed line-height at 2560px (ultra-wide desktop).
 *
 * Usage:
 *   node .agents/skills/text-balance/scripts/playwright_balance.js hu/space-research.html
 *   node .agents/skills/text-balance/scripts/playwright_balance.js --width=2560 hu/overview.html
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

async function measurePage(filePath, width = 2560, height = 1440) {
    const absPath = path.resolve(filePath);
    if (!fs.existsSync(absPath)) {
        throw new Error(`File does not exist: ${absPath}`);
    }

    const browser = await chromium.launch({ headless: true });
    try {
        const context = await browser.newContext({
            viewport: { width: Number(width), height: Number(height) }
        });
        const page = await context.newPage();

        // Disable animations and transitions for instant layout stabilization
        await page.addInitScript(() => {
            const style = document.createElement('style');
            style.innerHTML = '* { transition: none !important; animation: none !important; }';
            document.head.appendChild(style);
        });

        await page.goto(`file://${absPath}`, { waitUntil: 'domcontentloaded' });

        // Ensure web fonts are fully loaded for precise typographic line measurements
        await page.evaluate(async () => {
            if (document.fonts) await document.fonts.ready;
        });
        await page.waitForTimeout(100);

        const results = await page.evaluate(() => {
            // Temporarily unhide tabpanes for accurate measurement of cards inside tabs
            document.querySelectorAll('.aircraft-tab-pane, [role="tabpanel"], .tab-pane').forEach(el => el.style.display = 'block');

            const data = {};
            document.querySelectorAll('section').forEach(sec => {
                const secId = sec.id || sec.className.split(' ')[0] || 'section';
                const rawCards = Array.from(sec.querySelectorAll('.card, [class*="-card"], [class^="card-"]')).filter(el => {
                    const cls = typeof el.className === 'string' ? el.className : '';
                    if (/-(title|desc|description|role|name|image|img|icon|badge|meta|header|footer|body|actions|label|wrapper|inner|content|banner|tagline)/.test(cls)) return false;
                    if (/card-(grid|list|container|group|icon|media|image|img|header|body|footer|actions)/.test(cls)) return false;
                    return true;
                });
                const cards = rawCards.filter(el => !rawCards.some(other => other !== el && el.contains(other)));
                if (cards.length > 1) {
                    const cardList = [];
                    cards.forEach((c, idx) => {
                        const h3 = c.querySelector('h2, h3, h4, [class*="title"], [class*="name"]');
                        const ps = Array.from(c.querySelectorAll('p, [class*="description"], [class*="desc"], [class*="bio"], [class*="text"]'));
                        let p = ps.find(el => /(description|desc|bio)/.test(el.className));
                        if (!p && ps.length > 0) {
                            p = ps.reduce((max, el) => (el.innerText.trim().length > max.innerText.trim().length ? el : max), ps[0]);
                        }
                        if (p) {
                            let lines = 0;
                            try {
                                const range = document.createRange();
                                range.selectNodeContents(p);
                                const rects = range.getClientRects();
                                if (rects && rects.length > 0) {
                                    lines = rects.length;
                                }
                            } catch (e) {}

                            if (!lines || lines <= 1) {
                                const cs = window.getComputedStyle(p);
                                const lh = parseFloat(cs.lineHeight) || 24;
                                lines = Math.round(p.offsetHeight / lh);
                            }

                            cardList.push({
                                index: idx + 1,
                                title: h3 ? h3.innerText.trim() : `Card ${idx + 1}`,
                                text: p.innerText.trim(),
                                lines: Math.max(1, lines),
                                height: p.offsetHeight,
                                chars: p.innerText.trim().length,
                                words: p.innerText.trim().split(/\s+/).filter(Boolean).length
                            });
                        }
                    });
                    if (cardList.length > 1) {
                        data[secId] = cardList;
                    }
                }
            });
            return data;
        });

        await context.close();
        return results;
    } finally {
        await browser.close();
    }
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const targetFile = args.find(a => !a.startsWith('--')) || 'hu/space-research.html';
    const widthArg = (args.find(a => a.startsWith('--width=')) || '').replace('--width=', '') || '2560';

    measurePage(targetFile, parseInt(widthArg, 10)).then(res => {
        console.log(JSON.stringify(res, null, 2));
    }).catch(err => {
        console.error(JSON.stringify({ error: err.message }));
        process.exit(1);
    });
}

module.exports = { measurePage };
