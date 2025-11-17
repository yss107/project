#!/bin/bash
# Setup script for Face Emotion Detection project

echo "======================================================"
echo "Face Emotion Detection - Setup Script"
echo "======================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Install dependencies
echo ""
echo "Installing dependencies..."
echo "This may take a few minutes..."
echo ""

pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "======================================================"
echo "Setup complete!"
echo "======================================================"
echo ""
echo "Next steps:"
echo "1. Test the installation: python3 demo.py"
echo "2. Run simple interface: python3 emotion_detector.py"
echo "3. Run GUI interface: python3 emotion_detector_gui.py"
echo "4. Train your model: python3 train_model.py"
echo ""
echo "Note: Make sure you have a webcam connected!"
echo "======================================================"
