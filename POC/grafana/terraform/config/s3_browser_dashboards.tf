# S3 Browser dashboard generation and management

# Generate S3 browser dashboards for each team (will be placed in team folders by team_dashboards.tf)
locals {
  # S3 browser dashboard template
  s3_browser_template = jsondecode(file("${local.dashboard_path_absolute}/s3-browser-template.json"))

  # Extract hostname from Grafana URL for iframe source (remove protocol and port)
  grafana_host = replace(
    replace(
      replace(var.grafana_url, "http://", ""),
      "https://", ""
    ),
    ":3000", ""
  )

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
        "{{GRAFANA_HOST}}", local.grafana_host
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
        "{{GRAFANA_HOST}}", local.grafana_host
      )
    )
  )
  folder    = grafana_folder.admin_folder.id
  overwrite = true

  # Ignore changes to fields that Grafana manages
  lifecycle {
    ignore_changes = [
      config_json,  # Ignore JSON formatting differences
    ]
  }
}
