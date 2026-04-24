# CodeReviewer API Reference

Base runtime default: `http://localhost:8000` (systemd deployment on this VPS runs `http://127.0.0.1:8787`)

Auth status: **No authentication is currently enforced**. Run only in controlled environments.

## Endpoint summary

### Product surfaces
- `GET /` — branded landing page.
- `GET /app` — implemented CodeReviewer Web console.

### Runtime profile endpoints
- `GET /api/providers`
  - Response: `string[]` (supported providers).
- `GET /api/models?provider=<provider>`
  - Response: array of model descriptors filtered by provider when provided.
- `GET /api/runtime-profiles`
  - Response: `RuntimeProfile[]`.
- `POST /api/runtime-profiles`
  - Request body: `RuntimeProfile`.
  - Response: created `RuntimeProfile`.
  - Validation: returns `400` when provider/model pairing is invalid.

### Review endpoints
- `POST /api/reviews`
  - Request body: `ReviewJob` with `repository`, `runtime_profile_id`, and `changes`.
  - Response: persisted `ReviewJob` with lifecycle state and summary.
- `GET /api/reviews`
  - Response: `ReviewJob[]`.
- `GET /api/reviews/{job_id}`
  - Response: `ReviewJob`.
  - Errors: `404` when job is not found.

### Memory endpoints
- `GET /api/memory/{repository_name}?memory_type=<type>`
  - Response: `MemoryRecord[]`.
  - Returns review history and workspace records by repository.

### Feedback endpoints
- `POST /api/feedback`
  - Request body: `ReviewFeedbackEvent`.
  - Response: stored `ReviewFeedbackEvent`.
- `GET /api/feedback?review_job_id=<id>`
  - Response: `ReviewFeedbackEvent[]`.

### Agent orchestration endpoints
- `POST /api/agents/spawn-all`
  - Response: `{ "agents": string[] }` (active agent roster).
- `GET /api/agents`
  - Response: `string[]` (same roster for UI selection).
- `POST /api/agents/chat`
  - Request body: `{ "agent_name": string, "message": string }`.
  - Response: `{ "agent_name": string, "response": string }` with agent name prefix in response text.

## Request / response examples

### Create runtime profile
```bash
curl -X POST http://localhost:8000/api/runtime-profiles \
  -H 'content-type: application/json' \
  -d '{
    "name": "default",
    "provider": "anthropic",
    "model_id": "claude-sonnet-4",
    "auth_reference": "local-key",
    "is_default": true
  }'
```

### Submit review
```bash
curl -X POST http://localhost:8000/api/reviews \
  -H 'content-type: application/json' \
  -d '{
    "repository": {"name": "demo", "branch": "main"},
    "runtime_profile_id": "<runtime-profile-id>",
    "changes": [
      {
        "path": "a.py",
        "change_type": "modified",
        "patch": "@@\\n+# TODO remove hardcoded password"
      }
    ]
  }'
```

### Retrieve feedback for a review
```bash
curl 'http://localhost:8000/api/feedback?review_job_id=job-1'
```

### Spawn all agents
```bash
curl -X POST http://localhost:8000/api/agents/spawn-all
```

### Send message to named agent
```bash
curl -X POST http://localhost:8000/api/agents/chat \
  -H 'content-type: application/json' \
  -d "{\"agent_name\":\"code-reviewer\",\"message\":\"clean repos\"}"
```

## Error behavior
- FastAPI/Pydantic validation failures return HTTP `422` with details.
- Runtime profile compatibility validation failures return HTTP `400`.
- Unknown review IDs return HTTP `404`.

## Contract source of truth
Typed request/response contracts live in `src/codereviewer/core/models.py`. Keep this document aligned with those models and `src/codereviewer/api/app.py`.
