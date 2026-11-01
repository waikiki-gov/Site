---
name: spell-check
description: >-
  Audits, verifies, and corrects copy quality, spelling, grammar, typography, domain conventions, and project-specific editorial rules across English and Hungarian HTML pages in the Sovereign Nation of Waikiki site. Use this skill whenever checking spelling, auditing copy quality, validating ampersand or whitespace rules, or reviewing text and language style on site pages.
---

# Spell Check, Copy Quality & Editorial Style Skill

This skill provides the comprehensive runbook, linguistic conventions, design system requirements, editorial policies, and automated audit tools for ensuring 100% clean, error-free, sophisticated, and dignified copy and code across all pages of the Sovereign Nation of Waikiki portal in both English and Hungarian.

---

## When to Use This Skill

Activate this skill when:
- The user requests a spell check, copy audit, proofreading, or language style review on one or more pages.
- Elevating Hungarian or English copy quality, eliminating word repetition, or correcting unidiomatic Hungarian phrasing (*igényes megfogalmazás, szóismétlések és magyartalan szerkezetek kerülése*).
- New HTML pages have been created or existing copy has been modified.
- Checking compliance with project editorial rules (ampersands, 0 empty lines, 4-space formatting, alternating `light-bg` section classes).
- Reviewing typography hierarchy (display serif `Fraunces` vs. body `Manrope`) and design system token usage.
- Reviewing Hungarian orthography (compound hyphenation, en-dashes vs. hyphens, vowel lengthening, proper noun suffixation, quotation marks).
- Checking English spelling and style (UK/US variants, Title Case headings, curly quotes, native macOS NSSpellChecker compliance).
- Validating canonical lore, geography, botanical/ecological biomes, alpine engineering, or aerospace terminology.
- Ensuring CSS and media query adherence (desktop-first `@media (max-width: ...)`, avoiding `min-width`).

---

## Editorial, Style & Formatting Principles

Before making or reviewing edits, consult the canonical references:
1. [Style Guidelines](../../rules/STYLE-GUIDELINES.md) — Tropical Luxe design system, typography hierarchy, color tokens, motion kinematics, UI components, accessibility, and desktop-first media queries.
2. [Agent Workflow & Rules](../../rules/AGENTS.md) — Ampersand rule, alternating section styles, desktop-first media queries, and HTML build utilities.
3. [Editorial, Style & Orthography Guidelines](./references/editorial_rules.md) — Tone and register, bilingual editorial symmetry, Hungarian phrasing standards, English conventions, and structural invariants.
4. [Domain Whitelist & Lore Dictionary](./references/domain_whitelist.md) — Canonical characters, royal family, government officials, geography, ecological biomes, botanical and zoological species, space exploration vehicles, alpine technology, and financial institutions.
5. [Companion Skill: Locale Sync](../locale-sync/SKILL.md) — For detecting active changes and synchronizing content and specs between Hungarian and English counterpart pages.

---

### Key Linguistic & Editorial Rules at a Glance

