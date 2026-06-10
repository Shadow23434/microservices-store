FROM python:3.10-slim
WORKDIR /app
COPY book-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY docker/wait_for_db.py .
COPY book-service/book_service/ .
CMD ["sh", "-c", "python wait_for_db.py && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8888"]
