import datetime
from layer1.db_connection import get_db_connection


def insert_order(order_id, customer_id, order_date, amount, status):
    conn = get_db_connection()
    curs = conn.cursor()

    try:
        # Convert Python date into string for JDBC compatibility
        order_date_str = order_date.strftime("%Y-%m-%d")

        # Insert into orders table
        curs.execute("""
            INSERT INTO orders (order_id, customer_id, order_date, amount, status)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, customer_id, order_date_str, amount, status))

        # Log into change_log table (with tenant_id support)
        curs.execute("""
            INSERT INTO change_log (table_name, record_id, change_type, tenant_id)
            VALUES ('orders', ?, 'INSERT', 'tenant_ABC')
        """, (order_id,))

        conn.commit()
    finally:
        curs.close()
        conn.close()


# Example usage
if __name__ == "__main__":
    insert_order("O2021", "C210", datetime.date.today(), 9999.00, "PAID")


