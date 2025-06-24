# SSL Certificate Management

This directory contains SSL certificates for the Grafana ALB deployment.
The certificate used for the ALB is self-signed, and is designed for dev use or **temporary** production use, assuming you want to purchase a real domain to use. It will be replaced by a AWS issued cert for the official domain that you choose, or will be bypassed completely if you purchase the domain before doing your deployment.

## Files

- `wildcard-elb.key` - Private key for the wildcard certificate
- `wildcard-elb.crt` - Self-signed wildcard certificate for `*.us-west-2.elb.amazonaws.com`
- `generate-wildcard-cert.sh` - Script to regenerate the certificates

## Current Certificate

The current certificate is a self-signed wildcard certificate for:
- **Domain**: `*.us-west-2.elb.amazonaws.com`
- **Validity**: 10 years
- **Purpose**: Provides immediate HTTPS functionality for ALB while ACM certificates are pending validation

## Regenerating Certificates

If you need to recreate the certificates (e.g., for a different region or if they become corrupted):

```bash
cd POC/grafana/terraform/infra/certificates
chmod +x generate-wildcard-cert.sh
./generate-wildcard-cert.sh
```

### For Different Regions

To generate certificates for a different AWS region:

1. Edit `generate-wildcard-cert.sh`
2. Change the `REGION` variable (e.g., `REGION="us-east-1"`)
3. Run the script

## Certificate Details

The certificates are created with:
- **Key Size**: 2048 bits RSA
- **Subject**: `/C=US/ST=California/L=Irvine/O=UCI/OU=RCS3/CN=*.us-west-2.elb.amazonaws.com`
- **Subject Alternative Names**: 
  - `*.us-west-2.elb.amazonaws.com`
  - `us-west-2.elb.amazonaws.com`

## How Certificates Are Used

1. **Terraform Upload**: Terraform uploads these files to AWS Certificate Manager (ACM)
2. **ALB Association**: The ALB uses the ACM certificate for HTTPS listeners
3. **Immediate Functionality**: Provides working HTTPS while domain certificates validate
4. **Manual Switch**: Eventually replaced with validated ACM certificates for custom domains

## Security Notes

- These are **self-signed certificates** - browsers will show security warnings
- They are intended as a **temporary fallback** until proper domain certificates validate
- The certificates are **publicly committed** to the repository (acceptable for self-signed certs)
- **Do not commit** real private keys or certificates from Certificate Authorities

## Backup

The generation script automatically creates timestamped backups of existing certificates before creating new ones:
- `wildcard-elb.key.bak.YYYYMMDD_HHMMSS`
- `wildcard-elb.crt.bak.YYYYMMDD_HHMMSS`
