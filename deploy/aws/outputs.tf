# =============================================================================
# AWS EKS Outputs
# =============================================================================

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_certificate_authority" {
  description = "EKS cluster CA certificate"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.aws_region}"
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.rds.db_instance_address
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "rabbitmq_endpoint" {
  description = "Amazon MQ RabbitMQ endpoint"
  value       = aws_mq_broker.rabbitmq.instances[0].endpoints[0]
}

output "ecr_repositories" {
  description = "ECR repository URLs"
  value = {
    for name, repo in aws_ecr_repository.repos : name => repo.repository_url
  }
}

output "certificate_arn" {
  description = "ACM certificate ARN"
  value       = aws_acm_certificate.main.arn
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}
