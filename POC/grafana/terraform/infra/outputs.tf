# Instance Outputs
output "grafana_instance_id" {
  value       = aws_instance.grafana.id
  description = "ID of the Grafana EC2 instance"
}

# Primary Grafana URL (conditional based on ALB and domain)
output "grafana_url" {
  value = "https://${var.grafana_subdomain}.${var.domain_name}"
}

# ALB DNS name (for reference)
output "alb_dns_name" {
  value       = var.use_alb ? "https://${aws_lb.grafana[0].dns_name}" : null
}

# Usage Information
output "alb_enabled" {
  value       = var.use_alb
  description = "Whether ALB is enabled for this deployment"
}

output "custom_domain_enabled" {
  value       = var.domain_name != ""
  description = "Whether custom domain is configured"
}