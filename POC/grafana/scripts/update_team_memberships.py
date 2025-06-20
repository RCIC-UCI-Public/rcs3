#!/usr/bin/env python3
"""
Grafana Team Membership Manager

A consolidated script to automate the addition of users to Grafana teams and grant admin privileges.
Replaces the previous shell script wrapper for better cross-platform compatibility.

Usage: python3 update_team_memberships.py <environment>
Example: python3 update_team_memberships.py dev
Example: python3 update_team_memberships.py prod
"""

import argparse
import getpass
import json
import os
import sys
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_dependencies():
    """Check for required Python packages."""
    print("Checking for required Python packages...")
    missing_packages = []
    
    try:
        import requests
        print("✓ requests package available.")
    except ImportError:
        missing_packages.append("requests")
    
    try:
        import hcl2
        print("✓ python-hcl2 package available.")
    except ImportError:
        missing_packages.append("python-hcl2")
    
    if missing_packages:
        print(f"✗ Missing required packages: {', '.join(missing_packages)}")
        print("\nPlease install dependencies with:")
        print("  pip install -r requirements.txt")
        print("\nOr install manually:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    
    print("✓ All required packages are available.")
    return True

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Add members to Grafana teams and grant admin privileges.',
        epilog='Example: python3 update_team_memberships.py dev'
    )
    parser.add_argument('environment', 
                       help='Environment name (e.g., dev, prod)')
    
    return parser.parse_args()

