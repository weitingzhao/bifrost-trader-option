#!/bin/bash
# Build MkDocs documentation site
# This script builds the static documentation site

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

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

# Check if build was successful
if [ -d "site" ]; then
    echo ""
    echo "✅ Documentation built successfully!"
    echo "📁 Output directory: $PROJECT_ROOT/site"
    echo ""
    echo "📊 Build statistics:"
    echo "   - Total files: $(find site -type f | wc -l | tr -d ' ')"
    echo "   - Total size: $(du -sh site | cut -f1)"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Review the site locally:"
    echo "      cd site && python -m http.server 8000"
    echo ""
    echo "   2. Deploy to web server:"
    echo "      ./scripts/docs/deploy_docs.sh"
    echo ""
else
    echo "❌ Error: Build failed - site directory not found"
    exit 1
fi

