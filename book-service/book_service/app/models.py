from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.CharField(max_length=10, blank=True, default="0.0")
    reviews = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    image = models.URLField(max_length=1000, blank=True, default="")
    category = models.CharField(max_length=255, blank=True, default="")
    format = models.CharField(max_length=255, blank=True, default="")
    pages = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, blank=True, default="")
    publisher = models.CharField(max_length=255, blank=True, default="")
    publicationDate = models.CharField(max_length=100, blank=True, default="")
    isbn = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.title