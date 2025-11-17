"""
Basic tests for Face Emotion Detection project
Tests code structure and logic without requiring full dependencies
"""

import sys
import os

def test_file_structure():
    """Test if all required files exist"""
    print("Testing file structure...")
    required_files = [
        'emotion_detector.py',
        'emotion_detector_gui.py',
        'train_model.py',
        'demo.py',
        'requirements.txt',
        'README.md',
        'setup.sh'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (missing)")
            all_exist = False
    
    return all_exist


def test_imports():
    """Test if Python files can be imported (syntax check)"""
    print("\nTesting Python file syntax...")
    
    try:
        import py_compile
        files_to_check = [
            'emotion_detector.py',
            'emotion_detector_gui.py',
            'train_model.py',
            'demo.py'
        ]
        
        all_valid = True
        for file in files_to_check:
            try:
                py_compile.compile(file, doraise=True)
                print(f"  ✓ {file}")
            except py_compile.PyCompileError as e:
                print(f"  ✗ {file}: {e}")
                all_valid = False
        
        return all_valid
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_requirements():
    """Test if requirements.txt is valid"""
    print("\nTesting requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.readlines()
        
        print(f"  ✓ Found {len(requirements)} dependencies:")
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                print(f"    - {req}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_readme():
    """Test if README.md exists and has content"""
    print("\nTesting README.md...")
    
    try:
        with open('README.md', 'r') as f:
            content = f.read()
        
        required_sections = [
            'Installation',
            'Usage',
            'Features',
            'Training'
        ]
        
        all_present = True
        for section in required_sections:
            if section.lower() in content.lower():
                print(f"  ✓ Section '{section}' present")
            else:
                print(f"  ✗ Section '{section}' missing")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_code_structure():
    """Test if main classes and functions are defined"""
    print("\nTesting code structure...")
    
    try:
        # Read emotion_detector.py
        with open('emotion_detector.py', 'r') as f:
            content = f.read()
        
        required_items = [
            'class EmotionDetector',
            'def create_model',
            'def detect_faces',
            'def predict_emotion',
            'def run_realtime_detection'
        ]
        
        all_present = True
        for item in required_items:
            if item in content:
                print(f"  ✓ {item}")
            else:
                print(f"  ✗ {item} (missing)")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Face Emotion Detection - Basic Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_imports),
        ("Requirements", test_requirements),
        ("README Documentation", test_readme),
        ("Code Structure", test_code_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✓ All tests passed! Project structure is valid.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run demo: python3 demo.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
