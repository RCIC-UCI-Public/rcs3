# Operational Procedures Guide

This guide provides step-by-step procedures for common operational tasks in the Grafana monitoring solution.

## Adding New Teams and Users

### Procedure: Add New Team

**When to use**: When a new team or project needs access to S3 monitoring.

**Prerequisites**:
- S3 bucket(s) following naming convention: `{name}-uci-{letter}-bkup-bucket`
- CloudWatch metrics configured for the bucket(s)

**Steps**:

1. **Update Configuration**:
   ```bash
   cd POC/grafana/terraform/config
   vim terraform.dev.tfvars  # or terraform.prod.tfvars
   ```

2. **Add Team Entry**:
   ```hcl
   bucket_teams = {
     # Existing teams...
     "Team new-project" = {
       members = ["user1@example.com", "user2@example.com"]
       buckets = ["new-project-uci-s-bkup-bucket"]
     }
   }
   ```

3. **Deploy Configuration**:
   ```bash
   ./deploy-dev.sh  # or ./deploy-prod.sh
   ```

4. **Update Team Memberships**:
   ```bash
   cd POC/grafana/scripts
   python update_team_memberships.py
   ```

5. **Verify Team Creation**:
   - Log into Grafana as admin
   - Check new team folder exists
   - Verify team members can access folder
   - Test bucket dropdown shows only team buckets

### Procedure: Add User to Existing Team

**Steps**:

1. **Update Team Configuration**:
   ```hcl
   "Team existing-team" = {
     members = ["existing-user", "new-user@example.com"]  # Add new user
     buckets = ["existing-bucket"]
   }
   ```

2. **Deploy and Update**:
   ```bash
   cd POC/grafana/terraform/config
   ./deploy-dev.sh
   cd ../scripts
   python update_team_memberships.py
   ```

3. **Notify User**:
   - Provide Grafana URL
   - Share default password (to be changed on first login)
   - Explain team folder access

### Procedure: Remove User from Team

**Steps**:

1. **Update Configuration**:
   ```hcl
   "Team existing-team" = {
     members = ["user1"]  # Remove user2
     buckets = ["existing-bucket"]
   }
   ```

2. **Deploy Changes**:
   ```bash
   ./deploy-dev.sh
   cd ../scripts
   python update_team_memberships.py
   ```

3. **Optional - Disable User**:
   - Log into Grafana as admin
   - Go to Server Admin → Users
   - Disable user account if no longer needed

## Dashboard Management

### Procedure: Add New Dashboard

**Steps**:

1. **Create Dashboard in Grafana**:
   - Log in as admin
   - Create and configure new dashboard
   - Test with different buckets

2. **Export Dashboard JSON**:
   - Dashboard Settings → JSON Model
   - Copy full JSON content

3. **Save to Repository**:
   ```bash
   cd POC/grafana/dashboards
   vim new-dashboard.json  # Paste JSON content
   ```

4. **Configure Dashboard Type**:
   
   For **team dashboards** (bucket-specific):
   ```bash
   # No additional configuration needed
   # Will be deployed to all team folders with bucket filtering
   ```
   
   For **common dashboards** (shared):
   ```hcl
   # In terraform.tfvars
   common_dashboards = ["cost-estimates.json", "new-dashboard.json"]
   ```

5. **Deploy Dashboard**:
   ```bash
   cd POC/grafana/terraform/config
   ./deploy-dev.sh
   ```

### Procedure: Update Existing Dashboard

**Steps**:

1. **Modify in Grafana**:
   - Edit dashboard panels/queries
   - Test changes thoroughly

2. **Export and Update**:
   ```bash
   # Export JSON from Grafana
   cd POC/grafana/dashboards
   vim existing-dashboard.json  # Update with new JSON
   ```

3. **Deploy Changes**:
   ```bash
   cd POC/grafana/terraform/config
   ./deploy-dev.sh
   ```

4. **Verify Deployment**:
   - Check admin folder for unrestricted version
   - Check team folders for filtered versions
   - Verify bucket filtering still works

### Procedure: Remove Dashboard

**Steps**:

1. **Remove from Repository**:
   ```bash
   cd POC/grafana/dashboards
   rm old-dashboard.json
   ```

2. **Update Common Dashboards (if applicable)**:
   ```hcl
   # Remove from common_dashboards list in terraform.tfvars
   common_dashboards = ["remaining-dashboard.json"]
   ```

