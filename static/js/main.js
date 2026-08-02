/* LocalRide — global site behaviour: theme toggle, mobile nav, toasts, loader */

document.addEventListener('DOMContentLoaded', function () {
  /* ---------- Theme (dark/light) ---------- */
  const root = document.documentElement;
  const saved = localStorage.getItem('localride-theme');
  if (saved) root.setAttribute('data-theme', saved);

  const toggleBtn = document.getElementById('themeToggle');
  if (toggleBtn) {
    updateToggleIcon();
    toggleBtn.addEventListener('click', function () {
      const current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('localride-theme', next);
      updateToggleIcon();
    });
  }
  function updateToggleIcon() {
    const isDark = root.getAttribute('data-theme') === 'dark';
    toggleBtn.textContent = isDark ? '☀️' : '🌙';
  }

  /* ---------- Mobile nav ---------- */
  const mobileToggle = document.getElementById('mobileToggle');
  const navLinks = document.getElementById('navLinks');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => navLinks.classList.toggle('mobile-open'));
  }

  const sidebarToggle = document.getElementById('sidebarToggle');
  const dashSidebar = document.getElementById('dashSidebar');
  if (sidebarToggle && dashSidebar) {
    sidebarToggle.addEventListener('click', () => dashSidebar.classList.toggle('open'));
  }

  /* ---------- Auto-dismiss toasts ---------- */
  document.querySelectorAll('.toast').forEach(function (toast, i) {
    setTimeout(() => {
      toast.style.transition = 'opacity .4s ease, transform .4s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(30px)';
      setTimeout(() => toast.remove(), 400);
    }, 4500 + i * 300);
  });

  /* ---------- Star rating widget ---------- */
  document.querySelectorAll('.star-rating').forEach(function (widget) {
    const input = document.querySelector(widget.dataset.target);
    const stars = widget.querySelectorAll('span');
    stars.forEach(function (star) {
      star.addEventListener('click', function () {
        const val = parseInt(star.dataset.value, 10);
        if (input) input.value = val;
        stars.forEach(s => s.classList.toggle('active', parseInt(s.dataset.value, 10) <= val));
      });
    });
  });

  /* ---------- Submit-loader on forms with data-loading ---------- */
  document.querySelectorAll('form[data-loading]').forEach(function (form) {
    form.addEventListener('submit', function () {
      showLoader();
    });
  });
});

function showLoader() {
  const overlay = document.getElementById('loaderOverlay');
  if (overlay) overlay.classList.add('active');
}
function hideLoader() {
  const overlay = document.getElementById('loaderOverlay');
  if (overlay) overlay.classList.remove('active');
}
