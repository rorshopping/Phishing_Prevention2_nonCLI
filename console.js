/* PhishDefend AI — Operations Console
 * Concise dashboard + client setup wizard + deep-dive views.
 * Monitor everything · trigger everything.
 */
'use strict';

const $ = (sel) => document.querySelector(sel);

const state = {
  token: sessionStorage.getItem('ops_token') || '',
  autoRefresh: true,
  tab: 'dashboard',
  moreTab: 'campaigns',
  status: null,
  clients: [],
  campaigns: [],
  training: [],
  vishing: [],
  activity: [],
  setup: { step: 1, client: {}, employees: [], launched: null },
  refreshTimer: null,
};

/* ---------------- helpers ---------------- */

function esc(v) {
  return String(v == null ? '' : v).replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])
  );
}

function fmtDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d)) return '—';
  return d.toLocaleString([], { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function timeAgo(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  if (isNaN(d)) return '—';
  const s = Math.max(0, Math.floor((Date.now() - d.getTime()) / 1000));
  if (s < 60) return s + 's ago';
  const m = Math.floor(s / 60);
  if (m < 60) return m + 'm ago';
  const h = Math.floor(m / 60);
  if (h < 24) return h + 'h ago';
  return Math.floor(h / 24) + 'd ago';
}

function pct(part, total) {
  return total > 0 ? ((part / total) * 100).toFixed(1) : '0.0';
}

function statusBadge(status) {
  return `<span class="badge badge-${esc(status)}">${esc(status)}</span>`;
}

function toast(message, isError = false) {
  const t = $('#toast');
  t.textContent = message;
  t.className = 'toast show' + (isError ? ' error' : '');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 5000);
}

/* ---------------- API ---------------- */

async function api(path, opts = {}) {
  const headers = Object.assign({}, opts.headers || {});
  if (opts.body) headers['Content-Type'] = 'application/json';
  if (state.token) headers['Authorization'] = 'Bearer ' + state.token;
  const resp = await fetch(path, Object.assign({}, opts, { headers }));
  const text = await resp.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch (_) { data = text; }
  if (!resp.ok) {
    let msg = 'HTTP ' + resp.status;
    if (data && (data.detail || data.error)) {
      msg = typeof (data.detail || data.error) === 'string' ? data.detail || data.error : JSON.stringify(data.detail || data.error);
    }
    const err = new Error(msg);
    err.status = resp.status;
    throw err;
  }
  return data;
}

async function guarded(fn, fallback = null) {
  try { return await fn(); } catch (e) {
    if (e.status === 401) showTokenPrompt();
    return fallback;
  }
}

/* ---------------- modal ---------------- */

function openModal(title, bodyHtml, actionsHtml) {
  const root = $('#modal-root');
  root.innerHTML = `
    <div class="modal-backdrop">
      <div class="modal">
        <h3>${esc(title)}</h3>
        <div id="modal-body">${bodyHtml}</div>
        <div class="form-actions" id="modal-actions">${actionsHtml || ''}</div>
      </div>
    </div>`;
  root.querySelector('.modal-backdrop').addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-backdrop')) closeModal();
  });
  return root;
}

function closeModal() { $('#modal-root').innerHTML = ''; }

function modalResult(html, ok = true) {
  const body = $('#modal-body');
  body.insertAdjacentHTML('beforeend', `<div class="result-box ${ok ? 'ok' : 'err'}">${html}</div>`);
  const actions = $('#modal-actions');
  const btn = actions.querySelector('button[data-submit]');
  if (btn) { btn.disabled = false; btn.textContent = btn.dataset.submit; }
}

function setSubmitBusy(btn, label) {
  btn.disabled = true;
  btn.textContent = label || 'Working…';
}

/* ---------------- auth ---------------- */

function showTokenPrompt() {
  const wrap = $('#token-wrap');
  wrap.hidden = false;
  const input = $('#token-input');
  input.value = state.token;
  input.focus();
  toast('Ops token required', true);
}

/* ---------------- status + global stats ---------------- */

async function loadStatus() {
  const data = await guarded(() => api('/ops/status'));
  if (data) state.status = data;
  else if (!state.status) state.status = { health: { db: 'error', gophish: 'unreachable' }, scheduler: { running: false }, counts: {} };
  renderStatusPills();
  renderStatCards();
}

function renderStatusPills() {
  const st = state.status || {};
  const h = st.health || {};
  const s = st.scheduler || {};
  const db = h.db === 'connected' ? 'ok' : 'bad';
  const gp = h.gophish === 'reachable' ? 'ok' : 'bad';
  const sch = s.configured ? (s.running ? 'ok' : 'warn') : 'bad';
  $('#status-pills').innerHTML = `
    <span class="pill ${db}">DB · ${esc(h.db || 'unknown')}</span>
    <span class="pill ${gp}">Gophish · ${esc(h.gophish || 'unknown')}</span>
    <span class="pill ${sch}">Scheduler · ${s.running ? 'running' : s.configured ? 'stopped' : 'disabled'}</span>`;
}

