# Grafana Team Management and Admin Privileges Scripts

This directory contains scripts to automate Grafana user management, including team membership assignment and admin privilege granting.

## Overview

The scripts read configuration from Terraform tfvars files and use the Grafana API to:
1. Add users to teams based on the `bucket_teams` configuration
2. Grant admin privileges to users listed in the `admin_users` configuration

## Files

- `update_team_memberships.sh` - Main shell script wrapper
- `add_team_members.py` - Python script that handles the actual API calls

## Configuration

The scripts read from Terraform configuration files located at `../terraform/config/terraform.{environment}.tfvars`.

### Required Configuration Variables

```hcl
# Grafana connection settings
grafana_url = "http://your-grafana-instance:3000"
grafana_username = "admin"
grafana_password = "your-admin-password"  # Optional - can be prompted

# Admin users (will be granted Admin role)
admin_users = ["admin2", "admin3"]

# Team configurations
bucket_teams = {
  "Team lopez-fedaykin" = {
    members = ["user1", "user2"]
    buckets = ["lopez-fedaykin-uci-s-bkup-bucket"]
  },
  "Team ppapadop-mass" = {
    members = ["user3", "user2"] 
    buckets = ["ppapadop-mass-uci-s-bkup-bucket"]
  }
}
```

## Usage

### Basic Usage

```bash
# Run for development environment
./update_team_memberships.sh dev

# Run for production environment
./update_team_memberships.sh prod
```

### What the Script Does

1. **Validates Configuration**: Checks that the required tfvars file exists
2. **Installs Dependencies**: Ensures the `requests` Python package is installed
3. **Connects to Grafana**: Authenticates using the configured credentials
4. **Processes Team Memberships**: 
   - Reads the `bucket_teams` configuration
   - Adds users to their respective teams
   - Skips users already in teams
5. **Grants Admin Privileges**:
   - Reads the `admin_users` configuration
   - Grants Admin role to specified users
   - Skips users who already have Admin privileges

### Password Handling

The script supports two methods for password authentication:

1. **Config File**: Include `grafana_password = "your-password"` in the tfvars file
2. **Interactive Prompt**: If no password is in the config file, you'll be prompted to enter it

## Example Output

```
Using configuration file: ../terraform/config/terraform.dev.tfvars
Checking for required Python packages...
Processing team memberships and admin privileges...
Reading Grafana configuration from ../terraform/config/terraform.dev.tfvars...
Extracted Grafana config: {'url': 'http://18.236.165.247:3000', 'username': 'admin'}
Reading team configuration from ../terraform/config/terraform.dev.tfvars...
Found bucket_teams section
Found team: Team lopez-fedaykin
Team Team lopez-fedaykin members: ['user1', 'user2']
Found 2 teams in configuration.
Reading admin users configuration from ../terraform/config/terraform.dev.tfvars...
Extracted admin users: ['admin2']
Found 1 admin users in configuration.
Connecting to Grafana at http://18.236.165.247:3000...
Fetching existing teams and users...

Processing team 'Team lopez-fedaykin' (ID: 1):
  - Adding user 'user1' (ID: 2) to team...
  - Successfully added user 'user1' to team.

Team membership setup complete.

Processing 1 admin users...
  - Granting Admin privileges to user 'admin2' (ID: 3)...
  - Successfully granted Admin privileges to 'admin2'.

Admin privileges setup complete.
All operations completed.
Script execution complete.
```

## Requirements

- Python 3.x
- `requests` Python package (auto-installed if missing)
- Access to Grafana API
- Valid Grafana admin credentials

## Terraform Integration

This script is designed to work with the Grafana Terraform configuration. The typical workflow is:

1. Update `admin_users` and `bucket_teams` in your tfvars file
2. Run `terraform apply` to create users and teams
3. Run this script to assign team memberships and admin privileges

Note: Terraform can create users and teams but cannot grant admin privileges, which is why this script is necessary.

## Error Handling

The script includes error handling for common scenarios:
- Missing configuration files
- Network connectivity issues
- Authentication failures
- Missing users or teams in Grafana
- API request failures

If a user or team is not found in Grafana, the script will skip it and continue processing other items.

## Troubleshooting

### User Not Found
If a user is not found in Grafana, ensure:
1. The user was created by Terraform
2. The username in the config matches exactly (case-sensitive)
3. The user hasn't been deleted from Grafana

### Team Not Found
If a team is not found in Grafana, ensure:
1. The team was created by Terraform
2. The team name in the config matches exactly
3. The team hasn't been deleted from Grafana

### Authentication Errors
If authentication fails:
1. Verify the `grafana_url` is correct and accessible
2. Ensure the `grafana_username` exists and has admin privileges
3. Check that the password is correct
4. Verify Grafana is running and responding

### Permission Errors
If API calls fail with permission errors:
1. Ensure the authenticated user has admin privileges
2. Check that the organization ID is correct (defaults to 1)
3. Verify the Grafana version supports the API endpoints used
