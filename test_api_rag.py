#!/usr/bin/env python3
"""
Test script to verify Flask API RAG endpoint works correctly
"""

import requests
import json

def test_rag_api():
    print("🧪 Testing Flask API RAG Endpoint...")
    print("=" * 50)
    
    # Test data
    tenant_id = "tenant_ABC"
    query = "What are the highest value orders?"
    
    url = f"http://127.0.0.1:5000/api/tenant/{tenant_id}/ai/query"
    headers = {"X-Tenant-ID": tenant_id}
    payload = {"query": query}
    
    try:
        print(f"📡 Sending request to: {url}")
        print(f"🔍 Query: {query}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"📝 Response: {result.get('response', 'No response')[:200]}...")
            print(f"🔧 Status: {result.get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask API. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_rag_api()
    print("\n" + "=" * 50)
    if success:
        print("🎉 RAG API test passed! Your app should work correctly.")
    else:
        print("❌ RAG API test failed. Check the Flask server and Ollama.") 