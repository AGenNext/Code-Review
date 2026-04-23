# AgentNxt CodeReviewer Architecture

## Architecture principles
- Shared-core-first: business/domain logic belongs in `src/codereviewer/core`.
- Typed contracts: API and service boundaries use explicit typed payloads.
- Surface adapters: each surface composes shared backend capabilities; no surface forks core logic.
- Core agent architecture: Claude Agent SDK remains the primary agent integration decision via adapter boundaries.

## Shared core
- `core/models.py`: canonical review entities and contracts.
- `core/logic.py`: severity-to-recommendation and summary scoring.

## Backend/API
- FastAPI app in `api/app.py`.
- Services:
  - `ReviewService`: orchestrates job lifecycle.
  - `RuntimeProfileService`: manages provider/model runtime profiles.
  - `ClaudeAgentSDKReviewer`: Claude Agent SDK boundary adapter.

## Surface architecture by product surface

### AgentNxt CodeReviewer Web / Cloud (implemented)
- Runtime: backend + web UI served from the current Python application surface.
- Flow: UI -> API routes -> services -> shared core.
- Scope now: end-to-end review submission + result retrieval, runtime profile management.

### AgentNxt CodeReviewer Desktop (scaffolded)
- Runtime target: packaged desktop client consuming existing API contracts.
- Architectural role: repo-adjacent and local-first review workflows.
- Required dependency rule: desktop surface must remain a consumer of shared core contracts, never a replacement.

### AgentNxt CodeReviewer Mobile (scaffolded)
- Runtime target: mobile client for triage and decision workflows.
- Architectural role: notification-driven interaction and lightweight finding inspection.
- Required dependency rule: mobile UI stays thin; semantics remain backend/core owned.

### AgentNxt CodeReviewer VS Code (scaffolded)
- Runtime target: IDE extension that maps findings into editor diagnostics.
- Architectural role: in-editor feedback and remediation loop.
- Required dependency rule: consumes typed APIs; no duplicated scoring or finding taxonomy logic.

### AgentNxt CodeReviewer Slack (scaffolded)
- Runtime target: bot/app transport for notifications and workflow commands.
- Architectural role: collaborative alerting and team routing.
- Required dependency rule: Slack message formatting wraps shared finding outputs.

### AgentNxt CodeReviewer GitHub (scaffolded)
- Runtime target: GitHub App/webhook + checks integration.
- Architectural role: pull request gating and annotation delivery.
- Required dependency rule: check results derive from shared review outcomes.

### AgentNxt CodeReviewer Chrome (planned)
- Runtime target: browser extension for context capture and submission.
- Architectural role: lightweight browser-side launch point for reviews.
- Required dependency rule: extension sends captured context to backend APIs; review logic remains server/core-side.

## Surface status integrity
The repository deliberately distinguishes **implemented**, **scaffolded**, and **planned** surfaces so architecture documentation reflects reality and does not overstate delivery.
