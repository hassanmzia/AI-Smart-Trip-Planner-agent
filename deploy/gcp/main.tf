# =============================================================================
# GCP GKE Infrastructure for AI Smart Trip Planner
# =============================================================================
# Usage:
#   cd deploy/gcp
#   terraform init
#   terraform plan -var-file="terraform.tfvars"
#   terraform apply -var-file="terraform.tfvars"
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.10"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.10"
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
  # backend "gcs" {
  #   bucket = "trip-planner-terraform-state"
  #   prefix = "gke/terraform.tfstate"
  # }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

provider "google-beta" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# -----------------------------------------------------------------------------
# Enable Required APIs
# -----------------------------------------------------------------------------
resource "google_project_service" "apis" {
  for_each = toset([
    "container.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "artifactregistry.googleapis.com",
    "compute.googleapis.com",
    "servicenetworking.googleapis.com",
  ])

  service            = each.key
  disable_on_destroy = false
}

# -----------------------------------------------------------------------------
# VPC Network
# -----------------------------------------------------------------------------
resource "google_compute_network" "main" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false

  depends_on = [google_project_service.apis]
}

resource "google_compute_subnetwork" "gke" {
  name          = "${var.project_name}-gke-subnet"
  ip_cidr_range = var.gke_subnet_cidr
  region        = var.gcp_region
  network       = google_compute_network.main.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr
  }
}

# Private services access for Cloud SQL
resource "google_compute_global_address" "private_ip" {
  name          = "${var.project_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 20
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip.name]

  depends_on = [google_project_service.apis]
}

# Cloud Router for NAT
resource "google_compute_router" "main" {
  name    = "${var.project_name}-router"
  region  = var.gcp_region
  network = google_compute_network.main.id
}

resource "google_compute_router_nat" "main" {
  name                               = "${var.project_name}-nat"
  router                             = google_compute_router.main.name
  region                             = var.gcp_region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# -----------------------------------------------------------------------------
# GKE Cluster
# -----------------------------------------------------------------------------
resource "google_container_cluster" "main" {
  provider = google-beta

  name     = "${var.project_name}-gke"
  location = var.gcp_region

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.gke.name

  # Use Autopilot or Standard mode
  initial_node_count       = 1
  remove_default_node_pool = true

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.master_cidr
  }

  workload_identity_config {
    workload_pool = "${var.gcp_project_id}.svc.id.goog"
  }

  release_channel {
    channel = "REGULAR"
  }

  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }
  }

  depends_on = [google_project_service.apis]
}

# General node pool
resource "google_container_node_pool" "general" {
  name     = "general"
  cluster  = google_container_cluster.main.name
  location = var.gcp_region

  autoscaling {
    min_node_count = var.general_node_min_count
    max_node_count = var.general_node_max_count
  }

  node_config {
    machine_type = var.general_node_machine_type
    disk_size_gb = 50
    disk_type    = "pd-standard"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    labels = {
      workload = "general"
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}

# Worker node pool for Celery
resource "google_container_node_pool" "workers" {
  name     = "workers"
  cluster  = google_container_cluster.main.name
  location = var.gcp_region

  autoscaling {
    min_node_count = var.worker_node_min_count
    max_node_count = var.worker_node_max_count
  }

  node_config {
    machine_type = var.worker_node_machine_type
    disk_size_gb = 50
    disk_type    = "pd-standard"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    labels = {
      workload = "worker"
    }

    taint {
      key    = "workload"
      value  = "worker"
      effect = "PREFER_NO_SCHEDULE"
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}

# -----------------------------------------------------------------------------
# Cloud SQL for PostgreSQL
# -----------------------------------------------------------------------------
resource "google_sql_database_instance" "main" {
  name             = "${var.project_name}-postgres"
  database_version = "POSTGRES_15"
  region           = var.gcp_region

  settings {
    tier              = var.cloudsql_tier
    disk_size         = var.cloudsql_disk_size
    disk_autoresize   = true
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.id
    }

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"
    }

    insights_config {
      query_insights_enabled = true
    }
  }

  deletion_protection = var.environment == "production"

  depends_on = [google_service_networking_connection.private]
}

resource "google_sql_database" "main" {
  name     = "travel_agent_db"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "main" {
  name     = "travel_admin"
  instance = google_sql_database_instance.main.name
  password = var.postgres_password
}

# -----------------------------------------------------------------------------
# Memorystore for Redis
# -----------------------------------------------------------------------------
resource "google_redis_instance" "main" {
  name           = "${var.project_name}-redis"
  tier           = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  memory_size_gb = var.redis_memory_size_gb
  region         = var.gcp_region

  authorized_network = google_compute_network.main.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  redis_version = "REDIS_7_0"
  auth_enabled  = true

  depends_on = [google_service_networking_connection.private]
}

# -----------------------------------------------------------------------------
# Artifact Registry
# -----------------------------------------------------------------------------
resource "google_artifact_registry_repository" "main" {
  location      = var.gcp_region
  repository_id = var.project_name
  format        = "DOCKER"

  depends_on = [google_project_service.apis]
}

# -----------------------------------------------------------------------------
# Static IP for Ingress
# -----------------------------------------------------------------------------
resource "google_compute_global_address" "ingress" {
  name = "${var.project_name}-ingress-ip"
}

# GKE Managed Certificate
resource "google_compute_managed_ssl_certificate" "main" {
  provider = google-beta
  name     = "${var.project_name}-cert"

  managed {
    domains = [var.domain_name]
  }
}

# -----------------------------------------------------------------------------
# Kubernetes & Helm Providers
# -----------------------------------------------------------------------------
data "google_client_config" "default" {}

provider "kubernetes" {
  host                   = "https://${google_container_cluster.main.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.main.master_auth[0].cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = "https://${google_container_cluster.main.endpoint}"
    token                  = data.google_client_config.default.access_token
    cluster_ca_certificate = base64decode(google_container_cluster.main.master_auth[0].cluster_ca_certificate)
  }
}

# Deploy application via Helm
resource "helm_release" "trip_planner" {
  name             = "trip-planner"
  chart            = "../../helm/ai-trip-planner"
  namespace        = "trip-planner"
  create_namespace = true

  values = [
    file("../../helm/ai-trip-planner/cloud-values/gcp.yaml")
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
    value = google_redis_instance.main.auth_string
  }

  set {
    name  = "postgresql.external.host"
    value = google_sql_database_instance.main.private_ip_address
  }

  set {
    name  = "redis.external.host"
    value = google_redis_instance.main.host
  }

  set {
    name  = "ingress.annotations.kubernetes\\.io/ingress\\.global-static-ip-name"
    value = google_compute_global_address.ingress.name
  }

  set {
    name  = "backend.image.repository"
    value = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.main.repository_id}/backend"
  }

  set {
    name  = "frontend.image.repository"
    value = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.main.repository_id}/frontend"
  }

  set {
    name  = "mcpServer.image.repository"
    value = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.main.repository_id}/mcp-server"
  }

  depends_on = [
    google_container_cluster.main,
    google_container_node_pool.general,
    google_sql_database.main,
    google_redis_instance.main,
  ]
}
