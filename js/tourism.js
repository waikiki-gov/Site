/**
 * Tourism Page Specific JavaScript
 * Handles tourism page interactions and animations
 */

/**
 * Initialize tourism page specific features
 */
function initTourism() {
    initStatAnimations();
    initCardSequenceAnimation();
}

/**
 * Animate hero stats on page load
 */
function initStatAnimations() {
    const statItems = document.querySelectorAll('.hero-stats .stat-item');
    
    statItems.forEach((item, index) => {
        setTimeout(() => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            
            requestAnimationFrame(() => {
                item.style.transition = 'all 0.6s ease-out';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            });
        }, index * 100);
    });
}

/**
 * Add sequential fade-in animation to cards as they come into view
 */
function initCardSequenceAnimation() {
    const sections = document.querySelectorAll('section[id]');
    
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const cards = entry.target.querySelectorAll('.card');
                cards.forEach((card, index) => {
                    setTimeout(() => {
                        card.classList.add('fade-in-visible');
                    }, index * 100);
                });
                cardObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    });
    
    sections.forEach(section => {
        if (section.querySelector('.card-grid')) {
            cardObserver.observe(section);
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTourism);
} else {
    initTourism();
}
