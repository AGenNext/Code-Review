# Autonomyx Google Cloud Run Deployment Guide

## Overview

Deploy the complete Autonomyx ecosystem to Google Cloud Run with automated CI/CD using Cloud Build.

### Architecture

```
┌─────────────────────────────────────────────┐
│     Google Cloud Platform (GCP)             │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │   Cloud Load Balancer               │   │
│  │   (Distribute traffic)              │   │
│  └────────────┬────────────────────────┘   │
│               │                             │
│       ┌───────┴──────────┐                 │
│       │                  │                 │
│  ┌────▼────────┐    ┌────▼──────────┐     │
│  │ Cloud Run   │    │  Cloud Run    │     │
│  │ Landing     │    │  CodeReviewer │     │
│  │ (1 CPU)     │    │  (2 CPU)      │     │
│  └─────────────┘    └────┬──────────┘     │
│                           │                │
│                    ┌──────▼──────┐         │
│                    │ Cloud SQL   │         │
│                    │ PostgreSQL  │         │
│                    │ (Optional)  │         │
│                    └─────────────┘         │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │ Container Registry (gcr.io)        │   │
│  │ - code-reviewer:latest             │   │
│  │ - autonomyx-landing:latest         │   │
│  └────────────────────────────────────┘   │
│                                            │
└─────────────────────────────────────────────┘
```

## Prerequisites

### Local Setup

1. **Google Cloud SDK**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk
   
   # Or visit: https://cloud.google.com/sdk/docs/install
   ```

2. **Docker**
   ```bash
   # Already installed if you have Docker Desktop
   docker --version
   ```

3. **gcloud CLI**
   ```bash
   gcloud --version
   gcloud auth login
   ```

### GCP Account

- Active Google Cloud Project
- Billing enabled
- Owner or Editor IAM role

## Quick Deploy (5 minutes)

### Step 1: Set Your Project ID

```bash
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID
```

### Step 2: Run Deployment Script

```bash
cd code-reviewer
chmod +x deploy-cloudrun.sh
./deploy-cloudrun.sh $PROJECT_ID
```

**What the script does:**
- ✅ Enables required GCP APIs
- ✅ Creates secrets for API keys
- ✅ Builds Docker images using Cloud Build
- ✅ Pushes to Google Container Registry
- ✅ Deploys to Cloud Run
- ✅ Configures autoscaling

**Time:** ~5-10 minutes

### Step 3: Verify Deployment

```bash
# List deployed services
gcloud run services list --region=us-central1

# Test CodeReviewer
CODEREVIEWER_URL=$(gcloud run services describe code-reviewer \
  --region=us-central1 \
  --format='value(status.url)')

curl $CODEREVIEWER_URL/healthz

# Test Landing Page
LANDING_URL=$(gcloud run services describe autonomyx-landing \
  --region=us-central1 \
  --format='value(status.url)')

curl $LANDING_URL/healthz
```

## Manual Deployment

If you prefer to deploy step-by-step:

### Step 1: Enable APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  compute.googleapis.com \
  iam.googleapis.com
```

### Step 2: Create Secrets

```bash
# Create secret for Claude API key
echo -n "sk-ant-xxxxxxxxxx" | gcloud secrets create \
  code-reviewer-claude-key --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding code-reviewer-claude-key \
  --member=serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Step 3: Build CodeReviewer

```bash
cd code-reviewer

# Build using Cloud Build
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1

# Or build locally
gcloud builds submit \
  --tag=gcr.io/$PROJECT_ID/code-reviewer:latest \
  -f Dockerfile.cloudrun .
```

### Step 4: Deploy CodeReviewer

```bash
gcloud run deploy code-reviewer \
  --image=gcr.io/$PROJECT_ID/code-reviewer:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=2 \
  --timeout=3600 \
  --set-env-vars="PORT=8080,CLAUDE_AGENT_SDK_ENABLED=true"
```

### Step 5: Deploy Autonomyx Landing

```bash
cd ../autonomyx-landing

gcloud run deploy autonomyx-landing \
  --image=gcr.io/$PROJECT_ID/autonomyx-landing:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --memory=256Mi \
  --cpu=1
