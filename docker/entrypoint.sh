#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."

# Wait for PostgreSQL to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$(echo $DATABASE_URL | sed -E 's/.*@([^:]+).*/\1/')" -U "$POSTGRES_USER" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is up - running migrations"
python manage.py migrate --noinput

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8888
