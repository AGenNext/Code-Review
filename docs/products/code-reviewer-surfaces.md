# AgentNxt CodeReviewer Surfaces

This document defines every named product surface, its current status, and how each surface must depend on the shared core.

## Status legend
- **implemented**: runnable, user-facing product surface code exists in this repository.
- **scaffolded**: adapter boundary and workflow intent are documented; substantial implementation is pending.
- **planned**: surface direction is defined, with only minimal scaffolding.

## AgentNxt CodeReviewer Web
- **Purpose**: Primary production UI and API surface for review execution and results.
- **Intended user/workflow**: Engineers and reviewers submit jobs, inspect findings, and manage runtime profiles.
- **Current status**: **implemented**.
- **Relationship to shared core**: Uses shared domain models/logic in `src/codereviewer/core` through API/service layers.
- **Major planned capabilities**: Persistent storage, authN/authZ, richer policy and telemetry.
- **Already present in repo**: FastAPI endpoints, review/runtime services, web UI module.
- **Not yet implemented**: Persistent datastore, queue workers, full production security envelope.

## AgentNxt CodeReviewer Desktop
- **Purpose**: Local-first companion client for repository-adjacent review workflows that benefit from desktop runtime controls.
- **Intended user/workflow**: Developers/security reviewers run and inspect reviews close to local repositories and enterprise environments.
- **Current status**: **scaffolded**.
- **Relationship to shared core**: Must call shared API contracts and avoid any duplicated domain logic; `src/codereviewer/core` remains source of truth.
- **Major planned capabilities**: Local repository session management, richer diff visualization, local credentials integration.
- **Already present in repo**: Surface adapter README in `apps/desktop/README.md` documenting scope and next steps.
- **Not yet implemented**: Desktop application code, packaging pipeline, release/distribution automation.

### Desktop-specific definition
- **Why Desktop exists**: To support repo-adjacent workflows where local context and controlled runtime are more practical than browser-only usage.
- **How Desktop differs from Web / Cloud**: Desktop prioritizes local execution ergonomics and native packaging while Web / Cloud remains centralized and browser-based.
- **Intended runtime/packaging model**: Packaged desktop client (for example, a native shell around typed API calls) with signed release artifacts.
- **Likely local/offline role**: Local repository context capture and queued review execution with intermittent connectivity tolerance.
- **Current implementation status**: Surface is documented and scaffolded only; no desktop runtime has been implemented yet.

## AgentNxt CodeReviewer Mobile
- **Purpose**: Mobile triage and lightweight approval surface for asynchronous review operations.
- **Intended user/workflow**: On-call leads and reviewers quickly inspect critical findings and approve/escalate.
- **Current status**: **scaffolded**.
- **Relationship to shared core**: Consumes typed API contracts produced by shared services/core.
- **Major planned capabilities**: Push alerts, high-severity triage queue, compact finding views.
- **Already present in repo**: Surface adapter README in `apps/mobile/README.md`.
- **Not yet implemented**: Mobile app code, auth/session flows, distribution pipeline.

## AgentNxt CodeReviewer VS Code
- **Purpose**: In-editor code review assistance aligned with pull request and local branch context.
- **Intended user/workflow**: Developers receive findings and remediation hints without leaving the IDE.
- **Current status**: **scaffolded**.
- **Relationship to shared core**: Extension should call backend APIs and reuse shared finding types.
- **Major planned capabilities**: Inline diagnostics, quick fixes, review-on-save/commit hooks.
- **Already present in repo**: Surface adapter README in `apps/vscode/README.md`.
- **Not yet implemented**: Extension runtime, diagnostics provider, publishing setup.

## AgentNxt CodeReviewer Slack
- **Purpose**: Team collaboration surface for notifications and digest-style review summaries.
- **Intended user/workflow**: Teams monitor review outcomes and route follow-up actions in channels.
- **Current status**: **scaffolded**.
- **Relationship to shared core**: Slack adapter remains transport/UI only; findings semantics stay in shared core.
- **Major planned capabilities**: Alert routing, mention-based triage commands, scheduled digests.
- **Already present in repo**: Surface adapter README in `apps/slack/README.md`.
- **Not yet implemented**: Slack app/bot integration code, signing/verification and install flow.

## AgentNxt CodeReviewer GitHub
- **Purpose**: Native pull-request and check-run integration surface.
- **Intended user/workflow**: Repositories receive automated checks/status and structured review output directly in PR workflows.
- **Current status**: **scaffolded**.
- **Relationship to shared core**: GitHub integration maps shared findings into GitHub checks/comments, without forking review logic.
- **Major planned capabilities**: Check runs, commit status gating, PR annotations.
- **Already present in repo**: Surface adapter README in `apps/github/README.md`.
- **Not yet implemented**: GitHub App implementation, webhook handling, permissions hardening.

## AgentNxt CodeReviewer Chrome
- **Purpose**: Browser-assist surface for contextual capture and quick handoff into review flows.
- **Intended user/workflow**: Users capture code-review context from browser-hosted developer tools.
- **Current status**: **planned** (minimal scaffold).
- **Relationship to shared core**: Extension must send captured context to typed backend APIs; shared core remains authoritative.
- **Major planned capabilities**: Context capture, one-click review submission, lightweight finding overlays.
- **Already present in repo**: Planning boundary README in `apps/chrome/README.md`.
- **Not yet implemented**: Extension codebase, manifest/runtime integration, store packaging.
