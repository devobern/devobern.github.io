/**
 * Galerie Lightbox - Vanilla JS
 *
 * Features:
 * - Tastaturnavigation (← → ESC)
 * - Touch-Swipe auf Mobilgeräten
 * - EXIF-Anzeige
 * - Preloading benachbarter Bilder
 */

(function() {
  'use strict';

  let galleryData = [];
  let currentIndex = 0;
  let lightbox = null;
  let touchStartX = 0;
  let touchEndX = 0;

  // Initialisierung
  function init() {
    loadGalleryData();
  }

  // Galerie-Daten laden
  async function loadGalleryData() {
    try {
      const response = await fetch('/assets/gallery/gallery.json');
      if (!response.ok) throw new Error('Gallery data not found');
      galleryData = await response.json();
      renderGallery();
    } catch (error) {
      console.error('Galerie konnte nicht geladen werden:', error);
      showEmptyState();
    }
  }

  // Leerer Zustand anzeigen
  function showEmptyState() {
    const container = document.getElementById('gallery-grid');
    if (container) {
      container.innerHTML = '<p class="gallery-empty">Noch keine Fotos in der Galerie.</p>';
    }
  }

  // Galerie rendern
  function renderGallery() {
    const container = document.getElementById('gallery-grid');
    if (!container || galleryData.length === 0) {
      showEmptyState();
      return;
    }

    container.innerHTML = galleryData.map((item, index) => `
      <button class="gallery-item" data-index="${index}" aria-label="Bild ${index + 1} öffnen">
        <img src="${item.thumb}" alt="" loading="lazy" />
      </button>
    `).join('');

    // Event-Listener für Thumbnails
    container.querySelectorAll('.gallery-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const index = parseInt(e.currentTarget.dataset.index, 10);
        openLightbox(index);
      });
    });

    createLightbox();
  }

  // Lightbox erstellen
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

    // Event-Listener
    lightbox.querySelector('.lightbox-backdrop').addEventListener('click', closeLightbox);
    lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
    lightbox.querySelector('.lightbox-prev').addEventListener('click', showPrev);
    lightbox.querySelector('.lightbox-next').addEventListener('click', showNext);

    // Keyboard
    document.addEventListener('keydown', handleKeydown);

    // Touch-Events
    const content = lightbox.querySelector('.lightbox-content');
    content.addEventListener('touchstart', handleTouchStart, { passive: true });
    content.addEventListener('touchend', handleTouchEnd, { passive: true });
  }

  // Lightbox öffnen
  function openLightbox(index) {
    if (!lightbox || galleryData.length === 0) return;

    currentIndex = index;
    lightbox.classList.add('lightbox--open');
    document.body.style.overflow = 'hidden';
    showImage(currentIndex);

    // Fokus auf Lightbox setzen
    lightbox.querySelector('.lightbox-close').focus();
  }

  // Lightbox schliessen
  function closeLightbox() {
    if (!lightbox) return;

    lightbox.classList.remove('lightbox--open');
    document.body.style.overflow = '';
  }

  // Bild anzeigen
  function showImage(index) {
    const item = galleryData[index];
    if (!item) return;

    const img = lightbox.querySelector('.lightbox-image');
    const loader = lightbox.querySelector('.lightbox-loader');
    const exifEl = lightbox.querySelector('.lightbox-exif');
    const counterEl = lightbox.querySelector('.lightbox-counter');

    // Loader anzeigen
    loader.style.display = 'block';
    img.style.opacity = '0';

    // Bild laden
    img.onload = () => {
      loader.style.display = 'none';
      img.style.opacity = '1';
    };
    img.src = item.full;
    img.alt = item.filename;

    // EXIF anzeigen
    if (item.exif && Object.keys(item.exif).length > 0) {
      const exifParts = [];
      if (item.exif.camera) exifParts.push(item.exif.camera);
      if (item.exif.lens) exifParts.push(item.exif.lens);
      if (item.exif.focal_length) exifParts.push(item.exif.focal_length);
      if (item.exif.aperture) exifParts.push(item.exif.aperture);
      if (item.exif.shutter) exifParts.push(item.exif.shutter);
      if (item.exif.iso) exifParts.push(item.exif.iso);
      if (item.exif.date_display) exifParts.push(item.exif.date_display);

      exifEl.textContent = exifParts.join(' · ');
      exifEl.style.display = exifParts.length > 0 ? 'block' : 'none';
    } else {
      exifEl.style.display = 'none';
    }

    // Counter anzeigen
    counterEl.textContent = `${index + 1} / ${galleryData.length}`;

    // Navigation-Buttons
    lightbox.querySelector('.lightbox-prev').style.display = galleryData.length > 1 ? 'block' : 'none';
    lightbox.querySelector('.lightbox-next').style.display = galleryData.length > 1 ? 'block' : 'none';

    // Preload benachbarter Bilder
    preloadImage(index - 1);
    preloadImage(index + 1);
  }

  // Bild vorladen
  function preloadImage(index) {
    if (index < 0 || index >= galleryData.length) return;
    const img = new Image();
    img.src = galleryData[index].full;
  }

  // Vorheriges Bild
  function showPrev() {
    currentIndex = (currentIndex - 1 + galleryData.length) % galleryData.length;
    showImage(currentIndex);
  }

  // Nächstes Bild
  function showNext() {
    currentIndex = (currentIndex + 1) % galleryData.length;
    showImage(currentIndex);
  }

  // Tastatur-Handler
  function handleKeydown(e) {
    if (!lightbox || !lightbox.classList.contains('lightbox--open')) return;

    switch (e.key) {
      case 'Escape':
        closeLightbox();
        break;
      case 'ArrowLeft':
        showPrev();
        break;
      case 'ArrowRight':
        showNext();
        break;
    }
  }

  // Touch-Handler
  function handleTouchStart(e) {
    touchStartX = e.changedTouches[0].screenX;
  }

  function handleTouchEnd(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }

  function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) < swipeThreshold) return;

    if (diff > 0) {
      // Swipe links = nächstes Bild
      showNext();
    } else {
      // Swipe rechts = vorheriges Bild
      showPrev();
    }
  }

  // DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
