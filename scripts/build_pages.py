#!/usr/bin/env python3
"""
Rebuild the shared page chrome for every localized page of the Waikiki site.

What it does for each page in en/, hu/, en/bio/ and hu/bio/:
  * <head>    injects SEO meta, fonts, hreflang links and the no-flash theme script
  * header    brand, primary navigation, language pill, theme toggle, menu button
  * menu      full-screen grouped site map with live capital clock
  * hero      converts legacy hero markup into the unified `.hero` component
  * subnav    tab bar between the four pages of each royal couple
  * next      "continue the journey" banner linking to the next page
  * footer    grouped site map, motto, legal line

Generated regions are wrapped in <!-- @chrome:NAME --> markers so the script can
be re-run safely after menu or copy changes:

    python3 scripts/build_pages.py            # rebuild everything
    python3 scripts/build_pages.py --check    # report pages that would change
    python3 scripts/build_pages.py --empty    # generate an empty page (en/empty.html and hu/empty.html)
    python3 scripts/build_pages.py --new SLUG # generate a new empty page with the given slug
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "hu")

# --------------------------------------------------------------------------- #
# Site map
# --------------------------------------------------------------------------- #
GROUPS = [
    ("nation", {"en": "Nation", "hu": "Nemzet"}, [
        ("index", {"en": "Home", "hu": "Főoldal"}),
        ("overview", {"en": "Overview", "hu": "Áttekintés"}),
        ("history", {"en": "History", "hu": "Történelem"}),
        ("society", {"en": "Society", "hu": "Társadalom"}),
        ("culture", {"en": "Culture", "hu": "Kultúra"}),
        ("ideology", {"en": "Ideology", "hu": "Ideológia"}),
    ]),
    ("governance", {"en": "Governance", "hu": "Kormányzás"}, [
        ("government", {"en": "Government", "hu": "Kormány"}),
        ("leadership", {"en": "Leadership", "hu": "Vezetés"}),
        ("parties", {"en": "Politics", "hu": "Politika"}),
        ("constitution", {"en": "Constitution", "hu": "Alkotmány"}),
        ("military", {"en": "Military", "hu": "Hadsereg"}),
        ("diplomacy", {"en": "Diplomacy", "hu": "Diplomácia"}),
    ]),
    ("prosperity", {"en": "Prosperity", "hu": "Jólét"}, [
        ("economy", {"en": "Economy", "hu": "Gazdaság"}),
        ("banking-system", {"en": "Banking System", "hu": "Bankrendszer"}),
        ("wealth-fund", {"en": "Wealth Fund", "hu": "Vagyonalap"}),
        ("citizenship", {"en": "Citizenship", "hu": "Állampolgárság"}),
        ("infrastructure", {"en": "Infrastructure", "hu": "Infrastruktúra"}),
        ("space-research", {"en": "Space Research", "hu": "Űrkutatás"}),
    ]),
    ("royal", {"en": "Royal Family", "hu": "Királyi Család"}, [
        ("dynasty", {"en": "The Dynasty", "hu": "A Dinasztia"}),
        ("chease-and-jessica", {"en": "Chease and Jessica", "hu": "Chease és Jessica"}),
        ("raimondo-and-selena", {"en": "Raimondo and Selena", "hu": "Raimondo és Selena"}),
        ("angelina-and-taylor", {"en": "Angelina and Taylor", "hu": "Angelina és Taylor"}),
        ("jennifer-and-tyler", {"en": "Jennifer and Tyler", "hu": "Jennifer és Tyler"}),
    ]),
    ("visit", {"en": "Visit", "hu": "Látogatás"}, [
        ("tourism", {"en": "Tourism", "hu": "Turizmus"}),
        ("sights", {"en": "Sights", "hu": "Látnivalók"}),
        ("nature", {"en": "Nature", "hu": "Természet"}),
        ("travel-guide", {"en": "Travel Guide", "hu": "Utazási Kalauz"}),
        ("visa", {"en": "Visa and Entry", "hu": "Vízum és belépés"}),
        ("faq", {"en": "FAQ", "hu": "GYIK"}),
    ]),
]

PRIMARY_NAV = [
    ("tourism", {"en": "Visit", "hu": "Utazás"}),
    ("society", {"en": "Society", "hu": "Társadalom"}),
    ("economy", {"en": "Economy", "hu": "Gazdaság"}),
    ("government", {"en": "Government", "hu": "Kormány"}),
    ("history", {"en": "History", "hu": "Történelem"}),
    ("dynasty", {"en": "Royal Family", "hu": "Királyi Család"}),
]

COUPLES = ["chease-and-jessica", "raimondo-and-selena", "angelina-and-taylor", "jennifer-and-tyler"]

COUPLE_TABS = [
    ("", {"en": "Overview", "hu": "Áttekintés"}),
    ("-detailed", {"en": "Story", "hu": "Történet"}),
    ("-gallery", {"en": "Gallery", "hu": "Galéria"}),
    ("-private", {"en": "Private Life", "hu": "Magánélet"}),
]

BIOS = ["bio/raimondo", "bio/selena", "bio/angelina", "bio/taylor"]

# Reading order used for the "next chapter" banner.
SEQUENCE: list[str] = []
for _, _, _pages in GROUPS:
    for _slug, _ in _pages:
        SEQUENCE.append(_slug)
        if _slug == "dynasty":
            SEQUENCE.extend(BIOS)
        if _slug in COUPLES:
            SEQUENCE.extend(f"{_slug}{suffix}" for suffix, _ in COUPLE_TABS[1:])

# Short leads for pages that have no photographic hero.
COMPACT_LEADS = {
    "constitution": {
        "en": "The founding charter of the Sovereign Nation of Waikiki, adopted by referendum in 2000, defining the rights of citizens and the separation of powers.",
        "hu": "Waikiki Szuverén Állam alapító okirata, amelyet 2000-ben népszavazással fogadtak el, és amely rögzíti az állampolgárok jogait és a hatalmi ágak szétválasztását.",
    },
    "overview": {
        "en": "Three provinces, one nation and a quarter century of extraordinary growth: the essential facts about Waikiki at a glance.",
        "hu": "Három tartomány, egy nemzet és negyedszázadnyi rendkívüli fejlődés: Waikiki legfontosabb tényei egy pillantásra.",
    },
    "faq": {
        "en": "Clear answers to the questions most often asked about Waikiki's government, economy, society and way of life.",
        "hu": "Világos válaszok a Waikiki kormányzatával, gazdaságával, társadalmával és életmódjával kapcsolatos leggyakoribb kérdésekre.",
    },
}

T = {
    "menu": {"en": "Menu", "hu": "Menü"},
    "close": {"en": "Close", "hu": "Bezárás"},
    "night": {"en": "Night mode", "hu": "Éjszakai mód"},
    "clock_label": {"en": "Local time in the capital", "hu": "Helyi idő a fővárosban"},
    "clock_city": {"en": "Nova Aurelia, Waikiki Province", "hu": "Nova Aurelia, Waikiki tartomány"},
    "weather": {"en": "Sunny", "hu": "Napos"},
    "weather_temp": {"en": "28°C", "hu": "28°C"},
    "motto": {
        "en": "Prosperity, stability and progress, from the Caribbean to the Amazon.",
        "hu": "Jólét, stabilitás és haladás, a Karib-tengertől az Amazonasig.",
    },
    "about": {
        "en": "The official portal of the Nation of Waikiki. Founded 10 March 1999 · Nova Aurelia. This site was generated with AI, any resemblance to real people, countries or institutions is just a coincidence.",
        "hu": "Waikiki Állam hivatalos portálja. Alapítva 1999. március 10-én · Nova Aurelia. Ez az oldal mesterséges intelligenciával készült, bármilyen hasonlóság valós személyekhez, országokhoz vagy intézményekhez pusztán a véletlen műve.",
    },
    "rights": {
        "en": "© 2026 The Sovereign Nation of Waikiki. All rights reserved.",
        "hu": "© 2026 Waikiki Szuverén Állam. Minden jog fenntartva.",
    },
    "to_top": {"en": "Back to top", "hu": "Vissza a tetejére"},
    "scroll": {"en": "Scroll", "hu": "Görgetés"},
    "continue": {"en": "Continue the journey", "hu": "Folytassa az utazást"},
    "lang_name": {"en": "English", "hu": "Magyar"},
    "animate_chip": {"en": "Animate", "hu": "Animáció"},
}

GLOBE_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
    '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z"/></svg>'
)

THEME_ICON = (
    '<svg class="theme-icon" viewBox="0 0 24 24" aria-hidden="true">'
    '<mask id="theme-mask"><rect width="24" height="24" fill="#fff"/><circle class="theme-cut" cx="26" cy="2" r="6" fill="#000"/></mask>'
    '<circle class="theme-core" cx="12" cy="12" r="5" fill="currentColor" mask="url(#theme-mask)"/>'
    '<g class="theme-rays" stroke="currentColor" stroke-width="1.7" stroke-linecap="round">'
    '<path d="M12 1.5v2.2M12 20.3v2.2M1.5 12h2.2M20.3 12h2.2M4.6 4.6l1.5 1.5M17.9 17.9l1.5 1.5M4.6 19.4l1.5-1.5M17.9 6.1l1.5-1.5"/>'
    "</g></svg>"
)

FOOTER_WAVE = (
    '<svg class="footer-wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true">'
    '<path d="M0 50c160 0 160-36 320-36s160 36 320 36 160-36 320-36 160 36 320 36 160-36 160-36V90H0z"/></svg>'
)

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def esc(text: str) -> str:
    return html.escape(text, quote=True)

def strip_tags(fragment: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", fragment)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()

def label_for(slug: str, locale: str) -> str | None:
    for _, _, pages in GROUPS:
        for page_slug, labels in pages:
            if page_slug == slug:
                return labels[locale]
    return None

def group_for(slug: str) -> str:
    base = slug.split("/")[-1]
    if slug.startswith("bio/") or base in ("raimondo-and-bailey-detailed", "family-tree"):
        return "royal"
    for couple in COUPLES:
        if base.startswith(couple):
            return "royal"
    for key, _, pages in GROUPS:
        if any(page_slug == base for page_slug, _ in pages):
            return key
    return "nation"

def group_label(key: str, locale: str) -> str:
    for group_key, labels, _ in GROUPS:
        if group_key == key:
            return labels[locale]
    return ""

def couple_for(slug: str) -> str | None:
    for couple in COUPLES:
        if slug == couple or any(slug == f"{couple}{suffix}" for suffix, _ in COUPLE_TABS[1:]):
            return couple
    return None

class Page:
    """A localized page and its path context."""

    def __init__(self, path: Path):
        self.path = path
        rel = path.relative_to(ROOT)
        self.locale = rel.parts[0]
        self.slug = "/".join(rel.parts[1:])[: -len(".html")]
        self.depth = len(rel.parts) - 1  # en/x.html -> 1, en/bio/x.html -> 2
        self.root_prefix = "../" * self.depth
        self.locale_prefix = "../" * (self.depth - 1)
        self.group = group_for(self.slug)

    def href(self, slug: str) -> str:
        return f"{self.locale_prefix}{slug}.html"

    def other_locale_href(self) -> str:
        other = "hu" if self.locale == "en" else "en"
        return f"{self.root_prefix}{other}/{self.slug}.html"

    def asset(self, path: str) -> str:
        return f"{self.root_prefix}{path}"

    def brand_mark(self, curtain: bool = False, footer: bool = False) -> str:
        src = self.asset("icons/logo.svg")
        size = 64 if curtain else 44
        loading = "lazy" if footer else "eager"
        return f'<img class="brand-mark" src="{src}" alt="Waikiki" width="{size}" height="{size}" loading="{loading}" />'

# --------------------------------------------------------------------------- #
# Chrome builders
# --------------------------------------------------------------------------- #
def build_head(page: Page) -> str:
    other = "hu" if page.locale == "en" else "en"
    return f"""<!-- @chrome:head -->
    <meta name="theme-color" content="#fbf7f0" />
    <link rel="stylesheet" href="{page.asset('css/fonts.css')}" />
    <script>
    (function (d) {{
        var h = d.documentElement;
        h.classList.add('js');
        try {{
            if (localStorage.getItem('isDarkMode') === 'true') h.classList.add('body-dark');
            if (localStorage.getItem('isAnimationDisabled') === 'true') h.classList.add('no-reveal')
        }} catch (e) {{ }}
        setTimeout(function () {{
            if (!h.classList.contains('reveal-ready')) h.classList.remove('js')
        }}, 3500)
    }})(document);
    </script>
    <!-- /@chrome:head -->"""

def build_header(page: Page) -> str:
    loc = page.locale
    other = "hu" if loc == "en" else "en"
    nav_links = []
    for slug, labels in PRIMARY_NAV:
        current = ' aria-current="page"' if (slug == page.slug or (slug == "dynasty" and page.group == "royal")) else ""
        nav_links.append(f'<a href="{page.href(slug)}"{current}>{esc(labels[loc])}</a>')

    groups_html = []
    for _, labels, pages in GROUPS:
        items = []
        for slug, page_labels in pages:
            current = ' aria-current="page"' if slug == page.slug or couple_for(page.slug) == slug else ""
            items.append(f'<li><a href="{page.href(slug)}"{current}>{esc(page_labels[loc])}</a></li>')
        groups_html.append(
            f'<div class="menu-group"><h2>{esc(labels[loc])}</h2><ul>{"".join(items)}</ul></div>'
        )

    lang_chips = (
        f'<a class="menu-chip{" is-active" if loc == "en" else ""}" href="{page.root_prefix}en/{page.slug}.html" hreflang="en" lang="en">English</a>'
        f'<a class="menu-chip{" is-active" if loc == "hu" else ""}" href="{page.root_prefix}hu/{page.slug}.html" hreflang="hu" lang="hu">Magyar</a>'
    )

    return f"""<!-- @chrome:header -->
    <div class="page-curtain" aria-hidden="true">{page.brand_mark(curtain=True)}</div>
    <div class="scroll-progress" aria-hidden="true"></div>
    <header class="site-header">
        <a href="{page.href("index")}" class="brand">{page.brand_mark()}<span class="brand-word">Waikiki</span></a>
        <nav class="primary-nav">
            {"".join(nav_links)}
        </nav>
        <div class="header-actions">
            <a class="lang-pill" href="{page.other_locale_href()}" hreflang="{other}" lang="{other}" title="{esc(T["lang_name"][other])}">
                {GLOBE_ICON}
                <span>{other.upper()}</span>
            </a>
            <button class="icon-btn theme-toggle" type="button" data-theme-toggle aria-pressed="false">
                {THEME_ICON}
            </button>
            <button class="icon-btn menu-toggle" id="menu-toggle" type="button" aria-expanded="false" aria-controls="site-menu">
                <span class="menu-lines" aria-hidden="true"></span>
                <span class="menu-label-open">{esc(T["menu"][loc])}</span>
                <span class="menu-label-close">{esc(T["close"][loc])}</span>
                <span class="visually-hidden">{esc(T["menu"][loc])}</span>
            </button>
        </div>
    </header>
    <div class="site-menu" id="site-menu" aria-hidden="true" inert>
        <div class="site-menu-inner">
            <aside class="menu-aside">
                <div class="menu-clock-block">
                    <div class="menu-clock-header">
                        <p class="menu-clock-label">{esc(T["clock_label"][loc])}</p>
                        <div class="menu-weather" data-capital-weather><span class="weather-icon" aria-hidden="true">☀️</span> <span class="weather-temp">{esc(T["weather_temp"][loc])}</span> <span class="weather-desc">{esc(T["weather"][loc])}</span></div>
                    </div>
                    <p class="menu-clock" data-capital-clock>--:--</p>
                    <p class="menu-clock-city">{esc(T["clock_city"][loc])}</p>
                </div>
                <p class="menu-motto">{esc(T["motto"][loc])}</p>
                <div class="menu-aside-row">
                    {lang_chips}
                    <button class="menu-chip" type="button" data-theme-toggle aria-pressed="false">{esc(T["night"][loc])}</button>
                    <button class="menu-chip is-active" type="button" data-animate-toggle aria-pressed="true">{esc(T["animate_chip"][loc])}</button>
                </div>
            </aside>
            {"".join(groups_html)}
        </div>
    </div>
    <!-- /@chrome:header -->"""


def build_footer(page: Page) -> str:
    loc = page.locale
    cols = []
    for _, labels, pages in GROUPS:
        items = "".join(f'<li><a href="{page.href(slug)}">{esc(page_labels[loc])}</a></li>' for slug, page_labels in pages)
        cols.append(f'<div class="footer-col"><h2>{esc(labels[loc])}</h2><ul>{items}</ul></div>')
    other = "hu" if loc == "en" else "en"
    return f"""<!-- @chrome:footer -->
    <footer class="site-footer">
        {FOOTER_WAVE}
        <div class="footer-inner">
            <div class="footer-top">
                <div class="footer-brand">
                    <a href="{page.href("index")}" class="brand">{page.brand_mark(footer=True)}<span class="brand-word">Waikiki</span></a>
                    <p class="footer-motto">{esc(T["motto"][loc])}</p>
                    <p class="footer-about">{esc(T["about"][loc])}</p>
                </div>
                {"".join(cols)}
            </div>
            <span class="footer-mega" aria-hidden="true">Waikiki</span>
            <div class="footer-bottom">
                <p>{esc(T["rights"][loc])}</p>
                <nav>
                    <a style="margin-right: 40px" href="{page.other_locale_href()}" hreflang="{other}" lang="{other}">{esc(T["lang_name"][other])}</a>
                </nav>
            </div>
        </div>
    </footer>
    <button class="to-top" type="button">
        <svg viewBox="0 0 54 54" aria-hidden="true"><circle class="ring-bg" cx="27" cy="27" r="24"/><circle class="ring" cx="27" cy="27" r="24"/></svg><span aria-hidden="true">↑</span>
    </button>
    <!-- /@chrome:footer -->"""

def build_subnav(page: Page) -> str:
    couple = couple_for(page.slug)
    if not couple:
        return "<!-- @chrome:subnav --><!-- /@chrome:subnav -->"
    items = []
    for suffix, labels in COUPLE_TABS:
        slug = f"{couple}{suffix}"
        if not (ROOT / page.locale / f"{slug}.html").exists():
            continue
        current = ' aria-current="page"' if slug == page.slug else ""
        items.append(f'<li><a href="{page.href(slug)}"{current}>{esc(labels[page.locale])}</a></li>')
    return f"""<!-- @chrome:subnav -->
    <nav class="subnav">
        <ul class="subnav-list">
            {"".join(items)}
        </ul>
    </nav>
    <!-- /@chrome:subnav -->"""

TARGET_NEXT_IMAGES = {
    "overview": "UniversalUpscaler_Pro_Precise_2_1f1c19d5-4a8a-6240-8c96-a28f543c898c.jpg",
    "infrastructure": "UniversalUpscaler_Pro_Precise_2_1f1c1a29-2ad2-6700-ba29-0886f847836a.jpg",
    "space-research": "UniversalUpscaler_Pro_Precise_2_1f1c2357-5be5-6860-9aa6-0dca8e8888b7.jpg",
    "banking-system": "UniversalUpscaler_Pro_Precise_2_1f1c235a-8739-6b80-818f-9814e906014a.jpg",
    "constitution": "UniversalUpscaler_Pro_Precise_2_1f1c1a2a-3682-6450-b953-3cd17cf5a1a7.jpg",
    "nature": "UniversalUpscaler_Pro_Precise_2_1f1cafd8-c168-69e0-8654-e23fef3eb0b0.jpg",
    "travel-guide": "UniversalUpscaler_Pro_Precise_2_1f1c1a3a-8488-6130-962d-09f15cdbb0eb.jpg",
    "visa": "UniversalUpscaler_Pro_Precise_2_1f1c8726-8cda-62d0-a130-3eed92bc8395.jpg",
    "faq": "UniversalUpscaler_82625004-8a28-4ed6-9515-e204957d9457.jpg",
}

def build_next(page: Page, meta: dict[str, dict]) -> str:
    target = None
    if page.slug.endswith("-private"):
        target = "dynasty"
    elif page.slug == "raimondo-and-bailey-detailed":
        target = "angelina-and-taylor"
    elif page.slug in SEQUENCE:
        index = SEQUENCE.index(page.slug)
        for offset in range(1, len(SEQUENCE)):
            candidate = SEQUENCE[(index + offset) % len(SEQUENCE)]
            if meta.get(f"{page.locale}/{candidate}"):
                target = candidate
                break

    if not target:
        return "<!-- @chrome:next --><!-- /@chrome:next -->"

    info = meta.get(f"{page.locale}/{target}")
    if not info:
        return "<!-- @chrome:next --><!-- /@chrome:next -->"

    title = label_for(target, page.locale) or info["title"]
    image = info.get("image") or TARGET_NEXT_IMAGES.get(target) or meta.get(f"{page.locale}/index", {}).get("image")
    img_html = f'<div class="next-media"><img src="{page.asset("images/" + image)}" alt="" /></div>' if image else ""
    eyebrow = f'{T["continue"][page.locale]} · {group_label(group_for(target), page.locale)}'
    return f"""<!-- @chrome:next -->
    <section class="next-chapter">
        <a class="next-card" href="{page.href(target)}">
            {img_html}
            <span class="next-body">
                <span class="next-eyebrow">{esc(eyebrow)}</span>
                <span class="next-title">{esc(title)}</span>
                <span class="next-arrow" aria-hidden="true">→</span>
            </span>
        </a>
    </section>
    <!-- /@chrome:next -->"""

# --------------------------------------------------------------------------- #
# Legacy conversion
# --------------------------------------------------------------------------- #
def hero_html(page: Page, *, eyebrow: str, title: str, lead: str | None, image: str | None,
              img_style: str = "", stats: list[tuple[str, str]] | None = None, extra: str = "") -> str:
    loc = page.locale
    parts = ['<section class="hero{}" data-hero>'.format("" if image else " hero--compact")]
    if image:
        alt = (label_for(page.slug, loc) or strip_tags(title)).replace('"', '&quot;')
        style = f' style="{img_style}"' if img_style else ""
        parts.append(f'<div class="hero-media"><img src="{image}" alt="{alt}"{style} fetchpriority="high" /></div><div class="hero-veil"></div>')
    parts.append('<div class="hero-content">')
    if eyebrow:
        parts.append(f'<span class="hero-eyebrow">{eyebrow}</span>')
    parts.append(f'<h1 class="hero-title">{title}</h1>')
    if lead:
        parts.append(f'<p class="hero-lead">{lead}</p>')
    if extra:
        parts.append(extra)
    if stats:
        parts.append('<div class="hero-stats">' + "".join(
            f'<div class="stat-item"><span class="stat-number">{n}</span><span class="stat-label">{l}</span></div>' for n, l in stats
        ) + "</div>")
    parts.append("</div>")
    parts.append("</section>")
    return "".join(parts)

def tidy_title(title: str) -> str:
    title = re.sub(r'<span style="color:\s*#(?:BC9200|C95A41)"\s*>(.*?)</span>', r"<em>\1</em>", title, flags=re.I | re.S)
    return re.sub(r"\s+", " ", title).strip()

def convert_hero(page: Page, body: str) -> tuple[str, str]:
    """Return (body, lead_text) with the first legacy hero replaced."""
    loc = page.locale
    eyebrow_default = esc(f"{group_label(page.group, loc)} · {label_for(page.slug, loc) or ''}".strip(" ·"))

    # Variant A: <section class="hero" style="background: url(...)">
    match = re.search(r'<section class="hero" style="background: url\(\'([^\']+)\'\)[^"]*">(.*?)</section>', body, re.S)
    if match:
        image, inner = match.group(1), match.group(2)
        title = re.search(r"<h1[^>]*>(.*?)</h1>", inner, re.S).group(1)
        lead_m = re.search(r'<p class="liquid">(.*?)</p>', inner, re.S)
        lead = lead_m.group(1).strip() if lead_m else None
        stats = re.findall(r'<span class="stat-number">(.*?)</span>\s*<span class="stat-label">(.*?)</span>', inner, re.S)
        new = hero_html(page, eyebrow=eyebrow_default, title=tidy_title(title), lead=lead, image=image, stats=stats)
        return body[: match.start()] + new + body[match.end():], strip_tags(lead or "")

    # Variant B: <section class="hero-section"> with hero-bg / badge / title / desc
    match = re.search(r'<section class="hero-section">(.*?)</section>', body, re.S)
    if match:
        inner = match.group(1)
        img = re.search(r'<img src="([^"]+)" class="hero-img"(?: style="([^"]*)")?\s*/?>', inner)
        badge = re.search(r'<div class="hero-badge[^"]*">(.*?)</div>', inner, re.S)
        title = re.search(r'<h1 class="hero-title">(.*?)</h1>', inner, re.S).group(1)
        lead_m = re.search(r'<p class="hero-desc">(.*?)</p>', inner, re.S)
        actions = re.search(r'<div class="hero-actions".*?</div>', inner, re.S)
        image = img.group(1) if img and "TODO" not in img.group(1) else None
        if img and not image:
            image = page.asset("images/" + FALLBACK_IMAGE)
        new = hero_html(
            page,
            eyebrow=badge.group(1).strip() if badge else eyebrow_default,
            title=tidy_title(title),
            lead=lead_m.group(1).strip() if lead_m else None,
            image=image,
            img_style=(img.group(2) or "") if img else "",
            extra=actions.group(0) if actions else "",
        )
        return body[: match.start()] + new + body[match.end():], strip_tags(lead_m.group(1) if lead_m else "")

    # Variant C: no hero — promote the first page heading into a compact hero.
    lead = COMPACT_LEADS.get(page.slug, {}).get(loc)
    heading = re.search(r'<h1 class="faq-title section-title">(.*?)</h1>', body, re.S) or \
        re.search(r'<h2 class="section-title(?: mt-1)?">(.*?)</h2>', body, re.S)
    if heading and page.slug in COMPACT_LEADS:
        new = hero_html(page, eyebrow=eyebrow_default, title=tidy_title(heading.group(1)), lead=esc(lead), image=None)
        body = body[: heading.start()] + body[heading.end():]
        return new + body, lead or ""

    return body, ""

FALLBACK_IMAGE = "UniversalUpscaler_93281a3c-f408-4f55-b29b-e8a6b87ab85d-U.jpg"

def replace_block(text: str, name: str, content: str) -> str:
    pattern = re.compile(rf"<!-- @chrome:{name} -->.*?<!-- /@chrome:{name} -->", re.S)
    if pattern.search(text):
        return pattern.sub(lambda _: content, text, count=1)
    return text

def convert_legacy(page: Page, text: str) -> str:
    """Turn a page with the old nav/hamburger/footer markup into the marker layout."""
    nav_start = text.find('<nav class="nav-container">')
    panel = text.find('<nav class="hamburger-panel">')
    if nav_start == -1 or panel == -1:
        raise ValueError("legacy navigation not found")
    nav_end = text.find("</nav>", panel) + len("</nav>")
    footer_start = text.find("<footer>")
    footer_end = text.find("</footer>", footer_start) + len("</footer>")
    if footer_start == -1:
        raise ValueError("legacy footer not found")

    body = text[nav_end:footer_start]
    body = body.replace("<!-- Hero -->", "")
    body, _ = convert_hero(page, body)

    # Sub-navigation sits right after the hero; the next-chapter banner closes <main>.
    hero_end = body.find("</section>", body.find("data-hero")) + len("</section>") if "data-hero" in body else 0
    body = body[:hero_end] + "\n    <!-- @chrome:subnav --><!-- /@chrome:subnav -->" + body[hero_end:]
    body = body.rstrip() + "\n    <!-- @chrome:next --><!-- /@chrome:next -->\n"

    head_end = text.find("</head>")
    head = text[:head_end]
    head = re.sub(r'(<meta name="viewport"[^>]*>)', r"\1\n    <!-- @chrome:head --><!-- /@chrome:head -->", head, count=1)

    return (
        head + text[head_end:nav_start].rstrip()
        + "\n    <!-- @chrome:header --><!-- /@chrome:header -->\n    <main id=\"main\">"
        + body + "    </main>\n    <!-- @chrome:footer --><!-- /@chrome:footer -->"
        + text[footer_end:]
    )

# --------------------------------------------------------------------------- #
# Page metadata (titles, hero images, descriptions)
# --------------------------------------------------------------------------- #
def page_meta(text: str) -> dict:
    title = re.search(r"<title>(.*?)</title>", text, re.S)
    # Only look at page content, never at generated or legacy navigation.
    if '<main id="main">' in text:
        content = text[text.find('<main id="main">'):]
    elif '<nav class="hamburger-panel">' in text:
        content = text[text.find("</nav>", text.find('<nav class="hamburger-panel">')):]
    else:
        content = text
    content = re.sub(r"<!-- @chrome:(subnav|next) -->.*?<!-- /@chrome:\1 -->", "", content, flags=re.S)
    image = (
        re.search(r'class="hero-media"><img src="[./]*images/([^"]+)"', content)
        or re.search(r"<section class=\"hero[^>]*?url\('[./]*images/([^']+)'", content)
        or re.search(r'class="hero-overlay"></div><img src="[./]*images/([^"]+)"', content)
        or re.search(r'<img src="[./]*images/([^"]+)" class="w-full h-full', content)
    )
    lead = (
        re.search(r'<p class="hero-lead">(.*?)</p>', content, re.S)
        or re.search(r'<p class="liquid">(.*?)</p>', content, re.S)
        or re.search(r'<p class="hero-desc">(.*?)</p>', content, re.S)
        or re.search(r'<p class="narrative-text[^"]*">(.*?)</p>', content, re.S)
        or re.search(r'<p class="text-(?:lg|xl)[^"]*">(.*?)</p>', content, re.S)
        or re.search(r'<p class="section-intro">(.*?)</p>', content, re.S)
    )
    img = image.group(1) if image and "TODO" not in image.group(1) else None
    return {
        "title": strip_tags(title.group(1)) if title else "Waikiki",
        "image": img,
        "lead": strip_tags(lead.group(1)) if lead else "",
    }

# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def all_pages() -> list[Path]:
    pages = []
    for locale in LOCALES:
        pages += sorted((ROOT / locale).glob("*.html"))
        pages += sorted((ROOT / locale / "bio").glob("*.html"))
    return pages

# Embedded Node script for exact js-beautify HTML formatting
NODE_FORMAT_SCRIPT = """
const fs = require('fs');
const beautify = require('js-beautify').html;
const opts = {
    indent_size: 4,
    indent_char: ' ',
    max_preserve_newlines: 0,
    preserve_newlines: false,
    extra_liners: [],
    end_with_newline: true,
    wrap_line_length: 0,
    indent_inner_html: false
};
let input = fs.readFileSync(0, 'utf8');
let out = beautify(input, opts);
let lines = out.split(/\\r?\\n/).filter(l => l.trim().length > 0);
process.stdout.write(lines.join('\\n'));
"""

def format_and_remove_empty_lines(html_content: str) -> str:
    """Format document with 4-space indent and remove all empty lines."""
    try:
        proc = subprocess.run(
            ["node", "-e", NODE_FORMAT_SCRIPT],
            input=html_content,
            text=True,
            capture_output=True,
            check=True,
            cwd=str(ROOT),
        )
        if proc.stdout.strip():
            return proc.stdout
    except Exception:
        pass

    # Fallback if node or js-beautify is unavailable
    lines = [line for line in html_content.splitlines() if line.strip()]
    return "\n".join(lines) + "\n"

def format_file(file_path: Path) -> bool:
    """Format and strip blank lines for a single file in-place."""
    try:
        original = file_path.read_text(encoding="utf-8")
        processed = format_and_remove_empty_lines(original)
        if original != processed:
            file_path.write_text(processed, encoding="utf-8")
            try:
                rel = file_path.relative_to(ROOT)
            except ValueError:
                rel = file_path
            print(f"Formatted and cleaned: {rel}")
            return True
    except Exception as err:
        print(f"Error processing {file_path}: {err}", file=sys.stderr)
    return False

def get_all_html_files(directory: Path) -> list[Path]:
    """Recursively collect all .html files excluding node_modules and .git."""
    results = []
    if not directory.exists():
        return results
    for item in directory.rglob("*.html"):
        parts = item.parts
        if "node_modules" in parts or ".git" in parts:
            continue
        results.append(item)
    return sorted(results)

def process(path: Path, meta: dict) -> str:
    page = Page(path)
    text = path.read_text(encoding="utf-8")

    if "<!-- @chrome:header -->" not in text:
        text = convert_legacy(page, text)

    # Body hooks used by CSS/JS.
    body_classes = f"page-{page.slug.replace('/', '-')} group-{page.group}"
    text = re.sub(r"<body[^>]*>", f'<body class="{body_classes}">', text, count=1)

    text = replace_block(text, "head", build_head(page))
    text = replace_block(text, "header", build_header(page))
    text = replace_block(text, "subnav", build_subnav(page))
    text = replace_block(text, "next", build_next(page, meta))
    text = replace_block(text, "footer", build_footer(page))
    text = format_and_remove_empty_lines(text)
    return text

def create_empty_page(
    slug: str = "empty",
    title: str | None = None,
    group: str = "nation",
    locale: str = "en",
) -> Path:
    """Generate a clean starter template page following site rules and structure."""
    target_file = ROOT / locale / f"{slug}.html"
    target_file.parent.mkdir(parents=True, exist_ok=True)

    depth = len(Path(f"{locale}/{slug}.html").parts) - 1
    root_prefix = "../" * depth

    if locale == "hu":
        default_title = "Üres Oldal" if slug == "empty" else slug.split("/")[-1].replace("-", " ").capitalize()
        page_title = title or default_title
        eyebrow = f"{group_label(group, 'hu')} · Sablon"
        lead = "Kezdő sablonoldal Waikiki Állam hivatalos portáljához."
        sec1_title = "Áttekintés"
        sec1_intro = "Ez a szakasz készen áll a tartalomra és követi az oldal stílusirányelveit."
        sec2_title = "Részletek és Jellemzők"
        sec2_intro = "Váltakozó hátterű szakasz a vizuális ritmus fenntartásához."
    else:
        default_title = "Empty Page" if slug == "empty" else slug.split("/")[-1].replace("-", " ").title()
        page_title = title or default_title
        eyebrow = f"{group_label(group, 'en')} · Template"
        lead = "A clean starter template page for the Sovereign Nation of Waikiki portal."
        sec1_title = "Overview"
        sec1_intro = "This section is ready for content and structured according to site guidelines."
        sec2_title = "Details and Features"
        sec2_intro = "Alternating section with a soft background tone to maintain visual rhythm."

    template = f"""<!DOCTYPE html>
