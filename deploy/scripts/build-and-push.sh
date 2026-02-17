#!/usr/bin/env bash
# =============================================================================
# Build and Push Docker Images
# =============================================================================
# Usage:
#   ./deploy/scripts/build-and-push.sh <registry> [tag]
#
# Examples:
#   # AWS ECR
#   ./deploy/scripts/build-and-push.sh 123456789.dkr.ecr.us-east-1.amazonaws.com/ai-trip-planner v1.0.0
#
#   # Azure ACR
#   ./deploy/scripts/build-and-push.sh aitripplanneracr.azurecr.io v1.0.0
#
#   # GCP Artifact Registry
#   ./deploy/scripts/build-and-push.sh us-central1-docker.pkg.dev/my-project/ai-trip-planner v1.0.0
#
#   # On-prem registry
#   ./deploy/scripts/build-and-push.sh registry.local:5000/ai-trip-planner v1.0.0
# =============================================================================

set -euo pipefail

REGISTRY="${1:?Usage: $0 <registry> [tag]}"
TAG="${2:-latest}"
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "============================================"
echo "Building and pushing images"
echo "Registry: ${REGISTRY}"
echo "Tag:      ${TAG}"
echo "============================================"

# Build backend
echo ""
echo "[1/4] Building backend image..."
docker build -t "${REGISTRY}/backend:${TAG}" \
  -f "${ROOT_DIR}/backend/Dockerfile" \
  "${ROOT_DIR}/backend"

# Build frontend
echo ""
echo "[2/4] Building frontend image..."
docker build -t "${REGISTRY}/frontend:${TAG}" \
  -f "${ROOT_DIR}/frontend/Dockerfile" \
  "${ROOT_DIR}/frontend"

# Build MCP server
echo ""
echo "[3/4] Building MCP server image..."
docker build -t "${REGISTRY}/mcp-server:${TAG}" \
  -f "${ROOT_DIR}/mcp-server/Dockerfile" \
  "${ROOT_DIR}/mcp-server"

# Build Nginx
echo ""
echo "[4/4] Building Nginx image..."
docker build -t "${REGISTRY}/nginx:${TAG}" \
  -f "${ROOT_DIR}/nginx/Dockerfile" \
  "${ROOT_DIR}/nginx" 2>/dev/null || {
  # If no Nginx Dockerfile exists, build from config
  echo "No nginx Dockerfile found, building from config..."
  cat > "/tmp/nginx-dockerfile" <<'DOCKERFILE'
FROM nginx:1.25-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/
EXPOSE 80 443
DOCKERFILE
  docker build -t "${REGISTRY}/nginx:${TAG}" \
    -f "/tmp/nginx-dockerfile" \
    "${ROOT_DIR}/nginx"
}

# Push all images
echo ""
echo "============================================"
echo "Pushing images to registry..."
echo "============================================"

for SERVICE in backend frontend mcp-server nginx; do
  echo "Pushing ${REGISTRY}/${SERVICE}:${TAG}..."
  docker push "${REGISTRY}/${SERVICE}:${TAG}"
done

echo ""
echo "============================================"
echo "All images built and pushed successfully!"
echo "============================================"
echo ""
echo "Images:"
for SERVICE in backend frontend mcp-server nginx; do
  echo "  - ${REGISTRY}/${SERVICE}:${TAG}"
done
