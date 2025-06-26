# S3 Browser dashboard generation and management

# Generate S3 browser dashboards for each team (will be placed in team folders by team_dashboards.tf)
locals {
  # S3 browser dashboard template
  s3_browser_template = jsondecode(file("${local.dashboard_path_absolute}/s3-browser-template.json"))

  # Extract hostname from Grafana URL for iframe source (remove protocol, port, and trailing slash)
  grafana_host = trimsuffix(
    replace(
      replace(
        replace(
          replace(var.grafana_url, "http://", ""),
          "https://", ""
        ),
        ":3000", ""
      ),
      ":3001", ""
    ),
    "/"
  )

  # Extract protocol from Grafana URL
  grafana_protocol = split("://", var.grafana_url)[0]

  # Determine S3 browser URL based on whether ALB is used
  # Both ALB and non-ALB setups need /s3browser path
  # If no ALB: use host with port 3001 + /s3browser path
  # If ALB: use same host with /s3browser path
  s3_browser_url = strcontains(var.grafana_url, ":3000") ? "${local.grafana_protocol}://${local.grafana_host}:3001/s3browser" : "${local.grafana_protocol}://${local.grafana_host}/s3browser"

  # Generate S3 browser dashboards for each team
  team_s3_dashboards = { for team_name, team_config in var.bucket_teams : team_name =>
    # Convert dashboard to JSON string for global replacements, then parse back
    jsondecode(
      replace(
        replace(
          replace(
            replace(
              jsonencode(local.s3_browser_template),
              "{{TEAM_NAME}}", team_name
            ),
            "{{TEAM_UID}}", replace(lower(team_name), " ", "-")
          ),
          "{{TEAM_BUCKETS}}", join(",", team_config.buckets)
        ),
        "{{S3_BROWSER_URL}}", local.s3_browser_url
      )
    )
  }
}

# Create an admin S3 browser dashboard (shows all buckets)
resource "grafana_dashboard" "admin_s3_browser" {
  config_json = jsonencode(
    jsondecode(
      replace(
        replace(
          replace(
            replace(
              jsonencode(local.s3_browser_template),
              "{{TEAM_NAME}}", "Admin"
            ),
            "{{TEAM_UID}}", "admin"
          ),
          "{{TEAM_BUCKETS}}", "" # No filter - show all buckets
        ),
        "{{S3_BROWSER_URL}}", local.s3_browser_url
      )
    )
  )
  folder    = grafana_folder.admin_folder.id
  overwrite = true

  # Allow updates to config_json for iframe URL changes
  lifecycle {
    # Note: Removed ignore_changes for config_json to allow iframe URL updates
  }
}
