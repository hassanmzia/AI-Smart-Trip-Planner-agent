# AI Smart Trip Planner - Deployment Guide

## Architecture Overview

The application consists of 9 services:

| Service | Type | Description |
|---------|------|-------------|
| **Backend** | Deployment | Django REST API + LangChain AI agents |
| **Frontend** | Deployment | React + Vite + TypeScript SPA |
| **MCP Server** | Deployment | FastAPI agent communication server |
| **Celery Worker** | Deployment | Async task processing |
| **Celery Beat** | Deployment | Scheduled task scheduler |
| **Nginx** | Deployment | Reverse proxy with SSL (on-prem only) |
| **PostgreSQL** | StatefulSet | Primary database |
| **Redis** | StatefulSet | Cache & message broker |
| **RabbitMQ** | StatefulSet | Message queue for Celery |

## Prerequisites

- **kubectl** >= 1.28
- **Helm** >= 3.12
- **Docker** for building images
- A Kubernetes cluster (on-prem, EKS, AKS, or GKE)

## Quick Start

### 1. Build and Push Docker Images

```bash
# Make build script executable
chmod +x deploy/scripts/build-and-push.sh

# Build and push to your registry
./deploy/scripts/build-and-push.sh <your-registry-url> v1.0.0
```

### 2. Deploy

```bash
chmod +x deploy/scripts/deploy-helm.sh

# Deploy to your target environment
./deploy/scripts/deploy-helm.sh <on-prem|aws|azure|gcp> \
  --set global.domain=your-domain.com \
  --set secrets.openaiApiKey=sk-your-key \
  --set secrets.serpApiKey=your-key \
  --set backend.image.repository=your-registry/backend \
  --set backend.image.tag=v1.0.0 \
  --set frontend.image.repository=your-registry/frontend \
  --set frontend.image.tag=v1.0.0 \
  --set mcpServer.image.repository=your-registry/mcp-server \
  --set mcpServer.image.tag=v1.0.0
```

---

## Deployment Option 1: On-Premises Kubernetes

### Prerequisites
- Kubernetes cluster (kubeadm, k3s, RKE2, etc.)
- NGINX Ingress Controller
- Storage provisioner (local-path, Longhorn, Rook-Ceph)

### Setup

```bash
# Run the automated setup script
chmod +x deploy/on-prem/setup.sh
./deploy/on-prem/setup.sh
```

### Manual Deployment

```bash
# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace

# Deploy the application
helm install trip-planner ./helm/ai-trip-planner \
  --namespace trip-planner --create-namespace \
  -f helm/ai-trip-planner/cloud-values/on-prem.yaml \
  --set global.domain=trip-planner.yourcompany.com \
  --set secrets.openaiApiKey=sk-your-key \
  --set secrets.serpApiKey=your-key \
  --set global.storageClass=local-path
```

### With Existing TLS Certificates

```bash
# Create TLS secret
kubectl create secret tls trip-planner-tls \
  --cert=ssl/fullchain.pem \
  --key=ssl/private.key \
  -n trip-planner

# Deploy with TLS secret
helm install trip-planner ./helm/ai-trip-planner \
  -f helm/ai-trip-planner/cloud-values/on-prem.yaml \
  --set ingress.tls.secretName=trip-planner-tls \
  -n trip-planner
```

---

## Deployment Option 2: AWS (EKS)

### Using Terraform (Recommended)

Provisions: VPC, EKS, RDS PostgreSQL, ElastiCache Redis, Amazon MQ, ECR, ALB.

```bash
cd deploy/aws

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize and deploy
terraform init
terraform plan
terraform apply
```

### Using Helm Only (Existing EKS Cluster)

```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push images
./deploy/scripts/build-and-push.sh <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-trip-planner v1.0.0

# Install AWS Load Balancer Controller (if not installed)
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system --set clusterName=your-cluster

# Deploy
helm install trip-planner ./helm/ai-trip-planner \
  -f helm/ai-trip-planner/cloud-values/aws.yaml \
  --namespace trip-planner --create-namespace \
  --set global.domain=trip-planner.example.com \
  --set secrets.openaiApiKey=sk-your-key \
  --set postgresql.external.host=your-rds-endpoint.rds.amazonaws.com \
  --set redis.external.host=your-redis.cache.amazonaws.com \
  --set rabbitmq.external.host=your-mq-endpoint \
  --set ingress.annotations."alb\.ingress\.kubernetes\.io/certificate-arn"=arn:aws:acm:... \
  --set backend.image.repository=<account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-trip-planner/backend
```

---

## Deployment Option 3: Azure (AKS)

### Using Terraform (Recommended)

Provisions: Resource Group, VNet, AKS, Azure PostgreSQL Flexible Server, Azure Cache for Redis, ACR, Application Gateway.

```bash
cd deploy/azure

# Authenticate
az login

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize and deploy
terraform init
terraform plan
terraform apply

# Configure kubectl
az aks get-credentials --resource-group ai-trip-planner-production-rg --name ai-trip-planner-aks
```

### Using Helm Only (Existing AKS Cluster)

```bash
# Authenticate with ACR
az acr login --name yourregistry

# Build and push images
./deploy/scripts/build-and-push.sh yourregistry.azurecr.io v1.0.0

# Deploy
helm install trip-planner ./helm/ai-trip-planner \
  -f helm/ai-trip-planner/cloud-values/azure.yaml \
  --namespace trip-planner --create-namespace \
  --set global.domain=trip-planner.example.com \
  --set secrets.openaiApiKey=sk-your-key \
  --set postgresql.external.host=your-server.postgres.database.azure.com \
  --set redis.external.host=your-redis.redis.cache.windows.net \
  --set redis.external.port=6380 \
  --set backend.image.repository=yourregistry.azurecr.io/backend
```

