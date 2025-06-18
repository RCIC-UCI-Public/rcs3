# Instance Outputs
output "grafana_instance_id" {
  value       = aws_instance.grafana.id
  description = "ID of the Grafana EC2 instance"
}

output "grafana_az" {
  value       = aws_instance.grafana.availability_zone
  description = "Availability Zone of the Grafana EC2 instance"
}

output "grafana_public_ip" {
  value       = aws_instance.grafana.public_ip
  description = "Public IP of Grafana instance (dynamic, changes on restart)"
}

output "grafana_public_dns" {
  value       = aws_instance.grafana.public_dns
  description = "Public DNS of Grafana instance"
}

# Flexible IP Outputs (works with both elastic and dynamic IPs)
output "grafana_ip" {
  value       = var.use_elastic_ip ? aws_eip.grafana[0].public_ip : aws_instance.grafana.public_ip
  description = "Current public IP of Grafana instance (elastic if enabled, otherwise dynamic)"
}

output "grafana_ip_type" {
  value       = var.use_elastic_ip ? "elastic" : "dynamic"
  description = "Type of IP assignment (elastic or dynamic)"
}

output "grafana_url" {
  value       = "https://${var.use_elastic_ip ? aws_eip.grafana[0].public_ip : aws_instance.grafana.public_ip}"
  description = "HTTPS URL for Grafana access (with self-signed certificate) - ONLY public access method"
}

output "grafana_url_https" {
  value       = "https://${var.use_elastic_ip ? aws_eip.grafana[0].public_ip : aws_instance.grafana.public_ip}"
  description = "HTTPS URL for Grafana access (with self-signed certificate)"
}

output "grafana_internal_urls" {
  value = {
    http_internal = "http://localhost:3000"
    s3_browser_internal = "http://localhost:3001"
  }
  description = "Internal URLs accessible only via SSH to the instance (for troubleshooting)"
}

# Elastic IP specific outputs (only populated if using elastic IP)
output "grafana_elastic_ip" {
  value       = var.use_elastic_ip ? aws_eip.grafana[0].public_ip : null
  description = "Elastic IP address (null if not using elastic IP)"
}

output "grafana_elastic_ip_allocation_id" {
  value       = var.use_elastic_ip ? aws_eip.grafana[0].id : null
  description = "Elastic IP allocation ID (null if not using elastic IP)"
}
