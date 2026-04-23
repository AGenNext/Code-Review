# AgentNxt CodeReviewer Production Review

## Summary of changes
Implemented a production-oriented standalone repository baseline with typed domain model, FastAPI backend, web/cloud UI, runtime profile management, provider/model separation, tests, deploy assets, and multi-surface starter adapters.

## Files changed
- README.md, AGENTS.md
- src/codereviewer/*
- tests/*
- docs/products/*
- deploy/code-reviewer/*
- apps/*/README.md

## Risks
- In-memory persistence only.
- Claude Agent SDK integration is an adapter boundary with deterministic local analysis pending runtime wiring.

## Deferred items
- Database + queue execution.
- Authentication/authorization.
- Production telemetry and SLO alerts.

## Common-layer improvements suggested or implemented
- Implemented shared core models/logic under `src/codereviewer/core` to prevent surface-specific duplication.

## Surface-specific follow-up work
- Implement actual clients and transports for Desktop/Mobile/VS Code/Slack/GitHub/Chrome adapters.

## Provider/model/runtime gaps still remaining
- Credential secret vault integration
- Provider capability discovery from live endpoints
- Dynamic model catalog synchronization
