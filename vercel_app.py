from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
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

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# MongoDB Connection with Vercel support
def get_db_connection():
    """Get MongoDB connection with retry logic"""
    try:
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ MONGODB_URI not found")
            return None, None
        
        # Try different connection methods for Vercel
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            retryWrites=True,
            w="majority"
        )
        
        # Test connection
        client.admin.command('ping')
        db = client['placement_system']
        return client, db
        
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        return None, None

# Initialize database connection lazily
client = None
db = None

# Collections
users = None
companies = None
jobs = None
internships = None
placements = None
applications = None
trainings = None
system_ips = None
notifications = None

def initialize_database():
    """Initialize database connection on demand"""
    global client, db, users, companies, jobs, internships, placements
    global applications, trainings, system_ips, notifications
    
    if db is not None:
        return  # Already initialized
    
    client, db = get_db_connection()
    
    # Collections
    users = db['users'] if db else None
    companies = db['companies'] if db else None
    jobs = db['jobs'] if db else None
    internships = db['internships'] if db else None
    placements = db['placements'] if db else None
    applications = db['applications'] if db else None
    trainings = db['trainings'] if db else None
    system_ips = db['system_ips'] if db else None
    notifications = db['notifications'] if db else None
    
    if not db:
        print("⚠️  Warning: MongoDB connection failed. Some features may not work.")

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

# Store IPs on startup (only if not on Vercel)
if os.getenv('VERCEL') != '1':
    initialize_database()
    store_system_ips()

# IP Address API Endpoints
@app.route('/api/store-ip', methods=['POST'])
def store_ip_address():
    """Store IP addresses in MongoDB"""
    initialize_database()  # Ensure DB is connected
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
    initialize_database()  # Ensure DB is connected
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

# Main routes
@app.route('/')
def home():
    """Serve the home page with fallback for serverless environments"""
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback for serverless environments where templates might not be available
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CareerTrack AI - Server Running</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .status { color: #28a745; font-weight: bold; }
        .api-list { margin: 20px 0; }
        .api-item { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; font-family: monospace; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 CareerTrack AI Server</h1>
        <p class="status">✅ Server is running successfully!</p>
        
        <h2>Available API Endpoints:</h2>
        <div class="api-list">
            <div class="api-item">GET /health - Health check</div>
            <div class="api-item">GET /test-db - Database connection test</div>
            <div class="api-item">GET /api/current-ip - Get current IP information</div>
            <div class="api-item">GET /api/get-ips - Get stored IP addresses</div>
            <div class="api-item">POST /api/store-ip - Store IP addresses</div>
        </div>
        
        <h2>Server Information:</h2>
        <p>Environment: """ + os.getenv('VERCEL_ENV', 'development') + """</p>
        <p>Timestamp: """ + datetime.now().isoformat() + """</p>
        
        <div class="error">
            ⚠️ Template rendering failed: """ + str(e) + """<br>
            Server is running but templates may not be properly configured for deployment.
        </div>
    </div>
</body>
</html>
        """
        return html_content

@app.route('/test-db')
def test_db():
    initialize_database()  # Ensure DB is connected
    if db:
        try:
            db.admin.command('ping')
            return jsonify({
                'status': 'connected',
                'database': 'placement_system',
                'collections': db.list_collection_names()
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    else:
        return jsonify({
            'status': 'not_connected',
            'message': 'Database not available'
        }), 500

# Health check endpoint for Vercel
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('VERCEL_ENV', 'development')
    })

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Include all your existing API endpoints here...
# (Add your existing routes for authentication, internships, etc.)

# Vercel serverless handler
try:
    from vercel_wsgi import handler as vercel_handler
except ImportError:
    # vercel-wsgi not available in local development
    def vercel_handler(environ, start_response):
        """Fallback handler for local development"""
        return app(environ, start_response)

if __name__ == '__main__':
    # Initialize database for local development
    initialize_database()
    
    # Create uploads directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Run development server
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
