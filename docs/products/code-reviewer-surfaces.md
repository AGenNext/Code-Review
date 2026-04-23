# CodeReviewer Surface Definitions

## CodeReviewer Web
- Purpose: primary review submission and findings exploration surface.
- Workflow: create runtime profile -> submit diff review -> inspect findings/history.
- Status: **implemented**.
- Shared core relationship: consumes backend contracts from shared core models.
- Exists now: FastAPI + HTML UI in `src/codereviewer/api` and `src/codereviewer/web`.
- Not yet implemented: advanced UI filtering and auth-based tenancy.
- Next milestone: pagination/filtering and operator observability panels.

## CodeReviewer Desktop
- Purpose: repo-adjacent workflows in controlled environments.
- Intended runtime/packaging: packaged desktop shell (e.g., Tauri/Electron) consuming existing API.
- Status: **scaffolded**.
- Shared core relationship: must not duplicate review logic.
- Exists now: adapter definition doc only.
- Not yet implemented: packaged runtime, secure profile management, update channel.
- Next milestone: minimal shell with profile/review/history views.

## CodeReviewer Mobile
- Purpose: on-call triage and high-severity decision actions.
- Intended workflow: consume review alerts, inspect findings, submit feedback.
- Status: **scaffolded**.
- Shared core relationship: thin client over backend APIs.
- Exists now: adapter definition doc only.
- Not yet implemented: app runtime and auth/session handling.
- Next milestone: read-only review history + feedback submission.

## CodeReviewer VS Code
- Purpose: in-editor diagnostics for changed files.
- Intended workflow: PR diff reviewed in backend, diagnostics shown in editor.
- Status: **scaffolded**.
- Shared core relationship: extension displays backend outputs, no duplicated engine.
- Exists now: adapter definition doc only.
- Not yet implemented: extension runtime and diagnostics mapping.
- Next milestone: extension command to submit current diff.

## CodeReviewer Slack
- Purpose: collaborative notifications and approvals.
- Intended workflow: receive findings digest and route high-severity alerts.
- Status: **scaffolded**.
- Shared core relationship: message transport around shared findings models.
- Exists now: adapter definition doc only.
- Not yet implemented: Slack app runtime and interaction handlers.
- Next milestone: digest notification with deep-links to Web.

## CodeReviewer GitHub
- Purpose: pull-request checks integration.
- Intended workflow: run review per PR and post status/check annotations.
- Status: **scaffolded**.
- Shared core relationship: webhook adapter calls backend review APIs.
- Exists now: adapter definition doc only.
- Not yet implemented: GitHub App/webhook/check-run transport.
- Next milestone: PR check-run creation with summary results.

## CodeReviewer Chrome
- Purpose: browser-side context capture for review submission.
- Intended workflow: capture snippets/context and forward to backend review.
- Status: **planned**.
- Shared core relationship: capture-only client; review remains backend-owned.
- Exists now: planning stub.
- Not yet implemented: extension scaffold and submission flow.
- Next milestone: manifest + authenticated submit action.