| Rule | Requirement |
| :--- | :--- |
| **Tone & Register** | Formal, dignified, inspiring, and objective state publication register. Avoid colloquialisms, sensationalism, journalistic hype, and bureaucratic clutter. |
| **Igényes stílus & szókincs** | Rich, sophisticated, and statesmanlike Hungarian phrasing (*választékos stílusréteg*). Express complex technical, constitutional, and ecological ideas with precision and elegance. |
| **Szóismétlések kerülése** | **Strictly avoid word repetition**: Do not repeat identical words or roots in adjacent sentences, bullet points, or peer card components. Use context-rich synonyms. |
| **Magyartalan szerkezetek kerülése** | Eliminate unnatural foreign calques, translationese, heavy passive/impersonal constructions (*„kerül lebonyolításra”* $\rightarrow$ *„bonyolítja le”*), and tautologies (*„színpompás morpho-pillangók”*). Ensure natural Hungarian syntactic cadence. |
| **Ampersands** | Always write out **"and"** (English) and **"és"** (Hungarian) instead of `&` in titles, section headings, card headers, labels, and running copy. (Exceptions: `Walker Finance & Insurance Holding`, `R&D`, `AT&T`, HTML entities). |
| **Alternating Section Styles** | Top-level `<section>` elements must alternate strictly between normal and `light-bg` styles. |
| **Typography Pairing** | **Display Serif**: `Fraunces` for hero titles, section headlines, card titles, stat numbers, brand insignia, and quotes.<br>**Body & Interface**: `Manrope` for body text, navigation links, buttons, table data, subnavigation, and chips. |
| **Color Tokens** | Use official design tokens: `--sand-50`, `--sand-100`, `--sand-200`, `--primary-dark`, `--secondary`, `--primary`, `--primary-light`, `--tertiary`, `--accent`, `--accent-hover`, province colors (`--waikiki`, `--amazonia`, `--brazilia`), and dark mode tokens. |
| **Desktop-First Media Queries** | Write base CSS for desktop/large screens. Adapt for smaller viewports exclusively with `@media (max-width: ...)` queries, strictly avoiding `min-width`. |
| **Headings Casing** | **Hungarian**: Sentence case (capitalize only the first word and proper nouns).<br>**English**: Title Case (capitalize principal words). |
| **Quotes** | **Hungarian**: `„...”` (bottom-99 / top-99). Never use straight double quotes `"` or English `“...”`.<br>**English**: `“...”` (curly quotes). Never use straight `"`. |
| **Dashes & Hyphens** | Use regular hyphen (`-`, U+002D) everywhere. Never use en-dash (`–`, U+2013). Disallow double hyphens in non-date compound words (e.g., `Covid-19 világjárvány` instead of `Covid-19-világjárvány`). Double hyphens permitted for year intervals (e.g., `2002-2004-es`). |
| **Specific Terms** | `Pacifikus háború` $\rightarrow$ `Csendes-óceáni háború`. `COVID-19` $\rightarrow$ `Covid-19`. `zárt körű` $\rightarrow$ `zártkörű`. `infrastruktúrafejlesztés` $\rightarrow$ `infrastruktúra-fejlesztés`. `waikiki-i` $\rightarrow$ `Waikiki-i` (prefer noun phrasing: `Waikiki polgárai`). `Nova Aurélia` $\rightarrow$ `Nova Aurelia` (adjective: `Nova Auréliai`). |
| **A „szuverén” szó** | The word `szuverén` is reserved for the official state name (`Waikiki Szuverén Állam`) and the footer; avoid gratuitous use in body prose (use *önálló*, *független*, *saját jogán eljáró*). |
| **Hungarian Suffixation** | Apply vowel lengthening (*Raimondóval*, *Selenával*, *Isla de la Estrellán*) and proper foreign suffix assimilation (*Chease-zel*, *Lautnerrel*, *Baileyvel*). Titles in running prose remain lowercase (*„waikiki hercegnője”*, *„a diktátor rendelete”*). |
| **HTML Formatting** | Exactly 4-space indentation and **0 empty lines** throughout the document. |
| **TODO Markers** | Never alter or remove `TODO` placeholders during copy or spelling audits. |

---

## 1. Hungarian Linguistic Refinement & Phrasing Standards

### A. Igényes, Választékos Megfogalmazás (Elevated Phrasing)
All Hungarian copy represents the official state documentation, national heritage, and constitutional pride of Waikiki. Strive for literary elegance, gravitas, and natural Hungarian idioms:
- Prefer rich, descriptive verbs over generic auxiliaries (*biztosít*, *nyújt*, *van*, *képez*).
  - *Gyenge*: „A létesítmény kiváló lehetőséget biztosít a pihenésre.”
  - *Igényes*: „A komplexum a zavartalan kikapcsolódás és a testi-lelki megújulás szentélye.”
- Elevate technical and geographical descriptions:
  - *Gyenge*: „A hegyekben nagyon hideg van és sok a hó.”
  - *Igényes*: „A hegyvidéki bérceket örök hó és szubalpin mikroklíma uralja, ideális feltételeket teremtve az alpesi élvonalnak.”

### B. Szóismétlések Szigorú Kerülése (Anti-Repetition Rule)
Never repeat identical content words, verbs, or stems across consecutive sentences, neighboring cards, or parallel list items.

| Overused Word / Stem | Sophisticated Hungarian Alternates |
| :--- | :--- |
| **biztosít** | szavatol, garantál, elősegíti, megalapozza, kínál, elmélyíti, záloga, szolgálja |
| **számára** | rétegnek, polgároknak, látogatóknak, közösségnek, kötelékében, részére, javára |
| **kiemelkedő** | mérvadó, páratlan, meghatározó, élenjáró, rangos, számottevő, kivételes, fenséges |
| **fejlesztés / fejleszt** | korszerűsítés, bővítés, beruházás, finomhangolás, modernizáció, felvirágoztatás |
| **lehetőséget nyújt** | utat nyit, teret enged, felvértezi, felkínálja, megnyitja kapuit, lehetővé teszi |
| **zártkörű** | szűk körű, privát, meghitt, kötetlen, bizalmas, diszkrét |
| **területén** | szférájában, berkeiben, vonzáskörzetében, mezsgyéjén, horizontján |
| **különleges** | egyedülálló, sajátos, ritka, rendhagyó, egyedi arculatú, unikális |

