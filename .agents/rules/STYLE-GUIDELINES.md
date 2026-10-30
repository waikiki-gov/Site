# Sovereign Nation of Waikiki — Style Guidelines
**Tropical Luxe & Lagoon Night Design System**
*Version 3.0 · Sovereign Identity & Modern Web Standard*

---

## 1. Design Vision & Philosophy

The Sovereign Nation of Waikiki digital identity is rooted in **Tropical Luxe** — an editorial, sovereign, warm, and highly kinetic design language inspired by the Caribbean seas, the lush Amazonian rainforest, warm sunlit sands, and royal heritage.

- **Warm and Sovereign**: Replacing generic corporate colors with warm ivory sands (`#FBF7F0`), sovereign navy (`#003366`), deep midnight navy (`#002244`), luminous azure (`#6BA4D9`), vibrant coral/terracotta (`#C95A41`), and regal brass/gold (`#C28A29`).
- **Kinetic and Atmospheric**: Scroll-driven storytelling, word-split headline reveals, pointer-reactive spotlight glow cards, smooth page transit curtains, and an interactive back-to-top progress ring.
- **Editorial Typography**: A dual-type pairing featuring `Fraunces` (high-contrast display optical serif) and `Manrope` (clean, contemporary geometric grotesque).
- **Dual Sovereign Modes**: Default *Tropical Luxe Light* and *Midnight Sovereign* dark mode with seamless preference persistence (`localStorage.isDarkMode`).

---

## 2. Color Palette and Design Tokens

### Primary Palette (Sovereign Navy and Tropical Sands)
| Token | Value | Semantic Role |
| :--- | :--- | :--- |
| `--sand-50` | `#FBF7F0` | Primary page canvas, warm ivory backdrop |
| `--sand-100` | `#F5EDE1` | Secondary surface, subtle contrast bands |
| `--sand-200` | `#E8DCB8` | Warm border accents, subtle dividers |
| `--primary-dark` | `#001830` | Deepest brand tone, midnight headers, high-contrast text |
| `--secondary` | `#002244` | Secondary midnight navy, hero veils, badges, button backdrops |
| `--primary` | `#003366` | Primary sovereign navy, interactive elements, active links |
| `--primary-light` | `#1A528F` | Vibrant royal blue, province tone, success states |
| `--tertiary` | `#6BA4D9` | Soft azure glow, luminous indicators, dark mode primary |
| `--accent` | `#C28A29` | Accent gold, royal insignia, stars, timeline nodes, brass accents |
| `--accent-hover` | `#C95A41` | Dynamic accent coral/amber, active states, callouts |
| `--accent-light` | `#F5C46E` | Illuminated gold accents, night mode badges |
| `--accent-dark` | `#78531A` | Deep antique gold, high contrast brass text |

### Midnight Sovereign Palette (Dark Mode)
| Token | Value | Semantic Role |
| :--- | :--- | :--- |
| Canvas | `#0A1420` | Deep midnight sovereign background |
| Surface Card | `#0E2035` | Glassmorphic floating surfaces with 1px azure border |
| Surface Subtle | `#091626` | Secondary dark surface, header backdrop |
| Text Primary | `#FBF7F0` | High-contrast ivory text |
| Text Secondary | `#C2CDD8` | Muted cool slate body text |
| Accent Glow | `#6BA4D9` | Soft azure luminous indicators |
| Accent Coral | `#E3735A` | Vivid nocturnal highlight |

### Province Identity Colors
- **Waikiki Province**: `--waikiki: #1A528F`, hover: `#296BB3` (Deep sovereign azure)
- **Amazonia Province**: `--amazonia: #4E8B5A`, hover: `#62A56F` (Lush Amazonian emerald)
- **Brazilia Province**: `--brazilia: #C28A29`, hover: `#ECC677` (Warm sunlit brass)

### Private Page Colors
- **Private Section**: `--private: #0A1930` (Midnight navy base)
- **Intimate Section**: `--intimate: #3D1520` (Deep royal wine backdrop)
- **Adventure Section**: `--adventure: #123F43` (Deep oceanic teal)
- **Milestones Section**: `--milestones: var(--secondary)` (`#002244` - Midnight navy secondary)

---

## 3. Typography Hierarchy

### Typefaces
- **Display Serif**: `Fraunces` (Google Fonts: 400, 600, 700, 800, italic, optical size 144)
  - Used for: Brand insignia, hero titles, section headlines, stat numbers, card titles, quotes.
- **Body & Interface**: `Manrope` (Google Fonts: 400, 500, 600, 700, 800)
  - Used for: Narrative body text, navigation links, buttons, table data, subnavigation, chips.

### Scale & Hierarchy
- **Hero Title (`.hero-title`)**: `clamp(2.75rem, 6vw, 4.5rem)`, weight 800, line-height 1.05, tracking `-0.02em`.
- **Section Title (`.section-title`)**: `clamp(2rem, 4vw, 3rem)`, weight 700, line-height 1.15. Decorated with warm gradient accent pill.
- **Card Title (`.card h3`, `.admin-card h3`)**: `clamp(1.25rem, 2vw, 1.5rem)`, weight 700, line-height 1.25.
- **Hero Lead (`.hero-lead`)**: `clamp(1.1rem, 1.6vw, 1.35rem)`, weight 400, line-height 1.65.
- **Body Text (`p`, `.narrative-text`)**: `clamp(1rem, 1.3vw, 1.12rem)`, weight 400, line-height 1.8.
- **Eyebrow / Subhead (`.hero-eyebrow`)**: `0.85rem`, weight 700, uppercase, tracking `0.18em`, coral glow.

