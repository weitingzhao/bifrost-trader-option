#!/bin/bash
# Setup MkDocs site folder on web server (10.0.0.75)
# This script creates the documentation directory with correct permissions
# Run this before deploying documentation to prevent nginx folder exceptions

set -e

# Configuration
WEB_SERVER="10.0.0.75"
WEB_SERVER_USER="vision"
DOCS_DEPLOY_PATH="/var/www/docs"

echo "=========================================="
echo "Setting up MkDocs Site Folder"
echo "=========================================="
echo ""
echo "📡 Server: $WEB_SERVER_USER@$WEB_SERVER"
echo "📁 Docs path: $DOCS_DEPLOY_PATH"
echo ""

# Test SSH connection
echo "🔌 Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$WEB_SERVER_USER@$WEB_SERVER" exit 2>/dev/null; then
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

# Create documentation directory
echo "📁 Creating documentation directory..."
if ssh "$WEB_SERVER_USER@$WEB_SERVER" "
    # Create directory if it doesn't exist
    sudo mkdir -p $DOCS_DEPLOY_PATH 2>&1
    
    # Set ownership to allow deployment
    sudo chown $WEB_SERVER_USER:$WEB_SERVER_USER $DOCS_DEPLOY_PATH 2>&1
    
    # Set permissions (755 for directory, allows read/execute)
    sudo chmod 755 $DOCS_DEPLOY_PATH 2>&1
    
    # Create a placeholder index.html if directory is empty
    if [ ! -f $DOCS_DEPLOY_PATH/index.html ]; then
        echo '<!DOCTYPE html><html><head><title>Bifrost Documentation</title></head><body><h1>Documentation will be deployed here</h1><p>Run ./scripts/docs/deploy_docs.sh to deploy documentation.</p></body></html>' | sudo tee $DOCS_DEPLOY_PATH/index.html > /dev/null 2>&1
        sudo chown $WEB_SERVER_USER:$WEB_SERVER_USER $DOCS_DEPLOY_PATH/index.html 2>&1
    fi
" 2>&1; then
    echo "✅ Directory setup completed"
else
    echo "⚠️  Warning: Sudo commands may require password"
    echo ""
    echo "💡 If sudo password is required, you can:"
    echo "   1. SSH into server and run commands manually:"
    echo "      ssh $WEB_SERVER_USER@$WEB_SERVER"
    echo "      sudo mkdir -p $DOCS_DEPLOY_PATH"
    echo "      sudo chown $WEB_SERVER_USER:$WEB_SERVER_USER $DOCS_DEPLOY_PATH"
    echo "      sudo chmod 755 $DOCS_DEPLOY_PATH"
    echo ""
    echo "   2. Or configure passwordless sudo for this user"
    echo ""
    echo "   Continuing with verification..."
fi
echo ""

# Verify directory was created
echo "🔍 Verifying directory setup..."
if ssh "$WEB_SERVER_USER@$WEB_SERVER" "[ -d $DOCS_DEPLOY_PATH ]"; then
    echo "✅ Directory created: $DOCS_DEPLOY_PATH"
    
    # Check permissions
    PERMS=$(ssh "$WEB_SERVER_USER@$WEB_SERVER" "stat -c '%a %U:%G' $DOCS_DEPLOY_PATH" || echo "")
    echo "   Permissions: $PERMS"
    echo ""
    
    # Check if directory is writable
    if ssh "$WEB_SERVER_USER@$WEB_SERVER" "[ -w $DOCS_DEPLOY_PATH ]"; then
        echo "✅ Directory is writable by $WEB_SERVER_USER"
    else
        echo "⚠️  Warning: Directory may not be writable"
    fi
    echo ""
else
    echo "❌ Error: Directory was not created"
    exit 1
fi

# Set final permissions for nginx to serve files
echo "🔐 Setting final permissions for nginx..."
ssh "$WEB_SERVER_USER@$WEB_SERVER" "
    # Ensure www-data can read the directory
    sudo chown -R $WEB_SERVER_USER:$WEB_SERVER_USER $DOCS_DEPLOY_PATH
    sudo chmod -R 755 $DOCS_DEPLOY_PATH
    
    # After deployment, ownership will be changed to www-data:www-data
    # But for now, allow deployment user to write
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📁 Directory ready: $DOCS_DEPLOY_PATH"
echo ""
echo "📝 Next steps:"
echo "   1. Deploy documentation:"
echo "      ./scripts/docs/deploy_docs.sh"
echo ""
echo "   2. Verify deployment:"
echo "      curl http://$WEB_SERVER/docs/"
echo ""
echo "💡 Note: If you encountered sudo password prompts, you may need to:"
echo "   - Configure passwordless sudo, or"
echo "   - Run this script's commands manually on the server"
echo ""
echo "=========================================="

