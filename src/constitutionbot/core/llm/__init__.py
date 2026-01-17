"""LLM Provider abstraction module.

This module provides a unified interface for multiple LLM providers:
- Anthropic Claude
- OpenAI GPT
- Ollama (local models)

Usage:
    from constitutionbot.core.llm import LLMProviderFactory, LLMProvider

    # Async usage (with database session)
    provider = await LLMProviderFactory.create_provider(session)

    # Sync usage (env vars only)
    provider = LLMProviderFactory.create_provider_sync()

    # Generate content
    response = provider.generate("Your prompt here")
"""

from constitutionbot.core.llm.base import BaseLLMProvider
from constitutionbot.core.llm.config import (
    AVAILABLE_MODELS,
    AnthropicConfig,
    LLMConfig,
    LLMProviderType,
    OllamaConfig,
    OpenAIConfig,
)
from constitutionbot.core.llm.factory import (
    LLMProviderFactory,
    get_llm_provider,
    get_llm_provider_sync,
)
from constitutionbot.core.llm.protocol import LLMProvider
from constitutionbot.core.llm.providers import (
    AnthropicProvider,
    OllamaProvider,
    OpenAIProvider,
)

__all__ = [
    # Protocol and base
    "LLMProvider",
    "BaseLLMProvider",
    # Factory
    "LLMProviderFactory",
    "get_llm_provider",
    "get_llm_provider_sync",
    # Provider implementations
    "AnthropicProvider",
    "OpenAIProvider",
    "OllamaProvider",
    # Configuration
    "LLMProviderType",
    "LLMConfig",
    "AnthropicConfig",
    "OpenAIConfig",
    "OllamaConfig",
    "AVAILABLE_MODELS",
]
