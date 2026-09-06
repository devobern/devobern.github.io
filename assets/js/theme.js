/**
 * Theme handling.
 *
 * Wird bewusst ohne `defer` im <head> geladen: data-theme muss gesetzt sein,
 * bevor der Body gerendert wird, sonst blitzt kurz das falsche Theme auf.
 * Die Verdrahtung des Buttons passiert deshalb erst auf DOMContentLoaded.
 */
(function () {
  'use strict';

  var GISCUS_ORIGIN = 'https://giscus.app';

  function readStoredTheme() {
    try {
      var stored = localStorage.getItem('theme');
      return stored === 'dark' || stored === 'light' ? stored : null;
    } catch (e) {
      return null;
    }
  }

  function prefersDark() {
    return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  }

  function getTheme() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  function setGiscusTheme(theme) {
    var iframe = document.querySelector('iframe.giscus-frame');
    if (!iframe || !iframe.contentWindow) return;
    iframe.contentWindow.postMessage({ giscus: { setConfig: { theme: theme } } }, GISCUS_ORIGIN);
  }

  function applyTheme(theme, persist) {
    document.documentElement.setAttribute('data-theme', theme);
    if (persist) {
      try { localStorage.setItem('theme', theme); } catch (e) { /* Storage blockiert */ }
    }
    setGiscusTheme(theme);
  }

  // Sofort anwenden, noch vor dem ersten Paint.
  applyTheme(readStoredTheme() || (prefersDark() ? 'dark' : 'light'), false);

  function onReady() {
    var btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.addEventListener('click', function () {
        applyTheme(getTheme() === 'dark' ? 'light' : 'dark', true);
      });
    }

    // Systemwechsel übernehmen, solange der Nutzer nichts manuell gewählt hat.
    if (window.matchMedia) {
      var mq = window.matchMedia('(prefers-color-scheme: dark)');
      var onChange = function (event) {
        if (readStoredTheme()) return;
        applyTheme(event.matches ? 'dark' : 'light', false);
      };
      if (mq.addEventListener) {
        mq.addEventListener('change', onChange);
      } else if (mq.addListener) {
        mq.addListener(onChange);
      }
    }

    // Sobald das Giscus-iframe meldet, dass es bereit ist, Theme angleichen.
    window.addEventListener('message', function (event) {
      if (event.origin !== GISCUS_ORIGIN) return;
      if (!event.data || !event.data.giscus) return;
      setGiscusTheme(getTheme());
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
})();
