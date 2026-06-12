#!/usr/bin/env python3
"""
Fix reviews and orders by fetching product_id_map from existing products API.
Run this after seed_all_services.py if products already exist.
"""

import os
import sys
import requests
import psycopg2
from datetime import datetime

# ── PostgreSQL config ──────────────────────────────────────────────────────────
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'YJtnVQdASgimWjIppfKiPXWrVJkqAzbw')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'thomas.proxy.rlwy.net')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '35746')

# ── HTTP Service URLs ──────────────────────────────────────────────────────────
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'https://microservice-store-production.up.railway.app/api/products/')

# ── DB connection strings ──────────────────────────────────────────────────────
def get_db_url(db_name):
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{db_name}"

DATABASES = {
    'customers': get_db_url('customer_db'),
    'reviews': get_db_url('comment_rate_db'),
    'orders': get_db_url('order_db'),
    'payments': get_db_url('pay_db'),
    'shipments': get_db_url('ship_db'),
}

# ── Sample data (from seed_all_services.py) ────────────────────────────────────
CUSTOMERS = [
    {"name": "Nguyen Van An", "email": "nguyenvanan@example.com"},
    {"name": "Tran Minh Chau", "email": "tranminhchau@example.com"},
    {"name": "Le Hoang Duc", "email": "lehoangduc@example.com"},
    {"name": "Le Thi Mai", "email": "mai@example.com"},
    {"name": "Nguyen Tuan Kiet", "email": "kiet@example.com"},
    {"name": "Tran Huong Giang", "email": "giang@example.com"},
]

REVIEWS = [
    {"customer_email": "nguyenvanan@example.com", "product_name": "The Midnight Library", "rating": 5, "comment": "Sách tuyệt vời, rất đáng suy ngẫm về các lựa chọn trong cuộc đời."},
    {"customer_email": "nguyenvanan@example.com", "product_name": "Atomic Habits", "rating": 5, "comment": "Nội dung thực tế, hữu ích để thay đổi thói quen."},
    {"customer_email": "tranminhchau@example.com", "product_name": "Project Hail Mary", "rating": 4, "comment": "Một chuyến phiêu lưu không gian thú vị."},
    {"customer_email": "lehoangduc@example.com", "product_name": "Dune", "rating": 5, "comment": "Tuyệt tác Sci-Fi không thể bỏ qua."},
    {"customer_email": "mai@example.com", "product_name": "Clean Code", "rating": 5, "comment": "Sách gối đầu giường cho mọi lập trình viên."},
    {"customer_email": "mai@example.com", "product_name": "The Pragmatic Programmer", "rating": 5, "comment": "Kiến thức vô giá cho sự nghiệp IT."},
    {"customer_email": "kiet@example.com", "product_name": "Fluent Python", "rating": 4, "comment": "Sách hay cho ai muốn hiểu sâu về Python."},
    {"customer_email": "giang@example.com", "product_name": "1984", "rating": 5, "comment": "Một tác phẩm kinh điển đáng sợ lại rất thực tế."},
]

ORDERS = [
    {
        "customer_email": "nguyenvanan@example.com",
        "address": "123 Nguyen Hue, Quan 1, TP.HCM",
        "total": 79.50, "method": "credit_card",
        "items": [
            {"product_name": "Fluent Python", "qty": 1, "price": 45.00},
            {"product_name": "Clean Code", "qty": 1, "price": 34.50},
        ]
    },
    {
        "customer_email": "tranminhchau@example.com",
        "address": "45 Le Loi, Hai Chau, Da Nang",
        "total": 22.50, "method": "e_wallet",
        "items": [
            {"product_name": "Project Hail Mary", "qty": 1, "price": 22.50},
        ]
    },
]

def execute_query(db_key, query, params=(), fetch_one=False, fetch_all=False):
    conn_string = DATABASES.get(db_key)
    if not conn_string:
        return None
    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        cur.execute(query, params)

        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        else:
            if query.strip().upper().startswith('INSERT') and 'RETURNING' in query.upper():
                result = cur.fetchone()
                result = result[0] if result else None
            else:
                result = None

        conn.commit()
        conn.close()
        return result[0] if fetch_one and result else result
    except Exception as e:
        print(f"  [ERROR] DB({db_key}): {e}")
        if 'conn' in locals():
            conn.close()
        return None

