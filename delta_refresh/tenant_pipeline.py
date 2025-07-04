from layer1.db_connection import get_db_connection
from utils.embedding_generator import generate_embedding
from chroma_module.multitenant_chroma import upsert_tenant_embedding

print("✅ Imported tenant_pipeline")

def run_tenant_pipeline():
    """Process change_log entries on a per-tenant basis using Oracle join strategy."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT record_id, tenant_id FROM change_log")
            changes = cur.fetchall()
            print(f"📋 Found {len(changes)} entries in change_log")

            for record_id, tenant_id in changes:
                print(f"🔍 Looking up full order data for record_id: {record_id}")
                # Join ORDER_HEADER_ALL, ORDER_LINES_ALL, BILLING_SCHEDULES_ALL, etc.
                cur.execute(
                    '''
                    SELECT h.ORDER_ID, h.ORDER_NUMBER, h.ORDER_DATE, h.CUSTOMER_ID, h.STATUS,
                           l.LINE_ID, l.PRODUCT_ID, l.QUANTITY, l.UNIT_PRICE,
                           b.BILLING_SCH_ID, b.BILLING_TYPE,
                           d.DELIVERY_ID, d.DELIVERY_DATE,
                           p.PRICING_SCH_ID, p.PRICING_TYPE
                    FROM ORDER_HEADER_ALL h
                    LEFT JOIN ORDER_LINES_ALL l ON h.ORDER_ID = l.ORDER_ID
                    LEFT JOIN BILLING_SCHEDULES_ALL b ON h.ORDER_ID = b.ORDER_ID
                    LEFT JOIN ORDER_DELIVERIES_ALL d ON h.ORDER_ID = d.ORDER_ID
                    LEFT JOIN PRICING_SCHEDULES_ALL p ON h.ORDER_ID = p.ORDER_ID
                    WHERE h.ORDER_ID = :1
                    ''', [record_id]
                )
                row = cur.fetchone()
                if not row:
                    print(f"⚠️ No data found for ORDER_ID {record_id}, skipping.")
                    continue

                # Unpack and build a descriptive sentence
                (order_id, order_number, order_date, customer_id, status,
                 line_id, product_id, quantity, unit_price,
                 billing_sch_id, billing_type,
                 delivery_id, delivery_date,
                 pricing_sch_id, pricing_type) = row

                sentence = (
                    f"Order {order_number} (ID: {order_id}) for customer {customer_id} on {order_date}, "
                    f"status: {status}, line: {line_id}, product: {product_id}, qty: {quantity}, price: {unit_price}, "
                    f"billing: {billing_type}, delivery: {delivery_date}, pricing: {pricing_type}"
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
