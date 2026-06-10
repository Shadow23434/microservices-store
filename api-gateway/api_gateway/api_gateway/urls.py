"""
URL configuration for api_gateway project.

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

from django.urls import path, re_path
from app.views import (
    GatewayView,
    HealthCheck,
    RootView,
    book_list,
    view_cart,
    customers_page,
    orders_page,
    staff_page,
    payments_page,
    shipments_page,
    reviews_page,
)

urlpatterns = [
    path("", RootView.as_view(), name="root"),
    path("health/", HealthCheck.as_view(), name="health-check"),
    # Template pages
    path("books/", book_list, name="book-list"),
    path("customers/", customers_page, name="customers-page"),
    path("orders/", orders_page, name="orders-page"),
    path("staff-page/", staff_page, name="staff-page"),
    path("payments-page/", payments_page, name="payments-page"),
    path("shipments-page/", shipments_page, name="shipments-page"),
    path("reviews-page/", reviews_page, name="reviews-page"),
    path("cart/<int:customer_id>/", view_cart, name="view-cart"),
    re_path(
        r"^api/(?P<resource>[\w-]+)/(?P<path>.*)$",
        GatewayView.as_view(),
        name="gateway",
    ),
]
