# AI Service MVP Plan v2

> Tài liệu hợp nhất từ:
> - AI_SERVICE_MVP_PLAN.md
> - AI_SERVICE_SUPPLEMENT_MULTI_SIGNAL.md
>
> Phiên bản v2 này giữ nguyên toàn bộ kế hoạch MVP gốc và bổ sung đầy đủ phần Multi‑Signal Recommendation (Order + Wishlist + Cart + Review), Wishlist nội bộ, cập nhật clients.py, recommender.py, API, models và docker-compose.

---

## PHẦN A — KẾ HOẠCH MVP GỐC

# AI Service — Kế hoạch triển khai MVP (Gợi ý sản phẩm + Chatbot tư vấn)

> Tài liệu này mô tả kế hoạch triển khai chi tiết cho **AI Service** của hệ thống `microservices-store`, ở mức **MVP** (Minimum Viable Product): tập trung vào 2 tính năng cốt lõi — **gợi ý sản phẩm (recommendation)** và **chatbot tư vấn (consultation chatbot)**.

---

## 0. Bối cảnh & Quyết định kiến trúc

### 0.1 Hiện trạng

Repo đã có sẵn service `recommender-ai-service` (Django + DRF, port `8888` nội bộ, DB `recommender_db`), được gateway proxy qua `/api/recommendations/`. Hiện tại service này chỉ có:

- Model `Recommendation` với field `recommended_book_ids` (tên cũ, còn sót lại từ thời `book-service`, trong khi hệ thống đã migrate sang `product-service`).
- 1 view `RecommendationView`: lấy review ≥ 4 sao của khách từ `comment-rate-service`, lấy toàn bộ sản phẩm từ `product-service`, rồi gợi ý 5 sản phẩm **chưa được review** — đây chỉ là logic loại trừ đơn giản, chưa thực sự "gợi ý".
- Chưa có chatbot, chưa có lưu lịch sử hội thoại, chưa tích hợp LLM.

Tài liệu `docs/BUSINESS_ANALYSIS.MD` (mục 7) đã vẽ ra một **vision dài hạn** rất đầy đủ cho AI Service: LSTM sequence model, Knowledge Graph (Neo4j), RAG với Vector DB (ChromaDB), Kafka, FastAPI... Đây là kiến trúc mục tiêu cho giai đoạn **production/scale**, **không phù hợp để bắt đầu ở MVP** vì kéo theo quá nhiều hạ tầng mới (Neo4j, Vector DB, Kafka, training pipeline).

### 0.2 Quyết định kiến trúc cho MVP

| Quyết định                | Lựa chọn                                                                                                               | Lý do                                                                                                                                                                    |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Service nào đảm nhiệm AI? | **Mở rộng `recommender-ai-service` hiện có**, không tạo service mới                                                    | Tránh thêm container/DB mới; chatbot và recommendation dùng chung dữ liệu sản phẩm/đánh giá nên chia sẻ service client là hợp lý                                         |
| Framework                 | Tiếp tục **Django + DRF** (giống 12 service khác)                                                                      | Đồng bộ pattern Dockerfile, migration, `wait_for_db.py`, settings — không tăng độ phức tạp vận hành cho MVP                                                              |
| Thuật toán gợi ý          | **Content-based + Popularity** (rule-based, không cần ML)                                                              | Không cần training pipeline/model lưu trữ; vẫn cho kết quả "có lý" hơn hẳn bản hiện tại                                                                                  |
| Chatbot                   | **RAG-lite**: gọi trực tiếp `product-service` để lấy "context" (không cần Vector DB riêng) + 1 LLM để sinh câu trả lời | Catalog nhỏ → semantic search qua vector DB chưa cần thiết; lọc theo `product_type`/`category_id`/`search`/giá là đủ cho MVP                                             |
| LLM                       | Provider **pluggable** qua biến môi trường (`mock` / `openrouter` / `anthropic` / `openai`)                            | **`openrouter`** là default cho MVP — dùng free model (không tốn phí), API key miễn phí tại openrouter.ai; `mock` cho CI/test hoàn toàn offline; dễ đổi nhà cung cấp sau |
| Hạ tầng mới               | **Không** thêm Neo4j / Kafka / ChromaDB ở MVP                                                                          | Đẩy sang roadmap sau MVP (mục 16)                                                                                                                                        |

> Nếu sau này muốn tách AI Service thành service riêng tên `ai-service` (đổi tên khỏi `recommender-ai-service`), nên làm ở một PR riêng sau khi MVP ổn định — việc đổi tên kéo theo sửa `docker-compose.yml`, `Dockerfile` path, gateway `SERVICES` dict, `.env`, và `CLAUDE.md`.

---

## 1. Mục tiêu & Phạm vi MVP

### 1.1 Mục tiêu

1. Khách hàng đăng nhập (có `customer_id`) nhận được danh sách gợi ý sản phẩm **có lý do** (dựa trên sở thích thể loại/loại sản phẩm + độ phổ biến), thay vì danh sách "sản phẩm chưa review".
2. Trang chi tiết sản phẩm có thể hiển thị "Sản phẩm tương tự" (cùng category/loại).
3. Có chatbot (textbox) cho phép khách mô tả nhu cầu bằng ngôn ngữ tự nhiên (tiếng Việt) và nhận lại: (a) câu trả lời tư vấn, (b) danh sách sản phẩm phù hợp lấy từ dữ liệu thật của `product-service` (không bịa).
4. Lưu lịch sử hội thoại cơ bản để chatbot "nhớ" trong cùng 1 phiên.

### 1.2 Trong phạm vi (In scope)

- API gợi ý sản phẩm theo khách hàng (`/api/recommendations/<customer_id>/`).
- API sản phẩm tương tự theo sản phẩm (`/api/recommendations/similar/<product_id>/`).
- API chatbot (`POST /api/chat/`, `GET /api/chat/<conversation_id>/`).
- Trích lọc nhu cầu từ câu hỏi (rule-based, có thể nâng cấp bằng LLM).
- Truy vấn `product-service` + `comment-rate-service` để lấy dữ liệu thật làm "context".
- Sinh câu trả lời tự nhiên bằng LLM (có thể chạy ở chế độ `mock` không cần API key).
- Lưu `Conversation` / `ChatMessage` trong `recommender_db`.
- Cập nhật API Gateway, `docker-compose.yml`, `.env.example`.
- Một FAQ tĩnh nhỏ (giao hàng/đổi trả/thanh toán) để chatbot trả lời câu hỏi chung.

### 1.3 Ngoài phạm vi MVP (Out of scope — để Phase sau)

- Vector Database / semantic search (ChromaDB, Qdrant, Pinecone, pgvector).
- Mô hình LSTM / sequence model, training pipeline.
- Knowledge Graph (Neo4j).
- Kafka / event streaming cho hành vi người dùng theo thời gian thực.
- Chatbot tra cứu **trạng thái đơn hàng** / vận chuyển (cần tích hợp sâu `order-service`, `ship-service` + xác thực khách hàng).
- Cá nhân hoá trang chủ theo real-time clickstream.
- Đa ngôn ngữ (chỉ tiếng Việt ở MVP).

---

## 2. Kiến trúc tổng thể MVP

```mermaid
flowchart TB
    FE["Frontend (React/Vite)"] -->|HTTP| GW["API Gateway :8888"]

    GW -->|"/api/recommendations/*"| AI
    GW -->|"/api/chat/*"| AI

    subgraph AI["recommender-ai-service (AI Service)"]
        REC["Recommendation Engine\n(multi-signal affinity)"]
        CHAT["Chatbot Engine\n(RAG-lite)"]
        LLMA["LLM Provider Adapter\n(mock / openrouter / anthropic / openai)"]
        DB[("recommender_db\nRecommendation, Conversation, ChatMessage")]

        REC --> DB
        CHAT --> DB
        CHAT --> LLMA
    end

    REC -->|"GET /api/products/"| PS["product-service"]
    REC -->|"GET /reviews/ (signal w=2)"| CRS["comment-rate-service"]
    REC -->|"GET /orders/ (signal w=4)"| OS["order-service"]
    REC -->|"GET /cart/ (signal w=2.5)"| CS["cart-service"]
    REC -->|"GET /wishlist/ (signal w=3)"| WS["wishlist-service*"]
    CHAT -->|"GET /api/products/?...filters"| PS
    CHAT -->|"GET rating (optional)"| CRS
    LLMA -.->|"khi PROVIDER != mock"| EXT["OpenRouter / Anthropic / OpenAI API"]
```

> \* `wishlist-service` — cần xác nhận endpoint thực tế trong repo (có thể là `catalog-service` hoặc service riêng). Nếu chưa có, client trả `[]` và engine vẫn chạy bình thường với 3 tín hiệu còn lại.

**Thành phần chính trong `recommender-ai-service`:**

| Thành phần                | Vai trò                                                                                                                                                          |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Recommendation Engine     | Tính danh sách gợi ý theo `customer_id` (multi-signal affinity: order + wishlist + cart + review) và "similar products" theo `product_id`                        |
| Chatbot Engine (RAG-lite) | Nhận message → trích filter → truy vấn `product-service` → ghép context → gọi LLM sinh câu trả lời                                                               |
| LLM Provider Adapter      | Lớp trừu tượng cho phép cắm `mock` (rule-based, không tốn phí) / `openrouter` (free model, **mặc định MVP**) / `anthropic` / `openai`                            |
| Service Clients           | Wrapper gọi 5 service nội bộ (`product`, `comment-rate`, `order`, `cart`, `wishlist`) song song bằng `ThreadPoolExecutor`; mỗi client có timeout + fallback `[]` |
| Models                    | `Recommendation` (cache gợi ý), `Conversation`, `ChatMessage`                                                                                                    |

---

## 3. Data Model (`recommender_db`)

### 3.1 Cập nhật model `Recommendation`

Đổi tên field cho khớp với `product-service` (đã migrate từ "book" sang "product"), và bổ sung lý do/thuật toán để debug + hiển thị trên UI.

```python
# app/models.py
from django.db import models


class Recommendation(models.Model):
    customer_id = models.IntegerField(unique=True)
    recommended_product_ids = models.TextField(default="")  # CSV, đổi tên từ recommended_book_ids
    algorithm = models.CharField(max_length=50, default="popularity")
    reason = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_product_ids(self):
        if not self.recommended_product_ids:
            return []
        return [int(x) for x in self.recommended_product_ids.split(",") if x.strip()]

    def set_product_ids(self, ids):
        self.recommended_product_ids = ",".join(str(i) for i in ids)

    def __str__(self):
        return f"Recommendations for Customer {self.customer_id}"
```

### 3.2 Model mới: `Conversation` & `ChatMessage`

```python
class Conversation(models.Model):
    # customer_id null = khách chưa đăng nhập, dùng session_id
    customer_id = models.IntegerField(null=True, blank=True, db_index=True)
    session_id = models.CharField(max_length=64, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation #{self.id} (customer={self.customer_id}, session={self.session_id})"


class ChatMessage(models.Model):
    ROLE_CHOICES = [("user", "User"), ("assistant", "Assistant")]

    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    product_ids = models.TextField(blank=True, default="")  # CSV sản phẩm gợi ý kèm câu trả lời (nếu có)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
```

### 3.3 Migration

```bash
docker compose exec recommender-ai-service python manage.py makemigrations app --name product_chat_models
docker compose exec recommender-ai-service python manage.py migrate
```

> Vì đây là field rename (`recommended_book_ids` → `recommended_product_ids`) trên 1 bảng nhỏ chưa có dữ liệu quan trọng, có thể dùng `RenameField` trong migration để Django tự xử lý, hoặc xoá volume `recommender_db` rồi để `init-data` seed lại từ đầu (đơn giản hơn cho môi trường dev).

