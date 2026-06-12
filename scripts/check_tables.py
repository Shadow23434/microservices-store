#!/usr/bin/env python3
"""Check what tables exist in each database"""
import sys
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = sys.argv[1]
parsed = urlparse(DATABASE_URL)

DBS = [
    'catalog_db',
    'customer_db',
    'product_db',
    'cart_db',
    'staff_db',
    'manager_db',
    'order_db',
    'ship_db',
    'pay_db',
    'comment_rate_db',
    'recommender_db',
    'gateway_db'
]

for db_name in DBS:
    print(f"\n{'='*60}")
    print(f"Database: {db_name}")
    print('='*60)

    try:
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=db_name
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]

        if tables:
            for table in tables:
                print(f"  - {table}")
        else:
            print("  (no tables)")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"  ERROR: {e}")
