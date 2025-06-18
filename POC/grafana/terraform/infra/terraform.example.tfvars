# Environment and Project details
environment  = "dev"
project_name = "backup-metrics"

# S3 Configuration
s3_bucket_name = "your-s3-bucket-name-here"

# Allowed IP addresses in CIDR notation
allowed_cidr_blocks = ["68.5.95.209/32"] # Replace with your IP

# Elastic IP Configuration
use_elastic_ip = false  # Set to true for production, false for dev (saves $3.65/month)
