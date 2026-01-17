"""Base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    Provides common functionality and enforces the provider interface.
    """

    def __init__(
        self,
        model: str,
        max_tokens: int = 4096,
    ):
        """Initialize the provider.

        Args:
            model: The model identifier to use
            max_tokens: Default maximum tokens for responses
        """
        self._model = model
        self._max_tokens = max_tokens

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name."""
        ...

    @property
    def model_name(self) -> str:
        """Get the model name being used."""
        return self._model

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from a single prompt."""
        ...

    @abstractmethod
    def generate_with_messages(
        self,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from a multi-turn conversation."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        ...

    def _get_max_tokens(self, max_tokens: Optional[int]) -> int:
        """Get max tokens to use, with fallback to default."""
        return max_tokens if max_tokens is not None else self._max_tokens
