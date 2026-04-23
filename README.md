# CodeReviewer

CodeReviewer (`agentnxt/code-reviewer`) is a production-oriented code review service with a typed FastAPI backend, SQLite persistence, review lifecycle tracking, and a Claude Agent SDK integration boundary.

## Purpose
CodeReviewer helps teams submit code diffs, execute policy-guided reviews, inspect findings, and capture feedback for controlled quality improvements.

## Product entry points
- Landing page: `GET /`
- Web console (implemented UI): `GET /app`
- API docs in repository: `docs/products/code-reviewer-api.md`
- Runtime start command: `python -m codereviewer.main`

## CI/CD baseline
A GitHub Actions baseline is available at `.github/workflows/ci.yml` and includes:
- Python setup and dependency installation.
- `pytest` execution.
- Python package build validation (`python -m build`).
- Container build validation using `deploy/code-reviewer/Dockerfile`.

## Automated test path
```bash
pip install -e .[dev]
pytest -q
```

## Implemented capabilities (verified repo reality)
- FastAPI backend with review, runtime profile, memory, and feedback APIs.
- Durable SQLite persistence for runtime profiles, review jobs, feedback events, and memory records.
- Review job lifecycle with `queued`, `running`, `completed`, `failed` states and timestamps.
- Deterministic local reviewer adapter with explicit Claude Agent SDK integration boundary.
- Web UI console plus a branded landing page.
- Context-budget manager for prioritized diff chunk selection.

## Architecture summary
- Shared core: `src/codereviewer/core` (Pydantic models + scoring logic).
- Services: orchestration, runtime-profile validation, context budgeting, feedback ingestion.
- Persistence: `src/codereviewer/infra/repositories.py` with SQLite-backed repositories.
- API + web: `src/codereviewer/api/app.py` and `src/codereviewer/web/*`.

## Runtime/provider/model summary
- Provider selection is separate from model selection.
- Supported providers: `anthropic`, `bedrock`, `vertex`, `foundry`.
- Runtime profiles validate provider/model compatibility and support default profile behavior.

## Surface Status Matrix

| Surface | Status | What exists now |
|---|---|---|
| CodeReviewer Web | implemented | FastAPI + landing page + web console for submission/history/profile flows |
| CodeReviewer Desktop | scaffolded | Adapter definition in `apps/desktop/README.md` |
| CodeReviewer Mobile | scaffolded | Adapter definition in `apps/mobile/README.md` |
| CodeReviewer VS Code | scaffolded | Adapter definition in `apps/vscode/README.md` |
| CodeReviewer Slack | scaffolded | Adapter definition in `apps/slack/README.md` |
| CodeReviewer GitHub | scaffolded | Adapter definition in `apps/github/README.md` |
| CodeReviewer Chrome | planned | Planning stub in `apps/chrome/README.md` |

## Branding and assets
- Product name is locked as `CodeReviewer`.
- Repo slug is locked as `code-reviewer`.
- Web brand assets are served from `src/codereviewer/web/static/logo.svg` and `src/codereviewer/web/static/favicon.svg`.

## Current production limitations
- API routes are currently unauthenticated (single-team controlled environments only).
- SQLite is suitable for single-instance deployments, not high-concurrency multi-worker scale.
- Queue-backed async execution, retries, and cancellation are not implemented yet.

## Run locally
```bash
pip install -e .[dev]
pytest -q
python -m codereviewer.main
```

## Docker/Coolify configuration
All container runtime configuration is environment-driven.

1. Copy `deploy/code-reviewer/.env.example` to `deploy/code-reviewer/.env`.
2. Set values for:
- `HOST`
- `PORT`
- `PORT_START`
- `PORT_END`
- `APP_PORT`
- `CODEREVIEWER_DB_PATH`
- `SIGNOZ_ENABLED`
- `SIGNOZ_SERVICE_NAME`
- `SIGNOZ_OTLP_TRACES_ENDPOINT`
- `NOTIFICATIONS_ENABLED`
- `NOTIFICATION_CHANNELS`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `SMTP_TO`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`
- `SSO_ENABLED`
- `SSO_PROVIDER`
- `SSO_ISSUER_URL`
- `SSO_CLIENT_ID`
- `SSO_CLIENT_SECRET`
- `SSO_AUDIENCE`
- `SSO_REDIRECT_URI`
- `SSO_SCOPES`
- `CLAUDE_AGENT_SDK_ENABLED`
- `CLAUDE_AGENT_SDK_STRICT`
- `CLAUDE_AGENT_SDK_MODEL`
- `CLAUDE_AGENT_SDK_MAX_TOKENS`
- `CLAUDE_AGENT_SDK_TEMPERATURE`
- `CLAUDE_API_KEY`
- `LITELLM_ENABLED`
- `LITELLM_BASE_URL`
- `LITELLM_API_KEY`
- `LITELLM_MODEL`
- `LITELLM_PROVIDER_PREFIX_MAP`

Then run:
```bash
docker compose -f deploy/code-reviewer/docker-compose.yml up --build
```

### Notifications API
- `POST /api/notifications/test` sends a test notification when SMTP is configured and notifications are enabled.

### SSO Config API
- `GET /api/sso/config` returns effective SSO runtime configuration (secret value is not returned).

### Claude Agent SDK Runtime
- Set `CLAUDE_AGENT_SDK_ENABLED=true` to enable real Claude-backed review calls.
- Set `CLAUDE_API_KEY` (or use a runtime profile auth reference that already contains an `sk-ant-` key).
- `CLAUDE_AGENT_SDK_STRICT=true` makes SDK failures fail the review job instead of falling back to local deterministic rules.
- Set `LITELLM_ENABLED=true` to route calls through a LiteLLM gateway (`LITELLM_BASE_URL`).
- With LiteLLM enabled, model resolution uses runtime profile model (converted to `anthropic/<model>` when needed) or `LITELLM_MODEL`.
- `LITELLM_PROVIDER_PREFIX_MAP` controls provider-to-prefix routing (JSON map), e.g. `{"vertex":"vertex_ai/","bedrock":"bedrock/","anthropic":"anthropic/"}`.
- Runtime profile metadata supports overrides:
  - `litellm_model`: use exact LiteLLM model route (highest priority)
  - `litellm_provider`: choose provider key from prefix map for model prefixing

### Multitenancy and Agent Identity
- Tenant scope header: `X-Tenant-ID` (defaults to `default`).
- Agent identity header: `X-Agent-ID`.
- If `X-Tenant-ID` is absent and `X-Agent-ID` is provided, tenant is derived as `agent:<agent_id>`.
- Set `MULTITENANCY_REQUIRE_AGENT_IDENTITY=true` to require `X-Agent-ID` on API requests.
