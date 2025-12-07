# Site Architecture

## Overview

The Waikiki Government Site follows a modular architecture with clear separation between common components and page-specific implementations. This structure promotes maintainability, reusability, and easy extensibility for future pages.

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
- **Reset & Root Variables** - Global CSS reset, color palette, design tokens, and CSS custom properties for animations/spacing
- **Navigation** - Fixed navigation bar with logo and menu links
- **Hamburger Menu** - Mobile-friendly slide-out navigation panel
- **Footer** - Site-wide footer with links and copyright information
- **Common Animations** - Reusable animation keyframes (fadeIn, fadeInUp, slideIn, scaleIn)
- **Hero Section** - Common hero banner styles used across multiple pages
- **Section Styles** - Base section layouts, titles, and introductory text
- **Card Components** - Unified card grid system with hover effects and staggered animations
- **Responsive Design** - Mobile breakpoints for common components

### Page-Specific CSS Files

#### index.css
- **Hero Decorations** - Floating background elements for landing page
- **Government Section** - Leadership cards with specialized styling
- **Economy Section** - Economic statistics display
- **Timeline Section** - Historical timeline with alternating layout
- **Responsive Overrides** - Mobile-specific adjustments for index page

#### economy.css
- **Data Visualization** - Chart containers and wrappers for Chart.js
- **Area Charts** - SVG-based area chart styles with labels
- **Bar Charts** - Vertical and horizontal bar chart styles
- **Donut Charts** - Circular chart visualizations
- **Line Charts** - Multi-line chart styles with data points
- **Stats Grid** - Metric display cards
- **Responsive Charts** - Mobile adaptations for all visualizations

#### history.css
- **Hero Decorations** - Subtle floating elements for history page
- **Expanded Timeline** - Period-based timeline with event markers
- **Narrative Content** - Text styling for historical narratives
- **Event Markers** - Interactive timeline dots and connectors
- **Responsive Timeline** - Mobile-friendly timeline layout

#### tourism.css
- **Hero Styling** - Tourism-specific hero section with decorative elements
- **Stat Items** - Tourism statistics display
- **Card Enhancements** - Tourism-specific card hover effects
- **Responsive Design** - Mobile adaptations for tourism content

#### wealth-fund.css
- **Timeline Styles** - Wealth fund history timeline
- **Priority Lists** - Investment priority displays
- **Projection Charts** - Future value projections
- **Stats Grid** - Fund performance metrics
- **Responsive Design** - Mobile layout for fund information

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

## Animation System

### CSS Custom Properties for Animation Timing
All animation timing is centralized using CSS custom properties for consistency:
```css
--transition-duration: 0.5s;              /* Standard transition duration */
--transition-easing: cubic-bezier(0.4, 0, 0.2, 1);  /* Smooth easing function */
--animation-duration: 0.8s;               /* Standard animation duration */
--base-animation-delay: 0.05s;            /* Starting delay for staggered animations */
--animation-delay-increment: 0.08s;       /* Increment between staggered items */
```

### Staggered Animation Delays
Elements use calculated delays for natural staggered appearance:
```css
.card:nth-child(1) { animation-delay: calc(var(--base-animation-delay) + 0 * var(--animation-delay-increment)); }
.card:nth-child(2) { animation-delay: calc(var(--base-animation-delay) + 1 * var(--animation-delay-increment)); }
/* And so on... */
```

This ensures:
- Consistent timing across all pages
- Easy global adjustment by changing CSS variables
- Earlier appearance on scroll (base delay reduced from 0.15s to 0.05s)
- Smoother visual flow with smaller increments (0.08s vs 0.1s)

### Intersection Observer
All scroll-based animations use the Intersection Observer API for performance:
- Elements with `.fade-in` class automatically fade in when scrolled into view
- Configurable thresholds and root margins in `js/common.js`
- Root margin set to `-100px` for earlier triggering (reduced from `-200px`)

### CSS Animations
Predefined keyframe animations in `common.css`:
- `fadeIn` - Simple opacity transition
- `fadeInUp` - Fade in with upward motion
- `slideInFromTop` - Slide down entrance
- `slideInFromLeft` - Slide from left entrance
- `scaleIn` - Scale up with fade in

### Custom Easing
JavaScript smooth scroll uses custom cubic easing for natural feel:
```javascript
const ease = progress < 0.5
    ? 4 * progress * progress * progress
    : 1 - Math.pow(-2 * progress + 2, 3) / 2;
```

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

Minimum browser versions:
- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Future Considerations

### Potential Enhancements
- Dark mode support using the defined `--dark-bg` variable
- Additional page templates for new content sections
- Internationalization (i18n) support
- Enhanced accessibility improvements (ARIA labels, keyboard navigation)
- Progressive Web App (PWA) capabilities
- Service Worker for offline support

### Optimization Opportunities
- CSS and JS minification for production
- Image optimization and lazy loading
- Critical CSS inlining
- Resource preloading for fonts and assets
- CDN integration for static assets

### Recent Improvements (2025-12-07)
- **Removed all color gradients** - Replaced with solid colors and opacity variations for cleaner appearance
- **CSS custom properties** - Added variables for animation timing, transitions, and spacing
- **Consolidated animations** - Unified timing using calculated delays based on CSS variables
- **Cleaned up duplicates** - Removed ~661 lines of duplicate CSS (23% reduction)
- **Extracted common hero** - Moved shared hero section styles to common.css
- **Earlier animations** - Reduced root margin from -200px to -100px and base delay from 0.15s to 0.05s
- **Simplified history.css** - Removed all duplicates, reduced from 891 to 205 lines

## Maintenance Notes

### When Adding New Common Styles
1. Add to `css/common.css` only if used by 2+ pages
2. Use semantic class names
3. Follow existing naming conventions
4. Add comments for complex selectors
5. Utilize CSS custom properties for values that may need adjustment
6. Avoid color gradients - use solid colors with opacity variations

### When Adding New Common Scripts
1. Add to `js/common.js` only if used by 2+ pages
2. Use function declarations with clear names
3. Add JSDoc comments for public functions
4. Call from `initCommon()` function
5. Use CONFIG object for configurable values

### When Adding New Pages
1. Link to `common.css` for base styles
2. Create page-specific CSS only for unique styling needs
3. Use common hero section structure where applicable
4. Include `common.js` for base functionality
5. Follow staggered animation patterns using CSS custom properties
6. Ensure hamburger menu includes link to new page

### Version Control
- All CSS/JS files are tracked in git
- Use `.gitignore` for build artifacts and dependencies
- Removed files (old versions) should be cleaned up after migration
- Commit messages should clearly describe optimization changes

## References

- [README.md](README.md) - Project overview and narrative content
- [STYLE-GUIDELINES.md](STYLE-GUIDELINES.md) - Content and design guidelines
- [content/](content/) - Canonical Markdown sources for site content
