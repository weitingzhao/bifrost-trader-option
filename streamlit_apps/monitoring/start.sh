#!/bin/bash
# Start the Streamlit Status Monitor

cd "$(dirname "$0")"
echo "=========================================="
echo "Starting Bifrost Status Monitor"
echo "=========================================="
echo ""
echo "📊 Streamlit Dashboard will open in your browser"
echo "🌐 URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

streamlit run app.py

