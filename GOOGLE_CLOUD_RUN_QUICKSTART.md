# ✅ DEPLOY TO GOOGLE CLOUD RUN - QUICK START

## What You Get

Deploy **Autonomyx** (landing page + CodeReviewer service) to Google Cloud Run in under 5 minutes.

```
✅ CodeReviewer: https://code-reviewer-xxxxxxxx-uc.a.run.app
✅ Landing Page: https://autonomyx-landing-xxxxxxxx-uc.a.run.app
✅ Auto-scaling: 1-100 instances
✅ Health checks: Built-in
✅ Monitoring: Cloud Logging & Cloud Console
```

---

## STEP 1: Setup Google Cloud (2 minutes)

### Create GCP Project

1. Visit: https://console.cloud.google.com
2. Create new project
3. Note your Project ID (e.g., `my-autonomyx-prod`)

### Install gcloud CLI

**macOS:**
```bash
brew install --cask google-cloud-sdk
gcloud init
```

**Linux/Windows:**
Visit: https://cloud.google.com/sdk/docs/install

### Login & Set Project

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud config set compute/region us-central1
```

---

## STEP 2: Deploy with One Command (3 minutes)

### Clone & Deploy CodeReviewer

```bash
# Clone the repo
git clone https://github.com/agentnxt/code-reviewer.git
cd code-reviewer

# Make script executable
chmod +x deploy-cloudrun.sh

# Run deployment (replace with your Project ID)
./deploy-cloudrun.sh your-gcp-project-id
```

**What the script does:**
1. ✅ Enables Cloud Run API
2. ✅ Enables Cloud Build API
3. ✅ Builds Docker image using Cloud Build
4. ✅ Pushes to Google Container Registry
5. ✅ Deploys to Cloud Run
6. ✅ Configures autoscaling

**Output:**
```
CodeReviewer Service:
  URL: https://code-reviewer-xxxxxxxx-uc.a.run.app
  Health Check: https://code-reviewer-xxxxxxxx-uc.a.run.app/healthz
  API Docs: https://code-reviewer-xxxxxxxx-uc.a.run.app/docs

Autonomyx Landing Page:
  URL: https://autonomyx-landing-xxxxxxxx-uc.a.run.app
  Health Check: https://autonomyx-landing-xxxxxxxx-uc.a.run.app/healthz
```

---

## STEP 3: Verify Deployment (1 minute)

### Test Services

```bash
# Get CodeReviewer URL
CODEREVIEWER_URL=$(gcloud run services describe code-reviewer \
  --region=us-central1 --format='value(status.url)')

# Get Landing URL
LANDING_URL=$(gcloud run services describe autonomyx-landing \
  --region=us-central1 --format='value(status.url)')

# Test health checks
curl $CODEREVIEWER_URL/healthz
curl $LANDING_URL/healthz
```

### View in Cloud Console

1. Visit: https://console.cloud.google.com/run
2. Select your project
3. See both services listed
4. Click services to view logs and metrics

---

## Services Configuration

### CodeReviewer
- **URL:** `https://code-reviewer-xxxxxxxx-uc.a.run.app`
- **CPU:** 2 vCPU
- **Memory:** 1 GiB
- **Timeout:** 3600s (1 hour)
- **Max Instances:** 100
- **Port:** 8080

**Access:**
- API: `$URL/api`
- Docs: `$URL/docs`
- Health: `$URL/healthz`

### Autonomyx Landing Page
- **URL:** `https://autonomyx-landing-xxxxxxxx-uc.a.run.app`
- **CPU:** 1 vCPU
- **Memory:** 256 MiB
- **Max Instances:** 100
- **Port:** 8080

---

## Manual Deployment (If Script Fails)

### Step 1: Enable APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com
```

### Step 2: Deploy CodeReviewer

```bash
cd code-reviewer

gcloud run deploy code-reviewer \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --timeout 3600
```

### Step 3: Deploy Landing Page

```bash
cd ../autonomyx-landing

gcloud run deploy autonomyx-landing \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 1
```

---

## Logging & Monitoring

### View Real-Time Logs

```bash
# AGenNext CodeReview logs
gcloud logs read "resource.labels.service_name=code-reviewer" --limit=50 --follow

# Landing page logs
gcloud logs read "resource.labels.service_name=autonomyx-landing" --limit=50 --follow
```

### View Metrics

1. Visit: https://console.cloud.google.com/run
2. Click service name
3. View "Metrics" tab
   - Requests per second
   - Latency
   - Error rate
   - CPU/Memory usage

### Cloud Monitoring

```bash
# View all metrics
gcloud monitoring metrics-descriptors list | grep run.googleapis.com

# Create alert
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="CodeReviewer High Error Rate"
```

---

## Configuration

### Environment Variables

Update via gcloud:

```bash
gcloud run services update code-reviewer \
  --region us-central1 \
  --set-env-vars "CLAUDE_AGENT_SDK_ENABLED=true,SIGNOZ_ENABLED=false"
```

### Add Claude API Key

1. Create secret:
   ```bash
   echo -n "sk-ant-xxxxxxxxxx" | gcloud secrets create \
     code-reviewer-claude-key --data-file=-
   ```

2. Grant access:
   ```bash
   gcloud secrets add-iam-policy-binding code-reviewer-claude-key \
     --member=serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com \
     --role=roles/secretmanager.secretAccessor
   ```

3. Use in service:
   ```bash
   gcloud run services update code-reviewer \
     --set-env-vars "CLAUDE_API_KEY=$(gcloud secrets versions access latest --secret=code-reviewer-claude-key)"
   ```

---

## Scaling & Performance

### Increase Capacity

```bash
# Increase CPU/Memory
gcloud run services update code-reviewer \
  --memory 2Gi \
  --cpu 4

