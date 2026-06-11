# Kế Hoạch Loại Bỏ `book-service` — Chỉ Dùng `product-service`

> **Repo:** Shadow23434/microservices-store  
> **Mục tiêu:** Xoá hoàn toàn `book-service`, mọi chức năng chạy qua `product-service`  

---

## Tổng Quan Hiện Trạng

Sau khi đọc toàn bộ source code, dưới đây là những gì **đã làm xong** và **còn thiếu**:

### ✅ Đã Làm Xong (Không Cần Động Vào)

| Thành phần | Trạng thái |
|---|---|
| `product-service/` — models, views, serializers, urls, settings | Hoàn chỉnh |
| `cart-service` — `CartItem.product_id`, gọi `PRODUCT_SERVICE_URL` | ✅ |
| `order-service` — `OrderItem.product_id/product_name/product_type`, gọi `PRODUCT_SERVICE_URL` | ✅ |
| `comment-rate-service` — `Review.product_id/product_type` | ✅ |
| `recommender-ai-service` — gọi `PRODUCT_SERVICE_URL` | ✅ |
| `docker-compose.yml` — `product-service` container đã định nghĩa với `product_db` | ✅ |
| `api-gateway/views.py` — `book_list()` đã gọi product-service | ✅ |
| `api-gateway/views.py` — đã có `"products"` trong `SERVICES` dict | ✅ |
| `frontend/src/api/productService.ts` — đầy đủ | ✅ |
| `frontend/src/types.ts` — có `Product`, `ProductReview`, `CartItemProduct` | ✅ |

### ❌ Còn Cần Làm (6 Phase bên dưới)

---

## Phase 1 — Tạo Migration cho `product-service` ⚡ CHẠY TRƯỚC TIÊN

**Vấn đề:** Thư mục `product-service/product_service/app/migrations/` chỉ có `__init__.py`, chưa có migration nào. Service sẽ crash ngay khi khởi động.

### Bước 1.1 — Tạo migration file

```bash
# Chạy trong container hoặc local venv của product-service
cd product-service/product_service
python manage.py makemigrations app
python manage.py migrate
```

Lệnh này tạo ra file `app/migrations/0001_initial.py` gồm 5 bảng:
`products`, `book_details`, `laptop_details`, `mobile_details`, `cloth_details`

**Kiểm tra sau khi tạo:**
```bash
python manage.py showmigrations app
# ✅ Kết quả mong đợi:
# app
#  [X] 0001_initial
```

### Bước 1.2 — Chạy thử product-service độc lập

```bash
docker compose up --build product-service
docker compose exec product-service python manage.py showmigrations
curl http://localhost:8888/api/products/
# ✅ Phải trả về: {"count":0,"next":null,"previous":null,"results":[]}
```

---

## Phase 2 — Dọn `docker-compose.yml`

**File:** `docker-compose.yml`

Cần thực hiện **3 thay đổi** trong file này:

### Bước 2.1 — Xoá block `book-service`

```yaml
# XOÁ toàn bộ block này:
book-service:
  build:
    context: .
    dockerfile: book-service/Dockerfile
  env_file: .env
  environment:
    DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/book_db
  depends_on:
    postgres:
      condition: service_healthy
```

### Bước 2.2 — Xoá `book_db` khỏi postgres

```yaml
# TRƯỚC:
POSTGRES_MULTIPLE_DATABASES: >
  customer_db,book_db,product_db,cart_db,...

# SAU:
POSTGRES_MULTIPLE_DATABASES: >
  customer_db,product_db,cart_db,staff_db,manager_db,
  catalog_db,order_db,ship_db,pay_db,
  comment_rate_db,recommender_db,gateway_db
```

### Bước 2.3 — Xoá `book-service` khỏi `depends_on` của `api-gateway` và xoá env `BOOK_SERVICE_URL`