---

## 4. Recommendation Engine

### 4.1 Nguồn dữ liệu & trọng số tín hiệu

Mỗi hành vi của khách hàng mang một mức độ "intent" khác nhau — từ việc thực sự mua hàng (mạnh nhất) đến chỉ review (trung bình). Engine gán trọng số tương ứng:

| Tín hiệu                   | Service                | Trọng số affinity | Loại khỏi kết quả?           | Lý do hiển thị                            |
| -------------------------- | ---------------------- | ----------------- | ---------------------------- | ----------------------------------------- |
| **Đã mua** (order history) | `order-service`        | **4.0**           | ✅ Có — đã sở hữu            | —                                         |
| **Wishlist** (yêu thích)   | `wishlist-service`     | **3.0**           | ❌ Không — nhắc nhở muốn mua | "Phù hợp với danh sách yêu thích của bạn" |
| **Cart** (giỏ hiện tại)    | `cart-service`         | **2.5**           | ✅ Có — đang mua             | "Có thể bạn cũng thích"                   |
| **Review ≥ 4 sao**         | `comment-rate-service` | **2.0**           | ✅ Có — đã trải nghiệm       | "Dựa trên sản phẩm bạn đánh giá cao"      |
| **Review < 4 sao**         | `comment-rate-service` | **0.5**           | ✅ Có — không thích lắm      | —                                         |
| **Popularity fallback**    | `comment-rate-service` | —                 | —                            | "Được nhiều khách đánh giá cao"           |

**Quy tắc loại trừ:**

- `exclude_ids` = `ordered_ids` ∪ `reviewed_ids` ∪ `cart_ids`
- Wishlist item **không bị loại** → có thể xuất hiện như sản phẩm "nhắc nhở" (khách đã muốn nhưng chưa mua)
- Tất cả client call đều có `timeout=5s` + `try/except` trả `[]` — 1 service down không làm sập engine

**Ghi chú endpoint wishlist:** cần xác nhận URL thực tế trong repo (xem `WISHLIST_SERVICE_URL` ở mục 7). Nếu service chưa có hoặc trả lỗi, `get_wishlist_by_customer` trả `[]` — engine vẫn hoạt động với 3 tín hiệu còn lại.

### 4.2 Thuật toán multi-signal affinity

**Bước xử lý cho `GET /recommendations/<customer_id>/`:**

1. **Gọi song song** 5 nguồn dữ liệu bằng `ThreadPoolExecutor` (tránh cộng dồn latency tuần tự):
   - `comment-rate-service` → reviews của khách
   - `order-service` → lịch sử đơn hàng + items
   - `cart-service` → giỏ hiện tại
   - `wishlist-service` → danh sách yêu thích
   - `product-service` → toàn bộ sản phẩm active

2. **Trích `product_id`** từ mỗi nguồn → xây `exclude_ids` = `ordered` ∪ `reviewed` ∪ `cart`

3. **Xây affinity map** `category_affinity[cat_id]` và `type_affinity[product_type]` bằng cách cộng trọng số tín hiệu cho từng sản phẩm đã tương tác:

   ```
   category_affinity[cat]  += WEIGHT[signal]  (với mọi sản phẩm pid của signal đó)
   type_affinity[type]     += WEIGHT[signal]
   ```

4. **Nếu affinity map rỗng** (khách hoàn toàn mới, không có tín hiệu nào) → **Popularity fallback** (bước 7).

5. **Score sản phẩm ứng viên** (loại `exclude_ids`):

   ```
   score = 3.0 × category_affinity[category_id] + 1.0 × type_affinity[product_type]
   ```

   Giữ `score > 0`, sort giảm dần, lấy top N (mặc định 8).

6. **Chọn `reason`** hiển thị dựa trên tín hiệu mạnh nhất đang có:
   `wishlist` → `order` → `cart` → `review ≥ 4` → fallback.

7. **Popularity fallback**: bù thiếu nếu chưa đủ N — tính `popularity_score = avg_rating × (1 + 0.1 × total_reviews)`, loại `exclude_ids ∪ kết_quả_đã_có`.

8. **Cache** vào model `Recommendation` → trả response.

**Bước xử lý cho `GET /recommendations/similar/<product_id>/`:**

1. Lấy sản phẩm gốc từ `product-service`.
2. Lọc sản phẩm có cùng `category_id` **hoặc** cùng `product_type`, ưu tiên `category_id` khớp trước.
3. Trả về top 6. _(Không cần tín hiệu khách hàng — endpoint này không yêu cầu `customer_id`.)_

### 4.3 Code minh hoạ — `app/services/recommender.py`

```python
from collections import Counter
from . import clients

DEFAULT_LIMIT = 8


def build_recommendations(customer_id, limit=DEFAULT_LIMIT):
    reviews = clients.get_reviews_by_customer(customer_id)
    seen_ids = {r["product_id"] for r in reviews}
    liked_ids = {r["product_id"] for r in reviews if r.get("rating", 0) >= 4}

    all_products = clients.get_all_products()
    by_id = {p["id"]: p for p in all_products}

    if not liked_ids:
        return _popularity_fallback(all_products, exclude=seen_ids, limit=limit)

    category_affinity = Counter()
    type_affinity = Counter()
    for pid in liked_ids:
        p = by_id.get(pid)
        if not p:
            continue
        if p.get("category_id"):
            category_affinity[p["category_id"]] += 1
        type_affinity[p["product_type"]] += 1

    scored = []
    for p in all_products:
        if p["id"] in seen_ids or not p.get("is_active", True):
            continue
        score = 2 * category_affinity.get(p.get("category_id"), 0)
        score += 1 * type_affinity.get(p["product_type"], 0)
        if score > 0:
            scored.append((p, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    results = [
        _to_result(p, score, "Dựa trên sản phẩm bạn đã đánh giá cao")
        for p, score in scored[:limit]
    ]

    if len(results) < limit:
        used_ids = seen_ids | {r["product_id"] for r in results}
        results += _popularity_fallback(all_products, exclude=used_ids, limit=limit - len(results))

    return results


def _popularity_fallback(all_products, exclude, limit):
    scored = []
    for p in all_products:
        if p["id"] in exclude or not p.get("is_active", True):
            continue
        rating = clients.get_product_rating(p["id"])
        avg = rating.get("average_rating") or 0
        total = rating.get("total_reviews") or 0
        score = avg * (1 + 0.1 * total)
        scored.append((p, score, rating))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [
        _to_result(p, score, "Sản phẩm được nhiều khách đánh giá cao", rating)
        for p, score, rating in scored[:limit]
    ]


def _to_result(product, score, reason, rating=None):
    rating = rating or clients.get_product_rating(product["id"])
    return {
        "product_id": product["id"],
        "name": product["name"],
        "product_type": product["product_type"],
        "price": product["price"],
        "score": round(float(score), 2),
        "reason": reason,
        "average_rating": rating.get("average_rating"),
    }


def build_similar_products(product_id, limit=6):
    all_products = clients.get_all_products()
    target = next((p for p in all_products if p["id"] == product_id), None)
    if not target:
        return []

    candidates = [
        p for p in all_products
        if p["id"] != product_id
        and p.get("is_active", True)
        and (p.get("category_id") == target.get("category_id") or p["product_type"] == target["product_type"])
    ]
    candidates.sort(key=lambda p: p.get("category_id") != target.get("category_id"))
    return candidates[:limit]
```

### 4.4 API

**`GET /api/recommendations/<customer_id>/`**

```json
{
  "customer_id": 1,
  "recommendations": [
    {
      "product_id": 12,
      "name": "Atomic Habits",
      "product_type": "book",
      "price": "159000.00",
      "score": 4.0,
      "reason": "Dựa trên sản phẩm bạn đã đánh giá cao",
      "average_rating": 4.5
    }
  ]
}
```

**`GET /api/recommendations/similar/<product_id>/`**

```json
{
  "product_id": 12,
  "similar_products": [
    {
      "id": 15,
      "name": "Deep Work",
      "product_type": "book",
      "price": "149000.00",
      "category_id": 3
    }
  ]
}
```

---

## 5. Chatbot tư vấn (RAG-lite)

### 5.1 Luồng xử lý

```mermaid
sequenceDiagram
    participant U as User (Frontend)
    participant GW as API Gateway
    participant AI as recommender-ai-service (/chat/)
    participant PS as product-service
    participant CRS as comment-rate-service
    participant LLM as LLM Provider

    U->>GW: POST /api/chat/ {message, customer_id?, session_id?, conversation_id?}
    GW->>AI: POST /chat/
    AI->>AI: extract_filters(message) -- rule-based hoặc LLM
    AI->>PS: GET /api/products/?product_type=&search=&ordering=
    PS-->>AI: candidate products
    AI->>AI: lọc theo min_price/max_price (Python)
    AI->>CRS: GET rating cho top candidates (optional)
    CRS-->>AI: average_rating
    AI->>LLM: generate_answer(message, products, history, store_faq)
    LLM-->>AI: câu trả lời (tiếng Việt)
    AI->>AI: lưu Conversation + 2x ChatMessage (user, assistant)
    AI-->>GW: {conversation_id, answer, products}
    GW-->>U: JSON
```

### 5.2 Chiến lược trích xuất nhu cầu (filter extraction)

| Chiến lược                          | Cách làm                                                                                                                          | Ưu điểm                                                          | Nhược điểm                                         | Khi nào dùng                                                                 |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------- |
| **A. Rule-based (regex/keyword)**   | Python thuần: bắt từ khoá loại sản phẩm (`sách`, `laptop`, `điện thoại`, `áo`...) + regex số tiền (`dưới 1 triệu`, `khoảng 500k`) | Miễn phí, nhanh, không cần LLM, hoạt động với `MockProvider`     | Kém chính xác với câu phức tạp/đa ý                | **Mặc định cho MVP** — luôn chạy để pre-filter, giảm số sản phẩm gửi cho LLM |
| **B. LLM call riêng để trích JSON** | Gọi LLM 1 lần, yêu cầu trả JSON `{product_type, min_price, max_price, keywords, sort}`                                            | Hiểu ngôn ngữ tự nhiên tốt hơn                                   | Thêm 1 lượt gọi LLM (chi phí/latency)              | Bật khi `LLM_PROVIDER != mock` và cần độ chính xác cao hơn                   |
| **C. Tool use (function calling)**  | LLM tự gọi "tool" `search_products(...)`, AI service thực thi rồi trả kết quả cho LLM tiếp tục                                    | Một luồng hội thoại tự nhiên, LLM quyết định khi nào cần tra cứu | Cần model hỗ trợ tool use tốt (Claude/GPT-4 class) | Nâng cấp **sau MVP**, khi đã chọn `anthropic` làm provider chính             |

**Quyết định MVP:** dùng **Chiến lược A** làm lớp pre-filter bắt buộc (chạy với mọi provider, kể cả `mock`). Khi `LLM_PROVIDER=anthropic`/`openai`, có thể bật thêm **Chiến lược B** như một bước "làm giàu" filter trước khi query `product-service` (cấu hình bằng cờ `LLM_EXTRACT_FILTERS=true/false`, mặc định `false` ở MVP để tiết kiệm chi phí — 1 lượt gọi LLM/chat là đủ).

### 5.3 Rule-based extractor — `app/services/nlp.py`

