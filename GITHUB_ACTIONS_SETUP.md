# GitHub Actions Setup - Docker Hub Auto-Push

## ✅ Your Setup Information

**GitHub Repo:** https://github.com/agentnxt/code-reviewer
**Docker Hub Username:** `agentnext`
**Docker Hub Token:** (See your hub.docker.com/settings/security - never commit tokens!)

## Add GitHub Secrets (2 minutes)

### Method 1: GitHub Web UI (Recommended)

**Step 1: Go to Settings → Secrets**
```
https://github.com/agentnxt/code-reviewer/settings/secrets/actions
```

**Step 2: Click "New repository secret"**

**Step 3: Add Secret #1 - Username**
```
Name: DOCKER_HUB_USERNAME
Value: agentnext
Click: "Add secret"
```

**Step 4: Add Secret #2 - Token**
```
Name: DOCKER_HUB_TOKEN
Value: [Your Docker Hub Token - get from hub.docker.com/settings/security]
Click: "Add secret"
```

✅ Both secrets should now appear in the list.

### Method 2: GitHub CLI (If Installed)

```bash
cd code-reviewer

gh secret set DOCKER_HUB_USERNAME --body "agentnext"
gh secret set DOCKER_HUB_TOKEN --body "[Your Docker Hub Token]"

# Verify
gh secret list
```

## Get Your Docker Hub Token

1. Visit: https://hub.docker.com/settings/security
2. Click: "New Access Token"
3. Name: `github-actions`
4. Copy token (shows only once!)
5. Add to GitHub secret: DOCKER_HUB_TOKEN

## Verify Secrets Were Added

Visit: https://github.com/agentnxt/code-reviewer/settings/secrets/actions

You should see:
```
✓ DOCKER_HUB_USERNAME (updated X seconds ago)
✓ DOCKER_HUB_TOKEN    (updated X seconds ago)
```

(Token value is hidden for security)

## Security Best Practices

⚠️ **IMPORTANT:**
- Never commit secrets to Git
- Never paste tokens in code or docs
- Always use GitHub Secrets (encrypted storage)
- Rotate tokens every 90 days
- Regenerate immediately if leaked

GitHub's Secret Scanning will block any commits containing tokens.

## Test the Setup

### Trigger a Build

```bash
cd code-reviewer

# Make a test commit
git commit --allow-empty -m "test: trigger GitHub Actions with secrets"
git push origin main
```

### Watch the Build

Go to: https://github.com/agentnxt/code-reviewer/actions

Click the latest workflow run and watch:

1. **test** - Runs pytest (29 tests)
   - Should pass ✅
   
2. **package-build** - Builds Python package
   - Should pass ✅
   
3. **container-build** - Builds Docker image and pushes
   - Should complete successfully ✅

**Build time:** ~5-10 minutes total

### Check Docker Hub

After workflow completes (look for ✅ green checkmark):

```bash
# Option 1: Visit Docker Hub
https://hub.docker.com/r/agentnext/code-reviewer

# Option 2: Pull locally
docker pull agentnext/code-reviewer:latest

# Option 3: Search
docker search agentnext/code-reviewer
```

You should see the image with tags like:
- `latest`
- `main-abc123def` (main branch + commit sha)

## What Happens Automatically Now

Every time you push to main:

```
git push origin main
  ↓
GitHub detects push
  ↓
Workflow triggers .github/workflows/ci.yml
  ↓
1. Run tests (pytest -q)
2. Build package (python -m build)
3. Build Docker image (docker build)
4. Login to Docker Hub (using secrets)
5. Push image (docker push agentnext/code-reviewer:latest)
  ↓
✅ Image available at: docker.io/agentnext/code-reviewer:latest
```

Takes ~5-10 minutes. No manual commands needed!

## Workflow Details

**Triggers:**
- Every push to `main` branch
- Every pull request (builds but doesn't push)
- Can manually trigger from Actions tab

**Jobs:**
- `test` - Pytest on Python 3.11
- `package-build` - Python package validation
- `container-build` - Docker build & push

**Auto-Tagging:**
- `latest` - Latest main branch
- `main-<sha>` - Branch + commit SHA
- `v*` - Semantic version tags (v0.1.0, v1.0.0, etc.)

**Image Tags on Docker Hub:**
```
agentnext/code-reviewer:latest
agentnext/code-reviewer:main-a1b2c3d4e5f6
agentnext/code-reviewer:v0.1.0  (when tagged)
```

## Troubleshooting

### Workflow shows "Failure" in Docker Push Step?

Check the logs:
```
https://github.com/agentnxt/code-reviewer/actions
→ Click failed run
→ Click "container-build" job
→ Expand "Build and push Docker image"
→ Look for error message
```

Common fixes:
- ❌ Wrong token → Regenerate new token at hub.docker.com/settings/security
- ❌ Secrets not set → Re-add both secrets
- ❌ Token expired → Create new token with full permissions

### Secrets Not Working?

Verify they're added:
```
https://github.com/agentnxt/code-reviewer/settings/secrets/actions
```

Both should show:
```
✓ DOCKER_HUB_USERNAME
✓ DOCKER_HUB_TOKEN
```

If missing, add them again.

### Tests Failing?

```bash
cd code-reviewer
python3 -m pytest -q
```

Should show: `29 passed in 0.28s`

If different, check logs in GitHub Actions.

### Want to Debug Locally?

```bash
cd code-reviewer

# Run tests
python3 -m pytest -q

# Build Docker image
docker build -f deploy/code-reviewer/Dockerfile . -t test:latest

# Check image
docker images | grep test
```

## Next Steps

1. ✅ **Add secrets** (GitHub Secrets UI)
   - DOCKER_HUB_USERNAME = agentnext
   - DOCKER_HUB_TOKEN = [your token from hub.docker.com]

2. **Test the workflow**
   ```bash
   git commit --allow-empty -m "test: GitHub Actions"
   git push origin main
   ```

3. **Monitor the build**
   - https://github.com/agentnxt/code-reviewer/actions
   - Wait for ✅ green checkmarks

4. **Verify image pushed**
   - https://hub.docker.com/r/agentnext/code-reviewer
   - Or: `docker pull agentnext/code-reviewer:latest`

5. **Use the image**
   ```bash
   docker compose -f docker-compose.unified.yml up -d
   ```

## Reference

**Key Files:**
- Workflow: `.github/workflows/ci.yml`
- Dockerfile: `deploy/code-reviewer/Dockerfile`
- Docker Compose: `docker-compose.unified.yml`

**Useful Links:**
- GitHub Secrets: https://github.com/agentnxt/code-reviewer/settings/secrets/actions
- GitHub Actions: https://github.com/agentnxt/code-reviewer/actions
- Docker Hub Repo: https://hub.docker.com/r/agentnext/code-reviewer
- Docker Hub Settings: https://hub.docker.com/settings/security

**Documentation:**
- See `DOCKER_BUILD_TROUBLESHOOTING.md` in repo for detailed info

---

## ✅ SETUP COMPLETE

Your GitHub Actions are now configured for automated Docker Hub pushes!

**From now on:**
- `git push origin main` → Auto-builds and pushes Docker image
- No manual docker commands needed
- Image available at `docker.io/agentnext/code-reviewer:latest`

---

**Ready? Test it:**
```bash
cd code-reviewer
git commit --allow-empty -m "test: trigger GitHub Actions"
git push origin main
```

Then watch: https://github.com/agentnxt/code-reviewer/actions

🚀 **Automated Docker Hub deploys enabled!**
