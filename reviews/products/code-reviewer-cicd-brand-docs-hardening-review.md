# CodeReviewer CI/CD + Brand + Docs Hardening Review

## What was added
- Added GitHub Actions CI baseline (`.github/workflows/ci.yml`) with test, package build, and container build validation jobs.
- Added a dedicated API reference document (`docs/products/code-reviewer-api.md`).
- Added CI/test automation documentation (`docs/products/code-reviewer-cicd.md`).
- Added a branded landing page and split web console routing (`/` landing, `/app` console).
- Added static brand assets (`logo.svg`, `favicon.svg`) and consistent title/favicon usage.

## What was corrected
- Clarified product entry points in root README.
- Replaced single-page root UI with explicit landing-page-first product entry.
- Normalized branding strings to `CodeReviewer`.
- Removed ambiguous API discoverability by documenting endpoint-level behavior and errors.

## CI/CD decisions made
- Single workflow file with separate jobs for test, package build, and container validation.
- Python 3.11 fixed in CI to align with `pyproject.toml` minimum runtime.
- Container build validation included because real Docker assets already exist in `deploy/code-reviewer/`.

## Test automation decisions made
- Stable command standardized to `pytest -q`.
- Dependency installation standardized to `pip install -e .[dev]`.
- Test path documented in both README and CI/CD docs for local/CI parity.

## API documentation improvements made
- Added endpoint inventory covering providers, models, runtime profiles, reviews, memory, and feedback.
- Added request/response examples for runtime profile creation and review submission.
- Documented error semantics (`400`, `404`, `422`) and auth status truthfully.

## Landing page decisions made
- Landing page is now a distinct product entry surface with capabilities, surface status, and entry links.
- Web console remains implemented and accessible at `/app`.

## Brand/logo asset decisions made
- Introduced in-repo SVG logo and favicon placeholders under `src/codereviewer/web/static/`.
- Standardized title/icon references across landing page and web console.
- Brand source remains local static assets (no external broken URLs).

## Remaining gaps
- API authentication/authorization is still not implemented.
- No deployment workflow (only build/test validation).
- No artifact publishing/release tagging automation.
- No automated security/dependency scanning workflow yet.

## Common-layer reusable standards identified
1. Require each product repo to include a CI baseline that validates tests + package build + container build when Docker assets exist.
2. Require a dedicated API reference file tied explicitly to typed contract modules.
3. Require a distinct product landing route separate from internal operator UI.
4. Require local static brand assets over external URLs unless an approved asset host exists.
