# Import common dashboards (available to all users)
resource "grafana_dashboard" "common_dashboards" {
  for_each = { for file in local.common_dashboard_files : file => local.processed_dashboards[file] }

  # Convert processed dashboard back to JSON
  config_json = jsonencode(each.value)
  folder      = grafana_folder.common_folder.id
  overwrite   = true

  # Ignore changes to fields that Grafana manages
  lifecycle {
    ignore_changes = [
      config_json,  # Ignore JSON formatting differences
    ]
  }
}

# Import team-restricted dashboards (only available to admins and teams)
resource "grafana_dashboard" "admin_dashboards" {
  for_each = { for file in local.team_restricted_dashboard_files : file => local.processed_dashboards[file] }

  # Convert processed dashboard back to JSON
  config_json = jsonencode(each.value)
  folder      = grafana_folder.admin_folder.id
  overwrite   = true

  # Ignore changes to fields that Grafana manages
  lifecycle {
    ignore_changes = [
      config_json,  # Ignore JSON formatting differences
    ]
  }
}
