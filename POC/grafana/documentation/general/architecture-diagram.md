# Architecture Diagram and System Overview

This document provides a comprehensive overview of the Grafana monitoring solution architecture, components, and data flow.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    Users                                         │
│                            (Teams & Administrators)                             │
└─────────────────────────────┬───────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             Internet                                            │
└─────────────────────────────┬───────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          Route 53 DNS                                          │
│                    (dashboard.uci.domain.com)                                  │
└─────────────────────────────┬───────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     Application Load Balancer                                  │
│                         (SSL Termination)                                      │
│                       ┌─────────────────────┐                                 │
│                       │  ACM Certificate    │                                 │
│                       │  (Auto-renewal)     │                                 │
│                       └─────────────────────┘                                 │
└─────────────────────────────┬───────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              VPC                                               │
│  ┌─────────────────────┐                           ┌─────────────────────────┐  │
│  │   Public Subnets    │                           │   Private Subnets       │  │
│  │                     │                           │                         │  │
│  │  ┌───────────────┐  │                           │  ┌───────────────────┐  │  │
│  │  │      ALB      │  │                           │  │    EC2 Instance   │  │  │
│  │  │   Targets     │  │                           │  │                   │  │  │
│  │  └───────────────┘  │                           │  │  ┌─────────────┐  │  │  │
│  │                     │                           │  │  │   Grafana   │  │  │  │
│  │  ┌───────────────┐  │                           │  │  │  (Port 3000)│  │  │  │
│  │  │  NAT Gateway  │  │                           │  │  └─────────────┘  │  │  │
│  │  └───────────────┘  │                           │  │                   │  │  │
│  │                     │                           │  │  ┌─────────────┐  │  │  │
│  └─────────────────────┘                           │  │  │ S3 Browser  │  │  │  │
│                                                     │  │  │ (Port 3001) │  │  │  │
│                                                     │  │  └─────────────┘  │  │  │
│                                                     │  │                   │  │  │
│                                                     │  │  ┌─────────────┐  │  │  │
│                                                     │  │  │  IAM Role   │  │  │  │
│                                                     │  │  │ (Instance)  │  │  │  │
│                                                     │  │  └─────────────┘  │  │  │
│                                                     │  └───────────────────┘  │  │
│                                                     └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AWS Services                                         │
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   CloudWatch    │  │   S3 Buckets    │  │   S3 Storage    │                │
│  │                 │  │                 │  │      Lens       │                │
│  │  ┌───────────┐  │  │ ┌─────────────┐ │  │                 │                │
│  │  │  Metrics  │  │  │ │Team Buckets │ │  │ ┌─────────────┐ │                │
│  │  │           │  │  │ │             │ │  │ │   Metrics   │ │                │
│  │  │ • Standard│  │  │ │lopez-fedayk │ │  │ │             │ │                │
│  │  │ • Custom  │  │  │ │ppapadop-mass│ │  │ │ • Storage   │ │                │
│  │  │ • Backup  │  │  │ │    ...      │ │  │ │ • Costs     │ │                │
│  │  └───────────┘  │  │ └─────────────┘ │  │ │ • Requests  │ │                │
│  └─────────────────┘  └─────────────────┘  │ └─────────────┘ │                │
│                                            └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Infrastructure Components

#### 1. **Route 53 DNS**
```
Purpose: Domain name resolution
Configuration:
- Primary domain (prod): dashboard.uci.domain.com
- Dev subdomain: dashboard.uci-dev.domain.com
- DNS delegation for multi-account setups
- Health checks for ALB endpoints
```

#### 2. **Application Load Balancer (ALB)**
```
Purpose: SSL termination and traffic routing
Features:
- SSL/TLS termination with ACM certificates
- HTTP to HTTPS redirection
- Target group health checks
- Path-based routing:
  - / → Grafana (port 3000)
  - /s3-browser → S3 Browser (port 3001)
```

#### 3. **VPC and Networking**
```
Network Design:
- Public Subnets: ALB, NAT Gateway
- Private Subnets: EC2 instances
- Security Groups:
  - ALB SG: 80/443 from internet
  - EC2 SG: 3000/3001 from ALB SG
- NACLs: Default allowing all traffic
```

#### 4. **EC2 Instance**
```
Configuration:
- Instance Type: t3.small (dev) / t3.medium+ (prod)
- AMI: Amazon Linux 2
- EBS: Encrypted general purpose SSD
- IAM Role: CloudWatch and S3 permissions
- User Data: Automated installation script
```

