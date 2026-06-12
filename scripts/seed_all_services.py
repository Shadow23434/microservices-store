#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed script for all microservices.

Covers two mechanisms:
  1. Direct PostgreSQL — categories, customers, carts, staff,
                         managers, reviews, orders, payments, shipments
  2. HTTP API          — all products (books, laptops, mobiles, clothing)
                         via product-service

Product catalogue:
  - Books   : 16 titles
  - Laptops : 6 models  (LAPTOP-001 … LAPTOP-006)
  - Mobiles : 5 models  (MOBILE-001 … MOBILE-005)
  - Clothing: 6 items   (CLOTH-001  … CLOTH-006)

Usage:
    python seed_all_services.py
"""

import os
import sys
import requests
import psycopg2
from datetime import datetime
import time

# ── PostgreSQL config ──────────────────────────────────────────────────────────
POSTGRES_USER     = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST     = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT     = os.getenv('POSTGRES_PORT', '5432')

# ── HTTP Service URLs ──────────────────────────────────────────────────────────
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://api-gateway:8888/api/products/')

# ── DB connection strings ──────────────────────────────────────────────────────
def get_db_url(db_name):
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{db_name}"

DATABASES = {
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

# All products seeded via product-service API.
# Books use product_type='book' with ISBN as SKU for deduplication.
PRODUCTS = [
    # ── Books ─────────────────────────────────────────────────────────────────
    {
        "name": "The Midnight Library",
        "product_type": "book",
        "price": "24.99",
        "stock": 15,
        "description": "Between life and death there is a library...",
        "image_url": "https://picsum.photos/seed/book1/300/450",
        "sku": "978-0525559474",
        "detail": {
            "author": "Matt Haig", "isbn": "978-0525559474",
            "publisher": "Viking", "pages": 304, "language": "English"
            }
    },
    {
        "name": "Atomic Habits",
        "product_type": "book",
        "price": "19.99",
        "stock": 42,
        "description": "No matter your goals, Atomic Habits offers a proven framework...",
        "image_url": "https://picsum.photos/seed/book2/300/450",
        "sku": "978-0735211292",
        "detail": {
            "author": "James Clear", "isbn": "978-0735211292",
            "publisher": "Avery", "pages": 320, "language": "English"
            }
    },
    {
        "name": "Project Hail Mary",
        "product_type": "book",
        "price": "22.50",
        "stock": 8,
        "description": "Ryland Grace is the sole survivor...",
        "image_url": "https://picsum.photos/seed/book3/300/450",
        "sku": "978-0593135204",
        "detail": {
            "author": "Andy Weir", "isbn": "978-0593135204",
            "publisher": "Ballantine Books", "pages": 496, "language": "English"
            }
    },
    {
        "name": "Dune",
        "product_type": "book",
        "price": "21.00",
        "stock": 25,
        "description": "Set on the desert planet Arrakis...",
        "image_url": "https://picsum.photos/seed/book4/300/450",
        "sku": "978-0441172719",
        "detail": {
            "author": "Frank Herbert", "isbn": "978-0441172719",
            "publisher": "Ace Books", "pages": 896, "language": "English"
            }
    },
    {
        "name": "The Silent Patient",
        "product_type": "book",
        "price": "18.50",
        "stock": 12,
        "description": "Alicia Berenson's life is seemingly perfect...",
        "image_url": "https://picsum.photos/seed/book5/300/450",
        "sku": "978-1250301697",
        "detail": {
            "author": "Alex Michaelides", "isbn": "978-1250301697",
            "publisher": "Celadon Books", "pages": 336, "language": "English"
            }
    },
    {
        "name": "Sapiens: A Brief History of Humankind",
        "product_type": "book",
        "price": "25.00",
        "stock": 30,
        "description": "From a renowned historian...",
        "image_url": "https://picsum.photos/seed/book6/300/450",
        "sku": "978-0062316097",
        "detail": {
            "author": "Yuval Noah Harari", "isbn": "978-0062316097",
            "publisher": "Harper", "pages": 464, "language": "English"
            }
    },
    {
        "name": "Thinking, Fast and Slow",
        "product_type": "book",
        "price": "20.00",
        "stock": 18,
        "description": "The phenomenal New York Times Bestseller...",
        "image_url": "https://picsum.photos/seed/book7/300/450",
        "sku": "978-0374533557",
        "detail": {
            "author": "Daniel Kahneman", "isbn": "978-0374533557",
            "publisher": "Farrar, Straus and Giroux", "pages": 499, "language": "English"
            }
    },
    {
        "name": "1984",
        "product_type": "book",
        "price": "15.99",
        "stock": 50,
        "description": "Among the seminal texts of the 20th century...",
        "image_url": "https://picsum.photos/seed/book8/300/450",
        "sku": "978-0451524935",
        "detail": {
            "author": "George Orwell", "isbn": "978-0451524935",
            "publisher": "Signet Classic", "pages": 328, "language": "English"
            }
    },
    {
        "name": "The Alchemist",
        "product_type": "book",
        "price": "16.99",
        "stock": 35,
        "description": "Paulo Coelho's enchanting novel...",
        "image_url": "https://picsum.photos/seed/book9/300/450",
        "sku": "978-0062315007",
        "detail": {
            "author": "Paulo Coelho", "isbn": "978-0062315007",
            "publisher": "HarperOne", "pages": 208, "language": "English"
            }
    },
    {
        "name": "Becoming",
        "product_type": "book",
        "price": "22.00",
        "stock": 22,
        "description": "In a life filled with meaning and accomplishment...",
        "image_url": "https://picsum.photos/seed/book10/300/450",
        "sku": "978-1524763138",
        "detail": {
            "author": "Michelle Obama", "isbn": "978-1524763138",
            "publisher": "Crown", "pages": 448, "language": "English"
            }
    },
    {
        "name": "The Psychology of Money",
        "product_type": "book",
        "price": "18.99",
        "stock": 40,
        "description": "Doing well with money isn't necessarily about what you know...",
        "image_url": "https://picsum.photos/seed/book11/300/450",
        "sku": "978-0857197689",
        "detail": {
            "author": "Morgan Housel", "isbn": "978-0857197689",
            "publisher": "Harriman House", "pages": 252, "language": "English"
            }
    },
    {
        "name": "Educated",
        "product_type": "book",
        "price": "17.99",
        "stock": 14,
        "description": "An unforgettable memoir about a young girl...",
        "image_url": "https://picsum.photos/seed/book12/300/450",
        "sku": "978-0399590504",
        "detail": {
            "author": "Tara Westover", "isbn": "978-0399590504",
            "publisher": "Random House", "pages": 352, "language": "English"
            }
    },
    {
        "name": "Clean Code",
        "product_type": "book",
        "price": "34.50",
        "stock": 25,
        "description": "Even bad code can function...",
        "image_url": "https://picsum.photos/seed/book13/300/450",
        "sku": "978-0132350884",
        "detail": {
            "author": "Robert C. Martin", "isbn": "978-0132350884",
            "publisher": "Prentice Hall", "pages": 464, "language": "English"
            }
    },
    {
        "name": "The Pragmatic Programmer",
        "product_type": "book",
        "price": "39.99",
        "stock": 15,
        "description": "The Pragmatic Programmer is one of those rare tech books...",
        "image_url": "https://picsum.photos/seed/book14/300/450",
        "sku": "978-0135957059",
        "detail": {
            "author": "David Thomas", "isbn": "978-0135957059",
            "publisher": "Addison-Wesley", "pages": 352, "language": "English"
            }
    },
    {
        "name": "Fluent Python",
        "product_type": "book",
        "price": "45.00",
        "stock": 12,
        "description": "Python's simplicity lets you become productive quickly...",
        "image_url": "https://picsum.photos/seed/book15/300/450",
        "sku": "978-1492056355",
        "detail": {
            "author": "Luciano Ramalho", "isbn": "978-1492056355",
            "publisher": "O'Reilly Media", "pages": 984, "language": "English"
            }
    },
    {
        "name": "Designing Data-Intensive Applications",
        "product_type": "book",
        "price": "42.50",
        "stock": 20,
        "description": "Data is at the center of many challenges...",
        "image_url": "https://picsum.photos/seed/book16/300/450",
        "sku": "978-1449373320",
        "detail": {
            "author": "Martin Kleppmann", "isbn": "978-1449373320",
            "publisher": "O'Reilly Media", "pages": 616, "language": "English"
            }
    },
    # ── Laptops ───────────────────────────────────────────────────────────────
    {
        "name": "MacBook Air M3",
        "product_type": "laptop",
        "price": "1299.99",
        "stock": 10,
        "description": "Apple M3 chip, 15.3-inch Liquid Retina display",
        "image_url": "https://cdn.tgdd.vn/Products/Images/44/322616/macbook-air-15-inch-m3-2024-1.jpg",
        "sku": "LAPTOP-001",
        "detail": {
            "brand": "Apple", "cpu": "Apple M3", "ram_gb": 16,
            "storage_gb": 512, "display_inch": 15.3, "os": "macOS Sequoia"
        },
    },
    {
        "name": "Dell XPS 15",
        "product_type": "laptop",
        "price": "1149.99",
        "stock": 8,
        "description": "Intel Core i7, NVIDIA GeForce RTX 4050",
        "image_url": "https://cdn.tgdd.vn/Products/Images/44/314837/dell-xps-15-9530-i7-71015716-1.jpg",
        "sku": "LAPTOP-002",
        "detail": {
            "brand": "Dell", "cpu": "Intel Core i7-13700H", "ram_gb": 16,
            "storage_gb": 1000, "display_inch": 15.6, "os": "Windows 11",
            "gpu": "NVIDIA GeForce RTX 4050"
        },
    },
    {
        "name": "Lenovo ThinkPad X1 Carbon Gen 11",
        "product_type": "laptop",
        "price": "1399.99",
        "stock": 6,
        "description": "Ultra-thin business laptop, Intel Core i7, 14-inch IPS display",
        "image_url": "https://cdnv2.tgdd.vn/mwg-static/tgdd/Products/Images/44/332376/lenovo-thinkpad-x1-carbon-ultra-7-21kc00agvn-1-638679579239911068.jpg",
        "sku": "LAPTOP-003",
        "detail": {
            "brand": "Lenovo", "cpu": "Intel Core i7-1365U", "ram_gb": 16,
            "storage_gb": 512, "display_inch": 14.0, "os": "Windows 11 Pro",
            "gpu": "Intel Iris Xe Graphics"
        },
    },
    {
        "name": "ASUS ROG Strix G16",
        "product_type": "laptop",
        "price": "1799.99",
        "stock": 5,
        "description": "AMD Ryzen 9, NVIDIA RTX 4070, 16-inch QHD 240Hz gaming display",
        "image_url": "https://cdn.tgdd.vn/Products/Images/44/305663/asus-gaming-rog-strix-g16-g614ji-i7-n4084w-glr-1-750x500.jpg",
        "sku": "LAPTOP-004",
        "detail": {
            "brand": "ASUS", "cpu": "AMD Ryzen 9 7945HX", "ram_gb": 32,
            "storage_gb": 1000, "display_inch": 16.0, "os": "Windows 11",
            "gpu": "NVIDIA GeForce RTX 4070"
        },
    },
    {
        "name": "HP Spectre x360 14",
        "product_type": "laptop",
        "price": "1519.99",
        "stock": 7,
        "description": "2-in-1 convertible laptop, Intel Core i7, OLED touch display",
        "image_url": "https://cdnv2.tgdd.vn/mwg-static/tgdd/Products/Images/44/326268/hp-spectre-x360-14-eu0050tu-ultra-7-a19blpa-glr-1-638647607976964037.jpg",
        "sku": "LAPTOP-005",
        "detail": {
            "brand": "HP", "cpu": "Intel Core i7-1355U", "ram_gb": 16,
            "storage_gb": 512, "display_inch": 13.5, "os": "Windows 11 Home",
            "gpu": "Intel Iris Xe Graphics"
        },
    },
    {
        "name": "MacBook Pro M3 Max",
        "product_type": "laptop",
        "price": "3159.99",
        "stock": 4,
        "description": "Apple M3 Max chip, 16-inch Liquid Retina XDR display, 48GB RAM",
        "image_url": "https://cdn.tgdd.vn/Products/Images/44/327737/macbook-pro-16-inch-m3-max-64gb-1tb-40gpu-den-1.jpg",
        "sku": "LAPTOP-006",
        "detail": {
            "brand": "Apple", "cpu": "Apple M3 Max", "ram_gb": 48,
            "storage_gb": 1000, "display_inch": 16.2, "os": "macOS Sequoia"
        },
    },
    # ── Mobiles ───────────────────────────────────────────────────────────────
    {
        "name": "iPhone 16 Pro",
        "product_type": "mobile",
        "price": "1199.99",
        "stock": 20,
        "description": "A18 Pro chip, 6.3-inch Super Retina XDR display",
        "image_url": "https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-16-pro-finish-select-202409-6-3inch_GEO_US?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1725297999059",
        "sku": "MOBILE-001",
        "detail": {
            "brand": "Apple", "screen_inch": 6.3, "battery_mah": 3500,
            "ram_gb": 8, "storage_gb": 256, "camera_mp": 48, "os": "iOS 18"
        },
    },
    {
        "name": "Samsung Galaxy S25 Ultra",
        "product_type": "mobile",
        "price": "1359.99",
        "stock": 15,
        "description": "Snapdragon 8 Elite, 6.9-inch Dynamic AMOLED, built-in S Pen",
        "image_url": "https://i.gadgets360cdn.com/products/large/samsung-galaxy-s25-ultra-795x800-1738321292.jpg",
        "sku": "MOBILE-002",
        "detail": {
            "brand": "Samsung", "screen_inch": 6.9, "battery_mah": 5000,
            "ram_gb": 12, "storage_gb": 256, "camera_mp": 200, "os": "Android 15"
        },
    },
    {
        "name": "Xiaomi 14T Pro",
        "product_type": "mobile",
        "price": "719.99",
        "stock": 25,
        "description": "Dimensity 9300+, Leica cameras, 6.67-inch AMOLED 144Hz",
        "image_url": "https://cdnv2.tgdd.vn/mwg-static/tgdd/Products/Images/42/329890/xiaomi-14t-pro-black-1-638660516724586225.jpg",
        "sku": "MOBILE-003",
        "detail": {
            "brand": "Xiaomi", "screen_inch": 6.67, "battery_mah": 5000,
            "ram_gb": 12, "storage_gb": 256, "camera_mp": 50, "os": "Android 14"
        },
    },
    {
        "name": "Google Pixel 9 Pro",
        "product_type": "mobile",
        "price": "1079.99",
        "stock": 12,
        "description": "Google Tensor G4 chip, 6.3-inch LTPO OLED, advanced AI camera",
        "image_url": "https://tse4.mm.bing.net/th/id/OIP.CrfXiyUZrIDUdKkSD_-J7wHaHa?r=0&cb=thfc1falcon2&rs=1&pid=ImgDetMain&o=7&rm=3",
        "sku": "MOBILE-004",
        "detail": {
            "brand": "Google", "screen_inch": 6.3, "battery_mah": 4700,
            "ram_gb": 16, "storage_gb": 128, "camera_mp": 50, "os": "Android 15"
        },
    },
    {
        "name": "OPPO Find X8 Pro",
        "product_type": "mobile",
        "price": "1119.99",
        "stock": 10,
        "description": "Dimensity 9400, Hasselblad dual periscope cameras, 6.78-inch AMOLED",
        "image_url": "https://cdn.renderhub.com/rever-art/oppo-find-x8-all-colors/oppo-find-x8-all-colors-01.jpg",
        "sku": "MOBILE-005",
        "detail": {
            "brand": "OPPO", "screen_inch": 6.78, "battery_mah": 5910,
            "ram_gb": 16, "storage_gb": 256, "camera_mp": 50, "os": "Android 15"
        },
    },
    # ── Clothing ──────────────────────────────────────────────────────────────
    {
        "name": "Premium Cotton Polo Shirt",
        "product_type": "cloth",
        "price": "18.00",
        "stock": 100,
        "description": "Classic fit polo shirt, 100% cotton",
        "image_url": "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=800&auto=format&fit=crop",
        "sku": "CLOTH-001",
        "detail": {
            "brand": "Premium Basics", "sizes": "S,M,L,XL,XXL",
            "color": "Navy Blue", "material": "100% Cotton", "gender": "unisex"
        },
    },
    {
        "name": "Slim Fit Denim Jeans",
        "product_type": "cloth",
        "price": "26.00",
        "stock": 80,
        "description": "Modern slim fit jeans with stretch fabric for all-day comfort",
        "image_url": "https://picsum.photos/seed/cloth2/400/500",
        "sku": "CLOTH-002",
        "detail": {
            "brand": "DenimCo", "sizes": "28,30,32,34,36",
            "color": "Indigo Blue", "material": "98% Cotton, 2% Elastane", "gender": "male"
        },
    },
    {
        "name": "Classic Hoodie Sweatshirt",
        "product_type": "cloth",
        "price": "22.00",
        "stock": 60,
        "description": "Comfortable pullover hoodie with kangaroo pocket and adjustable drawstring",
        "image_url": "https://picsum.photos/seed/cloth3/400/500",
        "sku": "CLOTH-003",
        "detail": {
            "brand": "UrbanWear", "sizes": "S,M,L,XL,XXL",
            "color": "Charcoal Grey", "material": "80% Cotton, 20% Polyester", "gender": "unisex"
        },
    },
    {
        "name": "Floral Summer Dress",
        "product_type": "cloth",
        "price": "19.20",
        "stock": 50,
        "description": "Lightweight floral print midi dress, perfect for summer outings",
        "image_url": "https://picsum.photos/seed/cloth4/400/500",
        "sku": "CLOTH-004",
        "detail": {
            "brand": "BloomStyle", "sizes": "XS,S,M,L,XL",
            "color": "White Floral", "material": "100% Viscose", "gender": "female"
        },
    },
    {
        "name": "Performance Running Shorts",
        "product_type": "cloth",
        "price": "12.80",
        "stock": 120,
        "description": "Breathable quick-dry fabric, built-in liner, zippered back pocket",
        "image_url": "https://picsum.photos/seed/cloth5/400/500",
        "sku": "CLOTH-005",
        "detail": {
            "brand": "ActiveFit", "sizes": "S,M,L,XL,XXL",
            "color": "Black", "material": "88% Polyester, 12% Elastane", "gender": "unisex"
        },
    },
    {
        "name": "Merino Wool Turtleneck",
        "product_type": "cloth",
        "price": "35.60",
        "stock": 40,
        "description": "Ultra-soft merino wool turtleneck, temperature-regulating for all seasons",
        "image_url": "https://picsum.photos/seed/cloth6/400/500",
        "sku": "CLOTH-006",
        "detail": {
            "brand": "WoolLux", "sizes": "S,M,L,XL",
            "color": "Cream White", "material": "100% Merino Wool", "gender": "unisex"
        },
    },
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
    {"name": "Vuong Security",  "email": "security.team@example.com",  "role": "support",    "emp_id": "STF004"},
]

MANAGERS = [
    {"name": "Nguyen Operations", "email": "operations.manager@example.com", "dept": "operations", "emp_id": "MGR001"},
    {"name": "Tran Inventory",    "email": "inventory.manager@example.com",  "dept": "inventory",  "emp_id": "MGR002"},
    {"name": "Le Finance",        "email": "finance.manager@example.com",    "dept": "finance",    "emp_id": "MGR003"},
    {"name": "Truong IT",         "email": "it.manager@example.com",         "dept": "operations", "emp_id": "MGR004"},
]

# product_name must match a name in PRODUCTS — resolved to product_id after API seed (step 6)
REVIEWS = [
    {"customer_email": "nguyenvanan@example.com",  "product_name": "The Midnight Library",          "rating": 5, "comment": "Sách tuyệt vời, rất đáng suy ngẫm về các lựa chọn trong cuộc đời."},
    {"customer_email": "nguyenvanan@example.com",  "product_name": "Atomic Habits",                 "rating": 5, "comment": "Nội dung thực tế, hữu ích để thay đổi thói quen."},
    {"customer_email": "tranminhchau@example.com", "product_name": "Project Hail Mary",             "rating": 4, "comment": "Một chuyến phiêu lưu không gian thú vị."},
    {"customer_email": "lehoangduc@example.com",   "product_name": "Dune",                          "rating": 5, "comment": "Tuyệt tác Sci-Fi không thể bỏ qua."},
    {"customer_email": "mai@example.com",          "product_name": "Clean Code",                    "rating": 5, "comment": "Sách gối đầu giường cho mọi lập trình viên."},
    {"customer_email": "mai@example.com",          "product_name": "The Pragmatic Programmer",      "rating": 5, "comment": "Kiến thức vô giá cho sự nghiệp IT."},
    {"customer_email": "kiet@example.com",         "product_name": "Fluent Python",                 "rating": 4, "comment": "Sách hay cho ai muốn hiểu sâu về Python."},
    {"customer_email": "giang@example.com",        "product_name": "1984",                          "rating": 5, "comment": "Một tác phẩm kinh điển đáng sợ lại rất thực tế."},
]

# product_name in items must match a name in PRODUCTS
ORDERS = [
    {
        "customer_email": "nguyenvanan@example.com",
        "address": "123 Nguyen Hue, Quan 1, TP.HCM",
        "total": 79.50, "method": "credit_card",
        "items": [
            {"product_name": "Fluent Python", "qty": 1, "price": 45.00},
            {"product_name": "Clean Code",    "qty": 1, "price": 34.50},
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


# ── Required tables per database ───────────────────────────────────────────────
REQUIRED_TABLES = {
    'categories': ['app_category'],
    'customers':  ['app_customer'],
    'carts':      ['app_cart'],
    'staff':      ['app_staff'],
    'managers':   ['app_manager'],
    'reviews':    ['app_review'],
    'orders':     ['app_order', 'app_orderitem'],
    'payments':   ['app_payment'],
    'shipments':  ['app_shipment'],
}


# ── Wait for all databases and tables to be ready ────────────────────────────
def wait_for_databases(max_retries=30, delay=2):
    """Wait until all databases have their required tables (i.e. migrations completed)."""
    print("\n[WAIT] Waiting for all database tables to be ready...")
    all_ready = False

    for attempt in range(1, max_retries + 1):
        missing = []
        for db_key, tables in REQUIRED_TABLES.items():
            conn_string = DATABASES.get(db_key)
            if not conn_string:
                missing.append(f"{db_key} (no connection string)")
                continue
            try:
                conn = psycopg2.connect(conn_string)
                cur = conn.cursor()
                for table in tables:
                    cur.execute(
                        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                        (table,)
                    )
                    if not cur.fetchone()[0]:
                        missing.append(f"{db_key}.{table}")
                conn.close()
            except Exception as e:
                missing.append(f"{db_key} (connection error: {e})")

        if not missing:
            all_ready = True
            print(f"  [OK] All tables ready after {attempt} attempt(s)")
            break

        print(f"  [RETRY {attempt}/{max_retries}] Still waiting for: {', '.join(missing[:5])}")
        if len(missing) > 5:
            print(f"         ... and {len(missing) - 5} more")
        time.sleep(delay)

    if not all_ready:
        print("  [ERROR] Some tables are still missing after max retries!")
        print(f"  Missing: {', '.join(missing)}")
        sys.exit(1)


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


# ── Step 6: Seed all products via product-service API ─────────────────────────
def seed_products_via_api():
    """Seed all products (books + laptops + mobiles + clothing) to product-service.
    Returns dict {product_name: product_id} for downstream use in reviews & orders.
    """
    print("\n[6] Seeding products via product-service API...")
    name_to_id = {}
    success, failed = 0, 0

    for product in PRODUCTS:
        try:
            resp = requests.post(
                PRODUCT_SERVICE_URL,
                json=product,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            pid = data.get('id')
            if pid:
                name_to_id[product['name']] = pid
            print(f"  [OK] {product['name']} ({product['product_type']})")
            success += 1
        except requests.exceptions.HTTPError as e:
            err_body = ''
            if hasattr(e, 'response') and e.response is not None:
                try:
                    err_body = e.response.text[:500]
                except Exception:
                    pass
            print(f"  [FAIL] {product['name']} — {e}")
            if err_body:
                print(f"         Response: {err_body}")
            failed += 1
        except requests.exceptions.RequestException as e:
            print(f"  [FAIL] {product['name']} — {e}")
            failed += 1

    print(f"  Done: {success} created / {failed} failed")
    return name_to_id


# ── Main ───────────────────────────────────────────────────────────────────────
def seed_all():
    print("=" * 60)
    print("Starting full seed across all microservices")
    print("=" * 60)

    # Wait for all DB tables to exist (migrations must complete first)
    wait_for_databases()
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stats = {}

    # ── 1. CATEGORIES ──────────────────────────────────────────────────────────
    count = 0
    for c in CATEGORIES:
        exists = execute_query('categories', "SELECT id FROM app_category WHERE name=%s", (c['name'],), fetch_one=True)
        if not exists:
            execute_query('categories',
                "INSERT INTO app_category (name, description, applicable_types, created_at) VALUES (%s, %s, %s, %s)",
                (c['name'], c['desc'], '', now))
            count += 1
    stats['categories'] = execute_query('categories', "SELECT COUNT(1) FROM app_category", fetch_one=True) or 0
    print(f"[OK] Categories seeded (+{count})")

    # ── 2. CUSTOMERS ───────────────────────────────────────────────────────────
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

    # ── 3. CARTS (1 per customer) ──────────────────────────────────────────────
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

    # ── 4. STAFF ───────────────────────────────────────────────────────────────
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

    # ── 5. MANAGERS ────────────────────────────────────────────────────────────
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

    # ── 6. PRODUCTS via API — must run before reviews & orders ─────────────────
    product_id_map = seed_products_via_api()
    stats['products'] = len(product_id_map)

    # ── 7. REVIEWS ─────────────────────────────────────────────────────────────
    count = 0
    for r in REVIEWS:
        cust_id    = execute_query('customers', "SELECT id FROM app_customer WHERE email=%s", (r['customer_email'],), fetch_one=True)
        product_id = product_id_map.get(r['product_name'])
        if not product_id:
            print(f"  [SKIP] Review: '{r['product_name']}' not in product_id_map")
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
                product_id = product_id_map.get(item['product_name'])
                if not product_id:
                    print(f"  [SKIP] Order item: '{item['product_name']}' not in product_id_map")
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

    stats['orders']      = execute_query('orders',    "SELECT COUNT(1) FROM app_order",     fetch_one=True) or 0
    stats['order_items'] = execute_query('orders',    "SELECT COUNT(1) FROM app_orderitem", fetch_one=True) or 0
    stats['payments']    = execute_query('payments',  "SELECT COUNT(1) FROM app_payment",   fetch_one=True) or 0
    stats['shipments']   = execute_query('shipments', "SELECT COUNT(1) FROM app_shipment",  fetch_one=True) or 0
    print(f"[OK] Orders/Payments/Shipments seeded "
          f"(+{order_count} orders, +{item_count} items, +{pay_count} pays, +{ship_count} ships)")

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SEED SUMMARY")
    print("=" * 60)
    labels = {
        'categories':  'Categories  (catalog_db)',
        'customers':   'Customers   (customer_db)',
        'carts':       'Carts       (cart_db)',
        'staff':       'Staff       (staff_db)',
        'managers':    'Managers    (manager_db)',
        'products':    'Products    (product-service API)',
        'reviews':     'Reviews     (comment_rate_db)',
        'orders':      'Orders      (order_db)',
        'order_items': 'Order Items (order_db)',
        'payments':    'Payments    (pay_db)',
        'shipments':   'Shipments   (ship_db)',
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