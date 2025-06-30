# S3 Browser Setup Guide

This guide covers how to set up and configure the S3 Browser component for both production deployment and local development.

## Overview

The S3 Browser is a Node.js proxy service that provides a web interface for browsing S3 buckets. It integrates with Grafana dashboards and respects team bucket restrictions.

## Production Setup (Automatic)

In production, the S3 Browser is automatically deployed and configured:

- **Automatic Deployment**: Installed via Terraform during infrastructure deployment
- **IAM Authentication**: Uses EC2 instance IAM role for S3 access
- **Service Management**: Runs as systemd service on port 3001
- **Integration**: Embedded in team dashboards via iframe

### Production Architecture

```
User → ALB → EC2:3001 → S3 Browser → S3 Buckets
                ↓
            IAM Role Authentication
```

### Automatic Configuration

The following is handled automatically in production:
- Node.js and npm installation
- S3 Browser service installation
- systemd service configuration
- IAM role assignment
- ALB routing configuration

## Local Development Setup

For local development and testing, you need to set up the S3 Browser manually.

### Prerequisites

- Node.js 16+ installed
- AWS CLI configured
- Access to S3 buckets for testing

### Step 1: Install Dependencies

```bash
cd POC/grafana/s3-browser-proxy
npm install
```

### Step 2: Configure AWS Credentials

Create a credentials file for local development:

```bash
cp config/credentials.json.example config/credentials.json
```

Edit `config/credentials.json`:

```json
{
  "accessKeyId": "AKIA...",
  "secretAccessKey": "your-secret-key",
  "region": "us-west-2"
}
```

**⚠️ Security Note**: Never commit credentials.json to version control. It's included in .gitignore.

### Step 3: Local Configuration

The S3 Browser automatically detects local vs production environment:

- **Local**: Uses credentials.json file
- **Production**: Uses IAM role

### Step 4: Run Locally

```bash
# Start the server
npm start

# Or use node directly
node server.js
```

The service will start on `http://localhost:3001`

### Step 5: Test Local Setup

1. **Direct Access**: Navigate to `http://localhost:3001`
2. **API Test**: Check `http://localhost:3001/api/buckets`
3. **Bucket Browse**: Try `http://localhost:3001/api/buckets/your-bucket-name`

## Configuration Options

### Environment Variables

The S3 Browser supports these environment variables:

```bash
# Port configuration
PORT=3001

# AWS region (if not in credentials)
AWS_REGION=us-west-2

# Enable debug logging
DEBUG=true

# CORS configuration
CORS_ORIGIN=*
```

### Server Configuration

Key configuration options in `server.js`:

```javascript
const config = {
  port: process.env.PORT || 3001,
  cors: {
    origin: process.env.CORS_ORIGIN || '*',
    credentials: true
  },
  aws: {
    region: process.env.AWS_REGION || 'us-west-2'
  }
}
```

## API Endpoints

The S3 Browser provides these REST endpoints:

### List Buckets
```
GET /api/buckets
```
Returns list of accessible S3 buckets.

### List Objects
```
GET /api/buckets/:bucketName
GET /api/buckets/:bucketName?prefix=path/to/folder&delimiter=/
```
Returns objects in specified bucket with optional prefix filtering.

### Get Object Metadata
```
GET /api/buckets/:bucketName/object/:objectKey
```
Returns metadata for specific object.

### Download Object
```
GET /api/buckets/:bucketName/download/:objectKey
```
Provides download link for object.

## Web Interface

### Features

- **Bucket Browsing**: Navigate folder structure
- **File Preview**: View file metadata and properties
- **Download**: Direct download links
- **Search**: Filter objects by name
- **Responsive**: Works on desktop and mobile

### Integration with Grafana

The S3 Browser is embedded in Grafana dashboards via iframe:

```html
<iframe src="https://your-grafana-url:3001" width="100%" height="600px"></iframe>
```

## Team Restrictions

### Bucket Filtering

The S3 Browser respects team bucket restrictions:

- **Team Users**: Only see buckets assigned to their team
- **Admin Users**: See all buckets
- **Filtering**: Applied at API level

