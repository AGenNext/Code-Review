# Integration Testing SOP

## Objective
Validate interactions across API, services, and persistence boundaries.

## Scope
- API routes and request/response models
- Repository interactions (SQLite)
- Review lifecycle orchestration

## Preconditions
- Python 3.11+
- Test environment with writable filesystem

## Procedure
1. Install test dependencies
```bash
pip install -e .[dev]
```
2. Run integration-focused tests (or full suite when split markers are not available)
```bash
pytest -q
```
3. Validate lifecycle transitions in test output/logs for review jobs.
4. Verify `/healthz` and key API routes in local run if needed.

## Pass/Fail criteria
- All integration tests pass.
- No unexpected state transition failures.
- No schema/contract regression in API responses.

## Evidence
- CI job link
- Test command and summary (`passed/failed/skipped`)
