// ==========================================================================
// SUPER ADMIN JAVASCRIPT LOGIC
// ==========================================================================

let tenantsData = [];

document.addEventListener('DOMContentLoaded', () => {
  loadDashboardData();
  // Auto refresh every 30s
  setInterval(loadDashboardData, 30000);
});

async function loadDashboardData() {
  await Promise.all([
    fetchSuperAdminStats(),
    fetchTenants()
  ]);
}

// 1. Fetch Stats
async function fetchSuperAdminStats() {
  try {
    const res = await fetch('/api/superadmin/stats');
    const data = await res.json();
    if (data.success && data.stats) {
      document.getElementById('stat-total-tenants').textContent = data.stats.total_tenants || 0;
      document.getElementById('stat-active-bots').textContent = data.stats.active_tenants || 0;
      document.getElementById('stat-total-orders').textContent = data.stats.total_orders || 0;
      document.getElementById('stat-total-revenue').textContent = formatPrice(data.stats.total_revenue || 0);
    }
  } catch (err) {
    console.error("Error fetching stats:", err);
  }
}

// 2. Fetch Tenants
async function fetchTenants() {
  try {
    const res = await fetch('/api/superadmin/tenants');
    const data = await res.json();
    if (data.success) {
      tenantsData = data.tenants || [];
      renderTenantsTable(tenantsData);
    }
  } catch (err) {
    console.error("Error fetching tenants:", err);
  }
}

