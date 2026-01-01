#!/bin/bash
# Build MkDocs documentation site
# This script builds the static documentation site

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Verify we're in the right directory
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ Error: mkdocs.yml not found in $PROJECT_ROOT"
    echo "   Current directory: $(pwd)"
    exit 1
fi

echo "=========================================="
echo "Building MkDocs Documentation"
echo "=========================================="
echo ""

# Check if mkdocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo "❌ Error: mkdocs is not installed"
    echo "Install with: pip install mkdocs mkdocs-material"
    exit 1
fi

# Build the documentation
echo "📖 Building documentation site..."
mkdocs build

# Get site directory from mkdocs.yml or use default
SITE_DIR="mkdocs_site"
if [ -f "mkdocs.yml" ]; then
    # Try to extract site_dir from mkdocs.yml
    EXTRACTED_DIR=$(grep -E "^site_dir:" mkdocs.yml | sed 's/site_dir:[[:space:]]*//' | tr -d '"' | tr -d "'" || echo "")
    if [ -n "$EXTRACTED_DIR" ]; then
        SITE_DIR="$EXTRACTED_DIR"
    fi
fi

# Check if build was successful
if [ -d "$SITE_DIR" ]; then
    echo ""
    echo "✅ Documentation built successfully!"
    echo "📁 Output directory: $PROJECT_ROOT/$SITE_DIR"
    echo ""
    echo "📊 Build statistics:"
    echo "   - Total files: $(find "$SITE_DIR" -type f | wc -l | tr -d ' ')"
    echo "   - Total size: $(du -sh "$SITE_DIR" | cut -f1)"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Review the site locally:"
    echo "      cd $SITE_DIR && python -m http.server 8000"
    echo ""
    echo "   2. Deploy to web server:"
    echo "      ./scripts/docs/deploy_docs.sh"
    echo ""
else
    echo "❌ Error: Build failed - $SITE_DIR directory not found"
    exit 1
fi

