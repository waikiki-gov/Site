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
  - H1 (Hero): `4rem` (64px) on desktop, `2.5rem` (40px) on mobile
  - H2 (Section Titles): `3rem` (48px) on desktop, `2.2rem` (35px) on mobile
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

### Standard Timing
- **Transition Duration**: `0.5s` (500ms) for all hover effects
- **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)` for smooth, professional feel
- **Entry Animation Duration**: `0.8s` (800ms) with staggered delays
- **Animation Delays**: Calculated using `calc(var(--base-animation-delay) + N * var(--animation-delay-increment))`

### Hover Effects - Unified
All interactive elements use consistent hover animations:
- **Transform**: `translateY(-8px) scale(1.03)`
- **No 3D transforms**: Avoid `rotate3d`, `rotateX`, `rotateY`
- **No aggressive scaling**: Maximum scale is `1.03`
- **Consistent shadow enhancement**: Increase shadow spread on hover
- **Duration**: Always use `var(--transition-duration)`

### Entry Animations
**Staggered Delays:**
- Uses CSS custom properties for calculated delays
- First item: `0.05s` (base delay)
- Increment: `0.08s` per item (0.05s, 0.13s, 0.21s, ...)
- Earlier appearance than previous implementation (reduced from 0.15s base)

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

## Best Practices

### DO:
- ✅ Use consistent spacing throughout
- ✅ Apply unified hover effects (translateY + scale)
- ✅ Use the defined color palette
- ✅ Use CSS custom properties for timing and spacing
- ✅ Maintain `var(--transition-duration)` for all transitions
- ✅ Use `var(--transition-easing)` for smooth animations
- ✅ Calculate animation delays using CSS custom properties
- ✅ Test animations on different devices
- ✅ Ensure accessibility (contrast ratios, focus states)
- ✅ Use solid colors or subtle opacity variations

### DON'T:
- ❌ Use color gradients (use solid colors with opacity instead)
- ❌ Use 3D rotations or transforms
- ❌ Mix different animation timings randomly
- ❌ Use harsh or sudden animations
- ❌ Scale elements beyond 1.03x (our standard hover scale)
- ❌ Use colors outside the defined palette
- ❌ Create inconsistent spacing
- ❌ Use excessive animations
- ❌ Hard-code timing values (use CSS variables instead)

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
- Debounce scroll events

## Browser Support

### Targets
- Chrome/Edge: Latest 2 versions
- Firefox: Latest
- Safari: Latest 2 versions
- Mobile browsers: Latest