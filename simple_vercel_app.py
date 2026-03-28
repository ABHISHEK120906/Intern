from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    """Simple home page for serverless"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>CareerTrack AI - Working</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
        .status { color: #28a745; font-size: 24px; font-weight: bold; }
        .api-list { margin: 20px 0; }
        .api-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 CareerTrack AI Server</h1>
        <p class="status">✅ Server is working perfectly!</p>
        
        <h2>Available Endpoints:</h2>
        <div class="api-list">
            <div class="api-item">GET /health - Health Check</div>
            <div class="api-item">GET /api/status - System Status</div>
            <div class="api-item">GET / - This Page</div>
        </div>
        
        <h2>Server Info:</h2>
        <p>Environment: ''' + os.getenv('VERCEL_ENV', 'development') + '''</p>
        <p>Time: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
        
        <p><strong>🎯 Serverless function is working!</strong></p>
    </div>
</body>
</html>
    '''

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('VERCEL_ENV', 'development'),
        'message': 'Serverless function working perfectly!'
    })

@app.route('/api/status')
def status():
    return jsonify({
        'server': 'CareerTrack AI',
        'status': 'operational',
        'database': 'disabled (for testing)',
        'features': ['basic_api', 'health_check'],
        'timestamp': datetime.now().isoformat()
    })

# Vercel handler
try:
    from vercel_wsgi import handler as vercel_handler
except ImportError:
    def vercel_handler(environ, start_response):
        return app(environ, start_response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
