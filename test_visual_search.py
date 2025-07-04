import requests
import json
import time
import re
import pandas as pd

def test_visual_search():
    """Test the enhanced visual search interface with better data extraction"""
    
    print("🎨 Testing Enhanced Visual Search Interface")
    print("=" * 60)
    print("This test demonstrates the improved data extraction and visualization")
    print()
    
    # Wait for server
    print("⏳ Connecting to search server...")
    time.sleep(2)
    
    base_url = "http://127.0.0.1:5000"
    tenant_id = "tenant_ABC"
    
    # Test queries that will show different visual elements
    test_queries = [
        "High value orders over 5000",
        "Active orders for customers",
        "Orders with billing information"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
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
                print(f"✅ Found {len(results)} results")
                
                # Process results like the visual interface does
                processed_results = []
                for j, res in enumerate(results):
                    sentence = res['sentence']
                    
                    # Extract key information
                    order_match = re.search(r'Order\s+([^\s(]+)', sentence)
                    order_number = order_match.group(1) if order_match else "N/A"
                    
                    customer_match = re.search(r'customer\s+([^\s,]+)', sentence, re.IGNORECASE)
                    customer = customer_match.group(1) if customer_match else "N/A"
                    
                    status_match = re.search(r'status:\s*([^,]+)', sentence, re.IGNORECASE)
                    status = status_match.group(1) if status_match else "N/A"
                    
                    date_match = re.search(r'(\d{2}-[A-Z]{3}-\d{2})', sentence)
                    date = date_match.group(1) if date_match else "N/A"
                    
                    relevance = max(0, 100 - (res['score'] * 50))
                    
                    processed_results.append({
                        'Rank': j + 1,
                        'Order': order_number,
                        'Customer': customer,
                        'Status': status,
                        'Date': date,
                        'Relevance': relevance,
                        'Score': res['score']
                    })
                
                # Display processed results
                print("\n📊 Processed Results:")
                print(f"{'Rank':<4} {'Order':<20} {'Customer':<10} {'Status':<15} {'Relevance':<10}")
                print("-" * 70)
                
                for result in processed_results:
                    rank_icon = "🥇" if result['Rank'] == 1 else "🥈" if result['Rank'] == 2 else "🥉" if result['Rank'] == 3 else "  "
                    status_icon = "🟢" if 'ACTIVE' in result['Status'].upper() else "💰" if 'PAID' in result['Status'].upper() else "🔴" if 'TERMINATED' in result['Status'].upper() else "⚪"
                    
                    print(f"{rank_icon} {result['Rank']:<2} {result['Order']:<20} {result['Customer']:<10} {status_icon} {result['Status']:<12} {result['Relevance']:>6.1f}%")
                
                # Show analytics
                print(f"\n📈 Analytics:")
                print(f"   • Best Score: {min([r['score'] for r in results]):.4f}")
                print(f"   • Average Score: {sum([r['score'] for r in results]) / len(results):.4f}")
                print(f"   • Score Range: {min([r['score'] for r in results]):.4f} - {max([r['score'] for r in results]):.4f}")
                
                # Status distribution
                statuses = [r['Status'] for r in processed_results]
                status_counts = {}
                for status in statuses:
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                print(f"   • Status Distribution: {status_counts}")
                
            else:
                print(f"❌ Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            break
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("🎨 Visual Search Test Complete!")
    print("\n💡 Key Visual Enhancements:")
    print("   • 📊 Score distribution histograms")
    print("   • 🥇🥈🥉 Rank indicators with medals")
    print("   • 🟢💰🔴 Color-coded status indicators")
    print("   • 📈 Progress bars for relevance")
    print("   • 📋 Pie charts for status distribution")
    print("   • 📊 Scatter plots for relevance vs rank")
    print("   • 💡 AI-powered search insights")
    print("\n🌐 Open http://localhost:8501 to see the full visual interface!")

if __name__ == "__main__":
    test_visual_search() 