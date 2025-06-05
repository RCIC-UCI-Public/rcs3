# Create customized dashboards per team with bucket filtering (only for team-restricted dashboards)
resource "grafana_dashboard" "team_dashboards" {
  for_each = {
    for td in flatten([
      for team_name, team in var.bucket_teams : [
        for file_name in local.team_restricted_dashboard_files : {
          team_name   = team_name
          file_name   = file_name
          bucket_list = team.buckets
        }
      ]
    ]) : "${td.team_name}-${td.file_name}" => td
  }

  # Get the base dashboard JSON
  config_json = jsonencode(merge(
    local.processed_dashboards[each.value.file_name],
    {
      # Modify the templating section to restrict bucket options
      templating = merge(
        lookup(local.processed_dashboards[each.value.file_name], "templating", {}),
        {
          list = [
            for item in lookup(lookup(local.processed_dashboards[each.value.file_name], "templating", {}), "list", []) :
            # If this is the bucket variable, add regex filter for team buckets
            merge(item, item.name == "bucket" ? {
              # Apply regex to limit buckets shown in dropdown
              regex = join("|", [for bucket in each.value.bucket_list : "^${bucket}$"])
            } : {})
          ]
        }
      ),

      # Add team name to title
      title = "${lookup(local.processed_dashboards[each.value.file_name], "title", each.value.file_name)} - ${each.value.team_name}"
    }
  ))

  folder    = grafana_folder.team_folders[each.value.team_name].id
  overwrite = true

  # Ignore changes to fields that Grafana manages
  lifecycle {
    ignore_changes = [
      config_json,  # Ignore JSON formatting differences
    ]
  }
}

# Create team-specific S3 browser dashboards in team folders
resource "grafana_dashboard" "team_s3_browser_dashboards" {
  for_each = local.team_s3_dashboards

  config_json = jsonencode(each.value)
  folder      = grafana_folder.team_folders[each.key].id
  overwrite   = true

  # Ignore changes to fields that Grafana manages
  lifecycle {
    ignore_changes = [
      config_json,  # Ignore JSON formatting differences
    ]
  }
}

# Create folders for each team
resource "grafana_folder" "team_folders" {
  for_each = var.bucket_teams

  title = "${each.key} Dashboards"
}

# Set folder permissions for teams
resource "grafana_folder_permission" "team_folder_permissions" {
  for_each = var.bucket_teams

  folder_uid = grafana_folder.team_folders[each.key].uid

  permissions {
    team_id    = grafana_team.bucket_teams[each.key].id
    permission = "View"
  }
}

# Output team dashboard URLs for reference
output "team_dashboard_urls" {
  value = merge(
    {
      for key, dashboard in grafana_dashboard.team_dashboards : key => "${var.grafana_url}/d/${dashboard.dashboard_id}"
    },
    {
      for key, dashboard in grafana_dashboard.team_s3_browser_dashboards : "s3-browser-${key}" => "${var.grafana_url}/d/${dashboard.dashboard_id}"
    }
  )
}
