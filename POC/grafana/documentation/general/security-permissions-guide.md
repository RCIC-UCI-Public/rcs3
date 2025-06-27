# Security & Permissions Guide

This guide covers the security model, IAM permissions, network security, and access controls for the Grafana monitoring solution.

## Security Architecture Overview

The system implements multi-layered security:
- **Network Security**: VPC, security groups, ALB restrictions
- **AWS IAM**: Role-based access for resources
- **Grafana Authentication**: User/team-based dashboard access
- **S3 Bucket Isolation**: Team-specific bucket access

## IAM Roles and Policies

### Grafana EC2 Instance Role

The EC2 instance running Grafana has an IAM role with the following permissions:

**Role Name**: `grafana-instance-role`

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics",
        "cloudwatch:GetMetricData"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::*-uci-*-bkup-bucket",
        "arn:aws:s3:::*-uci-*-bkup-bucket/*"
      ]
    }
  ]
}
```

### S3 Browser Service Role

The S3 browser proxy has additional S3 permissions for bucket browsing:

**Additional Permissions**:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:ListAllMyBuckets",
    "s3:GetBucketLocation",
    "s3:GetObjectVersion",
    "s3:ListBucketVersions"
  ],
  "Resource": "*"
}
```

## Network Security

### VPC Configuration

- **Private Subnets**: EC2 instances run in private subnets
- **Public Subnets**: ALB and NAT gateways in public subnets
- **Internet Access**: Outbound only through NAT gateway

### Security Groups

#### ALB Security Group
```
Inbound:
- Port 443 (HTTPS): 0.0.0.0/0
- Port 80 (HTTP): 0.0.0.0/0 (redirects to HTTPS)

Outbound:
- Port 3000: EC2 security group
```

#### EC2 Security Group
```
Inbound:
- Port 3000: ALB security group (Grafana)
- Port 3001: ALB security group (S3 Browser)
- Port 22: Management subnet (SSH - if enabled)

Outbound:
- Port 443: 0.0.0.0/0 (HTTPS to AWS APIs)
- Port 80: 0.0.0.0/0 (HTTP updates)
```

### SSL/TLS Configuration

**Certificate Management**:
- **Provider**: AWS Certificate Manager (ACM)
- **Validation**: DNS validation through Route 53
- **Renewal**: Automatic
- **Protocols**: TLS 1.2 and 1.3 only

**ALB SSL Policy**: `ELBSecurityPolicy-TLS-1-2-2017-01`

## Grafana Access Control

### User Authentication

**Authentication Method**: Grafana local authentication
- Users created automatically via Terraform
- Default passwords set in configuration
- Force password change on first login (recommended)

### Permission Model

#### Admin Users
```
Permissions:
- Full access to all folders
- Dashboard creation/modification
- User management
- System configuration
```

#### Team Users
```
Permissions:
- View access to team folder only
- View access to common folder
- Cannot modify dashboards
- Cannot access other team folders
```

### Folder Structure

```
Grafana Folders:
├── Admin (Admin users only)
│   └── Unrestricted dashboards
├── Common Dashboards (All teams)
│   └── Shared dashboards
├── Team A Dashboards (Team A only)
│   └── Bucket-filtered dashboards
└── Team B Dashboards (Team B only)
    └── Bucket-filtered dashboards
```

## Team Isolation

### Dashboard Isolation

Each team gets:
- **Dedicated folder** with team-specific dashboards
- **Bucket filtering** - only their buckets visible in dropdowns
- **No cross-team access** to other team folders

### S3 Bucket Access

**Team Bucket Restrictions**:
- Teams can only see their assigned buckets
- Bucket lists filtered at dashboard level
- S3 browser respects team bucket assignments

### Data Isolation

**CloudWatch Metrics**:
- All teams see same metric namespace
- Bucket filtering provides data isolation
- No sensitive data in metric names

## Credential Management

### S3 Browser Credentials

**Production Deployment**:
- Uses EC2 instance IAM role
- No stored credentials required
- Automatic credential refresh

