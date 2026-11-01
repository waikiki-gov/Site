# Editorial, Style & Orthography Guidelines

This document details the stylistic conventions, tone of voice, linguistic rules, typography, design tokens, and structural invariants governing all content on the Sovereign Nation of Waikiki portal.

---

## 1. Tone, Dignity & Register

The site represents the official public face of a modern, sovereign constitutional state. The tone across all pages and languages must be:
- **Authoritative & Dignified**: Respectful, statesmanlike, and balanced. Avoid sensationalism, colloquialisms, slang, and hyperbolic journalistic prose.
- **Inspiring yet Objective**: Reflect technological advancement, cultural heritage, and ecological stewardship with measured pride backed by clear facts, dates, and metrics.
- **Consistent Bilingual Voice**: Ensure the Hungarian and English versions convey identical depth, gravitas, and nuance rather than reading like loose, machine-translated paraphrases.

---

## 2. Bilingual Editorial Symmetry

| Dimension | Hungarian (`hu/`) | English (`en/`) |
| :--- | :--- | :--- |
| **Heading Casing** | **Sentence case**: Capitalize only the first word and proper nouns. | **Title Case**: Capitalize principal words. |
| **Quotation Marks** | **Smart quotes**: `„Idézet”` (bottom-99 and top-99). Never use `“...”` or straight `"` in running Hungarian prose. | **Curly quotes**: `“Quote”` (top-66 and top-99). Never use straight `"`. |
| **Hyphenation & Dashes** | Standard hyphen `-` (U+002D) for date ranges and en-dashes (`2026-2030`, `Hold-program`). Never use en-dash `–` (U+2013). | Standard hyphen `-` for compound modifiers (`deep-space`, `carbon-neutral`, `cryo-cooled`). |
| **Number Format** | Space as thousands separator: `180 000 kg`, `35 000 kN`. Decimal comma: `2,5 milliárd $`, `Mach 0,85`. | Comma as thousands separator: `180,000 kg` or space matching template. Decimal point: `$2.5 Billion`, `Mach 0.85`. |
| **Currency** | `300 millió $`, `2 milliárd $`, `120 Mrd Ft`, `WUD`. | `$300 Million`, `$2 Billion`, `WUD`. |
| **Conjunction** | Always use **"és"** in prose, headers, and cards. | Always use **"and"** in prose, headers, and cards. |

---

## 3. Ampersand Policy (AGENTS.md & STYLE-GUIDELINES.md)

1. **Rule**: In titles, section headings, card headers, labels, navigation, and copy, always use the spelled-out word:
   - **Hungarian**: Use `és`
   - **English**: Use `and`
2. **Strictly Prohibited**: Naked `&` symbols in narrative prose or headings (e.g. `Chease & Jessica` is invalid; use `Chease és Jessica` or `Chease and Jessica`).
3. **Exceptions**:
   - Official registered corporate trademarks: `Walker Finance & Insurance Holding`, `R&D`, `Q&A`, `AT&T`, `S&P`.
   - HTML entities in code: `&copy;`, `&amp;`, `&nbsp;`, `&quot;`, `&lt;`, `&gt;`.

---

## 4. Hungarian Orthography & Project-Specific Rules

### A. Mandatory Terms & Forms
- **Csendes-óceáni háború**: Always write `Csendes-óceáni háború` in historical texts (never `Pacifikus háború`).
- **Covid-19**: Write `Covid-19` with a lowercase "ovid" and a single hyphen (never `COVID-19`).
- **Nova Aurelia**: The capital city is written without accents: `Nova Aurelia`.
  - Adjective form: `Nova Auréliai` (capitalized, single word without hyphen).
