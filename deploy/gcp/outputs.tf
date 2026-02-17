# =============================================================================
# GCP GKE Outputs
# =============================================================================

output "cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.main.name
}

output "cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.main.endpoint
}

output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.main.name} --region ${var.gcp_region} --project ${var.gcp_project_id}"
}

output "cloudsql_instance" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "cloudsql_private_ip" {
  description = "Cloud SQL private IP"
  value       = google_sql_database_instance.main.private_ip_address
}

output "redis_host" {
  description = "Memorystore Redis host"
  value       = google_redis_instance.main.host
}

output "ingress_ip" {
  description = "Static IP for ingress"
  value       = google_compute_global_address.ingress.address
}

output "artifact_registry" {
  description = "Artifact Registry URL"
  value       = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.main.repository_id}"
}

output "docker_push_commands" {
  description = "Commands to tag and push images"
  value       = <<-EOT
    # Configure Docker for Artifact Registry
    gcloud auth configure-docker ${var.gcp_region}-docker.pkg.dev

    # Build and push images
    docker build -t ${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.main.repository_id}/backend:latest ./backend
    docker push ${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.main.repository_id}/backend:latest
  EOT
}
