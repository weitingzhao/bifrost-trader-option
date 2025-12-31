#!/bin/bash
# Clean environment commit script - bypasses Cursor shell issues
# This script uses a minimal environment to avoid shell initialization problems

# Use a clean bash environment
exec /bin/bash --norc --noprofile << 'EOF'
set -e

# Change to project directory
cd /Users/vision-mac-trader/Desktop/stocks/bifrost-trader-option

echo "📋 Checking git status..."
/usr/bin/git status --short

echo ""
echo "📦 Staging all changes..."
/usr/bin/git add -A

echo ""
echo "📝 Committing changes..."
/usr/bin/git commit -m "Refactor Streamlit monitoring app and add API development guide

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
BRANCH=$(/usr/bin/git branch --show-current)
echo "Current branch: $BRANCH"

echo ""
echo "🚀 Pushing to GitHub..."
/usr/bin/git push origin "$BRANCH"

echo ""
echo "✅ Successfully pushed to GitHub!"
EOF

