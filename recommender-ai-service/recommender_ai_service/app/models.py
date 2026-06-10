from django.db import models


class Recommendation(models.Model):
    customer_id = models.IntegerField(unique=True)
    # Luu danh sach book_id duoc goi y, ngan cach bang dau phay
    recommended_book_ids = models.TextField(default="")
    updated_at = models.DateTimeField(auto_now=True)

    def get_book_ids(self):
        if not self.recommended_book_ids:
            return []
        return [int(x) for x in self.recommended_book_ids.split(",") if x.strip()]

    def set_book_ids(self, ids):
        self.recommended_book_ids = ",".join(str(i) for i in ids)

    def __str__(self):
        return f"Recommendations for Customer {self.customer_id}"
