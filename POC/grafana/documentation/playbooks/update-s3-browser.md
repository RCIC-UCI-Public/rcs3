# S3 Browser Update Playbook

Simple steps to update the S3 Browser application when source code changes are made.

## Dev Environment

1. **Deploy to S3**
   ```bash
   cd POC/grafana/terraform/infra
   ./deploy-dev.sh
   ```

2. **Find EC2 Instance**
   ```bash
   aws ec2 describe-instances --filters "Name=tag:Name,Values=*grafana*" --query "Reservations[].Instances[].InstanceId" --output text
   ```

3. **Connect to Instance**
   ```bash
   aws ssm start-session --target INSTANCE_ID
   ```

4. **Download Updated Files**
   ```bash
   cd /opt/s3-browser
   sudo aws s3 cp s3://backup-metrics-tfstate-dev/s3-browser/server.js server.js
   sudo aws s3 cp s3://backup-metrics-tfstate-dev/s3-browser/package.json package.json
   sudo aws s3 cp s3://backup-metrics-tfstate-dev/s3-browser/public/index.html public/index.html
   sudo chown -R ubuntu:ubuntu /opt/s3-browser
   ```

5. **Install Dependencies (if needed)**
   ```bash
   npm install
   ```

6. **Restart Service**
   ```bash
   sudo systemctl stop s3-browser
   sudo systemctl start s3-browser
   sudo systemctl status s3-browser
   ```

## Prod Environment

1. **Deploy to S3**
   ```bash
   cd POC/grafana/terraform/infra
   ./deploy-prod.sh
   ```

2. **Find EC2 Instance**
   ```bash
   aws ec2 describe-instances --filters "Name=tag:Name,Values=*grafana*" --query "Reservations[].Instances[].InstanceId" --output text
   ```

3. **Connect to Instance**
   ```bash
   aws ssm start-session --target INSTANCE_ID
   ```

4. **Download Updated Files**
   ```bash
   cd /opt/s3-browser
   sudo aws s3 cp s3://rcs3-godfather-uci-p-bucket/s3-browser/server.js server.js
   sudo aws s3 cp s3://rcs3-godfather-uci-p-bucket/s3-browser/package.json package.json
   sudo aws s3 cp s3://rcs3-godfather-uci-p-bucket/s3-browser/public/index.html public/index.html
   sudo chown -R ubuntu:ubuntu /opt/s3-browser
   ```

5. **Install Dependencies (if needed)**
   ```bash
   npm install
   ```

6. **Restart Service**
   ```bash
   sudo systemctl stop s3-browser
   sudo systemctl start s3-browser
   sudo systemctl status s3-browser
   ```
