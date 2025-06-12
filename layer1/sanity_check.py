from layer1.db_connection import get_db_connection


def run_sanity_check():
    """Execute simple queries to verify orders and change_log tables."""
    conn = get_db_connection()
    try:
        curs = conn.cursor()
        try:
            curs.execute("SELECT * FROM orders")
            orders = curs.fetchall()
            print("Orders:")
            for row in orders:
                print(row)

            curs.execute("SELECT * FROM change_log")
            changes = curs.fetchall()
            print("Change Log:")
            for row in changes:
                print(row)
        finally:
            curs.close()
    finally:
        conn.close()


if __name__ == "__main__":
    run_sanity_check()
