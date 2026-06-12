from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Recommendation, WishlistItem, Conversation, ChatMessage
from .serializers import (
    RecommendationSerializer,
    ChatRequestSerializer,
    WishlistItemSerializer,
)
from .services import recommender
from .services import nlp
from .services import clients
from .services import store_faq
from .services.llm.factory import get_llm_provider


class RecommendationView(APIView):
    """
    GET /api/recommendations/<customer_id>/
    Returns a list of recommended products based on multi-signal analysis
    (order history, wishlist, cart, reviews).
    """
    def get(self, request, customer_id):
        recs = recommender.build_recommendations(customer_id)

        # Save results to DB
        rec_obj, _ = Recommendation.objects.get_or_create(customer_id=customer_id)
        rec_obj.set_product_ids([r["product_id"] for r in recs])
        rec_obj.algorithm = "multi_signal"
        rec_obj.reason = recs[0]["reason"] if recs else ""
        rec_obj.save()

        serializer = RecommendationSerializer(rec_obj)
        return Response({
            "customer_id": customer_id,
            "recommendations": recs,
            "cached_at": rec_obj.updated_at,
        })


class SimilarProductsView(APIView):
    """
    GET /api/recommendations/similar/<product_id>/
    Returns a list of products similar to the given product.
    """
    def get(self, request, product_id):
        similar = recommender.build_similar_products(product_id, limit=6)
        return Response({
            "product_id": product_id,
            "similar_products": similar,
        })


class WishlistView(APIView):
    """
    GET  /api/recommendations/wishlist/?customer_id=<id>  — list wishlist items
    POST /api/recommendations/wishlist/                   — add product to wishlist
    """
    def get(self, request):
        customer_id = request.query_params.get("customer_id")
        if not customer_id:
            return Response(
                {"error": "customer_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        items = WishlistItem.objects.filter(customer_id=customer_id)
        serializer = WishlistItemSerializer(items, many=True)
        return Response({
            "customer_id": customer_id,
            "wishlist_items": serializer.data,
        })

    def post(self, request):
        serializer = WishlistItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WishlistItemView(APIView):
    """
    DELETE /api/recommendations/wishlist/<customer_id>/<product_id>/
    Remove a product from the wishlist.
    """
    def delete(self, request, customer_id, product_id):
        try:
            item = WishlistItem.objects.get(
                customer_id=customer_id,
                product_id=product_id,
            )
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WishlistItem.DoesNotExist:
            return Response(
                {"error": "Wishlist item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class ChatView(APIView):
    """
    POST /api/chat/
    Product consultation chatbot: receives questions, extracts filters,
    finds matching products, and generates responses via LLM.
    """
    def post(self, request):
        try:
            serializer = ChatRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            message = serializer.validated_data["message"]
            customer_id = serializer.validated_data.get("customer_id")
            session_id = serializer.validated_data.get("session_id", "")

            # 1. Create or retrieve current conversation
            if customer_id:
                conversation = Conversation.objects.filter(customer_id=customer_id).last()
                if not conversation:
                    conversation = Conversation.objects.create(
                        customer_id=customer_id,
                        session_id=session_id,
                    )
            else:
                # Guest user — create new conversation with session_id
                conversation = Conversation.objects.create(session_id=session_id)

            # 2. Save user message
            ChatMessage.objects.create(
                conversation=conversation,
                role="user",
                content=message,
            )

            # 3. Extract filters from the question
            filters = nlp.extract_filters(message)

            # 4. Find matching products
            products = clients.search_products(filters)

            # 5. Get chat history
            history = [
                {"role": m.role, "content": m.content}
                for m in ChatMessage.objects.filter(conversation=conversation).order_by("created_at")
            ]

            # 6. Call LLM to generate response
            llm_provider = get_llm_provider()
            answer = llm_provider.generate_answer(
                message=message,
                products=products,
                history=history,
                store_faq=store_faq.STORE_FAQ,
            )

            # 7. Save assistant message
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
        except Exception as e:
            print(f"ChatView error: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": "Sorry, the system is currently experiencing issues. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChatHistoryView(APIView):
    """
    GET /api/chat/<conversation_id>/
    Retrieve chat history for a given conversation.
    """
    def get(self, request, conversation_id):
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        messages = ChatMessage.objects.filter(conversation=conversation).order_by("created_at")

        # Build response with product info for assistant messages
        message_list = []
        for msg in messages:
            msg_data = {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            }

            # If assistant message has associated products, attach them
            if msg.role == "assistant" and msg.product_ids:
                product_ids = msg.get_product_ids()
                if product_ids:
                    all_products = clients.get_all_products()
                    products = [p for p in all_products if p["id"] in product_ids]
                    msg_data["products"] = products

            message_list.append(msg_data)

        return Response({
            "conversation_id": conversation.id,
            "customer_id": conversation.customer_id,
            "messages": message_list,
        })


class HealthCheckView(APIView):
    """
    GET /health/
    Health check endpoint for recommender-ai-service.
    """
    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "recommender-ai-service",
        })
