#!/bin/bash

# Cấu hình
PROJECT_ID=$(gcloud config get-value project)
REGION=asia-southeast1
REPO_NAME=hello-docker-repo
IMAGE_NAME=hello-docker
SERVICE_NAME=hello-docker-service
IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME"

echo "🔧 Project ID: $PROJECT_ID"
echo "📍 Region: $REGION"
echo "🐳 Image URI: $IMAGE_URI"
echo ""

# Enable Artifact Registry API (nếu chưa bật)
echo "🔓 Enabling Artifact Registry API..."
gcloud services enable artifactregistry.googleapis.com

# Tạo repository nếu chưa có
echo "📁 Checking Docker repository..."
gcloud artifacts repositories describe $REPO_NAME --location=$REGION > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "📦 Repository not found. Creating..."
  gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for $IMAGE_NAME"
else
  echo "✅ Repository already exists."
fi

# Kiểm tra image đã tồn tại chưa
echo "🔍 Checking if Docker image exists in Artifact Registry..."
EXISTING_IMAGE=$(gcloud artifacts docker images list "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME" \
  --format="value(IMAGE)" | grep "$IMAGE_NAME")

if [ -z "$EXISTING_IMAGE" ]; then
  echo "📤 Image not found. Building and pushing Docker image..."
  docker build -t $IMAGE_URI .
  docker push $IMAGE_URI
else
  echo "✅ Docker image already exists."
fi

# Gán quyền truy cập Artifact Registry cho Cloud Run service account
echo "🔐 Granting Artifact Registry access to Cloud Run..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
SERVICE_ACCOUNT="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/artifactregistry.reader" \
  --quiet

# Deploy lên Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_URI \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated

# In URL
echo "🌍 Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format='value(status.url)')

echo ""
echo "✅ DONE! Your app is live at:"
echo "👉 $SERVICE_URL"
