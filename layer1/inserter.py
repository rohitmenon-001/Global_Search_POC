import datetime
from layer1.db_connection import get_db_connection


def insert_order(order_id, customer_id, order_date, amount, status):
    conn = get_db_connection()
    curs = conn.cursor()

    try:
        # Insert into orders table
        curs.execute(
            """
            INSERT INTO orders (order_id, customer_id, order_date, amount, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, customer_id, order_date, amount, status),
        )

        # Log into change_log table
        curs.execute(
            """
            INSERT INTO change_log (table_name, record_id, change_type)
            VALUES ('orders', ?, 'INSERT')
            """,
            (order_id,),
        )

        conn.commit()
    finally:
        curs.close()
        conn.close()


# Example usage
if __name__ == "__main__":
    insert_order("O1001", "C100", datetime.date.today(), 5000.00, "PAID")
