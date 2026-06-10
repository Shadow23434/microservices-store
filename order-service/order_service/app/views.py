import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer

PAY_SERVICE_URL = os.environ.get("PAY_SERVICE_URL", "http://pay-service:8000")
SHIP_SERVICE_URL = os.environ.get("SHIP_SERVICE_URL", "http://ship-service:8000")


class OrderListCreate(APIView):
    def get(self, request):
        customer_id = request.query_params.get("customer_id")
        orders = (
            Order.objects.filter(customer_id=customer_id)
            if customer_id
            else Order.objects.all()
        )
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        items_data = request.data.get("items", [])

        # Build order data — auto-calculate total_amount from items if provided
        order_data = {
            "customer_id": request.data.get("customer_id"),
            "shipping_address": request.data.get("shipping_address", ""),
            "status": request.data.get("status", "pending"),
        }
        if items_data:
            order_data["total_amount"] = sum(
                float(item.get("unit_price", 0)) * int(item.get("quantity", 1))
                for item in items_data
            )
        else:
            order_data["total_amount"] = request.data.get("total_amount", 0)

        serializer = OrderSerializer(data=order_data)
        if serializer.is_valid():
            order = serializer.save()

            # Tao cac san pham trong don hang
            for item in items_data:
                OrderItem.objects.create(
                    order=order,
                    book_id=int(item["book_id"]),
                    quantity=int(item.get("quantity", 1)),
                    unit_price=float(item["unit_price"]),
                )

            # Tao payment cho don hang
            try:
                requests.post(
                    f"{PAY_SERVICE_URL}/payments/",
                    json={
                        "order_id": order.id,
                        "customer_id": order.customer_id,
                        "amount": str(order.total_amount),
                        "method": request.data.get("payment_method", "credit_card"),
                    },
                    timeout=5,
                )
            except requests.exceptions.RequestException:
                pass  # Log loi, khong chặn tao order

            # Tao shipment cho don hang
            try:
                requests.post(
                    f"{SHIP_SERVICE_URL}/shipments/",
                    json={
                        "order_id": order.id,
                        "customer_id": order.customer_id,
                        "address": request.data.get("shipping_address", ""),
                    },
                    timeout=5,
                )
            except requests.exceptions.RequestException:
                pass

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(APIView):
    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(OrderSerializer(order).data)

    def patch(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderItemCreate(APIView):
    def post(self, request):
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            # Cap nhat tong tien order
            order = item.order
            total = sum(i.unit_price * i.quantity for i in order.items.all())
            order.total_amount = total
            order.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
