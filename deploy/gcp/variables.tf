# =============================================================================
# GCP GKE Variables
# =============================================================================

variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "ai-trip-planner"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

# Networking
variable "gke_subnet_cidr" {
  description = "GKE subnet CIDR"
  type        = string
  default     = "10.0.0.0/20"
}

variable "pods_cidr" {
  description = "Pods secondary range CIDR"
  type        = string
  default     = "10.4.0.0/14"
}

variable "services_cidr" {
  description = "Services secondary range CIDR"
  type        = string
  default     = "10.8.0.0/20"
}

variable "master_cidr" {
  description = "GKE master CIDR"
  type        = string
  default     = "172.16.0.0/28"
}

# GKE Node Pools
variable "general_node_machine_type" {
  description = "Machine type for general nodes"
  type        = string
  default     = "e2-standard-2"
}

variable "general_node_min_count" {
  type    = number
  default = 2
}

variable "general_node_max_count" {
  type    = number
  default = 6
}

variable "worker_node_machine_type" {
  description = "Machine type for worker nodes"
  type        = string
  default     = "e2-standard-4"
}

variable "worker_node_min_count" {
  type    = number
  default = 1
}

variable "worker_node_max_count" {
  type    = number
  default = 5
}

# Cloud SQL
variable "cloudsql_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-custom-2-4096"
}

variable "cloudsql_disk_size" {
  description = "Cloud SQL disk size in GB"
  type        = number
  default     = 20
}

variable "postgres_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

# Memorystore Redis
variable "redis_memory_size_gb" {
  description = "Redis memory size in GB"
  type        = number
  default     = 1
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
