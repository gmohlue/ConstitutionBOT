"""Anthropic Claude API client wrapper."""

from typing import Optional

from anthropic import Anthropic

from constitutionbot.config import get_settings


class ClaudeClient:
    """Wrapper for the Anthropic Claude API."""

    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[Anthropic] = None

    @property
    def client(self) -> Anthropic:
        """Get or create the Anthropic client."""
        if self._client is None:
            api_key = self.settings.anthropic_api_key.get_secret_value()
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            self._client = Anthropic(api_key=api_key)
        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from Claude.

        Args:
            prompt: The user prompt/message
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens in response (default from settings)
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            The generated text response
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.settings.anthropic_model,
            "max_tokens": max_tokens or self.settings.anthropic_max_tokens,
            "messages": messages,
            "temperature": temperature,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)

        # Extract text from response
        return response.content[0].text

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


# Singleton instance
_claude_client: Optional[ClaudeClient] = None


def get_claude_client() -> ClaudeClient:
    """Get the singleton Claude client instance."""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client
