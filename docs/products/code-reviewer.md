# AgentNxt CodeReviewer Product

AgentNxt CodeReviewer is a production application that analyzes repository changes and emits structured review findings with severity, recommendations, and summary risk scoring.

## Product shape
- Product family: multi-surface code review product.
- Implemented primary surface: AgentNxt CodeReviewer Web / Cloud.
- Additional surfaces: Desktop, Mobile, VS Code, Slack, GitHub, Chrome (scaffolded or planned).
- Shared-core-first rule: domain logic lives in `src/codereviewer/core`, not in individual surfaces.

## Core capabilities
- Review job submission and execution
- Structured findings and summary output
- Runtime profile management
- Provider/model configuration as first-class UX
- Reusable core for multi-surface clients

## Core architecture decision
Claude Agent SDK remains the core agent architecture decision behind the reviewer adapter boundary; surfaces should integrate through typed contracts without replacing that primary architecture.