### Implementation

Bucket filtering is implemented in the backend:

```javascript
// Filter buckets based on user team
app.get('/api/buckets', (req, res) => {
  const userTeam = getUserTeam(req);
  const allowedBuckets = getTeamBuckets(userTeam);
  const filteredBuckets = allBuckets.filter(bucket => 
    allowedBuckets.includes(bucket.Name)
  );
  res.json(filteredBuckets);
});
```

## Troubleshooting

### Local Development Issues

#### Credentials Not Working

1. **Check Credentials Format**:
   ```json
   {
     "accessKeyId": "AKIA...",
     "secretAccessKey": "...",
     "region": "us-west-2"
   }
   ```

2. **Verify AWS Access**:
   ```bash
   aws s3 ls --profile your-profile
   ```

3. **Check Permissions**:
   - Ensure access keys have S3 read permissions
   - Verify bucket policies allow access

#### CORS Issues

If running Grafana locally, you may need to update CORS settings:

```javascript
// In server.js
const corsOptions = {
  origin: ['http://localhost:3000', 'https://your-grafana-domain'],
  credentials: true
};
```

#### Port Conflicts

If port 3001 is in use:

```bash
# Use different port
PORT=3002 npm start
```

### Production Issues

#### Service Not Starting

1. **Check Service Status**:
   ```bash
   sudo systemctl status s3-browser
   ```

2. **View Logs**:
   ```bash
   sudo journalctl -u s3-browser -f
   ```

3. **Check File Permissions**:
   ```bash
   ls -la /opt/s3-browser/
   sudo chown -R ubuntu:ubuntu /opt/s3-browser/
   ```

#### IAM Permission Issues

1. **Verify Instance Role**:
   ```bash
   aws sts get-caller-identity
   ```

2. **Test S3 Access**:
   ```bash
   aws s3 ls
   ```

3. **Check CloudTrail**: Look for access denied errors

#### Network Connectivity

1. **Check Security Groups**:
   - ALB → EC2 port 3001 allowed
   - EC2 → Internet for AWS API calls

2. **Test Internal Connectivity**:
   ```bash
   curl http://localhost:3001/api/buckets
   ```

3. **Check ALB Target Health**:
   - Verify target group health in AWS console

## Maintenance and Updates

### Updating S3 Browser Code

1. **Update Local Files**:
   ```bash
   cd POC/grafana/s3-browser-proxy
   # Make changes to server.js or public/index.html
   ```

2. **Deploy via Terraform**:
   ```bash
   cd POC/grafana/terraform/infra
   ./deploy-dev.sh  # or deploy-prod.sh
   ```

3. **Update on Server**:
   Follow the [S3 Browser Update Playbook](../playbooks/update-s3-browser.md)

### Adding New Features

When adding new API endpoints or features:

1. **Update server.js**: Add new routes and handlers
2. **Update public/index.html**: Add frontend functionality
3. **Test Locally**: Verify changes work in development
4. **Deploy**: Use standard deployment process

### Security Updates

Regular maintenance tasks:

1. **Update Node.js Dependencies**:
   ```bash
   npm audit
   npm update
   ```

2. **Monitor Security Advisories**: Check for Node.js and npm security updates

3. **Review Access Logs**: Monitor for unusual access patterns

## Best Practices

### Development

1. **Never Commit Credentials**: Always use .gitignore for credentials.json
2. **Use Environment Variables**: For configuration that varies by environment
3. **Test Locally**: Verify changes before deploying
4. **Document API Changes**: Update this guide when adding features

### Production

1. **Monitor Service Health**: Set up alerts for service failures
2. **Regular Updates**: Keep dependencies updated
3. **Log Monitoring**: Monitor application logs for errors
4. **Performance Monitoring**: Track response times and resource usage

### Security

1. **Minimal Permissions**: Use least privilege for IAM roles
2. **Access Logging**: Enable and monitor access logs
3. **Regular Audits**: Review user access and permissions
4. **Secure Headers**: Implement security headers in responses