```python
import re

PRODUCT_TYPE_KEYWORDS = {
    "book": ["sach", "truyen", "tieu thuyet", "giao trinh", "sách", "truyện", "tiểu thuyết", "giáo trình"],
    "laptop": ["laptop", "may tinh", "macbook", "máy tính"],
    "mobile": ["dien thoai", "smartphone", "iphone", "samsung", "điện thoại"],
    "cloth": ["ao", "quan", "dam", "vay", "giay", "áo", "quần", "đầm", "váy", "giày"],
}

PRICE_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(trieu|tr|nghin|k|đ|d|vnd|triệu|nghìn)?", re.IGNORECASE)
UNDER_WORDS = ["duoi", "toi da", "khong qua", "dưới", "tối đa", "không quá"]
OVER_WORDS = ["tren", "toi thieu", "tu", "trên", "tối thiểu", "từ"]


def extract_filters(message: str) -> dict:
    text = message.lower()
    filters = {"product_type": None, "min_price": None, "max_price": None, "keywords": []}

    for ptype, kws in PRODUCT_TYPE_KEYWORDS.items():
        if any(kw in text for kw in kws):
            filters["product_type"] = ptype
            break

    match = PRICE_RE.search(text)
    if match:
        value = float(match.group(1).replace(",", "."))
        unit = (match.group(2) or "").lower()
        if unit in ("trieu", "tr", "triệu"):
            value *= 1_000_000
        elif unit in ("nghin", "k", "nghìn"):
            value *= 1_000

        if any(w in text for w in UNDER_WORDS):
            filters["max_price"] = value
        elif any(w in text for w in OVER_WORDS):
            filters["min_price"] = value
        else:
            filters["max_price"] = value  # mặc định hiểu là "ngân sách tối đa"

    # từ khoá tìm kiếm: bỏ stop-word ngắn, lấy tối đa 5 từ có nghĩa
    stop_words = {"toi", "muon", "mua", "can", "tôi", "muốn", "mua", "cần", "mot", "một"}
    words = [w for w in re.findall(r"[\wÀ-ỹ]+", text) if len(w) > 2 and w not in stop_words]
    filters["keywords"] = words[:5]
    return filters
```

### 5.4 Service client mở rộng — `app/services/clients.py`

```python
import os
import requests

PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://product-service:8888")
COMMENT_RATE_SERVICE_URL = os.environ.get("COMMENT_RATE_SERVICE_URL", "http://comment-rate-service:8888")
TIMEOUT = 5


def get_all_products(**params):
    try:
        r = requests.get(f"{PRODUCT_SERVICE_URL}/api/products/", params=params, timeout=TIMEOUT)
        data = r.json()
        return data.get("results", data) if isinstance(data, dict) else data
    except requests.exceptions.RequestException:
        return []


def search_products(filters: dict, limit=10):
    params = {}
    if filters.get("product_type"):
        params["product_type"] = filters["product_type"]
    if filters.get("keywords"):
        params["search"] = " ".join(filters["keywords"][:3])
    if filters.get("sort") == "price_asc":
        params["ordering"] = "price"
    elif filters.get("sort") == "price_desc":
        params["ordering"] = "-price"

    products = get_all_products(**params)

    min_price, max_price = filters.get("min_price"), filters.get("max_price")
    if min_price is not None:
        products = [p for p in products if float(p["price"]) >= min_price]
    if max_price is not None:
        products = [p for p in products if float(p["price"]) <= max_price]

    products = [p for p in products if p.get("is_active", True)]
    return products[:limit]


def get_reviews_by_customer(customer_id):
    try:
        r = requests.get(f"{COMMENT_RATE_SERVICE_URL}/reviews/", params={"customer_id": customer_id}, timeout=TIMEOUT)
        return r.json()
    except requests.exceptions.RequestException:
        return []


def get_product_rating(product_id):
    try:
        r = requests.get(f"{COMMENT_RATE_SERVICE_URL}/reviews/product/{product_id}/rating/", timeout=TIMEOUT)
        return r.json()
    except requests.exceptions.RequestException:
        return {"average_rating": None, "total_reviews": 0}
```

> **Lưu ý:** `product-service` hiện **chưa hỗ trợ filter theo `min_price`/`max_price`** qua query param (chỉ có `product_type`, `category_id`, `is_active`, `search`, `ordering` — xem mục 8). MVP xử lý lọc giá **ở phía AI service (Python)** sau khi lấy danh sách — chấp nhận được vì catalog hiện còn nhỏ. Nếu catalog lớn, chuyển lọc giá xuống `product-service` (Phase sau).

### 5.5 FAQ tĩnh (Store Knowledge) — `app/services/store_faq.py`

Một đoạn context tĩnh nhỏ giúp chatbot trả lời câu hỏi chung (giao hàng, đổi trả, thanh toán) mà không cần tra DB:

```python
STORE_FAQ = """\
- Giao hàng: toàn quốc, 2-5 ngày làm việc, miễn phí cho đơn từ 300.000đ.
- Đổi trả: trong 7 ngày nếu sản phẩm lỗi/hư hỏng, còn nguyên tem mác.
- Thanh toán: COD, chuyển khoản ngân hàng, ví điện tử.
- Liên hệ hỗ trợ: hotline trong giờ hành chính (8h-17h, T2-T6).
"""
```

> MVP: hardcode trong code. Phase sau có thể chuyển sang file cấu hình/CMS để team vận hành tự sửa không cần deploy lại.

### 5.6 LLM Provider Abstraction

```python
# app/services/llm/base.py
from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_answer(self, message: str, products: list, history: list, store_faq: str) -> str:
        """Sinh câu trả lời tiếng Việt, chỉ dựa trên `products` đã được retrieve."""
        raise NotImplementedError
```

```python
# app/services/llm/mock_provider.py
from .base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    """Không gọi API ngoài — dùng cho dev/test/CI."""

    def generate_answer(self, message, products, history, store_faq):
        if not products:
            return (
                "Hiện mình chưa tìm thấy sản phẩm phù hợp với yêu cầu này. "
                "Bạn có thể cho mình biết thêm về loại sản phẩm, ngân sách hoặc nhu cầu cụ thể không?"
            )
        names = ", ".join(p["name"] for p in products[:3])
        return f"Bạn có thể tham khảo các sản phẩm sau: {names}."
```

```python
# app/services/llm/openrouter_provider.py
import os
from openai import OpenAI
from .base import BaseLLMProvider

# Free models trên OpenRouter — xem danh sách đầy đủ tại https://openrouter.ai/models?q=free
# Các model free được khuyên dùng cho tiếng Việt (2025):
#   meta-llama/llama-3.1-8b-instruct:free   — cân bằng tốt, hiểu tiếng Việt khá
#   qwen/qwen-2.5-7b-instruct:free          — đặc biệt tốt với tiếng Việt / Á Đông
#   google/gemma-2-9b-it:free               — nhẹ, nhanh
DEFAULT_FREE_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
MODEL = os.environ.get("LLM_MODEL", DEFAULT_FREE_MODEL)


class OpenRouterProvider(BaseLLMProvider):
    """
    Gọi OpenRouter API (tương thích OpenAI) với free model.
    Không tốn phí — chỉ cần API key miễn phí tại https://openrouter.ai/settings/keys
    Giới hạn: ~20 req/phút và 200 req/ngày với free tier (đủ dùng cho MVP/dev).
    """

    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        )
        self.model = MODEL

    def generate_answer(self, message, products, history, store_faq):
        product_lines = "\n".join(
            f"- {p['name']} ({p['product_type']}): {p['price']}đ"
            for p in products[:5]
        ) or "Không có sản phẩm nào khớp trong catalog."

        system = (
            "Bạn là nhân viên tư vấn bán hàng của BookStore, trả lời ngắn gọn, "
            "thân thiện, bằng tiếng Việt. CHỈ đề xuất sản phẩm có trong danh sách "
            "dưới đây — KHÔNG bịa thêm sản phẩm, giá, hoặc thông tin tồn kho.\n\n"
            f"Thông tin cửa hàng:\n{store_faq}\n\n"
            f"Sản phẩm phù hợp với yêu cầu hiện tại:\n{product_lines}"
        )

        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=400,
            messages=[{"role": "system", "content": system}]
                      + history
                      + [{"role": "user", "content": message}],
            extra_headers={
                # Header khuyến nghị của OpenRouter để thống kê sử dụng (không bắt buộc)
                "HTTP-Referer": os.environ.get("OPENROUTER_SITE_URL", "http://localhost"),
                "X-Title": os.environ.get("OPENROUTER_APP_NAME", "BookStore AI"),
            },
        )
        return resp.choices[0].message.content
```

```python
# app/services/llm/anthropic_provider.py  (giữ lại, dùng khi LLM_PROVIDER=anthropic)
import os
import anthropic
from .base import BaseLLMProvider

MODEL = os.environ.get("LLM_MODEL", "claude-haiku-4-5")


class AnthropicProvider(BaseLLMProvider):
    def __init__(self):
        self.client = anthropic.Anthropic()  # đọc ANTHROPIC_API_KEY từ env

    def generate_answer(self, message, products, history, store_faq):
        product_lines = "\n".join(
            f"- {p['name']} ({p['product_type']}): {p['price']}đ"
            for p in products[:5]
        ) or "Không có sản phẩm nào khớp trong catalog."

        system = (
            "Bạn là nhân viên tư vấn bán hàng của BookStore, trả lời ngắn gọn, "
            "thân thiện, bằng tiếng Việt. CHỈ đề xuất sản phẩm có trong danh sách "
            "dưới đây — KHÔNG bịa thêm sản phẩm, giá, hoặc thông tin tồn kho.\n\n"
            f"Thông tin cửa hàng:\n{store_faq}\n\n"
            f"Sản phẩm phù hợp với yêu cầu hiện tại:\n{product_lines}"
        )

        resp = self.client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=system,
            messages=history + [{"role": "user", "content": message}],
        )
        return resp.content[0].text
```

```python
# app/services/llm/__init__.py
import os


def get_llm_provider():
    provider = os.environ.get("LLM_PROVIDER", "mock")
    if provider == "openrouter":
        from .openrouter_provider import OpenRouterProvider
        return OpenRouterProvider()
    if provider == "anthropic":
        from .anthropic_provider import AnthropicProvider
        return AnthropicProvider()
    if provider == "openai":
        from .openai_provider import OpenAIProvider  # tương tự openrouter_provider
        return OpenAIProvider()
    from .mock_provider import MockLLMProvider
    return MockLLMProvider()
```

> **Tại sao OpenRouter là lựa chọn mặc định cho MVP?**
> OpenRouter cung cấp nhiều model **hoàn toàn miễn phí** (suffix `:free`) thông qua API key tạo tại [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys) — không cần thẻ tín dụng. Vì OpenRouter dùng định dạng API tương thích với OpenAI, ta chỉ cần thư viện `openai` (đã cần cho `openai_provider.py`), không phát sinh dependency mới. Giới hạn free tier (~200 req/ngày) đủ dùng thoải mái trong giai đoạn MVP/dev.

### 5.7 View & Serializer

```python
# app/serializers.py (bổ sung)
from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    session_id = serializers.CharField(required=False, allow_blank=True, max_length=64)
    conversation_id = serializers.IntegerField(required=False, allow_null=True)
```

