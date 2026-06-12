#!/bin/bash
# Test script cho AI Service

BASE_URL="http://localhost:8888"

echo "=========================================="
echo "Testing AI Service Endpoints"
echo "=========================================="

# Test 1: Health Check
echo -e "\n1. Health Check..."
curl -s "$BASE_URL/health/" | jq '.'

# Test 2: Get Recommendations for customer 1
echo -e "\n2. Get Recommendations for customer_id=1..."
curl -s "$BASE_URL/api/recommendations/1/" | jq '.'

# Test 3: Get Similar Products for product 1
echo -e "\n3. Get Similar Products for product_id=1..."
curl -s "$BASE_URL/api/recommendations/similar/1/" | jq '.'

# Test 4: Add to Wishlist
echo -e "\n4. Add product_id=2 to wishlist for customer_id=1..."
curl -s -X POST "$BASE_URL/api/recommendations/wishlist/" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "product_id": 2}' | jq '.'

# Test 5: Get Wishlist
echo -e "\n5. Get Wishlist for customer_id=1..."
curl -s "$BASE_URL/api/recommendations/wishlist/?customer_id=1" | jq '.'

# Test 6: Chat with Bot
echo -e "\n6. Chat with bot..."
curl -s -X POST "$BASE_URL/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tôi muốn mua laptop dưới 20 triệu", "customer_id": 1, "session_id": "test-session"}' | jq '.'

# Test 7: Get Conversation History
echo -e "\n7. Get conversation history..."
# Get the conversation_id from the previous response
CONV_ID=$(curl -s -X POST "$BASE_URL/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "Có loại nào rẻ hơn không?", "customer_id": 1, "session_id": "test-session"}' | jq -r '.conversation_id')

curl -s "$BASE_URL/api/chat/$CONV_ID/" | jq '.'

# Test 8: Remove from Wishlist
echo -e "\n8. Remove product_id=2 from wishlist..."
curl -s -X DELETE "$BASE_URL/api/recommendations/wishlist/1/2/" | jq '.'

echo -e "\n=========================================="
echo "All tests completed!"
echo "=========================================="
