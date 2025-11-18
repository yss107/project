#!/usr/bin/env python3
"""
Test script for Medicine Search System
Tests basic functionality of all major features
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/v1"

def test_home_page():
    """Test if home page loads"""
    print("Testing home page...")
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert "Medicine Search System" in response.text
    print("✓ Home page loads successfully")

def test_search_api():
    """Test medicine search API"""
    print("\nTesting search API...")
    response = requests.get(f"{API_URL}/medicines/search?q=paracetamol")
    assert response.status_code == 200
    data = response.json()
    assert "medicines" in data
    assert len(data["medicines"]) > 0
    print(f"✓ Search API works - Found {data['count']} medicine(s)")

def test_registration():
    """Test user registration"""
    print("\nTesting user registration...")
    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "username": f"testuser_{hash(str(requests.get(BASE_URL).elapsed))}",
            "email": f"test_{hash(str(requests.get(BASE_URL).elapsed))}@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert "user" in data
    print(f"✓ User registration works - User ID: {data['user']['id']}")
    return data["token"]

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    # First register a user
    username = f"logintest_{hash(str(requests.get(BASE_URL).elapsed))}"
    password = "testpass123"
    
    requests.post(
        f"{API_URL}/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password
        }
    )
    
    # Now login
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "username": username,
            "password": password
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    print("✓ User login works")
    return data["token"]

def test_saved_search(token):
    """Test saved search functionality"""
    print("\nTesting saved search...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create saved search
    response = requests.post(
        f"{API_URL}/saved-searches",
        headers=headers,
        json={"query": "aspirin", "filters": ""}
    )
    assert response.status_code == 201
    
    # Get saved searches
    response = requests.get(f"{API_URL}/saved-searches", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "saved_searches" in data
    assert len(data["saved_searches"]) > 0
    print(f"✓ Saved search works - {len(data['saved_searches'])} search(es) saved")

def test_interaction_checker():
    """Test drug interaction checker"""
    print("\nTesting drug interaction checker...")
    response = requests.post(
        f"{API_URL}/interactions/check",
        json={"medicine_indices": [0, 1, 2]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "medicines" in data
    assert "interactions" in data
    print(f"✓ Interaction checker works - Found {len(data['interactions'])} interaction(s)")

def test_statistics():
    """Test statistics API"""
    print("\nTesting statistics API...")
    response = requests.get(f"{API_URL}/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_medicines" in data
    assert "total_manufacturers" in data
    print(f"✓ Statistics API works - {data['total_medicines']} medicines, {data['total_manufacturers']} manufacturers")

def test_medicine_detail():
    """Test medicine detail API"""
    print("\nTesting medicine detail API...")
    response = requests.get(f"{API_URL}/medicines/0")
    assert response.status_code == 200
    data = response.json()
    assert "medicine" in data
    print(f"✓ Medicine detail API works - Retrieved: {data['medicine']['name']}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Medicine Search System - Feature Tests")
    print("=" * 60)
    
    try:
        test_home_page()
        test_search_api()
        token = test_registration()
        token2 = test_login()
        test_saved_search(token2)
        test_interaction_checker()
        test_statistics()
        test_medicine_detail()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
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
        return 1

if __name__ == "__main__":
    sys.exit(main())
