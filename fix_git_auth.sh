#!/bin/bash
# Script to fix GitHub authentication for weitingzhao account

cd /Users/vision-mac-trader/Desktop/stocks/bifrost-trader-option

echo "🔧 Fixing GitHub authentication..."
echo ""

# Option 1: Update remote URL to include username
echo "📝 Updating remote URL to include username..."
git remote set-url origin https://weitingzhao@github.com/weitingzhao/bifrost-trader-option.git

echo "✅ Remote URL updated"
echo ""

# Option 2: Clear cached credentials (macOS Keychain)
echo "🔑 Clearing cached credentials..."
if command -v git-credential-osxkeychain > /dev/null 2>&1; then
    echo "host=github.com
protocol=https" | git credential-osxkeychain erase
    echo "✅ Credentials cleared from macOS Keychain"
else
    echo "⚠️  git-credential-osxkeychain not found, skipping credential clearing"
fi

echo ""
echo "✅ Authentication setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Try pushing: git push origin main"
echo "2. When prompted, enter your GitHub password or Personal Access Token"
echo ""
echo "💡 If you don't have a Personal Access Token, create one at:"
echo "   https://github.com/settings/tokens"
echo "   (Select 'repo' scope for full repository access)"
echo ""
echo "🚀 To push now, run:"
echo "   git push origin main"