**Local Development**:
- Requires credentials.json file
- AWS access keys for development
- Should be excluded from version control

### Grafana Credentials

**Admin Credentials**:
- Set during Terraform deployment
- Stored in Grafana database
- Should be changed after deployment

**User Credentials**:
- Generated automatically
- Default password in Terraform config
- Users should change on first login

## Security Best Practices

### Deployment Security

1. **Change Default Passwords**:
   ```bash
   # Update terraform.tfvars
   default_user_password = "SecurePassword123!"
   ```

2. **Restrict Admin Access**:
   ```hcl
   admin_users = ["specific-admin-user"]  # Minimal list
   ```

3. **Use Strong SSL**:
   ```hcl
   use_alb = true  # Enables SSL termination
   ```

### Operational Security

1. **Regular Updates**:
   - Keep Grafana updated
   - Update EC2 instance packages
   - Monitor security advisories

2. **Access Monitoring**:
   - Monitor CloudTrail logs
   - Review Grafana access logs
   - Set up alerting for admin actions

3. **Network Monitoring**:
   - Monitor VPC Flow Logs
   - Set up intrusion detection
   - Regular security group audits

### Data Protection

1. **Encryption in Transit**:
   - HTTPS/TLS for all web traffic
   - TLS for API calls to AWS
   - Encrypted S3 bucket access

2. **Encryption at Rest**:
   - EBS volumes encrypted
   - S3 bucket encryption (customer managed)
   - CloudWatch Logs encryption

## Compliance Considerations

### Data Residency
- All data stays within specified AWS region
- No cross-region data transfer
- VPC provides network isolation

### Access Logging
- ALB access logs (if enabled)
- CloudTrail API logs
- Grafana audit logs

### Data Retention
- CloudWatch metrics: Standard retention
- Application logs: Configurable retention
- Access logs: Configurable retention

## Security Incident Response

### Suspected Compromise

1. **Immediate Actions**:
   ```bash
   # Rotate instance credentials
   aws iam update-access-key --access-key-id AKIA... --status Inactive
   
   # Check recent activity
   aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=grafana-role
   ```

2. **Isolate Instance**:
   - Modify security groups to block traffic
   - Create snapshot for forensics
   - Replace instance if necessary

3. **Review and Remediate**:
   - Review all user accounts
   - Check dashboard modifications
   - Audit team memberships

### Password Compromise

1. **Reset User Passwords**:
   ```bash
   cd POC/grafana/terraform/config
   # Update default_user_password in tfvars
   ./deploy-dev.sh  # or deploy-prod.sh
   ```

2. **Force Re-authentication**:
   - Clear Grafana sessions
   - Require all users to log in again

## Monitoring and Alerting

### Security Monitoring

**Recommended CloudWatch Alarms**:
- Unusual API call patterns
- Failed authentication attempts
- Administrative actions
- Network traffic anomalies

**Grafana Security Monitoring**:
- Failed login attempts
- Administrative dashboard changes
- New user creation
- Permission changes

### Security Metrics

Track these metrics for security monitoring:
- Number of active sessions
- Failed authentication rate
- Admin action frequency
- Dashboard modification frequency

## Troubleshooting Security Issues

### Access Denied Errors

1. **Check IAM Permissions**:
   ```bash
   aws iam simulate-principal-policy \
     --policy-source-arn arn:aws:iam::ACCOUNT:role/grafana-instance-role \
     --action-names cloudwatch:GetMetricStatistics \
     --resource-arns "*"
   ```

2. **Verify Security Groups**:
   - Check ALB → EC2 connectivity
   - Verify port 3000/3001 access
   - Check outbound rules for AWS API access

### Certificate Issues

1. **Check Certificate Status**:
   ```bash
   aws acm describe-certificate --certificate-arn arn:aws:acm:...
   ```

2. **Verify DNS Validation**:
   - Check Route 53 validation records
   - Verify domain ownership
   - Check certificate renewal status
