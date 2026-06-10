from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Shipment
from .serializers import ShipmentSerializer


class ShipmentListCreate(APIView):
    def get(self, request):
        order_id = request.query_params.get("order_id")
        shipments = (
            Shipment.objects.filter(order_id=order_id)
            if order_id
            else Shipment.objects.all()
        )
        return Response(ShipmentSerializer(shipments, many=True).data)

    def post(self, request):
        serializer = ShipmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShipmentDetail(APIView):
    def get_object(self, pk):
        try:
            return Shipment.objects.get(pk=pk)
        except Shipment.DoesNotExist:
            return None

    def get(self, request, pk):
        shipment = self.get_object(pk)
        if not shipment:
            return Response(
                {"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(ShipmentSerializer(shipment).data)

    def patch(self, request, pk):
        shipment = self.get_object(pk)
        if not shipment:
            return Response(
                {"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ShipmentSerializer(shipment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
