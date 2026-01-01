#!/bin/bash
# Start nginx on web server (10.0.0.75) and fix configuration issues
# Can be run via SSH from dev PC OR directly on the server

# Configuration
WEB_SERVER="10.0.0.75"
WEB_SERVER_USER="vision"

# Detect if running locally on server or remotely via SSH
IS_LOCAL=false
if [ -n "$SSH_CONNECTION" ]; then
    CURRENT_HOST=$(hostname 2>/dev/null || echo "")
    if echo "$CURRENT_HOST" | grep -qi "web-server\|10.0.0.75"; then
        IS_LOCAL=true
    fi
else
    CURRENT_HOST=$(hostname 2>/dev/null || echo "")
    if echo "$CURRENT_HOST" | grep -qi "web-server\|10.0.0.75"; then
        IS_LOCAL=true
    fi
fi

# If not local, run via SSH with password prompt
if [ "$IS_LOCAL" = false ]; then
    echo "=========================================="
    echo "Starting Nginx on Web Server"
    echo "=========================================="
    echo ""
    echo "📡 Server: $WEB_SERVER_USER@$WEB_SERVER"
    echo ""
    
    # Test SSH connection
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$WEB_SERVER_USER@$WEB_SERVER" exit 2>/dev/null; then
        echo "❌ Error: Cannot connect to $WEB_SERVER"
        exit 1
    fi
    
    echo "✅ SSH connection successful"
    echo ""
    echo "🚀 Starting nginx with password prompt..."
    echo ""
    
    # Use ssh -t to allocate pseudo-terminal for password prompts
    ssh -t "$WEB_SERVER_USER@$WEB_SERVER" "
        # Check nginx configuration first
        echo '🧪 Testing nginx configuration...'
        if sudo nginx -t 2>&1; then
            echo '✅ Configuration is valid'
            echo ''
            echo '🚀 Starting nginx...'
            if sudo systemctl start nginx 2>&1; then
                echo '✅ Nginx started successfully'
                echo ''
                # Check status
                sudo systemctl status nginx --no-pager -l | head -10
            else
                echo '❌ Failed to start nginx'
                exit 1
            fi
        else
            echo '❌ Configuration has errors'
            echo ''
            echo '🔧 Attempting to fix configuration...'
            echo ''
            
            # Check for missing bifrost config
            if [ -L /etc/nginx/sites-enabled/bifrost ] && [ ! -f /etc/nginx/sites-available/bifrost ]; then
                echo '⚠️  Missing bifrost config file, removing broken symlink...'
                sudo rm /etc/nginx/sites-enabled/bifrost
                echo '✅ Removed broken symlink'
                echo ''
                echo '🧪 Testing configuration again...'
                if sudo nginx -t 2>&1; then
                    echo '✅ Configuration is now valid'
                    echo ''
                    echo '🚀 Starting nginx...'
                    if sudo systemctl start nginx 2>&1; then
                        echo '✅ Nginx started successfully'
                        echo ''
                        sudo systemctl status nginx --no-pager -l | head -10
                    else
                        echo '❌ Failed to start nginx'
                        exit 1
                    fi
                else
                    echo '❌ Configuration still has errors'
                    echo '   Please check: sudo nginx -t'
                    exit 1
                fi
            else
                echo '❌ Configuration errors need manual fixing'
                echo '   Please check: sudo nginx -t'
                exit 1
            fi
        fi
    " || {
        echo ""
        echo "⚠️  Could not start nginx remotely"
        echo "   Please SSH into server and run: sudo systemctl start nginx"
    }
    
else
    # Running locally on the server
    echo "=========================================="
    echo "Starting Nginx (Local)"
    echo "=========================================="
    echo ""
    
    # Check nginx configuration first
    echo "🧪 Testing nginx configuration..."
    if sudo nginx -t 2>&1; then
        echo "✅ Configuration is valid"
        echo ""
        echo "🚀 Starting nginx..."
        if sudo systemctl start nginx 2>&1; then
            echo "✅ Nginx started successfully"
            echo ""
            sudo systemctl status nginx --no-pager -l | head -10
        else
            echo "❌ Failed to start nginx"
            exit 1
        fi
    else
        echo "❌ Configuration has errors"
        echo ""
        echo "🔧 Attempting to fix configuration..."
        echo ""
        
        # Check for missing bifrost config
        if [ -L /etc/nginx/sites-enabled/bifrost ] && [ ! -f /etc/nginx/sites-available/bifrost ]; then
            echo "⚠️  Missing bifrost config file, removing broken symlink..."
            sudo rm /etc/nginx/sites-enabled/bifrost
            echo "✅ Removed broken symlink"
            echo ""
            echo "🧪 Testing configuration again..."
            if sudo nginx -t 2>&1; then
                echo "✅ Configuration is now valid"
                echo ""
                echo "🚀 Starting nginx..."
                if sudo systemctl start nginx 2>&1; then
                    echo "✅ Nginx started successfully"
                    echo ""
                    sudo systemctl status nginx --no-pager -l | head -10
                else
                    echo "❌ Failed to start nginx"
                    exit 1
                fi
            else
                echo "❌ Configuration still has errors"
                echo "   Please check: sudo nginx -t"
                exit 1
            fi
        else
            echo "❌ Configuration errors need manual fixing"
            echo "   Please check: sudo nginx -t"
            exit 1
        fi
    fi
fi

echo ""
echo "=========================================="

