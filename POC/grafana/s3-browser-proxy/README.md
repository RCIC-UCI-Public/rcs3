# S3 Browser Proxy

A Node.js web application that provides a browser interface for S3 buckets with team-based filtering.

## Prerequisites

### System Requirements

#### Windows
1. **Node.js 18+ and npm**
   - Download from: https://nodejs.org/
   - Or install via Chocolatey: `choco install nodejs`
   - Or install via Scoop: `scoop install nodejs`

2. **Git**
   - Download from: https://git-scm.com/download/win
   - Or install via Chocolatey: `choco install git`

3. **AWS CLI (optional for local S3 access)**
   - Download from: https://aws.amazon.com/cli/
   - Or install via Chocolatey: `choco install awscli`

4. **Windows Terminal or PowerShell** (recommended)
   - Download from Microsoft Store or use built-in PowerShell

#### macOS
1. **Node.js 18+ and npm**
   - Download from: https://nodejs.org/
   - Or install via Homebrew: `brew install node`
   - Or install via MacPorts: `sudo port install nodejs18`

2. **Git**
   - Install via Homebrew: `brew install git`
   - Or download from: https://git-scm.com/download/mac
   - Or use Xcode Command Line Tools: `xcode-select --install`

3. **AWS CLI (optional for local S3 access)**
   - Install via Homebrew: `brew install awscli`
   - Or download from: https://aws.amazon.com/cli/

### Verification

After installation, verify your setup:

```bash
# Check Node.js version (should be 18+)
node --version

# Check npm version
npm --version

# Check Git version
git --version

# Check AWS CLI (if installed)
aws --version
```

### AWS Configuration (Optional)

If you want to test with real S3 buckets locally, configure AWS credentials:

```bash
# Configure AWS CLI with your credentials
aws configure

# Or export environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_SESSION_TOKEN=your_session_token  # if using temporary credentials
```

## Local Development

### Quick Start
```bash
# Install dependencies (first time only)
npm install

# Start the service
./start-service.sh

# Stop the service
./stop-service.sh
```

The application will be available at http://localhost:3001

### Setup (First Time)
```bash
# Install Node.js dependencies and configure
./setup.sh
```

### Platform-Specific Notes

#### Windows Users
- Use PowerShell or Command Prompt for running commands
- If shell scripts (.sh files) don't work, run the npm commands directly:
  ```powershell
  npm install
  npm start
  ```
- For development, consider using Windows Subsystem for Linux (WSL) for a more Unix-like experience

#### macOS Users
- Make sure shell scripts are executable:
  ```bash
  chmod +x start-service.sh stop-service.sh setup.sh
  ```
- If you encounter permission issues with npm, consider using a Node version manager like `nvm`

### Development Environment Setup

1. **Clone the repository** (if working from source):
   ```bash
   git clone <repository-url>
   cd POC/grafana/s3-browser-proxy
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment** (optional):
   - Copy `config/example.json` to `config/local.json`
   - Modify settings as needed for local development

4. **Start development server**:
   ```bash
   npm run dev
   # Or use the convenience script
   ./start-service.sh
   ```

### Troubleshooting

#### Common Issues

**Node.js version conflicts**:
- Use Node Version Manager (nvm) to manage multiple Node.js versions
- Windows: Install nvm-windows
- macOS: Install nvm via Homebrew or curl

**Permission errors on macOS**:
```bash
# Fix npm permissions
sudo chown -R $(whoami) ~/.npm
# Or use a Node version manager
```

**Port 3001 already in use**:
```bash
# Find and kill the process using port 3001
# Windows:
netstat -ano | findstr :3001
taskkill /PID <process_id> /F

# macOS:
lsof -ti:3001 | xargs kill -9
```

**AWS credentials not working**:
- Ensure credentials are properly configured
- Check that IAM user has S3 read permissions
- Verify region settings match your S3 buckets

## Files

- **server.js** - Main Node.js application
- **package.json** - Dependencies and configuration
- **start-service.sh** - Start the service locally
- **stop-service.sh** - Stop the service locally
- **setup.sh** - Initial setup and dependency installation
- **public/** - Web interface files
- **config/** - Configuration examples

## EC2 Deployment

The service is automatically deployed and configured as a systemd service on the EC2 instance during Terraform infrastructure deployment. No manual deployment steps are required.

## Usage

- **Browse S3 buckets**: Navigate to http://localhost:3001
- **Team filtering**: Add `?filter=bucket1,bucket2` to URL for specific buckets
- **Grafana integration**: Embedded via iframes in team-specific dashboards

## Updates

The easiest way to deploy changes to the html/JS is to: 
- run the infra *terraform apply* process
- ssh into the ec2 instance
- run the following at the ec2 CLI:
- aws s3 cp s3://backup-metrics-tfstate-dev/scripts/install-grafana-s3browser.sh /tmp/install-script.sh
- chmod +x /tmp/install-script.sh
- sudo /tmp/install-script.sh