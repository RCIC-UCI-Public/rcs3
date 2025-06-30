# Grafana Monitoring Solution for RCS3

## Overview

This project delivers a comprehensive, cloud-native monitoring and analytics platform for RCS3 using Grafana, AWS, and supporting automation. It enables real-time S3 metrics visualization, cost insights, and operational dashboards, with infrastructure-as-code for repeatable, environment-specific deployments.

## Architecture

- **Grafana Dashboards:** Prebuilt JSON dashboards for S3 metrics, cost estimates, and operational insights
- **Infrastructure as Code:** Terraform modules provision AWS resources (Route 53, EC2, ALB, S3, IAM, ACM, networking) for both dev and prod environments
- **S3 Browser Proxy:** Node.js service for secure S3 access and integration with Grafana dashboards
- **Team Management:** Automated team-based access control with bucket filtering
- **Security:** Multi-layered security with VPC isolation, SSL termination, and IAM-based access

## Key Features

- **Multi-Environment Support:** Automated AWS infrastructure provisioning (dev/prod)
- **Team-Based Access Control:** Secure, isolated dashboard access per team
- **S3 Browser Integration:** Direct S3 bucket browsing within Grafana
- **Cost Analytics:** Real-time cost estimation and optimization insights
- **Automated Deployment:** Complete infrastructure-as-code with Terraform
- **SSL/DNS Management:** Automated SSL certificates and DNS delegation

## Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Terraform 1.0+ installed
- Python 3.8+ with required packages
- Domain name in Route 53 (for production with SSL)

### Deployment Options

Choose your deployment path:

| Option | Description | Cost | Use Case |
|--------|-------------|------|----------|
| **Path A** | Simple dev/testing (no SSL) | ~$15/month | Development, POC |
| **Path B** | Production only (SSL + domain) | ~$36/month | Single environment |
| **Path C** | Full dev + prod (SSL + domains) | ~$71/month | Complete solution |

### Quick Deploy (Development)

```bash
# 1. Clone and configure
git clone <repository>
cd POC/grafana/terraform/infra
cp terraform.example.tfvars terraform.dev.tfvars
# Edit terraform.dev.tfvars with your settings

# 2. Deploy infrastructure
./deploy-dev.sh

# 3. Deploy configuration
cd ../config
cp terraform.tfvars.example terraform.dev.tfvars
# Edit terraform.dev.tfvars with teams and users
./deploy-dev.sh

# 4. Configure team memberships
cd ../scripts
python update_team_memberships.py
```

Access your Grafana instance at the URL provided in the Terraform output.

## Project Structure

```
POC/grafana/
├── README.md                     # This file
├── dashboards/                   # Grafana dashboard JSON files
├── s3-browser-proxy/            # Node.js S3 browser service
├── scripts/                     # Python automation scripts
├── terraform/
│   ├── infra/                   # Core AWS infrastructure (VPC, ALB, EC2)
│   └── config/                  # Grafana configuration (teams, dashboards)
└── documentation/
    ├── playbooks/               # Step-by-step operational guides
    │   ├── deployment.md        # Comprehensive deployment guide
    │   ├── teardown.md          # Clean removal procedures
    │   ├── update-dashboard.md  # Dashboard update process
    │   └── update-s3-browser.md # S3 browser maintenance
    └── docs/                    # Detailed technical documentation
        ├── configuration-guide.md       # Teams, users, and system config
        ├── security-permissions-guide.md # Security model and IAM
        ├── s3-browser-setup.md         # S3 browser local dev setup
        ├── operational-procedures.md    # Day-to-day operations
        ├── environment-specific-notes.md # Dev vs prod considerations
        └── architecture-diagram.md      # System architecture overview
```

## Documentation

### 📚 **Getting Started**
- **[Deployment Guide](documentation/playbooks/deployment.md)** - Complete deployment instructions for all environments
- **[Configuration Guide](documentation/docs/configuration-guide.md)** - Teams, users, buckets, and system parameters
- **[Architecture Overview](documentation/docs/architecture-diagram.md)** - System design and component relationships

### 🔧 **Operations**
- **[Operational Procedures](documentation/docs/operational-procedures.md)** - Day-to-day management tasks
- **[Update Dashboard Guide](documentation/playbooks/update-dashboard.md)** - Modify and deploy dashboards
- **[S3 Browser Setup](documentation/docs/s3-browser-setup.md)** - Local development and troubleshooting
- **[Environment-Specific Notes](documentation/docs/environment-specific-notes.md)** - Dev vs prod considerations

