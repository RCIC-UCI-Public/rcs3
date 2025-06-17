#!/bin/bash

# Deploy infrastructure to dev environment
echo "Deploying infrastructure to dev environment..."

# Initialize Terraform with dev backend configuration
echo "Initializing Terraform with dev backend configuration..."
terraform init -backend-config=backend-dev.hcl

# Validate configuration
echo "Validating Terraform configuration..."
terraform validate

#  Apply
echo "Applying changes to dev environment..."
terraform apply -var-file=terraform.dev.tfvars