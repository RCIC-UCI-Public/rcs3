#!/bin/bash
set -ex

# Log to both console and file
LOG_FILE="/var/log/user-data.log"
touch $LOG_FILE
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

echo "[INFO] Starting Grafana and S3 Browser installation..."

# Wait for apt to be available
sleep 10

# Install prerequisites
DEBIAN_FRONTEND=noninteractive apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y apt-transport-https software-properties-common wget curl

# Add Grafana repository
echo "[INFO] Adding Grafana repository key..."
curl https://packages.grafana.com/gpg.key | gpg --dearmor | sudo tee /usr/share/keyrings/grafana.gpg > /dev/null

echo "[INFO] Adding Grafana repository..."
echo "deb [signed-by=/usr/share/keyrings/grafana.gpg] https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

echo "[INFO] Updating package lists..."
apt-get update

echo "[INFO] Installing Grafana..."
apt-get install -y grafana

# Verify installation
echo "[INFO] Verifying Grafana package installation..."
dpkg -l | grep grafana

# Create directories
mkdir -p /etc/grafana/provisioning/datasources
mkdir -p /etc/grafana/provisioning/dashboards
mkdir -p /var/lib/grafana/dashboards

# Configure dashboard provider
cat > /etc/grafana/provisioning/dashboards/default.yaml << 'EODS'
apiVersion: 1
providers:
  - name: 'Default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: true
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
EODS

# Configure Grafana server
cat > /etc/grafana/grafana.ini << EODS
[paths]
provisioning = /etc/grafana/provisioning

[server]
protocol = http
http_port = 3000
domain = localhost

[security]
admin_password = ${GRAFANA_ADMIN_PASSWORD}

[auth.anonymous]
enabled = true
org_role = Viewer

[panels]
disable_sanitize_html = true

[log]
mode = console file
level = debug
EODS

# Set permissions
chown -R grafana:grafana /etc/grafana/provisioning
chown -R grafana:grafana /var/lib/grafana/dashboards

# Start Grafana
systemctl enable grafana-server
systemctl start grafana-server

# Install Node.js and npm for S3 browser
echo "[INFO] Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

# Verify Node.js installation
node --version
npm --version

# Create S3 browser application directory
mkdir -p /opt/s3-browser
cd /opt/s3-browser

# Download package.json from S3
echo "[INFO] Downloading package.json from S3..."
aws s3 cp s3://rcs3-godfather-uci-p-bucket/s3-browser/package.json package.json

# Install dependencies
npm install

# Download the S3 browser files from S3
echo "[INFO] Downloading S3 browser application files from S3..."

# Download server.js from S3
aws s3 cp s3://rcs3-godfather-uci-p-bucket/s3-browser/server.js server.js

# Create public directory and download HTML interface from S3
mkdir -p public
aws s3 cp s3://rcs3-godfather-uci-p-bucket/s3-browser/public/index.html public/index.html

# Create systemd service for S3 browser
cat > /etc/systemd/system/s3-browser.service << 'EOS3SERVICE'
[Unit]
Description=S3 Browser Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/s3-browser
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production
Environment=PORT=3001

[Install]
WantedBy=multi-user.target
EOS3SERVICE

# Set ownership and permissions
chown -R ubuntu:ubuntu /opt/s3-browser
chmod +x /opt/s3-browser/server.js

# Enable and start S3 browser service
systemctl daemon-reload
systemctl enable s3-browser
systemctl start s3-browser

# Verify services are running
systemctl status grafana-server
systemctl status s3-browser

echo "[INFO] Installation complete - Grafana on port 3000, S3 Browser on port 3001"
