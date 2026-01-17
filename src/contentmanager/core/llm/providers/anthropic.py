"""Anthropic Claude LLM provider."""

from typing import Optional

from anthropic import Anthropic

from contentmanager.core.llm.base import BaseLLMProvider
from contentmanager.core.llm.message_utils import normalize_for_anthropic


class AnthropicProvider(BaseLLMProvider):
    """LLM provider for Anthropic Claude models."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
    ):
        """Initialize the Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model identifier (e.g., 'claude-sonnet-4-20250514')
            max_tokens: Default maximum tokens for responses
        """
        super().__init__(model=model, max_tokens=max_tokens)
        self._api_key = api_key
        self._client: Optional[Anthropic] = None

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "anthropic"

    @property
    def client(self) -> Anthropic:
        """Get or create the Anthropic client."""
        if self._client is None:
            if not self._api_key:
                raise ValueError("Anthropic API key not configured")
            self._client = Anthropic(api_key=self._api_key)
        return self._client

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
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self._model,
            "max_tokens": self._get_max_tokens(max_tokens),
            "messages": messages,
            "temperature": temperature,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

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
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            The generated text response
        """
        normalized_messages = normalize_for_anthropic(messages)

        if not normalized_messages:
            raise ValueError("No valid messages provided")

        kwargs = {
            "model": self._model,
            "max_tokens": self._get_max_tokens(max_tokens),
            "messages": normalized_messages,
            "temperature": temperature,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def is_available(self) -> bool:
        """Check if the provider is available and configured.

        Returns:
            True if the provider can be used, False otherwise
        """
        return bool(self._api_key)
