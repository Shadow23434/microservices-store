from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    customer_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - Customer {self.customer_id} - {self.status}"

    def add_item(self, product_id, quantity, unit_price):
        if self.status != 'DRAFT':
            raise BusinessRuleViolation("Cannot add item to confirmed order")
        # Tính total lại
        self.total += unit_price * quantity
        self.save()

class OrderItem(models.Model):  # Child Entity – KHÔNG được truy cập trực tiếp
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE) # Phải thuộc Order
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255, default='')
    product_type = models.CharField(max_length=50, default='book')
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Product {self.product_id} x{self.quantity} in Order #{self.order.id}"
