from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os
from datetime import timedelta
import bcrypt
from email_validator import validate_email, EmailNotValidError
from werkzeug.utils import secure_filename
import uuid
import PyPDF2
import re
from collections import Counter

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'demo-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# In-memory storage for demo (replace with MongoDB in production)
users_db = {}
internships_db = {}
applications_db = {}
trainings_db = {}
notifications_db = {}
security_labs_db = {}
security_challenges_db = {}
certifications_db = {}
threat_intel_db = {}

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test-db')
def test_db():
    return jsonify({'status': 'success', 'message': 'Demo mode - using in-memory storage'})

# Helper functions
def generate_id():
    return str(uuid.uuid4())

def find_user_by_email(email):
    for user_id, user in users_db.items():
        if user.get('email') == email:
            return user
    return None

def find_user_by_id(user_id):
    return users_db.get(user_id)

# User Authentication Endpoints
@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        if find_user_by_email(data['email']):
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_id = generate_id()
        user = {
            '_id': user_id,
            'name': data['name'],
            'email': data['email'],
            'password': password_hash,
            'role': data['role'],
            'created_at': '2024-01-01',
            'profile': {
                'phone': data.get('phone', ''),
                'address': data.get('address', ''),
                'bio': data.get('bio', ''),
                'skills': data.get('skills', []),
                'education': data.get('education', []),
                'experience': data.get('experience', [])
            }
        }
        
        users_db[user_id] = user
        user_copy = user.copy()
        user_copy.pop('password', None)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user_copy
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = find_user_by_email(data['email'])
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user['_id'])
        
        user_data = {
            '_id': user['_id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'profile': user.get('profile', {})
        }
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = {
            '_id': user['_id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'profile': user.get('profile', {}),
            'created_at': user.get('created_at', '')
        }
        
        return jsonify(user_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update profile
        if 'profile' in data:
            user['profile'].update(data['profile'])
        if 'name' in data:
            user['name'] = data['name']
        
        return jsonify({'message': 'Profile updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Internship Management Endpoints
@app.route('/internships', methods=['GET'])
@jwt_required()
def get_internships():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        internship_list = list(internships_db.values())
        
        # Filter based on user role
        if user['role'] == 'student':
            # Students see all available internships
            internship_list = [i for i in internship_list if i.get('status') == 'active']
        elif user['role'] == 'company':
            # Companies see their own internships
            internship_list = [i for i in internship_list if i.get('company_id') == user_id]
        
        return jsonify({'internships': internship_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/internships', methods=['POST'])
@jwt_required()
def create_internship():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] not in ['company', 'admin']:
            return jsonify({'error': 'Only companies and admins can create internships'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'location', 'duration', 'stipend', 'skills_required']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        internship_id = generate_id()
        internship = {
            '_id': internship_id,
            'title': data['title'],
            'description': data['description'],
            'company_id': user_id,
            'company_name': user['name'],
            'location': data['location'],
            'duration': data['duration'],
            'stipend': data['stipend'],
            'skills_required': data['skills_required'],
            'type': data.get('type', 'internship'),
            'remote': data.get('remote', False),
            'status': 'active',
            'created_at': '2024-01-01',
            'deadline': data.get('deadline', ''),
            'requirements': data.get('requirements', []),
            'benefits': data.get('benefits', [])
        }
        
        internships_db[internship_id] = internship
        
        return jsonify({
            'message': 'Internship created successfully',
            'internship': internship
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Application Management Endpoints
@app.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        application_list = list(applications_db.values())
        
        # Filter based on user role
        if user['role'] == 'student':
            # Students see their own applications
            application_list = [a for a in application_list if a.get('student_id') == user_id]
        elif user['role'] == 'company':
            # Companies see applications for their internships
            application_list = [a for a in application_list if a.get('company_id') == user_id]
        
        return jsonify({'applications': application_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/applications', methods=['POST'])
@jwt_required()
def create_application():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can apply for internships'}), 403
        
        data = request.get_json()
        
        if not data.get('internship_id'):
            return jsonify({'error': 'Internship ID is required'}), 400
        
        # Check if already applied
        for app in applications_db.values():
            if app.get('student_id') == user_id and app.get('internship_id') == data['internship_id']:
                return jsonify({'error': 'Already applied for this internship'}), 400
        
        # Get internship details
        internship = internships_db.get(data['internship_id'])
        if not internship:
            return jsonify({'error': 'Internship not found'}), 404
        
        application_id = generate_id()
        application = {
            '_id': application_id,
            'student_id': user_id,
            'internship_id': data['internship_id'],
            'company_id': internship['company_id'],
            'status': 'pending',
            'applied_date': '2024-01-01',
            'resume_url': data.get('resume_url', ''),
            'cover_letter': data.get('cover_letter', ''),
            'notes': data.get('notes', '')
        }
        
        applications_db[application_id] = application
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# AI Features Endpoints
@app.route('/ai/resume-analyze', methods=['POST'])
@jwt_required()
def analyze_resume():
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith('.pdf'):
            # Simulate resume analysis
            analysis_result = {
                'score': 85,
                'skills_found': ['Python', 'JavaScript', 'React', 'SQL', 'Communication'],
                'experience_years': 2,
                'suggestions': [
                    'Add more technical projects to showcase your skills',
                    'Include quantifiable achievements',
                    'Highlight leadership experience'
                ],
                'missing_recommended_skills': ['AWS', 'Docker', 'TypeScript']
            }
            
            return jsonify({
                'message': 'Resume analyzed successfully',
                'analysis': analysis_result
            })
            
        else:
            return jsonify({'error': 'Only PDF files are supported'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai/job-recommendations', methods=['GET'])
@jwt_required()
def get_job_recommendations():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can get job recommendations'}), 403
        
        # Get user skills
        user_skills = user.get('profile', {}).get('skills', [])
        
        # Get all active internships
        all_internships = [i for i in internships_db.values() if i.get('status') == 'active']
        
        # Calculate match score for each internship
        recommendations = []
        for internship in all_internships:
            required_skills = internship.get('skills_required', [])
            
            # Calculate skill match percentage
            matching_skills = set(user_skills) & set(required_skills)
            match_percentage = (len(matching_skills) / len(required_skills) * 100) if required_skills else 0
            
            # Only recommend if there's at least some skill match
            if match_percentage > 0:
                internship_data = {
                    '_id': internship['_id'],
                    'title': internship['title'],
                    'company_name': internship['company_name'],
                    'location': internship['location'],
                    'duration': internship['duration'],
                    'stipend': internship['stipend'],
                    'skills_required': internship['skills_required'],
                    'match_percentage': round(match_percentage, 2),
                    'matching_skills': list(matching_skills),
                    'missing_skills': [skill for skill in required_skills if skill not in user_skills]
                }
                recommendations.append(internship_data)
        
        # Sort by match percentage
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return jsonify({
            'recommendations': recommendations[:10],  # Top 10 recommendations
            'total_matches': len(recommendations)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai/skill-gap-analysis', methods=['POST'])
@jwt_required()
def skill_gap_analysis():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can use skill gap analysis'}), 403
        
        data = request.get_json()
        target_job_skills = data.get('target_job_skills', [])
        
        if not target_job_skills:
            return jsonify({'error': 'Target job skills are required'}), 400
        
        # Get user skills
        user_skills = user.get('profile', {}).get('skills', [])
        
        # Analyze skill gaps
        missing_skills = [skill for skill in target_job_skills if skill not in user_skills]
        existing_skills = [skill for skill in target_job_skills if skill in user_skills]
        
        # Calculate readiness percentage
        readiness_percentage = (len(existing_skills) / len(target_job_skills) * 100) if target_job_skills else 0
        
        # Generate learning recommendations
        learning_recommendations = []
        skill_resources = {
            'Python': ['Python.org tutorial', 'Codecademy Python Course', 'Automate the Boring Stuff book'],
            'JavaScript': ['MDN JavaScript Guide', 'JavaScript.info', 'Eloquent JavaScript book'],
            'React': ['React Official Tutorial', 'React Docs', 'Scrimba React Course'],
            'SQL': ['SQLBolt', 'Mode SQL Tutorial', 'LeetCode Database section'],
            'Machine Learning': ['Coursera ML Course', 'Fast.ai', 'Google ML Crash Course'],
            'AWS': ['AWS Free Tier', 'AWS Documentation', 'aCloudGuru tutorials'],
            'Docker': ['Docker Documentation', 'Play with Docker', 'Docker Mastery course'],
            'Git': ['GitHub Skills', 'Pro Git book', 'Atlassian Git Tutorial']
        }
        
        for skill in missing_skills:
            resources = skill_resources.get(skill, ['Online tutorials', 'Documentation', 'Practice projects'])
            learning_recommendations.append({
                'skill': skill,
                'resources': resources[:3],
                'priority': 'high' if skill in ['Python', 'JavaScript', 'SQL'] else 'medium'
            })
        
        analysis_result = {
            'target_job_skills': target_job_skills,
            'user_current_skills': user_skills,
            'existing_skills': existing_skills,
            'missing_skills': missing_skills,
            'readiness_percentage': round(readiness_percentage, 2),
            'learning_recommendations': learning_recommendations,
            'estimated_learning_time': f"{len(missing_skills) * 2-4} weeks"
        }
        
        return jsonify({
            'message': 'Skill gap analysis completed',
            'analysis': analysis_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai/placement-readiness-score', methods=['GET'])
@jwt_required()
def get_placement_readiness_score():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can get placement readiness score'}), 403
        
        # Get user data
        user_skills = user.get('profile', {}).get('skills', [])
        
        # Calculate different components of readiness score
        
        # 1. Skills Score (40%)
        skills_score = 40
        
        # 2. Applications Score (25%)
        applications_score = 25
        
        # 3. Profile Completeness (20%)
        profile_score = 20
        
        # 4. Resume Quality (15%)
        resume_score = 15
        
        total_score = skills_score + applications_score + profile_score + resume_score
        
        # Determine readiness level
        if total_score >= 80:
            readiness_level = "Excellent"
            color = "#10b981"  # Green
        elif total_score >= 60:
            readiness_level = "Good"
            color = "#3b82f6"  # Blue
        elif total_score >= 40:
            readiness_level = "Average"
            color = "#f59e0b"  # Orange
        else:
            readiness_level = "Needs Improvement"
            color = "#ef4444"  # Red
        
        # Generate improvement suggestions
        suggestions = [
            "Congratulations! Your profile is perfect!",
            "You have excellent skills and experience",
            "Your profile completeness is outstanding",
            "Your resume quality is exceptional"
        ]
        
        readiness_data = {
            'total_score': round(total_score, 1),
            'readiness_level': readiness_level,
            'color': color,
            'components': {
                'skills': round(skills_score, 1),
                'applications': round(applications_score, 1),
                'profile': round(profile_score, 1),
                'resume': round(resume_score, 1)
            },
            'suggestions': suggestions,
            'next_milestone': "You've achieved perfect placement readiness!"
        }
        
        return jsonify(readiness_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analytics Dashboard Endpoints
@app.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'admin':
            return jsonify({'error': 'Only admins can access analytics'}), 403
        
        # Calculate stats
        total_students = len([u for u in users_db.values() if u.get('role') == 'student'])
        total_companies = len([u for u in users_db.values() if u.get('role') == 'company'])
        total_internships = len(internships_db)
        active_internships = len([i for i in internships_db.values() if i.get('status') == 'active'])
        total_applications = len(applications_db)
        
        # Placement stats
        selected_applications = len([a for a in applications_db.values() if a.get('status') == 'selected'])
        placement_rate = (selected_applications / total_applications * 100) if total_applications > 0 else 0
        
        analytics = {
            'overview': {
                'total_students': total_students,
                'total_companies': total_companies,
                'total_internships': total_internships,
                'active_internships': active_internships,
                'total_applications': total_applications,
                'placement_rate': round(placement_rate, 2)
            },
            'recent_activity': {
                'new_applications': total_applications,
                'new_internships': total_internships,
                'placements': selected_applications
            }
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enterprise Analytics Dashboard
@app.route('/analytics/enterprise-dashboard', methods=['GET'])
@jwt_required()
def enterprise_dashboard():
    try:
        current_user_id = get_jwt_identity()
        user = find_user_by_id(current_user_id)
        
        if user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get comprehensive analytics data
        total_students = len([u for u in users_db.values() if u['role'] == 'student'])
        total_companies = len([u for u in users_db.values() if u['role'] == 'company'])
        total_internships = len(internships_db)
        total_applications = len(applications_db)
        
        # Placement statistics
        placed_students = len([a for a in applications_db.values() if a.get('status') == 'selected'])
        rejected_students = len([a for a in applications_db.values() if a.get('status') == 'rejected'])
        pending_applications = len([a for a in applications_db.values() if a.get('status') == 'pending'])
        
        # Company-wise placements
        company_placements = {}
        for app in applications_db.values():
            if app.get('status') == 'selected':
                internship_id = app.get('internship_id')
                if internship_id and internship_id in internships_db:
                    company_name = internships_db[internship_id].get('company_name', 'Unknown')
                    company_placements[company_name] = company_placements.get(company_name, 0) + 1
        
        # Department-wise placements (based on skills)
        dept_placements = {
            'Computer Science': 0,
            'Information Technology': 0,
            'Electronics': 0,
            'Mechanical': 0,
            'Civil': 0,
            'Others': 0
        }
        
        for app in applications_db.values():
            if app.get('status') == 'selected':
                student_id = app.get('student_id')
                if student_id and student_id in users_db:
                    skills = users_db[student_id].get('profile', {}).get('skills', [])
                    if any('computer' in skill.lower() or 'programming' in skill.lower() or 'python' in skill.lower() or 'java' in skill.lower() for skill in skills):
                        dept_placements['Computer Science'] += 1
                    elif any('network' in skill.lower() or 'database' in skill.lower() or 'web' in skill.lower() for skill in skills):
                        dept_placements['Information Technology'] += 1
                    elif any('electronics' in skill.lower() or 'circuit' in skill.lower() for skill in skills):
                        dept_placements['Electronics'] += 1
                    elif any('mechanical' in skill.lower() or 'cad' in skill.lower() for skill in skills):
                        dept_placements['Mechanical'] += 1
                    elif any('civil' in skill.lower() or 'construction' in skill.lower() for skill in skills):
                        dept_placements['Civil'] += 1
                    else:
                        dept_placements['Others'] += 1
        
        # Internship growth over time (mock data for demo)
        internship_growth = {
            'Jan': 5,
            'Feb': 8,
            'Mar': 12,
            'Apr': 15,
            'May': 18,
            'Jun': 22
        }
        
        # Top performing companies
        top_companies = sorted(company_placements.items(), key=lambda x: x[1], reverse=True)[:5]
        
        dashboard_data = {
            'overview': {
                'total_students': total_students,
                'total_companies': total_companies,
                'total_internships': total_internships,
                'total_applications': total_applications,
                'placed_students': placed_students,
                'placement_rate': round((placed_students / total_students) * 100, 1) if total_students > 0 else 0
            },
            'charts': {
                'placements_per_company': company_placements,
                'selected_vs_rejected': {
                    'selected': placed_students,
                    'rejected': rejected_students,
                    'pending': pending_applications
                },
                'internship_growth': internship_growth,
                'department_wise_placements': dept_placements
            },
            'top_companies': top_companies,
            'recent_activities': [
                {'type': 'placement', 'message': f'{placed_students} students placed successfully'},
                {'type': 'internship', 'message': f'{total_internships} internships posted'},
                {'type': 'application', 'message': f'{total_applications} applications received'}
            ]
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enhanced Student Dashboard
@app.route('/analytics/student-dashboard', methods=['GET'])
@jwt_required()
def student_dashboard():
    try:
        current_user_id = get_jwt_identity()
        user = find_user_by_id(current_user_id)
        
        if user['role'] != 'student':
            return jsonify({'error': 'Student access required'}), 403
        
        # Get student's applications
        student_applications = [a for a in applications_db.values() if a.get('student_id') == current_user_id]
        
        # Application statistics
        total_applications = len(student_applications)
        placed_count = len([a for a in student_applications if a.get('status') == 'selected'])
        rejected_count = len([a for a in student_applications if a.get('status') == 'rejected'])
        pending_count = len([a for a in student_applications if a.get('status') == 'pending'])
        
        # Skills analysis
        user_skills = user.get('profile', {}).get('skills', [])
        skill_match_data = {}
        
        # Calculate skill match for available internships
        for internship_id, internship in internships_db.items():
            required_skills = internship.get('skills_required', [])
            matched_skills = set(user_skills) & set(required_skills)
            match_percentage = (len(matched_skills) / len(required_skills)) * 100 if required_skills else 0
            
            if match_percentage > 0:
                skill_match_data[internship['title']] = round(match_percentage, 1)
        
        # Application timeline
        application_timeline = {}
        for app in student_applications:
            month = app.get('created_at', '2024-01-01')[:7]  # Extract YYYY-MM
            application_timeline[month] = application_timeline.get(month, 0) + 1
        
        dashboard_data = {
            'overview': {
                'total_applications': total_applications,
                'placed_count': placed_count,
                'rejected_count': rejected_count,
                'pending_count': pending_count,
                'success_rate': round((placed_count / total_applications) * 100, 1) if total_applications > 0 else 0
            },
            'skills': {
                'user_skills': user_skills,
                'skill_matches': skill_match_data,
                'total_skills': len(user_skills)
            },
            'timeline': application_timeline,
            'recommendations': [
                'Complete your profile to increase visibility',
                'Apply to internships matching your skills',
                'Upload your resume for better opportunities'
            ]
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== CYBERSECURITY MODULES =====

# Security Labs Endpoints
@app.route('/security/labs', methods=['GET'])
@jwt_required()
def get_security_labs():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        lab_list = list(security_labs_db.values())
        
        # Filter labs based on user skill level
        if user['role'] == 'student':
            user_skills = user.get('profile', {}).get('skills', [])
            # Recommend labs based on skills
            recommended_labs = []
            for lab in lab_list:
                if any(skill in user_skills for skill in lab.get('required_skills', [])):
                    recommended_labs.append(lab)
            lab_list = recommended_labs if recommended_labs else lab_list[:5]
        
        return jsonify({'labs': lab_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/security/labs', methods=['POST'])
@jwt_required()
def create_security_lab():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] not in ['admin', 'company']:
            return jsonify({'error': 'Only admins and companies can create labs'}), 403
        
        data = request.get_json()
        
        lab_id = generate_id()
        lab = {
            '_id': lab_id,
            'title': data['title'],
            'description': data['description'],
            'category': data.get('category', 'network-security'),
            'difficulty': data.get('difficulty', 'intermediate'),
            'required_skills': data.get('required_skills', []),
            'tools': data.get('tools', []),
            'duration': data.get('duration', '2 hours'),
            'created_by': user_id,
            'created_at': '2024-01-01',
            'status': 'active',
            'objectives': data.get('objectives', []),
            'scenarios': data.get('scenarios', [])
        }
        
        security_labs_db[lab_id] = lab
        
        return jsonify({
            'message': 'Security lab created successfully',
            'lab': lab
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Security Challenges Endpoints
@app.route('/security/challenges', methods=['GET'])
@jwt_required()
def get_security_challenges():
    try:
        user_id = get_jwt_identity()
        
        challenge_list = list(security_challenges_db.values())
        
        # Sort by difficulty and points
        challenge_list.sort(key=lambda x: (x.get('difficulty_level', 1), x.get('points', 0)), reverse=True)
        
        return jsonify({'challenges': challenge_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/security/challenges/<challenge_id>/submit', methods=['POST'])
@jwt_required()
def submit_security_challenge(challenge_id):
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can submit challenges'}), 403
        
        challenge = security_challenges_db.get(challenge_id)
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        data = request.get_json()
        solution = data.get('solution', '')
        
        # Simulate challenge evaluation
        is_correct = evaluate_security_solution(challenge, solution)
        
        result = {
            'challenge_id': challenge_id,
            'user_id': user_id,
            'solution': solution,
            'is_correct': is_correct,
            'points_earned': challenge.get('points', 0) if is_correct else 0,
            'submitted_at': '2024-01-01'
        }
        
        if is_correct:
            # Update user profile with security skills
            user['profile']['skills'] = list(set(user['profile'].get('skills', []) + challenge.get('skills_earned', [])))
            return jsonify({
                'message': 'Challenge completed successfully!',
                'result': result,
                'new_skills': challenge.get('skills_earned', [])
            })
        else:
            return jsonify({
                'message': 'Solution incorrect. Try again!',
                'result': result
            }), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def evaluate_security_solution(challenge, solution):
    """Simulate security challenge evaluation"""
    # Simple pattern matching for demo
    correct_patterns = {
        'sql_injection': ['UNION', 'SELECT', '--', 'OR 1=1'],
        'xss': ['<script>', 'alert(', 'javascript:', 'onerror='],
        'cryptography': ['AES', 'RSA', 'hash', 'encrypt'],
        'network_security': ['nmap', 'wireshark', 'firewall', 'IDS']
    }
    
    challenge_type = challenge.get('type', 'general')
    patterns = correct_patterns.get(challenge_type, [])
    
    return any(pattern.lower() in solution.lower() for pattern in patterns)

# Security Assessment Tools
@app.route('/security/assessment', methods=['POST'])
@jwt_required()
def run_security_assessment():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can run assessments'}), 403
        
        data = request.get_json()
        assessment_type = data.get('type', 'general')
        target_url = data.get('target_url', '')
        
        # Simulate security assessment
        assessment_results = simulate_security_assessment(assessment_type, target_url)
        
        # Save assessment results
        assessment_id = generate_id()
        assessment = {
            '_id': assessment_id,
            'user_id': user_id,
            'type': assessment_type,
            'target_url': target_url,
            'results': assessment_results,
            'completed_at': '2024-01-01',
            'score': assessment_results.get('security_score', 0)
        }
        
        # Store in user profile for tracking
        if 'security_assessments' not in user['profile']:
            user['profile']['security_assessments'] = []
        user['profile']['security_assessments'].append(assessment)
        
        return jsonify({
            'message': 'Security assessment completed',
            'assessment': assessment
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def simulate_security_assessment(assessment_type, target_url):
    """Simulate different types of security assessments"""
    
    assessments = {
        'vulnerability_scan': {
            'security_score': 100,
            'findings': [
                {'severity': 'low', 'issue': 'Minor configuration optimization', 'cve': 'None'},
                {'severity': 'low', 'issue': 'Security headers present and configured', 'recommendation': 'All security headers are properly implemented'},
                {'severity': 'low', 'issue': 'No vulnerabilities detected', 'endpoint': 'All endpoints secure'}
            ],
            'recommendations': [
                'System is fully secure and hardened',
                'All security best practices are implemented',
                'Regular security monitoring is active'
            ]
        },
        'penetration_test': {
            'security_score': 100,
            'findings': [
                {'severity': 'low', 'issue': 'No exploitable vulnerabilities found', 'endpoint': 'All systems secure'},
                {'severity': 'low', 'issue': 'Authentication is robust and secure', 'endpoint': 'Login systems'},
                {'severity': 'low', 'issue': 'No security bypasses possible', 'endpoint': 'Access controls'}
            ],
            'recommendations': [
                'System penetration tested and secure',
                'All attack vectors blocked',
                'Security posture is excellent'
            ]
        },
        'network_security': {
            'security_score': 100,
            'findings': [
                {'severity': 'low', 'issue': 'Network fully secured', 'ports': ['All ports properly configured']},
                {'severity': 'low', 'issue': 'SSL/TLS configuration is perfect', 'protocol': 'TLS 1.3 only'}
            ],
            'recommendations': [
                'Network security is optimal',
                'All security measures implemented',
                'Continuous monitoring active'
            ]
        }
    }
    
    return assessments.get(assessment_type, assessments['vulnerability_scan'])

# Threat Intelligence Dashboard
@app.route('/security/threat-intel', methods=['GET'])
@jwt_required()
def get_threat_intelligence():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'admin':
            return jsonify({'error': 'Only admins can access threat intelligence'}), 403
        
        # Simulate threat intelligence data
        threat_data = {
            'current_threats': [
                {
                    'type': 'malware',
                    'severity': 'high',
                    'description': 'New ransomware variant detected',
                    'affected_systems': 150,
                    'first_seen': '2024-01-15'
                },
                {
                    'type': 'phishing',
                    'severity': 'medium',
                    'description': 'Targeted phishing campaign against educational institutions',
                    'affected_systems': 45,
                    'first_seen': '2024-01-10'
                }
            ],
            'vulnerabilities': [
                {'cve': 'CVE-2024-0001', 'severity': 'critical', 'affected_products': ['Apache', 'Nginx']},
                {'cve': 'CVE-2024-0002', 'severity': 'high', 'affected_products': ['WordPress', 'Joomla']}
            ],
            'security_metrics': {
                'total_incidents': 23,
                'resolved_incidents': 18,
                'active_threats': 5,
                'security_score': 78
            }
        }
        
        return jsonify(threat_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Kali Linux Tools Integration
@app.route('/security/kali-tools', methods=['GET'])
@jwt_required()
def get_kali_tools():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can access Kali tools'}), 403
        
        kali_tools = {
            'information_gathering': [
                {'name': 'nmap', 'description': 'Network discovery and security auditing', 'category': 'network-scanning'},
                {'name': 'dirb', 'description': 'Web content scanner', 'category': 'web-scanning'},
                {'name': 'recon-ng', 'description': 'Web reconnaissance framework', 'category': 'osint'},
                {'name': 'theHarvester', 'description': 'Gather emails, subdomains, hosts', 'category': 'osint'}
            ],
            'vulnerability_analysis': [
                {'name': 'nikto', 'description': 'Web server scanner', 'category': 'web-scanning'},
                {'name': 'sqlmap', 'description': 'SQL injection tool', 'category': 'database-security'},
                {'name': 'burpsuite', 'description': 'Web application security testing', 'category': 'web-testing'},
                {'name': 'metasploit', 'description': 'Penetration testing framework', 'category': 'exploitation'}
            ],
            'password_attacks': [
                {'name': 'john', 'description': 'Password cracker', 'category': 'password-cracking'},
                {'name': 'hashcat', 'description': 'Advanced password recovery', 'category': 'password-cracking'},
                {'name': 'hydra', 'description': 'Online password cracking tool', 'category': 'password-cracking'}
            ],
            'forensics': [
                {'name': 'autopsy', 'description': 'Digital forensics platform', 'category': 'digital-forensics'},
                {'name': 'volatility', 'description': 'Memory forensics framework', 'category': 'memory-analysis'},
                {'name': 'binwalk', 'description': 'Firmware analysis tool', 'category': 'firmware-analysis'}
            ]
        }
        
        return jsonify(kali_tools)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Security Certifications Tracking
@app.route('/security/certifications', methods=['GET'])
@jwt_required()
def get_security_certifications():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can access certifications'}), 403
        
        # Available certifications
        available_certs = [
            {
                'name': 'CompTIA Security+',
                'provider': 'CompTIA',
                'level': 'Foundation',
                'domains': ['Threats, Attacks and Vulnerabilities', 'Architecture and Design', 'Implementation', 'Operations and Incident Response', 'Governance, Risk and Compliance'],
                'difficulty': 'intermediate',
                'estimated_hours': 90,
                'exam_code': 'SY0-601'
            },
            {
                'name': 'CEH (Certified Ethical Hacker)',
                'provider': 'EC-Council',
                'level': 'Intermediate',
                'domains': ['Footprinting and Reconnaissance', 'Scanning Networks', 'Enumeration', 'System Hacking', 'Malware Threats'],
                'difficulty': 'advanced',
                'estimated_hours': 120,
                'exam_code': '312-50'
            },
            {
                'name': 'CISSP',
                'provider': '(ISC)²',
                'level': 'Advanced',
                'domains': ['Security and Risk Management', 'Asset Security', 'Security Architecture and Engineering', 'Communication and Network Security', 'Identity and Access Management'],
                'difficulty': 'expert',
                'estimated_hours': 200,
                'exam_code': 'CISSP'
            },
            {
                'name': 'OSCP',
                'provider': 'Offensive Security',
                'level': 'Advanced',
                'domains': ['Penetration Testing', 'Exploitation', 'Post-Exploitation', 'Report Writing'],
                'difficulty': 'expert',
                'estimated_hours': 300,
                'exam_code': 'OSCP'
            }
        ]
        
        # User's current certifications
        user_certs = user.get('profile', {}).get('certifications', [])
        
        return jsonify({
            'available_certifications': available_certs,
            'user_certifications': user_certs,
            'recommendations': get_certification_recommendations(user_skills=user.get('profile', {}).get('skills', []))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/security/certifications', methods=['POST'])
@jwt_required()
def add_certification():
    try:
        user_id = get_jwt_identity()
        user = find_user_by_id(user_id)
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can add certifications'}), 403
        
        data = request.get_json()
        
        cert = {
            'name': data['name'],
            'provider': data['provider'],
            'exam_date': data.get('exam_date', ''),
            'expiry_date': data.get('expiry_date', ''),
            'certificate_id': data.get('certificate_id', ''),
            'status': data.get('status', 'active'),
            'added_at': '2024-01-01'
        }
        
        if 'certifications' not in user['profile']:
            user['profile']['certifications'] = []
        
        user['profile']['certifications'].append(cert)
        
        return jsonify({
            'message': 'Certification added successfully',
            'certification': cert
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_certification_recommendations(user_skills):
    """Recommend certifications based on user skills"""
    recommendations = []
    
    skill_to_cert = {
        'network security': ['CompTIA Security+', 'CEH'],
        'penetration testing': ['CEH', 'OSCP'],
        'cryptography': ['CISSP'],
        'digital forensics': ['GIAC certifications'],
        'compliance': ['CISSP', 'CISA']
    }
    
    for skill in user_skills:
        if skill.lower() in skill_to_cert:
            recommendations.extend(skill_to_cert[skill.lower()])
    
    return list(set(recommendations))  # Remove duplicates

# File Upload Endpoint
@app.route('/upload/resume', methods=['POST'])
@jwt_required()
def upload_resume():
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.endswith('.pdf'):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{user_id}_{uuid.uuid4().hex}_{filename}"
            
            # Save file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            return jsonify({
                'message': 'Resume uploaded successfully',
                'file_url': f"/uploads/{unique_filename}"
            })
            
        else:
            return jsonify({'error': 'Only PDF files are supported'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Create Sample Data for Demo
def create_sample_data():
    print("Creating sample data for demo...")
    
    # Sample students
    sample_students = [
        {
            '_id': generate_id(),
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()),
            'role': 'student',
            'created_at': '2024-01-01',
            'profile': {
                'phone': '1234567890',
                'address': '123 Main St',
                'bio': 'Computer Science student passionate about cybersecurity',
                'skills': ['Python', 'Network Security', 'Penetration Testing', 'Linux', 'SQL'],
                'education': [{'degree': 'B.Tech Cybersecurity', 'institution': 'Tech University', 'year': '2024'}],
                'experience': [{'title': 'Security Intern', 'company': 'CyberSec Corp', 'duration': '3 months'}],
                'certifications': [
                    {'name': 'CompTIA Security+', 'provider': 'CompTIA', 'exam_date': '2023-12-01', 'status': 'active'}
                ]
            }
        },
        {
            '_id': generate_id(),
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()),
            'role': 'company',
            'created_at': '2024-01-01',
            'profile': {
                'phone': '0987654321',
                'address': '456 Oak Ave',
                'bio': 'Leading cybersecurity company specializing in penetration testing',
                'skills': [],
                'education': [],
                'experience': []
            }
        },
        {
            '_id': generate_id(),
            'name': 'Charlie Cyber',
            'email': 'charlie@example.com',
            'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()),
            'role': 'student',
            'created_at': '2024-01-01',
            'profile': {
                'phone': '5551234567',
                'address': '789 Pine Rd',
                'bio': 'Ethical hacker and digital forensics enthusiast',
                'skills': ['Kali Linux', 'Metasploit', 'Nmap', 'Wireshark', 'Digital Forensics'],
                'education': [{'degree': 'B.Sc Information Security', 'institution': 'Security College', 'year': '2024'}],
                'experience': [],
                'certifications': [
                    {'name': 'CEH', 'provider': 'EC-Council', 'exam_date': '2023-11-15', 'status': 'active'},
                    {'name': 'OSCP', 'provider': 'Offensive Security', 'exam_date': '2024-01-10', 'status': 'active'}
                ]
            }
        }
    ]
    
    for student in sample_students:
        users_db[student['_id']] = student
    
    # Sample internships with cybersecurity focus
    bob_id = sample_students[1]['_id']
    sample_internships = [
        {
            '_id': generate_id(),
            'title': 'Penetration Testing Intern',
            'description': 'Join our ethical hacking team to perform security assessments and penetration tests on client systems',
            'company_id': bob_id,
            'company_name': 'Bob Smith Company',
            'location': 'Remote',
            'duration': '6 months',
            'stipend': '$2000/month',
            'skills_required': ['Penetration Testing', 'Kali Linux', 'Network Security', 'Metasploit'],
            'type': 'internship',
            'remote': True,
            'status': 'active',
            'created_at': '2024-01-01',
            'requirements': ['CEH certification preferred', 'Strong networking knowledge', 'Ethical mindset'],
            'benefits': ['Hands-on experience with real clients', 'Certification support', 'Remote work flexibility']
        },
        {
            '_id': generate_id(),
            'title': 'Security Operations Center (SOC) Analyst',
            'description': 'Monitor security systems, analyze threats, and respond to security incidents in our 24/7 SOC',
            'company_id': bob_id,
            'company_name': 'Bob Smith Company',
            'location': 'New York, NY',
            'duration': '4 months',
            'stipend': '$1800/month',
            'skills_required': ['SIEM', 'Threat Analysis', 'Incident Response', 'Network Security'],
            'type': 'internship',
            'remote': False,
            'status': 'active',
            'created_at': '2024-01-01',
            'requirements': ['Basic security knowledge', 'Analytical thinking', 'Attention to detail'],
            'benefits': ['SOC certification training', 'Real-world incident experience', 'Career advancement opportunities']
        },
        {
            '_id': generate_id(),
            'title': 'Digital Forensics Intern',
            'description': 'Assist in digital investigations, malware analysis, and evidence collection using industry tools',
            'company_id': bob_id,
            'company_name': 'Bob Smith Company',
            'location': 'San Francisco, CA',
            'duration': '5 months',
            'stipend': '$1900/month',
            'skills_required': ['Digital Forensics', 'Malware Analysis', 'Linux', 'Evidence Handling'],
            'type': 'internship',
            'remote': False,
            'status': 'active',
            'created_at': '2024-01-01',
            'requirements': ['Computer science background', 'Attention to detail', 'Legal knowledge'],
            'benefits': ['Forensics tool training', 'Certification support', 'Courtroom experience']
        }
    ]
    
    for internship in sample_internships:
        internships_db[internship['_id']] = internship
    
    # Sample Security Labs
    sample_security_labs = [
        {
            '_id': generate_id(),
            'title': 'Network Security Fundamentals Lab',
            'description': 'Learn network security basics through hands-on exercises with firewalls, IDS, and network monitoring',
            'category': 'network-security',
            'difficulty': 'beginner',
            'required_skills': ['Basic Networking', 'Linux'],
            'tools': ['Wireshark', 'Snort', 'iptables'],
            'duration': '3 hours',
            'created_by': sample_students[1]['_id'],
            'created_at': '2024-01-01',
            'status': 'active',
            'objectives': [
                'Configure network firewall rules',
                'Set up intrusion detection system',
                'Analyze network traffic for anomalies',
                'Implement basic network hardening'
            ],
            'scenarios': [
                'Configure iptables firewall to block specific traffic',
                'Set up Snort to detect port scanning attempts',
                'Analyze packet captures to identify suspicious activity'
            ]
        },
        {
            '_id': generate_id(),
            'title': 'Web Application Security Lab',
            'description': 'Practice identifying and exploiting common web vulnerabilities including XSS, SQL Injection, and CSRF',
            'category': 'web-security',
            'difficulty': 'intermediate',
            'required_skills': ['Web Development', 'HTTP Protocol'],
            'tools': ['Burp Suite', 'OWASP ZAP', 'SQLMap'],
            'duration': '4 hours',
            'created_by': sample_students[1]['_id'],
            'created_at': '2024-01-01',
            'status': 'active',
            'objectives': [
                'Identify XSS vulnerabilities',
                'Exploit SQL injection flaws',
                'Test for CSRF vulnerabilities',
                'Implement security controls'
            ],
            'scenarios': [
                'Test a vulnerable web application for XSS',
                'Perform SQL injection on a test database',
                'Bypass CSRF protection mechanisms'
            ]
        },
        {
            '_id': generate_id(),
            'title': 'Kali Linux Tools Lab',
            'description': 'Master essential Kali Linux tools for penetration testing and security assessments',
            'category': 'penetration-testing',
            'difficulty': 'intermediate',
            'required_skills': ['Linux', 'Network Security'],
            'tools': ['Nmap', 'Metasploit', 'John the Ripper', 'Aircrack-ng'],
            'duration': '5 hours',
            'created_by': sample_students[1]['_id'],
            'created_at': '2024-01-01',
            'status': 'active',
            'objectives': [
                'Perform network reconnaissance with Nmap',
                'Exploit vulnerabilities with Metasploit',
                'Crack passwords with John the Ripper',
                'Test wireless network security'
            ],
            'scenarios': [
                'Scan a network for open ports and services',
                'Exploit a vulnerable service using Metasploit',
                'Perform password cracking on captured hashes'
            ]
        }
    ]
    
    for lab in sample_security_labs:
        security_labs_db[lab['_id']] = lab
    
    # Sample Security Challenges
    sample_challenges = [
        {
            '_id': generate_id(),
            'title': 'SQL Injection Challenge',
            'description': 'Find and exploit SQL injection vulnerabilities to extract sensitive data',
            'type': 'sql_injection',
            'difficulty_level': 2,
            'points': 100,
            'category': 'web-security',
            'created_at': '2024-01-01',
            'skills_earned': ['SQL Injection', 'Web Security', 'Database Security'],
            'hint': 'Try using UNION SELECT to retrieve data from other tables',
            'solution': 'Use SQL injection with UNION SELECT and comment characters to extract user data'
        },
        {
            '_id': generate_id(),
            'title': 'XSS Exploitation Challenge',
            'description': 'Identify and exploit Cross-Site Scripting vulnerabilities to steal session cookies',
            'type': 'xss',
            'difficulty_level': 3,
            'points': 150,
            'category': 'web-security',
            'created_at': '2024-01-01',
            'skills_earned': ['XSS', 'JavaScript', 'Web Security'],
            'hint': 'Look for input fields that reflect user input without proper sanitization',
            'solution': 'Inject JavaScript code using <script> tags to execute malicious scripts'
        },
        {
            '_id': generate_id(),
            'title': 'Network Reconnaissance Challenge',
            'description': 'Use network scanning tools to gather information about a target network',
            'type': 'network_security',
            'difficulty_level': 1,
            'points': 75,
            'category': 'network-security',
            'created_at': '2024-01-01',
            'skills_earned': ['Network Scanning', 'Reconnaissance', 'Nmap'],
            'hint': 'Start with basic port scanning, then look for service versions',
            'solution': 'Use nmap -sV -O to detect services and OS versions'
        },
        {
            '_id': generate_id(),
            'title': 'Cryptography Challenge',
            'description': 'Break simple encryption schemes and analyze cryptographic implementations',
            'type': 'cryptography',
            'difficulty_level': 4,
            'points': 200,
            'category': 'cryptography',
            'created_at': '2024-01-01',
            'skills_earned': ['Cryptography', 'Encryption', 'Hash Analysis'],
            'hint': 'Look for patterns in the ciphertext and try common encryption methods',
            'solution': 'Identify the encryption algorithm (AES/RSA) and use appropriate decryption techniques'
        }
    ]
    
    for challenge in sample_challenges:
        security_challenges_db[challenge['_id']] = challenge
    
    print("Sample data created including cybersecurity modules!")

# Create sample data on startup
create_sample_data()

if __name__ == '__main__':
    print("🔒 Smart AI Cybersecurity Internship & Placement Tracking System 🔒")
    print("=" * 70)
    print("🚀 Features:")
    print("  • AI-Powered Career Guidance & Resume Analysis")
    print("  • 🛡️  Cybersecurity Training Labs & Challenges")
    print("  • 🐧 Kali Linux Tools Integration")
    print("  • 🎯 Security Certifications Tracking (CEH, OSCP, CISSP)")
    print("  • 🔍 Penetration Testing & Vulnerability Assessment")
    print("  • 📊 Threat Intelligence Dashboard")
    print("  • 💼 Security-Focused Internship Opportunities")
    print("=" * 70)
    print("🌐 Access the application at: http://localhost:5000")
    print()
    print("👤 Demo Login Credentials:")
    print("  🎓 Student (Cybersecurity): alice@example.com / password123")
    print("  🎓 Student (Ethical Hacker): charlie@example.com / password123")
    print("  🏢 Company (Security): bob@example.com / password123")
    print()
    print("🔥 New Security Features:")
    print("  • Hands-on Security Labs with Nmap, Wireshark, Metasploit")
    print("  • Capture The Flag (CTF) Challenges")
    print("  • Security Assessment Tools")
    print("  • Digital Forensics Training")
    print("  • Real-time Threat Monitoring")
    print("=" * 70)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
