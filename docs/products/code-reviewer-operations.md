# AgentNxt CodeReviewer Operations

## Runtime configuration
- Manage runtime profiles through `/api/runtime-profiles`.
- Provider and model are independently configured in profile payload.

## APIs
- `POST /api/runtime-profiles`
- `GET /api/runtime-profiles`
- `GET /api/providers`
- `GET /api/models?provider=...`
- `POST /api/reviews`
- `GET /api/reviews`
- `GET /api/reviews/{job_id}`

## Hardening checklist
- Replace in-memory repositories with persistent datastore.
- Integrate official Claude Agent SDK runtime pipeline.
- Add authN/authZ and audit logging.
