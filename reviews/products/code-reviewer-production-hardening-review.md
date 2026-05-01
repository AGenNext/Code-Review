# AGenNext CodeReview Production Hardening Review

## What was hardened
- Introduced durable SQLite persistence for profiles, jobs, feedback, and memory.
- Added explicit review lifecycle timestamps/states and failure capture.
- Hardened runtime profile validation with provider/model compatibility checks.
- Improved diff analysis to only inspect added lines and dedupe findings.
- Added context-budget selection strategy and tests.
- Added feedback event model for guarded self-improvement loop.
- Updated docs for architecture, operations, roadmap, and surface clarity.

## What remains not yet production-grade
- Queue-worker execution with retries/timeouts/cancellation.
- AuthN/AuthZ, tenant isolation, and audited admin workflows.
- Online Claude Agent SDK runtime transport integration.

## Architecture decisions preserved
- Product name and repo identity preserved (`CodeReviewer`, `code-reviewer`).
- Claude Agent SDK kept as the core agent architecture boundary.
- Provider selection remains separate from model selection.
- Surface truthfulness maintained (`implemented`/`scaffolded`/`planned`).

## Risks
- SQLite is single-instance friendly but limited for high-write concurrency.
- Heuristic reviewer remains limited until full model-backed analysis is wired.

## Deferred items
- DB migration tooling.
- Background worker subsystem.
- Policy/rule management UI.

## Reusable lessons for future product prompts
- Require persistence-level acceptance criteria, not only “replace in-memory”.
- Require explicit context budget behavior + overflow tests.
- Require explicit self-improvement guardrails and event schema before adaptation automation.

## Memory decisions made
- Durable `review_history` memory is implemented by default.
- `workspace` memory model is defined and stored durably.
- Transient run memory remains in-process and non-durable.

## Self-improvement decisions made
- Feedback is event-sourced and reviewable.
- Adaptation is intentionally manual/guarded for now.

## Dynamic context-window decisions made
- File-priority context selection.
- Configurable budgeted truncation strategy.
- Deterministic chunk selection for testability.