<html lang="{locale}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- @chrome:head --><!-- /@chrome:head -->
    <title>{esc(page_title)}</title>
    <link rel="icon" href="{root_prefix}icons/favicon.ico" />
    <link rel="apple-touch-icon" sizes="1024x1024" href="{root_prefix}icons/logo-blue.png" />
    <link href="{root_prefix}manifest.json" rel="manifest" />
    <link rel="stylesheet" href="{root_prefix}css/common.css" />
</head>
<body class="page-{slug.replace('/', '-')} group-{group}">
    <!-- @chrome:header --><!-- /@chrome:header -->
    <main id="main">
        <section class="hero hero--compact" data-hero>
            <div class="hero-content">
                <span class="hero-eyebrow">{esc(eyebrow)}</span>
                <h1 class="hero-title">{esc(page_title)}</h1>
                <p class="hero-lead">{esc(lead)}</p>
            </div>
        </section>
        <!-- @chrome:subnav --><!-- /@chrome:subnav -->
        <section id="overview">
            <h2 class="section-title">{esc(sec1_title)}</h2>
            <p class="section-intro">{esc(sec1_intro)}</p>
        </section>
        <section id="details" class="light-bg">
            <h2 class="section-title">{esc(sec2_title)}</h2>
            <p class="section-intro">{esc(sec2_intro)}</p>
        </section>
        <!-- @chrome:next --><!-- /@chrome:next -->
    </main>
    <!-- @chrome:footer --><!-- /@chrome:footer -->
    <script src="{root_prefix}js/common.js"></script>
