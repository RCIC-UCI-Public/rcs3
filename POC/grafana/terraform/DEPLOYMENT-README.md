# Terraform Deployment Guide

This document explains how to deploy the Grafana infrastructure and configuration to different environments using the new backend configuration system.

## Overview

The Terraform configuration has been updated to support multiple environments (dev and prod) without requiring manual edits to the main configuration files. Each environment uses its own S3 bucket for state storage.

## Environment Configuration

### Dev Environment
- **State Bucket**: `backup-metrics-tfstate-dev`
- **S3 Bucket for Resources**: `backup-metrics-tfstate-dev` (configurable via `s3_bucket_name` variable)
- **Infrastructure State Key**: `tfstate/terraform_infra.tfstate`
- **Config State Key**: `tfstate/terraform_grafana_config.tfstate`

### Prod Environment
- **State Bucket**: `rcs3-godfather-uci-p-bucket`
- **S3 Bucket for Resources**: `rcs3-godfather-uci-p-bucket` (configurable via `s3_bucket_name` variable)
- **Infrastructure State Key**: `tfstate/terraform_infra.tfstate`
- **Config State Key**: `tfstate/terraform_grafana_config.tfstate`

## Deployment Instructions

### Quick Deployment (Recommended)

Use the provided deployment scripts for easy deployment:

#### Deploy to Dev Environment
```bash
# Deploy infrastructure
cd POC/grafana/terraform/infra
./deploy-dev.sh

# Deploy Grafana configuration
cd ../config
./deploy-dev.sh
```

#### Deploy to Prod Environment
```bash
# Deploy infrastructure
cd POC/grafana/terraform/infra
./deploy-prod.sh

# Deploy Grafana configuration
cd ../config
./deploy-prod.sh
```

### Manual Deployment

If you prefer to run commands manually:

#### Dev Environment
```bash
# Infrastructure
cd POC/grafana/terraform/infra
terraform init -backend-config=backend-dev.hcl
terraform plan -var-file=terraform.dev.tfvars
terraform apply -var-file=terraform.dev.tfvars

# Configuration
cd ../config
terraform init -backend-config=backend-dev.hcl
terraform plan -var-file=terraform.dev.tfvars
terraform apply -var-file=terraform.dev.tfvars
```

#### Prod Environment
```bash
# Infrastructure
cd POC/grafana/terraform/infra
terraform init -backend-config=backend-prod.hcl
terraform plan -var-file=terraform.prod.tfvars
terraform apply -var-file=terraform.prod.tfvars

# Configuration
cd ../config
terraform init -backend-config=backend-prod.hcl
terraform plan -var-file=terraform.prod.tfvars
terraform apply -var-file=terraform.prod.tfvars
```

## File Structure

```
POC/grafana/terraform/
├── infra/
│   ├── backend-dev.hcl          # Dev backend configuration
│   ├── backend-prod.hcl         # Prod backend configuration
│   ├── deploy-dev.sh            # Dev deployment script
│   ├── deploy-prod.sh           # Prod deployment script
│   ├── main.tf                  # Main infrastructure config
│   ├── terraform.dev.tfvars     # Dev variables
│   └── terraform.prod.tfvars    # Prod variables
├── config/
│   ├── backend-dev.hcl          # Dev backend configuration
│   ├── backend-prod.hcl         # Prod backend configuration
│   ├── deploy-dev.sh            # Dev deployment script
│   ├── deploy-prod.sh           # Prod deployment script
│   ├── providers.tf             # Provider configuration
│   ├── terraform.dev.tfvars     # Dev variables
│   └── terraform.prod.tfvars    # Prod variables
└── DEPLOYMENT-README.md         # This file
```

## Backend Configuration Files

The backend configuration files (`.hcl`) contain the S3 bucket settings for each environment:

**backend-dev.hcl**:
```hcl
bucket  = "backup-metrics-tfstate-dev"
key     = "tfstate/terraform_[module].tfstate"
region  = "us-west-2"
encrypt = true
```

**backend-prod.hcl**:
```hcl
bucket  = "rcs3-godfather-uci-p-bucket"
key     = "tfstate/terraform_[module].tfstate"
region  = "us-west-2"
encrypt = true
```

## Important Notes

1. **First-time Setup**: When switching to this new system, you may need to migrate existing state. Run `terraform init -migrate-state` if prompted.

2. **State Isolation**: Each environment maintains completely separate state files, ensuring no cross-environment interference.

3. **Deployment Order**: Always deploy infrastructure (`infra`) before configuration (`config`) since the config module depends on outputs from the infrastructure module.

4. **Confirmation**: The deployment scripts include confirmation prompts before applying changes to prevent accidental deployments.

## Troubleshooting

### State Migration
If you encounter state migration issues:
```bash
terraform init -migrate-state -backend-config=backend-[env].hcl
```

### Backend Reconfiguration
If you need to reconfigure the backend:
```bash
terraform init -reconfigure -backend-config=backend-[env].hcl
```

### Viewing Current State
To see what's in your current state:
```bash
terraform show
terraform state list
