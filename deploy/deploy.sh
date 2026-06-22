#!/bin/bash
# ─────────────────────────────────────────────────────────────────────
# deploy.sh — One-command GCP Cloud Run deployment
# Usage: bash deploy/deploy.sh
# ─────────────────────────────────────────────────────────────────────

set -e

# ── CONFIGURE THESE ───────────────────────────────────────────────────
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="voice-orchestrator"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Building and deploying $SERVICE_NAME to GCP Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region:  $REGION"
echo ""

# Build and push Docker image
echo "📦 Building Docker image..."
gcloud builds submit --tag "$IMAGE" --project "$PROJECT_ID" .

echo ""
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 3 \
  --timeout 300 \
  --set-secrets="MONGODB_URI=MONGODB_URI:latest,VAPI_API_KEY=VAPI_API_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,VAPI_PHONE_NUMBER_ID=VAPI_PHONE_NUMBER_ID:latest" \
  --project "$PROJECT_ID"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌍 Service URL:"
gcloud run services describe "$SERVICE_NAME" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --format 'value(status.url)'
