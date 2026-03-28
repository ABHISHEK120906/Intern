import requests

# Login
login_response = requests.post('http://localhost:5000/auth/login', json={
    'email': 'alice@example.com',
    'password': 'password123'
})

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get challenges
    challenges_response = requests.get('http://localhost:5000/security/challenges', headers=headers)
    if challenges_response.status_code == 200:
        challenges = challenges_response.json()['challenges']
        
        # Find SQL Injection challenge
        sql_challenge = None
        for challenge in challenges:
            if challenge.get('type') == 'sql_injection':
                sql_challenge = challenge
                break
        
        if sql_challenge:
            print(f'Testing SQL Injection Challenge: {sql_challenge["title"]}')
            
            # Submit correct SQL injection solution
            submit_response = requests.post(
                f'http://localhost:5000/security/challenges/{sql_challenge["_id"]}/submit',
                headers=headers,
                json={'solution': 'UNION SELECT * FROM users--'}
            )
            
            print(f'Status: {submit_response.status_code}')
            result = submit_response.json()
            print(f'Message: {result["message"]}')
            print(f'Correct: {result["result"]["is_correct"]}')
            print(f'Points: {result["result"]["points_earned"]}')
            if 'new_skills' in result:
                print(f'New Skills: {result["new_skills"]}')
        else:
            print('SQL Injection challenge not found')
else:
    print('Login failed')