```python
# app/views.py (bổ sung)
from .models import Conversation, ChatMessage
from .serializers import ChatRequestSerializer
from .services import clients, nlp, store_faq
from .services.llm import get_llm_provider


class ChatView(APIView):
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        conversation = _get_or_create_conversation(data)
        history = _build_history(conversation)

        filters = nlp.extract_filters(data["message"])
        products = clients.search_products(filters)

        llm = get_llm_provider()
        answer = llm.generate_answer(data["message"], products, history, store_faq.STORE_FAQ)

        ChatMessage.objects.create(conversation=conversation, role="user", content=data["message"])
        ChatMessage.objects.create(
            conversation=conversation,
            role="assistant",
            content=answer,
            product_ids=",".join(str(p["id"]) for p in products[:5]),
        )

        return Response({
            "conversation_id": conversation.id,
            "answer": answer,
            "products": products[:5],
        })


class ChatHistoryView(APIView):
    def get(self, request, conversation_id):
        conversation = Conversation.objects.filter(id=conversation_id).first()
        if not conversation:
            return Response({"error": "Conversation not found"}, status=404)
        messages = conversation.messages.all()
        return Response({
            "conversation_id": conversation.id,
            "messages": [
                {"role": m.role, "content": m.content, "created_at": m.created_at}
                for m in messages
            ],
        })


def _get_or_create_conversation(data):
    if data.get("conversation_id"):
        conv = Conversation.objects.filter(id=data["conversation_id"]).first()
        if conv:
            return conv
    return Conversation.objects.create(
        customer_id=data.get("customer_id"),
        session_id=data.get("session_id", ""),
    )


def _build_history(conversation, max_messages=10):
    messages = conversation.messages.order_by("-created_at")[:max_messages]
    return [{"role": m.role, "content": m.content} for m in reversed(list(messages))]
```

### 5.8 API

**`POST /api/chat/`**

Request:

```json
{
  "message": "Tôi muốn mua laptop học lập trình dưới 15 triệu",
  "customer_id": 1
}
```

Response:

```json
{
  "conversation_id": 7,
  "answer": "Bạn có thể tham khảo Laptop A (RAM 16GB, SSD 512GB, 14.500.000đ), rất phù hợp để học lập trình trong tầm giá dưới 15 triệu.",
  "products": [
    {
      "id": 201,
      "name": "Laptop A",
      "product_type": "laptop",
      "price": "14500000.00"
    }
  ]
}
```

**`GET /api/chat/<conversation_id>/`** — trả về lịch sử hội thoại (cho frontend load lại khi quay lại trang).

---

## 6. Thay đổi cần thực hiện ở các service khác

| Service                          | Thay đổi                                                                                                                                                                                                                   | Bắt buộc cho MVP? |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| `product-service`                | Không bắt buộc sửa. **Tuỳ chọn**: thêm `price_min`/`price_max` vào `FilterSet` của `ProductViewSet` (dùng `django_filters.NumberFilter` với `lookup_expr='gte'/'lte'`) để chatbot lọc giá hiệu quả hơn ở DB thay vì Python | Không (Phase 1.5) |
| `comment-rate-service`           | Không cần sửa — endpoint `/reviews/` và `/reviews/product/<id>/rating/` đã đủ dùng                                                                                                                                         | —                 |
| `catalog-service`                | Không cần sửa ở MVP. **Tuỳ chọn**: AI service gọi `/categories/<id>/` để lấy `name` category, giúp chatbot nói "trong danh mục Văn học" thay vì chỉ ID                                                                     | Không (Phase 2)   |
| `cart-service` / `order-service` | Không gọi ở MVP. Sẽ dùng ở Phase 1.5 để bổ sung tín hiệu "đã thêm vào giỏ" / "đã mua" cho recommendation                                                                                                                   | Không             |

---

## 7. Cập nhật API Gateway, docker-compose, `.env`

### 7.1 API Gateway — `api-gateway/api_gateway/app/views.py`

Thêm resource `chat` vào `SERVICES`, dùng chung URL với `recommendations` (cùng service):

```python
SERVICES = {
    # ... các resource hiện có ...
    "recommendations": os.environ.get("RECOMMENDER_SERVICE_URL", "http://recommender-ai-service:8888"),
    "chat": os.environ.get("RECOMMENDER_SERVICE_URL", "http://recommender-ai-service:8888"),  # MỚI
}
```

Không cần thêm `urls.py` mới — pattern `re_path(r"^api/(?P<resource>[\w-]+)/(?P<path>.*)$", GatewayView.as_view())` đã generic. `GatewayView.dispatch` sẽ tự build `full_path = f"chat/{path}"`, khớp với `urls.py` của AI service ở mục 5.7/9.

Trong `HealthCheck`, có thể thêm (không bắt buộc — `chat` dùng chung URL với `recommendations` nên health đã được kiểm tra):

```python
health_endpoints = {
    # ...
    "chat": f"{SERVICES['chat']}/chat/",  # GET trả 405 vẫn được tính là "up"
}
```

### 7.2 `docker-compose.yml` — service `recommender-ai-service`

```yaml
recommender-ai-service:
  build:
    context: .
    dockerfile: recommender-ai-service/Dockerfile
  env_file: .env
  environment:
    DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/recommender_db
    PRODUCT_SERVICE_URL: http://product-service:8888
    COMMENT_RATE_SERVICE_URL: http://comment-rate-service:8888
    LLM_PROVIDER: ${LLM_PROVIDER:-openrouter} # MỚI: mock | openrouter | anthropic | openai
    LLM_MODEL: ${LLM_MODEL:-meta-llama/llama-3.1-8b-instruct:free} # MỚI: free model mặc định
    OPENROUTER_API_KEY: ${OPENROUTER_API_KEY:-} # MỚI: lấy tại openrouter.ai/settings/keys
    OPENROUTER_SITE_URL: ${OPENROUTER_SITE_URL:-http://localhost} # MỚI: tuỳ chọn, cho OpenRouter analytics
    OPENROUTER_APP_NAME: ${OPENROUTER_APP_NAME:-BookStore AI} # MỚI: tuỳ chọn
    ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-} # Giữ lại khi cần dùng LLM_PROVIDER=anthropic
    OPENAI_API_KEY: ${OPENAI_API_KEY:-} # Giữ lại khi cần dùng LLM_PROVIDER=openai
  depends_on:
    postgres:
      condition: service_healthy
    product-service:
      condition: service_started
    comment-rate-service:
      condition: service_started
```

> Sửa thêm: file `views.py` hiện tại có default `COMMENT_RATE_SERVICE_URL = "http://comment-rate-service:8000"` — port không khớp convention `8888` của toàn hệ thống. `docker-compose.yml` đang override đúng giá trị nên không lỗi thực tế, nhưng nên sửa default này về `8888` cho nhất quán (dọn dẹp ở Phase 0).

### 7.3 `.env.example` — bổ sung

```env
# AI Service (recommender-ai-service)
# Provider: mock (offline, không cần key) | openrouter (free, RECOMMENDED) | anthropic | openai
LLM_PROVIDER=openrouter

# OpenRouter — Đăng ký free API key tại: https://openrouter.ai/settings/keys
# Free models được khuyên dùng (suffix :free):
#   meta-llama/llama-3.1-8b-instruct:free   (mặc định, tiếng Việt khá)
#   qwen/qwen-2.5-7b-instruct:free          (tốt hơn cho tiếng Việt/Á Đông)
#   google/gemma-2-9b-it:free               (nhẹ hơn)
# Xem đầy đủ tại: https://openrouter.ai/models?q=free
LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_API_KEY=
OPENROUTER_SITE_URL=http://localhost
OPENROUTER_APP_NAME=BookStore AI

# Chỉ cần khi LLM_PROVIDER=anthropic hoặc LLM_PROVIDER=openai
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
```

### 7.4 `recommender-ai-service/requirements.txt` — bổ sung

```text
openai>=1.0.0
```

> **Lý do dùng `openai` thay vì `anthropic`:** OpenRouter sử dụng API tương thích OpenAI — thư viện `openai` kết nối được với cả OpenRouter **lẫn** OpenAI chính thức (chỉ cần đổi `base_url`). Nếu muốn dùng `LLM_PROVIDER=anthropic`, thêm riêng `anthropic>=0.40.0`. `mock` không cần thêm dependency nào.

---

## 8. Cấu trúc thư mục đề xuất (sau khi mở rộng)

```
recommender-ai-service/
├── Dockerfile
├── requirements.txt
└── recommender_ai_service/
    ├── manage.py
    ├── app/
    │   ├── models.py            # Recommendation, Conversation, ChatMessage
    │   ├── serializers.py        # RecommendationSerializer, ChatRequestSerializer
    │   ├── views.py               # RecommendationView, SimilarProductsView, ChatView, ChatHistoryView
    │   ├── migrations/
    │   └── services/
    │       ├── __init__.py
    │       ├── clients.py          # gọi product-service, comment-rate-service
    │       ├── recommender.py      # recommendation engine
    │       ├── nlp.py               # rule-based filter extraction
    │       ├── store_faq.py         # FAQ tĩnh
    │       └── llm/
    │           ├── __init__.py      # factory get_llm_provider()
    │           ├── base.py
    │           ├── mock_provider.py
    │           ├── openrouter_provider.py   # ← MỚI (default MVP)
    │           ├── anthropic_provider.py
    │           └── openai_provider.py
    └── recommender_ai_service/
        ├── settings.py
        └── urls.py
```

### 8.1 `app/urls.py` (đầy đủ sau khi thêm)

```python
from django.contrib import admin
from django.urls import path
from app.views import (
    RecommendationView,
    SimilarProductsView,
    ChatView,
    ChatHistoryView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("recommendations/<int:customer_id>/", RecommendationView.as_view(), name="recommendations"),
    path("recommendations/similar/<int:product_id>/", SimilarProductsView.as_view(), name="similar-products"),
    path("chat/", ChatView.as_view(), name="chat"),
    path("chat/<int:conversation_id>/", ChatHistoryView.as_view(), name="chat-history"),
]
```

---

## 9. Danh sách file cần tạo / sửa (checklist)

