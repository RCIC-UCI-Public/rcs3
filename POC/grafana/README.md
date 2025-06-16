# Grafana S3 Monitoring System - Deployment Guide

This system provides Grafana dashboards for monitoring S3 storage usage with team-based access controls and an integrated S3 browser.

## Prerequisites

Before starting, ensure you have the following installed on your system:

### Required Software (All Platforms)
- **AWS CLI** installed and configured
- **Terraform** installed (version 1.0+)
- **Python 3.6+** with pip (for team management script)
- Access to an AWS account with appropriate permissions

### Platform-Specific Requirements

#### Windows
- **PowerShell** or **Command Prompt** (built-in)

#### macOS
- **Terminal** (built-in)
- **Homebrew** - Recommended for easy package installation

#### Linux
- **Terminal/Shell** (built-in)

### Installation Instructions by Platform

#### Windows Installation
1. **Install AWS CLI**:
   ```powershell
   # Option 1: Download MSI installer from AWS website
   # https://aws.amazon.com/cli/
   
   # Option 2: Using Chocolatey (if installed)
   choco install awscli
   
   # Option 3: Using pip
   pip install awscli
   ```

2. **Install Terraform**:
   ```powershell
   # Option 1: Download from HashiCorp website
   # https://www.terraform.io/downloads.html
   
   # Option 2: Using Chocolatey (if installed)
   choco install terraform
   ```

3. **Install Python 3**:
   ```powershell
   # Option 1: Download from Python.org (recommended)
   # https://www.python.org/downloads/
   
   # Option 2: Microsoft Store (easiest)
   # Search for "Python 3" in Microsoft Store
   
   # Option 3: Using Chocolatey (if installed)
   choco install python
   ```

#### macOS Installation
1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install AWS CLI**:
   ```bash
   # Option 1: Using Homebrew (recommended)
   brew install awscli
   
   # Option 2: Using pip
   pip3 install awscli
   ```

3. **Install Terraform**:
   ```bash
   # Using Homebrew (recommended)
   brew install terraform
   ```

4. **Install Python 3**:
   ```bash
   # Option 1: Using Homebrew (recommended)
   brew install python3
   
   # Option 2: macOS usually has Python 3 pre-installed
   # Check version: python3 --version
   ```

#### Linux Installation
1. **Install AWS CLI**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install awscli
   
   # CentOS/RHEL/Fedora
   sudo yum install awscli
   # or
   sudo dnf install awscli
   
   # Using pip (universal)
   pip3 install awscli
   ```

2. **Install Terraform**:
   ```bash
   # Download and install manually
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

3. **Install Python 3**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip
   
   # CentOS/RHEL/Fedora
   sudo yum install python3 python3-pip
   # or
   sudo dnf install python3 python3-pip
   
   # Most Linux distributions have Python 3 pre-installed
   # Check version: python3 --version
   ```

## Quick Start Guide

### Step 1: Configure AWS Credentials

Set your temporary AWS credentials:

#### Windows (PowerShell)
```powershell
$env:AWS_ACCESS_KEY_ID="..."
$env:AWS_SECRET_ACCESS_KEY="..."
$env:AWS_SESSION_TOKEN="..."
```

#### Windows (Command Prompt)
```cmd
set AWS_ACCESS_KEY_ID=...
set AWS_SECRET_ACCESS_KEY=...
set AWS_SESSION_TOKEN=...
```

#### macOS/Linux (Bash/Terminal)
```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
```

**Note**: These credentials are temporary and will need to be refreshed periodically during deployment.

### Step 2: Configure Infrastructure Settings

Navigate to the infrastructure directory and update the configuration file:

```bash
cd terraform/infra
```

Edit `main.tf` to configure the S3 backend:
- Update the `bucket` name in the terraform backend configuration
- Ensure the `region` matches your target AWS region

Edit `dev.tfvars` to set your environment-specific values:
- `project_name`: Name for your project resources
- `environment`: Environment name (e.g., "dev", "prod")
- `allowed_cidr_blocks`: IP CIDR blocks that should have access to the Grafana instance
- `grafana_password`: Strong password for Grafana admin access

**Important**: The `allowed_cidr_blocks` must include the IP ranges from which you'll access Grafana. You can find your current IP at https://whatismyipaddress.com/

### Step 3: Deploy Infrastructure

Initialize and deploy the infrastructure:

```bash
terraform init
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars"
```

**Save the outputs**: After deployment completes, save these important values:
- `grafana_url`: The URL to access your Grafana instance
- `grafana_admin_password`: The admin password (if auto-generated)
- `ec2_public_ip`: The public IP of your Grafana server

### Step 4: Configure Grafana Settings

Navigate to the configuration directory:

```bash
cd ../config
```

Update `providers.tf` to configure the S3 backend (same bucket and region as infrastructure).

Edit `terraform.dev.tfvars` with the values from Step 3:
- `grafana_url`: Use the URL from infrastructure output
- `grafana_username`: Set to "admin" (the default admin username)
- `bucket_teams`: Configure your teams and their assigned S3 buckets
- `admin_users`: List users who should have admin privileges

**Important Notes**:
- Do NOT include `grafana_password` in the config file for security reasons
- The script will prompt for the password when needed
- Ensure proper spacing around the `=` operator in the config file

**Example team configuration**:
```hcl
# Grafana Configuration
grafana_username = "admin"
grafana_url      = "http://34.222.140.89:3000"

