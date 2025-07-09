#!/usr/bin/env python3
"""
Test script to verify API integration with RAG agent
"""

import requests
import json
import time

def test_api_status():
    """Test API status endpoint"""
    try:
        response = requests.get("http://127.0.0.1:5000/api/tenant/tenant_ABC/ai/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data}")
            return True
        else:
            print(f"❌ API Status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Status error: {e}")
        return False

def test_ai_query():
    """Test AI query endpoint"""
    try:
        query = "What are the highest value orders?"
        response = requests.post(
            "http://127.0.0.1:5000/api/tenant/tenant_ABC/ai/query",
            json={"query": query},
            headers={"X-Tenant-ID": "tenant_ABC"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Query successful")
            print(f"Status: {data.get('status')}")
            print(f"Response: {data.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ AI Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI Query error: {e}")
        return False

def test_semantic_search():
    """Test semantic search endpoint"""
    try:
        query = "high value orders"
        response = requests.post(
            "http://127.0.0.1:5000/api/tenant/tenant_ABC/search",
            json={"query": query},
            headers={"X-Tenant-ID": "tenant_ABC"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Semantic Search successful: {len(data)} results")
            return True
        else:
            print(f"❌ Semantic Search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Semantic Search error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Testing API Integration...")
    print("=" * 50)
    
    # Wait a moment for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(2)
    
    tests = [
        ("API Status Test", test_api_status),
        ("Semantic Search Test", test_semantic_search),
        ("AI Query Test", test_ai_query)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"⚠️ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API tests passed! Integration is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("💡 Make sure the Flask API server is running: python api/app.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 