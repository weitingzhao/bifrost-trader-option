#!/bin/bash
# Install Python dependencies for Bifrost
# Run this from the project root directory

set -e

echo "=========================================="
echo "Bifrost Dependency Installation"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Dependencies installed successfully!"
echo "=========================================="
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
echo "Next steps:"
echo "1. Set up PostgreSQL + TimescaleDB (see docs/database/HOME.md)"
echo "2. Create .env file from .env.example"
echo "3. Run database migrations"
echo "4. Test connections"

