# AgentNxt CodeReviewer GitHub Surface Adapter

## Purpose
GitHub is the pull-request-native automation surface for checks, status reporting, and contextual review feedback.

## Current status
**Scaffolded**: adapter documentation exists; GitHub App/webhook runtime is not implemented yet.

## Shared core dependency rule
GitHub checks/comments must be projections of shared core review outputs and API contracts; no GitHub-specific fork of domain logic is allowed.

## Next implementation steps
1. Define GitHub App permissions and event matrix.
2. Implement webhook ingestion and signature verification.
3. Map review findings to checks/status/annotations.
4. Add deployment and secret-management guidance.
