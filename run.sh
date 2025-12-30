#!/bin/bash
# Startup script for Bifrost Options Trading Strategy Analyzer

echo "Starting Bifrost Options Trading Strategy Analyzer..."
echo "Make sure IB TWS or IB Gateway is running and logged in!"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Using default configuration."
fi

# Run the application
python3 -m src.main


