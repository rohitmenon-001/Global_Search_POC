#!/usr/bin/env python3
"""
Test script to verify RAG agent integration with Streamlit app
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_rag_import():
    """Test if RAG agent can be imported"""
    try:
        from rag_agent_simple import SimpleRAGAgent
        print("✅ RAG agent import successful")
        return True
    except ImportError as e:
        print(f"❌ RAG agent import failed: {e}")
        return False

def test_rag_initialization():
    """Test if RAG agent can be initialized"""
    try:
        from rag_agent_simple import SimpleRAGAgent
        agent = SimpleRAGAgent(tenant_id="tenant_ABC")
        print("✅ RAG agent initialization successful")
        return True
    except Exception as e:
        print(f"❌ RAG agent initialization failed: {e}")
        return False

def test_rag_response():
    """Test if RAG agent can generate responses"""
    try:
        from rag_agent_simple import SimpleRAGAgent
        agent = SimpleRAGAgent(tenant_id="tenant_ABC")
        
        # Test with a simple query
        result = agent.generate_response("What are the highest value orders?")
        
        if result['status'] == 'success':
            print("✅ RAG agent response generation successful")
            print(f"Response: {result['response'][:100]}...")
            return True
        else:
            print(f"❌ RAG agent response failed: {result['response']}")
            return False
            
    except Exception as e:
        print(f"❌ RAG agent response test failed: {e}")
        return False

def test_streamlit_integration():
    """Test if Streamlit app can import RAG agent"""
    try:
        # Simulate what the Streamlit app does
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            from rag_agent_simple import SimpleRAGAgent
            RAG_AVAILABLE = True
            print("✅ Streamlit integration test successful")
            return True
        except ImportError as e:
            print(f"❌ Streamlit integration test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Streamlit integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing RAG Agent Integration...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_rag_import),
        ("Initialization Test", test_rag_initialization),
        ("Response Test", test_rag_response),
        ("Streamlit Integration Test", test_streamlit_integration)
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
        print("🎉 All tests passed! RAG integration is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 