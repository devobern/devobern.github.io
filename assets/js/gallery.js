/**
 * Gallery Lightbox - Vanilla JS
 *
 * Features:
 * - Category filtering
 * - Keyboard navigation (← → ESC), focus trap and focus restore
 * - Touch/swipe support
 * - EXIF display
 * - Image preloading
 *
 * Beschriftungen kommen als data-Attribute vom Server (siehe
 * _includes/gallery.html), damit die Lightbox ohne Inline-Skript
 * mehrsprachig bleibt (CSP: script-src 'self').
 */

(function () {
  'use strict';

  // Nur Dateinamen ohne Pfadanteile zulassen, damit ein manipuliertes
  // data-file nie zu einer fremden URL aufgelöst werden kann.
  var SAFE_FILENAME = /^[A-Za-z0-9._-]+$/;

  var DEFAULT_LABELS = {
    dialog: 'Bildansicht',
    close: 'Schliessen',
    prev: 'Vorheriges Bild',
    next: 'Nächstes Bild',
    loading: 'Laden…'
  };

  var FOCUSABLE = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  var galleryData = [];
  var allItems = [];
  var visibleItems = [];
  var currentIndex = 0;
  var lightbox = null;
  var labels = DEFAULT_LABELS;
  var lastFocused = null;
  var touchStartX = 0;

  function isSafeFilename(name) {
    return typeof name === 'string' && name.length > 0 && SAFE_FILENAME.test(name);
  }

  function readLabels(container) {
    var d = container.dataset;
    return {
      dialog: d.labelDialog || DEFAULT_LABELS.dialog,
      close: d.labelClose || DEFAULT_LABELS.close,
      prev: d.labelPrev || DEFAULT_LABELS.prev,
      next: d.labelNext || DEFAULT_LABELS.next,
      loading: d.labelLoading || DEFAULT_LABELS.loading
    };
  }

  function init() {
    var container = document.getElementById('gallery-grid');
    if (!container) return;

    labels = readLabels(container);
    allItems = Array.prototype.slice.call(container.querySelectorAll('.gallery-item'));
    visibleItems = allItems.slice();

    loadExifData();
    setupFilters();
    createLightbox();
    setupGalleryItems();
  }

  function loadExifData() {
    fetch('/assets/gallery/gallery.json')
      .then(function (response) {
        if (!response.ok) throw new Error('Gallery data not found');
        return response.json();
      })
      .then(function (data) {
        galleryData = Array.isArray(data) ? data : [];
      })
      .catch(function (error) {
        console.warn('EXIF data could not be loaded:', error);
        galleryData = [];
      });
  }

  function setupFilters() {
    var filters = document.querySelectorAll('.gallery-filter');
    Array.prototype.forEach.call(filters, function (btn) {
      btn.addEventListener('click', function () {
        Array.prototype.forEach.call(filters, function (f) {
          f.classList.remove('gallery-filter--active');
          f.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('gallery-filter--active');
        btn.setAttribute('aria-selected', 'true');
        filterGallery(btn.dataset.category);
      });
    });
  }

  function filterGallery(category) {
    allItems.forEach(function (item) {
      var match = category === 'all' || item.dataset.category === category;
      if (match) {
        item.removeAttribute('data-hidden');
      } else {
        item.setAttribute('data-hidden', 'true');
      }
    });
    visibleItems = allItems.filter(function (item) {
      return !item.hasAttribute('data-hidden');
    });
  }

  function setupGalleryItems() {
    allItems.forEach(function (item) {
      item.addEventListener('click', function () {
        var index = visibleItems.indexOf(item);
        if (index !== -1) openLightbox(index);
      });
    });
  }

  function getExifForFile(filename) {
    var baseName = filename.replace(/\.webp$/, '');
    return galleryData.filter(function (item) {
      return item.filename === baseName;
    })[0];
  }

  function createLightbox() {
    if (lightbox) return;

    lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.setAttribute('role', 'dialog');
    lightbox.setAttribute('aria-modal', 'true');
    lightbox.setAttribute('aria-label', labels.dialog);
    lightbox.hidden = true;

    // textContent statt innerHTML: die Beschriftungen stammen aus
    // Seiteninhalten und werden hier nie als Markup interpretiert.
    var backdrop = el('div', 'lightbox-backdrop');
    var content = el('div', 'lightbox-content');

    var closeBtn = button('lightbox-close', labels.close, '×');
    var prevBtn = button('lightbox-prev', labels.prev, '‹');
    var nextBtn = button('lightbox-next', labels.next, '›');

    var imageContainer = el('div', 'lightbox-image-container');
    var image = document.createElement('img');
    image.className = 'lightbox-image';
    image.alt = '';
    var loader = el('div', 'lightbox-loader');
    loader.textContent = labels.loading;
    imageContainer.appendChild(image);
    imageContainer.appendChild(loader);

    var exif = el('div', 'lightbox-exif');
    var counter = el('div', 'lightbox-counter');

    content.appendChild(closeBtn);
    content.appendChild(prevBtn);
    content.appendChild(nextBtn);
    content.appendChild(imageContainer);
    content.appendChild(exif);
    content.appendChild(counter);

    lightbox.appendChild(backdrop);
    lightbox.appendChild(content);
    document.body.appendChild(lightbox);

    backdrop.addEventListener('click', closeLightbox);
    closeBtn.addEventListener('click', closeLightbox);
    prevBtn.addEventListener('click', showPrev);
    nextBtn.addEventListener('click', showNext);
    document.addEventListener('keydown', handleKeydown);

    content.addEventListener('touchstart', function (e) {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    content.addEventListener('touchend', function (e) {
      var diff = touchStartX - e.changedTouches[0].screenX;
      if (Math.abs(diff) > 50) {
        if (diff > 0) { showNext(); } else { showPrev(); }
      }
    }, { passive: true });
  }

  function el(tag, className) {
    var node = document.createElement(tag);
    node.className = className;
    return node;
  }

  function button(className, label, glyph) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = className;
    btn.setAttribute('aria-label', label);
    btn.textContent = glyph;
    return btn;
  }

  function isOpen() {
    return !!lightbox && lightbox.classList.contains('lightbox--open');
  }

  function openLightbox(index) {
    if (!lightbox || visibleItems.length === 0) return;
    lastFocused = document.activeElement;
    currentIndex = index;
    lightbox.hidden = false;
    lightbox.classList.add('lightbox--open');
    document.body.style.overflow = 'hidden';
    showImage(currentIndex);
    lightbox.querySelector('.lightbox-close').focus();
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove('lightbox--open');
    lightbox.hidden = true;
    document.body.style.overflow = '';
    if (lastFocused && typeof lastFocused.focus === 'function') {
      lastFocused.focus();
    }
    lastFocused = null;
  }

  function showImage(index) {
    var item = visibleItems[index];
    if (!item) return;

    var img = lightbox.querySelector('.lightbox-image');
    var loader = lightbox.querySelector('.lightbox-loader');
    var exifEl = lightbox.querySelector('.lightbox-exif');
    var counterEl = lightbox.querySelector('.lightbox-counter');

    var filename = item.dataset.file;
    if (!isSafeFilename(filename)) {
      console.warn('Skipping image with unexpected filename:', filename);
      return;
    }

    loader.style.display = 'block';
    img.style.opacity = '0';
    img.onload = function () {
      loader.style.display = 'none';
      img.style.opacity = '1';
    };
    img.src = '/assets/gallery/full/' + encodeURIComponent(filename);
    img.alt = item.dataset.alt || '';

    var exifData = getExifForFile(filename);
    var parts = exifData && exifData.exif ? [
      exifData.exif.camera,
      exifData.exif.lens,
      exifData.exif.focal_length,
      exifData.exif.aperture,
      exifData.exif.shutter,
      exifData.exif.iso,
      exifData.exif.date_display
    ].filter(Boolean) : [];
    exifEl.textContent = parts.join(' · ');
    exifEl.style.display = parts.length ? 'block' : 'none';

    counterEl.textContent = (index + 1) + ' / ' + visibleItems.length;

    var showNav = visibleItems.length > 1 ? 'block' : 'none';
    lightbox.querySelector('.lightbox-prev').style.display = showNav;
    lightbox.querySelector('.lightbox-next').style.display = showNav;

    preloadImage(index - 1);
    preloadImage(index + 1);
  }

  function preloadImage(index) {
    var item = visibleItems[index];
    if (!item || !isSafeFilename(item.dataset.file)) return;
    var img = new Image();
    img.src = '/assets/gallery/full/' + encodeURIComponent(item.dataset.file);
  }

  function showPrev() {
    currentIndex = (currentIndex - 1 + visibleItems.length) % visibleItems.length;
    showImage(currentIndex);
  }

  function showNext() {
    currentIndex = (currentIndex + 1) % visibleItems.length;
    showImage(currentIndex);
  }

  function trapFocus(event) {
    var focusable = Array.prototype.filter.call(
      lightbox.querySelectorAll(FOCUSABLE),
      function (node) { return node.offsetParent !== null; }
    );
    if (focusable.length === 0) return;
    var first = focusable[0];
    var last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function handleKeydown(e) {
    if (!isOpen()) return;
    switch (e.key) {
      case 'Escape': closeLightbox(); break;
      case 'ArrowLeft': showPrev(); break;
      case 'ArrowRight': showNext(); break;
      case 'Tab': trapFocus(e); break;
      default: break;
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
