from rest_framework import serializers
from .models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    book_ids = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = ["id", "customer_id", "book_ids", "updated_at"]

    def get_book_ids(self, obj):
        return obj.get_book_ids()
