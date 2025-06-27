# Grafana Teardown Playbook

This playbook provides steps to completely remove the Grafana monitoring solution and all associated resources.

## Prerequisites
- AWS CLI access configured
- Terraform installed
- Access to the same environment used for deployment

## ⚠️ Warning
This process will permanently delete all Grafana resources, including:
- Grafana instance and data
- Associated AWS infrastructure
- Dashboards and configurations
- User settings and permissions

**Ensure you have backups of any important data before proceeding.**

## Teardown Steps

### 1. Authenticate to AWS CLI
Ensure your AWS CLI is authenticated and configured for the target environment:

```bash
aws sts get-caller-identity
```

### 2. Destroy Configuration Resources
First, destroy the Grafana configuration resources:

**For Dev:**
```bash
cd POC/grafana/terraform/config
terraform destroy -var-file=terraform.dev.tfvars
```

**For Prod:**
```bash
cd POC/grafana/terraform/config
terraform destroy -var-file=terraform.prod.tfvars
```

### 3. Destroy Infrastructure Resources
Next, destroy the underlying infrastructure:

**For Dev:**
```bash
cd POC/grafana/terraform/infra
terraform destroy -var-file=terraform.dev.tfvars
```

**For Prod:**
```bash
cd POC/grafana/terraform/infra
terraform destroy -var-file=terraform.prod.tfvars
```

## Verification
After teardown:
1. Verify resources are removed from AWS console
2. Check that Grafana endpoint is no longer accessible
3. Confirm S3 buckets are empty (if they were created for this deployment)

## Clean Up (Optional)
If desired, you can also remove the Terraform state files:
- The state files remain in the S3 buckets specified in the backend configuration
- Only delete these if you're certain you won't need to reference the previous state

## Troubleshooting
- If resources fail to destroy due to dependencies, check for any manually created resources that need to be removed first
- For persistent resources, use AWS console to manually remove them, then run terraform destroy again
- If state is corrupted, you may need to manually remove resources from AWS console
