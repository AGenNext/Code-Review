# CodeReviewer Architecture

## Shared core
- Path: `src/codereviewer/core`.
- Contains typed domain contracts (reviews, findings, runtime profiles, feedback, memory) and deterministic scoring logic.
- Shared by all current/future surfaces.

## Backend/API
- Path: `src/codereviewer/api/app.py`.
- FastAPI routes expose providers/models, runtime profiles, reviews, memory, and feedback APIs.

## Persistence model
- Path: `src/codereviewer/infra/repositories.py`.
- SQLite-backed repositories for:
  - runtime profiles
  - review jobs
  - feedback events
  - memory records
- Schema bootstrap is automatic at service startup.

## Review execution flow
1. API receives `ReviewJob`.
2. Review enters `queued`, then `running`.
3. Runtime profile is validated/resolved.
4. ContextBudgetManager prioritizes/truncates diff chunks.
5. ClaudeAgentSDKReviewer performs analysis.
6. Findings are summarized; review is persisted as `completed`/`failed`.
7. Review-history memory is written.

## Claude Agent SDK boundary
- `services/claude_agent_sdk.py` is the integration boundary.
- Current local heuristic engine exists for deterministic testing and scaffolding.
- Remaining gap: replace analyzer internals with live Claude Agent SDK runtime orchestration.

## Memory model
- Transient run memory: in-process and request-scoped.
- Durable review history: persisted `review_history` memory records per repository.
- Durable workspace memory: `workspace` memory type schema supported and retrievable.
- Rule/policy memory: currently explicit in code/policies, not user-editable in runtime.

## Feedback / self-improvement model
- Feedback events are captured and persisted via typed API.
- Improvement pipeline is guarded and reviewable: storage now, controlled rule/prompt updates later.
- No autonomous mutation of core policies.

## Dynamic context-window strategy
- File-priority weighting with security-sensitive bias.
- Prompt budget via char budget proxy derived from runtime profile token limits.
- Overflow strategy: deterministic truncation and reduced chunk set.

## Surface architecture
- CodeReviewer Web: **implemented** (API + UI).
- CodeReviewer Desktop: **scaffolded**.
- CodeReviewer Mobile: **scaffolded**.
- CodeReviewer VS Code: **scaffolded**.
- CodeReviewer Slack: **scaffolded**.
- CodeReviewer GitHub: **scaffolded**.
- CodeReviewer Chrome: **planned**.

## Current hardening gaps
- Queue/worker-backed async execution and retries.
- AuthN/AuthZ and tenant isolation.
- Migration framework for evolving persistence schema.
