#!/usr/bin/env bash
# =============================================================================
# Deploy to Hugging Face Spaces
# =============================================================================
# Prerequisites:
#   - huggingface-cli installed: pip install huggingface_hub
#   - Logged in: huggingface-cli login
#
# Usage:
#   ./deploy/huggingface/deploy.sh <your-hf-username>/<space-name>
#
# Example:
#   ./deploy/huggingface/deploy.sh myuser/ai-trip-planner
# =============================================================================

set -euo pipefail

SPACE_NAME="${1:?Usage: $0 <username/space-name>}"
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
WORK_DIR=$(mktemp -d)

echo "============================================"
echo "Deploying AI Trip Planner to HF Spaces"
echo "Space: ${SPACE_NAME}"
echo "============================================"

# Check prerequisites
command -v git >/dev/null 2>&1 || { echo "ERROR: git is required"; exit 1; }

# Clone or create the Space repo
echo ""
echo "Cloning HF Space repository..."
if git ls-remote "https://huggingface.co/spaces/${SPACE_NAME}" &>/dev/null; then
  git clone "https://huggingface.co/spaces/${SPACE_NAME}" "${WORK_DIR}/space"
else
  echo "Space doesn't exist yet. Creating..."
  mkdir -p "${WORK_DIR}/space"
  cd "${WORK_DIR}/space"
  git init
  git remote add origin "https://huggingface.co/spaces/${SPACE_NAME}"
fi

cd "${WORK_DIR}/space"

# Copy application code
echo "Copying application code..."
rm -rf backend frontend mcp-server

cp -r "${ROOT_DIR}/backend" .
cp -r "${ROOT_DIR}/frontend" .
cp -r "${ROOT_DIR}/mcp-server" .

# Copy HF-specific files
cp "${ROOT_DIR}/deploy/huggingface/Dockerfile" .
cp "${ROOT_DIR}/deploy/huggingface/README.md" .

# Clean up unnecessary files
rm -rf backend/venv backend/__pycache__ backend/.pytest_cache
rm -rf frontend/node_modules frontend/dist
rm -rf mcp-server/venv mcp-server/__pycache__
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Commit and push
echo ""
echo "Committing and pushing to HF Spaces..."
git add -A
git commit -m "Deploy AI Trip Planner to HF Spaces" 2>/dev/null || echo "No changes to commit"
git push origin main 2>/dev/null || git push -u origin HEAD:main

echo ""
echo "============================================"
echo "Deployment complete!"
echo "============================================"
echo "Space URL: https://huggingface.co/spaces/${SPACE_NAME}"
echo ""
echo "Remember to set Secrets in Space Settings:"
echo "  - OPENAI_API_KEY"
echo "  - SERP_API_KEY"
echo "============================================"

# Cleanup
rm -rf "${WORK_DIR}"
