# Dashboard file discovery and processing logic

# Process dashboard files
locals {
  # Get absolute path for dashboards
  dashboard_path_absolute = abspath(var.dashboards_path)

  # Find dashboard files (exclude S3 browser template)
  dashboard_files = setsubtract(
    fileset(local.dashboard_path_absolute, "*.json"),
    ["s3-browser-template.json"]
  )

  # Separate common dashboards from team-restricted dashboards
  common_dashboard_files = toset([
    for file in local.dashboard_files : file
    if contains(var.common_dashboards, file)
  ])

  team_restricted_dashboard_files = setsubtract(
    local.dashboard_files,
    local.common_dashboard_files
  )
}

# Process dashboards if files exist
locals {
  # Debug file info
  file_info = { for file in local.dashboard_files : file => {
    path   = "${local.dashboard_path_absolute}/${file}"
    exists = fileexists("${local.dashboard_path_absolute}/${file}")
  } }

  # Read and decode all dashboard JSON files
  raw_dashboards = { for file in local.dashboard_files : file =>
    jsondecode(file("${local.dashboard_path_absolute}/${file}"))
  }

  # Process each dashboard to remove instance-specific metadata and update datasource UIDs
  processed_dashboards = { for file, dashboard in local.raw_dashboards : file => merge(
    dashboard,
    {
      # Remove instance-specific fields
      uid       = null # Let Grafana generate a new UID
      version   = null # Reset version
      id        = null # Remove any existing ID
      iteration = null # Reset iteration

      # Update datasource UIDs
      templating = merge(dashboard.templating, {
        list = [for item in lookup(dashboard.templating, "list", []) : merge(item, {
          datasource = lookup(item, "datasource", null) == null ? null : merge(item.datasource, {
            uid = lookup(item.datasource, "type", "") == "cloudwatch" ? grafana_data_source.cloudwatch.uid : lookup(item.datasource, "uid", null)
          })
        })]
      })

      # Update panel datasources
      panels = [for panel in dashboard.panels : merge(panel, {
        datasource = lookup(panel, "datasource", null) == null ? null : merge(lookup(panel, "datasource", {}), {
          uid = lookup(lookup(panel, "datasource", {}), "type", "") == "cloudwatch" ? grafana_data_source.cloudwatch.uid : lookup(lookup(panel, "datasource", {}), "uid", null)
        })
        targets = [for target in lookup(panel, "targets", []) : merge(target, {
          datasource = lookup(target, "datasource", null) == null ? null : merge(lookup(target, "datasource", {}), {
            uid = lookup(lookup(target, "datasource", {}), "type", "") == "cloudwatch" ? grafana_data_source.cloudwatch.uid : lookup(lookup(target, "datasource", {}), "uid", null)
          })
        })]
      })]
    }
  ) }
}
