#!/bin/bash

# generate-wildcard-cert.sh
# Creates self-signed wildcard certificate for AWS ALB
# This script recreates the certificates used by the ALB for immediate HTTPS functionality

set -e  # Exit on any error

# Configuration
REGION="us-west-2"
DOMAIN="*.${REGION}.elb.amazonaws.com"
KEY_FILE="wildcard-elb.key"
CERT_FILE="wildcard-elb.crt"
VALIDITY_DAYS=3650  # 10 years

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AWS ALB Wildcard Certificate Generator ===${NC}"
echo "Domain: ${DOMAIN}"
echo "Region: ${REGION}"
echo "Validity: ${VALIDITY_DAYS} days (~10 years)"
echo ""

# Check if OpenSSL is available
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}Error: OpenSSL is not installed or not in PATH${NC}"
    echo "Please install OpenSSL to continue"
    exit 1
fi

# Get script directory (where certificates should be created)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"
echo ""

# Backup existing certificates if they exist
if [ -f "$KEY_FILE" ] || [ -f "$CERT_FILE" ]; then
    echo -e "${YELLOW}Backing up existing certificates...${NC}"
    BACKUP_SUFFIX=$(date +"%Y%m%d_%H%M%S")
    
    if [ -f "$KEY_FILE" ]; then
        cp "$KEY_FILE" "${KEY_FILE}.bak.${BACKUP_SUFFIX}"
        echo "Backed up: ${KEY_FILE} → ${KEY_FILE}.bak.${BACKUP_SUFFIX}"
    fi
    
    if [ -f "$CERT_FILE" ]; then
        cp "$CERT_FILE" "${CERT_FILE}.bak.${BACKUP_SUFFIX}"
        echo "Backed up: ${CERT_FILE} → ${CERT_FILE}.bak.${BACKUP_SUFFIX}"
    fi
    echo ""
fi

# Generate private key
echo -e "${GREEN}Generating private key...${NC}"
openssl genrsa -out "$KEY_FILE" 2048

if [ $? -eq 0 ]; then
    echo "✓ Private key generated: $KEY_FILE"
else
    echo -e "${RED}✗ Failed to generate private key${NC}"
    exit 1
fi

# Generate self-signed certificate
echo -e "${GREEN}Generating self-signed certificate...${NC}"
openssl req -new -x509 -key "$KEY_FILE" -out "$CERT_FILE" -days "$VALIDITY_DAYS" -subj "/C=US/ST=California/L=Irvine/O=UCI/OU=RCS3/CN=${DOMAIN}" -extensions v3_req -config <(
cat <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${DOMAIN}
DNS.2 = ${REGION}.elb.amazonaws.com
EOF
)

if [ $? -eq 0 ]; then
    echo "✓ Certificate generated: $CERT_FILE"
else
    echo -e "${RED}✗ Failed to generate certificate${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Certificate Generation Complete ===${NC}"

# Display certificate information
echo -e "${YELLOW}Certificate Details:${NC}"
openssl x509 -in "$CERT_FILE" -text -noout | grep -A 2 "Subject:"
openssl x509 -in "$CERT_FILE" -text -noout | grep -A 5 "Subject Alternative Name:"
openssl x509 -in "$CERT_FILE" -text -noout | grep -A 2 "Validity"

echo ""
echo -e "${GREEN}Files created:${NC}"
echo "  Private Key: $(pwd)/$KEY_FILE"
echo "  Certificate: $(pwd)/$CERT_FILE"

echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. These certificates are ready for use with Terraform"
echo "2. Run 'terraform plan' to see if Terraform detects any changes"
echo "3. If deploying to a different region, modify REGION variable and re-run"
echo ""
echo -e "${GREEN}✓ Certificate generation completed successfully!${NC}"
