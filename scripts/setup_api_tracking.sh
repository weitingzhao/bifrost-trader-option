#!/bin/bash
# Setup script for API change tracking

echo "Setting up API change tracking..."

# Create directories
mkdir -p api_schemas
mkdir -p docs/api

# Install tracking dependencies
echo "Installing dependencies..."
pip install deepdiff pydantic[email] > /dev/null 2>&1

# Make scripts executable
chmod +x scripts/track_api_changes.py

echo "✅ API tracking setup complete!"
echo ""
echo "Usage:"
echo "  Export current schema: python scripts/track_api_changes.py export"
echo "  List endpoints: python scripts/track_api_changes.py list"
echo "  Compare schemas: python scripts/track_api_changes.py compare --old schema1.json --new schema2.json"
echo "  Generate changelog: python scripts/track_api_changes.py changelog"

