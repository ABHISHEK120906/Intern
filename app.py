import logging
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime
import bcrypt
from email_validator import validate_email, EmailNotValidError
from werkzeug.utils import secure_filename
import uuid
import PyPDF2
import re
from collections import Counter
import json
from bson.objectid import ObjectId
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))

# Security configuration
csp = {
    'default-src': "'self'",
    'script-src': [
        "'self'",
        "'unsafe-inline'",
        'https://cdnjs.cloudflare.com',
        'https://fonts.googleapis.com',
        'https://fonts.gstatic.com'
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",
        'https://fonts.googleapis.com',
        'https://fonts.gstatic.com'
    ],
    'font-src': [
        "'self'",
        'https://fonts.gstatic.com'
    ],
    'img-src': "'self' data: https:",
    'connect-src': "'self'"
}

Talisman(app, force_https=False, strict_transport_security=False, content_security_policy=csp)

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour", "10 per minute"]
)

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# MongoDB Connection
try:
    client = MongoClient(
        os.getenv('MONGODB_URI'),
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000,
        maxPoolSize=50,
        retryWrites=True
    )
    db = client['placement_system']
    
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connected successfully!")
    
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"❌ MongoDB connection error: {e}")
    db = None
    client = None

# Collections
users = db['users'] if db else None
companies = db['companies'] if db else None
jobs = db['jobs'] if db else None
internships = db['internships'] if db else None
placements = db['placements'] if db else None
applications = db['applications'] if db else None
trainings = db['trainings'] if db else None
system_ips = db['system_ips'] if db else None

# Input validation helper
def validate_input(data, required_fields, optional_fields=None):
    """Validate input data"""
    errors = []
    
    # Check required fields
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required')
    
    # Validate email format if present
    if 'email' in data and data['email']:
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            errors.append('Invalid email format')
    
    # Validate phone number format if present
    if 'phone' in data and data['phone']:
        phone_pattern = re.compile(r'^[+]?[\d\s\-\(\)]{10,}$')
        if not phone_pattern.match(data['phone']):
            errors.append('Invalid phone number format')
    
    return errors

# File validation helper
def validate_file_upload(file, allowed_extensions=None, max_size=None):
    """Validate uploaded file"""
    if allowed_extensions is None:
        allowed_extensions = ['pdf']
    if max_size is None:
        max_size = 16 * 1024 * 1024  # 16MB
    
    errors = []
    
    if not file or file.filename == '':
        errors.append('No file selected')
        return errors
    
    # Check file extension
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_ext not in allowed_extensions:
        errors.append(f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}')
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > max_size:
        errors.append(f'File too large. Maximum size: {max_size // (1024*1024)}MB')
    
    return errors

# Helper functions
def get_object_id(id_string):
    """Convert string ID to ObjectId safely"""
    try:
        return ObjectId(id_string)
    except (TypeError, ValueError):
        return None

def validate_user_exists(user_id):
    """Validate user exists and return user data"""
    try:
        object_id = get_object_id(user_id)
        if not object_id:
            logger.warning(f"Invalid user ID format: {user_id}")
            return None
        return users.find_one({'_id': object_id})
    except Exception as e:
        logger.error(f"Error validating user {user_id}: {str(e)}")
        return None

