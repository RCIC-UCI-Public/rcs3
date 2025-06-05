#!/usr/bin/env zsh
# Script to automate the addition of users to Grafana teams and grant admin privileges

# Change to the script directory
cd "$(dirname "$0")"

# Check if environment parameter is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <environment>"
    echo "Example: $0 dev"
    echo "Example: $0 prod"
    exit 1
fi

ENVIRONMENT="$1"
CONFIG_FILE="../terraform/config/terraform.${ENVIRONMENT}.tfvars"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file '$CONFIG_FILE' not found."
    echo "Make sure terraform.${ENVIRONMENT}.tfvars exists in ../terraform/config/"
    exit 1
fi

echo "Using configuration file: $CONFIG_FILE"

# Check for required Python packages and install if missing
echo "Checking for required Python packages..."
if ! python3 -c "import requests" 2>/dev/null; then
  echo "Installing required Python package 'requests'..."
  pip3 install requests || {
    echo "Failed to install 'requests' package. Please install it manually with:"
    echo "pip3 install requests"
    exit 1
  }
  echo "Package installed successfully."
fi

# Check if password is in config file
if grep -q "^grafana_password = " "$CONFIG_FILE"; then
    echo "Using Grafana password from config file."
    echo "Processing team memberships and admin privileges..."
    # Execute the Python script without prompting for password
    python3 add_team_members.py --config-file="$CONFIG_FILE" --admin-password="$(grep '^grafana_password = ' "$CONFIG_FILE" | cut -d'"' -f2)"
else
    # Ask for password if not in config file
    echo "Enter Grafana admin password:"
    read -s ADMIN_PASSWORD
    
    echo "Processing team memberships and admin privileges..."
    # Execute the Python script with password
    python3 add_team_members.py \
      --config-file="$CONFIG_FILE" \
      --admin-password="$ADMIN_PASSWORD"
fi

echo "Script execution complete."
