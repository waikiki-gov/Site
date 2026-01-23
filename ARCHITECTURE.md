# Site Architecture

## Overview

The Waikiki Government Site follows a modular architecture with clear separation between common components and page-specific implementations. This structure promotes maintainability, reusability and easy extensibility for future pages.

## Directory Structure

```
/
├── css/
│   ├── common.css          # Shared styles across all pages
│   ├── index.css           # Landing page styles
│   ├── economy.css         # Economy page visualizations
│   ├── history.css         # History page timeline styles
│   ├── faq.css             # FAQ page styles
│   ├── parties.css         # Parties page styles
│   ├── wealth-fund.css     # Wealth fund page styles
│   └── ...                 # additional page-specific styles
├── js/
│   ├── common.js           # Shared JavaScript functionality
│   ├── economy.js          # Economy page chart and data logic
│   ├── wealth-fund.js      # Wealth fund page scripts
│   ├── chart.min.js        # Chart.js library
│   └── ...                 # other page scripts
├── content/                # Canonical Markdown content sources
├── icons/                  # Icon and SVG assets
├── images/                 # Images and illustrations
├── index.html              # Landing page (locale selector)
├── en/                     # English localized pages
│   ├── index.html          # Landing page
│   ├── economy.html        # Economic data and visualizations
│   ├── history.html        # National history timeline
│   ├── tourism.html        # Tourist information
│   ├── wealth-fund.html    # National Wealth Fund information
│   ├── diplomacy.html      # International relations
│   ├── culture.html        # Cultural information
│   ├── leadership.html     # Leadership biographies
│   ├── military.html       # Military information
│   ├── parties.html        # Political parties
│   ├── faq.html            # FAQ
│   └── ...                 # Other English-localized pages
├── hu/                     # Hungarian localized pages
│   ├── index.html          # Landing page
│   ├── economy.html        # Economic data and visualizations
│   ├── history.html        # National history timeline
│   ├── tourism.html        # Tourist information
│   ├── wealth-fund.html    # National Wealth Fund information
│   ├── diplomacy.html      # International relations
│   ├── culture.html        # Cultural information
│   ├── leadership.html     # Leadership biographies
│   ├── military.html       # Military information
│   ├── parties.html        # Political parties
│   ├── faq.html            # FAQ
│   └── ...                 # Other Hungarian-localized pages
├── .gitignore
├── .nojekyll
├── README.md
├── STYLE-GUIDELINES.md
└── ARCHITECTURE.md         # This file
```

## Localization

- Bilingual layout with parallel directories: English pages in `en/`, Hungarian pages in `hu/`
- Localized HTML files mirror page names and pull shared assets from `css/`, `js/`, `icons/`, and `images/`
- Canonical narrative lives in `content/` and should remain the single source of truth for both locales
- When adding a new page, create both `en/`, and `hu/` variants to keep navigation and URLs aligned

## CSS Architecture

### common.css
Contains styles that are shared across all pages:
- **Reset & Root Variables** - Global CSS reset, color palette, design tokens and CSS custom properties for animations/spacing
- **Navigation** - Fixed navigation bar with logo and menu links
- **Hamburger Menu** - Mobile-friendly slide-out navigation panel
- **Footer** - Site-wide footer with links and copyright information
- **Common Animations** - Reusable animation keyframes (fadeIn, fadeInUp, slideIn, scaleIn)
- **Hero Section** - Common hero banner styles used across multiple pages
- **Section Styles** - Base section layouts, titles and introductory text
- **Card Components** - Unified card grid system with hover effects and staggered animations
- **Responsive Design** - Mobile breakpoints for common components

## JavaScript Architecture

### common.js
Contains functionality shared across all pages:
- **Configuration** - Centralized constants (navbar height, scroll duration, thresholds, animation timing)
- **Smooth Scrolling** - Anchor link navigation with custom easing
- **Intersection Observers** - Fade-in animations for sections and elements
- **Navigation Highlighting** - Active state management based on scroll position
- **Scroll Progress Indicator** - Visual progress bar at top of page
- **Card Hover Effects** - Enhanced interactivity for card components
- **Hamburger Menu** - Mobile navigation panel with overlay and interactions

### Page-Specific JavaScript Files

#### common.js
- Shared initialization, smooth scrolling, intersection observers, navigation highlighting, and common UI behaviors

#### economy.js
- Chart initialization and configuration for Chart.js
- Data processing: transform CSV/JSON for charts
- Interactive charts: tooltips and hover interactions

