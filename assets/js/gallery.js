/**
 * Gallery Lightbox - Vanilla JS
 *
 * Features:
 * - Category filtering
 * - Keyboard navigation (← → ESC)
 * - Touch/swipe support
 * - EXIF display
 * - Image preloading
 */

(function() {
  'use strict';

  let galleryData = [];
  let allItems = [];
  let visibleItems = [];
  let currentIndex = 0;
  let lightbox = null;
  let touchStartX = 0;

  function init() {
    const container = document.getElementById('gallery-grid');
    if (!container) return;

    allItems = Array.from(container.querySelectorAll('.gallery-item'));
    visibleItems = [...allItems];

    loadExifData();
    setupFilters();
    createLightbox();
    setupGalleryItems();
  }

  async function loadExifData() {
    try {
      const response = await fetch('/assets/gallery/gallery.json');
      if (!response.ok) throw new Error('Gallery data not found');
      galleryData = await response.json();
    } catch (error) {
      console.warn('EXIF data could not be loaded:', error);
      galleryData = [];
    }
  }

  function setupFilters() {
    const filters = document.querySelectorAll('.gallery-filter');
    filters.forEach(btn => {
      btn.addEventListener('click', () => {
        const category = btn.dataset.category;

        filters.forEach(f => {
          f.classList.remove('gallery-filter--active');
          f.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('gallery-filter--active');
        btn.setAttribute('aria-selected', 'true');

        filterGallery(category);
      });
    });
  }

  function filterGallery(category) {
    allItems.forEach(item => {
      const match = category === 'all' || item.dataset.category === category;
      if (match) {
        item.removeAttribute('data-hidden');
      } else {
        item.setAttribute('data-hidden', 'true');
      }
    });
    visibleItems = allItems.filter(item => !item.hasAttribute('data-hidden'));
  }

  function setupGalleryItems() {
    allItems.forEach(item => {
      item.addEventListener('click', () => {
        const index = visibleItems.indexOf(item);
        if (index !== -1) openLightbox(index);
      });
    });
  }

  function getExifForFile(filename) {
    const baseName = filename.replace('.webp', '');
    return galleryData.find(item => item.filename === baseName);
  }

  function createLightbox() {
    if (lightbox) return;

    lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.setAttribute('role', 'dialog');
    lightbox.setAttribute('aria-modal', 'true');
    lightbox.setAttribute('aria-label', 'Bildansicht');
    lightbox.innerHTML = `
      <div class="lightbox-backdrop"></div>
      <div class="lightbox-content">
        <button class="lightbox-close" aria-label="Schliessen">&times;</button>
        <button class="lightbox-prev" aria-label="Vorheriges Bild">&#8249;</button>
        <button class="lightbox-next" aria-label="Nächstes Bild">&#8250;</button>
        <div class="lightbox-image-container">
          <img class="lightbox-image" src="" alt="" />
          <div class="lightbox-loader">Laden...</div>
        </div>
        <div class="lightbox-exif"></div>
        <div class="lightbox-counter"></div>
      </div>
    `;

    document.body.appendChild(lightbox);

    lightbox.querySelector('.lightbox-backdrop').addEventListener('click', closeLightbox);
    lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
    lightbox.querySelector('.lightbox-prev').addEventListener('click', showPrev);
    lightbox.querySelector('.lightbox-next').addEventListener('click', showNext);

    document.addEventListener('keydown', handleKeydown);

    const content = lightbox.querySelector('.lightbox-content');
    content.addEventListener('touchstart', e => { touchStartX = e.changedTouches[0].screenX; }, { passive: true });
    content.addEventListener('touchend', e => {
      const diff = touchStartX - e.changedTouches[0].screenX;
      if (Math.abs(diff) > 50) diff > 0 ? showNext() : showPrev();
    }, { passive: true });
  }

  function openLightbox(index) {
    if (!lightbox || visibleItems.length === 0) return;
    currentIndex = index;
    lightbox.classList.add('lightbox--open');
    document.body.style.overflow = 'hidden';
    showImage(currentIndex);
    lightbox.querySelector('.lightbox-close').focus();
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove('lightbox--open');
    document.body.style.overflow = '';
  }

  function showImage(index) {
    const item = visibleItems[index];
    if (!item) return;

    const img = lightbox.querySelector('.lightbox-image');
    const loader = lightbox.querySelector('.lightbox-loader');
    const exifEl = lightbox.querySelector('.lightbox-exif');
    const counterEl = lightbox.querySelector('.lightbox-counter');

    const filename = item.dataset.file;
    const alt = item.dataset.alt;

    loader.style.display = 'block';
    img.style.opacity = '0';

    img.onload = () => {
      loader.style.display = 'none';
      img.style.opacity = '1';
    };
    img.src = `/assets/gallery/full/${filename}`;
    img.alt = alt;

    const exifData = getExifForFile(filename);
    if (exifData?.exif) {
      const parts = [
        exifData.exif.camera,
        exifData.exif.lens,
        exifData.exif.focal_length,
        exifData.exif.aperture,
        exifData.exif.shutter,
        exifData.exif.iso,
        exifData.exif.date_display
      ].filter(Boolean);
      exifEl.textContent = parts.join(' · ');
      exifEl.style.display = parts.length ? 'block' : 'none';
    } else {
      exifEl.style.display = 'none';
    }

    counterEl.textContent = `${index + 1} / ${visibleItems.length}`;

    const showNav = visibleItems.length > 1 ? 'block' : 'none';
    lightbox.querySelector('.lightbox-prev').style.display = showNav;
    lightbox.querySelector('.lightbox-next').style.display = showNav;

    preloadImage(index - 1);
    preloadImage(index + 1);
  }

  function preloadImage(index) {
    const item = visibleItems[index];
    if (!item) return;
    const img = new Image();
    img.src = `/assets/gallery/full/${item.dataset.file}`;
  }

  function showPrev() {
    currentIndex = (currentIndex - 1 + visibleItems.length) % visibleItems.length;
    showImage(currentIndex);
  }

  function showNext() {
    currentIndex = (currentIndex + 1) % visibleItems.length;
    showImage(currentIndex);
  }

  function handleKeydown(e) {
    if (!lightbox?.classList.contains('lightbox--open')) return;
    switch (e.key) {
      case 'Escape': closeLightbox(); break;
      case 'ArrowLeft': showPrev(); break;
      case 'ArrowRight': showNext(); break;
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
