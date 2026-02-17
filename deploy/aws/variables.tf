# =============================================================================
# AWS EKS Variables
# =============================================================================

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "ai-trip-planner"
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "ai-trip-planner-eks"
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS"
  type        = string
  default     = "1.29"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

# VPC
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnets" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "database_subnets" {
  description = "Database subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]
}

# EKS Node Groups
variable "general_node_instance_types" {
  description = "Instance types for general workload nodes"
  type        = list(string)
  default     = ["t3.large"]
}

variable "general_node_min_size" {
  type    = number
  default = 2
}

variable "general_node_max_size" {
  type    = number
  default = 6
}

variable "general_node_desired_size" {
  type    = number
  default = 3
}

variable "worker_node_instance_types" {
  description = "Instance types for worker/celery nodes"
  type        = list(string)
  default     = ["t3.xlarge"]
}

variable "worker_node_min_size" {
  type    = number
  default = 1
}

variable "worker_node_max_size" {
  type    = number
  default = 5
}

variable "worker_node_desired_size" {
  type    = number
  default = 2
}

# RDS
variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "rds_allocated_storage" {
  type    = number
  default = 20
}

variable "rds_max_allocated_storage" {
  type    = number
  default = 100
}

# ElastiCache
variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.medium"
}

variable "redis_auth_token" {
  description = "Redis AUTH token"
  type        = string
  sensitive   = true
}

# Amazon MQ
variable "mq_instance_type" {
  description = "Amazon MQ instance type"
  type        = string
  default     = "mq.t3.micro"
}

variable "rabbitmq_password" {
  description = "RabbitMQ password"
  type        = string
  sensitive   = true
}

# API Keys
variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "serp_api_key" {
  description = "SerpAPI key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "stripe_secret_key" {
  description = "Stripe secret key"
  type        = string
  sensitive   = true
  default     = ""
}
