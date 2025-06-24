# Grafana Deployment Playbook

This playbook provides high-level steps to deploy the Grafana monitoring solution for RCS3.

## Prerequisites
- AWS CLI access configured
- Terraform installed
- Python environment set up
- Required S3 buckets for Terraform state

## Deployment Steps

### 1. Domain Setup (High Level)
- Pre-purchase domain in Route 53 **OR**
- Let Terraform create the hosted zone, then purchase domain later
- If domain was pre-purchased, import the hosted zone before first apply
- [See Domain Setup Details below](#domain-setup-details)

### 2. Verify S3 Bucket Exists
Ensure the required S3 bucket for Terraform state storage exists:
- **Dev**: `backup-metrics-tfstate-dev`
- **Prod**: `rcs3-godfather-uci-p-bucket`

```bash
aws s3 ls s3://[bucket-name]
```

### 3. Update Infrastructure Variables
Update the appropriate Terraform variables file:
- **Dev**: `POC/grafana/terraform/infra/terraform.dev.tfvars`
- **Prod**: `POC/grafana/terraform/infra/terraform.prod.tfvars`

Review and modify variables as needed for your environment.

### 4. Authenticate to AWS CLI
Ensure your AWS CLI is authenticated and configured for the target environment:

```bash
aws sts get-caller-identity
```

### 5. Deploy Infrastructure
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

### 6. Capture Output DNS
After infrastructure deployment, capture the Grafana DNS endpoint from Terraform outputs:

```bash
terraform output grafana_url
```

Save this DNS value for the next step.

### 7. Update Configuration Variables
Update the configuration Terraform variables file with the DNS from step 6:
- **Dev**: `POC/grafana/terraform/config/terraform.dev.tfvars`
- **Prod**: `POC/grafana/terraform/config/terraform.prod.tfvars`

Add or update the Grafana URL/DNS configuration.

### 8. Deploy Configuration
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

### 9. Configure User/Team Memberships
Run the Python script to set up user and team memberships in Grafana:

```bash
cd POC/grafana/scripts
python update_team_memberships.py
```

## Domain Setup Details

- **Option A: Pre-purchase domain in Route 53**
  1. Buy domain in Route 53
  2. AWS creates hosted zone automatically
  3. Import hosted zone:  
     `terraform import aws_route53_zone.custom ZONE_ID`
  4. Run `terraform apply`

- **Option B: Let Terraform create hosted zone, purchase domain later**
  1. Run `terraform apply` (Terraform creates hosted zone, ACM cert, DNS records)
  2. Purchase domain in Route 53 (must match hosted zone name exactly)
  3. Re-run `terraform apply` to complete ACM validation

- **ACM Certificate**
  - ACM cert is free, auto-renews, and is validated via DNS records in the hosted zone.
  - ALB uses self-signed cert until ACM cert is validated.

- **Route 53 Hosted Zone**
  - $0.50/month per zone
  - Managed by Terraform (import if pre-existing)

- **Domain**
  - $12–$15/year (typical)

- **ALB**
  - $16–$25/month minimum

- **No ALB Option**
  - See playbook notes for direct EC2 + Let's Encrypt/NGINX if you want to avoid ALB cost.

## Verification
After deployment:
1. Access Grafana at the DNS endpoint from step 6
2. Verify dashboards are loaded
3. Test user access and permissions
4. Confirm data sources are connected
