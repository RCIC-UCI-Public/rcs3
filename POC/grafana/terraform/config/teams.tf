resource "grafana_team" "bucket_teams" {
  for_each = var.bucket_teams

  name  = each.key
  email = lookup(each.value, "email", null)
}

# Create a flattened list of all unique users from all teams
locals {
  all_users = distinct(flatten([
    for team in var.bucket_teams : team.members
  ]))
}

# Create users automatically based on member names
resource "grafana_user" "bucket_users" {
  for_each = toset(local.all_users)

  email    = "${each.key}@example.com" # Default email pattern
  name     = each.key
  login    = each.key
  password = var.default_user_password
}

# Create admin users
resource "grafana_user" "admin_users" {
  for_each = toset(var.admin_users)

  email    = "${each.key}@example.com" # Default email pattern
  name     = each.key
  login    = each.key
  password = var.default_user_password
  is_admin = true
}