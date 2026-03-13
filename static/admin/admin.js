/**
 * admin.js — Shared utilities for the Entertainment Hub Admin Portal
 * Included by all admin pages.
 */

// ── Auth Guard ────────────────────────────────────────────────────────────────
async function requireAdmin() {
  try {
    const res = await fetch('/api/admin/check');
    if (!res.ok) {
      window.location.href = '/admin/index.html';
      return;
    }
    const data = await res.json();
    // Set admin name in sidebar
    const el = document.getElementById('admin-name');
    const greet = document.getElementById('greeting');
    if (el)    el.textContent = `Logged in as: ${data.admin}`;
    if (greet) greet.textContent = data.admin;
  } catch {
    window.location.href = '/admin/index.html';
  }
}

// ── Fetch wrapper (adds JSON headers) ─────────────────────────────────────────
async function adminFetch(url, options = {}) {
  const defaults = {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
  };
  try {
    const res = await fetch(url, { ...defaults, ...options,
      headers: { ...defaults.headers, ...(options.headers || {}) } });
    if (res.status === 403 || res.status === 401) {
      window.location.href = '/admin/index.html';
      return null;
    }
    return res;
  } catch (err) {
    showToast('Network error: ' + err.message, 'error');
    return null;
  }
}

// ── Logout ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      await fetch('/api/admin/logout', { method: 'POST' });
      window.location.href = '/admin/index.html';
    });
  }
});

// ── Toast Notification ────────────────────────────────────────────────────────
function showToast(message, type = 'success') {
  // Remove existing toasts
  document.querySelectorAll('.toast').forEach(t => t.remove());

  const icon = type === 'success' ? 'bx-check-circle' : 'bx-error-circle';
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<i class='bx ${icon}'></i><span>${message}</span>`;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('leaving');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
