"""
Mock LLM provider — doesn't call real API, provides simple rule-based responses.
Used for dev/test when no API key is available or to avoid costs.
"""

from .base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    """Mock provider — no API key needed, no cost."""

    def generate_answer(self, message, products, history, store_faq):
        """Generate simple response based on products and FAQ."""
        from ..store_faq import get_faq_answer

        # Check FAQ first
        faq_answer = get_faq_answer(message)
        if faq_answer:
            return faq_answer

        # If matching products found
        if products:
            product_names = [p["name"] for p in products[:3]]
            if len(product_names) == 1:
                product_list = product_names[0]
            elif len(product_names) == 2:
                product_list = f"{product_names[0]} and {product_names[1]}"
            else:
                product_list = ", ".join(product_names[:-1]) + f", and {product_names[-1]}"

            return (
                f"Based on your request, I found {len(products)} matching products: "
                f"{product_list}. Would you like to see details of any specific product?"
            )

        # No matching products — give a helpful response instead of generic "sorry"
        msg_lower = message.lower().strip()

        # Greetings / general conversation
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "xin chao", "chao"]
        if any(g in msg_lower for g in greetings):
            return (
                "Hello! Welcome to BookStore. We have books, laptops, phones, and clothing. "
                "What are you looking for today?"
            )

        # Suggest browsing categories
        return (
            "I couldn't find an exact match, but our store offers books, laptops, phones, and clothing. "
            "Try asking about a specific product type, like 'show me books' or 'I need a laptop'. "
            "You can also specify a price range!"
        )
