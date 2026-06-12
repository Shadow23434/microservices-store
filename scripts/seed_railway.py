#!/usr/bin/env python3
"""
Seed data cho Railway deployment.
Sử dụng: python seed_railway.py --api-url https://your-app.up.railway.app

Cần set environment variable DATABASE_URL trước khi chạy.
"""

import os
import sys
import time
import argparse
import psycopg2
import requests
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlparse
from decimal import Decimal

# Parse DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

parsed = urlparse(DATABASE_URL)
DB_CONFIG = {
    'host': parsed.hostname,
    'port': parsed.port or 5432,
    'user': parsed.username,
    'password': parsed.password,
}


def get_connection(db_name):
    """Get database connection"""
    return psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=db_name
    )


def wait_for_databases():
    """Wait for all databases to be ready with tables"""
    print("Waiting for databases to be ready...")

    checks = [
        ('catalog_db', 'catalog_service_category'),
        ('customer_db', 'customer_service_customer'),
        ('cart_db', 'cart_service_cart'),
        ('staff_db', 'staff_service_staff'),
        ('manager_db', 'manager_service_manager'),
        ('comment_rate_db', 'comment_rate_service_review'),
        ('order_db', 'order_service_order'),
        ('pay_db', 'pay_service_payment'),
        ('ship_db', 'ship_service_shipment'),
    ]

    for db_name, table in checks:
        retries = 0
        while retries < 30:
            try:
                conn = get_connection(db_name)
                cur = conn.cursor()
                cur.execute(f"SELECT 1 FROM {table} LIMIT 1")
                cur.close()
                conn.close()
                print(f"  OK {db_name}.{table}")
                break
            except Exception as e:
                retries += 1
                if retries == 30:
                    print(f"  FAIL {db_name}.{table} - timeout: {e}")
                    return False
                time.sleep(2)

    return True


def seed_categories():
    """Seed categories"""
    print("\nSeeding categories...")
    conn = get_connection('catalog_db')
    cur = conn.cursor()

    categories = [
        ('Fiction', 'Fictional books', 'book'),
        ('Self-Help', 'Self-improvement books', 'book'),
        ('Sci-Fi', 'Science fiction books', 'book'),
        ('Mystery', 'Mystery and thriller books', 'book'),
        ('Non-Fiction', 'Non-fiction books', 'book'),
        ('Biography', 'Biography books', 'book'),
        ('Technology', 'Technology books', 'book,laptop'),
        ('Business', 'Business books', 'book'),
        ('Fantasy', 'Fantasy books', 'book'),
    ]

    for name, description, applicable_types in categories:
        cur.execute(
            """INSERT INTO catalog_service_category
               (name, description, applicable_types, created_at)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT DO NOTHING""",
            (name, description, applicable_types, datetime.now())
        )

    conn.commit()
    print(f"  Created {len(categories)} categories")
    cur.close()
    conn.close()


def seed_customers():
    """Seed customers"""
    print("\nSeeding customers...")
    conn = get_connection('customer_db')
    cur = conn.cursor()

    customers = [
        ('Nguyen Van An', 'an.nguyen@example.com'),
        ('Tran Thi Binh', 'binh.tran@example.com'),
        ('Le Hoang Cuong', 'cuong.le@example.com'),
        ('Pham My Dung', 'dung.pham@example.com'),
        ('Hoang Duc Em', 'em.hoang@example.com'),
        ('Vu Thi Phuong', 'phuong.vu@example.com'),
    ]

    for name, email in customers:
        cur.execute(
            """INSERT INTO customer_service_customer (name, email)
               VALUES (%s, %s)
               ON CONFLICT (email) DO NOTHING""",
            (name, email)
        )

    conn.commit()
    print(f"  Created {len(customers)} customers")
    cur.close()
    conn.close()


def seed_carts():
    """Seed carts - one cart per customer"""
    print("\nSeeding carts...")

    # Get customer IDs from customer_db
    conn_customer = get_connection('customer_db')
    cur_customer = conn_customer.cursor()
    cur_customer.execute("SELECT id FROM customer_service_customer")
    customer_ids = [row[0] for row in cur_customer.fetchall()]
    cur_customer.close()
    conn_customer.close()

    # Create carts in cart_db
    conn_cart = get_connection('cart_db')
    cur_cart = conn_cart.cursor()

    for customer_id in customer_ids:
        cur_cart.execute(
            """INSERT INTO cart_service_cart (customer_id)
               VALUES (%s)
               ON CONFLICT DO NOTHING""",
            (customer_id,)
        )

    conn_cart.commit()
    print(f"  Created {len(customer_ids)} carts")
    cur_cart.close()
    conn_cart.close()


