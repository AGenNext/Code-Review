# Test Case Policy

## Objective
Define a minimum quality bar for test coverage and test design before merge/deploy.

## Scope
- Backend API behavior
- Core domain logic (`src/codereviewer/core`)
- Persistence flows and review lifecycle transitions
- Operational checks (smoke, integration, vulnerability, e2e)

## Test case requirements
- Each new feature must include:
  - At least one happy-path test
  - At least one failure-path test
  - Input validation test coverage where applicable
- Each bug fix must include a regression test that fails before and passes after the fix.
- Changes to state transitions must explicitly test `queued`, `running`, `completed`, and `failed` paths where relevant.

## Quality criteria
- Tests must be deterministic and isolated.
- Avoid hidden external dependencies unless test type explicitly requires them.
- Prefer typed test data and explicit assertions over snapshot-only checks.

## Merge gate policy
- Unit/integration test suite must pass in CI.
- Smoke test must pass on deployed artifact.
- High/Critical vulnerability findings must be triaged before production rollout.
- E2E critical-path checks must pass for release tags.

## Ownership and feedback
- PR owner is responsible for test completeness.
- Reviewers must block merges when required test categories are missing.
- Repeated test gaps should be converted into reusable instructions in `openautonomyx/common-instructions`.