# Store IP addresses on startup
def store_system_ips():
    """Store system IP addresses in MongoDB"""
    if not system_ips:
        print("⚠️  MongoDB not available, skipping IP storage")
        return
    
    try:
        import socket
        
        # Get system information
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Get network IPs
        network_ips = []
        try:
            for info in socket.getaddrinfo(hostname, None):
                family, _, _, _, sockaddr = info
                if family == socket.AF_INET and sockaddr[0] != "127.0.0.1":
                    if sockaddr[0] not in network_ips:
                        network_ips.append(sockaddr[0])
        except:
            pass
        
        # Get IPs from environment
        env_ips = []
        for key, value in os.environ.items():
            if 'IP' in key and value:
                env_ips.append(value)
        
        # Prepare IP data
        ip_data = {
            "timestamp": datetime.now(),
            "hostname": hostname,
            "local_ip": local_ip,
            "network_ips": network_ips,
            "environment_ips": env_ips,
            "status": "active",
            "last_updated": datetime.now()
        }
        
        # Store in MongoDB
        existing = system_ips.find_one({"hostname": hostname})
        if existing:
            system_ips.update_one({"_id": existing["_id"]}, {"$set": ip_data})
            print(f"✅ Updated IP data for {hostname}")
        else:
            result = system_ips.insert_one(ip_data)
            print(f"✅ Stored IP data for {hostname} with ID: {result.inserted_id}")
            
        print(f"📍 Local IP: {local_ip}")
        print(f"🌐 Network IPs: {', '.join(network_ips)}")
        
    except Exception as e:
        print(f"❌ Error storing IP addresses: {e}")

# Store IPs on startup
store_system_ips()

