
# Add this to your app.py for IP storage API
@app.route('/api/store-ip', methods=['POST'])
def store_ip_address():
    """Store IP addresses in MongoDB"""
    try:
        data = request.get_json()
        
        ip_data = {
            "timestamp": datetime.now(),
            "local_ip": data.get('local_ip'),
            "public_ip": data.get('public_ip'),
            "network_ips": data.get('network_ips', []),
            "hostname": data.get('hostname', 'Unknown'),
            "status": "active",
            "last_updated": datetime.now()
        }
        
        # Store in MongoDB
        result = db['system_ips'].insert_one(ip_data)
        
        return jsonify({
            'success': True,
            'message': 'IP addresses stored successfully',
            'id': str(result.inserted_id)
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
        ips = list(db['system_ips'].find({}, {'_id': 0}))
        return jsonify({
            'success': True,
            'ips': ips
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
