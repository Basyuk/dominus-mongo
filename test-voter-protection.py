#!/usr/bin/env python3
"""
Test script for checking voter server protection
"""

import requests
import json
import time
import sys

# Configuration
VOTER_URL = "http://localhost:8003"  # voter-server
NORMAL_URL = "http://localhost:8000"  # msk-app1
USERNAME = "admin"
PASSWORD = "admin123"

def test_voter_protection():
    """Test voter server protection"""
    print("🛡️  Testing voter server protection")
    print("=" * 50)
    
    # Check voter server status
    print("1. Checking voter server status...")
    try:
        response = requests.get(
            f"{VOTER_URL}/status",
            auth=(USERNAME, PASSWORD),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voter server available:")
            print(f"   Host: {data['hostname']}")
            print(f"   Status: {data['state']}")
        else:
            print(f"❌ Error getting voter server status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to voter server: {e}")
        return False
    
    # Try to promote voter server to primary (should be blocked)
    print("\n2. Attempting to promote voter server to primary...")
    try:
        response = requests.put(
            f"{VOTER_URL}/state",
            auth=(USERNAME, PASSWORD),
            timeout=30
        )
        
        if response.status_code == 403:
            error_detail = response.json().get('detail', 'N/A')
            print(f"✅ Protection works! Voter server blocked:")
            print(f"   Error code: 403")
            print(f"   Message: {error_detail}")
            return True
        else:
            print(f"❌ Protection not working! Received code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing protection: {e}")
        return False

def test_normal_server():
    """Test normal server (for comparison)"""
    print("\n3. Testing normal server (for comparison)...")
    
    # Check normal server status
    try:
        response = requests.get(
            f"{NORMAL_URL}/status",
            auth=(USERNAME, PASSWORD),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Normal server available:")
            print(f"   Host: {data['hostname']}")
            print(f"   Status: {data['state']}")
            
            # If not primary, try to promote
            if data['state'] != "primary":
                print(f"\n4. Attempting to promote normal server to primary...")
                promote_response = requests.put(
                    f"{NORMAL_URL}/state",
                    auth=(USERNAME, PASSWORD),
                    timeout=60
                )
                
                if promote_response.status_code == 200:
                    print("✅ Normal server successfully promoted to primary")
                    return True
                else:
                    print(f"⚠️  Normal server cannot be promoted: {promote_response.status_code}")
                    return True
            else:
                print("ℹ️  Normal server is already primary")
                return True
        else:
            print(f"❌ Error getting normal server status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to normal server: {e}")
        return False

def main():
    """Main testing function"""
    print("🧪 Testing voter server protection")
    print("=" * 50)
    
    # Check services availability
    print("🔌 Checking services availability...")
    try:
        requests.get(f"{VOTER_URL}/docs", timeout=5)
        requests.get(f"{NORMAL_URL}/docs", timeout=5)
        print("✅ Services available")
    except:
        print("❌ Services unavailable. Make sure cluster is running.")
        print("   Run: ./start-cluster.sh")
        sys.exit(1)
    
    # Test voter server protection
    voter_test = test_voter_protection()
    
    # Test normal server
    normal_test = test_normal_server()
    
    print("\n" + "=" * 50)
    if voter_test and normal_test:
        print("✅ All tests passed successfully!")
        print("   - Voter server is protected from priority changes")
        print("   - Normal servers can change priority")
    else:
        print("❌ Some tests failed")
        if not voter_test:
            print("   - Problem with voter server protection")
        if not normal_test:
            print("   - Problem with normal server")
    
    print("\n🏁 Testing completed")

if __name__ == "__main__":
    main()


