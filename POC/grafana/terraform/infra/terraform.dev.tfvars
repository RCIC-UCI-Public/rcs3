# Environment and Project details
environment  = "dev"
project_name = "backup-metrics"

# S3 Configuration
s3_bucket_name = "backup-metrics-tfstate-dev"

# Allowed IP addresses in CIDR notation
allowed_cidr_blocks = ["68.5.95.209/32"] # Scott's IP

# ALB Configuration
use_alb = true  # Dev: Use simple EC2 direct access (saves ~$16/month)
