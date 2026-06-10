from django.db import models


class Cart(models.Model):
    # Lưu ID của khách hàng từ Customer Service
    customer_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for Customer {self.customer_id}"


class CartItem(models.Model):
    # Quan hệ 1-Nhiều: Một giỏ hàng có nhiều sản phẩm
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)

    # Lưu ID của sách từ Book Service
    book_id = models.IntegerField()
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Book {self.book_id} (x{self.quantity}) in Cart {self.cart.id}"