- **Waikiki melléknévi alak**: Prefer noun phrases (`Waikiki polgárai`, `Waikiki területe`) over the adjective `Waikiki-i`. If unavoidable, capitalize the W: `Waikiki-i`.
- **zártkörű**: Spelled as one word (`zártkörű`). Where repeated frequently in proximity, vary with elegant synonyms (*szűk körű*, *privát*, *meghitt*, *kötetlen*, *bizalmas*).
- **infrastruktúra-fejlesztés**: Spelled with a hyphen according to compound word length rules (similarly: *infrastruktúra-fejlesztési*, *infrastruktúra-fejlesztésben*).
- **A „szuverén” szó használata**: Restrict `szuverén` to official state designations (`Waikiki Szuverén Állam`) or the footer. In general body copy, avoid repetitive usage; choose natural alternatives (*önálló*, *független*, *saját jogán eljáró*).
- **TODO megőrzése**: Never remove or alter `TODO` comments or placeholders during text audits.

### B. Hyphenation in Hungarian Compounds
- **Year intervals**: Double hyphens are permitted in inflected year intervals (e.g. `2002-2004-es`, `2009-2010-ben`, `2021-2024-es`).
- **Single hyphen rule for words**: Avoid multiple hyphens in regular words:
  - `Covid-19-világjárvány` $\rightarrow$ `Covid-19 világjárvány`
  - `Covid-19-járvány` $\rightarrow$ `Covid-19 járvány`
  - `Covid-19-oltási program` $\rightarrow$ `Covid-19 oltási program`
- **Foreign compound phrases**: Write foreign compound phrases separately with suffixes attached to the last element (e.g. `VIP lounge-ok`, `cash flow-t`).

### C. Foreign Names, Titles & Suffixation
- **Official titles in running prose**: Keep lowercase when appearing in running sentences (e.g. *„waikiki hercegnője”*, *„a diktátor és kísérete”*, *„az államfő rendelete”*).
- **Vowel lengthening before suffixes**: Apply Hungarian vowel lengthening rules when adding inflectional suffixes:
  - *Raimondo* $\rightarrow$ *Raimondóval*, *Raimondót*, *Raimondónak*, *Raimondóé*
  - *Selena* $\rightarrow$ *Selenával*, *Selenát*, *Selenának*, *Selenáért*
  - *Jessica* $\rightarrow$ *Jessicával*, *Jessicát*
  - *Isla de la Estrella* $\rightarrow$ *Isla de la Estrellán*
- **Consonant assimilation with final consonants**:
  - *Chease* [csíz] $\rightarrow$ *Chease-zel*, *Chease-nek*
  - *Taylor Lautner* $\rightarrow$ *Lautnerrel*, *Taylorral*
  - *Bailey Pickett* $\rightarrow$ *Baileyvel*, *Pickett-tel*
  - *Tyler Posey* $\rightarrow$ *Poseyval*, *Tylerrel*

### D. Igényes Nyelvhasználat & Államférfiúi Regiszter
A szövegek a szuverén Waikiki hivatalos állami portáljának anyagát képezik, ezért megfogalmazásuknak méltóságteljesnek, választékosnak és gördülékenynek kell lennie:
- Kerüld a lapos, semmitmondó vagy hivatali szürkeségű mondatokat.
- Használj kifejező igéket és plasztikus jelzőket a sematikus fordulatok helyett.
- Kiemelt figyelemmel ügyelj a tudományos, űrkutatási, alpesi mérnöki és természetvédelmi terminusok pontos, természetes beillesztésére.

### E. Szóismétlések Szigorú Kiküszöbölése (Anti-Repetition)
Egászmás melletti vagy közeli mondatokban, felsorolásokban és kártyablokkokban tilos ugyanazt a tartalmas szót vagy szótövet megismételni. Használj gazdag szinonimakészletet:

| Gyakran ismételt kifejezés | Választékos magyar alternatívák |
| :--- | :--- |
| **biztosít** | szavatol, garantál, elősegíti, megalapozza, elmélyíti, záloga, szolgálja, nyújt |
| **számára** | részére, javára, polgároknak, lakosoknak, közösségnek, rétegnek |
| **kiemelkedő** | rangos, meghatározó, mérvadó, páratlan, élenjáró, számottevő, fenséges |
| **fejlesztés** | beruházás, korszerűsítés, bővítés, finomhangolás, modernizáció, gyarapodás |
| **lehetőséget nyújt** | utat nyit, teret enged, felvértezi, felkínálja, megnyitja kapuit, elérhetővé teszi |
| **zártkörű** | szűk körű, privát, meghitt, kötetlen, bizalmas, diszkrét |
| **területén** | szférájában, berkeiben, vonzáskörzetében, mezsgyéjén, horizontján |
| **különleges** | rendhagyó, egyedülálló, ritka, sajátos arculatú, unikális |