# Increase max instances
gcloud run services update code-reviewer \
  --max-instances 500
```

### Monitor Performance

```bash
# Get current metrics
gcloud run services describe code-reviewer \
  --region us-central1 \
  --format='yaml(status.observedGeneration,status.traffic)'
```

---

## Cost Estimation

**Monthly Cost (Approximate):**
- CodeReviewer: ~$50 (2 CPU @ 80% usage)
- Landing Page: ~$5 (1 CPU @ 10% usage)
- Storage: ~$0.10 (images in registry)
- **Total: ~$111/month (production) or ~$22/month (development)**

**Reduce Costs:**
```bash
# Lower CPU
gcloud run services update code-reviewer --cpu 1

# Lower memory
gcloud run services update code-reviewer --memory 512Mi

# Set min instances to 0 (cold starts)
gcloud run services update code-reviewer --min-instances 0
```

---

## Custom Domain

### Map Custom Domain

```bash
# Create domain mapping
gcloud run domain-mappings create \
  --service=code-reviewer \
  --domain=api.autonomyx.com

# Verify DNS (follow GCP instructions)
# Add CNAME: api.autonomyx.com → ghs.googlehosted.com
```

### Update Landing Page Domain

```bash
gcloud run domain-mappings create \
  --service=autonomyx-landing \
  --domain=autonomyx.com
```

---

## Continuous Deployment (Optional)

### Setup Cloud Build Trigger

1. Visit: https://console.cloud.google.com/cloud-build/triggers
2. Create new trigger
3. Connect GitHub repo
4. Create trigger:
   - Event: Push to main
   - Build config: Cloud Build file
   - File location: `cloudbuild.yaml`

### Result

Every `git push` automatically:
- ✅ Builds Docker image
- ✅ Pushes to Container Registry
- ✅ Deploys to Cloud Run

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
gcloud logs read "resource.labels.service_name=code-reviewer" --limit=100

# Check service status
gcloud run services describe code-reviewer --region us-central1

# Common fixes:
# 1. Port must be 8080
# 2. Must exit cleanly on SIGTERM
# 3. Health check path must exist
```

### Out of Memory

```bash
# Increase memory
gcloud run services update code-reviewer --memory 2Gi

# Check current usage
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_latencies"'
```

### Build Fails

```bash
# Check Cloud Build logs
gcloud builds log $(gcloud builds list --limit=1 --format='value(ID)')

# Common fixes:
# 1. Dockerfile.cloudrun exists
# 2. Port is 8080
# 3. All dependencies in requirements.txt
```

---

## Cleanup

### Delete Services

```bash
gcloud run services delete code-reviewer --region us-central1
gcloud run services delete autonomyx-landing --region us-central1
```

### Delete Container Images

```bash
gcloud container images delete gcr.io/$PROJECT_ID/code-reviewer:latest
gcloud container images delete gcr.io/$PROJECT_ID/autonomyx-landing:latest
```

### Delete Project (Complete Cleanup)

```bash
gcloud projects delete YOUR_PROJECT_ID
```

---

## Quick Reference

| Task | Command |
|------|---------|
| List services | `gcloud run services list` |
| View service | `gcloud run services describe SERVICE_NAME` |
| View logs | `gcloud logs read --limit=50` |
| Update service | `gcloud run services update SERVICE_NAME --memory 2Gi` |
| Delete service | `gcloud run services delete SERVICE_NAME` |
| Get service URL | `gcloud run services describe SERVICE_NAME --format='value(status.url)'` |

---

## Files Reference

**In code-reviewer repo:**
- `Dockerfile.cloudrun` - Cloud Run Dockerfile
- `cloudbuild.yaml` - Cloud Build config
- `deploy-cloudrun.sh` - Deployment script
- `GOOGLE_CLOUD_RUN_DEPLOYMENT.md` - Full guide

**In autonomyx-landing repo:**
- `Dockerfile.cloudrun` - Cloud Run Dockerfile
- `cloudbuild.yaml` - Cloud Build config
- `nginx.cloudrun.conf` - Nginx config

---

## Next Steps

1. ✅ **Deploy:** `./deploy-cloudrun.sh $PROJECT_ID`
2. ✅ **Verify:** Test health checks
3. ✅ **Monitor:** View logs in Cloud Console
4. ✅ **Optimize:** Adjust CPU/memory as needed
5. ✅ **Setup CI/CD:** Connect Cloud Build trigger

---

## ✅ YOU'RE LIVE ON GOOGLE CLOUD RUN!

Both services are now:
- ✅ Running on Google Cloud Run
- ✅ Auto-scaling 1-100 instances
- ✅ Monitored by Cloud Logging
- ✅ Production-ready
- ✅ Accessible via HTTPS URLs

**CodeReviewer:** https://code-reviewer-xxxxxxxx-uc.a.run.app  
**Landing Page:** https://autonomyx-landing-xxxxxxxx-uc.a.run.app

---

For detailed information, see: `GOOGLE_CLOUD_RUN_DEPLOYMENT.md`
