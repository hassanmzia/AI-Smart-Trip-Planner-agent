# =============================================================================
# Azure AKS Variables
# =============================================================================

variable "azure_location" {
  description = "Azure region"
  type        = string
  default     = "East US"
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

variable "kubernetes_version" {
  description = "Kubernetes version for AKS"
  type        = string
  default     = "1.29"
}

# Networking
variable "vnet_cidr" {
  description = "VNet address space"
  type        = string
  default     = "10.0.0.0/16"
}

variable "aks_subnet_cidr" {
  description = "AKS subnet CIDR"
  type        = string
  default     = "10.0.0.0/20"
}

variable "database_subnet_cidr" {
  description = "Database subnet CIDR"
  type        = string
  default     = "10.0.16.0/24"
}

variable "redis_subnet_cidr" {
  description = "Redis subnet CIDR"
  type        = string
  default     = "10.0.17.0/24"
}

variable "appgw_subnet_cidr" {
  description = "Application Gateway subnet CIDR"
  type        = string
  default     = "10.0.18.0/24"
}

# AKS Node Pools
variable "general_node_vm_size" {
  description = "VM size for general node pool"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "general_node_min_count" {
  type    = number
  default = 2
}

variable "general_node_max_count" {
  type    = number
  default = 6
}

variable "worker_node_vm_size" {
  description = "VM size for worker node pool"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "worker_node_min_count" {
  type    = number
  default = 1
}

variable "worker_node_max_count" {
  type    = number
  default = 5
}

# PostgreSQL
variable "postgres_sku" {
  description = "Azure PostgreSQL SKU"
  type        = string
  default     = "B_Standard_B2s"
}

variable "postgres_storage_mb" {
  description = "PostgreSQL storage in MB"
  type        = number
  default     = 32768
}

variable "postgres_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

# Redis
variable "redis_capacity" {
  description = "Redis cache capacity"
  type        = number
  default     = 1
}

variable "redis_family" {
  description = "Redis cache family"
  type        = string
  default     = "C"
}

variable "redis_sku" {
  description = "Redis cache SKU"
  type        = string
  default     = "Standard"
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
