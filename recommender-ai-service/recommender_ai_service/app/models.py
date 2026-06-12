from django.db import models


class Recommendation(models.Model):
    """Store product recommendation results for each customer."""
    customer_id = models.IntegerField(unique=True)
    recommended_product_ids = models.TextField(default="")  # CSV product IDs
    algorithm = models.CharField(max_length=50, default="multi_signal")
    reason = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_product_ids(self):
        if not self.recommended_product_ids:
            return []
        return [int(x) for x in self.recommended_product_ids.split(",") if x.strip()]

    def set_product_ids(self, ids):
        self.recommended_product_ids = ",".join(str(i) for i in ids)

    def __str__(self):
        return f"Recommendations for Customer {self.customer_id}"


class WishlistItem(models.Model):
    """
    Internal wishlist — used because the repo doesn't have a dedicated wishlist-service.
    Frontend calls POST/DELETE /recommendations/wishlist/ to add/remove items.
    Recommendation engine reads directly via ORM (no HTTP call needed).
    """
    customer_id = models.IntegerField(db_index=True)
    product_id = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("customer_id", "product_id")
        ordering = ["-added_at"]

    def __str__(self):
        return f"Wishlist: customer={self.customer_id} product={self.product_id}"


class Conversation(models.Model):
    """Store chatbot conversation history."""
    customer_id = models.IntegerField(db_index=True, null=True, blank=True)
    session_id = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} - Customer {self.customer_id}"


class ChatMessage(models.Model):
    """Store individual messages within a conversation."""
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    product_ids = models.TextField(blank=True)  # CSV product IDs mentioned in the message
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def get_product_ids(self):
        if not self.product_ids:
            return []
        return [int(x) for x in self.product_ids.split(",") if x.strip()]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