### 🔒 **Security**
- **[Security & Permissions Guide](documentation/docs/security-permissions-guide.md)** - Security model, IAM roles, and access controls
- **[Teardown Guide](documentation/playbooks/teardown.md)** - Safe removal procedures

## Key Features Explained

### Team-Based Access Control
Each team gets:
- **Dedicated folder** with team-specific dashboards
- **Bucket filtering** - only their S3 buckets visible
- **Isolated access** - no cross-team data visibility
- **S3 browser integration** respecting team boundaries

### Multi-Environment Support
- **Development**: Cost-effective testing with optional SSL
- **Production**: Full SSL, monitoring, and reliability features
- **Shared configuration** with environment-specific overrides

### S3 Browser Integration
- **Native S3 browsing** within Grafana dashboards
- **Team-restricted access** to assigned buckets only
- **Secure proxy** using IAM roles for authentication
- **Download capabilities** for backup files

### Cost Analytics
- **Real-time cost estimation** based on S3 storage and requests
- **Configurable pricing** for different AWS contracts
- **Storage class analysis** (Standard vs Deep Archive)
- **Trend analysis** for cost optimization

## Team Configuration Example

```hcl
bucket_teams = {
  "Team Lopez-Fedaykin" = {
    members = ["user1", "user2", "user3"]
    buckets = ["lopez-fedaykin-uci-s-bkup-bucket"]
  },
  "Team Data-Science" = {
    members = ["scientist1", "analyst1"]
    buckets = [
      "research-data-uci-p-bkup-bucket",
      "ml-models-uci-s-bkup-bucket"
    ]
  }
}
```

## Troubleshooting

### Common Issues
- **Teams can't see buckets**: Check bucket name patterns and team configuration
- **Dashboard shows no data**: Verify CloudWatch metrics and time ranges
- **S3 browser not loading**: Check service status and IAM permissions
- **SSL certificate issues**: Verify DNS delegation and ACM validation

### Support Resources
- **[Operational Procedures](documentation/docs/operational-procedures.md)** - Common task procedures
- **[Security Guide](documentation/docs/security-permissions-guide.md)** - Permission troubleshooting
- **[Architecture Diagram](documentation/docs/architecture-diagram.md)** - System component relationships

## Maintenance

### Regular Tasks
- **Team Management**: Add/remove users and teams as needed
- **Dashboard Updates**: Export from Grafana, commit to Git, deploy
- **Cost Review**: Update pricing parameters for contract changes
- **Security Updates**: Monitor and apply security patches

### Automated Features
- **SSL Certificate Renewal**: Automatic via AWS Certificate Manager
- **DNS Management**: Automated delegation and health checks
- **Infrastructure Scaling**: Auto-scaling groups for high availability
- **Backup**: Terraform state and dashboard JSON in version control

## Development and Contributions

### Local Development
1. **S3 Browser**: See [S3 Browser Setup Guide](documentation/docs/s3-browser-setup.md)
2. **Dashboard Development**: Create in Grafana, export JSON, commit to repository
3. **Testing**: Always test changes in dev environment first

### Best Practices
- **Infrastructure as Code**: All changes via Terraform
- **Version Control**: Dashboard JSON and configuration in Git
- **Environment Parity**: Keep dev and prod configurations similar
- **Documentation**: Update guides when adding features

## Cost Optimization

### Development Environment
- **Temporary deployment**: Destroy when not needed (~50-70% cost savings)
- **Smaller instances**: Use t3.small for development
- **No ALB**: Direct IP access for internal testing

### Production Environment
- **Reserved Instances**: For predictable long-term usage
- **Right-sizing**: Monitor and adjust instance types based on usage
- **Efficient monitoring**: Optimize CloudWatch metric collection

## Security

This solution implements enterprise-grade security:
- **Network isolation**: VPC with private subnets
- **SSL/TLS encryption**: All traffic encrypted in transit
- **IAM-based access**: No stored credentials, role-based permissions
- **Team isolation**: Strict separation of team data and access
- **Audit logging**: CloudTrail integration for compliance

---

## Getting Help

- **Quick Start**: Follow the [Deployment Guide](documentation/playbooks/deployment.md)
- **Configuration**: See [Configuration Guide](documentation/docs/configuration-guide.md)
- **Operations**: Check [Operational Procedures](documentation/docs/operational-procedures.md)
- **Troubleshooting**: Review environment-specific documentation

Ready to deploy? Start with the **[Deployment Guide](documentation/playbooks/deployment.md)**! 🚀
