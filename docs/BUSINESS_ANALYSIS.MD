# PHÂN TÍCH NGHIỆP VỤ — HỆ THỐNG E-COMMERCE MICROSERVICES

---

## MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Kiến trúc & Công nghệ nền tảng](#2-kiến-trúc--công-nghệ-nền-tảng)
3. [Phân tích yêu cầu](#3-phân-tích-yêu-cầu)
4. [Domain Driven Design — Phân rã hệ thống](#4-domain-driven-design--phân-rã-hệ-thống)
5. [Thiết kế chi tiết từng Microservice](#5-thiết-kế-chi-tiết-từng-microservice)
6. [Luồng nghiệp vụ tổng thể](#6-luồng-nghiệp-vụ-tổng-thể)
7. [AI Service — Tư vấn & Gợi ý sản phẩm](#7-ai-service--tư-vấn--gợi-ý-sản-phẩm)
8. [Kiến trúc triển khai hoàn chỉnh](#8-kiến-trúc-triển-khai-hoàn-chỉnh)
9. [Bảo mật hệ thống](#9-bảo-mật-hệ-thống)
10. [Đánh giá hệ thống](#10-đánh-giá-hệ-thống)

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Mục tiêu

Xây dựng nền tảng thương mại điện tử theo kiến trúc **Microservices** có khả năng:

- Mở rộng độc lập từng thành phần theo tải thực tế.
- Triển khai, cập nhật từng service mà không ảnh hưởng toàn hệ thống.
- Phân tách rõ trách nhiệm theo miền nghiệp vụ (Domain Driven Design).
- Tích hợp AI Service để cá nhân hóa trải nghiệm mua sắm.

### 1.2 Các thành phần chính

| Thành phần           | Vai trò                                       | Công nghệ             |
| -------------------- | --------------------------------------------- | --------------------- |
| Client / Web UI      | Giao diện cho Guest, Customer, Admin          | React / HTML          |
| **API Gateway**      | Điểm vào duy nhất, định tuyến request         | Nginx                 |
| **Product Service**  | Quản lý sản phẩm, danh mục, tồn kho           | Django REST Framework |
| **User Service**     | Xác thực, phân quyền RBAC, hồ sơ              | Django REST Framework |
| **Cart Service**     | Quản lý giỏ hàng tạm thời                     | Django REST Framework |
| **Order Service**    | Điều phối đặt hàng, quản lý trạng thái        | Django REST Framework |
| **Payment Service**  | Xử lý thanh toán, cổng thanh toán             | Django REST Framework |
| **Shipping Service** | Vận đơn, phí giao hàng, trạng thái vận chuyển | Django REST Framework |
| **AI Service**       | Gợi ý sản phẩm, chatbot tư vấn                | Python / FastAPI      |
| **Databases**        | Lưu trữ riêng cho từng service                | PostgreSQL / MySQL    |

### 1.3 Kiến trúc tổng thể (sơ đồ logic)

```
Client / Web UI
      │
      ▼
┌─────────────────────────────────┐
│         API Gateway (Nginx)     │
│  /api/products → Product Svc    │
│  /api/auth     → User Svc       │
│  /api/cart     → Cart Svc       │
│  /api/orders   → Order Svc      │
│  /api/payments → Payment Svc    │
│  /api/shipping → Shipping Svc   │
│  /api/ai       → AI Svc         │
└─────────────────────────────────┘
      │ Docker Internal Network
      ├── Product Service  ──► product_db
      ├── User Service     ──► user_db
      ├── Cart Service     ──► cart_db
      ├── Order Service    ──► order_db
      ├── Payment Service  ──► payment_db
      ├── Shipping Service ──► shipping_db
      └── AI Service       ──► ai_db / vector_db
```

---

## 2. KIẾN TRÚC & CÔNG NGHỆ NỀN TẢNG

### 2.1 Monolithic vs Microservices — Tại sao chọn Microservices?

| Tiêu chí   | Monolithic                       | Microservices                               |
| ---------- | -------------------------------- | ------------------------------------------- |
| Codebase   | Một codebase lớn                 | Nhiều codebase độc lập                      |
| Deployment | Deploy toàn bộ hệ thống cùng lúc | Deploy độc lập từng service                 |
| Scaling    | Mở rộng toàn bộ ứng dụng         | Mở rộng riêng service chịu tải cao          |
| Database   | Dùng chung một CSDL              | Mỗi service sở hữu DB riêng                 |
| Coupling   | Dễ phát sinh coupling chặt       | Giảm coupling qua API & Event               |
| Vận hành   | Đơn giản ban đầu                 | Phức tạp hơn do hệ thống phân tán           |
| Phù hợp    | MVP, hệ thống nhỏ, nhóm ít       | Hệ thống lớn, nhiều nhóm, cần scale độc lập |

**Lý do chọn Microservices cho E-Commerce:**

- Nhiều miền nghiệp vụ có vòng đời dữ liệu và tần suất thay đổi khác nhau.
- Product và Cart cần scale nhiều hơn trong các đợt khuyến mãi.
- Payment cần kiểm soát bảo mật và tích hợp bên ngoài riêng biệt.
- Nhiều nhóm phát triển có thể làm việc song song mà không xung đột.

### 2.2 Nguyên tắc thiết kế Microservices

| Nguyên tắc                | Ý nghĩa                                                |
| ------------------------- | ------------------------------------------------------ |
| **Single Responsibility** | Mỗi service tập trung vào một năng lực nghiệp vụ chính |
| **Loose Coupling**        | Giảm phụ thuộc trực tiếp giữa các service              |
| **High Cohesion**         | Các logic liên quan nên nằm trong cùng một service     |
| **Database per Service**  | Service sở hữu và bảo vệ dữ liệu nội bộ                |
| **Design for Failure**    | Thiết kế với giả định lỗi mạng/service có thể xảy ra   |
| **Observability**         | Hệ thống cần logging, metrics và tracing               |

### 2.3 Domain Driven Design (DDD)

DDD giúp xác định ranh giới service theo nghiệp vụ thay vì tầng kỹ thuật.

**Các khái niệm cốt lõi:**

| Khái niệm           | Mô tả                                                   | Ví dụ trong E-Commerce         |
| ------------------- | ------------------------------------------------------- | ------------------------------ |
| **Entity**          | Đối tượng có định danh riêng, vòng đời độc lập          | User, Product, Order           |
| **Value Object**    | Đối tượng không có định danh, so sánh theo giá trị      | Address, Money, Email          |
| **Aggregate**       | Cụm entity/VO được quản lý qua một aggregate root       | Order (root) + OrderItem       |
| **Bounded Context** | Ranh giới trong đó model nghiệp vụ có ý nghĩa nhất quán | Product Context, Order Context |
| **Context Map**     | Sơ đồ quan hệ giữa các bounded context                  | Cart → Product → Order         |

---

## 3. PHÂN TÍCH YÊU CẦU

### 3.1 Yêu cầu chức năng (Functional Requirements)

| Mã    | Yêu cầu                                                         | Độ ưu tiên | Service          |
| ----- | --------------------------------------------------------------- | ---------- | ---------------- |
| FR-01 | Xem danh sách sản phẩm, phân trang, lọc theo danh mục/giá       | Cao        | Product Service  |
| FR-02 | Xem chi tiết sản phẩm (tên, mô tả, ảnh, giá, tồn kho, danh mục) | Cao        | Product Service  |
| FR-03 | Admin thêm, cập nhật, vô hiệu hóa sản phẩm & quản lý danh mục   | Cao        | Product Service  |
| FR-04 | Đăng ký, đăng nhập, cập nhật hồ sơ, quản lý địa chỉ giao hàng   | Cao        | User Service     |
| FR-05 | Phân quyền theo vai trò: Guest, Customer, Admin                 | Cao        | User Service     |
| FR-06 | Thêm sản phẩm vào giỏ hàng, cập nhật số lượng, xóa sản phẩm     | Cao        | Cart Service     |
| FR-07 | Tạo đơn hàng từ giỏ hàng, xem lịch sử và chi tiết đơn hàng      | Cao        | Order Service    |
| FR-08 | Xử lý thanh toán bằng COD hoặc cổng thanh toán giả lập          | Cao        | Payment Service  |
| FR-09 | Tạo vận đơn, tính phí giao hàng, cập nhật trạng thái vận chuyển | Trung bình | Shipping Service |
| FR-10 | Ghi nhận hành vi người dùng để phục vụ gợi ý sản phẩm AI        | Trung bình | AI Service       |

### 3.2 Yêu cầu phi chức năng (Non-functional Requirements)

| Nhóm                       | Mô tả                                                        | Tiêu chí đánh giá                                      |
| -------------------------- | ------------------------------------------------------------ | ------------------------------------------------------ |
| **Hiệu năng**              | API phổ biến phản hồi nhanh trong điều kiện tải thông thường | Thời gian phản hồi < 500ms cho API đọc dữ liệu         |
| **Khả năng mở rộng**       | Mỗi service scale độc lập                                    | Tăng instance mà không deploy lại toàn hệ thống        |
| **Bảo mật**                | Bảo vệ thông tin đăng nhập, phân quyền API                   | Mật khẩu hash, JWT, endpoint Admin yêu cầu role        |
| **Độ tin cậy**             | Lỗi một service không làm sập toàn bộ hệ thống               | Service lỗi được cô lập, API trả lỗi rõ ràng           |
| **Tính nhất quán dữ liệu** | Chấp nhận eventual consistency trong luồng liên service      | Order, Payment, Shipping đồng bộ qua API/event         |
| **Dễ bảo trì**             | Codebase từng service có trách nhiệm rõ ràng                 | Thay đổi Product Service không ảnh hưởng User Service  |
| **Khả năng triển khai**    | Docker hóa để triển khai mọi môi trường                      | Mỗi service có Dockerfile và cấu hình môi trường riêng |

### 3.3 Tác nhân hệ thống (System Actors)

| Tác nhân              | Vai trò                                                                            |
| --------------------- | ---------------------------------------------------------------------------------- |
| **Guest**             | Chưa đăng nhập; xem sản phẩm, tìm kiếm, đăng ký tài khoản                          |
| **Customer**          | Đã đăng nhập; quản lý hồ sơ, giỏ hàng, đặt hàng, thanh toán, theo dõi vận chuyển   |
| **Admin**             | Quản trị toàn bộ: sản phẩm, danh mục, người dùng, đơn hàng, thanh toán, vận chuyển |
| **Payment Gateway**   | Hệ thống ngoài / module giả lập xác nhận kết quả thanh toán                        |
| **Shipping Provider** | Đơn vị vận chuyển / module giả lập cập nhật trạng thái giao hàng                   |
| **AI Service**        | Phân tích hành vi người dùng, sinh danh sách gợi ý sản phẩm                        |

### 3.4 Use Case tổng quát

| Actor      | Use Case                | Mô tả                                                       |
| ---------- | ----------------------- | ----------------------------------------------------------- |
| Guest      | Xem & tìm kiếm sản phẩm | Duyệt catalog, lọc danh mục, xem chi tiết trước đăng nhập   |
| Guest      | Đăng ký tài khoản       | Tạo tài khoản mới để trở thành Customer                     |
| Customer   | Quản lý giỏ hàng        | Thêm, sửa số lượng, xóa sản phẩm trong giỏ                  |
| Customer   | Đặt hàng                | Chuyển giỏ hàng thành đơn với thông tin giao hàng cụ thể    |
| Customer   | Thanh toán              | Chọn phương thức thanh toán, nhận kết quả giao dịch         |
| Customer   | Theo dõi đơn hàng       | Xem trạng thái xử lý, thanh toán và vận chuyển              |
| Admin      | Quản lý sản phẩm        | Thêm, sửa, vô hiệu hóa sản phẩm và danh mục                 |
| Admin      | Quản lý đơn hàng        | Theo dõi, xác nhận, hủy hoặc cập nhật trạng thái đơn        |
| AI Service | Gợi ý sản phẩm          | Sinh danh sách sản phẩm phù hợp dựa trên hành vi người dùng |

---

## 4. DOMAIN DRIVEN DESIGN — PHÂN RÃ HỆ THỐNG

### 4.1 Xác định Subdomain

| Subdomain          | Loại              | Mô tả                                                      |
| ------------------ | ----------------- | ---------------------------------------------------------- |
| **Catalog**        | Supporting Domain | Quản lý sản phẩm, danh mục, hình ảnh, giá, tồn kho         |
| **Identity**       | Supporting Domain | Tài khoản, xác thực, hồ sơ, vai trò, quyền truy cập        |
| **Cart**           | Supporting Domain | Giỏ hàng tạm thời trước khi tạo đơn                        |
| **Ordering**       | **Core Domain**   | Quy trình đặt hàng, trạng thái đơn, snapshot sản phẩm      |
| **Payment**        | Generic Domain    | Thanh toán, trạng thái giao dịch, kết quả cổng thanh toán  |
| **Shipping**       | Supporting Domain | Vận đơn, phí giao hàng, mã theo dõi, trạng thái vận chuyển |
| **Recommendation** | Core Enhancement  | Phân tích hành vi, gợi ý sản phẩm phù hợp                  |

### 4.2 Bounded Context & Mapping sang Microservice

| Bounded Context        | Entity chính                                         | Microservice         | Database    |
| ---------------------- | ---------------------------------------------------- | -------------------- | ----------- |
| Product Context        | Product, Category, ProductImage, Inventory           | **Product Service**  | product_db  |
| User Context           | User, Role, Permission, Address                      | **User Service**     | user_db     |
| Cart Context           | Cart, CartItem                                       | **Cart Service**     | cart_db     |
| Order Context          | Order, OrderItem, OrderStatusHistory                 | **Order Service**    | order_db    |
| Payment Context        | Payment, PaymentEvent, Transaction                   | **Payment Service**  | payment_db  |
| Shipping Context       | Shipment, ShippingRate, ShipmentStatusHistory        | **Shipping Service** | shipping_db |
| Recommendation Context | UserBehavior, ProductEmbedding, RecommendationResult | **AI Service**       | ai_db       |

### 4.3 Context Map — Quan hệ giữa các Service

| Nguồn         | Đích             | Quan hệ / Mục đích                                          |
| ------------- | ---------------- | ----------------------------------------------------------- |
| Cart Service  | Product Service  | Kiểm tra sản phẩm, giá và tồn kho trước khi thêm vào giỏ    |
| Order Service | Cart Service     | Lấy dữ liệu giỏ hàng khi người dùng checkout                |
| Order Service | Product Service  | Kiểm tra lại giá và tồn kho tại thời điểm tạo đơn           |
| Order Service | Payment Service  | Tạo yêu cầu thanh toán và nhận kết quả giao dịch            |
| Order Service | Shipping Service | Tạo vận đơn sau khi đơn hàng hợp lệ / thanh toán thành công |
| AI Service    | Product Service  | Lấy metadata sản phẩm phục vụ mô hình gợi ý                 |
| AI Service    | User Service     | Lấy định danh người dùng / hành vi được phép xử lý          |

### 4.4 Nguyên tắc tách Service

- Tách theo năng lực nghiệp vụ, **không tách theo tầng kỹ thuật**.
- Mỗi service **sở hữu database riêng** — không truy cập trực tiếp DB của service khác.
- Giao tiếp giữa service **qua API hoặc event message**.
- Một service có thể triển khai, mở rộng và rollback **độc lập**.
- Dữ liệu liên service dùng **ID tham chiếu hoặc snapshot** thay vì foreign key xuyên database.
- Chấp nhận **eventual consistency** trong các luồng phức tạp (đặt hàng, thanh toán, vận chuyển).

---

## 5. THIẾT KẾ CHI TIẾT TỪNG MICROSERVICE

### 5.1 Product Service

**Vai trò:** Quản lý catalog sản phẩm — nguồn dữ liệu đầu vào cho Cart, Order, AI Service.

**Domain Model:**

```
Product (Aggregate Root)
  ├── id, name, description, price
  ├── stock_quantity, status (active/inactive/out_of_stock)
  ├── category_id, created_at, updated_at
  │
Category
  ├── id, name, parent_id
  │
ProductImage
  ├── id, product_id, image_url, is_thumbnail
```

**Quy tắc nghiệp vụ:**

- Giá sản phẩm không được âm.
- Số lượng tồn kho không được nhỏ hơn 0.
- Sản phẩm `inactive` không hiển thị cho Customer.
- Sản phẩm hết hàng không thể thêm vào giỏ.

**API Endpoints:**

| Method | Endpoint                      | Mô tả                                 | Phân quyền |
| ------ | ----------------------------- | ------------------------------------- | ---------- |
| GET    | `/products`                   | Danh sách sản phẩm, phân trang và lọc | Public     |
| GET    | `/products/{id}`              | Chi tiết một sản phẩm                 | Public     |
| GET    | `/categories`                 | Danh sách danh mục                    | Public     |
| POST   | `/products`                   | Tạo sản phẩm mới                      | Admin      |
| PUT    | `/products/{id}`              | Cập nhật thông tin sản phẩm           | Admin      |
| DELETE | `/products/{id}`              | Vô hiệu hóa sản phẩm                  | Admin      |
| GET    | `/products/{id}/availability` | Kiểm tra tồn kho và trạng thái bán    | Internal   |
| PATCH  | `/products/{id}/stock`        | Cập nhật tồn kho                      | Internal   |

**Database Schema (product_db):**

| Table          | Field          | Type     | Ghi chú                          |
| -------------- | -------------- | -------- | -------------------------------- |
| products       | id             | UUID/INT | Primary key                      |
| products       | name           | VARCHAR  | Tên sản phẩm                     |
| products       | price          | DECIMAL  | Giá bán                          |
| products       | stock_quantity | INT      | Tồn kho                          |
| products       | status         | VARCHAR  | active / inactive / out_of_stock |
| categories     | id             | UUID/INT | Primary key danh mục             |
| product_images | product_id     | UUID/INT | FK tham chiếu sản phẩm           |

---

### 5.2 User Service

**Vai trò:** Quản lý định danh, xác thực, phân quyền RBAC, hồ sơ cá nhân và địa chỉ giao hàng.

**Phân loại người dùng:**

| Loại         | Quyền chính                                                        |
| ------------ | ------------------------------------------------------------------ |
| **Guest**    | Xem sản phẩm, tìm kiếm, đăng ký                                    |
| **Customer** | Quản lý hồ sơ, địa chỉ, giỏ hàng, đơn hàng, thanh toán, vận chuyển |
| **Admin**    | Quản lý sản phẩm, người dùng, đơn hàng, thanh toán, vận chuyển     |

**RBAC Model:**

```
User ──n:n──► Role ──n:n──► Permission
                 └─────────────────────
```

**Permission ví dụ:**

| Permission    | Mô tả                          |
| ------------- | ------------------------------ |
| product.read  | Xem thông tin sản phẩm         |
| product.write | Tạo, sửa, vô hiệu hóa sản phẩm |
| order.read    | Xem thông tin đơn hàng         |
| order.manage  | Quản lý trạng thái đơn hàng    |
| user.manage   | Quản lý người dùng và vai trò  |

**API Endpoints:**

| Method | Endpoint              | Mô tả                          |
| ------ | --------------------- | ------------------------------ |
| POST   | `/auth/register`      | Đăng ký tài khoản mới          |
| POST   | `/auth/login`         | Đăng nhập, nhận JWT token      |
| GET    | `/users/me`           | Xem hồ sơ cá nhân              |
| PUT    | `/users/me`           | Cập nhật hồ sơ                 |
| GET    | `/users/me/addresses` | Danh sách địa chỉ giao hàng    |
| POST   | `/users/me/addresses` | Thêm địa chỉ giao hàng mới     |
| GET    | `/users/{id}`         | Admin xem thông tin người dùng |

**Luồng đăng ký / đăng nhập:**

```
Đăng ký:
1. Customer nhập email, password, thông tin cá nhân
2. User Service kiểm tra email đã tồn tại chưa
3. Hash password (bcrypt)
4. Tạo User, gán role Customer
5. Trả kết quả đăng ký

Đăng nhập:
1. Customer nhập email, password
2. User Service tìm User theo email
3. So sánh password với password_hash
4. Sinh JWT token (sub, email, roles, exp, iat)
5. Client dùng token cho các API cần xác thực
```

---

### 5.3 Cart Service

**Vai trò:** Quản lý giỏ hàng tạm thời trước khi tạo đơn hàng.

**Domain Model:**

```
Cart
  ├── id, user_id, status (active/checked_out/abandoned)
  ├── created_at, updated_at
  │
CartItem
  ├── id, cart_id, product_id
  ├── product_name_snapshot, unit_price_snapshot
  ├── quantity
```

**Logic xử lý:**

- Mỗi Customer có **một giỏ hàng active** tại một thời điểm.
- Thêm sản phẩm đã có trong giỏ → **tăng quantity** thay vì tạo dòng mới.
- Quantity không được < 1.
- Trước khi thêm: gọi Product Service kiểm tra sản phẩm tồn tại, `active`, đủ tồn kho.
- Lưu **snapshot tên và giá** tại thời điểm thêm vào giỏ (hiển thị nhanh).
- Khi checkout: Order Service vẫn kiểm tra lại giá và tồn kho hiện tại.

**API Endpoints:**

| Method | Endpoint           | Mô tả                            |
| ------ | ------------------ | -------------------------------- |
| GET    | `/cart`            | Xem giỏ hàng hiện tại            |
| POST   | `/cart/items`      | Thêm sản phẩm vào giỏ            |
| PUT    | `/cart/items/{id}` | Cập nhật số lượng sản phẩm       |
| DELETE | `/cart/items/{id}` | Xóa một sản phẩm khỏi giỏ        |
| DELETE | `/cart`            | Xóa toàn bộ giỏ hàng             |
| POST   | `/cart/checkout`   | Chuẩn bị dữ liệu để tạo đơn hàng |

**Database Schema (cart_db):**

| Table      | Field               | Type     | Ghi chú                          |
| ---------- | ------------------- | -------- | -------------------------------- |
| carts      | id                  | UUID/INT | Primary key                      |
| carts      | user_id             | UUID/INT | ID từ User Service               |
| carts      | status              | VARCHAR  | active / checked_out / abandoned |
| cart_items | product_id          | UUID/INT | ID từ Product Service            |
| cart_items | unit_price_snapshot | DECIMAL  | Giá tại thời điểm thêm           |
| cart_items | quantity            | INT      | Số lượng                         |

---

### 5.4 Order Service

**Vai trò:** Trung tâm điều phối quy trình mua hàng — tạo đơn, quản lý trạng thái, phối hợp Payment & Shipping.

**Domain Model:**

```
Order (Aggregate Root)
  ├── id, user_id, status, total_amount
  ├── shipping_fee, payment_status, shipping_status
  ├── created_at
  │
OrderItem
  ├── id, order_id, product_id
  ├── product_name_snapshot, unit_price, quantity, subtotal
  │
OrderStatusHistory
  ├── id, order_id, old_status, new_status, changed_at
```

**Trạng thái đơn hàng:**

| Trạng thái   | Ý nghĩa                                    |
| ------------ | ------------------------------------------ |
| `PENDING`    | Vừa tạo, đang chờ thanh toán hoặc xác nhận |
| `PAID`       | Thanh toán thành công                      |
| `PROCESSING` | Đang được chuẩn bị                         |
| `SHIPPED`    | Đã giao cho đơn vị vận chuyển              |
| `DELIVERED`  | Đã giao thành công                         |
| `CANCELLED`  | Đã bị hủy                                  |
| `FAILED`     | Thất bại do lỗi thanh toán / xử lý         |

**Workflow đặt hàng:**

```
1. Customer bấm Checkout từ giỏ hàng
2. Cart Service trả CartItem hợp lệ
3. Order Service kiểm tra lại sản phẩm với Product Service
4. Order Service tạo Order (PENDING) + OrderItem (snapshot)
5. Order Service yêu cầu Payment Service tạo Payment
6. Order Service yêu cầu Shipping Service tạo Shipment
7. Trả thông tin đơn hàng cho Customer
```

**Consistency & Transaction Boundary:**

- Order Service **không mở transaction** trải sang Payment / Shipping.
- Mỗi service đảm bảo transaction trong DB riêng.
- Nếu bước sau thất bại → cập nhật trạng thái phù hợp (không rollback xuyên DB).

**API Endpoints:**

| Method | Endpoint                        | Mô tả                                |
| ------ | ------------------------------- | ------------------------------------ |
| POST   | `/orders`                       | Tạo đơn hàng mới                     |
| GET    | `/orders`                       | Danh sách đơn hàng của user hiện tại |
| GET    | `/orders/{id}`                  | Chi tiết đơn hàng                    |
| PATCH  | `/orders/{id}/cancel`           | Hủy đơn hàng                         |
| PATCH  | `/orders/{id}/status`           | Admin cập nhật trạng thái            |
| POST   | `/orders/{id}/payment-callback` | Nhận kết quả từ Payment Service      |

---

### 5.5 Payment Service

**Vai trò:** Quản lý giao dịch thanh toán, tích hợp cổng thanh toán, lưu lịch sử sự kiện.

**Domain Model:**

```
Payment
  ├── id, order_id, user_id, amount
  ├── method (COD / gateway)
  ├── status, transaction_code
  ├── created_at, updated_at
  │
PaymentEvent
  ├── id, payment_id, event_type, payload, created_at
```

**Trạng thái thanh toán:**

| Trạng thái  | Ý nghĩa                             |
| ----------- | ----------------------------------- |
| `PENDING`   | Tạo khi đơn hàng yêu cầu thanh toán |
| `SUCCESS`   | Giao dịch thành công                |
| `FAILED`    | Giao dịch thất bại                  |
| `REFUNDED`  | Hoàn tiền                           |
| `CANCELLED` | Hủy giao dịch trước khi hoàn tất    |

**API Endpoints:**

| Method | Endpoint                 | Mô tả                            |
| ------ | ------------------------ | -------------------------------- |
| POST   | `/payments`              | Tạo giao dịch thanh toán         |
| GET    | `/payments/{id}`         | Xem chi tiết giao dịch           |
| POST   | `/payments/{id}/confirm` | Xác nhận thanh toán (giả lập)    |
| POST   | `/payments/{id}/cancel`  | Hủy giao dịch                    |
| POST   | `/payments/callback`     | Nhận callback từ payment gateway |

**Tích hợp cổng thanh toán giả lập:**

1. Customer chọn thanh toán → Payment tạo ở `PENDING`.
2. Gateway giả lập trả `SUCCESS` hoặc `FAILED`.
3. Payment Service cập nhật trạng thái.
4. Gửi kết quả về Order Service để cập nhật đơn hàng.

---

### 5.6 Shipping Service

**Vai trò:** Quản lý vận đơn, tính phí giao hàng, theo dõi trạng thái vận chuyển.

**Domain Model:**

```
Shipment
  ├── id, order_id, user_id
  ├── receiver_name, receiver_phone, address
  ├── shipping_fee, status, tracking_code
  ├── created_at
  │
ShippingRate
  ├── id, area_type, base_fee, extra_fee
  │
ShipmentStatusHistory
  ├── id, shipment_id, status, changed_at
```

**Trạng thái vận chuyển:**

| Trạng thái      | Ý nghĩa                             |
| --------------- | ----------------------------------- |
| `PENDING`       | Vận đơn vừa tạo, chưa bàn giao      |
| `READY_TO_SHIP` | Sẵn sàng giao cho đơn vị vận chuyển |
| `SHIPPING`      | Đang trên đường giao                |
| `DELIVERED`     | Giao thành công                     |
| `FAILED`        | Giao hàng thất bại                  |
| `RETURNED`      | Hoàn về                             |

**Công thức tính phí:**

```
shipping_fee = base_fee + distance_fee + weight_fee

Cấu hình cơ bản:
  Nội thành : 20.000 VND
  Ngoại thành: 35.000 VND
  Khác tỉnh : 50.000 VND
```

**API Endpoints:**

| Method | Endpoint                      | Mô tả                        |
| ------ | ----------------------------- | ---------------------------- |
| POST   | `/shipments`                  | Tạo vận đơn cho đơn hàng     |
| GET    | `/shipments/{id}`             | Xem thông tin vận chuyển     |
| GET    | `/shipments/order/{order_id}` | Xem vận chuyển theo đơn hàng |
| PATCH  | `/shipments/{id}/status`      | Cập nhật trạng thái          |
| POST   | `/shipments/calculate-fee`    | Tính phí giao hàng           |

---

## 6. LUỒNG NGHIỆP VỤ TỔNG THỂ

### 6.1 Luồng xem sản phẩm

```
Customer ──GET /api/products──► API Gateway
                                      │
                              Product Service ──► product_db
                                      │
                            Danh sách sản phẩm (phân trang)
                                      │
                              Customer ◄── Kết quả
```

### 6.2 Luồng thêm vào giỏ hàng

```
Customer chọn sản phẩm + số lượng
         │
         ▼
Cart Service nhận product_id + quantity
         │
         ├──► Product Service (kiểm tra tồn kho & active?)
         │              └── Hợp lệ
         ▼
Tạo mới / cập nhật CartItem
         │
Customer ◄── Giỏ hàng mới
```

### 6.3 Luồng đặt hàng (Checkout)

```
Customer bấm Checkout
         │
         ▼
API Gateway ──► Order Service
                    │
                    ├──1──► Cart Service (lấy CartItem)
                    ├──2──► Product Service (kiểm tra giá + tồn kho)
                    ├──3── Tạo Order (PENDING) + OrderItems (snapshot)
                    ├──4──► Payment Service (tạo giao dịch)
                    ├──5──► Shipping Service (tạo vận đơn)
                    │
Customer ◄── Mã đơn hàng + trạng thái
```

### 6.4 Luồng thanh toán

```
Order Service ──POST /payments──► Payment Service
                                        │
                              Xử lý giao dịch (giả lập)
                                        │
                         SUCCESS ◄──────┴──────► FAILED
                            │                       │
                    Update Order PAID          Giữ PENDING
                    / PROCESSING               hoặc FAILED
```

### 6.5 Luồng giao hàng

```
Shipping Service tạo Shipment
         │
PENDING ──► READY_TO_SHIP ──► SHIPPING ──► DELIVERED
                                             │
                              Thông báo về Order Service
                                             │
                              Customer theo dõi trạng thái
```

### 6.6 Sequence End-to-End (Checkout Flow)

| Bước | Nguồn           | Đích             | Hành động                  |
| ---- | --------------- | ---------------- | -------------------------- |
| 1    | Client          | API Gateway      | Gửi yêu cầu checkout       |
| 2    | API Gateway     | Order Service    | Chuyển request tạo đơn     |
| 3    | Order Service   | Cart Service     | Lấy giỏ hàng hiện tại      |
| 4    | Order Service   | Product Service  | Kiểm tra giá và tồn kho    |
| 5    | Order Service   | Payment Service  | Tạo payment ở `PENDING`    |
| 6    | Payment Service | Order Service    | Trả kết quả thanh toán     |
| 7    | Order Service   | Shipping Service | Tạo vận đơn nếu đơn hợp lệ |
| 8    | Order Service   | Client           | Trả thông tin đơn hàng     |

---

## 7. AI SERVICE — TƯ VẤN & GỢI Ý SẢN PHẨM

### 7.1 Mục tiêu

AI Service bổ trợ trải nghiệm mua sắm bằng cách:

- Gợi ý sản phẩm phù hợp với lịch sử hành vi người dùng.
- Tư vấn sản phẩm qua chatbot ngôn ngữ tự nhiên.
- Tìm kiếm sản phẩm theo ngữ nghĩa (semantic search).
- Cá nhân hóa trang chủ, trang chi tiết sản phẩm và giỏ hàng.

### 7.2 Kiến trúc AI Service

```
Frontend / Mobile App
         │
    API Gateway
         │
      AI Service
    ┌─────────────────────────────┐
    │  API Layer                  │
    │  Recommendation Engine      │
    │  Chatbot / RAG Engine       │
    │  Model Layer (LSTM, Embed)  │
    │  Data Layer                 │
    └─────────────────────────────┘
         │
    ┌────┴────────────┐
    │                 │
  LSTM Model        Neo4j          Vector DB
                Knowledge Graph   (ChromaDB)
         │
    ┌────┴───────────────┐
Product Service  User Service  Order Service
```

### 7.3 Dữ liệu hành vi người dùng

| Loại dữ liệu      | Nguồn                       | Ý nghĩa             | Trọng số gợi ý |
| ----------------- | --------------------------- | ------------------- | -------------- |
| Lượt xem sản phẩm | Frontend, Product Service   | Quan tâm            | 1              |
| Tìm kiếm sản phẩm | Search Service, API Gateway | Nhu cầu hiện tại    | 2              |
| Thêm vào giỏ hàng | Cart Service                | Mức độ quan tâm cao | 3              |
| Đánh giá tốt      | Review Service              | Hài lòng sau mua    | 4              |
| Mua hàng          | Order Service               | Quyết định thực tế  | 5              |

### 7.4 Mô hình LSTM (Sequence Modeling)

**Ý tưởng:** Hành vi mua sắm có tính tuần tự — sản phẩm trước ảnh hưởng đến quan tâm tiếp theo.

**Cấu trúc mô hình:**

```
Product Sequence (chuỗi hành vi người dùng)
         │
  Embedding Layer (chuyển product_id thành vector)
         │
     LSTM Layer (học quan hệ tuần tự)
         │
     Dense Layer / Softmax
         │
  Recommended Product (Pn+1)
```

**Ví dụ:**

```
Input:  [Laptop → Chuột → Bàn phím]
Output: [Tai nghe, Màn hình, Balo laptop]
```

**Quy trình training:**

1. Thu thập lịch sử hành vi người dùng.
2. Sắp xếp theo thứ tự thời gian.
3. Chuyển `product_id` → chỉ số số học.
4. Tạo chuỗi huấn luyện.
5. Train LSTM dự đoán sản phẩm tiếp theo.
6. Lưu model → REST API inference.

### 7.5 Knowledge Graph với Neo4j

**Node chính:** User, Product, Category, Brand, Order, Tag

**Quan hệ:** `VIEWED`, `BOUGHT`, `ADDED_TO_CART`, `BELONGS_TO`, `MADE_BY`, `SIMILAR_TO`

**Truy vấn gợi ý (Cypher):**

```cypher
MATCH (u:User {id: "U001"})-[:BOUGHT]->(p:Product)
      -[:BELONGS_TO]->(c:Category)
      <-[:BELONGS_TO]-(recommend:Product)
WHERE NOT (u)-[:BOUGHT]->(recommend)
RETURN recommend
LIMIT 5;
```

**So sánh Neo4j vs RDBMS:**

| Tiêu chí            | Neo4j                          | MySQL/PostgreSQL     |
| ------------------- | ------------------------------ | -------------------- |
| Quan hệ phức tạp    | Tự nhiên qua node/relationship | Cần nhiều JOIN table |
| Gợi ý theo quan hệ  | Phù hợp                        | Khó và chậm          |
| Dữ liệu giao dịch   | Không phải lựa chọn chính      | Phù hợp hơn          |
| Khả năng giải thích | Tốt (lần theo quan hệ)         | Khó trực quan        |

### 7.6 RAG — Chatbot tư vấn sản phẩm

**Pipeline:**

```
User Question (ngôn ngữ tự nhiên)
         │
  Text Embedding (chuyển câu hỏi → vector)
         │
  Vector Database Search (tìm sản phẩm liên quan)
         │
  Retrieve Product Documents (ngữ cảnh)
         │
  LLM Generate Answer (sinh câu trả lời dựa trên ngữ cảnh)
         │
  Response + Danh sách sản phẩm phù hợp
```

**Ví dụ:**

```
User: "Tôi cần một đôi giày chạy bộ dưới 1 triệu"

AI Service:
  → Tìm sản phẩm giày chạy bộ, giá < 1.000.000
  → Trả lời: "Bạn có thể tham khảo Giày chạy bộ X (850.000đ),
     đế êm, trọng lượng nhẹ, phù hợp chạy bộ hằng ngày."
```

**Vector Database so sánh:**

| Công nghệ    | Ưu điểm                               | Hạn chế                            |
| ------------ | ------------------------------------- | ---------------------------------- |
| **FAISS**    | Nhanh, phù hợp tìm kiếm vector cục bộ | Cần tự xây API và quản lý metadata |
| **ChromaDB** | Dễ sử dụng, phù hợp prototype         | Chưa tối ưu cho hệ thống rất lớn   |
| **Pinecone** | Managed service, dễ mở rộng           | Phụ thuộc nền tảng bên ngoài       |
| **Qdrant**   | Filtering tốt, hiệu năng cao          | Cần triển khai thêm hạ tầng        |

### 7.7 Hybrid Model

| Thành phần            | Vai trò                                              |
| --------------------- | ---------------------------------------------------- |
| **LSTM**              | Dự đoán sản phẩm tiếp theo dựa trên chuỗi hành vi    |
| **Knowledge Graph**   | Khai thác quan hệ user - product - category - brand  |
| **RAG**               | Chatbot tư vấn dựa trên dữ liệu sản phẩm             |
| **Vector Search**     | Tìm kiếm sản phẩm theo ngữ nghĩa                     |
| **Rule-based Filter** | Lọc theo giá, tồn kho, danh mục, điều kiện nghiệp vụ |

**Luồng Hybrid Recommendation:**

```
User Behavior
     │
LSTM Recommendation (ứng viên ban đầu)
     │
Knowledge Graph Expansion (mở rộng sản phẩm liên quan)
     │
Business Rule Filter (loại hết hàng, vượt ngân sách...)
     │
Ranking (sắp xếp theo điểm phù hợp)
     │
Final Recommendation List
```

### 7.8 API mẫu AI Service

**Recommendation List:**

```
GET /api/ai/recommendations?user_id=U001

Response:
{
  "user_id": "U001",
  "recommendations": [
    {
      "product_id": "P101",
      "name": "Giày chạy bộ X",
      "score": 0.92,
      "reason": "Tương tự sản phẩm bạn đã xem"
    }
  ]
}
```

**Chatbot tư vấn:**

```
POST /api/ai/chat

Request:
{ "user_id": "U001", "message": "Tôi muốn mua laptop học lập trình dưới 15 triệu" }

Response:
{
  "answer": "Bạn có thể tham khảo Laptop A (RAM 16GB, SSD 512GB, < 15 triệu)",
  "products": [{ "product_id": "P201", "name": "Laptop A", "price": 14500000 }]
}
```

### 7.9 Tech Stack AI Service

| Thành phần       | Công nghệ           |
| ---------------- | ------------------- |
| API Service      | FastAPI             |
| Machine Learning | TensorFlow / Keras  |
| Vector Database  | ChromaDB            |
| Knowledge Graph  | Neo4j               |
| Database         | PostgreSQL          |
| Message / Event  | Kafka               |
| Container        | Docker              |
| Monitoring       | Prometheus, Grafana |

---

## 8. KIẾN TRÚC TRIỂN KHAI HOÀN CHỈNH

### 8.1 API Gateway (Nginx)

| Vai trò               | Mô tả                                       |
| --------------------- | ------------------------------------------- |
| **Reverse Proxy**     | Chuyển request từ client đến service nội bộ |
| **Routing**           | Map path sang service phù hợp               |
| **Security Boundary** | Chỉ Gateway expose public port              |
| **Logging**           | Ghi log request tại entrypoint              |
| **CORS**              | Điều khiển domain được phép truy cập        |
| **Load Balancing**    | Phân phối request đến nhiều instance        |

**Routing:**

| Đường dẫn ngoài  | Service đích     |
| ---------------- | ---------------- |
| `/api/products/` | Product Service  |
| `/api/auth/`     | User Service     |
| `/api/users/`    | User Service     |
| `/api/cart/`     | Cart Service     |
| `/api/orders/`   | Order Service    |
| `/api/payments/` | Payment Service  |
| `/api/shipping/` | Shipping Service |
| `/api/ai/`       | AI Service       |

### 8.2 Xác thực JWT

**JWT Claims:**

| Claim   | Ý nghĩa                              |
| ------- | ------------------------------------ |
| `sub`   | Định danh người dùng                 |
| `email` | Email đăng nhập                      |
| `roles` | Danh sách vai trò (Customer / Admin) |
| `exp`   | Thời điểm token hết hạn              |
| `iat`   | Thời điểm phát hành                  |

**Luồng xác thực:**

```
1. Customer gửi email + password đến /api/auth/login
2. API Gateway chuyển → User Service
3. User Service kiểm tra tài khoản + password_hash
4. Sinh JWT access token
5. Client lưu token, gửi Authorization: Bearer <token>
6. Service nhận request, kiểm tra token và role
7. Hợp lệ → xử lý nghiệp vụ và trả response
```

### 8.3 Phân loại API theo bảo mật

| Nhóm API     | Người gọi          | Ví dụ                      | Bảo mật             |
| ------------ | ------------------ | -------------------------- | ------------------- |
| Public API   | Guest              | `/api/products`            | Không cần token     |
| Customer API | Customer           | `/api/cart`, `/api/orders` | JWT Customer        |
| Admin API    | Admin              | `/api/admin/products`      | JWT Admin           |
| Internal API | Service khác       | `/internal/products/{id}`  | Network nội bộ      |
| AI API       | Customer / Service | `/api/ai/recommendations`  | JWT / service token |

### 8.4 Giao tiếp giữa các Service

| Service nguồn | Service đích     | API                                | Mục đích                             |
| ------------- | ---------------- | ---------------------------------- | ------------------------------------ |
| Cart Service  | Product Service  | `GET /internal/products/{id}`      | Kiểm tra sản phẩm trước khi thêm giỏ |
| Order Service | Cart Service     | `GET /internal/carts/current`      | Lấy giỏ hàng khi tạo đơn             |
| Order Service | Product Service  | `POST /internal/inventory/reserve` | Giữ / giảm tồn kho                   |
| Order Service | Payment Service  | `POST /payments`                   | Tạo giao dịch                        |
| Order Service | Shipping Service | `POST /shipments`                  | Tạo vận đơn                          |
| AI Service    | Product Service  | `GET /products`                    | Lấy metadata sản phẩm                |

**Best Practice giao tiếp:**

| Best Practice                      | Lý do                                   |
| ---------------------------------- | --------------------------------------- |
| Không truy cập DB của service khác | Giữ ranh giới ownership dữ liệu         |
| Có timeout khi gọi API nội bộ      | Tránh request treo khi service đích lỗi |
| API contract rõ ràng               | Giảm lỗi tích hợp giữa nhiều nhóm       |
| Dùng correlation ID                | Dễ truy vết request qua nhiều service   |
| Thiết kế API idempotent            | Tránh xử lý trùng khi client retry      |
| Tránh gọi vòng tròn                | Giảm coupling và tránh deadlock         |

### 8.5 Docker hóa hệ thống

**Danh sách Container:**

| Container        | Port nội bộ | Port public | Vai trò                    |
| ---------------- | ----------- | ----------- | -------------------------- |
| api-gateway      | 80          | **8080**    | Entrypoint                 |
| product-service  | 8000        | -           | Catalog                    |
| user-service     | 8000        | -           | Xác thực                   |
| cart-service     | 8000        | -           | Giỏ hàng                   |
| order-service    | 8000        | -           | Đơn hàng                   |
| payment-service  | 8000        | -           | Thanh toán                 |
| shipping-service | 8000        | -           | Vận chuyển                 |
| ai-service       | 8000        | -           | Gợi ý & tư vấn             |
| \*-db            | 5432        | -           | Database riêng mỗi service |

**Biến môi trường:**

| Biến                   | Ý nghĩa                            |
| ---------------------- | ---------------------------------- |
| `DATABASE_URL`         | Chuỗi kết nối database của service |
| `JWT_SECRET`           | Khóa bí mật JWT                    |
| `SERVICE_NAME`         | Tên service dùng trong logging     |
| `PRODUCT_SERVICE_URL`  | URL nội bộ Product Service         |
| `PAYMENT_SERVICE_URL`  | URL nội bộ Payment Service         |
| `SHIPPING_SERVICE_URL` | URL nội bộ Shipping Service        |

### 8.6 Database — MySQL vs PostgreSQL

| Tiêu chí         | MySQL                | PostgreSQL                         |
| ---------------- | -------------------- | ---------------------------------- |
| Độ phổ biến      | Rất phổ biến, dễ học | Phổ biến trong hệ thống phức tạp   |
| Transaction      | Tốt với InnoDB       | Mạnh, tuân thủ ACID tốt            |
| JSON             | Hỗ trợ JSON          | Hỗ trợ **JSONB** mạnh và linh hoạt |
| Full-text search | Cơ bản               | Mạnh hơn cho truy vấn nâng cao     |
| Phù hợp          | Dễ cài, dễ học       | Mở rộng truy vấn phức tạp          |

### 8.7 Nguyên tắc triển khai

| Nguyên tắc                     | Cách áp dụng                                             |
| ------------------------------ | -------------------------------------------------------- |
| **Database per service**       | Mỗi service có DB riêng, không cho service khác truy cập |
| **Loose coupling**             | Giao tiếp qua REST API / event, không phụ thuộc code     |
| **High cohesion**              | Mỗi service tập trung vào một nhóm nghiệp vụ             |
| **Independent deployment**     | Mỗi service có Dockerfile riêng                          |
| **Stateless service**          | Không lưu session trong bộ nhớ cục bộ                    |
| **Externalized configuration** | DB URL, secret key qua biến môi trường                   |
| **Observability**              | Log, health check và metrics mỗi service                 |

---

## 9. BẢO MẬT HỆ THỐNG

| Rủi ro                        | Giải pháp                                            |
| ----------------------------- | ---------------------------------------------------- |
| Truy cập API trái phép        | JWT + phân quyền RBAC                                |
| Lộ mật khẩu                   | Hash password trước khi lưu vào database             |
| Gọi internal API từ bên ngoài | Chỉ expose API Gateway, không expose service nội bộ  |
| Lộ secret trong source code   | Dùng biến môi trường, `.env` không commit lên git    |
| Request quá nhiều (DDoS)      | Cấu hình rate limit tại API Gateway                  |
| Dữ liệu đầu vào không hợp lệ  | Validate request bằng serializer/schema tại boundary |
| CORS sai cấu hình             | Chỉ allow domain client hợp lệ                       |

---

## 10. ĐÁNH GIÁ HỆ THỐNG

### 10.1 Hiệu năng mong muốn

| Tiêu chí              | Mục tiêu                                 |
| --------------------- | ---------------------------------------- |
| API đọc dữ liệu (GET) | < 500ms                                  |
| API tạo đơn hàng      | < 2s                                     |
| Tỷ lệ thành công      | > 99%                                    |
| Throughput            | Đủ cho tải thông thường và scale khi cần |

### 10.2 Khả năng mở rộng

| Service         | Đặc điểm scale                               |
| --------------- | -------------------------------------------- |
| Product Service | Scale nhiều trong đợt khuyến mãi (đọc nhiều) |
| Cart Service    | Scale theo lượng người dùng đồng thời        |
| Order Service   | Scale theo tần suất đặt hàng                 |
| Payment Service | Scale theo giao dịch, cần reliability cao    |
| AI Service      | Scale riêng, không ảnh hưởng nghiệp vụ lõi   |

### 10.3 Ưu điểm kiến trúc

- **Mở rộng độc lập:** Chỉ scale service cần thiết, tiết kiệm tài nguyên.
- **Triển khai độc lập:** Cập nhật Payment mà không deploy lại Product.
- **Cô lập lỗi:** Payment lỗi vẫn cho xem sản phẩm và giỏ hàng.
- **Phát triển song song:** Nhiều nhóm làm việc đồng thời trên các service khác nhau.
- **Công nghệ linh hoạt:** Mỗi service chọn DB/stack phù hợp nhất.
- **Tích hợp AI dễ dàng:** AI Service thêm vào hệ thống mà không ảnh hưởng core.

### 10.4 Nhược điểm & thách thức

- **Độ phức tạp vận hành:** Cần quản lý nhiều service, DB, network, logging phân tán.
- **Eventual consistency:** Không thể dùng transaction đơn giản xuyên service.
- **Debugging khó hơn:** Lỗi có thể xảy ra ở bất kỳ service nào trong luồng.
- **Chi phí hạ tầng:** Cần service discovery, API Gateway, container orchestration.
- **Giao tiếp qua mạng:** Mỗi lời gọi giữa service là network call — có thể timeout/fail.

### 10.5 So sánh lựa chọn triển khai

| Lựa chọn           | Ưu điểm                     | Nhược điểm             | Quyết định                  |
| ------------------ | --------------------------- | ---------------------- | --------------------------- |
| **REST API**       | Dễ hiểu, dễ test            | Coupling runtime       | **Dùng chính**              |
| **Message Queue**  | Giảm coupling, bất đồng bộ  | Phức tạp hơn           | Hướng mở rộng               |
| **Docker Compose** | Dễ chạy local/demo          | Chưa tối ưu production | **Dùng cho môi trường học** |
| **Kubernetes**     | Scale tốt, production-ready | Cần nhiều cấu hình     | Optional                    |

---

## PHỤ LỤC — CHECKLIST THIẾT KẾ

### Checklist Chapter 2 — E-Commerce Microservices

| Tiêu chí                                         | Trạng thái |
| ------------------------------------------------ | ---------- |
| Xác định đủ actor chính của hệ thống             | ✅ Đạt     |
| Có danh sách Functional Requirements             | ✅ Đạt     |
| Có danh sách Non-functional Requirements         | ✅ Đạt     |
| Có Bounded Context và Context Map                | ✅ Đạt     |
| Có ít nhất 6 service cốt lõi                     | ✅ Đạt     |
| Mỗi service có model và API                      | ✅ Đạt     |
| Mỗi service có database riêng                    | ✅ Đạt     |
| Có workflow checkout tổng thể                    | ✅ Đạt     |
| Có giải thích consistency & transaction boundary | ✅ Đạt     |

### Checklist Chapter 3 — AI Service

| Tiêu chí                           | Trạng thái |
| ---------------------------------- | ---------- |
| Có mô tả mục tiêu AI Service       | ✅ Đạt     |
| Có thiết kế Recommendation List    | ✅ Đạt     |
| Có thiết kế Chatbot tư vấn         | ✅ Đạt     |
| Có giải thích mô hình LSTM         | ✅ Đạt     |
| Có mô tả Knowledge Graph với Neo4j | ✅ Đạt     |
| Có mô tả RAG pipeline              | ✅ Đạt     |
| Có API mẫu cho AI Service          | ✅ Đạt     |
| Có tech stack triển khai           | ✅ Đạt     |
| Có so sánh công nghệ thay thế      | ✅ Đạt     |