### F. Magyartalan Kifejezések és Szerkezetek Felszámolása
1. **Kerüld a terpeszkedő kifejezéseket és passzív igeneves szerkezeteket**:
   - Kerüld a „kerül lebonyolításra / átadásra / bemutatásra” típusú fordulatokat: használd az aktív igéket (*szervezik*, *adják át*, *mutatják be*).
   - Kerüld a felesleges elöljárószerű kifejezéseket (*„megvalósításra kerülő beruházás tekintetében”* $\rightarrow$ *„a megvalósuló beruházásban”*).
2. **Pleonazmusok és szóhalmozások megszüntetése**:
   - A nyilvánvaló vagy kétszeresen leírt tulajdonságokat finomítsd (pl. *„színpompás morpho-pillangók”* helyett *„lazúrkék morpho-pillangók”* vagy *„Morpho-pillangók”*).
3. **Természetes mondatfűzés és magyar szórend**:
   - A mondat hangsúlyos része kerüljön az ige elé (fókuszpozíció).
   - Ügyelj az igekötők természetes elválására és helyzetére.

---

## 5. English Style & Dialect Conventions

- **Dialect Consistency**: International and elevated UK/US spelling variants are supported. Accepted forms include:
  - `-our` variants (*colour*, *favour*, *honour*, *neighbour*) and `-or` variants.
  - `-ise / -isation` and `-ize / -ization`.
  - Standard terminology: *programme*, *manoeuvre*, *artefact*, *teleferic*, *sovereigntist*.
- **Compound Modifiers**: Hyphenate compound adjectives preceding nouns:
  - *carbon-neutral economy*, *zero-emission transport*, *deep-space outpost*, *high-speed corridor*, *near-rectilinear halo orbit*, *cryo-cooled glacier*.
- **Numbers in Headings**: Prefer numerals for technical and physical specifications (`Delta III B`, `115 m`, `35,000 kN`, `10 Astronauts`).

---

## 6. HTML Formatting & Structural Invariants

1. **Indentation**: Exactly 4 spaces per indentation level across all HTML tags.
2. **0 Empty Lines**: The document must contain zero blank or empty lines (`\n\n`).
3. **Alternating Section Styles**: Top-level page `<section>` elements must alternate strictly between normal and `light-bg` styles:
   - Section 1: `<section id="..." class="fade-in">`
   - Section 2: `<section id="..." class="light-bg fade-in">`
   - Section 3: `<section id="..." class="fade-in">`
4. **Card Structure**:
   - Each card in a grid contains an optional `<span class="card-icon">` (omitted for technical schematics/rockets), an optional `<span class="spec-badge">`, an `<h3>` heading, a `<p>` description, and an optional `<ul class="spec-list">`.
5. **Page Titles**: Must end with the standardized branding suffix:
   - Hungarian: `<title>Oldalcím — Waikiki Szuverén Állam</title>`
   - English: `<title>Page Title — Sovereign Nation of Waikiki</title>`

---

## 7. Style Guidelines & Design System Specifications (`STYLE-GUIDELINES.md`)

### A. Typography Hierarchy
- **Display Serif**: `Fraunces` (Google Fonts: 400, 600, 700, 800, italic, optical size 144)
  - Insignia, hero titles (`.hero-title`), section headlines (`.section-title`), stat numbers (`.stat-number`), card titles (`.card h3`), blockquotes.
- **Body & Interface**: `Manrope` (Google Fonts: 400, 500, 600, 700, 800)
  - Narrative body text (`p`, `.narrative-text`), navigation links, buttons, table data, subnav rails, chips.
