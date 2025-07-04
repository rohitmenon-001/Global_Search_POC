import requests
import json
import time

def test_semantic_search():
    """Test the semantic search API endpoint"""
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test queries
    test_queries = [
        "Order for customer C100",
        "Orders with status PAID",
        "High value orders over 5000",
        "Recent orders from last month",
        "Orders with billing type LINE"
    ]
    
    base_url = "http://127.0.0.1:5000"
    tenant_id = "tenant_ABC"
    
    print(f"🔍 Testing semantic search for tenant: {tenant_id}")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: '{query}'")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/api/tenant/{tenant_id}/search",
                headers={
                    "Content-Type": "application/json",
                    "X-Tenant-ID": tenant_id
                },
                json={"query": query},
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Success! Found {len(results)} results")
                
                for j, result in enumerate(results, 1):
                    print(f"  {j}. Record ID: {result['record_id']}")
                    print(f"     Score: {result['score']:.4f}")
                    print(f"     Content: {result['sentence'][:100]}...")
                    print()
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - server may not be running")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Search testing completed!")

if __name__ == "__main__":
    test_semantic_search() 