"""
OpenRouter LLM provider — uses OpenRouter API with a free model.
Default provider for MVP — free, no credit card required.
"""

import os
from .base import BaseLLMProvider

try:
    import openai
except ImportError:
    openai = None


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter provider — uses free model, no cost."""

    def __init__(self):
        if openai is None:
            raise ImportError("openai package not installed. Run: pip install openai>=1.0.0")

        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self.model = os.environ.get("LLM_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

    def generate_answer(self, message, products, history, store_faq):
        """Call OpenRouter API to generate a response."""
        # Build context from products
        if products:
            product_lines = []
            for p in products[:5]:  # Limit to 5 products to avoid long context
                price = f"${float(p.get('price', 0)):,.0f}"
                product_lines.append(f"- {p['name']} ({p.get('product_type', '')}) - {price}")
            product_context = "\n".join(product_lines)
        else:
            product_context = "No relevant products found."

        # Build system prompt
        system_prompt = f"""You are a helpful shopping assistant for Store — an online store selling books, laptops, phones, and clothing. Answer the customer's questions in a friendly and professional manner.

STORE INFORMATION:
{store_faq}

RELEVANT PRODUCTS FOR THE CURRENT QUERY:
{product_context}

GUIDELINES:
- Answer concisely and clearly (2-4 sentences)
- If relevant products exist, introduce the 1-3 best matches with their prices
- If no relevant products were found for the specific query, mention what the store DOES have available (books, laptops, phones, clothing) and suggest the customer describe their needs more clearly
- DO NOT invent products not in the list above
- Use store FAQ information when relevant
- If the user's message is a greeting or general question, respond naturally"""

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add chat history (max 5 most recent messages)
        for msg in history[-5:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current question
        messages.append({"role": "user", "content": message})

        # Call API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=400,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenRouter API error: {e}")
            # Fallback to mock if API fails
            from .mock_provider import MockLLMProvider
            return MockLLMProvider().generate_answer(message, products, history, store_faq)
