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

## Coolify deployment (recommended)

Deploying via Coolify is the preferred production path on this host.

- Image: `ghcr.io/agentnxt/code-reviewer:latest`
- Container port: `8080`
- Domain: `codereviewer.agnxxt.com`
- SSL: Let's Encrypt (enable in Coolify)

Required environment variables:
- `PYTHONPATH=/app/src`
- `PORT=8080`

Health check:
- Path: `/healthz`
- Expected: `200` with `{"status":"ok"}`

## Deployment instruction boundaries

### In scope
- Coolify deployment steps for CodeReviewer using GHCR image tags.
- Domain and TLS setup for `codereviewer.agnxxt.com`.
- Required runtime environment variables and health check contract.

### Out of scope
- Organization-wide deployment policy.
- DNS provider-specific account automation.
- Non-CodeReviewer service orchestration details.

## Shared instruction contribution rule
When deployment or execution guidance here reveals reusable patterns, upstream them to `openautonomyx/common-instructions` so other repos can reuse the same instruction layer.

## Skill feedback loop
If usage patterns reveal repeated friction, convert the lesson into a reusable instruction pattern and upstream it to `openautonomyx/common-instructions`.

## Prompt registry
Track recurring operational prompts in a lightweight registry. Upstream reusable prompts to `openautonomyx/common-instructions` with clear purpose, trigger, inputs, and output contract.

## Subagent evaluation and feedback policy
CodeReviewer workflows should generate per-subagent evaluation and feedback for every reviewed subagent contribution, including decision summary, key findings, and concrete follow-up actions.

## Deployment policy
Production deployment must be CI/CD-only. Direct server deployment is not allowed.
See `docs/products/code-reviewer-deployment-policy.md`.

## Execution discipline rules
- No context switching during active execution unless priorities are explicitly changed.
- Maintain strict priority order from the active task list.
- Track work with explicit task states: `pending`, `in_progress`, `blocked`, `done`.
- For long-running tasks, run them in background jobs and continue non-blocking foreground tasks.

## Communication rules
- Keep responses concise and to the point.
- Respond after research/verification.
- Clarify when unclear; do not guess.
- Check available past memory/context before asking follow-up questions.

## Dynamic context handling
Use established session context by default so users do not need to repeat stable details in every call. Request context only when missing, conflicting, or stale.

## Project status tracking
Status must be continuously tracked in GitHub. Primary tracker: `PROJECT_STATUS.md` (optionally mirrored to GitHub Projects).

## Service consolidation rule
Always consolidate services and avoid duplicates. Extend existing services by default; do not introduce parallel duplicate service implementations without explicit approval.

## Pre-task model recommendation rule
Before any new task is started, provide a best-fit LLM model recommendation balancing cost, speed, and benchmark quality, with one primary choice and optional fallback.

## Pre-project deep research rule
Before any new project starts, perform deep research and state the recommended approach with rationale (architecture options, risks, cost/speed tradeoffs, operational complexity) before execution.

## Reuse-first rule
Do not reinvent the wheel. Reuse proven solutions by default; implement custom components only when necessary and justified.

## Repository governance standard
This repository follows a one-product-per-repo model and requires complete product artifacts (PRD, design, HLD, DB schema, prompts, seed-data docs). See `docs/products/repository-governance-policy.md`.

Environment variable policy:
- Use `.env.example` as the non-secret variable template.
- Keep secrets in secret manager/platform secrets, never in git.

## Mandatory deployed-service baseline
All production services must provide SSO, mail, notifications, error monitoring, telemetry, and analytics as baseline capabilities.

## Code-deploy responsibility
`code-deploy` is responsible for CI/CD setup and deployment automation, not manual production deploy steps.

## Multi-agent responsibility model
- `code-assist`: writes and maintains project documents.
- `code-reviewer`: reviews PRD, HLD, LLD, and code.
- `code-tester`: validates documents and test outcomes.
- Reviewer feedback should be instructional to improve subagent capability over time.

## Logging and traceability rule
All reviews must be logged. Every action must include an action ID and trace metadata so workflows are fully traceable.

## Agent identity logging
All review/action logs must include `agent_id`.

## Identifier and version rule
All key entities/actions must have unique IDs; mutable entities must carry explicit versions.

## Registry-first rule
Resolve all reusable items from registries first. If missing, register first (model/skill/prompt/service-image) before use.

## Canonical registry IDs
Registries must expose canonical IDs; operational workflows should reference canonical IDs, not display names.

## Registry publish rule
Registry publishing must go through GitHub PR review and CI workflow gates; no direct manual publishing.


### Agent orchestration APIs
- `POST /api/agents/spawn-all` returns the active roster used by UI/terminal chat.
- `GET /api/agents` lists available agents.
- `POST /api/agents/chat` routes a message to a selected agent and returns response prefixed with agent name.
- Web UI now includes **Agent Chat** panel on `/app`.

### VPS systemd service
- Service name: `code-reviewer`
- Unit path: `/etc/systemd/system/code-reviewer.service`
- Runtime bind: `0.0.0.0:8787`
- Health check: `curl http://127.0.0.1:8787/healthz`
