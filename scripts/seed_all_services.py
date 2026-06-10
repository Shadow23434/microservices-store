#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed script for all microservices.

Covers two mechanisms:
  1. Direct PostgreSQL — categories, books, customers, carts, staff,
                         managers, reviews, orders, payments, shipments
  2. HTTP API          — non-book sample products (laptops, mobiles, clothing)
                         to product-service, then full book migration from
                         book-service → product-service

Usage:
    python seed_all_services.py
"""

import os
import sys
import time
import requests
import psycopg2
from datetime import datetime

# ── PostgreSQL config ──────────────────────────────────────────────────────────
POSTGRES_USER     = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST     = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT     = os.getenv('POSTGRES_PORT', '5432')

# ── HTTP Service URLs ──────────────────────────────────────────────────────────
BOOK_SERVICE_URL    = "http://localhost:8888/api/books/"
PRODUCT_SERVICE_URL = "http://localhost:8888/api/products/"

# ── DB connection strings ──────────────────────────────────────────────────────
def get_db_url(db_name):
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{db_name}"

DATABASES = {
    'books':      get_db_url('book_db'),
    'categories': get_db_url('catalog_db'),
    'customers':  get_db_url('customer_db'),
    'carts':      get_db_url('cart_db'),
    'staff':      get_db_url('staff_db'),
    'managers':   get_db_url('manager_db'),
    'reviews':    get_db_url('comment_rate_db'),
    'orders':     get_db_url('order_db'),
    'payments':   get_db_url('pay_db'),
    'shipments':  get_db_url('ship_db'),
}

# ── Sample data ────────────────────────────────────────────────────────────────
CATEGORIES = [
    {"name": "Fiction",      "desc": "Fiction books"},
    {"name": "Self-Help",    "desc": "Self-help and self-improvement books"},
    {"name": "Sci-Fi",       "desc": "Science fiction"},
    {"name": "Mystery",      "desc": "Mystery and thriller books"},
    {"name": "Non-Fiction",  "desc": "Non-fiction books"},
    {"name": "Biography",    "desc": "Biographies and autobiographies"},
    {"name": "Technology",   "desc": "Technology and computer science"},
    {"name": "Business",     "desc": "Business, finance and investing"},
    {"name": "Fantasy",      "desc": "Fantasy world books"},
]

BOOKS = [
    {"title": "The Midnight Library",                    "author": "Matt Haig",         "price": 24.99, "stock": 15, "image": "https://picsum.photos/seed/book1/300/450",  "category": "Fiction",      "format": "Hardcover", "pages": 304, "language": "English", "publisher": "Viking",                   "pub_date": "Sept 29, 2020", "isbn": "978-0525559474", "desc": "Between life and death there is a library..."},
    {"title": "Atomic Habits",                           "author": "James Clear",        "price": 19.99, "stock": 42, "image": "https://picsum.photos/seed/book2/300/450",  "category": "Self-Help",    "format": "Paperback", "pages": 320, "language": "English", "publisher": "Avery",                    "pub_date": "Oct 16, 2018",  "isbn": "978-0735211292", "desc": "No matter your goals, Atomic Habits offers a proven framework..."},
    {"title": "Project Hail Mary",                       "author": "Andy Weir",          "price": 22.50, "stock":  8, "image": "https://picsum.photos/seed/book3/300/450",  "category": "Sci-Fi",       "format": "Hardcover", "pages": 496, "language": "English", "publisher": "Ballantine Books",          "pub_date": "May 4, 2021",   "isbn": "978-0593135204", "desc": "Ryland Grace is the sole survivor..."},
    {"title": "Dune",                                    "author": "Frank Herbert",      "price": 21.00, "stock": 25, "image": "https://picsum.photos/seed/book4/300/450",  "category": "Sci-Fi",       "format": "Paperback", "pages": 896, "language": "English", "publisher": "Ace Books",                "pub_date": "Oct 1, 1990",   "isbn": "978-0441172719", "desc": "Set on the desert planet Arrakis..."},
    {"title": "The Silent Patient",                      "author": "Alex Michaelides",   "price": 18.50, "stock": 12, "image": "https://picsum.photos/seed/book5/300/450",  "category": "Mystery",      "format": "Paperback", "pages": 336, "language": "English", "publisher": "Celadon Books",             "pub_date": "Feb 5, 2019",   "isbn": "978-1250301697", "desc": "Alicia Berenson's life is seemingly perfect..."},
    {"title": "Sapiens: A Brief History of Humankind",   "author": "Yuval Noah Harari",  "price": 25.00, "stock": 30, "image": "https://picsum.photos/seed/book6/300/450",  "category": "Non-Fiction",  "format": "Paperback", "pages": 464, "language": "English", "publisher": "Harper",                   "pub_date": "Feb 10, 2015",  "isbn": "978-0062316097", "desc": "From a renowned historian..."},
    {"title": "Thinking, Fast and Slow",                 "author": "Daniel Kahneman",    "price": 20.00, "stock": 18, "image": "https://picsum.photos/seed/book7/300/450",  "category": "Non-Fiction",  "format": "Paperback", "pages": 499, "language": "English", "publisher": "Farrar, Straus and Giroux","pub_date": "Apr 2, 2013",   "isbn": "978-0374533557", "desc": "The phenomenal New York Times Bestseller..."},
    {"title": "1984",                                    "author": "George Orwell",      "price": 15.99, "stock": 50, "image": "https://picsum.photos/seed/book8/300/450",  "category": "Fiction",      "format": "Paperback", "pages": 328, "language": "English", "publisher": "Signet Classic",           "pub_date": "Jan 1, 1950",   "isbn": "978-0451524935", "desc": "Among the seminal texts of the 20th century..."},
    {"title": "The Alchemist",                           "author": "Paulo Coelho",       "price": 16.99, "stock": 35, "image": "https://picsum.photos/seed/book9/300/450",  "category": "Fiction",      "format": "Paperback", "pages": 208, "language": "English", "publisher": "HarperOne",                "pub_date": "Apr 15, 2014",  "isbn": "978-0062315007", "desc": "Paulo Coelho's enchanting novel..."},
    {"title": "Becoming",                                "author": "Michelle Obama",     "price": 22.00, "stock": 22, "image": "https://picsum.photos/seed/book10/300/450", "category": "Biography",    "format": "Hardcover", "pages": 448, "language": "English", "publisher": "Crown",                    "pub_date": "Nov 13, 2018",  "isbn": "978-1524763138", "desc": "In a life filled with meaning and accomplishment..."},
    {"title": "The Psychology of Money",                 "author": "Morgan Housel",      "price": 18.99, "stock": 40, "image": "https://picsum.photos/seed/book11/300/450", "category": "Self-Help",    "format": "Paperback", "pages": 252, "language": "English", "publisher": "Harriman House",           "pub_date": "Sep 8, 2020",   "isbn": "978-0857197689", "desc": "Doing well with money isn't necessarily about what you know..."},
    {"title": "Educated",                                "author": "Tara Westover",      "price": 17.99, "stock": 14, "image": "https://picsum.photos/seed/book12/300/450", "category": "Biography",    "format": "Paperback", "pages": 352, "language": "English", "publisher": "Random House",             "pub_date": "Feb 20, 2018",  "isbn": "978-0399590504", "desc": "An unforgettable memoir about a young girl..."},
    {"title": "Clean Code",                              "author": "Robert C. Martin",   "price": 34.50, "stock": 25, "image": "https://picsum.photos/seed/book13/300/450", "category": "Technology",   "format": "Paperback", "pages": 464, "language": "English", "publisher": "Prentice Hall",            "pub_date": "Aug 1, 2008",   "isbn": "978-0132350884", "desc": "Even bad code can function..."},
    {"title": "The Pragmatic Programmer",                "author": "David Thomas",       "price": 39.99, "stock": 15, "image": "https://picsum.photos/seed/book14/300/450", "category": "Technology",   "format": "Hardcover", "pages": 352, "language": "English", "publisher": "Addison-Wesley",           "pub_date": "Sep 13, 2019",  "isbn": "978-0135957059", "desc": "The Pragmatic Programmer is one of those rare tech books..."},
    {"title": "Fluent Python",                           "author": "Luciano Ramalho",    "price": 45.00, "stock": 12, "image": "https://picsum.photos/seed/book15/300/450", "category": "Technology",   "format": "Paperback", "pages": 984, "language": "English", "publisher": "O'Reilly Media",           "pub_date": "May 20, 2022",  "isbn": "978-1492056355", "desc": "Python's simplicity lets you become productive quickly..."},
    {"title": "Designing Data-Intensive Applications",   "author": "Martin Kleppmann",   "price": 42.50, "stock": 20, "image": "https://picsum.photos/seed/book16/300/450", "category": "Technology",   "format": "Paperback", "pages": 616, "language": "English", "publisher": "O'Reilly Media",           "pub_date": "Mar 16, 2017",  "isbn": "978-1449373320", "desc": "Data is at the center of many challenges..."},
]

CUSTOMERS = [
    {"name": "Nguyen Van An",     "email": "nguyenvanan@example.com"},
    {"name": "Tran Minh Chau",    "email": "tranminhchau@example.com"},
    {"name": "Le Hoang Duc",      "email": "lehoangduc@example.com"},
    {"name": "Le Thi Mai",        "email": "mai@example.com"},
    {"name": "Nguyen Tuan Kiet",  "email": "kiet@example.com"},
    {"name": "Tran Huong Giang",  "email": "giang@example.com"},
]

STAFF = [
    {"name": "Pham Thi Kho",    "email": "warehouse.team@example.com", "role": "warehouse", "emp_id": "STF001"},
    {"name": "Vu Bao Sales",    "email": "sales.team@example.com",     "role": "sales",      "emp_id": "STF002"},
    {"name": "Do Support",      "email": "support.team@example.com",   "role": "support",    "emp_id": "STF003"},
    {"name": "Vuong Security",  "email": "security.team@example.com",  "role": "security",   "emp_id": "STF004"},
]

MANAGERS = [
    {"name": "Nguyen Operations", "email": "operations.manager@example.com", "dept": "operations", "emp_id": "MGR001"},
    {"name": "Tran Inventory",    "email": "inventory.manager@example.com",  "dept": "inventory",  "emp_id": "MGR002"},
    {"name": "Le Finance",        "email": "finance.manager@example.com",    "dept": "finance",    "emp_id": "MGR003"},
    {"name": "Truong IT",         "email": "it.manager@example.com",         "dept": "it",         "emp_id": "MGR004"},
]

REVIEWS = [
    {"customer_email": "nguyenvanan@example.com",  "book_title": "The Midnight Library",   "rating": 5, "comment": "Sách tuyệt vời, rất đáng suy ngẫm về các lựa chọn trong cuộc đời."},
    {"customer_email": "nguyenvanan@example.com",  "book_title": "Atomic Habits",          "rating": 5, "comment": "Nội dung thực tế, hữu ích để thay đổi thói quen."},
    {"customer_email": "tranminhchau@example.com", "book_title": "Project Hail Mary",      "rating": 4, "comment": "Một chuyến phiêu lưu không gian thú vị."},
    {"customer_email": "lehoangduc@example.com",   "book_title": "Dune",                   "rating": 5, "comment": "Tuyệt tác Sci-Fi không thể bỏ qua."},
    {"customer_email": "mai@example.com",          "book_title": "Clean Code",             "rating": 5, "comment": "Sách gối đầu giường cho mọi lập trình viên."},
    {"customer_email": "mai@example.com",          "book_title": "The Pragmatic Programmer","rating": 5, "comment": "Kiến thức vô giá cho sự nghiệp IT."},
    {"customer_email": "kiet@example.com",         "book_title": "Fluent Python",          "rating": 4, "comment": "Sách hay cho ai muốn hiểu sâu về Python."},
    {"customer_email": "giang@example.com",        "book_title": "1984",                   "rating": 5, "comment": "Một tác phẩm kinh điển đáng sợ lại rất thực tế."},
]

ORDERS = [
    {
        "customer_email": "nguyenvanan@example.com",
        "address": "123 Nguyen Hue, Quan 1, TP.HCM",
        "total": 44.98, "method": "credit_card",
        "items": [
            {"book_title": "Fluent Python", "qty": 1, "price": 24.99},
            {"book_title": "Clean Code",    "qty": 1, "price": 19.99},
        ]
    },
    {
        "customer_email": "tranminhchau@example.com",
        "address": "45 Le Loi, Hai Chau, Da Nang",
        "total": 22.50, "method": "paypal",
        "items": [
            {"book_title": "Fluent Python", "qty": 1, "price": 22.50},
        ]
    },
]

# Non-book sample products for product-service.
# Books are intentionally excluded here — they are populated by
# migrate_books_to_products() which reads from book-service after
# the PostgreSQL seed, avoiding duplicates in product-service.
SAMPLE_PRODUCTS = [
    {
        "name": "MacBook Air M3",
        "product_type": "laptop",
        "price": "32990000",
        "stock": 10,
        "description": "Apple M3 chip, 15.3-inch Liquid Retina display",
        "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbair15-m3-midnight-select-202402?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1708367688034",
        "sku": "LAPTOP-001",
        "detail": {
            "brand": "Apple",
            "cpu": "Apple M3",
            "ram_gb": 16,
            "storage_gb": 512,
            "display_inch": 15.3,
            "os": "macOS Sequoia",
        },
    },
    {
        "name": "Dell XPS 15",
        "product_type": "laptop",
        "price": "28500000",
        "stock": 8,
        "description": "Intel Core i7, NVIDIA GeForce RTX 4050",
        "image_url": "https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/notebooks/xps-notebooks/xps-15-9530/media-gallery/black/notebook-xps-15-9530-t-black-gallery-1.psd?fmt=pjpg&pscan=auto&scl=1&wid=1200&hei=900&qlt=100,1&resMode=sharp2&size=1200,900",
        "sku": "LAPTOP-002",
        "detail": {
            "brand": "Dell",
            "cpu": "Intel Core i7-13700H",
            "ram_gb": 16,
            "storage_gb": 1000,
            "display_inch": 15.6,
            "os": "Windows 11",
            "gpu": "NVIDIA GeForce RTX 4050",
        },
    },
    {
        "name": "iPhone 16 Pro",
        "product_type": "mobile",
        "price": "29990000",
        "stock": 20,
        "description": "A18 Pro chip, 6.3-inch Super Retina XDR display",
        "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-16-pro-finish-select-202409-6-3inch_GEO_US?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1725297999059",
        "sku": "MOBILE-001",
        "detail": {
            "brand": "Apple",
            "screen_inch": 6.3,
            "battery_mah": 3500,
            "ram_gb": 8,
            "storage_gb": 256,
            "camera_mp": 48,
            "os": "iOS 18",
        },
    },
    {
        "name": "Premium Cotton Polo Shirt",
        "product_type": "cloth",
        "price": "450000",
        "stock": 100,
        "description": "Classic fit polo shirt, 100% cotton",
        "image_url": "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=800&auto=format&fit=crop",
        "sku": "CLOTH-001",
        "detail": {
            "brand": "Premium Basics",
            "sizes": "S,M,L,XL,XXL",
            "color": "Navy Blue",
            "material": "100% Cotton",
            "gender": "unisex",
        },
    },
]

# ── Helpers ────────────────────────────────────────────────────────────────────
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


def column_exists(db_key, table_name, column_name):
    result = execute_query(
        db_key,
        "SELECT column_name FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
        (table_name, column_name),
        fetch_one=True,
    )
    return result is not None


# ── Step 9: Seed non-book products via HTTP ────────────────────────────────────
def seed_products_via_api():
    """Seed non-book sample products (laptops, mobiles, clothing) to product-service."""
    print("\n[9] Seeding sample products via product-service API...")
    success, failed = 0, 0

    for product in SAMPLE_PRODUCTS:
        try:
            resp = requests.post(
                PRODUCT_SERVICE_URL,
                json=product,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            resp.raise_for_status()
            print(f"  [OK] {product['name']} ({product['product_type']})")
            success += 1
        except requests.exceptions.RequestException as e:
            print(f"  [FAIL] {product['name']} — {e}")
            failed += 1

    print(f"  Done: {success} created / {failed} failed")
    return success


# ── Step 10: Migrate books from book-service → product-service via HTTP ────────
def migrate_books_to_products():
    """
    Fetch all books from book-service (paginated) and re-create them in
    product-service as products with product_type='book'.
    Must run after the PostgreSQL book seed so book-service has data.
    """
    print("\n[10] Migrating books (book-service → product-service)...")
    page, total_migrated, total_failed = 1, 0, 0

    while True:
        # Fetch one page of books
        try:
            resp = requests.get(BOOK_SERVICE_URL, params={"page": page}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Fetching books page {page}: {e}")
            break

        books     = data.get("results", []) if isinstance(data, dict) else data
        next_page = data.get("next")        if isinstance(data, dict) else None

        if not books:
            print("  No more books to migrate.")
            break

        # Push each book to product-service
        for book in books:
            product_payload = {
                "name":         book.get("title", "Untitled"),
                "product_type": "book",
                "price":        book.get("price", "0"),
                "stock":        book.get("stock", 0),
                "description":  book.get("description", ""),
                "category_id":  None,
                "image_url":    book.get("image", ""),
                "sku":          book.get("isbn", f"BOOK-{book.get('id', '')}"),
                "detail": {
                    "author":    book.get("author", ""),
                    "isbn":      book.get("isbn", ""),
                    "publisher": book.get("publisher", ""),
                    "pages":     book.get("pages"),
                    "language":  book.get("language", "vi"),
                },
            }
            try:
                cr = requests.post(
                    PRODUCT_SERVICE_URL,
                    json=product_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )
                cr.raise_for_status()
                print(f"  [OK] {book.get('title', 'Unknown')} (id={book.get('id')})")
                total_migrated += 1
                time.sleep(0.1)  # gentle rate-limiting
            except requests.exceptions.RequestException as e:
                print(f"  [FAIL] {book.get('title', 'Unknown')} — {e}")
                total_failed += 1

        if not next_page:
            break
        page += 1

    print(f"  Done: {total_migrated} migrated / {total_failed} failed")
    return total_migrated


# ── Main ───────────────────────────────────────────────────────────────────────
def seed_all():
    print("=" * 60)
    print("Starting full seed across all microservices")
    print("=" * 60)
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stats = {}

    # ── 1. CATEGORIES ──────────────────────────────────────────────────────────
    count = 0
    for c in CATEGORIES:
        exists = execute_query('categories', "SELECT id FROM app_category WHERE name=%s", (c['name'],), fetch_one=True)
        if not exists:
            execute_query('categories',
                "INSERT INTO app_category (name, description, created_at) VALUES (%s, %s, %s)",
                (c['name'], c['desc'], now))
            count += 1
    stats['categories'] = execute_query('categories', "SELECT COUNT(1) FROM app_category", fetch_one=True) or 0
    print(f"[OK] Categories seeded (+{count})")

    # ── 2. BOOKS ───────────────────────────────────────────────────────────────
    has_image = column_exists('books', 'app_book', 'image')
    count = 0
    for b in BOOKS:
        exists = execute_query('books',
            "SELECT id FROM app_book WHERE title=%s AND author=%s",
            (b['title'], b['author']), fetch_one=True)
        if not exists:
            if has_image:
                execute_query('books',
                    "INSERT INTO app_book "
                    "(title, author, price, stock, image, category, format, pages, language, "
                    " publisher, \"publicationDate\", isbn, description, rating, reviews) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (b['title'], b['author'], b['price'], b['stock'], b['image'],
                     b['category'], b['format'], b['pages'], b['language'],
                     b['publisher'], b['pub_date'], b['isbn'], b['desc'], '5.0', 0))
            else:
                execute_query('books',
                    "INSERT INTO app_book (title, author, price, stock) VALUES (%s,%s,%s,%s)",
                    (b['title'], b['author'], b['price'], b['stock']))
            count += 1
    stats['books'] = execute_query('books', "SELECT COUNT(1) FROM app_book", fetch_one=True) or 0
    print(f"[OK] Books seeded (+{count})")

    # ── 3. CUSTOMERS ───────────────────────────────────────────────────────────
    count = 0
    for c in CUSTOMERS:
        exists = execute_query('customers', "SELECT id FROM app_customer WHERE email=%s", (c['email'],), fetch_one=True)
        if not exists:
            execute_query('customers',
                "INSERT INTO app_customer (name, email) VALUES (%s, %s)",
                (c['name'], c['email']))
            count += 1
    stats['customers'] = execute_query('customers', "SELECT COUNT(1) FROM app_customer", fetch_one=True) or 0
    print(f"[OK] Customers seeded (+{count})")

    # ── 4. CARTS (1 per customer) ──────────────────────────────────────────────
    count = 0
    for c in CUSTOMERS:
        cust_id = execute_query('customers', "SELECT id FROM app_customer WHERE email=%s", (c['email'],), fetch_one=True)
        if cust_id:
            exists = execute_query('carts', "SELECT id FROM app_cart WHERE customer_id=%s", (cust_id,), fetch_one=True)
            if not exists:
                execute_query('carts',
                    "INSERT INTO app_cart (customer_id, created_at) VALUES (%s, %s)",
                    (cust_id, now))
                count += 1
    stats['carts'] = execute_query('carts', "SELECT COUNT(1) FROM app_cart", fetch_one=True) or 0
    print(f"[OK] Carts seeded (+{count})")

    # ── 5. STAFF ───────────────────────────────────────────────────────────────
    count = 0
    for s in STAFF:
        exists = execute_query('staff', "SELECT id FROM app_staff WHERE employee_id=%s", (s['emp_id'],), fetch_one=True)
        if not exists:
            execute_query('staff',
                "INSERT INTO app_staff (name, email, role, employee_id, is_active, created_at) "
                "VALUES (%s, %s, %s, %s, TRUE, %s)",
                (s['name'], s['email'], s['role'], s['emp_id'], now))
            count += 1
    stats['staff'] = execute_query('staff', "SELECT COUNT(1) FROM app_staff", fetch_one=True) or 0
    print(f"[OK] Staff seeded (+{count})")

    # ── 6. MANAGERS ────────────────────────────────────────────────────────────
    count = 0
    for m in MANAGERS:
        exists = execute_query('managers', "SELECT id FROM app_manager WHERE employee_id=%s", (m['emp_id'],), fetch_one=True)
        if not exists:
            execute_query('managers',
                "INSERT INTO app_manager (name, email, department, employee_id, is_active, created_at) "
                "VALUES (%s, %s, %s, %s, TRUE, %s)",
                (m['name'], m['email'], m['dept'], m['emp_id'], now))
            count += 1
    stats['managers'] = execute_query('managers', "SELECT COUNT(1) FROM app_manager", fetch_one=True) or 0
    print(f"[OK] Managers seeded (+{count})")

    # ── 7. REVIEWS ─────────────────────────────────────────────────────────────
    count = 0
    for r in REVIEWS:
        cust_id = execute_query('customers', "SELECT id FROM app_customer WHERE email=%s",    (r['customer_email'],), fetch_one=True)
        book_id = execute_query('books',     "SELECT id FROM app_book WHERE title=%s",        (r['book_title'],),     fetch_one=True)
        if cust_id and book_id:
            exists = execute_query('reviews',
                "SELECT id FROM app_review WHERE customer_id=%s AND book_id=%s",
                (cust_id, book_id), fetch_one=True)
            if not exists:
                execute_query('reviews',
                    "INSERT INTO app_review (customer_id, book_id, rating, comment, created_at, updated_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (cust_id, book_id, r['rating'], r['comment'], now, now))
                count += 1
    stats['reviews'] = execute_query('reviews', "SELECT COUNT(1) FROM app_review", fetch_one=True) or 0
    print(f"[OK] Reviews seeded (+{count})")

    # ── 8. ORDERS / PAYMENTS / SHIPMENTS ──────────────────────────────────────
    order_count = item_count = pay_count = ship_count = 0
    for o in ORDERS:
        cust_id = execute_query('customers', "SELECT id FROM app_customer WHERE email=%s", (o['customer_email'],), fetch_one=True)
        if not cust_id:
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

        if order_id:
            for item in o['items']:
                book_id = execute_query('books', "SELECT id FROM app_book WHERE title=%s", (item['book_title'],), fetch_one=True)
                if book_id:
                    exists = execute_query('orders',
                        "SELECT id FROM app_orderitem WHERE order_id=%s AND book_id=%s",
                        (order_id, book_id), fetch_one=True)
                    if not exists:
                        execute_query('orders',
                            "INSERT INTO app_orderitem (book_id, quantity, unit_price, order_id) VALUES (%s, %s, %s, %s)",
                            (book_id, item['qty'], item['price'], order_id))
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
                    "VALUES (%s, %s, %s, %s, 'pending', %s, %s)",
                    (order_id, cust_id, o['address'], f"TRK-{order_id}", now, now))
                ship_count += 1

    stats['orders']      = execute_query('orders',    "SELECT COUNT(1) FROM app_order",     fetch_one=True) or 0
    stats['order_items'] = execute_query('orders',    "SELECT COUNT(1) FROM app_orderitem", fetch_one=True) or 0
    stats['payments']    = execute_query('payments',  "SELECT COUNT(1) FROM app_payment",   fetch_one=True) or 0
    stats['shipments']   = execute_query('shipments', "SELECT COUNT(1) FROM app_shipment",  fetch_one=True) or 0
    print(f"[OK] Orders/Payments/Shipments seeded "
          f"(+{order_count} orders, +{item_count} items, +{pay_count} pays, +{ship_count} ships)")

    # ── 9. PRODUCTS (HTTP) ─────────────────────────────────────────────────────
    stats['products_seeded'] = seed_products_via_api()

    # ── 10. MIGRATE BOOKS → PRODUCTS (HTTP) ───────────────────────────────────
    stats['books_migrated'] = migrate_books_to_products()

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SEED SUMMARY")
    print("=" * 60)
    labels = {
        'categories':      'Categories    (catalog_db)',
        'books':           'Books         (book_db)',
        'customers':       'Customers     (customer_db)',
        'carts':           'Carts         (cart_db)',
        'staff':           'Staff         (staff_db)',
        'managers':        'Managers      (manager_db)',
        'reviews':         'Reviews       (comment_rate_db)',
        'orders':          'Orders        (order_db)',
        'order_items':     'Order Items   (order_db)',
        'payments':        'Payments      (pay_db)',
        'shipments':       'Shipments     (ship_db)',
        'products_seeded': 'Products      (product-service API)',
        'books_migrated':  'Books migrated(product-service API)',
    }
    for key, label in labels.items():
        print(f"  {label}: {stats.get(key, 0)}")
    print("=" * 60)


if __name__ == '__main__':
    try:
        seed_all()
    except KeyboardInterrupt:
        print("\n[WARNING] Seed interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)