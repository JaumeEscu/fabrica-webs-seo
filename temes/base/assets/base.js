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
