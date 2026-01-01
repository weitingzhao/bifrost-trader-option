#!/bin/bash
# DEPRECATED: This script has been merged into refresh_schema.sh
# Use refresh_schema.sh instead: ./scripts/database/refresh_schema.sh
# This file is kept for backward compatibility

set -e

echo "⚠️  Warning: generate_schema_docs.sh is deprecated"
echo "   Use refresh_schema.sh instead: ./scripts/database/refresh_schema.sh"
echo ""
echo "Running refresh_schema.sh..."
echo ""

exec "$(dirname "$0")/refresh_schema.sh"