```yaml
# TRƯỚC:
api-gateway:
  environment:
    PRODUCT_SERVICE_URL: http://product-service:8888
    BOOK_SERVICE_URL: http://book-service:8888   # ← XOÁ dòng này
    ...
  depends_on:
    book-service:           # ← XOÁ 3 dòng này
      condition: service_started
    product-service:
      condition: service_started
    ...
```

---

## Phase 3 — Dọn `api-gateway`

### Bước 3.1 — `api-gateway/api_gateway/app/views.py`: Xoá entry `"books"` khỏi SERVICES

```python
# TRƯỚC:
SERVICES = {
    "customers": os.environ.get("CUSTOMER_SERVICE_URL", ...),
    "products":  os.environ.get("PRODUCT_SERVICE_URL", "http://product-service:8888"),
    "books":     os.environ.get("BOOK_SERVICE_URL", "http://book-service:8888"),  # ← XOÁ
    "carts":     os.environ.get("CART_SERVICE_URL", ...),
    ...
}

# SAU:
SERVICES = {
    "customers":       os.environ.get("CUSTOMER_SERVICE_URL", "http://customer-service:8888"),
    "products":        os.environ.get("PRODUCT_SERVICE_URL", "http://product-service:8888"),
    "carts":           os.environ.get("CART_SERVICE_URL", "http://cart-service:8888"),
    "staff":           os.environ.get("STAFF_SERVICE_URL", "http://staff-service:8888"),
    "managers":        os.environ.get("MANAGER_SERVICE_URL", "http://manager-service:8888"),
    "categories":      os.environ.get("CATALOG_SERVICE_URL", "http://catalog-service:8888"),
    "orders":          os.environ.get("ORDER_SERVICE_URL", "http://order-service:8888"),
    "shipments":       os.environ.get("SHIP_SERVICE_URL", "http://ship-service:8888"),
    "payments":        os.environ.get("PAY_SERVICE_URL", "http://pay-service:8888"),
    "reviews":         os.environ.get("COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8888"),
    "recommendations": os.environ.get("RECOMMENDER_SERVICE_URL", "http://recommender-ai-service:8888"),
}
```

> Sau khi xoá, `GET /api/books/` sẽ trả 404. Để duy trì backward compat tạm thời, xem Bước 3.2.

### Bước 3.2 (Tuỳ chọn) — Thêm redirect `/api/books/` → `/api/products/?product_type=book`

Nếu frontend hoặc client bên ngoài vẫn cần dùng `/api/books/`, thêm route redirect trong `GatewayView.dispatch()`:

```python
def dispatch(self, request, resource, path="", *args, **kwargs):
    # Backward compat: /api/books/ → /api/products/?product_type=book
    if resource == "books":
        base_url = SERVICES["products"]
        full_path = f"products/{path}" if path else "products/"
        params = request.GET.copy()
        if not path:  # list endpoint chỉ, không phải /api/books/{id}/
            params["product_type"] = "book"
        request.GET = params
        return _proxy(request, base_url, full_path)

    if resource not in SERVICES:
        return JsonResponse({"error": f"Unknown resource: {resource}"}, status=404)
    base_url = SERVICES[resource]
    full_path = f"{resource}/{path}" if path else f"{resource}/"
    return _proxy(request, base_url, full_path)
```

### Bước 3.3 — `api-gateway/api_gateway/api_gateway/urls.py`: Đổi tên route `books/` thành `products/`

```python
# TRƯỚC:
from app.views import (..., book_list, ...)
urlpatterns = [
    ...
    path("books/", book_list, name="book-list"),  # ← đổi
    ...
]

# SAU (đổi cả URL lẫn function name):
from app.views import (..., product_list, ...)   # đổi import
urlpatterns = [
    ...
    path("products/", product_list, name="product-list"),  # ← URL mới
    path("books/",    product_list, name="book-list"),      # ← giữ alias tạm
    ...
]
```

