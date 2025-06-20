# Main Terraform configuration

provider "aws" {
  region = "us-west-2" # Default region, can be overridden via variables
}

# Remote state configuration - backend configured via backend config files
terraform {
  backend "s3" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Data sources
data "aws_region" "current" {}


# Tags that will be applied to all resources
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
    owner       = "UCI"
    CreatorName = "UCI"
    Name        = "${var.project_name}-${var.environment}"
    nukeoptout  = "true"
    CostCenter  = "grafana-monitoring"
  }
}
