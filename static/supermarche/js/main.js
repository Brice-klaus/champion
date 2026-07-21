document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('year').textContent = new Date().getFullYear();

  /* ---------- Thème sombre / clair ---------- */
  const root = document.documentElement;
  const themeBtn = document.getElementById('theme-toggle');
  const savedTheme = localStorage.getItem('champion-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    root.classList.add('dark');
  }

  themeBtn.addEventListener('click', () => {
    root.classList.toggle('dark');
    localStorage.setItem('champion-theme', root.classList.contains('dark') ? 'dark' : 'light');
  });

  /* ---------- Langue FR / EN ---------- */
  const langBtn = document.getElementById('lang-toggle');
  const langCurrent = document.getElementById('lang-current');
  const langOther = document.getElementById('lang-other');

  function applyLang(lang) {
    document.querySelectorAll('[data-fr][data-en]').forEach(el => {
      el.textContent = lang === 'fr' ? el.dataset.fr : el.dataset.en;
    });
    langCurrent.textContent = lang.toUpperCase();
    langOther.textContent = lang === 'fr' ? 'EN' : 'FR';
    document.documentElement.lang = lang;
    localStorage.setItem('champion-lang', lang);
  }

  const savedLang = localStorage.getItem('champion-lang') || 'fr';
  applyLang(savedLang);

  langBtn.addEventListener('click', () => {
    applyLang(localStorage.getItem('champion-lang') === 'fr' ? 'en' : 'fr');
  });

  /* ---------- Menu mobile ---------- */
  const mobileBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  mobileBtn.addEventListener('click', () => mobileMenu.classList.toggle('hidden'));

  /* ---------- Reveal au scroll ---------- */
  const revealEls = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });
  revealEls.forEach(el => io.observe(el));
});