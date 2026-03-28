#!/usr/bin/env python3
"""
IP Address MongoDB Storage Script
Store system IP addresses in MongoDB database
"""

import os
import socket
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def get_local_ip():
    """Get local IP address"""
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def get_public_ip():
    """Get public IP address"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            return response.json()['ip']
    except:
        pass
    return None

def get_all_network_ips():
    """Get all network interface IPs"""
    ips = []
    try:
        hostname = socket.gethostname()
        # Get all IP addresses for the host
        for info in socket.getaddrinfo(hostname, None):
            family, _, _, _, sockaddr = info
            if family == socket.AF_INET:  # IPv4
                ip = sockaddr[0]
                if ip != "127.0.0.1" and ip not in ips:
                    ips.append(ip)
    except:
        pass
    return ips

def store_ips_in_mongodb():
    """Store IP addresses in MongoDB"""
    print("🔍 Getting IP Addresses...")
    print("=" * 50)
    
    try:
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ MONGODB_URI not found in .env file")
            return False
        
        # Connect to MongoDB
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        db = client['placement_system']
        
        # Get all IP addresses
        local_ip = get_local_ip()
        public_ip = get_public_ip()
        network_ips = get_all_network_ips()
        
        print(f"🏠 Local IP: {local_ip}")
        print(f"🌍 Public IP: {public_ip}")
        print(f"📡 Network IPs: {', '.join(network_ips)}")
        
        # Create IP document
        ip_data = {
            "timestamp": datetime.now(),
            "local_ip": local_ip,
            "public_ip": public_ip,
            "network_ips": network_ips,
            "hostname": socket.gethostname(),
            "status": "active",
            "last_updated": datetime.now()
        }
        
        # Store in MongoDB
        ip_collection = db['system_ips']
        
        # Check if entry already exists
        existing = ip_collection.find_one({"hostname": socket.gethostname()})
        
        if existing:
            # Update existing entry
            ip_collection.update_one(
                {"_id": existing["_id"]},
                {"$set": ip_data}
            )
            print(f"✅ Updated IP data for hostname: {socket.gethostname()}")
        else:
            # Insert new entry
            result = ip_collection.insert_one(ip_data)
            print(f"✅ Stored IP data with ID: {result.inserted_id}")
        
        # Verify storage
        stored = ip_collection.find_one({"hostname": socket.gethostname()})
        print(f"📋 Verification: {stored}")
        
        # Show all stored IPs
        print(f"\n📊 All IP entries in database:")
        all_ips = ip_collection.find()
        for entry in all_ips:
            print(f"   🖥️  {entry['hostname']}: {entry['local_ip']} | Public: {entry.get('public_ip', 'N/A')}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing IPs in MongoDB: {str(e)}")
        return False

def update_env_with_ips():
    """Update .env file with current IPs"""
    print("\n📝 Updating .env file with IP addresses...")
    
    try:
        local_ip = get_local_ip()
        public_ip = get_public_ip()
        network_ips = get_all_network_ips()
        
        # Read current .env file
        env_file = '.env'
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add IP variables
        updated_lines = []
        ip_vars_added = False
        
        for line in lines:
            if line.startswith('LOCAL_IP=') or line.startswith('NETWORK_IP=') or line.startswith('PUBLIC_IP='):
                continue  # Skip existing IP lines
            updated_lines.append(line)
        
        # Add new IP variables
        updated_lines.append(f"LOCAL_IP={local_ip}\n")
        if public_ip:
            updated_lines.append(f"PUBLIC_IP={public_ip}\n")
        for i, ip in enumerate(network_ips):
            updated_lines.append(f"NETWORK_IP_{i+1}={ip}\n")
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ .env file updated with IP addresses")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 IP Address MongoDB Storage")
    print("=" * 60)
    
    # Store IPs in MongoDB
    mongo_success = store_ips_in_mongodb()
    
    # Update .env file
    env_success = update_env_with_ips()
    
    print("\n" + "=" * 60)
    if mongo_success and env_success:
        print("🎉 IP addresses successfully stored in MongoDB and .env updated!")
    else:
        print("⚠️  Some issues occurred during IP storage.")
    
    print("=" * 60)
