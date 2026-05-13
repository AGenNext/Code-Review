# AGenNext CodeReview Release and Deployment Checklist

Use this checklist before promoting AGenNext CodeReview to production or cutting a release.

## 1. Source control readiness

- [ ] All production changes are merged through reviewed pull requests.
- [ ] `main` is up to date and protected by required checks.
- [ ] No secrets, credentials, tokens, or private keys are committed.
- [ ] `.env.example` is current and contains only non-secret placeholders.
- [ ] Release notes are drafted from merged PRs and issue references.

## 2. CI/CD validation

Required checks before release:

- [ ] Pytest passes.
- [ ] Coverage gate passes.
- [ ] Ruff linting passes.
- [ ] Package build passes with `python -m build`.
- [ ] Docker image build passes.
- [ ] Container smoke test passes against `/healthz`.
- [ ] Bandit security scan passes or accepted findings are documented.
- [ ] pip-audit passes or accepted findings are documented.
- [ ] Trivy container scan passes for HIGH/CRITICAL vulnerabilities or accepted findings are documented.
- [ ] CodeQL completes without unresolved high-risk findings.
- [ ] SBOM artifact is generated and retained.

## 3. Runtime configuration

Validate production environment variables before deployment:

- [ ] `HOST=0.0.0.0`
- [ ] `PORT=8080`
- [ ] `PYTHONPATH=/app/src` when required by the deployment platform.
- [ ] `CODEREVIEWER_DB_PATH` points to persistent storage.
- [ ] `SECURITY_HARDENING_ENABLED=true`
- [ ] `API_BEARER_AUTH_ENABLED=true` for production API routes.
- [ ] `API_BEARER_TOKEN` is stored in platform secrets, not source control.
- [ ] `MULTITENANCY_REQUIRE_AGENT_IDENTITY` is set according to tenant policy.
- [ ] Claude/LiteLLM provider settings are configured only through secrets or runtime profile references.
- [ ] SMTP, notifications, SSO, telemetry, and monitoring settings are configured when required.

## 4. Container deployment validation

- [ ] Image is built from the release commit.
- [ ] Image tag is immutable and recorded in release notes.
- [ ] Container starts successfully.
- [ ] Container binds to port `8080`.
- [ ] Health check returns HTTP 200 from `/healthz`.
- [ ] Logs show no startup exceptions.
- [ ] SQLite data path is mounted to persistent storage when using SQLite.
- [ ] Resource limits are configured in the host/platform.

## 5. Coolify deployment validation

Recommended Coolify settings:

- [ ] Image: `agentnext/code-reviewer:<release-tag>` or approved immutable digest.
- [ ] Container port: `8080`.
- [ ] Domain: `codereviewer.agnxxt.com` or approved environment domain.
- [ ] TLS is enabled through Let's Encrypt.
- [ ] Health check path: `/healthz`.
- [ ] Required environment variables are present.
- [ ] Secrets are configured through Coolify secrets/environment management.
- [ ] Deployment logs are reviewed after rollout.

## 6. API smoke tests

Run after deployment:

- [ ] `GET /healthz` returns `200`.
- [ ] `GET /` loads the landing page.
- [ ] `GET /app` loads the web console.
- [ ] Auth-protected `/api/*` routes reject unauthenticated requests when bearer auth is enabled.
- [ ] Auth-protected `/api/*` routes accept valid bearer token requests.
- [ ] Review submission flow creates a queued/running/completed or failed job with traceable status.
- [ ] Runtime profile endpoint validates provider/model compatibility.
- [ ] Feedback endpoint records expected events.

## 7. Security and compliance

- [ ] Confirm hardened response headers are enabled.
- [ ] Confirm API auth is enabled for production.
- [ ] Confirm tenant header validation is enforced.
- [ ] Confirm action IDs and trace metadata are present in logs.
- [ ] Confirm `agent_id` is logged for agent-triggered actions.
- [ ] Confirm SBOM is stored with the release artifact.
- [ ] Confirm vulnerability exceptions, if any, have owner and expiry date.

## 8. Observability

- [ ] Application logs are visible from the deployment platform.
- [ ] Error monitoring is configured.
- [ ] Telemetry endpoint is configured when enabled.
- [ ] Notification test endpoint succeeds when notifications are enabled.
- [ ] Alert routing is configured for deployment failures and service downtime.

## 9. Rollback plan

Before rollout:

- [ ] Previous stable image tag or digest is recorded.
- [ ] Database backup/snapshot exists if persistent data is used.
- [ ] Rollback command/path is documented for the deployment platform.
- [ ] Owner is assigned for rollback decision.

Rollback trigger examples:

- Health check failure after deployment.
- Auth regression.
- Review jobs cannot be created or retrieved.
- Startup crashes or repeated container restarts.
- High-severity security finding introduced by the release.

## 10. Release approval

- [ ] CI/CD owner approval.
- [ ] Security owner approval for unresolved findings, if any.
- [ ] Product owner approval for release scope.
- [ ] Deployment owner approval for production rollout.

## Post-release follow-up

- [ ] Monitor logs and health checks after deployment.
- [ ] Confirm issue tracker is updated with release status.
- [ ] Close completed release checklist issue.
- [ ] File follow-up issues for deferred risks or improvements.
