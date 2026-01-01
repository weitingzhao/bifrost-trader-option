#!/bin/bash
# Deploy MkDocs documentation to web server (10.0.0.75)
# Simple script that builds and deploys documentation to nginx docs path

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
WEB_SERVER="10.0.0.75"
WEB_SERVER_USER="vision"
DOCS_DEPLOY_PATH="/var/www/docs"

# Get site directory from mkdocs.yml or use default
SITE_DIR="app_mkdocs"
if [ -f "$PROJECT_ROOT/mkdocs.yml" ]; then
    # Try to extract site_dir from mkdocs.yml
    EXTRACTED_DIR=$(grep -E "^site_dir:" "$PROJECT_ROOT/mkdocs.yml" | sed 's/site_dir:[[:space:]]*//' | tr -d '"' | tr -d "'" || echo "")
    if [ -n "$EXTRACTED_DIR" ]; then
        SITE_DIR="$EXTRACTED_DIR"
    fi
fi
LOCAL_SITE_DIR="$PROJECT_ROOT/$SITE_DIR"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Deploying Documentation to Web Server"
echo "=========================================="
echo ""
echo "📡 Target: $WEB_SERVER_USER@$WEB_SERVER:$DOCS_DEPLOY_PATH"
echo ""

# Build documentation (always build to ensure latest version)
echo "📖 Building documentation..."
"$SCRIPT_DIR/build_docs.sh"

# Verify site directory exists after build
if [ ! -d "$LOCAL_SITE_DIR" ]; then
    echo "❌ Error: Site directory not found after build: $LOCAL_SITE_DIR"
    echo ""
    echo "Please check:"
    echo "   1. mkdocs.yml exists and is valid"
    echo "   2. mkdocs is installed: pip install mkdocs mkdocs-material"
    echo "   3. Build completed successfully"
    exit 1
fi

# Verify directory has content
if [ ! -f "$LOCAL_SITE_DIR/index.html" ]; then
    echo "❌ Error: index.html not found in $LOCAL_SITE_DIR"
    echo "   Build may have failed"
    exit 1
fi

echo "✅ Documentation built successfully"
echo "   Directory: $LOCAL_SITE_DIR"
echo "   Files: $(find "$LOCAL_SITE_DIR" -type f | wc -l | tr -d ' ')"
echo ""

echo "📦 Preparing deployment..."
echo "   - Source: $LOCAL_SITE_DIR"
echo "   - Destination: $WEB_SERVER_USER@$WEB_SERVER:$DOCS_DEPLOY_PATH"
echo ""

# Test SSH connection
echo "🔌 Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$WEB_SERVER_USER@$WEB_SERVER" exit 2>/dev/null; then
    echo "❌ Error: Cannot connect to $WEB_SERVER"
    echo ""
    echo "Please ensure:"
    echo "   1. SSH key is set up for passwordless access"
    echo "   2. Server is accessible: ping $WEB_SERVER"
    echo "   3. User has permissions: ssh $WEB_SERVER_USER@$WEB_SERVER"
    exit 1
fi

echo "✅ SSH connection successful"
echo ""

# Ensure remote directory exists and has correct permissions (with password prompt)
echo "📁 Ensuring remote directory exists..."
echo "💡 This requires sudo privileges (will prompt for password)"
echo ""
ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
    sudo mkdir -p $DOCS_DEPLOY_PATH
    sudo chown $WEB_SERVER_USER:$WEB_SERVER_USER $DOCS_DEPLOY_PATH
    sudo chmod 755 $DOCS_DEPLOY_PATH
    echo '✅ Directory ready: $DOCS_DEPLOY_PATH'
" || {
    echo "⚠️  Warning: Could not create directory"
    echo "   Run ./scripts/nginx/setup_app_mkdocs.sh first to setup directory"
    exit 1
}

# Backup existing docs if they exist (with password prompt)
echo "💾 Backing up existing documentation..."
ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
    if [ -d $DOCS_DEPLOY_PATH ] && [ \"\$(ls -A $DOCS_DEPLOY_PATH 2>/dev/null)\" ]; then
        BACKUP_DIR=${DOCS_DEPLOY_PATH}.backup.\$(date +%Y%m%d_%H%M%S)
        sudo mv $DOCS_DEPLOY_PATH \$BACKUP_DIR 2>/dev/null || true
        echo \"✅ Backed up to: \$BACKUP_DIR\"
    fi
    sudo mkdir -p $DOCS_DEPLOY_PATH
    sudo chown $WEB_SERVER_USER:$WEB_SERVER_USER $DOCS_DEPLOY_PATH
    sudo chmod 755 $DOCS_DEPLOY_PATH
"

# Deploy files
echo "🚀 Deploying documentation..."
echo "   Copying files from $LOCAL_SITE_DIR to $DOCS_DEPLOY_PATH..."
rsync -avz --delete \
    --exclude='.git' \
    --exclude='.DS_Store' \
    --progress \
    "$LOCAL_SITE_DIR/" \
    "$WEB_SERVER_USER@$WEB_SERVER:$DOCS_DEPLOY_PATH/"

# Verify deployment
echo "🔍 Verifying deployment..."
FILE_COUNT=$(ssh "$WEB_SERVER_USER@$WEB_SERVER" "find $DOCS_DEPLOY_PATH -type f | wc -l" || echo "0")
echo "   Files deployed: $FILE_COUNT"

# Set proper permissions (with password prompt)
echo "🔐 Setting permissions for nginx..."
ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
    sudo chown -R www-data:www-data $DOCS_DEPLOY_PATH
    sudo chmod -R 755 $DOCS_DEPLOY_PATH
    echo '✅ Permissions set correctly'
"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📖 Documentation is now available at:"
echo "   http://$WEB_SERVER/docs/"
echo ""
echo "🌐 To access from other PCs:"
echo "   http://10.0.0.75/docs/"
echo ""
echo "📝 Note: Ensure nginx is configured (see scripts/nginx/ for setup scripts)"
echo ""
