/**
 * Photo Gallery for Raimondo & Selena
 * 
 * Loads images from a configured URL, renders a performant grid
 * with lazy loading / IntersectionObserver, and provides a lightbox detail view.
 * Designed for hundreds of images.
 */

const Gallery = (() => {
    'use strict';

    // ── State ──────────────────────────────────────────────
    let images = [];        // Array of image URL strings
    let currentIndex = -1;  // Lightbox index
    let isLargeGrid = false;

    // ── DOM refs (set in init) ─────────────────────────────
    let gridEl, countEl, lightbox, lbImg, lbCounter;

    // ── Lazy-load observer ────────────────────────────────
    let lazyObserver;

    // ── Public: initialise ────────────────────────────────
    function init(sourceUrl) {
        gridEl = document.getElementById('gallery-grid');
        countEl = document.getElementById('gallery-count');
        lightbox = document.getElementById('lightbox');
        lbImg = document.getElementById('lightbox-img');
        lbCounter = document.getElementById('lightbox-counter');

        if (!gridEl || !sourceUrl) return;

        setupLazyObserver();
        bindToolbar();
        bindLightbox();
        fetchImages(sourceUrl);
    }

    // ── Fetch image list ──────────────────────────────────
    async function fetchImages(url) {
        showLoading();
        try {
            const res = await fetch(url);
            if (!res.ok) throw new Error(res.statusText);
            const data = await res.json();

            // Accept an array of strings or objects with a .url / .src property
            images = (Array.isArray(data) ? data : data.images || data.photos || [])
                .map(item => (typeof item === 'string' ? item : item.url || item.src || ''))
                .filter(Boolean);

            if (images.length === 0) {
                showMessage('No Photos Found', 'The gallery source returned no images.');
                return;
            }

            updateCount();
            renderGrid();
        } catch (err) {
            showMessage('Could Not Load Gallery', 'Please check the image source URL and try again.');
        }
    }

    // ── Render grid (creates DOM once) ────────────────────
    function renderGrid() {
        gridEl.innerHTML = '';
        const fragment = document.createDocumentFragment();

        for (let i = 0; i < images.length; i++) {
            const thumb = document.createElement('div');
            thumb.className = 'gallery-thumb placeholder';
            thumb.dataset.index = i;

            const img = document.createElement('img');
            img.dataset.src = images[i]; // defer actual load
            img.alt = 'Photo ' + (i + 1);
            img.draggable = false;

            const overlay = document.createElement('div');
            overlay.className = 'thumb-overlay';
            overlay.innerHTML = '<span class="thumb-index">' + (i + 1) + '</span>';

            thumb.appendChild(img);
            thumb.appendChild(overlay);
            fragment.appendChild(thumb);

            // click → open lightbox
            thumb.addEventListener('click', () => openLightbox(i));
        }

        gridEl.appendChild(fragment);

        // Observe all thumbs for lazy loading
        gridEl.querySelectorAll('.gallery-thumb').forEach(el => lazyObserver.observe(el));
    }

    // ── Lazy loading via IntersectionObserver ──────────────
    function setupLazyObserver() {
        lazyObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                const thumb = entry.target;
                const img = thumb.querySelector('img');
                if (!img || img.src) return; // already loaded

                img.src = img.dataset.src;
                img.onload = () => {
                    thumb.classList.remove('placeholder');
                    thumb.classList.add('loaded');
                };
                img.onerror = () => {
                    thumb.classList.remove('placeholder');
                    thumb.classList.add('error');
                    img.remove();
                };

                lazyObserver.unobserve(thumb);
            });
        }, {
            rootMargin: '200px'  // start loading 200px before viewport
        });
    }

    // ── Toolbar controls ──────────────────────────────────
    function bindToolbar() {
        const btnSmall = document.getElementById('btn-grid-small');
        const btnLarge = document.getElementById('btn-grid-large');

        if (btnSmall) btnSmall.addEventListener('click', () => setGridSize(false));
        if (btnLarge) btnLarge.addEventListener('click', () => setGridSize(true));
    }

    function setGridSize(large) {
        isLargeGrid = large;
        gridEl.classList.toggle('large-grid', large);
        document.getElementById('btn-grid-small')?.classList.toggle('active', !large);
        document.getElementById('btn-grid-large')?.classList.toggle('active', large);
    }

    function updateCount() {
        if (countEl) countEl.textContent = images.length + ' photos';
    }

    // ── Lightbox ──────────────────────────────────────────
    function bindLightbox() {
        document.getElementById('lightbox-close')?.addEventListener('click', closeLightbox);
        document.getElementById('lightbox-prev')?.addEventListener('click', () => navigate(-1));
        document.getElementById('lightbox-next')?.addEventListener('click', () => navigate(1));

        // Overlay click closes
        lightbox?.addEventListener('click', (e) => {
            if (e.target === lightbox || e.target.classList.contains('lightbox-img-wrap')) closeLightbox();
        });

        // Keyboard
        document.addEventListener('keydown', handleKey);

        // Swipe support for touch devices
        let touchStartX = 0;
        lightbox?.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        lightbox?.addEventListener('touchend', (e) => {
            const diff = e.changedTouches[0].screenX - touchStartX;
            if (Math.abs(diff) > 60) navigate(diff < 0 ? 1 : -1);
        }, { passive: true });
    }

    function openLightbox(index) {
        currentIndex = index;
        showLightboxImage();
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
        currentIndex = -1;
    }

    function navigate(dir) {
        if (currentIndex < 0) return;
        currentIndex = (currentIndex + dir + images.length) % images.length;
        showLightboxImage();
    }

    function showLightboxImage() {
        if (!lbImg || currentIndex < 0) return;
        lbImg.classList.add('loading');
        lbImg.src = images[currentIndex];
        lbImg.onload = () => lbImg.classList.remove('loading');
        lbImg.onerror = () => lbImg.classList.remove('loading');
        if (lbCounter) lbCounter.textContent = (currentIndex + 1) + ' / ' + images.length;
    }

    function handleKey(e) {
        if (currentIndex < 0) return;
        switch (e.key) {
            case 'Escape': closeLightbox(); break;
            case 'ArrowLeft': navigate(-1); break;
            case 'ArrowRight': navigate(1); break;
        }
    }

    // ── UI helpers ────────────────────────────────────────
    function showLoading() {
        gridEl.innerHTML =
            '<div class="gallery-loading">' +
            '  <div class="gallery-spinner"></div>' +
            '  <p>Loading gallery images</p>' +
            '</div>';
    }

    function showMessage(title, text) {
        gridEl.innerHTML =
            '<div class="gallery-message">' +
            '  <h3>' + escapeHtml(title) + '</h3>' +
            '  <p>' + escapeHtml(text) + '</p>' +
            '</div>';
        if (countEl) countEl.textContent = '0 photos';
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    return { init };
})();
