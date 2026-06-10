from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, BookDetail, LaptopDetail, MobileDetail, ClothDetail
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related(
        'book_detail', 'laptop_detail', 'mobile_detail', 'cloth_detail'
    )
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product_type', 'category_id', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Create detail record based on product_type
        detail_data = request.data.get('detail', {})
        if detail_data:
            self._create_detail(product, detail_data)

        # Reload product with detail
        product.refresh_from_db()
        output_serializer = self.get_serializer(product)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Update detail if provided
        detail_data = request.data.get('detail', {})
        if detail_data:
            self._update_detail(product, detail_data)

        product.refresh_from_db()
        output_serializer = self.get_serializer(product)
        return Response(output_serializer.data)

    def _create_detail(self, product, detail_data):
        if product.product_type == 'book':
            BookDetail.objects.create(product=product, **detail_data)
        elif product.product_type == 'laptop':
            LaptopDetail.objects.create(product=product, **detail_data)
        elif product.product_type == 'mobile':
            MobileDetail.objects.create(product=product, **detail_data)
        elif product.product_type == 'cloth':
            ClothDetail.objects.create(product=product, **detail_data)

    def _update_detail(self, product, detail_data):
        detail_map = {
            'book': 'book_detail',
            'laptop': 'laptop_detail',
            'mobile': 'mobile_detail',
            'cloth': 'cloth_detail',
        }
        related_name = detail_map.get(product.product_type)
        if related_name:
            detail_obj = getattr(product, related_name, None)
            if detail_obj:
                for key, value in detail_data.items():
                    setattr(detail_obj, key, value)
                detail_obj.save()