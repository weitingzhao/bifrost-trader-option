#!/bin/bash
# Generate markdown documentation from schema_all.sql
# Creates a readable schema documentation for MkDocs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Generating Schema Documentation"
echo "=========================================="
echo ""

# Run Python script
python3 "$SCRIPT_DIR/generate_schema_docs.py"

echo ""
echo "✅ Done! Schema documentation generated in docs/database/SCHEMA.md"
echo ""
