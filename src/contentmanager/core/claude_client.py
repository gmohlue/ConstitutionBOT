"""Anthropic Claude API client wrapper.

DEPRECATED: This module is maintained for backward compatibility.
New code should use the LLM abstraction from `contentmanager.core.llm`.

Example:
    # Old way (still works)
    from contentmanager.core.claude_client import get_claude_client
    client = get_claude_client()
    response = client.generate("prompt")

    # New way (recommended)
    from contentmanager.core.llm import get_llm_provider_sync
    provider = get_llm_provider_sync()
    response = provider.generate("prompt")
"""

from typing import Optional

from contentmanager.config import get_settings
from contentmanager.core.llm import LLMProvider, get_llm_provider_sync


class ClaudeClient:
    """Wrapper for the Anthropic Claude API.

    This class is maintained for backward compatibility with existing code.
    Internally it uses the LLM provider abstraction.
    """

    def __init__(self):
        self.settings = get_settings()
        self._provider: Optional[LLMProvider] = None

    @property
    def provider(self) -> LLMProvider:
        """Get or create the LLM provider."""
        if self._provider is None:
            self._provider = get_llm_provider_sync()
        return self._provider

    # Backward compatibility: expose provider_name and model_name
    @property
    def provider_name(self) -> str:
        """Get the current provider name."""
        return self.provider.provider_name

    @property
    def model_name(self) -> str:
        """Get the current model name."""
        return self.provider.model_name

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt/message
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens in response (default from settings)
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            The generated text response
        """
        return self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def generate_with_context(
        self,
        prompt: str,
        context: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response with additional context.

        Args:
            prompt: The user prompt/message
            context: Additional context (e.g., Constitution sections)
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            The generated text response
        """
        full_prompt = f"""Context:
{context}

---

{prompt}"""

        return self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def generate_structured(
        self,
        prompt: str,
        output_format: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.5,
    ) -> str:
        """Generate a response with a specific output format.

        Args:
            prompt: The user prompt/message
            output_format: Description of expected output format
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (lower for more consistent output)

        Returns:
            The generated text response
        """
        formatted_prompt = f"""{prompt}

Output Format:
{output_format}"""

        return self.generate(
            prompt=formatted_prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

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
            max_tokens: Maximum tokens in response (default from settings)
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            The generated text response
        """
        return self.provider.generate_with_messages(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )


# Singleton instance
_claude_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    """Get the singleton Claude client instance.

    DEPRECATED: Use `get_llm_provider_sync()` from `contentmanager.core.llm` instead.
    """
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client
