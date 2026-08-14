document.addEventListener('DOMContentLoaded', () => {

  // Mobile nav toggle
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  toggle?.addEventListener('click', () => {
    navLinks?.classList.toggle('open');
  });

  document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks?.classList.remove('open');
    });
  });

  // Scroll-triggered fade-in
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.feature-card, .step, .pricing-card, .gdpr-list li').forEach(el => {
    el.classList.add('fade-in');
    observer.observe(el);
  });

  // Toast
  const toast = document.getElementById('toast');

  function showToast(message, isError = false) {
    toast.textContent = message;
    toast.style.borderColor = isError ? '#ef4444' : '#00d4aa';
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 5000);
  }

  // Contact form submission
  const form = document.getElementById('contact-form');

  // Formspree sends submissions to rorshopping@gmail.com
  // For local FastAPI backend, swap back to '/api/contact'
  const CONTACT_ENDPOINT = 'https://formspree.io/f/xrendngb';

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'Sending...';
    btn.disabled = true;

    try {
      const payload = {
        company_name: document.getElementById('company-name').value,
        email: document.getElementById('email').value,
        employees: document.getElementById('employees').value,
        interest: document.getElementById('interest').value,
        message: document.getElementById('message').value,
      };

      const resp = await fetch(CONTACT_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await resp.json();

      if (resp.ok) {
        showToast(data.message || data.next || 'Thank you! We will be in touch within 24 hours.');
        form.reset();
      } else {
        showToast(data.detail || data.error || 'Something went wrong. Please email us at rorshopping@gmail.com.', true);
      }
    } catch (err) {
      showToast('Network error. Please email us directly at rorshopping@gmail.com.', true);
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  });

  // Cookie consent banner
  const cookieBanner = document.getElementById('cookie-banner');
  const cookieAccept = document.getElementById('cookie-accept');

  if (!localStorage.getItem('gdpr_cookie_consent')) {
    setTimeout(() => cookieBanner?.classList.add('show'), 500);
  }

  cookieAccept?.addEventListener('click', () => {
    localStorage.setItem('gdpr_cookie_consent', 'accepted');
    cookieBanner.classList.remove('show');
    document.dispatchEvent(new CustomEvent('gdpr-consent-granted'));
  });

  // Smooth reveal for hero stats
  const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  });

  document.querySelectorAll('.stat').forEach((stat, i) => {
    stat.style.opacity = '0';
    stat.style.transform = 'translateY(20px)';
    stat.style.transition = `opacity 0.6s ease ${i * 0.15}s, transform 0.6s ease ${i * 0.15}s`;
    statsObserver.observe(stat);
  });

});
