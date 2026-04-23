# AgentNxt CodeReviewer

Production-ready standalone repo for AgentNxt CodeReviewer with a shared core, web/cloud surface, and starter adapters for Desktop, Mobile, VS Code, Slack, GitHub, and Chrome.

## Stack
- Python 3.11+
- FastAPI backend/API
- Shared domain/core in `src/codereviewer/core`
- Claude Agent SDK integration boundary in `src/codereviewer/services/claude_agent_sdk.py`

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m codereviewer.main
```

Open `http://localhost:8000`.

## Repository layout
- `src/codereviewer/core`: shared review domain model and logic
- `src/codereviewer/services`: runtime/profile and review orchestration services
- `src/codereviewer/api`: production API endpoints
- `src/codereviewer/web`: web/cloud UI surface
- `apps/*`: adapter starter architecture for additional surfaces
- `docs/products`: product, architecture, operations, roadmap
- `deploy/code-reviewer`: deploy manifests and env templates
- `tests`: core and API/service tests
