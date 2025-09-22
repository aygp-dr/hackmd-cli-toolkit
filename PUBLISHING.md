# Publishing to PyPI

## Prerequisites

1. Create PyPI account at https://pypi.org/account/register/
2. Generate API token at https://pypi.org/manage/account/token/
3. Install build tools:
   ```bash
   pip install build twine
   ```

## Build Process

1. Clean previous builds:
   ```bash
   rm -rf dist/ build/ *.egg-info src/*.egg-info
   ```

2. Generate README.md from README.org:
   ```bash
   gmake readme
   ```

3. Build the package:
   ```bash
   python -m build
   ```

4. Check the distribution:
   ```bash
   twine check dist/*
   ```

## Publishing

### Test PyPI (Recommended First)

1. Upload to TestPyPI:
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. Test installation:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ hackmd-cli
   ```

### Production PyPI

1. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

2. Verify installation:
   ```bash
   pip install hackmd-cli
   ```

## Using uv for Publishing

With uv, you can also publish directly:

```bash
# Build
uv build

# Publish (requires UV_PUBLISH_TOKEN env var or interactive auth)
uv publish
```

## GitHub Actions (Future)

Add to `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Version Management

1. Update version in:
   - `pyproject.toml`
   - `src/hackmd/__init__.py`

2. Commit with:
   ```bash
   git commit -m "chore: bump version to X.Y.Z"
   ```

3. Create tag:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

4. Create GitHub release:
   ```bash
   gh release create vX.Y.Z --generate-notes
   ```

## Troubleshooting

- **Missing README.md**: Run `gmake readme` first
- **Authentication failed**: Check your PyPI token is valid
- **Package exists**: Increment version number
- **Invalid metadata**: Check pyproject.toml syntax