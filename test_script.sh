#!/bin/bash
# Test script to verify commit_and_push.sh works
# This will check the script without actually committing

cd /Users/vision-mac-trader/Desktop/stocks/bifrost-trader-option

echo "🔍 Testing commit_and_push.sh script..."
echo ""

# Check if script exists
if [ ! -f "commit_and_push.sh" ]; then
    echo "❌ Error: commit_and_push.sh not found"
    exit 1
fi

echo "✅ Script file exists"

# Check if script is executable
if [ ! -x "commit_and_push.sh" ]; then
    echo "⚠️  Script is not executable, making it executable..."
    chmod +x commit_and_push.sh
fi

echo "✅ Script is executable"

# Check syntax
echo "🔍 Checking script syntax..."
if bash -n commit_and_push.sh; then
    echo "✅ Script syntax is valid"
else
    echo "❌ Script has syntax errors"
    exit 1
fi

# Check if we're in a git repository
echo "🔍 Checking if this is a git repository..."
if [ -d ".git" ]; then
    echo "✅ This is a git repository"
else
    echo "❌ Not a git repository"
    exit 1
fi

# Check git status (dry run)
echo "🔍 Checking git status..."
git status --short

# Check if there are changes to commit
echo "🔍 Checking for uncommitted changes..."
if [ -n "$(git status --porcelain)" ]; then
    echo "✅ There are uncommitted changes"
    echo ""
    echo "📋 Files that will be committed:"
    git status --short
else
    echo "⚠️  No uncommitted changes found"
fi

# Check current branch
BRANCH=$(git branch --show-current)
echo ""
echo "🌿 Current branch: $BRANCH"

# Check remote
echo "🔍 Checking remote configuration..."
if git remote get-url origin > /dev/null 2>&1; then
    REMOTE_URL=$(git remote get-url origin)
    echo "✅ Remote 'origin' configured: $REMOTE_URL"
else
    echo "⚠️  No remote 'origin' configured"
fi

echo ""
echo "✅ Script validation complete!"
echo ""
echo "📝 To actually commit and push, run:"
echo "   bash commit_and_push.sh"



