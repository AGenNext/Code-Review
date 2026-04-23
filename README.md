# AgentNxt CodeReviewer

AgentNxt CodeReviewer is a multi-surface product for repository analysis and structured AI-assisted code review.

The **currently implemented primary surface** is **AgentNxt CodeReviewer Web / Cloud** (FastAPI + web UI).
Other named surfaces are intentionally tracked as scaffolded adapters or planned work so product scope remains explicit and honest.

## Surface Status Matrix

| Surface | Status | What exists now in this repo | Primary use |
|---|---|---|---|
| AgentNxt CodeReviewer Web / Cloud | implemented | FastAPI app, API routes, services, web UI in `src/codereviewer/web` | Main production UI for review submission and result inspection |
| AgentNxt CodeReviewer Desktop | scaffolded | `apps/desktop/README.md` surface adapter definition | Repo-adjacent/local desktop workflows with optional offline-friendly operation |
| AgentNxt CodeReviewer Mobile | scaffolded | `apps/mobile/README.md` surface adapter definition | On-call/mobile triage and review approvals |
| AgentNxt CodeReviewer VS Code | scaffolded | `apps/vscode/README.md` surface adapter definition | In-editor feedback loop during development |
| AgentNxt CodeReviewer Slack | scaffolded | `apps/slack/README.md` surface adapter definition | Team notification and digest workflows |
| AgentNxt CodeReviewer GitHub | scaffolded | `apps/github/README.md` surface adapter definition | PR status/check integration and review automation |
| AgentNxt CodeReviewer Chrome | planned | `apps/chrome/README.md` planning boundary | Browser-assisted context capture for review workflows |

Status definitions:
- **implemented**: runnable product surface with concrete application code.
- **scaffolded**: surface contract and integration rules are documented; implementation is pending.
- **planned**: surface intent is defined but implementation scaffolding is minimal.

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
- `src/codereviewer/web`: AgentNxt CodeReviewer Web / Cloud
- `apps/*`: surface adapters for Desktop/Mobile/VS Code/Slack/GitHub/Chrome
- `docs/products`: product, surfaces, architecture, operations, roadmap
- `deploy/code-reviewer`: deploy manifests and env templates
- `tests`: core and API/service tests

## Product docs
- Product overview: `docs/products/code-reviewer.md`
- Surface definitions: `docs/products/code-reviewer-surfaces.md`
- Architecture: `docs/products/code-reviewer-architecture.md`
- Operations: `docs/products/code-reviewer-operations.md`
- Roadmap: `docs/products/code-reviewer-roadmap.md`
