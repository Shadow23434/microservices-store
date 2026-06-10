from django.db import models


class Review(models.Model):
    customer_id = models.IntegerField()
    product_id = models.IntegerField()
    product_type = models.CharField(max_length=50, blank=True, default='book')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("customer_id", "product_id")

    def __str__(self):
        return f"Review by Customer {self.customer_id} on Product {self.product_id} - {self.rating} stars"
