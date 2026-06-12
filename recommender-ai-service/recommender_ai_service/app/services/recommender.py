"""
Multi-signal recommendation engine.

Signals & weights:
    order    (purchased)       → weight 4.0  | excluded from results (already owned)
    wishlist (favorited)       → weight 3.0  | NOT excluded (reminder to purchase)
    cart     (in cart)         → weight 2.5  | excluded from results (currently buying)
    review≥4 (highly rated)    → weight 2.0  | excluded from results (already experienced)
    review<4 (low rated)       → weight 0.5  | excluded from results
    popularity (fallback)      → weight derived from avg_rating × (1 + 0.1×total)
"""

from . import clients


# ─── Signal weights ─────────────────────────────────────────
WEIGHT_ORDER    = 4.0
WEIGHT_WISHLIST = 3.0
WEIGHT_CART     = 2.5
WEIGHT_LIKED    = 2.0   # review >= 4 stars
WEIGHT_DISLIKED = 0.5   # review < 4 stars

# Score formula = category_affinity * CAT_FACTOR + type_affinity * TYPE_FACTOR
CAT_FACTOR  = 3.0
TYPE_FACTOR = 1.0

DEFAULT_LIMIT = 8


def build_recommendations(customer_id, limit=DEFAULT_LIMIT):
    """
    Return recommended products for customer_id, up to `limit` items.
    Each item: {product_id, name, product_type, price, score, reason, average_rating, in_wishlist}
    """
    # ── 1. Fetch all signals in parallel ────────────────────────────
    signals = clients.fetch_customer_signals(customer_id)
    reviews      = signals["reviews"]         # list[{product_id, rating, ...}]
    order_ids    = set(signals["order_ids"])  # set[int]
    cart_ids     = set(signals["cart_ids"])   # set[int]
    wishlist_ids = set(signals["wishlist_ids"])  # set[int]

    # Categorize reviews
    reviewed_ids = {r["product_id"] for r in reviews}
    liked_ids    = {r["product_id"] for r in reviews if r.get("rating", 0) >= 4}
    disliked_ids = reviewed_ids - liked_ids

    # ── 2. Determine exclude_ids (products to exclude from results) ──
    # Wishlist is NOT excluded — customer added it but hasn't purchased yet
    exclude_ids = order_ids | cart_ids | reviewed_ids

    # ── 3. Check for cold-start ────────────────────────────────────
    has_any_signal = bool(order_ids or wishlist_ids or cart_ids or liked_ids)
    if not has_any_signal:
        all_products = clients.get_all_products()
        return _popularity_fallback(all_products, exclude=exclude_ids, limit=limit)

    # ── 4. Fetch all products ──────────────────────────────────────
    all_products = clients.get_all_products()
    by_id = {p["id"]: p for p in all_products}

    # ── 5. Compute affinity maps from all signals ──────────────────
    category_affinity = {}  # cat_id -> total weight
    type_affinity = {}      # product_type -> total weight

    def _accumulate(product_id, weight):
        p = by_id.get(product_id)
        if not p:
            return
        cat = p.get("category_id")
        ptype = p.get("product_type", "")
        if cat:
            category_affinity[cat] = category_affinity.get(cat, 0) + weight
        if ptype:
            type_affinity[ptype] = type_affinity.get(ptype, 0) + weight

    for pid in order_ids:
        _accumulate(pid, WEIGHT_ORDER)
    for pid in wishlist_ids:
        _accumulate(pid, WEIGHT_WISHLIST)
    for pid in cart_ids:
        _accumulate(pid, WEIGHT_CART)
    for pid in liked_ids:
        _accumulate(pid, WEIGHT_LIKED)
    for pid in disliked_ids:
        _accumulate(pid, WEIGHT_DISLIKED)

    # ── 6. Score each candidate product ────────────────────────────
    scored = []
    for p in all_products:
        if p["id"] in exclude_ids or not p.get("is_active", True):
            continue
        cat   = p.get("category_id")
        ptype = p.get("product_type", "")
        score = (
            CAT_FACTOR  * category_affinity.get(cat, 0) +
            TYPE_FACTOR * type_affinity.get(ptype, 0)
        )
        if score > 0:
            scored.append((p, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    # ── 7. Select display reason ───────────────────────────────────
    reason = _select_reason(order_ids, wishlist_ids, cart_ids, liked_ids)

    # ── 8. Build main results ──────────────────────────────────────
    results = []
    for p, score in scored[:limit]:
        # Wishlist item appears in results → attach special reason
        item_reason = (
            "In your wishlist" if p["id"] in wishlist_ids
            else reason
        )
        results.append(_to_result(p, score, item_reason))

    # ── 9. Fill remaining with popularity fallback if needed ────────
    if len(results) < limit:
        used_ids = exclude_ids | {r["product_id"] for r in results}
        fallback = _popularity_fallback(all_products, exclude=used_ids, limit=limit - len(results))
        results.extend(fallback)

    return results[:limit]


def build_similar_products(product_id, limit=6):
    """
    Recommend similar products by product_id (no customer_id needed).
    Prioritizes same category_id, then same product_type.
    """
    all_products = clients.get_all_products()
    target = next((p for p in all_products if p["id"] == product_id), None)
    if not target:
        return []

    same_cat  = []
    same_type = []
    for p in all_products:
        if p["id"] == product_id or not p.get("is_active", True):
            continue
        if p.get("category_id") == target.get("category_id"):
            same_cat.append(p)
        elif p.get("product_type") == target.get("product_type"):
            same_type.append(p)

    candidates = (same_cat + same_type)[:limit]
    return candidates


# ─── Helpers ──────────────────────────────────────────────────────

def _select_reason(order_ids, wishlist_ids, cart_ids, liked_ids):
    """Select the reason string based on the strongest signal priority."""
    if order_ids:
        return "Based on your purchase history"
    if wishlist_ids:
        return "Matches your wishlist"
    if cart_ids:
        return "You might also like this"
    if liked_ids:
        return "Based on products you rated highly"
    return "Highly rated by other customers"


def _to_result(product, score, reason, rating=None):
    """Convert product dict + score into a response item."""
    if rating is None:
        rating = clients.get_product_rating(product["id"])
    return {
        "product_id":     product["id"],
        "name":           product.get("name", ""),
        "product_type":   product.get("product_type", ""),
        "price":          product.get("price", "0"),
        "score":          round(float(score), 2),
        "reason":         reason,
        "average_rating": rating.get("average_rating"),
        "in_wishlist":    False,  # can be set in view if needed
    }


def _popularity_fallback(all_products, exclude, limit):
    """Fallback: sort by popularity_score = avg_rating × (1 + 0.1 × total_reviews)."""
    scored = []
    for p in all_products:
        if p["id"] in exclude or not p.get("is_active", True):
            continue
        rating = clients.get_product_rating(p["id"])
        avg    = float(rating.get("average_rating") or 0)
        total  = int(rating.get("total_reviews") or 0)
        pop_score = avg * (1 + 0.1 * total)
        scored.append((p, pop_score, rating))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [
        _to_result(p, score, "Highly rated by other customers", rating)
        for p, score, rating in scored[:limit]
    ]
