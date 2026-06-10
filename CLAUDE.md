# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Django-based microservices e-commerce system with 13 independent services communicating via HTTP through an API Gateway. The system supports multiple product types (books, laptops, mobiles, clothing) and uses PostgreSQL with separate databases per service for data isolation.

## Architecture

### Service Communication Flow

```
Browser → API Gateway (localhost:8888) → Internal Services (Docker network, port 8888)
```

All inter-service communication happens via HTTP within the Docker network. The API Gateway is the only service exposed to the host machine.

### Service Dependencies

Critical runtime dependencies (service A calls service B):

- `customer-service` → `cart-service`: Auto-creates cart when customer is created
- `order-service` → `pay-service` + `ship-service`: Orchestrates payment and shipment on order creation
- `cart-service` → `product-service`: Validates product availability
- `recommender-ai-service` → `product-service` + `comment-rate-service`: Aggregates data for recommendations
- `order-service` → `product-service`: Fetches product details when creating orders

These dependencies are reflected in `docker-compose.yml` via `depends_on` and service URLs in environment variables.

### Gateway Proxy Routes

The API Gateway proxies these routes to respective services:

- `/api/customers/` → customer-service
- `/api/products/` → product-service (supports book, laptop, mobile, cloth types)
- `/api/books/` → book-service (legacy - still active during migration)
- `/api/carts/` → cart-service
- `/api/staff/` → staff-service
- `/api/managers/` → manager-service
- `/api/categories/` → catalog-service
- `/api/orders/` → order-service
- `/api/shipments/` → ship-service
- `/api/payments/` → pay-service
- `/api/reviews/` → comment-rate-service
- `/api/recommendations/` → recommender-ai-service

The gateway also serves Django template-based admin UI at root paths like `/books/`, `/customers/`, `/orders/`.

## Database Architecture

PostgreSQL 16 with 13 separate databases:

- `customer_db`, `product_db`, `book_db` (legacy), `cart_db`, `staff_db`, `manager_db`, `catalog_db`, `order_db`, `ship_db`, `pay_db`, `comment_rate_db`, `recommender_db`, `gateway_db`

All databases are created on first startup via `docker/postgres/init-multiple-db.sh`. Each service connects via `DATABASE_URL` environment variable in the format:
```
postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/<db_name>
```

## Commands

### Running the System

Start all services (builds images and starts containers):
```bash
docker compose up --build
```

Start in detached mode:
```bash
docker compose up -d --build
```

Check service status:
```bash
docker compose ps
```

Stop all services:
```bash
docker compose down
```

Remove volumes (resets all data):
```bash
docker compose down -v
```

### First Time Setup

**Automatic initialization happens on first startup:**

1. **Migrations**: Each service automatically runs `python manage.py migrate` on container startup (configured in each service's Dockerfile CMD)

2. **Data Seeding**: The `init-data` service automatically runs after all services are healthy:
   - Waits for API Gateway health endpoint to confirm all services are ready
   - Executes `scripts/seed_all_services.py` to populate databases with sample data
   - Seeds categories, books, customers, carts, staff, managers, reviews, orders, payments, shipments
   - Creates sample products (laptops, mobiles, clothing) via product-service API
   - Migrates existing books from book-service to product-service
   - Runs once and exits (does not restart)

**To re-run seeding manually** (if init-data service already completed):
```bash
docker compose run --rm init-data
```

**To skip automatic seeding** (start services without init-data):
```bash
docker compose up --build --scale init-data=0
```

### Viewing Logs

View logs for a specific service:
```bash
docker compose logs -f api-gateway
docker compose logs -f order-service
docker compose logs -f <service-name>
```

### Restarting Individual Services

Restart a service after code changes:
```bash
docker compose restart api-gateway
```

Rebuild and restart a service:
```bash
docker compose up --build -d api-gateway
```

### Migrations

Each service automatically runs `python manage.py migrate` on container startup (see Dockerfile CMD).

To run migrations manually on local machine (without Docker):
```powershell
.\scripts\run_migrations.ps1
```

Or on Linux/Mac:
```bash
./scripts/run_migrations.sh
```

### Seeding Data

Seed data using Python scripts (requires services to be running):
```bash
./scripts/seed_all.sh
```

Or use PowerShell version:
```powershell
.\scripts\seed_data.ps1
```

Individual seed scripts are in `scripts/`:
- `seed_books.py`
- `seed_categories.py`
- `seed_customers.py`

### Frontend Development

The `frontend/` directory contains a separate React/Vite application.

Start the frontend dev server:
```bash
cd frontend
npm install
npm run dev
```

The frontend typically runs on `http://localhost:5173` and makes API calls to the backend at `http://localhost:8888`.

## Service Structure

Each microservice follows the same Django structure:

```
<service-name>/
├── Dockerfile
├── requirements.txt
└── <service_name>/
    ├── manage.py
    ├── app/
    │   ├── models.py
    │   ├── views.py
    │   ├── serializers.py
    │   └── migrations/
    └── <service_name>/
        ├── settings.py
        ├── urls.py
        └── wsgi.py
```

All services use Django REST Framework for API endpoints. Service-to-service calls are made using Python `requests` library with service URLs from environment variables.

## Configuration

### Required Environment Variables

Copy `.env.example` to `.env` and set:

```
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

DJANGO_SECRET_KEY=<random_secret_key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### Service-Specific Environment Variables

Each service receives:
- `DATABASE_URL`: PostgreSQL connection string
- `<SERVICE>_SERVICE_URL`: URLs for services it depends on (e.g., `BOOK_SERVICE_URL=http://book-service:8888`)

These are configured in `docker-compose.yml` under each service's `environment` section.

## Key Business Flows

### Customer Creation
```
POST /api/customers/
→ customer-service creates customer
→ customer-service calls cart-service to create default cart
```

### Order Creation
```
POST /api/orders/
→ order-service creates order and order items
→ order-service calls pay-service to create payment record
→ order-service calls ship-service to create shipment record
```

## Debugging

### Service Not Starting

Check service logs:
```bash
docker compose logs -f <service-name>
```

Common issues:
- PostgreSQL not healthy: Wait for `pg_isready` healthcheck to pass
- Port 8888 already in use: Change port mapping in `docker-compose.yml`
- Missing `.env` file: Copy from `.env.example`

### Service Can't Connect to Another Service

Check that:
1. Target service is running: `docker compose ps`
2. Service URL environment variable is correct in `docker-compose.yml`
3. Services are in same Docker network (default: all services are in `microservice_default`)

### Database Issues

View PostgreSQL logs:
```bash
docker compose logs -f postgres
```

Connect to PostgreSQL directly:
```bash
docker compose exec postgres psql -U <POSTGRES_USER> -d <database_name>
```

Reset all data:
```bash
docker compose down -v
docker compose up --build
```

## Access URLs

- **API Gateway**: http://localhost:8888/
- **Admin UI**: http://localhost:8888/books/, /customers/, /orders/, etc.
- **Health Check**: http://localhost:8888/health/
- **API Endpoints**: http://localhost:8888/api/<resource>/
- **Frontend (if running)**: http://localhost:5173/

## Notes

- All services run on port 8888 internally, but only the API Gateway is exposed to the host
- PostgreSQL data persists in Docker volume `postgres_data`
- Each service's SQLite `db.sqlite3` files are legacy and no longer used (system migrated to PostgreSQL)
- Services use Django's development server (`runserver`), not production WSGI servers
- No authentication/authorization is currently implemented on inter-service calls