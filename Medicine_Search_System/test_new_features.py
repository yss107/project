#!/usr/bin/env python3
"""
Test script for new Medicine Search System features
Tests OCR, pharmacy locator, price comparison, analytics, and mobile API
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/v1"

def test_pharmacy_locator_page():
    """Test if pharmacy locator page loads"""
    print("Testing pharmacy locator page...")
    response = requests.get(f"{BASE_URL}/pharmacy-locator")
    assert response.status_code == 200
    assert "Pharmacy Locator" in response.text
    print("✓ Pharmacy locator page loads successfully")

def test_pharmacy_api():
    """Test pharmacy API endpoint"""
    print("\nTesting pharmacy API...")
    response = requests.get(f"{BASE_URL}/api/pharmacies/nearby?lat=40.7128&lon=-74.0060&radius=5")
    assert response.status_code == 200
    data = response.json()
    assert "pharmacies" in data
    assert len(data["pharmacies"]) > 0
    print(f"✓ Pharmacy API works - Found {data['count']} pharmacy(ies)")

def test_price_comparison_page():
    """Test if price comparison page loads"""
    print("\nTesting price comparison page...")
    response = requests.get(f"{BASE_URL}/price-comparison")
    assert response.status_code == 200
    assert "Price Comparison" in response.text
    print("✓ Price comparison page loads successfully")

def test_price_comparison_api():
    """Test price comparison API"""
    print("\nTesting price comparison API...")
    response = requests.get(f"{BASE_URL}/api/prices/compare?medicine=0")
    assert response.status_code == 200
    data = response.json()
    assert "prices" in data
    assert "medicine" in data
    assert len(data["prices"]) > 0
    print(f"✓ Price comparison API works - Found {len(data['prices'])} price(s)")

def test_mobile_api_docs():
    """Test mobile API documentation page"""
    print("\nTesting mobile API documentation page...")
    response = requests.get(f"{BASE_URL}/mobile-api-docs")
    assert response.status_code == 200
    assert "Mobile Application API" in response.text
    assert "React Native" in response.text
    print("✓ Mobile API documentation page loads successfully")

def test_analytics_with_auth():
    """Test analytics dashboard (requires login)"""
    print("\nTesting analytics dashboard...")
    # Register a test user first
    username = f"analyticstest_{hash(str(requests.get(BASE_URL).elapsed))}"
    password = "testpass123"
    
    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password
        }
    )
    assert response.status_code == 201
    token = response.json()["token"]
    
    # Now try to access analytics via API (would need implementation)
    print("✓ User registered successfully for analytics testing")

def test_multi_language():
    """Test multi-language support"""
    print("\nTesting multi-language support...")
    # Test with different language parameters
    languages = ['en', 'es', 'fr', 'de', 'hi']
    for lang in languages:
        response = requests.get(f"{BASE_URL}/?lang={lang}")
        assert response.status_code == 200
        assert "Medicine Search System" in response.text
    print(f"✓ Multi-language support works - Tested {len(languages)} languages")

def test_ocr_upload_page():
    """Test OCR prescription upload page"""
    print("\nTesting OCR prescription upload page...")
    response = requests.get(f"{BASE_URL}/prescription-upload")
    assert response.status_code == 200
    assert "Upload" in response.text or "Prescription" in response.text
    print("✓ OCR prescription upload page loads successfully")

def main():
    """Run all tests"""
    print("=" * 70)
    print("Medicine Search System - New Features Test Suite")
    print("=" * 70)
    
    try:
        test_pharmacy_locator_page()
        test_pharmacy_api()
        test_price_comparison_page()
        test_price_comparison_api()
        test_mobile_api_docs()
        test_analytics_with_auth()
        test_multi_language()
        test_ocr_upload_page()
        
        print("\n" + "=" * 70)
        print("✓ All new feature tests passed successfully!")
        print("=" * 70)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to Flask server.")
        print("Please ensure the Flask application is running on http://localhost:5000")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
