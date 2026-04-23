INDEX_HTML = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>CodeReviewer Web Console</title>
  <link rel=\"icon\" href=\"/static/favicon.svg\" type=\"image/svg+xml\" />
</head>
<body style=\"font-family: Inter, Arial, sans-serif; margin: 2rem; line-height: 1.4;\">
  <header style=\"display:flex; align-items:center; gap:0.75rem; margin-bottom: 1rem;\">
    <img src=\"/static/logo.svg\" alt=\"CodeReviewer logo\" style=\"width:40px;height:40px\" />
    <div>
      <h1 style=\"margin:0;\">CodeReviewer Web Console</h1>
      <p style=\"margin:0.25rem 0 0 0; color:#444;\">Implemented surface for runtime profile management, review submission, and history visibility.</p>
    </div>
  </header>

  <p><a href=\"/\">Back to CodeReviewer landing page</a></p>

  <h2>Configuration</h2>
  <div id=\"config-summary\" style=\"display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:0.75rem;\"></div>

  <h2>Runtime Profile</h2>
  <form id=\"profile-form\">
    <input id=\"name\" placeholder=\"Profile name\" required />
    <select id=\"provider\"></select>
    <select id=\"model\" required></select>
    <input id=\"auth\" placeholder=\"Auth reference\" required />
    <button type=\"submit\">Save profile</button>
  </form>

  <h2>Submit Review</h2>
  <form id=\"review-form\">
    <input id=\"repo\" placeholder=\"Repository name\" required />
    <select id=\"profile-id\" required></select>
    <textarea id=\"patch\" placeholder=\"Unified diff patch\" required style=\"width:100%;height:120px\"></textarea>
    <button type=\"submit\">Run review</button>
  </form>

  <h2>Review History</h2>
  <button id=\"refresh\">Refresh</button>
  <pre id=\"history\"></pre>

  <h2>Output</h2>
  <pre id=\"output\"></pre>

<script>
const output = document.getElementById('output');
let appConfig = null;

function showError(message) { output.textContent = `Error: ${message}`; }

function renderStatusCard(title, rows) {
  const card = document.createElement('section');
  card.style.border = '1px solid #ddd';
  card.style.borderRadius = '6px';
  card.style.padding = '0.75rem';
  const heading = document.createElement('h3');
  heading.textContent = title;
  heading.style.margin = '0 0 0.5rem 0';
  card.appendChild(heading);
  rows.forEach(([label, value]) => {
    const line = document.createElement('div');
    line.textContent = `${label}: ${value}`;
    card.appendChild(line);
  });
  return card;
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
  const models = appConfig.runtime.models
    .filter(model => model.provider === provider && model.enabled)
    .map(model => ({value: model.model_id, label: `${model.display_name} (${model.model_id})`}));
  setOptions(document.getElementById('model'), models, 'Select model');
}

function renderConfig() {
  const {integrations, runtime, identity} = appConfig;
  const summary = document.getElementById('config-summary');
  summary.textContent = '';
  summary.appendChild(renderStatusCard('Runtime', [
    ['tenant', identity.tenant_id],
    ['providers', runtime.providers.join(', ')],
    ['profiles', runtime.profiles.length],
    ['models', runtime.models.length]
  ]));
  summary.appendChild(renderStatusCard('LLM', [
    ['Claude SDK', integrations.claude_agent_sdk.enabled ? 'enabled' : 'disabled'],
    ['Claude key', integrations.claude_agent_sdk.api_key_configured ? 'configured' : 'missing'],
    ['LiteLLM', integrations.litellm.enabled ? 'enabled' : 'disabled'],
    ['LiteLLM key', integrations.litellm.api_key_configured ? 'configured' : 'missing']
  ]));
  summary.appendChild(renderStatusCard('Ops', [
    ['notifications', integrations.notifications.enabled ? 'enabled' : 'disabled'],
    ['SMTP', integrations.notifications.smtp_configured ? 'configured' : 'incomplete'],
    ['SigNoz', integrations.observability.signoz_enabled ? 'enabled' : 'disabled'],
    ['SSO', integrations.sso.enabled ? integrations.sso.provider : 'disabled']
  ]));
}

function renderRuntimeControls() {
  setOptions(
    document.getElementById('provider'),
    appConfig.runtime.providers.map(provider => ({value: provider, label: provider})),
    null
  );
  updateModelOptions();
  setOptions(
    document.getElementById('profile-id'),
    appConfig.runtime.profiles.map(profile => ({
      value: profile.id,
      label: `${profile.is_default ? '* ' : ''}${profile.name} - ${profile.provider}/${profile.model_id}`
    })),
    'Select runtime profile'
  );
}

async function loadConfig() {
  const res = await fetch('/api/config');
  appConfig = await res.json();
  if (!res.ok) return showError(appConfig.detail || 'Failed to load config');
  renderConfig();
  renderRuntimeControls();
}

async function refreshReviews() {
  const reviews = await fetch('/api/reviews').then(r => r.json());
  document.getElementById('history').textContent = JSON.stringify(reviews, null, 2);
}

document.getElementById('refresh').addEventListener('click', refreshReviews);
document.getElementById('provider').addEventListener('change', updateModelOptions);

document.getElementById('profile-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    name: document.getElementById('name').value,
    provider: document.getElementById('provider').value,
    model_id: document.getElementById('model').value,
    auth_reference: document.getElementById('auth').value,
    is_default: true
  };
  const res = await fetch('/api/runtime-profiles', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload)});
  const body = await res.json();
  if (!res.ok) return showError(body.detail || 'Failed to save profile');
  output.textContent = JSON.stringify(body, null, 2);
  await loadConfig();
});

document.getElementById('review-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const patch = document.getElementById('patch').value;
  if (!patch.includes('+')) return showError('Patch must include added lines to review.');
  const payload = {
    repository: {name: document.getElementById('repo').value, branch:'main'},
    runtime_profile_id: document.getElementById('profile-id').value,
    changes: [{path:'sample.py', change_type:'modified', patch}]
  };
  const res = await fetch('/api/reviews', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload)});
  const body = await res.json();
  if (!res.ok) return showError(body.detail || 'Failed to submit review');
  output.textContent = JSON.stringify(body, null, 2);
  refreshReviews();
});

loadConfig();
refreshReviews();
</script>
</body></html>
"""
