# Demo Script for Smart AI Internship Tracking System

# This script demonstrates the key features of the system
# Run these commands in PowerShell or Command Prompt

echo "=== Smart AI Internship Tracking System Demo ==="
echo ""

# 1. Test API Health
echo "1. Testing API Health..."
curl -s http://localhost:5000/test-db
echo ""
echo ""

# 2. Register a Student User
echo "2. Registering a Student User..."
curl -X POST http://localhost:5000/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "role": "student",
    "phone": "1234567890",
    "bio": "Computer Science student passionate about AI",
    "skills": ["Python", "JavaScript", "React", "SQL"]
  }'
echo ""
echo ""

# 3. Register a Company User
echo "3. Registering a Company User..."
curl -X POST http://localhost:5000/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "name": "Tech Corp",
    "email": "tech@corp.com",
    "password": "password123",
    "role": "company",
    "phone": "0987654321",
    "bio": "Leading technology company"
  }'
echo ""
echo ""

# 4. Student Login
echo "4. Student Login..."
$studentLogin = curl -X POST http://localhost:5000/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
echo $studentLogin
echo ""

# Extract token (simplified for demo)
$studentToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9" # This would be extracted from response

# 5. Company Login
echo "5. Company Login..."
$companyLogin = curl -X POST http://localhost:5000/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "tech@corp.com",
    "password": "password123"
  }'
echo $companyLogin
echo ""

# 6. Create Internship (Company)
echo "6. Creating Internship..."
curl -X POST http://localhost:5000/internships `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $companyToken" `
  -d '{
    "title": "Frontend Developer Intern",
    "description": "Join our team to build amazing web applications",
    "location": "Remote",
    "duration": "3 months",
    "stipend": "$1000/month",
    "skills_required": ["React", "JavaScript", "CSS", "HTML"],
    "type": "internship",
    "remote": true,
    "requirements": ["Basic React knowledge", "Good communication skills"],
    "benefits": ["Flexible hours", "Learning opportunities", "Certificate"]
  }'
echo ""
echo ""

# 7. Get Internships (Student)
echo "7. Getting Available Internships..."
curl -X GET http://localhost:5000/internships `
  -H "Authorization: Bearer $studentToken"
echo ""
echo ""

# 8. Apply for Internship (Student)
echo "8. Applying for Internship..."
curl -X POST http://localhost:5000/applications `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $studentToken" `
  -d '{
    "internship_id": "internship_id_here",
    "cover_letter": "I am excited to apply for this opportunity..."
  }'
echo ""
echo ""

# 9. Get AI Job Recommendations (Student)
echo "9. Getting AI Job Recommendations..."
curl -X GET http://localhost:5000/ai/job-recommendations `
  -H "Authorization: Bearer $studentToken"
echo ""
echo ""

# 10. Get Placement Readiness Score (Student)
echo "10. Getting Placement Readiness Score..."
curl -X GET http://localhost:5000/ai/placement-readiness-score `
  -H "Authorization: Bearer $studentToken"
echo ""
echo ""

# 11. Skill Gap Analysis (Student)
echo "11. Performing Skill Gap Analysis..."
curl -X POST http://localhost:5000/ai/skill-gap-analysis `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $studentToken" `
  -d '{
    "target_job_skills": ["Python", "React", "Node.js", "AWS", "Docker"]
  }'
echo ""
echo ""

# 12. View Applications (Student)
echo "12. Viewing Student Applications..."
curl -X GET http://localhost:5000/applications `
  -H "Authorization: Bearer $studentToken"
echo ""
echo ""

# 13. View Applications (Company)
echo "13. Viewing Company Applications..."
curl -X GET http://localhost:5000/applications `
  -H "Authorization: Bearer $companyToken"
echo ""
echo ""

# 14. Update Application Status (Company)
echo "14. Updating Application Status..."
curl -X PUT http://localhost:5000/applications/application_id/status `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $companyToken" `
  -d '{
    "status": "shortlisted"
  }'
echo ""
echo ""

echo "=== Demo Complete ==="
echo "Frontend available at: http://localhost:5000"
echo "Try the web interface for full experience!"
echo ""

# Note: This is a simplified demo script
# In a real scenario, you would:
# 1. Extract actual tokens from login responses
# 2. Use real internship IDs from the create response
# 3. Handle errors and validation
# 4. Use proper JSON parsing
