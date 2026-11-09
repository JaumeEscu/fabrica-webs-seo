// Menú mòbil. Res més: la web ha de funcionar sense JavaScript.
document.addEventListener('DOMContentLoaded', () => {
  const boto = document.querySelector('.menu-boto');
  const menu = document.getElementById('menu-principal');
  if (!boto || !menu) return;
  boto.addEventListener('click', () => {
    const obert = menu.classList.toggle('obert');
    boto.setAttribute('aria-expanded', obert);
  });
});

// Índex lateral: marca la secció que es llegeix.
document.addEventListener('DOMContentLoaded', () => {
  const enllacos = [...document.querySelectorAll('.index a[href^="#"]')];
  if (!enllacos.length || !('IntersectionObserver' in window)) return;
  const perId = new Map(enllacos.map(a => [a.getAttribute('href').slice(1), a]));
  const obs = new IntersectionObserver(entrades => {
    entrades.forEach(e => {
      if (!e.isIntersecting) return;
      enllacos.forEach(a => a.removeAttribute('aria-current'));
      perId.get(e.target.id)?.setAttribute('aria-current', 'true');
    });
  }, { rootMargin: '-20% 0px -70% 0px' });
  perId.forEach((_, id) => { const el = document.getElementById(id); if (el) obs.observe(el); });
});
