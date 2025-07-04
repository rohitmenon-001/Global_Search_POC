import oracledb
from config import db_config

# Initialize Oracle client (if needed)
# oracledb.init_oracle_client(lib_dir=None)  # Uncomment if using Oracle Instant Client

def get_oracle_connection():
    try:
        conn = oracledb.connect(
            user=db_config.ORACLE_USER,
            password=db_config.ORACLE_PASSWORD,
            dsn=db_config.ORACLE_DSN
        )
        return conn
    except oracledb.DatabaseError as err:
        print(f"Oracle connection error: {err}")
        return None

def fetch_change_log():
    conn = get_oracle_connection()
    if conn is None:
        return []
    try:
        cur = conn.cursor()
        cur.execute("SELECT table_name, record_id, change_type, tenant_id FROM change_log")
        rows = cur.fetchall()
        return rows
    except oracledb.DatabaseError as err:
        print(f"Error querying change_log: {err}")
        return []
    finally:
        if conn:
            conn.close()

def fetch_order_by_id(record_id):
    conn = get_oracle_connection()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT order_id, customer_id, order_date, amount, status FROM orders WHERE order_id = :1",
            (record_id,)
        )
        row = cur.fetchone()
        return row
    except oracledb.DatabaseError as err:
        print(f"Error querying orders table: {err}")
        return None
    finally:
        if conn:
            conn.close()

def insert_order(order_id, customer_id, order_date, amount, status, tenant_id="tenant_ABC"):
    conn = get_oracle_connection()
    if conn is None:
        return False
    try:
        cur = conn.cursor()
        # Insert order
        cur.execute("""
            INSERT INTO orders (order_id, customer_id, order_date, amount, status)
            VALUES (:1, :2, :3, :4, :5)
        """, (order_id, customer_id, order_date, amount, status))
        # Log change
        cur.execute("""
            INSERT INTO change_log (table_name, record_id, change_type, tenant_id)
            VALUES ('orders', :1, 'INSERT', :2)
        """, (order_id, tenant_id))
        conn.commit()
        return True
    except oracledb.DatabaseError as err:
        print(f"Error inserting order: {err}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
