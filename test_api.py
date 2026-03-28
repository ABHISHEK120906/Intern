# Quick Test Script - No Database Required

import requests
import json

BASE_URL = "http://localhost:5000"

def test_api():
    print("=== Smart AI Internship Tracking System - API Test ===")
    print()
    
    # Test 1: Check if server is running
    print("1. Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/test-db")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Flask server is running on http://localhost:5000")
        return
    print()
    
    # Test 2: Register a student
    print("2. Registering a student...")
    student_data = {
        "name": "Test Student",
        "email": "test@student.com",
        "password": "password123",
        "role": "student",
        "phone": "1234567890",
        "bio": "Computer Science student",
        "skills": ["Python", "JavaScript"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=student_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Test 3: Login as student
    print("3. Logging in as student...")
    login_data = {
        "email": "test@student.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        login_result = response.json()
        print(f"Response: {login_result}")
        
        if response.status_code == 200:
            token = login_result.get('access_token')
            print(f"Token received: {token[:20]}...")
            
            # Test 4: Get profile with token
            print("\n4. Testing authenticated endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                profile_response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
                print(f"Status: {profile_response.status_code}")
                print(f"Response: {profile_response.json()}")
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Test Complete ===")
    print("If all tests passed, the system is working correctly!")
    print("Open http://localhost:5000 in your browser to use the web interface.")

if __name__ == "__main__":
    test_api()
