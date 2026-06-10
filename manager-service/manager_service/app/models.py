from django.db import models


class Manager(models.Model):
    DEPARTMENT_CHOICES = [
        ("operations", "Operations"),
        ("inventory", "Inventory"),
        ("marketing", "Marketing"),
        ("finance", "Finance"),
    ]
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    department = models.CharField(
        max_length=50, choices=DEPARTMENT_CHOICES, default="operations"
    )
    employee_id = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.department}"