| File                                                                           | Hành động                                                                                                                                             |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `recommender-ai-service/recommender_ai_service/app/models.py`                  | Sửa `Recommendation`, thêm `Conversation`, `ChatMessage`                                                                                              |
| `recommender-ai-service/recommender_ai_service/app/migrations/000X_*.py`       | Tạo migration mới                                                                                                                                     |
| `recommender-ai-service/recommender_ai_service/app/serializers.py`             | Thêm `ChatRequestSerializer`, cập nhật `RecommendationSerializer`                                                                                     |
| `recommender-ai-service/recommender_ai_service/app/services/clients.py`        | Tạo mới                                                                                                                                               |
| `recommender-ai-service/recommender_ai_service/app/services/recommender.py`    | Tạo mới                                                                                                                                               |
| `recommender-ai-service/recommender_ai_service/app/services/nlp.py`            | Tạo mới                                                                                                                                               |
| `recommender-ai-service/recommender_ai_service/app/services/store_faq.py`      | Tạo mới                                                                                                                                               |
| `recommender-ai-service/recommender_ai_service/app/services/llm/*.py`          | Tạo mới (base, mock, **openrouter**, anthropic, openai, factory)                                                                                      |
| `recommender-ai-service/recommender_ai_service/app/views.py`                   | Refactor `RecommendationView`, thêm `SimilarProductsView`, `ChatView`, `ChatHistoryView`                                                              |
| `recommender-ai-service/recommender_ai_service/recommender_ai_service/urls.py` | Thêm route mới                                                                                                                                        |
| `recommender-ai-service/requirements.txt`                                      | Thêm `openai>=1.0.0` (dùng cho cả OpenRouter và OpenAI provider)                                                                                      |
| `api-gateway/api_gateway/app/views.py`                                         | Thêm `"chat"` vào `SERVICES` (và `HealthCheck`, tuỳ chọn)                                                                                             |
| `docker-compose.yml`                                                           | Thêm env vars: `LLM_PROVIDER`, `LLM_MODEL`, `OPENROUTER_API_KEY`, `OPENROUTER_SITE_URL`, `OPENROUTER_APP_NAME`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` |
| `.env.example`                                                                 | Thêm `LLM_PROVIDER=openrouter`, `LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free`, `OPENROUTER_API_KEY`, giữ `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`    |
| `CLAUDE.md` / `README.md`                                                      | Bổ sung route `/api/chat/` vào danh sách Gateway Proxy Routes                                                                                         |

---

## 10. Kế hoạch theo giai đoạn (Roadmap thực thi)

Ước tính cho **1 dev**, làm việc full-time:

| Giai đoạn                       | Nội dung                                                                                                                                         | Output chính                                                                                          | Ước tính     |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- | ------------ |
| **0. Chuẩn bị & dọn dẹp**       | Rename `recommended_book_ids` → `recommended_product_ids`; tạo migration; sửa default `COMMENT_RATE_SERVICE_URL`; tạo package `services/`        | Migration chạy được, `RecommendationView` cũ vẫn hoạt động sau refactor                               | 0.5 ngày     |
| **1. Recommendation Engine**    | `clients.py`, `recommender.py` (content-based + popularity), update `RecommendationView`, thêm `SimilarProductsView`                             | `GET /api/recommendations/<id>/`, `GET /api/recommendations/similar/<id>/` hoạt động với dữ liệu seed | 1.5 ngày     |
| **2. Chatbot — Backend**        | Models `Conversation`/`ChatMessage` + migration; `nlp.py`; `llm/` (base + mock + 1 provider thật); `store_faq.py`; `ChatView`, `ChatHistoryView` | `POST /api/chat/` hoạt động với `LLM_PROVIDER=mock`, và với provider thật khi có API key              | 2 - 3 ngày   |
| **3. Tích hợp Gateway & Infra** | Sửa `SERVICES` dict, `docker-compose.yml`, `.env.example`, `requirements.txt`, `CLAUDE.md`                                                       | `docker compose up --build` chạy đủ, health check OK                                                  | 0.5 ngày     |
| **4. Frontend (cơ bản)**        | Khu vực "Gợi ý cho bạn" ở trang chủ + "Sản phẩm tương tự" ở trang chi tiết; widget chat (nút nổi + khung chat)                                   | UI gọi được 3 API mới                                                                                 | 1.5 - 2 ngày |
| **5. Kiểm thử & hoàn thiện**    | Unit test cho `recommender.py`/`nlp.py`; script `curl`/Postman; cập nhật README                                                                  | Test pass, có demo script                                                                             | 1 ngày       |

**Tổng:** ~6.5 - 8.5 ngày làm việc cho MVP đầy đủ (backend + tích hợp gateway + frontend cơ bản + test).

> Nếu chỉ cần **backend MVP** (chưa cần frontend), Giai đoạn 0-3 ≈ **4-5 ngày**.

---

## 11. Kiểm thử & Definition of Done

### 11.1 Unit test (gợi ý)

- `recommender.py`: test `build_recommendations` với mock dữ liệu — trường hợp cold start (không có review) phải trả về popularity fallback; trường hợp có review ≥4 sao phải ưu tiên đúng category/type.
- `nlp.py`: test `extract_filters` với các câu mẫu ("laptop dưới 15 triệu", "áo sơ mi nam khoảng 300k", "sách kỹ năng sống") → kiểm tra `product_type`, `max_price` đúng kỳ vọng.
- `ChatView` với `LLM_PROVIDER=mock`: test end-to-end không cần network ra ngoài.

### 11.2 Smoke test thủ công (sau khi `docker compose up`)

```bash
# Gợi ý theo khách hàng
curl http://localhost:8888/api/recommendations/1/

# Sản phẩm tương tự
curl http://localhost:8888/api/recommendations/similar/1/

# Chatbot (provider mock — không cần API key)
curl -X POST http://localhost:8888/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Tôi muốn mua sách kỹ năng sống dưới 200k", "customer_id": 1}'

# Lấy lại lịch sử hội thoại
curl http://localhost:8888/api/chat/1/
```

### 11.3 Definition of Done (MVP)

- [ ] `recommended_product_ids` thay thế hoàn toàn `recommended_book_ids`, migration chạy sạch trên DB mới.
- [ ] `GET /api/recommendations/<customer_id>/` trả tối thiểu 1 sản phẩm hợp lệ (kể cả khi khách chưa có review nào — nhờ popularity fallback).
- [ ] `GET /api/recommendations/similar/<product_id>/` trả sản phẩm cùng category/type, loại trừ chính nó.
- [ ] `POST /api/chat/` hoạt động với `LLM_PROVIDER=mock` (không cần API key) — trả `answer` + `products` (có thể rỗng nếu không khớp).
- [ ] Khi cấu hình `LLM_PROVIDER=openrouter` + `OPENROUTER_API_KEY` hợp lệ, chatbot trả lời tự nhiên bằng tiếng Việt, **chỉ** đề xuất sản phẩm có thật trong `products`.
- [ ] `GET /api/chat/<conversation_id>/` trả đúng lịch sử user/assistant theo thứ tự thời gian.
- [ ] `docker compose up --build` chạy thành công, `/health/` báo `recommendations` (và `chat` nếu thêm) là `up`.
- [ ] Toàn bộ service call tới `product-service`/`comment-rate-service` có `timeout` + fallback rỗng khi lỗi (không làm sập AI service).

---

## 12. Rủi ro & Giảm thiểu

| Rủi ro                                                                       | Ảnh hưởng                                                   | Giảm thiểu                                                                                                                                    |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Chi phí/độ trễ gọi LLM                                                       | Tăng cost, chậm response                                    | **OpenRouter free model** không tốn phí ở MVP; giới hạn `max_tokens=400`, 1 lượt gọi LLM/chat; giữ `mock` cho CI offline                      |
| Giới hạn rate của OpenRouter free tier (~200 req/ngày)                       | Chatbot lỗi khi vượt giới hạn                               | Đủ dùng cho dev/demo; nếu cần nhiều hơn, nâng lên paid tier (~$5/tháng) hoặc chuyển `LLM_PROVIDER=anthropic`/`openai`                         |
| LLM "bịa" sản phẩm/giá không có thật (hallucination)                         | Sai thông tin cho khách                                     | Prompt yêu cầu **chỉ** dùng `products` đã retrieve; validate `product_ids` trả về có nằm trong danh sách trước khi response                   |
| `product-service`/`comment-rate-service` down hoặc chậm                      | AI service lỗi theo                                         | Áp dụng `timeout` + `try/except` trả fallback rỗng (đã có pattern trong code hiện tại), recommendation rơi về popularity hoặc rỗng            |
| Cold start (khách mới, sản phẩm mới)                                         | Không có dữ liệu để gợi ý                                   | Popularity fallback cho khách mới; sản phẩm mới vẫn xuất hiện qua "similar products" theo category                                            |
| Trích filter rule-based sai (regex tiếng Việt không dấu/có dấu)              | Chatbot tìm sai sản phẩm                                    | Test với cả câu có dấu/không dấu; LLM vẫn nhận `message` gốc để tự "hiểu" thêm khi sinh câu trả lời, không chỉ dựa vào filter                 |
| Lộ `OPENROUTER_API_KEY` / `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`             | Rủi ro bảo mật (dù OpenRouter free ít rủi ro tài chính hơn) | Chỉ lưu trong `.env` (không commit), set qua `env_file` trong `docker-compose.yml` như các secret khác                                        |
| Tăng số lượng request inter-service khi catalog lớn (lấy "toàn bộ sản phẩm") | Chậm dần khi data tăng                                      | Ghi chú rõ đây là giới hạn MVP; Phase sau: phân trang + filter ở `product-service`, hoặc cache danh sách sản phẩm trong AI service (TTL ngắn) |

---

## 13. Tích hợp Frontend (tóm tắt)

Không đi sâu vào chi tiết UI trong tài liệu này, nhưng MVP cần 2 điểm chạm chính trong `frontend/`:

1. **Trang chủ / trang sản phẩm**: gọi `GET /api/recommendations/<customer_id>/` (nếu khách đã đăng nhập) để render khu vực "Gợi ý cho bạn". Trang chi tiết sản phẩm gọi `GET /api/recommendations/similar/<product_id>/` cho "Sản phẩm tương tự".
2. **Chat widget**: 1 nút nổi (floating button) mở khung chat; lưu `conversation_id` trong state/local React (không dùng `localStorage` cho artifact, nhưng frontend thật của repo là ứng dụng React độc lập nên `localStorage`/`sessionStorage` bình thường vẫn dùng được ở đây) để tiếp tục hội thoại khi reload; gọi `POST /api/chat/`, hiển thị `answer` + render `products` dạng card (link tới trang chi tiết sản phẩm).

---

## 14. Roadmap sau MVP (liên kết `docs/BUSINESS_ANALYSIS.MD` §7)

Khi MVP ổn định và có dữ liệu hành vi thực tế, có thể nâng cấp theo đúng vision đã thiết kế trong `docs/BUSINESS_ANALYSIS.MD`:

| Hạng mục MVP hiện tại                                 | Nâng cấp Phase sau                                                                                          |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Content-based + popularity (rule-based)               | **Hybrid Model**: thêm LSTM sequence model dự đoán sản phẩm tiếp theo từ chuỗi hành vi (§7.4, §7.7)         |
| Tín hiệu: review only                                 | Bổ sung tín hiệu **cart** (`cart-service`) và **order** (`order-service`) — trọng số theo bảng §7.3         |
| Similar products theo category/type                   | **Knowledge Graph (Neo4j)**: quan hệ `BOUGHT`, `VIEWED`, `SIMILAR_TO` cho gợi ý đa quan hệ (§7.5)           |
| Retrieval bằng filter trực tiếp tới `product-service` | **RAG với Vector DB** (ChromaDB/pgvector): semantic search thực sự, không phụ thuộc filter chính xác (§7.6) |
| OpenRouter free model (RAG-lite, 1 call/chat)         | **Tool use / function calling** đầy đủ, multi-turn, có thể truy vấn nhiều tool (giá, tồn kho, đơn hàng)     |
| Cache `Recommendation` cập nhật khi gọi API           | **Event-driven** (Kafka): cập nhật gợi ý real-time theo hành vi (view/cart/purchase) (§7.9)                 |
| FAQ tĩnh trong code                                   | Chuyển FAQ vào CMS/`catalog-service`, AI service đọc động                                                   |

> Việc này nên được lập kế hoạch lại thành một tài liệu riêng (`AI_SERVICE_PHASE2_PLAN.md`) sau khi MVP được người dùng/giảng viên/khách hàng đánh giá, để tránh đầu tư hạ tầng (Neo4j/Kafka/Vector DB) trước khi xác nhận giá trị thực tế của các tính năng MVP.


---

## PHẦN B — BỔ SUNG MULTI‑SIGNAL RECOMMENDATION

# AI Service — Bổ sung Plan: Multi-Signal Recommendation
### (Order History + Wishlist + Cart + Review)

> **Tài liệu này bổ sung cho `AI_SERVICE_MVP_PLAN.md`.**  
> Gốc rễ của vấn đề: §4.1 & §2 của plan gốc đã mô tả đúng kiến trúc multi-signal (4 tín hiệu + trọng số),  
> nhưng code minh hoạ ở §4.3 (`recommender.py`) và §5.4 (`clients.py`) **chỉ dùng tín hiệu review** —  
> order, cart, wishlist hoàn toàn thiếu implementation.  
> Document này sửa tất cả gap đó, đồng thời xử lý wishlist (không có service riêng trong repo).

---

## Phân tích gap (Delta so với plan gốc)

| Hạng mục | Plan gốc (§) | Trạng thái thực tế | Bổ sung trong doc này |
|---|---|---|---|
| Bảng tín hiệu + trọng số | §4.1 ✅ đầy đủ | — | Không đổi |
| `clients.py` — order signal | §5.4 ❌ thiếu | Không có hàm nào | ✅ `get_orders_by_customer` |
| `clients.py` — cart signal | §5.4 ❌ thiếu | Không có hàm nào | ✅ `get_cart_by_customer` |
| `clients.py` — wishlist | §5.4 ❌ thiếu + ★ | Không có service riêng trong repo | ✅ Wishlist model nội bộ + hàm ORM |
| `recommender.py` — multi-signal + ThreadPoolExecutor | §4.3 ❌ chỉ review | Chỉ gọi reviews | ✅ Rewrite hoàn chỉnh |
| `models.py` — WishlistItem | §3 ❌ thiếu | Chỉ có `Recommendation` | ✅ Thêm model |
| Wishlist API endpoints | ❌ thiếu | — | ✅ Thêm 3 endpoints |
| `docker-compose.yml` — env vars | §7.2 ❌ thiếu | `ORDER_SERVICE_URL`, `CART_SERVICE_URL` chưa có | ✅ Thêm vào |
| `recommender-ai-service` `depends_on` | §7.2 ❌ thiếu | Chỉ depends product + comment | ✅ Thêm order + cart |

---

## Phát hiện từ repo thực tế (quan trọng)

Sau khi đọc `docker-compose.yml` và `CLAUDE.md`:

1. **`product-service` đã tồn tại** — `book-service` trong CLAUDE.md/README là tài liệu cũ chưa cập nhật.  
   Docker-compose confirm: `cart-service` và `order-service` đều dùng `PRODUCT_SERVICE_URL: http://product-service:8888`.

