# MkDocs Documentation Site

## Quick Start

### View Documentation Locally

```bash
# Install dependencies (if not already installed)
pip install mkdocs mkdocs-material mkdocs-git-revision-date-localized-plugin

# Start development server
mkdocs serve

# Or specify address
mkdocs serve --dev-addr=127.0.0.1:8000
```

Then open **http://127.0.0.1:8000** in your browser.

### Build Static Site

```bash
# Build static HTML
mkdocs build

# Output will be in site/ directory
```

## Features

- **Material Theme** - Beautiful, modern design with light/dark mode
- **Search** - Full-text search across all documentation
- **Navigation** - Organized by category (API, Database, Testing, etc.)
- **Responsive** - Works on mobile and desktop
- **Auto-reload** - Automatically refreshes when files change

## Documentation Structure

The site is organized into:

- **Home** - Overview and quick start
- **Project Plan** - Complete architecture and plan
- **API Documentation** - API development guides
- **Database** - Schema management and database guides
- **Testing** - Test strategies and coverage
- **Setup & Installation** - Setup guides
- **Development** - Development guides
- **Status & Progress** - Implementation status

## Configuration

Configuration is in `mkdocs.yml` at the project root.

### Adding New Pages

1. Add markdown file to appropriate `docs/` subdirectory
2. Add to `nav` section in `mkdocs.yml`
3. Restart server or rebuild

## Deploy to GitHub Pages

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy
```

This will make the documentation available at:
`https://your-username.github.io/bifrost-trader-option/`

## Troubleshooting

### Port Already in Use

```bash
mkdocs serve --dev-addr=127.0.0.1:8001
```

### Missing Pages

Check that files are listed in `mkdocs.yml` nav section.

### Build Errors

```bash
rm -rf site/ .mkdocs_cache/
mkdocs build
```

## More Information

See [docs/MKDOCS_SETUP.md](docs/MKDOCS_SETUP.md) for detailed setup instructions.

