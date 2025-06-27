# Configuration Guide

This guide covers how to configure teams, users, buckets, and system parameters for the Grafana monitoring solution.

## Overview

The system uses Terraform to manage configurations, with separate variable files for dev and prod environments. All configuration is defined in `terraform.tfvars` files.

## Configuration Files

- **Dev**: `POC/grafana/terraform/config/terraform.dev.tfvars`
- **Prod**: `POC/grafana/terraform/config/terraform.prod.tfvars`
- **Example**: `POC/grafana/terraform/config/terraform.tfvars.example`

## Team and User Configuration

### Adding Teams and Users

Teams are defined in the `bucket_teams` variable. Each team has members and associated S3 buckets.

```hcl
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
```

### Team Configuration Rules

1. **Team Names**: Use descriptive names that identify the team or project
2. **Members**: List all users who should have access to the team's dashboards
3. **Buckets**: List S3 buckets that the team should have access to
4. **Bucket Naming**: Buckets should follow the pattern `{name}-uci-{letter}-bkup-bucket`

### User Management

Users are automatically created in Grafana when deployed. Default settings:

- **Default Password**: Set in `default_user_password` (change after first login)
- **Team Assignment**: Users are automatically added to their specified teams
- **Permissions**: Team members get view access to their team folder

```hcl
default_user_password = "ChangeMe123!"
```

## Admin User Configuration

Admin users get full access to all folders and dashboards:

```hcl
admin_users = ["admin", "admin2", "scott.lusk"]
```

Admins can:
- Access all team folders
- Modify all dashboards
- Access the Admin folder with unrestricted dashboards

## Dashboard Configuration

### Common vs Team Dashboards

Dashboards are categorized as either:
- **Common**: Available to all teams in shared folder
- **Team**: Copied to each team folder with bucket restrictions

```hcl
common_dashboards = ["cost-estimates.json", "cost-estimates-improved.json"]
```

### Dashboard Behavior

- **Team Dashboards**: Bucket dropdown filtered to team's buckets only
- **Common Dashboards**: Available to all teams without bucket restrictions
- **Admin Dashboards**: Available in Admin folder with all buckets visible

## System Parameters

### Grafana URL Configuration

Set the base URL for your Grafana instance:

```hcl
grafana_url = "https://dashboard.uci-dev.rcs3.org"  # Dev
grafana_url = "https://dashboard.uci.rcs3.org"     # Prod
```

### Dashboard Path

Specify the path to dashboard JSON files:

```hcl
dashboards_path = "../../dashboards"
```

## S3 Browser Configuration

The S3 browser is automatically configured to work with team bucket restrictions. No additional configuration is typically needed.

## Deployment After Configuration Changes

After making configuration changes:

1. **Validate Configuration**:
   ```bash
   cd POC/grafana/terraform/config
   terraform validate
   ```

2. **Deploy Changes**:
   ```bash
   ./deploy-dev.sh  # or ./deploy-prod.sh
   ```

3. **Update Team Memberships**:
   ```bash
   cd POC/grafana/scripts
   python update_team_memberships.py
   ```

## Configuration Examples

### Example 1: Adding a New Team

```hcl
bucket_teams = {
  # Existing teams...
  "Team new-project" = {
    members = ["newuser1", "newuser2"]
    buckets = ["new-project-uci-d-bkup-bucket"]
  }
}
```

### Example 2: Multi-Bucket Team

```hcl
bucket_teams = {
  "Team multi-bucket" = {
    members = ["user1", "user2"]
    buckets = [
      "project1-uci-s-bkup-bucket",
      "project2-uci-p-bkup-bucket"
    ]
  }
}
```

## Best Practices

1. **Team Names**: Use consistent naming conventions
2. **Passwords**: Change default password after deployment
3. **Testing**: Always test configuration changes in dev first
4. **Backup**: Keep copies of working configurations
5. **Documentation**: Document any custom pricing or configuration

## Troubleshooting Configuration

### Team Not Visible
- Check team name spelling in `bucket_teams`
- Verify user is listed in team members
- Run team membership update script

### Dashboard Missing
- Verify dashboard file exists in `dashboards/` folder
- Check if dashboard should be in `common_dashboards` list
- Redeploy configuration after changes

### Bucket Access Issues
- Verify bucket name matches exactly in configuration
- Check bucket naming follows expected pattern
- Ensure bucket exists and has proper permissions

### Cost Data Incorrect
- Verify pricing parameters match your AWS contract
- Check discount percentages are in decimal format (45% = 0.45)
- Ensure region-specific pricing is used
