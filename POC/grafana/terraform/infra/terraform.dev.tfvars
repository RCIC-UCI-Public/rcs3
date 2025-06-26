# Environment and Project details
environment  = "dev"
project_name = "backup-metrics"

# S3 Configuration
s3_bucket_name = "backup-metrics-tfstate-dev"

# Allowed IP addresses in CIDR notation
allowed_cidr_blocks = [
  # UCI Network Blocks (ASN299)
  "128.195.0.0/16",  # General Public IPs
  "128.200.0.0/16",  # General Public IPs
  "160.87.0.0/16",   # UCI Health
  "169.234.0.0/16",  # Mobile Access & ResNet Public IPs
  "192.5.19.0/24",   # LightPath

  # Non-UCI Blocks
  "68.5.95.209/32",
  "68.96.70.0/24"
]

# ALB Configuration
use_alb = true  # Dev: Use simple EC2 direct access (saves ~$16/month)

# Domain Configuration
domain_name = "uci-dev.rcs3.org"
grafana_subdomain = "dashboard"

delegation_set_id = "N059266834246UBV0QBPY"

# aws route53 create-reusable-delegation-set --caller-reference "setup-$(date +%s)"
# {
#     "Location": "https://route53.amazonaws.com/2013-04-01/delegationset/N059266834246UBV0QBPY",
#     "DelegationSet": {
#         "Id": "/delegationset/N059266834246UBV0QBPY",
#         "CallerReference": "setup-1750877209",
#         "NameServers": [
#             "ns-848.awsdns-42.net",
#             "ns-1703.awsdns-20.co.uk",
#             "ns-1211.awsdns-23.org",
#             "ns-199.awsdns-24.com"
#         ]
#     }
# }
