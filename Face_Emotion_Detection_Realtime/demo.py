"""
Demo script for Face Emotion Detection
Quick test of the emotion detection system
"""

import cv2
import numpy as np
from emotion_detector import EmotionDetector


def test_basic_functionality():
    """Test basic functionality of the emotion detector"""
    print("=" * 60)
    print("Face Emotion Detection - Demo")
    print("=" * 60)
    print()
    
    # Initialize detector
    print("Initializing emotion detector...")
    detector = EmotionDetector()
    print("✓ Detector initialized successfully")
    print(f"✓ Model loaded with {len(detector.emotions)} emotion classes")
    print(f"  Emotions: {', '.join(detector.emotions)}")
    print()
    
    # Test face detection
    print("Testing face detection...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ Error: Cannot access camera")
        print("  Please check:")
        print("  - Camera is connected")
        print("  - Camera permissions are granted")
        print("  - No other application is using the camera")
        return False
    
    print("✓ Camera opened successfully")
    
    # Test a few frames
    print("\nTesting frame capture...")
    success_count = 0
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            success_count += 1
    
    cap.release()
    
    if success_count == 5:
        print(f"✓ Successfully captured {success_count}/5 frames")
    else:
        print(f"⚠ Warning: Only captured {success_count}/5 frames")
    
    print()
    print("=" * 60)
    print("Demo complete! All basic functionality working.")
    print()
    print("Next steps:")
    print("1. Run 'python emotion_detector.py' for simple interface")
    print("2. Run 'python emotion_detector_gui.py' for GUI interface")
    print("3. Run 'python train_model.py' to train your own model")
    print("=" * 60)
    
    return True


def show_model_architecture():
    """Display model architecture information"""
    print("\n" + "=" * 60)
    print("Model Architecture Information")
    print("=" * 60)
    
    detector = EmotionDetector()
    
    print("\nModel Summary:")
    detector.model.summary()
    
    print("\n" + "=" * 60)


def main():
    """Main demo function"""
    print("Face Emotion Detection System - Demo Script\n")
    
    # Test basic functionality
    success = test_basic_functionality()
    
    if success:
        # Ask if user wants to see model architecture
        response = input("\nWould you like to see the model architecture? (y/n): ")
        if response.lower() == 'y':
            show_model_architecture()
        
        # Ask if user wants to start real-time detection
        response = input("\nWould you like to start real-time detection now? (y/n): ")
        if response.lower() == 'y':
            print("\nStarting real-time emotion detection...")
            print("Press 'q' to quit\n")
            detector = EmotionDetector()
            detector.run_realtime_detection()


if __name__ == "__main__":
    main()