- **Typographic Scale**:
  - Hero Title (`.hero-title`): `clamp(2.75rem, 6vw, 4.5rem)`, weight 800, line-height 1.05.
  - Section Title (`.section-title`): `clamp(2rem, 4vw, 3rem)`, weight 700, line-height 1.15.
  - Card Title (`.card h3`): `clamp(1.25rem, 2vw, 1.5rem)`, weight 700, line-height 1.25.
  - Hero Lead (`.hero-lead`): `clamp(1.1rem, 1.6vw, 1.35rem)`, weight 400, line-height 1.65.
  - Body Text (`p`, `.narrative-text`): `clamp(1rem, 1.3vw, 1.12rem)`, weight 400, line-height 1.8.
  - Eyebrow (`.hero-eyebrow`): `0.85rem`, weight 700, uppercase, tracking `0.18em`.

### B. Color Tokens & Palette
- **Primary Tokens**:
  - Canvas: `--sand-50: #FBF7F0`
  - Secondary Surface: `--sand-100: #F5EDE1`
  - Dividers: `--sand-200: #E8DCB8`
  - Brand Navy: `--primary-dark: #001830`, `--secondary: #002244`, `--primary: #003366`, `--primary-light: #1A528F`
  - Azure & Gold: `--tertiary: #6BA4D9`, `--accent: #C28A29`, `--accent-hover: #C95A41`, `--accent-light: #F5C46E`, `--accent-dark: #78531A`
- **Midnight Sovereign (Dark Mode)**:
  - Canvas: `#0A1420` · Surface Card: `#0E2035` · Surface Subtle: `#091626`
  - Text: Primary `#FBF7F0`, Secondary `#C2CDD8` · Accents: Glow `#6BA4D9`, Coral `#E3735A`
- **Province Identifiers**:
  - Waikiki: `--waikiki: #1A528F` · Amazonia: `--amazonia: #4E8B5A` · Brazilia: `--brazilia: #C28A29`

### C. Desktop-First Media Queries
- Base CSS rules define styles for large (desktop) screens.
- Media queries adapt for tablet and mobile strictly via `@media (max-width: ...)` breakpoints.
- Avoid using `min-width` media queries.

### D. Motion & Kinematics
- Curves: `ease-out: cubic-bezier(0.16, 1, 0.3, 1)`, `spring: cubic-bezier(0.34, 1.56, 0.64, 1)`, `curtain: cubic-bezier(0.76, 0, 0.24, 1)`.
- Core Motion: Curtain Navigation (400ms), Word-Split Hero Reveal (`.split-word`), Scroll Reveal (`.fade-in`, `.revealed`), Spotlight Tracking Cards, Stat Number Count-Up, Smart Header, Back-to-Top Progress Ring.

### E. Accessibility & Landmarks
- Required Landmarks: `<header>`, `<nav>`, `<main id="main">`, `<section>`, `<article>`, `<footer>`.
- Contrast: Strict minimum 4.5:1 text-to-background ratio in both light and dark modes.
- Respect `@media (prefers-reduced-motion: reduce)`.
- Keyboard focus visible: `--coral-500` glow with `outline-offset: 3px`.

---

## 8. Automated Audit & Formatting Tooling

Always execute the automated build and audit scripts after any content or style update:
- **Format and clean single file**:
  ```bash
  python3 scripts/build_pages.py --format <path/to/page.html>
  ```
- **Format and clean all pages**:
  ```bash
  python3 scripts/build_pages.py --format --all
  ```
- **Run copy quality & spell checker**:
  ```bash
  python3 .agents/skills/spell-check/scripts/audit.py <path/to/page.html>
  ```
- **Run bilingual parity checker**:
  ```bash
  python3 .agents/skills/locale-sync/scripts/sync_check.py <path/to/page.html>
  ```
- **Run text balance auditor**:
  ```bash
  python3 .agents/skills/text-balance/scripts/text_balance.py --static <path/to/page.html>
  ```
- **Clean and purge unused CSS**:
  ```bash
  purgecss --css css/*.css --output css/ --content **/*.html **/*.js --keyframes
  ```
