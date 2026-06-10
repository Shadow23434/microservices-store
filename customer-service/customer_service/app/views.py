import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Customer
from .serializers import CustomerSerializer

# Docker: http://cart-service:8000 | Local: http://127.0.0.1:8003
CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://cart-service:8000")


class CustomerDetail(APIView):
    """API hỗ trợ Xem chi tiết và Xóa một khách hàng."""

    def _get_object(self, pk):
        try:
            return Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return None

    def get(self, request, pk):
        customer = self._get_object(pk)
        if not customer:
            return Response({"error": "Not found"}, status=404)
        return Response(CustomerSerializer(customer).data)

    def put(self, request, pk):
        customer = self._get_object(pk)
        if not customer:
            return Response({"error": "Not found"}, status=404)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        customer = self._get_object(pk)
        if not customer:
            return Response({"error": "Not found"}, status=404)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        customer = self._get_object(pk)
        if not customer:
            return Response({"error": "Not found"}, status=404)
        customer.delete()
        return Response(status=204)


class CustomerListCreate(APIView):
    """
    API hỗ trợ Lấy danh sách khách hàng và Tạo khách hàng mới.
    """

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)

        if serializer.is_valid():
            customer = serializer.save()

            # Gọi sang cart-service để tạo giỏ hàng cho khách hàng mới
            try:
                requests.post(
                    f"{CART_SERVICE_URL}/carts/",
                    json={"customer_id": customer.id},
                    timeout=5,  # Nên có timeout để tránh treo hệ thống nếu service kia sập
                )
            except requests.exceptions.RequestException as e:
                # Log lỗi nếu không gọi được sang cart-service
                print(f"Error calling cart-service: {e}")

            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
