# HackMD CLI Toolkit Makefile

.PHONY: all install dev test clean readme

all: readme install

# Convert README.org to README.md for Python packaging
README.md: README.org
	@echo "Converting $< to $@..."
	emacs --batch $< -f org-md-export-to-markdown --kill

readme: README.md

install: readme
	uv pip install -e .

dev: readme
	uv pip install -e ".[dev]"

test:
	pytest tests/

clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	rm -f README.md
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

run-auth:
	hackmd auth login

run-status:
	hackmd auth status

run-list:
	hackmd note list

.DEFAULT_GOAL := all