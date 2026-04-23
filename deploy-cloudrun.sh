#!/bin/bash

# Autonomyx Google Cloud Run Deployment Script
# Deploys CodeReviewer and Autonomyx Landing to Google Cloud Run

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1:-}"
REGION="us-central1"
CODEREVIEWER_SERVICE="code-reviewer"
LANDING_SERVICE="autonomyx-landing"

# Helper functions
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v gcloud &> /dev/null; then
        error "gcloud CLI is not installed. Visit https://cloud.google.com/sdk/docs/install"
    fi
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    log "Prerequisites check passed ✓"
}

# Validate Google Cloud project
validate_project() {
    if [ -z "$PROJECT_ID" ]; then
        error "PROJECT_ID is required. Usage: $0 <PROJECT_ID>"
    fi
    
    log "Setting Google Cloud project to: $PROJECT_ID"
    gcloud config set project "$PROJECT_ID" || error "Failed to set project"
    
    log "Validating project..."
    gcloud projects describe "$PROJECT_ID" &>/dev/null || error "Project $PROJECT_ID not found or not accessible"
}

# Enable required APIs
enable_apis() {
    log "Enabling required Google Cloud APIs..."
    
    gcloud services enable \
        run.googleapis.com \
        cloudbuild.googleapis.com \
        containerregistry.googleapis.com \
        compute.googleapis.com \
        iam.googleapis.com \
        --project="$PROJECT_ID" || error "Failed to enable APIs"
    
    log "APIs enabled ✓"
}

# Create secrets for CodeReviewer
create_secrets() {
    log "Setting up secrets for CodeReviewer..."
    
    # Check if secret already exists
    if gcloud secrets describe code-reviewer-claude-key --project="$PROJECT_ID" &>/dev/null; then
        warning "Secret 'code-reviewer-claude-key' already exists. Skipping creation."
    else
        read -sp "Enter your Claude API key: " CLAUDE_API_KEY
        echo
        
        if [ -z "$CLAUDE_API_KEY" ]; then
            warning "Claude API key not provided. Service will run without AI features."
        else
            echo -n "$CLAUDE_API_KEY" | gcloud secrets create code-reviewer-claude-key \
                --data-file=- \
                --project="$PROJECT_ID" || error "Failed to create secret"
            log "Secret created ✓"
        fi
    fi
}

# Build and push CodeReviewer
deploy_codereviewer() {
    log "Deploying CodeReviewer service..."
    
    # Build using Cloud Build
    log "Building CodeReviewer image using Cloud Build..."
    gcloud builds submit \
        --config=cloudbuild.yaml \
        --project="$PROJECT_ID" \
        . || error "Cloud Build failed for CodeReviewer"
    
    log "CodeReviewer image built ✓"
    
    # Deploy to Cloud Run
    log "Deploying to Cloud Run..."
    gcloud run deploy "$CODEREVIEWER_SERVICE" \
        --image="gcr.io/$PROJECT_ID/$CODEREVIEWER_SERVICE:latest" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --memory=1Gi \
        --cpu=2 \
        --timeout=3600 \
        --set-env-vars="PORT=8080,HOST=0.0.0.0,CLAUDE_AGENT_SDK_ENABLED=true" \
        --project="$PROJECT_ID" || error "Failed to deploy CodeReviewer to Cloud Run"
    
    CODEREVIEWER_URL=$(gcloud run services describe "$CODEREVIEWER_SERVICE" \
        --region="$REGION" \
        --format='value(status.url)' \
        --project="$PROJECT_ID")
    
    log "CodeReviewer deployed ✓"
    log "URL: $CODEREVIEWER_URL"
}

# Build and push Autonomyx Landing
deploy_landing() {
    log "Deploying Autonomyx Landing page..."
    
    cd ../autonomyx-landing || error "autonomyx-landing directory not found"
    
    # Build using Cloud Build
    log "Building Autonomyx Landing image using Cloud Build..."
    gcloud builds submit \
        --config=cloudbuild.yaml \
        --project="$PROJECT_ID" \
        . || error "Cloud Build failed for Autonomyx Landing"
    
    log "Autonomyx Landing image built ✓"
    
    # Deploy to Cloud Run
    log "Deploying to Cloud Run..."
    gcloud run deploy "$LANDING_SERVICE" \
        --image="gcr.io/$PROJECT_ID/$LANDING_SERVICE:latest" \
        --region="$REGION" \
        --platform=managed \
        --allow-unauthenticated \
        --memory=256Mi \
        --cpu=1 \
        --timeout=3600 \
        --project="$PROJECT_ID" || error "Failed to deploy Autonomyx Landing to Cloud Run"
    
    LANDING_URL=$(gcloud run services describe "$LANDING_SERVICE" \
        --region="$REGION" \
        --format='value(status.url)' \
        --project="$PROJECT_ID")
    
    log "Autonomyx Landing deployed ✓"
    log "URL: $LANDING_URL"
    
    cd ../code-reviewer || error "Failed to return to code-reviewer directory"
}

# Print deployment summary
print_summary() {
    log "======================================"
    log "DEPLOYMENT COMPLETE ✓"
    log "======================================"
    echo
    echo "CodeReviewer Service:"
    echo "  URL: $CODEREVIEWER_URL"
    echo "  Health Check: $CODEREVIEWER_URL/healthz"
    echo "  API Docs: $CODEREVIEWER_URL/docs"
    echo
    echo "Autonomyx Landing Page:"
    echo "  URL: $LANDING_URL"
    echo "  Health Check: $LANDING_URL/healthz"
    echo
    echo "Container Registry (gcr.io):"
    echo "  - gcr.io/$PROJECT_ID/code-reviewer:latest"
    echo "  - gcr.io/$PROJECT_ID/autonomyx-landing:latest"
    echo
    echo "Next Steps:"
    echo "  1. Test services:"
    echo "     curl $CODEREVIEWER_URL/healthz"
    echo "     curl $LANDING_URL/healthz"
    echo "  2. View logs:"
    echo "     gcloud logs read --limit=50 --project=$PROJECT_ID"
    echo "  3. Manage services:"
    echo "     gcloud run services list --region=$REGION --project=$PROJECT_ID"
    echo
}

# Main execution
main() {
    log "Autonomyx Google Cloud Run Deployment"
    log "======================================"
    echo
    
    check_prerequisites
    validate_project
    enable_apis
    create_secrets
    deploy_codereviewer
    deploy_landing
    print_summary
}

main "$@"
