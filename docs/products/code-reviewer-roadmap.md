# CodeReviewer Roadmap (Honest Sequence)

## Now (implemented)
- CodeReviewer Web is the only implemented product surface.
- Durable local persistence, feedback/event model, and context budgeting are implemented.

## Next hardening milestone
1. Queue-backed workers with retries/timeouts/cancellation.
2. Authentication, authorization, and auditability.
3. Migration tooling and retention operations.

## Surface milestones
- CodeReviewer GitHub (**scaffolded**): webhook + checks integration.
- CodeReviewer VS Code (**scaffolded**): editor diagnostics transport.
- CodeReviewer Slack (**scaffolded**): notifications + workflow actions.
- CodeReviewer Desktop (**scaffolded**): packaged desktop shell consuming shared APIs.
- CodeReviewer Mobile (**scaffolded**): triage-focused app.
- CodeReviewer Chrome (**planned**): browser extension for context capture.

## Truthfulness rule
Scaffolded/planned surfaces stay explicitly labeled until runnable implementations land.