```

## Configuration

### Environment Variables

**CodeReviewer (Cloud Run)**
```
PORT=8080
HOST=0.0.0.0
CLAUDE_AGENT_SDK_ENABLED=true
CLAUDE_API_KEY=[from secrets]
SIGNOZ_ENABLED=false
CODEREVIEWER_DB_PATH=/tmp/codereviewer.db
```

**Autonomyx Landing (Cloud Run)**
```
PORT=8080
```

### CPU & Memory Allocation

**CodeReviewer**
- CPU: 2 vCPU
- Memory: 1 GiB
- Timeout: 3600s (1 hour)
- Concurrency: 80
- Max instances: 100

**Autonomyx Landing**
- CPU: 1 vCPU
- Memory: 256 MiB
- Timeout: 3600s
- Concurrency: 100
- Max instances: 100

### Autoscaling

Both services have autoscaling enabled:
- Minimum instances: 1
- Maximum instances: 100
- Min requests for scaling down: 0.5
- Scales based on CPU/memory usage

## Accessing Your Services

### URLs

After deployment, you'll get URLs like:

```
CodeReviewer: https://code-reviewer-xxxxxxxx-uc.a.run.app
Landing Page: https://autonomyx-landing-xxxxxxxx-uc.a.run.app
```

### Health Checks

```bash
# CodeReviewer
curl https://code-reviewer-xxxxxxxx-uc.a.run.app/healthz

# Landing Page
curl https://autonomyx-landing-xxxxxxxx-uc.a.run.app/healthz
```

### API Documentation

CodeReviewer Swagger UI:
```
https://code-reviewer-xxxxxxxx-uc.a.run.app/docs
```

## Logging & Monitoring

### View Logs

```bash
# All logs
gcloud logs read --limit=50

# CodeReviewer logs
gcloud logs read "resource.labels.service_name=code-reviewer" --limit=50

# Real-time logs
gcloud logs read "resource.labels.service_name=code-reviewer" \
  --limit=50 --follow

# Filter by severity
gcloud logs read "severity=ERROR" --limit=20
```

### Cloud Logging Dashboard

Visit Cloud Logging in GCP Console:
```
https://console.cloud.google.com/logs
```

### Monitoring

View service metrics:
```bash
gcloud monitoring metrics-descriptors list | grep run.googleapis.com
```

## Continuous Deployment

### Option 1: Cloud Build Trigger (Recommended)

1. Connect GitHub repository
2. Create trigger for main branch
3. Build automatically on push

**Setup:**
```bash
# In GCP Console:
# 1. Go to Cloud Build → Triggers
# 2. Create New Trigger
# 3. Connect GitHub repo
# 4. Create trigger:
#    - Name: code-reviewer-deploy
#    - Event: Push to main
#    - Build config: Cloud Build file
#    - Location: repository (cloudbuild.yaml)
```

### Option 2: GitHub Actions (Current Setup)

GitHub Actions builds Docker images and pushes to Docker Hub.
Manually deploy from Docker Hub:

```bash
gcloud run deploy code-reviewer \
  --image=docker.io/agentnext/code-reviewer:latest \
  --region=us-central1 \
  --update
```

## Advanced Configuration

### Add Custom Domain

```bash
# Map custom domain to Cloud Run
gcloud run domain-mappings create \
  --service=code-reviewer \
  --domain=api.autonomyx.com \
  --region=us-central1
```

### Add IAM Permissions

```bash
# Allow specific users to invoke service
gcloud run services add-iam-policy-binding code-reviewer \
  --member=user:email@example.com \
  --role=roles/run.invoker

# Make service public
gcloud run services add-iam-policy-binding code-reviewer \
  --member=allUsers \
  --role=roles/run.invoker
```

### Connect to Cloud SQL

```bash
# Create Cloud SQL instance
gcloud sql instances create autonomyx-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Connect Cloud Run to Cloud SQL
gcloud run services update code-reviewer \
  --add-cloudsql-instances=$PROJECT_ID:us-central1:autonomyx-db \
  --region=us-central1
```

## Troubleshooting

### Service Fails to Deploy

1. **Check build logs:**
   ```bash
   gcloud builds log $(gcloud builds list --limit=1 --format='value(ID)')
   ```

2. **Check service logs:**
   ```bash
   gcloud logs read "resource.labels.service_name=code-reviewer" --limit=100
   ```

3. **Common issues:**
   - Port not 8080: Cloud Run requires port 8080
   - Out of memory: Increase memory allocation
   - Timeout: Check if service is hung

### Quota Exceeded

```bash
# Check quotas
gcloud compute project-info describe --project=$PROJECT_ID \
  --format='value(quotas[name="RESOURCES"].usage/quotas[name="RESOURCES"].limit)'

# Request quota increase in GCP Console
```

### Service Unreachable

```bash
# Check if service is running
gcloud run services describe code-reviewer --region=us-central1

# Check authentication
gcloud run services get-iam-policy code-reviewer

# Enable public access
gcloud run services add-iam-policy-binding code-reviewer \
  --member=allUsers \
  --role=roles/run.invoker
```

## Scaling & Performance

### Horizontal Scaling

Increase max instances:
```bash
gcloud run services update code-reviewer \
  --max-instances=500 \
  --region=us-central1
```

### Vertical Scaling

Increase CPU/Memory:
```bash
gcloud run services update code-reviewer \
  --memory=2Gi \
  --cpu=4 \
  --region=us-central1
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 100 https://code-reviewer-xxxxxxxx-uc.a.run.app/healthz

