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


## CI/CD operations
- Baseline CI workflow: `.github/workflows/ci.yml`.
- CI runs `pytest -q`, package build (`python -m build`), and Docker build validation.
- Local command parity is documented in `docs/products/code-reviewer-cicd.md`.

## Review logging and trace requirements
- Persist all review events with immutable identifiers.
- Required identifiers per event:
  - `review_id`
  - `action_id`
  - `trace_id`
  - `span_id` (when distributed tracing is enabled)
- Store lifecycle transitions and actor/system source for each action.
- Ensure logs support reconstruction of full review timeline.

## Agent identity requirement
- Every logged review/action event must include `agent_id` to identify the executing agent.
- `agent_id` must be present with `review_id`, `action_id`, and `trace_id` for correlation.

## Versioning requirement
- Track entity versions for review artifacts, profiles, prompts, and related mutable records.
- Log `entity_id` + `version` on create/update actions.

## Registry resolution requirement
- Execution must resolve models, skills, prompts, and deployable artifacts from registry records.
- Missing registry records must be created before operational use.

## Canonical ID requirement
- Model/skill/prompt/service-image registry lookups must use canonical IDs.
- Logs and audit records should store canonical IDs for deterministic traceability.