def get_product_id_map():
    """Fetch all products from API and build name->id map"""
    print("\n[1] Fetching products from API...")
    name_to_id = {}

    try:
        # Get all products (paginate if needed)
        page = 1
        while True:
            resp = requests.get(
                PRODUCT_SERVICE_URL,
                params={'page': page},
                timeout=30  # Increase timeout
            )
            resp.raise_for_status()
            data = resp.json()

            # Handle both list and paginated response
            if isinstance(data, list):
                products = data
                has_next = False
            else:
                products = data.get('results', data.get('products', []))
                has_next = data.get('next') is not None

            for product in products:
                if 'name' in product and 'id' in product:
                    name_to_id[product['name']] = product['id']

            if not has_next:
                break
            page += 1

        print(f"  [OK] Found {len(name_to_id)} products")
        return name_to_id

    except Exception as e:
        print(f"  [ERROR] Failed to fetch products: {e}")
        return {}

def seed_reviews(product_id_map):
    """Seed reviews"""
    print("\n[2] Seeding reviews...")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0

    for r in REVIEWS:
        cust_id = execute_query('customers',
            "SELECT id FROM app_customer WHERE email=%s",
            (r['customer_email'],), fetch_one=True)
        product_id = product_id_map.get(r['product_name'])

        if not product_id:
            print(f"  [SKIP] Review: '{r['product_name']}' not found")
            continue

        if cust_id:
            exists = execute_query('reviews',
                "SELECT id FROM app_review WHERE customer_id=%s AND product_id=%s",
                (cust_id, product_id), fetch_one=True)

            if not exists:
                execute_query('reviews',
                    "INSERT INTO app_review (customer_id, product_id, product_type, rating, comment, created_at, updated_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (cust_id, product_id, 'book', r['rating'], r['comment'], now, now))
                count += 1
                print(f"  [OK] Review: {r['customer_email']} -> {r['product_name']}")

    print(f"  Done: +{count} reviews")

def seed_orders(product_id_map):
    """Seed orders"""
    print("\n[3] Seeding orders...")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order_count = item_count = pay_count = ship_count = 0

    for o in ORDERS:
        cust_id = execute_query('customers',
            "SELECT id FROM app_customer WHERE email=%s",
            (o['customer_email'],), fetch_one=True)

        if not cust_id:
            print(f"  [SKIP] Order: customer {o['customer_email']} not found")
            continue

        order_id = execute_query('orders',
            "SELECT id FROM app_order WHERE customer_id=%s AND shipping_address=%s",
            (cust_id, o['address']), fetch_one=True)

        if not order_id:
            order_id = execute_query('orders',
                "INSERT INTO app_order (customer_id, status, total_amount, shipping_address, created_at, updated_at) "
                "VALUES (%s, 'pending', %s, %s, %s, %s) RETURNING id",
                (cust_id, o['total'], o['address'], now, now))
            order_count += 1
            print(f"  [OK] Order: {o['customer_email']} -> {o['address']}")

        if order_id:
            for item in o['items']:
                product_id = product_id_map.get(item['product_name'])
                if not product_id:
                    print(f"  [SKIP] Order item: '{item['product_name']}' not found")
                    continue

                exists = execute_query('orders',
                    "SELECT id FROM app_orderitem WHERE order_id=%s AND product_id=%s",
                    (order_id, product_id), fetch_one=True)

                if not exists:
                    execute_query('orders',
                        "INSERT INTO app_orderitem (product_id, product_name, product_type, quantity, unit_price, order_id) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (product_id, item['product_name'], 'book', item['qty'], item['price'], order_id))
                    item_count += 1

            exists = execute_query('payments', "SELECT id FROM app_payment WHERE order_id=%s", (order_id,), fetch_one=True)
            if not exists:
                execute_query('payments',
                    "INSERT INTO app_payment (order_id, customer_id, amount, method, status, created_at, updated_at) "
                    "VALUES (%s, %s, %s, %s, 'pending', %s, %s)",
                    (order_id, cust_id, o['total'], o['method'], now, now))
                pay_count += 1

            exists = execute_query('shipments', "SELECT id FROM app_shipment WHERE order_id=%s", (order_id,), fetch_one=True)
            if not exists:
                execute_query('shipments',
                    "INSERT INTO app_shipment (order_id, customer_id, address, tracking_number, status, created_at, updated_at) "
                    "VALUES (%s, %s, %s, %s, 'processing', %s, %s)",
                    (order_id, cust_id, o['address'], f"TRK-{order_id}", now, now))
                ship_count += 1

    print(f"  Done: +{order_count} orders, +{item_count} items, +{pay_count} payments, +{ship_count} shipments")

def main():
    print("=" * 60)
    print("FIX REVIEWS & ORDERS")
    print("=" * 60)
    print(f"API URL: {PRODUCT_SERVICE_URL}")

    product_id_map = get_product_id_map()

    if not product_id_map:
        print("\n[ERROR] No products found, cannot seed reviews/orders")
        sys.exit(1)

    seed_reviews(product_id_map)
    seed_orders(product_id_map)

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[WARNING] Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
