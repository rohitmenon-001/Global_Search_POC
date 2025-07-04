import requests
import json
import time

def demo_semantic_search():
    """Demonstrate the power of semantic search with various query types"""
    
    print("🚀 Global Search POC - Semantic Search Demonstration")
    print("=" * 70)
    print("This demo shows how semantic search understands meaning, not just keywords!")
    print()
    
    # Wait for server
    print("⏳ Connecting to search server...")
    time.sleep(2)
    
    base_url = "http://127.0.0.1:5000"
    tenant_id = "tenant_ABC"
    
    # Demo scenarios
    scenarios = [
        {
            "title": "🔍 Customer Search",
            "description": "Finding orders by customer - even with different terminology",
            "queries": [
                "Orders for customer C100",
                "Customer 100 orders",
                "Orders belonging to client 100"
            ]
        },
        {
            "title": "💰 Value-Based Search", 
            "description": "Finding orders by value ranges and pricing",
            "queries": [
                "High value orders over 5000",
                "Expensive orders",
                "Orders with high unit price"
            ]
        },
        {
            "title": "📅 Date-Based Search",
            "description": "Finding orders by time periods",
            "queries": [
                "Recent orders from last month",
                "Orders from June 2021",
                "New orders this year"
            ]
        },
        {
            "title": "📋 Status-Based Search",
            "description": "Finding orders by their current status",
            "queries": [
                "Active orders",
                "Orders with status PAID",
                "Terminated orders"
            ]
        },
        {
            "title": "🧾 Billing Search",
            "description": "Finding orders by billing information",
            "queries": [
                "Orders with billing type LINE",
                "Billing schedules",
                "Payment related orders"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['title']}")
        print(f"📝 {scenario['description']}")
        print("-" * 50)
        
        for i, query in enumerate(scenario['queries'], 1):
            print(f"\n  Query {i}: '{query}'")
            
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
                    print(f"    ✅ Found {len(results)} results")
                    
                    # Show best match
                    if results:
                        best_match = results[0]
                        print(f"    🏆 Best Match (Score: {best_match['score']:.4f}):")
                        print(f"       Order: {best_match['sentence'][:80]}...")
                    
                else:
                    print(f"    ❌ Error {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ Connection error: {e}")
                break
        
        time.sleep(1)  # Brief pause between scenarios
    
    print("\n" + "=" * 70)
    print("🎉 Semantic Search Demo Complete!")
    print("\n💡 Key Insights:")
    print("   • Semantic search understands meaning, not just exact words")
    print("   • It can handle synonyms and different phrasings")
    print("   • Results are ranked by relevance (lower scores = better matches)")
    print("   • The system works with natural language queries")
    print("\n🌐 Try the Streamlit UI at: http://localhost:8501")
    print("🔧 API endpoint: http://127.0.0.1:5000/api/tenant/{tenant_id}/search")

if __name__ == "__main__":
    demo_semantic_search() 