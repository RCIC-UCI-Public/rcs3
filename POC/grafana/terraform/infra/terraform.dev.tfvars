# Environment and Project details
environment  = "dev"
project_name = "backup-metrics"

# S3 Configuration
s3_bucket_name = "backup-metrics-tfstate-dev"

# Allowed IP addresses in CIDR notation
allowed_cidr_blocks = ["68.5.95.209/32","128.200.0.0/16","128.195.0.0/16","192.5.19.0/24","68.96.70.0/24"] # Replace with your IP blocks

# ALB Configuration
use_alb = true  # Dev: Use simple EC2 direct access (saves ~$16/month)

# Domain Configuration
domain_name = "uci-dev.rcs3.org"
grafana_subdomain = "dashboard"