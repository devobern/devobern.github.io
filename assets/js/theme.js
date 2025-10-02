(function(){
  try {
    var stored = localStorage.getItem('theme');
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    var theme = stored || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
    var btn = document.getElementById('theme-toggle');
    if(btn){
      function getTheme(){ return document.documentElement.getAttribute('data-theme') || 'light'; }
      function setTheme(t){ document.documentElement.setAttribute('data-theme', t); try{ localStorage.setItem('theme', t);}catch(e){} }
      btn.addEventListener('click', function(){ setTheme(getTheme()==='dark' ? 'light' : 'dark'); });
    }
  } catch(e) {/* noop */}
})();