Và đổi tên hàm trong `views.py`:
```python
# TRƯỚC:
def book_list(request):
    try:
        r = requests.get(f"{SERVICES['products']}/api/products/?product_type=book", timeout=5)
        ...
    return render(request, "books.html", {"books": books})

# SAU:
def product_list(request):
    product_type = request.GET.get("product_type", "")
    url = f"{SERVICES['products']}/api/products/"
    if product_type:
        url += f"?product_type={product_type}"
    try:
        r = requests.get(url, timeout=5)
        response_data = r.json()
        products = response_data.get("results", response_data) if isinstance(response_data, dict) else response_data
    except Exception:
        products = []
    return render(request, "products.html", {"products": products, "product_type": product_type})
```

---

## Phase 4 — Frontend (React/TypeScript)

Đây là phase có nhiều thay đổi nhất. Có **2 nhóm**:

- **Nhóm A (Logic nghiệp vụ):** Ảnh hưởng trực tiếp đến API call — phải sửa
- **Nhóm B (Đặt tên biến):** Chỉ đổi tên biến `bookId` → `productId` — làm sau hoặc để nguyên vẫn chạy được

---

### 4-A. `frontend/src/pages/Checkout.tsx` — QUAN TRỌNG (bug nếu không sửa)

Dòng 46 đang gửi sai field name lên order-service:

```typescript
// TRƯỚC (SAI — order-service không nhận book_id):
items.map(item => ({
  book_id: item.id,         // ← PHẢI ĐỔI
  quantity: item.quantity,
  unit_price: item.unit_price,
}))

// SAU (ĐÚNG):
items.map(item => ({
  product_id: item.id,      // ← product_id
  quantity: item.quantity,
  unit_price: item.unit_price,
}))
```

---

### 4-B. `frontend/src/pages/Home.tsx` — Đổi sang productService

```typescript
// TRƯỚC:
import bookService from '../api/bookService';
...
const allBooks = await bookService.getAllBooks() as unknown as any[];

// SAU:
import productService from '../api/productService';
...
const allProducts = await productService.getAllProducts() as unknown as any[];
// Nếu chỉ muốn sách: productService.getBooks()
```

---

### 4-C. `frontend/src/pages/Catalog.tsx` — Đổi sang productService

```typescript
// TRƯỚC:
import bookService from '../api/bookService';
...
bookService.getAllBooks() as unknown as any[]

// SAU:
import productService from '../api/productService';
...
productService.getAllProducts()
```

---

### 4-D. `frontend/src/pages/BookDetail.tsx` — Đổi sang productService

```typescript
// TRƯỚC:
import bookService from '../api/bookService';
...
bookService.getBookById(id)

// SAU:
import productService from '../api/productService';
...
productService.getProductById(id)
```

**Lưu ý:** Trang này render fields của `Book` (title, author, isbn...).
Sau khi đổi API, phải cập nhật render: dùng `product.name` thay `book.title`, lấy `author` từ `product.detail.author`, v.v.

---

### 4-E. `frontend/src/pages/Account.tsx` — Đổi sang productService + sửa field names

```typescript
// TRƯỚC:
import bookService from '../api/bookService';
...
const booksList = await bookService.getAllBooks()
const bookId = r.book_id || r.bookId;
const book = booksList.find((b: any) => b.id === bookId);

// SAU:
import productService from '../api/productService';
...
const productsList = await productService.getAllProducts()
const productId = r.product_id;
const product = productsList.find((p: any) => p.id === productId);
```

Sửa link review (dòng 418):
```typescript
// TRƯỚC:
<Link to={`/book/${review.book_id || review.bookId}`}>
  {review.bookTitle || `Book ID: ${review.book_id}`}
</Link>

// SAU:
<Link to={`/product/${review.product_id}`}>
  {review.productName || `Product ID: ${review.product_id}`}
</Link>
```

---

