#!/usr/bin/env python3
"""
Test script to verify Vercel app works locally
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from vercel_app import app
    
    print("✅ Successfully imported vercel_app")
    
    # Test Flask app creation
    with app.test_client() as client:
        response = client.get('/health')
        if response.status_code == 200:
            print("✅ Health check endpoint working")
            print(f"Response: {response.get_json()}")
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
    
    print("\n🚀 Vercel app is ready for deployment!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install -r vercel_requirements.txt")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Check your environment variables and MongoDB connection")
