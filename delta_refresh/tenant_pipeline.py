from layer1.db_connection import get_db_connection
from utils.embedding_generator import generate_embedding
from chromadb.multitenant_chroma import upsert_tenant_embedding


def run_tenant_pipeline():
    """Process change_log entries on a per-tenant basis."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT record_id, tenant_id FROM change_log")
            changes = cur.fetchall()
            for record_id, tenant_id in changes:
                cur.execute(
                    "SELECT order_id, customer_id, order_date, amount, status FROM orders WHERE order_id = ?",
                    (record_id,),
                )
                row = cur.fetchone()
                if not row:
                    continue
                order_id, customer_id, order_date, amount, status = row
                sentence = (
                    f"Order {order_id} for customer {customer_id} on {order_date} "
                    f"amount {amount} status {status}"
                )
                embedding = generate_embedding(sentence)
                upsert_tenant_embedding(tenant_id, record_id, sentence, embedding)
            cur.execute("DELETE FROM change_log")
            conn.commit()
        finally:
            cur.close()
    finally:
        conn.close()


if __name__ == "__main__":
    run_tenant_pipeline()