### C. Magyartalan Szerkezetek és Tükörfordítások Felszámolása
Avoid awkward literal translations, foreign syntactic calques, and German/English-style passive phrasing:
1. **Kerüld a terpeszkedő kifejezéseket és a passzív jellegű szerkezeteket**:
   - *Helytelen*: „A rendezvény megrendezésre kerül a minisztérium által.”
   - *Helyes*: „A rendezvényt a minisztérium szervezi.” / „A tárca ad otthont az eseménynek.”
   - *Helytelen*: „A megvalósítás eredményeképpen létrejövő létesítmények...”
   - *Helyes*: „A beruházás nyomán kiépülő létesítmények...”
2. **Szüntesd meg a pleonazmusokat és szóhalmozásokat (Tautologies)**:
   - *Helytelen*: „színpompás morpho-pillangók” (a morpho eleve ragyogó kék) $\rightarrow$ *Helyes*: „lazúrkék morpho-pillangók” vagy „Morpho-pillangók”.
   - *Helytelen*: „teljes mértékben tökéletes” $\rightarrow$ *Helyes*: „kifogástalan” / „tökéletes”.
   - *Helytelen*: „előre látható jövőbeni tervek” $\rightarrow$ *Helyes*: „távlati tervek”.
3. **Természetes szórend és igekötő-használat**:
   - Ügyelj a magyar fókuszpozícióra és az igekötők elválására tagadás, segédigék vagy hangsúlyos mondatrészek esetén.

---

## 2. Design System & Style Guidelines Integration

### A. Typography Hierarchy (`STYLE-GUIDELINES.md`)
The site employs an editorial dual-font pairing:
- **Display Optical Serif — `Fraunces`**:
  - Weights: 400, 600, 700, 800, italic, optical size 144.
  - Usage: Brand insignia, hero titles (`.hero-title`), section headlines (`.section-title`), stat numbers (`.stat-number`, `.economy-number`), card titles (`.card h3`, `.admin-card h3`), and blockquotes.
- **Body & Interface — `Manrope`**:
  - Weights: 400, 500, 600, 700, 800.
  - Usage: Narrative body copy (`p`, `.narrative-text`), navigation links, buttons, tables, subnav rails, chips, and metadata.

#### Typographic Scale
- **Hero Title (`.hero-title`)**: `clamp(2.75rem, 6vw, 4.5rem)`, weight 800, line-height 1.05, tracking `-0.02em`.
- **Section Title (`.section-title`)**: `clamp(2rem, 4vw, 3rem)`, weight 700, line-height 1.15. Decorated with warm gradient accent pill.
- **Card Title (`.card h3`, `.admin-card h3`)**: `clamp(1.25rem, 2vw, 1.5rem)`, weight 700, line-height 1.25.
- **Hero Lead (`.hero-lead`)**: `clamp(1.1rem, 1.6vw, 1.35rem)`, weight 400, line-height 1.65.
- **Body Text (`p`, `.narrative-text`)**: `clamp(1rem, 1.3vw, 1.12rem)`, weight 400, line-height 1.8.
- **Eyebrow / Subhead (`.hero-eyebrow`)**: `0.85rem`, weight 700, uppercase, tracking `0.18em`, coral glow.

### B. Color Palette & Semantic Tokens
- **Primary Palette (Tropical Luxe)**:
  - `--sand-50: #FBF7F0` (Primary page canvas, warm ivory backdrop)
  - `--sand-100: #F5EDE1` (Secondary surface, subtle contrast bands)
  - `--sand-200: #E8DCB8` (Warm border accents, subtle dividers)
  - `--primary-dark: #001830` (Deepest brand tone, midnight headers, high-contrast text)
  - `--secondary: #002244` (Secondary midnight navy, hero veils, badges, button backdrops)
  - `--primary: #003366` (Primary sovereign navy, interactive elements, active links)
  - `--primary-light: #1A528F` (Vibrant royal blue, province tone, success states)
  - `--tertiary: #6BA4D9` (Soft azure glow, luminous indicators, dark mode primary)
  - `--accent: #C28A29` (Accent gold, royal insignia, stars, timeline nodes, brass accents)
  - `--accent-hover: #C95A41` (Dynamic accent coral/amber, active states, callouts)
  - `--accent-light: #F5C46E` (Illuminated gold accents, night mode badges)
  - `--accent-dark: #78531A` (Deep antique gold, high contrast brass text)
- **Midnight Sovereign (Dark Mode)**:
  - Canvas: `#0A1420` · Surface Card: `#0E2035` · Surface Subtle: `#091626`
  - Text Primary: `#FBF7F0` · Text Secondary: `#C2CDD8` · Accent Glow: `#6BA4D9` · Accent Coral: `#E3735A`
