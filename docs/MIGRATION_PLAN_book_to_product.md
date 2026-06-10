# Kế Hoạch Chuyển Đổi: Book → Product (Multi-type)

> **Repository:** [Shadow23434/microservices-store](https://github.com/Shadow23434/microservices-store)
> **Mục tiêu:** Thay thế model `Book` đơn loại bằng model `Product` dùng chung, hỗ trợ nhiều loại sản phẩm: `book`, `laptop`, `mobile`, `cloth`, ...

---

## Mục Lục

1. [Phân tích hiện trạng](#1-phân-tích-hiện-trạng)
2. [Thiết kế model mới](#2-thiết-kế-model-mới)
3. [Chiến lược migration tổng thể](#3-chiến-lược-migration-tổng-thể)
4. [Phase 1 – Core: product-service](#phase-1--core-product-service)
5. [Phase 2 – Dependent services](#phase-2--dependent-services)
6. [Phase 3 – API Gateway & Proxy routes](#phase-3--api-gateway--proxy-routes)
7. [Phase 4 – Frontend](#phase-4--frontend)
8. [Phase 5 – Data migration](#phase-5--data-migration)
9. [Phase 6 – Cleanup & documentation](#phase-6--cleanup--documentation)
10. [Checklist tổng hợp](#checklist-tổng-hợp)
11. [Rủi ro & rollback](#rủi-ro--rollback)

---

## 1. Phân Tích Hiện Trạng

### 1.1 Các service bị ảnh hưởng

| Service | Mức độ thay đổi | Lý do |
|---|---|---|
| `book-service` | 🔴 **Cao** – đổi tên & cấu trúc hoàn toàn | Trở thành `product-service` |
| `cart-service` | 🔴 **Cao** | Tham chiếu `book_id` → `product_id` |
| `order-service` | 🔴 **Cao** | `OrderItem` chứa `book_id`, `book_title`, `book_price` |
| `catalog-service` | 🟡 **Trung bình** | Category cần nhận diện loại sản phẩm |
| `comment-rate-service` | 🟡 **Trung bình** | Review gắn với `book_id` → `product_id` |
| `recommender-ai-service` | 🟡 **Trung bình** | Feed dữ liệu từ book-service → product-service |
| `api-gateway` | 🟡 **Trung bình** | Route `/api/books/` → `/api/products/`, cập nhật UI templates |
| `customer-service` | 🟢 **Thấp** | Không tham chiếu book trực tiếp |
| `frontend` | 🟡 **Trung bình** | Tất cả API call và UI liên quan đến book |
| `docker-compose.yml` | 🟢 **Thấp** | Đổi tên service, biến môi trường |
| `scripts/seed_*.py` | 🟢 **Thấp** | Cập nhật seed data |

### 1.2 Model Book hiện tại (ước lượng)

```python
# book-service/book_service/app/models.py
class Book(models.Model):
    title       = models.CharField(max_length=255)
    author      = models.CharField(max_length=255)
    isbn        = models.CharField(max_length=20, unique=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    category_id = models.IntegerField(null=True)   # FK logic tới catalog-service
    image_url   = models.URLField(blank=True)
    publisher   = models.CharField(max_length=255, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
```

### 1.3 Cart item hiện tại (ước lượng)

```python
# cart-service
class CartItem(models.Model):
    cart       = models.ForeignKey(Cart, ...)
    book_id    = models.IntegerField()     # ← phải đổi thành product_id
    quantity   = models.IntegerField()
    unit_price = models.DecimalField(...)
```

### 1.4 Order item hiện tại (ước lượng)

```python
# order-service
class OrderItem(models.Model):
    order      = models.ForeignKey(Order, ...)
    book_id    = models.IntegerField()       # ← product_id
    quantity   = models.IntegerField()
    unit_price = models.DecimalField(...)
```

---

## 2. Thiết Kế Model Mới

### 2.1 Lựa chọn pattern

Với Django + microservices dùng PostgreSQL, pattern phù hợp nhất là **Multi-table inheritance (MTI)** kết hợp **One-to-One extension tables**:

```
┌─────────────────────────────────────────────┐
│                   Product                   │  ← bảng dùng chung
│  id, name, price, stock, description,       │
│  category_id, image_url, product_type,      │
│  created_at, updated_at                     │
└──────────────┬──────────────────────────────┘
               │ OneToOne FK (product_id)
    ┌──────────┼──────────┬──────────────┐
    ▼          ▼          ▼              ▼
┌────────┐ ┌────────┐ ┌────────┐  ┌─────────┐
│BookDet │ │LaptopD │ │MobileD │  │ClothDet │
│author  │ │brand   │ │brand   │  │brand    │
│isbn    │ │cpu     │ │screen  │  │size     │
│pages   │ │ram     │ │battery │  │color    │
│...     │ │...     │ │...     │  │...      │
└────────┘ └────────┘ └────────┘  └─────────┘
```

**Lý do chọn pattern này:**
- Truy vấn linh hoạt: filter sản phẩm theo type mà không JOIN phức tạp
- Dễ thêm loại sản phẩm mới: chỉ cần tạo thêm bảng detail
- Không bloat bảng chính với hàng chục trường nullable
- Phù hợp Django ORM và migration workflow

### 2.2 Model Product chung

```python
# product-service/product_service/app/models.py

class ProductType(models.TextChoices):
    BOOK   = 'book',   'Sách'
    LAPTOP = 'laptop', 'Laptop'
    MOBILE = 'mobile', 'Điện thoại'
    CLOTH  = 'cloth',  'Quần áo'
    # Thêm loại mới tại đây

class Product(models.Model):
    name         = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50, choices=ProductType.choices)
    price        = models.DecimalField(max_digits=12, decimal_places=2)
    stock        = models.IntegerField(default=0)
    description  = models.TextField(blank=True)
    category_id  = models.IntegerField(null=True, blank=True)
    image_url    = models.URLField(blank=True)
    sku          = models.CharField(max_length=100, unique=True, blank=True)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.product_type}] {self.name}"
```

### 2.3 Model chi tiết từng loại sản phẩm

```python
class BookDetail(models.Model):
    product      = models.OneToOneField(Product, on_delete=models.CASCADE,
                                        related_name='book_detail')
    author       = models.CharField(max_length=255)
    isbn         = models.CharField(max_length=20, unique=True, blank=True)
    publisher    = models.CharField(max_length=255, blank=True)
    published_date = models.DateField(null=True, blank=True)
    pages        = models.IntegerField(null=True, blank=True)
    language     = models.CharField(max_length=50, default='vi')

    class Meta:
        db_table = 'book_details'


class LaptopDetail(models.Model):
    product      = models.OneToOneField(Product, on_delete=models.CASCADE,
                                        related_name='laptop_detail')
    brand        = models.CharField(max_length=100)
    cpu          = models.CharField(max_length=255, blank=True)
    ram_gb       = models.IntegerField(null=True, blank=True)
    storage_gb   = models.IntegerField(null=True, blank=True)
    display_inch = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    os           = models.CharField(max_length=100, blank=True)
    weight_kg    = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    gpu          = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'laptop_details'


class MobileDetail(models.Model):
    product      = models.OneToOneField(Product, on_delete=models.CASCADE,
                                        related_name='mobile_detail')
    brand        = models.CharField(max_length=100)
    screen_inch  = models.DecimalField(max_digits=4, decimal_places=1, null=True)
    battery_mah  = models.IntegerField(null=True, blank=True)
    ram_gb       = models.IntegerField(null=True, blank=True)
    storage_gb   = models.IntegerField(null=True, blank=True)
    camera_mp    = models.IntegerField(null=True, blank=True)
    os           = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'mobile_details'


class ClothDetail(models.Model):
    product      = models.OneToOneField(Product, on_delete=models.CASCADE,
                                        related_name='cloth_detail')
    brand        = models.CharField(max_length=100, blank=True)
    sizes        = models.CharField(max_length=100, blank=True)   # "S,M,L,XL"
    color        = models.CharField(max_length=100, blank=True)
    material     = models.CharField(max_length=100, blank=True)
    gender       = models.CharField(max_length=20, blank=True)    # male/female/unisex

    class Meta:
        db_table = 'cloth_details'
```

### 2.4 Serializers

```python
# product-service/product_service/app/serializers.py

class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BookDetail
        exclude = ['product']

class LaptopDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LaptopDetail
        exclude = ['product']

class MobileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MobileDetail
        exclude = ['product']

class ClothDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ClothDetail
        exclude = ['product']

class ProductSerializer(serializers.ModelSerializer):
    detail = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = '__all__'

    def get_detail(self, obj):
        detail_map = {
            'book':   ('book_detail',   BookDetailSerializer),
            'laptop': ('laptop_detail', LaptopDetailSerializer),
            'mobile': ('mobile_detail', MobileDetailSerializer),
            'cloth':  ('cloth_detail',  ClothDetailSerializer),
        }
        related_name, serializer_cls = detail_map.get(obj.product_type, (None, None))
        if not related_name:
            return None
        detail_obj = getattr(obj, related_name, None)
        if detail_obj is None:
            return None
        return serializer_cls(detail_obj).data
```

### 2.5 Thay đổi trong catalog-service

Catalog cần thêm trường `applicable_types` để biết category nào dùng cho loại sản phẩm nào:

```python
# catalog-service
class Category(models.Model):
    name             = models.CharField(max_length=255)
    description      = models.TextField(blank=True)
    applicable_types = models.CharField(max_length=255, blank=True)
    # ví dụ: "book,laptop" hoặc "" (áp dụng cho tất cả)
```

---

## 3. Chiến Lược Migration Tổng Thể

```
Timeline (ước tính ~10–14 ngày làm việc)

Week 1
├── Phase 1: product-service (core model + API)    [3 ngày]
├── Phase 2: dependent services (cart, order, ...)  [3 ngày]
└── Phase 3: API Gateway + routes                   [1 ngày]

Week 2
├── Phase 4: Frontend                               [3 ngày]
├── Phase 5: Data migration script                  [1 ngày]
└── Phase 6: Cleanup, docs, testing                 [2 ngày]
```

**Nguyên tắc quan trọng:**
- Chạy `book-service` và `product-service` **song song** trong thời gian chuyển tiếp
- Giữ backward compatibility cho cart/order (chấp nhận cả `book_id` và `product_id`)
- Chỉ xóa `book-service` sau khi toàn bộ đã migrate và test xong

---

## Phase 1 – Core: product-service

### Bước 1.1: Tạo thư mục và Django project

```bash
# Copy book-service làm base, đổi tên
cp -r book-service product-service
cd product-service

# Đổi tên Django project bên trong
mv book_service product_service
# Cập nhật manage.py và settings.py: đổi 'book_service' → 'product_service'
```

**Các file cần đổi tên/sửa:**

```
product-service/
├── Dockerfile              # đổi tên project trong CMD
├── requirements.txt        # giữ nguyên
└── product_service/
    ├── manage.py           # DJANGO_SETTINGS_MODULE
    ├── app/
    │   ├── models.py       # ← Viết lại hoàn toàn (xem §2.2–2.3)
    │   ├── serializers.py  # ← Viết lại (xem §2.4)
    │   ├── views.py        # ← Viết lại
    │   ├── urls.py         # ← Cập nhật
    │   └── migrations/     # ← Xóa hết, chạy makemigrations lại
    └── product_service/
        ├── settings.py     # đổi INSTALLED_APPS, DB name: product_db
        ├── urls.py
        └── wsgi.py
```

### Bước 1.2: Viết Views cho product-service

```python
# product-service/product_service/app/views.py

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, BookDetail, LaptopDetail, MobileDetail, ClothDetail
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related(
        'book_detail', 'laptop_detail', 'mobile_detail', 'cloth_detail'
    )
    serializer_class    = ProductSerializer
    filter_backends     = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields    = ['product_type', 'category_id', 'is_active']
    search_fields       = ['name', 'description']
    ordering_fields     = ['price', 'created_at', 'name']

    def perform_create(self, serializer):
        product = serializer.save()
        self._create_detail(product, self.request.data)

    def _create_detail(self, product, data):
        detail_data = data.get('detail', {})
        if product.product_type == 'book':
            BookDetail.objects.create(product=product, **detail_data)
        elif product.product_type == 'laptop':
            LaptopDetail.objects.create(product=product, **detail_data)
        elif product.product_type == 'mobile':
            MobileDetail.objects.create(product=product, **detail_data)
        elif product.product_type == 'cloth':
            ClothDetail.objects.create(product=product, **detail_data)
```

### Bước 1.3: URLs

```python
# product-service/product_service/app/urls.py
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = router.urls
```

### Bước 1.4: Tạo migration và database

```bash
# Trong container hoặc local venv
python manage.py makemigrations app
python manage.py migrate
```

**Tạo database `product_db` trong PostgreSQL:**

```sql
-- docker/postgres/init-multiple-db.sh: thêm dòng
CREATE DATABASE product_db;
GRANT ALL PRIVILEGES ON DATABASE product_db TO $POSTGRES_USER;
```

### Bước 1.5: Endpoint API mới (product-service)

| Method | URL | Mô tả |
|---|---|---|
| `GET` | `/api/products/` | Danh sách tất cả sản phẩm |
| `GET` | `/api/products/?product_type=book` | Lọc theo loại |
| `GET` | `/api/products/?product_type=laptop` | Danh sách laptop |
| `GET` | `/api/products/{id}/` | Chi tiết 1 sản phẩm (kèm detail) |
| `POST` | `/api/products/` | Tạo sản phẩm mới |
| `PUT/PATCH` | `/api/products/{id}/` | Cập nhật sản phẩm |
| `DELETE` | `/api/products/{id}/` | Xóa (soft delete: is_active=False) |

**Ví dụ payload tạo laptop:**

```json
POST /api/products/
{
  "name": "MacBook Air M3",
  "product_type": "laptop",
  "price": "32990000",
  "stock": 10,
  "description": "Laptop Apple M3 chip",
  "category_id": 5,
  "detail": {
    "brand": "Apple",
    "cpu": "Apple M3",
    "ram_gb": 16,
    "storage_gb": 512,
    "display_inch": "15.3",
    "os": "macOS Sequoia"
  }
}
```

**Ví dụ payload tạo book:**

```json
POST /api/products/
{
  "name": "Clean Code",
  "product_type": "book",
  "price": "185000",
  "stock": 50,
  "description": "A Handbook of Agile Software Craftsmanship",
  "category_id": 1,
  "detail": {
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "publisher": "Prentice Hall",
    "pages": 431,
    "language": "en"
  }
}
```

### Bước 1.6: docker-compose.yml — thêm product-service

```yaml
# docker-compose.yml
product-service:
  build: ./product-service
  environment:
    - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/product_db
    - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
    - DJANGO_DEBUG=${DJANGO_DEBUG}
    - DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}
  depends_on:
    postgres:
      condition: service_healthy
  networks:
    - microservice_default
```

---

## Phase 2 – Dependent Services

### Bước 2.1: cart-service

**Thay đổi models.py:**

```python
# cart-service — TRƯỚC
class CartItem(models.Model):
    cart     = models.ForeignKey(Cart, ...)
    book_id  = models.IntegerField()       # ← xóa
    quantity = models.IntegerField()

# cart-service — SAU
class CartItem(models.Model):
    cart       = models.ForeignKey(Cart, ...)
    product_id = models.IntegerField()      # ← thêm
    quantity   = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
```

**Migration:**

```python
# Tạo migration mới:
# 1. Thêm cột product_id (nullable trước)
# 2. Data migration: product_id = book_id (trong giai đoạn chuyển tiếp)
# 3. Xóa cột book_id
```

**Cập nhật views.py — đổi BOOK_SERVICE_URL → PRODUCT_SERVICE_URL:**

```python
# cart-service/cart_service/app/views.py
PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:8888')

def validate_product(product_id):
    resp = requests.get(f"{PRODUCT_SERVICE_URL}/api/products/{product_id}/")
    if resp.status_code != 200:
        raise ValidationError("Product not found")
    data = resp.json()
    if data['stock'] < 1:
        raise ValidationError("Product out of stock")
    return data
```

**Environment variable trong docker-compose.yml:**

```yaml
cart-service:
  environment:
    - PRODUCT_SERVICE_URL=http://product-service:8888
    # Xóa: BOOK_SERVICE_URL
```

**Serializer:**

```python
# Đổi book_id → product_id trong CartItemSerializer
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CartItem
        fields = ['id', 'cart', 'product_id', 'quantity', 'unit_price']
```

### Bước 2.2: order-service

**Thay đổi models.py:**

```python
# order-service — SAU
class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id   = models.IntegerField()            # đổi từ book_id
    product_name = models.CharField(max_length=255) # đổi từ book_title/book_name
    product_type = models.CharField(max_length=50, blank=True)  # thêm mới
    quantity     = models.IntegerField()
    unit_price   = models.DecimalField(max_digits=12, decimal_places=2)
```

**Cập nhật create order logic:**

```python
# order-service/order_service/app/views.py
PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:8888')

def create_order_items(order, items_data):
    for item in items_data:
        # Lấy thông tin product
        product_resp = requests.get(
            f"{PRODUCT_SERVICE_URL}/api/products/{item['product_id']}/"
        )
        product = product_resp.json()

        OrderItem.objects.create(
            order        = order,
            product_id   = item['product_id'],
            product_name = product['name'],
            product_type = product['product_type'],
            quantity     = item['quantity'],
            unit_price   = item.get('unit_price', product['price']),
        )
```

**API payload đặt hàng mới:**

```json
POST /api/orders/
{
  "customer_id": 1,
  "shipping_address": "123 Nguyen Hue, Q1, HCM",
  "items": [
    {"product_id": 10, "quantity": 1, "unit_price": 32990000},
    {"product_id": 25, "quantity": 2, "unit_price": 185000}
  ]
}
```

### Bước 2.3: comment-rate-service

```python
# comment-rate-service — SAU
class Review(models.Model):
    customer_id  = models.IntegerField()
    product_id   = models.IntegerField()     # đổi từ book_id
    product_type = models.CharField(max_length=50, blank=True)  # thêm
    rating       = models.IntegerField(choices=[(i,i) for i in range(1,6)])
    comment      = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['customer_id', 'product_id']
```

**Cập nhật filter:**

```python
# Endpoint: GET /api/reviews/?product_id=10
# Thay vì: GET /api/reviews/?book_id=10
filterset_fields = ['product_id', 'product_type', 'customer_id', 'rating']
```

### Bước 2.4: recommender-ai-service

```python
# recommender-ai-service — TRƯỚC: gọi book-service và lấy book data
# SAU: gọi product-service, filter theo product_type nếu cần

PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:8888')

def get_all_products(product_type=None):
    url = f"{PRODUCT_SERVICE_URL}/api/products/"
    if product_type:
        url += f"?product_type={product_type}"
    resp = requests.get(url)
    return resp.json().get('results', [])

def get_product_reviews(product_id):
    url = f"{COMMENT_RATE_SERVICE_URL}/api/reviews/?product_id={product_id}"
    resp = requests.get(url)
    return resp.json().get('results', [])
```

**Cập nhật docker-compose.yml:**

```yaml
recommender-ai-service:
  environment:
    - PRODUCT_SERVICE_URL=http://product-service:8888
    # Xóa: BOOK_SERVICE_URL
```

### Bước 2.5: catalog-service

```python
# catalog-service — thêm trường applicable_types
class Category(models.Model):
    name             = models.CharField(max_length=255)
    description      = models.TextField(blank=True)
    applicable_types = models.CharField(max_length=255, blank=True,
                                        help_text="CSV: book,laptop,mobile,cloth hoặc để trống = tất cả")
    parent           = models.ForeignKey('self', null=True, blank=True,
                                         on_delete=models.SET_NULL, related_name='children')

    def get_applicable_types(self):
        if not self.applicable_types:
            return []  # áp dụng tất cả
        return [t.strip() for t in self.applicable_types.split(',')]
```

---

## Phase 3 – API Gateway & Proxy Routes

### Bước 3.1: Thêm route product-service

```python
# api-gateway — gateway/app/views.py hoặc urls.py
PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:8888')

# Thêm route mới (KHÔNG xóa /api/books/ ngay – backward compat)
urlpatterns = [
    # Route mới
    path('api/products/',        proxy_view(PRODUCT_SERVICE_URL + '/api/products/')),
    path('api/products/<int:pk>/',proxy_view(PRODUCT_SERVICE_URL + '/api/products/')),

    # Giữ tạm route cũ trong giai đoạn chuyển tiếp
    path('api/books/',           proxy_view(PRODUCT_SERVICE_URL + '/api/products/?product_type=book')),
    path('api/books/<int:pk>/',  proxy_view(PRODUCT_SERVICE_URL + '/api/products/')),
]
```

### Bước 3.2: Cập nhật Django admin templates

Tạo template `products/list.html` và `products/form.html` hỗ trợ dynamic form theo `product_type`.

```html
<!-- api-gateway/templates/products/form.html -->
<select name="product_type" id="product_type" onchange="showDetailFields()">
  <option value="book">Sách</option>
  <option value="laptop">Laptop</option>
  <option value="mobile">Điện thoại</option>
  <option value="cloth">Quần áo</option>
</select>

<!-- Fields hiển thị theo loại sản phẩm -->
<div id="book-fields" class="detail-fields">
  <input name="detail.author" placeholder="Tác giả">
  <input name="detail.isbn" placeholder="ISBN">
  ...
</div>
<div id="laptop-fields" class="detail-fields" style="display:none">
  <input name="detail.brand" placeholder="Thương hiệu">
  <input name="detail.cpu" placeholder="CPU">
  ...
</div>
```

### Bước 3.3: Health check

```python
# api-gateway — health check thêm product-service
SERVICES = {
    'book-service':    BOOK_SERVICE_URL,     # Giữ trong giai đoạn chuyển tiếp
    'product-service': PRODUCT_SERVICE_URL,  # Thêm mới
    ...
}
```

### Bước 3.4: Cập nhật environment variables

```yaml
# docker-compose.yml — api-gateway
api-gateway:
  environment:
    - PRODUCT_SERVICE_URL=http://product-service:8888
    - BOOK_SERVICE_URL=http://book-service:8888   # Giữ tạm
```

---

## Phase 4 – Frontend

### Bước 4.1: Cập nhật API service layer

```typescript
// frontend/src/services/api.ts

// TRƯỚC
export const getBooks = () => api.get('/api/books/');
export const getBook  = (id: number) => api.get(`/api/books/${id}/`);

// SAU
export const getProducts = (params?: ProductFilterParams) =>
  api.get('/api/products/', { params });

export const getProduct = (id: number) => api.get(`/api/products/${id}/`);

export const createProduct = (data: CreateProductPayload) =>
  api.post('/api/products/', data);

// Convenience helpers
export const getBooks   = () => getProducts({ product_type: 'book' });
export const getLaptops = () => getProducts({ product_type: 'laptop' });
export const getMobiles = () => getProducts({ product_type: 'mobile' });
export const getClothes = () => getProducts({ product_type: 'cloth' });
```

### Bước 4.2: TypeScript types mới

```typescript
// frontend/src/types/product.ts

export type ProductType = 'book' | 'laptop' | 'mobile' | 'cloth';

export interface BookDetail {
  author: string;
  isbn: string;
  publisher?: string;
  published_date?: string;
  pages?: number;
  language?: string;
}

export interface LaptopDetail {
  brand: string;
  cpu?: string;
  ram_gb?: number;
  storage_gb?: number;
  display_inch?: number;
  os?: string;
  weight_kg?: number;
}

export interface MobileDetail {
  brand: string;
  screen_inch?: number;
  battery_mah?: number;
  ram_gb?: number;
  storage_gb?: number;
  os?: string;
}

export interface ClothDetail {
  brand?: string;
  sizes?: string;
  color?: string;
  material?: string;
  gender?: string;
}

export interface Product {
  id: number;
  name: string;
  product_type: ProductType;
  price: string;
  stock: number;
  description: string;
  category_id: number | null;
  image_url: string;
  sku: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  detail: BookDetail | LaptopDetail | MobileDetail | ClothDetail | null;
}
```

### Bước 4.3: Component ProductCard

```typescript
// frontend/src/components/ProductCard.tsx
import React from 'react';
import { Product } from '../types/product';

const ProductTypeLabel: Record<string, string> = {
  book:   '📚 Sách',
  laptop: '💻 Laptop',
  mobile: '📱 Điện thoại',
  cloth:  '👕 Quần áo',
};

export const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
  return (
    <div className="product-card">
      <span className="product-type-badge">
        {ProductTypeLabel[product.product_type]}
      </span>
      <img src={product.image_url} alt={product.name} />
      <h3>{product.name}</h3>
      <p>{product.price.toLocaleString('vi-VN')} ₫</p>
      {product.product_type === 'book' && product.detail && (
        <p>Tác giả: {(product.detail as BookDetail).author}</p>
      )}
      {product.product_type === 'laptop' && product.detail && (
        <p>RAM: {(product.detail as LaptopDetail).ram_gb}GB</p>
      )}
    </div>
  );
};
```

### Bước 4.4: Cập nhật Cart context

```typescript
// Đổi cart item: book_id → product_id
interface CartItem {
  id: number;
  product_id: number;   // đổi từ book_id
  product: Product;     // full product object
  quantity: number;
  unit_price: number;
}
```

---

## Phase 5 – Data Migration

### Bước 5.1: Script migrate books → products

```python
# scripts/migrate_books_to_products.py
"""
Chạy sau khi product-service đã khởi động.
Lấy toàn bộ Books từ book-service, tạo tương ứng Product + BookDetail
trong product-service qua API.
"""
import requests
import json

BOOK_SERVICE    = "http://localhost:8888/api/books/"
PRODUCT_SERVICE = "http://localhost:8888/api/products/"

def migrate():
    page = 1
    while True:
        resp = requests.get(BOOK_SERVICE, params={"page": page})
        data = resp.json()
        books = data.get("results", data if isinstance(data, list) else [])

        for book in books:
            payload = {
                "name":         book["title"],
                "product_type": "book",
                "price":        book["price"],
                "stock":        book.get("stock", book.get("quantity", 0)),
                "description":  book.get("description", ""),
                "category_id":  book.get("category_id"),
                "image_url":    book.get("image_url", ""),
                "detail": {
                    "author":    book.get("author", ""),
                    "isbn":      book.get("isbn", ""),
                    "publisher": book.get("publisher", ""),
                    "pages":     book.get("pages"),
                    "language":  book.get("language", "vi"),
                }
            }
            create_resp = requests.post(PRODUCT_SERVICE,
                                        json=payload,
                                        headers={"Content-Type": "application/json"})
            if create_resp.status_code == 201:
                print(f"✅ Migrated: {book['title']}")
            else:
                print(f"❌ Failed: {book['title']} — {create_resp.text}")

        if not data.get("next"):
            break
        page += 1

    print("Migration complete!")

if __name__ == "__main__":
    migrate()
```

### Bước 5.2: Migration trong cart-service database

```sql
-- Chạy trực tiếp trong PostgreSQL
-- Giai đoạn 1: Thêm cột mới (đã thực hiện qua Django migration)
ALTER TABLE cart_cartitem ADD COLUMN product_id INTEGER;

-- Giai đoạn 2: Copy data (giả sử book_id trong product-service giữ nguyên ID)
UPDATE cart_cartitem SET product_id = book_id WHERE product_id IS NULL;

-- Giai đoạn 3: Sau khi xác nhận OK, đặt NOT NULL và xóa cột cũ
ALTER TABLE cart_cartitem ALTER COLUMN product_id SET NOT NULL;
ALTER TABLE cart_cartitem DROP COLUMN book_id;
```

### Bước 5.3: Migration trong order-service database

```sql
ALTER TABLE order_orderitem ADD COLUMN product_id INTEGER;
ALTER TABLE order_orderitem ADD COLUMN product_name VARCHAR(255);
ALTER TABLE order_orderitem ADD COLUMN product_type VARCHAR(50) DEFAULT 'book';

UPDATE order_orderitem
SET product_id   = book_id,
    product_name = COALESCE(book_title, book_name, ''),
    product_type = 'book'
WHERE product_id IS NULL;

-- Sau khi verify:
ALTER TABLE order_orderitem ALTER COLUMN product_id SET NOT NULL;
ALTER TABLE order_orderitem DROP COLUMN book_id;
ALTER TABLE order_orderitem DROP COLUMN book_title;
```

### Bước 5.4: Migration trong comment-rate-service

```sql
ALTER TABLE review_review ADD COLUMN product_id INTEGER;
ALTER TABLE review_review ADD COLUMN product_type VARCHAR(50) DEFAULT 'book';

UPDATE review_review
SET product_id   = book_id,
    product_type = 'book'
WHERE product_id IS NULL;

ALTER TABLE review_review ALTER COLUMN product_id SET NOT NULL;
ALTER TABLE review_review DROP COLUMN book_id;
```

---

## Phase 6 – Cleanup & Documentation

### Bước 6.1: Xóa backward compatibility routes

Sau khi toàn bộ service và frontend đã dùng `/api/products/`:

```python
# api-gateway — xóa route cũ
# path('api/books/', ...),       ← xóa
# path('api/books/<id>/', ...),  ← xóa
```

### Bước 6.2: Deprecate book-service

```yaml
# docker-compose.yml
# book-service:   ← comment out hoặc xóa hoàn toàn
#   build: ./book-service
#   ...
```

### Bước 6.3: Cập nhật README.md

Cập nhật bảng services:

| Service | Vai trò | Ghi chú |
|---|---|---|
| `product-service` | Quản lý sản phẩm | Hỗ trợ book, laptop, mobile, cloth |

Cập nhật bảng routes:

| Gateway Route | Service |
|---|---|
| `/api/products/` | product-service |

### Bước 6.4: Cập nhật seed scripts

```python
# scripts/seed_products.py
products = [
    # Books
    {"name": "Clean Code", "product_type": "book", "price": 185000, ...},
    # Laptops
    {"name": "MacBook Air M3", "product_type": "laptop", "price": 32990000, ...},
    # Mobiles
    {"name": "iPhone 16 Pro", "product_type": "mobile", "price": 29990000, ...},
    # Cloth
    {"name": "Áo Polo Nam", "product_type": "cloth", "price": 450000, ...},
]
```

---

## Checklist Tổng Hợp

### product-service
- [ ] Tạo thư mục `product-service/`
- [ ] Viết `Product`, `BookDetail`, `LaptopDetail`, `MobileDetail`, `ClothDetail` models
- [ ] Viết `ProductSerializer` với `detail` field động
- [ ] Viết `ProductViewSet` với filter theo `product_type`
- [ ] Tạo migration và chạy `migrate`
- [ ] Thêm vào `docker-compose.yml`
- [ ] Thêm `product_db` vào `init-multiple-db.sh`
- [ ] Test CRUD với từng loại sản phẩm

### cart-service
- [ ] Đổi `book_id` → `product_id` trong model
- [ ] Cập nhật `serializer`
- [ ] Cập nhật `validate_book()` → `validate_product()` với URL mới
- [ ] Cập nhật env var `PRODUCT_SERVICE_URL`
- [ ] Viết migration SQL

### order-service
- [ ] Đổi `book_id` → `product_id` trong `OrderItem`
- [ ] Đổi `book_title` → `product_name`, thêm `product_type`
- [ ] Cập nhật payload `POST /api/orders/`
- [ ] Cập nhật env var
- [ ] Viết migration SQL

### comment-rate-service
- [ ] Đổi `book_id` → `product_id`
- [ ] Thêm `product_type`
- [ ] Cập nhật filter fields
- [ ] Viết migration SQL

### recommender-ai-service
- [ ] Đổi URL gọi book-service → product-service
- [ ] Cập nhật env var

### catalog-service
- [ ] Thêm trường `applicable_types`
- [ ] Tạo migration
- [ ] Cập nhật serializer

### api-gateway
- [ ] Thêm route `/api/products/`
- [ ] Giữ `/api/books/` → proxy đến products?type=book (backward compat)
- [ ] Tạo template `products/list.html` và `products/form.html`
- [ ] Cập nhật health check
- [ ] Thêm `PRODUCT_SERVICE_URL` env

### frontend
- [ ] Cập nhật API service layer
- [ ] Thêm TypeScript types
- [ ] Viết `ProductCard` component
- [ ] Viết `ProductForm` với dynamic fields
- [ ] Cập nhật `CartContext`
- [ ] Cập nhật tất cả `book_id` references

### Data migration
- [ ] Chạy `migrate_books_to_products.py`
- [ ] Verify dữ liệu trong product-service
- [ ] Chạy SQL migration cho cart/order/review
- [ ] Verify FK consistency

### Cleanup
- [ ] Xóa backward compat route `/api/books/`
- [ ] Xóa `book-service` khỏi docker-compose
- [ ] Xóa `book_db` khỏi postgres init script
- [ ] Cập nhật README.md
- [ ] Cập nhật CLAUDE.md
- [ ] Cập nhật seed scripts

---

## Rủi Ro & Rollback

### Rủi ro chính

| Rủi ro | Xác suất | Giải pháp |
|---|---|---|
| ID mismatch (book_id ≠ product_id sau migrate) | Trung bình | Lưu mapping `old_book_id → new_product_id` trong migration script |
| Cart/Order đang pending bị broken | Trung bình | Chạy migration SQL sau giờ thấp điểm; không xóa `book_id` cho đến khi xác nhận |
| recommender model lỗi vì schema thay đổi | Thấp | Reset và retrain recommender sau khi product-service có đủ data |
| Frontend hiển thị sai type | Thấp | Type guard strict trong TypeScript |

### Chiến lược rollback

Vì book-service và product-service chạy **song song**, rollback đơn giản:

1. Đặt api-gateway route `/api/products/` → quay về `book-service`
2. Revert cart-service về dùng `book_id` (Django migration `--fake` về version trước)
3. Revert order-service tương tự
4. Stop `product-service` container

**Lệnh rollback nhanh:**

```bash
# Revert migrations cho từng service
docker compose exec cart-service python manage.py migrate app 000X_previous_migration
docker compose exec order-service python manage.py migrate app 000X_previous_migration

# Hoặc dùng git để revert code
git revert HEAD~N
docker compose up --build -d
```

---

> **Ghi chú:** Kế hoạch này dựa trên phân tích kiến trúc từ README và CLAUDE.md của repo. Một số tên field cụ thể (ví dụ `book_title` vs `book_name`) cần kiểm tra lại với source code thực tế trước khi implement.
