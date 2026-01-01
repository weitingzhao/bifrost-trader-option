#!/bin/bash
# Deploy MkDocs documentation to web server (10.0.0.75)
# This script builds and deploys the documentation to the web server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
WEB_SERVER="10.0.0.75"
WEB_SERVER_USER="vision"
DOCS_DEPLOY_PATH="/var/www/docs"
LOCAL_SITE_DIR="$PROJECT_ROOT/site"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Deploying Documentation to Web Server"
echo "=========================================="
echo ""
echo "📡 Target: $WEB_SERVER_USER@$WEB_SERVER:$DOCS_DEPLOY_PATH"
echo ""

# Check if site directory exists
if [ ! -d "$LOCAL_SITE_DIR" ]; then
    echo "⚠️  Site directory not found. Building documentation..."
    "$SCRIPT_DIR/build_docs.sh"
fi

# Check if site directory still doesn't exist after build
if [ ! -d "$LOCAL_SITE_DIR" ]; then
    echo "❌ Error: Site directory not found after build"
    exit 1
fi

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

# Create remote directory if it doesn't exist
echo "📁 Creating remote directory..."
ssh "$WEB_SERVER_USER@$WEB_SERVER" "sudo mkdir -p $DOCS_DEPLOY_PATH && sudo chown $WEB_SERVER_USER:$WEB_SERVER_USER $DOCS_DEPLOY_PATH"

# Backup existing docs if they exist
echo "💾 Backing up existing documentation..."
ssh "$WEB_SERVER_USER@$WEB_SERVER" "
    if [ -d $DOCS_DEPLOY_PATH ]; then
        sudo mv $DOCS_DEPLOY_PATH ${DOCS_DEPLOY_PATH}.backup.\$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
    fi
    sudo mkdir -p $DOCS_DEPLOY_PATH
    sudo chown $WEB_SERVER_USER:$WEB_SERVER_USER $DOCS_DEPLOY_PATH
"

# Deploy files
echo "🚀 Deploying documentation..."
rsync -avz --delete \
    --exclude='.git' \
    "$LOCAL_SITE_DIR/" \
    "$WEB_SERVER_USER@$WEB_SERVER:$DOCS_DEPLOY_PATH/"

# Set proper permissions
echo "🔐 Setting permissions..."
ssh "$WEB_SERVER_USER@$WEB_SERVER" "sudo chown -R www-data:www-data $DOCS_DEPLOY_PATH && sudo chmod -R 755 $DOCS_DEPLOY_PATH"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📖 Documentation is now available at:"
echo "   http://$WEB_SERVER/docs/"
echo ""
echo "🌐 To access from other PCs:"
echo "   http://10.0.0.75/docs/"
echo ""
echo "📝 Next steps:"
echo "   1. Configure nginx on web server (see scripts/nginx/nginx_docs.conf)"
echo "   2. Test access from another PC"
echo ""

