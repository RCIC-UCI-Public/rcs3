# Instance Outputs
output "grafana_instance_id" {
  value       = aws_instance.grafana.id
  description = "ID of the Grafana EC2 instance"
}

output "grafana_az" {
  value       = aws_instance.grafana.availability_zone
  description = "Availability Zone of the Grafana EC2 instance"
}

# Primary Grafana URL (conditional based on ALB)
output "grafana_url" {
  value       = var.use_alb ? "https://${aws_lb.grafana[0].dns_name}" : "http://${aws_instance.grafana.public_ip}:3000"
  description = "Primary Grafana URL - ALB HTTPS if enabled, otherwise direct EC2 HTTP"
}

# Usage Information
output "alb_enabled" {
  value       = var.use_alb
  description = "Whether ALB is enabled for this deployment"
}
