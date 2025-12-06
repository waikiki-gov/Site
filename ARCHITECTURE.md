# Site Architecture

## Overview

The Waikiki Government Site follows a modular architecture with clear separation between common components and page-specific implementations. This structure promotes maintainability, reusability, and easy extensibility for future pages.

## Directory Structure

```
/
├── css/
│   ├── common.css          # Shared styles across all pages
│   └── index.css           # Landing page specific styles
├── js/
│   ├── common.js           # Shared JavaScript functionality
│   └── index.js            # Landing page specific scripts
├── content/                # Markdown content files (canonical narrative sources)
├── index.html              # Landing page
├── .gitignore
├── .nojekyll
├── README.md
├── STYLE-GUIDELINES.md
└── ARCHITECTURE.md         # This file
```

## CSS Architecture

### common.css
Contains styles that are shared across all pages:
- **Reset & Root Variables** - Global CSS reset, color palette, and design tokens
- **Navigation** - Fixed navigation bar with logo and menu links
- **Footer** - Site-wide footer with links and copyright information
- **Common Animations** - Reusable animation keyframes (fadeIn, fadeInUp, slideIn, scaleIn)
- **Section Styles** - Base section layouts, titles, and introductory text
- **Card Components** - Unified card grid system with hover effects
- **Responsive Design** - Mobile breakpoints for common components

### index.css
Contains styles specific to the landing page:
- **Hero Section** - Large banner with animated background elements
- **Government Section** - Leadership cards with specialized styling
- **Economy Section** - Economic statistics display
- **Timeline Section** - Historical timeline with alternating layout
- **Responsive Overrides** - Mobile-specific adjustments for index page

## JavaScript Architecture

### common.js
Contains functionality shared across all pages:
- **Configuration** - Centralized constants (navbar height, scroll duration, thresholds)
- **Smooth Scrolling** - Anchor link navigation with custom easing
- **Intersection Observers** - Fade-in animations for sections and elements
- **Navigation Highlighting** - Active state management based on scroll position
- **Scroll Progress Indicator** - Visual progress bar at top of page
- **Card Hover Effects** - Enhanced interactivity for card components

### index.js
Contains functionality specific to the landing page:
- **Hero Parallax** - Parallax scrolling effect for hero section
- **Stats Animation** - Number counting animations (configurable)
- **Timeline Animation** - Scroll-based timeline reveal effects
- **Ripple Effects** - Interactive click feedback on stat items
- **Section Title Animation** - Enhanced entrance animations for titles

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

## Animation System

### Intersection Observer
All scroll-based animations use the Intersection Observer API for performance:
- Elements with `.fade-in` class automatically fade in when scrolled into view
- Configurable thresholds and root margins in `js/common.js`

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
- Horizontal menu links
- Responsive: Hides menu on mobile (< 768px)

### Hero Section (Index Page)
- Full-width banner with background animations
- Large title and subtitle
- Statistics display with hover effects
- Animated floating background elements

### Card Grid System
- Responsive grid layout (auto-fit, minmax(350px, 1fr))
- Consistent padding and border radius
- Hover animations (lift and scale)
- Icon support with proper sizing

### Timeline Component (Index Page)
- Alternating left/right layout
- Central vertical line
- Animated dots at each milestone
- Hover effects on timeline items

### Footer
- Full-width dark background
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
- Additional page templates (government, society, economy detail pages)
- Internationalization (i18n) support
- Accessibility improvements (ARIA labels, keyboard navigation)
- Progressive Web App (PWA) capabilities
- Service Worker for offline support

### Optimization Opportunities
- CSS and JS minification for production
- Image optimization and lazy loading
- Critical CSS inlining
- Resource preloading for fonts and assets
- CDN integration for static assets

## Maintenance Notes

### When Adding New Common Styles
1. Add to `css/common.css` only if used by 2+ pages
2. Use semantic class names
3. Follow existing naming conventions
4. Add comments for complex selectors

### When Adding New Common Scripts
1. Add to `js/common.js` only if used by 2+ pages
2. Use function declarations with clear names
3. Add JSDoc comments for public functions
4. Call from `initCommon()` function

### Version Control
- All CSS/JS files are tracked in git
- Old files (`styles.css`, `script.js`) should be removed after migration
- Use `.gitignore` for build artifacts and dependencies

## References

- [README.md](README.md) - Project overview and narrative content
- [STYLE-GUIDELINES.md](STYLE-GUIDELINES.md) - Content and design guidelines
- [content/](content/) - Canonical Markdown sources for site content