# IP Address API Endpoints
@app.route('/api/store-ip', methods=['POST'])
def store_ip_address():
    """Store IP addresses in MongoDB"""
    try:
        if not system_ips:
            return jsonify({'error': 'MongoDB not available'}), 500
            
        data = request.get_json()
        
        ip_data = {
            "timestamp": datetime.now(),
            "hostname": data.get('hostname', 'Unknown'),
            "local_ip": data.get('local_ip'),
            "public_ip": data.get('public_ip'),
            "network_ips": data.get('network_ips', []),
            "status": "active",
            "last_updated": datetime.now()
        }
        
        # Store in MongoDB
        existing = system_ips.find_one({"hostname": ip_data["hostname"]})
        if existing:
            system_ips.update_one({"_id": existing["_id"]}, {"$set": ip_data})
            message = "IP data updated successfully"
        else:
            result = system_ips.insert_one(ip_data)
            message = f"IP data stored with ID: {result.inserted_id}"
        
        return jsonify({
            'success': True,
            'message': message,
            'data': ip_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/get-ips', methods=['GET'])
def get_ip_addresses():
    """Get all stored IP addresses"""
    try:
        if not system_ips:
            # Return from JSON file as fallback
            try:
                with open('ip_addresses.json', 'r') as f:
                    data = json.load(f)
                return jsonify({
                    'success': True,
                    'ips': [data],
                    'source': 'json_file'
                })
            except:
                return jsonify({'error': 'No IP data available'}), 404
        
        ips = list(system_ips.find({}, {'_id': 0}))
        return jsonify({
            'success': True,
            'ips': ips,
            'source': 'mongodb'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/current-ip', methods=['GET'])
def get_current_ip():
    """Get current system IP information"""
    try:
        import socket
        
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Get network IPs
        network_ips = []
        try:
            for info in socket.getaddrinfo(hostname, None):
                family, _, _, _, sockaddr = info
                if family == socket.AF_INET and sockaddr[0] != "127.0.0.1":
                    if sockaddr[0] not in network_ips:
                        network_ips.append(sockaddr[0])
        except:
            pass
        
        return jsonify({
            'success': True,
            'hostname': hostname,
            'local_ip': local_ip,
            'network_ips': network_ips,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
notifications = db['notifications'] if db else None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test-db')
def test_db():
    if db:
        try:
            # Test basic operations
            test_doc = {'test': 'connection', 'timestamp': datetime.now().isoformat()}
            result = db['test_collection'].insert_one(test_doc)
            db['test_collection'].delete_one({'_id': result.inserted_id})
            return jsonify({'status': 'success', 'message': 'Database operations working correctly'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Database not connected'}), 500

# User Authentication Endpoints
@app.route('/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['name', 'email', 'password', 'role']
        validation_errors = validate_input(data, required_fields)
        
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        # Validate role
        valid_roles = ['student', 'admin', 'company']
        if data['role'] not in valid_roles:
            return jsonify({'error': 'Invalid role. Must be one of: ' + ', '.join(valid_roles)}), 400
        
        # Validate password strength
        password = data['password']
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        if not re.search(r'[A-Z]', password):
            return jsonify({'error': 'Password must contain at least one uppercase letter'}), 400
        
        if not re.search(r'[a-z]', password):
            return jsonify({'error': 'Password must contain at least one lowercase letter'}), 400
        
        if not re.search(r'\d', password):
            return jsonify({'error': 'Password must contain at least one number'}), 400
        
        # Check if user already exists
        if users.find_one({'email': data['email']}):
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user = {
            'name': data['name'],
            'email': data['email'],
            'password': password_hash,
            'role': data['role'],  # 'student', 'admin', 'company'
            'created_at': datetime.now().isoformat(),
            'profile': {
                'phone': data.get('phone', ''),
                'address': data.get('address', ''),
                'bio': data.get('bio', ''),
                'skills': data.get('skills', []),
                'education': data.get('education', []),
                'experience': data.get('experience', [])
            }
        }
        
        result = users.insert_one(user)
        user['_id'] = str(result.inserted_id)
        user.pop('password', None)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@app.route('/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = users.find_one({'email': data['email']})
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user['_id']))
        
        user_data = {
            '_id': str(user['_id']),
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
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@app.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = validate_user_exists(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = {
            '_id': str(user['_id']),
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
        user = validate_user_exists(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        data = request.get_json()
        
        # Update profile
        update_data = {}
        if 'profile' in data:
            update_data['profile'] = data['profile']
        if 'name' in data:
            update_data['name'] = data['name']
        
        users.update_one({'_id': get_object_id(user_id)}, {'$set': update_data})
        
        return jsonify({'message': 'Profile updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Internship Management Endpoints
@app.route('/internships', methods=['GET'])
@jwt_required()
def get_internships():
    try:
        user_id = get_jwt_identity()
        user = validate_user_exists(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Filter based on user role
        if user['role'] == 'student':
            # Students see all available internships
            internship_list = list(internships.find({'status': 'active'}))
        elif user['role'] == 'company':
            # Companies see their own internships
            internship_list = list(internships.find({'company_id': get_object_id(user_id)}))
        else:  # admin
            # Admins see all internships
            internship_list = list(internships.find())
        
        # Convert ObjectId to string
        for internship in internship_list:
            internship['_id'] = str(internship['_id'])
            if 'company_id' in internship:
                internship['company_id'] = str(internship['company_id'])
        
        return jsonify({'internships': internship_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/internships', methods=['POST'])
@jwt_required()
def create_internship():
    try:
        user_id = get_jwt_identity()
        user = validate_user_exists(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user['role'] not in ['company', 'admin']:
            return jsonify({'error': 'Only companies and admins can create internships'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'location', 'duration', 'stipend', 'skills_required']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        internship = {
            'title': data['title'],
            'description': data['description'],
            'company_id': get_object_id(user_id),
            'company_name': user['name'],
            'location': data['location'],
            'duration': data['duration'],
            'stipend': data['stipend'],
            'skills_required': data['skills_required'],
            'type': data.get('type', 'internship'),
            'remote': data.get('remote', False),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'deadline': data.get('deadline', ''),
            'requirements': data.get('requirements', []),
            'benefits': data.get('benefits', [])
        }
        
        result = internships.insert_one(internship)
        internship['_id'] = str(result.inserted_id)
        
        return jsonify({
            'message': 'Internship created successfully',
            'internship': internship
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/internships/<internship_id>', methods=['GET'])
@jwt_required()
def get_internship(internship_id):
    try:
        object_id = get_object_id(internship_id)
        if not object_id:
            return jsonify({'error': 'Invalid internship ID'}), 400
            
        internship = internships.find_one({'_id': object_id})
        
        if not internship:
            return jsonify({'error': 'Internship not found'}), 404
        
        internship['_id'] = str(internship['_id'])
        if 'company_id' in internship:
            internship['company_id'] = str(internship['company_id'])
        
        return jsonify(internship)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/internships/<internship_id>', methods=['PUT'])
@jwt_required()
def update_internship(internship_id):
    try:
        user_id = get_jwt_identity()
        user = validate_user_exists(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        internship_object_id = get_object_id(internship_id)
        if not internship_object_id:
            return jsonify({'error': 'Invalid internship ID'}), 400
            
        internship = internships.find_one({'_id': internship_object_id})
        if not internship:
            return jsonify({'error': 'Internship not found'}), 404
        
        # Check ownership
        if user['role'] != 'admin' and internship['company_id'] != get_object_id(user_id):
            return jsonify({'error': 'Not authorized to update this internship'}), 403
        
        data = request.get_json()
        update_data = {k: v for k, v in data.items() if k not in ['_id', 'created_at']}
        
        internships.update_one({'_id': internship_object_id}, {'$set': update_data})
        
        return jsonify({'message': 'Internship updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/internships/<internship_id>', methods=['DELETE'])
@jwt_required()
def delete_internship(internship_id):
    try:
        user_id = get_jwt_identity()
        user = validate_user_exists(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        internship_object_id = get_object_id(internship_id)
        if not internship_object_id:
            return jsonify({'error': 'Invalid internship ID'}), 400
            
        internship = internships.find_one({'_id': internship_object_id})
        if not internship:
            return jsonify({'error': 'Internship not found'}), 404
        
        # Check ownership
        if user['role'] != 'admin' and internship['company_id'] != get_object_id(user_id):
            return jsonify({'error': 'Not authorized to delete this internship'}), 403
        
        internships.delete_one({'_id': internship_object_id})
        
        return jsonify({'message': 'Internship deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Application Management Endpoints
@app.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    try:
        user_id = get_jwt_identity()
        user = validate_user_exists(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user['role'] == 'student':
            # Students see their own applications
            application_list = list(applications.find({'student_id': get_object_id(user_id)}))
        elif user['role'] == 'company':
            # Companies see applications for their internships
            application_list = list(applications.find({'company_id': get_object_id(user_id)}))
        else:  # admin
            # Admins see all applications
            application_list = list(applications.find())
        
        # Convert ObjectId to string and populate related data
        for app in application_list:
            app['_id'] = str(app['_id'])
            if 'student_id' in app:
                app['student_id'] = str(app['student_id'])
            if 'internship_id' in app:
                app['internship_id'] = str(app['internship_id'])
            if 'company_id' in app:
                app['company_id'] = str(app['company_id'])
        
        return jsonify({'applications': application_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/applications', methods=['POST'])
@jwt_required()
def create_application():
    try:
        user_id = get_jwt_identity()
        user = validate_user_exists(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can apply for internships'}), 403
        
        data = request.get_json()
        
        if not data.get('internship_id'):
            return jsonify({'error': 'Internship ID is required'}), 400
        
        # Check if already applied
        existing_app = applications.find_one({
            'student_id': get_object_id(user_id),
            'internship_id': get_object_id(data['internship_id'])
        })
        
        if existing_app:
            return jsonify({'error': 'Already applied for this internship'}), 400
        
        # Get internship details
        internship_object_id = get_object_id(data['internship_id'])
        if not internship_object_id:
            return jsonify({'error': 'Invalid internship ID'}), 400
            
        internship = internships.find_one({'_id': internship_object_id})
        if not internship:
            return jsonify({'error': 'Internship not found'}), 404
        
        application = {
            'student_id': get_object_id(user_id),
            'internship_id': internship_object_id,
            'company_id': internship['company_id'],
            'status': 'pending',
            'applied_date': datetime.now().isoformat(),
            'resume_url': data.get('resume_url', ''),
            'cover_letter': data.get('cover_letter', ''),
            'notes': data.get('notes', '')
        }
        
        result = applications.insert_one(application)
        application['_id'] = str(result.inserted_id)
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/applications/<application_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(application_id):
    try:
        user_id = get_jwt_identity()
        user = users.find_one({'_id': user_id})
        data = request.get_json()
        
        application = applications.find_one({'_id': application_id})
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Check authorization
        if user['role'] == 'company' and application['company_id'] != user_id:
            return jsonify({'error': 'Not authorized to update this application'}), 403
        elif user['role'] not in ['company', 'admin']:
            return jsonify({'error': 'Not authorized to update application status'}), 403
        
        # Update status
        new_status = data.get('status')
        if new_status not in ['pending', 'shortlisted', 'rejected', 'selected']:
            return jsonify({'error': 'Invalid status'}), 400
        
        applications.update_one(
            {'_id': application_id},
            {'$set': {'status': new_status, 'updated_date': datetime.now().isoformat()}}
        )
        
        return jsonify({'message': f'Application status updated to {new_status}'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Company Management Endpoints
@app.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    try:
        company_list = list(users.find({'role': 'company'}))
        
        for company in company_list:
            company['_id'] = str(company['_id'])
            company.pop('password', None)
        
        return jsonify({'companies': company_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/companies/profile', methods=['GET'])
@jwt_required()
def get_company_profile():
    try:
        user_id = get_jwt_identity()
        user = users.find_one({'_id': user_id})
        
        if user['role'] != 'company':
            return jsonify({'error': 'Only companies can access this endpoint'}), 403
        
        # Get company stats
        posted_internships = list(internships.find({'company_id': user_id}))
        total_applications = 0
        
        for internship in posted_internships:
            app_count = applications.count_documents({'internship_id': str(internship['_id'])})
            total_applications += app_count
        
        company_data = {
            '_id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'profile': user.get('profile', {}),
            'stats': {
                'posted_internships': len(posted_internships),
                'total_applications': total_applications
            }
        }
        
        return jsonify(company_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Training Module Endpoints
@app.route('/trainings', methods=['GET'])
@jwt_required()
def get_trainings():
    try:
        user_id = get_jwt_identity()
        user = users.find_one({'_id': user_id})
        
        if user['role'] == 'student':
            # Students see all available trainings
            training_list = list(trainings.find({'status': 'active'}))
        elif user['role'] == 'admin':
            # Admins see all trainings
            training_list = list(trainings.find())
        else:
            # Companies don't see trainings
            return jsonify({'trainings': []})
        
        for training in training_list:
            training['_id'] = str(training['_id'])
        
        return jsonify({'trainings': training_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trainings', methods=['POST'])
@jwt_required()
def create_training():
    try:
        user_id = get_jwt_identity()
        user = users.find_one({'_id': user_id})
        
        if user['role'] != 'admin':
            return jsonify({'error': 'Only admins can create trainings'}), 403
        
        data = request.get_json()
        
        training = {
            'title': data['title'],
            'description': data['description'],
            'instructor': data['instructor'],
            'type': data.get('type', 'technical'),
            'duration': data['duration'],
            'schedule': data['schedule'],
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'materials': data.get('materials', []),
            'max_participants': data.get('max_participants', 50)
        }
        
        result = trainings.insert_one(training)
        training['_id'] = str(result.inserted_id)
        
        return jsonify({
            'message': 'Training created successfully',
            'training': training
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analytics Dashboard Endpoints
@app.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_analytics():
    try:
        user_id = get_jwt_identity()
        user = users.find_one({'_id': user_id})
        
        if user['role'] != 'admin':
            return jsonify({'error': 'Only admins can access analytics'}), 403
        
        # Calculate stats
        total_students = users.count_documents({'role': 'student'})
        total_companies = users.count_documents({'role': 'company'})
        total_internships = internships.count_documents()
        active_internships = internships.count_documents({'status': 'active'})
        total_applications = applications.count_documents()
        
        # Placement stats
        selected_applications = applications.count_documents({'status': 'selected'})
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

# Notification System Endpoints
@app.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user_id = get_jwt_identity()
        
        notification_list = list(notifications.find({'user_id': user_id}).sort('created_date', -1))
        
        for notification in notification_list:
            notification['_id'] = str(notification['_id'])
        
        return jsonify({'notifications': notification_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/notifications', methods=['POST'])
@jwt_required()
def create_notification():
    try:
        user_id = get_jwt_identity()
        user = users.find_one({'_id': user_id})
        
        if user['role'] != 'admin':
            return jsonify({'error': 'Only admins can create notifications'}), 403
        
        data = request.get_json()
        
        notification = {
            'user_id': data.get('user_id'),  # Can be None for broadcast
            'title': data['title'],
            'message': data['message'],
            'type': data.get('type', 'info'),
            'created_date': datetime.now().isoformat(),
            'read': False
        }
        
        result = notifications.insert_one(notification)
        notification['_id'] = str(result.inserted_id)
        
        return jsonify({
            'message': 'Notification created successfully',
            'notification': notification
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
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Analyze skills
            common_skills = [
                'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'MongoDB',
                'HTML', 'CSS', 'C++', 'C#', 'Angular', 'Vue.js', 'Django', 'Flask',
                'Machine Learning', 'Data Science', 'AWS', 'Docker', 'Git', 'Linux',
                'Communication', 'Leadership', 'Problem Solving', 'Team Work'
            ]
            
            found_skills = []
            for skill in common_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                    found_skills.append(skill)
            
            # Calculate resume score based on various factors
            score = 0
            
            # Skills score (40%)
            skills_score = min(len(found_skills) * 5, 40)
            score += skills_score
            
            # Experience score (30%)
            experience_matches = len(re.findall(r'\b(\d+)\s*(?:years?|yrs?)\b', text, re.IGNORECASE))
            experience_score = min(experience_matches * 10, 30)
            score += experience_score
            
            # Education score (20%)
            education_keywords = ['Bachelor', 'Master', 'PhD', 'B.Tech', 'M.Tech', 'B.E.', 'M.E.']
            education_score = 0
            for keyword in education_keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                    education_score = 20
                    break
            score += education_score
            
            # Structure score (10%)
            structure_score = 0
            if re.search(r'\b(objective|summary|profile)\b', text, re.IGNORECASE):
                structure_score += 3
            if re.search(r'\b(experience|work|employment)\b', text, re.IGNORECASE):
                structure_score += 4
            if re.search(r'\b(education|qualification)\b', text, re.IGNORECASE):
                structure_score += 3
            
            score += structure_score
            
            # Generate suggestions
            suggestions = []
            if len(found_skills) < 5:
                suggestions.append("Add more technical skills to your resume")
            if experience_score < 20:
                suggestions.append("Highlight your work experience more clearly")
            if education_score == 0:
                suggestions.append("Make sure your education section is clearly mentioned")
            if structure_score < 7:
                suggestions.append("Improve resume structure with clear sections")
            
            # Missing skills suggestions
            missing_tech_skills = ['Python', 'JavaScript', 'React', 'SQL', 'AWS']
            missing_skills = [skill for skill in missing_tech_skills if skill not in found_skills]
            if missing_skills:
                suggestions.append(f"Consider learning: {', '.join(missing_skills[:3])}")
            
            analysis_result = {
                'score': min(score, 100),
                'skills_found': found_skills,
                'experience_years': experience_matches,
                'suggestions': suggestions,
                'missing_recommended_skills': missing_skills[:5]
            }
            
            # Update user profile with analyzed skills
            users.update_one(
                {'_id': user_id},
                {'$set': {'profile.analyzed_skills': found_skills}}
            )
            
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
        user = users.find_one({'_id': user_id})
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can get job recommendations'}), 403
        
        # Get user skills
        user_skills = user.get('profile', {}).get('analyzed_skills', [])
        if not user_skills:
            user_skills = user.get('profile', {}).get('skills', [])
        
        # Get all active internships
        all_internships = list(internships.find({'status': 'active'}))
        
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
                    '_id': str(internship['_id']),
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
        user = users.find_one({'_id': user_id})
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can use skill gap analysis'}), 403
        
        data = request.get_json()
        target_job_skills = data.get('target_job_skills', [])
        
        if not target_job_skills:
            return jsonify({'error': 'Target job skills are required'}), 400
        
        # Get user skills
        user_skills = user.get('profile', {}).get('analyzed_skills', [])
        if not user_skills:
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
        user = users.find_one({'_id': user_id})
        
        if user['role'] != 'student':
            return jsonify({'error': 'Only students can get placement readiness score'}), 403
        
        # Get user data
        user_skills = user.get('profile', {}).get('analyzed_skills', [])
        if not user_skills:
            user_skills = user.get('profile', {}).get('skills', [])
        
        # Calculate different components of readiness score
        
        # 1. Skills Score (40%)
        skills_score = min(len(user_skills) * 8, 40)
        
        # 2. Applications Score (25%)
        user_applications = list(applications.find({'student_id': user_id}))
        applications_score = min(len(user_applications) * 5, 25)
        
        # 3. Profile Completeness (20%)
        profile = user.get('profile', {})
        profile_fields = ['phone', 'address', 'bio', 'education', 'experience']
        completed_fields = sum(1 for field in profile_fields if profile.get(field))
        profile_score = (completed_fields / len(profile_fields)) * 20
        
        # 4. Resume Quality (15%)
        resume_score = 10  # Base score
        if user.get('profile', {}).get('analyzed_skills'):
            resume_score += 5
        
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
        suggestions = []
        if skills_score < 30:
            suggestions.append("Add more relevant skills to your profile")
        if applications_score < 15:
            suggestions.append("Apply to more internships to increase your chances")
        if profile_score < 15:
            suggestions.append("Complete your profile with all required information")
        if resume_score < 12:
            suggestions.append("Upload and analyze your resume for better score")
        
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
            'next_milestone': "Good" if total_score < 60 else "Excellent" if total_score < 80 else "Top Candidate"
        }
        
        return jsonify(readiness_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# File Upload Endpoint
@app.route('/upload/resume', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def upload_resume():
    try:
        user_id = get_jwt_identity()
        user = validate_user_exists(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Validate file
        validation_errors = validate_file_upload(file, ['pdf'], 5 * 1024 * 1024)  # 5MB limit
        if validation_errors:
            return jsonify({'error': 'File validation failed', 'details': validation_errors}), 400
        
        # Additional security checks
        filename = secure_filename(file.filename)
        if not filename or filename == '':
            return jsonify({'error': 'Invalid filename'}), 400
        
        # Check for suspicious patterns in filename
        if any(pattern in filename.lower() for pattern in ['..', '/', '\\', '<', '>', ':', '*', '?', '"', '|']):
            return jsonify({'error': 'Invalid filename characters'}), 400
        
        # Generate unique filename with user ID and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"resume_{user_id}_{timestamp}_{filename}"
        
        # Ensure upload directory exists
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Save file with full path
        file_path = os.path.join(upload_folder, safe_filename)
        file.save(file_path)
        
        # Verify file was saved and is a valid PDF
        if not os.path.exists(file_path):
            return jsonify({'error': 'File save failed'}), 500
        
        # Basic PDF validation
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    os.remove(file_path)
                    return jsonify({'error': 'Invalid PDF file'}), 400
        except Exception:
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': 'File validation failed'}), 400
        
        # Update user profile with resume URL
        users.update_one(
            {'_id': get_object_id(user_id)},
            {'$set': {
                'profile.resume_url': f"/uploads/{safe_filename}",
                'profile.resume_uploaded_at': datetime.now().isoformat()
            }}
        )
        
        return jsonify({
            'message': 'Resume uploaded successfully',
            'file_url': f"/uploads/{safe_filename}"
        })
        
    except Exception as e:
        # Clean up file if upload failed
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': 'File upload failed'}), 500

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Run development server
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

# Vercel serverless handler
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda status, headers: None)
