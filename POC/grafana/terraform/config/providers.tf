# Configure Terraform backend and required providers - backend configured via backend config files
terraform {
  backend "s3" {}

  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "~> 2.1.0"
    }
  }
}

# Configure Grafana Provider
provider "grafana" {
  url = var.grafana_url

  # Use API key if provided, otherwise use username/password
  auth = var.grafana_api_key != null ? var.grafana_api_key : "${var.grafana_username}:${var.grafana_password}"

  # Skip SSL verification for self-signed certs
  insecure_skip_verify = true
}
