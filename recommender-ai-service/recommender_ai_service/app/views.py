import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recommendation
from .serializers import RecommendationSerializer

# Docker: http://product-service:8888 | Local: http://127.0.0.1:8888
PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://product-service:8888")
# Docker: http://comment-rate-service:8000 | Local: http://127.0.0.1:8010
COMMENT_RATE_SERVICE_URL = os.environ.get(
    "COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8000"
)


class RecommendationView(APIView):
    def get(self, request, customer_id):
        rec, _ = Recommendation.objects.get_or_create(customer_id=customer_id)

        # Goi sang comment-rate-service de lay san pham khach da danh gia cao (>= 4 sao)
        try:
            r = requests.get(
                f"{COMMENT_RATE_SERVICE_URL}/reviews/?customer_id={customer_id}",
                timeout=5,
            )
            reviews = r.json()
            liked_product_ids = [
                rv["product_id"] for rv in reviews if rv.get("rating", 0) >= 4
            ]
        except requests.exceptions.RequestException:
            liked_product_ids = []

        # Goi sang product-service lay tat ca san pham
        try:
            r = requests.get(f"{PRODUCT_SERVICE_URL}/api/products/", timeout=5)
            response_data = r.json()
            all_products = response_data.get("results", response_data) if isinstance(response_data, dict) else response_data
            # Goi y cac san pham chua duoc danh gia (don gian nhat)
            recommended = [p for p in all_products if p["id"] not in liked_product_ids][:5]
            rec.set_book_ids([p["id"] for p in recommended])
            rec.save()
        except requests.exceptions.RequestException:
            recommended = []

        return Response(
            {
                "customer_id": customer_id,
                "recommended_products": recommended,
            }
        )
