#!/bin/bash
# Launch Bifrost Portal UI (Skote Starterkit-based)
# This script launches the portal UI for development and testing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PORTAL_UI_DIR="$PROJECT_ROOT/app_portal"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Bifrost Portal UI Launcher"
echo "=========================================="
echo ""

# Check if portal UI directory exists
if [ ! -d "$PORTAL_UI_DIR" ]; then
    echo -e "${RED}❌ Error: Portal UI directory not found: $PORTAL_UI_DIR${NC}"
    exit 1
fi

cd "$PORTAL_UI_DIR"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found in portal UI directory${NC}"
    echo "   Please ensure Starterkit code has been copied to app_portal/"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    echo ""
    npm install
    echo ""
fi

# Check for config.env
if [ ! -f "config.env" ]; then
    echo -e "${YELLOW}⚠️  config.env not found, creating default...${NC}"
    cat > config.env << 'EOF'
PORT=4100
NODE_ENV=development
DATABASE_LOCAL=mongodb+srv://themesbrand:themesbrand@cluster0.abxzaou.mongodb.net/test
EOF
    echo "   Created default config.env"
else
    echo "✅ Using existing config.env"
fi

# Read port from config.env or use default
DEFAULT_PORT=$(grep -E "^PORT=" config.env 2>/dev/null | cut -d '=' -f2 | tr -d ' ' || echo "4100")
PORT=$DEFAULT_PORT

# Function to check if port is in use
check_port() {
    local port=$1
    lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to update config.env port
update_config_port() {
    local new_port=$1
    if [ -f "config.env" ]; then
        # Create backup
        cp config.env config.env.backup 2>/dev/null || true
        # Update port in config.env
        if grep -q "^PORT=" config.env; then
            # macOS sed requires different syntax
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s/^PORT=.*/PORT=$new_port/" config.env
            else
                sed -i "s/^PORT=.*/PORT=$new_port/" config.env
            fi
        else
            echo "PORT=$new_port" >> config.env
        fi
    fi
}

# Check if port is already in use
if check_port $PORT; then
    echo -e "${YELLOW}⚠️  Port $PORT is already in use${NC}"
    
    # Try to find what's using the port
    PID=$(lsof -ti:$PORT 2>/dev/null | head -1)
    if [ ! -z "$PID" ]; then
        PROCESS=$(ps -p $PID -o comm= 2>/dev/null || echo "unknown")
        echo "   Process using port: $PROCESS (PID: $PID)"
    fi
    
    echo ""
    echo "Options:"
    echo "  1) Use a different port (recommended: 4200)"
    echo "  2) Kill the existing process on port $PORT"
    echo "  3) Exit and manually stop the process"
    echo ""
    read -p "Enter choice [1-3] (default: 1): " choice
    choice=${choice:-1}
    
    case $choice in
        1)
            # Use alternative port
            ALTERNATIVE_PORT=4200
            # Check if alternative port is also in use
            if check_port $ALTERNATIVE_PORT; then
                echo -e "${RED}Port $ALTERNATIVE_PORT is also in use. Please free a port manually.${NC}"
                exit 1
            fi
            PORT=$ALTERNATIVE_PORT
            echo -e "${GREEN}✅ Using alternative port: $PORT${NC}"
            update_config_port $PORT
            echo "   Updated config.env to use port $PORT"
            ;;
        2)
            # Kill existing process
            if [ ! -z "$PID" ]; then
                echo -e "${YELLOW}Killing process $PID...${NC}"
                kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
                sleep 2
                if check_port $PORT; then
                    echo -e "${RED}Failed to kill process. Please stop it manually.${NC}"
                    exit 1
                else
                    echo -e "${GREEN}✅ Process stopped. Using port $PORT${NC}"
                fi
            else
                echo -e "${RED}Could not find process to kill.${NC}"
                exit 1
            fi
            ;;
        3)
            echo "Exiting. Please stop the process on port $PORT manually."
            exit 1
            ;;
        *)
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

# Double-check port is available before starting
if check_port $PORT; then
    echo -e "${RED}❌ Error: Port $PORT is still in use. Cannot start server.${NC}"
    exit 1
fi

# Read final port from config.env to ensure we have the correct value
FINAL_PORT=$(grep -E "^PORT=" config.env 2>/dev/null | cut -d '=' -f2 | tr -d ' ' || echo "$PORT")
if check_port $FINAL_PORT; then
    echo -e "${RED}❌ Error: Port $FINAL_PORT is still in use. Cannot start server.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Starting Bifrost Portal UI on http://localhost:${FINAL_PORT}${NC}"
echo ""
echo -e "${BLUE}Portal UI Information:${NC}"
echo "  - Location: $PORTAL_UI_DIR"
echo "  - Port: $FINAL_PORT"
echo "  - Environment: $(grep -E "^NODE_ENV=" config.env 2>/dev/null | cut -d '=' -f2 | tr -d ' ' || echo "development")"
echo ""
echo -e "${YELLOW}Note:${NC}"
echo "  - This is the Node.js/Express version (Starterkit)"
echo "  - For Vue.js conversion, see app_portal/README.md"
echo "  - MongoDB connection may fail (OK for UI viewing)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "=========================================="
echo ""

# Start the server
npm start

