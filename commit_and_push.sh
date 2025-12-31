#!/bin/bash
# Script to commit and push changes to GitHub
# Run this script directly in your terminal: bash commit_and_push.sh

set -e  # Exit on error

echo "📋 Checking git status..."
git status

echo ""
echo "📦 Staging all changes..."
git add -A

echo ""
echo "📝 Committing changes..."
git commit -m "Refactor Streamlit monitoring app and add API development guide

- Created utils.py to consolidate shared functions (run_ssh_command, get_status, etc.)
- Removed duplicate code from app.py (~280 lines removed)
- Updated pages to import from utils.py for better maintainability
- Renamed 'FastAPI Live Logs' to 'API Logs' and made it child of 'APP-Server Status'
- Added comprehensive API development guide (docs/api/API_DEVELOPMENT_GUIDE.md)
- Added API changelog template (docs/api/API_CHANGELOG.md)
- Created API tracking script (scripts/track_api_changes.py)
- Improved code organization and maintainability"

echo ""
echo "🌿 Checking current branch..."
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"

echo ""
echo "🚀 Pushing to GitHub..."
git push origin "$BRANCH"

echo ""
echo "✅ Successfully pushed to GitHub!"

