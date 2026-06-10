from django.contrib import admin
from .models import Product, BookDetail, LaptopDetail, MobileDetail, ClothDetail


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'product_type', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['product_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'sku']


@admin.register(BookDetail)
class BookDetailAdmin(admin.ModelAdmin):
    list_display = ['product', 'author', 'isbn', 'publisher']
    search_fields = ['author', 'isbn', 'publisher']


@admin.register(LaptopDetail)
class LaptopDetailAdmin(admin.ModelAdmin):
    list_display = ['product', 'brand', 'cpu', 'ram_gb', 'storage_gb']
    search_fields = ['brand', 'cpu']


@admin.register(MobileDetail)
class MobileDetailAdmin(admin.ModelAdmin):
    list_display = ['product', 'brand', 'screen_inch', 'ram_gb', 'storage_gb']
    search_fields = ['brand']


@admin.register(ClothDetail)
class ClothDetailAdmin(admin.ModelAdmin):
    list_display = ['product', 'brand', 'sizes', 'color', 'material']
    search_fields = ['brand', 'material']