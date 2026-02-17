# =============================================================================
# AWS EKS Infrastructure for AI Smart Trip Planner
# =============================================================================
# Usage:
#   cd deploy/aws
#   terraform init
#   terraform plan -var-file="terraform.tfvars"
#   terraform apply -var-file="terraform.tfvars"
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
  }

  # Uncomment for remote state
  # backend "s3" {
  #   bucket         = "trip-planner-terraform-state"
  #   key            = "aws/eks/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "ai-trip-planner"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# -----------------------------------------------------------------------------
# VPC
# -----------------------------------------------------------------------------
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets
  database_subnets = var.database_subnets

  enable_nat_gateway     = true
  single_nat_gateway     = var.environment != "production"
  enable_dns_hostnames   = true
  enable_dns_support     = true

  # Tags required for EKS
  public_subnet_tags = {
    "kubernetes.io/role/elb"                    = 1
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb"           = 1
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"
  }

  tags = {
    Environment = var.environment
  }
}

# -----------------------------------------------------------------------------
# EKS Cluster
# -----------------------------------------------------------------------------
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  # Cluster addons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent              = true
      service_account_role_arn = module.ebs_csi_irsa.iam_role_arn
    }
  }

  # Managed Node Groups
  eks_managed_node_groups = {
    # General workloads (backend, frontend, mcp-server)
    general = {
      name           = "general"
      instance_types = var.general_node_instance_types
      min_size       = var.general_node_min_size
      max_size       = var.general_node_max_size
      desired_size   = var.general_node_desired_size

      labels = {
        workload = "general"
      }
    }

    # Worker nodes (celery workers, data processing)
    workers = {
      name           = "workers"
      instance_types = var.worker_node_instance_types
      min_size       = var.worker_node_min_size
      max_size       = var.worker_node_max_size
      desired_size   = var.worker_node_desired_size

      labels = {
        workload = "worker"
      }

      taints = {
        dedicated = {
          key    = "workload"
          value  = "worker"
          effect = "PREFER_NO_SCHEDULE"
        }
      }
    }
  }

  tags = {
    Environment = var.environment
  }
}

# EBS CSI Driver IRSA
module "ebs_csi_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name             = "${var.cluster_name}-ebs-csi"
  attach_ebs_csi_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:ebs-csi-controller-sa"]
    }
  }
}

# -----------------------------------------------------------------------------
# RDS PostgreSQL
# -----------------------------------------------------------------------------
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "${var.project_name}-postgres"

  engine               = "postgres"
  engine_version       = "15"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = var.rds_instance_class

  allocated_storage     = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage

  db_name  = "travel_agent_db"
  username = "travel_admin"
  port     = 5432

  multi_az               = var.environment == "production"
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = 7
  deletion_protection     = var.environment == "production"
  skip_final_snapshot     = var.environment != "production"

  performance_insights_enabled = true

  tags = {
    Environment = var.environment
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

# -----------------------------------------------------------------------------
# ElastiCache Redis
# -----------------------------------------------------------------------------
resource "aws_elasticache_subnet_group" "redis" {
  name       = "${var.project_name}-redis"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  name_prefix = "${var.project_name}-redis-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  tags = {
    Name = "${var.project_name}-redis-sg"
  }
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = "${var.project_name}-redis"
  description          = "Redis for AI Trip Planner"
  node_type            = var.redis_node_type
  num_cache_clusters   = var.environment == "production" ? 2 : 1
  port                 = 6379

  subnet_group_name  = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.redis_auth_token

  automatic_failover_enabled = var.environment == "production"

  tags = {
    Environment = var.environment
  }
}

