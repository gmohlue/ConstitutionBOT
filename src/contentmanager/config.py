"""Configuration management using Pydantic settings."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_base_dir() -> Path:
    """Get the base directory of the project."""
    return Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Paths - using Optional with computed defaults
    base_dir: Path = Field(default_factory=_get_base_dir)
    data_dir: Optional[Path] = Field(default=None)
    constitution_uploads_dir: Optional[Path] = Field(default=None)
    constitution_processed_dir: Optional[Path] = Field(default=None)
    prompts_dir: Optional[Path] = Field(default=None)
    database_dir: Optional[Path] = Field(default=None)

    # LLM Provider Selection
    llm_provider: str = Field(default="anthropic")  # anthropic, openai, ollama

    # Anthropic API
    anthropic_api_key: SecretStr = Field(default=SecretStr(""))
    anthropic_model: str = Field(default="claude-sonnet-4-20250514")
    anthropic_max_tokens: int = Field(default=4096)

    # OpenAI API
    openai_api_key: SecretStr = Field(default=SecretStr(""))
    openai_model: str = Field(default="gpt-4o")
    openai_max_tokens: int = Field(default=4096)

    # Ollama (Local LLM)
    ollama_host: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3.2")
    ollama_max_tokens: int = Field(default=4096)

    # Twitter/X API
    twitter_api_key: SecretStr = Field(default=SecretStr(""))
    twitter_api_secret: SecretStr = Field(default=SecretStr(""))
    twitter_access_token: SecretStr = Field(default=SecretStr(""))
    twitter_access_secret: SecretStr = Field(default=SecretStr(""))
    twitter_bearer_token: SecretStr = Field(default=SecretStr(""))

    # Dashboard
    dashboard_secret_key: SecretStr = Field(default=SecretStr("dev-secret-key-change-in-production"))
    dashboard_username: str = Field(default="admin")
    dashboard_password: SecretStr = Field(default=SecretStr("admin"))
    dashboard_host: str = Field(default="127.0.0.1")
    dashboard_port: int = Field(default=8000)

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./data/database/contentmanager.db")

    # Bot Settings
    bot_enabled: bool = Field(default=False)
    mention_check_interval: int = Field(default=60)  # seconds
    auto_generate_enabled: bool = Field(default=False)
    auto_generate_interval: int = Field(default=3600)  # seconds

    # Content Settings
    max_tweet_length: int = Field(default=280)
    max_thread_tweets: int = Field(default=10)
    default_hashtags: list[str] = Field(default_factory=lambda: ["#SAConstitution", "#CivicEducation"])

    @model_validator(mode="after")
    def set_derived_paths(self) -> "Settings":
        """Set derived paths after initialization."""
        if self.data_dir is None:
            object.__setattr__(self, "data_dir", self.base_dir / "data")
        if self.constitution_uploads_dir is None:
            object.__setattr__(self, "constitution_uploads_dir", self.data_dir / "constitution" / "uploads")
        if self.constitution_processed_dir is None:
            object.__setattr__(self, "constitution_processed_dir", self.data_dir / "constitution" / "processed")
        if self.prompts_dir is None:
            object.__setattr__(self, "prompts_dir", self.data_dir / "prompts" / "system_prompts")
        if self.database_dir is None:
            object.__setattr__(self, "database_dir", self.data_dir / "database")

        # Ensure directories exist
        for dir_path in [
            self.constitution_uploads_dir,
            self.constitution_processed_dir,
            self.prompts_dir,
            self.database_dir,
        ]:
            if dir_path:
                dir_path.mkdir(parents=True, exist_ok=True)

        return self

    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for migrations."""
        return self.database_url.replace("sqlite+aiosqlite:", "sqlite:")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
