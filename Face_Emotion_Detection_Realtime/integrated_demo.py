"""
Comprehensive Integration Demo
Shows all features of the Face Emotion Detection system
"""

import sys
import os


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70 + "\n")


def check_dependencies():
    """Check if all dependencies are installed"""
    print_header("Checking Dependencies")
    
    dependencies = {
        'cv2': 'opencv-python',
        'tensorflow': 'tensorflow',
        'numpy': 'numpy',
        'PIL': 'pillow',
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'sklearn': 'scikit-learn',
        'seaborn': 'seaborn'
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed!")
    return True


def check_camera():
    """Check if camera is accessible"""
    print_header("Checking Camera")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("✗ Camera not accessible")
            print("\nTroubleshooting:")
            print("  1. Check if camera is connected")
            print("  2. Grant camera permissions")
            print("  3. Close other apps using camera")
            print("  4. Try different camera index (1, 2, etc.)")
            return False
        
        # Test frame capture
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print("✓ Camera is working!")
            print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
            return True
        else:
            print("✗ Cannot capture frames")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def show_project_info():
    """Display project information"""
    print_header("Face Emotion Detection System")
    
    info = """
    📹 Real-time face emotion detection using device camera
    🎯 7 Emotion Classes: Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise
    🧠 Deep Learning Model: CNN with 3 convolutional blocks
    🖥️  Two Interfaces: Simple OpenCV & Advanced GUI
    📊 Features: Real-time stats, screenshots, emotion tracking
    
    Based on Kaggle Human Face Emotions Dataset
    https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions
    """
    print(info)


def show_features():
    """Display available features"""
    print_header("Available Features")
    
    features = [
        ("Real-time Detection", "Live emotion detection from camera"),
        ("GUI Interface", "User-friendly interface with statistics"),
        ("Model Training", "Train custom models on your data"),
        ("Emotion Tracking", "Track emotions over time"),
        ("Screenshot Capture", "Save moments with detected emotions"),
        ("Confidence Scores", "See prediction confidence levels"),
        ("Multiple Faces", "Detect multiple faces simultaneously"),
        ("Visual Feedback", "Bounding boxes, labels, probability bars")
    ]
    
    for i, (feature, description) in enumerate(features, 1):
        print(f"{i}. {feature}")
        print(f"   {description}\n")


def show_usage_options():
    """Display usage options"""
    print_header("Usage Options")
    
    options = [
        ("Quick Demo", "python3 demo.py", "Test installation & basic features"),
        ("Simple Interface", "python3 emotion_detector.py", "OpenCV-based real-time detection"),
        ("GUI Interface", "python3 emotion_detector_gui.py", "Advanced interface with controls"),
        ("Examples", "python3 examples.py", "Interactive usage examples"),
        ("Train Model", "python3 train_model.py", "Train on Kaggle dataset"),
        ("Structure Test", "python3 test_structure.py", "Verify project structure")
    ]
    
    for i, (name, command, description) in enumerate(options, 1):
        print(f"{i}. {name}")
        print(f"   Command: {command}")
        print(f"   Description: {description}\n")


def show_model_info():
    """Display model architecture info"""
    print_header("Model Architecture")
    
    print("CNN Architecture:")
    print("  Input: 48x48x1 (grayscale)")
    print("  - Conv Block 1: 32 & 64 filters")
    print("  - Conv Block 2: 128 & 128 filters")
    print("  - Conv Block 3: 256 filters")
    print("  - Dense Layers: 512 & 256 units")
    print("  Output: 7 classes (softmax)")
    print()
    print("Training:")
    print("  - Optimizer: Adam")
    print("  - Loss: Categorical Crossentropy")
    print("  - Data Augmentation: Optional")
    print("  - Regularization: Dropout, BatchNorm")
    print()
    print("Performance:")
    print("  - Speed: ~30 FPS")
    print("  - Latency: 20-30ms per face")
    print("  - Model Size: ~10-15 MB")


def show_dataset_info():
    """Display dataset information"""
    print_header("Dataset Information")
    
    print("Source: Kaggle - Human Face Emotions Dataset")
    print("URL: https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions")
    print()
    print("Dataset Structure:")
    print("  - Format: CSV or Image directories")
    print("  - Images: 48x48 grayscale")
    print("  - Classes: 7 emotions")
    print("  - Size: Thousands of labeled examples")
    print()
    print("Emotion Classes:")
    emotions = [
        "0: Angry", "1: Disgust", "2: Fear", "3: Happy",
        "4: Neutral", "5: Sad", "6: Surprise"
    ]
    for emotion in emotions:
        print(f"  {emotion}")


def run_interactive_menu():
    """Run interactive menu"""
    while True:
        print_header("Interactive Menu")
        
        options = [
            "Show Project Information",
            "Show Features",
            "Show Usage Options",
            "Show Model Architecture",
            "Show Dataset Information",
            "Check Dependencies",
            "Check Camera",
            "Run Quick Demo",
            "Exit"
        ]
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        choice = input("\nSelect an option (1-9): ")
        
        if choice == '1':
            show_project_info()
        elif choice == '2':
            show_features()
        elif choice == '3':
            show_usage_options()
        elif choice == '4':
            show_model_info()
        elif choice == '5':
            show_dataset_info()
        elif choice == '6':
            check_dependencies()
        elif choice == '7':
            check_camera()
        elif choice == '8':
            print("\nLaunching demo...")
            try:
                import demo
                demo.main()
            except Exception as e:
                print(f"Error running demo: {e}")
        elif choice == '9':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")


def main():
    """Main function"""
    print("\n" + "="*70)
    print(" "*15 + "FACE EMOTION DETECTION SYSTEM")
    print(" "*20 + "Comprehensive Demo")
    print("="*70)
    
    # Quick system check
    print("\n🔍 Running System Check...")
    
    deps_ok = check_dependencies()
    camera_ok = check_camera()
    
    print("\n" + "="*70)
    print("System Check Results:")
    print(f"  Dependencies: {'✓ Ready' if deps_ok else '✗ Missing'}")
    print(f"  Camera: {'✓ Ready' if camera_ok else '✗ Not Available'}")
    print("="*70)
    
    if deps_ok and camera_ok:
        print("\n✓ System is ready to use!")
        print("\nYou can now:")
        print("  • Run real-time detection")
        print("  • Use the GUI interface")
        print("  • Train your own models")
    else:
        print("\n⚠ System is not fully ready")
        if not deps_ok:
            print("  → Install dependencies: pip install -r requirements.txt")
        if not camera_ok:
            print("  → Check camera connection and permissions")
    
    # Show quick info
    show_project_info()
    
    # Ask if user wants interactive menu
    choice = input("\nWould you like to explore the interactive menu? (y/n): ")
    if choice.lower() == 'y':
        run_interactive_menu()
    else:
        print("\nQuick Start Commands:")
        print("  python3 demo.py                    - Quick demo")
        print("  python3 emotion_detector.py        - Simple interface")
        print("  python3 emotion_detector_gui.py    - GUI interface")
        print("\nFor full documentation, see README.md")
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
