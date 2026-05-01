# AGENTS: AGenNext CodeReview

## Repo identity
- Org: `agentnxt`
- Repo: `code-reviewer`
- Product display name: `CodeReviewer`
- Product repo slug: `code-reviewer`

## Working rules
- Treat this repository root as the only working root.
- Do not create nested org folders or scaffold sibling repos inside this repository.
- Keep product-first naming for surfaces: `CodeReviewer Web`, `CodeReviewer Desktop`, `CodeReviewer Mobile`, `CodeReviewer VS Code`, `CodeReviewer Slack`, `CodeReviewer GitHub`, `CodeReviewer Chrome`.
- Do not introduce shorthand variants such as `coderev`.
- Maintain shared-core-first architecture: domain logic belongs in `src/codereviewer/core`.
- Keep backend contracts typed via Pydantic models.

## Architecture rules
- Use Claude Agent SDK as the core agent architecture for this product.
- Keep provider selection separate from model selection in API and UI.
- Preserve support for providers: `anthropic`, `bedrock`, `vertex`, `foundry`.
- Do not present scaffolded surfaces as implemented products.
- Surface-specific folders are not sufficient documentation by themselves.

## Documentation rules
- The root `README.md` must include a surface status matrix.
- Every named surface must be explicitly labeled as one of: `implemented`, `scaffolded`, or `planned`.
- Every named surface must be documented in product or architecture docs, not only represented by folder stubs.
- Desktop must be described explicitly when named, including purpose, status, and intended runtime model.
- Prompts and docs must distinguish clearly between `build now` work and `architecture only` work.
- When naming matters, state org, repo, path, and product name separately.
- If a name is a deliberate choice, treat it as locked unless changed explicitly in the source of truth.

## Coding conventions
- Python code should be typed and test-covered.
- Keep changes small, explicit, and reviewable.
- Avoid vague placeholders when a concrete status or boundary can be stated.

## Testing
- Run `pytest` for all changes.
- If tests cannot run, document the exact reason and the exact missing dependency or environment constraint.

## Deployment baseline
- Preferred deployment path: Coolify with GHCR image.
- Preferred public hostname: `codereviewer.agnxxt.com`.
- TLS must be enabled with Let's Encrypt via Coolify/Traefik.
- Runtime env must include `PYTHONPATH=/app/src` and `PORT=8080` for container startup.
- Health endpoint contract: `GET /healthz` returns HTTP 200 and `{"status":"ok"}`.

## Deployment rules (common-instructions aligned)
1. Keep deployment instructions explicit, repo-specific, and execution-oriented.
2. Use clear in-scope/out-of-scope boundaries for operational docs.
3. Do not include org-wide platform policy in this repo; reference source repos when needed.
4. Record required runtime env and health endpoint contract whenever deployment docs are updated.

## Common-instructions feedback loop
- For any reusable instruction/prompt/process improvement discovered in this repo, create or update an equivalent artifact in `openautonomyx/common-instructions`.
- Treat shared-instruction extraction as default behavior, not an optional step.
- When the improvement is repo-specific, capture the shared core pattern in `common-instructions` and keep only repo-local details here.

## Skill feedback loop
- When repeated operator/user friction appears, propose a reusable skill-level instruction update.
- Capture the improvement as a concise feedback note and upstream it to `openautonomyx/common-instructions` when broadly reusable.
- Keep repo-specific implementation details local; upstream only the reusable instruction pattern.

## Prompt registry
- Maintain a lightweight prompt registry for this repo's recurring operational prompts.
- When a prompt becomes reusable across repositories, add or update it in `openautonomyx/common-instructions` and reference it from this repo.
- Keep prompt entries explicit: purpose, trigger, required inputs, expected output contract.

## Subagent review evaluation and feedback
- For every subagent contribution reviewed by CodeReviewer, produce an explicit per-subagent evaluation record.
- Each record must include: subagent identifier, change scope, decision summary, critical findings, and required follow-up actions.
- Provide actionable feedback for each subagent reviewed, not only aggregate feedback.
- Capture recurring subagent quality patterns and upstream reusable guidance to `openautonomyx/common-instructions`.

