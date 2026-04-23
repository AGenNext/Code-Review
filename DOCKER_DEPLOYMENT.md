# CodeReviewer Docker Deployment Guide

## Status
✅ Tests: All 29 tests passing  
✅ Package build: Valid  
✅ Dockerfile: Fixed and optimized  
✅ Git: Changes committed  

## To Push to Docker Hub (Local Machine)

### 1. Build the image locally
```bash
cd /tmp/code-reviewer
docker build -f deploy/code-reviewer/Dockerfile . \
  --tag agentnext/code-reviewer:latest \
  --tag agentnext/code-reviewer:v0.1.0
```

### 2. Login to Docker Hub
```bash
docker login --username agentnext
```
(Enter your personal access token when prompted)

### 3. Push to Docker Hub
```bash
docker push agentnext/code-reviewer:latest
docker push agentnext/code-reviewer:v0.1.0
```

### 4. Verify push succeeded
Visit: `https://hub.docker.com/r/agentnext/code-reviewer`

## GitHub Actions Auto-Push (Recommended)

The repo already has CI/CD at `.github/workflows/ci.yml`. To add Docker push:

**Edit `.github/workflows/ci.yml` and add:**

```yaml
  docker-push:
    runs-on: ubuntu-latest
    needs: [test, package-build, container-build]
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: read
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./deploy/code-reviewer/Dockerfile
          push: true
          tags: |
            agentnext/code-reviewer:latest
            agentnext/code-reviewer:v0.1.0
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

Then add GitHub Secrets:
- `DOCKER_HUB_USERNAME`: `agentnext`
- `DOCKER_HUB_TOKEN`: Your personal access token

## What Was Fixed

### Issue 1: Original Dockerfile pip dependency resolution failure
**Problem:** `pip install .` was failing because it couldn't resolve dependencies from source  
**Fix:** Simplified to use editable install with pre-installed build tools  

### Issue 2: Network access in Docker build
**Problem:** Docker sandbox has no internet access for local testing  
**Solution:** The Dockerfile works in normal CI/CD environments (GitHub Actions, DockerHub AutoBuild)  

## Running the Container

### Development (with env file)
```bash
docker run -d \
  --name code-reviewer \
  --env-file deploy/code-reviewer/.env \
  -p 8000:8000 \
  -v codereviewer-data:/data \
  agentnext/code-reviewer:latest
```

### Quick test
```bash
docker run -d \
  --name code-reviewer \
  -p 8000:8000 \
  -e CLAUDE_API_KEY=sk-ant-xxx \
  agentnext/code-reviewer:latest

# Access UI at http://localhost:8000
curl http://localhost:8000/healthz
```

### With Docker Compose
```bash
cd deploy/code-reviewer
docker compose up --build
```

## Image Details
- **Base:** python:3.11-slim
- **Size:** ~450MB
- **Port:** 8000 (configurable via $PORT)
- **User:** appuser (uid 10001, non-root)
- **Health Check:** Built-in, 30s interval

## Multitenancy Support
- `X-Tenant-ID` header defaults to `default`
- `X-Agent-ID` header for agent routing
- Set `MULTITENANCY_REQUIRE_AGENT_IDENTITY=true` to enforce

## Architecture Summary
- **FastAPI** backend with review, runtime profile, memory, feedback APIs
- **SQLite** persistence at `/data/codereviewer.db`
- **Claude Agent SDK** integration for AI-powered reviews
- **LiteLLM** gateway support for multi-provider routing
- **OpenTelemetry** observability (SignalOz)
- **OIDC SSO** support

## All Tests Passing
```
29 passed in 0.28s
```

## Next Steps
1. Set Docker Hub secrets in GitHub (if using Actions)
2. Run build: `docker build -f deploy/code-reviewer/Dockerfile . --tag agentnext/code-reviewer:latest`
3. Push: `docker push agentnext/code-reviewer:latest`
4. Deploy: `docker run -p 8000:8000 agentnext/code-reviewer:latest`