2. **Không có `wishlist-service`** — Repo có 12 service, không có service nào cho wishlist.  
   Giải pháp MVP: thêm model `WishlistItem` trực tiếp vào `recommender-ai-service` (dùng `recommender_db`),  
   kèm 3 API endpoint để frontend thêm/xoá/liệt kê wishlist.

3. **`recommender-ai-service` trong docker-compose hiện tại** chỉ có:
   ```yaml
   PRODUCT_SERVICE_URL: http://product-service:8888
   COMMENT_RATE_SERVICE_URL: http://comment-rate-service:8888
   ```
   Cần thêm `ORDER_SERVICE_URL` và `CART_SERVICE_URL`.

4. **Naming field trong order-service**: Repo đã migrate sang product-service nên order items  
   nhiều khả năng dùng `product_id`. Tuy nhiên code client có fallback check cả `book_id` để an toàn.

---

## §3-BSUNG — Cập nhật `models.py`: thêm `WishlistItem`

Thêm model sau vào `app/models.py` (ngay sau `Recommendation`, trước `Conversation`):

```python
class WishlistItem(models.Model):
    """
    Wishlist nội bộ — dùng vì repo không có wishlist-service riêng.
    Frontend gọi POST/DELETE /recommendations/wishlist/ để thêm/xoá.
    Recommendation engine đọc trực tiếp qua ORM (không cần HTTP call).
    """
    customer_id = models.IntegerField(db_index=True)
    product_id  = models.IntegerField()
    added_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("customer_id", "product_id")
        ordering = ["-added_at"]

    def __str__(self):
        return f"Wishlist: customer={self.customer_id} product={self.product_id}"
```

**Migration:**
```bash
docker compose exec recommender-ai-service python manage.py makemigrations app --name add_wishlist_item
docker compose exec recommender-ai-service python manage.py migrate
```

---

## §5.4-BSUNG — `clients.py` đầy đủ (thay thế §5.4 plan gốc)

File: `recommender-ai-service/recommender_ai_service/app/services/clients.py`

```python
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

PRODUCT_SERVICE_URL      = os.environ.get("PRODUCT_SERVICE_URL",      "http://product-service:8888")
COMMENT_RATE_SERVICE_URL = os.environ.get("COMMENT_RATE_SERVICE_URL",  "http://comment-rate-service:8888")
ORDER_SERVICE_URL        = os.environ.get("ORDER_SERVICE_URL",         "http://order-service:8888")
CART_SERVICE_URL         = os.environ.get("CART_SERVICE_URL",          "http://cart-service:8888")
TIMEOUT = 5


# ─────────────────────────────────────────────
# product-service
# ─────────────────────────────────────────────

def get_all_products(**params):
    """GET /products/ — trả toàn bộ sản phẩm active."""
    try:
        r = requests.get(f"{PRODUCT_SERVICE_URL}/products/", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return data.get("results", data) if isinstance(data, dict) else data
    except Exception:
        return []


def search_products(filters: dict, limit=10):
    """Lọc sản phẩm theo filter dict (cho chatbot). Lọc giá ở Python vì product-service chưa hỗ trợ."""
    params = {}
    if filters.get("product_type"):
        params["product_type"] = filters["product_type"]
    if filters.get("keywords"):
        params["search"] = " ".join(filters["keywords"][:3])
    if filters.get("sort") == "price_asc":
        params["ordering"] = "price"
    elif filters.get("sort") == "price_desc":
        params["ordering"] = "-price"

    products = get_all_products(**params)

    min_p, max_p = filters.get("min_price"), filters.get("max_price")
    if min_p is not None:
        products = [p for p in products if float(p.get("price", 0)) >= min_p]
    if max_p is not None:
        products = [p for p in products if float(p.get("price", 0)) <= max_p]

    return [p for p in products if p.get("is_active", True)][:limit]


# ─────────────────────────────────────────────
# comment-rate-service (signal: review)
# ─────────────────────────────────────────────

def get_reviews_by_customer(customer_id):
    """
    GET /reviews/?customer_id={id}
    Trả list: [{product_id, rating, ...}]
    """
    try:
        r = requests.get(
            f"{COMMENT_RATE_SERVICE_URL}/reviews/",
            params={"customer_id": customer_id},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("results", data) if isinstance(data, dict) else data
    except Exception:
        return []


def get_product_rating(product_id):
    """
    GET /reviews/product/{id}/rating/
    Trả: {average_rating, total_reviews}
    """
    try:
        r = requests.get(
            f"{COMMENT_RATE_SERVICE_URL}/reviews/product/{product_id}/rating/",
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return {"average_rating": None, "total_reviews": 0}


# ─────────────────────────────────────────────
# order-service (signal: purchase history, weight=4.0)
# ─────────────────────────────────────────────

def get_orders_by_customer(customer_id):
    """
    GET /orders/?customer_id={id}
    Response giả định (DRF standard):
      [
        {
          "id": 1, "customer_id": 1,
          "items": [{"product_id": 12, "quantity": 1, "unit_price": "150000.00"}, ...]
        },
        ...
      ]

    Fallback: nếu field gọi là "book_id" (version cũ của repo), hàm _extract_product_id
    sẽ tự nhận dạng. Nếu endpoint trả 404/lỗi → trả [].
    """
    try:
        r = requests.get(
            f"{ORDER_SERVICE_URL}/orders/",
            params={"customer_id": customer_id},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        orders = data.get("results", data) if isinstance(data, dict) else data

        # Trích list product_id từ tất cả order items
        product_ids = []
        for order in (orders if isinstance(orders, list) else []):
            for item in order.get("items", []):
                pid = _extract_product_id(item)
                if pid is not None:
                    product_ids.append(pid)
        return product_ids  # list[int]
    except Exception:
        return []


def _extract_product_id(item: dict):
    """Nhận dạng field tên sản phẩm trong order/cart item (cả 'product_id' lẫn 'book_id')."""
    return item.get("product_id") or item.get("book_id")


# ─────────────────────────────────────────────
# cart-service (signal: cart intent, weight=2.5)
# ─────────────────────────────────────────────

def get_cart_by_customer(customer_id):
    """
    Thử 2 pattern endpoint phổ biến:
      1. GET /carts/?customer_id={id}   (query param — trả list)
      2. GET /carts/{customer_id}/      (path param   — trả object)

    Response giả định:
      Pattern 1: [{id, customer_id, items: [{product_id, quantity}, ...]}]
      Pattern 2: {id, customer_id, items: [{product_id, quantity}, ...]}

    Trả list[int] product_id hiện có trong giỏ.
    """
    for url, params in [
        (f"{CART_SERVICE_URL}/carts/",               {"customer_id": customer_id}),
        (f"{CART_SERVICE_URL}/carts/{customer_id}/", {}),
    ]:
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT)
            if r.status_code == 404:
                continue
            r.raise_for_status()
            data = r.json()

            # Flatten: list hoặc single object
            carts = data if isinstance(data, list) else [data]
            if isinstance(data, dict) and "results" in data:
                carts = data["results"]

            product_ids = []
            for cart in carts:
                for item in cart.get("items", []):
                    pid = _extract_product_id(item)
                    if pid is not None:
                        product_ids.append(pid)
            return product_ids
        except Exception:
            continue
    return []


# ─────────────────────────────────────────────
# wishlist (signal: save-for-later, weight=3.0)
# ─────────────────────────────────────────────
# KHÔNG gọi HTTP — đọc trực tiếp từ model WishlistItem trong recommender_db.
# Hàm này nằm ở đây để giữ interface thống nhất với các signal khác,
# nhưng được gọi NGOÀI ThreadPoolExecutor (vì là ORM call, không phải I/O blocking network).

def get_wishlist_product_ids_local(customer_id):
    """
    Đọc WishlistItem từ DB nội bộ (recommender_db).
    Không dùng requests — gọi trực tiếp ORM.
    Trả list[int].
    """
    try:
        from app.models import WishlistItem
        return list(
            WishlistItem.objects.filter(customer_id=customer_id).values_list("product_id", flat=True)
        )
    except Exception:
        return []


# ─────────────────────────────────────────────
# Helper: gọi song song (order + cart + review)
# ─────────────────────────────────────────────

def fetch_customer_signals(customer_id):
    """
    Gọi song song 3 service bên ngoài (order, cart, comment-rate) + 1 ORM local (wishlist).
    Dùng ThreadPoolExecutor để tránh cộng dồn latency.
    Trả dict với 4 key, mỗi key là list.

    Wishlist query local DB → NGOÀI executor (nhanh, không cần thread riêng).
    """
    results = {
        "order_ids":    [],
        "cart_ids":     [],
        "reviews":      [],
        "wishlist_ids": [],
    }

    tasks = {
        "order_ids": lambda: get_orders_by_customer(customer_id),
        "cart_ids":  lambda: get_cart_by_customer(customer_id),
        "reviews":   lambda: get_reviews_by_customer(customer_id),
    }

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fn): key for key, fn in tasks.items()}
        for future in as_completed(futures, timeout=TIMEOUT + 1):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception:
                results[key] = [] if key != "reviews" else []

    # Wishlist: local ORM, không cần thread
    results["wishlist_ids"] = get_wishlist_product_ids_local(customer_id)

    return results
```

> **Lưu ý xác nhận endpoint `order-service`:** Khi implement thực tế, cần `GET /orders/?customer_id={id}` trả về  
> danh sách orders với `items` field. Nếu endpoint hiện tại không hỗ trợ filter by `customer_id`,  
> cần thêm `FilterSet` cho `OrderViewSet` trong `order-service` (tương tự ghi chú về `product-service` filter giá ở §6 plan gốc).  
> Xem §6-BSUNG bên dưới.

---

## §4.3-BSUNG — `recommender.py` đầy đủ (thay thế §4.3 plan gốc)

File: `recommender-ai-service/recommender_ai_service/app/services/recommender.py`

