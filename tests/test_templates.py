"""Test template functionality."""

import pytest
from pathlib import Path
from hackmd import templates


def test_initialize_templates(tmp_path, monkeypatch):
    """Test template initialization."""
    # Use temporary directory for templates
    monkeypatch.setattr(templates, "TEMPLATES_DIR", tmp_path / "templates")

    # Initialize templates
    created = templates.initialize_templates()

    # Check that templates were created
    assert len(created) == 5
    assert "daily-journal.md" in created
    assert "meeting-notes.md" in created
    assert "bug-report.md" in created
    assert "project-readme.md" in created
    assert "weekly-review.md" in created

    # Check files exist
    for filename in created:
        assert (tmp_path / "templates" / filename).exists()


def test_list_templates(tmp_path, monkeypatch):
    """Test listing templates."""
    monkeypatch.setattr(templates, "TEMPLATES_DIR", tmp_path / "templates")

    # Before initialization
    assert templates.list_templates() == []

    # After initialization
    templates.initialize_templates()
    template_list = templates.list_templates()

    assert len(template_list) == 5
    assert "daily-journal" in template_list
    assert "meeting-notes" in template_list


def test_get_template(tmp_path, monkeypatch):
    """Test getting template content."""
    monkeypatch.setattr(templates, "TEMPLATES_DIR", tmp_path / "templates")

    # Initialize templates
    templates.initialize_templates()

    # Get existing template
    content = templates.get_template("daily-journal")
    assert content is not None
    assert "# Daily Journal" in content
    assert "{{date}}" in content

    # Get non-existent template
    content = templates.get_template("non-existent")
    assert content is None


def test_render_template(tmp_path, monkeypatch):
    """Test rendering template with variables."""
    monkeypatch.setattr(templates, "TEMPLATES_DIR", tmp_path / "templates")

    # Initialize templates
    templates.initialize_templates()

    # Render with custom variables
    variables = {"title": "Sprint Planning", "team": "Backend", "project": "API v2"}

    content = templates.render_template("meeting-notes", variables)
    assert content is not None
    assert "Sprint Planning" in content
    assert "Backend" in content
    assert "API v2" in content
    assert "{{title}}" not in content
    assert "{{team}}" not in content
    assert "{{project}}" not in content

    # Check that default date variables are included
    assert "{{date}}" not in content
    assert "{{time}}" not in content


def test_save_template(tmp_path, monkeypatch):
    """Test saving a new template."""
    monkeypatch.setattr(templates, "TEMPLATES_DIR", tmp_path / "templates")

    # Save new template
    content = "# Custom Template\n\n{{custom_var}}"
    path = templates.save_template("custom-template", content)

    assert path.exists()
    assert path.name == "custom-template.md"

    # Verify it can be loaded
    loaded = templates.get_template("custom-template")
    assert loaded == content
