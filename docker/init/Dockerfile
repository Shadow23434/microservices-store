FROM python:3.11-slim

WORKDIR /app

# Install curl and dependencies for seed script
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir psycopg2-binary requests

# Copy seed scripts
COPY scripts/seed_all_services.py /app/
COPY docker/init/entrypoint.sh /app/

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
