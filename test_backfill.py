#!/usr/bin/env python3
"""
Test script for Oracle backfill process with better error handling
"""

from layer1.db_connection import get_db_connection
from utils.embedding_generator import generate_embedding
from chroma_module.multitenant_chroma import upsert_tenant_embedding
import time
import traceback

def test_backfill_sample(tenant_id="tenant_ABC", limit=5):
    """Test backfill with a small sample first"""
    print(f"🔄 Testing backfill with {limit} sample records...")
    
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        
        # Test the join query with a small limit
        query = f"""
        SELECT h.ORDER_ID, h.ORDER_NUMBER, h.BOOKED_DATE, h.SELL_TO_CUSTOMER_ID, h.STATUS,
               l.LINE_ID, l.ITEM_ID, l.ORDERED_QUANTITY, l.UNIT_PRICE,
               b.BILLING_SCH_ID, b.BILLING_LINE_TYPE,
               d.DELIVERY_ID, d.DELIVERY_DATE_FROM,
               p.PRICING_SCH_ID, p.PRICING_STATUS
        FROM ORDER_HEADER_ALL h
        LEFT JOIN ORDER_LINES_ALL l ON h.ORDER_ID = l.ORDER_ID
        LEFT JOIN BILLING_SCHEDULES_ALL b ON h.ORDER_ID = b.ORDER_ID
        LEFT JOIN ORDER_DELIVERIES_ALL d ON h.ORDER_ID = d.ORDER_ID
        LEFT JOIN PRICING_SCHEDULES_ALL p ON h.ORDER_ID = p.ORDER_ID
        WHERE ROWNUM <= {limit}
        """
        
        print(f"📊 Executing query: {query[:100]}...")
        cur.execute(query)
        rows = cur.fetchall()
        print(f"✅ Query successful - found {len(rows)} rows")
        
        success_count = 0
        for i, row in enumerate(rows, 1):
            try:
                (order_id, order_number, booked_date, sell_to_customer_id, status,
                 line_id, item_id, ordered_quantity, unit_price,
                 billing_sch_id, billing_line_type,
                 delivery_id, delivery_date_from,
                 pricing_sch_id, pricing_status) = row
                
                sentence = (
                    f"Order {order_number} (ID: {order_id}) for customer {sell_to_customer_id} on {booked_date}, "
                    f"status: {status}, line: {line_id}, item: {item_id}, qty: {ordered_quantity}, price: {unit_price}, "
                    f"billing: {billing_line_type}, delivery from: {delivery_date_from}, pricing status: {pricing_status}"
                )
                
                print(f"  📝 Processing record {i}: {order_id}")
                embedding = generate_embedding(sentence)
                print(f"  🧠 Generated embedding (first 5 dims): {embedding[:5]}")
                
                upsert_tenant_embedding(tenant_id, order_id, sentence, embedding)
                print(f"  ✅ Upserted order {order_id} into ChromaDB for tenant '{tenant_id}'")
                success_count += 1
                
                # Small delay to avoid overwhelming the system
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  ❌ Error processing record {i}: {e}")
                traceback.print_exc()
                continue
        
        print(f"\n📊 Summary: {success_count}/{len(rows)} records processed successfully")
        cur.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        traceback.print_exc()
        return False
    finally:
        conn.close()
        print("🔒 Connection closed")
    
    return success_count > 0

def main():
    print("🧪 Testing Oracle Backfill Process...")
    print("=" * 50)
    
    # Test with a small sample first
    if test_backfill_sample(limit=3):
        print("\n✅ Sample backfill successful! Ready for full backfill.")
        print("\n💡 To run full backfill, use: python backfill_orders.py")
    else:
        print("\n❌ Sample backfill failed. Check the errors above.")

if __name__ == "__main__":
    main() 