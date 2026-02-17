# =============================================================================
# Azure AKS Infrastructure for AI Smart Trip Planner
# =============================================================================
# Usage:
#   cd deploy/azure
#   terraform init
#   terraform plan -var-file="terraform.tfvars"
#   terraform apply -var-file="terraform.tfvars"
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
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
  # backend "azurerm" {
  #   resource_group_name  = "trip-planner-tfstate"
  #   storage_account_name = "tripplannertfstate"
  #   container_name       = "tfstate"
  #   key                  = "aks/terraform.tfstate"
  # }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# -----------------------------------------------------------------------------
# Resource Group
# -----------------------------------------------------------------------------
resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.azure_location

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# -----------------------------------------------------------------------------
# Virtual Network
# -----------------------------------------------------------------------------
resource "azurerm_virtual_network" "main" {
  name                = "${var.project_name}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = [var.vnet_cidr]
}

resource "azurerm_subnet" "aks" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.aks_subnet_cidr]
}

resource "azurerm_subnet" "database" {
  name                 = "database-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.database_subnet_cidr]

  delegation {
    name = "postgres-delegation"
    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}

resource "azurerm_subnet" "redis" {
  name                 = "redis-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.redis_subnet_cidr]
}

resource "azurerm_subnet" "appgw" {
  name                 = "appgw-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.appgw_subnet_cidr]
}

# -----------------------------------------------------------------------------
# AKS Cluster
# -----------------------------------------------------------------------------
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project_name}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.project_name
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name                = "general"
    vm_size             = var.general_node_vm_size
    min_count           = var.general_node_min_count
    max_count           = var.general_node_max_count
    auto_scaling_enabled = true
    vnet_subnet_id      = azurerm_subnet.aks.id
    os_disk_size_gb     = 50

    node_labels = {
      workload = "general"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "calico"
    load_balancer_sku = "standard"
    service_cidr      = "10.1.0.0/16"
    dns_service_ip    = "10.1.0.10"
  }

  ingress_application_gateway {
    subnet_id = azurerm_subnet.appgw.id
  }

  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  tags = {
    Environment = var.environment
  }
}

# Worker node pool for Celery workers
resource "azurerm_kubernetes_cluster_node_pool" "workers" {
  name                  = "workers"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = var.worker_node_vm_size
  min_count             = var.worker_node_min_count
  max_count             = var.worker_node_max_count
  auto_scaling_enabled  = true
  vnet_subnet_id        = azurerm_subnet.aks.id

  node_labels = {
    workload = "worker"
  }

  node_taints = [
    "workload=worker:PreferNoSchedule"
  ]
}

# -----------------------------------------------------------------------------
# Azure Database for PostgreSQL - Flexible Server
# -----------------------------------------------------------------------------
resource "azurerm_private_dns_zone" "postgres" {
  name                = "${var.project_name}.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                  = "postgres-vnet-link"
  private_dns_zone_name = azurerm_private_dns_zone.postgres.name
  virtual_network_id    = azurerm_virtual_network.main.id
  resource_group_name   = azurerm_resource_group.main.name
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.project_name}-postgres"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "15"
  delegated_subnet_id    = azurerm_subnet.database.id
  private_dns_zone_id    = azurerm_private_dns_zone.postgres.id
  administrator_login    = "travel_admin"
  administrator_password = var.postgres_password
  zone                   = "1"

  storage_mb = var.postgres_storage_mb
  sku_name   = var.postgres_sku

  high_availability {
    mode                      = var.environment == "production" ? "ZoneRedundant" : "Disabled"
    standby_availability_zone = var.environment == "production" ? "2" : null
  }

  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres]

  tags = {
    Environment = var.environment
  }
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "travel_agent_db"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# -----------------------------------------------------------------------------
# Azure Cache for Redis
# -----------------------------------------------------------------------------
resource "azurerm_redis_cache" "main" {
  name                = "${var.project_name}-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = var.redis_capacity
  family              = var.redis_family
  sku_name            = var.redis_sku
  non_ssl_port_enabled = false
  minimum_tls_version = "1.2"

  subnet_id = azurerm_subnet.redis.id

  redis_configuration {
    maxmemory_policy = "allkeys-lru"
  }

  tags = {
    Environment = var.environment
  }
}

# -----------------------------------------------------------------------------
# Azure Container Registry
# -----------------------------------------------------------------------------
resource "azurerm_container_registry" "main" {
  name                = replace("${var.project_name}acr", "-", "")
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Standard"
  admin_enabled       = false

  tags = {
    Environment = var.environment
  }
}

# Grant AKS pull access to ACR
resource "azurerm_role_assignment" "aks_acr" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}

# -----------------------------------------------------------------------------
# Kubernetes & Helm Providers
# -----------------------------------------------------------------------------
provider "kubernetes" {
  host                   = azurerm_kubernetes_cluster.main.kube_config[0].host
  client_certificate     = base64decode(azurerm_kubernetes_cluster.main.kube_config[0].client_certificate)
  client_key             = base64decode(azurerm_kubernetes_cluster.main.kube_config[0].client_key)
  cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.main.kube_config[0].cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = azurerm_kubernetes_cluster.main.kube_config[0].host
    client_certificate     = base64decode(azurerm_kubernetes_cluster.main.kube_config[0].client_certificate)
    client_key             = base64decode(azurerm_kubernetes_cluster.main.kube_config[0].client_key)
    cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.main.kube_config[0].cluster_ca_certificate)
  }
}

# Deploy application via Helm
resource "helm_release" "trip_planner" {
  name             = "trip-planner"
  chart            = "../../helm/ai-trip-planner"
  namespace        = "trip-planner"
  create_namespace = true

  values = [
    file("../../helm/ai-trip-planner/cloud-values/azure.yaml")
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
    name  = "secrets.postgresPassword"
    value = var.postgres_password
  }

  set_sensitive {
    name  = "secrets.redisPassword"
    value = azurerm_redis_cache.main.primary_access_key
  }

  set {
    name  = "postgresql.external.host"
    value = azurerm_postgresql_flexible_server.main.fqdn
  }

  set {
    name  = "redis.external.host"
    value = azurerm_redis_cache.main.hostname
  }

  set {
    name  = "redis.external.port"
    value = "6380"
  }

  set {
    name  = "backend.image.repository"
    value = "${azurerm_container_registry.main.login_server}/backend"
  }

  set {
    name  = "frontend.image.repository"
    value = "${azurerm_container_registry.main.login_server}/frontend"
  }

  set {
    name  = "mcpServer.image.repository"
    value = "${azurerm_container_registry.main.login_server}/mcp-server"
  }

  depends_on = [
    azurerm_kubernetes_cluster.main,
    azurerm_postgresql_flexible_server_database.main,
    azurerm_redis_cache.main,
  ]
}
