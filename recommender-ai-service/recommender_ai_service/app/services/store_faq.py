"""
Static store FAQ — used for chatbot responses to general questions.
"""

STORE_FAQ = """
STORE INFORMATION:

1. DELIVERY:
   - Nationwide delivery
   - Delivery time: 3-5 business days
   - Free delivery for orders over $50
   - Delivery fee: $3-$7 depending on region

2. RETURNS:
   - Returns accepted within 7 days if product is defective/damaged
   - Product must be in original packaging with tags intact
   - 100% refund if product does not match description

3. PAYMENT:
   - COD (cash on delivery)
   - Bank transfer
   - E-wallets (Momo, ZaloPay, VNPay)
   - Credit/debit cards

4. CONTACT:
   - Hotline: 1900 xxxx (8am-5pm, Mon-Fri)
   - Email: support@bookstore.vn
   - Address: 123 ABC Street, District XYZ, Ho Chi Minh City

5. WARRANTY:
   - Books: no warranty (returns only for printing defects)
   - Laptop/Mobile: 12-month manufacturer warranty
   - Clothing: size exchange within 7 days
"""


def get_faq_answer(question):
    """
    Answer FAQ questions using simple keyword matching.
    Returns None if no match found, so chatbot falls back to LLM.
    """
    question_lower = question.lower()

    # Delivery
    if any(kw in question_lower for kw in ["delivery", "shipping", "ship", "dispatch", "courier", "tracking", "how long"]):
        return (
            "Regarding delivery: We deliver nationwide within 3-5 business days. "
            "Free delivery for orders over $50. Standard delivery fee is $3-$7 depending on region."
        )

    # Returns
    if any(kw in question_lower for kw in ["return", "refund", "exchange", "send back", "money back", "defective"]):
        return (
            "Regarding returns: You can return items within 7 days if the product is defective/damaged, "
            "with original packaging and tags intact. We offer a 100% refund if the product does not match the description."
        )

    # Payment
    if any(kw in question_lower for kw in ["payment", "pay", "credit card", "cash", "cod", "bank transfer", "wallet", "visa"]):
        return (
            "Regarding payment: We support COD (cash on delivery), bank transfer, "
            "e-wallets (Momo, ZaloPay, VNPay), and credit/debit cards."
        )

    # Contact
    if any(kw in question_lower for kw in ["contact", "phone", "email", "support", "hotline", "reach", "address"]):
        return (
            "Regarding contact: Hotline 1900 xxxx (8am-5pm, Mon-Fri), email support@bookstore.vn, "
            "address: 123 ABC Street, District XYZ, Ho Chi Minh City."
        )

    # Warranty
    if any(kw in question_lower for kw in ["warranty", "guarantee", "repair", "broken", "defective"]):
        return (
            "Regarding warranty: Books have no warranty (returns only for printing defects). "
            "Laptop/Mobile come with a 12-month manufacturer warranty. Clothing can be exchanged for a different size within 7 days."
        )

    # No FAQ match found
    return None
