# Agent Skills and Tools

This document defines the skills and tools available to the management agent.

## Skills

### GitHub Operations

**Triggers:** "github", "pr", "pull request", "repo", "repository", "workflow"

Capabilities:
- Create and manage repositories
- Open and manage pull requests
- Check workflow status
- Manage issues and labels
- Review code

### Docker Operations

**Triggers:** "docker", "container", "deploy", "image", "push"

Capabilities:
- Build Docker images
- Push to registry
- Run containers
- Manage deployments

### Security Analysis

**Triggers:** "security", "vulnerability", "audit", "secure"

Capabilities:
- Scan for vulnerabilities
- Check dependencies
- Review security headers
- Validate credentials

### Code Review

**Triggers:** "review", "code review", "pr review"

Capabilities:
- Lint code
- Check style
- Review changes
- Suggest improvements

### QA Testing

**Triggers:** "test", "qa", "testing", "verify"

Capabilities:
- Run E2E tests
- Check functionality
- Verify deployments

### Release Management

**Triggers:** "release", "version", "changelog", "tag"

Capabilities:
- Create releases
- Generate changelogs
- Manage versions

## Tools

### GitHub Tool

```python
{
  "name": "github",
  "description": "GitHub operations",
  "actions": [
    "get_repo",
    "create_pr",
    "list_workflows",
    "get_workflow_status",
    "create_issue"
  ]
}
```

### Docker Tool

```python
{
  "name": "docker",
  "description": "Docker operations",
  "actions": [
    "build",
    "push",
    "run",
    "stop",
    "logs"
  ]
}
```

### File Editor Tool

```python
{
  "name": "file_editor",
  "description": "File operations",
  "actions": [
    "read",
    "write",
    "edit",
    "delete"
  ]
}
```

### Terminal Tool

```python
{
  "name": "terminal",
  "description": "Shell commands",
  "actions": [
    "execute",
    "check_status"
  ]
}
```

### Notification Tool

```python
{
  "name": "notification",
  "description": "Send notifications",
  "actions": [
    "send_email",
    "send_webhook",
    "send_push"
  ]
}
```

## Configuration

Set these environment variables:

```bash
# LLM Settings
LLM_MODEL=anthropic/claude-3-sonnet-20240229
LLM_API_KEY=your-api-key

# GitHub Settings
GITHUB_TOKEN=your-github-token
GITHUB_OWNER=your-org
GITHUB_REPO=your-repo

# Docker Settings
DOCKER_REGISTRY=ghcr.io
DOCKER_USERNAME=your-username

# Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email
SMTP_PASS=your-password
```

## Usage

```python
from agent.manager import run_agent

# Query the agent
result = run_agent("Build and push Docker image")
print(result["response"])

# Check status
result = run_agent("Show me the latest workflow run")
print(result["response"])
```

## Examples

| Query | Action |
|-------|--------|
| "Build Docker" | Build image |
| "Push to registry" | Push image to registry |
| "Run tests" | Run E2E tests |
| "Create PR" | Open pull request |
| "Check workflows" | List workflow runs |
| "Send notification" | Send email/webhook |