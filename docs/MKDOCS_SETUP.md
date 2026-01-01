# MkDocs Setup and Usage

## Overview

MkDocs generates a beautiful, searchable documentation website from the markdown files in the `docs/` directory.

## Installation

```bash
# Install MkDocs and Material theme
pip install mkdocs mkdocs-material mkdocs-git-revision-date-localized-plugin

# Or add to requirements.txt (already added)
pip install -r requirements.txt
```

## Usage

### Serve Locally (Development)

```bash
# Start development server
mkdocs serve

# Or specify address and port
mkdocs serve --dev-addr=127.0.0.1:8000
```

Then open http://127.0.0.1:8000 in your browser.

The server will auto-reload when you make changes to documentation files.

### Build Static Site

```bash
# Build static HTML site
mkdocs build

# Output will be in site/ directory
```

### Deploy to GitHub Pages

```bash
# Install gh-pages plugin
pip install mkdocs-material[imaging]

# Deploy to GitHub Pages
mkdocs gh-deploy
```

This will:
1. Build the site
2. Create/update the `gh-pages` branch
3. Push to GitHub
4. Make it available at `https://your-username.github.io/bifrost-trader-option/`

## Configuration

Configuration is in `mkdocs.yml` at the project root.

### Key Settings

- **Site name:** Bifrost Options Trading Strategy Analyzer
- **Theme:** Material (with light/dark mode)
- **Navigation:** Organized by category (API, Database, Testing, etc.)
- **Search:** Enabled with suggestions and highlighting

### Adding New Pages

1. Add the markdown file to the appropriate `docs/` subdirectory
2. Add it to the `nav` section in `mkdocs.yml`:

```yaml
nav:
  - Your Section:
    - your-section/your-page.md
```

3. Rebuild or restart the server

## Features

### Material Theme Features

- **Light/Dark Mode Toggle** - Switch between themes
- **Search** - Full-text search across all documentation
- **Navigation Tabs** - Easy navigation between sections
- **Code Highlighting** - Syntax highlighting for code blocks
- **Responsive Design** - Works on mobile and desktop

### Navigation Structure

The documentation is organized into:
- Home
- Project Plan
- API Documentation
- Database (with Schema Management as key section)
- Testing
- Setup & Installation
- Development
- Status & Progress

## Troubleshooting

### Port Already in Use

```bash
# Use a different port
mkdocs serve --dev-addr=127.0.0.1:8001
```

### Missing Pages

If a page doesn't appear:
1. Check the file exists in `docs/`
2. Check it's listed in `mkdocs.yml` nav section
3. Check for typos in file paths

### Build Errors

```bash
# Clean build
rm -rf site/ .mkdocs_cache/
mkdocs build
```

## Continuous Integration

You can set up GitHub Actions to automatically build and deploy:

```yaml
# .github/workflows/docs.yml
name: Deploy Docs
on:
  push:
    branches:
      - main
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install mkdocs mkdocs-material
      - run: mkdocs gh-deploy --force
```

## Accessing Documentation

### Local Development
- URL: http://127.0.0.1:8000
- Auto-reloads on file changes

### Production (GitHub Pages)
- URL: https://your-username.github.io/bifrost-trader-option/
- Updates automatically on push to main branch

## Tips

1. **Use relative links** in markdown files (they work in both GitHub and MkDocs)
2. **Add code blocks** with language tags for syntax highlighting
3. **Use admonitions** for notes, warnings, and tips
4. **Keep navigation organized** by category
5. **Update index.md** when adding major sections

