# Environment-Specific Deployment Notes

This guide outlines the key differences, considerations, and best practices for deploying and managing dev vs prod environments.

## Environment Overview

The system supports multiple deployment strategies with distinct characteristics:

| Aspect | Dev Environment | Prod Environment |
|--------|----------------|------------------|
| **Domain** | Optional/Subdomain | Required/Primary |
| **SSL** | Optional | Required |
| **Cost** | ~$15-36/month | ~$36-71/month |
| **Stability** | Can be destroyed | Always-on |
| **Users** | Limited testing | Full team access |

## Development Environment

### Purpose and Usage

**Primary Use Cases**:
- Feature testing and validation
- Dashboard development
- Configuration testing
- Training and demos
- Cost-effective experimentation

**Not Suitable For**:
- Production monitoring
- Business-critical dashboards
- Long-term data retention
- External user access

### Dev Environment Configuration

**Terraform Configuration** (`terraform.dev.tfvars`):
```hcl
# Basic dev setup (no ALB/SSL)
use_alb = false
domain_name = ""
instance_type = "t3.small"

# Or with custom domain
use_alb = true
domain_name = "uci-dev.yourdomain.com"
grafana_subdomain = "dashboard"
delegation_set_id = "N1PA6795SAMPLE"
```

**Team Configuration**:
```hcl
# Smaller team lists for testing
bucket_teams = {
  "Team test-project" = {
    members = ["developer1", "tester1"]
    buckets = ["test-bucket-uci-d-bkup-bucket"]
  }
}

# Test credentials
default_user_password = "DevPassword123!"
admin_users = ["admin", "developer1"]
```

### Dev Environment Lifecycle

**Creation**:
```bash
cd POC/grafana/terraform/infra
./deploy-dev.sh
cd ../config
./deploy-dev.sh
```

**Regular Destruction** (cost saving):
```bash
cd POC/grafana/terraform/infra
terraform destroy -var-file=terraform.dev.tfvars
cd ../config
terraform destroy -var-file=terraform.dev.tfvars
```

**Recreation**:
```bash
# Infrastructure and configuration are preserved in:
# - Git repository (code)
# - S3 bucket (Terraform state)
# Simply redeploy when needed
./deploy-dev.sh
```

### Dev-Specific Considerations

1. **Data Persistence**:
   - Grafana data is lost when instance is destroyed
   - Dashboard JSON preserved in Git
   - Terraform state preserved in S3

2. **Network Access**:
   - May use direct IP access (cheaper)
   - Security groups can be more permissive
   - SSL not required for internal testing

3. **Resource Sizing**:
   - Smaller instance types acceptable
   - Single AZ deployment sufficient
   - Basic monitoring adequate

4. **Update Strategy**:
   - Test all changes in dev first
   - Rapid iteration acceptable
   - Breaking changes allowed

## Production Environment

### Purpose and Usage

**Primary Use Cases**:
- Business-critical monitoring
- Team dashboard access
- Long-term metric storage
- External stakeholder access
- Operational decision making

**Critical Requirements**:
- High availability
- Data persistence
- Security compliance
- Performance optimization
- Backup and recovery

### Prod Environment Configuration

**Terraform Configuration** (`terraform.prod.tfvars`):
```hcl
# Production setup with ALB/SSL
use_alb = true
domain_name = "uci.yourdomain.com"
grafana_subdomain = "dashboard"
root_domain_name = "yourdomain.com"
instance_type = "t3.medium"  # Or larger

# Production security
enable_detailed_monitoring = true
backup_retention_days = 30
```

**Team Configuration**:
```hcl
# Full production teams
bucket_teams = {
  "Team lopez-fedaykin" = {
    members = ["user1", "user2", "user3"]
    buckets = ["lopez-fedaykin-uci-s-bkup-bucket"]
  },
  "Team ppapadop-mass" = {
    members = ["user4", "user5"]
    buckets = ["ppapadop-mass-uci-s-bkup-bucket"]
  }
}

# Strong production passwords
default_user_password = "ComplexProductionPassword123!"
admin_users = ["admin"]  # Minimal admin access
```

### Production Lifecycle

**Initial Deployment**:
```bash
cd POC/grafana/terraform/infra
./deploy-prod.sh
cd ../config
./deploy-prod.sh
cd ../scripts
python update_team_memberships.py
```

**Updates** (careful process):
```bash
# Always test in dev first
cd POC/grafana/terraform/config
./deploy-dev.sh  # Test changes
# If successful:
./deploy-prod.sh
```

**Never Destroy Production**:
```bash
# Production should never be destroyed except for complete migration
# Use terraform plan carefully
# Always have backups before major changes
```

### Prod-Specific Considerations

1. **High Availability**:
   - Multi-AZ ALB deployment
   - Auto-recovery capabilities
   - Health monitoring and alerting

2. **Security**:
   - SSL/TLS required
   - Restricted admin access
   - Strong password policies
   - Security group restrictions