#### wealth-fund.js
- Timeline rendering for the wealth fund
- Projection calculations and interactive detail panels

Note: `index.js` and `tourism.js` are not present in the repository; add them if page-specific scripts are required for those pages.

## Data sources and content

- Canonical content is stored as Markdown in the `content/` folder. These files are the authoritative source for page copy
- Tabular economic and statistical data is stored in `csv/` and processed by `js/economy.js`
- Image and icon assets live in `images/` and `icons/`

## Design principles

### Separation of Concerns
- **Common files** contain only code that will be reused across multiple pages
- **Page-specific files** contain code unique to that page
- No duplication between common and page-specific files

### Modularity
- Each CSS/JS file is independently functional
- Pages can mix and match components as needed
- Easy to add new pages by extending common base

### Performance
- CSS organized by component hierarchy
- JavaScript uses modern APIs (Intersection Observer, RequestAnimationFrame)
- Minimal DOM manipulation
- Efficient event delegation where appropriate

### Maintainability
- Clear file naming conventions (common.css, index.css, etc.)
- Well-commented code with JSDoc annotations
- Consistent code style across all files
- Logical grouping of related functionality

## Adding New Pages

To add a new page to the site:

1. Create the HTML file in the root directory (e.g., `about.html`)
2. Link to common.css for base styles:
   ```html
   <link rel="stylesheet" href="css/common.css">
   ```
3. Create page-specific CSS if needed (e.g., `css/about.css`):
   ```html
   <link rel="stylesheet" href="css/about.css">
   ```
4. Include common.js for base functionality:
   ```html
   <script src="js/common.js"></script>
   ```
5. Create page-specific JS if needed (e.g., `js/about.js`):
   ```html
   <script src="js/about.js"></script>
   ```

## Color Palette

The site uses a consistent color scheme defined in CSS custom properties:

- **Primary**: `#0071BC` - Main brand color, used for navigation and accents
- **Secondary**: `#0E308E` - Dark blue for headings and emphasis
- **Tertiary**: `#00B0C3` - Bright cyan for highlights
- **Gold**: `#BC9200` - Accent color for special elements
- **Silver**: `#555555` - Body text color
- **White**: `#FFFFFF` - Background and text on dark backgrounds
- **Light BG**: `#F5F9FC` - Subtle background for sections
- **Dark BG**: `#0A1930` - Reserved for future dark theme

**Design Principle**: No color gradients are used. All backgrounds use solid colors or subtle opacity variations to maintain a clean, professional appearance.

## Component Reference

### Navigation Bar
- Fixed position at top of page
- Logo with Waikiki symbol (₩)
- Horizontal menu links (on desktop)
- Hamburger menu for cross-page navigation
- Responsive: Switches to hamburger menu on mobile (< 768px)

### Hamburger Menu
- Fixed-position slide-out panel from right side
- Overlay background when open
- Links to all major pages
- Iconify icons for visual clarity
- Smooth transitions and keyboard support (ESC to close)

### Hero Section (Common Template)
- Full-width banner with subtle decorative elements
- Large title and subtitle
- Optional description text
- Statistics display with hover effects
- Animated entrance with staggered delays
- No color gradients (solid colors with opacity variations only)

### Card Grid System
- Responsive grid layout (auto-fit, minmax(350px, 1fr))
- Consistent padding (2.5rem) and border radius (20px)
- Hover animations (lift and scale)
- Staggered entrance animations
- Icon support with proper sizing
- Uses CSS custom properties for spacing

### Timeline Component (Index Page)
- Alternating left/right layout
- Central vertical line
- Animated dots at each milestone
- Hover effects on timeline items
- Calculated animation delays for smooth appearance

### Expanded Timeline (History Page)
- Period-based grouping
- Event markers with connecting lines
- Hover effects on markers and content
- Responsive single-column layout on mobile

### Footer
- Full-width background with secondary color
- Centered link menu matching navigation
- Copyright and additional information
- Hover effects on links

## Browser Support

The site uses modern web APIs and CSS features:
- CSS Custom Properties (CSS Variables)
- CSS Grid and Flexbox
- Intersection Observer API
- RequestAnimationFrame
- ES6+ JavaScript

## References

- [README.md](README.md) - Project overview and narrative content
- [STYLE-GUIDELINES.md](STYLE-GUIDELINES.md) - Content and design guidelines
- [content/](content/) - Canonical Markdown sources for site content
