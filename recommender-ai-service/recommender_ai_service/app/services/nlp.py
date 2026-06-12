"""
Rule-based filter extraction for chatbot.
Extracts filters from user questions to find matching products.
"""

import re


# Keywords to identify product_type
PRODUCT_TYPE_KEYWORDS = {
    "book": ["book", "novel", "textbook", "comic", "manga", "dictionary", "reading", "literature", "bestseller", "paperback", "hardcover", "fiction", "non-fiction"],
    "laptop": ["laptop", "computer", "notebook", "macbook", "thinkpad", "dell", "hp", "lenovo", "asus", "gaming laptop", "workstation", "ultrabook"],
    "mobile": ["phone", "smartphone", "iphone", "samsung", "mobile", "xiaomi", "oppo", "vivo", "android", "cellphone", "tablet"],
    "cloth": ["shirt", "pants", "dress", "jacket", "clothing", "fashion", "shoes", "hoodie", "t-shirt", "jeans", "coat", "skirt", "apparel"],
}

# Regex patterns to extract price
# Supports: "under 1 million", "over 500k", "between 100 and 500", "$500", "500 dollars"
PRICE_PATTERNS = [
    # "under X", "over X", "more than X", "less than X"
    re.compile(r'(under|over|more than|less than|above|below)\s+\$?([\d.,]+)\s*(k|thousand|million|m)?', re.IGNORECASE),
    # "between X and Y", "from X to Y"
    re.compile(r'(?:between|from)\s+\$?([\d.,]+)\s*(k|thousand|million|m)?\s+(?:and|to)\s+\$?([\d.,]+)\s*(k|thousand|million|m)?', re.IGNORECASE),
    # Price with currency unit: "$500", "500 dollars", "500 USD", "500k"
    re.compile(r'\$?([\d.,]+)\s*(k|thousand|million|m)?\s*(?:dollars?|usd)?', re.IGNORECASE),
]


def _normalize_price_value(value_str, unit):
    """Convert price value to float."""
    # Remove commas and dots used as separators
    value_str = value_str.replace(",", "").replace(".", "").strip()
    if not value_str:
        return None
    value = float(value_str)

    unit = (unit or "").lower()
    if unit in ["k", "thousand"]:
        value *= 1000
    elif unit in ["million", "m"]:
        value *= 1000000

    return value


def extract_filters(message):
    """
    Extract filters from user's question.

    Returns dict:
    {
        "product_type": "book" | "laptop" | "mobile" | "cloth" | None,
        "price_min": float | None,
        "price_max": float | None,
        "keywords": str | None
    }
    """
    filters = {
        "product_type": None,
        "price_min": None,
        "price_max": None,
        "keywords": None,
    }

    message_lower = message.lower()

    # 1. Extract product_type
    for product_type, keywords in PRODUCT_TYPE_KEYWORDS.items():
        if any(kw in message_lower for kw in keywords):
            filters["product_type"] = product_type
            break

    # 2. Extract price
    # Pattern 1: "under X", "over X", "more than X"
    match1 = PRICE_PATTERNS[0].search(message)
    if match1:
        operator = match1.group(1).lower()
        value = _normalize_price_value(match1.group(2), match1.group(3))

        if operator in ["under", "less than", "below"]:
            filters["price_max"] = value
        elif operator in ["over", "more than", "above"]:
            filters["price_min"] = value

    # Pattern 2: "between X and Y" or "from X to Y"
    if not (filters["price_min"] and filters["price_max"]):
        match2 = PRICE_PATTERNS[1].search(message)
        if match2:
            filters["price_min"] = _normalize_price_value(match2.group(1), match2.group(2))
            filters["price_max"] = _normalize_price_value(match2.group(3), match2.group(4))

    # Pattern 3: Plain price like "$500" or "500 dollars"
    if not filters["price_min"] and not filters["price_max"]:
        match3 = PRICE_PATTERNS[2].search(message)
        if match3:
            value = _normalize_price_value(match3.group(1), match3.group(2))
            filters["price_max"] = value

    # 3. Keywords (search terms)
    # Remove stop words and use remaining words as keywords
    stop_words = [
        "i", "me", "my", "we", "our", "you", "your", "it", "its",
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "for", "and", "nor", "but", "or", "yet", "so", "in", "on", "at",
        "to", "of", "with", "by", "from", "as", "into", "through", "during",
        "want", "buy", "find", "looking", "get", "show", "me", "please",
        "some", "any", "this", "that", "these", "those", "what", "which",
        "who", "whom", "how", "when", "where", "why", "all", "each", "every",
        "under", "over", "more", "less", "than", "between", "from", "to",
        "k", "thousand", "million", "m", "dollars", "dollar", "usd", "$",
    ]

    # Exclude product_type keywords from keyword extraction
    all_product_keywords = []
    for kws in PRODUCT_TYPE_KEYWORDS.values():
        all_product_keywords.extend(kws)

    # Split words and filter
    words = re.findall(r'\b\w+\b', message_lower)
    keywords_list = [
        w for w in words
        if w not in stop_words
        and w not in all_product_keywords
        and len(w) > 1
        and not w.isdigit()
    ]

    if keywords_list:
        filters["keywords"] = " ".join(keywords_list[:5])  # Take max 5 keywords

    return filters
