#!/usr/bin/env python3
"""HackMD CLI main entry point."""

import click
import json
import sys
from pathlib import Path
from getpass import getpass

@click.group()
@click.version_option()
def cli():
    """HackMD CLI - Manage your HackMD notes from the terminal."""
    pass

@cli.group()
def auth():
    """Manage authentication."""
    pass

@auth.command()
@click.option('--token', help='API token (will prompt if not provided)')
@click.option('--profile', default='default', help='Profile name')
def login(token, profile):
    """Authenticate with HackMD API."""
    if not token:
        click.echo("HackMD CLI - Authentication")
        click.echo("-" * 40)
        token = getpass("Enter your HackMD API token: ")

    if not token.strip():
        click.echo("✗ Error: Token cannot be empty", err=True)
        sys.exit(1)

    # Create config directory
    config_dir = Path.home() / ".config" / "hackmd"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Save token to config file
    config_file = config_dir / "config.json"

    config = {}
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)

    if 'profiles' not in config:
        config['profiles'] = {}

    config['profiles'][profile] = {
        'api_token': token,
        'api_base_url': 'https://api.hackmd.io/v1'
    }
    config['active_profile'] = profile

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    # Set restrictive permissions
    import os
    os.chmod(config_file, 0o600)

    click.echo("✓ Authentication successful")
    click.echo(f"✓ Token saved to profile '{profile}'")

    # Test the token
    _verify_token(token)

@auth.command()
def status():
    """Show authentication status."""
    config_file = Path.home() / ".config" / "hackmd" / "config.json"

    if not config_file.exists():
        click.echo("✗ Not authenticated. Run: hackmd auth login", err=True)
        sys.exit(1)

    with open(config_file, 'r') as f:
        config = json.load(f)

    profile = config.get('active_profile', 'default')
    profiles = config.get('profiles', {})

    if profile in profiles:
        click.echo(f"✓ Authenticated")
        click.echo(f"  Active profile: {profile}")
        token = profiles[profile].get('api_token', '')
        if token:
            masked_token = token[:8] + '...' + token[-4:] if len(token) > 12 else '***'
            click.echo(f"  Token: {masked_token}")
            _verify_token(token)
    else:
        click.echo("✗ No active profile found", err=True)

@cli.group()
def team():
    """Manage teams."""
    pass

@team.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table', help='Output format')
def list(format):
    """List your teams."""
    config = _load_config()
    if not config:
        click.echo("✗ Not authenticated. Run: hackmd auth login", err=True)
        sys.exit(1)

    import requests
    token = config['api_token']
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get('https://api.hackmd.io/v1/teams', headers=headers)
        if response.status_code == 200:
            teams = response.json()

            if format == 'json':
                import json as json_lib
                click.echo(json_lib.dumps(teams, indent=2))
            else:  # table format
                if teams:
                    click.echo("Your teams:")
                    for team in teams:
                        name = team.get('name', 'Unknown')
                        path = team.get('path', '')
                        team_id = team.get('id', '')
                        click.echo(f"  • {name} (path: {path}, id: {team_id})")
                else:
                    click.echo("No teams found")
        else:
            click.echo(f"✗ Error fetching teams: {response.status_code}", err=True)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)

@cli.group()
def config():
    """Manage configuration."""
    pass

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a configuration value."""
    config_file = Path.home() / ".config" / "hackmd" / "config.json"

    if not config_file.exists():
        click.echo("✗ Not configured. Run: hackmd auth login", err=True)
        sys.exit(1)

    with open(config_file, 'r') as f:
        config = json.load(f)

    # Handle nested keys
    if key == 'default.team':
        if 'defaults' not in config:
            config['defaults'] = {}
        config['defaults']['team'] = value
        click.echo(f"✓ Set default team to: {value}")
    else:
        config[key] = value
        click.echo(f"✓ Set {key} to: {value}")

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    import os
    os.chmod(config_file, 0o600)

@cli.group()
def note():
    """Manage notes."""
    pass

@note.command()
@click.option('--title', '-t', required=True, help='Note title')
@click.option('--content', '-c', help='Note content')
def create(title, content):
    """Create a new note."""
    config = _load_config()
    if not config:
        click.echo("✗ Not authenticated. Run: hackmd auth login", err=True)
        sys.exit(1)

    import requests
    token = config['api_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    data = {
        'title': title,
        'content': content or f'# {title}\n\nCreated with HackMD CLI'
    }

    try:
        response = requests.post('https://api.hackmd.io/v1/notes', json=data, headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            note = response.json()
            note_id = note.get('id', 'unknown')
            click.echo(f"✓ Note created successfully!")
            click.echo(f"  ID: {note_id}")
            click.echo(f"  Title: {title}")
            if 'publishLink' in note:
                click.echo(f"  URL: {note['publishLink']}")
        else:
            click.echo(f"✗ Error creating note: {response.status_code}", err=True)
            if response.text:
                click.echo(f"  {response.text}", err=True)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)

@note.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'csv']), default='table', help='Output format')
@click.option('--limit', '-l', type=int, default=20, help='Maximum number of notes to show')
def list(format, limit):
    """List your notes."""
    config = _load_config()
    if not config:
        click.echo("✗ Not authenticated. Run: hackmd auth login", err=True)
        sys.exit(1)

    import requests
    token = config['api_token']
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get('https://api.hackmd.io/v1/notes', headers=headers)
        if response.status_code == 200:
            notes = response.json()

            if format == 'json':
                import json as json_lib
                click.echo(json_lib.dumps(notes[:limit], indent=2))
            elif format == 'csv':
                if notes:
                    click.echo("id,title,createdAt,lastChangedAt")
                    for note in notes[:limit]:
                        title = note.get('title', 'Untitled').replace(',', ';')
                        note_id = note.get('id', '')
                        created = note.get('createdAt', '')
                        updated = note.get('lastChangedAt', '')
                        click.echo(f"{note_id},{title},{created},{updated}")
            else:  # table format
                if notes:
                    click.echo("Your notes:")
                    for note in notes[:limit]:
                        title = note.get('title', 'Untitled')
                        note_id = note.get('id', 'unknown')
                        click.echo(f"  • {title} ({note_id})")
                else:
                    click.echo("No notes found")
        else:
            click.echo(f"✗ Error fetching notes: {response.status_code}", err=True)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)

def _load_config():
    """Load active profile configuration."""
    config_file = Path.home() / ".config" / "hackmd" / "config.json"
    if not config_file.exists():
        return None

    with open(config_file, 'r') as f:
        config = json.load(f)

    profile = config.get('active_profile', 'default')
    profiles = config.get('profiles', {})

    if profile in profiles:
        return profiles[profile]

    # Backward compatibility - check for old format
    if 'api_token' in config:
        return config

    return None

def _verify_token(token):
    """Verify token by calling /me endpoint."""
    import requests
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get('https://api.hackmd.io/v1/me', headers=headers)
        if response.status_code == 200:
            user = response.json()
            click.echo(f"\n✓ Logged in as: {user.get('name', 'Unknown')}")
            click.echo(f"  Email: {user.get('email', 'N/A')}")
            return True
        elif response.status_code == 401:
            click.echo("\n✗ Error: Invalid token", err=True)
            return False
        else:
            click.echo(f"\n⚠ Warning: Unexpected response ({response.status_code})", err=True)
            return False
    except Exception as e:
        click.echo(f"\n⚠ Could not verify token: {e}", err=True)
        return None

def main():
    """Main entry point."""
    cli()

if __name__ == '__main__':
    main()