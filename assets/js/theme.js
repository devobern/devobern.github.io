(function(){
  try {
    var stored = localStorage.getItem('theme');
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    var theme = stored || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);

    function getTheme(){
      return document.documentElement.getAttribute('data-theme') || 'light';
    }

    function setGiscusTheme(themeValue){
      var iframe = document.querySelector('iframe.giscus-frame');
      if(iframe && iframe.contentWindow){
        iframe.contentWindow.postMessage({
          giscus: { setConfig: { theme: themeValue } }
        }, 'https://giscus.app');
      }
    }

    function setTheme(t){
      document.documentElement.setAttribute('data-theme', t);
      try{ localStorage.setItem('theme', t);}catch(e){}
      setGiscusTheme(t === 'dark' ? 'dark' : 'light');
    }

  var btn = document.getElementById('theme-toggle');
    if(btn){
      btn.addEventListener('click', function(){
        setTheme(getTheme()==='dark' ? 'light' : 'dark');
      });
    }

    // When Giscus iframe loads, align its theme with the current site theme
    window.addEventListener('message', function(event){
      if(event.origin !== 'https://giscus.app') return;
      if(!(event.data && event.data.giscus)) return;
      // At this point the iframe exists; apply current theme
      setGiscusTheme(getTheme()==='dark' ? 'dark' : 'light');
    });
  } catch(e) {/* noop */}
})();