```python
"""
Multi-signal recommendation engine.
Tín hiệu & trọng số:
    order    (đã mua)      → weight 4.0  | loại khỏi kết quả (đã sở hữu)
    wishlist (yêu thích)   → weight 3.0  | KHÔNG loại  (nhắc nhở muốn mua)
    cart     (giỏ hàng)    → weight 2.5  | loại khỏi kết quả (đang mua)
    review≥4 (đánh giá cao)→ weight 2.0  | loại khỏi kết quả (đã trải nghiệm)
    review<4 (đánh giá thấp)→weight 0.5  | loại khỏi kết quả
    popularity (fallback)  → weight dẫn xuất từ avg_rating × (1 + 0.1×total)
"""

from . import clients

# ─── Trọng số ───────────────────────────────
WEIGHT_ORDER    = 4.0
WEIGHT_WISHLIST = 3.0
WEIGHT_CART     = 2.5
WEIGHT_LIKED    = 2.0   # review >= 4
WEIGHT_DISLIKED = 0.5   # review < 4

# Hệ số score = category_affinity * CAT_FACTOR + type_affinity * TYPE_FACTOR
CAT_FACTOR  = 3.0
TYPE_FACTOR = 1.0

DEFAULT_LIMIT = 8


def build_recommendations(customer_id: int, limit: int = DEFAULT_LIMIT) -> list:
    """
    Trả list gợi ý sản phẩm cho customer_id, tối đa `limit` items.
    Mỗi item: {product_id, name, product_type, price, score, reason, average_rating}
    """
    # ── 1. Lấy song song tất cả tín hiệu ────────────────────────────────────
    signals = clients.fetch_customer_signals(customer_id)
    reviews      = signals["reviews"]        # list[{product_id, rating, ...}]
    order_ids    = set(signals["order_ids"]) # set[int]
    cart_ids     = set(signals["cart_ids"])  # set[int]
    wishlist_ids = set(signals["wishlist_ids"])  # set[int]

    # Phân loại reviews
    reviewed_ids = {r["product_id"] for r in reviews}
    liked_ids    = {r["product_id"] for r in reviews if r.get("rating", 0) >= 4}
    disliked_ids = reviewed_ids - liked_ids

    # ── 2. Xác định exclude_ids (sản phẩm loại khỏi kết quả) ────────────────
    # Wishlist KHÔNG bị loại — khách đã thêm vào wishlist nhưng chưa mua → cần nhắc
    exclude_ids = order_ids | cart_ids | reviewed_ids

    # ── 3. Kiểm tra cold-start ───────────────────────────────────────────────
    has_any_signal = bool(order_ids or wishlist_ids or cart_ids or liked_ids)
    if not has_any_signal:
        all_products = clients.get_all_products()
        return _popularity_fallback(all_products, exclude=exclude_ids, limit=limit)

    # ── 4. Lấy toàn bộ sản phẩm ─────────────────────────────────────────────
    all_products = clients.get_all_products()
    by_id = {p["id"]: p for p in all_products}

    # ── 5. Tính affinity map từ tất cả tín hiệu ─────────────────────────────
    # Cấu trúc: category_affinity[cat_id] = tổng weight
    category_affinity: dict[int, float] = {}
    type_affinity:     dict[str, float] = {}

    def _accumulate(product_id, weight):
        p = by_id.get(product_id)
        if not p:
            return
        cat = p.get("category_id")
        ptype = p.get("product_type", "")
        if cat:
            category_affinity[cat] = category_affinity.get(cat, 0) + weight
        if ptype:
            type_affinity[ptype] = type_affinity.get(ptype, 0) + weight

    for pid in order_ids:
        _accumulate(pid, WEIGHT_ORDER)
    for pid in wishlist_ids:
        _accumulate(pid, WEIGHT_WISHLIST)
    for pid in cart_ids:
        _accumulate(pid, WEIGHT_CART)
    for pid in liked_ids:
        _accumulate(pid, WEIGHT_LIKED)
    for pid in disliked_ids:
        _accumulate(pid, WEIGHT_DISLIKED)

    # ── 6. Score từng sản phẩm ứng viên ─────────────────────────────────────
    scored = []
    for p in all_products:
        if p["id"] in exclude_ids or not p.get("is_active", True):
            continue
        cat   = p.get("category_id")
        ptype = p.get("product_type", "")
        score = (
            CAT_FACTOR  * category_affinity.get(cat,   0) +
            TYPE_FACTOR * type_affinity.get(ptype, 0)
        )
        if score > 0:
            scored.append((p, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    # ── 7. Chọn reason hiển thị ──────────────────────────────────────────────
    reason = _select_reason(order_ids, wishlist_ids, cart_ids, liked_ids)

    # ── 8. Build kết quả chính ───────────────────────────────────────────────
    results = []
    for p, score in scored[:limit]:
        # Wishlist item xuất hiện trong kết quả → gắn reason đặc biệt
        item_reason = (
            "Sản phẩm trong danh sách yêu thích của bạn" if p["id"] in wishlist_ids
            else reason
        )
        results.append(_to_result(p, score, item_reason))

    # ── 9. Bù popularity fallback nếu chưa đủ ───────────────────────────────
    if len(results) < limit:
        used_ids = exclude_ids | {r["product_id"] for r in results}
        fallback = _popularity_fallback(all_products, exclude=used_ids, limit=limit - len(results))
        results.extend(fallback)

    return results[:limit]


def build_similar_products(product_id: int, limit: int = 6) -> list:
    """
    Gợi ý sản phẩm tương tự theo product_id (không cần customer_id).
    Ưu tiên cùng category_id, sau đó cùng product_type.
    """
    all_products = clients.get_all_products()
    target = next((p for p in all_products if p["id"] == product_id), None)
    if not target:
        return []

    same_cat   = []
    same_type  = []
    for p in all_products:
        if p["id"] == product_id or not p.get("is_active", True):
            continue
        if p.get("category_id") == target.get("category_id"):
            same_cat.append(p)
        elif p.get("product_type") == target.get("product_type"):
            same_type.append(p)

    candidates = (same_cat + same_type)[:limit]
    return candidates


# ─── Helpers ────────────────────────────────────────────────────────────────

def _select_reason(order_ids, wishlist_ids, cart_ids, liked_ids) -> str:
    """Chọn reason theo thứ tự ưu tiên tín hiệu mạnh nhất."""
    if order_ids:
        return "Dựa trên lịch sử mua hàng của bạn"
    if wishlist_ids:
        return "Phù hợp với danh sách yêu thích của bạn"
    if cart_ids:
        return "Bạn cũng có thể thích sản phẩm này"
    if liked_ids:
        return "Dựa trên sản phẩm bạn đã đánh giá cao"
    return "Được nhiều khách đánh giá cao"


def _to_result(product: dict, score: float, reason: str, rating: dict = None) -> dict:
    if rating is None:
        rating = clients.get_product_rating(product["id"])
    return {
        "product_id":     product["id"],
        "name":           product.get("name", ""),
        "product_type":   product.get("product_type", ""),
        "price":          product.get("price", "0"),
        "score":          round(float(score), 2),
        "reason":         reason,
        "average_rating": rating.get("average_rating"),
        "in_wishlist":    False,  # sẽ được set ở view nếu cần
    }


def _popularity_fallback(all_products: list, exclude: set, limit: int) -> list:
    """Fallback: sắp xếp theo popularity_score = avg_rating × (1 + 0.1 × total_reviews)."""
    scored = []
    for p in all_products:
        if p["id"] in exclude or not p.get("is_active", True):
            continue
        rating = clients.get_product_rating(p["id"])
        avg    = float(rating.get("average_rating") or 0)
        total  = int(rating.get("total_reviews") or 0)
        pop_score = avg * (1 + 0.1 * total)
        scored.append((p, pop_score, rating))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [
        _to_result(p, score, "Được nhiều khách đánh giá cao", rating)
        for p, score, rating in scored[:limit]
    ]
```

---

## §8-BSUNG — Wishlist API + cập nhật `views.py` và `urls.py`

### Wishlist endpoints mới

Thêm vào `app/views.py`:

```python
from .models import WishlistItem
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class WishlistView(APIView):
    """
    GET  /recommendations/wishlist/<customer_id>/  — liệt kê wishlist
    POST /recommendations/wishlist/                — thêm sản phẩm
    """

    def get(self, request, customer_id):
        items = WishlistItem.objects.filter(customer_id=customer_id).values(
            "product_id", "added_at"
        )
        return Response({"customer_id": customer_id, "items": list(items)})

    def post(self, request):
        customer_id = request.data.get("customer_id")
        product_id  = request.data.get("product_id")
        if not customer_id or not product_id:
            return Response(
                {"error": "customer_id và product_id là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        obj, created = WishlistItem.objects.get_or_create(
            customer_id=customer_id,
            product_id=product_id,
        )
        return Response(
            {"customer_id": customer_id, "product_id": product_id, "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class WishlistItemView(APIView):
    """
    DELETE /recommendations/wishlist/<customer_id>/<product_id>/  — xoá khỏi wishlist
    """

    def delete(self, request, customer_id, product_id):
        deleted, _ = WishlistItem.objects.filter(
            customer_id=customer_id, product_id=product_id
        ).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
```

### `app/urls.py` đầy đủ (thay thế §8.1 plan gốc)

```python
from django.contrib import admin
from django.urls import path
from app.views import (
    RecommendationView,
    SimilarProductsView,
    ChatView,
    ChatHistoryView,
    WishlistView,       # MỚI
    WishlistItemView,   # MỚI
)

urlpatterns = [
    path("admin/",                                          admin.site.urls),
    # Recommendation
    path("recommendations/<int:customer_id>/",              RecommendationView.as_view(),   name="recommendations"),
    path("recommendations/similar/<int:product_id>/",       SimilarProductsView.as_view(),  name="similar-products"),
    # Wishlist (nội bộ — thay thế wishlist-service)
    path("recommendations/wishlist/",                       WishlistView.as_view(),         name="wishlist-list-create"),
    path("recommendations/wishlist/<int:customer_id>/",     WishlistView.as_view(),         name="wishlist-list"),
    path("recommendations/wishlist/<int:customer_id>/<int:product_id>/",
                                                            WishlistItemView.as_view(),     name="wishlist-item"),
    # Chat
    path("chat/",                                           ChatView.as_view(),             name="chat"),
    path("chat/<int:conversation_id>/",                     ChatHistoryView.as_view(),      name="chat-history"),
]
```

### Cập nhật `RecommendationView` để gắn `in_wishlist` flag

Trong `app/views.py`, cập nhật `RecommendationView.get`:

```python
class RecommendationView(APIView):
    def get(self, request, customer_id):
        from .services.recommender import build_recommendations
        from .models import WishlistItem

        recs = build_recommendations(customer_id)

        # Gắn in_wishlist flag để frontend hiển thị icon trái tim
        wishlist_ids = set(
            WishlistItem.objects.filter(customer_id=customer_id)
            .values_list("product_id", flat=True)
        )
        for r in recs:
            r["in_wishlist"] = r["product_id"] in wishlist_ids

        return Response({"customer_id": customer_id, "recommendations": recs})
```

---

## §7.2-BSUNG — `docker-compose.yml`: cập nhật `recommender-ai-service`

**Thay khối `recommender-ai-service` hiện tại bằng:**

```yaml
  recommender-ai-service:
    build:
      context: .
      dockerfile: recommender-ai-service/Dockerfile
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/recommender_db
      PRODUCT_SERVICE_URL:      http://product-service:8888
      COMMENT_RATE_SERVICE_URL: http://comment-rate-service:8888
      ORDER_SERVICE_URL:        http://order-service:8888       # ← MỚI
      CART_SERVICE_URL:         http://cart-service:8888        # ← MỚI
      LLM_PROVIDER:  ${LLM_PROVIDER:-openrouter}
      LLM_MODEL:     ${LLM_MODEL:-meta-llama/llama-3.1-8b-instruct:free}
      OPENROUTER_API_KEY:   ${OPENROUTER_API_KEY:-}
      OPENROUTER_SITE_URL:  ${OPENROUTER_SITE_URL:-http://localhost}
      OPENROUTER_APP_NAME:  ${OPENROUTER_APP_NAME:-BookStore AI}
      ANTHROPIC_API_KEY:    ${ANTHROPIC_API_KEY:-}
      OPENAI_API_KEY:       ${OPENAI_API_KEY:-}
    depends_on:
      postgres:
        condition: service_healthy
      product-service:
        condition: service_started
      comment-rate-service:
        condition: service_started
      order-service:           # ← MỚI
        condition: service_started
      cart-service:            # ← MỚI
        condition: service_started
```

