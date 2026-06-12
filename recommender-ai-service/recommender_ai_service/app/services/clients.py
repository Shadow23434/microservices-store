"""
Service clients for recommender-ai-service.
Communicates with product-service, comment-rate-service, order-service, cart-service.
Uses ThreadPoolExecutor for parallel calls to avoid cumulative latency.
"""

import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Service URLs from environment variables
PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://product-service:8888")
COMMENT_RATE_SERVICE_URL = os.environ.get("COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8888")
ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://order-service:8888")
CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://cart-service:8888")

TIMEOUT = 5  # seconds


def get_all_products():
    """Fetch all products from product-service."""
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}/api/products/", timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []


def search_products(filters):
    """
    Search products with filters (for chatbot).
    Filters may include: product_type, category_id, price_min, price_max, keywords.
    Falls back to broader search if keyword filter yields no results.
    """
    try:
        params = {}
        if filters.get("product_type"):
            params["product_type"] = filters["product_type"]
        if filters.get("category_id"):
            params["category_id"] = filters["category_id"]

        response = requests.get(
            f"{PRODUCT_SERVICE_URL}/api/products/",
            params=params,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        products = response.json()

        # Filter by price on the Python side (product-service doesn't support price filtering)
        price_filtered = products
        if filters.get("price_min"):
            price_filtered = [p for p in price_filtered if float(p.get("price", 0)) >= float(filters["price_min"])]
        if filters.get("price_max"):
            price_filtered = [p for p in price_filtered if float(p.get("price", 0)) <= float(filters["price_max"])]

        # Filter by keywords (match in product name)
        if filters.get("keywords"):
            keywords = filters["keywords"].lower()
            keyword_matched = [p for p in price_filtered if keywords in p.get("name", "").lower()]
            # Fallback: if keyword matching eliminates all products, try matching
            # each keyword individually instead of the full phrase
            if not keyword_matched:
                individual_words = keywords.split()
                scored = {}
                for p in price_filtered:
                    name = p.get("name", "").lower()
                    score = sum(1 for w in individual_words if w in name)
                    if score > 0:
                        scored[p.get("id")] = (score, p)
                if scored:
                    # Sort by match score descending
                    keyword_matched = [item[1] for item in sorted(scored.values(), key=lambda x: -x[0])]
                else:
                    # Last fallback: return price-filtered products without keyword filter
                    keyword_matched = price_filtered

            return keyword_matched

        # Final fallback: if price filter eliminated everything, return all products
        # so the LLM (or mock) always has something to work with
        return price_filtered if price_filtered else products
    except Exception as e:
        print(f"Error searching products: {e}")
        return []


def get_reviews_by_customer(customer_id):
    """Fetch all reviews for a customer from comment-rate-service."""
    try:
        response = requests.get(
            f"{COMMENT_RATE_SERVICE_URL}/reviews/",
            params={"customer_id": customer_id},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching reviews for customer {customer_id}: {e}")
        return []


def get_product_rating(product_id):
    """Fetch average rating info for a product."""
    try:
        response = requests.get(
            f"{COMMENT_RATE_SERVICE_URL}/reviews/product/{product_id}/rating/",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching rating for product {product_id}: {e}")
        return {"average_rating": 0, "total_reviews": 0}


def get_orders_by_customer(customer_id):
    """Fetch customer orders from order-service."""
    try:
        response = requests.get(
            f"{ORDER_SERVICE_URL}/orders/",
            params={"customer_id": customer_id},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        orders = response.json()

        # Extract product_ids from order items
        product_ids = []
        for order in orders:
            items = order.get("items", [])
            for item in items:
                product_id = item.get("product_id") or item.get("book_id")
                if product_id:
                    product_ids.append(int(product_id))
        return product_ids
    except Exception as e:
        print(f"Error fetching orders for customer {customer_id}: {e}")
        return []


def get_cart_by_customer(customer_id):
    """
    Fetch product_ids in customer's cart from cart-service.
    Cart-service has endpoint: GET /carts/<customer_id>/ returning list of cart items.
    """
    try:
        response = requests.get(
            f"{CART_SERVICE_URL}/carts/{customer_id}/",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        cart_items = response.json()

        # Extract product_ids
        product_ids = []
        for item in cart_items:
            product_id = item.get("product_id") or item.get("book_id")
            if product_id:
                product_ids.append(int(product_id))
        return product_ids
    except Exception as e:
        print(f"Error fetching cart for customer {customer_id}: {e}")
        return []


def get_wishlist_by_customer(customer_id):
    """
    Fetch customer wishlist from internal database.
    Since there's no dedicated wishlist-service, we read directly from the WishlistItem model.
    """
    try:
        from app.models import WishlistItem
        return list(
            WishlistItem.objects.filter(customer_id=customer_id)
            .values_list("product_id", flat=True)
        )
    except Exception as e:
        print(f"Error fetching wishlist for customer {customer_id}: {e}")
        return []


def fetch_customer_signals(customer_id):
    """
    Fetch all customer signals (orders, cart, reviews, wishlist) in parallel.
    Returns a dict containing product_ids from each signal.
    """
    signals = {
        "order_ids": [],
        "cart_ids": [],
        "reviews": [],
        "wishlist_ids": []
    }

    # Use ThreadPoolExecutor for parallel calls
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks
        future_to_signal = {
            executor.submit(get_orders_by_customer, customer_id): "order_ids",
            executor.submit(get_cart_by_customer, customer_id): "cart_ids",
            executor.submit(get_reviews_by_customer, customer_id): "reviews",
        }

        # Wait for results with timeout
        try:
            for future in as_completed(future_to_signal, timeout=TIMEOUT + 1):
                signal_name = future_to_signal[future]
                try:
                    signals[signal_name] = future.result()
                except Exception as e:
                    print(f"Error fetching {signal_name}: {e}")
                    signals[signal_name] = []
        except TimeoutError:
            print("Timeout while fetching customer signals")

    # Wishlist is read from internal DB (no thread needed)
    signals["wishlist_ids"] = get_wishlist_by_customer(customer_id)

    return signals
