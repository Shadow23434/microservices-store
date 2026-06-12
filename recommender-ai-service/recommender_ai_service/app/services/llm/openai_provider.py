"""
OpenAI LLM provider — uses GPT API.
Alternative provider for using OpenAI instead of Anthropic/OpenRouter.
"""

import os
from .base import BaseLLMProvider

try:
    import openai
except ImportError:
    openai = None


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider — high quality, paid."""

    def __init__(self):
        if openai is None:
            raise ImportError("openai package not installed. Run: pip install openai>=1.0.0")

        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = os.environ.get("LLM_MODEL", "gpt-3.5-turbo")

    def generate_answer(self, message, products, history, store_faq):
        """Call OpenAI API to generate a response."""
        # Build context from products
        if products:
            product_lines = []
            for p in products[:5]:
                price = f"${float(p.get('price', 0)):,.0f}"
                product_lines.append(f"- {p['name']} ({p.get('product_type', '')}) - {price}")
            product_context = "\n".join(product_lines)
        else:
            product_context = "No relevant products found."

        # Build system prompt
        system_prompt = f"""You are a helpful shopping assistant for BookStore. Please answer the customer's questions in a friendly and professional manner in English.

STORE INFORMATION:
{store_faq}

RELEVANT PRODUCTS FOR THE CURRENT QUERY:
{product_context}

GUIDELINES:
- Answer concisely and clearly (2-4 sentences)
- If relevant products exist, introduce the 1-3 best matches
- If no relevant products, suggest the customer describe their needs more clearly
- DO NOT invent products not in the list above
- Use store FAQ information when relevant"""

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
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
            print(f"OpenAI API error: {e}")
            # Fallback to mock if API fails
            from .mock_provider import MockLLMProvider
            return MockLLMProvider().generate_answer(message, products, history, store_faq)
