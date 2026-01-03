#!/bin/bash
# Launch Skote Nodejs v4.2.0 theme for localhost access
# This script allows you to view the theme in your browser for reference

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
THEME_DIR="$PROJECT_ROOT/ref_themes/skote_nodejs_v4.2.0"
ADMIN_DIR="$THEME_DIR/Admin"
STARTERKIT_DIR="$THEME_DIR/Starterkit"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Skote Nodejs v4.2.0 Theme Launcher"
echo "=========================================="
echo ""

# Check if theme directory exists
if [ ! -d "$THEME_DIR" ]; then
    echo "❌ Error: Theme directory not found: $THEME_DIR"
    echo "   Please ensure the Skote theme is extracted to: ref_themes/skote_nodejs_v4.2.0/"
    exit 1
fi

# Function to launch Admin version
launch_admin() {
    echo -e "${BLUE}Launching Skote Admin version...${NC}"
    echo ""
    
    if [ ! -d "$ADMIN_DIR" ]; then
        echo "❌ Error: Admin directory not found: $ADMIN_DIR"
        return 1
    fi
    
    cd "$ADMIN_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing dependencies..."
        npm install
    fi
    
    # Use existing config.env from theme
    if [ ! -f "config.env" ]; then
        echo "❌ Error: config.env not found in theme directory"
        echo "   Expected: $ADMIN_DIR/config.env"
        echo "   Please ensure the Skote theme is properly extracted"
        return 1
    else
        echo "✅ Using config.env from theme"
    fi
    
    # Read port from config.env or use default
    PORT=$(grep -E "^PORT=" config.env 2>/dev/null | cut -d '=' -f2 || echo "3000")
    
    echo ""
    echo -e "${GREEN}✅ Starting Skote Admin on http://localhost:${PORT}${NC}"
    echo ""
    echo "Access at: http://localhost:${PORT}"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    npm start
}

# Function to launch Starterkit version
launch_starterkit() {
    echo -e "${BLUE}Launching Skote Starterkit version...${NC}"
    echo ""
    
    if [ ! -d "$STARTERKIT_DIR" ]; then
        echo "❌ Error: Starterkit directory not found: $STARTERKIT_DIR"
        return 1
    fi
    
    cd "$STARTERKIT_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing dependencies..."
        npm install
    fi
    
    # Use existing config.env from theme
    if [ ! -f "config.env" ]; then
        echo "❌ Error: config.env not found in theme directory"
        echo "   Expected: $STARTERKIT_DIR/config.env"
        echo "   Please ensure the Skote theme is properly extracted"
        return 1
    else
        echo "✅ Using config.env from theme"
    fi
    
    # Read port from config.env or use default
    PORT=$(grep -E "^PORT=" config.env 2>/dev/null | cut -d '=' -f2 || echo "3001")
    
    echo ""
    echo -e "${GREEN}✅ Starting Skote Starterkit on http://localhost:${PORT}${NC}"
    echo ""
    echo "Access at: http://localhost:${PORT}"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    npm start
}

# Function to open documentation
launch_docs() {
    echo -e "${BLUE}Opening Skote Documentation...${NC}"
    echo ""
    
    DOCS_DIR="$THEME_DIR/Documentation"
    if [ ! -d "$DOCS_DIR" ]; then
        echo "❌ Error: Documentation directory not found: $DOCS_DIR"
        return 1
    fi
    
    DOCS_INDEX="$DOCS_DIR/nodejs/index.html"
    if [ -f "$DOCS_INDEX" ]; then
        echo -e "${GREEN}✅ Opening documentation in browser...${NC}"
        echo ""
        # Try to open in default browser
        if command -v open >/dev/null 2>&1; then
            open "file://$DOCS_INDEX"
        elif command -v xdg-open >/dev/null 2>&1; then
            xdg-open "file://$DOCS_INDEX"
        else
            echo "Please open manually: file://$DOCS_INDEX"
        fi
    else
        echo "Documentation index not found at: $DOCS_INDEX"
    fi
}

# Main menu
if [ "$1" == "admin" ]; then
    launch_admin
elif [ "$1" == "starterkit" ]; then
    launch_starterkit
elif [ "$1" == "docs" ]; then
    launch_docs
else
    echo "Usage: $0 [admin|starterkit|docs]"
    echo ""
    echo "Options:"
    echo "  admin      - Launch Admin version (port 3000)"
    echo "  starterkit - Launch Starterkit version (port 3001)"
    echo "  docs       - Open documentation in browser"
    echo ""
    echo "Examples:"
    echo "  $0 admin      # Launch Admin version"
    echo "  $0 starterkit # Launch Starterkit version"
    echo "  $0 docs       # Open documentation"
    echo ""
    echo -e "${YELLOW}Which version would you like to launch?${NC}"
    echo "1) Admin (recommended - full features)"
    echo "2) Starterkit (minimal version)"
    echo "3) Documentation"
    echo ""
    read -p "Enter choice [1-3]: " choice
    
    case $choice in
        1)
            launch_admin
            ;;
        2)
            launch_starterkit
            ;;
        3)
            launch_docs
            ;;
        *)
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

