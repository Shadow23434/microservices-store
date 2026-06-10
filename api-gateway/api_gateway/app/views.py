import os
import requests
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

SERVICES = {
    "customers": os.environ.get("CUSTOMER_SERVICE_URL", "http://customer-service:8888"),
    "books": os.environ.get("BOOK_SERVICE_URL", "http://book-service:8888"),
    "carts": os.environ.get("CART_SERVICE_URL", "http://cart-service:8888"),
    "staff": os.environ.get("STAFF_SERVICE_URL", "http://staff-service:8888"),
    "managers": os.environ.get("MANAGER_SERVICE_URL", "http://manager-service:8888"),
    "categories": os.environ.get("CATALOG_SERVICE_URL", "http://catalog-service:8888"),
    "orders": os.environ.get("ORDER_SERVICE_URL", "http://order-service:8888"),
    "shipments": os.environ.get("SHIP_SERVICE_URL", "http://ship-service:8888"),
    "payments": os.environ.get("PAY_SERVICE_URL", "http://pay-service:8888"),
    "reviews": os.environ.get(
        "COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8888"
    ),
    "recommendations": os.environ.get(
        "RECOMMENDER_SERVICE_URL", "http://recommender-ai-service:8888"
    ),
}


#  Template Views


class RootView(APIView):
    def get(self, request):
        return render(request, "dashboard.html")


def book_list(request):
    try:
        r = requests.get(f"{SERVICES['books']}/books/", timeout=5)
        books = r.json()
    except Exception:
        books = []
    return render(request, "books.html", {"books": books})


def customers_page(request):
    return render(request, "customers.html")


def orders_page(request):
    return render(request, "orders.html")


def staff_page(request):
    return render(request, "staff.html")


def payments_page(request):
    return render(request, "payments.html")


def shipments_page(request):
    return render(request, "shipments.html")


def reviews_page(request):
    return render(request, "reviews.html")


def view_cart(request, customer_id):
    try:
        r = requests.get(f"{SERVICES['carts']}/carts/{customer_id}/", timeout=5)
        data = r.json()
        items = data if isinstance(data, list) else data.get("items", [])
    except Exception:
        items = []
    return render(request, "cart.html", {"items": items, "customer_id": customer_id})


#  API Proxy


def _proxy(request, service_url, path):
    url = f"{service_url}/{path}"
    method = request.method.lower()
    raw_body = request.body or None
    headers = {}
    content_type = request.content_type or ""
    if raw_body and content_type:
        headers["Content-Type"] = content_type
    try:
        resp = getattr(requests, method)(
            url, data=raw_body, headers=headers, params=request.GET, timeout=10
        )
        if resp.status_code == 204 or not resp.content:
            return JsonResponse({}, status=resp.status_code)
        try:
            return JsonResponse(resp.json(), status=resp.status_code, safe=False)
        except ValueError:
            return JsonResponse({}, status=resp.status_code)
    except requests.exceptions.ConnectionError:
        return JsonResponse(
            {"error": f"Service unavailable: {service_url}"}, status=503
        )
    except requests.exceptions.Timeout:
        return JsonResponse({"error": "Service timeout"}, status=504)


class GatewayView(APIView):
    def dispatch(self, request, resource, path="", *args, **kwargs):
        if resource not in SERVICES:
            return JsonResponse(
                {"error": f"Unknown resource: {resource}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        base_url = SERVICES[resource]
        full_path = f"{resource}/{path}" if path else f"{resource}/"
        return _proxy(request, base_url, full_path)

    def get(self, request, resource, path=""):
        return self.dispatch(request, resource, path)

    def post(self, request, resource, path=""):
        return self.dispatch(request, resource, path)

    def put(self, request, resource, path=""):
        return self.dispatch(request, resource, path)

    def patch(self, request, resource, path=""):
        return self.dispatch(request, resource, path)

    def delete(self, request, resource, path=""):
        return self.dispatch(request, resource, path)


class HealthCheck(APIView):
    def get(self, request):
        results = {}
        for name, url in SERVICES.items():
            try:
                resp = requests.get(f"{url}/{name}/", timeout=3)
                results[name] = "up" if resp.status_code < 500 else "degraded"
            except requests.exceptions.RequestException:
                results[name] = "down"
        overall = "healthy" if all(v == "up" for v in results.values()) else "degraded"
        return Response({"status": overall, "services": results})
