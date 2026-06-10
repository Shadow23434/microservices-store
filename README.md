# Bookstore Microservice

Hệ thống quản lý nhà sách theo kiến trúc microservices, dùng nhiều Django service giao tiếp qua API Gateway. Repo hiện có 2 lớp giao diện:

- Giao diện quản trị bằng Django templates trong `api-gateway`.
- Một frontend React/Vite riêng trong thư mục `frontend`.

## Tổng quan kiến trúc

Luồng chạy mặc định:

```text
Browser
  |
  | http://localhost:8888
  v
API Gateway (Django)
  |
  +-- /api/customers/        -> customer-service
  +-- /api/books/            -> book-service
  +-- /api/carts/            -> cart-service
  +-- /api/staff/            -> staff-service
  +-- /api/managers/         -> manager-service
  +-- /api/categories/       -> catalog-service
  +-- /api/orders/           -> order-service
  +-- /api/shipments/        -> ship-service
  +-- /api/payments/         -> pay-service
  +-- /api/reviews/          -> comment-rate-service
  +-- /api/recommendations/  -> recommender-ai-service
```

Tất cả Django service bên trong Docker network đều chạy trên cổng `8888`. Chỉ `api-gateway` được publish ra máy host qua `http://localhost:8888`.

## Danh sách service

| Service                  | Vai trò                | Ghi chú                             |
| ------------------------ | ---------------------- | ----------------------------------- |
| `api-gateway`            | Web UI + reverse proxy | Entry point của hệ thống            |
| `customer-service`       | Quản lý khách hàng     | Có liên kết tạo giỏ hàng            |
| `book-service`           | Quản lý sách           | Dữ liệu sách, tồn kho               |
| `cart-service`           | Quản lý giỏ hàng       | Phụ thuộc `book-service`            |
| `staff-service`          | Quản lý nhân viên      | CRUD staff                          |
| `manager-service`        | Quản lý quản lý        | CRUD manager                        |
| `catalog-service`        | Quản lý danh mục       | Category cho sách                   |
| `order-service`          | Quản lý đơn hàng       | Gọi `pay-service` và `ship-service` |
| `ship-service`           | Quản lý vận chuyển     | Tạo shipment                        |
| `pay-service`            | Quản lý thanh toán     | Tạo payment                         |
| `comment-rate-service`   | Đánh giá, bình luận    | Review và rating                    |
| `recommender-ai-service` | Gợi ý sách             | Dùng dữ liệu sách và review         |

## Yêu cầu môi trường

Để chạy toàn bộ hệ thống bằng Docker:

- Docker Desktop hoặc Docker Engine + Docker Compose v2
- PowerShell nếu muốn dùng các script hỗ trợ trên Windows

Để seed dữ liệu bằng `seed_data.ps1`, máy local cần thêm:

- `sqlite3` có trong `PATH`

Không cần cài Python trên máy nếu chỉ chạy bằng Docker Compose.

## Chạy hệ thống bằng Docker Compose

Từ thư mục gốc của repo:

```bash
docker compose up --build
```

Chạy nền:

```bash
docker compose up -d --build
```

Kiểm tra trạng thái:

```bash
docker compose ps
```

Dừng hệ thống:

```bash
docker compose down
```

Lưu ý:

- Mỗi container sẽ tự chạy `python manage.py migrate` khi khởi động.
- SQLite của từng service đang được mount ra file `db.sqlite3` trong từng thư mục service để dữ liệu giữ lại giữa các lần restart container.

## URL truy cập chính

### Giao diện quản trị qua API Gateway

| URL                                         | Mô tả                  |
| ------------------------------------------- | ---------------------- |
| `http://localhost:8888/`                    | Dashboard              |
| `http://localhost:8888/books/`              | Quản lý sách           |
| `http://localhost:8888/customers/`          | Quản lý khách hàng     |
| `http://localhost:8888/orders/`             | Quản lý đơn hàng       |
| `http://localhost:8888/staff-page/`         | Quản lý nhân viên      |
| `http://localhost:8888/payments-page/`      | Quản lý thanh toán     |
| `http://localhost:8888/shipments-page/`     | Quản lý vận chuyển     |
| `http://localhost:8888/reviews-page/`       | Quản lý đánh giá       |
| `http://localhost:8888/cart/<customer_id>/` | Xem giỏ hàng của khách |
| `http://localhost:8888/health/`             | Health check tổng hợp  |

### API qua Gateway

Mẫu endpoint:

```text
http://localhost:8888/api/<resource>/
http://localhost:8888/api/<resource>/<id>/
```

Danh sách resource đang được gateway proxy:

- `customers`
- `books`
- `carts`
- `staff`
- `managers`
- `categories`
- `orders`
- `shipments`
- `payments`
- `reviews`
- `recommendations`

Ví dụ:

