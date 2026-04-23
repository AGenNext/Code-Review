# CodeReviewer

CodeReviewer (`agentnxt/code-reviewer`) is a production-oriented code review service with a typed backend, durable SQLite persistence, review job lifecycle tracking, and a Claude Agent SDK integration boundary.

## Purpose
CodeReviewer helps teams submit code diffs, execute policy-guided reviews, inspect findings, and capture feedback for controlled quality improvements.

## Implemented capabilities (current repo reality)
- FastAPI backend with review, runtime profile, memory, and feedback APIs.
- Durable persistence for runtime profiles, review jobs, feedback events, and memory records (SQLite).
- Review job lifecycle with `queued`, `running`, `completed`, `failed` states and timestamps.
- Deterministic local reviewer adapter with explicit Claude Agent SDK integration boundary.
- Basic web/cloud UI for runtime profile creation, review submission, and review history viewing.
- Context-budget manager for prioritized diff chunk selection.

## Architecture summary
- Shared core: `src/codereviewer/core` (Pydantic models + scoring logic).
- Services: orchestration, runtime-profile validation, context budgeting, feedback ingestion.
- Persistence: `src/codereviewer/infra/repositories.py` with SQLite-backed repositories.
- API + web: `src/codereviewer/api/app.py` and `src/codereviewer/web/ui.py`.

## Runtime/provider/model summary
- Provider selection is separate from model selection.
- Supported providers: `anthropic`, `bedrock`, `vertex`, `foundry`.
- Runtime profiles validate provider/model compatibility and support default profile behavior.

## Memory summary
- Implemented durable memories:
  - `review_history`: persisted per repository after each review run.
  - `workspace`: schema available for repository-level durable context.
- Transient run memory remains in-process and is intentionally not persisted.

## Dynamic context-window summary
- Diff content is prioritized (security/auth-sensitive files first).
- Chunks are selected under a configurable character budget.
- Overflow is truncated deterministically and recorded in review-history memory metadata.

## Self-improvement summary
- Feedback events (`false_positive`, `false_negative`, `accepted`, `rejected`, `overridden`) are persisted.
- Improvement is guarded: events are stored for explicit review; no autonomous policy rewrite occurs.

## Surface Status Matrix

| Surface | Status | What exists now |
|---|---|---|
| CodeReviewer Web | implemented | FastAPI + HTML UI with submission/history/profile flows |
| CodeReviewer Desktop | scaffolded | Adapter definition in `apps/desktop/README.md` |
| CodeReviewer Mobile | scaffolded | Adapter definition in `apps/mobile/README.md` |
| CodeReviewer VS Code | scaffolded | Adapter definition in `apps/vscode/README.md` |
| CodeReviewer Slack | scaffolded | Adapter definition in `apps/slack/README.md` |
| CodeReviewer GitHub | scaffolded | Adapter definition in `apps/github/README.md` |
| CodeReviewer Chrome | planned | Planning stub in `apps/chrome/README.md` |

## Production readiness now
- Production-ready for controlled single-instance deployments using local SQLite and API/UI flows.
- Not yet production-ready for high-scale multi-worker operations, strict auth, and queue-backed asynchronous execution.

## Run
```bash
pip install -e .[dev]
pytest
python -m codereviewer.main
```
