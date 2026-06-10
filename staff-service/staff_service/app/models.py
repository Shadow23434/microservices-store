from django.db import models


class Staff(models.Model):
    ROLE_CHOICES = [
        ("warehouse", "Warehouse Staff"),
        ("sales", "Sales Staff"),
        ("support", "Customer Support"),
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="warehouse")
    employee_id = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"