3. **Performance**:
   - Appropriately sized instances
   - Monitoring and alerting
   - Resource utilization tracking

4. **Change Management**:
   - All changes tested in dev
   - Scheduled maintenance windows
   - Rollback procedures
   - Change documentation

## Cross-Environment Considerations

### Data Synchronization

**Dashboard Sync**:
```bash
# Dashboards stay in sync via Git
cd POC/grafana/dashboards
# Make changes
git add . && git commit -m "Dashboard updates"
# Deploy to both environments
```

**Configuration Sync**:
```bash
# Keep configurations similar but environment-specific
# Use same team structure but different URLs/passwords
# Maintain configuration parity where possible
```

### Testing Strategy

**Development Testing**:
1. Test new dashboards in dev
2. Validate team permissions
3. Test bucket filtering
4. Verify S3 browser integration
5. Performance testing with real data

**Production Validation**:
1. Deploy proven changes from dev
2. Smoke test critical functionality
3. Monitor system health
4. Validate user access
5. Confirm data accuracy

### Migration Between Environments

**Dev to Prod Migration**:
```bash
# 1. Export dashboard from dev Grafana
# 2. Update dashboard JSON in repository
# 3. Deploy to production
cd POC/grafana/terraform/config
./deploy-prod.sh
```

**Configuration Migration**:
```bash
# Copy configuration patterns but update for prod values
cp terraform.dev.tfvars terraform.prod.tfvars
# Edit for production URLs, passwords, team members
```

## Environment-Specific Troubleshooting

### Dev Environment Issues

**Common Problems**:
- Instance destroyed accidentally
- Test data conflicts
- Development credentials expired

**Quick Fixes**:
```bash
# Redeploy everything
cd POC/grafana/terraform/infra
./deploy-dev.sh
cd ../config
./deploy-dev.sh
```

### Production Environment Issues

**Common Problems**:
- SSL certificate issues
- Performance degradation
- User access problems

**Careful Resolution**:
```bash
# Always diagnose before acting
aws ssm start-session --target i-prod-instance
sudo systemctl status grafana-server
sudo journalctl -u grafana-server -n 100

# Make minimal, targeted fixes
# Document all changes
# Monitor impact
```

## Cost Management by Environment

### Dev Environment Cost Optimization

**Strategies**:
1. **Destroy When Not Needed**:
   ```bash
   # Friday evening
   terraform destroy -var-file=terraform.dev.tfvars
   # Monday morning
   ./deploy-dev.sh
   ```

2. **Use Smaller Instances**:
   ```hcl
   instance_type = "t3.small"  # vs t3.medium for prod
   ```

3. **Skip ALB for Internal Testing**:
   ```hcl
   use_alb = false  # Direct IP access
   ```

**Cost Savings**: ~50-70% vs production

### Production Environment Cost Management

**Strategies**:
1. **Reserved Instances**: For predictable long-term usage
2. **Right-Sizing**: Monitor and adjust instance types
3. **Efficient Monitoring**: Optimize CloudWatch usage

**Important**: Never compromise production reliability for cost

## Security Considerations by Environment

### Dev Environment Security

**Relaxed Security** (for development efficiency):
- Simpler passwords acceptable
- More permissive network access
- Broader admin access for testing

**Still Required**:
- No hardcoded credentials in code
- Proper AWS IAM roles
- VPC network isolation

### Production Environment Security

**Strict Security** (business requirement):
- Complex passwords required
- Minimal admin access
- Restricted network access
- SSL/TLS required
- Regular security audits
- Compliance with organizational policies

## Backup and Recovery Strategies

### Dev Environment

**Backup Strategy**:
- Dashboard JSON in Git (automatic)
- Terraform state in S3 (automatic)
- Configuration files in Git
- No instance-level backups needed

**Recovery Strategy**:
- Redeploy from scratch
- Restore from Git and Terraform state
- Acceptable data loss

### Production Environment

**Backup Strategy**:
- Dashboard JSON in Git
- Terraform state in S3
- Configuration files in Git
- EBS snapshots (optional)
- Grafana database backups (optional)

**Recovery Strategy**:
- Infrastructure recovery via Terraform
- Configuration recovery via Git
- Minimal data loss tolerance
- Documented recovery procedures

## Deployment Checklist

### Dev Deployment Checklist

- [ ] Update dashboard JSON in Git
- [ ] Test Terraform plan
- [ ] Deploy infrastructure changes
- [ ] Deploy configuration changes
- [ ] Smoke test functionality
- [ ] Document any issues for prod deployment

### Production Deployment Checklist

- [ ] Changes tested and validated in dev
- [ ] Terraform plan reviewed
- [ ] Backup current state documented
- [ ] Deploy during maintenance window
- [ ] Monitor system health post-deployment
- [ ] Validate user access
- [ ] Update change documentation
- [ ] Notify stakeholders of completion

This environment-specific guide ensures proper separation of concerns and appropriate management strategies for each environment type.
