# Site Architecture

## Overview

The Waikiki Government Site follows a modular architecture with clear separation between common components and page-specific implementations. This structure promotes maintainability, reusability and easy extensibility for future pages.

## Directory Structure

```
/
├── css/
│   ├── common.css          # Shared styles across all pages
│   ├── index.css           # Landing page specific styles
│   ├── economy.css         # Economy page visualizations
│   ├── history.css         # History page timeline styles
│   ├── tourism.css         # Tourism page specific styles
│   └── wealth-fund.css     # Wealth fund page specific styles
├── js/
│   ├── common.js           # Shared JavaScript functionality
│   ├── index.js            # Landing page specific scripts
│   ├── economy.js          # Economy page chart logic
│   ├── tourism.js          # Tourism page specific scripts
│   ├── wealth-fund.js      # Wealth fund page specific scripts
│   └── chart.min.js        # Chart.js library
├── content/                # Markdown content files (canonical narrative sources)
├── index.html              # Landing page
├── economy.html            # Economic data and visualizations
├── history.html            # National history timeline
├── tourism.html            # Tourist information
├── wealth-fund.html        # National Wealth Fund information
├── diplomacy.html          # International relations
├── culture.html            # Cultural information
├── leadership.html         # Leadership biographies
├── military.html           # Military information
├── parties.html            # Political parties
├── .gitignore
├── .nojekyll
├── README.md
├── STYLE-GUIDELINES.md
└── ARCHITECTURE.md         # This file
```

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

### Page-Specific CSS Files


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

#### index.js
- **Hero Parallax** - Parallax scrolling effect for hero section
- **Stats Animation** - Number counting animations (configurable)
- **Timeline Animation** - Scroll-based timeline reveal effects
- **Ripple Effects** - Interactive click feedback on stat items
- **Section Title Animation** - Enhanced entrance animations for titles

#### economy.js
- **Chart Initialization** - Setup for Chart.js visualizations
- **Data Processing** - Transform economic data for charts
- **Interactive Charts** - Hover effects and tooltips for data points

#### tourism.js
- **Lightweight Enhancements** - Relies primarily on common.js fade-in system
- **Page-Specific Animations** - Any tourism-specific interactive elements

#### wealth-fund.js
- **Timeline Rendering** - Generate wealth fund history timeline
- **Projection Calculations** - Future value projection logic
- **Interactive Elements** - Fund-specific interactive features

## Design Principles

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

## Future Considerations

### Potential Enhancements
- Dark mode support using the defined `--dark-bg` variable
- Additional page templates for new content sections
- Internationalization (i18n) support
- Enhanced accessibility improvements (ARIA labels, keyboard navigation)
- Progressive Web App (PWA) capabilities
- Service Worker for offline support

## References

- [README.md](README.md) - Project overview and narrative content
- [STYLE-GUIDELINES.md](STYLE-GUIDELINES.md) - Content and design guidelines
- [content/](content/) - Canonical Markdown sources for site content
