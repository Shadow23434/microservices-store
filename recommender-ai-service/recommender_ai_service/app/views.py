import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recommendation
from .serializers import RecommendationSerializer

# Docker: http://book-service:8000 | Local: http://127.0.0.1:8002
BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://book-service:8000")
# Docker: http://comment-rate-service:8000 | Local: http://127.0.0.1:8010
COMMENT_RATE_SERVICE_URL = os.environ.get(
    "COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8000"
)


class RecommendationView(APIView):
    def get(self, request, customer_id):
        rec, _ = Recommendation.objects.get_or_create(customer_id=customer_id)

        # Goi sang comment-rate-service de lay sach khach da danh gia cao (>= 4 sao)
        try:
            r = requests.get(
                f"{COMMENT_RATE_SERVICE_URL}/reviews/?customer_id={customer_id}",
                timeout=5,
            )
            reviews = r.json()
            liked_book_ids = [
                rv["book_id"] for rv in reviews if rv.get("rating", 0) >= 4
            ]
        except requests.exceptions.RequestException:
            liked_book_ids = []

        # Goi sang book-service lay tat ca sach
        try:
            r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=5)
            all_books = r.json()
            # Goi y cac sach chua duoc danh gia (don gian nhat)
            recommended = [b for b in all_books if b["id"] not in liked_book_ids][:5]
            rec.set_book_ids([b["id"] for b in recommended])
            rec.save()
        except requests.exceptions.RequestException:
            recommended = []

        return Response(
            {
                "customer_id": customer_id,
                "recommended_books": recommended,
            }
        )
