# Quick Test Script for Challenge Submission
import requests

# First login to get token
login_response = requests.post("http://localhost:5000/auth/login", json={
    "email": "alice@example.com",
    "password": "password123"
})

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get challenges
    challenges_response = requests.get("http://localhost:5000/security/challenges", headers=headers)
    if challenges_response.status_code == 200:
        challenges = challenges_response.json()['challenges']
        if challenges:
            challenge_id = challenges[0]['_id']
            print(f"Testing challenge: {challenges[0]['title']}")
            
            # Submit challenge
            submit_response = requests.post(
                f"http://localhost:5000/security/challenges/{challenge_id}/submit",
                headers=headers,
                json={"solution": "UNION SELECT * FROM users--"}
            )
            
            print(f"Status: {submit_response.status_code}")
            print(f"Response: {submit_response.text}")
        else:
            print("No challenges found")
    else:
        print("Failed to get challenges")
else:
    print("Login failed")