# Using hey
go install github.com/rakyll/hey@latest
hey -n 1000 -c 100 https://code-reviewer-xxxxxxxx-uc.a.run.app/healthz
```

## Cost Optimization

### Accurate Cost Estimates

**Google Cloud Run Pricing (2024):**
- vCPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GB-second
- Free tier: 2M requests, 360K GB-seconds, 180K vCPU-seconds/month

**Development Configuration (Min instances = 0):**
```
CodeReviewer: 1 CPU, 512Mi, 10% usage   ~$20/month
Landing:      1 CPU, 256Mi, 5% usage    ~$2/month
Container Registry:                     ~$0.10/month
Total: ~$22/month

Calculation:
- 2,592,000 seconds/month (30 days)
- 10% active = 259,200 seconds
- 1 vCPU × 259,200 × $0.00002400 = $6.22
- 0.5 GB × 259,200 × $0.00000250 = $0.32
```

**Production Configuration (Min instances = 1):**
```
CodeReviewer: 2 CPU, 1Gi, 80% usage    ~$105/month
Landing:      1 CPU, 256Mi, 10% usage  ~$6/month
Container Registry:                    ~$0.10/month
Total: ~$111/month

Calculation:
- 2,592,000 seconds/month
- 80% active = 2,073,600 seconds
- 2 vCPU × 2,073,600 × $0.00002400 = $99.54
- 1 GB × 2,073,600 × $0.00000250 = $5.18
```

**Enterprise Configuration (High traffic):**
```
CodeReviewer: 4 CPU, 2Gi, 90% usage    ~$420/month
Landing:      2 CPU, 512Mi, 50% usage  ~$60/month
Database (Cloud SQL):                  ~$100+/month
Total: ~$580+/month
```

**Free Tier Coverage:**
- May cover low-traffic apps entirely
- 2M requests/month = ~67k requests/day
- Check usage: `gcloud billing accounts list`

### Cost Reduction Strategies

**Immediate savings:**
```bash
# Lower CPU (saves ~$50/month)
gcloud run services update code-reviewer --cpu=1

# Lower memory (saves ~$25/month)
gcloud run services update code-reviewer --memory=512Mi

# Set min instances to 0 (no idle cost, cold starts only)
gcloud run services update code-reviewer --min-instances=0

# Result with these changes: ~$20/month development cost
```

**Monitoring costs:**
```bash
# Check current spending
gcloud billing accounts list
gcloud compute project-info describe --project=$PROJECT_ID

# Set up budget alerts
gcloud billing budgets create --billing-account=BILLING_ACCOUNT_ID
```

**Long-term optimization:**
1. Use committed use discounts (3-year: 25% discount)
2. Use Compute Engine instead of Cloud Run for stable workloads
3. Implement aggressive caching
4. Use CDN for static content (landing page)
5. Schedule lower instances during off-hours

## Cleanup

### Delete Services

```bash
# Delete CodeReviewer
gcloud run services delete code-reviewer --region=us-central1

# Delete Landing Page
gcloud run services delete autonomyx-landing --region=us-central1
```

### Delete Container Images

```bash
# Delete CodeReviewer image
gcloud container images delete gcr.io/$PROJECT_ID/code-reviewer:latest

# Delete Landing image
gcloud container images delete gcr.io/$PROJECT_ID/autonomyx-landing:latest

# List all images
gcloud container images list --repository=gcr.io/$PROJECT_ID
```

### Delete Secrets

```bash
gcloud secrets delete code-reviewer-claude-key
```

## Reference

**Official Documentation:**
- Cloud Run: https://cloud.google.com/run/docs
- Cloud Build: https://cloud.google.com/build/docs
- Container Registry: https://cloud.google.com/container-registry/docs
- Pricing: https://cloud.google.com/run/pricing

**Key Files:**
- `Dockerfile.cloudrun` - Cloud Run Dockerfile
- `cloudbuild.yaml` - Cloud Build configuration
- `k8s-cloudrun-service.yaml` - Knative service spec
- `deploy-cloudrun.sh` - Automated deployment script

**CLI Reference:**
```bash
# Create service
gcloud run deploy SERVICE_NAME

# List services
gcloud run services list

# Update service
gcloud run services update SERVICE_NAME

# View service details
gcloud run services describe SERVICE_NAME

# Delete service
gcloud run services delete SERVICE_NAME

# View logs
gcloud logs read

# Check status
gcloud run describe SERVICE_NAME
```

---

## ✅ SUMMARY

You can now deploy Autonomyx to Google Cloud Run with:

1. **Automated:** `./deploy-cloudrun.sh $PROJECT_ID`
2. **Manual:** Step-by-step gcloud commands
3. **CI/CD:** Cloud Build triggers + GitHub

All services auto-scale, have health checks, and are production-ready!
