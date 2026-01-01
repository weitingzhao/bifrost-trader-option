#!/bin/bash
# Refresh database schema files
# Validates schema synchronization and generates markdown documentation
# This script:
#   1. Reads schema_*.sql files directly (no intermediate file generation)
#   2. Generates markdown documentation (SCHEMA.md) for MkDocs
#   3. Verifies schema synchronization (Django → SQLAlchemy → schema files)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCS_FILE="$PROJECT_ROOT/docs/database/SCHEMA.md"

echo "=========================================="
echo "Refreshing Database Schema"
echo "=========================================="
echo ""

# Check that schema files exist
echo "📦 Checking schema files..."
SCHEMA_FILES=(
    "$SCRIPT_DIR/schema_options.sql"
    "$SCRIPT_DIR/schema_strategies.sql"
    "$SCRIPT_DIR/schema_data_collection.sql"
)

MISSING_FILES=()
for schema_file in "${SCHEMA_FILES[@]}"; do
    if [ ! -f "$schema_file" ]; then
        MISSING_FILES+=("$(basename "$schema_file")")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "❌ Error: Missing schema files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo "   ✅ schema_options.sql"
echo "   ✅ schema_strategies.sql"
echo "   ✅ schema_data_collection.sql"
echo ""

# Generate markdown documentation and verify schema
echo "📝 Generating markdown documentation and verifying schema..."
echo ""

# Run Python script to generate markdown and verify schema
# Python script reads schema_*.sql files directly (no schema_all.sql needed)
python3 "$SCRIPT_DIR/refresh_schema.py"

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Schema Refresh Complete"
else
    echo "⚠️  Schema Refresh Complete (with warnings)"
fi
echo "=========================================="
echo ""
echo "📁 Generated files:"
echo "   ✅ docs/database/SCHEMA.md (index with links)"
echo "   ✅ docs/database/SCHEMA_OPTIONS.md (Options app)"
echo "   ✅ docs/database/SCHEMA_STRATEGIES.md (Strategies app)"
echo "   ✅ docs/database/SCHEMA_DATA_COLLECTION.md (Data Collection app)"
echo ""
echo "💡 Note:"
echo "   - Reads schema_*.sql files directly (no intermediate file)"
echo "   - Validates Django → SQLAlchemy → schema files synchronization"
echo "   - Generates markdown documentation from source files"
echo ""
echo "📚 View in MkDocs:"
echo "   mkdocs serve"
echo "   Then navigate to: Database > SCHEMA"
echo ""

exit $EXIT_CODE


