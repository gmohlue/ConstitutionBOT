"""LLM Provider Protocol definition."""

from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol defining the interface for LLM providers.

    This protocol enables duck-typing for provider implementations,
    allowing any class with these methods to be used as a provider.
    """

    @property
    def provider_name(self) -> str:
        """Get the provider name (e.g., 'anthropic', 'openai', 'ollama')."""
        ...

    @property
    def model_name(self) -> str:
        """Get the model name being used."""
        ...

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from a single prompt.

        Args:
            prompt: The user prompt/message
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            The generated text response
        """
        ...

    def generate_with_messages(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from a multi-turn conversation.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Roles should be 'user' or 'assistant'
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            The generated text response
        """
        ...

    def is_available(self) -> bool:
        """Check if the provider is available and configured.

        Returns:
            True if the provider can be used, False otherwise
        """
        ...