### Application Components

#### 1. **Grafana Server**
```
Installation:
- Package: Official Grafana repository
- Service: systemd managed
- Port: 3000 (internal)
- Database: SQLite (embedded)
- Configuration: /etc/grafana/grafana.ini

Features:
- CloudWatch data source
- Team-based access control
- Folder-based dashboard organization
- Custom dashboard variables
```

#### 2. **S3 Browser Proxy**
```
Technology: Node.js + Express
Installation: /opt/s3-browser/
Service: systemd managed (s3-browser.service)
Port: 3001 (internal)

API Endpoints:
- GET /api/buckets - List accessible buckets
- GET /api/buckets/:bucket - List objects in bucket
- GET /api/buckets/:bucket/download/:key - Download object
```

#### 3. **Team Management System**
```
Implementation: Terraform + Python scripts
Components:
- Terraform: Infrastructure as code
- Python: Team membership automation
- Grafana API: User and team management
```

## Data Flow Architecture

### 1. **Metrics Collection Flow**

```
S3 Buckets → S3 Storage Lens → CloudWatch Metrics → Grafana Dashboards
     │              │                    │                │
     │              ▼                    │                ▼
     │         ┌──────────┐              │         ┌─────────────┐
     │         │ Standard │              │         │   Team      │
     │         │ Metrics  │              │         │ Dashboards  │
     │         │          │              │         │             │
     │         │• Storage │              │         │• Filtered   │
     │         │• Objects │              │         │• Isolated   │
     │         │• Requests│              │         │• Secure     │
     │         └──────────┘              │         └─────────────┘
     │                                   │
     ▼                                   ▼
┌────────────┐                   ┌─────────────┐
│Custom      │                   │ Admin       │
│Backup      │                   │ Dashboards  │
│Metrics     │                   │             │
│            │                   │• Unrestricted│
│backup_age  │                   │• All buckets │
└────────────┘                   └─────────────┘
```

### 2. **User Access Flow**

```
User Login → Authentication → Team Assignment → Folder Access → Dashboard View
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
┌─────────┐  ┌─────────────┐  ┌──────────┐  ┌─────────────┐  ┌──────────┐
│Browser  │  │   Grafana   │  │   Team   │  │   Folder    │  │Filtered  │
│Request  │  │Local Auth   │  │Membership│  │Permissions  │  │Buckets   │
│         │  │             │  │          │  │             │  │          │
│Username │  │• Password   │  │• Team A  │  │• Team Folder│  │• Bucket A│
│Password │  │• Validation │  │• Team B  │  │• Common     │  │• Bucket B│
│         │  │• Session    │  │• Admin   │  │• Admin      │  │• No Other│
└─────────┘  └─────────────┘  └──────────┘  └─────────────┘  └──────────┘
```

### 3. **S3 Browser Integration Flow**

```
Grafana Dashboard → Iframe → S3 Browser → AWS S3 API → Bucket Contents
      │               │          │           │            │
      ▼               ▼          ▼           ▼            ▼
┌──────────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐
│   Team       │ │ Iframe  │ │Node.js  │ │   IAM   │ │  Filtered   │
│ Dashboard    │ │Embedded │ │Proxy    │ │  Role   │ │  Objects    │
│              │ │         │ │         │ │         │ │             │
│• S3 Browser  │ │• Port   │ │• Auth   │ │• S3     │ │• Team       │
│  Panel       │ │  3001   │ │• Filter │ │  Access │ │  Buckets    │
│• Iframe URL  │ │• Team   │ │• API    │ │• CW     │ │  Only       │
└──────────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────┘
```

## Security Architecture

### 1. **Network Security Layers**

```
Internet → WAF (Optional) → ALB → Security Groups → EC2 Instance
    │           │            │         │              │
    ▼           ▼            ▼         ▼              ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐
│External │ │   Web   │ │   SSL   │ │Network  │ │Application  │
│Traffic  │ │Application│ │Termina- │ │Access   │ │    Level    │
│         │ │Firewall │ │  tion   │ │Control  │ │             │
│• HTTPS  │ │         │ │         │ │         │ │• Grafana    │
│• Public │ │• Rate   │ │• TLS    │ │• Ports  │ │  Auth       │
│  Access │ │  Limit  │ │  1.2+   │ │  3000   │ │• Team       │
│         │ │• OWASP  │ │• Auto   │ │  3001   │ │  Isolation  │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────┘
```

