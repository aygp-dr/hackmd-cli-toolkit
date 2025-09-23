"""Test CLI commands."""

import pytest
from click.testing import CliRunner
from hackmd.cli import cli


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "HackMD CLI" in result.output


def test_auth_help():
    """Test auth subcommand help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["auth", "--help"])
    assert result.exit_code == 0
    assert "Manage authentication" in result.output


def test_note_help():
    """Test note subcommand help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["note", "--help"])
    assert result.exit_code == 0
    assert "Manage notes" in result.output


def test_team_help():
    """Test team subcommand help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["team", "--help"])
    assert result.exit_code == 0
    assert "Manage teams" in result.output


def test_config_help():
    """Test config subcommand help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "--help"])
    assert result.exit_code == 0
    assert "Manage configuration" in result.output


def test_template_help():
    """Test template subcommand help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["template", "--help"])
    assert result.exit_code == 0
    assert "Manage note templates" in result.output


def test_template_list():
    """Test template list command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["template", "list"])
    assert result.exit_code == 0
    # Should show available templates
    assert "daily-journal" in result.output or "No templates found" in result.output
