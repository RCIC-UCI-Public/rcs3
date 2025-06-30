# =============================================================================
# Grafana Infrastructure Configuration - Example Template
# =============================================================================
# Copy this file to terraform.dev.tfvars or terraform.prod.tfvars and customize
# See documentation/docs/configuration-guide.md for detailed explanations

# =============================================================================
# REQUIRED VARIABLES (All Environments)
# =============================================================================

# Environment identifier - REQUIRED
# Valid values: "dev", "prod", "staging", etc.
environment = "dev"  # Change to "prod" for production

# Project name - used in resource naming - REQUIRED
project_name = "backup-metrics"

# S3 bucket for Terraform state and file uploads - REQUIRED
# Dev example: "backup-metrics-tfstate-dev"
# Prod example: "your-prod-bucket-name"
s3_bucket_name = "your-s3-bucket-name-here"

# Network access control - REQUIRED
# IP addresses/CIDR blocks allowed to access Grafana
allowed_cidr_blocks = [
  "YOUR.IP.ADDRESS/32",     # Your specific IP
  # "10.0.0.0/8",           # Private networks
  # "172.16.0.0/12",        # Private networks
  # "192.168.0.0/16"        # Private networks
]

# =============================================================================
# DEPLOYMENT STRATEGY - Choose One (REQUIRED)
# =============================================================================

# ALB Configuration - determines deployment complexity and cost
use_alb = false  # Choose deployment strategy:
                 # false = Simple dev setup (direct EC2 access, ~$15/month)
                 # true  = Production setup (ALB + SSL, ~$36/month)

# =============================================================================
# OPTIONAL VARIABLES (SSL/Domain Configuration)
# =============================================================================
# Only needed if use_alb = true

# Domain name for Grafana access (only if use_alb = true)
# Dev example: "uci-dev.yourdomain.com"
# Prod example: "uci.yourdomain.com"
# domain_name = "your.domain.com"

# Subdomain for Grafana service (only if use_alb = true)
# grafana_subdomain = "dashboard"  # Creates dashboard.your.domain.com

# =============================================================================
# ENVIRONMENT-SPECIFIC VARIABLES
# =============================================================================

# -----------------------------------------------------------------------------
# DEV ENVIRONMENT ONLY
# -----------------------------------------------------------------------------
# Uncomment and configure for dev environment with custom domain:

# Delegation set ID for stable DNS (DEV ONLY)
# Create with: aws route53 create-reusable-delegation-set --caller-reference "dev-$(date +%s)"
# delegation_set_id = "N1234567890123456789"

# -----------------------------------------------------------------------------
# PROD ENVIRONMENT ONLY  
# -----------------------------------------------------------------------------
# Uncomment and configure for production environment:

# Root domain name (PROD ONLY - must own this domain in Route 53)
# root_domain_name = "yourdomain.com"

# Dev environment delegation (PROD ONLY - if you have both dev and prod)
# Configure this in PROD to delegate dev subdomain to dev account
# dev_delegation = {
#   subdomain = "uci-dev"  # Creates uci-dev.yourdomain.com for dev
#   name_servers = [
#     "ns-1234.awsdns-12.org",     # From dev delegation set
#     "ns-5678.awsdns-34.co.uk",   # From dev delegation set
#     "ns-9012.awsdns-56.com",     # From dev delegation set
#     "ns-3456.awsdns-78.net"      # From dev delegation set
#   ]
# }

# =============================================================================
# ADDITIONAL OPTIONAL VARIABLES
# =============================================================================

# EC2 instance type (optional - defaults provided)
# instance_type = "t3.small"   # Dev: smaller instance
# instance_type = "t3.medium"  # Prod: larger instance

# Key pair name for SSH access (optional - not recommended for production)
# key_name = "your-key-pair-name"

# =============================================================================
# EXAMPLE CONFIGURATIONS
# =============================================================================

# Example 1: Simple Dev Environment (No SSL, Direct IP Access)
# environment = "dev"
# project_name = "backup-metrics"
# s3_bucket_name = "my-dev-bucket"
# allowed_cidr_blocks = ["YOUR.IP.ADDRESS/32"]
# use_alb = false

# Example 2: Dev Environment with Custom Domain
# environment = "dev"
# project_name = "backup-metrics"
# s3_bucket_name = "my-dev-bucket"
# allowed_cidr_blocks = ["YOUR.IP.ADDRESS/32"]
# use_alb = true
# domain_name = "uci-dev.mydomain.com"
# grafana_subdomain = "dashboard"
# delegation_set_id = "N1234567890123456789"

# Example 3: Production Environment
# environment = "prod"
# project_name = "backup-metrics"
# s3_bucket_name = "my-prod-bucket"
# allowed_cidr_blocks = ["YOUR.COMPANY.CIDR/24"]
# use_alb = true
# domain_name = "uci.mydomain.com"
# grafana_subdomain = "dashboard"
# root_domain_name = "mydomain.com"

# =============================================================================
# DEPLOYMENT PATHS SUMMARY
# =============================================================================
# Path A (Simple Dev): use_alb = false, no domain variables
# Path B (Prod Only): use_alb = true, domain_name, root_domain_name
# Path C (Dev + Prod): use_alb = true, all domain variables in both environments
