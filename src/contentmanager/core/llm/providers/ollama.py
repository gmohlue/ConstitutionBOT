"""Ollama LLM provider for local models."""

from typing import Optional

import httpx

from contentmanager.core.llm.base import BaseLLMProvider
from contentmanager.core.llm.message_utils import normalize_for_ollama


class OllamaProvider(BaseLLMProvider):
    """LLM provider for Ollama local models."""

    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3.2",
        max_tokens: int = 4096,
    ):
        """Initialize the Ollama provider.

        Args:
            host: Ollama server URL (default: http://localhost:11434)
            model: Model identifier (e.g., 'llama3.2', 'mistral', 'codellama')
            max_tokens: Default maximum tokens for responses
        """
        super().__init__(model=model, max_tokens=max_tokens)
        self._host = host.rstrip("/")
        self._client: Optional[httpx.Client] = None

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "ollama"

    @property
    def client(self) -> httpx.Client:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=120.0)
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
        normalized = normalize_for_ollama(messages, system_prompt)

        return self._chat(normalized, max_tokens, temperature)

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
        normalized = normalize_for_ollama(messages, system_prompt)

        if not normalized:
            raise ValueError("No valid messages provided")

        return self._chat(normalized, max_tokens, temperature)

    def _chat(
        self,
        messages: list[dict],
        max_tokens: Optional[int],
        temperature: float,
    ) -> str:
        """Send a chat request to Ollama.

        Args:
            messages: Normalized messages list
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            The generated text response
        """
        url = f"{self._host}/api/chat"

        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": self._get_max_tokens(max_tokens),
            },
        }

        response = self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        return data["message"]["content"]

    def is_available(self) -> bool:
        """Check if the provider is available and configured.

        Tests connection to Ollama server and checks if model is available.

        Returns:
            True if the provider can be used, False otherwise
        """
        try:
            response = self.client.get(f"{self._host}/api/tags")
            if response.status_code != 200:
                return False

            # Check if the configured model is available
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]

            # Check for exact match or model name without tag
            return any(
                self._model == m or self._model == m.split(":")[0]
                for m in models
            )
        except (httpx.HTTPError, Exception):
            return False

    def list_models(self) -> list[str]:
        """List available models on the Ollama server.

        Returns:
            List of model names, or empty list if unavailable
        """
        try:
            response = self.client.get(f"{self._host}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except (httpx.HTTPError, Exception):
            pass
        return []

    def __del__(self):
        """Clean up HTTP client."""
        if self._client:
            self._client.close()