---

## §6-BSUNG — Thay đổi cần thiết ở các service khác

Bổ sung vào bảng §6 của plan gốc:

| Service | Thay đổi | Bắt buộc cho MVP? |
|---|---|---|
| `order-service` | **Bắt buộc**: `OrderViewSet` cần hỗ trợ `?customer_id=` filter. Thêm `OrderFilter(FilterSet)` với `customer_id = NumberFilter(field_name='customer_id')`, đăng ký `filterset_class = OrderFilter` trong `OrderViewSet`. Response phải trả `items` với `product_id` trong mỗi order item. | **✅ Bắt buộc** (không có → `order_ids=[]`, signal mạnh nhất bị mất) |
| `cart-service` | **Bắt buộc**: Xác nhận endpoint. Client thử cả `GET /carts/?customer_id=` và `GET /carts/{customer_id}/`. Cần đảm bảo response trả `items` list với `product_id`. | **✅ Bắt buộc** (không có → `cart_ids=[]`) |
| `product-service` | Không thay đổi so với plan gốc. | Không |
| `comment-rate-service` | Không thay đổi. | Không |

### Cách thêm `customer_id` filter cho `order-service`

Nếu `order-service` chưa có filter này, thêm vào `order_service/app/views.py`:

```python
# order-service/order_service/app/views.py
import django_filters
from .models import Order
from rest_framework import viewsets

class OrderFilter(django_filters.FilterSet):
    customer_id = django_filters.NumberFilter(field_name='customer_id', lookup_expr='exact')

    class Meta:
        model = Order
        fields = ['customer_id']

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items').all()
    filterset_class = OrderFilter
    # ... giữ nguyên các config khác
```

```txt
# order-service/requirements.txt — kiểm tra đã có chưa, nếu chưa thêm:
django-filter>=23.0
```

---

## §9-BSUNG — Danh sách file cần tạo/sửa (bổ sung vào §9 plan gốc)

| File | Hành động | Thay thế/Bổ sung |
|---|---|---|
| `recommender-ai-service/.../app/models.py` | Thêm `WishlistItem` | Bổ sung §3 plan gốc |
| `recommender-ai-service/.../app/migrations/000X_add_wishlist_item.py` | Migration mới | Bổ sung |
| `recommender-ai-service/.../app/services/clients.py` | **Thay hoàn toàn** bằng version đầy đủ | Thay §5.4 plan gốc |
| `recommender-ai-service/.../app/services/recommender.py` | **Thay hoàn toàn** bằng multi-signal version | Thay §4.3 plan gốc |
| `recommender-ai-service/.../app/views.py` | Thêm `WishlistView`, `WishlistItemView`; cập nhật `RecommendationView` | Bổ sung §5.7 plan gốc |
| `recommender-ai-service/.../urls.py` | **Thay hoàn toàn** bằng urls đầy đủ | Thay §8.1 plan gốc |
| `docker-compose.yml` | Thêm `ORDER_SERVICE_URL`, `CART_SERVICE_URL`; thêm `depends_on` | Thay §7.2 plan gốc |
| `order-service/.../app/views.py` | Thêm `OrderFilter` + `filterset_class` | MỚI — Bắt buộc |
| `order-service/requirements.txt` | Xác nhận `django-filter>=23.0` | Kiểm tra |
| `CLAUDE.md` / `README.md` | Thêm routes `/api/recommendations/wishlist/` vào Gateway Proxy Routes | Bổ sung |

---

## §11-BSUNG — Kiểm thử bổ sung

### Smoke test multi-signal

```bash
# ─── 1. Thêm vào wishlist ──────────────────────────────────────────────────
curl -X POST http://localhost:8888/api/recommendations/wishlist/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "product_id": 5}'

# ─── 2. Xem wishlist ───────────────────────────────────────────────────────
curl http://localhost:8888/api/recommendations/wishlist/1/

# ─── 3. Gợi ý có kèm in_wishlist flag ────────────────────────────────────
curl http://localhost:8888/api/recommendations/1/
# → Sản phẩm cùng category với product_id=5 phải có score cao hơn
# → product_id=5 phải có in_wishlist=true

# ─── 4. Kiểm tra order signal ─────────────────────────────────────────────
# Seed 1 order cho customer_id=1 với product_id=X,
# rồi gọi recommendations: X phải bị exclude (đã mua), nhưng cùng-category-với-X phải có score cao

# ─── 5. Kiểm tra cart signal ──────────────────────────────────────────────
# Thêm product_id=Y vào cart của customer_id=1,
# gọi recommendations: Y phải bị exclude (đang trong giỏ), same-type sản phẩm tăng score

# ─── 6. Xoá khỏi wishlist ─────────────────────────────────────────────────
curl -X DELETE http://localhost:8888/api/recommendations/wishlist/1/5/
```

### Unit test bổ sung — `recommender.py`

```python
# tests/test_recommender.py

from unittest.mock import patch
from app.services.recommender import build_recommendations

def make_product(id, cat, ptype="book", price="100000"):
    return {"id": id, "category_id": cat, "product_type": ptype, "price": price, "is_active": True, "name": f"P{id}"}

@patch("app.services.clients.fetch_customer_signals")
@patch("app.services.clients.get_all_products")
@patch("app.services.clients.get_product_rating", return_value={"average_rating": 4.0, "total_reviews": 10})
def test_order_signal_excludes_and_boosts(mock_rating, mock_products, mock_signals):
    """Sản phẩm đã mua bị loại; cùng category được boost."""
    mock_products.return_value = [
        make_product(1, cat=10),   # đã mua → loại
        make_product(2, cat=10),   # cùng cat với 1 → cao điểm
        make_product(3, cat=20),   # cat khác → thấp hơn
    ]
    mock_signals.return_value = {
        "order_ids":    [1],
        "cart_ids":     [],
        "reviews":      [],
        "wishlist_ids": [],
    }
    recs = build_recommendations(customer_id=99)
    ids = [r["product_id"] for r in recs]
    assert 1 not in ids,  "Sản phẩm đã mua phải bị loại"
    assert ids[0] == 2,   "Sản phẩm cùng category phải được ưu tiên"


@patch("app.services.clients.fetch_customer_signals")
@patch("app.services.clients.get_all_products")
@patch("app.services.clients.get_product_rating", return_value={"average_rating": 4.5, "total_reviews": 5})
def test_wishlist_not_excluded(mock_rating, mock_products, mock_signals):
    """Sản phẩm trong wishlist KHÔNG bị loại — phải xuất hiện trong kết quả."""
    mock_products.return_value = [
        make_product(10, cat=5),   # trong wishlist
        make_product(11, cat=5),   # cùng cat
        make_product(12, cat=9),
    ]
    mock_signals.return_value = {
        "order_ids":    [],
        "cart_ids":     [],
        "reviews":      [],
        "wishlist_ids": [10],
    }
    recs = build_recommendations(customer_id=99)
    ids = [r["product_id"] for r in recs]
    assert 10 in ids, "Sản phẩm trong wishlist KHÔNG được loại"
    # p10 có wishlist signal (3.0) → category 5 được boost → p10 và p11 có score cao
    assert ids.index(10) <= ids.index(12), "Wishlist item phải xuất hiện trước sản phẩm khác category"


@patch("app.services.clients.fetch_customer_signals")
@patch("app.services.clients.get_all_products")
@patch("app.services.clients.get_product_rating", return_value={"average_rating": 3.8, "total_reviews": 50})
def test_cold_start_popularity_fallback(mock_rating, mock_products, mock_signals):
    """Khách mới không có tín hiệu → trả popularity fallback."""
    mock_products.return_value = [make_product(i, cat=1) for i in range(1, 15)]
    mock_signals.return_value = {
        "order_ids": [], "cart_ids": [], "reviews": [], "wishlist_ids": []
    }
    recs = build_recommendations(customer_id=999)
    assert len(recs) > 0, "Cold-start vẫn phải trả kết quả (popularity fallback)"
    assert all(r["reason"] == "Được nhiều khách đánh giá cao" for r in recs)
```

---

## §11.3-BSUNG — Definition of Done bổ sung

Bổ sung vào checklist §11.3 plan gốc:

- [ ] `POST /api/recommendations/wishlist/` với `{customer_id, product_id}` trả `201 Created`.
- [ ] `DELETE /api/recommendations/wishlist/<cid>/<pid>/` xoá thành công, trả `204 No Content`.
- [ ] `GET /api/recommendations/<customer_id>/` trả field `in_wishlist: true` cho sản phẩm đang trong wishlist của khách.
- [ ] Khi khách có ≥1 order, `order_ids` từ `order-service` được dùng để compute affinity — sản phẩm đã mua **không xuất hiện** trong kết quả.
- [ ] Khi khách có sản phẩm trong cart, chúng bị loại khỏi kết quả nhưng cùng-category được boost score.
- [ ] `fetch_customer_signals` dùng `ThreadPoolExecutor` — không gọi order/cart/review tuần tự (kiểm bằng `time` hay log).
- [ ] Nếu bất kỳ service nào (order/cart/comment-rate) down, `fetch_customer_signals` vẫn trả về dict với key bị lỗi là `[]` — không raise exception.

---

## Tóm tắt thay đổi (Quick Reference)

```
plan gốc §4.3  recommender.py   → THAY HOÀN TOÀN (multi-signal + ThreadPool)
plan gốc §5.4  clients.py       → THAY HOÀN TOÀN (thêm order/cart/wishlist clients)
plan gốc §3.1  models.py        → BỔ SUNG WishlistItem
plan gốc §8.1  urls.py          → BỔ SUNG wishlist routes
plan gốc §5.7  views.py         → BỔ SUNG WishlistView, WishlistItemView, cập nhật RecommendationView
plan gốc §7.2  docker-compose   → THÊM ORDER_SERVICE_URL, CART_SERVICE_URL, depends_on
plan gốc §6    service changes  → THÊM yêu cầu order-service filter by customer_id (bắt buộc)

MỚI HOÀN TOÀN: Wishlist model + 3 endpoints (thay thế wishlist-service không tồn tại)
```

> **Estimate bổ sung**: Phần này thêm ~1 ngày vào timeline (xác nhận endpoint cart/order,
> implement filter order-service, test multi-signal), đưa tổng Phase 0-3 lên khoảng **5-6 ngày**.


---

## KẾT LUẬN V2

Phiên bản v2 được xem là bản đầy đủ để triển khai MVP vì đã:
1. Bao gồm Recommendation Engine.
2. Bao gồm Chatbot RAG‑lite.
3. Bao gồm LLM Provider abstraction.
4. Bao gồm Conversation History.
5. Bao gồm Multi‑Signal Recommendation.
6. Bao gồm Wishlist nội bộ thay cho wishlist-service.
7. Bao gồm cập nhật docker-compose, env và gateway.
8. Bao gồm các thay đổi bắt buộc ở order-service và cart-service.

Khuyến nghị triển khai theo đúng thứ tự:
- Phase 1: Models + Migrations.
- Phase 2: Service Clients.
- Phase 3: Recommendation Engine.
- Phase 4: Chatbot.
- Phase 5: Gateway + Frontend Integration.
- Phase 6: Testing & Deployment.
