# backfill_orders.py

from layer1.db_connection import get_db_connection
from utils.embedding_generator import generate_embedding
from chroma_module.multitenant_chroma import upsert_tenant_embedding

def backfill_orders_to_chroma(tenant_id="tenant_ABC"):
    print("🔄 Starting backfill of orders into ChromaDB...")
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT order_id, customer_id, order_date, amount, status FROM orders")
            rows = cur.fetchall()
            print(f"📦 Found {len(rows)} orders in H2 database.")

            for row in rows:
                order_id, customer_id, order_date, amount, status = row
                sentence = (
                    f"Order {order_id} for customer {customer_id} on {order_date} "
                    f"amount {amount} status {status}"
                )
                embedding = generate_embedding(sentence)
                print(f"🧠 Generated embedding for {order_id} (first 5 dims): {embedding[:5]}")
                upsert_tenant_embedding(tenant_id, order_id, sentence, embedding)
                print(f"✅ Upserted order {order_id} into ChromaDB for tenant '{tenant_id}'")

        finally:
            cur.close()
            print("🔒 Cursor closed.")
    finally:
        conn.close()
        print("🔒 Connection closed.")

if __name__ == "__main__":
    backfill_orders_to_chroma()
