/**
 * LexReg AI – Main JavaScript
 */

// ── Dark Mode ────────────────────────────────────────────────────────────────
function toggleDarkMode() {
  const html    = document.documentElement;
  const isDark  = html.getAttribute('data-theme') === 'dark';
  const newTheme = isDark ? 'light' : 'dark';
  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('lexreg-theme', newTheme);

  const icon = document.getElementById('darkModeIcon');
  if (icon) {
    icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
}

// Load saved theme on page load
(function () {
  const saved = localStorage.getItem('lexreg-theme');
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved);
    const icon = document.getElementById('darkModeIcon');
    if (icon) icon.className = saved === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
})();

// ── Sidebar Toggle (mobile) ──────────────────────────────────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar) sidebar.classList.toggle('open');
}

// Close sidebar when clicking outside (mobile)
document.addEventListener('click', function (e) {
  const sidebar = document.getElementById('sidebar');
  const toggle  = document.querySelector('.sidebar-toggle');
  if (sidebar && toggle && window.innerWidth < 992) {
    if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  }
});

// ── Flash Toast auto-dismiss ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.flash-toast').forEach(function (toast) {
    setTimeout(function () {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all .4s ease';
      setTimeout(() => toast.remove(), 400);
    }, 5000);
  });
});

// ── Notifications ─────────────────────────────────────────────────────────────
async function loadNotifications() {
  try {
    const r    = await fetch('/api/notifications');
    const data = await r.json();
    const list = document.getElementById('notifList');
    const dot  = document.getElementById('notifDot');
    if (!list) return;

    if (data.length === 0) {
      list.innerHTML = '<div class="text-center p-4 text-muted small"><i class="fas fa-bell-slash mb-2 d-block fs-4"></i>No new notifications</div>';
      if (dot) dot.style.display = 'none';
      return;
    }

    if (dot) dot.style.display = 'block';

    const icons = { success: 'check-circle text-success', info: 'info-circle text-info',
                    warning: 'exclamation-triangle text-warning', error: 'times-circle text-danger' };

    list.innerHTML = data.map(n => `
      <div class="notif-item">
        <i class="fas fa-${icons[n.type] || 'info-circle text-info'} flex-shrink-0"></i>
        <div>
          <div class="small">${n.message}</div>
          <div style="font-size:11px;color:var(--text-muted);">${n.time}</div>
        </div>
      </div>
    `).join('');
  } catch (e) { /* silent */ }
}

async function markAllRead() {
  await fetch('/api/notifications/mark-read', {
    method: 'POST',
    headers: { 'X-CSRFToken': getCSRF() }
  });
  document.getElementById('notifDot').style.display = 'none';
  document.getElementById('notifList').innerHTML =
    '<div class="text-center p-4 text-muted small">All notifications marked as read</div>';
}

// Load notifications when dropdown opens
document.addEventListener('DOMContentLoaded', function () {
  const notifBtn = document.getElementById('notifBtn');
  if (notifBtn) {
    notifBtn.addEventListener('click', loadNotifications);
    // Also poll every 30s
    loadNotifications();
    setInterval(loadNotifications, 30000);
  }
});

// ── CSRF Token Helper ─────────────────────────────────────────────────────────
function getCSRF() {
  const el = document.querySelector('[name=csrf_token]');
  if (el) return el.value;
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

// ── Tooltip Init ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const tooltips = document.querySelectorAll('[title]');
  tooltips.forEach(el => {
    new bootstrap.Tooltip(el, { trigger: 'hover', placement: 'top' });
  });
});

// ── Active nav link highlight ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-nav a').forEach(link => {
    if (link.getAttribute('href') && path.startsWith(link.getAttribute('href'))) {
      link.classList.add('active');
    }
  });
});
