# Environment and Project details
environment  = "prod"
project_name = "backup-metrics"

# S3 Configuration
s3_bucket_name = "rcs3-godfather-uci-p-bucket"

# Allowed IP addresses in CIDR notation
allowed_cidr_blocks = ["68.5.95.209/32","128.200.0.0/16","128.195.0.0/16","192.5.19.0/24","68.96.70.0/24"] # Replace with your IP blocks

# Elastic IP Configuration
use_elastic_ip = true  # Enable stable IP for production (costs $3.65/month)
