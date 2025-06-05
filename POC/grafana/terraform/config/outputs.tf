# Output values for the Grafana configuration module

# Dashboard URLs for easy access
output "dashboard_urls" {
  description = "URLs for all created dashboards"
  value = merge(
    {
      for name, dashboard in grafana_dashboard.common_dashboards : "common-${name}" => "${var.grafana_url}/d/${dashboard.dashboard_id}"
    },
    {
      for name, dashboard in grafana_dashboard.admin_dashboards : "admin-${name}" => "${var.grafana_url}/d/${dashboard.dashboard_id}"
    }
  )
}

# S3 Browser information and URLs
output "s3_browser_info" {
  description = "S3 browser dashboard information and URLs"
  value = {
    s3_browser_url = "http://${local.grafana_host}:3001"
    team_dashboards = {
      for team_name, team_config in var.bucket_teams : team_name => {
        dashboard_url   = "${var.grafana_url}/d/s3-browser-${replace(lower(team_name), " ", "-")}"
        buckets         = team_config.buckets
        filtered_s3_url = "http://${local.grafana_host}:3001?filter=${join(",", team_config.buckets)}"
      }
    }
  }
}

# Debug outputs for troubleshooting
output "debug_file_discovery" {
  description = "Debug information about dashboard file discovery"
  value = {
    path_used   = local.dashboard_path_absolute
    files_found = local.dashboard_files
  }
}

output "debug_file_info" {
  description = "Debug information about individual dashboard files"
  value       = local.file_info
}

output "debug_dashboard_count" {
  description = "Debug information about dashboard processing counts"
  value = {
    files_found     = length(local.dashboard_files)
    files_processed = length(local.processed_dashboards)
  }
}
