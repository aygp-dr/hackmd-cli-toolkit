#!/usr/bin/env python3
"""
Quick HackMD auth login implementation for testing.
"""

import os
import sys
import json
from pathlib import Path
from getpass import getpass

def auth_login():
    """Simple auth login for HackMD API token."""
    print("HackMD CLI - Authentication")
    print("-" * 40)

    # Get token interactively
    token = getpass("Enter your HackMD API token: ")

    if not token.strip():
        print("✗ Error: Token cannot be empty")
        sys.exit(1)

    # Create config directory
    config_dir = Path.home() / ".config" / "hackmd"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Save token to config file (simplified - in production would use keyring)
    config_file = config_dir / "config.json"

    config = {}
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)

    config['api_token'] = token
    config['api_base_url'] = 'https://api.hackmd.io/v1'

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    # Set restrictive permissions
    os.chmod(config_file, 0o600)

    print("✓ Authentication successful")
    print(f"✓ Token saved to {config_file}")
    print("\nYou can now use hackmd commands:")
    print("  hackmd note list")
    print("  hackmd note create --title 'My Note'")

    return token

def test_token(token):
    """Test the token by making a simple API call."""
    import requests

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    try:
        response = requests.get('https://api.hackmd.io/v1/me', headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"\n✓ Logged in as: {user.get('name', 'Unknown')}")
            print(f"  Email: {user.get('email', 'N/A')}")
            return True
        elif response.status_code == 401:
            print("\n✗ Error: Invalid token - authentication failed")
            return False
        else:
            print(f"\n⚠ Warning: Unexpected response ({response.status_code})")
            return False
    except Exception as e:
        print(f"\n⚠ Could not verify token: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("  HackMD CLI Toolkit - Authentication Setup")
    print("=" * 50)
    print()
    print("Get your API token from: https://hackmd.io/settings#api")
    print()

    token = auth_login()

    # Try to verify the token
    print("\nVerifying token...")
    test_token(token)