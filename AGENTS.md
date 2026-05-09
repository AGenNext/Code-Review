# Project Agent Configuration

This file contains context and instructions for AI agents working on this repository.

## Repository Overview

This is a production-ready project with:
- **Landing page** (index.html) - SEO-optimized with security headers
- **GitHub Pages deployment** - Automatic via GitHub Actions
- **Docker** - Containerized with Nginx and security hardening
- **SSO authentication** - OAuth2/OpenID Connect (auth/server.js)
- **Notifications** - Multi-channel system (email, webhook, push, in-app)
- **Email service** - Transactional templates
- **LangGraph AI Agent** - Management agent for GitHub/Docker operations

## Key Files

| File | Purpose |
|------|---------|
| `index.html` | Landing page with SEO meta, security headers |
| `.github/workflows/deploy.yml` | GitHub Pages deployment workflow |
| `Dockerfile` | Docker build with security hardening |
| `nginx.conf` | Nginx config with security headers |
| `agent/manager.py` | LangGraph management agent |
| `agent/tools.py` | Agent tools (GitHub, Docker, Terminal, file_editor) |
| `auth/server.js` | SSO OAuth server |
| `notifications/index.js` | Notification system |
| `emails/index.js` | Email service with templates |
| `tests/e2e.spec.js` | E2E tests with Playwright |

## Agent Configuration

### Environment Variables

```bash
# Required for agent
GITHUB_TOKEN=your-github-token
LLM_API_KEY=your-llm-api-key

# Optional
GITHUB_OWNER=your-org
GITHUB_REPO=your-repo
DOCKER_REGISTRY=ghcr.io
SESSION_SECRET=your-session-secret
```

### Available Skills

- **GitHub**: PR management, workflow status, issues
- **Docker**: Build, push, run, logs
- **Security**: Vulnerability scanning, dependency audit
- **QA**: E2E testing, verification
- **Release**: Changelog, versioning

### Tools

The agent uses these tools:
- `GitHubTool` - Repository and PR operations
- `DockerTool` - Container operations
- `TerminalTool` - Shell command execution
- `file_editor` - file_editor operations

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt
npm install

# Run agent
python agent/manager.py

# Build Docker
docker build -t project .
docker run -p 8080:80 project

# Run tests
npm test

# Deploy to GitHub Pages
git push origin main
```

## Deployment

1. **GitHub Pages**: Push to main branch triggers workflow
2. **Docker**: Build and push manually or via CI

## Common Tasks

| Task | Command |
|------|---------|
| Build Docker | `docker build -t project .` |
| Run container | `docker run -p 8080:80 project` |
| Push image | `docker push ghcr.io/owner/project:latest` |
| Run agent | `python agent/manager.py` |
| Run tests | `npx playwright test` |