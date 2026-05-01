# AGenNext CodeReview Mobile Surface Adapter

## Purpose
Mobile provides quick triage, escalation, and approval workflows for review findings when users are away from desktop/browser contexts.

## Current status
**Scaffolded**: only adapter documentation exists; mobile application code is not yet implemented.

## Shared core dependency rule
Mobile must rely on backend APIs backed by `src/codereviewer/core` and must not reimplement scoring or finding semantics locally.

## Next implementation steps
1. Define mobile app shell and authentication/session flow.
2. Implement high-severity findings inbox and action flow.
3. Add push notification integration.
4. Add distribution/release pipeline.
