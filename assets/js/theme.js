(function(){
  try {
    var stored = localStorage.getItem('theme');
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    var theme = stored || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);

    function getTheme(){
      return document.documentElement.getAttribute('data-theme') || 'light';
    }

    function setTheme(t){
      document.documentElement.setAttribute('data-theme', t);
      try{ localStorage.setItem('theme', t);}catch(e){}

      // Notify Giscus iframe (if present) so it can update its theme
      var iframe = document.querySelector('iframe.giscus-frame');
      if(iframe && iframe.contentWindow){
        var giscusTheme = (t === 'dark') ? 'dark' : 'light';
        iframe.contentWindow.postMessage({
          giscus: {
            setConfig: {
              theme: giscusTheme
            }
          }
        }, 'https://giscus.app');
      }
    }

    var btn = document.getElementById('theme-toggle');
    if(btn){
      btn.addEventListener('click', function(){
        setTheme(getTheme()==='dark' ? 'light' : 'dark');
      });
    }
  } catch(e) {/* noop */}
})();
