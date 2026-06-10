#!/bin/bash
set -e

echo "==================================="
echo "Waiting for services to be ready..."
echo "==================================="

# Wait for API gateway to be responsive (ensures all services are up)
MAX_RETRIES=60
RETRY_COUNT=0

until curl -f http://api-gateway:8888/health/ -m 5 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "ERROR: API Gateway did not become healthy in time"
        exit 1
    fi
    echo "Waiting for API Gateway... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
done

echo ""
echo "==================================="
echo "All services are ready!"
echo "Running seed script..."
echo "==================================="
echo ""

# Run the seed script
python /app/seed_all_services.py

echo ""
echo "==================================="
echo "Seeding completed successfully!"
echo "==================================="
