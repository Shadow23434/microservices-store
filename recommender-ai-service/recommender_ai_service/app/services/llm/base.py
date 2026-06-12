"""
Base class for LLM providers.
All providers (mock, openrouter, anthropic, openai) must implement this interface.
"""

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate_answer(self, message, products, history, store_faq):
        """
        Generate a response based on the question, products, chat history, and FAQ.

        Args:
            message (str): Current user question
            products (list): List of matching products from product-service
            history (list): Recent chat history [{"role": "user|assistant", "content": "..."}]
            store_faq (str): Store FAQ information

        Returns:
            str: Response text in English
        """
        pass
