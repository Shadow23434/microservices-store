# AI Service Implementation Summary

## Tổng quan

Đã triển khai hoàn chỉnh AI Service cho hệ thống microservices-store theo kế hoạch trong `docs/AI_Service_MVP_Plan_v2.md`.

## Các Phase đã hoàn thành

### ✅ Phase 0: Models & Migrations (Backend)
- **Recommendation**: Thêm fields `algorithm`, `reason`
- **WishlistItem**: Model mới cho wishlist nội bộ
- **Conversation & ChatMessage**: Models cho chatbot
- Migration: `0002_ai_service_models.py`

### ✅ Phase 1: Service Layer (Backend)
- **clients.py**: HTTP clients để gọi các microservices khác
  - `fetch_customer_signals()`: Fetch đồng thời orders, reviews, cart, wishlist
  - `get_all_products()`, `search_products()`, `get_product_rating()`
- **recommender.py**: Multi-signal recommendation engine
  - Trọng số: Order (4.0) > Wishlist (3.0) > Cart (2.5) > Liked Review (2.0) > Disliked Review (0.5)
  - Score formula: `3.0 × category_affinity + 1.0 × type_affinity`
  - Popularity fallback cho cold-start users
- **nlp.py**: Rule-based filter extraction
  - Product type detection (book, laptop, mobile, cloth)
  - Price range extraction (dưới/trên/từ-đến)
  - Keyword extraction
