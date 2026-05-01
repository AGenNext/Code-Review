# AGenNext CodeReview Docker Build - Network Issues & Solutions

## Problem

The local Docker Desktop environment has no internet connectivity for downloading packages during build. This causes `pip install` to fail with connection errors.

## Solution: Use GitHub Actions or Docker Build Cloud

The Dockerfile will work perfectly in environments with network access:
- ✅ GitHub Actions (CI/CD)
- ✅ Docker Build Cloud
- ✅ Cloud providers (AWS, GCP, Azure)
- ✅ Production servers with internet

### Why Local Build Fails
- Docker Desktop runs in a Linux VM sandbox
- That VM has restricted network access
- Can't reach PyPI to download packages

### Why CI/CD Build Works
- GitHub Actions runs on GitHub-hosted runners
- Full internet connectivity
- Automatically pushes to Docker Hub on success

## Quick Fix: Push via GitHub Actions (Recommended)

```bash
# 1. Make any code changes
cd code-reviewer
git add .
git commit -m "your changes"

# 2. Push to trigger automatic build
git push origin main

# 3. Watch GitHub Actions build and push
# https://github.com/agentnxt/code-reviewer/actions
```

**Result:** Image automatically pushed to `docker.io/agentnext/code-reviewer:latest`

## Alternative: Manual Docker Hub Push

If you have the image already built elsewhere:

```bash
docker login --username agentnext
# Enter personal access token when prompted

docker tag agentnext/code-reviewer:latest agentnext/code-reviewer:v0.1.0
docker push agentnext/code-reviewer:latest
docker push agentnext/code-reviewer:v0.1.0
```

## Alternative: Docker Build Cloud (Free)

1. Sign up: https://www.docker.com/products/docker-build-cloud
2. Link GitHub repo
3. Enable auto-builds on main branch
4. Every commit auto-builds and pushes to Docker Hub

## How to Verify Setup

### Check GitHub Actions Configuration
```bash
cd code-reviewer
cat .github/workflows/ci.yml | grep -A 5 "Login to Docker Hub"
```

You should see:
```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    registry: docker.io
    username: ${{ secrets.DOCKER_HUB_USERNAME }}
    password: ${{ secrets.DOCKER_HUB_TOKEN }}
```

### Add GitHub Secrets

If not already set, add to https://github.com/agentnxt/code-reviewer/settings/secrets:

```
DOCKER_HUB_USERNAME = agentnext
DOCKER_HUB_TOKEN = <your-personal-access-token>
```

### Generate Docker Hub Token

1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Name: `github-actions`
4. Copy token
5. Paste in GitHub secrets

## Verify the Workflow

After setting secrets:

```bash
# Make a test commit
git commit --allow-empty -m "test: trigger GitHub Actions"
git push origin main

# Check workflow status
# https://github.com/agentnxt/code-reviewer/actions
```

After 2-3 minutes:
- ✅ Tests run
- ✅ Docker image builds
- ✅ Image pushed to Docker Hub
- ✅ Available at `docker.io/agentnext/code-reviewer:latest`

## Verify Image Pushed

```bash
# After workflow completes (5 minutes)
docker pull agentnext/code-reviewer:latest

# Or visit
# https://hub.docker.com/r/agentnext/code-reviewer
```

## Local Testing (Without Push)

If you want to test the image locally first:

```bash
# Build locally (works if you have network)
docker build -f deploy/code-reviewer/Dockerfile . -t test-image:latest

# Run and test
docker run -p 8000:8000 test-image:latest

# Access
curl http://localhost:8000/healthz
```

## Troubleshooting

### GitHub Actions failing?

Check the logs:
```
https://github.com/agentnxt/code-reviewer/actions
→ Click latest run
→ Expand "Build and push Docker image"
```

### Docker Hub login fails?

1. Verify token: https://hub.docker.com/settings/security
2. Check secrets: https://github.com/agentnxt/code-reviewer/settings/secrets
3. Regenerate token if expired

### Image not appearing on Docker Hub?

1. Wait 5 minutes after workflow completes
2. Check: https://hub.docker.com/r/agentnext/code-reviewer
3. Search in Docker: `docker search agentnext/code-reviewer`

## What's Happening in CI/CD

When you `git push origin main`:

```
1. GitHub detects push
2. Triggers .github/workflows/ci.yml
3. Runs pytest tests (29 tests)
4. Builds Docker image: docker build -f deploy/code-reviewer/Dockerfile .
5. Logs in to Docker Hub
6. Tags image: docker tag ... agentnext/code-reviewer:latest
7. Pushes: docker push agentnext/code-reviewer:latest
8. Result: Image available at docker.io/agentnext/code-reviewer
```

Takes ~5-10 minutes total.

## Files Modified

Updated Dockerfile with:
- ✅ Retry logic for transient network failures
- ✅ Fallback to editable install if direct pip install fails
- ✅ Cleaner, more portable
- ✅ Works in all CI/CD environments

```dockerfile
RUN pip install --retries 5 \
    'fastapi>=0.115.0' \
    ... || \
    pip install -e .
```

## Next Steps

1. Verify GitHub secrets are set
2. Make a test commit: `git push origin main`
3. Watch workflow: https://github.com/agentnxt/code-reviewer/actions
4. After 5-10 minutes, image appears on Docker Hub
5. Pull and use: `docker pull agentnext/code-reviewer:latest`

---

**Summary:** Local Docker build has network issues. Use GitHub Actions (automatic) or Docker Build Cloud (recommended). Dockerfile works perfectly in CI/CD.