```bash
curl http://localhost:8888/api/books/

curl http://localhost:8888/api/customers/

curl -X POST http://localhost:8888/api/customers/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Nguyen Van A","email":"a@example.com"}'

curl -X POST http://localhost:8888/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "shipping_address": "123 Nguyen Hue, Quan 1, TP.HCM",
    "items": [
      {"book_id": 1, "quantity": 1, "unit_price": 320000}
    ]
  }'
```

## Script hỗ trợ trong repo

### `run_migrations.ps1`

Script này dùng để tạo lại virtual environment và chạy migration cho một nhóm Django service trên máy local, không phụ thuộc Docker.

Chạy bằng PowerShell:

```powershell
.\run_migrations.ps1
```

Phù hợp khi bạn cần sửa schema hoặc debug riêng từng service trong môi trường local.

### `seed_data.ps1`

Script này seed dữ liệu mẫu trực tiếp vào các file SQLite hiện có trong repo.

Chạy bằng PowerShell:

```powershell
.\seed_data.ps1
```

Script hiện seed các nhóm dữ liệu sau:

- Category
- Book
- Customer
- Cart
- Staff
- Manager
- Review
- Order
- Payment
- Shipment

Lưu ý:

- Cần có `sqlite3` trong `PATH`.
- Nên chạy sau khi DB đã được migrate.

## Frontend React

Thư mục `frontend` là một ứng dụng React dùng Vite.

Nếu muốn chạy frontend:

```bash
cd frontend
npm install
npm run dev
```

## Guide chạy giao diện

Bạn có thể chạy giao diện theo 2 cách, tùy mục đích sử dụng.

### Cách 1: Chạy giao diện Django templates (nhanh nhất)

Phù hợp để kiểm thử nhanh toàn bộ hệ thống qua API Gateway.

1. Từ thư mục gốc repo, chạy backend bằng Docker Compose:

```bash
docker compose up -d --build
```

2. Chờ các service lên xong rồi mở:

- `http://localhost:8888/` (dashboard)
- `http://localhost:8888/books/`
- `http://localhost:8888/customers/`
- `http://localhost:8888/orders/`

3. Xem log nếu trang chưa lên:

```bash
docker compose logs -f api-gateway
```

### Cách 2: Chạy giao diện React/Vite

Phù hợp khi phát triển UI hiện đại ở thư mục `frontend`.

1. Đảm bảo backend (API Gateway) đang chạy ở `http://localhost:8888`.

2. Mở terminal mới và chạy frontend:

```bash
cd frontend
npm install
npm run dev
```

3. Mở URL Vite hiển thị trên terminal (thường là `http://localhost:5173`).

### Luồng chạy khuyến nghị khi dev UI

1. Chạy backend trước:

```bash
docker compose up -d --build
```

2. Chạy frontend React:

```bash
cd frontend
npm run dev
```

3. Khi xong việc:

```bash
docker compose down
```

> Nếu lỗi API/CORS, kiểm tra lại API base URL trong frontend và đảm bảo `api-gateway` đang healthy.

## Cấu trúc thư mục chính

```text
microservice/
├── docker-compose.yml
├── README.md
├── run_migrations.ps1
├── seed_data.ps1
├── api-gateway/
├── book-service/
├── cart-service/
├── catalog-service/
├── comment-rate-service/
├── customer-service/
├── frontend/
├── manager-service/
├── order-service/
├── pay-service/
├── recommender-ai-service/
├── ship-service/
└── staff-service/
```

Mỗi backend service đều có cấu trúc Django tương tự:

```text
<service>/
├── Dockerfile
├── requirements.txt
└── <django_project>/
    ├── manage.py
    ├── app/
    └── <django_project>/
```

## Luồng nghiệp vụ chính

### Tạo khách hàng

```text
POST /api/customers/
-> customer-service tạo customer
-> customer-service gọi cart-service để tạo cart mặc định
```

### Tạo đơn hàng

```text
POST /api/orders/
-> order-service tạo order và order items
-> order-service gọi pay-service để tạo payment
-> order-service gọi ship-service để tạo shipment
```

## Một số lệnh thường dùng

```bash
docker compose logs -f api-gateway
docker compose logs -f order-service
docker compose restart api-gateway
docker compose up --build -d api-gateway
docker compose up --build -d order-service
docker compose down -v
```

## Lưu ý vận hành

- Nếu cổng `8888` bị chiếm, đổi mapping trong `docker-compose.yml`.
- Dữ liệu SQLite được giữ trong các file `db.sqlite3` của từng service. Nếu xóa các file này hoặc mount volume khác, dữ liệu hiện tại sẽ mất.
- `docker compose down -v` không xóa bind-mounted SQLite trong repo, nhưng vẫn có thể xóa các volume Docker khác nếu sau này dự án bổ sung volume named.
