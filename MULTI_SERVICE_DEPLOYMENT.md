# Autonomyx + CodeReviewer Multi-Service Deployment Guide

This guide covers deploying both the Autonomyx landing page and CodeReviewer service in a unified container environment.

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Nginx Reverse Proxy             │
│  (Port 80/443, request routing)         │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────────┐
│  Autonomyx  │  │  CodeReviewer   │
│  Landing    │  │  Service        │
│  (Port 80)  │  │  (Port 8000)    │
└─────────────┘  └──────┬──────────┘
                        │
                  ┌─────▼─────┐
                  │  SQLite   │
                  │   /data   │
                  └───────────┘
```

## Quick Start - Development

### 1. Prerequisites
- Docker Desktop installed
- `.env` file configured (see `deploy/code-reviewer/.env.example`)

### 2. Start services locally
```bash
# Development mode (hot-reload for CodeReviewer)
docker compose -f docker-compose.dev.yml up --build

# Or production mode (both services)
docker compose -f docker-compose.prod.yml up --build
```

### 3. Access services
- **Autonomyx Landing:** http://localhost:3000
- **CodeReviewer Web UI:** http://localhost:8000
- **CodeReviewer API:** http://localhost:8000/api

## Production Deployment

### 1. Build and tag images

**CodeReviewer:**
```bash
docker build -f deploy/code-reviewer/Dockerfile . \
  --tag agentnext/code-reviewer:latest \
  --tag agentnext/code-reviewer:v0.1.0

docker push agentnext/code-reviewer:latest
```

**Autonomyx Landing (from its repo):**
```bash
docker build -f Dockerfile . \
  --tag agentnext/autonomyx-landing:latest \
  --tag agentnext/autonomyx-landing:v1.0

docker push agentnext/autonomyx-landing:latest
```

### 2. Production environment setup

Create `deploy/code-reviewer/.env`:
```env
HOST=0.0.0.0
PORT=8000
CODEREVIEWER_DB_PATH=/data/codereviewer.db

# Claude Agent SDK
CLAUDE_AGENT_SDK_ENABLED=true
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxx
CLAUDE_AGENT_SDK_MODEL=claude-opus-4-1
CLAUDE_AGENT_SDK_STRICT=true

# LiteLLM Gateway (optional)
LITELLM_ENABLED=false
LITELLM_BASE_URL=http://localhost:4000

# Observability
SIGNOZ_ENABLED=true
SIGNOZ_SERVICE_NAME=code-reviewer
SIGNOZ_OTLP_TRACES_ENDPOINT=http://signoz-collector:4318/v1/traces

# Notifications
NOTIFICATIONS_ENABLED=true
NOTIFICATION_CHANNELS=email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@autonomyx.com
SMTP_TO=team@autonomyx.com
SMTP_USE_TLS=true

# SSO (OIDC)
SSO_ENABLED=true
SSO_PROVIDER=oidc
SSO_ISSUER_URL=https://your-idp.com
SSO_CLIENT_ID=your-client-id
SSO_CLIENT_SECRET=your-client-secret
SSO_AUDIENCE=code-reviewer-api
SSO_REDIRECT_URI=https://autonomyx.com/auth/callback
SSO_SCOPES=openid,profile,email

# Multitenancy
MULTITENANCY_REQUIRE_AGENT_IDENTITY=false
```

### 3. Deploy with docker-compose
```bash
docker compose -f docker-compose.prod.yml up -d
```

### 4. Configure SSL/TLS

Place certificates in `./ssl/`:
```bash
mkdir -p ssl
# Copy your cert.pem and key.pem here
```

Then uncomment SSL lines in `nginx.conf`:
```nginx
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

Rebuild:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 5. Health checks
```bash
# Nginx proxy
curl http://localhost/healthz

# CodeReviewer
curl http://localhost:8000/healthz

# CodeReviewer API
curl http://localhost:8000/api/status
```

## Kubernetes Deployment

