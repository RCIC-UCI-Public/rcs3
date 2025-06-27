# =============================================================================
# Grafana Configuration - Example Template
# =============================================================================
# Copy this file to terraform.dev.tfvars or terraform.prod.tfvars and customize
# See documentation/docs/configuration-guide.md for detailed explanations

# =============================================================================
# REQUIRED VARIABLES (All Environments)
# =============================================================================

# Grafana admin credentials - REQUIRED
# Default admin user for Grafana login
grafana_username = "admin"

# Grafana URL - REQUIRED
# This should match the output from your infrastructure deployment:
# For simple dev: "http://EC2-IP:3000"
# For ALB setup: "https://dashboard.your-domain.com"
grafana_url = "https://dashboard.your-domain.com"

# Dashboard file location - REQUIRED
# Relative path from terraform config directory to dashboard JSON files
dashboards_path = "../../dashboards"

# Team and bucket configuration - REQUIRED
# Define teams, their members, and which S3 buckets they can access
bucket_teams = {
  "Team Example-Project" = {
    members = ["user1", "user2", "user3"]
    buckets = ["example-project-uci-s-bkup-bucket"]
  },
  "Team Another-Lab" = {
    members = ["scientist1", "researcher1"]
    buckets = [
      "another-lab-data-uci-p-bkup-bucket",
      "another-lab-models-uci-s-bkup-bucket"
    ]
  }
}

# Default password for all created users - REQUIRED
# Users should change this on first login
default_user_password = "ChangeMe123!"

# =============================================================================
# ADMIN USERS CONFIGURATION
# =============================================================================

# Additional users with full system access
# These users can access all folders and modify all dashboards
admin_users = ["admin2"]  # Add additional admin usernames as needed

# =============================================================================
# DASHBOARD CONFIGURATION
# =============================================================================

# Common dashboards available to all teams - OPTIONAL
# Dashboards listed here will be deployed to a shared "Common Dashboards" folder
# All other dashboards will be deployed to individual team folders with bucket filtering
common_dashboards = [
  # "cost-estimates.json",              # Cost analysis across all buckets
  # "cost-estimates-improved.json"      # Enhanced cost dashboard
]

# =============================================================================
# ENVIRONMENT-SPECIFIC EXAMPLES
# =============================================================================

# -----------------------------------------------------------------------------
# DEV ENVIRONMENT EXAMPLE
# -----------------------------------------------------------------------------
# Development environment typically has:
# - Smaller team lists for testing
# - Test bucket names
# - Simple passwords
# - Limited admin users

# Example dev configuration:
# grafana_username = "admin"
# grafana_url = "https://dashboard.uci-dev.yourdomain.com"
# dashboards_path = "../../dashboards"
# admin_users = ["admin", "developer1"]
# common_dashboards = ["cost-estimates.json"]
# bucket_teams = {
#   "Team test-project" = {
#     members = ["testuser1", "testuser2"]
#     buckets = ["test-project-uci-d-bkup-bucket"]
#   }
# }
# default_user_password = "DevPassword123!"

# -----------------------------------------------------------------------------
# PROD ENVIRONMENT EXAMPLE
# -----------------------------------------------------------------------------
# Production environment typically has:
# - Full team lists with real users
# - Production bucket names
# - Strong passwords
# - Minimal admin users

# Example prod configuration:
# grafana_username = "admin"
# grafana_url = "https://dashboard.uci.yourdomain.com"
# dashboards_path = "../../dashboards"
# admin_users = ["admin", "sysadmin"]
# common_dashboards = ["cost-estimates.json", "cost-estimates-improved.json"]
# bucket_teams = {
#   "Team lopez-fedaykin" = {
#     members = ["user1", "user2"]
#     buckets = ["lopez-fedaykin-uci-s-bkup-bucket"]
#   },
#   "Team research-lab" = {
#     members = ["scientist1", "researcher1", "analyst1"]
#     buckets = [
#       "research-lab-data-uci-p-bkup-bucket",
#       "research-lab-models-uci-s-bkup-bucket"
#     ]
#   }
# }
# default_user_password = "ComplexProductionPassword123!"