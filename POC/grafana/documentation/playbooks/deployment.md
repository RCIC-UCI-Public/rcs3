# Grafana Deployment Playbook

This playbook provides multiple deployment paths for the Grafana monitoring solution for RCS3.

## Prerequisites
- AWS CLI access configured
- Terraform installed
- Python environment set up
- Required S3 buckets for Terraform state

## Deployment Paths

Choose your deployment path based on your needs:

### 🚀 **Path A: Simple Testing/Development (No ALB, No SSL)**
- Direct EC2 access via IP and port 3000
- No domain, no SSL, no monthly ALB costs
- Perfect for testing and proof-of-concept

### 🔒 **Path B: Production Only (Real Domain + SSL)**
- Single production environment with custom domain
- Full SSL via ALB and ACM
- Professional setup for production use

### 🌐 **Path C: Production + Development (Real Domains + SSL)**
- Both prod and dev environments with custom domains
- DNS delegation from prod to dev
- Full SSL for both environments

---

## Path A: Simple Testing/Development

### Setup
1. Set `use_alb = false` in your terraform.tfvars
2. Set `domain_name = ""` (or omit entirely)

### Steps
1. **Deploy Infrastructure:**
   ```bash
   cd POC/grafana/terraform/infra
   ./deploy-dev.sh  # or ./deploy-prod.sh
   ```

2. **Get EC2 Public IP:**
   ```bash
   terraform output grafana_instance_id
   # Use AWS console or CLI to get public IP
   ```

3. **Access Grafana:**
   - URL: `http://[EC2-PUBLIC-IP]:3000`
   - S3 Browser: `http://[EC2-PUBLIC-IP]:3001`

### Costs
- **EC2 instance only** (~$10-20/month depending on instance type)
- **No ALB, DNS, or certificate costs**

---

## Path B: Production Only (Real Domain + SSL)

### Prerequisites
- Purchase domain in Route 53 in your prod account

### Steps
1. **Configure Terraform variables** (`terraform.prod.tfvars`):
   ```hcl
   use_alb = true
   domain_name = "uci.yourdomain.com"
   grafana_subdomain = "dashboard"
   root_domain_name = "yourdomain.com"
   ```

2. **Deploy Infrastructure:**
   ```bash
   cd POC/grafana/terraform/infra
   ./deploy-prod.sh
   ```

3. **Access Grafana:**
   - URL: `https://grafana.uci.yourdomain.com`
   - Initial access via ALB DNS (with cert warnings) until DNS propagates

### Result
- Fully functional production environment with trusted SSL
- DNS delegation and ACM validation automatic
- Professional-grade setup

---

## Path C: Production + Development (Real Domains + SSL)

This is the most complete setup with both environments having real domains.

### Prerequisites
- Purchase root domain in Route 53 in your prod account (e.g., `yourdomain.com`)

### Step-by-Step Process

#### 1. **Create Reusable Delegation Set (Dev Account)**
```bash
# Run in dev account
aws route53 create-reusable-delegation-set --caller-reference "dev-delegation-$(date +%s)"
```
Save the returned `Id` value.

#### 2. **Configure Dev Terraform** (`terraform.dev.tfvars`):
```hcl
use_alb = true
domain_name = "uci-dev.yourdomain.com"
grafana_subdomain = "dashboard"
delegation_set_id = "N1PA6795SAMPLE"  # From step 1
```

#### 3. **Deploy Dev Infrastructure:**
```bash
cd POC/grafana/terraform/infra
./deploy-dev.sh
```

#### 4. **Get Dev Name Servers:**
```bash
terraform output custom_hosted_zone_name_servers
```
Copy these name servers.

#### 5. **Configure Prod Terraform** (`terraform.prod.tfvars`):
```hcl
use_alb = true
domain_name = "uci.yourdomain.com"
grafana_subdomain = "dashboard"
root_domain_name = "yourdomain.com"

dev_delegation = {
  subdomain = "uci-dev"
  name_servers = [
    "ns-1226.awsdns-25.org",
    "ns-1664.awsdns-16.co.uk",
    "ns-79.awsdns-09.com",
    "ns-914.awsdns-50.net"
  ]
}
```

#### 6. **Deploy Prod Infrastructure:**
```bash
cd POC/grafana/terraform/infra
./deploy-prod.sh
```

### Result
- **Dev**: `https://grafana.uci-dev.yourdomain.com`
- **Prod**: `https://grafana.uci.yourdomain.com`
- Both environments have trusted SSL certificates
- DNS delegation working automatically
- Stable name servers via delegation set

---

## Configuration and Final Steps (All Paths)

### 1. Update Configuration Variables
Update the configuration Terraform variables file:
- **Dev**: `POC/grafana/terraform/config/terraform.dev.tfvars`
- **Prod**: `POC/grafana/terraform/config/terraform.prod.tfvars`

Add the Grafana URL from your deployment.

### 2. Deploy Configuration
```bash
cd POC/grafana/terraform/config
./deploy-dev.sh  # or ./deploy-prod.sh
```

### 3. Configure User/Team Memberships
```bash
cd POC/grafana/scripts
python update_team_memberships.py
```

---

## Cost Summary

| Component | Path A (Simple) | Path B (Prod Only) | Path C (Prod + Dev) |
|-----------|-----------------|-------------------|-------------------|
| **EC2** | ~$15/month | ~$15/month | ~$30/month |
| **ALB** | $0 | ~$20/month | ~$40/month |
| **Domain** | $0 | ~$15/year | ~$15/year |
| **Route 53 Zones** | $0 | $0.50/month | $1.00/month |
| **Total/Month** | **~$15** | **~$36** | **~$71** |

---

## Troubleshooting

### Certificate Warnings
- Normal during initial deployment
- Certificates become trusted once DNS validation completes
- Can take 5-30 minutes after DNS delegation is active

### DNS Propagation
- Global DNS propagation can take up to 48 hours
- Test with `dig` or `nslookup` to verify delegation

### ALB Health Checks
- Check target group health in AWS console
- Ensure security groups allow ALB → EC2 traffic on port 3000

---

## Why Reusable Delegation Sets?

A reusable delegation set ensures your dev environment has stable name servers even if you destroy and recreate the infrastructure. Without it, you'd need to update the NS records in prod every time you rebuild dev.