### 1. Create namespace
```bash
kubectl create namespace autonomyx
```

### 2. Deploy CodeReviewer
```yaml
# code-reviewer-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-reviewer
  namespace: autonomyx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: code-reviewer
  template:
    metadata:
      labels:
        app: code-reviewer
    spec:
      containers:
      - name: code-reviewer
        image: agentnext/code-reviewer:latest
        ports:
        - containerPort: 8000
        env:
        - name: HOST
          value: "0.0.0.0"
        - name: PORT
          value: "8000"
        - name: CLAUDE_API_KEY
          valueFrom:
            secretKeyRef:
              name: code-reviewer-secrets
              key: claude-api-key
        volumeMounts:
        - name: data
          mountPath: /data
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: code-reviewer-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: code-reviewer
  namespace: autonomyx
spec:
  selector:
    app: code-reviewer
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: code-reviewer-pvc
  namespace: autonomyx
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

Deploy:
```bash
kubectl create secret generic code-reviewer-secrets \
  --from-literal=claude-api-key=sk-ant-xxxxxxxxxxxx \
  -n autonomyx

kubectl apply -f code-reviewer-deployment.yaml
```

## Monitoring & Observability

### SignalOz Integration
```bash
# Start SignalOz locally (if not already running)
docker run -d \
  --name signoz \
  -p 4318:4318 \
  -p 4317:4317 \
  signoz/signoz:latest

# Update .env
SIGNOZ_ENABLED=true
SIGNOZ_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces
```

### Prometheus Metrics
Add to Prometheus scrape config:
```yaml
- job_name: 'code-reviewer'
  static_configs:
    - targets: ['localhost:8000']
```

## Troubleshooting

### CodeReviewer won't start
```bash
docker logs code-reviewer
docker compose -f docker-compose.dev.yml logs -f code-reviewer
```

### Database connection issues
```bash
# Check volume mount
docker volume ls | grep code-reviewer

# Reset database
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up
```

### Nginx routing issues
```bash
# Check Nginx config
docker exec autonomyx-proxy nginx -t

# View logs
docker logs autonomyx-proxy
```

### Claude Agent SDK failures
```bash
# Set SDK to non-strict mode first
CLAUDE_AGENT_SDK_STRICT=false

# Verify API key
curl -H "Authorization: Bearer $CLAUDE_API_KEY" \
  https://api.anthropic.com/v1/models
```

## Performance Tuning

### Database
- SQLite is suitable for single-instance. For scale, migrate to PostgreSQL:
```env
DATABASE_URL=postgresql://user:pass@db:5432/codereviewer
```

### Caching
- Enable Redis for session/result caching (feature coming)

### Load Balancing
- Deploy multiple CodeReviewer replicas behind nginx/k8s service mesh
- Use persistent volume for `/data` across replicas

## Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] SSO/OIDC enabled for authentication
- [ ] API authentication enabled (bearer tokens)
- [ ] CORS configured properly
- [ ] Database backups automated
- [ ] Secrets in Docker Secrets or K8s Secrets
- [ ] Network policies defined
- [ ] Rate limiting enabled

## Automated Deployments

### GitHub Actions → Docker Hub → Production
The repo includes `.github/workflows/ci.yml` which:
1. Runs tests on every push
2. Builds Docker image
3. Pushes to Docker Hub on main branch
4. Tags with semantic versioning

To trigger deployment on image push:
1. Set up webhook from Docker Hub to your deployment service
2. Or use ArgoCD/Flux for GitOps

## Support & Maintenance

- **Logs:** `docker logs code-reviewer`
- **Database:** `/data/codereviewer.db` (SQLite)
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/healthz
- **Metrics:** OpenTelemetry compatible

## Next Steps

1. Configure `.env` with your API keys and SMTP settings
2. Deploy with `docker compose -f docker-compose.prod.yml up -d`
3. Set up SSL/TLS certificates
4. Configure GitHub Actions secrets for Docker Hub push
5. Monitor logs and metrics via SignalOz
