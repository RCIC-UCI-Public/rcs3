#!/bin/bash

# Deploy Grafana configuration to prod environment
echo "Deploying Grafana configuration to prod environment..."

# Initialize Terraform with prod backend configuration
echo "Initializing Terraform with prod backend configuration..."
terraform init -backend-config=backend-prod.hcl

# Validate configuration
echo "Validating Terraform configuration..."
terraform validate

#  Apply
echo "Applying changes to dev environment..."
terraform apply -var-file=terraform.prod.tfvars