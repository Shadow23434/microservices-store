import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

# Docker: http://book-service:8000 | Local: http://127.0.0.1:8002
BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")


class CartCreate(APIView):
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddCartItem(APIView):
    def post(self, request):
        book_id = request.data.get("book_id")

        # 1. Kiểm tra tính tồn tại của sách thông qua Book Service
        try:
            # Thay vì lấy tất cả sách, tốt nhất nên gọi API chi tiết của 1 cuốn sách:
            # f"{BOOK_SERVICE_URL}/books/{book_id}/"
            r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
            books = r.json()

            if not any(b["id"] == book_id for b in books):
                return Response(
                    {"error": "Book not found in Book Service"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except requests.exceptions.RequestException:
            return Response(
                {"error": "Cannot connect to Book Service"},
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
