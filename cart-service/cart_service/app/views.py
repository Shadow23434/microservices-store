import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

# Docker: http://product-service:8888 | Local: http://127.0.0.1:8888
PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://product-service:8888")


class CartCreate(APIView):
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddCartItem(APIView):
    def post(self, request):
        product_id = request.data.get("product_id")

        # 1. Kiểm tra tính tồn tại của sản phẩm thông qua Product Service
        try:
            r = requests.get(f"{PRODUCT_SERVICE_URL}/api/products/{product_id}/", timeout=5)
            if r.status_code == 404:
                return Response(
                    {"error": "Product not found in Product Service"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if r.status_code != 200:
                return Response(
                    {"error": "Error fetching product from Product Service"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            product = r.json()
            if product.get('stock', 0) < 1:
                return Response(
                    {"error": "Product out of stock"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except requests.exceptions.RequestException:
            return Response(
                {"error": "Cannot connect to Product Service"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # 2. Lưu sản phẩm vào giỏ hàng
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewCart(APIView):
    def get(self, request, customer_id):
        try:
            # Lấy giỏ hàng theo customer_id
            cart = Cart.objects.get(customer_id=customer_id)
            items = CartItem.objects.filter(cart=cart)
            serializer = CartItemSerializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND
            )
