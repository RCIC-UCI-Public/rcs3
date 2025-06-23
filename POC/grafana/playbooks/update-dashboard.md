# Grafana Dashboard Update Playbook

## Overview
This playbook provides steps to update or add Grafana dashboards so that they can be deployed to all team folders.

## Background
- This repo contains a folder of dashboards in JSON format.
- Besides the "overview" dashboards, they are all S3 bucket based.
- We don't have the ability to dynamically set permissions on the S3 bucket list
- To work around that limitation we make a copy of each dashboard and put it into the team folder associated with that bucket

## Prerequisites
- Access to Grafana UI
- Access to the local repository containing dashboard JSON files
- Terraform installed and configured

## Update Steps

### 1. Modify Dashboard via Grafana UI
1. Log in to Grafana.
2. Navigate to the dashboard you want to modify or create a new dashboard.
3. Make changes to panels, queries, or settings as needed.

### 2. Save Dashboard in Grafana
1. Click **Save Dashboard** in the top-right corner.
2. Provide a name for the dashboard if it's new.
3. Ensure the dashboard is saved successfully.

### 3. Export Dashboard JSON
1. Click **Settings** for the dashboard.
2. Navigate to the **JSON Model** tab.
3. Copy the full JSON content displayed.

### 4. Update Local Repository
1. Navigate to the `POC/grafana/dashboards` directory in your local repository.
2. Either overwrite an existing dashboard JSON file or create a new file:
   - Use the dashboard name from Grafana as the filename (e.g., `bucket-overview.json`).
   - Save the copied JSON content into the file.

### 5. Determine Dashboard Placement
1. By default, dashboards are assumed to be bucket-based/team dashboards.
   - These will be deployed to the  **Admin** folder and each team folder.
2. If the dashboard should be a single instance available to all users:
   - Add the dashboard filename to the `common_dashboards` key in the Terraform configuration file:
     - Path: `POC/grafana/terraform/config/terraform.[env].tfvars`
     - Example:
       ```hcl
       common_dashboards = ["cost-estimates.json", "bucket-overview.json"]
       ```

### 6. Deploy Changes
1. Run the Terraform configuration deployment script to apply changes:
2. **Don't forget to run the team updates python script any time you run the Terraform config deployment**

**For Dev:**
```bash
cd POC/grafana/terraform/config
./deploy-dev.sh
```

**For Prod:**
```bash
cd POC/grafana/terraform/config
./deploy-prod.sh
```

### 7. Verify Dashboard Deployment
1. Log in to Grafana.
2. Navigate to the dashboard location (team folder or common folder).
3. Verify the dashboard appears with the correct panels and data.

## Troubleshooting

### Dashboard Not Appearing
- Ensure the JSON file was saved correctly in the repository.
- Verify the Terraform deployment completed successfully.
- Check the Grafana logs for errors.

### Incorrect Data or Panels
- Verify the JSON content matches the intended configuration.
- Check data source connections and queries in Grafana.

## Notes
- Dashboard names in Grafana are derived from the `title` field in the JSON.
- Always test changes in the Dev environment before deploying to Prod.
