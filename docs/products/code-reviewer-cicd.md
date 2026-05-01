# AGenNext CodeReview CI/CD and Automation

## CI workflow location
- `.github/workflows/ci.yml`

## What CI validates
1. Installs dependencies with Python 3.11.
2. Runs test suite using `pytest -q`.
3. Builds distributable package with `python -m build`.
4. Validates container build with `docker build -f deploy/code-reviewer/Dockerfile .`.

## Local parity commands
```bash
pip install -e .[dev]
pytest -q
python -m build
docker build -f deploy/code-reviewer/Dockerfile .
```

## Test execution notes
- Test suite path: `tests/`.
- API integration checks use FastAPI `TestClient` and local SQLite.
- Tests are designed to run without external managed services.

## Operational caveats
- CI validates build and test integrity, not production deployment orchestration.
- No release publishing workflow is configured yet.
- No secret-scanning or dependency-scanning workflow is configured yet.
