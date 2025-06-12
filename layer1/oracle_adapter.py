import os
import cx_Oracle

# Placeholder credentials - can be overridden by environment variables
ORACLE_HOST = os.getenv("ORACLE_HOST", "your_host")
ORACLE_PORT = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_SERVICE_NAME = os.getenv("ORACLE_SERVICE_NAME", "your_service")
ORACLE_USER = os.getenv("ORACLE_USER", "your_user")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "your_password")


def get_oracle_connection():
    """Return a live Oracle DB connection."""
    dsn = cx_Oracle.makedsn(ORACLE_HOST, ORACLE_PORT, service_name=ORACLE_SERVICE_NAME)
    conn = None
    try:
        conn = cx_Oracle.connect(
            user=ORACLE_USER,
            password=ORACLE_PASSWORD,
            dsn=dsn,
        )
    except cx_Oracle.Error as err:
        print(f"Oracle connection error: {err}")
    finally:
        return conn


def fetch_change_log():
    """Fetch all records from the change_log table."""
    conn = get_oracle_connection()
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        cur.execute("SELECT table_name, record_id, change_type FROM change_log")
        rows = cur.fetchall()
        return rows
    except cx_Oracle.Error as err:
        print(f"Error querying change_log: {err}")
        return []
    finally:
        cur.close()
        conn.close()


def fetch_order_by_id(record_id):
    """Fetch a single order record by ID."""
    conn = get_oracle_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT order_id, customer_id, order_date, amount, status FROM orders WHERE order_id = :1",
            (record_id,),
        )
        row = cur.fetchone()
        return row
    except cx_Oracle.Error as err:
        print(f"Error querying orders table: {err}")
        return None
    finally:
        cur.close()
        conn.close()
