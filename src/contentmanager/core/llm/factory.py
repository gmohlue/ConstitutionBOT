"""Factory for creating LLM providers."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from contentmanager.config import get_settings
from contentmanager.core.llm.config import LLMProviderType
from contentmanager.core.llm.protocol import LLMProvider
from contentmanager.core.llm.providers.anthropic import AnthropicProvider
from contentmanager.core.llm.providers.ollama import OllamaProvider
from contentmanager.core.llm.providers.openai import OpenAIProvider


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    @classmethod
    async def create_provider(
        cls,
        session: AsyncSession,
        provider_type: Optional[str] = None,
    ) -> LLMProvider:
        """Create an LLM provider with credentials from database or env.

        This method first checks the database for stored credentials,
        then falls back to environment variables.

        Args:
            session: Database session for fetching stored credentials
            provider_type: Optional provider type override. If not specified,
                          uses the configured default provider.

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If no valid provider can be configured
        """
        from contentmanager.database.repositories.credentials import CredentialsRepository

        settings = get_settings()
        repo = CredentialsRepository(session)

        # Determine provider type
        if provider_type is None:
            # Check if LLM_PROVIDER is set, otherwise default to anthropic
            provider_type = getattr(settings, "llm_provider", "anthropic")

        provider_type = LLMProviderType(provider_type)

        if provider_type == LLMProviderType.ANTHROPIC:
            # Try database first, then env
            api_key = await repo.get_credential("anthropic_api_key")
            if not api_key:
                api_key = settings.anthropic_api_key.get_secret_value()

            if not api_key:
                raise ValueError(
                    "Anthropic API key not configured. Set ANTHROPIC_API_KEY or "
                    "configure via dashboard."
                )

            model = getattr(settings, "anthropic_model", "claude-sonnet-4-20250514")
            max_tokens = getattr(settings, "anthropic_max_tokens", 4096)

            return AnthropicProvider(
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
            )

        elif provider_type == LLMProviderType.OPENAI:
            # Try database first, then env
            api_key = await repo.get_credential("openai_api_key")
            if not api_key:
                api_key = getattr(settings, "openai_api_key", None)
                if api_key:
                    api_key = api_key.get_secret_value()

            if not api_key:
                raise ValueError(
                    "OpenAI API key not configured. Set OPENAI_API_KEY or "
                    "configure via dashboard."
                )

            model = getattr(settings, "openai_model", "gpt-4o")
            max_tokens = getattr(settings, "openai_max_tokens", 4096)

            return OpenAIProvider(
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
            )

        elif provider_type == LLMProviderType.OLLAMA:
            host = getattr(settings, "ollama_host", "http://localhost:11434")
            model = getattr(settings, "ollama_model", "llama3.2")
            max_tokens = getattr(settings, "ollama_max_tokens", 4096)

            provider = OllamaProvider(
                host=host,
                model=model,
                max_tokens=max_tokens,
            )

            if not provider.is_available():
                raise ValueError(
                    f"Ollama not available at {host} or model '{model}' not found. "
                    f"Ensure Ollama is running and the model is pulled."
                )

            return provider

        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    @classmethod
    def create_provider_sync(
        cls,
        provider_type: Optional[str] = None,
    ) -> LLMProvider:
        """Create an LLM provider using only environment variables.

        This is a synchronous fallback for contexts where async is not available.
        Only uses environment variables, not database-stored credentials.

        Args:
            provider_type: Optional provider type override

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If no valid provider can be configured
        """
        settings = get_settings()

        # Determine provider type
        if provider_type is None:
            provider_type = getattr(settings, "llm_provider", "anthropic")

        provider_type = LLMProviderType(provider_type)

        if provider_type == LLMProviderType.ANTHROPIC:
            api_key = settings.anthropic_api_key.get_secret_value()
            if not api_key:
                raise ValueError(
                    "Anthropic API key not configured. Set ANTHROPIC_API_KEY."
                )

            model = getattr(settings, "anthropic_model", "claude-sonnet-4-20250514")
            max_tokens = getattr(settings, "anthropic_max_tokens", 4096)

            return AnthropicProvider(
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
            )

        elif provider_type == LLMProviderType.OPENAI:
            api_key = getattr(settings, "openai_api_key", None)
            if api_key:
                api_key = api_key.get_secret_value()

            if not api_key:
                raise ValueError(
                    "OpenAI API key not configured. Set OPENAI_API_KEY."
                )

            model = getattr(settings, "openai_model", "gpt-4o")
            max_tokens = getattr(settings, "openai_max_tokens", 4096)

            return OpenAIProvider(
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
            )

        elif provider_type == LLMProviderType.OLLAMA:
            host = getattr(settings, "ollama_host", "http://localhost:11434")
            model = getattr(settings, "ollama_model", "llama3.2")
            max_tokens = getattr(settings, "ollama_max_tokens", 4096)

            provider = OllamaProvider(
                host=host,
                model=model,
                max_tokens=max_tokens,
            )

            return provider

        else:
            raise ValueError(f"Unknown provider type: {provider_type}")


async def get_llm_provider(
    session: AsyncSession,
    provider_type: Optional[str] = None,
) -> LLMProvider:
    """Convenience function to get an LLM provider.

    This is the primary entry point for getting a provider instance.

    Args:
        session: Database session
        provider_type: Optional provider type override

    Returns:
        Configured LLM provider instance
    """
    return await LLMProviderFactory.create_provider(session, provider_type)


def get_llm_provider_sync(provider_type: Optional[str] = None) -> LLMProvider:
    """Convenience function to get an LLM provider synchronously.

    Uses only environment variables for configuration.

    Args:
        provider_type: Optional provider type override

    Returns:
        Configured LLM provider instance
    """
    return LLMProviderFactory.create_provider_sync(provider_type)