function renderStatCards() {
  const c = (state.status && state.status.counts) || {};
  const cam = c.campaigns || {};
  const sent = c.emails_sent || 0;
  const clickRate = sent > 0 ? pct(c.clicks || 0, sent) : '0.0';
  const risk = (state.status && state.status.risk) || {};
  const cards = [
    ['Active clients', c.clients_active || 0, `of ${c.clients_total || 0} total`, 'accent'],
    ['Employees', c.employees_active || 0, `of ${c.employees_total || 0} total`, ''],
    ['Running campaigns', cam.running || 0, `${cam.scheduled || 0} scheduled`, cam.running ? 'warn' : ''],
    ['Emails sent', sent, `${c.clicks || 0} clicks`, ''],
    ['Click rate', clickRate + '%', `${c.fails || 0} creds submitted`, clickRate > 15 ? 'bad' : clickRate > 5 ? 'warn' : 'ok'],
    ['Pending training', c.pending_training || 0, 'assignments', (c.pending_training || 0) > 0 ? 'warn' : 'ok'],
  ];
  $('#stat-cards').innerHTML = cards.map(([label, value, hint, cls]) => `
    <div class="stat-card">
      <div class="label">${esc(label)}</div>
      <div class="value ${cls}">${esc(value)}</div>
      <div class="hint">${esc(hint)}</div>
    </div>`).join('');
}

/* ---------------- dashboard ---------------- */

function renderDashboard() {
  const st = state.status || {};
  const content = $('#content');

  const running = (st.running_campaigns || []).map((rc) => {
    const t = rc.totals || {};
    const total = t.sent || 0;
    const progress = `
      <div class="progress" title="opened ${t.opened} · clicked ${t.clicked} · creds ${t.credentials_submitted}">
        ${t.opened ? `<span class="seg-open" style="width:${pct(t.opened, total)}%"></span>` : ''}
        ${t.clicked ? `<span class="seg-click" style="width:${pct(t.clicked, total)}%"></span>` : ''}
        ${t.credentials_submitted ? `<span class="seg-fail" style="width:${pct(t.credentials_submitted, total)}%"></span>` : ''}
      </div>`;
    return `
      <tr>
        <td><a class="btn-link" onclick="openCampaignDetail('${rc.id}')">${esc(rc.name)}</a></td>
        <td>${esc(rc.client_name || '—')}</td>
        <td>${statusBadge('running')}</td>
        <td class="num">${total}</td>
        <td class="num">${t.opened || 0}</td>
        <td class="num">${t.clicked || 0}</td>
        <td class="num">${t.credentials_submitted || 0}</td>
        <td>${progress}</td>
        <td>
          <button class="btn-link" onclick="monitorCampaign('${rc.id}')">monitor</button>
          <button class="btn-link" onclick="cancelCampaign('${rc.id}')">cancel</button>
        </td>
      </tr>`;
  }).join('') || '<tr><td colspan="9" class="empty">No campaigns currently running — nothing to monitor</td></tr>';

  const activity = (st.recent_activity || []).slice(0, 8).map(activityItem).join('') ||
    '<div class="empty">No activity yet</div>';

  content.innerHTML = `
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Running campaigns</span>
        <span class="muted small">${(st.running_campaigns || []).length} active · avg risk ${esc((st.risk || {}).average_score || 0)}</span>
      </div>
      <div class="panel-body">
        <table>
          <thead><tr><th>Campaign</th><th>Client</th><th>Status</th><th>Sent</th><th>Opened</th><th>Clicked</th><th>Creds</th><th>Progress</th><th></th></tr></thead>
          <tbody>${running}</tbody>
        </table>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Recent activity</span>
        <button class="btn-link" onclick="switchTab('more'); setMoreTab('activity')">view all →</button>
      </div>
      <div class="panel-body">${activity}</div>
    </div>`;
}

function activityItem(a) {
  return `
    <div class="activity-item">
      <div class="activity-time">${timeAgo(a.created_at)}</div>
      <div>
        <div><span class="activity-action">${esc(a.action)}</span>
          ${a.client_name ? `<span class="muted"> · ${esc(a.client_name)}</span>` : ''}</div>
        ${a.details ? `<div class="activity-detail">${esc(JSON.stringify(a.details))}</div>` : ''}
      </div>
    </div>`;
}

/* ---------------- clients ---------------- */

async function loadClients() {
  const clients = await guarded(() => api('/clients'));
  if (!clients) return;
  const dashboards = await Promise.all(
    clients.map((c) => guarded(() => api('/clients/' + c.id + '/dashboard'), null))
  );
  state.clients = clients.map((c, i) => Object.assign({}, c, { dashboard: dashboards[i] }));
  renderClients();
}

