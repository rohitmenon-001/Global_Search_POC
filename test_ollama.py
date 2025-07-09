#!/usr/bin/env python3
"""
Simple diagnostic script to test Ollama connectivity and model availability
"""

import requests
import json

def test_ollama():
    print("🔍 Testing Ollama Connection...")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running and responding")
        else:
            print(f"❌ Ollama health check failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Ollama connection timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Make sure it's running on localhost:11434")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Check available models
    print("\n2. Checking available models...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models_data = response.json()
        available_models = [model.get('name', '') for model in models_data.get('models', [])]
        
        if available_models:
            print(f"✅ Available models: {', '.join(available_models)}")
            
            # Test 3: Test model inference
            print(f"\n3. Testing inference with model: {available_models[0]}")
            test_model = available_models[0].split(':')[0]  # Remove tag if present
            
            test_payload = {
                "model": test_model,
                "prompt": "Hello, this is a test. Please respond with 'Test successful'.",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 50
                }
            }
            
            print("   Sending test request...")
            inference_response = requests.post(
                "http://localhost:11434/api/generate",
                json=test_payload,
                timeout=30
            )
            
            if inference_response.status_code == 200:
                response_data = inference_response.json()
                response_text = response_data.get('response', '')
                print(f"✅ Model inference successful!")
                print(f"   Response: {response_text[:100]}...")
                return True
            else:
                print(f"❌ Model inference failed: {inference_response.status_code}")
                print(f"   Response: {inference_response.text}")
                return False
        else:
            print("❌ No models available. Please pull a model first.")
            print("   Try: ollama pull llama3")
            return False
            
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Ollama is working correctly.")
    else:
        print("❌ Tests failed. Please check Ollama setup.") 