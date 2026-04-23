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
