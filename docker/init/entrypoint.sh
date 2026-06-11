#!/bin/bash
set -e

echo "==================================="
echo "Waiting for services to be ready..."
echo "==================================="

# Wait for API gateway and all services to be healthy
MAX_RETRIES=90
RETRY_COUNT=0

while true; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "ERROR: Services did not become healthy in time"
        echo "Last health check response:"
        curl -s http://api-gateway:8888/health/ || true
        exit 1
    fi

    # Check if API Gateway is responsive
    HTTP_CODE=$(curl -s -o /tmp/health.json -w "%{http_code}" http://api-gateway:8888/health/ -m 10 2>/dev/null || true)

    # If curl failed entirely, normalize to "000"
    if [ -z "$HTTP_CODE" ] || [ ${#HTTP_CODE} -gt 3 ]; then
        HTTP_CODE="000"
    fi

    if [ "$HTTP_CODE" = "200" ]; then
        # Parse JSON response to check if status is "healthy"
        STATUS=$(cat /tmp/health.json | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "unknown")

        if [ "$STATUS" = "healthy" ]; then
            echo ""
            echo "✓ All services are healthy!"
            break
        else
            echo "Waiting for services to be healthy... ($RETRY_COUNT/$MAX_RETRIES) - Status: $STATUS"
            # Show which services are down
            cat /tmp/health.json | python3 -c "import sys, json; data=json.load(sys.stdin); down=[k for k,v in data.get('services',{}).items() if v=='down']; print(f'  Down: {down}') if down else None" 2>/dev/null || true
        fi
    else
        echo "Waiting for API Gateway... ($RETRY_COUNT/$MAX_RETRIES) - HTTP $HTTP_CODE"
    fi

    sleep 3
done

echo ""
echo "==================================="
echo "All services are ready!"
echo "Waiting 5 seconds for services to stabilize..."
echo "==================================="
sleep 5
echo ""
echo "Running seed script..."
echo ""

# Run the seed script
python /app/seed_all_services.py

echo ""
echo "==================================="
echo "Seeding completed successfully!"
echo "==================================="