### 4-F. `frontend/src/api/reviewService.ts` — Đổi param `book_id` → `product_id`

```typescript
// TRƯỚC:
const reviewService = {
  getReviews: (params?: { book_id?: number; customer_id?: number }) =>
    axiosClient.get('/api/reviews/', { params }),
  ...
  getBookRating: (bookId: number) =>
    axiosClient.get(`/api/reviews/book/${bookId}/rating/`),
};

// SAU:
const reviewService = {
  getReviews: (params?: { product_id?: number; customer_id?: number }) =>
    axiosClient.get('/api/reviews/', { params }),
  ...
  getProductRating: (productId: number) =>
    axiosClient.get(`/api/reviews/?product_id=${productId}`),
};
```

---

### 4-G. `frontend/src/types.ts` — Cập nhật `CartItem` và `Review`

```typescript
// TRƯỚC:
export interface CartItem extends Book {   // ← kéo theo Book interface cũ
  quantity: number;
}

export interface Review {
  id: string;
  bookId: number;          // ← đổi
  bookTitle: string;       // ← đổi
  bookImage: string;       // ← đổi
  ...
}

// SAU:
export interface CartItem extends Product {  // ← dùng Product interface mới
  quantity: number;
}

// Hoặc dùng CartItemProduct đã có sẵn trong types.ts:
// export interface CartItemProduct { id, product_id, product, quantity, unit_price }

export interface Review {
  id: string;
  product_id: number;      // ← đổi
  productName: string;     // ← đổi
  productImage: string;    // ← đổi
  ...
}
```

---

### 4-H. `frontend/src/contexts/CartContext.tsx` — `addToCart` dùng `Product` thay `Book`

```typescript
// TRƯỚC:
import { Book, CartItem } from '../types';
...
const addToCart = (book: Book, quantity: number = 1) => { ... }

// SAU:
import { Product, CartItem } from '../types';
...
const addToCart = (product: Product, quantity: number = 1) => { ... }
```

---

### 4-I. `frontend/src/contexts/ReviewContext.tsx` — Đổi `bookId` → `productId`

```typescript
// TRƯỚC:
getReviewsByBookId: (bookId: number) => Review[];
...
const getReviewsByBookId = (bookId: number) => {
  return reviews.filter(r => Number(r.bookId) === Number(bookId));
};

// SAU:
getReviewsByProductId: (productId: number) => Review[];
...
const getReviewsByProductId = (productId: number) => {
  return reviews.filter(r => Number(r.product_id) === Number(productId));
};
```

---

### 4-J. Xoá `frontend/src/api/bookService.ts`

File này có thể xoá sau khi tất cả trang đã đổi sang dùng `productService`. Dùng lệnh:
```bash
git rm frontend/src/api/bookService.ts
```

---

## Phase 5 — Cập nhật `scripts/seed_all_services.py`

File hiện tại seed thẳng vào `book_db` và có nhiều tham chiếu `book_id`, `book_title`. Cần sửa:

### Bước 5.1 — Xoá reference đến `book_db` và `BOOK_SERVICE_URL`

```python
# TRƯỚC:
BOOK_SERVICE_URL = "http://localhost:8888/api/books/"
DB_URLS = {
    'books':   get_db_url('book_db'),   # ← XOÁ
    'products': get_db_url('product_db'),
    ...
}

# SAU:
DB_URLS = {
    'products': get_db_url('product_db'),
    'carts':    get_db_url('cart_db'),
    ...
}
```

### Bước 5.2 — Chuyển BOOKS_DATA sang seed vào product-service qua API

