# HTTPS Implementation Summary

## What Was Implemented

This implementation adds **HTTPS support with self-signed certificates** and **optional Elastic IP** to your existing Grafana deployment.

## Key Features

### 🔒 HTTPS Security
- **Self-signed SSL certificates** automatically generated for current IP address
- **Port 443** for HTTPS access (ONLY public access method)
- **Ports 3000 & 3001** localhost-only (accessible via SSH for troubleshooting)
- **Certificate regeneration** on instance restart (works with dynamic or static IPs)

### 💰 Cost-Flexible Elastic IP
- **Development**: `use_elastic_ip = false` (FREE - dynamic IP)
- **Production**: `use_elastic_ip = true` ($3.65/month - static IP)
- **Easy switching** between modes with single variable change

## Files Modified

### Infrastructure (`terraform/infra/`)
- ✅ `variables.tf` - Added `use_elastic_ip` variable
- ✅ `ec2.tf` - Added conditional Elastic IP resources and HTTPS security group rule
- ✅ `outputs.tf` - Added flexible IP/URL outputs for both modes
- ✅ `terraform.dev.tfvars` - Set `use_elastic_ip = false` (free dev)
- ✅ `terraform.prod.tfvars` - Set `use_elastic_ip = true` (stable prod)
- ✅ `terraform.example.tfvars` - Added example configuration
- ✅ `install-grafana-s3browser.sh` - Added SSL certificate generation and HTTPS config

### Documentation
- ✅ `README.md` - Updated with HTTPS configuration and access instructions
- ✅ `HTTPS-IMPLEMENTATION-SUMMARY.md` - This summary document

## Usage Instructions

### For Development (Free)
```bash
# terraform.dev.tfvars already configured with:
use_elastic_ip = false

# Deploy normally
terraform apply -var-file="terraform.dev.tfvars"

# Access via HTTPS (certificate warning expected)
# URL: https://[dynamic-ip] (changes on restart)
```

### For Production (Stable IP)
```bash
# terraform.prod.tfvars already configured with:
use_elastic_ip = true

# Deploy normally  
terraform apply -var-file="terraform.prod.tfvars"

# Access via HTTPS (certificate warning expected)
# URL: https://[static-ip] (never changes)
```

### Switching Between Modes
```bash
# Switch from dev to prod
terraform apply -var-file="terraform.prod.tfvars"

# Switch from prod to dev (releases Elastic IP)
terraform apply -var-file="terraform.dev.tfvars"
```

## Access URLs After Deployment

Terraform will output these URLs:
```
grafana_url = "https://1.2.3.4"            # ONLY public access method
grafana_ip = "1.2.3.4"                     # Current IP
grafana_ip_type = "dynamic"                 # or "elastic"
grafana_internal_urls = {
  http_internal = "http://localhost:3000"
  s3_browser_internal = "http://localhost:3001"
}
```

### Public Access
- **HTTPS Only**: `https://[IP]` - The only way to access Grafana from the internet
- **No HTTP**: Ports 3000 and 3001 are not publicly accessible

### Internal Access (SSH Required)
- **Grafana HTTP**: `http://localhost:3000` - For troubleshooting via SSH
- **S3 Browser**: `http://localhost:3001` - For troubleshooting via SSH

## Browser Certificate Warnings

Since we use self-signed certificates, browsers will show warnings:

### Chrome
1. Click "Advanced"
2. Click "Proceed to [IP] (unsafe)"

### Firefox
1. Click "Advanced"
2. Click "Accept the Risk and Continue"

### Safari
1. Click "Show Details"
2. Click "visit this website"
3. Click "Visit Website"

## Cost Summary

- **Development**: $0/month (dynamic IP, free SSL)
- **Production**: $3.65/month (Elastic IP only, free SSL)
- **Certificate**: Self-signed (free) vs Let's Encrypt (free but complex)

## Next Steps

1. **Test in Dev**: Deploy with `use_elastic_ip = false` to test HTTPS functionality
2. **Switch to Prod**: Change to `use_elastic_ip = true` when ready for stable IP
3. **Future Route 53**: Easy to add DNS later (just add hosted zone pointing to same IP)

## Troubleshooting

- **HTTPS not working**: Check port 443 in security group rules
- **Certificate errors**: Expected with self-signed certs - click through warnings  
- **IP changed**: Normal with `use_elastic_ip = false` - get new IP from terraform output
- **Cost concerns**: Keep `use_elastic_ip = false` for development

## Architecture Benefits

- ✅ **Secure**: HTTPS encryption in transit
- ✅ **Flexible**: Choose stability vs cost
- ✅ **Simple**: No external dependencies
- ✅ **Scalable**: Easy upgrade path to Route 53 + real certificates
- ✅ **Cost-effective**: Pay only for what you need
