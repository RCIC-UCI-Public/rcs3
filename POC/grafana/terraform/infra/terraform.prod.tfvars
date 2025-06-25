# Environment and Project details
environment  = "prod"
project_name = "backup-metrics"

# S3 Configuration
s3_bucket_name = "rcs3-godfather-uci-p-bucket"

# Allowed IP addresses in CIDR notation
allowed_cidr_blocks = ["68.5.95.209/32","128.200.0.0/16","128.195.0.0/16","192.5.19.0/24","68.96.70.0/24"] # Replace with your IP blocks

# ALB Configuration
use_alb = true  # Prod: Use ALB for professional HTTPS setup (~$16/month)

# Domain Configuration
domain_name = "rcs3.uci.edu"
grafana_subdomain = "grafana"

root_domain_name = "rcs3.org"

dev_delegation = {
  subdomain = "uci-dev"
  name_servers = [
    "ns-1211.awsdns-23.org",
    "ns-1703.awsdns-20.co.uk",
    "ns-199.awsdns-24.com",
    "ns-848.awsdns-42.net"
  ]
}