## Deployment policy enforcement
- Enforce CI/CD-only production deployments.
- Reject direct server deployment workflows for production.
- Require test, vulnerability, smoke, and release-gate evidence in pipeline outputs.

## Execution discipline
1. No context switching during active execution unless explicitly reprioritized.
2. Maintain strict priority order from the active task list.
3. Keep an explicit task list with statuses (`pending`, `in_progress`, `blocked`, `done`).
4. For long-running tasks, spin off a background job/process and continue foreground work.
5. Rejoin background tasks only at defined checkpoints or when they become blocking.

## Communication rules
1. Be concise and to the point.
2. Speak after research/verification, not before.
3. If requirements are unclear, ask a clarifying question instead of guessing.
4. Before asking a question, check available past memory/context in repo artifacts and prior run notes.

## Dynamic context handling
- Reuse established session context, prior decisions, and task state by default.
- Do not require users to restate stable context on every call.
- Ask for context only when missing, conflicting, or stale.
- When context changes, record the delta explicitly and continue with updated state.

## Project status tracking
- Always keep project status updated in a GitHub-native tracker.
- Default tracker is `PROJECT_STATUS.md` at repository root.
- Optionally mirror status to GitHub Projects, but do not let them drift.
- Update tracker on each material status change (at least: priority, owner, status, updated timestamp, blocker notes).

## Service consolidation rule
- Always consolidate services and avoid duplicate service deployments/components.
- Before adding a new service, verify whether an existing service can be extended.
- Reject parallel duplicate implementations unless explicitly approved with a migration/deprecation plan.

## Pre-task model recommendation
- Before starting any new task, recommend the best-fit LLM model first.
- Recommendation must optimize for: cost-effectiveness, speed, and benchmark quality.
- State one primary recommendation and optional fallback.
- Do not begin execution of a new task until model recommendation is provided.

## Pre-project deep research rule
- Before starting any new project, perform deep research to determine the best implementation approach.
- Compare at least: architecture options, delivery risk, cost/speed tradeoffs, and operational complexity.
- Document recommendation rationale before execution begins.
- Do not start project execution until research findings and chosen approach are stated.

## Reuse-first rule
- Do not reinvent the wheel.
- Prefer proven existing libraries, services, and patterns before creating new implementations.
- Build custom solutions only when reuse options are insufficient and document the justification.

## Repository governance standard
- Keep repos clean and structured.
- Enforce one product per repository.
- Required artifacts per product repo: PRD, design doc, HLD, DB schema doc, prompt docs/registry, and seed-data spec/scripts (when applicable).
- Keep all env variables declared in env templates (for example `.env.example`) with safe defaults from deployed-service baselines where possible.
- Store secrets only in approved secret manager; never commit secrets.

## Mandatory deployed-service baseline
- Every deployed production service must include: SSO, mail, notifications, error monitoring, telemetry, and analytics.
- Treat these as required deployment gates unless a documented exception is approved.

## Code-deploy responsibility
- `code-deploy` must configure and maintain CI/CD pipelines for deployment.
- Manual production deployment is not part of `code-deploy` execution path.

## Multi-agent responsibility model
- `code-assist` is responsible for drafting and maintaining all required project documentation.
- `code-reviewer` must review PRD, HLD, LLD, and code changes.
- `code-tester` must validate documentation quality/completeness in addition to test execution.
- Reviewer outputs must include teacher-style guidance to improve subagent skills, not only pass/fail judgments.

## Logging and traceability rule
- Keep logs of all reviews.
- Assign an action ID to every operation.
- Attach trace metadata to all workflow actions for end-to-end observability.

## Agent identity logging
- Include `agent_id` in every review and action log record.

## Identifier and version rule
- Require unique IDs and explicit versioning for mutable entities.

## Registry-first execution rule
- Always fetch from registry first.
- If not present, add to the relevant registry first (model registry, skill registry, prompt registry, service/image registry), then use.

## Canonical registry IDs
- Use canonical registry IDs as the source-of-truth identifiers for all registry-resolved items.

## Registry publish rule
- Do not publish directly to registries.
- Publish only through GitHub-reviewed PR flow and CI workflow execution.
