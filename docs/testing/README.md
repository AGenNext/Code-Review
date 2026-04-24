# CodeReviewer Testing Documentation

This folder defines the test policy and standard operating procedures (SOPs) for CodeReviewer.

## Documents
- `docs/testing/test-case-policy.md`
- `docs/testing/vulnerability-testing-sop.md`
- `docs/testing/integration-testing-sop.md`
- `docs/testing/smoke-testing-sop.md`
- `docs/testing/e2e-testing-sop.md`

## Execution order (recommended)
1. Smoke test
2. Integration tests
3. Vulnerability checks
4. End-to-end tests

## Evidence requirements
- Save command outputs in CI logs or release notes.
- Record failures with reproduction steps and owner.
- Do not mark release-ready unless critical test gates pass.
