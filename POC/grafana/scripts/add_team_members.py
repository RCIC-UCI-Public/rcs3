#!/usr/bin/env python3
"""
Script to add members to Grafana teams based on configuration.
Uses the Grafana API to add users to their respective teams and grant admin privileges.
"""

import argparse
import json
import os
import re
import requests
import sys

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Add members to Grafana teams and grant admin privileges.')
    parser.add_argument('--config-file', required=True, help='Path to terraform tfvars file containing grafana and teams config')
    parser.add_argument('--admin-password', required=True, help='Grafana admin password')
    
    return parser.parse_args()

def extract_teams_config(config_file):
    """Extract team configuration from tfvars file."""
    teams_config = {}
    
    print(f"Opening file: {config_file}")
    # Simple parser for tfvars format - for production use, consider a proper HCL parser
    with open(config_file, 'r') as f:
        content = f.read()
    
    print(f"File content length: {len(content)} characters")
    
    # Extract bucket_teams section using a simple approach
    if 'bucket_teams = {' in content:
        print("Found bucket_teams section")
        teams_section = content.split('bucket_teams = {')[1]
        # Find the matching closing brace by counting braces
        brace_count = 1
        close_pos = 0
        for i, char in enumerate(teams_section):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    close_pos = i
                    break
        
        teams_section = teams_section[:close_pos]
        print(f"Extracted teams section: {teams_section}")
        
        # Parse each team
        current_team = None
        team_content = ""
        
        # Split the content into lines for easier processing
        lines = teams_section.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for team definitions (e.g., "Team name" = {)
            if '"' in line and '=' in line and '{' in line:
                # Extract team name
                parts = line.split('=', 1)
                name_part = parts[0].strip()
                if name_part.startswith('"') and name_part.endswith('"'):
                    current_team = name_part[1:-1]  # Remove quotes
                    teams_config[current_team] = {'members': []}
                    print(f"Found team: {current_team}")
                
            # Look for member definitions
            if current_team and 'members = [' in line:
                members_text = line
                # If the members definition spans multiple lines
                while ']' not in members_text and i < len(lines) - 1:
                    i += 1
                    members_text += lines[i]
                
                # Extract member names
                if 'members = [' in members_text and ']' in members_text:
                    members_str = members_text.split('members = [')[1].split(']')[0]
                    members = []
                    for m in members_str.split(','):
                        m = m.strip().strip('"')
                        if m:  # Only add non-empty strings
                            members.append(m)
                    
                    teams_config[current_team]['members'] = members
                    print(f"Team {current_team} members: {members}")
            
            # Look for buckets definitions
            if current_team and 'buckets = [' in line:
                buckets_text = line
                # If the buckets definition spans multiple lines
                while ']' not in buckets_text and i < len(lines) - 1:
                    i += 1
                    buckets_text += lines[i]
                
                # Extract bucket names
                if 'buckets = [' in buckets_text and ']' in buckets_text:
                    buckets_str = buckets_text.split('buckets = [')[1].split(']')[0]
                    buckets = []
                    for b in buckets_str.split(','):
                        b = b.strip().strip('"')
                        if b:  # Only add non-empty strings
                            buckets.append(b)
                    
                    teams_config[current_team]['buckets'] = buckets
            
            i += 1
    
    print(f"Extracted configuration: {json.dumps(teams_config, indent=2)}")
    return teams_config

def extract_grafana_config(config_file):
    """Extract Grafana configuration from tfvars file."""
    grafana_config = {}
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Extract grafana configuration values using regex to handle whitespace
    for line in content.split('\n'):
        line = line.strip()
        
        # Extract grafana_url (handle variable whitespace around =)
        url_match = re.match(r'grafana_url\s*=\s*"([^"]*)"', line)
        if url_match:
            grafana_config['url'] = url_match.group(1)
            
        # Extract grafana_username (handle variable whitespace around =)
        username_match = re.match(r'grafana_username\s*=\s*"([^"]*)"', line)
        if username_match:
            grafana_config['username'] = username_match.group(1)
            
        # Extract grafana_password (handle variable whitespace around =)
        password_match = re.match(r'grafana_password\s*=\s*"([^"]*)"', line)
        if password_match:
            grafana_config['password'] = password_match.group(1)
    
    print(f"Extracted Grafana config: {grafana_config}")
    return grafana_config

def extract_admin_users(config_file):
    """Extract admin users list from tfvars file."""
    admin_users = []
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Look for admin_users definition
    if 'admin_users = [' in content:
        admin_section = content.split('admin_users = [')[1]
        # Find the closing bracket
        close_pos = admin_section.find(']')
        if close_pos != -1:
            admin_section = admin_section[:close_pos]
            
            # Parse admin usernames
            for user in admin_section.split(','):
                user = user.strip().strip('"')
                if user:  # Only add non-empty strings
                    admin_users.append(user)
    
    print(f"Extracted admin users: {admin_users}")
    return admin_users

def get_grafana_session(grafana_url, admin_user, admin_password):
    """Create a session for Grafana API requests."""
    session = requests.Session()
    session.auth = (admin_user, admin_password)
    
    # Test connection and authentication
    try:
        response = session.get(f"{grafana_url}/api/org")
        if response.status_code != 200:
            print(f"Authentication failed: {response.status_code}")
            sys.exit(1)
    except requests.RequestException as e:
        print(f"Error connecting to Grafana: {e}")
        sys.exit(1)
        
    return session

def get_teams(session, grafana_url):
    """Get all teams from Grafana."""
    try:
        response = session.get(f"{grafana_url}/api/teams/search?perpage=100")
        if response.status_code != 200:
            print(f"Failed to get teams: {response.status_code}")
            return {}
        
        teams_data = response.json()
        # Print teams found in Grafana for debugging
        print("Teams found in Grafana:")
        for team in teams_data.get('teams', []):
            print(f"  - {team['name']} (ID: {team['id']})")
        
        # Create a case-insensitive mapping and a regular mapping
        teams_map = {team['name']: team['id'] for team in teams_data.get('teams', [])}
        teams_map_lower = {team['name'].lower(): team['id'] for team in teams_data.get('teams', [])}
        
        return {'exact': teams_map, 'lower': teams_map_lower}
    except requests.RequestException as e:
        print(f"Error getting teams: {e}")
        return {'exact': {}, 'lower': {}}

def get_users(session, grafana_url):
    """Get all users from Grafana."""
    try:
        response = session.get(f"{grafana_url}/api/users")
        if response.status_code != 200:
            print(f"Failed to get users: {response.status_code}")
            return {}
        
        users_data = response.json()
        return {user['login']: user['id'] for user in users_data}
    except requests.RequestException as e:
        print(f"Error getting users: {e}")
        return {}

def get_team_members(session, grafana_url, team_id):
    """Get existing team members."""
    try:
        response = session.get(f"{grafana_url}/api/teams/{team_id}/members")
        if response.status_code != 200:
            print(f"Failed to get team members: {response.status_code}")
            return []
        
        members_data = response.json()
        return [member['userId'] for member in members_data]
    except requests.RequestException as e:
        print(f"Error getting team members: {e}")
        return []

def add_user_to_team(session, grafana_url, team_id, user_id):
    """Add a user to a team."""
    try:
        response = session.post(
            f"{grafana_url}/api/teams/{team_id}/members",
            json={"userId": user_id}
        )
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error adding user to team: {e}")
        return False

def get_user_permissions(session, grafana_url, user_id):
    """Get current permissions for a user."""
    try:
        response = session.get(f"{grafana_url}/api/orgs/1/users/{user_id}")
        if response.status_code != 200:
            print(f"Failed to get user permissions: {response.status_code}")
            return None
        
        user_data = response.json()
        return user_data.get('role', 'Viewer')
    except requests.RequestException as e:
        print(f"Error getting user permissions: {e}")
        return None

def set_user_admin_privileges(session, grafana_url, user_id):
    """Set admin privileges for a user."""
    try:
        # Update the user's role to Admin
        response = session.patch(
            f"{grafana_url}/api/orgs/1/users/{user_id}",
            json={"role": "Admin"}
        )
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Error setting admin privileges: {e}")
        return False

def process_admin_users(session, grafana_url, admin_users, users):
    """Process admin users and grant them admin privileges."""
    if not admin_users:
        print("No admin users specified in configuration.")
        return
    
    print(f"\nProcessing {len(admin_users)} admin users...")
    
    for admin_user in admin_users:
        if admin_user not in users:
            print(f"  - Admin user '{admin_user}' not found in Grafana. Skipping.")
            continue
            
        user_id = users[admin_user]
        current_role = get_user_permissions(session, grafana_url, user_id)
        
        if current_role == 'Admin':
            print(f"  - User '{admin_user}' already has Admin role. Skipping.")
            continue
            
        print(f"  - Granting Admin privileges to user '{admin_user}' (ID: {user_id})...")
        success = set_user_admin_privileges(session, grafana_url, user_id)
        
        if success:
            print(f"  - Successfully granted Admin privileges to '{admin_user}'.")
        else:
            print(f"  - Failed to grant Admin privileges to '{admin_user}'.")

def main():
    """Main entry point."""
    args = parse_args()
    
    # Extract Grafana configuration
    print(f"Reading Grafana configuration from {args.config_file}...")
    grafana_config = extract_grafana_config(args.config_file)
    
    if not grafana_config.get('url') or not grafana_config.get('username'):
        print("Error: Missing required Grafana configuration (grafana_url, grafana_username) in config file.")
        sys.exit(1)
    
    # Use password from command line argument (interactive prompt)
    admin_password = args.admin_password
    
    # Extract team configuration
    print(f"Reading team configuration from {args.config_file}...")
    teams_config = extract_teams_config(args.config_file)
    
    # Extract admin users configuration
    print(f"Reading admin users configuration from {args.config_file}...")
    admin_users = extract_admin_users(args.config_file)
    
    if not teams_config and not admin_users:
        print("No team configuration or admin users found. Check the format of your config file.")
        sys.exit(1)
    
    if teams_config:
        print(f"Found {len(teams_config)} teams in configuration.")
    if admin_users:
        print(f"Found {len(admin_users)} admin users in configuration.")
    
    # Connect to Grafana API
    print(f"Connecting to Grafana at {grafana_config['url']}...")
    session = get_grafana_session(grafana_config['url'], grafana_config['username'], admin_password)
    
    # Get existing teams and users
    print("Fetching existing teams and users...")
    teams = get_teams(session, grafana_config['url'])
    users = get_users(session, grafana_config['url'])
    
    print(f"Found {len(teams['exact'])} teams and {len(users)} users in Grafana.")
    
    # Add users to teams
    if teams_config:
        for team_name, team_config in teams_config.items():
            # Try exact match first, then case-insensitive match
            team_id = None
            
            if team_name in teams['exact']:
                team_id = teams['exact'][team_name]
            elif team_name.lower() in teams['lower']:
                team_id = teams['lower'][team_name.lower()]
                print(f"Found team '{team_name}' using case-insensitive match")
            else:
                print(f"Team '{team_name}' not found in Grafana. Available teams: {list(teams['exact'].keys())}. Skipping.")
                continue
                
            existing_members = get_team_members(session, grafana_config['url'], team_id)
            
            print(f"\nProcessing team '{team_name}' (ID: {team_id}):")
            
            for member in team_config.get('members', []):
                if member not in users:
                    print(f"  - User '{member}' not found in Grafana. Skipping.")
                    continue
                    
                user_id = users[member]
                
                if user_id in existing_members:
                    print(f"  - User '{member}' already in team. Skipping.")
                    continue
                    
                print(f"  - Adding user '{member}' (ID: {user_id}) to team...")
                success = add_user_to_team(session, grafana_config['url'], team_id, user_id)
                
                if success:
                    print(f"  - Successfully added user '{member}' to team.")
                else:
                    print(f"  - Failed to add user '{member}' to team.")
        
        print("\nTeam membership setup complete.")
    
    # Process admin users
    if admin_users:
        process_admin_users(session, grafana_config['url'], admin_users, users)
        print("\nAdmin privileges setup complete.")
    
    print("\nAll operations completed.")

if __name__ == "__main__":
    main()