3. **Deploy Changes**:
   ```bash
   cd POC/grafana/terraform/config
   ./deploy-dev.sh
   ```

## User Password Management

### Procedure: Reset User Password

**For Single User**:

1. **Reset in Grafana UI**:
   - Log in as admin
   - Server Admin → Users
   - Select user → Reset Password

**For All Users**:

1. **Update Default Password**:
   ```bash
   cd POC/grafana/terraform/config
   vim terraform.dev.tfvars
   ```

2. **Change Password**:
   ```hcl
   default_user_password = "NewSecurePassword123!"
   ```

3. **Deploy Changes**:
   ```bash
   ./deploy-dev.sh
   ```

### Procedure: Force Password Change

**Steps**:

1. **Reset All Passwords**:
   ```bash
   # Update default_user_password in terraform.tfvars
   ./deploy-dev.sh
   cd ../scripts
   python update_team_memberships.py
   ```

2. **Notify Users**:
   - Send email with new temporary password
   - Instruct to change on first login

## Bucket and Metric Management

### Procedure: Add Bucket to Existing Team

**Steps**:

1. **Update Team Configuration**:
   ```hcl
   "Team existing-team" = {
     members = ["user1", "user2"]
     buckets = [
       "existing-bucket-uci-s-bkup-bucket",
       "new-bucket-uci-p-bkup-bucket"  # Add new bucket
     ]
   }
   ```

2. **Deploy Configuration**:
   ```bash
   ./deploy-dev.sh
   ```

3. **Verify Bucket Access**:
   - Check team dashboards show new bucket in dropdown
   - Verify metrics are available for new bucket

### Procedure: Handle Missing Metrics

**Common Issue**: Bucket appears in dropdown but no data shows.

**Troubleshooting Steps**:

1. **Verify CloudWatch Metrics**:
   ```bash
   aws cloudwatch list-metrics --namespace "AWS/S3/Storage-Lens" \
     --dimensions Name=bucket_name,Value=bucket-name
   ```

2. **Check Custom Metrics** (for backup age):
   ```bash
   aws cloudwatch list-metrics --namespace "rcs3" \
     --metric-name "bucket-prefix_key_age"
   ```

3. **Verify Bucket Naming**:
   - Ensure bucket follows pattern: `{name}-uci-{letter}-bkup-bucket`
   - Check bucket exists and has proper permissions

4. **Check Time Range**:
   - Metrics may have delay
   - Try extending time range in dashboard

## System Maintenance

### Procedure: Update Grafana

**Steps**:

1. **Backup Current Configuration**:
   ```bash
   # Export current dashboards and settings
   # Document current Grafana version
   ```

2. **Update Infrastructure**:
   ```bash
   cd POC/grafana/terraform/infra
   # Update Grafana version in install script
   vim install-grafana-s3browser.sh
   ```

3. **Deploy Update**:
   ```bash
   ./deploy-dev.sh  # Test in dev first
   # If successful:
   ./deploy-prod.sh
   ```

4. **Verify Functionality**:
   - Test login functionality
   - Verify all dashboards load
   - Check team permissions
   - Test S3 browser integration

### Procedure: Scale EC2 Instance

**When**: Performance issues or increased usage.

**Steps**:

1. **Update Instance Type**:
   ```bash
   cd POC/grafana/terraform/infra
   vim terraform.dev.tfvars  # or prod
   ```

2. **Change Instance Type**:
   ```hcl
   instance_type = "t3.large"  # Or desired size
   ```

3. **Apply Changes**:
   ```bash
   ./deploy-dev.sh
   ```

4. **Monitor Performance**:
   - Check CPU and memory usage
   - Monitor response times
   - Verify all services restart properly

### Procedure: Backup and Recovery

**Regular Backup**:

1. **Export Dashboards**:
   ```bash
   # Already stored in Git repository
   cd POC/grafana/dashboards
   git add -A && git commit -m "Dashboard backup $(date)"
   ```

2. **Backup Configuration**:
   ```bash
   cd POC/grafana/terraform/config
   cp terraform.*.tfvars backup/
   ```

**Recovery Process**:

1. **Redeploy Infrastructure**:
   ```bash
   cd POC/grafana/terraform/infra
   ./deploy-dev.sh
   ```