# -----------------------------------------------------------------------------
# Amazon MQ (RabbitMQ)
# -----------------------------------------------------------------------------
resource "aws_security_group" "mq" {
  name_prefix = "${var.project_name}-mq-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5671
    to_port         = 5671
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  ingress {
    from_port       = 15671
    to_port         = 15671
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  tags = {
    Name = "${var.project_name}-mq-sg"
  }
}

resource "aws_mq_broker" "rabbitmq" {
  broker_name = "${var.project_name}-rabbitmq"

  engine_type        = "RabbitMQ"
  engine_version     = "3.12"
  host_instance_type = var.mq_instance_type
  deployment_mode    = var.environment == "production" ? "CLUSTER_MULTI_AZ" : "SINGLE_INSTANCE"

  security_groups = [aws_security_group.mq.id]
  subnet_ids      = var.environment == "production" ? slice(module.vpc.private_subnets, 0, 2) : [module.vpc.private_subnets[0]]

  user {
    username = "travel_mq"
    password = var.rabbitmq_password
  }

  publicly_accessible = false

  tags = {
    Environment = var.environment
  }
}

# -----------------------------------------------------------------------------
# ECR Repositories
# -----------------------------------------------------------------------------
resource "aws_ecr_repository" "repos" {
  for_each = toset(["backend", "frontend", "mcp-server", "nginx"])

  name                 = "${var.project_name}/${each.key}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
  }
}

# -----------------------------------------------------------------------------
# AWS Load Balancer Controller
# -----------------------------------------------------------------------------
module "lb_controller_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name                              = "${var.cluster_name}-lb-controller"
  attach_load_balancer_controller_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
}

# -----------------------------------------------------------------------------
# ACM Certificate
# -----------------------------------------------------------------------------
resource "aws_acm_certificate" "main" {
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Environment = var.environment
  }
}

# -----------------------------------------------------------------------------
# Kubernetes & Helm Providers
# -----------------------------------------------------------------------------
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", var.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", var.cluster_name]
    }
  }
}

# AWS Load Balancer Controller Helm Release
resource "helm_release" "aws_lb_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = "1.7.1"

  set {
    name  = "clusterName"
    value = var.cluster_name
  }

  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = module.lb_controller_irsa.iam_role_arn
  }

  depends_on = [module.eks]
}

# Deploy application via Helm
resource "helm_release" "trip_planner" {
  name       = "trip-planner"
  chart      = "../../helm/ai-trip-planner"
  namespace  = "trip-planner"
  create_namespace = true

  values = [
    file("../../helm/ai-trip-planner/cloud-values/aws.yaml")
  ]

  set {
    name  = "global.domain"
    value = var.domain_name
  }

  set_sensitive {
    name  = "secrets.openaiApiKey"
    value = var.openai_api_key
  }

  set_sensitive {
    name  = "secrets.serpApiKey"
    value = var.serp_api_key
  }

  set_sensitive {
    name  = "secrets.stripeSecretKey"
    value = var.stripe_secret_key
  }

  set_sensitive {
    name  = "secrets.postgresPassword"
    value = module.rds.db_instance_password
  }

  set_sensitive {
    name  = "secrets.redisPassword"
    value = var.redis_auth_token
  }

  set_sensitive {
    name  = "secrets.rabbitmqPassword"
    value = var.rabbitmq_password
  }

  set {
    name  = "postgresql.external.host"
    value = module.rds.db_instance_address
  }

  set {
    name  = "redis.external.host"
    value = aws_elasticache_replication_group.redis.primary_endpoint_address
  }

  set {
    name  = "rabbitmq.external.host"
    value = aws_mq_broker.rabbitmq.instances[0].endpoints[0]
  }

  set {
    name  = "ingress.annotations.alb\\.ingress\\.kubernetes\\.io/certificate-arn"
    value = aws_acm_certificate.main.arn
  }

  set {
    name  = "ingress.annotations.alb\\.ingress\\.kubernetes\\.io/subnets"
    value = join("\\,", module.vpc.public_subnets)
  }

  set {
    name  = "backend.image.repository"
    value = aws_ecr_repository.repos["backend"].repository_url
  }

  set {
    name  = "frontend.image.repository"
    value = aws_ecr_repository.repos["frontend"].repository_url
  }

  set {
    name  = "mcpServer.image.repository"
    value = aws_ecr_repository.repos["mcp-server"].repository_url
  }

  depends_on = [
    module.eks,
    module.rds,
    aws_elasticache_replication_group.redis,
    aws_mq_broker.rabbitmq,
    helm_release.aws_lb_controller,
  ]
}
