#!/usr/bin/env python3
"""
Database Connection Test Script
Test MongoDB connection and basic operations
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test MongoDB connection and basic operations"""
    print("🔍 Testing MongoDB Connection...")
    print("=" * 50)
    
    try:
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ MONGODB_URI not found in .env file")
            return False
        
        print(f"📡 Connecting to MongoDB...")
        print(f"   URI: {mongodb_uri.split('@')[1] if '@' in mongodb_uri else 'Local'}")
        
        # Test connection
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test server connection
        client.admin.command('ping')
        print("✅ MongoDB Connection Successful!")
        
        # Get database info
        db_name = mongodb_uri.split('/')[-1].split('?')[0] if '/' in mongodb_uri else 'test'
        db = client[db_name]
        
        print(f"📊 Database: {db_name}")
        
        # Test basic operations
        test_collection = db.connection_test
        
        # Insert test document
        test_doc = {"test": "connection", "timestamp": "2024-03-28"}
        result = test_collection.insert_one(test_doc)
        print(f"✅ Insert Test: Document ID {result.inserted_id}")
        
        # Find test document
        found_doc = test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Find Test: Document found - {found_doc}")
        
        # Delete test document
        delete_result = test_collection.delete_one({"_id": result.inserted_id})
        print(f"✅ Delete Test: {delete_result.deleted_count} document deleted")
        
        # List collections
        collections = db.list_collection_names()
        print(f"📋 Existing Collections: {len(collections)}")
        for collection in collections[:5]:  # Show first 5
            print(f"   - {collection}")
        
        # Close connection
        client.close()
        print("✅ Connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database Connection Error: {str(e)}")
        print("\n🔧 Possible Solutions:")
        print("1. Check MongoDB URI in .env file")
        print("2. Verify network connection")
        print("3. Check MongoDB credentials")
        print("4. Ensure MongoDB server is running")
        return False

def check_app_dependencies():
    """Check if all required packages are installed"""
    print("\n🔍 Checking Dependencies...")
    print("=" * 30)
    
    required_packages = [
        'flask', 'pymongo', 'python-dotenv', 'bcrypt',
        'jwt', 'werkzeug', 'cors'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All dependencies installed!")
        return True

if __name__ == "__main__":
    print("🚀 CareerTrack AI - Database & Dependencies Check")
    print("=" * 60)
    
    # Check dependencies
    deps_ok = check_app_dependencies()
    
    # Test database
    db_ok = test_database_connection()
    
    print("\n" + "=" * 60)
    if deps_ok and db_ok:
        print("🎉 ALL CHECKS PASSED! Ready for deployment!")
    else:
        print("⚠️  Some issues found. Please fix before deployment.")
    
    print("=" * 60)