---

## Deployment Option 4: GCP (GKE)

### Using Terraform (Recommended)

Provisions: VPC, GKE, Cloud SQL, Memorystore Redis, Artifact Registry, Global Static IP, Managed SSL Certificate.

```bash
cd deploy/gcp

# Authenticate
gcloud auth application-default login

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize and deploy
terraform init
terraform plan
terraform apply

# Configure kubectl
gcloud container clusters get-credentials ai-trip-planner-gke --region us-central1
```

### Using Helm Only (Existing GKE Cluster)

```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push images
./deploy/scripts/build-and-push.sh us-central1-docker.pkg.dev/your-project/ai-trip-planner v1.0.0

# Deploy
helm install trip-planner ./helm/ai-trip-planner \
  -f helm/ai-trip-planner/cloud-values/gcp.yaml \
  --namespace trip-planner --create-namespace \
  --set global.domain=trip-planner.example.com \
  --set secrets.openaiApiKey=sk-your-key \
  --set postgresql.external.host=10.x.x.x \
  --set redis.external.host=10.x.x.x \
  --set backend.image.repository=us-central1-docker.pkg.dev/your-project/ai-trip-planner/backend
```

---

## Common Operations

### Upgrade

```bash
helm upgrade trip-planner ./helm/ai-trip-planner \
  -f helm/ai-trip-planner/cloud-values/<environment>.yaml \
  -n trip-planner --reuse-values
```

### Rollback

```bash
# List revisions
helm history trip-planner -n trip-planner

# Rollback to previous version
helm rollback trip-planner <revision> -n trip-planner
```

### Scale

```bash
# Scale backend replicas
kubectl scale deployment trip-planner-ai-trip-planner-backend \
  --replicas=4 -n trip-planner

# Or via Helm
helm upgrade trip-planner ./helm/ai-trip-planner \
  -n trip-planner --reuse-values \
  --set backend.replicaCount=4
```

### View Logs

```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend -n trip-planner -f

# Celery worker logs
kubectl logs -l app.kubernetes.io/component=celery-worker -n trip-planner -f

# All pods
kubectl get pods -n trip-planner
```

### Run Django Management Commands

```bash
# Get a backend pod name
POD=$(kubectl get pods -n trip-planner -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -it $POD -n trip-planner -- python manage.py migrate

# Create superuser
kubectl exec -it $POD -n trip-planner -- python manage.py createsuperuser

# Collect static files
kubectl exec -it $POD -n trip-planner -- python manage.py collectstatic --noinput
```

### Uninstall

```bash
helm uninstall trip-planner -n trip-planner
kubectl delete namespace trip-planner
```

---

## Configuration Reference

### Required Secrets

| Secret | Description | Required |
|--------|-------------|----------|
| `secrets.djangoSecretKey` | Django secret key | Yes |
| `secrets.openaiApiKey` | OpenAI API key for AI agents | Yes |
| `secrets.serpApiKey` | SerpAPI key for travel search | Recommended |
| `secrets.stripeSecretKey` | Stripe secret key | For payments |
| `secrets.stripePublishableKey` | Stripe publishable key | For payments |
| `secrets.weatherApiKey` | Weather API key | Optional |
| `secrets.postgresPassword` | PostgreSQL password | Yes |
| `secrets.redisPassword` | Redis password | Yes |
| `secrets.rabbitmqPassword` | RabbitMQ password | Yes |

### Using Existing Secrets

Instead of passing secrets via Helm values, create a Kubernetes secret manually:

```bash
kubectl create secret generic trip-planner-secrets \
  --from-literal=django-secret-key='your-key' \
  --from-literal=openai-api-key='sk-xxx' \
  --from-literal=postgres-password='password' \
  --from-literal=redis-password='password' \
  --from-literal=rabbitmq-password='password' \
  --from-literal=serp-api-key='key' \
  --from-literal=stripe-secret-key='key' \
  --from-literal=stripe-publishable-key='key' \
  --from-literal=weather-api-key='key' \
  -n trip-planner

# Then reference it in Helm
helm install trip-planner ./helm/ai-trip-planner \
  --set secrets.existingSecret=trip-planner-secrets \
  -n trip-planner
```

### Cloud Provider Comparison

| Feature | On-Prem | AWS | Azure | GCP |
|---------|---------|-----|-------|-----|
| **K8s Service** | Self-managed | EKS | AKS | GKE |
| **Database** | In-cluster PostgreSQL | RDS | Azure PostgreSQL Flexible | Cloud SQL |
| **Cache** | In-cluster Redis | ElastiCache | Azure Cache for Redis | Memorystore |
| **Message Queue** | In-cluster RabbitMQ | Amazon MQ | In-cluster RabbitMQ | In-cluster RabbitMQ |
| **Load Balancer** | NGINX Ingress | ALB | Application Gateway | GCE Ingress |
| **Container Registry** | Self-hosted | ECR | ACR | Artifact Registry |
| **TLS Certificates** | cert-manager | ACM | cert-manager | Managed Certificates |
| **Storage Class** | local-path/Longhorn | gp3 | managed-csi | standard-rwo |
| **Autoscaling** | Optional | Enabled | Enabled | Enabled |
| **IaC** | Shell script | Terraform | Terraform | Terraform |
