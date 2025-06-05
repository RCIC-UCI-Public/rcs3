# Configure Terraform backend and required providers
terraform {
  backend "s3" {
    bucket  = "backup-metrics-tfstate-dev"
    key     = "terraform_grafana_config.tfstate"
    region  = "us-west-2"
    encrypt = true
  }

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
}
