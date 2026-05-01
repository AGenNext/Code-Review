# AGenNext CodeReview Deployment Policy

## Policy statement
All deployments must be executed through approved CI/CD pipelines.

Direct server deployments (manual SSH deploys, ad-hoc `docker run`, manual artifact mutation on production hosts) are not allowed for production environments.

## Mandatory rules
1. CI/CD-only release path
- Build, test, scan, and deploy must run from versioned pipeline definitions.
- Deployment artifacts must be traceable to commit SHA and immutable image tags.

2. No direct production server deploys
- No manual container/image updates directly on production hosts.
- No bypass of release gates or approval checks.

3. Required release gates
- Test suite pass (unit + integration at minimum).
- Vulnerability checks completed and triaged.
- Smoke test after deployment.
- E2E critical path checks for release promotions.

4. Rollback readiness
- Every deploy must have a defined rollback artifact/tag.
- Rollback steps must be documented and tested.

5. Auditability
- Keep deployment logs, approver history, artifact digests, and environment target records.

## Best practices
- Use immutable tags (`<commit-sha>`) in addition to convenience tags (`latest`, `main`).
- Promote the same artifact across environments; do not rebuild per environment.
- Use environment-specific config only via managed secrets/variables.
- Enforce least privilege for CI/CD credentials.
- Use staged rollout where possible (canary/blue-green) and verify health gates.

## Exceptions
Any exception to CI/CD-only deployment must be time-bound, incident-justified, approved, and documented post-incident.

## Mandatory service integrations
Production deployments must verify availability/configuration of:
- SSO
- Mail
- Notifications
- Error monitoring
- Telemetry
- Analytics

Deployments are non-compliant if these integrations are absent without an approved exception.

## Role requirement: code-deploy
`code-deploy` must implement deployment through CI/CD configuration and pipeline execution.
Direct manual production deployment does not satisfy this role requirement.

## Registry publish gate
Registry publish actions must be executed only by approved GitHub workflow runs after PR review and merge.
Manual or out-of-band publish actions are non-compliant.
