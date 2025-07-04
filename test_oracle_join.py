#!/usr/bin/env python3
"""
Test script to debug Oracle join queries
"""

from layer1.db_connection import get_db_connection

def test_oracle_connection():
    """Test basic Oracle connection"""
    try:
        conn = get_db_connection()
        print("✅ Oracle connection successful!")
        return conn
    except Exception as e:
        print(f"❌ Oracle connection failed: {e}")
        return None

def test_table_access(conn, table_name):
    """Test access to a specific table"""
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        print(f"✅ {table_name} has {count} records")
        cur.close()
        return True
    except Exception as e:
        print(f"❌ Failed to access {table_name}: {e}")
        return False

def test_simple_join(conn):
    """Test a simple join query"""
    try:
        cur = conn.cursor()
        # Test with a simpler join first
        cur.execute("""
            SELECT h.ORDER_ID, h.ORDER_NUMBER 
            FROM ORDER_HEADER_ALL h 
            WHERE ROWNUM <= 5
        """)
        rows = cur.fetchall()
        print(f"✅ Simple ORDER_HEADER_ALL query successful - found {len(rows)} rows")
        for row in rows:
            print(f"   Order ID: {row[0]}, Order Number: {row[1]}")
        cur.close()
        return True
    except Exception as e:
        print(f"❌ Simple query failed: {e}")
        return False

def test_join_query(conn):
    """Test the actual join query"""
    try:
        cur = conn.cursor()
        # Test the join with a limit
        cur.execute("""
            SELECT h.ORDER_ID, h.ORDER_NUMBER, l.LINE_ID
            FROM ORDER_HEADER_ALL h 
            LEFT JOIN ORDER_LINES_ALL l ON h.ORDER_ID = l.ORDER_ID
            WHERE ROWNUM <= 5
        """)
        rows = cur.fetchall()
        print(f"✅ Join query successful - found {len(rows)} rows")
        for row in rows:
            print(f"   Order ID: {row[0]}, Order Number: {row[1]}, Line ID: {row[2]}")
        cur.close()
        return True
    except Exception as e:
        print(f"❌ Join query failed: {e}")
        return False

def main():
    print("🔍 Testing Oracle Join Queries...")
    print("=" * 50)
    
    # Test connection
    conn = test_oracle_connection()
    if not conn:
        return
    
    print("\n📊 Testing individual table access:")
    print("-" * 30)
    
    # Test each table individually
    tables = ['ORDER_HEADER_ALL', 'ORDER_LINES_ALL', 'BILLING_SCHEDULES_ALL', 
              'ORDER_DELIVERIES_ALL', 'PRICING_SCHEDULES_ALL']
    
    for table in tables:
        test_table_access(conn, table)
    
    print("\n🔗 Testing simple query:")
    print("-" * 30)
    test_simple_join(conn)
    
    print("\n🔗 Testing join query:")
    print("-" * 30)
    test_join_query(conn)
    
    conn.close()
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main() 