function renderClients() {
  const content = $('#content');
  if (!state.clients.length) {
    content.innerHTML = `<div class="panel"><div class="panel-body"><div class="empty">No clients yet. Go to the <button class="btn-link" onclick="switchTab('setup')">Setup</button> tab to create one.</div></div></div>`;
    return;
  }
  content.innerHTML = state.clients.map((c) => {
    const d = c.dashboard;
    const s = (d && d.summary) || {};
    const risk = (d && d.risk) || {};
    const metrics = [
      ['Employees', s.total_employees || 0, ''],
      ['Campaigns', s.total_campaigns || 0, ''],
      ['Running', s.active_campaigns || 0, (s.active_campaigns || 0) ? 'warn' : ''],
      ['Click rate', (s.click_rate || 0) + '%', (s.click_rate || 0) >= 15 ? 'bad' : ''],
      ['Fail rate', (s.fail_rate || 0) + '%', (s.fail_rate || 0) >= 10 ? 'bad' : ''],
      ['Avg risk', risk.average_risk_score || 0, (risk.average_risk_score || 0) >= 40 ? 'bad' : (risk.average_risk_score || 0) >= 15 ? 'warn' : 'ok'],
      ['Pending training', s.pending_training || 0, (s.pending_training || 0) ? 'warn' : ''],
    ];
    return `
      <div class="client-card">
        <div class="client-head">
          <div>
            <h3 class="client-name">${esc(c.company_name)}</h3>
            <div class="client-meta">${esc(c.industry || '—')} · ${esc(c.country)} · ${esc(c.contact_email)}
              ${c.vishing_enabled ? ' · <span class="badge badge-running">vishing</span>' : ''}
              ${c.is_active ? '' : ' · <span class="badge badge-cancelled">inactive</span>'}</div>
          </div>
          <span class="faint small mono">${c.id.slice(0, 8)}</span>
        </div>
        <div class="client-metrics">
          ${metrics.map(([l, v, cls]) => `<div class="metric"><div class="m-label">${esc(l)}</div><div class="m-value ${cls}">${esc(v)}</div></div>`).join('')}
        </div>
        <div class="client-actions">
          <button class="btn btn-primary btn-sm" onclick="openTriggerModal('${c.id}')">Trigger campaign</button>
          <button class="btn btn-sm" onclick="openAddEmployees('${c.id}')">Add employees</button>
          <a class="btn btn-sm" href="/reports/client/${c.id}" target="_blank">Report</a>
          <a class="btn btn-sm" href="/reports/client/${c.id}/csv" target="_blank">CSV</a>
        </div>
      </div>`;
  }).join('');
}

/* ---------------- setup wizard ---------------- */

function renderSetup() {
  const content = $('#content');
  const st = state.setup;

  if (st.launched) {
    content.innerHTML = `
      <div class="panel">
        <div class="panel-body">
          <div class="success-panel">
            <div class="big">🎉</div>
            <h3>${esc(st.launched.client_name)} is set up and running</h3>
            <div class="sub">Campaign <span class="mono">${esc(st.launched.campaign_id)}</span> launched · ${st.launched.employees} employees · ${st.launched.email_mode} mode</div>
            <div class="flex" style="justify-content:center">
              <button class="btn btn-primary" onclick="switchTab('dashboard')">Go to dashboard</button>
              <button class="btn" onclick="resetSetup()">Setup another client</button>
            </div>
          </div>
        </div>
      </div>`;
    return;
  }

  const step = st.step;
  const chips = [
    ['1', 'Client details'],
    ['2', 'Employees'],
    ['3', 'Review & launch'],
  ].map(([n, label], i) => {
    const s = i + 1;
    const cls = s === step ? 'active' : s < step ? 'done' : '';
    const mark = s < step ? '✓' : n;
    return `<div class="step-chip ${cls}"><span class="num">${mark}</span> ${label}</div>`;
  }).join('');

  let body = '';
  let footer = '';

  if (step === 1) {
    body = `
      <div class="form-row"><label>Company name *</label><input id="s-name" value="${esc(st.client.name || '')}" placeholder="Acme GmbH"></div>
      <div class="form-row"><label>Contact email *</label><input id="s-email" type="email" value="${esc(st.client.email || '')}" placeholder="security@acme.de"></div>
      <div class="form-row inline">
        <div><label>Industry</label><input id="s-industry" value="${esc(st.client.industry || '')}" placeholder="Manufacturing"></div>
        <div><label>Country</label><input id="s-country" value="${esc(st.client.country || 'DE')}" maxlength="2"></div>
      </div>
      <div class="form-row inline">
        <div><label>Campaigns / year</label><input id="s-cpy" type="number" value="${st.client.cpy || 25}" min="1"></div>
        <div><label>Vishing calls</label>
          <select id="s-vishing">
            <option value="false" ${st.client.vishing === false ? 'selected' : ''}>disabled</option>
            <option value="true" ${st.client.vishing ? 'selected' : ''}>enabled</option>
          </select>
        </div>
      </div>`;
    footer = `
      <div class="right">
        <button class="btn btn-primary" id="s-next">Next: Employees →</button>
      </div>`;
  } else if (step === 2) {
    body = `
      <div class="form-row">
        <label>Employee emails (one per line)</label>
        <textarea id="s-employees" placeholder="max.mustermann@acme.de&#10;erika.muster@acme.de">${esc(st.employees.join('\n'))}</textarea>
      </div>
      <div class="emp-chips" id="s-emp-preview"></div>`;
    footer = `
      <div class="right">
        <button class="btn" id="s-back">← Back</button>
        <button class="btn btn-primary" id="s-next">Next: Review →</button>
      </div>`;
  } else if (step === 3) {
    const emps = st.employees;
    const clickHint = 'First campaign will be launched automatically.';
    body = `
      <div class="setup-summary">
        <div class="row"><span class="k">Client</span><span class="v">${esc(st.client.name)}</span></div>
        <div class="row"><span class="k">Contact</span><span class="v">${esc(st.client.email)}</span></div>
        <div class="row"><span class="k">Industry / country</span><span class="v">${esc(st.client.industry || '—')} / ${esc(st.client.country)}</span></div>
        <div class="row"><span class="k">Campaigns per year</span><span class="v">${st.client.cpy}</span></div>
        <div class="row"><span class="k">Vishing</span><span class="v">${st.client.vishing ? 'enabled' : 'disabled'}</span></div>
        <div class="row"><span class="k">Employees</span><span class="v">${emps.length}</span></div>
      </div>
      <div class="hr"></div>
      <div class="form-row inline">
        <div>
          <label>Difficulty</label>
          <select id="s-difficulty">
            <option value="easy">easy</option>
            <option value="medium" selected>medium</option>
            <option value="hard">hard</option>
          </select>
        </div>
        <div>
          <label>Email mode</label>
          <select id="s-mode">
            <option value="test" selected>test (safe aliases)</option>
            <option value="prod">prod (real addresses)</option>
          </select>
        </div>
      </div>
      <div class="check-row"><input type="checkbox" id="s-vishing-on" checked><label for="s-vishing-on">Trigger vishing calls after launch (if enabled for client)</label></div>
      <div class="result-box" style="display:none" id="s-result"></div>
      <div class="faint small mt">${clickHint}</div>`;
    footer = `
      <div class="right">
        <button class="btn" id="s-back">← Back</button>
        <button class="btn btn-launch" id="s-launch">Create client & launch →</button>
      </div>`;
  }

  content.innerHTML = `
    <div class="panel">
      <div class="panel-header"><span class="panel-title">New client setup</span></div>
      <div class="panel-body">
        <div class="stepper">${chips}</div>
        ${body}
        <div class="wizard-footer">${footer}</div>
      </div>
    </div>`;

  bindWizard(step);
}

