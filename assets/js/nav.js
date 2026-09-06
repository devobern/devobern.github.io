/**
 * Mobile navigation (hamburger).
 *
 * Progressive Enhancement: ohne JavaScript bleibt der Knopf `hidden` und die
 * Navigation eine gewöhnliche, immer sichtbare Liste. Erst dieses Skript
 * blendet den Knopf ein und macht die Liste einklappbar.
 *
 * Der Umbruchpunkt steht in --nav-breakpoint (assets/css/style.css) und wird
 * hier ausgelesen, damit CSS und JS nicht auseinanderlaufen können.
 */
(function () {
  'use strict';

  var FALLBACK_BREAKPOINT = '40rem';

  function onReady() {
    var toggle = document.getElementById('nav-toggle');
    var nav = document.getElementById('site-nav');
    if (!toggle || !nav) return;

    var breakpoint = getComputedStyle(document.documentElement)
      .getPropertyValue('--nav-breakpoint').trim() || FALLBACK_BREAKPOINT;
    var mq = window.matchMedia('(max-width: ' + breakpoint + ')');

    nav.classList.add('is-collapsible');
    toggle.hidden = false;

    function isOpen() {
      return toggle.getAttribute('aria-expanded') === 'true';
    }

    function setOpen(open, moveFocus) {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      nav.classList.toggle('is-open', open);
      // Das Panel steht im DOM vor dem Knopf, damit auf dem Desktop
      // Lese- und Fokusreihenfolge zur sichtbaren Reihenfolge passen. Beim
      // Öffnen wandert der Fokus deshalb aktiv hinein, sonst würde Tab die
      // gerade eingeblendeten Links überspringen.
      if (open && moveFocus) {
        var first = nav.querySelector('a[href]');
        if (first) first.focus();
      }
    }

    function close(refocus) {
      if (!isOpen()) return;
      setOpen(false, false);
      if (refocus) toggle.focus();
    }

    toggle.addEventListener('click', function () {
      setOpen(!isOpen(), true);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') close(true);
    });

    // Tippen ausserhalb schliesst das Panel, ein Klick darin nicht.
    document.addEventListener('click', function (event) {
      if (!isOpen()) return;
      if (nav.contains(event.target) || toggle.contains(event.target)) return;
      close(false);
    });

    // Verlässt der Fokus die Kopfzeile per Tab, schliesst das Panel mit.
    document.addEventListener('focusin', function (event) {
      if (!isOpen()) return;
      if (nav.contains(event.target) || toggle.contains(event.target)) return;
      close(false);
    });

    // Beim Wechsel auf die Desktop-Breite den Zustand zurücksetzen, sonst
    // bleibt `aria-expanded="false"` an einer sichtbaren Navigation hängen.
    function onBreakpointChange(event) {
      if (!event.matches) close(false);
    }
    if (mq.addEventListener) {
      mq.addEventListener('change', onBreakpointChange);
    } else if (mq.addListener) {
      mq.addListener(onBreakpointChange);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
})();
