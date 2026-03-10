/**
 * Photo Gallery for Raimondo & Selena
 *
 * SETUP — Google Drive as image source:
 * 1. Go to https://script.google.com and create a new project.
 * 2. Replace the default code with:
 *
 *    function doGet() {
 *      var folder = DriveApp.getFolderById('1d5EJCWrHyZEOSdJrg0m8CDIzsthv4DPQ');
 *      var files = folder.getFiles();
 *      var ids = [];
 *      while (files.hasNext()) {
 *        var f = files.next();
 *        if (f.getMimeType().indexOf('image/') === 0) ids.push(f.getId());
 *      }
 *      ids.sort();
 *      return ContentService.createTextOutput(JSON.stringify(ids))
 *        .setMimeType(ContentService.MimeType.JSON);
 *    }
 *
 * 3. Click Deploy > New deployment > Web app. Set "Execute as" = Me, "Who has access" = Anyone.
 * 4. Copy the deployment URL and paste it as GALLERY_SOURCE_URL below.
 *
 */

const Gallery = (() => {
    'use strict';

    // ── Configuration ─────────────────────────────────────
    // Paste your Google Apps Script web-app URL here (see SETUP above)
    const GALLERY_SOURCE_URL = 'https://script.google.com/macros/s/AKfycbwOmRU6MOZPwy7pKGUmNtz5ZJK0pV-muH7Uq6be_pbmyivmnzqgwLPiiIhFSR7CXYI/exec';

    // ── i18n ──────────────────────────────────────────────
    const STRINGS = {
        en: { photos: 'photos', loading: 'Loading gallery images', noTitle: 'No Photos Found', noText: 'The gallery source returned no images.', errTitle: 'Could Not Load Gallery', errText: 'Please check the image source URL and try again.', photo: 'Photo' },
        hu: { photos: 'fotó', loading: 'Képek betöltése', noTitle: 'Nem találhatók fotók', noText: 'A galéria forrása nem tartalmazott képeket.', errTitle: 'Nem sikerült betölteni a galériát', errText: 'Kérjük, ellenőrizze a képforrás URL-jét, és próbálja újra.', photo: 'Fotó' }
    };
    const lang = document.documentElement.lang === 'hu' ? 'hu' : 'en';
    const t = STRINGS[lang];

    // ── State ──────────────────────────────────────────────
    let images = [];        // { thumb: string, full: string } per image
    let currentIndex = -1;  // Lightbox index
    let isLargeGrid = false;

    // ── DOM refs (set in init) ─────────────────────────────
    let gridEl, countEl, lightbox, lbImg, lbCounter, lbSpinner;

    // ── Lazy-load observer ────────────────────────────────
    let lazyObserver;

    // ── Public: initialise ────────────────────────────────
    function init(sourceUrl) {
        gridEl = document.getElementById('gallery-grid');
        countEl = document.getElementById('gallery-count');
        lightbox = document.getElementById('lightbox');
        lbImg = document.getElementById('lightbox-img');
        lbCounter = document.getElementById('lightbox-counter');
        lbSpinner = document.getElementById('lightbox-spinner');

        if (!gridEl) return;

        setupLazyObserver();
        bindToolbar();
        bindLightbox();
        fetchImages(sourceUrl || GALLERY_SOURCE_URL);
    }

    // ── Resolve a single item to { thumb, full } ─────────
    function resolveImage(item) {
        const val = typeof item === 'string'
            ? item
            : item.url || item.src || item.id || '';
        if (!val) return null;
        if (val.startsWith('http')) return { thumb: val, full: val };
        // Treat as Google Drive file ID
        return {
            thumb: 'https://drive.google.com/thumbnail?id=' + encodeURIComponent(val) + '&sz=w400',
            full: 'https://drive.google.com/thumbnail?id=' + encodeURIComponent(val) + '&sz=w2000'
        };
    }

    // ── Fetch image list ──────────────────────────────────
    async function fetchImages(url) {
        if (!url) {
            showMessage(t.errTitle, t.errText);
            return;
        }
        showLoading();
        try {
            const res = await fetch(url);
            if (!res.ok) throw new Error(res.statusText);
            const data = await res.json();

            const raw = Array.isArray(data) ? data : data.images || data.photos || [];
            images = raw.map(resolveImage).filter(Boolean);

            if (images.length === 0) {
                showMessage(t.noTitle, t.noText);
                return;
            }

            updateCount();
            renderGrid();
        } catch (err) {
            showMessage(t.errTitle, t.errText);
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
            img.dataset.src = images[i].thumb; // defer actual load
            img.alt = t.photo + ' ' + (i + 1);
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
        if (countEl) countEl.textContent = images.length + ' ' + t.photos;
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
        const newSrc = images[currentIndex].full;
        if (lbImg.src === newSrc) return;
        if (lbSpinner) lbSpinner.classList.add('visible');
        const preload = new Image();
        preload.onload = () => {
            lbImg.src = newSrc;
            if (lbSpinner) lbSpinner.classList.remove('visible');
        };
        preload.onerror = () => {
            lbImg.src = newSrc;
            if (lbSpinner) lbSpinner.classList.remove('visible');
        };
        preload.src = newSrc;
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
            '  <p>' + t.loading + '</p>' +
            '</div>';
    }

    function showMessage(title, text) {
        gridEl.innerHTML =
            '<div class="gallery-message">' +
            '  <h3>' + escapeHtml(title) + '</h3>' +
            '  <p>' + escapeHtml(text) + '</p>' +
            '</div>';
        if (countEl) countEl.textContent = '0 ' + t.photos;
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    return { init };
})();
