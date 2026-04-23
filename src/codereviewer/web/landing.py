LANDING_HTML = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>CodeReviewer</title>
  <meta name=\"description\" content=\"CodeReviewer is a production-oriented code review service with typed APIs and a web console.\" />
  <link rel=\"icon\" href=\"/static/favicon.svg\" type=\"image/svg+xml\" />
</head>
<body style=\"font-family: Inter, Arial, sans-serif; margin: 2rem; line-height: 1.5; color: #111;\">
  <main style=\"max-width: 880px; margin: 0 auto;\">
    <header style=\"display:flex; align-items:center; gap:1rem;\">
      <img src=\"/static/logo.svg\" alt=\"CodeReviewer logo\" style=\"width:56px;height:56px\" />
      <div>
        <h1 style=\"margin:0\">CodeReviewer</h1>
        <p style=\"margin:0.25rem 0 0 0;color:#444\">Production-oriented code review for policy-guided diff analysis and feedback capture.</p>
      </div>
    </header>

    <section>
      <h2>What CodeReviewer does</h2>
      <p>CodeReviewer accepts code diffs, evaluates added lines for security and quality signals, stores review history durably, and lets operators collect structured review feedback.</p>
    </section>

    <section>
      <h2>Core capabilities</h2>
      <ul>
        <li>Runtime profile management with provider/model compatibility checks.</li>
        <li>Review submission and retrieval APIs with persisted lifecycle state.</li>
        <li>Durable SQLite persistence for reviews, runtime profiles, memory, and feedback events.</li>
        <li>Dynamic context budgeting for deterministic prompt construction.</li>
      </ul>
    </section>

    <section>
      <h2>Surface status</h2>
      <ul>
        <li><strong>CodeReviewer Web:</strong> implemented</li>
        <li><strong>CodeReviewer Desktop:</strong> scaffolded</li>
        <li><strong>CodeReviewer Mobile:</strong> scaffolded</li>
        <li><strong>CodeReviewer VS Code:</strong> scaffolded</li>
        <li><strong>CodeReviewer Slack:</strong> scaffolded</li>
        <li><strong>CodeReviewer GitHub:</strong> scaffolded</li>
        <li><strong>CodeReviewer Chrome:</strong> planned</li>
      </ul>
    </section>

    <section>
      <h2>Entry points</h2>
      <ul>
        <li><a href=\"/app\">Open CodeReviewer Web Console</a></li>
        <li>API reference in repository docs: <code>docs/products/code-reviewer-api.md</code></li>
      </ul>
      <p style=\"color:#444\">Current auth status: API routes are currently unauthenticated and intended for controlled environments only.</p>
    </section>
  </main>
</body>
</html>
"""