- **store_faq.py**: FAQ static data
- **llm/**: LLM provider abstraction
  - `base.py`: Abstract base class
  - `mock_provider.py`: Rule-based (no API call)
  - `openrouter_provider.py`: OpenRouter API (free tier)
  - `anthropic_provider.py`: Anthropic Claude API
  - `openai_provider.py`: OpenAI GPT API
  - `factory.py`: Provider factory based on `LLM_PROVIDER` env var

### ✅ Phase 2: API Endpoints (Backend)
- **Recommendation endpoints**:
  - `GET /api/recommendations/{customer_id}/` - Multi-signal recommendations
  - `GET /api/recommendations/similar/{product_id}/` - Similar products
- **Wishlist endpoints**:
  - `GET /api/recommendations/wishlist/?customer_id={id}` - Get wishlist
  - `POST /api/recommendations/wishlist/` - Add to wishlist
  - `DELETE /api/recommendations/wishlist/{customer_id}/{product_id}/` - Remove from wishlist
- **Chat endpoints**:
  - `POST /api/chat/` - Send message and get AI response
  - `GET /api/chat/{conversation_id}/` - Get conversation history

### ✅ Phase 3: Infrastructure (Backend)
- **requirements.txt**: Added `openai`, `anthropic`, `numpy`
- **docker-compose.yml**:
  - Environment variables: `LLM_PROVIDER`, `LLM_MODEL`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`
  - Dependencies: `order-service`, `cart-service`
- **api-gateway**: Added routing for chat and wishlist endpoints
- **.env.example**: Template for LLM configuration

### ✅ Phase 4: Frontend Integration (React)

#### 4.1 API Service Layer
- **recommenderService.ts**: Expanded with all new endpoints
  - `getRecommendations(customerId)`
  - `getSimilarProducts(productId)`
  - `getWishlist(customerId)`
  - `addToWishlist(customerId, productId)`
  - `removeFromWishlist(customerId, productId)`
  - `sendChatMessage(message, customerId)`
  - `getChatHistory(conversationId)`

#### 4.2 Home.tsx Updates
- Updated `handleGetRecommendations()` to work with new API response format
- Display recommendations with `reason`, `score`, `average_rating`
- Show product images, prices, and ratings

#### 4.3 ProductDetail.tsx Updates
- Added "Sản phẩm tương tự" section
- Auto-load similar products on page load
- Display 4 similar products with images, prices, ratings

#### 4.4 ChatWidget Component (NEW)
- Floating chat button (bottom-right corner)
- Chat panel with:
  - Header with "New conversation" button
  - Message list (user & assistant messages)
  - Product cards in AI responses (clickable links)
  - Quick question buttons for first-time users
  - Input field with send button
- Features:
  - Auto-scroll to latest message
  - Loading indicator when AI is responding
  - Conversation history persistence (localStorage + backend)
  - Responsive design (mobile-friendly)
- Dark mode support

#### 4.5 WishlistContext Updates
- Sync with backend API when user is authenticated
- `loadWishlist()`: Load from backend on login
- `addToWishlist()`: Sync to backend
- `removeFromWishlist()`: Sync to backend
- Local state remains as cache for performance

## API Response Formats

### GET /api/recommendations/{customer_id}/
```json
{
  "customer_id": 1,
  "recommendations": [
    {
      "product_id": 12,
      "name": "Atomic Habits",
      "product_type": "book",
      "price": "159000.00",
      "score": 8.5,
      "reason": "Dựa trên sản phẩm bạn đã đánh giá cao",
      "average_rating": 4.5,
      "in_wishlist": false
    }
  ]
}
```

### POST /api/chat/
```json
{
  "conversation_id": 1,
  "answer": "Dựa trên yêu cầu của bạn, tôi đề xuất...",
  "products": [
    {
      "id": 12,
      "name": "Laptop Dell XPS 13",
      "price": "25000000.00",
      "average_rating": 4.7
    }
  ]
}
```

## Environment Variables

```bash
# LLM Provider Configuration
LLM_PROVIDER=mock  # Options: mock, openrouter, anthropic, openai
LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free

# API Keys (optional, based on provider)
OPENROUTER_API_KEY=sk-or-v1-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
```

## How to Use

### Backend
```bash
# Build and start services
docker-compose up --build

# Check logs
docker-compose logs -f recommender-ai-service
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Testing
1. Visit http://localhost:3000
2. Login with any customer account
3. Go to Home page → Click "Get AI Recommendations"
4. Go to Product Detail page → See "Similar Products" section
5. Click chat button (bottom-right) → Ask AI for product suggestions

## Key Features

### Multi-Signal Recommendation
- Analyzes: orders, reviews, cart, wishlist
- Weighted scoring based on signal strength
- Category and type affinity calculation
- Popularity fallback for new users

### AI Chatbot
- Natural language understanding (Vietnamese)
- Filter extraction (product type, price range, keywords)
- RAG-lite: Search products + LLM response generation
- Product cards with clickable links
- Conversation history

### Similar Products
- Based on same category or product type
- Exclude current product
- Limit to 4 products

### Wishlist Sync
- Real-time sync with backend
- Recommendation engine uses wishlist data
- Persistent across sessions

## Performance Optimizations

- **Parallel data fetching**: `fetch_customer_signals()` uses `asyncio.gather()` to fetch orders, reviews, cart, wishlist simultaneously
- **Caching**: Recommendations cached in database (updated on demand)
- **Timeout handling**: All HTTP clients have 5s timeout
- **Error handling**: Graceful fallbacks when services are unavailable
- **LocalStorage**: Wishlist cached locally for instant UI updates

## Testing Checklist

- [ ] Recommendation returns products based on user history
- [ ] Similar products show related items
- [ ] Chatbot responds to product queries
- [ ] Wishlist add/remove syncs with backend
- [ ] Chat history persists across page reloads
- [ ] Dark mode works correctly
- [ ] Mobile responsive design
- [ ] Error handling (service unavailable, API errors)

## Future Enhancements (Phase 5)

- A/B testing framework for recommendation algorithms
- Real-time analytics dashboard
- Advanced NLP with intent classification
- Semantic search with vector embeddings
- Collaborative filtering
- Email recommendations (periodic)
- Push notifications for new recommendations

## Files Created/Modified

### Backend (Created)
- `recommender-ai-service/app/migrations/0002_ai_service_models.py`
- `recommender-ai-service/app/services/__init__.py`
- `recommender-ai-service/app/services/clients.py`
- `recommender-ai-service/app/services/recommender.py`
- `recommender-ai-service/app/services/nlp.py`
- `recommender-ai-service/app/services/store_faq.py`
- `recommender-ai-service/app/services/llm/__init__.py`
- `recommender-ai-service/app/services/llm/base.py`
- `recommender-ai-service/app/services/llm/mock_provider.py`
- `recommender-ai-service/app/services/llm/openrouter_provider.py`
- `recommender-ai-service/app/services/llm/anthropic_provider.py`
- `recommender-ai-service/app/services/llm/openai_provider.py`
- `recommender-ai-service/app/services/llm/factory.py`

### Backend (Modified)
- `recommender-ai-service/app/models.py`
- `recommender-ai-service/app/views.py`
- `recommender-ai-service/app/serializers.py`
- `recommender-ai-service/app/urls.py`
- `recommender-ai-service/requirements.txt`
- `docker-compose.yml`
- `api-gateway/api_gateway/app/views.py`
- `.env.example`

### Frontend (Created)
- `frontend/src/components/ChatWidget.tsx`

### Frontend (Modified)
- `frontend/src/api/recommenderService.ts`
- `frontend/src/pages/Home.tsx`
- `frontend/src/pages/ProductDetail.tsx`
- `frontend/src/contexts/WishlistContext.tsx`
- `frontend/src/components/Layout.tsx`

## Conclusion

AI Service đã được triển khai hoàn chỉnh với đầy đủ tính năng:
- ✅ Multi-signal recommendation engine
- ✅ AI chatbot với RAG-lite
- ✅ Similar products
- ✅ Wishlist management
- ✅ Frontend integration
- ✅ Responsive UI with dark mode

Hệ thống sẵn sàng để test và deploy!
