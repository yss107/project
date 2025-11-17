#!/usr/bin/env python3
"""
Test script for Face Emotion Detection Web Interface
Tests the structure and components without requiring camera or full dependencies
"""

import sys
import os

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        'web_app.py',
        'templates/index.html',
        'static/style.css',
        'emotion_detector.py',
        'requirements.txt',
        'README.md',
        'WEB_INTERFACE_GUIDE.md',
        'start_web.sh'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_exist = False
    
    return all_exist

def test_html_structure():
    """Test HTML file for key components"""
    print("\nTesting HTML structure...")
    
    with open('templates/index.html', 'r') as f:
        html_content = f.read()
    
    required_elements = [
        ('Socket.IO', 'socket.io' in html_content),
        ('Chart.js', 'chart.js' in html_content),
        ('Video Feed', 'videoFeed' in html_content),
        ('Emotion Display', 'emotionDisplay' in html_content),
        ('Start Button', 'startBtn' in html_content),
        ('Charts', 'timelineChart' in html_content and 'distributionChart' in html_content),
        ('WebSocket Connection', 'socket.on' in html_content),
        ('Emotion Bars', 'emotionBars' in html_content),
    ]
    
    all_present = True
    for name, condition in required_elements:
        if condition:
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} - MISSING")
            all_present = False
    
    return all_present

def test_web_app_structure():
    """Test web_app.py for key components"""
    print("\nTesting web_app.py structure...")
    
    with open('web_app.py', 'r') as f:
        code = f.read()
    
    required_components = [
        ('Flask Import', 'from flask import Flask' in code),
        ('SocketIO Import', 'from flask_socketio import SocketIO' in code),
        ('EmotionDetector', 'EmotionDetector' in code),
        ('Video Feed Route', '@app.route(\'/video_feed\')' in code),
        ('Start Camera API', '@app.route(\'/api/start_camera\'' in code),
        ('Stop Camera API', '@app.route(\'/api/stop_camera\'' in code),
        ('Stats API', '@app.route(\'/api/stats\')' in code),
        ('Reset API', '@app.route(\'/api/reset_stats\'' in code),
        ('WebSocket Handlers', '@socketio.on' in code),
        ('Main Function', 'def main():' in code),
    ]
    
    all_present = True
    for name, condition in required_components:
        if condition:
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} - MISSING")
            all_present = False
    
    return all_present

def test_documentation():
    """Test documentation files"""
    print("\nTesting documentation...")
    
    docs_complete = True
    
    # Check README
    with open('README.md', 'r') as f:
        readme = f.read()
    
    readme_items = [
        ('Web Interface Section', 'Web Interface' in readme or 'web interface' in readme.lower()),
        ('Web App Usage', 'web_app.py' in readme),
        ('Port 5000', '5000' in readme),
        ('Features Listed', '🎨' in readme or 'Modern' in readme),
    ]
    
    for name, condition in readme_items:
        if condition:
            print(f"  ✓ README: {name}")
        else:
            print(f"  ✗ README: {name} - MISSING")
            docs_complete = False
    
    # Check Web Interface Guide
    if os.path.exists('WEB_INTERFACE_GUIDE.md'):
        with open('WEB_INTERFACE_GUIDE.md', 'r') as f:
            guide = f.read()
        
        if len(guide) > 1000:
            print(f"  ✓ WEB_INTERFACE_GUIDE.md (comprehensive)")
        else:
            print(f"  ✗ WEB_INTERFACE_GUIDE.md (incomplete)")
            docs_complete = False
    
    return docs_complete

def test_requirements():
    """Test requirements.txt for web dependencies"""
    print("\nTesting requirements.txt...")
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
    
    required_deps = [
        ('Flask', 'flask' in requirements.lower()),
        ('Flask-SocketIO', 'flask-socketio' in requirements.lower()),
        ('Python-SocketIO', 'python-socketio' in requirements.lower()),
        ('OpenCV', 'opencv' in requirements.lower()),
        ('NumPy', 'numpy' in requirements.lower()),
    ]
    
    all_present = True
    for name, condition in required_deps:
        if condition:
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} - MISSING")
            all_present = False
    
    return all_present

def test_css_and_styling():
    """Test CSS and visual elements"""
    print("\nTesting CSS and styling...")
    
    with open('templates/index.html', 'r') as f:
        html = f.read()
    
    style_features = [
        ('Gradient Background', 'linear-gradient' in html),
        ('Animations', '@keyframes' in html or 'animation:' in html),
        ('Responsive Design', '@media' in html),
        ('Glassmorphism', 'backdrop-filter' in html or 'blur' in html),
        ('Emotion Colors', 'emotion-angry' in html or '#ff4444' in html),
    ]
    
    all_present = True
    for name, condition in style_features:
        if condition:
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} - MISSING")
            all_present = False
    
    return all_present

def main():
    """Run all tests"""
    print("=" * 60)
    print("Face Emotion Detection Web Interface - Test Suite")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("File Structure", test_file_structure()))
    results.append(("HTML Structure", test_html_structure()))
    results.append(("Web App Code", test_web_app_structure()))
    results.append(("Documentation", test_documentation()))
    results.append(("Requirements", test_requirements()))
    results.append(("CSS & Styling", test_css_and_styling()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Web interface is ready to use.")
        print("\nTo start the web interface, run:")
        print("  python web_app.py")
        print("\nThen open: http://localhost:5000")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
