# Grafana Deployment Playbook

This playbook provides high-level steps to deploy the Grafana monitoring solution for RCS3.

## Prerequisites
- AWS CLI access configured
- Terraform installed
- Python environment set up
- Required S3 buckets for Terraform state

## Deployment Steps

### 1. Verify S3 Bucket Exists
Ensure the required S3 bucket for Terraform state storage exists:
- **Dev**: `backup-metrics-tfstate-dev`
- **Prod**: `rcs3-godfather-uci-p-bucket`

```bash
aws s3 ls s3://[bucket-name]
```

### 2. Update Infrastructure Variables
Update the appropriate Terraform variables file:
- **Dev**: `POC/grafana/terraform/infra/terraform.dev.tfvars`
- **Prod**: `POC/grafana/terraform/infra/terraform.prod.tfvars`

Review and modify variables as needed for your environment.

### 3. Authenticate to AWS CLI
Ensure your AWS CLI is authenticated and configured for the target environment:

```bash
aws sts get-caller-identity
```

### 4. Deploy Infrastructure
Run the infrastructure deployment script:

**For Dev:**
```bash
cd POC/grafana/terraform/infra
./deploy-dev.sh
```

**For Prod:**
```bash
cd POC/grafana/terraform/infra
./deploy-prod.sh
```

### 5. Capture Output DNS
After infrastructure deployment, capture the Grafana DNS endpoint from Terraform outputs:

```bash
terraform output grafana_dns
```

Save this DNS value for the next step.

### 6. Update Configuration Variables
Update the configuration Terraform variables file with the DNS from step 5:
- **Dev**: `POC/grafana/terraform/config/terraform.dev.tfvars`
- **Prod**: `POC/grafana/terraform/config/terraform.prod.tfvars`

Add or update the Grafana URL/DNS configuration.

### 7. Deploy Configuration
Run the configuration deployment script:

**For Dev:**
```bash
cd POC/grafana/terraform/config
./deploy-dev.sh
```

**For Prod:**
```bash
cd POC/grafana/terraform/config
./deploy-prod.sh
```

### 8. Configure User/Team Memberships
Run the Python script to set up user and team memberships in Grafana:

```bash
cd POC/grafana/scripts
python update_team_memberships.py
```

## Verification
After deployment:
1. Access Grafana at the DNS endpoint from step 5
2. Verify dashboards are loaded
3. Test user access and permissions
4. Confirm data sources are connected