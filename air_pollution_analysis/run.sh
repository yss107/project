#!/bin/bash

# Air Pollution Analysis Dashboard - Run Script

echo "🌍 Air Pollution Analysis Dashboard"
echo "===================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed"
    echo "Please install pip for Python 3"
    exit 1
fi

echo "✓ pip3 found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Check if data files exist
if [ ! -f "data/StationData-NY_QueensCollege.txt" ] || [ ! -f "data/StationData-Bogota_SanCristobal.txt" ]; then
    echo "⚠️  Data files not found. Generating sample data..."
    cd data
    python3 generate_sample_data.py
    cd ..
    
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to generate sample data"
        exit 1
    fi
    
    echo "✓ Sample data generated"
    echo ""
fi

# Start the Flask application
echo "🚀 Starting the dashboard..."
echo ""
echo "Dashboard will be available at:"
echo "  → http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
