/**
 * Tourism Page Specific JavaScript
 * Handles tourism page interactions and animations
 */

/**
 * Initialize tourism page specific features
 */
function initTourism() {
    initStatAnimations();
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

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTourism);
} else {
    initTourism();
}
