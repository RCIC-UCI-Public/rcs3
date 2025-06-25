# Grafana Configuration
# These values should come from the infra module's outputs:
grafana_username = "admin"
grafana_url      = "https://backup-metrics-dev-grafana-alb-1770820205.us-west-2.elb.amazonaws.com"

# Path to dashboard JSON files
dashboards_path = "../../dashboards"

# Admin users (will be created with admin privileges)
admin_users = ["admin2"]

# Common dashboards available to all users
common_dashboards = ["cost-estimates.json", "cost-estimates-improved.json"]

# Define teams and their bucket access permissions
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

# Default password for all users (can be overridden)
default_user_password = "ChangeMe123!"