```python
# TRƯỚC: seed trực tiếp vào book_db bằng SQL
conn = psycopg2.connect(DB_URLS['books'])
cursor.execute("INSERT INTO app_book (title, author, price, ...) VALUES (%s, ...)", ...)

# SAU: seed qua product-service API
PRODUCT_SERVICE_URL = "http://localhost:8888/api/products/"

for book in BOOKS_DATA:
    payload = {
        "name":         book["title"],
        "product_type": "book",
        "price":        book["price"],
        "stock":        book["stock"],
        "description":  book.get("desc", ""),
        "image_url":    book.get("image", ""),
        "detail": {
            "author":   book["author"],
            "isbn":     book.get("isbn", ""),
            "publisher": book.get("publisher", ""),
            "pages":    book.get("pages"),
            "language": book.get("language", "en"),
        }
    }
    requests.post(PRODUCT_SERVICE_URL, json=payload)
```

### Bước 5.3 — Đổi `book_title` → `product_id` trong REVIEWS_DATA

```python
# TRƯỚC:
REVIEWS_DATA = [
    {"customer_email": "mai@example.com", "book_title": "Clean Code", "rating": 5, ...},
    ...
]
# Dùng book_title để lookup book → lấy ID → tạo review

# SAU:
# Sau khi seed products xong, lưu mapping title → product_id
# Sau đó tạo review với product_id thật
```

### Bước 5.4 — Đổi `book_id` trong ORDERS_DATA thành `product_id`

```python
# TRƯỚC:
{"book_title": "Fluent Python", "qty": 1, "price": 24.99}

# SAU:
{"product_id": <id_từ_product_service>, "qty": 1, "price": 24.99}
```

---

## Phase 6 — Cleanup Cuối Cùng

Sau khi test toàn bộ hệ thống hoạt động ổn định:

### Bước 6.1 — Xoá thư mục `book-service/`

```bash
git rm -r book-service/
git commit -m "chore: remove book-service, fully migrated to product-service"
```

### Bước 6.2 — Xoá alias route trong api-gateway (nếu đã thêm ở Bước 3.2)

```python
# Xoá dòng này khỏi urls.py (nếu đã thêm):
path("books/", product_list, name="book-list"),
```

### Bước 6.3 — Cập nhật README.md

Đổi bảng services:
```markdown
| `product-service` | Quản lý sản phẩm | Hỗ trợ book, laptop, mobile, cloth |
```

Đổi bảng API routes:
```markdown
+-- /api/products/  -> product-service   (hỗ trợ ?product_type=book|laptop|mobile|cloth)
```

Xoá dòng:
```markdown
+-- /api/books/     -> book-service      # ← XOÁ
```

### Bước 6.4 — Cập nhật CLAUDE.md

Phản ánh kiến trúc mới: không còn `book-service`.

---

## Thứ Tự Thực Hiện Khuyến Nghị

```
Ngày 1 (Backend)
├── Phase 1: Tạo migration cho product-service              [30 phút]
├── Phase 2: Dọn docker-compose.yml                        [30 phút]
├── Phase 3: Dọn api-gateway (SERVICES + route)            [1 giờ]
└── Test: docker compose up --build && curl tests           [1 giờ]

Ngày 2 (Frontend — Logic)
├── Phase 4A: Checkout.tsx — sửa book_id → product_id      [15 phút] ⚡ bug fix
├── Phase 4B–4E: Home, Catalog, BookDetail, Account pages  [2 giờ]
├── Phase 4F–4G: reviewService.ts, types.ts                [1 giờ]
└── Test: npm run dev + kiểm tra flow mua hàng             [1 giờ]

Ngày 3 (Frontend — Cleanup + Seed + Final)
├── Phase 4H–4J: Contexts + xoá bookService.ts             [1 giờ]
├── Phase 5: Cập nhật seed_all_services.py                 [2 giờ]
├── Phase 6: Xoá book-service/, dọn docs                   [30 phút]
└── Final test: docker compose up + seed + full flow       [1 giờ]
```

---

## Checklist Tổng Hợp

### Phase 1 — product-service migrations
- [ ] `python manage.py makemigrations app` → tạo `0001_initial.py`
- [ ] `python manage.py migrate`
- [ ] Test: `GET /api/products/` trả `{"count":0,"results":[]}`