function bindWizard(step) {
  const back = $('#s-back');
  if (back) back.addEventListener('click', () => { captureSetup(step); state.setup.step--; renderSetup(); });

  if (step === 1) {
    const fieldMap = {
      's-name': 'name', 's-email': 'email', 's-industry': 'industry',
      's-country': 'country', 's-cpy': 'cpy', 's-vishing': 'vishing',
    };
    Object.entries(fieldMap).forEach(([id, key]) => {
      const el = document.getElementById(id);
      if (!el) return;
      const sync = () => {
        const v = el.value;
        state.setup.client[key] = id === 's-vishing' ? v === 'true'
          : id === 's-cpy' ? (Number(v) || 25)
          : v.trim();
      };
      el.addEventListener('input', sync);
      el.addEventListener('change', sync);
    });
    $('#s-next').addEventListener('click', () => {
      captureSetup(1);
      const c = state.setup.client;
      if (!c.name || !c.email) { toast('Company name and contact email are required', true); return; }
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(c.email)) { toast('Enter a valid contact email', true); return; }
      state.setup.step = 2;
      renderSetup();
    });
  } else if (step === 2) {
    const ta = $('#s-employees');
    const preview = () => {
      state.setup.employees = ta.value.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
      $('#s-emp-preview').innerHTML = state.setup.employees.length
        ? state.setup.employees.map((e) => `<span class="emp-chip">${esc(e)}</span>`).join('')
        : '<span class="faint small">No emails yet</span>';
    };
    ta.addEventListener('input', preview);
    preview();
    $('#s-next').addEventListener('click', () => {
      captureSetup(2);
      if (!state.setup.employees.length) { toast('Add at least one employee email', true); return; }
      state.setup.step = 3;
      renderSetup();
    });
  } else if (step === 3) {
    $('#s-launch').addEventListener('click', launchSetup);
  }
}

function captureSetup(step) {
  const c = state.setup.client;
  if (step === 1) {
    c.name = $('#s-name').value.trim();
    c.email = $('#s-email').value.trim();
    c.industry = $('#s-industry').value.trim() || null;
    c.country = ($('#s-country').value.trim() || 'DE').toUpperCase();
    c.cpy = Number($('#s-cpy').value) || 25;
    c.vishing = $('#s-vishing').value === 'true';
  } else if (step === 2) {
    state.setup.employees = $('#s-employees').value.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  }
}

async function launchSetup() {
  const btn = $('#s-launch');
  const result = $('#s-result');
  result.style.display = 'block';
  result.className = 'result-box';
  result.textContent = 'Creating client…';
  setSubmitBusy(btn, 'Creating & launching…');
  try {
    const c = state.setup.client;
    const client = await api('/clients', {
      method: 'POST',
      body: JSON.stringify({
        company_name: c.name,
        contact_email: c.email,
        industry: c.industry,
        country: c.country,
        campaigns_per_year: c.cpy,
        vishing_enabled: c.vishing,
      }),
    });
    result.textContent = `Client created (${client.id}). Adding employees…`;
    await api('/clients/' + client.id + '/employees', {
      method: 'POST',
      body: JSON.stringify(state.setup.employees.map((email) => ({ email }))),
    });
    result.textContent = `${state.setup.employees.length} employees added. Launching campaign…`;
    const launch = await api('/ops/clients/' + client.id + '/campaign', {
      method: 'POST',
      body: JSON.stringify({
        difficulty: $('#s-difficulty').value,
        email_mode: $('#s-mode').value,
        vishing_enabled: $('#s-vishing-on').checked,
      }),
    });
    state.setup.launched = {
      client_name: c.name,
      client_id: client.id,
      campaign_id: launch.campaign_id,
      employees: state.setup.employees.length,
      email_mode: $('#s-mode').value,
    };
    toast('Client created and campaign launched');
    state.clients = [];
    await loadStatus();
    await loadClients();
    renderSetup();
  } catch (e) {
    result.className = 'result-box err';
    result.textContent = 'Setup failed: ' + e.message + '\n\nClient may have been partially created — check the Clients tab.';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create client & launch →';
  }
}

