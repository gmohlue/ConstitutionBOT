"""LLM Provider configuration schemas."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LLMProviderType(str, Enum):
    """Supported LLM provider types."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"


class AnthropicConfig(BaseModel):
    """Configuration for Anthropic Claude provider."""

    api_key: str = ""
    model: str = Field(default="claude-sonnet-4-20250514")
    max_tokens: int = Field(default=4096)


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI GPT provider."""

    api_key: str = ""
    model: str = Field(default="gpt-4o")
    max_tokens: int = Field(default=4096)


class OllamaConfig(BaseModel):
    """Configuration for Ollama local provider."""

    host: str = Field(default="http://localhost:11434")
    model: str = Field(default="llama3.2")
    max_tokens: int = Field(default=4096)


class LLMConfig(BaseModel):
    """Complete LLM configuration."""

    provider: LLMProviderType = Field(default=LLMProviderType.ANTHROPIC)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)


# Available models per provider
AVAILABLE_MODELS = {
    LLMProviderType.ANTHROPIC: [
        "claude-sonnet-4-20250514",
        "claude-opus-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
    ],
    LLMProviderType.OPENAI: [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ],
    LLMProviderType.OLLAMA: [
        "llama3.2",
        "llama3.1",
        "llama2",
        "mistral",
        "codellama",
        "phi3",
    ],
}
