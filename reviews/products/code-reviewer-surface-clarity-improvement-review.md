# AgentNxt CodeReviewer Surface Clarity Improvement Review

## Summary of changes
- Added explicit multi-surface status documentation across root/product/architecture/roadmap docs.
- Added a dedicated surfaces reference document with per-surface purpose, workflow, status, shared-core relationship, and implementation gaps.
- Expanded every `apps/*/README.md` from placeholder text to concrete adapter intent, status, dependency rules, and next steps.

## Documentation gaps corrected
- Root documentation now distinguishes implemented vs scaffolded vs planned surfaces instead of grouping all non-web surfaces as generic “starter adapters”.
- Desktop surface is now defined as a real product surface with explicit rationale, workflow role, and packaging/runtime direction.
- Architecture and roadmap now reflect actual delivery state instead of implying equal maturity across surfaces.

## Surface-status decisions made
- **Implemented**: AgentNxt CodeReviewer Web / Cloud.
- **Scaffolded**: Desktop, Mobile, VS Code, Slack, GitHub.
- **Planned**: Chrome.

These labels were chosen based on verified repository reality (existing runnable code vs documentation-only adapters).

## Remaining surface implementation gaps
- Desktop: no packaged runtime or native client implementation yet.
- Mobile: no app runtime, session/auth flow, or deployment channel.
- VS Code: no extension runtime or diagnostics bridge.
- Slack: no app/bot transport implementation.
- GitHub: no app/webhook/checks implementation.
- Chrome: no extension code scaffold beyond planning documentation.

## Reusable prompt lessons exposed by this correction pass
1. Multi-surface prompts should require a mandatory status matrix in the root README.
2. Prompts should force per-surface sections that include “what exists now” and “what is missing”.
3. Prompts should require Desktop to be treated as a first-class product surface (not a folder placeholder).
4. Prompts should require architecture and roadmap docs to echo the same status vocabulary (`implemented`, `scaffolded`, `planned`) to avoid drift.
5. Prompts should include a truthfulness clause forbidding maturity overstatement for scaffolded/planned surfaces.
