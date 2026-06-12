#!/bin/bash

echo "=== Starting Microservices Store ==="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
export DATABASE_URL="${DATABASE_URL}"

MAX_RETRIES=30
RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
    python /app/docker/wait_for_db.py && break
    RETRY=$((RETRY + 1))
    echo "Retry $RETRY/$MAX_RETRIES..."
    sleep 2
done

if [ $RETRY -eq $MAX_RETRIES ]; then
    echo "ERROR: Could not connect to PostgreSQL after $MAX_RETRIES attempts"
    exit 1
fi

echo "PostgreSQL is ready!"

# Map environment variables for supervisord
export CUSTOMER_DB_URL="${CUSTOMER_DB_URL:-$DATABASE_URL}"
export PRODUCT_DB_URL="${PRODUCT_DB_URL:-$DATABASE_URL}"
export CART_DB_URL="${CART_DB_URL:-$DATABASE_URL}"
export CATALOG_DB_URL="${CATALOG_DB_URL:-$DATABASE_URL}"
export ORDER_DB_URL="${ORDER_DB_URL:-$DATABASE_URL}"
export SHIP_DB_URL="${SHIP_DB_URL:-$DATABASE_URL}"
export PAY_DB_URL="${PAY_DB_URL:-$DATABASE_URL}"
export COMMENT_RATE_DB_URL="${COMMENT_RATE_DB_URL:-$DATABASE_URL}"
export STAFF_DB_URL="${STAFF_DB_URL:-$DATABASE_URL}"
export MANAGER_DB_URL="${MANAGER_DB_URL:-$DATABASE_URL}"
export RECOMMENDER_DB_URL="${RECOMMENDER_DB_URL:-$DATABASE_URL}"

echo "Starting all services with supervisord..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
