from layer1.db_connection import get_db_connection
from utils.embedding_generator import generate_embedding
from chroma_module.multitenant_chroma import upsert_tenant_embedding

print("✅ Imported tenant_pipeline")

def run_tenant_pipeline():
    """Process change_log entries on a per-tenant basis."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT record_id, tenant_id FROM change_log")
            changes = cur.fetchall()
            print(f"📋 Found {len(changes)} entries in change_log")

            for record_id, tenant_id in changes:
                print(f"🔍 Looking up full order data for record_id: {record_id}")
                cur.execute(
                    "SELECT order_id, customer_id, order_date, amount, status FROM orders WHERE order_id = ?",
                    (record_id,),
                )
                row = cur.fetchone()
                if not row:
                    print(f"⚠️ No data found for order_id {record_id}, skipping.")
                    continue

                order_id, customer_id, order_date, amount, status = row
                sentence = (
                    f"Order {order_id} for customer {customer_id} on {order_date} "
                    f"amount {amount} status {status}"
                )

                embedding = generate_embedding(sentence)
                print(f"🧠 Generated embedding (first 5 dims): {embedding[:5]}")

                try:
                    print(f"📡 Upserting embedding for tenant {tenant_id} with record_id {record_id}")
                    upsert_tenant_embedding(tenant_id, record_id, sentence, embedding)
                    print(f"✅ Upserted embedding for tenant {tenant_id} with record_id {record_id}")
                except Exception as e:
                    print(f"❌ Error during upsert for record_id {record_id}: {e}")

            print("🧹 Cleaning up change_log")
            cur.execute("DELETE FROM change_log")
            conn.commit()
        finally:
            cur.close()
    finally:
        conn.close()
        print("🔒 DB connection closed")

def process_tenant_pipeline():
    """Alias for ``run_tenant_pipeline`` for compatibility."""
    run_tenant_pipeline()

if __name__ == "__main__":
    print("🚀 Running tenant pipeline")
    run_tenant_pipeline()
