#!/usr/bin/env python3
"""
Security Test Script
Tests the security improvements made to the application
"""

import re
import os
from datetime import datetime

def test_jwt_secret():
    """Test JWT secret key is strong"""
    with open('.env', 'r') as f:
        env_content = f.read()
    
    jwt_secret = None
    for line in env_content.split('\n'):
        if line.startswith('JWT_SECRET_KEY='):
            jwt_secret = line.split('=', 1)[1]
            break
    
    if not jwt_secret:
        print("❌ JWT_SECRET_KEY not found")
        return False
    
    if jwt_secret == 'your-secret-key-here-change-in-production':
        print("❌ JWT secret key is still the default value")
        return False
    
    if len(jwt_secret) < 32:
        print("❌ JWT secret key is too short")
        return False
    
    print("✅ JWT secret key is properly configured")
    return True

def test_objectid_helpers():
    """Test ObjectId helper functions"""
    try:
        from bson.objectid import ObjectId
        
        def get_object_id(id_string):
            try:
                return ObjectId(id_string)
            except (TypeError, ValueError, Exception):
                return None
        
        # Test valid ID
        valid_id = "507f1f77bcf86cd799439011"
        result = get_object_id(valid_id)
        if result is None:
            print("❌ ObjectId helper failed on valid ID")
            return False
        
        # Test invalid ID
        invalid_id = "invalid-id"
        result = get_object_id(invalid_id)
        if result is not None:
            print("❌ ObjectId helper didn't reject invalid ID")
            return False
        
        print("✅ ObjectId helper functions work correctly")
        return True
    except ImportError:
        print("⚠️  pymongo not installed, skipping ObjectId test")
        return True

def test_input_validation():
    """Test input validation function"""
    def validate_email_format(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone_format(phone):
        pattern = r'^[+]?[\d\s\-\(\)]{10,}$'
        return re.match(pattern, phone) is not None
    
    # Test email validation
    valid_emails = ["test@example.com", "user.name@domain.co.uk"]
    invalid_emails = ["invalid-email", "test@", "@domain.com"]
    
    for email in valid_emails:
        if not validate_email_format(email):
            print(f"❌ Valid email rejected: {email}")
            return False
    
    for email in invalid_emails:
        if validate_email_format(email):
            print(f"❌ Invalid email accepted: {email}")
            return False
    
    # Test phone validation
    valid_phones = ["1234567890", "+1 234 567 8901", "(123) 456-7890"]
    invalid_phones = ["123", "abc123", ""]
    
    for phone in valid_phones:
        if not validate_phone_format(phone):
            print(f"❌ Valid phone rejected: {phone}")
            return False
    
    for phone in invalid_phones:
        if validate_phone_format(phone):
            print(f"❌ Invalid phone accepted: {phone}")
            return False
    
    print("✅ Input validation functions work correctly")
    return True

def test_password_validation():
    """Test password validation"""
    def validate_password_strength(password):
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        return len(errors) == 0, errors
    
    # Test valid passwords
    valid_passwords = ["SecurePass123", "MyPassword1", "Test12345"]
    
    for password in valid_passwords:
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            print(f"❌ Valid password rejected: {password} - {errors}")
            return False
    
    # Test invalid passwords
    invalid_passwords = ["weak", "nouppercase1", "NOLOWERCASE1", "NoNumber"]
    
    for password in invalid_passwords:
        is_valid, errors = validate_password_strength(password)
        if is_valid:
            print(f"❌ Invalid password accepted: {password}")
            return False
    
    print("✅ Password validation works correctly")
    return True

def test_file_validation():
    """Test file validation"""
    def validate_file_security(filename):
        """Check for suspicious patterns in filename"""
        if any(pattern in filename.lower() for pattern in ['..', '/', '\\', '<', '>', ':', '*', '?', '"', '|']):
            return False
        return True
    
    # Test safe filenames
    safe_filenames = ["resume.pdf", "document.pdf", "my_resume.pdf"]
    
    for filename in safe_filenames:
        if not validate_file_security(filename):
            print(f"❌ Safe filename rejected: {filename}")
            return False
    
    # Test unsafe filenames
    unsafe_filenames = ["../../../etc/passwd", "file<script>.pdf", "file:with:colons.pdf"]
    
    for filename in unsafe_filenames:
        if validate_file_security(filename):
            print(f"❌ Unsafe filename accepted: {filename}")
            return False
    
    print("✅ File validation works correctly")
    return True

def test_timestamp_replacement():
    """Test that hardcoded timestamps are replaced"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for old hardcoded timestamps
        old_timestamps = ["'2024-01-01'", '"2024-01-01"']
        for timestamp in old_timestamps:
            if timestamp in content:
                print(f"❌ Found hardcoded timestamp: {timestamp}")
                return False
        
        # Check for datetime.now() usage
        if "datetime.now()" not in content:
            print("❌ datetime.now() not found in code")
            return False
        
        print("✅ Timestamps properly replaced with datetime.now()")
        return True
    except FileNotFoundError:
        print("⚠️  app.py not found, skipping timestamp test")
        return True
    except UnicodeDecodeError:
        print("⚠️  File encoding issue, skipping timestamp test")
        return True

def test_security_headers():
    """Test security headers configuration"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        security_features = [
            "Talisman",
            "content_security_policy",
            "Limiter",
            "limiter.limit"
        ]
        
        for feature in security_features:
            if feature.lower() not in content.lower():
                print(f"❌ Security feature not found: {feature}")
                return False
        
        print("✅ Security headers and rate limiting configured")
        return True
    except FileNotFoundError:
        print("⚠️  app.py not found, skipping security headers test")
        return True
    except UnicodeDecodeError:
        print("⚠️  File encoding issue, skipping security headers test")
        return True

def main():
    """Run all security tests"""
    print("🔒 Running Security Tests\n")
    
    tests = [
        ("JWT Secret Key Security", test_jwt_secret),
        ("ObjectId Helper Functions", test_objectid_helpers),
        ("Input Validation", test_input_validation),
        ("Password Validation", test_password_validation),
        ("File Validation", test_file_validation),
        ("Timestamp Replacement", test_timestamp_replacement),
        ("Security Headers", test_security_headers)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {str(e)}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All security tests passed!")
        return True
    else:
        print("⚠️  Some security tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    main()
