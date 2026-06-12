from rest_framework import serializers
from .models import Recommendation, WishlistItem, Conversation, ChatMessage


class RecommendationSerializer(serializers.ModelSerializer):
    product_ids = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = ["id", "customer_id", "product_ids", "algorithm", "reason", "updated_at"]

    def get_product_ids(self, obj):
        return obj.get_product_ids()


class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ["id", "customer_id", "product_id", "added_at"]
        read_only_fields = ["id", "added_at"]


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "customer_id", "session_id", "created_at", "updated_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "conversation", "role", "content", "product_ids", "created_at"]


class ChatRequestSerializer(serializers.Serializer):
    """Serializer cho request body của POST /api/chat/"""
    message = serializers.CharField(max_length=2000)
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    session_id = serializers.CharField(required=False, allow_blank=True, default="")
