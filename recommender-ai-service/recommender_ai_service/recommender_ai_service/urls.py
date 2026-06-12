"""
URL configuration for recommender_ai_service project.

Gateway routing:
  /api/recommendations/... → recommender-ai-service/recommendations/...
  /api/chat/...            → recommender-ai-service/chat/...
"""

from django.contrib import admin
from django.urls import path
from app.views import (
    RecommendationView,
    SimilarProductsView,
    WishlistView,
    WishlistItemView,
    ChatView,
    ChatHistoryView,
    HealthCheckView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Health check
    path("health/", HealthCheckView.as_view(), name="health-check"),

    # Recommendation endpoints (gateway strips /api/ prefix)
    path("recommendations/<int:customer_id>/", RecommendationView.as_view(), name="recommendations"),
    path("recommendations/similar/<int:product_id>/", SimilarProductsView.as_view(), name="similar-products"),

    # Wishlist endpoints
    path("recommendations/wishlist/", WishlistView.as_view(), name="wishlist-list"),
    path("recommendations/wishlist/<int:customer_id>/<int:product_id>/",
         WishlistItemView.as_view(), name="wishlist-item"),

    # Chat endpoints
    path("chat/", ChatView.as_view(), name="chat"),
    path("chat/<int:conversation_id>/", ChatHistoryView.as_view(), name="chat-history"),
]
