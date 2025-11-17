#!/bin/bash

# Quick start script for Face Emotion Detection Web Interface
# This script installs dependencies and runs the web application

echo "=================================================="
echo "  Face Emotion Detection - Web Interface"
echo "=================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Check if in correct directory
if [ ! -f "web_app.py" ]; then
    echo "❌ Error: web_app.py not found!"
    echo "Please run this script from the Face_Emotion_Detection_Realtime directory."
    exit 1
fi

echo "Installing dependencies..."
echo ""

# Install requirements
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
    echo ""
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "=================================================="
echo "  Starting Web Server..."
echo "=================================================="
echo ""
echo "🌐 Open your browser and navigate to:"
echo "   http://localhost:5000"
echo ""
echo "💡 Press CTRL+C to stop the server"
echo ""
echo "=================================================="
echo ""

# Run the web application
python3 web_app.py
