FROM python:3.10-slim

# Install supervisor for managing multiple processes
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all service requirements and install dependencies
COPY api-gateway/requirements.txt ./api-gateway/
COPY cart-service/requirements.txt ./cart-service/
COPY catalog-service/requirements.txt ./catalog-service/
COPY comment-rate-service/requirements.txt ./comment-rate-service/
COPY customer-service/requirements.txt ./customer-service/
COPY manager-service/requirements.txt ./manager-service/
COPY order-service/requirements.txt ./order-service/
COPY pay-service/requirements.txt ./pay-service/
COPY product-service/requirements.txt ./product-service/
COPY recommender-ai-service/requirements.txt ./recommender-ai-service/
COPY ship-service/requirements.txt ./ship-service/
COPY staff-service/requirements.txt ./staff-service/

RUN pip install --no-cache-dir \
    -r api-gateway/requirements.txt \
    -r cart-service/requirements.txt \
    -r catalog-service/requirements.txt \
    -r comment-rate-service/requirements.txt \
    -r customer-service/requirements.txt \
    -r manager-service/requirements.txt \
    -r order-service/requirements.txt \
    -r pay-service/requirements.txt \
    -r product-service/requirements.txt \
    -r recommender-ai-service/requirements.txt \
    -r ship-service/requirements.txt \
    -r staff-service/requirements.txt

# Copy wait_for_db script
COPY docker/wait_for_db.py ./docker/

# Copy all service code
COPY api-gateway/api_gateway/ ./api-gateway/api_gateway/
COPY cart-service/cart_service/ ./cart-service/cart_service/
COPY catalog-service/catalog_service/ ./catalog-service/catalog_service/
COPY comment-rate-service/comment_rate_service/ ./comment-rate-service/comment_rate_service/
COPY customer-service/customer_service/ ./customer-service/customer_service/
COPY manager-service/manager_service/ ./manager-service/manager_service/
COPY order-service/order_service/ ./order-service/order_service/
COPY pay-service/pay_service/ ./pay-service/pay_service/
COPY product-service/product_service/ ./product-service/product_service/
COPY recommender-ai-service/recommender_ai_service/ ./recommender-ai-service/recommender_ai_service/
COPY ship-service/ship_service/ ./ship-service/ship_service/
COPY staff-service/staff_service/ ./staff-service/staff_service/

# Copy supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy startup script
COPY start-services.sh /app/
RUN chmod +x /app/start-services.sh

# Expose API Gateway port
EXPOSE 8888

# Start all services
CMD ["/app/start-services.sh"]