def seed_staff():
    """Seed staff members"""
    print("\nSeeding staff...")
    conn = get_connection('staff_db')
    cur = conn.cursor()

    staff_list = [
        ('Nguyen Van A', 'staff_a@example.com', 'warehouse', 'STAFF001'),
        ('Tran Thi B', 'staff_b@example.com', 'sales', 'STAFF002'),
        ('Le Van C', 'staff_c@example.com', 'support', 'STAFF003'),
        ('Pham Thi D', 'staff_d@example.com', 'warehouse', 'STAFF004'),
    ]

    for name, email, role, employee_id in staff_list:
        cur.execute(
            """INSERT INTO staff_service_staff
               (name, email, role, employee_id, is_active)
               VALUES (%s, %s, %s, %s, true)
               ON CONFLICT (employee_id) DO NOTHING""",
            (name, email, role, employee_id)
        )

    conn.commit()
    print(f"  Created {len(staff_list)} staff members")
    cur.close()
    conn.close()


def seed_managers():
    """Seed managers"""
    print("\nSeeding managers...")
    conn = get_connection('manager_db')
    cur = conn.cursor()

    managers = [
        ('Nguyen Quan Ly A', 'mgr_a@example.com', 'operations', 'MGR001'),
        ('Tran Quan Ly B', 'mgr_b@example.com', 'inventory', 'MGR002'),
        ('Le Quan Ly C', 'mgr_c@example.com', 'finance', 'MGR003'),
        ('Pham Quan Ly D', 'mgr_d@example.com', 'marketing', 'MGR004'),
    ]

    for name, email, department, employee_id in managers:
        cur.execute(
            """INSERT INTO manager_service_manager
               (name, email, department, employee_id, is_active)
               VALUES (%s, %s, %s, %s, true)
               ON CONFLICT (employee_id) DO NOTHING""",
            (name, email, department, employee_id)
        )

    conn.commit()
    print(f"  Created {len(managers)} managers")
    cur.close()
    conn.close()


