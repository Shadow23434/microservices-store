#!/bin/bash
# run_migrations.sh
# Script to run Django migrations for all services via Docker Compose

set -e

services=(
    "customer-service"
    "book-service"
    "cart-service"
    "staff-service"
    "manager-service"
    "catalog-service"
    "order-service"
    "ship-service"
    "pay-service"
    "comment-rate-service"
    "recommender-ai-service"
    "api-gateway"
)

echo "=== Running migrations for all services ==="

for svc in "${services[@]}"; do
    echo "--- Migrating $svc ---"
    docker compose exec "$svc" python manage.py migrate --noinput
done

echo "=== All migrations completed successfully ==="