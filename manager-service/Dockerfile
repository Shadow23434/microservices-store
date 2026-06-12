FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wait_for_db.py .
COPY manager_service/ .
CMD ["sh", "-c", "python wait_for_db.py && python manage.py migrate --noinput && gunicorn manager_service.wsgi:application --bind 0.0.0.0:8888 --workers 2 --timeout 120"]