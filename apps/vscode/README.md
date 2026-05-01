# AGenNext CodeReview VS Code Surface Adapter

## Purpose
VS Code integrates review results directly into the editor to shorten the feedback loop during coding and pull-request preparation.

## Current status
**Scaffolded**: extension scope is documented, but extension runtime code is not present yet.

## Shared core dependency rule
The extension must consume typed backend contracts and shared finding structures; domain logic remains centralized in `src/codereviewer/core`.

## Next implementation steps
1. Scaffold extension runtime and command palette actions.
2. Implement API client + authentication/session handoff.
3. Map findings to diagnostics and code actions.
4. Add packaging and marketplace publishing workflow.
