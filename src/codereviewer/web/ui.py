INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CodeReviewer Flow Console</title>
  <link rel="icon" href="/static/favicon.svg" type="image/svg+xml" />
  <style>
    :root {
      --bg: #f4f7fb;
      --panel: #ffffff;
      --ink: #18212f;
      --muted: #607089;
      --line: #dbe3ef;
      --brand: #0d6efd;
      --brand-soft: #e9f2ff;
      --ok: #198754;
      --warn: #fd7e14;
      --danger: #dc3545;
      --radius: 12px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: radial-gradient(circle at 0% 0%, #eff6ff 0, var(--bg) 38%), var(--bg);
      color: var(--ink);
      font-family: "Segoe UI", "Inter", Arial, sans-serif;
    }
    .shell { max-width: 1280px; margin: 0 auto; padding: 1.25rem; }
    .top {
      display: grid;
      grid-template-columns: 1.6fr 1fr;
      gap: 1rem;
      align-items: stretch;
      margin-bottom: 1rem;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: 0 8px 24px rgba(20, 45, 93, 0.05);
    }
    .hero { padding: 1rem 1.15rem; display: flex; gap: .9rem; align-items: center; }
    .hero h1 { margin: 0; font-size: 1.45rem; }
    .hero p { margin: .25rem 0 0 0; color: var(--muted); }
    .logo { width: 46px; height: 46px; }
    .stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(120px, 1fr));
      gap: .6rem;
      padding: .85rem 1rem 1rem;
    }
    .stat {
      background: linear-gradient(160deg, #fff 0%, #f8fbff 100%);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: .6rem .7rem;
    }
    .stat small { color: var(--muted); display: block; }
    .stat strong { font-size: 1.15rem; }
    .actions { padding: 1rem; display: grid; gap: .55rem; }
    .actions button {
      background: var(--brand);
      color: #fff;
      border: none;
      border-radius: 10px;
      padding: .6rem .8rem;
      cursor: pointer;
      font-weight: 600;
    }
    .actions button.secondary { background: #4f637d; }
    .actions a { color: var(--brand); text-decoration: none; font-size: .92rem; }
    .grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 1rem; margin-bottom: 1rem; }
    .section { padding: .95rem 1rem 1rem; }
    .section h2 { margin: 0 0 .6rem 0; font-size: 1rem; }
    .hint { color: var(--muted); font-size: .88rem; margin: 0 0 .7rem; }

    .flow-wrap { overflow: auto; border: 1px dashed var(--line); border-radius: 10px; padding: .7rem; background: #fcfdff; }
    svg text { font-size: 12px; fill: #233247; }
    .node-main { fill: #e8f2ff; stroke: #5b9cff; stroke-width: 1.2; }
    .node-sub { fill: #f3fff6; stroke: #63bb7f; stroke-width: 1.2; }
    .edge { stroke: #8aa3c2; stroke-width: 1.2; marker-end: url(#arrow); }

    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: .48rem .42rem; border-bottom: 1px solid var(--line); font-size: .9rem; }
    th { color: var(--muted); font-size: .78rem; text-transform: uppercase; letter-spacing: .03em; }
    .pill { display: inline-block; border-radius: 999px; padding: .14rem .45rem; font-size: .74rem; font-weight: 700; }
    .p-ok { background: #e7f7ed; color: var(--ok); }
    .p-run { background: #eef4ff; color: #2552a7; }
    .p-warn { background: #fff2e7; color: var(--warn); }

    .timeline { position: relative; margin: .35rem 0 0; padding-left: 1rem; }
    .timeline:before { content: ''; position: absolute; left: 4px; top: 0; bottom: 0; width: 2px; background: var(--line); }
    .t-item { position: relative; padding: 0 0 .8rem .85rem; }
    .t-item:before { content: ''; position: absolute; left: -1px; top: 3px; width: 10px; height: 10px; border-radius: 50%; background: var(--brand); }
    .t-item .meta { color: var(--muted); font-size: .8rem; }

    .controls { display: grid; grid-template-columns: 1fr 1fr; gap: .7rem; margin-top: .7rem; }
    form { border: 1px solid var(--line); border-radius: 10px; padding: .65rem; background: #fbfdff; }
    label { font-size: .79rem; color: var(--muted); display: block; margin-bottom: .2rem; }
    input, select, textarea, button {
      width: 100%; padding: .5rem .55rem; border-radius: 8px; border: 1px solid #cfd9e7; font: inherit;
    }
    textarea { min-height: 90px; resize: vertical; }
    form button { margin-top: .5rem; background: #1f6feb; color: #fff; border: none; font-weight: 600; cursor: pointer; }
    pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; }
    #output { max-height: 240px; overflow: auto; background: #0f1b2d; color: #d8e5ff; border-radius: 10px; padding: .8rem; }

    @media (max-width: 980px) {
      .top, .grid { grid-template-columns: 1fr; }
      .stats { grid-template-columns: repeat(2, minmax(130px, 1fr)); }
      .controls { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="top">
      <article class="panel">
        <div class="hero">
          <img class="logo" src="/static/logo.svg" alt="CodeReviewer logo" />
          <div>
            <h1>Agent Flow Console</h1>
            <p>Observe primary and subagent execution flows, decision logs, and model/profile versions in one surface.</p>
          </div>
        </div>
        <div class="stats" id="stats"></div>
      </article>
      <aside class="panel actions">
        <button id="refresh">Refresh Telemetry</button>
        <button class="secondary" id="seed-demo">Seed Demo Flow</button>
        <a href="/">Back to landing</a>
        <a href="/api/reviews">API: /api/reviews</a>
      </aside>
    </section>

    <section class="grid">
      <article class="panel section">
        <h2>Flow Graph</h2>
        <p class="hint">Main review jobs and inferred subagent stages (analyze, test, package, deploy-check).</p>
        <div class="flow-wrap">
          <svg id="flow-svg" width="100%" height="360" viewBox="0 0 1000 360" preserveAspectRatio="xMinYMin meet"></svg>
        </div>
      </article>

      <article class="panel section">
        <h2>Version Timeline</h2>
        <p class="hint">Runtime profiles and model versions configured for this tenant.</p>
        <div id="timeline" class="timeline"></div>
      </article>
    </section>

    <section class="grid">
      <article class="panel section">
        <h2>Decision Logs</h2>
        <p class="hint">Recent events synthesized from review history and feedback records.</p>
        <div style="overflow:auto; max-height:320px;">
          <table>
            <thead><tr><th>Trace</th><th>Agent</th><th>Stage</th><th>Status</th><th>Version</th><th>When</th></tr></thead>
            <tbody id="log-rows"></tbody>
          </table>
        </div>
      </article>

      <article class="panel section">
        <h2>Ops Console</h2>
        <p class="hint">Keep existing profile/review operations available from the same screen.</p>
        <div class="controls">
          <form id="profile-form">
            <label>Profile name</label><input id="name" placeholder="e.g. reviewer-main" required />
            <label>Provider</label><select id="provider"></select>
            <label>Model</label><select id="model" required></select>
            <label>Auth ref</label><input id="auth" placeholder="vault://path#key" required />
            <button type="submit">Save Profile</button>
          </form>

          <form id="review-form">
            <label>Repository</label><input id="repo" placeholder="agentnxt/code-reviewer" required />
            <label>Runtime profile</label><select id="profile-id" required></select>
            <label>Patch (unified diff)</label><textarea id="patch" placeholder="@@ ..."></textarea>
            <button type="submit">Run Review</button>
          </form>
        </div>
      </article>
    </section>

    <section class="panel section">
      <h2>Agent Chat</h2>
      <p class="hint">Each agent has its own chat panel for cleaner execution and tracking.</p>
      <div id="agent-panels" class="controls" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));"></div>
      <pre id="chat-output" style="margin-top:.6rem;background:#f8fbff;border:1px solid #dbe3ef;border-radius:10px;padding:.7rem"></pre>
    </section>

    <section class="panel section">
      <h2>Output</h2>
      <pre id="output"></pre>
    </section>
  </div>

<script>
const output = document.getElementById('output');
const stats = document.getElementById('stats');
const timeline = document.getElementById('timeline');
const logRows = document.getElementById('log-rows');
const flowSvg = document.getElementById('flow-svg');
const chatOutput = document.getElementById('chat-output');
const agentPanels = document.getElementById('agent-panels');

let appConfig = null;
let reviewJobs = [];

const fmt = (iso) => {
  if (!iso) return '-';
  const d = new Date(iso);
  return isNaN(d) ? iso : d.toLocaleString();
};

const short = (v, n=8) => (v || '').toString().slice(0, n);
const randId = () => Math.random().toString(36).slice(2, 10);

function pill(status) {
  const map = {
    completed: ['p-ok', 'completed'],
    success: ['p-ok', 'success'],
    running: ['p-run', 'running'],
    queued: ['p-run', 'queued'],
    failed: ['p-warn', 'failed'],
    pending: ['p-warn', 'pending']
  };
  const [klass, label] = map[(status || '').toLowerCase()] || ['p-run', status || 'unknown'];
  return `<span class="pill ${klass}">${label}</span>`;
}

function renderStats() {
  const profiles = appConfig?.runtime?.profiles || [];
  const models = appConfig?.runtime?.models || [];
  const latest = reviewJobs[0];
  const cards = [
    ['Reviews', reviewJobs.length],
    ['Runtime Profiles', profiles.length],
    ['Model Catalog', models.length],
    ['Last Job', latest ? short(latest.id) : 'none']
  ];
  stats.innerHTML = cards.map(([k, v]) => `<div class="stat"><small>${k}</small><strong>${v}</strong></div>`).join('');
}

function ensureDemoData() {
  if (reviewJobs.length) return;
  const now = Date.now();
  reviewJobs = [
    {id:`job_${randId()}`, status:'completed', created_at:new Date(now-3600e3).toISOString(), runtime_profile_id:'demo-v3', agent_id:'agent.reviewer.lead', repository:{name:'agentnxt/code-reviewer'}},
    {id:`job_${randId()}`, status:'running', created_at:new Date(now-1200e3).toISOString(), runtime_profile_id:'demo-v4', agent_id:'agent.reviewer.ops', repository:{name:'openautonomyx/common-instructions'}},
  ];
}

function renderFlow() {
  ensureDemoData();
  const width = 1000;
  const laneY = [60, 160, 260];
  const stages = ['analyze', 'test', 'package', 'deploy-check'];
  const stageX = [290, 470, 650, 830];

  let content = `
    <defs>
      <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
        <path d="M0,0 L8,4 L0,8 z" fill="#8aa3c2"></path>
      </marker>
    </defs>`;

  reviewJobs.slice(0,3).forEach((job, i) => {
    const y = laneY[i % laneY.length];
    content += `<rect class="node-main" x="28" y="${y-24}" rx="10" ry="10" width="200" height="48"></rect>`;
    content += `<text x="40" y="${y-2}">Main: ${short(job.id, 12)} (${job.status})</text>`;

    let prevX = 228;
    stages.forEach((stg, idx) => {
      const x = stageX[idx];
      content += `<line class="edge" x1="${prevX}" y1="${y}" x2="${x-8}" y2="${y}"></line>`;
      content += `<rect class="node-sub" x="${x}" y="${y-20}" rx="9" ry="9" width="130" height="40"></rect>`;
      content += `<text x="${x+12}" y="${y+4}">${stg}</text>`;
      prevX = x + 130;
    });
  });

  flowSvg.innerHTML = content;
}

function renderTimeline() {
  const profiles = [...(appConfig?.runtime?.profiles || [])];
  const models = appConfig?.runtime?.models || [];
  timeline.innerHTML = '';

  if (!profiles.length) {
    timeline.innerHTML = '<div class="t-item"><div><strong>demo-v4</strong></div><div class="meta">anthropic/claude-sonnet-4 · default</div></div>';
    return;
  }

  profiles.sort((a,b) => (a.updated_at || '').localeCompare(b.updated_at || ''));
  profiles.forEach((p, idx) => {
    const model = models.find(m => m.model_id === p.model_id);
    const item = document.createElement('div');
    item.className = 't-item';
    item.innerHTML = `
      <div><strong>${p.name || p.id || `profile-${idx+1}`}</strong></div>
      <div class="meta">${p.provider}/${p.model_id}${p.is_default ? ' · default' : ''}</div>
      <div class="meta">${model?.display_name || 'runtime model'}${model?.version ? ` · v${model.version}` : ''}</div>`;
    timeline.appendChild(item);
  });
}

function stageRowsFromJob(job) {
  const trace = short(job.id, 8);
  const baseVersion = job.runtime_profile_id || 'v-runtime';
  const agent = job.agent_id || 'agent.reviewer';
  const when = job.created_at || new Date().toISOString();
  return [
    ['analyze', 'success'],
    ['test', job.status === 'failed' ? 'failed' : 'success'],
    ['package', job.status === 'running' ? 'running' : 'success'],
    ['deploy-check', job.status === 'queued' ? 'queued' : (job.status === 'running' ? 'running' : 'pending')],
  ].map(([stage, status]) => ({trace, agent, stage, status, version: baseVersion, when}));
}

function renderLogs() {
  const rows = reviewJobs.flatMap(stageRowsFromJob).slice(0, 40);
  logRows.innerHTML = rows.map(r => `
    <tr>
      <td>${r.trace}</td>
      <td>${r.agent}</td>
      <td>${r.stage}</td>
      <td>${pill(r.status)}</td>
      <td>${r.version}</td>
      <td>${fmt(r.when)}</td>
    </tr>`).join('');
}

function setOptions(select, options, placeholder) {
  select.textContent = '';
  if (placeholder) {
    const option = document.createElement('option');
    option.value = '';
    option.textContent = placeholder;
    select.appendChild(option);
  }
  options.forEach(({value, label}) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = label;
    select.appendChild(option);
  });
}

function updateModelOptions() {
  const provider = document.getElementById('provider').value;
  const models = (appConfig?.runtime?.models || [])
    .filter(m => m.provider === provider && m.enabled)
    .map(m => ({value: m.model_id, label: `${m.display_name} (${m.model_id})`}));
  setOptions(document.getElementById('model'), models, 'Select model');
}

function renderRuntimeControls() {
  setOptions(document.getElementById('provider'), (appConfig.runtime.providers || []).map(p => ({value:p, label:p})), null);
  updateModelOptions();
  setOptions(
    document.getElementById('profile-id'),
    (appConfig.runtime.profiles || []).map(p => ({ value: p.id, label: `${p.is_default ? '* ' : ''}${p.name} - ${p.provider}/${p.model_id}` })),
    'Select runtime profile'
  );
}

async function loadConfig() {
  const res = await fetch('/api/config');
  const body = await res.json();
  if (!res.ok) throw new Error(body.detail || 'failed to load config');
  appConfig = body;
  renderRuntimeControls();
}

async function loadReviews() {
  const res = await fetch('/api/reviews');
  const body = await res.json();
  if (!res.ok) throw new Error(body.detail || 'failed to load reviews');
  reviewJobs = body || [];
}

async function refreshAll() {
  try {
    await Promise.all([loadConfig(), loadReviews()]);
    renderStats();
    renderFlow();
    renderTimeline();
    renderLogs();
    output.textContent = 'Refreshed flow console.';
  } catch (err) {
    output.textContent = `Error: ${err.message}`;
  }
}

document.getElementById('refresh').addEventListener('click', refreshAll);
document.getElementById('provider').addEventListener('change', updateModelOptions);
document.getElementById('seed-demo').addEventListener('click', () => {
  reviewJobs = [];
  ensureDemoData();
  renderStats();
  renderFlow();
  renderTimeline();
  renderLogs();
  output.textContent = 'Seeded demo flow.';
});

document.getElementById('profile-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    name: document.getElementById('name').value,
    provider: document.getElementById('provider').value,
    model_id: document.getElementById('model').value,
    auth_reference: document.getElementById('auth').value,
    is_default: true
  };
  const res = await fetch('/api/runtime-profiles', {
    method: 'POST', headers: {'content-type': 'application/json'}, body: JSON.stringify(payload)
  });
  const body = await res.json();
  if (!res.ok) return (output.textContent = `Error: ${body.detail || 'Failed to save profile'}`);
  output.textContent = JSON.stringify(body, null, 2);
  await refreshAll();
});

document.getElementById('review-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const patch = document.getElementById('patch').value;
  if (!patch.includes('+')) return (output.textContent = 'Error: Patch must include added lines to review.');
  const payload = {
    repository: {name: document.getElementById('repo').value, branch: 'main'},
    runtime_profile_id: document.getElementById('profile-id').value,
    changes: [{path: 'sample.py', change_type: 'modified', patch}]
  };
  const res = await fetch('/api/reviews', {
    method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload)
  });
  const body = await res.json();
  if (!res.ok) return (output.textContent = `Error: ${body.detail || 'Failed to submit review'}`);
  output.textContent = JSON.stringify(body, null, 2);
  await refreshAll();
});



function agentStatusPill(active) {
  return active ? '<span class="pill p-ok">active</span>' : '<span class="pill p-warn">disabled</span>';
}

async function sendAgentMessage(agentName, message, outputEl) {
  const res = await fetch('/api/agents/chat', {
    method: 'POST', headers: {'content-type':'application/json'}, body: JSON.stringify({agent_name: agentName, message})
  });
  const body = await res.json();
  if (!res.ok) {
    outputEl.textContent = `Error: ${body.detail || 'chat failed'}`;
    return;
  }
  outputEl.textContent = body.response;
}

function renderAgentPanels(states) {
  agentPanels.innerHTML = '';
  states.forEach((st) => {
    const card = document.createElement('form');
    card.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem;">
        <strong>${st.agent_name}</strong>
        ${agentStatusPill(st.active)}
      </div>
      <label>Message</label>
      <input name="message" placeholder="task for ${st.agent_name}" ${st.active ? '' : 'disabled'} required />
      <button type="submit" ${st.active ? '' : 'disabled'}>Send</button>
      <pre style="margin-top:.5rem;background:#f8fbff;border:1px solid #dbe3ef;border-radius:8px;padding:.5rem;min-height:56px"></pre>
    `;
    const msgInput = card.querySelector('input[name="message"]');
    const out = card.querySelector('pre');
    card.addEventListener('submit', async (e) => {
      e.preventDefault();
      await sendAgentMessage(st.agent_name, msgInput.value, out);
    });
    agentPanels.appendChild(card);
  });
}

async function initAgents() {
  const spawnRes = await fetch('/api/agents/spawn-all', {method: 'POST'});
  const spawnBody = await spawnRes.json();
  if (!spawnRes.ok) throw new Error(spawnBody.detail || 'failed to spawn agents');

  const stateRes = await fetch('/api/agents/state');
  const stateBody = await stateRes.json();
  if (!stateRes.ok) throw new Error(stateBody.detail || 'failed to load agent state');

  renderAgentPanels(stateBody.agents || []);
  chatOutput.textContent = `Agents loaded: ${(spawnBody.agents || []).join(', ')}\nMax idle seconds: ${stateBody.max_idle_seconds}`;
}

refreshAll();
initAgents();
</script>
</body>
</html>
"""
