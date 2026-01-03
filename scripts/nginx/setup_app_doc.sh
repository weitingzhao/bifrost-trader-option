#!/bin/bash
# Setup MkDocs site folder on web server (10.0.0.75)
# This script creates the documentation directory with correct permissions
# Can be run via SSH from dev PC OR directly on the server
# This script detects if it's running locally or remotely

# Note: set -e removed to allow graceful error handling for sudo password prompts

# Configuration
WEB_SERVER="10.0.0.75"
WEB_SERVER_USER="vision"
DOCS_DEPLOY_PATH="/var/www/docs"
REMOTE_SCRIPT_PATH="~/bifrost-scripts/nginx/setup_app_doc.sh"

# Get script directory and path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_FILE="$SCRIPT_DIR/setup_app_doc.sh"

# Detect if running locally on server or remotely via SSH
IS_LOCAL=false
if [ -n "$SSH_CONNECTION" ]; then
    # Running via SSH - check if we're already on the target server
    CURRENT_HOST=$(hostname 2>/dev/null || echo "")
    if echo "$CURRENT_HOST" | grep -qi "web-server\|10.0.0.75"; then
        IS_LOCAL=true
    fi
else
    # Not via SSH - check if we're on the server
    CURRENT_HOST=$(hostname 2>/dev/null || echo "")
    if echo "$CURRENT_HOST" | grep -qi "web-server\|10.0.0.75"; then
        IS_LOCAL=true
    fi
fi

# If not local, copy script to server first
if [ "$IS_LOCAL" = false ]; then
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
    
    # Copy script to server
    echo "📋 Copying setup_app_doc.sh to server..."
    ssh "$WEB_SERVER_USER@$WEB_SERVER" "mkdir -p ~/bifrost-scripts/nginx"
    scp "$SCRIPT_FILE" "$WEB_SERVER_USER@$WEB_SERVER:$REMOTE_SCRIPT_PATH"
    ssh "$WEB_SERVER_USER@$WEB_SERVER" "chmod +x $REMOTE_SCRIPT_PATH"
    echo "✅ Script copied to: $REMOTE_SCRIPT_PATH"
    echo ""
    
    echo "=========================================="
    echo "SCRIPT COPIED TO SERVER"
    echo "=========================================="
    echo ""
    echo "📝 Next steps:"
    echo ""
    echo "   1. SSH into the server:"
    echo "      ssh $WEB_SERVER_USER@$WEB_SERVER"
    echo ""
    echo "   2. Run the script locally (with sudo):"
    echo "      sudo $REMOTE_SCRIPT_PATH"
    echo ""
    echo "   This will create the directory with correct permissions."
    echo ""
    echo "💡 Alternative: If you have passwordless sudo configured,"
    echo "   the script will attempt to run remotely (may require password)."
    echo ""
    echo "=========================================="
    
    # Optionally try to run remotely (will fail if sudo needs password)
    echo ""
    read -p "Attempt to run setup remotely now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🚀 Attempting remote setup..."
        ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "sudo $REMOTE_SCRIPT_PATH" || {
            echo ""
            echo "⚠️  Remote execution failed (likely needs sudo password)"
            echo "   Please run the script locally on the server as shown above."
        }
    fi
    
else
    # Running locally on the server
    echo "=========================================="
    echo "Setting up MkDocs Site Folder"
    echo "=========================================="
    echo ""
    echo "📡 Server: $WEB_SERVER (running locally)"
    echo "📁 Docs path: $DOCS_DEPLOY_PATH"
    echo ""
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then 
        echo "⚠️  Warning: This script requires sudo privileges"
        echo "   Some commands may prompt for password"
        echo ""
    fi
    
    # Create documentation directory
    echo "📁 Creating documentation directory..."
    if sudo mkdir -p "$DOCS_DEPLOY_PATH" 2>/dev/null; then
        echo "✅ Directory created"
    else
        echo "❌ Error: Could not create directory (may need sudo password)"
        echo ""
        echo "Please run: sudo mkdir -p $DOCS_DEPLOY_PATH"
        exit 1
    fi
    
    # Set ownership to allow deployment
    echo "🔐 Setting ownership..."
    if sudo chown "$WEB_SERVER_USER:$WEB_SERVER_USER" "$DOCS_DEPLOY_PATH" 2>/dev/null; then
        echo "✅ Ownership set to $WEB_SERVER_USER:$WEB_SERVER_USER"
    else
        echo "⚠️  Warning: Could not set ownership (may need sudo password)"
    fi
    
    # Set permissions (755 for directory, allows read/execute)
    echo "🔐 Setting permissions..."
    if sudo chmod 755 "$DOCS_DEPLOY_PATH" 2>/dev/null; then
        echo "✅ Permissions set to 755"
    else
        echo "⚠️  Warning: Could not set permissions (may need sudo password)"
    fi
    
    # Create a placeholder index.html if directory is empty
    if [ ! -f "$DOCS_DEPLOY_PATH/index.html" ]; then
        echo "📄 Creating placeholder index.html..."
        if echo '<!DOCTYPE html><html><head><title>Bifrost Documentation</title></head><body><h1>Documentation will be deployed here</h1><p>Run ./scripts/docs/deploy_docs.sh to deploy documentation.</p></body></html>' | sudo tee "$DOCS_DEPLOY_PATH/index.html" > /dev/null 2>&1; then
            sudo chown "$WEB_SERVER_USER:$WEB_SERVER_USER" "$DOCS_DEPLOY_PATH/index.html" 2>/dev/null
            echo "✅ Placeholder created"
        else
            echo "⚠️  Warning: Could not create placeholder"
        fi
    fi
    
    echo ""
    
    # Verify directory was created
    echo "🔍 Verifying directory setup..."
    if [ -d "$DOCS_DEPLOY_PATH" ]; then
        echo "✅ Directory exists: $DOCS_DEPLOY_PATH"
        
        # Check permissions
        PERMS=$(stat -c '%a %U:%G' "$DOCS_DEPLOY_PATH" 2>/dev/null || stat -f '%Sp %Su:%Sg' "$DOCS_DEPLOY_PATH" 2>/dev/null || echo "")
        echo "   Permissions: $PERMS"
        echo ""
        
        # Check if directory is writable
        if [ -w "$DOCS_DEPLOY_PATH" ]; then
            echo "✅ Directory is writable by current user"
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
    if sudo chown -R "$WEB_SERVER_USER:$WEB_SERVER_USER" "$DOCS_DEPLOY_PATH" 2>/dev/null && \
       sudo chmod -R 755 "$DOCS_DEPLOY_PATH" 2>/dev/null; then
        echo "✅ Final permissions set correctly"
    else
        echo "⚠️  Warning: Could not set final permissions (may need sudo password)"
        echo "   Directory should still work for deployment"
    fi
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
    echo "=========================================="
fi
