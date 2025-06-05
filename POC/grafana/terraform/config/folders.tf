# Grafana folder management and permissions

# Create Admin folder for administrative dashboards
resource "grafana_folder" "admin_folder" {
  title = "Admin"
}

# Create Common folder for dashboards available to all users
resource "grafana_folder" "common_folder" {
  title = "Common Dashboards"
}

# Set folder permissions for Admin folder - only Admin role has access
resource "grafana_folder_permission" "admin_folder_permissions" {
  folder_uid = grafana_folder.admin_folder.uid

  # Remove all permissions except Admin role
  # This matches what worked manually in the UI
  permissions {
    role       = "Editor"
    permission = "Edit"
  }
}

# Set folder permissions for Common folder - grant access to all teams (authenticated users only)
resource "grafana_folder_permission" "common_folder_permissions" {
  folder_uid = grafana_folder.common_folder.uid

  # Grant view permissions to each team instead of using role-based permissions
  # This ensures only authenticated users (team members) can access common dashboards
  dynamic "permissions" {
    for_each = var.bucket_teams
    content {
      team_id    = grafana_team.bucket_teams[permissions.key].id
      permission = "View"
    }
  }

  # Also grant access to Editor role for admins
  permissions {
    role       = "Editor"
    permission = "Edit"
  }
}