### Phase 2 — docker-compose.yml
- [ ] Xoá block `book-service:`
- [ ] Xoá `book_db` khỏi `POSTGRES_MULTIPLE_DATABASES`
- [ ] Xoá `BOOK_SERVICE_URL` khỏi env api-gateway
- [ ] Xoá `book-service` khỏi `depends_on` của api-gateway
- [ ] Test: `docker compose up --build` không có lỗi

### Phase 3 — api-gateway
- [ ] Xoá `"books": BOOK_SERVICE_URL` khỏi `SERVICES` dict
- [ ] (Tuỳ chọn) Thêm redirect `/api/books/` → product-service
- [ ] Đổi tên `book_list` → `product_list`
- [ ] Đổi URL `/books/` → `/products/` trong urls.py
- [ ] Test: `GET /api/products/` qua gateway hoạt động
- [ ] Test: `GET /api/books/` trả 404 (hoặc redirect nếu có bước 3.2)

### Phase 4 — Frontend
- [ ] **Checkout.tsx:** `book_id` → `product_id` trong payload
- [ ] **Home.tsx:** đổi sang `productService.getAllProducts()`
- [ ] **Catalog.tsx:** đổi sang `productService.getAllProducts()`
- [ ] **BookDetail.tsx:** đổi sang `productService.getProductById()`
- [ ] **Account.tsx:** đổi sang `productService`, sửa `book_id` → `product_id`
- [ ] **reviewService.ts:** `book_id` → `product_id`, `getBookRating` → `getProductRating`
- [ ] **types.ts:** `CartItem extends Product`, `Review.bookId` → `Review.product_id`
- [ ] **CartContext.tsx:** `addToCart(book: Book)` → `addToCart(product: Product)`
- [ ] **ReviewContext.tsx:** `getReviewsByBookId` → `getReviewsByProductId`
- [ ] **Xoá** `frontend/src/api/bookService.ts`
- [ ] Test: npm run dev, thêm sản phẩm vào giỏ, checkout

### Phase 5 — Seed scripts
- [ ] Xoá `BOOK_SERVICE_URL` và `book_db` reference
- [ ] Seed books qua product-service API thay vì SQL trực tiếp
- [ ] Đổi `book_title` → `product_id` trong REVIEWS_DATA
- [ ] Đổi `book_id` → `product_id` trong ORDERS_DATA
- [ ] Test: chạy seed, verify data hiện đúng

### Phase 6 — Cleanup
- [ ] `git rm -r book-service/`
- [ ] Xoá alias `/books/` route (nếu không cần nữa)
- [ ] Cập nhật README.md
- [ ] Cập nhật CLAUDE.md
- [ ] `docker compose down -v && docker compose up --build`
- [ ] Final test: full user flow (browse → add to cart → checkout)

---

## Rủi Ro Cần Lưu Ý

| Rủi ro | Mức độ | Giải pháp |
|---|---|---|
| `product-service` không có migrations → crash ngay khi start | **Cao** | Phase 1 phải làm trước khi bất kỳ service nào start |
| `Checkout.tsx` gửi `book_id` thay `product_id` → order-service bỏ qua `product_name` | **Cao** | Phase 4A là bug fix ưu tiên cao |
| `book_db` bị xoá nhưng postgres volume cũ vẫn tồn tại | Thấp | `docker compose down -v` trước khi rebuild |
| Frontend trang BookDetail render sai field sau đổi API | Trung bình | Kiểm tra `product.name` vs `book.title`, `product.detail.author` vs `book.author` |

---

> **Ghi chú quan trọng:** Vì `product-service` chưa có migration file, toàn bộ hệ thống hiện tại **sẽ không chạy được** nếu khởi động với `product-service` (container sẽ crash). Phase 1 là việc đầu tiên phải làm.
