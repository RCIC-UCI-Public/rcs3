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
  description = "Public IP of Grafana instance"
}

output "grafana_public_dns" {
  value       = aws_instance.grafana.public_dns
  description = "Public DNS of Grafana instance"
}
