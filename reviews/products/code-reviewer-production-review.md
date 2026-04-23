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

## Prompt Self-Review

### Summary
The production prompt was strong enough to bootstrap the repo, but it was not strict enough about product surface documentation and implemented-versus-scaffolded clarity.

### What the prompt got right
- Explicit org, repo, executor, prompt storage identity, and vision document identity
- Explicit Claude Agent SDK requirement
- Explicit provider support requirement for Anthropic, Bedrock, Vertex AI, and Microsoft Foundry
- Explicit model selection requirement separate from provider selection
- Explicit shared-core requirement
- Explicit Web / Cloud primary surface requirement

### What the prompt got wrong
- It allowed non-web surfaces to be satisfied with thin starter folders and placeholder README files
- It did not require the root `README.md` to document all named surfaces clearly
- It did not require implemented vs scaffolded vs planned status to be stated explicitly
- It did not force a proper Desktop surface definition
- It used the phrase `starter architecture` without defining minimum documentation deliverables for each surface

### Resulting gap
The repo now presents a real Web / Cloud baseline, but Desktop, Mobile, VS Code, Slack, GitHub, and Chrome are only lightly scaffolded. The root README does not clearly explain each surface, especially Desktop, in product terms.

### Prompt correction required
Future product prompts for multi-surface products must:
- require a surface status matrix in the root `README.md`
- require every named surface to be marked as `implemented`, `scaffolded`, or `planned`
- require a per-surface section in the architecture documentation
- require Desktop to be described as a product surface, not only as a folder stub
- distinguish clearly between `build now` and `define architecture only`

### Action
A follow-up prompt revision is required for CodeReviewer and should be reused for future multi-surface product repos.