# Admin users (will be created with admin privileges)
admin_users = ["admin2"]

# Common dashboards available to all users
common_dashboards = ["cost-estimates.json", "lifecycle-metrics.json"]

# Define teams and their bucket access permissions
bucket_teams = {
  "Team lopez-fedaykin" = {
    members = ["user1", "user2"]
    buckets = ["lopez-fedaykin-uci-s-bkup-bucket"]
  },
  "Team ppapadop-mass" = {
    members = ["user3", "user2"]
    buckets = ["ppapadop-mass-uci-s-bkup-bucket"]
  }
}

# Default password for all users (can be overridden)
default_user_password = "ChangeMe123!"
```

### Step 5: Deploy Grafana Configuration

Initialize and deploy the Grafana configuration:

```bash
terraform init
terraform plan -var-file="terraform.dev.tfvars"
terraform apply -var-file="terraform.dev.tfvars"
```

### Step 6: Configure Team Memberships

First, install the required Python dependencies, then run the team membership script:

#### All Platforms - Install Dependencies
```bash
cd ../scripts
pip install -r requirements.txt
```

#### Run the Script

#### All Platforms (Python Script)
```bash
python3 update_team_memberships.py dev
```

#### Windows (PowerShell)
```powershell
python update_team_memberships.py dev
```

#### Windows (Command Prompt)
```cmd
python update_team_memberships.py dev
```

**When prompted**:
- Enter the Grafana admin password from Step 3
- The script will automatically create teams and assign users
- Admin privileges will be granted to users listed in `admin_users`

**Note**: The script uses proper HCL parsing for reliable configuration reading and prompts for the admin password for security (never stores it in configuration files).

## Access Your System

After successful deployment:

1. **Grafana Dashboard**: Open the `grafana_url` from Step 3 in your browser
2. **Login**: Use `admin` as username and the password from Step 3
3. **Browse S3**: Navigate to the "S3 Browser" folder for team-specific S3 access

## Project Structure

```
grafana/
├── README.md              # This deployment guide
├── terraform/
│   ├── infra/            # Infrastructure (EC2, networking, etc.)
│   └── config/           # Grafana configuration (dashboards, teams)
│       ├── providers.tf  # Terraform backend and provider config
│       ├── variables.tf  # Variable definitions
│       ├── dashboard_processing.tf  # Dashboard file processing
│       ├── folders.tf    # Folder creation and permissions
│       ├── main.tf       # Core dashboard resources
│       ├── outputs.tf    # Output values
│       └── terraform.dev.tfvars  # Environment configuration
├── scripts/              # Team management scripts
├── dashboards/           # Grafana dashboard JSON files
├── s3-browser-proxy/     # S3 browser web application
```

## Common Issues & Solutions

### Access Issues
- **Can't reach Grafana**: Check that your IP is included in `allowed_cidr_blocks`
- **Login fails**: Verify the admin password from infrastructure outputs

### Deployment Issues
- **Terraform fails**: Ensure AWS credentials are valid and not expired
- **Permission errors**: Verify your AWS account has necessary permissions for EC2, VPC, and IAM

### Team Setup Issues
- **Script fails**: Ensure Grafana is accessible and admin password is correct
- **Configuration parsing errors**: Check that config file has proper formatting with correct spacing around `=` operators
- **Users not appearing**: Check that usernames match exactly in team configuration
- **Missing grafana_url or grafana_username**: Ensure both values are properly set in terraform.dev.tfvars

### Python Issues
- **Python not found**: Ensure Python 3.6+ is installed and in your PATH
  - Windows: Try `python` instead of `python3` if using Python from Microsoft Store
  - Check version: `python --version` or `python3 --version`
- **pip install fails**: Ensure you have internet access and pip is installed
  - Try: `python -m pip install requests` instead of `pip install requests`
- **Permission errors**: On macOS/Linux, you might need `pip3 install --user requests`
- **Import errors**: The script requires `requests` and `python-hcl2` packages (install with `pip install -r requirements.txt`)

### Configuration Fixes
The recent updates have fixed:
- **Parsing issues with whitespace**: The script now handles variable spacing around `=` in config files
- **Password handling**: The script properly prompts for passwords and handles security correctly
- **File organization**: Config files have been refactored for better maintainability

## Security Notes

- This system creates an EC2 instance accessible from the internet
- Access is restricted to the IP ranges specified in `allowed_cidr_blocks`
- The Grafana instance includes an integrated S3 browser for team-specific bucket access
- All S3 access is read-only for security
- Admin passwords are never stored in configuration files - always prompted when needed
