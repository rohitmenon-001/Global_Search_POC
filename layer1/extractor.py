import pandas as pd
from layer1.db_connection import get_db_connection


def extract_change_log():
    """Query all entries from the change_log table and return a DataFrame."""
    conn = get_db_connection()
    try:
        df = pd.read_sql("SELECT * FROM change_log", conn)
        print(df)
        return df
    finally:
        conn.close()


if __name__ == "__main__":
    extract_change_log()
