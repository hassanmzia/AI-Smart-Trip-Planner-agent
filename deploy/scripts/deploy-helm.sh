#!/usr/bin/env bash
# =============================================================================
# Deploy AI Trip Planner with Helm
# =============================================================================
# Usage:
#   ./deploy/scripts/deploy-helm.sh <environment> [extra-args...]
#
# Examples:
#   ./deploy/scripts/deploy-helm.sh on-prem
#   ./deploy/scripts/deploy-helm.sh aws --set global.domain=myapp.com
#   ./deploy/scripts/deploy-helm.sh azure --set secrets.openaiApiKey=sk-xxx
#   ./deploy/scripts/deploy-helm.sh gcp
# =============================================================================

set -euo pipefail

ENVIRONMENT="${1:?Usage: $0 <on-prem|aws|azure|gcp> [extra-helm-args...]}"
shift
EXTRA_ARGS=("$@")

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
CHART_DIR="${ROOT_DIR}/helm/ai-trip-planner"
NAMESPACE="trip-planner"
RELEASE_NAME="trip-planner"

# Validate environment
case "${ENVIRONMENT}" in
  on-prem|aws|azure|gcp)
    VALUES_FILE="${CHART_DIR}/cloud-values/${ENVIRONMENT}.yaml"
    ;;
  *)
    echo "ERROR: Invalid environment '${ENVIRONMENT}'"
    echo "Valid options: on-prem, aws, azure, gcp"
    exit 1
    ;;
esac

echo "============================================"
echo "Deploying AI Trip Planner"
echo "Environment: ${ENVIRONMENT}"
echo "Namespace:   ${NAMESPACE}"
echo "Release:     ${RELEASE_NAME}"
echo "============================================"

# Check prerequisites
command -v helm >/dev/null 2>&1 || { echo "ERROR: helm is not installed"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl is not installed"; exit 1; }

# Verify cluster connectivity
echo ""
echo "Verifying cluster connectivity..."
kubectl cluster-info || { echo "ERROR: Cannot connect to Kubernetes cluster"; exit 1; }

# Create namespace if it doesn't exist
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# Check if this is an install or upgrade
if helm status "${RELEASE_NAME}" -n "${NAMESPACE}" >/dev/null 2>&1; then
  ACTION="upgrade"
  echo "Existing release found - performing upgrade..."
else
  ACTION="install"
  echo "No existing release - performing fresh install..."
fi

# Deploy
echo ""
echo "Running helm ${ACTION}..."
helm "${ACTION}" "${RELEASE_NAME}" "${CHART_DIR}" \
  --namespace "${NAMESPACE}" \
  --values "${VALUES_FILE}" \
  --wait \
  --timeout 10m \
  "${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}"

echo ""
echo "============================================"
echo "Deployment complete!"
echo "============================================"

# Show status
echo ""
echo "Pod status:"
kubectl get pods -n "${NAMESPACE}" -o wide

echo ""
echo "Services:"
kubectl get svc -n "${NAMESPACE}"

echo ""
echo "Ingress:"
kubectl get ingress -n "${NAMESPACE}"
