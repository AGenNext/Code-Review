INDEX_HTML = """
<!doctype html>
<html>
<head><title>AgentNxt CodeReviewer Web</title></head>
<body style=\"font-family: sans-serif; margin: 2rem;\">
  <h1>AgentNxt CodeReviewer Web</h1>
  <p>Production web/cloud surface for review orchestration.</p>

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
    <textarea id=\"patch\" placeholder=\"Patch text\" required></textarea>
    <button type=\"submit\">Run review</button>
  </form>

  <pre id=\"output\"></pre>

<script>
async function loadProviders() {
  const providers = await fetch('/api/providers').then(r => r.json());
  const select = document.getElementById('provider');
  providers.forEach(p => {
    const o = document.createElement('option'); o.value = p; o.textContent = p; select.appendChild(o);
  });
}

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
  document.getElementById('output').textContent = JSON.stringify(await res.json(), null, 2);
});

document.getElementById('review-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    repository: {name: document.getElementById('repo').value, branch:'main'},
    runtime_profile_id: document.getElementById('profile-id').value,
    changes: [{path:'sample.py', change_type:'modified', patch: document.getElementById('patch').value}]
  };
  const res = await fetch('/api/reviews', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload)});
  document.getElementById('output').textContent = JSON.stringify(await res.json(), null, 2);
});

loadProviders();
</script>
</body></html>
"""
