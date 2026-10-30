/* ==========================================================================
   WAIKIKI — SHARED INTERACTION & MOTION ENGINE
   Loaded on every page. Page-specific scripts (economy.js, gallery.js, …)
   run independently on top of this file.

   Modules:
     theme        Night-mode toggle (persisted in localStorage)
     style        Site style switcher and override linker (persisted in localStorage)
     curtain      Page enter/leave transition
     header       Scrolled / hidden / on-hero header states
     menu         Full-screen overlay menu + live capital clock
     reveal       Scroll-triggered reveal + word-split headlines
     counters     Count-up animation for statistics
     parallax     Hero parallax and [data-parallax] layers
     pointer      Card spotlight and magnetic buttons
     rail         Auto-generated section navigation rail
     progress     Scroll progress bar + back-to-top ring
     timeline     Scroll-drawn timeline line
     faq          Smooth accordion expansion and collapse
     filter       Filter chips for landmark and hotel grids
   ========================================================================== */

(function () {
    'use strict';

    const root = document.documentElement;
    const DARK_STORAGE_KEY = 'isDarkMode';
    const DARK_CLASS = 'body-dark';
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    /* utils */
    const $ = (selector, scope = document) => scope.querySelector(selector);
    const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

    /** Run a callback at most once per animation frame. */
    function rafThrottle(callback) {
        let queued = false;
        return (...args) => {
            if (queued) return;
            queued = true;
            requestAnimationFrame(() => {
                queued = false;
                callback(...args);
            });
        };
    }

    /* theme */
    function isDark() {
        return root.classList.contains(DARK_CLASS);
    }

    function applyTheme(dark) {
        root.classList.toggle(DARK_CLASS, dark);
        document.body.classList.remove(DARK_CLASS, 'body-light');
        try {
            localStorage.setItem(DARK_STORAGE_KEY, String(dark));
        } catch (e) { /* storage unavailable */ }
        $$('[data-theme-toggle]').forEach((button) => {
            button.setAttribute('aria-pressed', String(dark));
            if (button.classList.contains('menu-chip')) {
                button.classList.toggle('is-active', dark);
            }
        });
        const meta = $('meta[name="theme-color"]');
        if (meta) {
            const bg = getComputedStyle(root).getPropertyValue('--bg').trim();
            if (bg) meta.setAttribute('content', bg);
        }
        document.dispatchEvent(new CustomEvent('themechange', { detail: { dark } }));
    }

    /* Global for backwards compatibility with inline onclick handlers. */
    window.setTheme = function () {
        applyTheme(!isDark());
    };

    function initTheme() {
        let stored = null;
        try {
            stored = localStorage.getItem(DARK_STORAGE_KEY);
        } catch (e) { /* storage unavailable */ }
        applyTheme(stored === 'true');
        $$('[data-theme-toggle]').forEach((button) => {
            button.addEventListener('click', () => {
                root.classList.add('theme-transition');
                window.setTheme();
            });
        });
    }

    /* style */
    const STYLE_STORAGE_KEY = 'waikikiSiteStyle';
    const STYLE_LINK_ID = 'waikiki-style-override';
    const STYLES = [
        {
            id: 'default',
            name: { en: 'Classic', hu: 'Klasszikus' },
            desc: { en: 'Tropical Luxe · Ivory and Navy', hu: 'Tr\u00f3pusi luxus \u00b7 Elef\u00e1ntcsont \u00e9s tengerk\u00e9k' },
            colors: ['#003366', '#c28a29', '#fbf7f0']
        },
        {
            id: 'amazonia',
            name: { en: 'Amazonia', hu: 'Amaz\u00f3nia' },
            desc: { en: 'Rainforest · Emerald and Jade', hu: 'Es\u0151erd\u0151 \u00b7 Smaragd \u00e9s j\u00e1de' },
            file: 'themes/style-amazonia.css',
            colors: ['#185a3e', '#c4933f', '#f1f7f2']
        },
        {
            id: 'oceanic',
            name: { en: 'Oceanic', hu: '\u00d3ce\u00e1n' },
            desc: { en: 'Caribbean · Azure and Coral', hu: 'Karib-tenger \u00b7 Az\u00far \u00e9s korall' },
            file: 'themes/style-oceanic.css',
            colors: ['#09527a', '#e05a47', '#eff6fa']
        },
        {
            id: 'royal',
            name: { en: 'Royal', hu: 'Kir\u00e1lyi' },
            desc: { en: 'Dynasty · Velvet and Crown Gold', hu: 'Dinasztia \u00b7 B\u00e1rsony \u00e9s arany' },
            file: 'themes/style-royal.css',
            colors: ['#6e1b34', '#c99738', '#fbf4f2']
        },
        {
            id: 'sunset',
            name: { en: 'Sunset', hu: 'Naplemente' },
            desc: { en: 'Caribbean Dusk · Terracotta and Amber', hu: 'Karibi alkony \u00b7 Terrakotta \u00e9s borosty\u00e1n' },
            file: 'themes/style-sunset.css',
            colors: ['#a34426', '#d97706', '#fcf4ed']
        },
        {
            id: 'slate',
            name: { en: 'Slate', hu: 'Tit\u00e1n' },
            desc: { en: 'High-Tech · Titanium and Cobalt', hu: 'Cs\u00facstechnika \u00b7 Tit\u00e1n \u00e9s kobalt' },
            file: 'themes/style-slate.css',
            colors: ['#1e293b', '#06b6d4', '#f1f5f9']
        }
    ];

    const PALETTE_ICON = '<svg class="style-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.563-2.512 5.563-5.563C22 6.5 17.5 2 12 2z"/><circle cx="12" cy="7" r="1.5" fill="currentColor"/><circle cx="7.5" cy="11.5" r="1.5" fill="currentColor"/><circle cx="16.5" cy="11.5" r="1.5" fill="currentColor"/><circle cx="10" cy="16.5" r="1.5" fill="currentColor"/></svg>';

    function getLocale() {
        return (document.documentElement.lang || 'en').toLowerCase().startsWith('hu') ? 'hu' : 'en';
    }

    function getCssBasePath() {
        const commonLink = $('link[rel="stylesheet"][href*="common.css"]');
        if (commonLink) {
            const href = commonLink.getAttribute('href');
            return href.substring(0, href.lastIndexOf('/') + 1);
        }
        const commonScript = $('script[src*="common.js"]');
        if (commonScript) {
            const src = commonScript.getAttribute('src');
            const scriptBase = src.substring(0, src.lastIndexOf('/') + 1);
            return scriptBase.replace(/js\/$/, 'css/');
        }
        return '../css/';
    }

    function getActiveStyle() {
        return root.getAttribute('data-site-style') || 'default';
    }

    function applyStyle(styleId, animate = false) {
        const target = STYLES.some((s) => s.id === styleId) ? styleId : 'default';
        const styleDef = STYLES.find((s) => s.id === target);

        if (animate) {
            root.classList.add('theme-transition');
        }

        let link = document.getElementById(STYLE_LINK_ID);

        if (target === 'default') {
            if (link) link.remove();
            root.removeAttribute('data-site-style');
        } else {
            const basePath = getCssBasePath();
            const targetHref = basePath + styleDef.file;
            if (!link) {
                link = document.createElement('link');
                link.id = STYLE_LINK_ID;
                link.rel = 'stylesheet';
                document.head.appendChild(link);
            }
            if (link.getAttribute('href') !== targetHref) {
                link.href = targetHref;
            }
            root.setAttribute('data-site-style', target);
        }

        try {
            localStorage.setItem(STYLE_STORAGE_KEY, target);
        } catch (e) { /* storage unavailable */ }

        const meta = $('meta[name="theme-color"]');
        if (meta) {
            requestAnimationFrame(() => {
                const bg = getComputedStyle(root).getPropertyValue('--bg').trim();
                if (bg) meta.setAttribute('content', bg);
            });
        }

        updateStyleSwitcherUI(target);
        document.dispatchEvent(new CustomEvent('stylechange', { detail: { style: target } }));
    }

    window.setStyle = function (styleId) {
        applyStyle(styleId, true);
    };

    window.getStyle = getActiveStyle;

    function updateStyleSwitcherUI(activeId) {
        const loc = getLocale();
        const activeDef = STYLES.find((s) => s.id === activeId) || STYLES[0];

        const toggleBtn = $('#style-toggle');
        if (toggleBtn) {
            toggleBtn.setAttribute('title', `${loc === 'hu' ? 'St\u00edlus' : 'Style'}: ${activeDef.name[loc]}`);
            toggleBtn.classList.toggle('has-custom-style', activeId !== 'default');
        }

        $$('[data-style-select]').forEach((button) => {
            const sid = button.getAttribute('data-style-select');
            const isActive = sid === activeId;
            button.classList.toggle('is-active', isActive);
            button.setAttribute('aria-pressed', String(isActive));
        });
    }

    function initStyle() {
        let stored = null;
        try {
            stored = localStorage.getItem(STYLE_STORAGE_KEY);
        } catch (e) { /* storage unavailable */ }
        applyStyle(stored || 'default', false);
    }

    function injectStyleSwitcherStyles() {
        if ($('#waikiki-style-switcher-css')) return;
        const style = document.createElement('style');
        style.id = 'waikiki-style-switcher-css';
        style.textContent = `
            .style-toggle {
                position: relative;
            }
            .style-toggle svg {
                width: 20px;
                height: 20px;
                transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            }
            .style-toggle:hover svg {
                transform: rotate(20deg) scale(1.1);
            }
            .style-toggle.is-active svg,
            .style-toggle.has-custom-style svg {
                color: var(--accent);
            }
            .style-popover {
                position: fixed;
                top: calc(var(--header-h-compact) + 10px);
                right: var(--gutter);
                z-index: calc(var(--z-header) + 20);
                width: min(340px, calc(100vw - 2rem));
                background: var(--surface);
                border: var(--border-width) solid var(--line-strong);
                border-radius: var(--radius);
                box-shadow: var(--shadow-xl);
                backdrop-filter: blur(var(--blur-lg));
                -webkit-backdrop-filter: blur(var(--blur-lg));
                padding: 1.15rem;
                opacity: 0;
                visibility: hidden;
                transform: translateY(-8px) scale(0.96);
                transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1), transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.25s;
                pointer-events: none;
            }
            .style-popover.is-open {
                opacity: 1;
                visibility: visible;
                transform: translateY(0) scale(1);
                pointer-events: auto;
            }
            .style-popover-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 0.85rem;
                padding-bottom: 0.65rem;
                border-bottom: 1px solid var(--line);
            }
            .style-popover-title {
                font-family: var(--font-display);
                font-size: 1.12rem;
                font-weight: 600;
                color: var(--heading);
                margin: 0;
                line-height: 1.2;
            }
            .style-popover-subtitle {
                font-size: 0.74rem;
                color: var(--muted);
                margin: 0.15rem 0 0 0;
            }
            .style-popover-close {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                background: var(--surface-2);
                color: var(--text);
                border: none;
                cursor: pointer;
                font-size: 1.1rem;
                line-height: 1;
                transition: background 0.2s, color 0.2s, transform 0.2s;
            }
            .style-popover-close:hover {
                background: var(--accent);
                color: #ffffff;
                transform: scale(1.08);
            }
            .style-options-grid {
                display: flex;
                flex-direction: column;
                gap: 0.45rem;
                max-height: 380px;
                overscroll-behavior: contain;
                padding-right: 2px;
            }
            .style-option-btn {
                display: flex;
                align-items: center;
                gap: 0.85rem;
                padding: 0.65rem 0.85rem;
                border-radius: var(--radius-sm);
                background: var(--surface-2);
                border: 1px solid transparent;
                color: var(--heading);
                cursor: pointer;
                text-align: left;
                width: 100%;
                font-family: var(--font-sans);
                transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), background 0.2s, border-color 0.2s, box-shadow 0.2s;
            }
            .style-option-btn:hover {
                background: var(--surface);
                border-color: var(--line-strong);
                transform: translateX(3px);
            }
            .style-option-btn.is-active {
                background: var(--surface);
                border-color: var(--primary);
                box-shadow: 0 0 0 2px var(--primary-subtle);
            }
            .style-swatch {
                display: flex;
                align-items: center;
                gap: 3px;
                padding: 3px 5px;
                background: rgba(0, 0, 0, 0.05);
                border-radius: 20px;
                flex-shrink: 0;
            }
            .body-dark .style-swatch {
                background: rgba(255, 255, 255, 0.1);
            }
            .style-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                border: 1px solid rgba(0, 0, 0, 0.15);
                flex-shrink: 0;
            }
            .style-option-info {
                flex: 1;
                min-width: 0;
            }
            .style-option-name {
                display: block;
                font-size: 0.86rem;
                font-weight: 700;
                color: var(--heading);
                line-height: 1.2;
            }
            .style-option-desc {
                display: block;
                font-size: 0.71rem;
                color: var(--muted);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                line-height: 1.3;
                margin-top: 1px;
            }
            .style-option-check {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 18px;
                height: 18px;
                border-radius: 50%;
                background: var(--primary);
                color: #ffffff;
                font-size: 0.68rem;
                opacity: 0;
                transform: scale(0.5);
                transition: opacity 0.2s, transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
                flex-shrink: 0;
            }
            .style-option-btn.is-active .style-option-check {
                opacity: 1;
                transform: scale(1);
            }
        `;
        document.head.appendChild(style);
    }

    function initStyleUI() {
        injectStyleSwitcherStyles();
        const loc = getLocale();

        // 1. Header action button
        const headerActions = $('.header-actions');
        let styleBtn = $('#style-toggle');
        if (headerActions && !styleBtn) {
            styleBtn = document.createElement('button');
            styleBtn.className = 'icon-btn style-toggle';
            styleBtn.id = 'style-toggle';
            styleBtn.type = 'button';
            styleBtn.setAttribute('aria-haspopup', 'dialog');
            styleBtn.setAttribute('aria-expanded', 'false');
            styleBtn.setAttribute('aria-label', loc === 'hu' ? 'St\u00edlus v\u00e1laszt\u00e1sa' : 'Choose site style');
            styleBtn.innerHTML = PALETTE_ICON;

            const menuToggle = $('#menu-toggle', headerActions);
            if (menuToggle) {
                headerActions.insertBefore(styleBtn, menuToggle);
            } else {
                headerActions.appendChild(styleBtn);
            }
        }

        // 2. Popover dialog
        let popover = $('#style-popover');
        if (!popover) {
            popover = document.createElement('div');
            popover.className = 'style-popover';
            popover.id = 'style-popover';
            popover.setAttribute('role', 'dialog');
            popover.setAttribute('aria-label', loc === 'hu' ? 'St\u00edlus v\u00e1laszt\u00f3' : 'Style switcher');

            const optionsHtml = STYLES.map((s) => {
                const dots = s.colors.map((c) => `<span class="style-dot" style="background:${c}"></span>`).join('');
                return `
                    <button class="style-option-btn" type="button" data-style-select="${s.id}" aria-pressed="false">
                        <span class="style-swatch">${dots}</span>
                        <span class="style-option-info">
                            <span class="style-option-name">${s.name[loc]}</span>
                            <span class="style-option-desc">${s.desc[loc]}</span>
                        </span>
                        <span class="style-option-check" aria-hidden="true">\u2713</span>
                    </button>
                `;
            }).join('');

            popover.innerHTML = `
                <div class="style-popover-header">
                    <div>
                        <h2 class="style-popover-title">${loc === 'hu' ? 'St\u00edlus' : 'Site Style'}</h2>
                        <p class="style-popover-subtitle">${loc === 'hu' ? 'Alkalmazkodik az eg\u00e9sz oldalhoz' : 'Adapts the whole nation'}</p>
                    </div>
                    <button class="style-popover-close" id="style-popover-close" type="button" aria-label="${loc === 'hu' ? 'Bez\u00e1r\u00e1s' : 'Close'}">\u00d7</button>
                </div>
                <div class="style-options-grid">
                    ${optionsHtml}
                </div>
            `;
            document.body.appendChild(popover);

            popover.querySelectorAll('[data-style-select]').forEach((button) => {
                button.addEventListener('click', () => {
                    const sid = button.getAttribute('data-style-select');
                    applyStyle(sid, true);
                    setTimeout(() => {
                        popover.classList.remove('is-open');
                        if (styleBtn) {
                            styleBtn.setAttribute('aria-expanded', 'false');
                            styleBtn.classList.remove('is-active');
                        }
                    }, 220);
                });
            });

            const closeBtn = $('#style-popover-close', popover);
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    popover.classList.remove('is-open');
                    if (styleBtn) {
                        styleBtn.setAttribute('aria-expanded', 'false');
                        styleBtn.classList.remove('is-active');
                        styleBtn.focus();
                    }
                });
            }
        }

        if (styleBtn && !styleBtn._hasStyleListener) {
            styleBtn._hasStyleListener = true;
            styleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const isOpen = popover.classList.toggle('is-open');
                styleBtn.setAttribute('aria-expanded', String(isOpen));
                styleBtn.classList.toggle('is-active', isOpen);
            });
        }

        if (!document._hasStyleGlobalListeners) {
            document._hasStyleGlobalListeners = true;
            document.addEventListener('click', (e) => {
                const pop = $('#style-popover');
                const btn = $('#style-toggle');
                if (pop && pop.classList.contains('is-open')) {
                    if (!pop.contains(e.target) && (!btn || !btn.contains(e.target))) {
                        pop.classList.remove('is-open');
                        if (btn) {
                            btn.setAttribute('aria-expanded', 'false');
                            btn.classList.remove('is-active');
                        }
                    }
                }
            });

            document.addEventListener('keydown', (e) => {
                const pop = $('#style-popover');
                const btn = $('#style-toggle');
                if (e.key === 'Escape' && pop && pop.classList.contains('is-open')) {
                    pop.classList.remove('is-open');
                    if (btn) {
                        btn.setAttribute('aria-expanded', 'false');
                        btn.classList.remove('is-active');
                        btn.focus();
                    }
                }
            });
        }

        updateStyleSwitcherUI(getActiveStyle());
    }

    // Early link injection before DOM ready
    initStyle();

    /* animate */
    const ANIMATION_STORAGE_KEY = 'isAnimationDisabled';

    function isAnimate() {
        return !root.classList.contains('no-reveal');
    }

    function applyAnimate(enabled) {
        root.classList.toggle('no-reveal', !enabled);
        try {
            localStorage.setItem(ANIMATION_STORAGE_KEY, String(!enabled));
        } catch (e) { /* storage unavailable */ }

        $$('[data-animate-toggle]').forEach((button) => {
            button.setAttribute('aria-pressed', String(enabled));
            button.classList.toggle('is-disabled', !enabled);
            if (button.classList.contains('menu-chip')) {
                button.classList.toggle('is-active', enabled);
            }
        });

        if (!enabled) {
            $$('[data-reveal]').forEach((element) => {
                element.classList.add('is-in');
            });
            $$('.split-word > span').forEach((span) => {
                span.style.transform = 'none';
                span.style.opacity = '1';
            });
        } else if ('IntersectionObserver' in window && !prefersReducedMotion && window._revealObserver) {
            $$('[data-reveal]').forEach((element) => {
                const rect = element.getBoundingClientRect();
                if (rect.top > window.innerHeight) {
                    element.classList.remove('is-in');
                    window._revealObserver.observe(element);
                }
            });
        }

        document.dispatchEvent(new CustomEvent('animatechange', { detail: { enabled } }));
    }

    window.toggleAnimate = function () {
        applyAnimate(!isAnimate());
    };

    function initAnimate() {
        let disabled = false;
        try {
            disabled = localStorage.getItem(ANIMATION_STORAGE_KEY) === 'true';
        } catch (e) { /* storage unavailable */ }
        applyAnimate(!disabled);
        $$('[data-animate-toggle]').forEach((button) => {
            button.addEventListener('click', () => {
                window.toggleAnimate();
            });
        });
    }

    /* curtain */
    function initCurtain() {
        // Restore pages served from the back/forward cache.
        window.addEventListener('pageshow', (event) => {
            if (event.persisted) root.classList.remove('is-leaving');
        });

        if (prefersReducedMotion || !isAnimate()) return;

        document.addEventListener('click', (event) => {
            const link = event.target.closest('a[href]');
            if (!link || event.defaultPrevented) return;
            if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
            if (link.target && link.target !== '_self') return;
            if (link.hasAttribute('download')) return;

            const url = new URL(link.href, window.location.href);
            if (url.origin !== window.location.origin) return;
            if (url.pathname === window.location.pathname && url.hash) return;
            if (!/\.html?$|\/$/.test(url.pathname)) return;

            event.preventDefault();
            root.classList.add('is-leaving');
            window.setTimeout(() => { window.location.href = url.href; }, 520);
        });
    }

    /* header */
    function initHeader() {
        const header = $('.site-header');
        if (!header) return;

        const hero = $('main > .hero:not(.hero--compact), main > .min-h-screen:first-child');
        let lastY = window.scrollY;

        const update = () => {
            const y = window.scrollY;
            const heroBottom = hero ? hero.offsetHeight - header.offsetHeight : 0;
            const scrolled = y > 24;
            const goingDown = y > lastY + 4;
            const goingUp = y < lastY - 4;

            header.classList.toggle('is-scrolled', scrolled);
            header.classList.toggle('on-hero', Boolean(hero) && y < heroBottom - 40 && !scrolled);

            if (!root.classList.contains('menu-open')) {
                if (goingDown && y > 320) {
                    header.classList.add('is-hidden');
                    root.classList.add('header-hidden');
                } else if (goingUp || y < 320) {
                    header.classList.remove('is-hidden');
                    root.classList.remove('header-hidden');
                }
            }
            lastY = y;
        };

        update();
        window.addEventListener('scroll', rafThrottle(update), { passive: true });
    }

    /* menu */
    function initMenu() {
        const toggle = $('#menu-toggle');
        const menu = $('#site-menu');
        const header = $('.site-header');
        if (!toggle || !menu) return;

        $$('.menu-group, .menu-aside', menu).forEach((element, index) => element.style.setProperty('--i', index));

        const setOrigin = () => {
            const rect = toggle.getBoundingClientRect();
            menu.style.setProperty('--cx', `${rect.left + rect.width / 2}px`);
            menu.style.setProperty('--cy', `${rect.top + rect.height / 2}px`);
        };

        const updateMenuScroll = () => {
            const isScrolled = menu.scrollTop > 8;
            root.classList.toggle('menu-scrolled', isScrolled);
            if (header) header.classList.toggle('menu-scrolled', isScrolled);
        };
        menu.addEventListener('scroll', rafThrottle(updateMenuScroll), { passive: true });

        const open = () => {
            setOrigin();
            root.classList.add('menu-open');
            updateMenuScroll();
            toggle.setAttribute('aria-expanded', 'true');
            menu.setAttribute('aria-hidden', 'false');
            menu.removeAttribute('inert');
            const firstLink = $('a', menu);
            if (firstLink) window.setTimeout(() => firstLink.focus({ preventScroll: true }), 450);
        };

        const close = () => {
            root.classList.remove('menu-open');
            root.classList.remove('menu-scrolled');
            if (header) header.classList.remove('menu-scrolled');
            toggle.setAttribute('aria-expanded', 'false');
            menu.setAttribute('aria-hidden', 'true');
            menu.setAttribute('inert', '');
            menu.scrollTop = 0;
        };

        toggle.addEventListener('click', () => (root.classList.contains('menu-open') ? close() : open()));
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && root.classList.contains('menu-open')) {
                close();
                toggle.focus();
            }
        });
        menu.addEventListener('click', (event) => {
            if (event.target.closest('a[href^="#"]')) close();
        });

        // Live clock and capital weather for Nova Aurelia (America/Havana).
        const clock = $('[data-capital-clock]', menu);
        const weatherEl = $('[data-capital-weather]', menu);
        if (clock) {
            const isHu = root.lang === 'hu';
            const format = new Intl.DateTimeFormat(isHu ? 'hu-HU' : 'en-GB', {
                hour: '2-digit',
                minute: '2-digit',
                timeZone: 'America/Havana'
            });
            const hourFormat = new Intl.DateTimeFormat('en-US', {
                hour: 'numeric',
                hour12: false,
                timeZone: 'America/Havana'
            });

            const updateClockAndWeather = () => {
                const now = new Date();
                clock.textContent = format.format(now);
                if (weatherEl) {
                    const localHour = parseInt(hourFormat.format(now), 10);
                    const isNight = localHour >= 20 || localHour < 6;
                    const icon = isNight ? '🌙' : '☀️';
                    const temp = isNight ? '24°C' : '28°C';
                    const desc = isNight ? (isHu ? 'Tiszta éjszaka' : 'Clear night') : (isHu ? 'Napos' : 'Sunny');
                    weatherEl.innerHTML = `<span class="weather-icon" aria-hidden="true">${icon}</span> <span class="weather-temp">${temp}</span> <span class="weather-desc">${desc}</span>`;
                }
            };
            updateClockAndWeather();
            window.setInterval(updateClockAndWeather, 15000);
        }
    }

    /* reveal */
    function splitWords(element) {
        if (element.dataset.split === 'done') return;
        let wordIndex = 0;

        const walk = (node) => {
            Array.from(node.childNodes).forEach((child) => {
                if (child.nodeType === Node.TEXT_NODE) {
                    const parts = child.textContent.split(/(\s+)/);
                    if (!child.textContent.trim()) return;
                    const fragment = document.createDocumentFragment();
                    parts.forEach((part) => {
                        if (!part) return;
                        if (/^\s+$/.test(part)) {
                            fragment.appendChild(document.createTextNode(' '));
                            return;
                        }
                        const outer = document.createElement('span');
                        outer.className = 'split-word';
                        const inner = document.createElement('span');
                        inner.textContent = part;
                        inner.style.setProperty('--w', wordIndex++);
                        outer.appendChild(inner);
                        fragment.appendChild(outer);
                    });
                    child.replaceWith(fragment);
                } else if (child.nodeType === Node.ELEMENT_NODE && child.tagName !== 'BR') {
                    walk(child);
                }
            });
        };

        walk(element);
        element.dataset.split = 'done';
    }

    const REVEAL_GROUPS = [
        // [selector, variant]
        ['.section-intro, .narrative-text, .narrative-content > h3, .narrative-content > ol, .narrative-section-title', ''],
        ['.card, .stat-card, .economy-stat, .faq-item, .reference-card, .admin-card, .stat-box, .content-block, .timeline-event, .timeline-period, .timeline-item, .data-viz-container, .data-viz-container-half, .info-stat, .member-card', ''],
        ['.table, .map-container, .video-wrapper, .comparison-item, .faq-section-title, .private-intro, .next-card, .section-link-wrapper, .faq-cta', ''],
        ['.gallery-item, .sight-image', 'image'],
        ['[data-reveal]', null]
    ];

    const REVEAL_THRESHOLD = 0.1;
    const REVEAL_ROOT_MARGIN = '0px 0px -5% 0px';

    function initReveal() {
        const targets = new Set();

        REVEAL_GROUPS.forEach(([selector, variant]) => {
            $$(selector).forEach((element) => {
                if (element.closest('.hero, .site-menu, .site-header, .site-footer, .lightbox, #root')) return;
                if (variant !== null && !element.hasAttribute('data-reveal')) element.setAttribute('data-reveal', variant);
                targets.add(element);
            });
        });

        // Section headings reveal word-by-word.
        $$('.section-title, .display, [data-split]').forEach((heading) => {
            if (heading.closest('.hero')) return;
            splitWords(heading);
            heading.setAttribute('data-reveal', 'split');
            targets.add(heading);
        });

        // Stagger siblings that share a parent.
        const counters = new Map();
        targets.forEach((element) => {
            if (element.style.getPropertyValue('--i')) return;
            const parent = element.parentElement;
            const index = counters.get(parent) || 0;
            element.style.setProperty('--i', Math.min(index, 8));
            counters.set(parent, index + 1);
        });

        if (prefersReducedMotion || !isAnimate() || !('IntersectionObserver' in window)) {
            targets.forEach((element) => element.classList.add('is-in'));
        } else {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    entry.target.classList.add('is-in');
                    observer.unobserve(entry.target);
                });
            }, { threshold: REVEAL_THRESHOLD, rootMargin: REVEAL_ROOT_MARGIN });
            window._revealObserver = observer;
            targets.forEach((element) => observer.observe(element));
        }

        // Legacy `.fade-in` hooks used by older page scripts.
        $$('.fade-in').forEach((element) => element.classList.add('visible'));

        // Hero headline plays immediately after the curtain lifts.
        const heroTitle = $('.hero .hero-title');
        if (heroTitle) {
            splitWords(heroTitle);
            heroTitle.style.setProperty('--base-delay', prefersReducedMotion ? '0ms' : '650ms');
            requestAnimationFrame(() => requestAnimationFrame(() => heroTitle.classList.add('is-in')));
        }

        root.classList.add('reveal-ready');
    }

    /* counters */
    /** Parse "$41.8T", "8,8M km²", "<1%" into prefix / number / suffix. */
    function parseStat(text) {
        const match = text.match(/^(\D*?)(\d+(?:[.,]\d+)*)(.*)$/s);
        if (!match) return null;
        const [, prefix, raw, suffix] = match;
        const thousands = /^\d{1,3}([.,]\d{3})+$/.test(raw) && !/^\d+[.,]\d{1,2}$/.test(raw);
        let decimals = 0;
        let separator = '.';
        let value;
        if (thousands) {
            value = parseFloat(raw.replace(/[.,]/g, ''));
        } else {
            const decimalMatch = raw.match(/[.,](\d+)$/);
            if (decimalMatch) {
                decimals = decimalMatch[1].length;
                separator = raw.includes(',') ? ',' : '.';
            }
            value = parseFloat(raw.replace(',', '.'));
        }
        if (Number.isNaN(value)) return null;
        return { prefix, suffix, value, decimals, separator, thousands, raw };
    }

    function formatStat(stat, current) {
        let number;
        if (stat.thousands) {
            number = Math.round(current).toLocaleString('en-US').replace(/,/g, stat.raw.includes('.') ? '.' : ',');
        } else {
            number = current.toFixed(stat.decimals).replace('.', stat.separator);
        }
        return `${stat.prefix}${number}${stat.suffix}`;
    }

    function initCounters() {
        const elements = $$('.stat-number, .economy-number, .stat-big, .stat-value, [data-count]');
        if (!elements.length) return;

        const animate = (element) => {
            const original = element.dataset.countText || element.textContent.trim();
            element.dataset.countText = original;
            const stat = parseStat(original);
            if (!stat || prefersReducedMotion) return;
            if (/^\d{4}$/.test(stat.raw) && !stat.prefix) return; // leave years alone

            const duration = 1800 + Math.min(stat.value, 400) * 2;
            const start = performance.now();
            const step = (now) => {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 4);
                element.textContent = formatStat(stat, stat.value * eased);
                if (progress < 1) requestAnimationFrame(step);
                else element.textContent = original;
            };
            requestAnimationFrame(step);
        };

        if (!('IntersectionObserver' in window)) return;
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                const inHero = entry.target.closest('.hero');
                window.setTimeout(() => animate(entry.target), inHero ? 1300 : 150);
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.4 });
        elements.forEach((element) => observer.observe(element));
    }

    /* parallax */
    function initParallax() {
        if (prefersReducedMotion) return;
        const heroMedia = $('.hero .hero-media');
        const layers = $$('[data-parallax]');
        if (!heroMedia && !layers.length) return;

        const update = () => {
            const y = window.scrollY;
            const vh = window.innerHeight;
            if (heroMedia && y < vh * 1.2) {
                heroMedia.style.setProperty('--hero-shift', `${y * 0.28}px`);
            }
            layers.forEach((layer) => {
                const rect = layer.getBoundingClientRect();
                if (rect.bottom < -200 || rect.top > vh + 200) return;
                const speed = parseFloat(layer.dataset.parallax) || 0.15;
                const offset = (rect.top + rect.height / 2 - vh / 2) * -speed;
                layer.style.transform = `translate3d(0, ${offset.toFixed(1)}px, 0)`;
            });
        };

        update();
        window.addEventListener('scroll', rafThrottle(update), { passive: true });
        window.addEventListener('resize', rafThrottle(update));
    }

    /* pointer */
    function initPointerEffects() {
        if (!finePointer || prefersReducedMotion) return;

        // Spotlight that follows the cursor across cards.
        document.addEventListener('pointermove', rafThrottle((event) => {
            const card = event.target.closest && event.target.closest('.card, .stat-card, .tile, .province-card, .sanctuary-item, .charter-rule-card, .hover-card');
            if (!card) return;
            const rect = card.getBoundingClientRect();
            card.style.setProperty('--mx', `${event.clientX - rect.left}px`);
            card.style.setProperty('--my', `${event.clientY - rect.top}px`);
        }), { passive: true });
    }

    /* rail */
    function initSectionRail() {
        const sections = $$('main > section[id]').filter((section) => $('.section-title, h2, h3', section));
        if (sections.length < 3) return;

        const rail = document.createElement('nav');
        rail.className = 'section-rail';
        rail.setAttribute('aria-label', root.lang === 'hu' ? 'Fejezetek' : 'Sections');

        const links = sections.map((section) => {
            const heading = $('.section-title, h2, h3', section);
            const label = (section.dataset.label || heading.dataset.label || heading.textContent).replace(/\s+/g, ' ').trim();
            const link = document.createElement('a');
            link.href = `#${section.id}`;
            link.innerHTML = '<span class="rail-label"></span><span class="rail-dot"></span>';
            link.querySelector('.rail-label').textContent = label.length > 42 ? `${label.slice(0, 40)}…` : label;
            link.setAttribute('aria-label', label);
            rail.appendChild(link);
            return link;
        });
        document.body.appendChild(rail);

        const hero = $('main > .hero');
        const setActive = rafThrottle(() => {
            const marker = window.innerHeight * 0.35;
            let activeIndex = -1;
            sections.forEach((section, index) => {
                if (section.getBoundingClientRect().top <= marker) activeIndex = index;
            });
            links.forEach((link, index) => link.classList.toggle('is-active', index === activeIndex));
            const pastHero = hero ? hero.getBoundingClientRect().bottom < window.innerHeight * 0.5 : window.scrollY > 200;
            const footer = $('.site-footer');
            const beforeFooter = footer ? footer.getBoundingClientRect().top > window.innerHeight * 0.6 : true;
            rail.classList.toggle('is-visible', pastHero && beforeFooter);
        });

        setActive();
        window.addEventListener('scroll', setActive, { passive: true });
    }

    /* progress */
    function initProgress() {
        const bar = $('.scroll-progress');
        const toTop = $('.to-top');

        if (toTop) {
            toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' }));
        }

        const update = () => {
            const max = document.documentElement.scrollHeight - window.innerHeight;
            const progress = max > 0 ? Math.min(window.scrollY / max, 1) : 0;
            if (bar) bar.style.setProperty('--progress', progress.toFixed(4));
            if (toTop) {
                toTop.style.setProperty('--progress', progress.toFixed(4));
                toTop.classList.toggle('is-visible', window.scrollY > 700);
            }
        };

        update();
        window.addEventListener('scroll', rafThrottle(update), { passive: true });
        window.addEventListener('resize', rafThrottle(update));
    }

    /* timeline */
    function initTimelines() {
        const timelines = $$('.timeline, .timeline-container, .timeline-expanded');
        if (!timelines.length) return;

        const update = () => {
            const vh = window.innerHeight;
            timelines.forEach((timeline) => {
                const rect = timeline.getBoundingClientRect();
                const progress = Math.min(Math.max((vh * 0.65 - rect.top) / rect.height, 0), 1);
                timeline.style.setProperty('--line-progress', progress.toFixed(4));
            });
        };

        update();
        window.addEventListener('scroll', rafThrottle(update), { passive: true });
    }

    /* marquee */
    function initMarquees() {
        $$('.marquee-track').forEach((track) => {
            if (track.dataset.cloned) return;
            Array.from(track.children).forEach((item) => {
                const clone = item.cloneNode(true);
                clone.setAttribute('aria-hidden', 'true');
                track.appendChild(clone);
            });
            track.dataset.cloned = 'true';
        });
    }

    /* faq */
    function initFaqAccordion() {
        const items = $$('details.faq-item');
        if (!items.length) return;

        items.forEach((details) => {
            const summary = details.querySelector('.faq-question') || details.querySelector('summary');
            if (!summary) return;

            let animation = null;
            let isClosing = false;
            let isExpanding = false;

            summary.addEventListener('click', (e) => {
                if (prefersReducedMotion) return;
                e.preventDefault();

                if (isClosing || !details.open) {
                    open();
                } else if (isExpanding || details.open) {
                    close();
                }
            });

            function open() {
                if (animation) animation.cancel();
                isClosing = false;
                isExpanding = true;
                details.classList.remove('is-closing');

                const startHeight = details.getBoundingClientRect().height;
                details.open = true;
                const endHeight = details.getBoundingClientRect().height;
                details.style.height = `${startHeight}px`;

                animation = details.animate(
                    {
                        height: [`${startHeight}px`, `${endHeight}px`],
                    },
                    {
                        duration: 380,
                        easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
                    }
                );

                animation.onfinish = () => {
                    details.style.height = '';
                    animation = null;
                    isExpanding = false;
                };

                animation.oncancel = () => {
                    isExpanding = false;
                    details.style.height = '';
                };
            }

            function close() {
                if (animation) animation.cancel();
                isExpanding = false;
                isClosing = true;
                details.classList.add('is-closing');

                const startHeight = details.getBoundingClientRect().height;
                details.open = false;
                const endHeight = details.getBoundingClientRect().height;
                details.open = true;
                details.style.height = `${startHeight}px`;

                animation = details.animate(
                    {
                        height: [`${startHeight}px`, `${endHeight}px`],
                    },
                    {
                        duration: 320,
                        easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
                    }
                );

                animation.onfinish = () => {
                    details.open = false;
                    details.classList.remove('is-closing');
                    details.style.height = '';
                    animation = null;
                    isClosing = false;
                };

                animation.oncancel = () => {
                    isClosing = false;
                    details.classList.remove('is-closing');
                    details.style.height = '';
                };
            }
        });
    }

    /* filter */
    function initFilterBar(bar) {
        const grid = document.getElementById(bar.dataset.filterFor);
        if (!grid) return;
        const items = $$('[data-filter-item]', grid);
        const chips = $$('[data-filter]', bar);

        bar.addEventListener('click', (event) => {
            const chip = event.target.closest('[data-filter]');
            if (!chip || chip.getAttribute('aria-pressed') === 'true') return;
            const key = chip.dataset.filter;

            chips.forEach((other) => other.setAttribute('aria-pressed', String(other === chip)));

            items.forEach((item, index) => {
                const match = key === 'all' || (item.dataset.cat || '').split(/\s+/).includes(key);
                item.classList.remove('is-filtering-in');
                item.hidden = !match;
                if (match) {
                    // Filtered cards must be visible even if the scroll reveal has not fired yet.
                    item.classList.add('is-in');
                    item.style.animationDelay = `${Math.min(index, 8) * 45}ms`;
                    void item.offsetWidth; // restart the entrance animation
                    item.classList.add('is-filtering-in');
                }
            });
        });
    }

    window.initFilterBar = initFilterBar;

    function initFilterBars() {
        $$('.filter-bar[data-filter-for]').forEach(initFilterBar);
    }

    /* boot */
    function init() {
        initTheme();
        initStyleUI();
        initAnimate();
        initCurtain();
        initHeader();
        initMenu();
        initMarquees();
        initReveal();
        initCounters();
        initParallax();
        initPointerEffects();
        initSectionRail();
        initProgress();
        initTimelines();
        initFaqAccordion();
        initFilterBars();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
