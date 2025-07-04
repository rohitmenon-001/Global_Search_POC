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
            cur.execute(
                '''
                SELECT h.ORDER_ID, h.ORDER_NUMBER, h.BOOKED_DATE, h.SELL_TO_CUSTOMER_ID, h.STATUS,
                       l.LINE_ID, l.ITEM_ID, l.ORDERED_QUANTITY, l.UNIT_PRICE,
                       b.BILLING_SCH_ID, b.BILLING_LINE_TYPE,
                       d.DELIVERY_ID, d.DELIVERY_DATE_FROM,
                       p.PRICING_SCH_ID, p.PRICING_STATUS
                FROM (
                    SELECT * FROM ORDER_HEADER_ALL WHERE ROWNUM <= 50
                ) h
                LEFT JOIN ORDER_LINES_ALL l ON h.ORDER_ID = l.ORDER_ID
                LEFT JOIN BILLING_SCHEDULES_ALL b ON h.ORDER_ID = b.ORDER_ID
                LEFT JOIN ORDER_DELIVERIES_ALL d ON h.ORDER_ID = d.ORDER_ID
                LEFT JOIN PRICING_SCHEDULES_ALL p ON h.ORDER_ID = p.ORDER_ID
                ''')
            rows = cur.fetchall()
            print(f"📦 Found {len(rows)} joined records in Oracle database.")

            for row in rows:
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
