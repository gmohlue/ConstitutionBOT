"""OpenAI GPT LLM provider."""

from typing import Optional

from constitutionbot.core.llm.base import BaseLLMProvider
from constitutionbot.core.llm.message_utils import normalize_for_openai


class OpenAIProvider(BaseLLMProvider):
    """LLM provider for OpenAI GPT models."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        max_tokens: int = 4096,
    ):
        """Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model identifier (e.g., 'gpt-4o', 'gpt-4', 'gpt-3.5-turbo')
            max_tokens: Default maximum tokens for responses
        """
        super().__init__(model=model, max_tokens=max_tokens)
        self._api_key = api_key
        self._client = None

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openai"

    @property
    def client(self):
        """Get or create the OpenAI client."""
        if self._client is None:
            if not self._api_key:
                raise ValueError("OpenAI API key not configured")
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self._api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
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
        normalized = normalize_for_openai(messages, system_prompt)

        response = self.client.chat.completions.create(
            model=self._model,
            messages=normalized,
            max_tokens=self._get_max_tokens(max_tokens),
            temperature=temperature,
        )

        return response.choices[0].message.content

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
        normalized = normalize_for_openai(messages, system_prompt)

        if not normalized:
            raise ValueError("No valid messages provided")

        response = self.client.chat.completions.create(
            model=self._model,
            messages=normalized,
            max_tokens=self._get_max_tokens(max_tokens),
            temperature=temperature,
        )

        return response.choices[0].message.content

    def is_available(self) -> bool:
        """Check if the provider is available and configured.

        Returns:
            True if the provider can be used, False otherwise
        """
        if not self._api_key:
            return False
        try:
            from openai import OpenAI  # noqa: F401
            return True
        except ImportError:
            return False
