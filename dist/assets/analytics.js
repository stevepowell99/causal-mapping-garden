(function(){
  'use strict';
  // GoatCounter analytics. Disabled on file:// to avoid counting local previews/PDF builds.
  var goatcounter = "https://causal-mapping-garden.goatcounter.com/count";
  if (!goatcounter) return;
  if (location.protocol === 'file:') return;
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://gc.zgo.at/count.js';
  s.setAttribute('data-goatcounter', goatcounter);
  document.head.appendChild(s);
})();
