(function () {
  'use strict';
  var MEASUREMENT_ID = 'G-XXXXXXXXXX';

  function isConsented() {
    return window.localStorage && localStorage.getItem('gdpr_cookie_consent') === 'accepted';
  }

  function loadGA() {
    if (window.dataLayer && window.dataLayer['gtag.done']) {
      return;
    }
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    gtag('js', new Date());
    gtag('config', MEASUREMENT_ID, { anonymize_ip: true });

    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + MEASUREMENT_ID;
    s.onload = function () {
      if (window.gtag) {
        gtag('config', MEASUREMENT_ID, { anonymize_ip: true });
      }
    };
    document.head.appendChild(s);
    window.dataLayer['gtag.done'] = true;
  }

  function loadVercelAnalytics() {
    if (document.getElementById('vercel-insights-script')) {
      return;
    }
    window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
    var s = document.createElement('script');
    s.id = 'vercel-insights-script';
    s.defer = true;
    s.src = '/_vercel/insights/script.js';
    document.head.appendChild(s);
  }

  function loadAnalytics() {
    if (MEASUREMENT_ID && MEASUREMENT_ID.indexOf('G-') === 0 && MEASUREMENT_ID !== 'G-XXXXXXXXXX') {
      loadGA();
    }
    loadVercelAnalytics();
  }

  if (isConsented()) {
    loadAnalytics();
  } else {
    document.addEventListener('gdpr-consent-granted', loadAnalytics, { once: true });
  }
})();
