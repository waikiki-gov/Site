# Waikiki Website Style Guidelines

## Overview
This document defines the design system and style guidelines for the Waikiki official website. All changes and additions should follow these guidelines to maintain consistency and professional appearance.

## Color Palette

### Primary Colors
- **Primary Blue**: `#0071BC` - Main brand color, used for navigation, links, accents
- **Secondary Blue**: `#0E308E` - Headings, important text
- **Tertiary Cyan**: `#00B0C3` - Accents, highlights

### Accent Colors
- **Gold**: `#BC9200` - Premium elements, important stats, royal family elements
- **Silver**: `#555555` - Body text, secondary information

### Background Colors
- **White**: `#FFFFFF` - Card backgrounds, content areas
- **Light Background**: `#F5F9FC` - Alternate section backgrounds
- **Dark Background**: `#0A1930` - Footer, dark sections

## Typography

### Font Family
- Primary: `Inter`, fallback to system fonts (`Segoe UI`, `Tahoma`, `Geneva`, `Verdana`, `sans-serif`)
- Load from Google Fonts: `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap`

### Font Sizes
- **Headings**:
  - H1 (Hero): `4rem` (64px)
  - H2 (Section Titles): `3rem` (48px)
  - H3 (Card Titles): `1.6rem` (25.6px)
- **Body Text**: `1rem` (16px), line-height `1.6`
- **Section Intro**: `1.2rem` (19.2px), line-height `1.8`
- **Small Text**: `0.95rem` (15.2px)

### Font Weights
- Light: `300`
- Regular: `400`
- Medium: `500`
- Semi-bold: `600`
- Bold: `700`
- Extra-bold: `800`

## Spacing System

### Standard Spacing Units
- **Sections**: `100px` vertical padding (80px for compact sections)
- **Cards**: `2.5rem` padding
- **Grid Gaps**: `2.5rem` between cards
- **Margins**:
  - Section title bottom: `1.5rem`
  - Card title bottom: `1.2rem`
  - Between elements: `4rem`

## Components

### Cards
```css
background: white
padding: 2.5rem
border-radius: 20px
box-shadow: 0 8px 30px rgba(0,0,0,0.08)
border-left: 5px solid var(--primary)
```

**Hover State:**
```css
transform: translateY(-8px) scale(1.03)
box-shadow: 0 16px 50px rgba(0,0,0,0.12)
border-left-width: 8px
```

### Leader Cards
```css
background: white
padding: 2.5rem
border-radius: 20px
box-shadow: 0 8px 30px rgba(0,0,0,0.08)
border-top: 5px solid var(--gold)
text-align: center
```

**Hover State:**
```css
transform: translateY(-8px) scale(1.03)
box-shadow: 0 16px 50px rgba(0,0,0,0.15)
```

### Stat Items (Hero Section)
```css
background: rgba(255, 255, 255, 0.12)
padding: 2rem 2.5rem
border-radius: 16px
backdrop-filter: blur(10px)
border: 1px solid rgba(255, 255, 255, 0.2)
```

**Hover State:**
```css
transform: translateY(-8px) scale(1.03)
background: rgba(255, 255, 255, 0.18)
```

## Animations & Transitions

### Standard Timing
- **Transition Duration**: `0.5s` (500ms) for all hover effects
- **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)` for smooth, professional feel
- **Entry Animation Duration**: `0.8s` (800ms) with staggered delays

### Hover Effects - Unified
All interactive elements use consistent hover animations:
- **Transform**: `translateY(-8px) scale(1.03)`
- **No 3D transforms**: Avoid `rotate3d`, `rotateX`, `rotateY`
- **No aggressive scaling**: Maximum scale is `1.03`
- **Consistent shadow enhancement**: Increase shadow spread on hover

### Entry Animations
**Staggered Delays:**
- First item: `0.15s`
- Increment: `0.1s` per item (0.15s, 0.25s, 0.35s, ...)

**fadeInUp Animation:**
```css
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(40px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

**scaleIn Animation (for stat items):**
```css
@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.8);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}
```

## Smooth Scrolling

### Anchor Scroll Behavior
- Duration: `1200ms` (1.2 seconds)
- Easing: Cubic easing with smooth acceleration and deceleration
- Offset: `-80px` to account for fixed navigation

## Icons

### Guidelines
- Prefer official icon sets or high-quality images over emoji
- Icon size in cards: `3.5rem` (56px)
- Icons should be meaningful and relevant to content
- Consistent style across all sections

### Recommended Sources
- Official government/institutional icons when available
- SVG icons from reputable icon libraries
- Custom-designed icons matching brand colors

## Grid Layouts

### Card Grids
```css
display: grid
grid-template-columns: repeat(auto-fit, minmax(350px, 1fr))
gap: 2.5rem
```

### Leadership Grid
```css
display: grid
grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))
gap: 2.5rem
```

## Responsive Design

### Breakpoints
- Mobile: `max-width: 768px`
- Tablet: `769px - 1024px`
- Desktop: `1025px+`

### Mobile Adjustments
- Reduce padding: `1.5rem` instead of `3rem`
- Smaller font sizes for headings
- Single column layouts
- Simplified navigation

## Best Practices

### DO:
- ✅ Use consistent spacing throughout
- ✅ Apply unified hover effects (translateY + scale)
- ✅ Use the defined color palette
- ✅ Maintain 0.5s transition duration
- ✅ Use cubic-bezier easing
- ✅ Test animations on different devices
- ✅ Ensure accessibility (contrast ratios, focus states)

### DON'T:
- ❌ Use 3D rotations or transforms
- ❌ Mix different animation timings randomly
- ❌ Use harsh or sudden animations
- ❌ Scale elements beyond 1.05x
- ❌ Use colors outside the defined palette
- ❌ Create inconsistent spacing
- ❌ Use excessive animations

## Accessibility

### Requirements
- Color contrast ratio: Minimum 4.5:1 for body text
- Color contrast ratio: Minimum 3:1 for large text (18pt+)
- All interactive elements must have focus states
- Support keyboard navigation
- Meaningful alt text for images
- ARIA labels where appropriate

### Focus States
```css
:focus {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
}
```

## Performance

### Optimization
- Use CSS transitions over JavaScript animations when possible
- Minimize DOM manipulation
- Use `will-change` property sparingly
- Optimize images (WebP format where supported)
- Lazy load images below the fold
- Debounce scroll events

## Browser Support

### Targets
- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 13+, Chrome Android Latest

### Fallbacks
- Provide fallbacks for `backdrop-filter`
- Ensure site is functional without JavaScript
- Test on browsers without CSS Grid support

## Version History

- **v1.0** (2025-12-06): Initial style guidelines established
  - Unified animations to 0.5s with cubic-bezier easing
  - Standardized hover effects (translateY -8px, scale 1.03)
  - Implemented smoother scroll behavior (1200ms)
  - Established consistent spacing and colors
