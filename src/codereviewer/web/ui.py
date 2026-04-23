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

  <h2>Runtime Profile</h2>
  <form id=\"profile-form\">
    <input id=\"name\" placeholder=\"Profile name\" required />
    <select id=\"provider\"></select>
    <input id=\"model\" placeholder=\"Model ID\" required />
    <input id=\"auth\" placeholder=\"Auth reference\" required />
    <button type=\"submit\">Save profile</button>
  </form>

  <h2>Submit Review</h2>
  <form id=\"review-form\">
    <input id=\"repo\" placeholder=\"Repository name\" required />
    <input id=\"profile-id\" placeholder=\"Runtime profile ID\" required />
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

function showError(message) { output.textContent = `Error: ${message}`; }

async function loadProviders() {
  const providers = await fetch('/api/providers').then(r => r.json());
  const select = document.getElementById('provider');
  providers.forEach(p => { const o = document.createElement('option'); o.value = p; o.textContent = p; select.appendChild(o); });
}

async function refreshReviews() {
  const reviews = await fetch('/api/reviews').then(r => r.json());
  document.getElementById('history').textContent = JSON.stringify(reviews, null, 2);
}

document.getElementById('refresh').addEventListener('click', refreshReviews);

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

loadProviders();
refreshReviews();
</script>
</body></html>
"""