### Editorial & Typography Standards
- **Ampersand Usage**: Always prefer the written word **"and"** (in English) and **"és"** (in Hungarian) instead of the ampersand symbol (`&` / `&amp;`) in titles, section headlines, card titles, and body copy.

---

## 4. Motion Engine & Kinematics

All motion follows natural organic physics with custom cubic Bézier curves:
- **Ease Out (Deceleration)**: `cubic-bezier(0.16, 1, 0.3, 1)` — default for modals, menus, cards.
- **Spring (Snappy overshoot)**: `cubic-bezier(0.34, 1.56, 0.64, 1)` — badges, active pills, icons.
- **Curtain Transit**: `cubic-bezier(0.76, 0, 0.24, 1)` — page transition curtains (400ms).

### Core Motion Behaviors
1. **Curtain Navigation**:
   - Internal links activate an SVG/glass curtain that slides up smoothly before loading target pages, ensuring an app-like seamless feel.
2. **Word-Split Hero Reveal**:
   - Titles with `.split-word` split into animated inline spans that rise with staggered delays (`calc(0.04s * index)`).
3. **Scroll Reveal (`.fade-in`, `.revealed`)**:
   - Elements automatically observe intersection and enter with subtle translation (`translateY(24px)`) and opacity fade.
4. **Spotlight Tracking Cards (`.card`, `.hover-card`)**:
   - Cards track cursor coordinates (`--mouse-x`, `--mouse-y`) to cast a subtle radial light across their glass surface.
5. **Statistic Number Count-Up (`.stat-number`, `.economy-number`)**:
   - Animates numbers smoothly from 0 to target value on scroll entry with ease-out interpolation.
6. **Smart Header**:
   - Transparent over hero; shrinks to compact blur header upon scrolling; automatically hides on rapid scroll-down and reveals on scroll-up.
7. **Floating Back-to-Top with Progress Ring**:
   - Bottom-right FAB featuring an SVG circle that tracks total page scroll progress percentage, elevating on hover.

---

## 5. UI Components

### Navigation & Header
- **Sovereign Heraldic Emblem (`icons/logo.svg`)**: Standalone detailed vector SVG asset incorporating Waikiki's constitutional national symbols:
  - **The Three Pyramids**: Central Great Pyramid with 6 architectural ashlar masonry courses, gilded capstone and star apex, flanked by the stepped pyramids of Amazonia and Brazilia provinces with faceted lighting.
  - **Tropical Palms**: Segmented coconut palm tree with textured bark rings and 7 feathered, arching fronds with individual leaf pinnae and tropical coconut clusters.
  - **Sovereign Elephant**: Heraldic elephant with raised trunk, polished ivory tusk, sculpted ear, and royal embroidered ceremonial saddle blanket.
  - **Laurel Wreath & Waves**: Twin golden laurel branches bound by a heraldic knot, hovering over dual ocean waves.
- **Fixed Glass Bar**: Glassmorphism with `backdrop-filter: blur(20px)` and subtle sand border.
- **Nav Links**: Magnetic subtle hover lift with animated underline pill.
- **Overlay Menu**: Full-screen luxury drawer featuring multi-column categorized site links, stable typography (no font change on hover), and a live Havana/Nova Aurelia clock.
- **Subnavigation Rail**: Sticky horizontal pill menu for deep page section jumps with active indicator tracking.

### Cards & Surfaces
- **Glassmorphism Tokens**:
  - `background: var(--surface-card)` (`#FFFFFF` in light, `#112A28` in night).
  - `border: 1px solid var(--border-subtle)`.
  - `box-shadow: 0 16px 36px -12px rgba(11, 59, 58, 0.12)`.
  - Hover state: `transform: translateY(-6px)`.

### Buttons & Controls
- **Primary Button (`.btn-primary`)**: Lagoon teal gradient into coral with warm sand text, pill radius, smooth scale on click.
- **Secondary Button (`.btn-secondary`)**: Translucent sand/glass with fine border, coral hover glow.
- **Theme Toggle (`.theme-toggle`)**: Dual-state sun/moon icon button with smooth rotation transition and instant theme application.

---

## 6. Accessibility & SEO Standards

- **Semantic Landmarks**: `<header>`, `<nav>`, `<main id="main">`, `<section>`, `<article>`, `<footer>`.
- **Contrast Compliance**: Minimum 4.5:1 text-to-background contrast ratio across both Light and Night modes.
- **Motion Reduction**: `@media (prefers-reduced-motion: reduce)` disables transit curtains and continuous animations for sensitive users.
- **Keyboard Navigation**: Clear `:focus-visible` rings with `--coral-500` glow and `outline-offset: 3px`.
- **Multilingual Semantics**: Proper `hreflang="hu"` and `hreflang="en"` links on language selectors; `lang` attributes on `<html>`.
- **Responsive Media Queries**: Desktop-first architecture. Base rules define large-screen styles; adaptations for smaller viewports use `@media (max-width: ...)` queries, avoiding `min-width` media queries.
- **Remove unused css**: `purgecss --css css/*.css --output css/ --content **/*.html **/*.js`