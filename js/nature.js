/* Sovereign Nation of Waikiki — Nature and Sanctuaries Interactive Engine */
(() => {
    'use strict';

    function initProvinceFilter() {
        const filterBtns = Array.from(document.querySelectorAll('.province-btn'));
        const cards = Array.from(document.querySelectorAll('.sanctuary-item'));

        if (!filterBtns.length || !cards.length) return;

        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const prov = btn.getAttribute('data-prov-filter') || 'all';

                filterBtns.forEach(b => {
                    const active = b === btn;
                    b.classList.toggle('is-active', active);
                    b.setAttribute('aria-pressed', active ? 'true' : 'false');
                });

                let visibleIdx = 0;
                cards.forEach(card => {
                    const cardProv = card.getAttribute('data-prov');
                    const show = prov === 'all' || cardProv === prov;

                    if (show) {
                        card.style.display = 'flex';
                        card.style.opacity = '0';
                        card.style.transform = 'translateY(14px)';
                        const delay = visibleIdx * 45;
                        visibleIdx++;

                        window.setTimeout(() => {
                            requestAnimationFrame(() => {
                                card.style.transition = 'opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.35s cubic-bezier(0.16, 1, 0.3, 1)';
                                card.style.opacity = '1';
                                card.style.transform = 'translateY(0)';
                                window.setTimeout(() => {
                                    card.style.transition = '';
                                    card.style.transform = '';
                                    card.style.opacity = '';
                                }, 360);
                            });
                        }, delay);
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    }

    function initRealmHotspots() {
        const realmZones = Array.from(document.querySelectorAll('.nat-realm-zone'));
        const zoneBadges = Array.from(document.querySelectorAll('.nat-zone-badge'));
        const provinceCards = Array.from(document.querySelectorAll('.province-card'));

        const allHotspots = [...realmZones, ...zoneBadges];
        if (!allHotspots.length) return;

        function highlightRealm(realmName) {
            realmZones.forEach(zone => {
                const matches = zone.getAttribute('data-realm') === realmName;
                if (!realmName) {
                    zone.style.opacity = '1';
                    zone.style.filter = '';
                } else {
                    zone.style.opacity = matches ? '1' : '0.45';
                    zone.style.filter = matches ? 'drop-shadow(0 0 12px rgba(245, 196, 110, 0.65))' : '';
                }
            });

            provinceCards.forEach(card => {
                const matches = card.getAttribute('data-prov') === realmName;
                card.style.borderColor = matches ? 'var(--accent, #C28A29)' : '';
                if (matches) {
                    card.style.boxShadow = '0 12px 30px rgba(194, 138, 41, 0.2)';
                } else {
                    card.style.boxShadow = '';
                }
            });
        }

        allHotspots.forEach(node => {
            const realm = node.getAttribute('data-realm');
            if (!realm) return;

            node.addEventListener('mouseenter', () => highlightRealm(realm));
            node.addEventListener('mouseleave', () => highlightRealm(null));

            node.addEventListener('click', () => {
                highlightRealm(realm);
                const targetCard = document.querySelector(`.province-card[data-prov="${realm}"]`);
                if (targetCard) {
                    targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    targetCard.classList.add('is-focused');
                    window.setTimeout(() => targetCard.classList.remove('is-focused'), 2000);
                }
            });
        });
    }

    function initCardSpotlight() {
        const cards = Array.from(document.querySelectorAll('.card, .province-card, .sanctuary-item, .charter-rule-card'));
        if (!cards.length) return;

        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                card.style.setProperty('--mx', `${x}px`);
                card.style.setProperty('--my', `${y}px`);
                card.style.setProperty('--mouse-x', `${x}px`);
                card.style.setProperty('--mouse-y', `${y}px`);
            }, { passive: true });
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        initProvinceFilter();
        initRealmHotspots();
        initCardSpotlight();
    });
})();
