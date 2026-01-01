#!/bin/bash
# Copy nginx setup scripts to web server (10.0.0.75)
# This script copies nginx setup scripts to the server for manual execution

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
WEB_SERVER="10.0.0.75"
WEB_SERVER_USER="vision"
SETUP_SCRIPT="$SCRIPT_DIR/setup_nginx.sh"
NGINX_CHECK_SCRIPT="$SCRIPT_DIR/check_nginx.sh"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Copying Nginx Setup Scripts to Web Server"
echo "=========================================="
echo ""
echo "📡 Target: $WEB_SERVER_USER@$WEB_SERVER"
echo ""

# Test SSH connection
echo "🔌 Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 "$WEB_SERVER_USER@$WEB_SERVER" exit 2>/dev/null; then
    echo "❌ Error: Cannot connect to $WEB_SERVER"
    echo ""
    echo "Please ensure:"
    echo "   1. Server is accessible: ping $WEB_SERVER"
    echo "   2. SSH key is configured: ssh-copy-id $WEB_SERVER_USER@$WEB_SERVER"
    echo "   3. User has SSH access"
    exit 1
fi

echo "✅ SSH connection successful"
echo ""

# Create remote scripts directory
echo "📁 Creating remote scripts directory..."
ssh "$WEB_SERVER_USER@$WEB_SERVER" "mkdir -p ~/bifrost-scripts/nginx"

# Copy setup script
if [ -f "$SETUP_SCRIPT" ]; then
    echo "📋 Copying setup_nginx.sh..."
    scp "$SETUP_SCRIPT" "$WEB_SERVER_USER@$WEB_SERVER:~/bifrost-scripts/nginx/"
else
    echo "⚠️  Warning: setup_nginx.sh not found at $SETUP_SCRIPT"
fi

# Copy nginx check script
if [ -f "$NGINX_CHECK_SCRIPT" ]; then
    echo "📋 Copying check_nginx.sh..."
    scp "$NGINX_CHECK_SCRIPT" "$WEB_SERVER_USER@$WEB_SERVER:~/bifrost-scripts/nginx/"
else
    echo "⚠️  Warning: check_nginx.sh not found at $NGINX_CHECK_SCRIPT"
fi

# Copy nginx configuration files
if [ -f "$SCRIPT_DIR/nginx_docs.conf" ]; then
    echo "📋 Copying nginx_docs.conf..."
    scp "$SCRIPT_DIR/nginx_docs.conf" "$WEB_SERVER_USER@$WEB_SERVER:~/bifrost-scripts/nginx/"
fi

if [ -f "$SCRIPT_DIR/bifrost.conf" ]; then
    echo "📋 Copying bifrost.conf..."
    scp "$SCRIPT_DIR/bifrost.conf" "$WEB_SERVER_USER@$WEB_SERVER:~/bifrost-scripts/nginx/"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
ssh "$WEB_SERVER_USER@$WEB_SERVER" "chmod +x ~/bifrost-scripts/nginx/*.sh 2>/dev/null || true"

echo ""
echo "✅ Scripts copied successfully!"
echo ""
echo "📝 Next steps:"
echo ""
echo "   1. SSH into the server:"
echo "      ssh $WEB_SERVER_USER@$WEB_SERVER"
echo ""
echo "   2. Check if nginx exists:"
echo "      ~/bifrost-scripts/nginx/check_nginx.sh"
echo ""
echo "   3. Run setup (will handle nginx removal/reinstall if needed):"
echo "      sudo ~/bifrost-scripts/nginx/setup_nginx.sh"
echo ""
echo "=========================================="

