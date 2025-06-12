from layer1.db_connection import get_db_connection


def process_delta_changes():
    """Process all rows in change_log and then clear the log."""
    conn = get_db_connection()
    try:
        curs = conn.cursor()
        try:
            curs.execute("SELECT record_id, change_type, change_timestamp FROM change_log")
            rows = curs.fetchall()
            for row in rows:
                record_id, change_type, timestamp = row
                print(record_id, change_type, timestamp)

            # After processing, clear the change_log
            curs.execute("DELETE FROM change_log")
            conn.commit()
        finally:
            curs.close()
    finally:
        conn.close()


if __name__ == "__main__":
    process_delta_changes()
