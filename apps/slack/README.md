# AgentNxt CodeReviewer Slack Surface Adapter

## Purpose
Slack enables team-facing review notifications, digests, and collaborative routing of high-priority findings.

## Current status
**Scaffolded**: integration boundaries are defined, but no Slack bot/app implementation exists yet.

## Shared core dependency rule
Slack integration must transport/render outputs from shared core-backed APIs and must not introduce separate review logic.

## Next implementation steps
1. Define Slack app scopes/events and security model.
2. Implement webhook/event receiver and command handlers.
3. Add digest and escalation message templates.
4. Add installation and operational runbooks.
