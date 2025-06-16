# Main Terraform configuration

provider "aws" {
  region = "us-west-2" # Default region, can be overridden via variables
}

# Remote state configuration
terraform {
  backend "s3" {
    bucket  = "rcs3-godfather-uci-p-bucket"
    key     = "tfstate/terraform_infra.tfstate"
    region  = "us-west-2"
    encrypt = true
  }

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
