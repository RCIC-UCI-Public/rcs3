#!/bin/bash

# Deploy infrastructure to prod environment
echo "Deploying infrastructure to prod environment..."

# Initialize Terraform with prod backend configuration
echo "Initializing Terraform with prod backend configuration..."
terraform init -backend-config=backend-prod.hcl

# Validate configuration
echo "Validating Terraform configuration..."
terraform validate

#  Apply
echo "Applying changes to prod environment..."
terraform apply -var-file=terraform.prod.tfvars