# AgentNxt CodeReviewer Roadmap

## Current baseline (implemented now)
- AgentNxt CodeReviewer Web / Cloud is the only implemented product surface.
- Shared core and API/service layer are in place for multi-surface reuse.

## Phase 1: harden the implemented surface
- Persistent storage and queue-backed execution.
- Provider auth vault integration.
- Enhanced finding taxonomy and policy controls.
- AuthN/authZ and auditability.

## Phase 2: move scaffolded surfaces into first runnable releases
1. **GitHub**: checks/status integration and webhook processing.
2. **VS Code**: in-editor diagnostics and remediation workflow.
3. **Slack**: review digest notifications and escalation actions.
4. **Desktop**: packaged local/repo-adjacent client for controlled environments.
5. **Mobile**: triage and high-severity action workflow.

## Phase 3: planned surfaces and ecosystem expansion
- **Chrome**: context-capture extension for browser-hosted workflows.
- Cross-surface policy consistency, telemetry, and release automation.

## Status discipline
Roadmap milestones must preserve clear status labels. Surfaces are not treated as complete products until runnable implementations exist in-repo.
