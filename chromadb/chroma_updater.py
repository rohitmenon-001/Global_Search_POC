from layer1.db_connection import get_db_connection


def generate_embedding(sentence: str):
    """Return a dummy embedding for the given sentence."""
    # Simple placeholder - returns fixed floats based on sentence length
    length = float(len(sentence))
    return [length, length / 2, length / 3]


def process_changes():
    conn = get_db_connection()
    try:
        curs = conn.cursor()
        try:
            curs.execute("SELECT record_id FROM change_log WHERE table_name='orders'")
            rows = curs.fetchall()
            for (record_id,) in rows:
                curs.execute(
                    "SELECT order_id, customer_id, order_date, amount, status FROM orders WHERE order_id = ?",
                    (record_id,),
                )
                order = curs.fetchone()
                if not order:
                    continue
                order_id, customer_id, order_date, amount, status = order
                sentence = (
                    f"Order {order_id} for customer {customer_id} on {order_date} "
                    f"amount {amount} status {status}"
                )
                embedding = generate_embedding(sentence)
                print(sentence)
                print(embedding)
        finally:
            curs.close()
    finally:
        conn.close()


if __name__ == "__main__":
    process_changes()
