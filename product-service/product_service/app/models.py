from django.db import models


class ProductType(models.TextChoices):
    BOOK = 'book', 'Sách'
    LAPTOP = 'laptop', 'Laptop'
    MOBILE = 'mobile', 'Điện thoại'
    CLOTH = 'cloth', 'Quần áo'


class Product(models.Model):
    name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50, choices=ProductType.choices)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    category_id = models.IntegerField(null=True, blank=True)
    image_url = models.URLField(blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.product_type}] {self.name}"


class BookDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='book_detail')
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    published_date = models.DateField(null=True, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, default='vi')

    class Meta:
        db_table = 'book_details'

    def __str__(self):
        return f"Book: {self.product.name}"


class LaptopDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='laptop_detail')
    brand = models.CharField(max_length=100)
    cpu = models.CharField(max_length=255, blank=True)
    ram_gb = models.IntegerField(null=True, blank=True)
    storage_gb = models.IntegerField(null=True, blank=True)
    display_inch = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    os = models.CharField(max_length=100, blank=True)
    weight_kg = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    gpu = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'laptop_details'

    def __str__(self):
        return f"Laptop: {self.product.name}"


class MobileDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='mobile_detail')
    brand = models.CharField(max_length=100)
    screen_inch = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    battery_mah = models.IntegerField(null=True, blank=True)
    ram_gb = models.IntegerField(null=True, blank=True)
    storage_gb = models.IntegerField(null=True, blank=True)
    camera_mp = models.IntegerField(null=True, blank=True)
    os = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'mobile_details'

    def __str__(self):
        return f"Mobile: {self.product.name}"


class ClothDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='cloth_detail')
    brand = models.CharField(max_length=100, blank=True)
    sizes = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, blank=True)
    material = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'cloth_details'

    def __str__(self):
        return f"Cloth: {self.product.name}"