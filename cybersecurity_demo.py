# Cybersecurity Features Demo Script
# This script demonstrates all the new security features

import requests
import json

BASE_URL = "http://localhost:5000"

def test_cybersecurity_features():
    print("🔒 Smart AI Cybersecurity Internship Tracking System - Demo")
    print("=" * 70)
    
    # Login as cybersecurity student
    print("\n1. 🔐 Login as Cybersecurity Student...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "alice@example.com",
        "password": "password123"
    })
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        token = login_data['access_token']
        print("✅ Login successful!")
        print(f"   User: {login_data['user']['name']}")
        print(f"   Role: {login_data['user']['role']}")
        print(f"   Skills: {', '.join(login_data['user']['profile']['skills'])}")
    else:
        print("❌ Login failed!")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Security Labs
    print("\n2. 🧪 Testing Security Labs...")
    labs_response = requests.get(f"{BASE_URL}/security/labs", headers=headers)
    if labs_response.status_code == 200:
        labs = labs_response.json()['labs']
        print(f"✅ Found {len(labs)} security labs:")
        for lab in labs:
            print(f"   📋 {lab['title']} - {lab['difficulty']} - {lab['duration']}")
            print(f"      Tools: {', '.join(lab['tools'])}")
    else:
        print("❌ Failed to load security labs")
    
    # Test Security Challenges
    print("\n3. 🏆 Testing Security Challenges...")
    challenges_response = requests.get(f"{BASE_URL}/security/challenges", headers=headers)
    if challenges_response.status_code == 200:
        challenges = challenges_response.json()['challenges']
        print(f"✅ Found {len(challenges)} security challenges:")
        for challenge in challenges:
            print(f"   🎯 {challenge['title']} - {challenge['points']} pts - Level {challenge['difficulty_level']}")
    else:
        print("❌ Failed to load security challenges")
    
    # Test Challenge Submission
    print("\n4. 🚀 Testing Challenge Submission...")
    if challenges:
        challenge_id = challenges[0]['_id']
        submit_response = requests.post(
            f"{BASE_URL}/security/challenges/{challenge_id}/submit",
            headers=headers,
            json={"solution": "UNION SELECT * FROM users--"}
        )
        if submit_response.status_code == 200:
            result = submit_response.json()
            print(f"✅ Challenge submitted: {result['message']}")
            print(f"   Points earned: {result['result']['points_earned']}")
            print(f"   New skills: {', '.join(result.get('new_skills', []))}")
        else:
            print("❌ Challenge submission failed")
    
    # Test Kali Linux Tools
    print("\n5. 🐧 Testing Kali Linux Tools...")
    tools_response = requests.get(f"{BASE_URL}/security/kali-tools", headers=headers)
    if tools_response.status_code == 200:
        tools = tools_response.json()
        print("✅ Kali Linux Tools Available:")
        for category, tool_list in tools.items():
            print(f"   📦 {category.replace('_', ' ').upper()}:")
            for tool in tool_list[:2]:  # Show first 2 tools from each category
                print(f"      • {tool['name']}: {tool['description']}")
    else:
        print("❌ Failed to load Kali tools")
    
    # Test Security Assessment
    print("\n6. 🔍 Testing Security Assessment...")
    assessment_response = requests.post(
        f"{BASE_URL}/security/assessment",
        headers=headers,
        json={
            "type": "vulnerability_scan",
            "target_url": "https://example.com"
        }
    )
    if assessment_response.status_code == 200:
        assessment = assessment_response.json()['assessment']
        print(f"✅ Security Assessment Completed:")
        print(f"   📊 Security Score: {assessment['score']}/100")
        print(f"   🔍 Findings: {len(assessment['results']['findings'])}")
        for finding in assessment['results']['findings']:
            print(f"      • {finding['severity']}: {finding['issue']}")
    else:
        print("❌ Security assessment failed")
    
    # Test Security Certifications
    print("\n7. 🎓 Testing Security Certifications...")
    certs_response = requests.get(f"{BASE_URL}/security/certifications", headers=headers)
    if certs_response.status_code == 200:
        certs_data = certs_response.json()
        print(f"✅ Security Certifications:")
        print(f"   📜 User Certifications: {len(certs_data['user_certifications'])}")
        for cert in certs_data['user_certifications']:
            print(f"      • {cert['name']} ({cert['provider']})")
        print(f"   📚 Available Certifications: {len(certs_data['available_certifications'])}")
        for cert in certs_data['available_certifications'][:2]:  # Show first 2
            print(f"      • {cert['name']} - {cert['level']} - {cert['estimated_hours']}h")
    else:
        print("❌ Failed to load certifications")
    
    # Test Threat Intelligence (Admin only)
    print("\n8. 🚨 Testing Threat Intelligence...")
    # Login as admin
    admin_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@placementsystem.com",
        "password": "admin123"
    })
    
    if admin_login.status_code == 200:
        admin_token = admin_login.json()['access_token']
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        threat_response = requests.get(f"{BASE_URL}/security/threat-intel", headers=admin_headers)
        if threat_response.status_code == 200:
            threat_data = threat_response.json()
            print("✅ Threat Intelligence Dashboard:")
            print(f"   🎯 Active Threats: {threat_data['security_metrics']['active_threats']}")
            print(f"   📊 Security Score: {threat_data['security_metrics']['security_score']}%")
            print(f"   🚨 Current Threats:")
            for threat in threat_data['current_threats']:
                print(f"      • {threat['type']} - {threat['severity']} - {threat['description']}")
        else:
            print("❌ Failed to load threat intelligence")
    else:
        print("⚠️  Admin login failed - skipping threat intelligence test")
    
    print("\n" + "=" * 70)
    print("🎉 Cybersecurity Features Demo Complete!")
    print("\n🌐 Open http://localhost:5000 in your browser to try the full interface")
    print("👤 Login Credentials:")
    print("   🎓 Student (Cybersecurity): alice@example.com / password123")
    print("   🎓 Student (Ethical Hacker): charlie@example.com / password123")
    print("   🏢 Company (Security): bob@example.com / password123")
    print("\n🔥 New Security Features to Try:")
    print("   • Hands-on Security Labs with Nmap, Wireshark, Metasploit")
    print("   • Capture The Flag (CTF) Challenges")
    print("   • Security Assessment Tools")
    print("   • Kali Linux Tools Integration")
    print("   • Security Certifications Tracking (CEH, OSCP, CISSP)")
    print("   • Threat Intelligence Dashboard (Admin)")
    print("=" * 70)

if __name__ == "__main__":
    test_cybersecurity_features()