### 2. **Access Control Matrix**

| User Type | Admin Folder | Common Folder | Team Folders | S3 Browser | System Admin |
|-----------|-------------|---------------|--------------|------------|--------------|
| **Admin** | ✅ Full     | ✅ Full      | ✅ All       | ✅ All     | ✅ Yes       |
| **Team A**| ❌ No       | ✅ View      | ✅ Team A    | ✅ Team A  | ❌ No        |
| **Team B**| ❌ No       | ✅ View      | ✅ Team B    | ✅ Team B  | ❌ No        |

### 3. **IAM Security Model**

```
EC2 Instance Role → AWS Services
       │                 │
       ▼                 ▼
┌─────────────┐    ┌─────────────┐
│ Permissions │    │  Services   │
│             │    │             │
│• CloudWatch │────│• GetMetrics │
│  Read       │    │• ListMetrics│
│             │    │             │
│• S3 Bucket  │────│• ListBucket │
│  Read       │    │• GetObject  │
│             │    │             │
│• Systems    │────│• SSM        │
│  Manager    │    │  Session    │
└─────────────┘    └─────────────┘
```

## Deployment Architecture

### 1. **Terraform Module Structure**

```
terraform/
├── infra/                   # Infrastructure resources
│   ├── vpc.tf              # Network infrastructure
│   ├── alb.tf              # Load balancer
│   ├── ec2.tf              # Compute resources
│   ├── domain.tf           # DNS and certificates
│   └── outputs.tf          # Infrastructure outputs
│
└── config/                  # Application configuration
    ├── datasources.tf      # Grafana data sources
    ├── teams.tf            # User and team management
    ├── folders.tf          # Folder structure
    ├── dashboards.tf       # Dashboard deployment
    └── s3_browser.tf       # S3 browser integration
```

### 2. **Deployment Flow**

```
Git Repository → Terraform Plan → Infrastructure Deploy → Config Deploy
      │               │              │                    │
      ▼               ▼              ▼                    ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│   Source    │ │ Validation  │ │    AWS      │ │   Application   │
│    Code     │ │             │ │Infrastructure│ │  Configuration  │
│             │ │• Syntax     │ │             │ │                 │
│• Dashboards │ │• Logic      │ │• VPC/ALB    │ │• Teams/Users    │
│• Config     │ │• Security   │ │• EC2/IAM    │ │• Dashboards     │
│• Scripts    │ │• Cost       │ │• DNS/SSL    │ │• Data Sources   │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────────┘
```

## Monitoring and Observability

### 1. **System Health Monitoring**

```
Application Metrics → CloudWatch → Alarms → Notifications
        │                │          │           │
        ▼                ▼          ▼           ▼
┌─────────────┐  ┌─────────────┐ ┌─────────┐ ┌─────────┐
│  Grafana    │  │ CloudWatch  │ │ Alarms  │ │   SNS   │
│  Metrics    │  │   Metrics   │ │         │ │ Topics  │
│             │  │             │ │• CPU    │ │         │
│• Uptime     │  │• EC2        │ │• Memory │ │• Email  │
│• Response   │  │• ALB        │ │• Disk   │ │• Slack  │
│• Errors     │  │• Custom     │ │• Custom │ │• PagerDuty
└─────────────┘  └─────────────┘ └─────────┘ └─────────┘
```

### 2. **Logging Architecture**

```
Application Logs → CloudWatch Logs → Log Analysis → Alerting
       │                 │               │            │
       ▼                 ▼               ▼            ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐ ┌─────────┐
│   System    │  │  Centralized│  │   Analysis  │ │ Actions │
│    Logs     │  │   Logging   │  │             │ │         │
│             │  │             │  │• Patterns   │ │• Alerts │
│• Grafana    │  │• Retention  │  │• Errors     │ │• Tickets│
│• S3 Browser │  │• Encryption │  │• Trends     │ │• Auto   │
│• System     │  │• Access     │  │• Security   │ │  Healing│
└─────────────┘  └─────────────┘  └─────────────┘ └─────────┘
```

This architecture provides a robust, scalable, and secure foundation for S3 monitoring and management with clear separation of concerns and comprehensive security controls.
