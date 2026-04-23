# CodeReviewer Operations

## Configuration model
- Runtime profiles specify provider, model, auth reference, generation controls.
- Provider/model compatibility is validated on profile creation.

## Environment assumptions
- Python 3.11+.
- Writable local filesystem for SQLite database (`.codereviewer/codereviewer.db`).

## Deployment assumptions
- Current deploy assets target containerized single-service operation.
- Web/API process can be run with Uvicorn.

## Persistence and retention
- Runtime profiles, review jobs, memory, and feedback are durable in SQLite.
- Retention is currently infinite unless operators prune database records.

## Memory operations
- `review_history` records are written automatically per run.
- `workspace` records can be stored/retrieved through repository APIs.

## Feedback loop operations
- Collect feedback events through `/api/feedback`.
- Use feedback as auditable input for manual/controlled policy adjustments.

## Operational gaps before broad production rollout
- Add queue workers and timeout/cancellation execution controls.
- Add auth, rate limits, and audit logs.
- Add backup/restore and migration process docs.
