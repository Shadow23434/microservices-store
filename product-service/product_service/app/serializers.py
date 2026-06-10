from rest_framework import serializers
from .models import Product, BookDetail, LaptopDetail, MobileDetail, ClothDetail


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookDetail
        exclude = ['id', 'product']


class LaptopDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaptopDetail
        exclude = ['id', 'product']


class MobileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileDetail
        exclude = ['id', 'product']


class ClothDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothDetail
        exclude = ['id', 'product']


class ProductSerializer(serializers.ModelSerializer):
    detail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_detail(self, obj):
        detail_map = {
            'book': ('book_detail', BookDetailSerializer),
            'laptop': ('laptop_detail', LaptopDetailSerializer),
            'mobile': ('mobile_detail', MobileDetailSerializer),
            'cloth': ('cloth_detail', ClothDetailSerializer),
        }
        related_name, serializer_cls = detail_map.get(obj.product_type, (None, None))
        if not related_name:
            return None
        detail_obj = getattr(obj, related_name, None)
        if detail_obj is None:
            return None
        return serializer_cls(detail_obj).data