def seed_products(api_url):
    """Seed products via API - supports book, laptop, mobile, cloth types"""
    print("\nSeeding products via API...")

    products = [
        # Books
        {
            'name': 'Dac Nhan Tam',
            'price': '120000',
            'description': 'Sach self-help noi tieng',
            'product_type': 'book',
            'stock': 50,
            'category_id': 1,
            'book_detail': {
                'author': 'Dale Carnegie',
                'isbn': '978-1234567890',
                'publisher': 'NXB Tre',
                'language': 'vi',
            }
        },
        {
            'name': 'Nha Gia Kim',
            'price': '95000',
            'description': 'Tieu thuyet triet hoc',
            'product_type': 'book',
            'stock': 30,
            'category_id': 1,
            'book_detail': {
                'author': 'Paulo Coelho',
                'isbn': '978-2345678901',
                'publisher': 'NXB Tre',
                'language': 'vi',
            }
        },
        {
            'name': 'Tuoi Tre Dang Gia Bao Nhieu',
            'price': '85000',
            'description': 'Sach self-help cho gioi tre',
            'product_type': 'book',
            'stock': 40,
            'category_id': 2,
            'book_detail': {
                'author': 'Rosie Nguyen',
                'isbn': '978-3456789012',
                'publisher': 'NXB Tre',
                'language': 'vi',
            }
        },
        {
            'name': 'Dune',
            'price': '180000',
            'description': 'Khoa hoc vien tuong',
            'product_type': 'book',
            'stock': 20,
            'category_id': 3,
            'book_detail': {
                'author': 'Frank Herbert',
                'isbn': '978-4567890123',
                'publisher': 'NXB Tre',
                'language': 'en',
            }
        },
        # Laptops
        {
            'name': 'MacBook Pro M2',
            'price': '45000000',
            'description': 'Laptop cao cap Apple',
            'product_type': 'laptop',
            'stock': 10,
            'category_id': 7,
            'laptop_detail': {
                'brand': 'Apple',
                'cpu': 'M2',
                'ram_gb': 16,
                'storage_gb': 512,
                'display_inch': '13.3',
                'os': 'macOS',
                'weight_kg': '1.4',
            }
        },
        {
            'name': 'Dell XPS 15',
            'price': '35000000',
            'description': 'Laptop Windows cao cap',
            'product_type': 'laptop',
            'stock': 15,
            'category_id': 7,
            'laptop_detail': {
                'brand': 'Dell',
                'cpu': 'i7-12700H',
                'ram_gb': 32,
                'storage_gb': 1024,
                'display_inch': '15.6',
                'os': 'Windows 11',
                'weight_kg': '1.9',
            }
        },
        # Mobiles
        {
            'name': 'iPhone 15 Pro',
            'price': '28000000',
            'description': 'Flagship Apple',
            'product_type': 'mobile',
            'stock': 20,
            'mobile_detail': {
                'brand': 'Apple',
                'screen_inch': '6.1',
                'battery_mah': 3274,
                'ram_gb': 8,
                'storage_gb': 256,
                'camera_mp': 48,
                'os': 'iOS 17',
            }
        },
        {
            'name': 'Samsung Galaxy S24',
            'price': '22000000',
            'description': 'Flagship Samsung',
            'product_type': 'mobile',
            'stock': 25,
            'mobile_detail': {
                'brand': 'Samsung',
                'screen_inch': '6.2',
                'battery_mah': 4000,
                'ram_gb': 8,
                'storage_gb': 128,
                'camera_mp': 50,
                'os': 'Android 14',
            }
        },
        # Clothing
        {
            'name': 'Ao thun nam',
            'price': '250000',
            'description': 'Ao thun cotton',
            'product_type': 'cloth',
            'stock': 100,
            'cloth_detail': {
                'brand': 'Local Brand',
                'sizes': 'S,M,L,XL',
                'color': 'White',
                'material': 'Cotton',
                'gender': 'male',
            }
        },
        {
            'name': 'Quan jean nu',
            'price': '450000',
            'description': 'Quan jean thoi trang',
            'product_type': 'cloth',
            'stock': 80,
            'cloth_detail': {
                'brand': 'Local Brand',
                'sizes': 'XS,S,M,L',
                'color': 'Blue',
                'material': 'Denim',
                'gender': 'female',
            }
        },
    ]

    created = 0
    failed = 0
    for product in products:
        try:
            response = requests.post(
                f"{api_url}/api/products/",
                json=product,
                timeout=10
            )
            if response.status_code in [200, 201]:
                created += 1
                print(f"  OK {product['name']}")
            else:
                failed += 1
                print(f"  FAIL {product['name']} - HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            failed += 1
            print(f"  FAIL {product['name']} - {e}")

    print(f"  Created {created}/{len(products)} products ({failed} failed)")


def seed_reviews():
    """Seed reviews"""
    print("\nSeeding reviews...")

    # Get customer IDs
    conn_customer = get_connection('customer_db')
    cur_customer = conn_customer.cursor()
    cur_customer.execute("SELECT id FROM customer_service_customer")
    customer_ids = [row[0] for row in cur_customer.fetchall()]
    cur_customer.close()
    conn_customer.close()

    if not customer_ids:
        print("  No customers found, skipping reviews")
        return

    conn = get_connection('comment_rate_db')
    cur = conn.cursor()

    reviews = [
        (customer_ids[0] if len(customer_ids) > 0 else 1, 1, 'book', 5, 'Sach rat hay!'),
        (customer_ids[1] if len(customer_ids) > 1 else 2, 2, 'book', 4, 'Dang doc'),
        (customer_ids[2] if len(customer_ids) > 2 else 3, 3, 'book', 5, 'Rat huu ich'),
        (customer_ids[3] if len(customer_ids) > 3 else 4, 1, 'book', 4, 'Noi dung tot'),
        (customer_ids[0] if len(customer_ids) > 0 else 1, 5, 'laptop', 5, 'Laptop tuyet voi'),
        (customer_ids[1] if len(customer_ids) > 1 else 2, 6, 'laptop', 4, 'Hieu nang cao'),
        (customer_ids[2] if len(customer_ids) > 2 else 3, 7, 'mobile', 5, 'Dien thoai dep'),
        (customer_ids[3] if len(customer_ids) > 3 else 4, 8, 'mobile', 4, 'Camera tot'),
    ]

    for customer_id, product_id, product_type, rating, comment in reviews:
        cur.execute(
            """INSERT INTO comment_rate_service_review
               (customer_id, product_id, product_type, rating, comment)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (customer_id, product_id) DO NOTHING""",
            (customer_id, product_id, product_type, rating, comment)
        )

    conn.commit()
    print(f"  Created {len(reviews)} reviews")
    cur.close()
    conn.close()


def seed_orders():
    """Seed orders with order items, payments, and shipments"""
    print("\nSeeding orders...")

    # Get customer IDs
    conn_customer = get_connection('customer_db')
    cur_customer = conn_customer.cursor()
    cur_customer.execute("SELECT id FROM customer_service_customer")
    customer_ids = [row[0] for row in cur_customer.fetchall()]
    cur_customer.close()
    conn_customer.close()

    if len(customer_ids) < 2:
        print("  Not enough customers, skipping orders")
        return

    # Create orders in order_db
    conn_order = get_connection('order_db')
    cur_order = conn_order.cursor()

    orders_data = [
        {
            'customer_id': customer_ids[0],
            'status': 'completed',
            'total_amount': Decimal('240000.00'),
            'shipping_address': '123 Nguyen Hue, Q1, HCM',
            'items': [
                {'product_id': 1, 'product_name': 'Dac Nhan Tam', 'product_type': 'book', 'quantity': 2, 'unit_price': Decimal('120000.00')},
            ]
        },
        {
            'customer_id': customer_ids[1] if len(customer_ids) > 1 else customer_ids[0],
            'status': 'pending',
            'total_amount': Decimal('45250000.00'),
            'shipping_address': '456 Le Loi, Q1, HCM',
            'items': [
                {'product_id': 5, 'product_name': 'MacBook Pro M2', 'product_type': 'laptop', 'quantity': 1, 'unit_price': Decimal('45000000.00')},
                {'product_id': 9, 'product_name': 'Ao thun nam', 'product_type': 'cloth', 'quantity': 1, 'unit_price': Decimal('250000.00')},
            ]
        },
    ]

    created_orders = 0
    for order_data in orders_data:
        # Insert order
        cur_order.execute(
            """INSERT INTO order_service_order
               (customer_id, status, total_amount, shipping_address)
               VALUES (%s, %s, %s, %s)
               RETURNING id""",
            (order_data['customer_id'], order_data['status'],
             order_data['total_amount'], order_data['shipping_address'])
        )
        order_id = cur_order.fetchone()[0]
        created_orders += 1

        # Insert order items
        for item in order_data['items']:
            cur_order.execute(
                """INSERT INTO order_service_orderitem
                   (order_id, product_id, product_name, product_type, quantity, unit_price)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (order_id, item['product_id'], item['product_name'],
                 item['product_type'], item['quantity'], item['unit_price'])
            )

        # Insert payment in pay_db
        conn_pay = get_connection('pay_db')
        cur_pay = conn_pay.cursor()
        cur_pay.execute(
            """INSERT INTO pay_service_payment
               (order_id, customer_id, amount, method, status)
               VALUES (%s, %s, %s, %s, %s)""",
            (order_id, order_data['customer_id'], order_data['total_amount'],
             'credit_card', 'completed' if order_data['status'] == 'completed' else 'pending')
        )
        conn_pay.commit()
        cur_pay.close()
        conn_pay.close()

        # Insert shipment in ship_db
        conn_ship = get_connection('ship_db')
        cur_ship = conn_ship.cursor()
        cur_ship.execute(
            """INSERT INTO ship_service_shipment
               (order_id, customer_id, address, tracking_number, status)
               VALUES (%s, %s, %s, %s, %s)""",
            (order_id, order_data['customer_id'], order_data['shipping_address'],
             str(uuid.uuid4()),
             'delivered' if order_data['status'] == 'completed' else 'processing')
        )
        conn_ship.commit()
        cur_ship.close()
        conn_ship.close()

    conn_order.commit()
    print(f"  Created {created_orders} orders (with items, payments, shipments)")
    cur_order.close()
    conn_order.close()


def main():
    parser = argparse.ArgumentParser(description='Seed data for Railway')
    parser.add_argument('--api-url', required=True,
                        help='API Gateway URL (e.g., https://your-app.up.railway.app)')
    args = parser.parse_args()

    print("=" * 60)
    print("RAILWAY SEED SCRIPT")
    print("=" * 60)
    print(f"API URL: {args.api_url}")
    print()

    if not wait_for_databases():
        print("\nERROR: Databases not ready")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("SEEDING DATA")
    print("=" * 60)

    try:
        seed_categories()
        seed_customers()
        seed_carts()
        seed_staff()
        seed_managers()
        seed_products(args.api_url)
        seed_reviews()
        seed_orders()

        print("\n" + "=" * 60)
        print("SEEDING COMPLETE!")
        print("=" * 60)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
