#!/usr/bin/env bash
# =============================================================================
# On-Premises Kubernetes Setup for AI Smart Trip Planner
# =============================================================================
# This script sets up prerequisites for on-prem deployment:
#   1. NGINX Ingress Controller
#   2. cert-manager (optional, for TLS certificates)
#   3. Deploys the application via Helm
#
# Prerequisites:
#   - kubectl configured with cluster access
#   - helm 3.x installed
#   - Docker images built and pushed to a registry
#
# Usage:
#   ./deploy/on-prem/setup.sh
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
NAMESPACE="trip-planner"

echo "============================================"
echo "On-Premises Kubernetes Setup"
echo "AI Smart Trip Planner"
echo "============================================"

# Check prerequisites
for cmd in kubectl helm; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: $cmd is required but not installed."
    exit 1
  fi
done

echo ""
echo "Verifying cluster connectivity..."
kubectl cluster-info || { echo "ERROR: Cannot connect to Kubernetes cluster"; exit 1; }

# Step 1: Install NGINX Ingress Controller
echo ""
echo "============================================"
echo "Step 1: Installing NGINX Ingress Controller"
echo "============================================"

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx 2>/dev/null || true
helm repo update

if ! helm status ingress-nginx -n ingress-nginx >/dev/null 2>&1; then
  helm install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.replicaCount=2 \
    --set controller.service.type=LoadBalancer \
    --wait
  echo "NGINX Ingress Controller installed."
else
  echo "NGINX Ingress Controller already installed."
fi

# Step 2: Install cert-manager (optional)
echo ""
echo "============================================"
echo "Step 2: Installing cert-manager"
echo "============================================"

helm repo add jetstack https://charts.jetstack.io 2>/dev/null || true
helm repo update

if ! helm status cert-manager -n cert-manager >/dev/null 2>&1; then
  helm install cert-manager jetstack/cert-manager \
    --namespace cert-manager \
    --create-namespace \
    --set crds.enabled=true \
    --wait
  echo "cert-manager installed."

  # Create ClusterIssuer for Let's Encrypt
  cat <<'EOF' | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF
  echo "Let's Encrypt ClusterIssuer created."
else
  echo "cert-manager already installed."
fi

# Step 3: Create namespace and TLS secret
echo ""
echo "============================================"
echo "Step 3: Setting up namespace and secrets"
echo "============================================"

kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# If you have existing TLS certificates, create a secret
if [ -f "${ROOT_DIR}/ssl/fullchain.pem" ] && [ -f "${ROOT_DIR}/ssl/private.key" ]; then
  echo "Found existing TLS certificates, creating secret..."
  kubectl create secret tls trip-planner-tls \
    --cert="${ROOT_DIR}/ssl/fullchain.pem" \
    --key="${ROOT_DIR}/ssl/private.key" \
    --namespace="${NAMESPACE}" \
    --dry-run=client -o yaml | kubectl apply -f -
  TLS_SECRET="trip-planner-tls"
  echo "TLS secret created."
else
  echo "No TLS certificates found in ssl/ directory."
  echo "cert-manager will handle certificate provisioning."
  TLS_SECRET=""
fi

# Step 4: Deploy application
echo ""
echo "============================================"
echo "Step 4: Deploying AI Trip Planner"
echo "============================================"

echo ""
echo "Deploying with Helm..."
echo "NOTE: Set your API keys and domain by adding --set flags"
echo ""

helm upgrade --install trip-planner "${ROOT_DIR}/helm/ai-trip-planner" \
  --namespace "${NAMESPACE}" \
  --values "${ROOT_DIR}/helm/ai-trip-planner/cloud-values/on-prem.yaml" \
  ${TLS_SECRET:+--set ingress.tls.secretName="${TLS_SECRET}"} \
  --wait \
  --timeout 10m

echo ""
echo "============================================"
echo "Deployment Complete!"
echo "============================================"
echo ""

# Show status
echo "Pod status:"
kubectl get pods -n "${NAMESPACE}"

echo ""
echo "Services:"
kubectl get svc -n "${NAMESPACE}"

echo ""
echo "Ingress:"
kubectl get ingress -n "${NAMESPACE}"

echo ""
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
echo "============================================"
echo "Next Steps:"
echo "============================================"
echo "1. Point your domain DNS to the ingress IP: ${INGRESS_IP}"
echo "2. Set API keys:"
echo "   helm upgrade trip-planner ${ROOT_DIR}/helm/ai-trip-planner \\"
echo "     -n ${NAMESPACE} \\"
echo "     -f ${ROOT_DIR}/helm/ai-trip-planner/cloud-values/on-prem.yaml \\"
echo "     --set secrets.openaiApiKey=YOUR_KEY \\"
echo "     --set secrets.serpApiKey=YOUR_KEY \\"
echo "     --set global.domain=your-domain.com"
echo "============================================"
