# AgentNxt CodeReviewer Desktop Surface Adapter

## Purpose
Desktop is the local/repo-adjacent surface for users who need native packaging, local context handling, or controlled enterprise workstation workflows.

## Current status
**Scaffolded**: this repository currently contains surface intent and dependency rules only; no desktop runtime implementation exists yet.

## Shared core dependency rule
Desktop must consume shared API/domain contracts and must not duplicate or fork review business logic from `src/codereviewer/core`.

## Next implementation steps
1. Define desktop runtime shell and packaging target.
2. Implement typed API client against existing backend endpoints.
3. Add local repository context capture flow.
4. Add build/sign/release pipeline.
