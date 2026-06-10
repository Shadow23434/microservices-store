"""
URL configuration for comment_rate_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from app.views import ReviewListCreate, ReviewDetail, BookAverageRating

urlpatterns = [
    path("admin/", admin.site.urls),
    path("reviews/", ReviewListCreate.as_view(), name="review-list-create"),
    path("reviews/<int:pk>/", ReviewDetail.as_view(), name="review-detail"),
    path(
        "reviews/book/<int:book_id>/rating/",
        BookAverageRating.as_view(),
        name="book-avg-rating",
    ),
]