</body>
</html>
"""
    target_file.write_text(template, encoding="utf-8")
    return target_file

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="only report pages that would change")
    parser.add_argument(
        "--new",
        nargs="?",
        const="empty",
        metavar="SLUG",
        help="generate a new empty page (default slug: empty)",
    )
    parser.add_argument(
        "--empty",
        dest="empty_flag",
        action="store_true",
        help="generate an empty page (alias for --new empty)",
    )
    parser.add_argument("--title", help="title for the new page")
    parser.add_argument(
        "--group",
        default="nation",
        choices=[g[0] for g in GROUPS],
        help="site group (default: nation)",
    )
    parser.add_argument(
        "--locale",
        choices=["en", "hu", "both"],
        default="both",
        help="locale to generate (default: both)",
    )
    parser.add_argument(
        "--format",
        nargs="*",
        metavar="FILE",
        help="format and clean specified HTML file(s), or '-' for stdin",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="format all HTML files across en/, hu/, and root",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="optional HTML file(s) to format and clean",
    )
    args = parser.parse_args()

    # Direct formatting mode
    formatting_files = None
    if args.format is not None:
        formatting_files = args.format
    elif args.files:
        formatting_files = args.files
    elif args.all:
        formatting_files = []

    if formatting_files is not None:
        if formatting_files == ["-"] or (len(formatting_files) == 1 and formatting_files[0] == "-"):
            stdin_content = sys.stdin.read()
            sys.stdout.write(format_and_remove_empty_lines(stdin_content))
            return 0

        target_files = []
        if args.all or not formatting_files:
            target_files += get_all_html_files(ROOT / "en")
            target_files += get_all_html_files(ROOT / "hu")
            root_index = ROOT / "index.html"
            if root_index.exists():
                target_files.append(root_index)
        else:
            for f in formatting_files:
                target_files.append(Path(f).resolve())

        changed = 0
        for p in target_files:
            if format_file(p):
                changed += 1
        print(f"Done. Processed {len(target_files)} file(s), updated {changed}.")
        return 0

    # Generate template / empty page if requested
    if args.new or args.empty_flag:
        slug = (args.new if args.new and args.new != "empty" else "empty").strip("/").removesuffix(".html")
        locales = ("en", "hu") if args.locale == "both" else (args.locale,)
        for loc in locales:
            created_path = create_empty_page(slug=slug, title=args.title, group=args.group, locale=loc)
            print(f"Created template: {created_path.relative_to(ROOT)}")

    paths = all_pages()

    # First pass: gather metadata (from current or legacy markup) for cross-links.
    meta = {}
    for path in paths:
        page = Page(path)
        meta[f"{page.locale}/{page.slug}"] = page_meta(path.read_text(encoding="utf-8"))

    changed = 0
    for path in paths:
        try:
            new_text = process(path, meta)
        except Exception as error:  # noqa: BLE001 - report and keep going
            print(f"!! {path.relative_to(ROOT)}: {error}", file=sys.stderr)
            continue
        if new_text != path.read_text(encoding="utf-8"):
            changed += 1
            if args.check:
                print(f"would update {path.relative_to(ROOT)}")
            else:
                path.write_text(new_text, encoding="utf-8")

    print(f"{'Would update' if args.check else 'Updated'} {changed} of {len(paths)} pages")
    return 0

if __name__ == "__main__":
    sys.exit(main())
