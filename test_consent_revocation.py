#!/usr/bin/env python3
"""
Test script for consent revocation API
"""

import requests
import json

# Test data
base_url = "http://localhost:8000"

def test_consent_revocation():
    """Test the consent revocation endpoint"""
    
    print("🧪 Testing Consent Revocation API...")
    
    # Test 1: Revoke email consent
    print("\n1️⃣ Testing email consent revocation...")
    
    payload = {
        "consent_type": "email"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer mock_jwt_token"  # Mock token for testing
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/consent/revoke",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"📤 Request: POST /api/consent/revoke")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        print(f"📨 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Email consent revocation: {result.get('message', 'SUCCESS')}")
        else:
            print(f"❌ Email consent revocation failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Revoke all consent
    print("\n2️⃣ Testing all consent revocation...")
    
    payload = {
        "consent_type": "all"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/consent/revoke",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"📤 Request: POST /api/consent/revoke")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        print(f"📨 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ All consent revocation: {result.get('message', 'SUCCESS')}")
        else:
            print(f"❌ All consent revocation failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_categories_endpoint():
    """Test the unified categories endpoint"""
    
    print("\n🧪 Testing Categories API...")
    
    headers = {
        "Authorization": "Bearer mock_jwt_token"  # Mock token for testing
    }
    
    try:
        response = requests.get(
            f"{base_url}/api/categories/unified",
            headers=headers,
            timeout=10
        )
        
        print(f"📤 Request: GET /api/categories/unified")
        print(f"📨 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            categories = result.get('categories', {})
            print(f"✅ Categories retrieved: {len(categories)} categories found")
            for category, data in categories.items():
                print(f"   📂 {category}: {data}")
        else:
            print(f"❌ Categories retrieval failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_health_endpoint():
    """Test the health endpoint"""
    
    print("\n🧪 Testing Health Endpoint...")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        
        print(f"📤 Request: GET /health")
        print(f"📨 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Server health: {result.get('status', 'OK')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    
    # Test basic connectivity first
    test_health_endpoint()
    
    # Test categories
    test_categories_endpoint()
    
    # Test consent revocation
    test_consent_revocation()
    
    print("\n🏁 Tests completed!")
