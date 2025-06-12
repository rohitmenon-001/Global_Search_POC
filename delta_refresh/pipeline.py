from layer1.db_connection import get_db_connection
from chromadb.chroma_client import upsert_embedding


def generate_embedding(sentence: str):
    """Return a dummy embedding for the given sentence."""
    length = float(len(sentence))
    return [length, length / 2, length / 3]


def run_pipeline():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT record_id FROM change_log")
            changes = cur.fetchall()
            for (record_id,) in changes:
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
                upsert_embedding(record_id, sentence, embedding)
            cur.execute("DELETE FROM change_log")
            conn.commit()
        finally:
            cur.close()
    finally:
        conn.close()


if __name__ == "__main__":
    run_pipeline()