function renderTenantsTable(list) {
  const tbody = document.getElementById('tenants-tbody');
  const countBadge = document.getElementById('tenants-count-badge');
  if (countBadge) countBadge.textContent = `${list.length} ta`;

  if (!list || list.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: 40px; color: var(--text-muted);">
          Birorta ham oshxona topilmadi. Yuqoridagi "Yangi Oshxona Qo'shish" tugmasini bosing.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = list.map(t => {
    const initials = t.name.slice(0, 2).toUpperCase();
    const botLink = t.bot_username 
      ? `<a href="https://t.me/${t.bot_username.replace('@', '')}" target="_blank" class="bot-tag">
           <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .37z"/></svg>
           <span>@${t.bot_username.replace('@', '')}</span>
         </a>`
      : `<span style="color: var(--text-muted); font-size: 12px;">Token: ${t.bot_token_masked}</span>`;

    const statusBadge = t.is_active
      ? `<span class="status-pill active"><span class="pulse-dot" style="width: 6px; height: 6px;"></span> Faol</span>`
      : `<span class="status-pill inactive">To'xtatilgan</span>`;

    return `
      <tr>
        <td style="font-weight: 700; color: var(--gold-light);">#${t.id}</td>
        <td>
          <div class="tenant-brand-cell">
            <div class="tenant-avatar">${initials}</div>
            <div>
              <div class="tenant-name-text">${t.name}</div>
              <div class="tenant-slug-text">slug: <code>${t.slug}</code></div>
            </div>
          </div>
        </td>
        <td>${botLink}</td>
        <td>
          <div class="credentials-box">
            <div class="cred-row">
              <span class="cred-label">Login:</span>
              <span class="cred-val">${t.admin_username}</span>
            </div>
          </div>
        </td>
        <td>
          <span style="font-family: monospace; font-size: 12px; color: var(--text-muted);">${t.admin_telegram_id || '—'}</span>
        </td>
        <td>
          <div style="font-weight: 700; color: var(--text-main);">${t.orders_count} ta</div>
          <div style="font-size: 11.5px; color: #10B981; font-weight: 600;">${formatPrice(t.total_revenue)}</div>
        </td>
        <td>${statusBadge}</td>
        <td>
          <div class="actions-cell">
            <button class="btn-action impersonate" onclick="impersonateTenant(${t.id})" title="Ushbu oshxona admin paneliga kirish">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>
              <span>Panel</span>
            </button>
            <button class="btn-action" onclick="toggleTenantStatus(${t.id})" title="${t.is_active ? 'To\'xtatish' : 'Faollashtirish'}">
              ${t.is_active ? '⏸️' : '▶️'}
            </button>
            ${t.id !== 1 ? `
              <button class="btn-action danger" onclick="deleteTenant(${t.id}, '${t.name}')" title="O'chirish">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
              </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

// 3. Search Filter
function filterTenants() {
  const query = document.getElementById('search-input').value.toLowerCase().trim();
  if (!query) {
    renderTenantsTable(tenantsData);
    return;
  }
  const filtered = tenantsData.filter(t => 
    t.name.toLowerCase().includes(query) || 
    t.slug.toLowerCase().includes(query) || 
    (t.bot_username && t.bot_username.toLowerCase().includes(query)) ||
    t.admin_username.toLowerCase().includes(query)
  );
  renderTenantsTable(filtered);
}

// 4. Modal Operations
function openCreateTenantModal() {
  document.getElementById('edit-tenant-id').value = '';
  document.getElementById('tenant-name').value = '';
  document.getElementById('tenant-slug').value = '';
  document.getElementById('tenant-bot-token').value = '';
  document.getElementById('tenant-admin-id').value = '';
  document.getElementById('tenant-username').value = '';
  document.getElementById('tenant-password').value = '';
  document.getElementById('bot-verify-result').style.display = 'none';
  document.getElementById('clone-menu-wrap').style.display = 'block';
  document.getElementById('modal-title-text').textContent = "Yangi Oshxona Qo'shish";
  document.getElementById('save-btn-text').textContent = "Saqlash & Botni Ishga Tushirish";
  
  generateRandomPassword();
  document.getElementById('create-modal-overlay').classList.add('active');
}

function closeCreateTenantModal() {
  document.getElementById('create-modal-overlay').classList.remove('active');
}

function autoGenerateSlug(name) {
  const slugInput = document.getElementById('tenant-slug');
  const userAdminInput = document.getElementById('tenant-username');
  if (!document.getElementById('edit-tenant-id').value) {
    const slug = name.toLowerCase()
      .replace(/[^a-z0-9]/g, '')
      .slice(0, 20);
    slugInput.value = slug;
    if (slug) {
      userAdminInput.value = `${slug}_admin`;
    }
  }
}

function generateRandomPassword() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";
  let pwd = "";
  for (let i = 0; i < 8; i++) {
    pwd += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  document.getElementById('tenant-password').value = pwd;
}

// 5. Verify Bot Token live via Telegram
async function verifyBotToken() {
  const token = document.getElementById('tenant-bot-token').value.trim();
  const resBox = document.getElementById('bot-verify-result');
  if (!token) {
    showToast("Bot tokenini kiriting!", "error");
    return;
  }

  resBox.className = "verify-status-box";
  resBox.style.display = "block";
  resBox.textContent = "Telegram API tekshirilmoqda...";

  try {
    const res = await fetch('/api/superadmin/verify-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    });
    const data = await res.json();
    if (data.success && data.bot) {
      resBox.className = "verify-status-box success";
      resBox.innerHTML = `✓ Bot topildi: <strong>@${data.bot.username}</strong> (${data.bot.first_name})`;
    } else {
      resBox.className = "verify-status-box error";
      resBox.textContent = "✗ " + (data.error || "Yaroqsiz bot token!");
    }
  } catch (err) {
    resBox.className = "verify-status-box error";
    resBox.textContent = "✗ Tekshirishda server xatoligi yuz berdi!";
  }
}

// 6. Save Tenant (Create)
async function handleSaveTenant(e) {
  e.preventDefault();
  const name = document.getElementById('tenant-name').value.trim();
  const slug = document.getElementById('tenant-slug').value.trim().toLowerCase();
  const bot_token = document.getElementById('tenant-bot-token').value.trim();
  const admin_telegram_id = document.getElementById('tenant-admin-id').value.trim();
  const admin_username = document.getElementById('tenant-username').value.trim();
  const admin_password = document.getElementById('tenant-password').value.trim();
  const clone_menu = document.getElementById('tenant-clone-menu').checked;

  const btn = document.getElementById('btn-save-tenant');
  const btnText = document.getElementById('save-btn-text');

  btn.disabled = true;
  btnText.textContent = "Ishga tushirilmoqda...";

  try {
    const res = await fetch('/api/superadmin/tenants/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        slug,
        bot_token,
        admin_telegram_id,
        admin_username,
        admin_password,
        clone_menu
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`"${name}" muvaffaqiyatli yaratildi va bot ishga tushirildi!`, "success");
      closeCreateTenantModal();
      loadDashboardData();
    } else {
      showToast(data.error || "Xatolik yuz berdi", "error");
    }
  } catch (err) {
    showToast("Server bilan bog'lanishda xatolik!", "error");
  } finally {
    btn.disabled = false;
    btnText.textContent = "Saqlash & Botni Ishga Tushirish";
  }
}

// 7. Toggle status
async function toggleTenantStatus(id) {
  try {
    const res = await fetch(`/api/superadmin/tenants/${id}/toggle`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(data.is_active ? "Oshxona va bot faollashtirildi!" : "Oshxona va bot to'xtatildi!", "success");
      loadDashboardData();
    } else {
      showToast(data.error || "Xatolik", "error");
    }
  } catch (e) {
    showToast("Xatolik", "error");
  }
}

// 8. Impersonate Tenant
async function impersonateTenant(id) {
  try {
    const res = await fetch(`/api/superadmin/tenants/${id}/impersonate`, { method: 'POST' });
    const data = await res.json();
    if (data.success && data.redirect) {
      window.location.href = data.redirect;
    }
  } catch (e) {
    showToast("Kirishda xatolik!", "error");
  }
}

// 9. Delete Tenant
async function deleteTenant(id, name) {
  if (!confirm(`"${name}" oshxonasini va barcha ma'lumotlarini o'chirishni tasdiqlaysizmi?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/superadmin/tenants/${id}/delete`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast("Oshxona o'chirildi!", "success");
      loadDashboardData();
    } else {
      showToast(data.error || "O'chirishda xatolik!", "error");
    }
  } catch (e) {
    showToast("Server xatoligi!", "error");
  }
}

// Utility Helpers
function formatPrice(val) {
  if (!val) return "0 so'm";
  return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " so'm";
}

function showToast(msg, type = "success") {
  const c = document.getElementById('toast-container');
  if (!c) return;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}