def get_config_file_path(environment):
    """Construct the configuration file path based on environment."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, "..", "terraform", "config", f"terraform.{environment}.tfvars")
    return os.path.normpath(config_file)

def check_config_file(config_file):
    """Check if configuration file exists."""
    if not os.path.isfile(config_file):
        print(f"✗ Error: Configuration file '{config_file}' not found.")
        print(f"Make sure terraform.{os.path.basename(config_file).split('.')[1]}.tfvars exists in ../terraform/config/")
        return False
    print(f"✓ Using configuration file: {config_file}")
    return True

def parse_terraform_config(config_file):
    """Parse terraform configuration file using proper HCL parser."""
    import hcl2
    
    print(f"Reading configuration from {config_file}...")
    try:
        with open(config_file, 'r') as f:
            config = hcl2.load(f)
        print("✓ Successfully parsed HCL configuration")
        return config
    except Exception as e:
        print(f"✗ Error parsing HCL configuration: {e}")
        print("Please check the syntax of your terraform configuration file.")
        return None

def extract_teams_config(config):
    """Extract team configuration from parsed HCL."""
    if not config:
        return {}
    
    bucket_teams = config.get('bucket_teams', {})
    if not bucket_teams:
        print("No bucket_teams configuration found.")
        return {}
    
    print(f"✓ Found {len(bucket_teams)} team(s) in configuration:")
    for team_name, team_config in bucket_teams.items():
        members = team_config.get('members', [])
        buckets = team_config.get('buckets', [])
        print(f"  - {team_name}: {len(members)} member(s), {len(buckets)} bucket(s)")
        print(f"    Members: {members}")
        print(f"    Buckets: {buckets}")
    
    return bucket_teams

def extract_grafana_config(config):
    """Extract Grafana configuration from parsed HCL."""
    if not config:
        return {}
    
    grafana_config = {}
    
    # Extract grafana configuration values
    if 'grafana_url' in config:
        grafana_config['url'] = config['grafana_url']
    
    if 'grafana_username' in config:
        grafana_config['username'] = config['grafana_username']
    
    if 'grafana_password' in config:
        grafana_config['password'] = config['grafana_password']
    
    return grafana_config

def extract_admin_users(config):
    """Extract admin users list from parsed HCL."""
    if not config:
        return []
    
    admin_users = config.get('admin_users', [])
    if admin_users:
        print(f"✓ Found {len(admin_users)} admin user(s): {admin_users}")
    
    return admin_users

def get_admin_password(grafana_config):
    """Get admin password from config or prompt user."""
    if 'password' in grafana_config:
        print("✓ Using Grafana password from config file.")
        return grafana_config['password']
    else:
        print("\nGrafana admin password not found in config file.")
        return getpass.getpass("Enter Grafana admin password: ")

def get_grafana_session(grafana_url, admin_user, admin_password):
    """Create a session for Grafana API requests."""
    import requests
    
    session = requests.Session()
    session.auth = (admin_user, admin_password)
    # Disable SSL verification for self-signed certificates
    session.verify = False
    
    # Test connection and authentication
    try:
        response = session.get(f"{grafana_url}/api/org")
        if response.status_code != 200:
            print(f"✗ Authentication failed: {response.status_code}")
            if response.status_code == 401:
                print("  Check your admin username and password.")
            sys.exit(1)
        print("✓ Successfully connected to Grafana API.")
    except requests.RequestException as e:
        print(f"✗ Error connecting to Grafana: {e}")
        sys.exit(1)
        
    return session

def get_teams(session, grafana_url):
    """Get all teams from Grafana."""
    import requests
    
    try:
        response = session.get(f"{grafana_url}/api/teams/search?perpage=100")
        if response.status_code != 200:
            print(f"✗ Failed to get teams: {response.status_code}")
            return {}
        
        teams_data = response.json()
        print(f"✓ Found {len(teams_data.get('teams', []))} teams in Grafana:")
        for team in teams_data.get('teams', []):
            print(f"  - {team['name']} (ID: {team['id']})")
        
        # Create a case-insensitive mapping and a regular mapping
        teams_map = {team['name']: team['id'] for team in teams_data.get('teams', [])}
        teams_map_lower = {team['name'].lower(): team['id'] for team in teams_data.get('teams', [])}
        
        return {'exact': teams_map, 'lower': teams_map_lower}
    except requests.RequestException as e:
        print(f"✗ Error getting teams: {e}")
        return {'exact': {}, 'lower': {}}

def get_users(session, grafana_url):
    """Get all users from Grafana."""
    import requests
    
    try:
        response = session.get(f"{grafana_url}/api/users")
        if response.status_code != 200:
            print(f"✗ Failed to get users: {response.status_code}")
            return {}
        
        users_data = response.json()
        print(f"✓ Found {len(users_data)} users in Grafana.")
        return {user['login']: user['id'] for user in users_data}
    except requests.RequestException as e:
        print(f"✗ Error getting users: {e}")
        return {}

def get_team_members(session, grafana_url, team_id):
    """Get existing team members."""
    import requests
    
    try:
        response = session.get(f"{grafana_url}/api/teams/{team_id}/members")
        if response.status_code != 200:
            print(f"✗ Failed to get team members: {response.status_code}")
            return []
        
        members_data = response.json()
        return [member['userId'] for member in members_data]
    except requests.RequestException as e:
        print(f"✗ Error getting team members: {e}")
        return []

def add_user_to_team(session, grafana_url, team_id, user_id):
    """Add a user to a team."""
    import requests
    
    try:
        response = session.post(
            f"{grafana_url}/api/teams/{team_id}/members",
            json={"userId": user_id}
        )
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"✗ Error adding user to team: {e}")
        return False

def get_user_permissions(session, grafana_url, user_id):
    """Get current permissions for a user."""
    import requests
    
    try:
        response = session.get(f"{grafana_url}/api/orgs/1/users/{user_id}")
        if response.status_code != 200:
            print(f"✗ Failed to get user permissions: {response.status_code}")
            return None
        
        user_data = response.json()
        return user_data.get('role', 'Viewer')
    except requests.RequestException as e:
        print(f"✗ Error getting user permissions: {e}")
        return None

def set_user_admin_privileges(session, grafana_url, user_id):
    """Set admin privileges for a user."""
    import requests
    
    try:
        # Update the user's role to Admin
        response = session.patch(
            f"{grafana_url}/api/orgs/1/users/{user_id}",
            json={"role": "Admin"}
        )
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"✗ Error setting admin privileges: {e}")
        return False

def process_teams(session, grafana_url, teams_config, teams, users):
    """Process team memberships."""
    if not teams_config:
        print("No team configuration found.")
        return
    
    print(f"\n📋 Processing {len(teams_config)} team(s)...")
    
    for team_name, team_config in teams_config.items():
        # Try exact match first, then case-insensitive match
        team_id = None
        
        if team_name in teams['exact']:
            team_id = teams['exact'][team_name]
        elif team_name.lower() in teams['lower']:
            team_id = teams['lower'][team_name.lower()]
            print(f"  ℹ️  Found team '{team_name}' using case-insensitive match")
        else:
            print(f"  ✗ Team '{team_name}' not found in Grafana. Available teams: {list(teams['exact'].keys())}. Skipping.")
            continue
            
        existing_members = get_team_members(session, grafana_url, team_id)
        
        print(f"\n  �� Processing team '{team_name}' (ID: {team_id}):")
        
        members_processed = 0
        for member in team_config.get('members', []):
            if member not in users:
                print(f"    ✗ User '{member}' not found in Grafana. Skipping.")
                continue
                
            user_id = users[member]
            
            if user_id in existing_members:
                print(f"    ✓ User '{member}' already in team. Skipping.")
                continue
                
            print(f"    ➕ Adding user '{member}' (ID: {user_id}) to team...")
            success = add_user_to_team(session, grafana_url, team_id, user_id)
            
            if success:
                print(f"    ✅ Successfully added user '{member}' to team.")
                members_processed += 1
            else:
                print(f"    ✗ Failed to add user '{member}' to team.")
        
        print(f"  📊 Team '{team_name}': {members_processed} member(s) processed.")

def process_admin_users(session, grafana_url, admin_users, users):
    """Process admin users and grant them admin privileges."""
    if not admin_users:
        print("No admin users specified in configuration.")
        return
    
    print(f"\n🔑 Processing {len(admin_users)} admin user(s)...")
    
    admin_processed = 0
    for admin_user in admin_users:
        if admin_user not in users:
            print(f"  ✗ Admin user '{admin_user}' not found in Grafana. Skipping.")
            continue
            
        user_id = users[admin_user]
        current_role = get_user_permissions(session, grafana_url, user_id)
        
        if current_role == 'Admin':
            print(f"  ✓ User '{admin_user}' already has Admin role. Skipping.")
            continue
            
        print(f"  🛡️  Granting Admin privileges to user '{admin_user}' (ID: {user_id})...")
        success = set_user_admin_privileges(session, grafana_url, user_id)
        
        if success:
            print(f"  ✅ Successfully granted Admin privileges to '{admin_user}'.")
            admin_processed += 1
        else:
            print(f"  ✗ Failed to grant Admin privileges to '{admin_user}'.")
    
    print(f"📊 Admin privileges: {admin_processed} user(s) processed.")

def main():
    """Main entry point."""
    print("🚀 Grafana Team Membership Manager")
    print("🔒 SSL verification disabled for self-signed certificates")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Parse arguments
    args = parse_args()
    environment = args.environment
    
    # Construct and check config file path
    config_file = get_config_file_path(environment)
    if not check_config_file(config_file):
        sys.exit(1)
    
    # Parse HCL configuration
    print(f"\n📖 Reading configuration for environment: {environment}")
    config = parse_terraform_config(config_file)
    if not config:
        sys.exit(1)
    
    # Extract configurations from parsed HCL
    grafana_config = extract_grafana_config(config)
    teams_config = extract_teams_config(config)
    admin_users = extract_admin_users(config)
    
    # Validate Grafana configuration
    if not grafana_config.get('url') or not grafana_config.get('username'):
        print("✗ Error: Missing required Grafana configuration (grafana_url, grafana_username) in config file.")
        sys.exit(1)
    
    # Check if we have something to do
    if not teams_config and not admin_users:
        print("✗ No team configuration or admin users found. Check the format of your config file.")
        sys.exit(1)
    
    print(f"✓ Configuration summary:")
    print(f"  - Grafana URL: {grafana_config['url']}")
    print(f"  - Admin username: {grafana_config['username']}")
    if teams_config:
        print(f"  - Teams configured: {len(teams_config)}")
    if admin_users:
        print(f"  - Admin users configured: {len(admin_users)}")
    
    # Get admin password
    admin_password = get_admin_password(grafana_config)
    
    # Connect to Grafana API
    print(f"\n🔗 Connecting to Grafana at {grafana_config['url']}...")
    session = get_grafana_session(grafana_config['url'], grafana_config['username'], admin_password)
    
    # Get existing teams and users
    print("\n📋 Fetching existing Grafana data...")
    teams = get_teams(session, grafana_config['url'])
    users = get_users(session, grafana_config['url'])
    
    # Process teams
    if teams_config:
        process_teams(session, grafana_config['url'], teams_config, teams, users)
    
    # Process admin users
    if admin_users:
        process_admin_users(session, grafana_config['url'], admin_users, users)
    
    print("\n🎉 All operations completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
