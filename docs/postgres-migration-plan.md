# Kế hoạch tích hợp PostgreSQL cho `microservices-bookstore`

> **Repo:** [Shadow23434/microservices-bookstore](https://github.com/Shadow23434/microservices-bookstore)  
> **Mục tiêu:** Thay thế toàn bộ SQLite (bind-mount) bằng PostgreSQL chạy trong Docker  
> **Ngày lập kế hoạch:** 2026-06-10

---

## Mục lục

1. [Tổng quan hiện trạng](#1-tổng-quan-hiện-trạng)
2. [Lý do chuyển sang PostgreSQL](#2-lý-do-chuyển-sang-postgresql)
3. [Kiến trúc DB sau khi migration](#3-kiến-trúc-db-sau-khi-migration)
4. [Danh sách thay đổi theo từng lớp](#4-danh-sách-thay-đổi-theo-từng-lớp)
5. [Hướng dẫn thực hiện chi tiết](#5-hướng-dẫn-thực-hiện-chi-tiết)
   - [Bước 1 – Cập nhật `docker-compose.yml`](#bước-1--cập-nhật-docker-composeyml)
   - [Bước 2 – Thêm `psycopg2-binary` vào `requirements.txt`](#bước-2--thêm-psycopg2-binary-vào-requirementstxt)
   - [Bước 3 – Sửa `settings.py` từng service](#bước-3--sửa-settingspy-từng-service)
   - [Bước 4 – Cập nhật `Dockerfile` (healthcheck & wait)](#bước-4--cập-nhật-dockerfile-healthcheck--wait)
   - [Bước 5 – Cập nhật script `seed_data` & `run_migrations`](#bước-5--cập-nhật-script-seed_data--run_migrations)
   - [Bước 6 – Migrate dữ liệu từ SQLite sang PostgreSQL](#bước-6--migrate-dữ-liệu-từ-sqlite-sang-postgresql)
6. [File `.env` quản lý credentials](#6-file-env-quản-lý-credentials)
7. [Checklist kiểm thử](#7-checklist-kiểm-thử)
8. [Rollback plan](#8-rollback-plan)
9. [Lưu ý vận hành](#9-lưu-ý-vận-hành)

---

## 1. Tổng quan hiện trạng

Hệ thống hiện tại gồm **12 Django service** + 1 React frontend, mỗi service dùng một file `db.sqlite3` riêng được bind-mount từ máy host vào container:

| Service | SQLite path (host) |
|---|---|
| `api-gateway` | `./api-gateway/api_gateway/db.sqlite3` |
| `customer-service` | `./customer-service/customer_service/db.sqlite3` |
| `book-service` | `./book-service/book_service/db.sqlite3` |
| `cart-service` | `./cart-service/cart_service/db.sqlite3` |
| `staff-service` | `./staff-service/staff_service/db.sqlite3` |
| `manager-service` | `./manager-service/manager_service/db.sqlite3` |
| `catalog-service` | `./catalog-service/catalog_service/db.sqlite3` |
| `order-service` | `./order-service/order_service/db.sqlite3` |
| `ship-service` | `./ship-service/ship_service/db.sqlite3` |
| `pay-service` | `./pay-service/pay_service/db.sqlite3` |
| `comment-rate-service` | `./comment-rate-service/comment_rate_service/db.sqlite3` |
| `recommender-ai-service` | `./recommender-ai-service/recommender_ai_service/db.sqlite3` |

---

## 2. Lý do chuyển sang PostgreSQL

| Tiêu chí | SQLite | PostgreSQL |
|---|---|---|
| Concurrent writes | ❌ File-lock, chỉ 1 writer tại 1 thời điểm | ✅ MVCC, nhiều writer đồng thời |
| Production-ready | ❌ Không phù hợp deploy thật | ✅ Tiêu chuẩn production |
| Scaling / Replica | ❌ Không hỗ trợ | ✅ Read-replica, streaming replication |
| Connection pooling | ❌ | ✅ PgBouncer, built-in |
| Full-text search | Hạn chế | ✅ `tsvector`, `GIN` index |
| JSON / JSONB | Cơ bản | ✅ JSONB với indexing mạnh |
| Migrations an toàn | Một số DDL bị hạn chế | ✅ Đầy đủ DDL |
| `recommender-ai-service` | Không dùng được `pgvector` | ✅ Tích hợp `pgvector` sau này |

---

## 3. Kiến trúc DB sau khi migration

Có 2 phương án. **Phương án B** được khuyến nghị cho dự án này.

### Phương án A – Mỗi service một PostgreSQL container riêng

```
customer-service  →  postgres-customer  (db: customer_db)
book-service      →  postgres-book      (db: book_db)
...
```

Ưu điểm: cô lập hoàn toàn theo microservice pattern thuần túy.  
Nhược điểm: 12 container PostgreSQL, tốn RAM (~150 MB × 12 ≈ 1.8 GB) – nặng cho môi trường dev.

### Phương án B – Một PostgreSQL container, 12 database riêng biệt ✅ (khuyến nghị)

```
                    ┌─────────────────────────────┐
                    │  postgres (single container) │
                    │  port: 5432                  │
                    │  ├── customer_db             │
                    │  ├── book_db                 │
                    │  ├── cart_db                 │
                    │  ├── staff_db                │
                    │  ├── manager_db              │
                    │  ├── catalog_db              │
                    │  ├── order_db                │
                    │  ├── ship_db                 │
                    │  ├── pay_db                  │
                    │  ├── comment_rate_db         │
                    │  ├── recommender_db          │
                    │  └── gateway_db              │
                    └─────────────────────────────┘
```

Ưu điểm: chỉ 1 container, dễ quản lý, vẫn giữ tách biệt data logic (khác database, khác user nếu muốn).  
Nhược điểm: chia sẻ tài nguyên – chấp nhận được ở môi trường dev/staging.

**Kế hoạch này thực hiện theo Phương án B.**

---

## 4. Danh sách thay đổi theo từng lớp

| File | Thay đổi |
|---|---|
| `docker-compose.yml` | Thêm service `postgres`, xóa `volumes` SQLite, thêm env `DATABASE_URL` / `DB_*`, thêm `depends_on: postgres` |
| `<service>/requirements.txt` | Thêm `psycopg2-binary>=2.9` (hoặc `psycopg[binary]>=3.1` nếu muốn psycopg3) |
| `<service>/<project>/settings.py` | Đổi `DATABASES` từ SQLite sang PostgreSQL, đọc từ env |
| `<service>/Dockerfile` | Thêm `wait-for-it.sh` hoặc dùng `depends_on.condition: service_healthy` |
| `run_migrations.ps1` / `.sh` | Thêm logic tạo DB PostgreSQL thay vì SQLite |
| `seed_data.ps1` / `.sh` | Thay `sqlite3` CLI bằng `psql` hoặc Django fixtures |
| `.env` (mới) | Tập trung credentials DB |
| `.gitignore` | Thêm `.env` |

---

## 5. Hướng dẫn thực hiện chi tiết

### Bước 1 – Cập nhật `docker-compose.yml`

Thay toàn bộ nội dung `docker-compose.yml` bằng phiên bản sau:

```yaml
# docker-compose.yml
name: microservice

services:

  # ─────────────────────────────────────────────
  # PostgreSQL – shared instance, 12 databases
  # ─────────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    container_name: postgres
    restart: unless-stopped
    env_file: .env
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      # Tạo tất cả database khi khởi động lần đầu
      POSTGRES_MULTIPLE_DATABASES: >
        customer_db,book_db,cart_db,staff_db,manager_db,
        catalog_db,order_db,ship_db,pay_db,
        comment_rate_db,recommender_db,gateway_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init-multiple-db.sh:/docker-entrypoint-initdb.d/init-multiple-db.sh:ro
    ports:
      - "5432:5432"        # expose để dùng psql từ host khi debug
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
      retries: 10

  # ─────────────────────────────────────────────
  # Application services
  # ─────────────────────────────────────────────
  customer-service:
    build: ./customer-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/customer_db
      CART_SERVICE_URL: http://cart-service:8888
    depends_on:
      postgres:
        condition: service_healthy
      cart-service:
        condition: service_started

  book-service:
    build: ./book-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/book_db
    depends_on:
      postgres:
        condition: service_healthy

  cart-service:
    build: ./cart-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/cart_db
      BOOK_SERVICE_URL: http://book-service:8888
    depends_on:
      postgres:
        condition: service_healthy
      book-service:
        condition: service_started

  staff-service:
    build: ./staff-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/staff_db
    depends_on:
      postgres:
        condition: service_healthy

  manager-service:
    build: ./manager-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/manager_db
    depends_on:
      postgres:
        condition: service_healthy

  catalog-service:
    build: ./catalog-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/catalog_db
    depends_on:
      postgres:
        condition: service_healthy

  order-service:
    build: ./order-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/order_db
      PAY_SERVICE_URL: http://pay-service:8888
      SHIP_SERVICE_URL: http://ship-service:8888
    depends_on:
      postgres:
        condition: service_healthy
      pay-service:
        condition: service_started
      ship-service:
        condition: service_started

  ship-service:
    build: ./ship-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/ship_db
    depends_on:
      postgres:
        condition: service_healthy

  pay-service:
    build: ./pay-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/pay_db
    depends_on:
      postgres:
        condition: service_healthy

  comment-rate-service:
    build: ./comment-rate-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/comment_rate_db
    depends_on:
      postgres:
        condition: service_healthy

  recommender-ai-service:
    build: ./recommender-ai-service
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/recommender_db
      BOOK_SERVICE_URL: http://book-service:8888
      COMMENT_RATE_SERVICE_URL: http://comment-rate-service:8888
    depends_on:
      postgres:
        condition: service_healthy
      book-service:
        condition: service_started
      comment-rate-service:
        condition: service_started

  api-gateway:
    build: ./api-gateway
    ports:
      - "8888:8888"
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/gateway_db
      CUSTOMER_SERVICE_URL: http://customer-service:8888
      BOOK_SERVICE_URL: http://book-service:8888
      CART_SERVICE_URL: http://cart-service:8888
      STAFF_SERVICE_URL: http://staff-service:8888
      MANAGER_SERVICE_URL: http://manager-service:8888
      CATALOG_SERVICE_URL: http://catalog-service:8888
      ORDER_SERVICE_URL: http://order-service:8888
      SHIP_SERVICE_URL: http://ship-service:8888
      PAY_SERVICE_URL: http://pay-service:8888
      COMMENT_RATE_SERVICE_URL: http://comment-rate-service:8888
      RECOMMENDER_SERVICE_URL: http://recommender-ai-service:8888
    depends_on:
      postgres:
        condition: service_healthy
      customer-service:
        condition: service_started
      book-service:
        condition: service_started
      cart-service:
        condition: service_started
      staff-service:
        condition: service_started
      manager-service:
        condition: service_started
      catalog-service:
        condition: service_started
      order-service:
        condition: service_started
      ship-service:
        condition: service_started
      pay-service:
        condition: service_started
      comment-rate-service:
        condition: service_started
      recommender-ai-service:
        condition: service_started

volumes:
  postgres_data:
    driver: local
```

> **Lưu ý quan trọng:** Xóa toàn bộ các dòng `volumes: - ./*/db.sqlite3:/app/db.sqlite3` cũ, thay bằng `postgres_data` volume ở trên.

---

### Bước 1b – Tạo script khởi tạo nhiều database

Tạo thư mục và file `docker/postgres/init-multiple-db.sh`:

```bash
#!/bin/bash
# docker/postgres/init-multiple-db.sh
# Tự động tạo các database được liệt kê trong POSTGRES_MULTIPLE_DATABASES

set -e

function create_database() {
    local database=$1
    echo "  Creating database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRES_USER;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
        db_trimmed=$(echo "$db" | xargs)  # trim whitespace
        create_database "$db_trimmed"
    done
    echo "Multiple databases created."
fi
```

```bash
chmod +x docker/postgres/init-multiple-db.sh
```

---

### Bước 2 – Thêm `psycopg2-binary` vào `requirements.txt`

Thực hiện cho **tất cả 12 service**. Mở `requirements.txt` của mỗi service và thêm:

```text
psycopg2-binary>=2.9.9
dj-database-url>=2.1.0
```

`dj-database-url` giúp parse `DATABASE_URL` env thành dict Django DATABASES – giảm code lặp.

Ví dụ file `book-service/requirements.txt` sau khi chỉnh:

```text
Django>=4.2,<5.0
djangorestframework>=3.14
psycopg2-binary>=2.9.9
dj-database-url>=2.1.0
# ... các package hiện tại khác giữ nguyên
```

> **Nếu đang dùng Python 3.12+** và muốn psycopg3: dùng `psycopg[binary]>=3.1` thay cho `psycopg2-binary`.

---

### Bước 3 – Sửa `settings.py` từng service

Áp dụng **cùng một pattern** cho tất cả 12 service. Mở file `settings.py` (thường ở `<service>/<django_project>/settings.py`) và thay khối `DATABASES`:

**Trước (SQLite):**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Sau (PostgreSQL qua `DATABASE_URL`):**

```python
import os
import dj_database_url

# Đọc DATABASE_URL từ environment, fallback về SQLite khi chạy local không có Docker
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    f"sqlite:///{BASE_DIR / 'db.sqlite3'}"  # fallback cho local dev
)

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,          # persistent connections
        conn_health_checks=True,   # tự reconnect nếu connection bị đứt
    )
}
```

Bảng tương ứng service ↔ `DATABASE_URL`:

| Service | `DATABASE_URL` (trong Docker) |
|---|---|
| `api-gateway` | `postgresql://bookstore:secret@postgres:5432/gateway_db` |
| `customer-service` | `postgresql://bookstore:secret@postgres:5432/customer_db` |
| `book-service` | `postgresql://bookstore:secret@postgres:5432/book_db` |
| `cart-service` | `postgresql://bookstore:secret@postgres:5432/cart_db` |
| `staff-service` | `postgresql://bookstore:secret@postgres:5432/staff_db` |
| `manager-service` | `postgresql://bookstore:secret@postgres:5432/manager_db` |
| `catalog-service` | `postgresql://bookstore:secret@postgres:5432/catalog_db` |
| `order-service` | `postgresql://bookstore:secret@postgres:5432/order_db` |
| `ship-service` | `postgresql://bookstore:secret@postgres:5432/ship_db` |
| `pay-service` | `postgresql://bookstore:secret@postgres:5432/pay_db` |
| `comment-rate-service` | `postgresql://bookstore:secret@postgres:5432/comment_rate_db` |
| `recommender-ai-service` | `postgresql://bookstore:secret@postgres:5432/recommender_db` |

> Thực tế `user/password` đọc từ `.env`, không hard-code vào code.

---

### Bước 4 – Cập nhật `Dockerfile` (healthcheck & wait)

Mỗi service cần đợi PostgreSQL sẵn sàng trước khi chạy migrate. Thêm script `wait-for-postgres.sh` hoặc dùng `pg_isready` trực tiếp trong `CMD`.

**Tạo file `docker/wait-for-postgres.sh` dùng chung:**

```bash
#!/bin/sh
# docker/wait-for-postgres.sh
# Sử dụng: wait-for-postgres.sh <host> <user> -- <command>

HOST=$1
USER=$2
shift 2

until pg_isready -h "$HOST" -U "$USER" > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL at $HOST..."
  sleep 2
done

echo "PostgreSQL is ready."
exec "$@"
```

**Cập nhật Dockerfile của từng service** – ví dụ `book-service/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Cài postgresql-client để có pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy wait script từ build context
COPY ../docker/wait-for-postgres.sh /wait-for-postgres.sh
RUN chmod +x /wait-for-postgres.sh

EXPOSE 8888

CMD ["/wait-for-postgres.sh", "postgres", "bookstore", "--", \
     "sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8888"]
```

> **Nếu không muốn sửa Dockerfile:** dùng `depends_on.condition: service_healthy` trong `docker-compose.yml` (đã cấu hình ở Bước 1) – đây là cách đơn giản hơn và đã đủ trong hầu hết trường hợp.

---

### Bước 5 – Cập nhật script `seed_data` & `run_migrations`

#### `run_migrations.sh` (Linux/macOS)

Thay logic tạo venv + SQLite bằng psql:

```bash
#!/bin/bash
# run_migrations.sh – chạy migration cho tất cả service qua Docker

set -e
source .env

echo "=== Running migrations for all services ==="

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

for svc in "${services[@]}"; do
  echo "--- Migrating $svc ---"
  docker compose exec "$svc" python manage.py migrate --noinput
done

echo "=== All migrations done ==="
```

#### `seed_data.sh` (Linux/macOS)

Thay `sqlite3` CLI bằng `docker compose exec` + Django shell:

```bash
#!/bin/bash
# seed_data.sh – seed dữ liệu mẫu qua Django management commands

set -e

echo "=== Seeding data ==="

# Ví dụ: seed categories
docker compose exec catalog-service python manage.py loaddata initial_categories.json

# Ví dụ: seed books
docker compose exec book-service python manage.py loaddata initial_books.json

# Hoặc dùng custom management command:
# docker compose exec book-service python manage.py seed_books

echo "=== Seed done ==="
```

> **Khuyến nghị:** Chuyển logic seed từ SQL thuần sang Django **fixtures** (`.json`) hoặc **management commands** (`python manage.py seed_*`) để không phụ thuộc vào CLI của từng DB engine.

#### `run_migrations.ps1` (Windows)

```powershell
# run_migrations.ps1
$services = @(
    "customer-service", "book-service", "cart-service",
    "staff-service", "manager-service", "catalog-service",
    "order-service", "ship-service", "pay-service",
    "comment-rate-service", "recommender-ai-service", "api-gateway"
)

foreach ($svc in $services) {
    Write-Host "--- Migrating $svc ---"
    docker compose exec $svc python manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Migration failed for $svc"
        exit 1
    }
}

Write-Host "=== All migrations done ==="
```

---

### Bước 6 – Migrate dữ liệu từ SQLite sang PostgreSQL

Nếu các file `db.sqlite3` hiện tại có dữ liệu cần giữ lại, thực hiện lần lượt cho từng service:

```bash
# Ví dụ cho book-service

# 1. Dump dữ liệu từ SQLite (chạy trên container cũ với SQLite)
docker compose exec book-service \
  python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude auth.permission --exclude contenttypes \
  -o /tmp/book_data.json

# 2. Copy file ra host
docker compose cp book-service:/tmp/book_data.json ./backups/book_data.json

# 3. Sau khi đổi sang PostgreSQL và đã migrate schema:
docker compose cp ./backups/book_data.json book-service:/tmp/book_data.json
docker compose exec book-service python manage.py loaddata /tmp/book_data.json
```

Hoặc dùng script batch `migrate_data.sh`:

```bash
#!/bin/bash
# migrate_data.sh – dump từ SQLite rồi load vào PostgreSQL

set -e
mkdir -p ./backups

SERVICES=("book-service" "customer-service" "cart-service" "staff-service"
          "manager-service" "catalog-service" "order-service" "ship-service"
          "pay-service" "comment-rate-service" "recommender-ai-service" "api-gateway")

# Phase 1: dump (chạy khi vẫn còn SQLite)
echo "=== Phase 1: Dumping SQLite data ==="
for svc in "${SERVICES[@]}"; do
  echo "Dumping $svc..."
  docker compose exec "$svc" python manage.py dumpdata \
    --natural-foreign --natural-primary \
    --exclude auth.permission --exclude contenttypes \
    -o /tmp/dump.json
  docker compose cp "$svc:/tmp/dump.json" "./backups/${svc}_dump.json"
done

echo "Dump hoàn tất. Giờ hãy:"
echo "1. Cập nhật code sang PostgreSQL"
echo "2. docker compose down && docker compose up --build -d"
echo "3. Chờ các service healthy"
echo "4. Chạy lại script với flag --load"
```

---

## 6. File `.env` quản lý credentials

Tạo file `.env` ở thư mục gốc repo:

```env
# .env
# ⚠️ KHÔNG commit file này lên git

POSTGRES_USER=bookstore
POSTGRES_PASSWORD=your_strong_password_here
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Django
DJANGO_SECRET_KEY=change_me_to_a_random_50_char_string
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Thêm vào `.gitignore`:

```gitignore
# .gitignore – thêm các dòng sau
.env
*.env
backups/
*.sqlite3
```

Tạo file `.env.example` để commit lên git làm template:

```env
# .env.example – template, không chứa secret thật
POSTGRES_USER=bookstore
POSTGRES_PASSWORD=CHANGE_ME
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=CHANGE_ME
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 7. Checklist kiểm thử

Sau khi hoàn thành các bước trên, kiểm tra theo thứ tự:

### 7.1 Khởi động hệ thống

```bash
# Xóa containers và volumes cũ
docker compose down -v

# Build và chạy lại
docker compose up --build -d

# Kiểm tra PostgreSQL healthy
docker compose ps postgres
# Expected: postgres   running (healthy)

# Xem log postgres init
docker compose logs postgres | grep "database creation"
```

### 7.2 Kiểm tra từng service

```bash
# Xem log migration của từng service
docker compose logs book-service | grep -E "(Applying|migrate|error)"

# Health check tổng hợp
curl http://localhost:8888/health/
```

### 7.3 Kiểm tra kết nối database

```bash
# Kết nối psql từ host
psql -h localhost -p 5432 -U bookstore -l
# Expected: liệt kê 12 database

# Kiểm tra tables trong một DB cụ thể
psql -h localhost -p 5432 -U bookstore -d book_db -c "\dt"
```

### 7.4 Kiểm tra API

```bash
# CRUD books
curl http://localhost:8888/api/books/

# Tạo customer mới
curl -X POST http://localhost:8888/api/customers/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com"}'

# Tạo order
curl -X POST http://localhost:8888/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "shipping_address": "123 Test St", "items": [{"book_id": 1, "quantity": 1, "unit_price": 100000}]}'
```

### 7.5 Test persistence

```bash
# Restart containers (không dùng -v)
docker compose restart

# Kiểm tra dữ liệu vẫn còn
curl http://localhost:8888/api/customers/1/
```

---

## 8. Rollback plan

Nếu có vấn đề, rollback về SQLite:

```bash
# 1. Dừng hệ thống
docker compose down

# 2. Checkout lại branch hoặc stash changes
git stash  # hoặc git checkout -- docker-compose.yml <service>/settings.py ...

# 3. Khởi động lại với SQLite
docker compose up --build -d

# 4. Dữ liệu SQLite vẫn còn trong các file db.sqlite3 trên host
```

> **Khuyến nghị:** Tạo branch riêng `feature/postgres-migration` trước khi bắt đầu. Chỉ merge vào `main` sau khi tất cả kiểm thử pass.

---

## 9. Lưu ý vận hành

### Backup PostgreSQL

```bash
# Backup toàn bộ
docker compose exec postgres pg_dumpall -U bookstore > backups/full_backup_$(date +%Y%m%d).sql

# Backup một database cụ thể
docker compose exec postgres pg_dump -U bookstore book_db > backups/book_db_$(date +%Y%m%d).sql

# Restore
docker compose exec -T postgres psql -U bookstore book_db < backups/book_db_20260610.sql
```

### Xem dữ liệu khi debug

```bash
# Kết nối psql vào một DB cụ thể
docker compose exec postgres psql -U bookstore -d order_db

# Trong psql:
\dt               -- liệt kê tables
SELECT * FROM order_order LIMIT 5;
\q                -- thoát
```

### Khi thêm service mới

1. Tạo database mới trong `POSTGRES_MULTIPLE_DATABASES` (hoặc chạy `CREATE DATABASE` thủ công).
2. Thêm `DATABASE_URL` env cho service mới trong `docker-compose.yml`.
3. Cập nhật `settings.py` của service mới theo pattern đã mô tả.
4. Chạy `python manage.py migrate` trong container.

### Performance tuning cơ bản

Thêm vào `settings.py` của các service có traffic cao:

```python
DATABASES = {
    'default': {
        **dj_database_url.parse(DATABASE_URL, conn_max_age=600),
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30s query timeout
        }
    }
}
```

---

*Kế hoạch được tổng hợp dựa trên cấu trúc thực tế của repo `Shadow23434/microservices-bookstore`. Mọi thay đổi nên được thực hiện trên branch riêng và kiểm thử đầy đủ trước khi merge.*
