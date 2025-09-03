#!/usr/bin/env python3
"""
Test script for checking Dominus MongoDB Status Service API
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"

def test_get_status():
    """Test getting status"""
    print("🔍 Testing GET /status...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/status",
            auth=(USERNAME, PASSWORD),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status retrieved successfully:")
            print(f"   Service: {data['service_name']}")
            print(f"   Status: {data['state']}")
            print(f"   Host: {data['hostname']}")
            print(f"   User: {data['user']}")
            return data['state']
        else:
            print(f"❌ Error getting status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def test_promote_to_primary():
    """Test promoting to primary"""
    print("\n🚀 Testing PUT /state (promote to primary)...")
    
    try:
        response = requests.put(
            f"{BASE_URL}/state",
            auth=(USERNAME, PASSWORD),
            timeout=60  # Increase timeout for promotion operation
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server successfully promoted to primary:")
            print(f"   New status: {data['state']}")
            print(f"   Message: {data.get('message', 'N/A')}")
            return True
        elif response.status_code == 403:
            print(f"⚠️  Server is a voter and cannot change priority:")
            print(f"   Error: {response.json().get('detail', 'N/A')}")
            return False
        else:
            print(f"❌ Error promoting to primary: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_all_services():
    """Test all services"""
    services = [
        ("http://localhost:8000", "msk-app1"),
        ("http://localhost:8001", "vlg-app01"),
        ("http://localhost:8002", "msk-app01"),
        ("http://localhost:8003", "voter-server")
    ]
    
    print("\n🌐 Testing all services:")
    
    for url, hostname in services:
        print(f"\n--- {hostname} ({url}) ---")
        
        try:
            response = requests.get(
                f"{url}/status",
                auth=(USERNAME, PASSWORD),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {data['state']}")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")

def main():
    """Main testing function"""
    print("🧪 Testing Dominus MongoDB Status Service")
    print("=" * 50)
    
    # Check service availability
    print("🔌 Checking service availability...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print("✅ Service available")
    except:
        print("❌ Service unavailable. Make sure it's running.")
        print("   Run: ./start-cluster.sh")
        sys.exit(1)
    
    # Test getting status
    current_status = test_get_status()
    
    if current_status:
        print(f"\n📊 Current status: {current_status}")
        
        # If not primary, try to promote
        if current_status != "primary":
            success = test_promote_to_primary()
            if success:
                # Check new status
                time.sleep(5)
                new_status = test_get_status()
                if new_status == "primary":
                    print("✅ Promotion to primary successful!")
                else:
                    print(f"⚠️  Status after promotion: {new_status}")
        else:
            print("ℹ️  Server is already primary")
    
    # Test all services
    test_all_services()
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed")

if __name__ == "__main__":
    main()
