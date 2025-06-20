# S3 Browser Update Playbook

This playbook provides steps to update the S3 Browser application when changes are made to the source code.

## Prerequisites
- AWS CLI access configured
- Terraform installed
- Access to AWS Systems Manager Session Manager
- S3 Browser source files updated in the local repository

## Update Steps

### 1. Deploy Infrastructure Changes
Run the infrastructure Terraform to copy updated files to S3:

**For Dev:**
```bash
cd POC/grafana/terraform/infra
./deploy-dev.sh
```

**For Prod:**
```bash
cd POC/grafana/terraform/infra
./deploy-prod.sh
```

This will upload the updated S3 browser files to S3:
- `s3-browser/server.js`
- `s3-browser/package.json`
- `s3-browser/public/index.html`

### 2. Connect to EC2 Instance
Log into the Grafana EC2 instance using AWS Systems Manager Session Manager:

```bash
# Find the instance ID first
aws ec2 describe-instances --filters "Name=tag:Name,Values=*grafana*" --query "Reservations[].Instances[].InstanceId" --output text

# Connect via Session Manager (replace INSTANCE_ID with actual ID)
aws ssm start-session --target INSTANCE_ID
```

### 3. Copy Files from S3 to Local Directory
Once connected to the EC2 instance, copy the updated files from S3:

```bash
# Navigate to the S3 browser application directory
cd /opt/s3-browser

# Download updated server.js
sudo aws s3 cp s3://[BUCKET_NAME]/s3-browser/server.js server.js
sudo aws s3 cp s3://backup-metrics-tfstate-dev/s3-browser/server.js server.js

# Download updated package.json
sudo aws s3 cp s3://[BUCKET_NAME]/s3-browser/package.json package.json

# Download updated HTML interface
sudo aws s3 cp s3://[BUCKET_NAME]/s3-browser/public/index.html public/index.html
sudo aws s3 cp s3://backup-metrics-tfstate-dev/s3-browser/public/index.html public/index.html

# Set correct ownership
sudo chown -R ubuntu:ubuntu /opt/s3-browser
```

**Note:** Replace `[BUCKET_NAME]` with:
- Dev: `backup-metrics-tfstate-dev`
- Prod: `rcs3-godfather-uci-p-bucket`

### 4. Install Updated Dependencies (if package.json changed)
If package.json was updated, install new dependencies:

```bash
cd /opt/s3-browser
npm install
```

### 5. Restart S3 Browser Service
Restart the S3 browser service to apply changes:

```bash
# Stop the service
sudo systemctl stop s3-browser

# Start the service
sudo systemctl start s3-browser

# Verify the service is running
sudo systemctl status s3-browser
```

## Verification
After the update:
1. Check that the S3 browser service is running:
   ```bash
   sudo systemctl status s3-browser
   ```

2. Test the S3 browser interface through the ALB endpoint

3. Check service logs if issues occur:
   ```bash
   sudo journalctl -u s3-browser -f
   ```

## Troubleshooting

### Service Won't Start
- Check service logs: `sudo journalctl -u s3-browser -n 50`
- Verify file permissions: `ls -la /opt/s3-browser/`
- Check Node.js dependencies: `cd /opt/s3-browser && npm list`

### Files Not Updated
- Verify Terraform applied successfully
- Check S3 bucket for updated files with timestamps
- Confirm correct bucket name and paths

### Permission Issues
- Ensure files are owned by ubuntu user: `sudo chown -R ubuntu:ubuntu /opt/s3-browser`
- Verify EC2 instance has S3 read permissions

## File Locations Reference
- **Application Directory**: `/opt/s3-browser/`
- **Service Name**: `s3-browser`
- **Service Configuration**: `/etc/systemd/system/s3-browser.service`
- **Application Port**: `3001` (internal)
- **S3 Bucket Paths**:
  - `s3-browser/server.js`
  - `s3-browser/package.json`
  - `s3-browser/public/index.html`
