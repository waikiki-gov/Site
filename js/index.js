/* Index Page Specific JavaScript - Waikiki Government Site */

/**
 * Parallax effect for hero section
 */
function initHeroParallax() {
    let lastScrollTop = 0;
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const hero = document.querySelector('.hero');
        
        if (hero && scrollTop < hero.offsetHeight) {
            const heroContent = document.querySelector('.hero-content');
            if (heroContent) {
                heroContent.style.transform = `translateY(${scrollTop * 0.3}px)`;
                heroContent.style.opacity = `${1 - (scrollTop / hero.offsetHeight) * 0.5}`;
            }
        }
        
        lastScrollTop = scrollTop;
    });
}

/**
 * Animate numbers counting up
 * @param {HTMLElement} element - Element containing the number
 * @param {number} start - Starting value
 * @param {number} end - Ending value
 * @param {number} duration - Animation duration in ms
 */
function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = Math.floor(progress * (end - start) + start);
        element.textContent = current;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

/**
 * Initialize stat number counting animations
 */
function initStatsAnimation() {
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                entry.target.dataset.animated = 'true';
                const text = entry.target.textContent;
                const match = text.match(/(\d+)/);
                if (match) {
                    const number = parseInt(match[0]);
                    entry.target.textContent = '0';
                    setTimeout(() => {
                        animateValue(entry.target, 0, number, 1500);
                    }, 200);
                }
            }
        });
    }, { threshold: 0.5 });

    // Observe stat numbers (currently disabled as per original code pattern)
    // Uncomment if stat counting animation is desired
    // document.querySelectorAll('.stat-number, .economy-number').forEach(stat => {
    //     statsObserver.observe(stat);
    // });
}

/**
 * Initialize timeline items animation on scroll
 */
function initTimelineAnimation() {
    const timelineObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'scale(1)';
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('.timeline-item').forEach(item => {
        timelineObserver.observe(item);
    });
}

/**
 * Add ripple effect on stat item clicks
 */
function initRippleEffect() {
    document.querySelectorAll('.stat-item, .economy-stat').forEach(item => {
        item.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

/**
 * Animate section titles on view
 */
function initSectionTitleAnimation() {
    const titleObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'slideInFromLeft 0.8s ease-out';
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.section-title').forEach(title => {
        titleObserver.observe(title);
    });
}

/**
 * Initialize all index page specific functionality
 */
function initIndex() {
    initHeroParallax();
    initStatsAnimation();
    initTimelineAnimation();
    initRippleEffect();
    initSectionTitleAnimation();
    
    console.log('Waikiki Official Website - Index Page Loaded');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initIndex);
} else {
    initIndex();
}