function resetSetup() {
  state.setup = { step: 1, client: {}, employees: [], launched: null };
  renderSetup();
}

/* ---------------- more tab ---------------- */

function renderMore() {
  const content = $('#content');
  const subtabs = [
    ['campaigns', 'Campaigns'],
    ['training', 'Training'],
    ['vishing', 'Vishing'],
    ['activity', 'Activity'],
  ];
  content.innerHTML = `
    <div class="subtab-nav">
      ${subtabs.map(([id, label]) => `<button class="subtab ${state.moreTab === id ? 'active' : ''}" data-more="${id}">${label}</button>`).join('')}
    </div>
    <div id="more-content"><div class="empty">Loading…</div></div>`;
  content.querySelectorAll('.subtab').forEach((b) => {
    b.addEventListener('click', () => { setMoreTab(b.dataset.more); });
  });
  loadMoreTab();
}

function setMoreTab(tab) {
  state.moreTab = tab;
  renderMore();
}

async function loadMoreTab() {
  const container = $('#more-content');
  if (!container) return;
  const fn = {
    campaigns: loadCampaignsInto,
    training: loadTrainingInto,
    vishing: loadVishingInto,
    activity: loadActivityInto,
  }[state.moreTab];
  if (fn) await fn(container);
}

/* ----- campaigns (more) ----- */

async function loadCampaignsInto(container) {
  const campaigns = await guarded(() => api('/ops/campaigns'));
  if (!campaigns) { container.innerHTML = '<div class="empty">Failed to load</div>'; return; }
  state.campaigns = campaigns;
  if (!campaigns.length) { container.innerHTML = '<div class="panel"><div class="panel-body"><div class="empty">No campaigns yet.</div></div></div>'; return; }
  const rows = campaigns.map((c) => {
    const total = c.sent_count || 0;
    const progress = `
      <div class="progress">
        ${c.click_count ? `<span class="seg-click" style="width:${pct(c.click_count, total)}%"></span>` : ''}
        ${c.fail_count ? `<span class="seg-fail" style="width:${pct(c.fail_count, total)}%"></span>` : ''}
      </div>`;
    const gids = (c.gophish_campaign_id || '').split(',').filter(Boolean).length;
    return `
      <tr>
        <td><a class="btn-link" onclick="openCampaignDetail('${c.id}')">${esc(c.name)}</a></td>
        <td>${esc(c.client_name || '—')}</td>
        <td>${statusBadge(c.status)}</td>
        <td>${esc(c.difficulty)}</td>
        <td class="faint small">${gids ? gids + ' gophish' : '—'}</td>
        <td class="num">${total}</td>
        <td class="num">${pct(c.click_count || 0, total)}%</td>
        <td class="num">${c.fail_count || 0}</td>
        <td>${progress}</td>
        <td class="faint small">${fmtDate(c.created_at)}</td>
        <td>
          <button class="btn-link" onclick="monitorCampaign('${c.id}')">monitor</button>
          ${c.status === 'running' || c.status === 'scheduled' ? `<button class="btn-link" onclick="cancelCampaign('${c.id}')">cancel</button>` : ''}
        </td>
      </tr>`;
  }).join('');
  container.innerHTML = `
    <div class="panel">
      <div class="panel-header"><span class="panel-title">All campaigns</span><span class="muted small">${campaigns.length} total</span></div>
      <div class="panel-body">
        <table>
          <thead><tr><th>Campaign</th><th>Client</th><th>Status</th><th>Difficulty</th><th>Gophish</th><th>Sent</th><th>Click %</th><th>Creds</th><th>Progress</th><th>Created</th><th></th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
}

/* ----- training (more) ----- */

async function loadTrainingInto(container) {
  const training = await guarded(() => api('/ops/training'));
  if (!training) { container.innerHTML = '<div class="empty">Failed to load</div>'; return; }
  state.training = training;
  const pending = training.filter((t) => t.status === 'pending').length;
  const completed = training.filter((t) => t.status === 'completed').length;
  const rows = training.map((t) => `
    <tr>
      <td class="mono small">${esc(t.employee)}</td>
      <td>${esc(t.client_name || '—')}</td>
      <td>${esc(t.training_type)}</td>
      <td><span class="badge badge-${t.status === 'completed' ? 'completed-t' : 'pending'}">${esc(t.status)}</span></td>
      <td class="num">${t.score_before != null ? t.score_before : '—'}</td>
      <td class="num">${t.score_after != null ? t.score_after : '—'}</td>
      <td class="faint small">${fmtDate(t.assigned_at)}</td>
      <td>${t.status === 'pending' ? `<button class="btn btn-sm" onclick="completeTraining('${t.id}')">Complete</button>` : '—'}</td>
    </tr>`).join('') || '<tr><td colspan="8" class="empty">No training assignments</td></tr>';
  container.innerHTML = `
    <div class="stat-cards" style="padding:0 0 14px">
      <div class="stat-card"><div class="label">Total</div><div class="value">${training.length}</div></div>
      <div class="stat-card"><div class="label">Pending</div><div class="value ${pending ? 'warn' : 'ok'}">${pending}</div></div>
      <div class="stat-card"><div class="label">Completed</div><div class="value ok">${completed}</div></div>
    </div>
    <div class="panel">
      <div class="panel-header"><span class="panel-title">Training assignments</span></div>
      <div class="panel-body">
        <table>
          <thead><tr><th>Employee</th><th>Client</th><th>Type</th><th>Status</th><th>Before</th><th>After</th><th>Assigned</th><th></th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
}

