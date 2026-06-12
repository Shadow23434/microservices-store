import os
import requests
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

SERVICES = {
    "customers": os.environ.get("CUSTOMER_SERVICE_URL", "http://localhost:8881"),
    "products": os.environ.get("PRODUCT_SERVICE_URL", "http://localhost:8882"),
    "carts": os.environ.get("CART_SERVICE_URL", "http://localhost:8883"),
    "catalog": os.environ.get("CATALOG_SERVICE_URL", "http://localhost:8884"),
    "orders": os.environ.get("ORDER_SERVICE_URL", "http://localhost:8885"),
    "shipments": os.environ.get("SHIP_SERVICE_URL", "http://localhost:8886"),
    "payments": os.environ.get("PAY_SERVICE_URL", "http://localhost:8887"),
    "reviews": os.environ.get(
        "COMMENT_RATE_SERVICE_URL", "http://localhost:8888"
    ),
    "staff": os.environ.get("STAFF_SERVICE_URL", "http://localhost:8889"),
    "managers": os.environ.get("MANAGER_SERVICE_URL", "http://localhost:8890"),
    "recommender": os.environ.get(
        "RECOMMENDER_SERVICE_URL", "http://localhost:8891"
    ),
    "chat": os.environ.get(
        "RECOMMENDER_SERVICE_URL", "http://localhost:8891"
    ),
}


#  Template Views


class RootView(APIView):
    def get(self, request):
        return render(request, "dashboard.html")


def product_list(request):
    product_type = request.GET.get("product_type", "")
    url = f"{SERVICES['products']}/api/products/"
    if product_type:
        url += f"?product_type={product_type}"
    try:
        r = requests.get(url, timeout=5)
        response_data = r.json()
        products = response_data.get("results", response_data) if isinstance(response_data, dict) else response_data
    except Exception:
        products = []
    return render(request, "products.html", {"products": products, "product_type": product_type})


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
    # Always forward Content-Type header to ensure downstream services
    # (e.g. DRF) can correctly parse the request body
    content_type = request.META.get("CONTENT_TYPE", "")
    headers = {}
    if content_type:
        # Đảm bảo charset=utf-8 để downstream service decode đúng tiếng Việt
        if "json" in content_type and "charset" not in content_type.lower():
            content_type = f"{content_type}; charset=utf-8"
        headers["Content-Type"] = content_type
    try:
        # Tăng timeout lên 120s cho các request cần gọi LLM API (chat, recommendations)
        timeout = 120 if "chat" in url or "recommendations" in url else 10
        resp = getattr(requests, method)(
            url, data=raw_body, headers=headers, params=request.GET, timeout=timeout
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
        # Only product-service uses /api/ prefix; all others mount at root
        if resource == "products":
            full_path = f"api/products/{path}" if path else "api/products/"
        else:
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
        # Define correct health check URLs for each service
        health_endpoints = {
            "customers": f"{SERVICES['customers']}/customers/",
            "products": f"{SERVICES['products']}/api/products/",
            "carts": f"{SERVICES['carts']}/carts/1/",
            "staff": f"{SERVICES['staff']}/staff/",
            "managers": f"{SERVICES['managers']}/managers/",
            "categories": f"{SERVICES['categories']}/categories/",
            "orders": f"{SERVICES['orders']}/orders/",
            "shipments": f"{SERVICES['shipments']}/shipments/",
            "payments": f"{SERVICES['payments']}/payments/",
            "reviews": f"{SERVICES['reviews']}/reviews/",
            "recommendations": f"{SERVICES['recommendations']}/recommendations/1/",
        }
        results = {}
        for name, endpoint in health_endpoints.items():
            try:
                resp = requests.get(endpoint, timeout=5)
                # Any HTTP response (even 4xx/5xx) means the service is UP
                # — Django is running and processing requests.
                # Only connection failure / timeout means truly DOWN.
                results[name] = "up"
            except requests.exceptions.RequestException:
                results[name] = "down"
        overall = "healthy" if all(v == "up" for v in results.values()) else "degraded"
        return Response({"status": overall, "services": results})
