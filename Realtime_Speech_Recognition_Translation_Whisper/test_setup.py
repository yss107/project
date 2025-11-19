#!/usr/bin/env python3
"""
Simple test script to verify the setup without downloading models
Tests imports and basic functionality
"""

import sys
import os

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch: {e}")
        return False
    
    try:
        import transformers
        print(f"✅ Transformers {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Transformers: {e}")
        return False
    
    try:
        import sounddevice
        print(f"✅ sounddevice {sounddevice.__version__}")
    except ImportError as e:
        print(f"❌ sounddevice: {e}")
        return False
    
    try:
        import soundfile
        print(f"✅ soundfile {soundfile.__version__}")
    except ImportError as e:
        print(f"❌ soundfile: {e}")
        return False
    
    try:
        from deep_translator import GoogleTranslator
        print(f"✅ deep-translator")
    except ImportError as e:
        print(f"❌ deep-translator: {e}")
        return False
    
    try:
        import numpy
        print(f"✅ numpy {numpy.__version__}")
    except ImportError as e:
        print(f"❌ numpy: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True


def test_cuda():
    """Test CUDA availability"""
    print("\nTesting CUDA...")
    
    import torch
    
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"CUDA version: {torch.version.cuda}")
    else:
        print("Will use CPU (this is fine, just slower)")
    
    return True


def test_translator():
    """Test translator functionality"""
    print("\nTesting translator...")
    
    try:
        from deep_translator import GoogleTranslator
        
        translator = GoogleTranslator(target='es')
        result = translator.translate("Hello World")
        print(f"Translation test: 'Hello World' -> '{result}'")
        print("✅ Translator working!")
        return True
    except Exception as e:
        print(f"❌ Translator error: {e}")
        return False


def test_audio_devices():
    """Test audio device detection"""
    print("\nTesting audio devices...")
    
    try:
        import sounddevice as sd
        
        devices = sd.query_devices()
        print(f"Found {len(devices)} audio devices")
        
        # Find default input device
        default_input = sd.default.device[0]
        print(f"Default input device: {devices[default_input]['name']}")
        
        print("✅ Audio devices detected!")
        return True
    except Exception as e:
        print(f"⚠️ Audio device warning: {e}")
        print("(This is okay if running headless)")
        return True


def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        "requirements.txt",
        "README.md",
        "realtime_speech_translator.py",
        "batch_transcriber.py",
        "example_usage.py",
        ".env.example",
        "Whisper_Realtime_Demo.ipynb"
    ]
    
    all_exist = True
    for file in required_files:
        path = os.path.join(base_dir, file)
        if os.path.exists(path):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    if all_exist:
        print("\n✅ All files present!")
    
    return all_exist


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 Testing Whisper Real-time Speech Recognition Setup")
    print("="*80 + "\n")
    
    results = []
    
    # Run tests
    results.append(("File Structure", test_file_structure()))
    results.append(("Imports", test_imports()))
    results.append(("CUDA", test_cuda()))
    results.append(("Translator", test_translator()))
    results.append(("Audio Devices", test_audio_devices()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80 + "\n")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. (Optional) Set up W&B: export WANDB_API_KEY=your_key")
        print("3. Run examples: python example_usage.py")
        print("4. Or start real-time: python realtime_speech_translator.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\nTo install dependencies:")
        print("pip install -r requirements.txt")
    print("="*80 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
