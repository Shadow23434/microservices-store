# AI Service (Recommender AI Service)

## Tổng quan

AI Service cung cấp các tính năng thông minh cho hệ thống e-commerce:

1. **Recommendation Engine**: Gợi ý sản phẩm dựa trên đa tín hiệu (order history, wishlist, cart, reviews)
2. **Similar Products**: Tìm sản phẩm tương tự
3. **Wishlist**: Quản lý danh sách yêu thích
4. **Chatbot**: Tư vấn sản phẩm bằng AI (RAG-lite với LLM)

## Kiến trúc

### Multi-Signal Recommendation

Sử dụng 5 tín hiệu với trọng số khác nhau:

| Tín hiệu | Trọng số | Nguồn | Ghi chú |
|----------|----------|-------|---------|
| Order History | 4.0 | order-service | Sản phẩm đã mua |
| Wishlist | 3.0 | recommender_db (local) | Sản phẩm yêu thích |
| Cart | 2.5 | cart-service | Sản phẩm trong giỏ |
| Review ≥4★ | 2.0 | comment-rate-service | Đánh giá tích cực |
| Review <4★ | 0.5 | comment-rate-service | Đánh giá tiêu cực |

**Công thức tính điểm:**
```
score = 3.0 × category_affinity + 1.0 × type_affinity
```

### Chatbot (RAG-lite)

Luồng xử lý:
1. User gửi câu hỏi → ChatView
2. NLP Extractor trích xuất filters (product_type, price_range, keywords)
3. Clients.py gọi product-service tìm sản phẩm phù hợp
4. LLM Provider sinh câu trả lời dựa trên context
5. Lưu conversation vào database

**LLM Providers hỗ trợ:**
- `mock`: Rule-based, không cần API key (cho dev/test)
- `openrouter`: Default, dùng free model (khuyến nghị cho MVP)
- `anthropic`: Claude API (production)
- `openai`: GPT API (production)

## API Endpoints

### 1. Recommendations

**GET /api/recommendations/{customer_id}/**

Trả về danh sách sản phẩm gợi ý cho khách hàng.

Response:
```json
{
  "customer_id": 1,
  "recommendations": [
    {
      "product_id": 101,
      "name": "Laptop Dell XPS 13",
      "product_type": "laptop",
      "price": "25000000.00",
      "score": 8.5,
      "reason": "Dựa trên lịch sử mua hàng của bạn",
      "average_rating": 4.5,
      "total_reviews": 120,
      "in_wishlist": false
    }
  ]
}
```

### 2. Similar Products

**GET /api/recommendations/similar/{product_id}/**

Trả về các sản phẩm tương tự (cùng category hoặc type).

Response:
```json
{
  "product_id": 101,
  "similar_products": [
    {
      "id": 102,
      "name": "Laptop HP Spectre x360",
      "product_type": "laptop",
      "price": "28000000.00"
    }
  ]
}
```

### 3. Wishlist

**GET /api/recommendations/wishlist/?customer_id={id}**

Lấy danh sách wishlist của khách hàng.

**POST /api/recommendations/wishlist/**

Thêm sản phẩm vào wishlist.

Request:
```json
{
  "customer_id": 1,
  "product_id": 101
}
```

**DELETE /api/recommendations/wishlist/{customer_id}/{product_id}/**

Xóa sản phẩm khỏi wishlist.

### 4. Chat

**POST /api/chat/**

Gửi câu hỏi và nhận câu trả lời từ chatbot.

Request:
```json
{
  "message": "Tôi muốn mua laptop dưới 20 triệu",
  "customer_id": 1,
  "session_id": "abc123"
}
```

Response:
```json
{
  "conversation_id": 5,
  "answer": "Dựa trên yêu cầu của bạn, tôi đề xuất Laptop Dell XPS 13 với giá 25 triệu...",
  "products": [
    {
      "id": 101,
      "name": "Laptop Dell XPS 13",
      "price": "25000000.00"
    }
  ]
}
```

**GET /api/chat/{conversation_id}/**

Lấy lịch sử conversation.

## Cấu hình

### Environment Variables

Trong `docker-compose.yml`:

```yaml
LLM_PROVIDER: mock  # mock | openrouter | anthropic | openai
LLM_MODEL: meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_API_KEY: your_openrouter_key
ANTHROPIC_API_KEY: your_anthropic_key
OPENAI_API_KEY: your_openai_key
```

### Lấy OpenRouter API Key

1. Đăng ký tại https://openrouter.ai
2. Vào Settings → API Keys
3. Tạo key mới (miễn phí)
4. Thêm vào `.env`: `OPENROUTER_API_KEY=sk-or-v1-...`

## Development

### Chạy service

```bash
docker-compose up recommender-ai-service
```

### Test với curl

```bash
# Get recommendations
curl http://localhost:8888/api/recommendations/1/

# Get similar products
curl http://localhost:8888/api/recommendations/similar/101/

# Add to wishlist
curl -X POST http://localhost:8888/api/recommendations/wishlist/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "product_id": 101}'

# Chat with bot
curl -X POST http://localhost:8888/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Tôi muốn mua laptop dưới 20 triệu", "customer_id": 1}'
```

## Cấu trúc thư mục

```
recommender-ai-service/
├── app/
│   ├── models.py              # Recommendation, WishlistItem, Conversation, ChatMessage
│   ├── views.py               # API endpoints
│   ├── serializers.py         # DRF serializers
│   └── services/
│       ├── __init__.py
│       ├── clients.py         # Gọi các service khác (ThreadPoolExecutor)
│       ├── recommender.py     # Multi-signal recommendation engine
│       ├── nlp.py             # Extract filters từ câu hỏi
│       ├── store_faq.py       # FAQ tĩnh về cửa hàng
│       └── llm/
│           ├── __init__.py
│           ├── base.py        # Abstract base class
│           ├── mock_provider.py
│           ├── openrouter_provider.py
│           ├── anthropic_provider.py
│           ├── openai_provider.py
│           └── factory.py     # Factory pattern
└── recommender_ai_service/
    └── urls.py                # URL routing
```

## Troubleshooting

### Service calls timeout

Kiểm tra:
- Các service phụ thuộc có đang chạy không
- Environment variables `*_SERVICE_URL` có đúng không
- Network trong docker-compose

### LLM không trả lời

Kiểm tra:
- `LLM_PROVIDER` có được set không
- API key có hợp lệ không (nếu dùng openrouter/anthropic/openai)
- Xem logs: `docker-compose logs recommender-ai-service`

### Recommendations trống

Nguyên nhân có thể:
- Khách hàng mới, chưa có tín hiệu (cold-start) → trả về popularity-based
- Service calls lỗi → check logs
- Không có sản phẩm phù hợp → check product-service

## Performance

- **ThreadPoolExecutor**: Gọi song song các service (giảm latency)
- **Timeout**: 5s cho mỗi service call
- **Fallback**: Nếu service lỗi, trả về kết quả rỗng hoặc popularity-based

## Roadmap

### Phase 1 (Current - MVP)
- ✅ Multi-signal recommendation
- ✅ Similar products
- ✅ Wishlist management
- ✅ Chatbot với RAG-lite
- ✅ LLM provider abstraction

### Phase 2 (Future)
- ⏳ Semantic search với vector embeddings
- ⏳ Real-time recommendation (WebSocket)
- ⏳ A/B testing framework
- ⏳ Advanced analytics dashboard