- **Province Identity Tokens**:
  - Waikiki: `--waikiki: #1A528F`, hover: `#296BB3` (Deep sovereign azure)
  - Amazonia: `--amazonia: #4E8B5A`, hover: `#62A56F` (Lush Amazonian emerald)
  - Brazilia: `--brazilia: #C28A29`, hover: `#ECC677` (Warm sunlit brass)
- **Private Section Tokens**:
  - `--private: #0A1930` · `--intimate: #3D1520` · `--adventure: #123F43` · `--milestones: var(--secondary)`

### C. Motion Engine & Kinematics
All motion follows organic physics:
- **Ease Out**: `cubic-bezier(0.16, 1, 0.3, 1)` (modals, menus, card reveals).
- **Spring**: `cubic-bezier(0.34, 1.56, 0.64, 1)` (badges, active pills, icons).
- **Curtain Transit**: `cubic-bezier(0.76, 0, 0.24, 1)` (page transition curtains, 400ms).
- **Core Behaviors**: Curtain Navigation, Word-Split Hero Reveal (`.split-word`), Scroll Reveal (`.fade-in`, `.revealed`), Spotlight Tracking Cards (`.card`, `.hover-card`), Stat Count-Up (`.stat-number`), Smart Header, Floating Back-to-Top with Progress Ring.

### D. Responsive Architecture & Media Query Guidelines
- **Desktop-First Standard**: Default styles must be written for large screens (desktop).
- **Media Queries**: Responsive adaptations must exclusively use `@media (max-width: ...)` queries to adapt for smaller screens. Never write `min-width` queries.
- **CSS Purging**: Keep stylesheets optimized and purged of unused classes via `purgecss --css css/*.css --output css/ --content **/*.html **/*.js --keyframes`.

### E. Accessibility & Structural Landmarks
- **Landmarks**: Every page must have proper landmarks: `<header>`, `<nav>`, `<main id="main">`, `<section>`, `<article>`, `<footer>`.
- **Contrast Compliance**: Strict minimum of 4.5:1 text-to-background contrast ratio across light and dark modes.
- **Reduced Motion**: Respect `@media (prefers-reduced-motion: reduce)`.
- **Keyboard Navigation**: Clear `:focus-visible` rings with `--coral-500` glow and `outline-offset: 3px`.
- **Multilingual Links**: Valid `hreflang="hu"` and `hreflang="en"` links on language selectors; `lang` attributes on `<html>`.

---

## Step-by-Step Audit Workflow

### Step 1: Run the Automated Quality Auditor

Execute the audit helper script to scan for typography anomalies, duplicate words, ampersand violations, empty lines, Hungarian typos, and English spelling:

```bash
# Audit all pages across both languages
python3 .agents/skills/spell-check/scripts/audit.py

# Audit only Hungarian pages
python3 .agents/skills/spell-check/scripts/audit.py --lang hu

# Audit only English pages
python3 .agents/skills/spell-check/scripts/audit.py --lang en

# Audit specific page(s)
python3 .agents/skills/spell-check/scripts/audit.py hu/family-tree.html hu/space-research.html

# Automatically fix safe whitespace & punctuation spacing issues
python3 .agents/skills/spell-check/scripts/audit.py --fix
```

### Step 2: Contextual & Stylistic Review

Automated tools catch mechanics, but the agent must evaluate:
- **Tone, Dignity & Sophistication**: Verify elevated register, statesmanlike gravitas, and absence of colloquialisms or bureaucratic monotony.
- **Anti-Repetition Check**: Ensure adjacent sentences, list items, and card rows do not repeat identical verbs (*biztosít*), nouns (*fejlesztés*), or adverbs.
- **Idiomatic Hungarian Check**: Verify natural sentence structure, eliminating clumsy translationese or passive calques.
- **Bilingual Symmetry**: Compare with the counterpart page (`hu/<page>.html` $\leftrightarrow$ `en/<page>.html`) to ensure concepts, numbers, and facts are identically aligned.
- **Typography & Layout**: Verify Display Serif `Fraunces` vs Body `Manrope`, alternating `light-bg` section classes, and absence of naked `&` ampersands.

### Step 3: Format & Clean Pages Post-Edit

Whenever an HTML file is edited:
1. Re-format the document with 4-space indentation and remove blank lines:
   ```bash
   python3 scripts/build_pages.py --format <path/to/page.html>
   ```
2. Or format all pages if multiple were edited:
   ```bash
   python3 scripts/build_pages.py --format --all
   ```

### Step 4: Verification

Re-run the audit script, locale sync check, and text balance check:
```bash
python3 .agents/skills/spell-check/scripts/audit.py
python3 .agents/skills/locale-sync/scripts/sync_check.py
python3 .agents/skills/text-balance/scripts/text_balance.py --static <path/to/page.html>
```
Expected output:
```text
[SUCCESS] All checks passed! Site copy is 100% clean.
```