async function completeTraining(assignmentId) {
  const scoreStr = prompt('Score after training (0–100, optional):');
  if (scoreStr === null) return;
  const score = scoreStr.trim() === '' ? null : Math.max(0, Math.min(100, Number(scoreStr)));
  const body = {};
  if (score != null && !isNaN(score)) body.score_after = score;
  const res = await guarded(() => api('/training/' + assignmentId + '/complete', { method: 'POST', body: JSON.stringify(body) }));
  if (res) toast('Training marked complete');
  refreshCurrent();
}

/* ----- vishing (more) ----- */

async function loadVishingInto(container) {
  const sessions = await guarded(() => api('/ops/vishing'));
  if (!sessions) { container.innerHTML = '<div class="empty">Failed to load</div>'; return; }
  state.vishing = sessions;
  const rows = sessions.map((s) => `
    <tr>
      <td class="mono small">${esc(s.id.slice(0, 8))}</td>
      <td>${esc(s.client_name || '—')}</td>
      <td class="mono small">${esc(s.employee)}</td>
      <td>${statusBadge(s.status)}</td>
      <td class="num">${s.call_duration}s</td>
      <td>${s.sensitive_info_disclosed ? '⚠️ yes' : '—'}</td>
      <td class="faint small">${fmtDate(s.created_at)}</td>
    </tr>`).join('') || '<tr><td colspan="7" class="empty">No vishing sessions</td></tr>';
  container.innerHTML = `
    <div class="panel">
      <div class="panel-header"><span class="panel-title">Vishing sessions</span><span class="muted small">${sessions.length} total</span></div>
      <div class="panel-body">
        <table>
          <thead><tr><th>Session</th><th>Client</th><th>Employee</th><th>Status</th><th>Duration</th><th>Info disclosed</th><th>Created</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
}

/* ----- activity (more) ----- */

async function loadActivityInto(container) {
  const activity = await guarded(() => api('/ops/activity?limit=200'));
  if (!activity) { container.innerHTML = '<div class="empty">Failed to load</div>'; return; }
  state.activity = activity;
  container.innerHTML = `
    <div class="panel">
      <div class="panel-header"><span class="panel-title">Audit log</span><span class="muted small">${activity.length} events</span></div>
      <div class="panel-body">
        ${activity.map(activityItem).join('') || '<div class="empty">No activity yet</div>'}
      </div>
    </div>`;
}

/* ---------------- campaign detail / actions ---------------- */

async function openCampaignDetail(campaignId) {
  const data = await guarded(() => api('/campaigns/' + campaignId + '/results'));
  if (!data) return;
  const c = data.campaign;
  const results = data.results || [];
  const sent = results.length;
  const opened = results.filter((r) => r.email_opened).length;
  const clicked = results.filter((r) => r.link_clicked).length;
  const submitted = results.filter((r) => r.credentials_submitted).length;
  const reported = results.filter((r) => r.reported_phishing).length;

  const rows = results.map((r) => `
    <tr>
      <td class="mono small">${esc(r.email_hash ? r.email_hash.slice(0, 16) : r.employee_id.slice(0, 8))}</td>
      <td>${r.email_opened ? '✓' : '—'}</td>
      <td>${r.link_clicked ? '✓' : '—'}</td>
      <td class="${r.credentials_submitted ? 'bad' : ''}">${r.credentials_submitted ? '✓' : '—'}</td>
      <td>${r.reported_phishing ? '✓' : '—'}</td>
      <td class="faint small">${r.email_opened ? timeAgo(r.opened_at) : '—'}</td>
      <td class="faint small">${r.link_clicked ? timeAgo(r.clicked_at) : '—'}</td>
      <td>${r.training_completed ? '✓' : '—'}</td>
    </tr>`).join('') || '<tr><td colspan="8" class="empty">No results yet</td></tr>';

  const canCancel = c.status === 'running' || c.status === 'scheduled';
  openModal(`Campaign · ${c.name}`, `
    <div class="flex-between">
      <div class="flex">
        ${statusBadge(c.status)}
        <span class="badge badge-draft">${esc(c.difficulty)}</span>
      </div>
      <span class="faint small mono">${c.id.slice(0, 8)}</span>
    </div>
    <div class="campaign-metrics">
      <div class="metric"><div class="m-label">Sent</div><div class="m-value">${sent}</div></div>
      <div class="metric"><div class="m-label">Opened</div><div class="m-value">${opened} <span class="muted small">(${pct(opened, sent)}%)</span></div></div>
      <div class="metric"><div class="m-label">Clicked</div><div class="m-value">${clicked} <span class="muted small">(${pct(clicked, sent)}%)</span></div></div>
      <div class="metric"><div class="m-label">Creds submitted</div><div class="m-value">${submitted}</div></div>
      <div class="metric"><div class="m-label">Reported</div><div class="m-value">${reported}</div></div>
      <div class="metric"><div class="m-label">Created</div><div class="m-value small">${fmtDate(c.created_at)}</div></div>
    </div>
    <div class="flex" style="margin-bottom:8px">
      <a class="btn btn-sm" href="/reports/campaign/${c.id}" target="_blank">HTML report</a>
      <a class="btn btn-sm" href="/reports/campaign/${c.id}/csv" target="_blank">CSV</a>
      <button class="btn btn-sm" id="d-assign-training">Assign training (failures)</button>
      <button class="btn btn-sm" id="d-monitor">Monitor now</button>
      ${canCancel ? '<button class="btn btn-sm btn-danger" id="d-cancel">Cancel campaign</button>' : ''}
    </div>
    <div class="panel-title">Per-employee results</div>
    <table class="mt">
      <thead><tr><th>Employee</th><th>Opened</th><th>Clicked</th><th>Creds</th><th>Reported</th><th>Opened at</th><th>Clicked at</th><th>Trained</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`, `
    <button class="btn" onclick="closeModal()">Close</button>`);

  const root = $('#modal-root');
  root.querySelector('#d-monitor')?.addEventListener('click', async () => {
    const b = root.querySelector('#d-monitor');
    b.disabled = true;
    const res = await guarded(() => api('/ops/campaigns/' + campaignId + '/monitor', { method: 'POST' }));
    b.disabled = false;
    if (res) { modalResult(JSON.stringify(res, null, 2)); refreshCurrent(); }
  });
  root.querySelector('#d-assign-training')?.addEventListener('click', async () => {
    const b = root.querySelector('#d-assign-training');
    b.disabled = true;
    const res = await guarded(() => api('/training/campaign/' + campaignId + '/assign-all', { method: 'POST' }));
    b.disabled = false;
    if (res) { modalResult(`Assigned ${res.total} training assignments`, true); refreshCurrent(); }
  });
  root.querySelector('#d-cancel')?.addEventListener('click', async () => {
    if (!confirm('Cancel this campaign?')) return;
    const res = await guarded(() => api('/campaigns/' + campaignId + '/cancel', { method: 'POST' }));
    if (res) { modalResult('Campaign cancelled', true); refreshCurrent(); }
  });
}

async function monitorCampaign(campaignId) {
  const btn = event && event.currentTarget;
  if (btn) btn.disabled = true;
  const res = await guarded(() => api('/ops/campaigns/' + campaignId + '/monitor', { method: 'POST' }));
  if (btn) btn.disabled = false;
  if (res) toast('Monitored: sent=' + (res.sent ?? '—') + ' clicked=' + (res.clicked ?? '—'));
  refreshCurrent();
}

async function cancelCampaign(campaignId) {
  if (!confirm('Cancel this campaign?')) return;
  const res = await guarded(() => api('/campaigns/' + campaignId + '/cancel', { method: 'POST' }));
  if (res) toast('Campaign cancelled');
  refreshCurrent();
}

/* ---------------- trigger campaign / add employees ---------------- */

function openTriggerModal(clientId) {
  const clients = state.clients;
  const options = clients.length
    ? clients.map((c) => `<option value="${c.id}" ${c.id === clientId ? 'selected' : ''}>${esc(c.company_name)}</option>`).join('')
    : '<option value="">— no clients —</option>';

  openModal('Trigger phishing campaign', `
    <div class="form-row">
      <label>Client</label>
      <select id="t-client">${options}</select>
    </div>
    <div class="form-row inline">
      <div>
        <label>Difficulty</label>
        <select id="t-difficulty">
          <option value="easy">easy</option>
          <option value="medium" selected>medium</option>
          <option value="hard">hard</option>
        </select>
      </div>
      <div>
        <label>Email mode</label>
        <select id="t-mode">
          <option value="test" selected>test (aliases)</option>
          <option value="prod">prod (real addresses)</option>
        </select>
      </div>
    </div>
    <div class="check-row">
      <input type="checkbox" id="t-vishing" checked>
      <label for="t-vishing">Schedule vishing calls (if client enabled)</label>
    </div>
    <div class="result-box" style="display:none" id="t-result"></div>`, `
    <button class="btn" onclick="closeModal()">Cancel</button>
    <button class="btn btn-primary" data-submit="Launch campaign" id="t-submit">Launch campaign</button>`);

  $('#t-submit').addEventListener('click', async () => {
    const btn = $('#t-submit');
    const cid = $('#t-client').value;
    if (!cid) { toast('Select a client first', true); return; }
    const mode = $('#t-mode').value;
    setSubmitBusy(btn, 'Planning & launching…');
    try {
      const body = { difficulty: $('#t-difficulty').value, email_mode: mode, vishing_enabled: $('#t-vishing').checked };
      const res = await api(`/ops/clients/${cid}/campaign`, { method: 'POST', body: JSON.stringify(body) });
      const result = $('#t-result');
      result.style.display = 'block';
      result.className = 'result-box ok';
      result.textContent = `Campaign ${res.campaign_id}\nStatus: ${res.status}\nEmployees: ${res.employee_count}\nMode: ${mode}\nVishing: ${res.vishing_included}\n\nLaunched. Watch it on the Dashboard.`;
      refreshCurrent();
    } catch (e) {
      const result = $('#t-result');
      result.style.display = 'block';
      result.className = 'result-box err';
      result.textContent = 'Failed: ' + e.message;
    } finally {
      btn.disabled = false;
      btn.textContent = 'Launch campaign';
    }
  });
}

function openAddEmployees(clientId) {
  const client = state.clients.find((c) => c.id === clientId);
  openModal(`Add employees · ${client ? client.company_name : ''}`, `
    <div class="form-row">
      <label>Emails (one per line)</label>
      <textarea id="e-emails" placeholder="name@company.de"></textarea>
    </div>
    <div class="result-box" style="display:none" id="e-result"></div>`, `
    <button class="btn" onclick="closeModal()">Cancel</button>
    <button class="btn btn-primary" data-submit="Add employees" id="e-submit">Add employees</button>`);

  $('#e-submit').addEventListener('click', async () => {
    const btn = $('#e-submit');
    const emails = $('#e-emails').value.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
    if (!emails.length) { toast('Enter at least one email', true); return; }
    setSubmitBusy(btn, 'Adding…');
    try {
      const res = await api('/clients/' + clientId + '/employees', {
        method: 'POST',
        body: JSON.stringify(emails.map((email) => ({ email }))),
      });
      const result = $('#e-result');
      result.style.display = 'block';
      result.className = 'result-box ok';
      result.textContent = `Added ${res.length} employees.`;
      refreshCurrent();
    } catch (e) {
      const result = $('#e-result');
      result.style.display = 'block';
      result.className = 'result-box err';
      result.textContent = 'Failed: ' + e.message;
    } finally {
      btn.disabled = false;
      btn.textContent = 'Add employees';
    }
  });
}

/* ---------------- manual ops actions ---------------- */

async function runMonitorAll() {
  const btn = $('#btn-monitor');
  btn.disabled = true;
  btn.textContent = 'Monitoring…';
  try {
    const res = await api('/ops/monitor', { method: 'POST' });
    toast(`Monitored ${res.monitored} running campaign(s)`);
  } catch (e) {
    toast('Monitor failed: ' + e.message, true);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Monitor running';
    refreshCurrent();
  }
}

async function runScheduler() {
  const btn = $('#btn-scheduler');
  btn.disabled = true;
  btn.textContent = 'Running…';
  try {
    const res = await api('/ops/run-scheduler', { method: 'POST' });
    toast(`Scheduler pass done — ${res.campaigns} client(s) processed`);
  } catch (e) {
    toast('Scheduler failed: ' + e.message, true);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Run scheduler now';
    refreshCurrent();
  }
}

/* ---------------- tab management ---------------- */

const TAB_LOADERS = {
  dashboard: async () => { await loadStatus(); renderDashboard(); },
  clients: loadClients,
  setup: null, // rendered only on explicit tab switch — never during auto-refresh (preserves typing)
  more: renderMore,
};

async function switchTab(tab) {
  state.tab = tab;
  document.querySelectorAll('.tab').forEach((t) => t.classList.toggle('active', t.dataset.tab === tab));
  if (tab === 'setup') renderSetup();
  else await TAB_LOADERS[tab]();
  updateLastUpdated();
}

async function refreshCurrent() {
  await loadStatus();
  if (state.tab !== 'setup') {
    const loader = TAB_LOADERS[state.tab];
    if (loader) await loader();
  }
  updateLastUpdated();
}

function updateLastUpdated() {
  $('#last-updated').textContent = 'Updated ' + new Date().toLocaleTimeString();
}

/* ---------------- polling ---------------- */

function startTimer() {
  stopTimer();
  state.refreshTimer = setInterval(() => {
    if (state.autoRefresh && document.visibilityState === 'visible') {
      refreshCurrent();
    }
  }, 10000);
}

function stopTimer() {
  if (state.refreshTimer) clearInterval(state.refreshTimer);
  state.refreshTimer = null;
}

/* ---------------- bindings ---------------- */

function bindEvents() {
  $('#tabs').addEventListener('click', (e) => {
    const tab = e.target.closest('.tab');
    if (tab) switchTab(tab.dataset.tab);
  });
  $('#btn-refresh').addEventListener('click', refreshCurrent);
  $('#btn-monitor').addEventListener('click', runMonitorAll);
  $('#btn-scheduler').addEventListener('click', runScheduler);
  $('#btn-setup').addEventListener('click', () => switchTab('setup'));
  $('#token-apply').addEventListener('click', () => {
    state.token = $('#token-input').value.trim();
    sessionStorage.setItem('ops_token', state.token);
    $('#token-wrap').hidden = true;
    refreshCurrent();
  });

  $('#auto-refresh').addEventListener('change', (e) => {
    state.autoRefresh = e.target.checked;
    if (state.autoRefresh) startTimer();
    else stopTimer();
  });
}

/* ---------------- boot ---------------- */

async function boot() {
  try {
    const cfg = await api('/ops/config');
    if (cfg.auth_required) $('#token-wrap').hidden = false;
  } catch (_) { /* config endpoint is public; ignore */ }

  bindEvents();
  await refreshCurrent();
  if (state.autoRefresh) startTimer();
}

document.addEventListener('DOMContentLoaded', boot);
