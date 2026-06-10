from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Review
from .serializers import ReviewSerializer


class ReviewListCreate(APIView):
    def get(self, request):
        book_id = request.query_params.get("book_id")
        customer_id = request.query_params.get("customer_id")
        reviews = Review.objects.all()
        if book_id:
            reviews = reviews.filter(book_id=book_id)
        if customer_id:
            reviews = reviews.filter(customer_id=customer_id)
        return Response(ReviewSerializer(reviews, many=True).data)

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetail(APIView):
    def get_object(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return None

    def get(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response(
                {"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(ReviewSerializer(review).data)

    def put(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response(
                {"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = self.get_object(pk)
        if not review:
            return Response(
                {"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND
            )
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookAverageRating(APIView):
    """Tinh diem trung binh cua mot cuon sach"""

    def get(self, request, book_id):
        reviews = Review.objects.filter(book_id=book_id)
        if not reviews.exists():
            return Response(
                {"book_id": book_id, "average_rating": None, "total_reviews": 0}
            )
        avg = sum(r.rating for r in reviews) / reviews.count()
        return Response(
            {
                "book_id": book_id,
                "average_rating": round(avg, 2),
                "total_reviews": reviews.count(),
            }
        )
