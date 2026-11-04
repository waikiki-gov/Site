/* Ski Paradise page: island tabs and interactive map hotspots */
(() => {
    'use strict';

    function initSkiParadise() {
        var tabBtns = document.querySelectorAll('.island-tab-btn');
        var panels = document.querySelectorAll('.island-panel');
        tabBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var target = btn.getAttribute('data-tab');
                tabBtns.forEach(function(b) {
                    var active = b === btn;
                    b.classList.toggle('is-active', active);
                    b.setAttribute('aria-selected', active ? 'true' : 'false');
                });
                panels.forEach(function(panel) {
                    var match = panel.id === 'panel-' + target;
                    panel.classList.toggle('is-active', match);
                });
            });
        });
        panels.forEach(function(panel) {
            var pins = panel.querySelectorAll('.map-hotspot[data-spot]');
            var cards = panel.querySelectorAll('.island-hotspot-card[data-spot]');
            function activateSpot(spotId) {
                pins.forEach(function(p) {
                    p.classList.toggle('is-active', p.getAttribute('data-spot') === spotId);
                });
                cards.forEach(function(c) {
                    c.classList.toggle('is-active', c.getAttribute('data-spot') === spotId);
                });
            }
            pins.forEach(function(pin) {
                var id = pin.getAttribute('data-spot');
                pin.addEventListener('mouseenter', function() {
                    activateSpot(id);
                });
                pin.addEventListener('click', function() {
                    activateSpot(id);
                    var card = panel.querySelector('.island-hotspot-card[data-spot="' + id + '"]');
                    if (card) card.scrollIntoView({
                        behavior: 'smooth',
                        block: 'nearest'
                    });
                });
            });
            cards.forEach(function(card) {
                var id = card.getAttribute('data-spot');
                card.addEventListener('mouseenter', function() {
                    activateSpot(id);
                });
                card.addEventListener('click', function() {
                    activateSpot(id);
                });
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSkiParadise);
    } else {
        initSkiParadise();
    }
})();

