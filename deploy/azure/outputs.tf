# =============================================================================
# Azure AKS Outputs
# =============================================================================

output "resource_group_name" {
  description = "Azure resource group name"
  value       = azurerm_resource_group.main.name
}

output "cluster_name" {
  description = "AKS cluster name"
  value       = azurerm_kubernetes_cluster.main.name
}

output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.main.name} --name ${azurerm_kubernetes_cluster.main.name}"
}

output "postgres_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "redis_hostname" {
  description = "Redis cache hostname"
  value       = azurerm_redis_cache.main.hostname
}

output "acr_login_server" {
  description = "Azure Container Registry login server"
  value       = azurerm_container_registry.main.login_server
}

output "acr_push_command" {
  description = "Command to push images to ACR"
  value       = "az acr login --name ${azurerm_container_registry.main.name}"
}
