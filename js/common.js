/* Common JavaScript for all pages - Waikiki Government Site */

/**
 * Configuration constants
 */
const CONFIG = {
    NAVBAR_HEIGHT: 80,
    SCROLL_DURATION: 1200,
    ANIMATION_THRESHOLD: 0.15,
    OBSERVER_ROOT_MARGIN: '0px 0px -80px 0px'
};

/**
 * Smooth scroll functionality with custom easing
 * @param {HTMLElement} target - Target element to scroll to
 */
function smoothScrollTo(target) {
    if (!target) return;

    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition - CONFIG.NAVBAR_HEIGHT;
    let start = null;

    function animation(currentTime) {
        if (start === null) start = currentTime;
        const timeElapsed = currentTime - start;
        const progress = Math.min(timeElapsed / CONFIG.SCROLL_DURATION, 1);
        
        // Custom cubic easing function for natural acceleration and deceleration
        const ease = progress < 0.5
            ? 4 * progress * progress * progress
            : 1 - Math.pow(-2 * progress + 2, 3) / 2;
        
        window.scrollTo(0, startPosition + distance * ease);
        
        if (timeElapsed < CONFIG.SCROLL_DURATION) {
            requestAnimationFrame(animation);
        }
    }
    
    requestAnimationFrame(animation);
}

/**
 * Initialize smooth scrolling for all anchor links
 */
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const target = document.querySelector(targetId);
            smoothScrollTo(target);
        });
    });
}

/**
 * Create and initialize Intersection Observer for fade-in animations
 */
function initFadeInObserver() {
    const observerOptions = {
        threshold: CONFIG.ANIMATION_THRESHOLD,
        rootMargin: CONFIG.OBSERVER_ROOT_MARGIN
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                
                // Add staggered animation to children if they exist
                const children = entry.target.querySelectorAll('.card, .leader-card, .timeline-item');
                children.forEach((child, index) => {
                    setTimeout(() => {
                        child.style.opacity = '1';
                        child.style.transform = 'translateY(0)';
                    }, index * 100);
                });
            }
        });
    }, observerOptions);

    // Observe all fade-in elements
    document.querySelectorAll('.fade-in').forEach(element => {
        observer.observe(element);
    });
}

/**
 * Add active state to navigation links based on scroll position
 */
function initNavigationHighlight() {
    const sections = document.querySelectorAll('section[id]');
    
    function highlightNavigation() {
        const scrollY = window.pageYOffset;
        
        sections.forEach(section => {
            const sectionHeight = section.offsetHeight;
            const sectionTop = section.offsetTop - 100;
            const sectionId = section.getAttribute('id');
            
            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                document.querySelectorAll('.nav-links a').forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    window.addEventListener('scroll', highlightNavigation);
}

/**
 * Create scroll progress indicator at top of page
 */
function initScrollIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'scroll-indicator';
    indicator.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 4px;
        background: linear-gradient(90deg, #0071BC, #00B0C3);
        width: 0%;
        z-index: 10000;
        transition: width 0.1s ease;
    `;
    document.body.appendChild(indicator);
    
    window.addEventListener('scroll', () => {
        const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrollPercent = (scrollTop / scrollHeight) * 100;
        indicator.style.width = scrollPercent + '%';
    });
}

/**
 * Add hover effects to cards
 */
function initCardHoverEffects() {
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        });
    });
}

/**
 * Initialize hamburger menu functionality
 */
function initHamburgerMenu() {
    const hamburgerButton = document.querySelector('.hamburger-button');
    const hamburgerPanel = document.querySelector('.hamburger-panel');
    const hamburgerOverlay = document.querySelector('.hamburger-overlay');
    
    if (!hamburgerButton || !hamburgerPanel || !hamburgerOverlay) {
        return; // Elements not present on this page
    }
    
    function openMenu() {
        hamburgerButton.classList.add('active');
        hamburgerPanel.classList.add('active');
        hamburgerOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    function closeMenu() {
        hamburgerButton.classList.remove('active');
        hamburgerPanel.classList.remove('active');
        hamburgerOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    hamburgerButton.addEventListener('click', function(e) {
        e.stopPropagation();
        if (hamburgerPanel.classList.contains('active')) {
            closeMenu();
        } else {
            openMenu();
        }
    });
    
    hamburgerOverlay.addEventListener('click', closeMenu);
    
    // Close menu when clicking a link
    hamburgerPanel.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', closeMenu);
    });
    
    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && hamburgerPanel.classList.contains('active')) {
            closeMenu();
        }
    });
}

/**
 * Initialize all common functionality
 */
function initCommon() {
    initSmoothScrolling();
    initFadeInObserver();
    initNavigationHighlight();
    initScrollIndicator();
    initCardHoverEffects();
    initHamburgerMenu();
    
    console.log('Waikiki Official Website - Common Scripts Loaded');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCommon);
} else {
    initCommon();
}
