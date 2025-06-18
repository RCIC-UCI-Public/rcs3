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

# Get the current public IP address for SSL certificate
echo "[INFO] Getting current public IP address..."
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "[INFO] Public IP: $PUBLIC_IP"

# Create SSL certificate directory
mkdir -p /etc/grafana/ssl
cd /etc/grafana/ssl

# Generate self-signed SSL certificate
echo "[INFO] Generating self-signed SSL certificate..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout grafana.key \
    -out grafana.crt \
    -subj "/C=US/ST=CA/L=Irvine/O=UCI/OU=RCS3/CN=$PUBLIC_IP" \
    -addext "subjectAltName=IP:$PUBLIC_IP"

# Set proper permissions for SSL files
chown grafana:grafana /etc/grafana/ssl/grafana.key /etc/grafana/ssl/grafana.crt
chmod 400 /etc/grafana/ssl/grafana.key
chmod 444 /etc/grafana/ssl/grafana.crt

# Configure Grafana server with HTTPS on port 3000 (internal)
cat > /etc/grafana/grafana.ini << EODS
[paths]
provisioning = /etc/grafana/provisioning

[server]
protocol = https
http_port = 3000
domain = $PUBLIC_IP
cert_file = /etc/grafana/ssl/grafana.crt
cert_key = /etc/grafana/ssl/grafana.key

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

# Configure iptables to forward port 443 to 3000 for HTTPS access
echo "[INFO] Configuring port forwarding from 443 to 3000..."
iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 3000
iptables -t nat -A OUTPUT -p tcp -o lo --dport 443 -j REDIRECT --to-port 3000

# Save iptables rules to persist across reboots
apt-get install -y iptables-persistent
iptables-save > /etc/iptables/rules.v4

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
aws s3 cp s3://${S3_BUCKET_NAME}/s3-browser/package.json package.json

# Install dependencies
npm install

# Download the S3 browser files from S3
echo "[INFO] Downloading S3 browser application files from S3..."

# Download server.js from S3
aws s3 cp s3://${S3_BUCKET_NAME}/s3-browser/server.js server.js

# Create public directory and download HTML interface from S3
mkdir -p public
aws s3 cp s3://${S3_BUCKET_NAME}/s3-browser/public/index.html public/index.html

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

echo "[INFO] Installation complete!"
echo "[INFO] - Grafana HTTPS: https://$PUBLIC_IP (port 443) - Certificate warnings expected"
echo "[INFO] - Internal Grafana HTTP: http://localhost:3000 (SSH access only)"
echo "[INFO] - Internal S3 Browser: http://localhost:3001 (SSH access only)"
echo "[INFO] - SSL Certificate generated for IP: $PUBLIC_IP"
echo "[INFO] - PUBLIC ACCESS: Only HTTPS (port 443) is accessible from internet"
