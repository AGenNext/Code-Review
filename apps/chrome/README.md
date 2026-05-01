# AGenNext CodeReview Chrome Surface Adapter

## Purpose
Chrome is the browser-side context-capture and handoff surface for users working in web-based repository and review tools.

## Current status
**Planned**: this surface has planning documentation only and no concrete extension implementation yet.

## Shared core dependency rule
Chrome must submit captured context into shared backend APIs and rely on server/core-owned review logic in `src/codereviewer/core`.

## Next implementation steps
1. Define extension manifest and permission model.
2. Implement context capture and secure handoff to backend APIs.
3. Add lightweight launch/status UI.
4. Add packaging and store publication process.