2. **Restore Configuration**:
   ```bash
   cd POC/grafana/terraform/config
   ./deploy-dev.sh
   cd ../scripts
   python update_team_memberships.py
   ```

## Monitoring and Alerting

### Procedure: Set Up Health Monitoring

**CloudWatch Alarms**:

1. **EC2 Instance Health**:
   ```bash
   aws cloudwatch put-metric-alarm \
     --alarm-name "Grafana-Instance-CPU" \
     --alarm-description "High CPU on Grafana instance" \
     --metric-name CPUUtilization \
     --namespace AWS/EC2 \
     --statistic Average \
     --period 300 \
     --threshold 80 \
     --comparison-operator GreaterThanThreshold
   ```

2. **Application Health**:
   ```bash
   # Set up ALB target health monitoring
   aws cloudwatch put-metric-alarm \
     --alarm-name "Grafana-ALB-Unhealthy-Targets" \
     --metric-name UnHealthyHostCount \
     --namespace AWS/ApplicationELB \
     --statistic Average \
     --period 60 \
     --threshold 0 \
     --comparison-operator GreaterThanThreshold
   ```

### Procedure: Handle Service Outage

**Immediate Response**:

1. **Check Service Status**:
   ```bash
   # Connect to instance
   aws ssm start-session --target i-instanceid
   sudo systemctl status grafana-server
   sudo systemctl status s3-browser
   ```

2. **Check Logs**:
   ```bash
   sudo journalctl -u grafana-server -f
   sudo journalctl -u s3-browser -f
   ```

3. **Restart Services**:
   ```bash
   sudo systemctl restart grafana-server
   sudo systemctl restart s3-browser
   ```

4. **Check ALB Health**:
   - AWS Console → EC2 → Load Balancers
   - Check target group health

**Root Cause Analysis**:

1. **Review CloudTrail Logs**
2. **Check CloudWatch Metrics**
3. **Review Application Logs**
4. **Document Incident and Resolution**

## Cost Optimization

### Procedure: Review and Optimize Costs

**Monthly Review**:

1. **Check AWS Cost Explorer**:
   - Review EC2 costs
   - Check ALB costs
   - Monitor data transfer costs

2. **Optimize Infrastructure**:
   ```bash
   # Consider reserved instances for prod
   # Review instance sizing
   # Check for unused resources
   ```

3. **Update Cost Parameters**:
   ```hcl
   # Update pricing in terraform.tfvars if contracts change
   S3STD = 0.021      # Update with current pricing
   SDISCOUNT = 0.45   # Update with current discount
   ```

### Procedure: Environment Management

**Dev Environment Shutdown** (cost saving):

1. **Stop Infrastructure**:
   ```bash
   cd POC/grafana/terraform/infra
   terraform destroy -var-file=terraform.dev.tfvars
   ```

2. **Preserve State**:
   ```bash
   # Terraform state is preserved in S3
   # Configuration is preserved in Git
   ```

3. **Restart When Needed**:
   ```bash
   ./deploy-dev.sh
   cd ../config
   ./deploy-dev.sh
   ```

## Troubleshooting Common Issues

### Issue: Team Cannot See Their Buckets

**Resolution**:

1. **Check Configuration**:
   ```bash
   grep -A5 "Team name" terraform.dev.tfvars
   ```

2. **Verify Bucket Names**:
   ```bash
   aws s3 ls | grep "team-name"
   ```

3. **Redeploy Configuration**:
   ```bash
   ./deploy-dev.sh
   ```

### Issue: Dashboard Shows No Data

**Resolution**:

1. **Check Data Source**:
   - Grafana → Configuration → Data Sources
   - Test CloudWatch connection

2. **Verify Metrics**:
   ```bash
   aws cloudwatch list-metrics --namespace "AWS/S3/Storage-Lens"
   ```

3. **Check Time Range**:
   - Extend time range in dashboard
   - Check metric collection frequency

### Issue: S3 Browser Not Loading

**Resolution**:

1. **Check Service**:
   ```bash
   sudo systemctl status s3-browser
   sudo systemctl restart s3-browser
   ```

2. **Check Logs**:
   ```bash
   sudo journalctl -u s3-browser -n 50
   ```

3. **Verify Network**:
   ```bash
   curl http://localhost:3001/api/buckets
   ```

This operational procedures guide covers the most common tasks administrators will need to perform. Keep this guide updated as new procedures are developed or existing ones are refined.
