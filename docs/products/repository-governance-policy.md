# Repository Governance Policy

## Policy objective
Keep repositories clean, structured, and production-operable by enforcing a consistent one-product-per-repo model and standard artifact layout.

## Core rules
1. One product = one repository.
2. Repositories must stay clean, intentionally structured, and documentation-complete.
3. Product repos must include required architecture and operations artifacts.

## Required repository artifact set
Each product repository must contain and maintain:
- PRD (Product Requirements Document)
- Design document
- HLD (High-Level Design)
- Database schema documentation
- Prompt registry/prompt docs
- Seed data specification or seed scripts (when applicable)

## Environment and secret handling
- All environment variables must be declared in environment files (for example `.env.example`, deployment env templates).
- Default values should be derived from deployed service defaults where applicable.
- Secrets must not be committed to git.
- Secrets must be managed via approved secret manager (for example cloud secret manager or platform-managed secret store).

## Repository structure baseline (recommended)
- `docs/products/` for product-level docs (PRD, design, HLD, operations, API)
- `docs/testing/` for test policies and SOPs
- `src/` for implementation
- `deploy/` for deployment assets
- `prompts/` or documented prompt registry references
- `seed/` or documented seed-data process

## Compliance checklist
- [ ] Single product ownership is explicit in README.
- [ ] PRD, design doc, and HLD are present and current.
- [ ] Database schema documentation is present.
- [ ] Prompt documentation/registry is present.
- [ ] Seed data artifacts/specs are present (if applicable).
- [ ] `.env.example` (or equivalent) includes all required variables.
- [ ] Secrets are stored only in secret manager.
- [ ] Deployment docs reference CI/CD-only production policy.

## Mandatory production service capabilities
Every deployed production service must include or integrate with:
- SSO (authentication/identity)
- Mail delivery capability
- Notification channel support
- Error monitoring
- Telemetry (logs/metrics/traces)
- Analytics instrumentation

These are baseline requirements, not optional enhancements.

## Review and documentation role policy
- Documentation authorship baseline: `code-assist`.
- Review baseline: `code-reviewer` must review PRD/HLD/LLD and implementation changes.
- Validation baseline: `code-tester` validates documentation quality and consistency.
- Review outputs should include educational feedback for subagents (what to improve and why).

## Audit and traceability policy
- Keep a persistent log of all reviews.
- Every action must have a unique action ID.
- Every workflow must carry trace metadata for end-to-end correlation.
- Logs must be queryable by review ID, action ID, and trace ID.

## Agent identifier policy
- `agent_id` is mandatory for all review/action audit records.
- Audit queries must support filtering by `agent_id` in addition to review/action/trace identifiers.

## Identifier and versioning policy
- Every persisted entity and workflow event must have a unique identifier.
- Every mutable entity must include an explicit `version` field.
- Version must increment on each state/content change.
- Audit logs must record both identifier and version for every action.

## Registry-first policy
- All runtime dependencies and reusable capabilities must be resolved from an approved registry first.
- If an item is missing, register it in the appropriate registry before use.
- Registries include (at minimum): model registry, skill registry, prompt registry, and service/image registry.
- Direct ad-hoc usage without registry entry is non-compliant except for approved emergency exceptions.

## Canonical registry ID policy
- Every registry entry must have a canonical ID.
- Canonical IDs must be stable, unique, and used as the primary reference key across systems.
- Human-readable names are optional aliases and must not replace canonical IDs in automation.

## Registry publishing control policy
- Publishing to any registry must go through GitHub review process.
- Required path: pull request review/approval -> protected branch merge -> CI/CD publish workflow.
- Direct/manual registry publishing is prohibited for production registries.
