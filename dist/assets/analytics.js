(function(){
  'use strict';
  // Analytics are disabled on file:// so local previews/PDF builds don't pollute counts.
  if (location.protocol === 'file:') return;
  // GoatCounter.
  var goatcounter = "https://causal-mapping-garden.goatcounter.com/count";
  if (goatcounter) {
    var goatcounterScript = document.createElement('script');
    goatcounterScript.async = true;
    goatcounterScript.src = 'https://gc.zgo.at/count.js';
    goatcounterScript.setAttribute('data-goatcounter', goatcounter);
    document.head.appendChild(goatcounterScript);
  }
  // Umami Cloud.
  var umamiScriptUrl = "https://cloud.umami.is/script.js";
  var umamiWebsiteId = "cc6d6b30-1bf8-497f-b38a-7feae109d761";
  if (umamiScriptUrl && umamiWebsiteId) {
    var umamiScript = document.createElement('script');
    umamiScript.defer = true;
    umamiScript.src = umamiScriptUrl;
    umamiScript.setAttribute('data-website-id', umamiWebsiteId);
    document.head.appendChild(umamiScript);
  }
})();
