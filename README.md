# Project

This is the project workspace - a production-ready landing page with GitHub Pages, Docker, SSO, notifications, email, and AI agent support.

## Features

- **Landing Page** - SEO-optimized with security headers
- **GitHub Pages** - Automatic deployment via GitHub Actions
- **Docker** - Containerized deployment with security hardening
- **SSO** - OAuth2/OpenID Connect authentication
- **Notifications** - Multi-channel notifications (email, webhook, push, in-app)
- **Email** - Transactional email with templates
- **AI Agent** - LangGraph-based management agent

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent
python agent/manager.py

# Build Docker
docker build -t project .
docker run -p 8080:80 project
```

## Documentation

- [API.md](API.md) - API documentation
- [HOWTO.md](HOWTO.md) - How-to guide
- [SSO.md](SSO.md) - SSO configuration
- [NOTIFICATIONS.md](NOTIFICATIONS.md) - Notification system
- [EMAILS.md](EMAILS.md) - Email service

## Project Structure

```
project/
├── index.html          # Landing page
├── README.md         # This file
├── API.md           # API docs
├── HOWTO.md         # How-to guide
├── SSO.md           # SSO config
├── NOTIFICATIONS.md # Notifications
├── EMAILS.md        # Email docs
├── Dockerfile      # Docker build
├── nginx.conf      # Nginx config
├── package.json   # NPM config
├── requirements.txt # Python deps
├── .github/
│   └── workflows/
│       └── deploy.yml
├── agent/
│   └── manager.py  # AI agent
├── auth/
│   └── server.js  # SSO server
├── emails/
│   └── index.js  # Email service
├── notifications/
│   └── index.js  # Notification system
└── tests/
    └── e2e.spec.js
```