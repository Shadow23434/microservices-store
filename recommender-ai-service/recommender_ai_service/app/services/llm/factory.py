"""
Factory function để lấy LLM provider dựa trên environment variable.
"""

import os


def get_llm_provider():
    """
    Trả về LLM provider instance dựa trên LLM_PROVIDER environment variable.

    Supported values:
        - "mock" (default): MockLLMProvider — không cần API key
        - "openrouter": OpenRouterProvider — free model, không tốn phí
        - "anthropic": AnthropicProvider — Claude, có phí
        - "openai": OpenAIProvider — GPT, có phí

    Returns:
        BaseLLMProvider instance
    """
    provider_name = os.environ.get("LLM_PROVIDER", "mock").lower()

    if provider_name == "openrouter":
        try:
            from .openrouter_provider import OpenRouterProvider
            return OpenRouterProvider()
        except Exception as e:
            print(f"Warning: Cannot load OpenRouter provider: {e}. Falling back to mock.")
            from .mock_provider import MockLLMProvider
            return MockLLMProvider()

    elif provider_name == "anthropic":
        try:
            from .anthropic_provider import AnthropicProvider
            return AnthropicProvider()
        except Exception as e:
            print(f"Warning: Cannot load Anthropic provider: {e}. Falling back to mock.")
            from .mock_provider import MockLLMProvider
            return MockLLMProvider()

    elif provider_name == "openai":
        try:
            from .openai_provider import OpenAIProvider
            return OpenAIProvider()
        except Exception as e:
            print(f"Warning: Cannot load OpenAI provider: {e}. Falling back to mock.")
            from .mock_provider import MockLLMProvider
            return MockLLMProvider()

    else:
        # Default to mock
        if provider_name != "mock":
            print(f"Warning: Unknown LLM_PROVIDER '{provider_name}'. Using mock.")
        from .mock_provider import MockLLMProvider
        return MockLLMProvider()
