"""Template management for HackMD CLI."""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

TEMPLATES_DIR = Path.home() / ".hackmd" / "templates"

DEFAULT_TEMPLATES = {
    "daily-journal.md": """# Daily Journal - {{date}}

## Morning Intention
- [ ] Primary focus:
- [ ] Energy level (1-10):
- [ ] Gratitude:

## Time Blocks
### 9:00-12:00 (Deep Work)
-

### 12:00-13:00 (Lunch/Break)
-

### 13:00-17:00 (Meetings/Collaboration)
-

### 17:00-18:00 (Wrap-up)
-

## Accomplished Today
-

## Challenges Faced
-

## Learning & Insights
-

## Tomorrow's Priority
-

## Evening Reflection
- What went well?
- What could improve?
- Energy level (1-10):

---
Tags: #journal #daily #{{month}} #{{year}}""",

    "meeting-notes.md": """# Meeting: {{title}}

**Date:** {{date}}
**Time:** {{time}}
**Attendees:** {{attendees}}
**Meeting Type:** {{type}}

## Agenda
1. {{agenda_item_1}}
2. {{agenda_item_2}}
3. {{agenda_item_3}}

## Discussion Notes

### Topic 1: {{topic}}
**Discussion:**
-

**Decision:**
-

## Action Items
| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| | | | [ ] |

## Key Decisions
1.

## Next Steps
-

---
Tags: #meeting #{{project}} #{{team}}""",

    "bug-report.md": """# Bug Report: {{title}}

**Reported By:** {{reporter}}
**Date:** {{date}}
**Severity:** {{severity}}
**Priority:** {{priority}}

## Summary
Brief description of the issue

## Environment
- **OS:** {{os}}
- **Browser/App:** {{browser}}
- **Version:** {{version}}

## Steps to Reproduce
1.
2.
3.

## Expected Behavior
What should happen:

## Actual Behavior
What actually happens:

## Screenshots/Logs
```
[Paste error logs here]
```

---
Tags: #bug #{{component}} #{{severity}}""",

    "project-readme.md": """# {{project_name}}

[![License](https://img.shields.io/badge/license-{{license}}-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-{{version}}-green.svg)](CHANGELOG.md)

## Overview
{{brief_description}}

## Features
- 🚀 {{feature_1}}
- 💡 {{feature_2}}
- 🔧 {{feature_3}}

## Quick Start

### Installation
```bash
{{installation_command}}
```

### Basic Usage
```bash
{{usage_example}}
```

## Documentation
- [User Guide](docs/USER_GUIDE.md)
- [API Reference](docs/API.md)

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md)

## License
{{license}} - see [LICENSE](LICENSE)

---
Tags: #project #{{language}} #{{category}}""",

    "weekly-review.md": """# Weekly Review - Week {{week_number}}, {{year}}

## Week Overview
**Dates:** {{start_date}} - {{end_date}}

## Accomplishments
### Professional
-

### Personal
-

## Challenges & Lessons
-

## Next Week's Priorities
1.
2.
3.

## Metrics
- Tasks completed: X/Y
- Focus time: X hours
- Meeting time: X hours

## Reflection
-

---
Tags: #weekly-review #{{month}} #{{year}}"""
}


def initialize_templates():
    """Initialize the templates directory with default templates."""
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    created = []
    for filename, content in DEFAULT_TEMPLATES.items():
        template_path = TEMPLATES_DIR / filename
        if not template_path.exists():
            template_path.write_text(content)
            created.append(filename)

    return created


def list_templates() -> list:
    """List all available templates."""
    if not TEMPLATES_DIR.exists():
        return []

    return [f.stem for f in TEMPLATES_DIR.glob("*.md")]


def get_template(name: str) -> Optional[str]:
    """Get template content by name."""
    template_file = TEMPLATES_DIR / f"{name}.md"
    if not template_file.exists():
        return None

    return template_file.read_text()


def render_template(name: str, variables: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Render a template with variables replaced."""
    content = get_template(name)
    if not content:
        return None

    # Default variables
    now = datetime.now()
    default_vars = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "month": now.strftime("%B"),
        "year": str(now.year),
        "week_number": str(now.isocalendar()[1]),
        "start_date": "",
        "end_date": "",
    }

    # Merge with provided variables
    if variables:
        default_vars.update(variables)

    # Replace all placeholders
    for key, value in default_vars.items():
        content = content.replace(f"{{{{{key}}}}}", value)

    return content


def save_template(name: str, content: str) -> Path:
    """Save a new or update an existing template."""
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    template_path = TEMPLATES_DIR / f"{name}.md"
    template_path.write_text(content)
    return template_path