#!/bin/bash

# Check if AWS CLI is already installed
if command -v aws &>/dev/null; then
    echo "AWS CLI is already installed."
    exit 0
fi

# Detect system architecture
arch=$(uname -m)

if [ "$arch" == "x86_64" ]; then
    package_url="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
elif [ "$arch" == "aarch64" ]; then
    package_url="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"
else
    echo "Unsupported architecture: $arch"
    exit 1
fi

# Download and install AWS CLI
echo "Downloading AWS CLI package..."
curl "$package_url" -o "awscliv2.zip"

echo "Unzipping package..."
unzip awscliv2.zip

echo "Installing AWS CLI..."
./aws/install

# Clean up
rm -f awscliv2.zip
rm -rf aws

echo "AWS CLI installation completed."
