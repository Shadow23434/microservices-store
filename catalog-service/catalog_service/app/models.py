from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    applicable_types = models.CharField(
        max_length=255,
        blank=True,
        help_text="CSV of product types: book,laptop,mobile,cloth or empty for all"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_applicable_types(self):
        """Returns list of applicable product types, empty list means all types."""
        if not self.applicable_types:
            return []
        return [t.strip() for t in self.applicable_types.split(',')]
